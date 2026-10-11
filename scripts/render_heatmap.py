"""Gráfico de contribuciones animado: las celdas entran en barrido diagonal.

    python scripts/render_heatmap.py [ruta-a-otro-contribuciones.json]

Escribe contribuciones.svg (inglés) y contribuciones.es.svg.
"""
import datetime as dt
import sys

from comun import ATENUADO, AZUL, EASE, IDIOMAS, escribir, leer, mezclar, tarjeta

ANCHO, ALTO = 876, 212
CELDA, PASO = 12, 15
X0, Y0 = 56, 58

TEXTOS = {
    "en": {
        "titulo": "{n} contributions in the last year",
        "meses": "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split(),
        "dias": {1: "Mon", 3: "Wed", 5: "Fri"},
        "menos": "Less", "mas": "More", "al": "updated",
        "aria": "GitHub contribution graph of Nicolás Uribe",
    },
    "es": {
        "titulo": "{n} contribuciones en el último año",
        "meses": "ene feb mar abr may jun jul ago sep oct nov dic".split(),
        "dias": {1: "lun", 3: "mié", 5: "vie"},
        "menos": "Menos", "mas": "Más", "al": "actualizado",
        "aria": "Gráfico de contribuciones en GitHub de Nicolás Uribe",
    },
}

NIVELES = ["#ffffff0d"] + [mezclar(AZUL, a) for a in (0.30, 0.52, 0.76, 1.0)]


def cortes(dias: list[dict]) -> list[int]:
    """Cuartiles sobre los días con actividad, como hace GitHub."""
    activos = sorted(d["n"] for d in dias if d["n"])
    if not activos:
        return [1, 2, 3]
    return [activos[min(len(activos) - 1, int(len(activos) * q))] for q in (0.25, 0.5, 0.75)]


def nivel(n: int, c: list[int]) -> int:
    if n == 0:
        return 0
    return 1 + sum(n > x for x in c)


def miles(n: int, idioma: str) -> str:
    return f"{n:,}".replace(",", "." if idioma == "es" else ",")


def render(datos: dict, idioma: str) -> str:
    t = TEXTOS[idioma]
    dias = datos["dias"]
    c = cortes(dias)
    primero = dt.date.fromisoformat(dias[0]["fecha"])
    # El calendario de GitHub arranca en domingo: fila 0 = domingo.
    desfase = (primero.weekday() + 1) % 7

    celdas, meses, mes_previo = [], [], None
    for i, d in enumerate(dias):
        col, fila = divmod(i + desfase, 7)
        fecha = dt.date.fromisoformat(d["fecha"])
        if fila == 0 or i == 0:
            if fecha.month != mes_previo and col < 51:
                if not meses or col - meses[-1][0] >= 3:
                    meses.append((col, t["meses"][fecha.month - 1]))
                mes_previo = fecha.month
        celdas.append(
            f'<rect class="c" x="{X0 + col * PASO}" y="{Y0 + fila * PASO}" width="{CELDA}" height="{CELDA}" rx="3" '
            f'fill="{NIVELES[nivel(d["n"], c)]}" style="animation-delay:{col * 20 + fila * 14}ms"/>'
        )

    etiquetas = "".join(
        f'<text class="tenue e" x="{X0 + col * PASO}" y="{Y0 - 10}">{nombre}</text>' for col, nombre in meses
    ) + "".join(
        f'<text class="tenue e" x="{X0 - 10}" y="{Y0 + fila * PASO + 10}" text-anchor="end">{nombre}</text>'
        for fila, nombre in t["dias"].items()
    )

    pie_y = Y0 + 7 * PASO + 22
    x_ley = X0 + 53 * PASO - 3
    leyenda = f'<text class="tenue e" x="{x_ley}" y="{pie_y}" text-anchor="end">{t["mas"]}</text>'
    x = x_ley - (len(t["mas"]) * 6.4 + 8)
    for color in reversed(NIVELES):
        x -= PASO
        leyenda += f'<rect x="{x:.0f}" y="{pie_y - 10}" width="{CELDA}" height="{CELDA}" rx="3" fill="{color}"/>'
    leyenda += f'<text class="tenue e" x="{x - 8:.0f}" y="{pie_y}" text-anchor="end">{t["menos"]}</text>'

    cuerpo = f"""<text class="t" x="{X0}" y="30"><tspan class="n">{miles(datos["total"], idioma)}</tspan>{t["titulo"].format(n="")}</text>
{etiquetas}
{"".join(celdas)}
<text class="tenue e mono" x="{X0}" y="{pie_y}">{t["al"]} {datos["actualizado"]}</text>
{leyenda}"""

    css = f"""
.t{{font-size:15px;fill:{ATENUADO}}}
.n{{font-weight:800;fill:#f5f5f7;letter-spacing:-.02em}}
.e{{font-size:11px}}
.c{{opacity:0;transform-box:fill-box;transform-origin:center;animation:entra .55s {EASE} forwards}}
@keyframes entra{{from{{opacity:0;transform:scale(.4)}}to{{opacity:1;transform:scale(1)}}}}"""
    return tarjeta(ANCHO, ALTO, cuerpo, css, t["aria"], radio=20)


def main() -> None:
    datos = leer("contribuciones.json", sys.argv[1] if len(sys.argv) > 1 else None)
    for idioma in IDIOMAS:
        escribir("contribuciones.svg" if idioma == "en" else "contribuciones.es.svg", render(datos, idioma))


if __name__ == "__main__":
    main()
