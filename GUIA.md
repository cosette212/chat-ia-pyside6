# 📘 Guía del proyecto: Chat de preguntas con IA

Esta guía explica **qué hace cada parte del proyecto, por qué se hizo así y cómo se cumple cada requisito**. Está pensada para que cualquier integrante del equipo pueda explicar el código en la presentación.

---

## Índice
1. [Cómo funciona, en una imagen](#1-cómo-funciona-en-una-imagen)
2. [Preparar el entorno en VS Code](#2-preparar-el-entorno-en-vs-code)
3. [Obtener la API key gratuita](#3-obtener-la-api-key-gratuita)
4. [Subir el proyecto a GitHub](#4-subir-el-proyecto-a-github)
5. [Explicación archivo por archivo](#5-explicación-archivo-por-archivo)
6. [La base de datos](#6-la-base-de-datos)
7. [Flujo completo de una pregunta](#7-flujo-completo-de-una-pregunta)
8. [Cómo se cumple cada requisito](#8-cómo-se-cumple-cada-requisito)
9. [Conceptos clave de PySide6](#9-conceptos-clave-de-pyside6)
10. [Problemas comunes](#10-problemas-comunes)
11. [Preguntas que pueden hacer en la presentación](#11-preguntas-que-pueden-hacer-en-la-presentación)

---

## 1. Cómo funciona, en una imagen

```
 ┌─────────────┐   usuario/contraseña   ┌──────────────┐
 │ VentanaLogin│ ─────────────────────▶ │   auth.py    │──┐
 └─────┬───────┘                        └──────────────┘  │
       │ login correcto                                   │
       ▼                                                  ▼
 ┌─────────────┐  cargar TXT/PDF  ┌────────────────┐   ┌──────────────┐
 │ VentanaChat │ ───────────────▶ │ file_loader.py │   │ database.py  │
 │  (PySide6)  │                  └────────────────┘   │   (SQLite)   │
 │             │  guardar/leer mensajes                │ chatbot.db   │
 │             │ ────────────────────────────────────▶ └──────────────┘
 │             │  pregunta + historial + texto   ┌──────────────┐    ┌─────────┐
 │             │ ──────── (QThread) ───────────▶ │ ai_client.py │──▶ │ Gemini  │
 │             │ ◀────────── respuesta ───────── └──────────────┘    │  (API)  │
 │             │  exportar                       ┌──────────────┐    └─────────┘
 │             │ ──────────────────────────────▶ │ exporter.py  │──▶ .json / .xml
 └─────────────┘                                 └──────────────┘
```

**Idea principal:** la interfaz (carpeta `app/ui`) solo dibuja y reacciona a clics. Todo el trabajo "de fondo" (base de datos, leer archivos, hablar con la IA, exportar) está en módulos separados. A esto se le llama **separación de responsabilidades**, y hace que el código sea más fácil de entender, probar y repartir entre el equipo.

---

## 2. Preparar el entorno en VS Code

**Requisitos:** Python 3.10 o superior, VS Code con la extensión **Python** (de Microsoft) y Git.

1. Descomprime el proyecto y en VS Code: **File → Open Folder…** → elige `proyecto-chatbot`.
2. Abre la terminal: **Terminal → New Terminal**.
3. Crea un **entorno virtual** (una "caja" aislada con las librerías del proyecto):
   ```bash
   python -m venv .venv
   ```
4. Actívalo:
   - Windows (PowerShell): `.venv\Scripts\activate`
     - Si sale error de "ejecución de scripts deshabilitada": `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` y vuelve a intentar.
   - Mac/Linux: `source .venv/bin/activate`

   Sabrás que está activo porque la terminal muestra `(.venv)` al inicio.
5. En VS Code: `Ctrl+Shift+P` → **Python: Select Interpreter** → elige el que dice `.venv`.
6. Instala las librerías:
   ```bash
   pip install -r requirements.txt
   ```
7. Crea tu archivo de configuración copiando la plantilla:
   - Windows: `copy .env.example .env`
   - Mac/Linux: `cp .env.example .env`

   Abre `.env` y pega tu API key (siguiente sección).
8. Prueba la conexión y ejecuta:
   ```bash
   python probar_api.py
   python main.py
   ```
9. En la app: **Registrarse** → **Ingresar** → **Nueva conversación** → elige `ejemplos/planetas.txt` → pregunta *"¿Cuál es el planeta con más lunas?"*.

| Librería | Para qué se usa |
|---|---|
| `PySide6` | Interfaz gráfica (Qt para Python) |
| `pypdf` | Extraer texto de archivos PDF |
| `requests` | Hacer la petición HTTP a la API de Gemini |
| `python-dotenv` | Leer la API key del archivo `.env` |

`sqlite3`, `json`, `xml`, `hashlib` ya vienen con Python.

---

## 3. Obtener la API key gratuita

1. Entra a **https://aistudio.google.com/apikey** con una cuenta de Google (Gmail).
2. Clic en **Create API key**.
3. Copia la clave y pégala en `.env`:
   ```
   GEMINI_API_KEY=AIza........
   GEMINI_MODEL=gemini-flash-latest
   ```
4. **No compartas la clave ni la subas a GitHub.** Por eso `.env` está en `.gitignore`. Cada integrante del equipo usa su propia clave en su `.env`.

Si el modelo da error 404 ("model not found"), corre `python probar_api.py`: muestra la lista de modelos de tu cuenta. Copia uno de la lista (por ejemplo uno que diga `flash`) en `GEMINI_MODEL`.

Si da error **429**, llegaste al límite gratuito de peticiones por minuto o por día; espera un poco.

---

## 4. Subir el proyecto a GitHub

**Una sola persona** crea el repositorio y luego invita a los demás.

### Primera vez (configurar Git)
```bash
git config --global user.name "Tu Nombre"
git config --global user.email "tu_correo@ejemplo.com"
```

### Crear el repositorio
1. En https://github.com → **New repository** → nombre `chat-ia-pyside6` → **sin** README, .gitignore ni licencia (ya los tenemos) → **Create repository**.
2. En la terminal de VS Code, dentro de la carpeta del proyecto:
   ```bash
   git init
   git add .
   git commit -m "Proyecto A: chat con IA en PySide6"
   git branch -M main
   git remote add origin https://github.com/TU_USUARIO/chat-ia-pyside6.git
   git push -u origin main
   ```
   La primera vez se abre el navegador para iniciar sesión en GitHub.
3. Antes del `commit`, revisa con `git status` que **no** aparezcan `.env` ni `chatbot.db`.

**Alternativa sin comandos:** en VS Code, barra izquierda → ícono de **Source Control** → **Publish to GitHub**.

### Que el equipo colabore
- Repo en GitHub → **Settings → Collaborators → Add people**.
- Los demás: `git clone https://github.com/TU_USUARIO/chat-ia-pyside6.git`, luego los pasos de la sección 2.
- Flujo diario:
  ```bash
  git pull                  # traer cambios de los demás ANTES de trabajar
  # ... editar ...
  git add .
  git commit -m "Describe qué cambiaste"
  git push
  ```

---

## 5. Explicación archivo por archivo

### `main.py` — punto de entrada
- Crea la `QApplication` (obligatoria en toda app Qt) y le aplica los estilos.
- La clase `Controlador` decide qué ventana mostrar:
  - `mostrar_login()` abre la ventana de login con `.exec()`. Si el login es correcto, crea la `VentanaChat`.
  - Cuando el usuario presiona **Cerrar sesión**, la ventana de chat emite la señal `sesion_cerrada` y el controlador vuelve a mostrar el login.
- `setQuitOnLastWindowClosed(False)`: por defecto Qt cierra la app cuando no queda ninguna ventana abierta. Lo desactivamos porque al pasar de chat → login hay un instante sin ventanas; nosotros decidimos cuándo salir.

### `app/database.py` — base de datos SQLite
- `sqlite3.connect("chatbot.db")` crea el archivo si no existe.
- `crear_tablas()` usa `CREATE TABLE IF NOT EXISTS` para no fallar si ya existen.
- `row_factory = sqlite3.Row` permite usar `fila["texto"]` en vez de `fila[2]`.
- **Consultas parametrizadas** (`?`): `execute("... WHERE username = ?", (username,))`. Nunca se arma el SQL pegando texto, eso evita **inyección SQL**.
- `commit()` confirma los cambios en el archivo.
- `PRAGMA foreign_keys = ON` + `ON DELETE CASCADE`: al borrar una conversación se borran solos sus mensajes.

### `app/auth.py` — usuarios y contraseñas
- **Registrar:** genera un `salt` aleatorio (`os.urandom(16)`), calcula `PBKDF2-SHA256(contraseña, salt)` 200,000 veces y guarda el hash y el salt. **La contraseña nunca se guarda.**
- **Iniciar sesión:** busca al usuario, recalcula el hash con la contraseña escrita y el salt guardado, y compara.
- ¿Por qué salt? Para que dos usuarios con la misma contraseña tengan hashes distintos y no se puedan usar tablas precalculadas.
- `hmac.compare_digest` compara sin revelar información por el tiempo que tarda.

### `app/file_loader.py` — lectura de archivos
- `.txt`: se lee con `read_text()`. Intenta UTF-8 y si falla Latin-1 (archivos de Windows con acentos).
- `.pdf`: `PdfReader` de `pypdf` recorre las páginas y `extract_text()` saca el texto. Se marca cada página (`--- Página 3 ---`) para que el modelo pueda decir en qué página está algo.
- Valida: extensión permitida, que haya texto (los PDF escaneados son imágenes y no tienen texto) y recorta si es enorme.
- El archivo **no se manda** al modelo, solo su texto (como pide el proyecto).

### `app/ai_client.py` — conexión con la IA
- Lee `GEMINI_API_KEY` y `GEMINI_MODEL` del `.env` con `load_dotenv()`.
- `preguntar()` arma un JSON con:
  - `system_instruction`: las reglas ("responde con base en el documento") **+ el texto completo del archivo**.
  - `contents`: el **historial** de la conversación (roles `user` / `model`) y al final la pregunta nueva.
- Lo envía con `requests.post(...)` y saca el texto de `candidates[0].content.parts`.
- Si algo falla (sin internet, clave mala, límite excedido) lanza `ErrorIA` con un mensaje claro que la interfaz muestra en una burbuja.
- **¿Por qué mandar el historial?** Los modelos no tienen memoria entre peticiones. Para "continuar" una conversación guardada, se le manda todo lo que ya se habló. Así funciona la reevaluación de conversaciones.

### `app/exporter.py` — JSON y XML
- `_datos_conversacion()` lee de la BD y arma un diccionario con la estructura pedida (`conversacion_id`, `archivo`, `mensajes`).
- **JSON:** `json.dump(..., ensure_ascii=False, indent=2)` conserva acentos y lo deja legible.
- **XML:** con `ElementTree` se crea `<conversacion id="1">`, `<archivo>`, `<mensajes>` y cada `<mensaje emisor="...">` con `<texto>` y `<fecha_hora>`. `ET.indent` agrega sangría. Los caracteres especiales (`&`, `<`) se escapan solos.

### `app/ui/styles.py` — apariencia
- Una hoja de estilos **QSS** (como CSS). Se aplican estilos por `objectName`, por ejemplo `#burbujaUsuario` (azul) y `#burbujaModelo` (blanco).
- En el código: `widget.setObjectName("burbujaUsuario")` conecta el widget con su estilo.

### `app/ui/login_window.py` — ventana de login
- Es un `QDialog` con dos `QLineEdit` (usuario y contraseña con `EchoMode.Password` para mostrar `••••`).
- Botón **Ingresar** → `auth.iniciar_sesion` → si es correcto, `self.accept()` cierra el diálogo con éxito.
- Botón **Registrarse** → `auth.registrar` y muestra un `QMessageBox` con el resultado.

### `app/ui/chat_window.py` — ventana principal
Tiene cuatro clases:

| Clase | Qué hace |
|---|---|
| `HiloIA(QThread)` | Consulta a la IA **en segundo plano** y emite `respuesta_lista` o `error` |
| `Burbuja(QWidget)` | Un mensaje: emisor, texto y fecha. Azul a la derecha (usuario), blanca a la izquierda (modelo). Las respuestas del modelo se muestran como Markdown |
| `CajaMensaje(QPlainTextEdit)` | Caja de texto donde **Enter envía** y **Shift+Enter** hace salto de línea |
| `VentanaChat(QMainWindow)` | Une todo: panel lateral + barra de archivo + mensajes + entrada |

Métodos importantes de `VentanaChat`:
- `cargar_lista_conversaciones()` — llena el historial del panel lateral. Se llama al entrar (**requisito: al ingresar se cargan las conversaciones**). Cada elemento guarda el `id` de la conversación oculto con `setData(Qt.UserRole, id)`.
- `nueva_conversacion()` — abre `QFileDialog`, lee el archivo y crea una conversación nueva en la BD con el texto del archivo.
- `abrir_conversacion(id)` — muestra el nombre del archivo y dibuja todos los mensajes guardados.
- `enviar_mensaje()` — guarda la pregunta, la muestra, pone "Pensando..." y lanza el `HiloIA`.
- `recibir_respuesta()` — quita "Pensando...", guarda la respuesta en la BD y la muestra.
- `_exportar()` — pide dónde guardar con `QFileDialog.getSaveFileName` y llama a `exporter`.

---

## 6. La base de datos

Archivo: `chatbot.db` (se crea solo al ejecutar). Puedes verlo con la extensión **SQLite Viewer** de VS Code o con *DB Browser for SQLite*.

```
usuarios                    conversaciones                     mensajes
─────────────────           ──────────────────────             ─────────────────────
id (PK)          ◀──┐       id (PK)              ◀──┐          id (PK)
username (UNIQUE)   └────── usuario_id (FK)         └───────── conversacion_id (FK)
password_hash               titulo                             emisor ('usuario'|'modelo')
salt                        archivo_nombre                     texto
creado_en                   archivo_ruta                       fecha_hora
                            archivo_texto
                            fecha_creacion
```

- **Relación 1 a muchos:** un usuario tiene muchas conversaciones; una conversación tiene muchos mensajes.
- Se guarda `archivo_texto` (el contenido ya extraído) para poder **continuar la conversación** aunque el archivo original se haya movido o borrado.
- `CHECK (emisor IN ('usuario','modelo'))` impide guardar emisores inválidos.

Requisito → columna:

| Pide el proyecto | Dónde está |
|---|---|
| Identificador de la conversación | `conversaciones.id` |
| Fecha y hora | `mensajes.fecha_hora`, `conversaciones.fecha_creacion` |
| Mensajes del usuario | `mensajes` con `emisor = 'usuario'` |
| Respuestas del sistema | `mensajes` con `emisor = 'modelo'` |
| Archivo asociado | `conversaciones.archivo_nombre` (+ ruta y texto) |

---

## 7. Flujo completo de una pregunta

1. El usuario escribe y presiona **Enter** → `CajaMensaje` emite `enviar` → `enviar_mensaje()`.
2. Se lee el **historial** de la BD (mensajes anteriores).
3. Si es la primera pregunta, se usa como título de la conversación.
4. Se **guarda** la pregunta (`agregar_mensaje(..., "usuario", ...)`) y se dibuja su burbuja.
5. Aparece la burbuja "Pensando..." y se bloquea la entrada.
6. Se crea `HiloIA` y se llama `start()` → en otro hilo corre `run()` → `ClienteIA.preguntar()` → petición HTTP a Gemini.
7. Al llegar la respuesta, el hilo emite `respuesta_lista(texto)`.
8. Qt ejecuta `recibir_respuesta()` en el hilo principal: se **guarda** la respuesta y se dibuja.

---

## 8. Cómo se cumple cada requisito

| Requisito | Cómo se cumple | Archivo |
|---|---|---|
| Área principal con la conversación | `QScrollArea` con burbujas | `chat_window.py` |
| Área inferior para escribir + botón enviar | `CajaMensaje` + botón **Enviar ➤** | `chat_window.py` |
| Burbujas diferenciadas usuario / modelo | Clase `Burbuja`, colores y alineación distintos | `chat_window.py`, `styles.py` |
| Panel lateral con opciones | Nueva conversación, historial, exportar, eliminar, cerrar sesión | `chat_window.py` |
| Usuario y contraseña | `VentanaLogin` + hash PBKDF2 | `login_window.py`, `auth.py` |
| Cargar TXT y PDF | `QFileDialog` + `pypdf` | `file_loader.py` |
| Mostrar nombre del archivo | Barra superior "📄 Archivo: …" | `chat_window.py` |
| Consultar un modelo de IA gratuito | Google Gemini (capa gratuita) por API REST | `ai_client.py` |
| Persistencia en BD relacional | SQLite con 3 tablas relacionadas | `database.py` |
| Cargar conversaciones al ingresar | `cargar_lista_conversaciones()` al abrir la ventana | `chat_window.py` |
| Reevaluar y continuar conversaciones | Se manda el historial completo al modelo | `ai_client.py`, `chat_window.py` |
| Exportar JSON y XML | `exportar_json`, `exportar_xml` con la estructura del enunciado | `exporter.py` |

---

## 9. Conceptos clave de PySide6

- **Widget:** cualquier elemento visual (`QLabel`, `QPushButton`, `QLineEdit`…).
- **Layout:** acomoda widgets automáticamente. `QVBoxLayout` = vertical, `QHBoxLayout` = horizontal. `addStretch()` agrega un "resorte" que empuja los elementos.
- **Señales y slots:** forma en que Qt conecta eventos con funciones.
  ```python
  boton.clicked.connect(self.enviar_mensaje)   # cuando se haga clic, llama a enviar_mensaje
  ```
  También se pueden crear señales propias: `respuesta_lista = Signal(str)`.
- **Hilo principal y QThread:** la interfaz solo se puede modificar desde el hilo principal. Las tareas lentas (como llamar a la IA) van en un `QThread` y devuelven resultados con señales. Si no se hiciera así, la ventana se congelaría mientras espera.
- **QDialog vs QMainWindow:** `QDialog` es una ventana temporal que regresa un resultado (login); `QMainWindow` es la ventana principal.
- **QSS:** estilos tipo CSS con `app.setStyleSheet(...)`.

---

## 10. Problemas comunes

| Problema | Solución |
|---|---|
| `ModuleNotFoundError: No module named 'PySide6'` | No está activo el `.venv` o no se instaló: activa el entorno y corre `pip install -r requirements.txt`. Revisa el intérprete en VS Code |
| "Falta GEMINI_API_KEY" | No existe `.env` o está mal escrito. Debe llamarse exactamente `.env` (no `.env.txt`) |
| Error 400 / API key not valid | Clave mal copiada; genera otra en AI Studio |
| Error 404 model not found | Cambia `GEMINI_MODEL` por uno de la lista de `python probar_api.py` |
| Error 429 | Límite gratuito alcanzado; espera unos minutos |
| "El archivo no contiene texto legible" | Es un PDF escaneado (imagen). Usa un PDF con texto seleccionable |
| Quiero empezar de cero con la BD | Cierra la app y borra `chatbot.db` |

---

## 11. Preguntas que pueden hacer en la presentación

- **¿Por qué SQLite?** Viene incluido en Python, no necesita servidor y la BD es un solo archivo; suficiente para una app de escritorio de un solo usuario a la vez.
- **¿Cómo protegen las contraseñas?** Con hash PBKDF2-SHA256 y salt aleatorio por usuario; la contraseña nunca se guarda.
- **¿Cómo "recuerda" el modelo la conversación?** No la recuerda: en cada pregunta se le manda el historial guardado en la BD junto con el texto del archivo.
- **¿Por qué usan un hilo?** Para que la ventana no se congele mientras se espera la respuesta de la API.
- **¿Qué pasa si se mueve o borra el archivo original?** Nada, porque el texto extraído está guardado en la BD.
- **¿Cómo evitan inyección SQL?** Con consultas parametrizadas (`?`).
- **¿Dónde está la API key?** En `.env`, que está en `.gitignore`, así no se publica en GitHub.
