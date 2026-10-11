"""Convierte assets/foto-preparada.png en retrato.svg: un retrato de caracteres.

Se corre a mano cuando cambia la foto (después de preparar_foto.py). Necesita
Pillow; sirve el mismo venv de control-gestos. El workflow no lo corre: el
retrato no cambia con los datos.

    C:\\Users\\PC_WIN11\\.venvs\\control-gestos\\Scripts\\python.exe scripts\\retrato_ascii.py
"""
from PIL import Image

from comun import EASE, MONO, RAIZ, escribir, tarjeta

ANCHO, ALTO = 840, 880
COLS, FILAS = 140, 88  # celda de 6x10: la proporción de una fuente monoespaciada
RAMPA = " .`,:;~-=+*oxX#@"  # sin < & ' ": no hay nada que escapar


def main() -> None:
    foto = Image.open(RAIZ / "assets" / "foto-preparada.png").convert("L")
    foto = foto.resize((COLS, FILAS), Image.LANCZOS)
    px = foto.load()

    alto_fila = ALTO / FILAS
    filas = []
    for f in range(FILAS):
        linea = "".join(RAMPA[px[c, f] * (len(RAMPA) - 1) // 255] for c in range(COLS))
        if not linea.strip():
            continue
        # NBSP: un espacio normal al borde se colapsa y textLength estira el resto.
        filas.append(
            f'<text class="f" y="{(f + 0.8) * alto_fila:.1f}" textLength="{ANCHO}" lengthAdjust="spacing" '
            f'style="animation-delay:{f * 16}ms">{linea.replace(" ", chr(160))}</text>'
        )

    cuerpo = f"""<defs><linearGradient id="tinta" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="{ANCHO}" y2="{ALTO}">
<stop offset="0" stop-color="#fff"/><stop offset=".5" stop-color="#fff"/><stop offset="1" stop-color="#8fb8ff"/>
</linearGradient></defs>
<g fill="url(#tinta)">{"".join(filas)}</g>"""

    css = f"""
.f{{font-family:{MONO};font-size:10px;font-weight:700;fill:inherit;opacity:0;animation:revela .5s {EASE} forwards}}
@keyframes revela{{from{{opacity:0}}to{{opacity:1}}}}"""
    escribir("retrato.svg", tarjeta(ANCHO, ALTO, cuerpo, css, "Nicolás Uribe — ASCII portrait"))


if __name__ == "__main__":
    main()
