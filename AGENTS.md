# AGENTS.md — Bodega Pisada

## Proyecto

Simulación con **Ciw** de la red de colas del centro de distribución que prepara los pedidos
de Pisada. Trabajo 2 de **INFB8091 — Desempeño de Sistemas**, UTEM, 2º semestre 2026.

**El objeto de estudio es la red de colas, no la bodega.** La bodega es el pretexto para
aplicar teoría de colas sobre un proceso con parámetros defendibles.

## Reglas de trabajo

1. **Explicar antes de implementar.** Ningún cambio de modelo se escribe sin decir primero
   qué se va a cambiar y por qué.
2. **Español neutro latinoamericano** en código, comentarios y documentación. Nombres de
   variables y funciones en español.
3. **Leer `logs/prompts.md` al iniciar sesión**, para no repetir trabajo ni contradecir
   decisiones ya tomadas.
4. **Un parámetro, un solo lugar.** Todo supuesto numérico vive en `modelo/parametros.py`.
   Está prohibido escribir una cifra a mano en un experimento o en la documentación: se
   importa. En el Trabajo 1 tres cifras quedaron desactualizadas por no seguir esta regla.
5. **Todo parámetro lleva su justificación escrita al lado.** Un número sin defensa no entra
   al modelo. El enunciado evalúa explícitamente la justificación.
6. **No agregar dependencias** sin justificarlo. El enunciado exige Ciw; matplotlib es para
   los gráficos de la presentación. Nada más sin discutirlo.
7. **Las comparaciones usan las mismas semillas.** Comparar dos configuraciones con semillas
   distintas mide ruido, no efecto.
8. **Replicar siempre.** Ningún resultado se reporta desde una sola corrida. Se informan la
   media y el rango. Si los rangos se solapan, la conclusión es que **no hay diferencia
   demostrable**, y así se escribe.
9. **Distinguir lo medido de lo supuesto.** `ρ = λ/(s·μ)` es una referencia teórica; lo que
   entrega la simulación es un resultado. No se mezclan en la misma frase sin decirlo.
10. **Verificar antes de dar algo por terminado.** Correr el script y leer la salida. No
    reportar un resultado que no se vio.
11. **Registrar cada prompt** en `logs/prompts.md`, con fecha, modelo, prompt, cambios,
    **defectos conocidos** y **propuestas no aprobadas**.
12. **Los errores propios se documentan, no se borran.** Si un experimento sale mal y hay que
    repetirlo, queda escrito qué falló y por qué.
13. **Preguntar antes de hacer commit** y antes de publicar en GitHub.
14. **Identidad visual UTEM** en la presentación: celeste `#00B6ED` de la Facultad de
    Ingeniería predominante, azul `#004EAA` y verde `#78BF26` institucionales, tipografía
    Aptos o Montserrat.
15. **La unidad de tiempo del modelo es el minuto.** Toda tasa es por minuto, todo tiempo en
    minutos. Si algo se expresa por hora, se dice explícitamente en el nombre o en el
    comentario.

## Defecto conocido del Trabajo 1 que no se repite

Un hallazgo se publicó como confirmado desde **una sola corrida por configuración**, y al
repetirlo tres veces no se reprodujo. De ahí vienen las reglas 7 y 8.
