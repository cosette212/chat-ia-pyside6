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
    border-bottom: 1px solid #e5e7eb;
    padding: 10px 16px;
    font-weight: bold;
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
#botonEnviar, #botonLogin {
    background-color: #2563eb;
    color: white;
    border: none;
    border-radius: 8px;
    padding: 10px 18px;
    font-weight: bold;
}
#botonEnviar:hover, #botonLogin:hover {
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
"""
