"""
Parámetros del modelo y su justificación.

Unidad de tiempo: **minutos**. Toda tasa está expresada por minuto y todo
tiempo de servicio en minutos. La jornada de bodega es de 600 minutos.

Este módulo no simula nada: concentra los supuestos para que cada número del
trabajo tenga un solo origen y pueda defenderse. Cambiar un parámetro acá lo
cambia en todos los experimentos.
"""

from dataclasses import dataclass
import math

# ─────────────────────────────────────────────────────────────────────────────
# Jornada
# ─────────────────────────────────────────────────────────────────────────────

APERTURA = 9.0          # 09:00
CIERRE = 19.0           # 19:00
JORNADA_MIN = (CIERRE - APERTURA) * 60      # 600 minutos
DIAS_HABILES_MES = 26                        # lunes a sábado

# ─────────────────────────────────────────────────────────────────────────────
# Demanda: perfil horario de pedidos liberados a preparación
# ─────────────────────────────────────────────────────────────────────────────
#
# Los pedidos de un comercio electrónico NO llegan a tasa constante. Se liberan
# a preparación en dos crestas: una a media mañana, cuando se procesa lo
# acumulado durante la noche, y otra a última hora, antes del corte del courier.
#
# Estos tramos son el primer motivo por el que el modelo no es una red de
# Jackson: Jackson exige llegadas de Poisson **homogéneas**.

TRAMOS = [
    # (hora_inicio, hora_fin, pedidos_por_hora, por qué)
    (9, 11, 24, "Se libera lo acumulado durante la noche, a ritmo moderado"),
    (11, 13, 33, "Cresta de media mañana: compras matinales ya pagadas"),
    (13, 14, 20, "Colación; se reduce la liberación para no acumular cola"),
    (14, 17, 30, "Régimen de tarde, el tramo más estable"),
    (17, 19, 38, "Cresta previa al corte del courier de las 19:00"),
]

PEDIDOS_DIA = sum(ph * (f - i) for i, f, ph, _ in TRAMOS)      # 300
LAMBDA_PROMEDIO_HORA = PEDIDOS_DIA / (JORNADA_MIN / 60)        # 30,0 pedidos/h
LAMBDA_PICO_HORA = max(ph for _, _, ph, _ in TRAMOS)           # 38 pedidos/h

# Expresado como Ciw los necesita: tasas por minuto y cortes en minutos
# contados desde la apertura.
TASAS_POR_MINUTO = [ph / 60 for _, _, ph, _ in TRAMOS]
CORTES_MINUTO = [(f - APERTURA) * 60 for _, f, _, _ in TRAMOS]


# ─────────────────────────────────────────────────────────────────────────────
# Estaciones
# ─────────────────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class Estacion:
    nombre: str
    servidores: int
    media_min: float
    familia: str
    justificacion: str


PICKING = Estacion(
    nombre="Picking",
    servidores=3,
    media_min=4.5,
    familia="lognormal",
    justificacion=(
        "Un operario recorre la bodega y recoge los SKU del pedido. El tiempo "
        "lo domina el desplazamiento, que depende de dónde caiga cada producto "
        "en la estantería, y de cuántas líneas traiga el pedido (1,4 en "
        "promedio). Es una suma de trayectos con cola derecha larga: un pedido "
        "con dos productos en pasillos opuestos puede triplicar la media. La "
        "lognormal es la forma estándar para tiempos de recorrido y no tiene "
        "la propiedad de falta de memoria de la exponencial."
    ),
)

# Desviación observable del picking, en minutos. Determina cuán pesada es la
# cola de la distribución.
PICKING_SD_MIN = 1.8

EMPAQUE = Estacion(
    nombre="Empaque",
    servidores=2,
    media_min=3.2,
    familia="erlang",
    justificacion=(
        "Armar la caja, proteger el producto, incluir la guía y sellar. Es una "
        "secuencia fija de cuatro sub-tareas de duración parecida, sin "
        "variabilidad de recorrido. Una Erlang con k=4 fases modela "
        "exactamente eso: suma de cuatro etapas exponenciales. Su varianza es "
        "la cuarta parte de la de una exponencial de la misma media, que es lo "
        "que se espera de una tarea estandarizada."
    ),
)
EMPAQUE_FASES = 4

CONTROL = Estacion(
    nombre="Control y etiquetado",
    servidores=1,
    media_min=1.8,
    familia="erlang",
    justificacion=(
        "Verificar el contenido contra el pedido, pesar y pegar la etiqueta "
        "del courier. Es la tarea más repetitiva de la línea y la de menor "
        "dispersión: una Erlang con k=8 fases se acerca a un tiempo casi "
        "determinista, conservando algo de variabilidad por los pedidos que "
        "requieren corrección."
    ),
)
CONTROL_FASES = 8

ESTACIONES = (PICKING, EMPAQUE, CONTROL)

# ─────────────────────────────────────────────────────────────────────────────
# Buffer con bloqueo
# ─────────────────────────────────────────────────────────────────────────────
#
# La mesa de despacho entre empaque y control tiene espacio físico para cinco
# cajas en espera. Cuando se llena, el operario de empaque que termina una caja
# **no puede soltarla** y queda bloqueado: deja de servir aunque tenga pedidos
# esperando.
#
# Ciw define la capacidad de un nodo como `queue_capacity + número de
# servidores`. Con capacidad de cola 5 y un servidor, el control admite 6
# pedidos antes de bloquear aguas arriba.
#
# Este bloqueo es el tercer motivo por el que el modelo no es analíticamente
# tratable: acopla las estaciones y rompe la independencia entre nodos.

CAPACIDAD_COLA_CONTROL = 5

# ─────────────────────────────────────────────────────────────────────────────
# Compromiso de servicio
# ─────────────────────────────────────────────────────────────────────────────
#
# El courier retira a las 19:00. Un pedido liberado a preparación debe salir
# el mismo día: si su control termina después del cierre, incumple.

SLA_MIN = JORNADA_MIN

# ─────────────────────────────────────────────────────────────────────────────
# Economía
# ─────────────────────────────────────────────────────────────────────────────
#
# El enunciado pide que los parámetros hagan viable el negocio. Los montos
# están en pesos chilenos y corresponden a una operación de comercio
# electrónico de calzado de tamaño medio.

TICKET_PROMEDIO = 75_000
# Margen que queda después del costo del producto, la comisión de la pasarela,
# el marketing y el envío. Es lo que la operación de bodega debe cubrir.
MARGEN_LOGISTICO_POR_PEDIDO = 6_000

# Costo empresa de un operario de bodega: sueldo bruto más leyes sociales.
SUELDO_OPERARIO_MES = 850_000
HORAS_OPERARIO_MES = 180
COSTO_OPERARIO_HORA = SUELDO_OPERARIO_MES / HORAS_OPERARIO_MES   # ≈ 4.722

ARRIENDO_BODEGA_MES = 2_500_000
INSUMOS_POR_PEDIDO = 400            # caja, relleno, cinta, etiqueta

# Costo de una hora extra: recargo legal del 50 %.
RECARGO_HORA_EXTRA = 1.5


def operarios_totales(picking=None, empaque=None, control=None) -> int:
    """Dotación total de la línea."""
    return (
        (PICKING.servidores if picking is None else picking)
        + (EMPAQUE.servidores if empaque is None else empaque)
        + (CONTROL.servidores if control is None else control)
    )


def parametros_lognormal(media: float, desviacion: float) -> tuple[float, float]:
    """
    Convierte la media y la desviación **observadas** a los parámetros (mu,
    sigma) de la normal subyacente, que es lo que `ciw.dists.Lognormal` espera.

    Es un detalle fácil de equivocar: pasarle directamente 4,5 y 1,8 produciría
    tiempos con media 97 minutos en vez de 4,5.
    """
    sigma2 = math.log(1 + (desviacion ** 2) / (media ** 2))
    mu = math.log(media) - sigma2 / 2
    return mu, math.sqrt(sigma2)


def capacidad_estacion_por_hora(estacion: Estacion, servidores: int | None = None) -> float:
    """Pedidos por hora que la estación puede terminar si nunca está ociosa."""
    s = estacion.servidores if servidores is None else servidores
    return s * (60.0 / estacion.media_min)


def utilizacion_teorica(estacion: Estacion, lambda_hora: float,
                        servidores: int | None = None) -> float:
    """
    rho = lambda / (s * mu). Es una **referencia**, no un resultado: ignora el
    bloqueo y la variabilidad de las llegadas, que es justamente lo que la
    simulación sí captura.
    """
    return lambda_hora / capacidad_estacion_por_hora(estacion, servidores)
