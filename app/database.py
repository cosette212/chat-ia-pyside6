"""
database.py
-----------
Capa de persistencia con SQLite.

Tablas:
  usuarios       -> cuentas para el login (usuario + hash de contraseña)
  conversaciones -> una conversación por archivo cargado, ligada a un usuario
  mensajes       -> cada mensaje (del usuario o del modelo) de una conversación

SQLite viene incluido en Python (módulo sqlite3), no hay que instalar nada.
La base se guarda en el archivo chatbot.db en la raíz del proyecto.
"""

import sqlite3
from datetime import datetime
from pathlib import Path

# Ruta del archivo de la base de datos (carpeta raíz del proyecto)
DB_PATH = Path(__file__).resolve().parent.parent / "chatbot.db"

FORMATO_FECHA = "%Y-%m-%d %H:%M:%S"


def ahora() -> str:
    """Fecha y hora actual como texto, ej. '2026-03-24 10:15:20'."""
    return datetime.now().strftime(FORMATO_FECHA)


class BaseDeDatos:
    def __init__(self, ruta: Path | str = DB_PATH):
        # check_same_thread=False porque la respuesta de la IA llega desde otro hilo
        self.conn = sqlite3.connect(str(ruta), check_same_thread=False)
        # row_factory permite acceder a las columnas por nombre: fila["texto"]
        self.conn.row_factory = sqlite3.Row
        # Activa las llaves foráneas (en SQLite vienen apagadas por defecto)
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.crear_tablas()

    # ------------------------------------------------------------------ #
    # Creación del esquema
    # ------------------------------------------------------------------ #
    def crear_tablas(self):
        self.conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS usuarios (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                username      TEXT    NOT NULL UNIQUE,
                password_hash TEXT    NOT NULL,
                salt          TEXT    NOT NULL,
                creado_en     TEXT    NOT NULL
            );

            CREATE TABLE IF NOT EXISTS conversaciones (
                id             INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id     INTEGER NOT NULL,
                titulo         TEXT    NOT NULL,
                archivo_nombre TEXT    NOT NULL,
                archivo_ruta   TEXT,
                archivo_texto  TEXT    NOT NULL,
                fecha_creacion TEXT    NOT NULL,
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS mensajes (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                conversacion_id INTEGER NOT NULL,
                emisor          TEXT    NOT NULL CHECK (emisor IN ('usuario', 'modelo')),
                texto           TEXT    NOT NULL,
                fecha_hora      TEXT    NOT NULL,
                FOREIGN KEY (conversacion_id) REFERENCES conversaciones(id) ON DELETE CASCADE
            );
            """
        )
        self.conn.commit()

    # ------------------------------------------------------------------ #
    # Usuarios
    # ------------------------------------------------------------------ #
    def crear_usuario(self, username: str, password_hash: str, salt: str) -> int:
        """Inserta un usuario. Lanza sqlite3.IntegrityError si ya existe."""
        cur = self.conn.execute(
            "INSERT INTO usuarios (username, password_hash, salt, creado_en) VALUES (?, ?, ?, ?)",
            (username, password_hash, salt, ahora()),
        )
        self.conn.commit()
        return cur.lastrowid

    def obtener_usuario(self, username: str):
        """Regresa la fila del usuario o None si no existe."""
        return self.conn.execute(
            "SELECT * FROM usuarios WHERE username = ?", (username,)
        ).fetchone()

    # ------------------------------------------------------------------ #
    # Conversaciones
    # ------------------------------------------------------------------ #
    def crear_conversacion(self, usuario_id, archivo_nombre, archivo_ruta, archivo_texto) -> int:
        fecha = ahora()
        titulo = f"{archivo_nombre} ({fecha[:16]})"
        cur = self.conn.execute(
            """INSERT INTO conversaciones
               (usuario_id, titulo, archivo_nombre, archivo_ruta, archivo_texto, fecha_creacion)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (usuario_id, titulo, archivo_nombre, archivo_ruta, archivo_texto, fecha),
        )
        self.conn.commit()
        return cur.lastrowid

    def listar_conversaciones(self, usuario_id):
        """Conversaciones del usuario, la más reciente primero."""
        return self.conn.execute(
            """SELECT id, titulo, archivo_nombre, fecha_creacion
               FROM conversaciones WHERE usuario_id = ?
               ORDER BY id DESC""",
            (usuario_id,),
        ).fetchall()

    def obtener_conversacion(self, conversacion_id):
        return self.conn.execute(
            "SELECT * FROM conversaciones WHERE id = ?", (conversacion_id,)
        ).fetchone()

    def renombrar_conversacion(self, conversacion_id, titulo):
        self.conn.execute(
            "UPDATE conversaciones SET titulo = ? WHERE id = ?", (titulo, conversacion_id)
        )
        self.conn.commit()

    def eliminar_conversacion(self, conversacion_id):
        # ON DELETE CASCADE borra también sus mensajes
        self.conn.execute("DELETE FROM conversaciones WHERE id = ?", (conversacion_id,))
        self.conn.commit()

    # ------------------------------------------------------------------ #
    # Mensajes
    # ------------------------------------------------------------------ #
    def agregar_mensaje(self, conversacion_id, emisor, texto) -> dict:
        fecha = ahora()
        cur = self.conn.execute(
            "INSERT INTO mensajes (conversacion_id, emisor, texto, fecha_hora) VALUES (?, ?, ?, ?)",
            (conversacion_id, emisor, texto, fecha),
        )
        self.conn.commit()
        return {"id": cur.lastrowid, "emisor": emisor, "texto": texto, "fecha_hora": fecha}

    def obtener_mensajes(self, conversacion_id):
        """Mensajes de la conversación en orden cronológico."""
        return self.conn.execute(
            """SELECT id, emisor, texto, fecha_hora FROM mensajes
               WHERE conversacion_id = ? ORDER BY id ASC""",
            (conversacion_id,),
        ).fetchall()

    def cerrar(self):
        self.conn.close()
