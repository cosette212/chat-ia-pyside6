"""
file_loader.py
--------------
Lee el archivo que el usuario selecciona y regresa su contenido como texto.

  - .txt -> se lee directamente
  - .pdf -> se extrae el texto página por página con la librería pypdf

El archivo NO se manda al modelo: lo que se manda es el texto extraído.
"""

from pathlib import Path

from pypdf import PdfReader

EXTENSIONES_PERMITIDAS = {".txt", ".pdf"}

# Límite de caracteres para no exceder lo que acepta el modelo (≈ 50k palabras)
MAX_CARACTERES = 300_000


class ErrorArchivo(Exception):
    """Error al leer el archivo (formato no válido, PDF sin texto, etc.)."""


def leer_txt(ruta: Path) -> str:
    # Intentamos UTF-8 y, si falla, Latin-1 (común en archivos creados en Windows)
    for codificacion in ("utf-8", "latin-1"):
        try:
            return ruta.read_text(encoding=codificacion)
        except UnicodeDecodeError:
            continue
    raise ErrorArchivo("No se pudo leer el archivo de texto.")


def leer_pdf(ruta: Path) -> str:
    try:
        lector = PdfReader(str(ruta))
    except Exception as e:
        raise ErrorArchivo(f"El PDF no se pudo abrir: {e}")

    paginas = []
    for numero, pagina in enumerate(lector.pages, start=1):
        texto = pagina.extract_text() or ""
        paginas.append(f"--- Página {numero} ---\n{texto}")
    return "\n\n".join(paginas)


def cargar_archivo(ruta: str) -> tuple[str, str]:
    """
    Lee el archivo y regresa (nombre_archivo, texto).
    Lanza ErrorArchivo si algo sale mal.
    """
    ruta = Path(ruta)
    extension = ruta.suffix.lower()

    if extension not in EXTENSIONES_PERMITIDAS:
        raise ErrorArchivo("Formato no permitido. Usa archivos .txt o .pdf")

    texto = leer_txt(ruta) if extension == ".txt" else leer_pdf(ruta)

    # Quitamos los encabezados de página para saber si de verdad hay texto
    if not texto.replace("--- Página", "").strip(" -0123456789\n"):
        raise ErrorArchivo(
            "El archivo no contiene texto legible (¿es un PDF escaneado como imagen?)."
        )

    if len(texto) > MAX_CARACTERES:
        texto = texto[:MAX_CARACTERES] + "\n\n[...texto recortado por longitud...]"

    return ruta.name, texto
