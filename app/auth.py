"""
auth.py
-------
Registro e inicio de sesión.

Las contraseñas NUNCA se guardan en texto plano. Se guarda:
  - salt: 16 bytes aleatorios distintos para cada usuario
  - hash: PBKDF2-SHA256(contraseña + salt) repetido 200,000 veces

Al iniciar sesión se vuelve a calcular el hash con la contraseña escrita y se
compara con el guardado. Todo con la librería estándar (hashlib), sin instalar nada.
"""

import hashlib
import hmac
import os
import sqlite3

from app.database import BaseDeDatos

ITERACIONES = 200_000


def _hashear(password: str, salt: bytes) -> str:
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, ITERACIONES)
    return digest.hex()


def registrar(db: BaseDeDatos, username: str, password: str) -> tuple[bool, str]:
    """Crea un usuario nuevo. Regresa (exito, mensaje)."""
    username = username.strip()
    if len(username) < 3:
        return False, "El usuario debe tener al menos 3 caracteres."
    if len(password) < 4:
        return False, "La contraseña debe tener al menos 4 caracteres."

    salt = os.urandom(16)
    try:
        db.crear_usuario(username, _hashear(password, salt), salt.hex())
    except sqlite3.IntegrityError:
        return False, "Ese usuario ya existe."
    return True, "Usuario registrado. Ya puedes iniciar sesión."


def iniciar_sesion(db: BaseDeDatos, username: str, password: str):
    """Regresa el id del usuario si las credenciales son correctas, si no None."""
    fila = db.obtener_usuario(username.strip())
    if fila is None:
        return None
    hash_calculado = _hashear(password, bytes.fromhex(fila["salt"]))
    # compare_digest compara en tiempo constante (buena práctica de seguridad)
    if hmac.compare_digest(hash_calculado, fila["password_hash"]):
        return fila["id"]
    return None
