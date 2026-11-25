# Bodega Pisada — simulación de una red de colas

Trabajo 2 del ramo **INFB8091 — Desempeño de Sistemas** (UTEM, 2º semestre 2026).
Profesor: Javier Aranda.

Simulación con **[Ciw](https://github.com/CiwPython/Ciw)** del centro de distribución que
prepara los pedidos de [Pisada](https://github.com/lmoral-sketch/pisada), la tienda del
Trabajo 1. El objeto de estudio es la **red de colas**, no la tienda.

**Integrantes:**

| # | Nombre |
|---|---|
| 1 | Catalina Emilia Araniz Arancibia |
| 2 | Gabriel Ignacio Araya López |
| 3 | Bianca Paola Torres Rivadeneira |
| 4 | Lucas Ángel Mora Loiza |
| 5 | Matías Torres Estay |

---

## El sistema

```
                    λ(t) no homogénea
                          │
                          ▼
   ┌──────────────┐   ┌──────────────┐   ┌──────────────────┐
   │  1. Picking  │──▶│  2. Empaque  │──▶│   3. Control y   │──▶ despacho
   │     s = 3    │   │     s = 2    │   │    etiquetado    │
   │  Lognormal   │   │  Erlang k=4  │   │     s = 1        │
   │   4,5 min    │   │   3,2 min    │   │  Erlang k=8      │
   └──────────────┘   └──────────────┘   │    1,8 min       │
                            ▲            │  cola máx. 5     │
                            └────────────┤  ← bloquea       │
                              bloqueo    └──────────────────┘
```

**Tres colas en serie** (el enunciado pide dos) y **picking con s = 3** (pide al menos una
estación con tres o más servidores).

## Por qué no se resuelve con las fórmulas del ramo

El enunciado exige que el modelo no sea fácilmente calculable. Lo es por **cuatro razones
independientes**, cada una suficiente por sí sola:

| # | Qué rompe | Qué supuesto invalida |
|---|---|---|
| 1 | Ningún servicio es exponencial: lognormal y dos Erlang | Las fórmulas M/M/s y la red de Jackson exigen servicio exponencial |
| 2 | Llegadas de Poisson **no homogéneas**, por tramos horarios | Jackson exige tasa de llegada constante |
| 3 | **Buffer finito con bloqueo** entre empaque y control | Acopla las estaciones: ya no son independientes |
| 4 | Retiro del courier en ventanas discretas, no en flujo continuo | No hay régimen estacionario que calcular |

La utilización teórica `ρ = λ/(s·μ)` se calcula igual, pero solo como **referencia**: anuncia
que el control supera ρ = 1 en la cresta de las 17:00 y nada más. Cuánto crece la cola en esas
dos horas, y qué pasa cuando el bloqueo se propaga hacia atrás, solo lo responde la simulación.

---

## Resultados

Día típico de **300 pedidos**, 30 réplicas:

| Estación | Wq (min) | W (min) | Lq | L | ρ | Bloqueo |
|---|---|---|---|---|---|---|
| Picking | 2,56 | 7,01 | 1,28 | 3,50 | 0,74 | — |
| Empaque | 4,02 | 7,35 | 1,96 | 3,57 | 0,78 | **9,8 %** |
| Control | 3,84 | 5,64 | 1,84 | 2,69 | **0,86** | — |

Tiempo total del pedido: **20,0 min** de media, **38,6 min** en el p(95).
Cumplimiento del compromiso de despacho del mismo día: **92,9 %**.

### Los tres hallazgos

**1. El cuello es el control, y el bloqueo del empaque es su síntoma.**
El empaque queda bloqueado en uno de cada diez pedidos porque la mesa de despacho se llena.
Es tentador concluir que falta espacio.

**2. Agrandar la mesa no sirve de nada.**
Pasarla de 5 a 15 cajas elimina casi todo el bloqueo (9,8 % → 0,4 %) y **no mejora el
cumplimiento ni un punto**. La cola no desaparece: se traslada. `Wq` del control sube de 3,84
a 5,19 minutos. Es gratis y vale la pena hacerlo, pero por higiene operativa, no por
desempeño.

**3. Reforzar donde no está el cuello empeora las cosas.**
Un tercer operario en empaque sube el cumplimiento 0,4 puntos y **triplica el bloqueo**, de
9,8 % a 26,1 %: alimenta más rápido una estación que no puede absorberlo.

### Límites de capacidad

| Límite | Valor | Qué significa |
|---|---|---|
| De servicio | ~242 pedidos/día | El último volumen con 95 % de cumplimiento |
| De saturación | ~450 pedidos/día | El throughput deja de crecer; la cola ya no se vacía |

La bodega **procesa** mucho más de lo que alcanza a despachar **a tiempo**. Esa distancia es
el margen real de maniobra.

### La mejora propuesta

Reforzar el control con un segundo operario **solo entre las 14:00 y las 19:00**, y agrandar
la mesa de despacho:

| | Base | Propuesta |
|---|---|---|
| Cumplimiento | 92,9 % | **95,1 %** |
| Tiempo medio | 20,0 min | **16,5 min** |
| Bloqueo en empaque | 9,8 % | **0,0 %** |
| Costo operativo | $12.986.667 | $13.907.500 |

Y hay un segundo efecto, que es el argumento más fuerte: al repetir el barrido de carga con
la mejora aplicada, **el límite de servicio pasa de 242 a 302 pedidos/día, un 25 % más**. Esos
60 pedidos diarios adicionales aportan **$8.772.400** de margen al mes contra **$942.153** de
costo. El retorno viene del crecimiento que habilita, no del ahorro en atrasos, así que no
depende del supuesto de cuánto cuesta un despacho tardío.

Cuesta **$920.833 al mes** y evita **176 despachos tardíos**. Se financia sola si un despacho
tardío le cuesta a la empresa más de **$5.241**. Contratar a la misma persona la jornada
completa logra casi lo mismo y necesita que el atraso cueste $7.062: la ventaja del turno
escalonado es pagar capacidad solo en las horas que hacen falta.

---

## Cómo ejecutarlo

```bash
python -m venv .venv && .venv/Scripts/activate
```

```bash
pip install -r requirements.txt
```

```bash
python experimentos/e01_base.py
```

Los tres experimentos, en orden:

| Script | Qué responde |
|---|---|
| `experimentos/e01_base.py` | ¿Cómo se comporta la bodega hoy y dónde está el cuello? |
| `experimentos/e02_carga.py` | ¿Hasta dónde aguanta? |
| `experimentos/e03_mejoras.py` | ¿Qué mejora conviene, y desde qué costo se paga sola? |
| `experimentos/e04_limite_mejorado.py` | ¿Hasta dónde aguanta **después** de la mejora? |
| `experimentos/g00_graficos.py` | Genera los gráficos de la presentación |
| `experimentos/g01_presentacion.py` | Genera `docs/presentacion.html` desde los resultados |

Los resultados quedan en `resultados/` en formato JSON.

## Estructura

```
bodega/
├── modelo/
│   ├── parametros.py   Todos los supuestos, con su justificación
│   ├── red.py          Construcción de la red en Ciw
│   ├── simular.py      Ejecución y extracción de W, Wq, L, Lq, ρ
│   └── economia.py     Costos, utilidad y punto de equilibrio
├── experimentos/       Los tres experimentos
├── resultados/         Salidas en JSON
├── docs/
│   ├── presentacion.html   17 láminas, generadas desde los resultados
│   ├── defensa.md          Preguntas probables del profesor y cómo responderlas
│   └── graficos/           Los cinco gráficos
└── logs/prompts.md     Registro de prompts exigido por el enunciado
```

## Nota sobre el uso de agentes de IA

Desarrollado con **Claude Code**, siguiendo las reglas de [`AGENTS.md`](AGENTS.md). El
registro completo de prompts está en [`logs/prompts.md`](logs/prompts.md), con fecha, modelo,
prompt, cambios y **defectos conocidos**.
