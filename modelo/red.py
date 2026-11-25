"""
Construcción de la red de colas en Ciw.

Tres estaciones en serie:

    pedidos ──> [1] Picking ──> [2] Empaque ──> [3] Control ──> despacho
                  s=3            s=2             s=1
                                              cola máx. 5
                                              (bloquea a empaque)
"""

import ciw

from . import parametros as p


def _dist_picking():
    mu, sigma = p.parametros_lognormal(p.PICKING.media_min, p.PICKING_SD_MIN)
    return ciw.dists.Lognormal(mean=mu, sd=sigma)


def _dist_empaque():
    return ciw.dists.Erlang(rate=p.EMPAQUE_FASES / p.EMPAQUE.media_min,
                            num_phases=p.EMPAQUE_FASES)


def _dist_control():
    return ciw.dists.Erlang(rate=p.CONTROL_FASES / p.CONTROL.media_min,
                            num_phases=p.CONTROL_FASES)


def distribucion_llegadas(factor: float = 1.0, horizonte: float | None = None):
    """
    Llegadas de Poisson **no homogéneas**, por tramos horarios.

    `factor` escala toda la demanda a la vez: es la palanca de las pruebas de
    carga. Con 1,0 es el día típico de 300 pedidos.
    """
    horizonte = p.JORNADA_MIN if horizonte is None else horizonte
    return ciw.dists.PoissonIntervals(
        rates=[t * factor for t in p.TASAS_POR_MINUTO],
        endpoints=list(p.CORTES_MINUTO),
        max_sample_date=horizonte,
    )


def construir_red(
    factor_demanda: float = 1.0,
    servidores_picking: int | None = None,
    servidores_empaque: int | None = None,
    servidores_control=None,
    capacidad_cola_control: int | None = None,
    horizonte: float | None = None,
):
    """
    Devuelve la red de Ciw.

    `servidores_control` acepta un entero o un `ciw.Schedule`, que es como se
    modela el turno escalonado de la propuesta de mejora.
    """
    s_pick = p.PICKING.servidores if servidores_picking is None else servidores_picking
    s_emp = p.EMPAQUE.servidores if servidores_empaque is None else servidores_empaque
    s_ctrl = p.CONTROL.servidores if servidores_control is None else servidores_control
    cap = (p.CAPACIDAD_COLA_CONTROL if capacidad_cola_control is None
           else capacidad_cola_control)

    return ciw.create_network(
        arrival_distributions=[
            distribucion_llegadas(factor_demanda, horizonte),
            None,      # nadie entra directo a empaque
            None,      # nadie entra directo a control
        ],
        service_distributions=[_dist_picking(), _dist_empaque(), _dist_control()],
        number_of_servers=[s_pick, s_emp, s_ctrl],
        queue_capacities=[float("inf"), float("inf"), cap],
        routing=ciw.routing.NetworkRouting(
            routers=[
                ciw.routing.Direct(to=2),
                ciw.routing.Direct(to=3),
                ciw.routing.Leave(),
            ]
        ),
    )


def turno_escalonado(base: int, refuerzo: int, desde_min: float, hasta_min: float,
                     horizonte: float | None = None):
    """
    Un `ciw.Schedule` con `base` servidores, que sube a `refuerzo` entre
    `desde_min` y `hasta_min`, y vuelve a `base` hasta el final del horizonte.

    Sirve para la mejora: reforzar el control solo en la cresta de la tarde, en
    vez de contratar a alguien la jornada completa.

    El horizonte se cubre por completo a propósito. Ciw repite el calendario de
    forma cíclica cuando la simulación excede el último corte, y eso habría
    hecho reaparecer el refuerzo después del cierre, inflando el resultado.
    """
    horizonte = p.JORNADA_MIN * 1.6 if horizonte is None else horizonte
    numeros, cortes = [], []
    if desde_min > 0:
        numeros.append(base)
        cortes.append(desde_min)
    numeros.append(refuerzo)
    cortes.append(hasta_min)
    if hasta_min < horizonte:
        numeros.append(base)
        cortes.append(horizonte)
    return ciw.Schedule(numbers_of_servers=numeros, shift_end_dates=cortes)
