import os
import logging
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN no está configurado. Crea un archivo .env con BOT_TOKEN=tu_token_aqui")

DOWNLOAD_DIR = os.path.join(os.path.expanduser("~"), "bot_videos")
MAX_FILE_SIZE_MB = 50
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

SUPPORTED_DOMAINS = [
    "youtube.com", "youtu.be",
    "tiktok.com", "vm.tiktok.com",
    "facebook.com", "fb.watch",
    "instagram.com", "instagr.am",
]

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)

QUALITY_FORMATS = [
    "best[height<=1080][ext=mp4]/best[height<=1080]/bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]",
    "best[height<=720][ext=mp4]/best[height<=720]/bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]",
    "best[height<=480][ext=mp4]/best[height<=480]/bestvideo[height<=480][ext=mp4]+bestaudio[ext=m4a]",
    "bestaudio/best",
]

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)
