"""
vista_previa.py
---------------
Ventanas para "ver contenido":

- DialogoVistaPrevia: muestra la conversación en JSON o XML
  antes de exportarla.
- DialogoContenidoArchivo: muestra el texto extraído del
  archivo cargado, que se utiliza como contexto para el modelo.
"""

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QComboBox, QDialog, QHBoxLayout, QLabel, QPlainTextEdit, QPushButton,
    QTextBrowser, QVBoxLayout,
)

from app import exporter
from app.file_loader import MARCA_RECORTE


class DialogoVistaPrevia(QDialog):
    exportar_solicitado = Signal(str)  # clave del formato elegido (ej. "pdf")

    def __init__(self, db, conversacion_id: int, clave_inicial: str = "json", parent=None):
        super().__init__(parent)
        self.db = db
        self.conversacion_id = conversacion_id
        self.setWindowTitle("Ver contenido de la conversación")
        self.resize(780, 580)

        lay = QVBoxLayout(self)

        # Selector de formato
        fila = QHBoxLayout()
        fila.addWidget(QLabel("Formato:"))
        self.selector = QComboBox()
        for clave, formato in exporter.FORMATOS.items():
            self.selector.addItem(formato.nombre, clave)  # la clave queda oculta en el item
        fila.addWidget(self.selector)
        fila.addStretch()
        lay.addLayout(fila)

        self.nota = QLabel()
        self.nota.setObjectName("notaVistaPrevia")
        self.nota.setWordWrap(True)
        lay.addWidget(self.nota)

        # Dos visores; solo se muestra el que corresponde al formato
        self.vista_texto = QPlainTextEdit()
        self.vista_texto.setObjectName("vistaCodigo")
        self.vista_texto.setReadOnly(True)
        self.vista_texto.setLineWrapMode(QPlainTextEdit.NoWrap)
        self.vista_documento = QTextBrowser()
        self.vista_documento.setOpenLinks(False)  # los enlaces no navegan dentro de la vista
        lay.addWidget(self.vista_texto, stretch=1)
        lay.addWidget(self.vista_documento, stretch=1)

        # Botones
        botones = QHBoxLayout()
        botones.addStretch()
        cerrar = QPushButton("Cerrar")
        cerrar.setObjectName("botonSecundario")
        cerrar.clicked.connect(self.accept)
        exportar = QPushButton("Exportar…")
        exportar.setObjectName("botonDialogo")
        exportar.clicked.connect(lambda: self.exportar_solicitado.emit(self.selector.currentData()))
        botones.addWidget(cerrar)
        botones.addWidget(exportar)
        lay.addLayout(botones)

        self.selector.currentIndexChanged.connect(self._actualizar)
        indice = self.selector.findData(clave_inicial)
        self.selector.setCurrentIndex(max(indice, 0))
        self._actualizar()

    def _actualizar(self):
        clave = self.selector.currentData()
        formato = exporter.FORMATOS[clave]
        try:
            contenido = exporter.vista_previa(self.db, self.conversacion_id, clave)
        except Exception as e:
            contenido = f"No se pudo generar la vista previa: {e}"
            formato = formato._replace(vista="texto")  # el error se muestra como texto simple

        es_texto = formato.vista == "texto"
        self.vista_texto.setVisible(es_texto)
        self.vista_documento.setVisible(not es_texto)
        if es_texto:
            self.vista_texto.setPlainText(contenido)
            self.nota.setText(f"Contenido exacto del archivo .{formato.extension} que se guardará.")
        else:
            self.vista_documento.setMarkdown(contenido)
            self.nota.setText(
                f"Vista aproximada: el archivo .{formato.extension} se genera con este contenido."
            )


class DialogoContenidoArchivo(QDialog):
    """Muestra el texto extraído del archivo cargado (solo lectura)."""

    def __init__(self, nombre: str, texto: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Contenido de {nombre}")
        self.resize(780, 580)

        lay = QVBoxLayout(self)

        nota = (
            f"Este es el texto que se envía al modelo (extraído de {nombre}): "
            f"{len(texto.split()):,} palabras · {len(texto):,} caracteres."
        )
        if texto.endswith(MARCA_RECORTE):
            nota += " El archivo era muy largo y se recortó."
        etiqueta = QLabel(nota)
        etiqueta.setObjectName("notaVistaPrevia")
        etiqueta.setWordWrap(True)
        lay.addWidget(etiqueta)

        visor = QPlainTextEdit()
        visor.setReadOnly(True)
        visor.setPlainText(texto)
        lay.addWidget(visor, stretch=1)

        botones = QHBoxLayout()
        botones.addStretch()
        cerrar = QPushButton("Cerrar")
        cerrar.setObjectName("botonSecundario")
        cerrar.clicked.connect(self.accept)
        botones.addWidget(cerrar)
        lay.addLayout(botones)
