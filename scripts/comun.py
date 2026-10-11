"""Lo que comparten las tres tarjetas: tokens, marco y lectura de datos.

Los tokens son los de la skill identidad-visual. Un SVG servido como <img> no
puede cargar fuentes ni ejecutar JS: solo CSS y fuentes del sistema.
"""
import json
from pathlib import Path
from xml.sax.saxutils import escape

RAIZ = Path(__file__).resolve().parent.parent
DATOS = RAIZ / "datos"

FONDO = "#0b0d13"
AZUL = "#0a84ff"
VIOLETA = "#bf5af2"
TURQUESA = "#40c8e0"
VERDE = "#30d158"
AMARILLO = "#ffd60a"
TEXTO = "#f5f5f7"
ATENUADO = "#8e8e93"

SANS = "Inter, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"
MONO = "ui-monospace, 'SF Mono', 'Cascadia Mono', Consolas, 'Liberation Mono', monospace"
EASE = "cubic-bezier(0.16, 1, 0.3, 1)"

IDIOMAS = ("en", "es")


def leer(nombre: str, ruta: str | None = None) -> dict:
    return json.loads(Path(ruta or DATOS / nombre).read_text(encoding="utf-8"))


def mezclar(color: str, alfa: float, sobre: str = FONDO) -> str:
    """Color plano equivalente a `color` con opacidad `alfa` encima de `sobre`."""
    a = [int(color[i : i + 2], 16) for i in (1, 3, 5)]
    b = [int(sobre[i : i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(x * alfa + y * (1 - alfa)):02x}" for x, y in zip(a, b))


def tarjeta(ancho: int, alto: int, cuerpo: str, css: str, titulo: str, tinte: str = AZUL, radio: int = 24) -> str:
    """Marco común: fondo radial, blob tintado detrás y borde de vidrio."""
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {ancho} {alto}" width="{ancho}" height="{alto}" role="img" aria-label="{escape(titulo)}">
<title>{escape(titulo)}</title>
<defs>
<radialGradient id="fondo" cx="50%" cy="0%" r="120%">
<stop offset="0" stop-color="#161b2b"/><stop offset=".55" stop-color="#0d1017"/><stop offset="1" stop-color="{FONDO}"/>
</radialGradient>
<linearGradient id="marca" x1="0" y1="0" x2="1" y2="1">
<stop offset="0" stop-color="#fff"/><stop offset=".5" stop-color="#fff"/><stop offset="1" stop-color="#8fb8ff"/>
</linearGradient>
<filter id="difuso" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="{round(ancho * 0.09)}"/></filter>
<clipPath id="recorte"><rect width="{ancho}" height="{alto}" rx="{radio}"/></clipPath>
</defs>
<style>
text{{font-family:{SANS};fill:{TEXTO}}}
.mono{{font-family:{MONO}}}
.tenue{{fill:{ATENUADO}}}
{css}
@media (prefers-reduced-motion: reduce){{*{{animation:none!important;opacity:1!important;transform:none!important;filter:none!important}}}}
</style>
<g clip-path="url(#recorte)">
<rect width="{ancho}" height="{alto}" fill="url(#fondo)"/>
<ellipse cx="{round(ancho * 0.78)}" cy="{round(alto * 0.12)}" rx="{round(ancho * 0.3)}" ry="{round(alto * 0.28)}" fill="{tinte}" opacity=".14" filter="url(#difuso)"/>
{cuerpo}
</g>
<rect x=".5" y=".5" width="{ancho - 1}" height="{alto - 1}" rx="{radio - 0.5}" fill="none" stroke="#fff" stroke-opacity=".08"/>
</svg>
"""


def escribir(nombre: str, svg: str) -> None:
    destino = RAIZ / nombre
    destino.write_text(svg, encoding="utf-8", newline="\n")
    print(f"{nombre}  {destino.stat().st_size / 1024:.1f} KB")
