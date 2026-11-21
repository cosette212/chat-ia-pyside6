"""
login_window.py
---------------
Ventana de inicio de sesión (QDialog).

Un QDialog se abre con .exec() y "bloquea" hasta que se cierra:
  - self.accept() -> el login fue correcto  (exec() regresa Accepted)
  - self.reject() -> el usuario cerró la ventana
"""
from pathlib import Path #CAMBIO NUEVO: Se importo pathlib

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QIcon, QPixmap  #CAMBIO NUEVO: Se importaron QIcon y QPixmap
from PySide6.QtWidgets import (
    QDialog, QHBoxLayout, QLabel, QLineEdit, QMessageBox, QPushButton, QStyle, QVBoxLayout,
)       #CAMBIO NUEVO: Se agrego QStyle a la lista de importaciones

from app import auth

#CAMBIO NUEVO: Se creó una carpeta en la raiz del proyecto (junto a main.py)
CARPETA_ASSETS = Path(__file__).resolve().parent.parent.parent / "assets"

class VentanaLogin(QDialog):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.usuario_id = None
        self.username = ""

        self.setWindowTitle("Chat con IA - Iniciar sesión")
        self.setFixedSize(380, 480)  #CAMBIO NUEVO: Se agrando la altura para el logo y campo extra
        self._construir_ui()

    def _construir_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 25, 30, 25)
        layout.setSpacing(10)

#CAMBIO NUEVO: Se agrego un logo a la ventana de login
        pixmap = QPixmap(str(CARPETA_ASSETS / "logo.png"))
        if not pixmap.isNull():
            logo = QLabel()
            logo.setPixmap(pixmap.scaledToWidth(200, Qt.SmoothTransformation))
            logo.setAlignment(Qt.AlignCenter)
            layout.addWidget(logo)

        titulo = QLabel("Chat con IA")
        titulo.setObjectName("tituloLogin")
        titulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(titulo)

        subtitulo = QLabel("Ingresa tu usuario y contraseña")
        subtitulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitulo)
        layout.addSpacing(10)

        self.campo_usuario = QLineEdit()
        self.campo_usuario.setPlaceholderText("Usuario")
        layout.addWidget(self.campo_usuario)

        self.campo_password = QLineEdit()
        self.campo_password.setPlaceholderText("Contraseña")
        self.campo_password.setEchoMode(QLineEdit.Password)  # muestra ••••
        # Enter en la contraseña = presionar "Ingresar"
        self.campo_password.returnPressed.connect(self.ingresar)
        layout.addWidget(self.campo_password)
        layout.addSpacing(10)

        #CAMBIO NUEVO: Se agrego un boton de mostrar/ocultar contraseña
        self.icono_cerrado = self._cargar_icono("ojo_cerrado.png", QStyle.SP_DialogNoButton)
        self.icono_abierto = self._cargar_icono("ojo_abierto.png", QStyle.SP_DialogYesButton)
        self.accion_ojo = QAction(self.icono_cerrado, "Mostrar contraseña", self)
        self.accion_ojo.setCheckable(True)
        self.accion_ojo.toggled.connect(self.mostrar_password)
        self.campo_password.addAction(self.accion_ojo, QLineEdit.TrailingPosition)

        #CAMBIO NUEVO: Campo para confrimar la contraeña
        self.campo_confirmar = QLineEdit()
        self.campo_confirmar.setPlaceholderText("Confirmar contraseña")
        self.campo_confirmar.setEchoMode(QLineEdit.Password)     
        layout.addWidget(self.campo_confirmar)
        self.campo_confirmar.addAction(self.accion_ojo, QLineEdit.TrailingPosition)
        layout.addSpacing(10)

        botones = QHBoxLayout()
        boton_registrar = QPushButton("Registrarse")
        boton_registrar.setObjectName("botonSecundario")
        boton_registrar.clicked.connect(self.registrar)

        boton_ingresar = QPushButton("Ingresar")
        boton_ingresar.setObjectName("botonLogin")
        boton_ingresar.setDefault(True)
        boton_ingresar.clicked.connect(self.ingresar)

        botones.addWidget(boton_registrar)
        botones.addWidget(boton_ingresar)
        layout.addLayout(botones)
        layout.addStretch()

#CAMBIO NUEVO: Se agrego la funcion para mostrar/ocultar la contraseña

    def _cargar_icono(self, nombre, respaldo):
        ruta = CARPETA_ASSETS / nombre
        if ruta.exists():
            return QIcon(str(ruta))
        return self.style().standardIcon(respaldo)

    def mostrar_password(self, visible):
        modo = QLineEdit.Normal if visible else QLineEdit.Password
        self.campo_password.setEchoMode(modo)
        self.campo_confirmar.setEchoMode(modo)
        self.accion_ojo.setIcon(self.icono_abierto if visible else self.icono_cerrado)
        
    # --- Acciones de los botones (slots) ---
    def ingresar(self):
        usuario = self.campo_usuario.text()
        password = self.campo_password.text()
        usuario_id = auth.iniciar_sesion(self.db, usuario, password)
        if usuario_id is None:
            QMessageBox.warning(self, "Error", "Usuario o contraseña incorrectos.")
            self.campo_password.clear()
            return
        self.usuario_id = usuario_id
        self.username = usuario.strip()
        self.accept()

    def registrar(self):
        #CAMBIO NUEVO: Se agrego una funcion para que se valide que ambas contraseñas coincidan antes de registrarse
        if self.campo_password.text() != self.campo_confirmar.text():
            QMessageBox.warning(self, "Registro", "Las contraseñas no coinciden.")
            return
        
        ok, mensaje = auth.registrar(
            self.db, self.campo_usuario.text(), self.campo_password.text()
        )
        if ok:
            QMessageBox.information(self, "Registro", mensaje)
        else:
            QMessageBox.warning(self, "Registro", mensaje)
