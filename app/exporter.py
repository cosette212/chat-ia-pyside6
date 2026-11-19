"""
exporter.py
-----------
Exporta una conversación guardada a JSON o XML con la estructura que pide
el proyecto. Usa solo librerías estándar: json y xml.etree.ElementTree.
"""

import json
import xml.etree.ElementTree as ET

from app.database import BaseDeDatos


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


def exportar_json(db: BaseDeDatos, conversacion_id: int, ruta_salida: str):
    datos = _datos_conversacion(db, conversacion_id)
    with open(ruta_salida, "w", encoding="utf-8") as f:
        # ensure_ascii=False conserva acentos y ñ; indent=2 lo hace legible
        json.dump(datos, f, ensure_ascii=False, indent=2)


def exportar_xml(db: BaseDeDatos, conversacion_id: int, ruta_salida: str):
    datos = _datos_conversacion(db, conversacion_id)

    raiz = ET.Element("conversacion", id=str(datos["conversacion_id"]))
    ET.SubElement(raiz, "archivo").text = datos["archivo"]
    nodo_mensajes = ET.SubElement(raiz, "mensajes")

    for m in datos["mensajes"]:
        nodo = ET.SubElement(nodo_mensajes, "mensaje", emisor=m["emisor"])
        ET.SubElement(nodo, "texto").text = m["texto"]
        ET.SubElement(nodo, "fecha_hora").text = m["fecha_hora"]

    arbol = ET.ElementTree(raiz)
    ET.indent(arbol, space="    ")  # sangría bonita
    arbol.write(ruta_salida, encoding="utf-8", xml_declaration=True)
