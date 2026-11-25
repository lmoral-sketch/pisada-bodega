"""
Ejecuta la simulación y extrae los indicadores de teoría de colas.

Cada corrida es **un día de bodega**, que abre vacía y cierra cuando ya no
entran pedidos. No se descarta un período de calentamiento a propósito: el
transitorio de la mañana no es ruido que haya que eliminar, es parte del
fenómeno que se estudia. Lo que se hace en cambio es **replicar días**, que es
la forma correcta de estimar en un sistema que nunca alcanza régimen
estacionario.
"""

from dataclasses import dataclass, field
from statistics import mean, median, quantiles

import ciw

from . import parametros as p
from .red import construir_red

NOMBRES = {1: "Picking", 2: "Empaque", 3: "Control"}


@dataclass
class IndicadoresEstacion:
    nodo: int
    nombre: str
    n: int
    Wq: float          # espera media en cola (min)
    W: float           # tiempo medio en el sistema de la estación (min)
    Lq: float          # nº medio esperando
    L: float           # nº medio en la estación
    rho: float         # utilización observada de los servidores
    bloqueo_medio: float   # minutos medios bloqueado por pedido
    pct_bloqueados: float  # % de pedidos que dejaron al servidor bloqueado


@dataclass
class ResultadoDia:
    pedidos_ingresados: int
    pedidos_despachados: int
    tiempo_total_medio: float
    tiempo_total_p95: float
    cumplimiento_sla: float
    estaciones: list[IndicadoresEstacion] = field(default_factory=list)


def _percentil(valores, q):
    if not valores:
        return 0.0
    if len(valores) < 2:
        return valores[0]
    return quantiles(valores, n=100)[q - 1]


def simular_dia(semilla: int, horizonte: float | None = None, **kwargs) -> ResultadoDia:
    """
    Una réplica. `kwargs` se pasan tal cual a `construir_red`.

    El horizonte de simulación excede la jornada para dejar que la cola
    pendiente al cierre termine de procesarse: así se mide cuánto se demora en
    vaciarse, que es parte del resultado.
    """
    horizonte = p.JORNADA_MIN if horizonte is None else horizonte
    ciw.seed(semilla)
    red = construir_red(horizonte=horizonte, **kwargs)
    sim = ciw.Simulation(red, tracker=ciw.trackers.NodePopulation())
    # Se simula más allá del cierre para vaciar la cola pendiente.
    sim.simulate_until_max_time(horizonte * 1.6)

    registros = sim.get_all_records()
    por_nodo = {n: [r for r in registros if r.node == n] for n in NOMBRES}

    # Recorrido completo del pedido: desde que entra a picking hasta que sale
    # de control.
    llegada, salida = {}, {}
    for r in registros:
        if r.node == 1:
            llegada[r.id_number] = r.arrival_date
        if r.node == 3:
            salida[r.id_number] = r.exit_date
    completos = [salida[i] - llegada[i] for i in salida if i in llegada]
    a_tiempo = [i for i in salida if i in llegada and salida[i] <= p.SLA_MIN]

    estaciones = []
    for nodo, nombre in NOMBRES.items():
        rs = por_nodo[nodo]
        if not rs:
            continue
        esperas = [r.waiting_time for r in rs]
        servicios = [r.service_time for r in rs]
        bloqueos = [r.time_blocked for r in rs]
        duracion = max(r.exit_date for r in rs)
        # L y Lq por la ley de Little sobre la ventana observada.
        lam = len(rs) / duracion
        Wq_, W_ = mean(esperas), mean(esperas) + mean(servicios) + mean(bloqueos)
        servidores = kwargs.get(
            {1: "servidores_picking", 2: "servidores_empaque", 3: "servidores_control"}[nodo]
        )
        if servidores is None or not isinstance(servidores, int):
            servidores = {1: p.PICKING.servidores, 2: p.EMPAQUE.servidores,
                          3: p.CONTROL.servidores}[nodo]
        estaciones.append(IndicadoresEstacion(
            nodo=nodo, nombre=nombre, n=len(rs),
            Wq=Wq_, W=W_,
            Lq=lam * Wq_, L=lam * W_,
            rho=sum(servicios) / (duracion * servidores),
            bloqueo_medio=mean(bloqueos),
            pct_bloqueados=100 * sum(1 for b in bloqueos if b > 0) / len(bloqueos),
        ))

    return ResultadoDia(
        pedidos_ingresados=len(llegada),
        pedidos_despachados=len(salida),
        tiempo_total_medio=mean(completos) if completos else 0.0,
        tiempo_total_p95=_percentil(sorted(completos), 95),
        cumplimiento_sla=100 * len(a_tiempo) / len(salida) if salida else 0.0,
        estaciones=estaciones,
    )


def replicar(dias: int = 30, semilla_base: int = 2026, **kwargs) -> list[ResultadoDia]:
    """Corre `dias` réplicas independientes con semillas consecutivas."""
    return [simular_dia(semilla_base + d, **kwargs) for d in range(dias)]


def resumir(resultados: list[ResultadoDia]) -> dict:
    """Promedia las réplicas y entrega el rango, que es lo que se reporta."""
    def col(f):
        return [f(r) for r in resultados]

    resumen = {
        "replicas": len(resultados),
        "pedidos_ingresados": mean(col(lambda r: r.pedidos_ingresados)),
        "pedidos_despachados": mean(col(lambda r: r.pedidos_despachados)),
        "tiempo_total_medio": mean(col(lambda r: r.tiempo_total_medio)),
        "tiempo_total_p95": mean(col(lambda r: r.tiempo_total_p95)),
        "sla_medio": mean(col(lambda r: r.cumplimiento_sla)),
        "sla_min": min(col(lambda r: r.cumplimiento_sla)),
        "sla_max": max(col(lambda r: r.cumplimiento_sla)),
        "estaciones": {},
    }
    for nodo, nombre in NOMBRES.items():
        filas = [e for r in resultados for e in r.estaciones if e.nodo == nodo]
        if not filas:
            continue
        resumen["estaciones"][nombre] = {
            "Wq": mean(e.Wq for e in filas),
            "W": mean(e.W for e in filas),
            "Lq": mean(e.Lq for e in filas),
            "L": mean(e.L for e in filas),
            "rho": mean(e.rho for e in filas),
            "bloqueo_medio": mean(e.bloqueo_medio for e in filas),
            "pct_bloqueados": mean(e.pct_bloqueados for e in filas),
        }
    return resumen
