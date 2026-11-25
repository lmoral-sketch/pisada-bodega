"""
E-01 — Modelo base: el día típico.

Treinta réplicas del día de 300 pedidos con la dotación actual (3 picking,
2 empaque, 1 control) y la mesa de despacho con capacidad 5.

Responde: ¿cómo se comporta la bodega hoy, y dónde está el cuello?
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modelo import economia as eco
from modelo import parametros as p
from modelo import simular as sim

REPLICAS = 30
SALIDA = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                      "resultados", "e01-base.json")


def main():
    print("E-01 · Modelo base — día típico de", p.PEDIDOS_DIA, "pedidos")
    print("=" * 72)

    print("\nUtilización teórica de referencia (rho = lambda / (s·mu)):")
    print(f"  {'Estación':<24}{'s':>3}{'cap/h':>9}{'rho medio':>12}{'rho cresta':>12}")
    for e in p.ESTACIONES:
        print(f"  {e.nombre:<24}{e.servidores:>3}"
              f"{p.capacidad_estacion_por_hora(e):>9.1f}"
              f"{p.utilizacion_teorica(e, p.LAMBDA_PROMEDIO_HORA):>12.2f}"
              f"{p.utilizacion_teorica(e, p.LAMBDA_PICO_HORA):>12.2f}")
    print("\n  En la cresta de las 17:00 el control supera rho = 1: la fórmula")
    print("  anuncia que la cola crece sin límite. La simulación dirá cuánto")
    print("  crece realmente en dos horas, que es lo que la fórmula no puede.")

    resultados = sim.replicar(REPLICAS)
    r = sim.resumir(resultados)

    print(f"\nResultados sobre {r['replicas']} réplicas")
    print("-" * 72)
    print(f"  Pedidos ingresados        {r['pedidos_ingresados']:>8.1f}")
    print(f"  Pedidos despachados       {r['pedidos_despachados']:>8.1f}")
    print(f"  Tiempo total medio        {r['tiempo_total_medio']:>8.1f} min")
    print(f"  Tiempo total p(95)        {r['tiempo_total_p95']:>8.1f} min")
    print(f"  Cumplimiento del SLA      {r['sla_medio']:>8.1f} %"
          f"   (entre {r['sla_min']:.1f} y {r['sla_max']:.1f})")

    print(f"\n  {'Estación':<12}{'Wq':>8}{'W':>8}{'Lq':>8}{'L':>8}"
          f"{'rho':>8}{'bloqueo':>10}")
    for nombre, e in r["estaciones"].items():
        print(f"  {nombre:<12}{e['Wq']:>8.2f}{e['W']:>8.2f}{e['Lq']:>8.2f}"
              f"{e['L']:>8.2f}{e['rho']:>8.2f}{e['pct_bloqueados']:>9.1f}%")

    print("\n  Wq y W en minutos · Lq y L en pedidos · bloqueo = % de pedidos")
    print("  que dejaron al servidor de esa estación esperando para soltar.")

    ev = eco.evaluar(operarios=p.operarios_totales(), pedidos_dia=p.PEDIDOS_DIA)
    print("\nEconomía mensual")
    print("-" * 72)
    print(f"  Pedidos al mes            {ev.pedidos_mes:>12,}".replace(",", "."))
    print(f"  Margen logístico          {eco.pesos(ev.margen_mes):>12}")
    print(f"  Sueldos ({ev.costos.operarios} operarios)      {eco.pesos(ev.costos.sueldos_mes):>12}")
    print(f"  Arriendo                  {eco.pesos(ev.costos.arriendo_mes):>12}")
    print(f"  Insumos                   {eco.pesos(ev.costos.insumos_mes):>12}")
    print(f"  Costo total               {eco.pesos(ev.costos.total_mes):>12}")
    print(f"  Utilidad                  {eco.pesos(ev.utilidad_mes):>12}")
    print(f"  Costo por pedido          {eco.pesos(ev.costos.costo_por_pedido):>12}")
    print(f"  Equilibrio                {ev.pedidos_equilibrio_dia:>12.0f} pedidos/día")

    perdida = eco.costo_de_incumplir(p.PEDIDOS_DIA, r["sla_medio"])
    print(f"  Costo de los atrasos      {eco.pesos(perdida):>12}  "
          f"({100 - r['sla_medio']:.1f} % fuera de plazo)")

    os.makedirs(os.path.dirname(SALIDA), exist_ok=True)
    with open(SALIDA, "w", encoding="utf-8") as f:
        json.dump({"resumen": r,
                   "economia": {"utilidad_mes": ev.utilidad_mes,
                                "costo_por_pedido": ev.costos.costo_por_pedido,
                                "equilibrio_dia": ev.pedidos_equilibrio_dia,
                                "costo_atrasos_mes": perdida}},
                  f, ensure_ascii=False, indent=1)
    print(f"\nGuardado en {SALIDA}")


if __name__ == "__main__":
    main()
