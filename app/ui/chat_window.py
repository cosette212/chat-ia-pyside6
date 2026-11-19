"""
chat_window.py
--------------
Ventana principal tipo chat.

Estructura visual:

  ┌──────────────┬──────────────────────────────────────────┐
  │ PANEL        │ 📄 Archivo: planetas.pdf                  │  <- barra de archivo
  │ LATERAL      ├──────────────────────────────────────────┤
  │              │        [burbuja usuario]  ──────────────▶│
  │ + Nueva conv │ ◀── [burbuja modelo]                      │  <- área de mensajes
  │ Historial    │                                          │     (QScrollArea)
  │  - conv 3    ├──────────────────────────────────────────┤
  │  - conv 2    │ [ escribe tu pregunta...      ] [Enviar] │  <- barra de entrada
  │ Exportar...  │                                          │
  └──────────────┴──────────────────────────────────────────┘

La llamada a la IA tarda unos segundos; si se hiciera en el hilo principal la
ventana se "congelaría". Por eso se hace en un QThread (HiloIA) y el resultado
regresa a la interfaz mediante una señal (Signal).
"""

from PySide6.QtCore import Qt, QThread, QTimer, Signal
from PySide6.QtWidgets import (
    QApplication, QFileDialog, QFrame, QHBoxLayout, QLabel, QListWidget, QListWidgetItem,
    QMainWindow, QMessageBox, QPlainTextEdit, QPushButton, QScrollArea,
    QVBoxLayout, QWidget,
)

from app import exporter
from app.ai_client import ClienteIA, ErrorIA
from app.file_loader import ErrorArchivo, cargar_archivo
from app.ui.styles import ESTILO, ESTILO_OSCURO

# ====================================================================== #
# Hilo que consulta al modelo sin congelar la interfaz
# ====================================================================== #
class HiloIA(QThread):
    respuesta_lista = Signal(str)  # se emite con el texto de la respuesta
    error = Signal(str)            # se emite si algo falla

    def __init__(self, cliente, archivo_nombre, archivo_texto, historial, pregunta):
        super().__init__()
        self.cliente = cliente
        self.archivo_nombre = archivo_nombre
        self.archivo_texto = archivo_texto
        self.historial = historial
        self.pregunta = pregunta

    def run(self):  # esto corre en el hilo secundario
        try:
            texto = self.cliente.preguntar(
                self.archivo_nombre, self.archivo_texto, self.historial, self.pregunta
            )
            self.respuesta_lista.emit(texto)
        except ErrorIA as e:
            self.error.emit(str(e))
        except Exception as e:
            self.error.emit(f"Error inesperado: {e}")


# ====================================================================== #
# Burbuja de mensaje
# ====================================================================== #
class Burbuja(QWidget):
    def __init__(self, emisor: str, texto: str, fecha_hora: str):
        super().__init__()
        es_usuario = emisor == "usuario"

        fila = QHBoxLayout(self)
        fila.setContentsMargins(10, 4, 10, 4)

        marco = QFrame()
        marco.setObjectName("burbujaUsuario" if es_usuario else "burbujaModelo")
        marco.setMaximumWidth(620)

        interior = QVBoxLayout(marco)
        interior.setContentsMargins(12, 8, 12, 8)
        interior.setSpacing(4)

        etiqueta_emisor = QLabel("Tú" if es_usuario else "🤖 Modelo")
        etiqueta_emisor.setObjectName("emisor")

        etiqueta_texto = QLabel(texto)
        etiqueta_texto.setWordWrap(True)
        etiqueta_texto.setTextInteractionFlags(Qt.TextSelectableByMouse)
        # Las respuestas del modelo suelen venir en Markdown (listas, **negritas**)
        etiqueta_texto.setTextFormat(Qt.PlainText if es_usuario else Qt.MarkdownText)

        etiqueta_fecha = QLabel(fecha_hora)
        etiqueta_fecha.setObjectName("fecha")
        etiqueta_fecha.setAlignment(Qt.AlignRight)

        interior.addWidget(etiqueta_emisor)
        interior.addWidget(etiqueta_texto)
        interior.addWidget(etiqueta_fecha)

        # Usuario a la derecha, modelo a la izquierda
        if es_usuario:
            fila.addStretch()
            fila.addWidget(marco)
        else:
            fila.addWidget(marco)
            fila.addStretch()


# ====================================================================== #
# Caja de texto: Enter envía, Shift+Enter hace salto de línea
# ====================================================================== #
class CajaMensaje(QPlainTextEdit):
    enviar = Signal()

    def keyPressEvent(self, evento):
        if evento.key() in (Qt.Key_Return, Qt.Key_Enter) and not (
            evento.modifiers() & Qt.ShiftModifier
        ):
            self.enviar.emit()
            return
        super().keyPressEvent(evento)


# ====================================================================== #
# Ventana principal
# ====================================================================== #
class VentanaChat(QMainWindow):
    sesion_cerrada = Signal()  # avisa a main.py que hay que volver al login

    def __init__(self, db, usuario_id: int, username: str):
        super().__init__()
        self.db = db
        self.usuario_id = usuario_id
        self.username = username
        self.cliente_ia = ClienteIA()

        self.conversacion_id = None  # conversación abierta actualmente
        self.hilo = None             # referencia al hilo para que no lo borre el recolector
        self.cerrando_sesion = False
        self.tema_oscuro = False     # empezamos en tema claro

        self.setWindowTitle(f"Chat con IA - {username}")
        self.resize(1100, 720)
        self._construir_ui()
        self.cargar_lista_conversaciones()   # requisito: al entrar se cargan sus conversaciones
        self.mostrar_bienvenida()

        if not self.cliente_ia.configurado():
            QMessageBox.warning(
                self, "API key",
                "No se encontró GEMINI_API_KEY en el archivo .env.\n"
                "Podrás ver tus conversaciones, pero no consultar al modelo.",
            )

    # ------------------------------------------------------------------ #
    # Construcción de la interfaz
    # ------------------------------------------------------------------ #
    def _construir_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout_principal = QHBoxLayout(central)
        layout_principal.setContentsMargins(0, 0, 0, 0)
        layout_principal.setSpacing(0)

        layout_principal.addWidget(self._crear_panel_lateral())
        layout_principal.addWidget(self._crear_zona_chat(), stretch=1)

    def _crear_panel_lateral(self) -> QWidget:
        panel = QWidget()
        panel.setObjectName("panelLateral")
        panel.setFixedWidth(270)
        lay = QVBoxLayout(panel)
        lay.setContentsMargins(14, 14, 14, 14)
        lay.setSpacing(8)

        usuario = QLabel(f"👤 {self.username}")
        usuario.setObjectName("etiquetaUsuario")
        lay.addWidget(usuario)

        boton_nueva = QPushButton("➕  Nueva conversación (cargar archivo)")
        boton_nueva.setObjectName("botonPrincipal")
        boton_nueva.clicked.connect(self.nueva_conversacion)
        lay.addWidget(boton_nueva)

        titulo = QLabel("HISTORIAL")
        titulo.setObjectName("tituloSeccion")
        lay.addWidget(titulo)

        self.lista_conversaciones = QListWidget()
        self.lista_conversaciones.itemClicked.connect(self.abrir_conversacion_desde_lista)
        lay.addWidget(self.lista_conversaciones, stretch=1)

        titulo_op = QLabel("OPCIONES")
        titulo_op.setObjectName("tituloSeccion")
        lay.addWidget(titulo_op)

        for texto, funcion in [
            ("📤  Exportar a JSON", self.exportar_json),
            ("📤  Exportar a XML", self.exportar_xml),
            ("🗑  Eliminar conversación", self.eliminar_conversacion),
            ("🚪  Cerrar sesión", self.cerrar_sesion),
        ]:
                    # Botón para cambiar de tema
            self.boton_tema = QPushButton("🌙  Modo oscuro")
            self.boton_tema.clicked.connect(self.cambiar_tema)
            lay.addWidget(self.boton_tema)
            boton = QPushButton(texto)
            boton.clicked.connect(funcion)
            lay.addWidget(boton)

        modelo = QLabel(f"Modelo: {self.cliente_ia.modelo}")
        modelo.setObjectName("tituloSeccion")
        lay.addWidget(modelo)
        return panel

    def _crear_zona_chat(self) -> QWidget:
        zona = QWidget()
        zona.setObjectName("zonaChat")
        lay = QVBoxLayout(zona)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        # Barra superior con el nombre del archivo
        self.etiqueta_archivo = QLabel("📄 Sin archivo cargado")
        self.etiqueta_archivo.setObjectName("barraArchivo")
        lay.addWidget(self.etiqueta_archivo)

        # Área de mensajes con scroll
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.contenedor = QWidget()
        self.contenedor.setObjectName("contenedorMensajes")
        self.layout_mensajes = QVBoxLayout(self.contenedor)
        self.layout_mensajes.setContentsMargins(0, 10, 0, 10)
        self.layout_mensajes.addStretch()  # empuja los mensajes hacia arriba
        self.scroll.setWidget(self.contenedor)
        lay.addWidget(self.scroll, stretch=1)

        # Barra inferior de entrada
        barra = QWidget()
        barra.setObjectName("barraEntrada")
        lay_barra = QHBoxLayout(barra)
        lay_barra.setContentsMargins(12, 10, 12, 10)

        self.caja_texto = CajaMensaje()
        self.caja_texto.setPlaceholderText(
            "Escribe tu pregunta sobre el archivo... (Enter envía, Shift+Enter = nueva línea)"
        )
        self.caja_texto.setFixedHeight(70)
        self.caja_texto.enviar.connect(self.enviar_mensaje)

        self.boton_enviar = QPushButton("Enviar ➤")
        self.boton_enviar.setObjectName("botonEnviar")
        self.boton_enviar.setFixedHeight(70)
        self.boton_enviar.clicked.connect(self.enviar_mensaje)

        lay_barra.addWidget(self.caja_texto, stretch=1)
        lay_barra.addWidget(self.boton_enviar)
        lay.addWidget(barra)
        return zona

    # ------------------------------------------------------------------ #
    # Manejo de burbujas
    # ------------------------------------------------------------------ #
    def limpiar_mensajes(self):
        # Quita todos los widgets excepto el stretch final
        while self.layout_mensajes.count() > 1:
            item = self.layout_mensajes.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def agregar_burbuja(self, emisor, texto, fecha_hora):
        burbuja = Burbuja(emisor, texto, fecha_hora)
        # se inserta antes del stretch final
        self.layout_mensajes.insertWidget(self.layout_mensajes.count() - 1, burbuja)
        # baja el scroll cuando Qt termine de acomodar el widget
        QTimer.singleShot(50, lambda: self.scroll.verticalScrollBar().setValue(
            self.scroll.verticalScrollBar().maximum()))
        return burbuja

    def mostrar_bienvenida(self):
        self.limpiar_mensajes()
        self.agregar_burbuja(
            "modelo",
            "¡Hola! Carga un archivo **TXT** o **PDF** con el botón "
            "*Nueva conversación* y hazme preguntas sobre su contenido.\n\n"
            "También puedes abrir una conversación anterior desde el historial "
            "para continuarla.",
            "",
        )

    # ------------------------------------------------------------------ #
    # Conversaciones
    # ------------------------------------------------------------------ #
    def cargar_lista_conversaciones(self):
        self.lista_conversaciones.clear()
        for conv in self.db.listar_conversaciones(self.usuario_id):
            item = QListWidgetItem(conv["titulo"])
            item.setData(Qt.UserRole, conv["id"])  # guardamos el id oculto en el item
            item.setToolTip(f"Archivo: {conv['archivo_nombre']}\nCreada: {conv['fecha_creacion']}")
            self.lista_conversaciones.addItem(item)
            if conv["id"] == self.conversacion_id:
                item.setSelected(True)

    def nueva_conversacion(self):
        ruta, _ = QFileDialog.getOpenFileName(
            self, "Selecciona un archivo", "", "Documentos (*.txt *.pdf)"
        )
        if not ruta:
            return  # el usuario canceló
        try:
            nombre, texto = cargar_archivo(ruta)
        except ErrorArchivo as e:
            QMessageBox.warning(self, "Archivo", str(e))
            return

        self.conversacion_id = self.db.crear_conversacion(self.usuario_id, nombre, ruta, texto)
        self.cargar_lista_conversaciones()
        self.abrir_conversacion(self.conversacion_id)

    def abrir_conversacion_desde_lista(self, item):
        self.abrir_conversacion(item.data(Qt.UserRole))

    def abrir_conversacion(self, conversacion_id):
        conv = self.db.obtener_conversacion(conversacion_id)
        if conv is None:
            return
        self.conversacion_id = conversacion_id
        palabras = len(conv["archivo_texto"].split())
        self.etiqueta_archivo.setText(
            f"📄 Archivo: {conv['archivo_nombre']}   ·   {palabras:,} palabras"
        )

        self.limpiar_mensajes()
        mensajes = self.db.obtener_mensajes(conversacion_id)
        if not mensajes:
            self.agregar_burbuja(
                "modelo", f"Archivo **{conv['archivo_nombre']}** cargado. ¿Qué quieres saber?", ""
            )
        for m in mensajes:
            self.agregar_burbuja(m["emisor"], m["texto"], m["fecha_hora"])
        self.caja_texto.setFocus()

    def eliminar_conversacion(self):
        if not self._hay_conversacion():
            return
        r = QMessageBox.question(self, "Eliminar", "¿Eliminar la conversación actual?")
        if r == QMessageBox.Yes:
            self.db.eliminar_conversacion(self.conversacion_id)
            self.conversacion_id = None
            self.etiqueta_archivo.setText("📄 Sin archivo cargado")
            self.cargar_lista_conversaciones()
            self.mostrar_bienvenida()

    # ------------------------------------------------------------------ #
    # Envío de mensajes y respuesta de la IA
    # ------------------------------------------------------------------ #
    def enviar_mensaje(self):
        pregunta = self.caja_texto.toPlainText().strip()
        if not pregunta or (self.hilo and self.hilo.isRunning()):
            return
        if self.conversacion_id is None:
            QMessageBox.information(self, "Archivo", "Primero carga un archivo (Nueva conversación).")
            return

        conv = self.db.obtener_conversacion(self.conversacion_id)
        # Historial ANTES de guardar la pregunta nueva (para continuar la conversación)
        historial = [dict(m) for m in self.db.obtener_mensajes(self.conversacion_id)]

        # Si es la primera pregunta, la usamos como título de la conversación
        if not historial:
            corto = pregunta if len(pregunta) <= 35 else pregunta[:35] + "…"
            self.db.renombrar_conversacion(self.conversacion_id, f"{corto} · {conv['archivo_nombre']}")
            self.cargar_lista_conversaciones()

        # 1) guardar y mostrar la pregunta
        msg = self.db.agregar_mensaje(self.conversacion_id, "usuario", pregunta)
        self.agregar_burbuja("usuario", msg["texto"], msg["fecha_hora"])
        self.caja_texto.clear()

        # 2) indicador de "escribiendo"
        self.burbuja_espera = self.agregar_burbuja("modelo", "_Pensando..._", "")
        self._bloquear_entrada(True)

        # 3) lanzar el hilo que consulta al modelo
        self.hilo = HiloIA(self.cliente_ia, conv["archivo_nombre"], conv["archivo_texto"],
                           historial, pregunta)
        self.hilo.respuesta_lista.connect(self.recibir_respuesta)
        self.hilo.error.connect(self.recibir_error)
        self.hilo.start()

    def recibir_respuesta(self, texto):
        self._quitar_burbuja_espera()
        msg = self.db.agregar_mensaje(self.conversacion_id, "modelo", texto)
        self.agregar_burbuja("modelo", msg["texto"], msg["fecha_hora"])
        self._bloquear_entrada(False)

    def recibir_error(self, error):
        self._quitar_burbuja_espera()
        # El error no se guarda en la BD: solo se muestra
        self.agregar_burbuja("modelo", f"⚠️ **No se pudo obtener respuesta.**\n\n{error}", "")
        self._bloquear_entrada(False)

    def _quitar_burbuja_espera(self):
        if getattr(self, "burbuja_espera", None):
            self.burbuja_espera.deleteLater()
            self.burbuja_espera = None

    def _bloquear_entrada(self, bloquear: bool):
        self.boton_enviar.setEnabled(not bloquear)
        self.caja_texto.setReadOnly(bloquear)
        self.lista_conversaciones.setEnabled(not bloquear)
        if not bloquear:
            self.caja_texto.setFocus()

    # ------------------------------------------------------------------ #
    # Exportación
    # ------------------------------------------------------------------ #
    def _hay_conversacion(self) -> bool:
        if self.conversacion_id is None:
            QMessageBox.information(self, "Aviso", "Abre o crea una conversación primero.")
            return False
        return True

    def _exportar(self, extension, funcion):
        if not self._hay_conversacion():
            return
        sugerido = f"conversacion_{self.conversacion_id}.{extension}"
        ruta, _ = QFileDialog.getSaveFileName(
            self, f"Exportar a {extension.upper()}", sugerido, f"{extension.upper()} (*.{extension})"
        )
        if not ruta:
            return
        if not ruta.lower().endswith(f".{extension}"):
            ruta += f".{extension}"
        try:
            funcion(self.db, self.conversacion_id, ruta)
            QMessageBox.information(self, "Exportar", f"Conversación exportada en:\n{ruta}")
        except Exception as e:
            QMessageBox.critical(self, "Exportar", f"Error al exportar: {e}")

    def exportar_json(self):
        self._exportar("json", exporter.exportar_json)

    def exportar_xml(self):
        self._exportar("xml", exporter.exportar_xml)

    # ------------------------------------------------------------------ #
    # Sesión
    # ------------------------------------------------------------------ #
    def cerrar_sesion(self):
        self.cerrando_sesion = True
        self.close()

    def closeEvent(self, evento):
        # Espera a que termine una consulta pendiente antes de cerrar
        if self.hilo and self.hilo.isRunning():
            self.hilo.wait(3000)
        evento.accept()
        if self.cerrando_sesion:
            self.sesion_cerrada.emit()


    # Tema claro / oscuro
    def cambiar_tema(self):
        self.tema_oscuro = not self.tema_oscuro    # True -> False, False -> True

        app = QApplication.instance()              # la aplicación que ya existe
        if self.tema_oscuro:
            app.setStyleSheet(ESTILO_OSCURO)
            self.boton_tema.setText("☀️  Modo claro")
        else:
            app.setStyleSheet(ESTILO)
            self.boton_tema.setText("🌙  Modo oscuro")