# 💬 Chat de preguntas sobre archivos con IA (Proyecto A)

Aplicación de escritorio en **Python + PySide6** para cargar un archivo **TXT o PDF**, hacerle preguntas a un modelo de IA (**Google Gemini**, capa gratuita), guardar las conversaciones en **SQLite** y exportarlas a **JSON** o **XML**.

## Funcionalidades
- Login con usuario y contraseña (contraseñas con hash PBKDF2 + salt)
- Interfaz tipo chat con burbujas para el usuario y el modelo, y panel lateral de opciones
- Carga de archivos `.txt` y `.pdf` (el PDF se convierte a texto)
- Respuestas del modelo basadas en el archivo cargado
- Historial en base de datos: al iniciar sesión se cargan tus conversaciones y puedes continuarlas
- Exportación a JSON y XML

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
    ├── file_loader.py   # lectura de TXT y PDF
    ├── ai_client.py     # conexión con Gemini (API REST)
    ├── exporter.py      # exportar a JSON / XML
    └── ui/
        ├── styles.py        # estilos QSS
        ├── login_window.py  # ventana de login
        └── chat_window.py   # ventana principal del chat
```

La explicación completa del código está en **[GUIA.md](GUIA.md)**.
