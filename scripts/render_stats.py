"""Tarjeta de números: contribuciones, rachas y reparto real de lenguajes.

    python scripts/render_stats.py [ruta-a-otro-contribuciones.json]

840x880, la misma caja que el retrato ASCII: a igual ancho quedan a igual alto.
Escribe numeros.svg (inglés) y numeros.es.svg.
"""
import sys

from comun import AMARILLO, ATENUADO, AZUL, EASE, IDIOMAS, TURQUESA, VERDE, VIOLETA, escribir, leer, tarjeta

ANCHO, ALTO, M = 840, 880, 56
COLORES = [AZUL, VIOLETA, TURQUESA, VERDE, AMARILLO]
RESTO = "#48484a"

TEXTOS = {
    "en": {
        "periodo": "last 12 months", "total": "contributions",
        "racha": "current streak", "larga": "longest streak", "activos": "active days",
        "dias": "d", "lenguajes": "languages", "repos": "{r} repos · {p} private",
        "otros": "Other", "al": "updated", "aria": "GitHub numbers of Nicolás Uribe",
    },
    "es": {
        "periodo": "últimos 12 meses", "total": "contribuciones",
        "racha": "racha actual", "larga": "racha más larga", "activos": "días activos",
        "dias": "d", "lenguajes": "lenguajes", "repos": "{r} repos · {p} privados",
        "otros": "Otros", "al": "actualizado", "aria": "Números en GitHub de Nicolás Uribe",
    },
}


def rachas(dias: list[dict]) -> tuple[int, int]:
    larga = corrida = 0
    for d in dias:
        corrida = corrida + 1 if d["n"] else 0
        larga = max(larga, corrida)
    # El día de hoy puede ir en cero sin haber roto la racha todavía.
    cola = dias[:-1] if dias and not dias[-1]["n"] else dias
    actual = 0
    for d in reversed(cola):
        if not d["n"]:
            break
        actual += 1
    return actual, larga


def num(valor: float, idioma: str, decimales: int = 0) -> str:
    texto = f"{valor:,.{decimales}f}"
    return texto.translate(str.maketrans(",.", ".,")) if idioma == "es" else texto


def render(contrib: dict, leng: dict, idioma: str) -> str:
    t = TEXTOS[idioma]
    dias = contrib["dias"]
    actual, larga = rachas(dias)
    activos = sum(1 for d in dias if d["n"])

    # --- fichas ---
    hueco = 20
    ancho_f = (ANCHO - 2 * M - 2 * hueco) / 3
    fichas = ""
    for i, (valor, unidad, etiqueta) in enumerate(
        [(actual, t["dias"], t["racha"]), (larga, t["dias"], t["larga"]), (activos, "", t["activos"])]
    ):
        x = M + i * (ancho_f + hueco)
        fichas += f"""<g class="sube" style="animation-delay:{260 + i * 80}ms">
<rect x="{x:.1f}" y="330" width="{ancho_f:.1f}" height="150" rx="22" fill="#fff" fill-opacity=".03" stroke="#fff" stroke-opacity=".06"/>
<text class="v" x="{x + 26:.1f}" y="408">{num(valor, idioma)}<tspan class="u" dx="4">{unidad}</tspan></text>
<text class="tenue et" x="{x + 26:.1f}" y="448">{etiqueta}</text>
</g>"""

    # --- lenguajes ---
    total = sum(leng["bytes"].values())
    orden = list(leng["bytes"].items())
    partes = [(n, b, COLORES[i]) for i, (n, b) in enumerate(orden[:5])]
    sobra = sum(b for _, b in orden[5:])
    if sobra:
        partes.append((t["otros"], sobra, RESTO))

    ancho_b = ANCHO - 2 * M
    barra, x = "", float(M)
    for nombre, b, color in partes:
        w = ancho_b * b / total
        barra += f'<rect x="{x:.1f}" y="596" width="{w + 0.5:.1f}" height="18" fill="{color}"/>'
        x += w

    leyenda = ""
    col_w = ancho_b / 2
    for i, (nombre, b, color) in enumerate(partes):
        col, fila = i % 2, i // 2
        lx, ly = M + col * col_w, 672 + fila * 46
        leyenda += f"""<g class="sube" style="animation-delay:{620 + i * 40}ms">
<circle cx="{lx + 9:.1f}" cy="{ly - 9}" r="8" fill="{color}"/>
<text class="l" x="{lx + 30:.1f}" y="{ly}">{nombre}</text>
<text class="l tenue" x="{lx + col_w - 36:.1f}" y="{ly}" text-anchor="end">{num(100 * b / total, idioma, 1)} %</text>
</g>"""

    cuerpo = f"""<text class="tenue mono cap sube" x="{M}" y="96">{t["periodo"]}</text>
<text class="grande" x="{M - 6}" y="236">{num(contrib["total"], idioma)}</text>
<text class="tenue sub sube" x="{M}" y="286" style="animation-delay:160ms">{t["total"]}</text>
{fichas}
<text class="tenue mono cap sube" x="{M}" y="560" style="animation-delay:520ms">{t["lenguajes"]}</text>
<text class="tenue mono cap sube" x="{ANCHO - M}" y="560" text-anchor="end" style="animation-delay:520ms">{t["repos"].format(r=leng["repos"], p=leng["privados"])}</text>
<clipPath id="pildora"><rect x="{M}" y="596" width="{ancho_b}" height="18" rx="9"/></clipPath>
<rect x="{M}" y="596" width="{ancho_b}" height="18" rx="9" fill="#fff" fill-opacity=".05"/>
<g clip-path="url(#pildora)"><g class="barra">{barra}</g></g>
{leyenda}
<text class="tenue mono pie" x="{M}" y="{ALTO - 44}">{t["al"]} {contrib["actualizado"]}</text>"""

    css = f"""
.cap{{font-size:22px;letter-spacing:.04em}}
.grande{{font-size:156px;font-weight:900;letter-spacing:-.05em;opacity:0;animation:enfoca 1.1s cubic-bezier(.22,1,.36,1) forwards}}
.sub{{font-size:30px}}
.v{{font-size:58px;font-weight:800;letter-spacing:-.03em}}
.u{{font-size:28px;font-weight:600;fill:{ATENUADO}}}
.et{{font-size:21px}}
.l{{font-size:25px}}
.pie{{font-size:20px}}
.sube{{opacity:0;animation:sube .6s {EASE} forwards}}
.barra{{transform-origin:{M}px 605px;transform:scaleX(0);animation:crece 1s {EASE} .6s forwards}}
@keyframes sube{{from{{opacity:0;transform:translateY(16px)}}to{{opacity:1;transform:none}}}}
@keyframes enfoca{{from{{opacity:0;filter:blur(10px)}}to{{opacity:1;filter:blur(0)}}}}
@keyframes crece{{to{{transform:scaleX(1)}}}}"""
    return tarjeta(ANCHO, ALTO, cuerpo, css, t["aria"], tinte=VIOLETA)


def main() -> None:
    contrib = leer("contribuciones.json", sys.argv[1] if len(sys.argv) > 1 else None)
    leng = leer("lenguajes.json")
    for idioma in IDIOMAS:
        escribir("numeros.svg" if idioma == "en" else "numeros.es.svg", render(contrib, leng, idioma))


if __name__ == "__main__":
    main()
