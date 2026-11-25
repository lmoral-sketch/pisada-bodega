# Preguntas probables y cómo responderlas

El enunciado dice dos veces que se evalúa **cómo justifican y defienden** las decisiones. Es
la parte que más pesa y la única que no se puede improvisar.

Las respuestas están con las cifras reales del trabajo. **Todas son verificables en el
repositorio**, y conviene saber dónde está cada una: si alguien duda de un número, abrir el
archivo en pantalla vale más que insistir de memoria.

> **Regla para los cinco:** si no saben una respuesta, díganlo y ofrezcan dónde buscarla. El
> trabajo ya documenta dos errores propios; inventar una respuesta en la defensa es el único
> error que no se puede corregir después.

---

## Sobre el modelo y las distribuciones

### 1. ¿Por qué no usaron exponenciales? Sería más simple.

Porque el enunciado pide explícitamente que el modelo **no sea fácilmente calculable con las
fórmulas del ramo**, y con exponenciales lo sería: tres M/M/s en serie son una red de
Jackson, que se resuelve nodo por nodo con lápiz y papel.

Pero la razón de fondo no es cumplir el requisito, es que **la exponencial no describe estas
tareas**. La exponencial no tiene memoria: implica que un empaque que lleva cinco minutos
tiene la misma probabilidad de terminar en el próximo minuto que uno que recién empieza. En
una tarea estandarizada de cuatro pasos eso es falso. Si lleva cinco minutos, ya va por el
último paso.

### 2. ¿Por qué lognormal en picking y Erlang en las otras dos?

Por la **forma** de cada tarea, no por conveniencia matemática.

**Picking es desplazamiento.** El operario camina a buscar entre uno y varios productos.
Depende de dónde cayeron en la estantería. La mayoría de los pedidos se resuelve cerca de la
media, pero uno con dos productos en pasillos opuestos puede triplicarla. Eso es una cola
derecha larga: lognormal, que es la forma estándar para tiempos de recorrido.

**Empaque y control son secuencias fijas.** Armar la caja, proteger, incluir la guía, sellar:
cuatro sub-tareas parecidas, una después de otra. Eso es exactamente una **Erlang**, que es la
suma de *k* etapas exponenciales. Usamos k=4 en empaque y k=8 en control, donde la tarea es
más repetitiva.

El número de fases no es decorativo: **la Erlang con k fases tiene 1/k de la varianza de una
exponencial de la misma media**. Elegir k es elegir cuánta dispersión tiene la tarea, y eso es
lo que distingue el empaque del control.

### 3. ¿De dónde sacaron los tiempos: 4,5 / 3,2 / 1,8 minutos?

Son **estimaciones razonadas, no mediciones de terreno**, y así está escrito en
`modelo/parametros.py`. No tenemos acceso a una bodega para cronometrar.

Lo que sí hicimos es amarrarlos a la realidad por el lado de la capacidad y del negocio:

- Con 4,5 min y tres pickers, la estación rinde **40 pedidos/hora**
- Con 3,2 min y dos empacadores, **37,5 pedidos/hora**
- Con 1,8 min y un controlador, **33,3 pedidos/hora**

Contra una demanda media de 30 pedidos/hora, eso da utilizaciones de 0,75 · 0,80 · 0,90. Son
cifras de una bodega **real**: una que opera al 30 % estaría sobredimensionada y una al 99 %
no existiría, porque colapsaría con cualquier imprevisto.

> **Si insisten:** reconocer el límite. «Es el supuesto más débil del trabajo. Lo que sí
> podemos defender es que el **comportamiento** del modelo no depende de esos valores exactos:
> E-02 escala la demanda un 60 % y las conclusiones se mantienen.»

### 4. ¿Por qué el buffer es de 5 y no de otro número?

Es el espacio físico de una mesa de despacho: caben unas cinco cajas antes de que no quepa
más. El número exacto importa menos de lo que parece, y **lo demostramos**: en E-03 lo
subimos a 15 y el cumplimiento **no cambió** (92,9 % en ambos casos). Lo único que cambió fue
dónde se forma la cola.

Esa es justamente una conclusión del trabajo, no una debilidad.

---

## Sobre por qué no se puede calcular

### 5. ¿Seguro que no se puede resolver analíticamente? Hay métodos para redes con bloqueo.

Existen aproximaciones, sí, pero ninguna fórmula cerrada del ramo lo resuelve. El modelo
rompe **cuatro supuestos a la vez**, y cada uno por separado ya basta:

| Lo que tenemos | Qué supuesto rompe |
|---|---|
| Servicios lognormal y Erlang | M/M/s y Jackson exigen servicio exponencial |
| λ que cambia cinco veces en el día | Jackson exige tasa constante |
| Buffer finito que bloquea aguas arriba | Los nodos dejan de ser independientes |
| Jornada que abre vacía y cierra | No hay régimen estacionario que calcular |

El cuarto es el más terminante: **las fórmulas describen el equilibrio de largo plazo**, y
nuestra bodega nunca llega ahí. Abre vacía, se llena en la cresta y se vacía al cierre. Lo
que medimos es un transitorio de diez horas.

### 6. Entonces, ¿para qué calcularon ρ = λ/(s·μ)?

Como **referencia**, y lo decimos así en la lámina. Sirve para dos cosas:

1. **Dimensionar antes de simular.** Nos dijo que el control iba a ser el cuello antes de
   escribir una línea de código.
2. **Anunciar el problema.** En la cresta de las 17:00 el control da ρ = 1,14, o sea «la cola
   crece sin límite».

Lo que la fórmula **no** puede decir es cuánto crece en dos horas, qué pasa cuando el bloqueo
se propaga hacia atrás, ni cuánto cuesta eso en pesos. Eso lo responde la simulación. Usamos
las dos herramientas para lo que cada una sirve.

---

## Sobre la simulación

### 7. ¿Cuántas réplicas hicieron y por qué?

Treinta réplicas por escenario, veinte en las pruebas de carga. Cada réplica es **un día
completo** con una semilla distinta.

Reportamos la media y el rango. En el modelo base el cumplimiento va de **88,7 % a 96,2 %**
entre días: esa dispersión es parte del resultado, no ruido que haya que esconder.

> Esto viene del Trabajo 1, donde publicamos como confirmado un hallazgo medido **una sola
> vez** y al repetirlo tres veces no se reprodujo. Por eso el `AGENTS.md` de este repositorio
> obliga a replicar siempre.

### 8. ¿Por qué no descartaron un período de calentamiento?

Porque **el transitorio no es ruido aquí: es el fenómeno**.

El calentamiento se descarta cuando uno quiere estimar el régimen estacionario de un sistema
que corre continuo. Nuestra bodega abre vacía todos los días y cierra vaciándose. Si
descartáramos la primera hora estaríamos tirando a la basura justo lo que queremos medir.

La forma correcta en un sistema así es **replicar días**, que es lo que hacemos.

### 9. ¿Cómo sabemos que la simulación está bien hecha?

Tres verificaciones:

1. **La ley de Little cierra.** `L = λ·W` y `Lq = λ·Wq` se calculan en `simular.py` a partir
   de las observaciones y son consistentes con los tiempos medidos.
2. **La utilización observada coincide con la teórica** donde el modelo se parece al caso
   simple: picking da 0,74 observado contra 0,75 teórico.
3. **El comportamiento responde como debe** al escalar la carga: tiempos que crecen de forma
   no lineal y utilización que se aplana, que es la firma de la saturación.

Y encontramos dos errores propios en el camino, documentados en `logs/prompts.md`: la
conversión de parámetros de la lognormal y un horizonte mal pasado que hacía entrar pedidos
después del cierre. Los dos aparecieron **porque verificamos**.

---

## Sobre los resultados y las mejoras

### 10. El cuello es el control. ¿No era obvio desde el principio?

Que el control fuera el más cargado, sí: ρ = 0,90 teórico lo anticipaba. **Lo que no era
obvio era el resto.**

Lo que la simulación mostró y la intuición no: el **empaque** es la estación que se ve
sufrir, porque queda bloqueada en 9,8 % de los pedidos. Un jefe de bodega mirando el piso
vería al empacador detenido con una caja en la mano y pediría más espacio. Nosotros probamos
esa hipótesis: **agrandar la mesa de 5 a 15 no mejora el cumplimiento ni un punto.**

El bloqueo baja de 9,8 % a 0,4 %, sí. Pero la cola no desaparece: se traslada. El `Wq` del
control sube de 3,84 a 5,19 minutos. Atacamos el síntoma y el sistema no mejoró.

### 11. ¿Por qué pusieron un escenario que no sirve, el del tercer empacador?

A propósito, **como control experimental**. Queríamos mostrar qué pasa al reforzar una
estación que no es el cuello.

El resultado: el cumplimiento sube 0,4 puntos y el bloqueo **se triplica**, de 9,8 % a 26,1 %.
Alimenta más rápido una estación que no puede absorberlo. Cuesta un sueldo completo y empeora
la operación.

Es el escenario más barato de simular y el más caro de descubrir en la realidad.

### 12. ¿Por qué el turno escalonado y no contratar a alguien completo?

Porque logra **prácticamente lo mismo por menos**:

| | Cumplimiento | Costo mensual |
|---|---|---|
| Base | 92,9 % | $12.986.667 |
| Jornada completa en control | 95,1 % | $14.214.444 |
| Refuerzo 14:00–19:00 + mesa | **95,1 %** | **$13.907.500** |

Mismo cumplimiento, **$306.944 menos al mes**. Y hay un argumento mejor que el costo: con
jornada completa el `ρ` del control cae a **0,44**. Esa persona estaría ociosa más de la mitad
del día. La demanda tiene cresta; la capacidad debería tenerla también.

### 13. Si la utilidad sube cuando crecen los pedidos aunque el servicio empeore, ¿no conviene saturarse?

Esta es la pregunta más incómoda y la tenemos contestada.

En E-02, con el costo de atraso que supusimos, el resultado neto **sigue subiendo** hasta 482
pedidos/día aunque el cumplimiento caiga a 67 %. Leído literalmente, el modelo recomienda
degradar el servicio.

Eso **no es una conclusión del trabajo: es una señal de que el supuesto está mal**. Un cliente
cuyo pedido llega tarde no cuesta $3.500 una vez; deja de comprar. Nuestro modelo no captura
la pérdida de clientes futuros.

Por eso no defendemos el número. Lo convertimos en pregunta: **¿desde qué costo de atraso
conviene cada mejora?** El refuerzo en la cresta se paga solo si un despacho tardío cuesta más
de **$5.241**. Ese es el número sobre el que la empresa decide, y no depende de nuestro
supuesto.

### 14. ¿Por qué el límite de servicio da 242 pedidos si hoy procesan 300?

Porque son dos cosas distintas, y distinguirlas es uno de los resultados.

- **Límite de servicio: 242 pedidos/día.** El último volumen con 95 % de cumplimiento.
- **Hoy: 300 pedidos/día con 92,9 %.** Ya están por sobre ese límite.
- **Saturación: ~482 pedidos/día.** La bodega sigue procesando todo, pero con 67 % a tiempo.

O sea: **la bodega puede con el doble de lo que alcanza a despachar a tiempo**. Esa distancia
es el margen real de maniobra, y solo se ve midiendo las dos cosas por separado.

---

## Sobre la economía

### 15. ¿De dónde salen los $6.000 de margen por pedido?

Es el **margen logístico**: lo que queda del ticket de $75.000 después del costo del producto,
la comisión de la pasarela, el marketing y el envío. Es lo que la operación de bodega tiene
que cubrir, no el margen bruto del negocio.

Con eso la bodega cuesta **$1.665 por pedido** y el punto de equilibrio está en **68 pedidos
diarios**. Operan a 300: el negocio cierra con holgura, que es lo que el enunciado pide.

### 16. ¿Por qué 6 operarios y no otra dotación?

Porque es la mínima que sostiene la demanda sin que ninguna estación quede sobre ρ = 1 en
promedio. Con un picker menos la primera estación daría 26,7 pedidos/hora contra una demanda
de 30: la cola crecería sin parar y la bodega nunca cerraría el día.

Es la dotación ajustada, no una holgada. Por eso la cresta de la tarde la quiebra.

---

## Preguntas de cierre

### 17. ¿Qué harían distinto si tuvieran más tiempo?

Tres cosas, en orden de importancia:

1. **Medir los tiempos de servicio en terreno** en vez de estimarlos. Es el supuesto más
   débil.
2. **Modelar el reproceso**: pedidos que vuelven de control a empaque por un error. Hoy el
   flujo es solo hacia adelante, y en una bodega real hay retorno.
3. **Modelar el ausentismo.** Un operario menos un lunes cualquiera probablemente importa más
   que todas las mejoras que evaluamos.

### 18. ¿Qué aprendieron?

Que **la estación que se ve sufrir no es la que hay que arreglar**. El empaque se veía
bloqueado, y la causa estaba una estación más adelante. Agrandar la mesa habría sido la
decisión natural y no habría servido de nada.

Y que la simulación permite equivocarse barato: probamos cinco intervenciones en minutos, dos
no funcionaron, y ninguna costó un sueldo real.

---

## Las tres cifras que todos deberían saber de memoria

| | |
|---|---|
| Cumplimiento actual | **92,9 %** |
| Cumplimiento con la mejora | **95,1 %**, por $920.833 al mes |
| Desde cuándo se paga sola | Si un atraso cuesta más de **$5.241** |
