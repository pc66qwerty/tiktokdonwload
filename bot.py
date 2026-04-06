import logging
from pathlib import Path

from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from config import BOT_TOKEN, ALLOWED_USERS, logger
from downloader import (
    DownloadError,
    FileTooLargeError,
    InvalidURLError,
    cleanup,
    download_video,
    is_valid_url,
)

# ──────────────────────────────────────────────
# Mensajes
# ──────────────────────────────────────────────

MSG_WELCOME = (
    "👋 *botcito pa descargar videos.*\n\n"
    "Solo videos de sin Marca de Agua:\n"
    "• 🎬 YouTube\n"
    "• 🎵 TikTok\n"
    "• 📘 Facebook\n"
    "• 📸 Instagram\n\n"
    "Pasa Link pa descargar :/.\n"
    "Usa /help si necesitas aiuda :V."
)

MSG_HELP = (
    "ℹ️ *Cómo usarme*\n\n"
    "1. Copia el link del video que quieras descargar.\n"
    "2. Pégalo aquí como mensaje de texto.\n"
    "3. Espera unos segundos mientras lo proceso.\n\n"
    "*Plataformas soportadas:*\n"
    "YouTube · TikTok · Facebook · Instagram\n\n"
    "*Límites:*\n"
    "• Tamaño máximo: 50 MB (límite de Telegram)\n"
    "• Solo videos públicos\n\n"
    "*Calidades que intento (en orden):*\n"
    "1080p → 720p → 480p → solo audio MP3"
)

MSG_DOWNLOADING = "⏳ Descargando tu video, espera un momento..."
MSG_SUCCESS_VIDEO = "Descargado con: @dessstikbot"
MSG_SUCCESS_AUDIO = "Descargado con: @dessstikbot"
MSG_TOO_LARGE = (
    "⚠️ El video es demasiado grande para Telegram (límite 50 MB).\n"
    "Intenta con un video más corto o en menor resolución."
)
MSG_INVALID_LINK = (
    "🔗 Eso no parece un link válido.\n"
    "Mándame una URL de YouTube, TikTok, Facebook o Instagram."
)
MSG_GENERAL_ERROR = (
    "❌ No pude descargar ese video.\n"
    "Verifica que el link sea válido y que el video sea público."
)
MSG_UNAUTHORIZED = "⛔ No tienes permiso para usar este bot."

# ──────────────────────────────────────────────
# Autorización
# ──────────────────────────────────────────────

def is_authorized(update: Update) -> bool:
    if not ALLOWED_USERS:
        return True  # Si no hay lista configurada, bot abierto
    return update.effective_user.id in ALLOWED_USERS


# ──────────────────────────────────────────────
# Handlers
# ──────────────────────────────────────────────

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_authorized(update):
        await update.message.reply_text(MSG_UNAUTHORIZED)
        return
    await update.message.reply_text(MSG_WELCOME, parse_mode="Markdown")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_authorized(update):
        await update.message.reply_text(MSG_UNAUTHORIZED)
        return
    await update.message.reply_text(MSG_HELP, parse_mode="Markdown")


async def handle_url(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_authorized(update):
        await update.message.reply_text(MSG_UNAUTHORIZED)
        return

    message = update.message
    url = message.text.strip()

    if not is_valid_url(url):
        await message.reply_text(MSG_INVALID_LINK)
        return

    status_msg = await message.reply_text(MSG_DOWNLOADING)
    await context.bot.send_chat_action(chat_id=message.chat_id, action=ChatAction.UPLOAD_VIDEO)

    file_path: Path | None = None
    try:
        file_path, is_audio = await download_video(url)

        if is_audio:
            await context.bot.send_chat_action(chat_id=message.chat_id, action=ChatAction.UPLOAD_DOCUMENT)
            with open(file_path, "rb") as f:
                await message.reply_audio(audio=f, caption=MSG_SUCCESS_AUDIO)
        else:
            await context.bot.send_chat_action(chat_id=message.chat_id, action=ChatAction.UPLOAD_VIDEO)
            with open(file_path, "rb") as f:
                await message.reply_video(video=f, caption=MSG_SUCCESS_VIDEO, supports_streaming=True)

    except InvalidURLError:
        await status_msg.edit_text(MSG_INVALID_LINK)

    except FileTooLargeError:
        await status_msg.edit_text(MSG_TOO_LARGE)

    except DownloadError as e:
        logger.error("DownloadError para %s: %s", url, e)
        await status_msg.edit_text(MSG_GENERAL_ERROR)

    except Exception as e:
        logger.exception("Error inesperado al procesar %s: %s", url, e)
        await status_msg.edit_text(MSG_GENERAL_ERROR)

    else:
        await status_msg.delete()

    finally:
        if file_path and file_path.exists():
            cleanup(file_path)


async def handle_non_url(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_authorized(update):
        await update.message.reply_text(MSG_UNAUTHORIZED)
        return
    await update.message.reply_text(MSG_INVALID_LINK)


# ──────────────────────────────────────────────
# Entry point
# ──────────────────────────────────────────────

def main() -> None:
    logger.info("Iniciando bot...")

    app = (
        Application.builder()
        .token(BOT_TOKEN)
        .build()
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))

    url_filter = filters.Regex(r"https?://")
    app.add_handler(MessageHandler(filters.TEXT & url_filter, handle_url))
    app.add_handler(MessageHandler(filters.TEXT & ~url_filter, handle_non_url))

    logger.info("Bot en ejecución. Presiona Ctrl+C para detener.")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
