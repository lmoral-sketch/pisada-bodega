"""
E-04 — Volver a simular la carga con la mejora aplicada.

El enunciado lo pide de forma explícita: *«Se debe simular con los nuevos
resultados y presentar conclusiones»*. E-03 comparó las intervenciones a
volumen fijo, que responde «¿cuál conviene?». Falta la otra pregunta, que es la
que importa para decidir si la inversión habilita crecimiento:

    ¿Hasta dónde aguanta la bodega DESPUÉS de la mejora?

Se repite el barrido de E-02 con la configuración propuesta —refuerzo del
control entre las 14:00 y las 19:00, y mesa de despacho de 15 cajas— y se
comparan los dos límites.
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

REPLICAS = 20
FACTORES = [0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6]
UMBRAL_SLA = 95.0
HORIZONTE = p.JORNADA_MIN * 1.6
REFUERZO_DESDE = (14 - p.APERTURA) * 60
HORAS_REFUERZO = (p.JORNADA_MIN - REFUERZO_DESDE) / 60

RUTA_E02 = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        "resultados", "e02-carga.json")
SALIDA = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                      "resultados", "e04-limite-mejorado.json")


def configuracion_mejorada():
    return {
        "servidores_control": red.turno_escalonado(
            base=1, refuerzo=2, desde_min=REFUERZO_DESDE,
            hasta_min=p.JORNADA_MIN, horizonte=HORIZONTE),
        "capacidad_cola_control": 15,
    }


def limite(puntos):
    cumplen = [x for x in puntos if x["sla"] >= UMBRAL_SLA]
    return max(cumplen, key=lambda x: x["factor"])["pedidos_dia"] if cumplen else None


def main():
    print("E-04 · El límite, después de la mejora")
    print("=" * 84)
    print("Configuración: refuerzo del control de 14:00 a 19:00 + mesa de 15 cajas")
    print(f"{REPLICAS} réplicas por punto, mismas semillas y mismos factores que E-02.\n")

    with open(RUTA_E02, encoding="utf-8") as f:
        antes = json.load(f)["puntos"]

    despues = []
    print(f"{'ped/día':>9}{'SLA antes':>12}{'SLA después':>14}{'Δ':>8}"
          f"{'T antes':>10}{'T después':>12}{'bloq desp.':>12}")
    print("-" * 84)
    for f_, a in zip(FACTORES, antes):
        res = sim.replicar(REPLICAS, factor_demanda=f_, **configuracion_mejorada())
        r = sim.resumir(res)
        fila = {
            "factor": f_,
            "pedidos_dia": r["pedidos_ingresados"],
            "sla": r["sla_medio"],
            "tiempo_medio": r["tiempo_total_medio"],
            "bloqueo_empaque": r["estaciones"]["Empaque"]["pct_bloqueados"],
            "rho_control": r["estaciones"]["Control"]["rho"],
        }
        despues.append(fila)
        print(f"{fila['pedidos_dia']:>9.0f}{a['sla']:>12.1f}{fila['sla']:>14.1f}"
              f"{fila['sla'] - a['sla']:>+8.1f}{a['tiempo_medio']:>10.1f}"
              f"{fila['tiempo_medio']:>12.1f}{fila['bloqueo_empaque']:>11.1f}%")

    lim_antes, lim_despues = limite(antes), limite(despues)

    print("\nEl límite se corrió")
    print("-" * 84)
    print(f"  Antes de la mejora   {lim_antes:>6.0f} pedidos/día con SLA ≥ {UMBRAL_SLA:.0f} %")
    if lim_despues:
        print(f"  Después de la mejora {lim_despues:>6.0f} pedidos/día")
        extra = lim_despues - lim_antes
        print(f"  Ganancia             {extra:>6.0f} pedidos/día "
              f"({100 * extra / lim_antes:+.0f} %)")
    else:
        print("  Después de la mejora: no se alcanza el umbral en el rango probado")
        extra = 0

    # ── ¿La mejora se paga con el crecimiento que habilita? ─────────────────
    if lim_despues:
        print("\nLo que vale ese espacio")
        print("-" * 84)
        base_costo = eco.costos_mensuales(p.operarios_totales(), p.PEDIDOS_DIA).total_mes
        nuevo_costo = eco.costos_mensuales(p.operarios_totales(), lim_despues,
                                           HORAS_REFUERZO).total_mes
        d_costo = nuevo_costo - base_costo
        margen_extra = extra * p.DIAS_HABILES_MES * (
            p.MARGEN_LOGISTICO_POR_PEDIDO - p.INSUMOS_POR_PEDIDO)
        print(f"  Pedidos adicionales que se pueden atender a tiempo  "
              f"{extra * p.DIAS_HABILES_MES:>10.0f} al mes")
        print(f"  Margen que aportan (neto de insumos)                "
              f"{eco.pesos(margen_extra):>10}")
        print(f"  Costo adicional de la mejora                        "
              f"{eco.pesos(d_costo):>10}")
        print(f"  Diferencia                                          "
              f"{eco.pesos(margen_extra - d_costo):>10}")
        print("\n  Esta es la lectura que faltaba: la mejora no solo reduce atrasos")
        print("  sobre el volumen actual, sino que **habilita crecer** sin")
        print("  contratar a nadie más. El retorno viene del crecimiento, no del")
        print("  ahorro, y por eso no dependía del supuesto de cuánto cuesta un")
        print("  atraso, que era el punto débil de E-03.")

    with open(SALIDA, "w", encoding="utf-8") as f:
        json.dump({"umbral_sla": UMBRAL_SLA, "replicas": REPLICAS,
                   "limite_antes": lim_antes, "limite_despues": lim_despues,
                   "puntos": despues}, f, ensure_ascii=False, indent=1)
    print(f"\nGuardado en {SALIDA}")


if __name__ == "__main__":
    main()
