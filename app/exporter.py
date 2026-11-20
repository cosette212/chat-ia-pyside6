"""
exporter.py
-----------
Exporta una conversación guardada a JSON o XML con la estructura que pide
el proyecto. Usa solo librerías estándar: json y xml.etree.ElementTree.

Cada formato se describe en el diccionario FORMATOS; la interfaz lo recorre
para construir el menú y la vista previa, así que agregar un formato nuevo
solo requiere registrarlo ahí y escribir su generador.
"""

import json
import xml.etree.ElementTree as ET
from typing import NamedTuple

from app.database import BaseDeDatos


class Formato(NamedTuple):
    nombre: str      # texto que ve el usuario en el menú
    extension: str   # extensión del archivo (sin punto)
    vista: str       # "texto" = se muestra tal cual / "documento" = se muestra ya con formato


FORMATOS = {
    "json": Formato("JSON", "json", "texto"),
    "xml": Formato("XML", "xml", "texto"),
}


# ====================================================================== #
# Datos de la conversación
# ====================================================================== #
def _datos_conversacion(db: BaseDeDatos, conversacion_id: int) -> dict:
    conv = db.obtener_conversacion(conversacion_id)
    if conv is None:
        raise ValueError(f"No existe la conversación {conversacion_id}")
    mensajes = db.obtener_mensajes(conversacion_id)
    return {
        "conversacion_id": conv["id"],
        "archivo": conv["archivo_nombre"],
        "mensajes": [
            {"emisor": m["emisor"], "texto": m["texto"], "fecha_hora": m["fecha_hora"]}
            for m in mensajes
        ],
    }


# ====================================================================== #
# Generadores: reciben los datos y regresan el contenido del archivo (str)
# ====================================================================== #
def _generar_json(datos: dict) -> str:
    # ensure_ascii=False conserva acentos y ñ; indent=2 lo hace legible
    return json.dumps(datos, ensure_ascii=False, indent=2)


def _generar_xml(datos: dict) -> str:
    raiz = ET.Element("conversacion", id=str(datos["conversacion_id"]))
    ET.SubElement(raiz, "archivo").text = datos["archivo"]
    nodo_mensajes = ET.SubElement(raiz, "mensajes")

    for m in datos["mensajes"]:
        nodo = ET.SubElement(nodo_mensajes, "mensaje", emisor=m["emisor"])
        ET.SubElement(nodo, "texto").text = m["texto"]
        ET.SubElement(nodo, "fecha_hora").text = m["fecha_hora"]

    ET.indent(raiz, space="    ")  # sangría bonita
    return "<?xml version='1.0' encoding='utf-8'?>\n" + ET.tostring(raiz, encoding="unicode")


_GENERADORES = {
    "json": _generar_json,
    "xml": _generar_xml,
}


# ====================================================================== #
# API pública
# ====================================================================== #
def vista_previa(db: BaseDeDatos, conversacion_id: int, clave: str) -> str:
    """Contenido exacto del archivo que se guardaría, para mostrarlo en pantalla."""
    return _GENERADORES[clave](_datos_conversacion(db, conversacion_id))


def exportar(db: BaseDeDatos, conversacion_id: int, clave: str, ruta_salida: str):
    """Exporta la conversación al formato `clave` (una llave de FORMATOS)."""
    if clave not in FORMATOS:
        raise ValueError(f"Formato desconocido: {clave}")
    datos = _datos_conversacion(db, conversacion_id)
    with open(ruta_salida, "w", encoding="utf-8", newline="") as f:
        f.write(_GENERADORES[clave](datos))