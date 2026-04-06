import os
import asyncio
import logging
import re
from pathlib import Path
from urllib.parse import urlparse

import yt_dlp

from config import (
    DOWNLOAD_DIR,
    MAX_FILE_SIZE_BYTES,
    QUALITY_FORMATS,
    SUPPORTED_DOMAINS,
    USER_AGENT,
)

logger = logging.getLogger(__name__)


class DownloadError(Exception):
    pass


class FileTooLargeError(Exception):
    pass


class InvalidURLError(Exception):
    pass


def is_valid_url(url: str) -> bool:
    try:
        result = urlparse(url.strip())
        return result.scheme in ("http", "https") and bool(result.netloc)
    except Exception:
        return False


def is_supported_platform(url: str) -> bool:
    try:
        netloc = urlparse(url.strip()).netloc.lower()
        netloc = netloc.removeprefix("www.")
        return any(domain in netloc for domain in SUPPORTED_DOMAINS)
    except Exception:
        return False


def _build_ydl_opts(fmt: str, output_template: str, is_audio_only: bool) -> dict:
    opts = {
        "format": fmt,
        "outtmpl": output_template,
        "quiet": True,
        "no_warnings": False,
        "noplaylist": True,
        "http_headers": {"User-Agent": USER_AGENT},
        "extractor_args": {
            "tiktok": {"webpage_download": ["1"]},
        },
        "socket_timeout": 30,
        "retries": 3,
    }

    if is_audio_only:
        opts["postprocessors"] = [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ]

    return opts


def _find_downloaded_file(output_template: str) -> Path | None:
    base = Path(output_template.replace("%(ext)s", "*").replace("%(title)s", "*"))
    parent = base.parent
    stem_pattern = base.stem

    # yt-dlp replaces the template; scan the directory for the newest file
    candidates = sorted(parent.glob("*"), key=lambda p: p.stat().st_mtime, reverse=True)
    for f in candidates:
        if f.is_file() and f.suffix.lower() in (".mp4", ".webm", ".mkv", ".mp3", ".m4a"):
            return f
    return None


async def download_video(url: str) -> tuple[Path, bool]:
    """
    Downloads a video, trying quality levels from highest to lowest.

    Returns:
        (path_to_file, is_audio_only)

    Raises:
        InvalidURLError, FileTooLargeError, DownloadError
    """
    if not is_valid_url(url):
        raise InvalidURLError("URL inválida")

    if not is_supported_platform(url):
        raise InvalidURLError("Plataforma no soportada")

    Path(DOWNLOAD_DIR).mkdir(parents=True, exist_ok=True)

    last_error: Exception | None = None

    for idx, fmt in enumerate(QUALITY_FORMATS):
        is_audio_only = idx == len(QUALITY_FORMATS) - 1
        output_template = os.path.join(DOWNLOAD_DIR, "%(id)s_%(title).60s.%(ext)s")

        ydl_opts = _build_ydl_opts(fmt, output_template, is_audio_only)

        logger.info("Intentando formato %d: %s | url=%s", idx + 1, fmt, url)

        try:
            downloaded_path = await asyncio.to_thread(_run_ydl, url, ydl_opts, output_template)
        except yt_dlp.utils.DownloadError as e:
            last_error = e
            logger.warning("Fallo formato %d: %s", idx + 1, e)
            continue

        if downloaded_path is None:
            last_error = DownloadError("No se encontró el archivo descargado")
            continue

        file_size = downloaded_path.stat().st_size
        logger.info("Descargado: %s (%.1f MB)", downloaded_path.name, file_size / 1024 / 1024)

        if file_size > MAX_FILE_SIZE_BYTES:
            downloaded_path.unlink(missing_ok=True)
            logger.info("Archivo supera 50 MB, reintentando en menor calidad...")
            continue

        return downloaded_path, is_audio_only

    # All formats exceeded 50 MB or failed
    if last_error and "too large" in str(last_error).lower():
        raise FileTooLargeError("El video supera el límite de 50 MB en todas las calidades")

    raise FileTooLargeError("El video es demasiado grande para enviarlo por Telegram (límite 50 MB)")


def _run_ydl(url: str, ydl_opts: dict, output_template: str) -> Path | None:
    """Blocking yt-dlp call executed inside a thread."""
    parent_dir = Path(os.path.dirname(output_template))

    # Collect files before download to find the new one reliably
    before = set(parent_dir.glob("*"))

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    after = set(parent_dir.glob("*"))
    new_files = [
        f for f in (after - before)
        if f.is_file() and f.suffix.lower() in (".mp4", ".webm", ".mkv", ".mp3", ".m4a")
    ]

    if new_files:
        # Return the largest new file (handles merged video+audio)
        return max(new_files, key=lambda p: p.stat().st_size)

    return _find_downloaded_file(output_template)


def cleanup(path: Path) -> None:
    try:
        path.unlink(missing_ok=True)
        logger.info("Archivo temporal eliminado: %s", path.name)
    except Exception as e:
        logger.warning("No se pudo eliminar %s: %s", path, e)
