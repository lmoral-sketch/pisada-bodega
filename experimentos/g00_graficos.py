"""
Gráficos de los resultados, para la presentación.

Lee los JSON que dejaron los experimentos: no recalcula nada y no tiene cifras
escritas a mano (regla 4 de AGENTS.md).

Paleta del Manual de Identidad Visual UTEM 2026, con el celeste de la Facultad
de Ingeniería como color predominante.
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

from modelo import parametros as p

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(RAIZ, "resultados")
OUT = os.path.join(RAIZ, "docs", "graficos")

CELESTE = "#00B6ED"      # Facultad de Ingeniería — predominante
AZUL = "#004EAA"         # institucional
VERDE = "#78BF26"        # institucional
TINTA = "#1a1a1a"
SUAVE = "#5a5a5a"
GRIS = "#d8dde3"

plt.rcParams.update({
    "font.family": ["Aptos", "Montserrat", "DejaVu Sans"],
    "font.size": 11,
    "axes.edgecolor": GRIS,
    "axes.labelcolor": TINTA,
    "axes.titlesize": 14,
    "axes.titleweight": "bold",
    "axes.titlecolor": AZUL,
    "text.color": TINTA,
    "xtick.color": SUAVE,
    "ytick.color": SUAVE,
    "figure.facecolor": "white",
    "axes.facecolor": "white",
})


def _marco(ax):
    for lado in ("top", "right"):
        ax.spines[lado].set_visible(False)
    ax.grid(axis="y", color=GRIS, linewidth=0.8, alpha=0.7)
    ax.set_axisbelow(True)


def _guardar(fig, nombre):
    os.makedirs(OUT, exist_ok=True)
    ruta = os.path.join(OUT, nombre)
    fig.savefig(ruta, bbox_inches="tight", dpi=150)
    plt.close(fig)
    print("  ✓", nombre)


def g1_perfil_llegadas():
    """El perfil horario: la primera razón por la que no es una red de Jackson."""
    fig, ax = plt.subplots(figsize=(9, 4.2))
    for ini, fin, ph, _ in p.TRAMOS:
        ax.barh(0, fin - ini, left=ini, height=0.6,
                color=CELESTE if ph < 35 else AZUL, edgecolor="white", linewidth=2)
        ax.text((ini + fin) / 2, 0, f"{ph}", ha="center", va="center",
                color="white", fontweight="bold", fontsize=13)
    ax.axhline(0.45, color=VERDE, linestyle="--", linewidth=1.5)
    ax.text(9.1, 0.52, f"media = {p.LAMBDA_PROMEDIO_HORA:.0f} pedidos/h",
            color=VERDE, fontsize=10, fontweight="bold")
    ax.set_xlim(9, 19)
    ax.set_ylim(-0.6, 0.75)
    ax.set_yticks([])
    ax.set_xticks(range(9, 20))
    ax.set_xticklabels([f"{h}:00" for h in range(9, 20)])
    ax.set_title("Las llegadas no son homogéneas")
    ax.set_xlabel("Hora de la jornada · el número es pedidos por hora")
    for lado in ("top", "right", "left"):
        ax.spines[lado].set_visible(False)
    _guardar(fig, "g1-perfil-llegadas.png")


def g2_degradacion():
    """Cumplimiento contra volumen: dónde deja de servir."""
    with open(os.path.join(RES, "e02-carga.json"), encoding="utf-8") as f:
        d = json.load(f)
    pts = d["puntos"]
    x = [q["pedidos_dia"] for q in pts]
    sla = [q["sla"] for q in pts]

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(x, sla, "o-", color=AZUL, linewidth=2.5, markersize=7,
            label="Cumplimiento del SLA")
    ax.axhline(d["umbral_sla"], color=VERDE, linestyle="--", linewidth=1.8)
    ax.text(x[0], d["umbral_sla"] + 1.2, f"umbral {d['umbral_sla']:.0f} %",
            color=VERDE, fontweight="bold", fontsize=10)

    base = [q for q in pts if abs(q["factor"] - 1.0) < 1e-9][0]
    ax.plot([base["pedidos_dia"]], [base["sla"]], "o", color=CELESTE,
            markersize=15, zorder=5)
    ax.annotate(f"hoy\n{base['pedidos_dia']:.0f} ped/día\n{base['sla']:.1f} %",
                xy=(base["pedidos_dia"], base["sla"]),
                xytext=(base["pedidos_dia"] + 42, base["sla"] - 10),
                color=CELESTE, fontweight="bold", fontsize=10,
                arrowprops=dict(arrowstyle="->", color=CELESTE, linewidth=1.5))

    cumplen = [q for q in pts if q["sla"] >= d["umbral_sla"]]
    if cumplen:
        lim = max(cumplen, key=lambda q: q["factor"])
        ax.axvline(lim["pedidos_dia"], color=SUAVE, linestyle=":", linewidth=1.5)
        ax.text(lim["pedidos_dia"] + 5, 62, "límite de servicio",
                rotation=90, color=SUAVE, fontsize=9, va="bottom", ha="left")

    ax.set_xlabel("Pedidos por día")
    ax.set_ylabel("Cumplimiento del despacho del mismo día (%)")
    ax.set_title("La degradación no es un escalón: es una pendiente", pad=16)
    ax.set_ylim(60, 100)
    _marco(ax)
    _guardar(fig, "g2-degradacion.png")


def g3_utilizacion():
    """Utilización por estación: el cuello y por qué el bloqueo la limita."""
    with open(os.path.join(RES, "e02-carga.json"), encoding="utf-8") as f:
        pts = json.load(f)["puntos"]
    x = [q["pedidos_dia"] for q in pts]

    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(13, 4.8))

    for clave, nombre, color in (("rho_picking", "Picking", CELESTE),
                                 ("rho_empaque", "Empaque", VERDE),
                                 ("rho_control", "Control", AZUL)):
        ax.plot(x, [q[clave] for q in pts], "o-", color=color, linewidth=2.4,
                markersize=6, label=nombre)
    ax.axhline(1.0, color=SUAVE, linestyle="--", linewidth=1.2)
    ax.text(x[0], 1.01, "ρ = 1", color=SUAVE, fontsize=9)
    ax.set_xlabel("Pedidos por día")
    ax.set_ylabel("Utilización ρ observada")
    ax.set_title("El control es el cuello")
    ax.set_ylim(0.5, 1.08)
    ax.legend(frameon=False)
    _marco(ax)

    ax2.plot(x, [q["bloqueo_empaque"] for q in pts], "o-", color=VERDE,
             linewidth=2.4, markersize=6)
    ax2.set_xlabel("Pedidos por día")
    ax2.set_ylabel("Pedidos que dejan bloqueado al empaque (%)")
    ax2.set_title("El bloqueo se propaga hacia atrás")
    _marco(ax2)

    _guardar(fig, "g3-utilizacion.png")


def g4_escenarios():
    """Las cinco intervenciones, comparadas."""
    with open(os.path.join(RES, "e03-mejoras.json"), encoding="utf-8") as f:
        esc = json.load(f)["escenarios"]
    nombres = [e["nombre"].replace(" (", "\n(") for e in esc]
    sla = [e["sla"] for e in esc]
    bloq = [e["bloqueo_empaque"] for e in esc]
    base_sla = esc[0]["sla"]

    fig, (ax, ax2) = plt.subplots(2, 1, figsize=(11, 8.4), sharex=True)
    pos = range(len(esc))

    colores = [SUAVE] + [CELESTE if s >= 95 else AZUL for s in sla[1:]]
    ax.bar(pos, sla, color=colores, width=0.62)
    ax.axhline(base_sla, color=SUAVE, linestyle="--", linewidth=1.3)
    ax.axhline(95, color=VERDE, linestyle="--", linewidth=1.6)
    ax.text(len(esc) - 0.4, 95.15, "meta 95 %", color=VERDE, fontsize=9,
            ha="right", fontweight="bold")
    for i, s in enumerate(sla):
        ax.text(i, s + 0.12, f"{s:.1f}", ha="center", fontsize=10,
                fontweight="bold", color=TINTA)
    ax.set_ylim(92, 96)
    ax.set_ylabel("Cumplimiento (%)")
    ax.set_title("Qué mejora cada intervención")
    _marco(ax)

    ax2.bar(pos, bloq, color=[SUAVE] + [VERDE] * (len(esc) - 1), width=0.62)
    for i, b in enumerate(bloq):
        ax2.text(i, b + 0.5, f"{b:.1f}%", ha="center", fontsize=10, color=TINTA)
    ax2.set_ylabel("Bloqueo en empaque (%)")
    ax2.set_title("Reforzar donde no está el cuello lo empeora")
    ax2.set_xticks(list(pos))
    ax2.set_xticklabels(nombres, fontsize=8.5, rotation=18, ha="right")
    _marco(ax2)

    _guardar(fig, "g4-escenarios.png")


def g5_equilibrio():
    """Desde qué costo de atraso conviene cada mejora."""
    with open(os.path.join(RES, "e03-mejoras.json"), encoding="utf-8") as f:
        d = json.load(f)
    esc, base = d["escenarios"], d["escenarios"][0]
    pedidos_mes = d["pedidos_dia"] * p.DIAS_HABILES_MES

    filas = []
    for e in esc[1:]:
        dc = e["costo_mes"] - base["costo_mes"]
        ev = pedidos_mes * (e["sla"] - base["sla"]) / 100
        if dc > 0 and ev > 0.5:
            filas.append((e["nombre"], dc / ev))
    filas.sort(key=lambda t: t[1])

    fig, ax = plt.subplots(figsize=(10, 4.4))
    nombres = [n.replace(" (", "\n(") for n, _ in filas]
    valores = [v for _, v in filas]
    colores = [CELESTE if v == min(valores) else AZUL for v in valores]
    barras = ax.barh(range(len(filas)), valores, color=colores, height=0.55)
    ax.set_yticks(range(len(filas)))
    ax.set_yticklabels(nombres, fontsize=9)
    ax.invert_yaxis()
    for b, v in zip(barras, valores):
        ax.text(v + max(valores) * 0.015, b.get_y() + b.get_height() / 2,
                "$" + f"{round(v):,}".replace(",", "."),
                va="center", fontsize=10, fontweight="bold", color=TINTA)
    ax.axvline(3500, color=VERDE, linestyle="--", linewidth=1.8)
    ax.text(3500, -0.75, "supuesto\n$3.500", color=VERDE, fontsize=9,
            ha="center", fontweight="bold")
    ax.set_xlabel("Costo de un despacho tardío a partir del cual la mejora se paga sola")
    ax.set_title("El número sobre el que hay que decidir")
    ax.xaxis.set_major_formatter(FuncFormatter(
        lambda v, _: "$" + f"{round(v):,}".replace(",", ".")))
    ax.set_xlim(0, max(valores) * 1.22)
    for lado in ("top", "right"):
        ax.spines[lado].set_visible(False)
    ax.grid(axis="x", color=GRIS, linewidth=0.8, alpha=0.7)
    ax.set_axisbelow(True)
    _guardar(fig, "g5-equilibrio.png")


def main():
    print("Gráficos de la presentación")
    print("-" * 40)
    g1_perfil_llegadas()
    g2_degradacion()
    g3_utilizacion()
    g4_escenarios()
    g5_equilibrio()
    print(f"\nEn {OUT}")


if __name__ == "__main__":
    main()
