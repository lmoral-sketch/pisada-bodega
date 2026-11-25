"""
La dimensión económica del modelo.

El enunciado pide que los parámetros hagan factible el negocio. Este módulo
traduce una configuración de la bodega a pesos: cuánto cuesta operarla, cuánto
deja cada pedido y cuál es el punto en que deja de convenir.
"""

from dataclasses import dataclass

from . import parametros as p


@dataclass
class Costos:
    operarios: int
    horas_extra_dia: float
    sueldos_mes: int
    arriendo_mes: int
    insumos_mes: int
    total_mes: int
    costo_por_pedido: float


@dataclass
class Resultado:
    pedidos_mes: int
    margen_mes: int
    costos: Costos
    utilidad_mes: int
    margen_sobre_ventas: float
    pedidos_equilibrio_dia: float


def costos_mensuales(operarios: int, pedidos_dia: float,
                     horas_extra_dia: float = 0.0) -> Costos:
    """
    Costo mensual de operar la bodega con esa dotación.

    Las horas extra se pagan con el recargo legal del 50 %.
    """
    horas_normales = operarios * (p.JORNADA_MIN / 60) * p.DIAS_HABILES_MES
    sueldos = horas_normales * p.COSTO_OPERARIO_HORA
    extras = (horas_extra_dia * p.DIAS_HABILES_MES
              * p.COSTO_OPERARIO_HORA * p.RECARGO_HORA_EXTRA)
    pedidos_mes = pedidos_dia * p.DIAS_HABILES_MES
    insumos = pedidos_mes * p.INSUMOS_POR_PEDIDO
    total = sueldos + extras + p.ARRIENDO_BODEGA_MES + insumos
    return Costos(
        operarios=operarios,
        horas_extra_dia=horas_extra_dia,
        sueldos_mes=round(sueldos + extras),
        arriendo_mes=p.ARRIENDO_BODEGA_MES,
        insumos_mes=round(insumos),
        total_mes=round(total),
        costo_por_pedido=total / pedidos_mes if pedidos_mes else float("inf"),
    )


def evaluar(operarios: int, pedidos_dia: float,
            horas_extra_dia: float = 0.0) -> Resultado:
    """Cuenta completa del mes para una configuración dada."""
    pedidos_mes = round(pedidos_dia * p.DIAS_HABILES_MES)
    margen = pedidos_mes * p.MARGEN_LOGISTICO_POR_PEDIDO
    c = costos_mensuales(operarios, pedidos_dia, horas_extra_dia)

    # Punto de equilibrio: cuántos pedidos diarios hacen falta para que el
    # margen cubra el costo. Los insumos escalan con el volumen, así que el
    # margen *neto de insumos* es lo que amortiza los costos fijos.
    margen_neto = p.MARGEN_LOGISTICO_POR_PEDIDO - p.INSUMOS_POR_PEDIDO
    fijos = c.total_mes - c.insumos_mes
    equilibrio_dia = (fijos / margen_neto) / p.DIAS_HABILES_MES

    return Resultado(
        pedidos_mes=pedidos_mes,
        margen_mes=margen,
        costos=c,
        utilidad_mes=margen - c.total_mes,
        margen_sobre_ventas=(margen - c.total_mes) / (pedidos_mes * p.TICKET_PROMEDIO),
        pedidos_equilibrio_dia=equilibrio_dia,
    )


def costo_de_incumplir(pedidos_dia: float, cumplimiento_sla: float,
                       costo_por_atraso: int = 3_500) -> int:
    """
    Lo que cuesta al mes que un pedido salga al día siguiente.

    `costo_por_atraso` es el valor asignado a un despacho tardío: reclamos,
    reenvíos y la fracción de clientes que no vuelve. Es un supuesto, y como
    tal se declara: el análisis se presenta también como sensibilidad.
    """
    atrasados_mes = pedidos_dia * (1 - cumplimiento_sla / 100) * p.DIAS_HABILES_MES
    return round(atrasados_mes * costo_por_atraso)


def pesos(n: float) -> str:
    """Formato chileno: $1.234.567"""
    return "$" + f"{round(n):,}".replace(",", ".")
