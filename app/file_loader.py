"""
file_loader.py
--------------
Lee el archivo que el usuario selecciona y regresa su contenido como texto.

  Texto:   .txt .md .log .csv .tsv .json .xml  -> se leen tal cual
  Web:     .html .htm                          -> se quitan las etiquetas y queda el texto visible
  PDF:     .pdf                                -> se extrae el texto página por página (pypdf)
  Word:    .docx                               -> se lee el XML interno con zipfile (sin librerías extra)
  Excel:   .xlsx                               -> se lee hoja por hoja con openpyxl

El archivo NO se manda al modelo: lo que se manda es el texto extraído.
"""

import re
import xml.etree.ElementTree as ET
import zipfile
from html.parser import HTMLParser
from pathlib import Path

from pypdf import PdfReader

# Límite de caracteres para no exceder lo que acepta el modelo (≈ 50k palabras)
MAX_CARACTERES = 300_000
MARCA_RECORTE = "\n\n[...texto recortado por longitud...]"


class ErrorArchivo(Exception):
    """Error al leer el archivo (formato no válido, PDF sin texto, etc.)."""


# ====================================================================== #
# Lectores: cada uno recibe la ruta (Path) y regresa el texto
# ====================================================================== #
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
        #texto = pagina.extract_text() or ""
        texto = pagina.extract_text(extraction_mode="layout") or ""
        paginas.append(f"--- Página {numero} ---\n{texto}")
    return "\n\n".join(paginas)


# ---------------------------- HTML ------------------------------------- #
class _ExtractorHTML(HTMLParser):
    """Junta solo el texto visible de una página HTML."""

    _IGNORAR = {"script", "style", "noscript", "template"}
    # Bloques: salto de línea al abrir y al cerrar (dejan una línea en blanco entre ellos)
    _BLOQUES = {
        "p", "div", "ul", "ol", "table", "pre", "blockquote",
        "section", "article", "header", "footer", "h1", "h2", "h3", "h4", "h5", "h6",
    }
    # Líneas: un solo salto de línea al abrir (elementos de lista, filas de tabla...)
    _LINEAS = {"br", "hr", "li", "tr"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.partes = []
        self._ignorando = 0

    def handle_starttag(self, tag, attrs):
        if tag in self._IGNORAR:
            self._ignorando += 1
        elif tag in self._BLOQUES or tag in self._LINEAS:
            self.partes.append("\n")
        elif tag in ("td", "th"):
            self.partes.append("\t")  # separa las celdas de una tabla

    def handle_endtag(self, tag):
        if tag in self._IGNORAR:
            self._ignorando = max(0, self._ignorando - 1)
        elif tag in self._BLOQUES:
            self.partes.append("\n")

    def handle_data(self, data):
        if not self._ignorando:
            self.partes.append(re.sub(r"\s+", " ", data))


def leer_html(ruta: Path) -> str:
    extractor = _ExtractorHTML()
    extractor.feed(leer_txt(ruta))
    extractor.close()
    texto = "".join(extractor.partes)
    lineas = [linea.strip() for linea in texto.splitlines()]
    return re.sub(r"\n{3,}", "\n\n", "\n".join(lineas)).strip()


# ---------------------------- Word (.docx) ----------------------------- #
# Un .docx es un zip; el texto está en word/document.xml
_W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"


def _texto_parrafo(parrafo) -> str:
    partes = []
    for el in parrafo.iter():
        if el.tag == _W + "t":
            partes.append(el.text or "")
        elif el.tag == _W + "tab":
            partes.append("\t")
        elif el.tag in (_W + "br", _W + "cr"):
            partes.append("\n")
    return "".join(partes)


def _bloques_docx(contenedor, lineas: list):
    for hijo in contenedor:
        if hijo.tag == _W + "p":
            lineas.append(_texto_parrafo(hijo))
        elif hijo.tag == _W + "tbl":
            # Cada fila de la tabla queda en una línea: celda | celda | celda
            for fila in hijo.iter(_W + "tr"):
                celdas = [
                    " ".join(_texto_parrafo(p) for p in celda.iter(_W + "p")).strip()
                    for celda in fila.findall(_W + "tc")
                ]
                lineas.append(" | ".join(celdas))
        elif hijo.tag == _W + "sdt":  # controles de contenido (ej. tabla de contenido)
            interior = hijo.find(_W + "sdtContent")
            if interior is not None:
                _bloques_docx(interior, lineas)


def leer_docx(ruta: Path) -> str:
    try:
        with zipfile.ZipFile(ruta) as z:
            raiz = ET.fromstring(z.read("word/document.xml"))
    except (zipfile.BadZipFile, KeyError, ET.ParseError) as e:
        raise ErrorArchivo(f"El archivo Word no se pudo abrir (¿está dañado?): {e}")

    cuerpo = raiz.find(_W + "body")
    if cuerpo is None:
        raise ErrorArchivo("El archivo Word no tiene contenido.")
    lineas = []
    _bloques_docx(cuerpo, lineas)
    return "\n".join(lineas)


# ---------------------------- Excel (.xlsx) ---------------------------- #
def leer_xlsx(ruta: Path) -> str:
    try:
        # Importación aquí adentro: si falta openpyxl, el resto de formatos sigue funcionando
        from openpyxl import load_workbook
    except ImportError:
        raise ErrorArchivo(
            "Para leer archivos .xlsx falta la librería openpyxl.\n"
            "Instálala con:  pip install openpyxl"
        )

    try:
        # read_only: no carga todo el libro en memoria
        # data_only: lee el valor de las fórmulas (el que Excel guardó), no la fórmula
        libro = load_workbook(str(ruta), read_only=True, data_only=True)
    except Exception as e:
        raise ErrorArchivo(f"El archivo Excel no se pudo abrir: {e}")

    partes = []
    total = 0
    hay_datos = False
    try:
        for hoja in libro.worksheets:
            partes.append(f"--- Hoja: {hoja.title} ---")
            for fila in hoja.iter_rows(values_only=True):
                celdas = ["" if v is None else str(v) for v in fila]
                while celdas and not celdas[-1]:  # quita las celdas vacías del final
                    celdas.pop()
                if not celdas:
                    continue
                linea = " | ".join(celdas)
                partes.append(linea)
                hay_datos = True
                total += len(linea) + 1
                if total > MAX_CARACTERES:  # no seguimos leyendo lo que se va a recortar
                    break
            if total > MAX_CARACTERES:
                break
    finally:
        libro.close()

    if not hay_datos:
        raise ErrorArchivo("El archivo Excel no tiene datos en ninguna hoja.")
    return "\n".join(partes)


# ====================================================================== #
# Tabla de formatos
# ====================================================================== #
_LECTORES = {
    ".txt": leer_txt, ".md": leer_txt, ".log": leer_txt,
    ".csv": leer_txt, ".tsv": leer_txt, ".json": leer_txt, ".xml": leer_txt,
    ".html": leer_html, ".htm": leer_html,
    ".pdf": leer_pdf,
    ".docx": leer_docx,
    ".xlsx": leer_xlsx,
}

EXTENSIONES_PERMITIDAS = set(_LECTORES)

# Filtro para el diálogo de "abrir archivo" de Qt
FILTRO_DIALOGO = "Documentos (" + " ".join(f"*{e}" for e in sorted(_LECTORES)) + ")"

# Formatos antiguos de Office: no se pueden leer, pero sabemos qué sugerir
_SUGERENCIAS = {".doc": ".docx", ".xls": ".xlsx"}


def cargar_archivo(ruta: str) -> tuple[str, str]:
    """
    Lee el archivo y regresa (nombre_archivo, texto).
    Lanza ErrorArchivo si algo sale mal.
    """
    ruta = Path(ruta)
    extension = ruta.suffix.lower()

    if extension not in EXTENSIONES_PERMITIDAS:
        mensaje = f"Formato no permitido ({extension or 'sin extensión'}).\n"
        if extension in _SUGERENCIAS:
            mensaje += f"Guárdalo como {_SUGERENCIAS[extension]} e inténtalo de nuevo.\n"
        mensaje += "Formatos admitidos: " + ", ".join(sorted(EXTENSIONES_PERMITIDAS))
        raise ErrorArchivo(mensaje)

    texto = _LECTORES[extension](ruta)

    if extension == ".pdf":
        # Quitamos los encabezados de página para saber si de verdad hay texto
        vacio = not texto.replace("--- Página", "").strip(" -0123456789\n")
        mensaje_vacio = "El archivo no contiene texto legible (¿es un PDF escaneado como imagen?)."
    else:
        vacio = not texto.strip()
        mensaje_vacio = "El archivo está vacío o no contiene texto legible."
    if vacio:
        raise ErrorArchivo(mensaje_vacio)

    if len(texto) > MAX_CARACTERES:
        texto = texto[:MAX_CARACTERES] + MARCA_RECORTE

    return ruta.name, texto
