"""
E-03 — Propuestas de mejora, simuladas y comparadas.

E-01 mostró dónde está el problema: el control tiene rho = 0,86 con un solo
operario y supera 1 en la cresta de la tarde; el empaque queda bloqueado en uno
de cada diez pedidos porque la mesa de despacho se llena.

Se proponen cinco intervenciones y se simulan todas con el mismo volumen, las
mismas semillas y las mismas réplicas, para que la comparación sea limpia.
Cada una se evalúa por lo que mejora **y** por lo que cuesta.
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from modelo import economia as eco
from modelo import parametros as p
from modelo import red
from modelo import simular as sim

REPLICAS = 30
HORIZONTE = p.JORNADA_MIN * 1.6
SALIDA = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                      "resultados", "e03-mejoras.json")

# Refuerzo de tarde: de 14:00 a 19:00, que es donde está la cresta.
REFUERZO_DESDE = (14 - p.APERTURA) * 60      # 300 min
REFUERZO_HASTA = p.JORNADA_MIN               # 600 min
HORAS_REFUERZO = (REFUERZO_HASTA - REFUERZO_DESDE) / 60


ESCENARIOS = [
    {
        "clave": "base",
        "nombre": "Base (sin cambios)",
        "kwargs": {},
        "operarios": 6,
        "horas_extra": 0.0,
        "idea": "La situación actual, como referencia.",
    },
    {
        "clave": "mesa",
        "nombre": "Mesa de despacho más grande (5 → 15)",
        "kwargs": {"capacidad_cola_control": 15},
        "operarios": 6,
        "horas_extra": 0.0,
        "idea": "No cuesta sueldos: solo más espacio físico para cajas en espera.",
    },
    {
        "clave": "control2",
        "nombre": "Segundo operario en control, jornada completa",
        "kwargs": {"servidores_control": 2},
        "operarios": 7,
        "horas_extra": 0.0,
        "idea": "La respuesta obvia: contratar donde está el cuello.",
    },
    {
        "clave": "turno",
        "nombre": "Refuerzo de control solo en la cresta (14:00–19:00)",
        "kwargs": {"servidores_control": red.turno_escalonado(
            base=1, refuerzo=2, desde_min=REFUERZO_DESDE,
            hasta_min=REFUERZO_HASTA, horizonte=HORIZONTE)},
        "operarios": 6,
        "horas_extra": HORAS_REFUERZO,
        "idea": "Pagar capacidad solo en las horas que hacen falta.",
    },
    {
        "clave": "turno_mesa",
        "nombre": "Refuerzo en la cresta + mesa de 15",
        "kwargs": {"servidores_control": red.turno_escalonado(
            base=1, refuerzo=2, desde_min=REFUERZO_DESDE,
            hasta_min=REFUERZO_HASTA, horizonte=HORIZONTE),
            "capacidad_cola_control": 15},
        "operarios": 6,
        "horas_extra": HORAS_REFUERZO,
        "idea": "Las dos anteriores juntas: capacidad cuando se necesita y "
                "sin bloqueo aguas arriba.",
    },
    {
        "clave": "empaque3",
        "nombre": "Tercer operario en empaque",
        "kwargs": {"servidores_empaque": 3},
        "operarios": 7,
        "horas_extra": 0.0,
        "idea": "Control: reforzar donde NO está el cuello, para mostrar que "
                "agregar gente en el lugar equivocado no sirve.",
    },
]


def evaluar_escenario(esc):
    # El horizonte NO se pasa aquí: `simular_dia` ya corre hasta 1,6 veces la
    # jornada para vaciar la cola. Pasarlo haría que siguieran entrando
    # pedidos después del cierre y la base dejaría de ser comparable.
    res = sim.replicar(REPLICAS, **esc["kwargs"])
    r = sim.resumir(res)
    ev = eco.evaluar(esc["operarios"], p.PEDIDOS_DIA, esc["horas_extra"])
    atrasos = eco.costo_de_incumplir(p.PEDIDOS_DIA, r["sla_medio"])
    return {
        "clave": esc["clave"], "nombre": esc["nombre"], "idea": esc["idea"],
        "sla": r["sla_medio"], "tiempo_medio": r["tiempo_total_medio"],
        "tiempo_p95": r["tiempo_total_p95"],
        "rho_control": r["estaciones"]["Control"]["rho"],
        "bloqueo_empaque": r["estaciones"]["Empaque"]["pct_bloqueados"],
        "wq_control": r["estaciones"]["Control"]["Wq"],
        "costo_mes": ev.costos.total_mes,
        "atrasos_mes": atrasos,
        "utilidad_mes": ev.utilidad_mes,
        "neto_mes": ev.utilidad_mes - atrasos,
    }


def main():
    print("E-03 · Propuestas de mejora")
    print("=" * 100)
    print(f"{p.PEDIDOS_DIA} pedidos/día · {REPLICAS} réplicas por escenario · "
          f"mismas semillas en todos\n")

    filas = [evaluar_escenario(e) for e in ESCENARIOS]
    base = filas[0]

    print(f"{'Escenario':<46}{'SLA %':>8}{'ΔSLA':>8}{'T med':>8}"
          f"{'ρ ctrl':>8}{'bloq':>8}{'Wq ctrl':>9}")
    print("-" * 100)
    for f in filas:
        d = f["sla"] - base["sla"]
        print(f"{f['nombre']:<46}{f['sla']:>8.1f}{d:>+8.1f}{f['tiempo_medio']:>8.1f}"
              f"{f['rho_control']:>8.2f}{f['bloqueo_empaque']:>7.1f}%{f['wq_control']:>9.2f}")

    print("\n\nLo que cuesta cada una, al mes")
    print("-" * 100)
    print(f"{'Escenario':<46}{'costo op.':>14}{'atrasos':>14}"
          f"{'neto':>16}{'Δ neto':>14}")
    print("-" * 100)
    for f in filas:
        d = f["neto_mes"] - base["neto_mes"]
        print(f"{f['nombre']:<46}{eco.pesos(f['costo_mes']):>14}"
              f"{eco.pesos(f['atrasos_mes']):>14}{eco.pesos(f['neto_mes']):>16}"
              f"{(eco.pesos(d) if d else '—'):>14}")

    # ── Las dos lecturas, que no coinciden ──────────────────────────────────
    mejor_sla = max(filas[1:], key=lambda f: f["sla"])
    mejor_neto = max(filas[1:], key=lambda f: f["neto_mes"])

    print(f"\n\nPor cumplimiento: {mejor_sla['nombre']}")
    print(f"  SLA {base['sla']:.1f} % → {mejor_sla['sla']:.1f} % "
          f"({mejor_sla['sla'] - base['sla']:+.1f} puntos), "
          f"bloqueo {base['bloqueo_empaque']:.1f} % → {mejor_sla['bloqueo_empaque']:.1f} %")
    print(f"Por resultado neto: {mejor_neto['nombre']}")

    if mejor_sla["clave"] != mejor_neto["clave"]:
        print("\n  Los dos criterios NO coinciden, y eso es el resultado, no un")
        print("  problema del modelo: con el costo de atraso supuesto")
        print(f"  ({eco.pesos(3500)} por pedido), ninguna mejora de dotación se paga sola.")

    # ── ¿Desde qué costo de atraso conviene reforzar? ───────────────────────
    print("\n\nSensibilidad: ¿cuánto tiene que costar un atraso para que convenga?")
    print("-" * 100)
    print("  El supuesto de $3.500 por despacho tardío es el más débil del")
    print("  análisis. En vez de defenderlo, se invierte la pregunta: ¿a partir")
    print("  de qué costo cada mejora se financia sola?")
    print(f"{'Escenario':<46}{'Δ costo/mes':>15}{'atrasos evitados':>19}{'punto de equilibrio':>22}")
    print("-" * 100)

    pedidos_mes = p.PEDIDOS_DIA * p.DIAS_HABILES_MES
    for f in filas[1:]:
        delta_costo = f["costo_mes"] - base["costo_mes"]
        evitados = pedidos_mes * (f["sla"] - base["sla"]) / 100
        if evitados > 0.5 and delta_costo > 0:
            equilibrio = delta_costo / evitados
            txt = eco.pesos(equilibrio) + " / atraso"
        elif delta_costo <= 0:
            txt = "no cuesta nada"
        else:
            txt = "nunca: no evita atrasos"
        print(f"{f['nombre']:<46}{eco.pesos(delta_costo):>15}"
              f"{evitados:>19.0f}{txt:>22}")

    print("\n  Leído al revés: si la empresa estima que un despacho tardío le")
    print("  cuesta más que el punto de equilibrio de una fila, esa mejora")
    print("  conviene. Es una decisión de negocio, y el modelo entrega el")
    print("  número exacto sobre el que decidir.")

    os.makedirs(os.path.dirname(SALIDA), exist_ok=True)
    with open(SALIDA, "w", encoding="utf-8") as fh:
        json.dump({"replicas": REPLICAS, "pedidos_dia": p.PEDIDOS_DIA,
                   "escenarios": filas}, fh, ensure_ascii=False, indent=1)
    print(f"\nGuardado en {SALIDA}")


if __name__ == "__main__":
    main()
