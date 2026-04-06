# Bot Descargador de Videos para Telegram

Bot de Telegram que descarga videos de YouTube, TikTok, Facebook e Instagram usando `yt-dlp`.

## Características

- Detecta automáticamente la plataforma por la URL
- Descarga en la mejor calidad disponible bajo 50 MB
- Fallback automático: 1080p → 720p → 480p → MP3
- Evita marca de agua en TikTok
- Limpia archivos temporales después de cada envío
- Mensajes de estado en español

---

## Requisitos previos

- Python 3.11 o superior
- `ffmpeg` instalado y en el PATH (necesario para mezclar video+audio y convertir a MP3)
  - **Windows:** descarga desde https://ffmpeg.org/download.html o instala con `choco install ffmpeg`
  - **Linux/macOS:** `sudo apt install ffmpeg` / `brew install ffmpeg`

---

## Instalación local

```bash
# 1. Clona o descarga el proyecto
cd bot-downloader

# 2. Crea un entorno virtual
python -m venv venv
source venv/bin/activate        # Linux/macOS
venv\Scripts\activate           # Windows

# 3. Instala dependencias
pip install -r requirements.txt

# 4. Configura el token
cp .env.example .env
# Edita .env y reemplaza "tu_token_aqui" con el token de @BotFather
```

### Obtener el token de Telegram

1. Abre Telegram y busca `@BotFather`
2. Envía `/newbot` y sigue las instrucciones
3. Copia el token y pégalo en el archivo `.env`

---

## Ejecutar el bot

```bash
python bot.py
```

El bot quedará escuchando mensajes. Presiona `Ctrl+C` para detenerlo.

---

## Deploy en Railway

1. Crea una cuenta en [railway.app](https://railway.app) y conecta tu repositorio de GitHub.
2. En el panel de Railway, ve a **Variables** y agrega:
   ```
   BOT_TOKEN=tu_token_aqui
   ```
3. Railway detecta automáticamente Python. Agrega un archivo `Procfile` si es necesario:
   ```
   worker: python bot.py
   ```
4. Haz deploy. Railway arrancará el bot automáticamente.

> **Nota:** Railway provee un sistema de archivos efímero, por lo que `/tmp/bot_videos/` funciona perfectamente para almacenamiento temporal.

---

## Deploy en Render

1. Crea una cuenta en [render.com](https://render.com).
2. Crea un nuevo **Background Worker** apuntando a tu repositorio.
3. Configura:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python bot.py`
4. En **Environment Variables**, agrega `BOT_TOKEN`.
5. Haz deploy.

---

## Estructura del proyecto

```
bot-downloader/
├── bot.py           # Handlers de Telegram y punto de entrada
├── downloader.py    # Lógica de descarga con yt-dlp
├── config.py        # Configuración global y logging
├── requirements.txt # Dependencias con versiones fijas
├── .env.example     # Plantilla de variables de entorno
└── README.md        # Este archivo
```

---

## Plataformas soportadas

| Plataforma  | Dominios                            |
|-------------|-------------------------------------|
| YouTube     | youtube.com, youtu.be               |
| TikTok      | tiktok.com, vm.tiktok.com           |
| Facebook    | facebook.com, fb.watch              |
| Instagram   | instagram.com, instagr.am           |

---

## Solución de problemas

| Problema | Solución |
|---|---|
| `BOT_TOKEN no está configurado` | Crea el archivo `.env` con tu token |
| Video demasiado grande | El video supera 50 MB incluso en 480p; intenta con uno más corto |
| Error en TikTok | Asegúrate de que el video sea público; los privados no se pueden descargar |
| `ffmpeg not found` | Instala ffmpeg y asegúrate de que esté en el PATH |
| Error de Instagram | Instagram limita el acceso; funciona mejor con posts públicos sin iniciar sesión |
