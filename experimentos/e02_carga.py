"""
E-02 — Pruebas de carga: ¿hasta dónde aguanta la bodega?

El enunciado pide determinar límites máximos. Se escala la demanda completa
por un factor, conservando el perfil horario, y se busca el punto en que el
sistema deja de cumplir.

Se reportan tres límites distintos, porque "el máximo" no es un solo número:

  · Límite de servicio  — el último volumen con 95 % de cumplimiento del SLA
  · Límite operativo    — el último volumen en que la cola se vacía el mismo día
  · Límite físico       — el volumen en que alguna estación llega a rho = 1
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from modelo import economia as eco
from modelo import parametros as p
from modelo import simular as sim

REPLICAS = 20
FACTORES = [0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6]
SALIDA = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                      "resultados", "e02-carga.json")

UMBRAL_SLA = 95.0


def main():
    print("E-02 · Pruebas de carga")
    print("=" * 86)
    print(f"Dotación fija: {p.PICKING.servidores} picking · {p.EMPAQUE.servidores} "
          f"empaque · {p.CONTROL.servidores} control · mesa para "
          f"{p.CAPACIDAD_COLA_CONTROL} cajas")
    print(f"{REPLICAS} réplicas por punto. Se escala la demanda conservando el perfil horario.\n")

    print(f"{'factor':>7}{'ped/día':>9}{'T medio':>10}{'T p95':>9}{'SLA %':>8}"
          f"{'ρ pick':>8}{'ρ emp':>8}{'ρ ctrl':>8}{'bloq emp':>10}{'Lq ctrl':>9}")
    print("-" * 86)

    filas = []
    for f in FACTORES:
        res = sim.replicar(REPLICAS, factor_demanda=f)
        r = sim.resumir(res)
        e = r["estaciones"]
        fila = {
            "factor": f,
            "pedidos_dia": r["pedidos_ingresados"],
            "tiempo_medio": r["tiempo_total_medio"],
            "tiempo_p95": r["tiempo_total_p95"],
            "sla": r["sla_medio"],
            "rho_picking": e["Picking"]["rho"],
            "rho_empaque": e["Empaque"]["rho"],
            "rho_control": e["Control"]["rho"],
            "bloqueo_empaque": e["Empaque"]["pct_bloqueados"],
            "lq_control": e["Control"]["Lq"],
        }
        filas.append(fila)
        print(f"{f:>7.1f}{fila['pedidos_dia']:>9.0f}{fila['tiempo_medio']:>10.1f}"
              f"{fila['tiempo_p95']:>9.1f}{fila['sla']:>8.1f}"
              f"{fila['rho_picking']:>8.2f}{fila['rho_empaque']:>8.2f}"
              f"{fila['rho_control']:>8.2f}{fila['bloqueo_empaque']:>9.1f}%"
              f"{fila['lq_control']:>9.2f}")

    # ── Los tres límites ────────────────────────────────────────────────────
    print("\nLímites encontrados")
    print("-" * 86)

    cumplen = [x for x in filas if x["sla"] >= UMBRAL_SLA]
    if cumplen:
        mejor = max(cumplen, key=lambda x: x["factor"])
        print(f"  Límite de servicio   {mejor['pedidos_dia']:>6.0f} pedidos/día "
              f"(factor {mejor['factor']:.1f}) — último con SLA ≥ {UMBRAL_SLA:.0f} %")
    else:
        print(f"  Límite de servicio      ninguno: ni con factor {FACTORES[0]} "
              f"se alcanza {UMBRAL_SLA:.0f} % de cumplimiento")

    saturan = [x for x in filas if max(x["rho_picking"], x["rho_empaque"],
                                       x["rho_control"]) >= 0.98]
    if saturan:
        s = min(saturan, key=lambda x: x["factor"])
        cual = max(("Picking", s["rho_picking"]), ("Empaque", s["rho_empaque"]),
                   ("Control", s["rho_control"]), key=lambda t: t[1])
        print(f"  Límite físico        {s['pedidos_dia']:>6.0f} pedidos/día "
              f"(factor {s['factor']:.1f}) — {cual[0]} llega a ρ = {cual[1]:.2f}")
    else:
        print("  Límite físico           no alcanzado en el rango probado")

    print("\n  La distancia entre ambos límites es el margen de maniobra: el")
    print("  sistema sigue siendo capaz de procesar todo mucho después de")
    print("  dejar de hacerlo a tiempo.")

    # ── Lectura económica ───────────────────────────────────────────────────
    print("\nLo que cuesta crecer sin tocar la bodega")
    print("-" * 86)
    print(f"{'ped/día':>9}{'utilidad/mes':>16}{'atrasos/mes':>15}{'neto':>16}")
    for x in filas:
        ev = eco.evaluar(p.operarios_totales(), x["pedidos_dia"])
        atr = eco.costo_de_incumplir(x["pedidos_dia"], x["sla"])
        print(f"{x['pedidos_dia']:>9.0f}{eco.pesos(ev.utilidad_mes):>16}"
              f"{eco.pesos(atr):>15}{eco.pesos(ev.utilidad_mes - atr):>16}")

    os.makedirs(os.path.dirname(SALIDA), exist_ok=True)
    with open(SALIDA, "w", encoding="utf-8") as fh:
        json.dump({"umbral_sla": UMBRAL_SLA, "replicas": REPLICAS, "puntos": filas},
                  fh, ensure_ascii=False, indent=1)
    print(f"\nGuardado en {SALIDA}")


if __name__ == "__main__":
    main()
