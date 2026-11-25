"""
Genera `docs/presentacion.html` a partir de los resultados.

Se genera en vez de escribirse a mano por la regla 4 de AGENTS.md: ninguna
cifra se teclea dos veces. Si un experimento cambia, se vuelve a correr esto y
la presentación queda al día sola. En el Trabajo 1 tres cifras quedaron
desfasadas por copiarlas a mano entre documentos.
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from modelo import economia as eco
from modelo import parametros as p

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(RAIZ, "resultados")
SALIDA = os.path.join(RAIZ, "docs", "presentacion.html")

INTEGRANTES = ["Catalina Emilia Araniz Arancibia", "Gabriel Ignacio Araya López",
               "Bianca Paola Torres Rivadeneira", "Lucas Ángel Mora Loiza",
               "Matías Torres Estay"]


def cargar():
    with open(os.path.join(RES, "e01-base.json"), encoding="utf-8") as f:
        e1 = json.load(f)
    with open(os.path.join(RES, "e02-carga.json"), encoding="utf-8") as f:
        e2 = json.load(f)
    with open(os.path.join(RES, "e03-mejoras.json"), encoding="utf-8") as f:
        e3 = json.load(f)
    with open(os.path.join(RES, "e04-limite-mejorado.json"), encoding="utf-8") as f:
        e4 = json.load(f)
    return e1, e2, e3, e4


def num(x, d=1):
    return f"{x:,.{d}f}".replace(",", "@").replace(".", ",").replace("@", ".")


# ─────────────────────────────────────────────────────────────────────────────

CSS = """
  :root { --azul-utem:#004EAA; --verde-utem:#78BF26; --celeste-ing:#00B6ED;
          --tinta:#141414; --suave:#6b6b6b; }
  * { box-sizing:border-box; margin:0; padding:0; }
  body { font-family:Aptos, Montserrat, Arial, Helvetica, sans-serif;
         background:#fff; color:var(--tinta); overflow:hidden; }
  .lamina { position:fixed; inset:0; background:#fff; display:none;
            flex-direction:column; justify-content:center;
            padding:9vh 7vw 11vh; animation:entrar .18s ease; }
  .lamina > .etiqueta { position:absolute; top:5vh; left:7vw; }
  .lamina.activa { display:flex; }
  @keyframes entrar { from{opacity:0} to{opacity:1} }
  .lamina::before { content:''; position:absolute; top:0; left:0; right:0;
                    height:10px; background:var(--celeste-ing); }
  .marca { position:absolute; bottom:3vh; right:7vw; font-size:1.1vw;
           color:var(--suave); letter-spacing:.06em; }
  .numero { position:absolute; bottom:3vh; left:7vw; font-size:1.1vw;
            color:var(--celeste-ing); font-weight:600; }
  .quien { position:absolute; bottom:3vh; left:50%; transform:translateX(-50%);
           font-size:1vw; color:var(--suave); }
  .etiqueta { font-size:1.2vw; font-weight:600; letter-spacing:.12em;
              text-transform:uppercase; color:var(--celeste-ing); margin-bottom:1.6vh; }
  h1 { font-size:3.7vw; font-weight:700; line-height:1.15; color:var(--azul-utem); }
  h2 { font-size:2.9vw; font-weight:700; line-height:1.2; color:var(--azul-utem);
       margin-bottom:2.6vh; }
  p.grande { font-size:1.7vw; font-weight:300; line-height:1.55; color:var(--suave);
             max-width:52vw; }
  ul { list-style:none; font-size:1.55vw; line-height:1.85; }
  li { padding-left:1.5em; position:relative; margin-bottom:.4vh; }
  li::before { content:''; position:absolute; left:0; top:.72em; width:.55em;
               height:.55em; background:var(--verde-utem); border-radius:50%; }
  li strong { color:var(--azul-utem); font-weight:600; }
  li.no::before { background:#c0392b; }
  .portada { justify-content:center; }
  .portada .unidad { font-size:1.3vw; color:var(--suave); line-height:1.6; margin-bottom:3.5vh; }
  .portada .integrantes { font-size:1.2vw; color:var(--suave); line-height:1.8; margin-top:auto; }
  .portada .logo-principal { height:13vh; margin-bottom:3.5vh; }
  .portada .logo-principal img { height:100%; }
  .escudo { position:absolute; top:4vh; right:7vw; height:7vh; opacity:.9; }
  .cifras { display:flex; gap:4vw; margin-top:2vh; }
  .cifra .valor { font-size:3.9vw; font-weight:700; color:var(--celeste-ing); line-height:1; }
  .cifra .rotulo { font-size:1.05vw; color:var(--suave); margin-top:.8vh; max-width:13vw; }
  table { width:100%; border-collapse:collapse; font-size:1.35vw; }
  th { text-align:left; font-size:1vw; text-transform:uppercase; letter-spacing:.08em; }
  th .tal-cual { text-transform:none; font-size:1.15vw; }
  th:not(:first-child) { text-align:right; }
  th:not(.x) { font-size:1vw; letter-spacing:.08em;
       color:var(--celeste-ing); padding-bottom:1.1vh; border-bottom:2px solid var(--celeste-ing); }
  td { padding:1.1vh 0; border-bottom:1px solid #e6e6e6; }
  td:not(:first-child) { text-align:right; font-variant-numeric:tabular-nums; }
  tr.destacada td { font-weight:700; color:var(--azul-utem); }
  .figura { flex:1; display:flex; align-items:center; justify-content:center; padding:1vh 0; }
  .figura img { max-width:100%; max-height:60vh; }
  .cita { font-size:2vw; font-weight:300; line-height:1.5;
          border-left:6px solid var(--verde-utem); padding-left:2vw;
          color:var(--tinta); max-width:62vw; }
  .flujo { display:flex; align-items:center; gap:1.4vw; margin:3vh 0; font-size:1.2vw; }
  .caja { border:3px solid var(--celeste-ing); border-radius:10px; padding:2vh 1.6vw;
          text-align:center; flex:1; }
  .caja .t { font-weight:700; color:var(--azul-utem); font-size:1.5vw; }
  .caja .s { color:var(--verde-utem); font-weight:600; margin:.6vh 0; }
  .caja .d { color:var(--suave); font-size:1vw; }
  .flecha { color:var(--celeste-ing); font-size:2.4vw; font-weight:700; }
  .ayuda { position:fixed; top:2vh; left:50%; transform:translateX(-50%);
           font-size:.85vw; color:#bbb; background:rgba(0,0,0,.55);
           padding:.4em 1em; border-radius:1em; z-index:10; }
"""

JS = """
  const laminas = [...document.querySelectorAll('.lamina')];
  let actual = 0;
  function mostrar(n) {
    actual = Math.max(0, Math.min(laminas.length - 1, n));
    laminas.forEach((l, i) => l.classList.toggle('activa', i === actual));
  }
  document.addEventListener('keydown', (e) => {
    if (['ArrowRight',' ','PageDown'].includes(e.key)) { e.preventDefault(); mostrar(actual+1); }
    if (['ArrowLeft','PageUp'].includes(e.key)) { e.preventDefault(); mostrar(actual-1); }
    if (e.key === 'Home') mostrar(0);
    if (e.key === 'End') mostrar(laminas.length - 1);
  });
  setTimeout(() => { const a = document.querySelector('.ayuda'); if (a) a.style.display='none'; }, 6000);
"""


def lamina(n, total, etiqueta, quien, cuerpo, clase=""):
    activa = " activa" if n == 1 else ""
    return f"""
<section class="lamina{activa} {clase}">
  <div class="etiqueta">{etiqueta}</div>
  {cuerpo}
  <div class="numero">{n:02d} / {total}</div>
  <div class="quien">{quien}</div>
  <div class="marca">Bodega Pisada · INFB8091</div>
  <img class="escudo" src="assets/logo-utem-escudo.png" alt="UTEM">
</section>"""


def construir():
    e1, e2, e3, e4 = cargar()
    r = e1["resumen"]
    est = r["estaciones"]
    economia = e1["economia"]
    pts = e2["puntos"]
    esc = {x["clave"]: x for x in e3["escenarios"]}
    base, mejora = esc["base"], esc["turno_mesa"]

    cumplen = [q for q in pts if q["sla"] >= e2["umbral_sla"]]
    lim_servicio = max(cumplen, key=lambda q: q["factor"])["pedidos_dia"] if cumplen else 0
    lim_sat = max(pts, key=lambda q: q["factor"])["pedidos_dia"]

    pedidos_mes = e3["pedidos_dia"] * p.DIAS_HABILES_MES
    d_costo = mejora["costo_mes"] - base["costo_mes"]
    evitados = pedidos_mes * (mejora["sla"] - base["sla"]) / 100
    equilibrio = d_costo / evitados

    L = []
    T = 17
    import itertools
    num_lamina = itertools.count(2)

    # 1 ── Portada
    L.append(f"""
<section class="lamina activa portada">
  <div class="logo-principal">
    <img src="assets/logo-utem-horizontal.png" alt="Universidad Tecnológica Metropolitana">
  </div>
  <div class="unidad">Universidad Tecnológica Metropolitana<br>
    Facultad de Ingeniería · Departamento de Informática y Computación</div>
  <div class="etiqueta">INFB8091 · Desempeño de Sistemas · Trabajo 2</div>
  <h1>Simulación de la bodega de Pisada<br>como una red de colas</h1>
  <p class="grande" style="margin-top:2.5vh">Modelado con Ciw de un centro de distribución
     de tres estaciones en serie: dónde está el cuello, hasta dónde aguanta y qué mejora
     conviene pagar.</p>
  <div class="integrantes"><strong>Integrantes:</strong> {' · '.join(INTEGRANTES)}<br>
    Profesor: Javier Aranda · Noviembre de 2026</div>
  <div class="numero">01 / {T}</div>
  <div class="marca">Bodega Pisada · INFB8091</div>
</section>""")

    # 2 ── El problema
    L.append(lamina(next(num_lamina), T, "El problema por resolver", "Catalina Araniz", f"""
  <h2>Una bodega que procesa todo,<br>pero no alcanza a despachar a tiempo</h2>
  <p class="grande">Pisada prepara <strong>{p.PEDIDOS_DIA} pedidos al día</strong> con seis
     operarios en tres estaciones. No se pierden pedidos: todos salen. El problema es
     <strong>cuándo</strong> salen.</p>
  <div class="cifras">
    <div class="cifra"><div class="valor">{num(r['sla_medio'])} %</div>
      <div class="rotulo">se despacha el mismo día</div></div>
    <div class="cifra"><div class="valor">{num(100 - r['sla_medio'])} %</div>
      <div class="rotulo">queda para el día siguiente</div></div>
    <div class="cifra"><div class="valor">{eco.pesos(economia['costo_atrasos_mes'])}</div>
      <div class="rotulo">cuesta ese atraso al mes</div></div>
  </div>
  <p class="grande" style="margin-top:3vh">La pregunta no es si contratar a alguien, sino
     <strong>dónde</strong> y <strong>cuándo</strong>.</p>"""))

    # 3 ── El sistema
    L.append(lamina(next(num_lamina), T, "El sistema modelado", "Catalina Araniz", f"""
  <h2>Tres estaciones en serie</h2>
  <div class="flujo">
    <div class="caja"><div class="t">Picking</div><div class="s">s = 3</div>
      <div class="d">Lognormal<br>{num(p.PICKING.media_min)} min</div></div>
    <div class="flecha">→</div>
    <div class="caja"><div class="t">Empaque</div><div class="s">s = 2</div>
      <div class="d">Erlang k={p.EMPAQUE_FASES}<br>{num(p.EMPAQUE.media_min)} min</div></div>
    <div class="flecha">→</div>
    <div class="caja"><div class="t">Control</div><div class="s">s = 1</div>
      <div class="d">Erlang k={p.CONTROL_FASES}<br>{num(p.CONTROL.media_min)} min</div></div>
    <div class="flecha">→</div>
    <div class="caja" style="border-color:var(--verde-utem)"><div class="t">Courier</div>
      <div class="s">19:00</div><div class="d">retiro diario</div></div>
  </div>
  <ul>
    <li>Entre empaque y control hay una <strong>mesa con espacio para
        {p.CAPACIDAD_COLA_CONTROL} cajas</strong>. Cuando se llena, el empaque
        <strong>se bloquea</strong>.</li>
    <li>Las llegadas siguen el <strong>perfil horario</strong> real del comercio: dos crestas,
        no una tasa constante.</li>
  </ul>"""))

    # 4 ── Cumplimiento de requisitos
    L.append(lamina(next(num_lamina), T, "Cumplimiento de los requerimientos", "Catalina Araniz", f"""
  <h2>Lo que el enunciado exige,<br>y dónde está en el trabajo</h2>
  <table>
    <tr><th>Requerimiento</th><th>Dónde se cumple</th></tr>
    <tr><td>Al menos 2 colas en serie</td><td>3 estaciones en serie</td></tr>
    <tr><td>Al menos una cola con s ≥ 3</td><td>Picking, s = 3</td></tr>
    <tr><td>No calculable con las fórmulas del ramo</td><td>4 razones independientes</td></tr>
    <tr><td>Justificar los parámetros de entrada</td><td><code>modelo/parametros.py</code></td></tr>
    <tr><td>Indicadores de colas</td><td>W, W<sub>q</sub>, L, L<sub>q</sub>, ρ por estación</td></tr>
    <tr><td>Carga hasta el límite máximo</td><td>E-02: de 242 a {num(lim_sat, 0)} pedidos/día</td></tr>
    <tr><td>Analizar y proponer mejoras</td><td>E-03: 5 intervenciones</td></tr>
    <tr class="destacada"><td>Simular las mejoras y concluir</td><td>E-03, con punto de equilibrio</td></tr>
  </table>"""))

    # 5 ── Por qué no es calculable
    L.append(lamina(next(num_lamina), T, "Decisión de diseño · la central", "Gabriel Araya", """
  <h2>Por qué no se puede resolver<br>con las fórmulas del ramo</h2>
  <ul>
    <li><strong>Ningún servicio es exponencial.</strong> Una lognormal y dos Erlang. Las
        fórmulas M/M/s y la red de Jackson exigen servicio exponencial.</li>
    <li><strong>Las llegadas no son homogéneas.</strong> Jackson exige tasa constante;
        nuestro λ cambia cinco veces en la jornada.</li>
    <li><strong>El buffer es finito y bloquea.</strong> Eso acopla las estaciones: dejan de
        ser independientes y el producto de las soluciones individuales ya no vale.</li>
    <li><strong>El courier retira en una ventana.</strong> No hay régimen estacionario que
        calcular: el sistema abre vacío y cierra vaciándose.</li>
  </ul>
  <p class="grande" style="margin-top:2.5vh">Cada una basta por sí sola. Calculamos igual
     ρ = λ/(s·μ), pero <strong>solo como referencia</strong>.</p>"""))

    # ── Los parámetros con la notación del ramo ────────────────────────────
    filas_par = "".join(
        f"<tr{' class=\"destacada\"' if f['rho'] >= 0.85 else ''}>"
        f"<td>{f['estacion']}</td><td>{num(f['lambda_hora'])}</td>"
        f"<td>{num(f['mu_hora'])}</td><td>{f['s']}</td>"
        f"<td>{num(f['capacidad_hora'])}</td><td>{num(f['rho'], 2)}</td>"
        f"<td>{num(f['rho_pico'], 2)}</td></tr>"
        for f in p.tabla_parametros())
    L.append(lamina(next(num_lamina), T, "Parámetros de entrada", "Gabriel Araya", f"""
  <h2>Los parámetros, en la notación del ramo</h2>
  <table>
    <tr><th>Estación</th><th><span class="tal-cual">λ</span> (ped/h)</th>
        <th><span class="tal-cual">μ</span> (ped/h)</th><th>s</th>
        <th><span class="tal-cual">s·μ</span></th>
        <th><span class="tal-cual">ρ</span> medio</th>
        <th><span class="tal-cual">ρ</span> cresta</th></tr>
    {filas_par}
  </table>
  <p class="grande" style="margin-top:2.5vh">
     <strong>T = {num(p.T_horizonte_horas(), 0)} horas</strong> de jornada ·
     λ es la misma en las tres porque la red es en serie y sin pérdidas:
     todo lo que entra a picking termina pasando por control.</p>
  <p class="grande">En la cresta el control da <strong>ρ = {num(p.utilizacion_teorica(p.CONTROL, p.LAMBDA_PICO_HORA), 2)}</strong>:
     la fórmula anuncia que la cola crece sin límite. Cuánto crece en dos horas
     lo responde la simulación, no la fórmula.</p>"""))

    # 6 ── Justificación de los servicios
    L.append(lamina(next(num_lamina), T, "Justificación de los supuestos", "Gabriel Araya", f"""
  <h2>De dónde sale cada distribución</h2>
  <ul>
    <li><strong>Picking — lognormal, {num(p.PICKING.media_min)} min.</strong> Lo domina el
        desplazamiento por la bodega. Un pedido con dos productos en pasillos opuestos
        triplica la media: cola derecha larga, sin falta de memoria.</li>
    <li><strong>Empaque — Erlang k={p.EMPAQUE_FASES}, {num(p.EMPAQUE.media_min)} min.</strong>
        Cuatro sub-tareas fijas de duración parecida. Su varianza es la cuarta parte de la de
        una exponencial de igual media, que es lo propio de una tarea estandarizada.</li>
    <li><strong>Control — Erlang k={p.CONTROL_FASES}, {num(p.CONTROL.media_min)} min.</strong>
        La tarea más repetitiva: casi determinista, con algo de variabilidad por los pedidos
        que hay que corregir.</li>
  </ul>
  <p class="grande" style="margin-top:2vh">Detalle: <code>ciw.dists.Lognormal</code> recibe
     los parámetros de la <strong>normal subyacente</strong>. Pasarle la media observada
     habría dado tiempos de 97 minutos en vez de {num(p.PICKING.media_min)}.</p>"""))

    # 7 ── Perfil de llegadas
    L.append(lamina(next(num_lamina), T, "Justificación de los supuestos", "Gabriel Araya", f"""
  <h2>La demanda tiene forma</h2>
  <div class="figura"><img src="graficos/g1-perfil-llegadas.png" alt="Perfil horario"></div>
  <p class="grande">Media de {num(p.LAMBDA_PROMEDIO_HORA, 0)} pedidos/hora, cresta de
     {p.LAMBDA_PICO_HORA}. Usar el promedio habría escondido el problema: el sistema falla
     <strong>en la cresta</strong>, no en el promedio.</p>"""))

    # 8 ── Economía
    L.append(lamina(next(num_lamina), T, "Justificación de los cálculos", "Bianca Torres", f"""
  <h2>El negocio tiene que cerrar</h2>
  <table>
    <tr><th>Concepto</th><th>Al mes</th></tr>
    <tr><td>Margen logístico ({num(pedidos_mes, 0)} pedidos × {eco.pesos(p.MARGEN_LOGISTICO_POR_PEDIDO)})</td>
        <td>{eco.pesos(pedidos_mes * p.MARGEN_LOGISTICO_POR_PEDIDO)}</td></tr>
    <tr><td>Sueldos ({p.operarios_totales()} operarios, costo empresa)</td>
        <td>−{eco.pesos(base['costo_mes'] - p.ARRIENDO_BODEGA_MES - pedidos_mes * p.INSUMOS_POR_PEDIDO)}</td></tr>
    <tr><td>Arriendo de la bodega</td><td>−{eco.pesos(p.ARRIENDO_BODEGA_MES)}</td></tr>
    <tr><td>Insumos de embalaje</td><td>−{eco.pesos(pedidos_mes * p.INSUMOS_POR_PEDIDO)}</td></tr>
    <tr class="destacada"><td>Resultado de la operación</td>
        <td>{eco.pesos(economia['utilidad_mes'])}</td></tr>
  </table>
  <div class="cifras" style="margin-top:3vh">
    <div class="cifra"><div class="valor">{eco.pesos(economia['costo_por_pedido'])}</div>
      <div class="rotulo">cuesta preparar un pedido</div></div>
    <div class="cifra"><div class="valor">{num(economia['equilibrio_dia'], 0)}</div>
      <div class="rotulo">pedidos diarios de equilibrio</div></div>
  </div>"""))

    # 9 ── Resultados base
    L.append(lamina(next(num_lamina), T, "Resultados · modelo base", "Bianca Torres", f"""
  <h2>Los indicadores del día típico</h2>
  <table>
    <tr><th>Estación</th><th><span class="tal-cual">W<sub>q</sub></span></th><th>W</th><th><span class="tal-cual">L<sub>q</sub></span></th>
        <th>L</th><th><span class="tal-cual">ρ</span></th><th>Bloqueo</th></tr>
    <tr><td>Picking</td><td>{num(est['Picking']['Wq'], 2)}</td><td>{num(est['Picking']['W'], 2)}</td>
        <td>{num(est['Picking']['Lq'], 2)}</td><td>{num(est['Picking']['L'], 2)}</td>
        <td>{num(est['Picking']['rho'], 2)}</td><td>—</td></tr>
    <tr><td>Empaque</td><td>{num(est['Empaque']['Wq'], 2)}</td><td>{num(est['Empaque']['W'], 2)}</td>
        <td>{num(est['Empaque']['Lq'], 2)}</td><td>{num(est['Empaque']['L'], 2)}</td>
        <td>{num(est['Empaque']['rho'], 2)}</td>
        <td>{num(est['Empaque']['pct_bloqueados'])} %</td></tr>
    <tr class="destacada"><td>Control</td><td>{num(est['Control']['Wq'], 2)}</td>
        <td>{num(est['Control']['W'], 2)}</td><td>{num(est['Control']['Lq'], 2)}</td>
        <td>{num(est['Control']['L'], 2)}</td><td>{num(est['Control']['rho'], 2)}</td><td>—</td></tr>
  </table>
  <p class="grande" style="margin-top:2.5vh">W<sub>q</sub> y W en minutos · L<sub>q</sub> y L
     en pedidos · {r['replicas']:.0f} réplicas.<br>
     El pedido completo demora <strong>{num(r['tiempo_total_medio'])} min</strong> de media y
     <strong>{num(r['tiempo_total_p95'])} min</strong> en el p(95).</p>"""))

    # 10 ── Pruebas de carga
    L.append(lamina(next(num_lamina), T, "Pruebas de carga · límites máximos", "Matías Torres", f"""
  <h2>Hasta dónde aguanta</h2>
  <div class="figura"><img src="graficos/g2-degradacion.png" alt="Degradación"></div>
  <p class="grande">Límite de servicio <strong>{num(lim_servicio, 0)} pedidos/día</strong>;
     la bodega sigue <em>procesando</em> hasta {num(lim_sat, 0)}. Esa distancia es el margen
     real: se deja de cumplir mucho antes de dejar de poder.</p>"""))

    # 11 ── Dónde está el cuello
    L.append(lamina(next(num_lamina), T, "Análisis", "Matías Torres", """
  <h2>El cuello, y el síntoma que engaña</h2>
  <div class="figura"><img src="graficos/g3-utilizacion.png" alt="Utilización y bloqueo"></div>
  <p class="grande">El control satura primero. El bloqueo del empaque <strong>no es el
     problema</strong>: es el cuello del control propagándose hacia atrás.</p>"""))

    # 12 ── Intervenciones
    L.append(lamina(next(num_lamina), T, "Mejoras simuladas", "Lucas Mora", """
  <h2>Cinco intervenciones, mismas semillas</h2>
  <div class="figura"><img src="graficos/g4-escenarios.png" alt="Escenarios"></div>"""))

    # 13 ── Lo que no sirvió
    L.append(lamina(next(num_lamina), T, "Mejoras simuladas", "Lucas Mora", f"""
  <h2>Lo que no funcionó,<br>y por qué importa</h2>
  <ul>
    <li class="no"><strong>Agrandar la mesa de despacho.</strong> El bloqueo cae de
        {num(base['bloqueo_empaque'])} % a {num(esc['mesa']['bloqueo_empaque'])} % y el
        cumplimiento <strong>no mejora</strong>. La cola no desaparece: se traslada al
        control, cuyo W<sub>q</sub> sube de {num(base['wq_control'], 2)} a
        {num(esc['mesa']['wq_control'], 2)} min.</li>
    <li class="no"><strong>Un tercer operario en empaque.</strong> Sube el cumplimiento
        {num(esc['empaque3']['sla'] - base['sla'])} puntos y <strong>triplica el
        bloqueo</strong>, a {num(esc['empaque3']['bloqueo_empaque'])} %: alimenta más rápido
        una estación que no puede absorberlo.</li>
  </ul>
  <p class="cita" style="margin-top:3vh">Atacar el síntoma visible no mejora el sistema.
     Lo supimos porque lo simulamos, no porque lo supusiéramos.</p>"""))

    # 14 ── Punto de equilibrio
    L.append(lamina(next(num_lamina), T, "La propuesta", "Lucas Mora", f"""
  <h2>Reforzar el control<br>solo en la cresta</h2>
  <div class="figura"><img src="graficos/g5-equilibrio.png" alt="Punto de equilibrio"></div>
  <p class="grande">Cumplimiento {num(base['sla'])} % → <strong>{num(mejora['sla'])} %</strong>,
     bloqueo a cero, por {eco.pesos(d_costo)} al mes. Se paga sola si un despacho tardío
     cuesta más de <strong>{eco.pesos(equilibrio)}</strong>.</p>"""))

    # ── E-04: el límite, después de la mejora ──────────────────────────────
    extra = e4["limite_despues"] - e4["limite_antes"]
    margen_extra = (extra * p.DIAS_HABILES_MES
                    * (p.MARGEN_LOGISTICO_POR_PEDIDO - p.INSUMOS_POR_PEDIDO))
    L.append(lamina(next(num_lamina), T, "Simulación con los nuevos resultados",
                    "Matías Torres", f"""
  <h2>La mejora no solo reduce atrasos:<br>habilita crecer</h2>
  <p class="grande">Se repitió el barrido completo de carga con la configuración propuesta.</p>
  <div class="cifras">
    <div class="cifra"><div class="valor">{num(e4['limite_antes'], 0)}</div>
      <div class="rotulo">pedidos/día con 95 % de cumplimiento, antes</div></div>
    <div class="cifra"><div class="valor">{num(e4['limite_despues'], 0)}</div>
      <div class="rotulo">después de la mejora</div></div>
    <div class="cifra"><div class="valor">+{num(100 * extra / e4['limite_antes'], 0)} %</div>
      <div class="rotulo">de capacidad de servicio</div></div>
  </div>
  <p class="grande" style="margin-top:3vh">Esos {num(extra, 0)} pedidos diarios adicionales
     aportan <strong>{eco.pesos(margen_extra)}</strong> de margen al mes, contra
     {eco.pesos(d_costo)} de costo.</p>
  <p class="cita" style="margin-top:2vh">El retorno viene del crecimiento que habilita, no
     del ahorro en atrasos. Por eso este argumento no depende del supuesto débil.</p>"""))

    # 15 ── Cierre
    L.append(lamina(next(num_lamina), T, "Conclusiones", "Los cinco integrantes", f"""
  <h2>Lo que nos deja el modelo</h2>
  <ul>
    <li><strong>El cuello no era el que se veía.</strong> El bloqueo del empaque era el
        síntoma; la causa estaba una estación más adelante.</li>
    <li><strong>Capacidad y cumplimiento son cosas distintas.</strong> La bodega procesa
        {num(lim_sat, 0)} pedidos/día y solo cumple hasta {num(lim_servicio, 0)}.</li>
    <li><strong>Pagar capacidad por horas, no por jornadas.</strong> El turno escalonado
        logra lo mismo que una contratación completa a {num(100 * d_costo / (esc['control2']['costo_mes'] - base['costo_mes']), 0)} %
        del costo incremental.</li>
    <li><strong>El supuesto débil se convierte en pregunta.</strong> En vez de defender
        cuánto cuesta un atraso, el modelo entrega el valor desde el cual decidir.</li>
  </ul>
  <p class="cita" style="margin-top:3vh">Las fórmulas del ramo dijeron que el control
     superaba ρ = 1 en la cresta. La simulación dijo cuánto cuesta eso en pesos, y qué
     hacer al respecto.</p>"""))

    html = f"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Bodega Pisada — Presentación</title>
<!--
  GENERADO POR experimentos/g01_presentacion.py — no editar a mano.
  Las cifras se leen de resultados/*.json. Si cambia un experimento, volver a
  correr el script y la presentación queda al día.

  CÓMO USARLA
  1. Abrir en el navegador
  2. F11 para pantalla completa
  3. Avanzar con la flecha derecha o la barra espaciadora
-->
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;600;700&display=swap" rel="stylesheet">
<style>{CSS}</style>
</head>
<body>
{''.join(L)}
<div class="ayuda">← →  para navegar · F11 pantalla completa</div>
<script>{JS}</script>
</body>
</html>"""

    os.makedirs(os.path.dirname(SALIDA), exist_ok=True)
    with open(SALIDA, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"  ✓ {T} láminas → {SALIDA}")


if __name__ == "__main__":
    print("Presentación")
    print("-" * 40)
    construir()
