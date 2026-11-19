"""
probar_api.py
-------------
Script de diagnóstico (no es parte de la interfaz). Sirve para:
  1. Verificar que la API key del .env funciona.
  2. Listar los modelos disponibles para tu cuenta.
  3. Hacer una pregunta de prueba al modelo configurado.

Uso:  python probar_api.py
"""

import os

import requests
from dotenv import load_dotenv

from app.ai_client import ClienteIA, ErrorIA

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY", "")
if not api_key:
    raise SystemExit("❌ No hay GEMINI_API_KEY en el archivo .env")

print("Modelos disponibles que soportan generateContent:")
r = requests.get(
    "https://generativelanguage.googleapis.com/v1beta/models",
    headers={"x-goog-api-key": api_key}, params={"pageSize": 100}, timeout=30,
)
if r.status_code != 200:
    raise SystemExit(f"❌ Error {r.status_code}: {r.text}")
for m in r.json().get("models", []):
    if "generateContent" in m.get("supportedGenerationMethods", []):
        print("  -", m["name"].replace("models/", ""))

cliente = ClienteIA()
print(f"\nProbando el modelo configurado: {cliente.modelo}")
try:
    print("✅ Respuesta:", cliente.preguntar(
        "prueba.txt", "La capital de Francia es París.", [], "¿Cuál es la capital de Francia?"
    ))
except ErrorIA as e:
    print("❌", e)
