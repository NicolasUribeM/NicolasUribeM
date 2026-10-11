"""Prepara la foto para el retrato ASCII: quita el fondo, recorta y aclara.

Se corre UNA vez, a mano, cuando cambia la foto. No lo corre el workflow:
necesita mediapipe y opencv, que viven en el venv de control-gestos.

    C:\\Users\\PC_WIN11\\.venvs\\control-gestos\\Scripts\\python.exe scripts\\preparar_foto.py

Entrada:  assets/foto-original.png   (fuera de git)
Salida:   assets/foto-preparada.png  (gris, fondo negro; la lee retrato_ascii.py)
"""
import argparse
import tempfile
import urllib.request
from pathlib import Path

import cv2
import mediapipe as mp
import numpy as np

RAIZ = Path(__file__).resolve().parent.parent
MODELO_URL = (
    "https://storage.googleapis.com/mediapipe-models/image_segmenter/"
    "selfie_segmenter/float16/latest/selfie_segmenter.tflite"
)

# Recorte sobre la foto original (1122x1402): cabeza, hombros y manos.
# Proporción 840:880, la misma de la tarjeta de números, para que queden parejas.
RECORTE = (215, 290, 935, 1045)  # x0, y0, x1, y1


def modelo_local() -> Path:
    destino = Path(tempfile.gettempdir()) / "selfie_segmenter.tflite"
    if not destino.exists():
        urllib.request.urlretrieve(MODELO_URL, destino)
    return destino


def mascara_persona(bgr: np.ndarray) -> np.ndarray:
    opciones = mp.tasks.vision.ImageSegmenterOptions(
        base_options=mp.tasks.BaseOptions(model_asset_path=str(modelo_local())),
        output_confidence_masks=True,
    )
    with mp.tasks.vision.ImageSegmenter.create_from_options(opciones) as seg:
        imagen = mp.Image(image_format=mp.ImageFormat.SRGB, data=cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB))
        mascaras = seg.segment(imagen).confidence_masks
    # El modelo de una sola clase devuelve la confianza de «persona» en la última.
    return mascaras[-1].numpy_view().astype(np.float32).squeeze()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--entrada", default=str(RAIZ / "assets" / "foto-original.png"))
    ap.add_argument("--salida", default=str(RAIZ / "assets" / "foto-preparada.png"))
    args = ap.parse_args()

    bgr = cv2.imdecode(np.fromfile(args.entrada, dtype=np.uint8), cv2.IMREAD_COLOR)
    if bgr is None:
        raise SystemExit(f"No pude leer {args.entrada}")

    mascara = mascara_persona(bgr)
    mascara = cv2.GaussianBlur(mascara, (0, 0), 2.0)

    gris = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    # El traje es negro sobre fondo negro: sin contraste local desaparece entero.
    gris = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8)).apply(gris)
    gris = (255.0 * (gris / 255.0) ** 0.8).astype(np.float32)

    # Piso para la silueta: que el saco se lea como forma aunque sea oscuro.
    piso = 34.0
    persona = np.clip((mascara - 0.35) / 0.3, 0.0, 1.0)
    salida = np.maximum(gris, piso) * persona

    x0, y0, x1, y1 = RECORTE
    salida = salida[y0:y1, x0:x1]
    ok, datos = cv2.imencode(".png", np.clip(salida, 0, 255).astype(np.uint8))
    datos.tofile(args.salida)
    print(f"listo: {args.salida}  {salida.shape[1]}x{salida.shape[0]}")


if __name__ == "__main__":
    main()
