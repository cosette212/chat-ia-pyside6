"""
ai_client.py
------------
Conexión con el modelo de IA (Google Gemini, tiene capa gratuita).

Se usa la API REST directamente con la librería `requests`, para que se vea
claro qué se envía y qué se recibe:

  POST https://generativelanguage.googleapis.com/v1beta/models/<modelo>:generateContent
  Header:  x-goog-api-key: <TU_API_KEY>
  Body:    {
             "system_instruction": {...},   <- instrucciones + texto del archivo
             "contents": [ ...historial... , {"role": "user", ...pregunta...} ]
           }

Para "continuar" una conversación guardada, se manda todo el historial de
mensajes previos; así el modelo recuerda lo que ya se habló.

La API key se lee del archivo .env (que NO se sube a GitHub).
"""

import os

import requests
from dotenv import load_dotenv

load_dotenv()  # carga las variables del archivo .env

URL_BASE = "https://generativelanguage.googleapis.com/v1beta/models"

INSTRUCCIONES = (
    "Eres un asistente que responde preguntas sobre el documento que se te "
    "proporciona. Responde en español, de forma clara y concisa. Basa tus "
    "respuestas en el contenido del documento; si la respuesta no está en él, "
    "dilo explícitamente.\n\n"
    "=== DOCUMENTO: {nombre} ===\n{texto}\n=== FIN DEL DOCUMENTO ==="
)


class ErrorIA(Exception):
    """Error al comunicarse con el modelo."""


class ClienteIA:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY", "").strip()
        self.modelo = os.getenv("GEMINI_MODEL", "gemini-flash-latest").strip()

    def configurado(self) -> bool:
        return bool(self.api_key)

    def preguntar(self, archivo_nombre: str, archivo_texto: str,
                  historial: list[dict], pregunta: str) -> str:
        """
        historial: lista de dicts {"emisor": "usuario"|"modelo", "texto": "..."}
        Regresa el texto de la respuesta del modelo.
        """
        if not self.configurado():
            raise ErrorIA("Falta GEMINI_API_KEY en el archivo .env")

        # Gemini usa los roles "user" y "model"
        contenidos = [
            {
                "role": "user" if m["emisor"] == "usuario" else "model",
                "parts": [{"text": m["texto"]}],
            }
            for m in historial
        ]
        contenidos.append({"role": "user", "parts": [{"text": pregunta}]})

        cuerpo = {
            "system_instruction": {
                "parts": [{"text": INSTRUCCIONES.format(nombre=archivo_nombre, texto=archivo_texto)}]
            },
            "contents": contenidos,
        }

        try:
            resp = requests.post(
                f"{URL_BASE}/{self.modelo}:generateContent",
                headers={"x-goog-api-key": self.api_key, "Content-Type": "application/json"},
                json=cuerpo,
                timeout=90,
            )
        except requests.RequestException as e:
            raise ErrorIA(f"No se pudo conectar con el modelo: {e}")

        if resp.status_code != 200:
            try:
                detalle = resp.json().get("error", {}).get("message", resp.text)
            except ValueError:
                detalle = resp.text
            raise ErrorIA(f"Error {resp.status_code} de la API: {detalle}")

        datos = resp.json()
        try:
            partes = datos["candidates"][0]["content"]["parts"]
            return "".join(p.get("text", "") for p in partes).strip()
        except (KeyError, IndexError):
            raise ErrorIA(f"Respuesta inesperada del modelo: {datos}")
