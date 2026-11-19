"""
main.py
-------
Punto de entrada de la aplicación. Ejecutar con:

    python main.py

Flujo:
  1. Se crea la base de datos (si no existe).
  2. Se muestra el login.
  3. Si el login es correcto, se abre la ventana de chat.
  4. Si se cierra sesión, se vuelve al login. Si se cierra la ventana, termina.
"""

import sys

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication, QDialog

from app.database import BaseDeDatos
from app.ui.chat_window import VentanaChat
from app.ui.login_window import VentanaLogin
from app.ui.styles import ESTILO


class Controlador:
    """Decide qué ventana se muestra (login o chat)."""

    def __init__(self, app: QApplication):
        self.app = app
        self.db = BaseDeDatos()
        self.ventana_chat = None

    def mostrar_login(self):
        login = VentanaLogin(self.db)
        if login.exec() == QDialog.Accepted:
            self.ventana_chat = VentanaChat(self.db, login.usuario_id, login.username)
            self.ventana_chat.sesion_cerrada.connect(self.al_cerrar_sesion)
            self.ventana_chat.show()
        else:
            self.salir()

    def al_cerrar_sesion(self):
        self.ventana_chat = None
        QTimer.singleShot(0, self.mostrar_login)

    def salir(self):
        self.db.cerrar()
        self.app.quit()


def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(ESTILO)
    # Controlamos nosotros cuándo termina la app (por el cambio login <-> chat)
    app.setQuitOnLastWindowClosed(False)

    controlador = Controlador(app)

    # Si el usuario cierra la ventana del chat (sin "Cerrar sesión"), salimos
    def revisar_ventanas():
        if controlador.ventana_chat is not None and not controlador.ventana_chat.isVisible():
            controlador.salir()
    app.lastWindowClosed.connect(revisar_ventanas)

    QTimer.singleShot(0, controlador.mostrar_login)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
