"""
styles.py
---------
Hoja de estilos (QSS) de la aplicación. QSS es como CSS pero para Qt.
Se seleccionan widgets por su clase (QPushButton) o por su objectName (#panelLateral).
"""

ESTILO = """
QWidget {
    font-family: "Segoe UI", "Helvetica Neue", Arial, sans-serif;
    font-size: 14px;
    color: #1f2937;
}

/* ---------- Panel lateral ---------- */
#panelLateral {
    background-color: #111827;
}
#panelLateral QLabel {
    color: #e5e7eb;
}
#etiquetaUsuario {
    font-size: 16px;
    font-weight: bold;
    padding: 6px 0;
}
#tituloSeccion {
    color: #9ca3af;
    font-size: 12px;
    font-weight: bold;
    padding-top: 10px;
}
#panelLateral QPushButton {
    background-color: #1f2937;
    color: #f9fafb;
    border: 1px solid #374151;
    border-radius: 6px;
    padding: 8px;
    text-align: left;
}
#panelLateral QPushButton:hover {
    background-color: #374151;
}
#panelLateral QPushButton#botonPrincipal {
    background-color: #2563eb;
    border: none;
    font-weight: bold;
}
#panelLateral QPushButton#botonPrincipal:hover {
    background-color: #1d4ed8;
}
#panelLateral QListWidget {
    background-color: #1f2937;
    color: #e5e7eb;
    border: 1px solid #374151;
    border-radius: 6px;
}
#panelLateral QListWidget::item {
    padding: 8px;
}
#panelLateral QListWidget::item:selected {
    background-color: #2563eb;
    color: white;
}

/* ---------- Zona de chat ---------- */
#zonaChat {
    background-color: #f3f4f6;
}
#barraArchivo {
    background-color: white;
    border: none;
    border-bottom: 1px solid #e5e7eb;
}
#textoBarraArchivo {
    font-weight: bold;
}
#botonVerArchivo {
    background-color: white;
    color: #2563eb;
    border: 1px solid #2563eb;
    border-radius: 6px;
    padding: 5px 12px;
}
#botonVerArchivo:hover {
    background-color: #eff6ff;
}
#botonVerArchivo:disabled {
    color: #9ca3af;
    border: 1px solid #d1d5db;
}
QScrollArea {
    border: none;
    background-color: #f3f4f6;
}
#contenedorMensajes {
    background-color: #f3f4f6;
}

/* Burbujas */
#burbujaUsuario {
    background-color: #2563eb;
    border-radius: 12px;
}
#burbujaUsuario QLabel {
    color: white;
}
#burbujaModelo {
    background-color: white;
    border: 1px solid #e5e7eb;
    border-radius: 12px;
}
#emisor {
    font-size: 12px;
    font-weight: bold;
}
#fecha {
    font-size: 11px;
    color: #9ca3af;
}
#burbujaUsuario #fecha {
    color: #dbeafe;
}

/* Entrada de texto */
#barraEntrada {
    background-color: white;
    border-top: 1px solid #e5e7eb;
}
QPlainTextEdit, QLineEdit {
    border: 1px solid #d1d5db;
    border-radius: 8px;
    padding: 8px;
    background-color: white;
}
QPlainTextEdit:focus, QLineEdit:focus {
    border: 1px solid #2563eb;
}
#botonEnviar, #botonLogin, #botonDialogo {
    background-color: #2563eb;
    color: white;
    border: none;
    border-radius: 8px;
    padding: 10px 18px;
    font-weight: bold;
}
#botonEnviar:hover, #botonLogin:hover, #botonDialogo:hover {
    background-color: #1d4ed8;
}
#botonEnviar:disabled {
    background-color: #93c5fd;
}
#botonSecundario {
    background-color: white;
    color: #2563eb;
    border: 1px solid #2563eb;
    border-radius: 8px;
    padding: 10px 18px;
}
#tituloLogin {
    font-size: 22px;
    font-weight: bold;
}

/* ---------- Menú desplegable (Exportar) y lista de formatos ---------- */
QMenu {
    background-color: white;
    border: 1px solid #d1d5db;
    border-radius: 6px;
    padding: 4px;
}
QMenu::item {
    padding: 7px 22px;
    border-radius: 4px;
}
QMenu::item:selected {
    background-color: #2563eb;
    color: white;
}
QMenu::separator {
    height: 1px;
    background-color: #e5e7eb;
    margin: 4px 8px;
}
QComboBox {
    border: 1px solid #d1d5db;
    border-radius: 6px;
    padding: 6px 10px;
    background-color: white;
    min-width: 220px;
}
QComboBox QAbstractItemView {
    background-color: white;
    selection-background-color: #2563eb;
    selection-color: white;
}

/* ---------- Vista previa del contenido ---------- */
#vistaCodigo {
    font-family: Consolas, "Courier New", monospace;
    font-size: 13px;
}
QTextBrowser {
    border: 1px solid #d1d5db;
    border-radius: 8px;
    padding: 8px;
    background-color: white;
}
#notaVistaPrevia {
    color: #6b7280;
    font-size: 12px;
}
"""


# ======================================================================
# TEMA OSCURO
ESTILO_OSCURO = ESTILO + """
QWidget {
    color: #e5e7eb;
}

/* Ventanas emergentes (login, mensajes de aviso) */
QDialog, QMessageBox {
    background-color: #1f2937;
}
QDialog QPushButton, QMessageBox QPushButton {
    background-color: #374151;
    color: #f9fafb;
    border: 1px solid #4b5563;
    border-radius: 6px;
    padding: 6px 14px;
}

/* Zona del chat */
#zonaChat, QScrollArea, #contenedorMensajes {
    background-color: #0f172a;
}
#barraArchivo {
    background-color: #1f2937;
    border-bottom: 1px solid #374151;
}
#textoBarraArchivo {
    color: #f9fafb;
}
#botonVerArchivo {
    background-color: #1f2937;
    color: #93c5fd;
    border: 1px solid #3b82f6;
}
#botonVerArchivo:hover {
    background-color: #374151;
}
#botonVerArchivo:disabled {
    color: #6b7280;
    border: 1px solid #374151;
}

/* Burbuja del modelo (la del usuario se queda azul) */
#burbujaModelo {
    background-color: #1f2937;
    border: 1px solid #374151;
}
#fecha {
    color: #6b7280;
}

/* Caja para escribir */
#barraEntrada {
    background-color: #1f2937;
    border-top: 1px solid #374151;
}
QPlainTextEdit, QLineEdit {
    background-color: #111827;
    border: 1px solid #374151;
    color: #f9fafb;
}

/* Botón "Registrarse" del login */
#botonSecundario {
    background-color: #1f2937;
    color: #93c5fd;
    border: 1px solid #3b82f6;
}
/* Menú desplegable, lista de formatos y vista previa */
QMenu {
    background-color: #1f2937;
    border: 1px solid #374151;
    color: #e5e7eb;
}
QMenu::separator {
    background-color: #374151;
}
QComboBox {
    background-color: #111827;
    border: 1px solid #374151;
    color: #f9fafb;
}
QComboBox QAbstractItemView {
    background-color: #1f2937;
    color: #e5e7eb;
    selection-background-color: #2563eb;
    selection-color: white;
}
QTextBrowser {
    background-color: #111827;
    border: 1px solid #374151;
    color: #f9fafb;
}
#notaVistaPrevia {
    color: #9ca3af;
}
"""
