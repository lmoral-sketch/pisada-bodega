# Registro de prompts

Exigido por el enunciado del Trabajo 2: *«El detalle de prompts usados para resolver el
trabajo»*. El formato sigue el del repositorio de ejemplo del profesor
(`github.com/jabtools/tiempo`), con dos campos propios: **defectos conocidos** y **propuestas
no aprobadas**.

---

## 2026-11-25 | agente: Claude Code (claude-opus-5)

- **Prompt:** «tengo que hacer un segundo trabajo, tiene que ver con la materia que hemos
  hablado te mandare el enunciado y los modulos que tengo disponible en canvas» + el PDF del
  enunciado y las capturas de los módulos de Canvas.
- **Cambios:** lectura del enunciado y contraste con el material del ramo ya digerido en
  `NOTAS.md`. Se extrajeron los requisitos duros: dos colas en serie, una estación con s ≥ 3,
  modelo no calculable con las fórmulas del ramo, pruebas de carga para determinar límites,
  mejoras simuladas, y una presentación —no un informe— que expongan los cinco integrantes.
- **Defectos conocidos:** el enunciado remite a una rúbrica que no viene adjunta; se pidió al
  equipo buscarla en Canvas. Tampoco se dispone del «Soporte Práctico de TEORÍA DE COLAS» de
  la Unidad 3, que podría traer ejemplos de Ciw que el profesor espera ver.
- **Propuestas no aprobadas:** ninguna.

## 2026-11-25 | agente: Claude Code (claude-opus-5)

- **Prompt:** elección del proceso a modelar entre cuatro alternativas; se eligió el centro de
  distribución de Pisada.
- **Cambios:** diseño del modelo de tres estaciones en serie y de las cuatro razones por las
  que no es analíticamente tratable.
- **Defectos conocidos:** ninguno en esta etapa.
- **Propuestas no aprobadas:** se descartaron urgencias de un CESFAM, taller de neumáticos y
  cocina de comida rápida. El centro de distribución se eligió porque da continuidad al
  Trabajo 1 y permite derivar los parámetros del catálogo ya construido.

## 2026-11-25 | agente: Claude Code (claude-opus-5)

- **Prompt:** «dale, arma el repo».
- **Cambios:**
  - Repositorio nuevo con entorno virtual, `ciw==3.2.7` y `matplotlib==3.11.2`.
  - `modelo/parametros.py`: jornada, perfil horario de llegadas en cinco tramos, las tres
    estaciones con su distribución y su justificación escrita, buffer con bloqueo, SLA y
    parámetros económicos.
  - `modelo/red.py`: construcción de la red en Ciw y el `Schedule` del turno escalonado.
  - `modelo/simular.py`: ejecución, réplicas y extracción de W, Wq, L, Lq, ρ y bloqueo.
  - `modelo/economia.py`: costos mensuales, utilidad, punto de equilibrio y costo de los
    atrasos.
  - Tres experimentos: modelo base, pruebas de carga y comparación de mejoras.
  - `AGENTS.md`, `README.md` y este registro.
- **Defectos conocidos:**
  - **Dos errores propios detectados y corregidos durante el desarrollo.** Primero,
    `ciw.dists.Lognormal` recibe la media y la desviación de la **normal subyacente**, no las
    observadas: pasarle 4,5 y 1,8 directamente habría producido tiempos de 97 minutos en vez
    de 4,5. Se agregó `parametros_lognormal()` para la conversión. Segundo, el experimento
    E-03 pasaba el horizonte a `replicar()`, lo que hacía que **siguieran entrando pedidos
    después del cierre**: la base daba 60 % de cumplimiento en vez de 93 % y ninguna
    comparación era válida. Se corrigió y se volvió a correr todo.
  - El costo de $3.500 por despacho tardío es un supuesto sin respaldo. En vez de defenderlo,
    E-03 lo trata como variable y calcula desde qué valor cada mejora se financia sola.
  - El modelo no representa ausentismo, errores de picking que obliguen a rehacer el pedido,
    ni quiebres de stock. Son simplificaciones declaradas.
- **Propuestas no aprobadas:** ninguna.

## 2026-11-25 | agente: Claude Code (claude-opus-5)

- **Prompt:** «Sí, ármala» — la presentación, que es el entregable principal del Trabajo 2.
- **Cambios:**
  - `experimentos/g00_graficos.py`: cinco gráficos con la paleta UTEM, con el celeste de la
    Facultad de Ingeniería predominante. Perfil de llegadas, curva de degradación,
    utilización y bloqueo, comparación de escenarios y punto de equilibrio.
  - `experimentos/g01_presentacion.py`: **genera** `docs/presentacion.html`, 15 láminas, en
    vez de escribirlas a mano. Las cifras se leen de `resultados/*.json`, de modo que si un
    experimento cambia la presentación queda al día volviendo a correr el script. Es la regla
    4 de `AGENTS.md` aplicada al entregable: en el Trabajo 1 tres cifras quedaron desfasadas
    por copiarlas entre documentos.
  - Reparto: las quince láminas están asignadas a los cinco integrantes, con el nombre de
    quien expone al pie de cada una, porque el enunciado exige que expongan todos.
  - La presentación cubre los cuatro puntos que el enunciado enumera: el problema, las
    decisiones de diseño, una lámina de evidencia de cumplimiento de los requerimientos, y la
    justificación de supuestos y cálculos.
- **Defectos conocidos:**
  - La fuente Aptos no está instalada en el equipo donde se generaron los gráficos, así que
    matplotlib usó la alternativa. El manual de identidad admite Montserrat como alternativa
    y la presentación HTML sí la carga desde Google Fonts.
  - La `ρ` del encabezado de la tabla se renderizaba como «P» por el `text-transform:
    uppercase`. Corregido excluyendo esos encabezados de la transformación.
  - No se ha incorporado la rúbrica: sigue sin estar disponible. La estructura de la
    presentación sigue el orden en que el enunciado enumera los requisitos, no una
    ponderación.
- **Propuestas no aprobadas:** ninguna.
