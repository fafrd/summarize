"""Downloads audio from YouTube using yt-dlp and converts it to 16-bit WAV."""

import subprocess
import traceback
from pathlib import Path

import structlog
import yt_dlp

from model import Entry

log = structlog.get_logger()

# Directory for storing downloaded audio
AUDIO_DIR = Path("temp")
AUDIO_DIR.mkdir(parents=True, exist_ok=True)


def fetch_video_title(url: str) -> str | None:
    """Extract the title of a YouTube video using yt-dlp.

    Args:
        url (str): URL of the YouTube video.

    Returns:
        str: Title of the video.

    """
    try:
        ydl_opts = {"quiet": True, "noprogress": True, "extract_flat": True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            if not info:
                msg = "failed to extract_info from youtube"
                raise Exception(msg)
            title = info.get("title", "")

            # Sanitize
            return title.replace("/", "_")
    except Exception as e:
        log.exception(f"Error fetching title for {url}: {e}")
        return None


def get_audio_filepath(entry_id: int, name: str) -> Path:
    """Generate a unique file path for the downloaded audio based on video title.

    Args:
        entry_id (int): ID of the entry in the database.
        name (str): Title of the video

    Returns:
        Path: File path for the downloaded audio.

    """
    sanitized_name = "".join(
        c for c in name if c.isalnum() or c in " _-"
    ).strip()  # Basic filename sanitization
    return AUDIO_DIR / f"{entry_id}_{sanitized_name}.mp3"


def download_audio(entry: Entry) -> str | None:
    """Download audio using yt-dlp and returns the file path.

    Args:
        entry (str): Entry object representing the video.

    """
    output_path = get_audio_filepath(entry.id, entry.name)

    # yt-dlp options
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": str(output_path).rsplit(".", 1)[0],
        "quiet": True,
        "noprogress": True,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            },
        ],
    }

    try:
        log.info(f"Downloading audio for: {entry.url}")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([entry.url])
    except yt_dlp.utils.DownloadError as e:
        log.exception(f"Error downloading {entry.url}: {e}")
        return None
    except yt_dlp.utils.ExtractorError as e:
        log.exception(f"Error extracting info from {entry.url}: {e}")
        return None
    except OSError as e:
        log.exception(f"OS error while downloading {entry.url}: {e}")
        return None

    try:
        if not output_path.exists():
            raise FileNotFoundError(f"Downloaded file not found at {output_path}")

        if output_path.stat().st_size <= 0:
            raise OSError(f"Downloaded file is empty: {output_path}")

        return output_path

    except Exception as e:
        traceback.print_exc()

        (f"Error checking download: {e}")
        return None


def convert_to_wav(entry: str) -> str | None:
    """Convert audio using ffmpeg to 16-bit WAV as required by whipser.cpp.

    Args:
        entry (Entry): Entry object representing the video.

    """
    input_audio = get_audio_filepath(entry.id, entry.name)
    output_audio = AUDIO_DIR / f"{entry.id}_{entry.name}.wav"

    if not Path.exists(output_audio):
        log.debug(f"Converting {input_audio} to 16kHz WAV...")
        try:
            subprocess.run(
                [
                    "ffmpeg",
                    "-i",
                    input_audio,
                    "-ar",
                    "16000",
                    "-ac",
                    "1",
                    "-c:a",
                    "pcm_s16le",
                    output_audio,
                ],
                check=True,
            )
            log.info(f"Conversion complete: {output_audio}")
        except subprocess.CalledProcessError as e:
            log.exception(f"Error converting {input_audio} to WAV: {e}")
            return None

    return output_audio
