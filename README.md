# Chat de preguntas sobre archivos con IA (Proyecto A)

Aplicación de escritorio en **Python + PySide6** para cargar un archivo (**PDF, Word, Excel, TXT, CSV, Markdown, JSON, XML, HTML...**), hacerle preguntas a un modelo de IA (**Google Gemini**, capa gratuita), guardar las conversaciones en **SQLite** y exportarlas a **JSON y XML**.

## Funcionalidades
- Login con usuario y contraseña (contraseñas con hash PBKDF2 + salt)
- Interfaz tipo chat con burbujas para el usuario y el modelo, y panel lateral de opciones
- Carga de archivos `.pdf`, `.docx`, `.xlsx`, `.html`/`.htm`, `.txt`, `.md`, `.csv`, `.tsv`, `.json`, `.xml` y `.log` (todos se convierten a texto)
- **Ver contenido** del archivo cargado: botón en la barra superior que muestra el texto extraído (lo que recibe el modelo)
- Respuestas del modelo basadas en el archivo cargado
- Historial en base de datos: al iniciar sesión se cargan tus conversaciones y puedes continuarlas
- Exportación a JSON y XML desde un botón con menú desplegable.
- **Ver contenido** de la exportación: vista previa de la conversación en el formato elegido antes de guardarla


## Login mejorado (Integrante 2 -- Gabriela)

**Archivo:** `app/ui/login_window.py` (y carpeta `assets/`)

- **Botón de ojo:** Dentro del campo de contraseña hay un ojo que alterna entre mostrar y ocultar el texto. Con la contraseña oculta aparece el ojo cerrado, al mostrarla se abre.
- **Confirmar contraseña:** Al registrarse hay que escribir la contraseña dos veces. Si no coinciden, se muestra un error y no se crea el usuario.
- **Logo:** La ventana de login muestra un logo guardado en `assets/logo.png`.
- **Ventana ajustada:** Se agrandó el tamaño de la ventana para que quepan todos los elementos.

* Icono del ojo cerrado: <a href="https://www.flaticon.es/iconos-gratis/ojo-de-cerca" title="ojo de cerca iconos">Ojo de cerca iconos creados por sonnycandra - Flaticon</a>


### Preguntas sugeridas y botón Copiar (Integrante 5)

**Archivo:** `app/ui/chat_window.py` (clases `Burbuja` y `VentanaChat`)

- **Preguntas sugeridas:** al abrir una conversación sin mensajes aparecen tres
  botones ("Resume el archivo", "Puntos principales", "Hazme un quiz de 3
  preguntas"). Al hacer clic, la pregunta se envía automáticamente al modelo.
  Los botones se ocultan después de la primera pregunta.
- **Botón Copiar:** cada respuesta del modelo tiene un botón "📋 Copiar" que
  guarda el texto en el portapapeles y muestra "✓ Copiado" por un momento.

## Instalación rápida
```bash
python -m venv .venv
# Windows:  .venv\Scripts\activate
# Mac/Linux: source .venv/bin/activate
pip install -r requirements.txt
copy .env.example .env      # en Mac/Linux: cp .env.example .env
# edita .env y pega tu API key de https://aistudio.google.com/apikey
python probar_api.py        # (opcional) verifica la API key
python main.py
```

## Estructura
```
proyecto-chatbot/
├── main.py              # punto de entrada (login -> chat)
├── probar_api.py        # diagnóstico de la API key / modelos
├── requirements.txt
├── .env.example         # plantilla de configuración (la real, .env, no se sube)
├── ejemplos/planetas.txt
└── app/
    ├── database.py      # SQLite: usuarios, conversaciones, mensajes
    ├── auth.py          # registro e inicio de sesión
    ├── file_loader.py   # lectura de PDF, Word, Excel, HTML y archivos de texto
    ├── ai_client.py     # conexión con Gemini (API REST)
    ├── exporter.py      # exportar a JSON / XML
    └── ui/
        ├── styles.py        # estilos QSS
        ├── login_window.py  # ventana de login
        ├── vista_previa.py  # ventanas "Ver contenido" (archivo cargado y vista previa de la exportación)
        └── chat_window.py   # ventana principal del chat
```

