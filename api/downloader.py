import os
import yt_dlp
from logger import log

# Directory for storing downloaded audio
AUDIO_DIR = "temp"
os.makedirs(AUDIO_DIR, exist_ok=True)

def fetch_video_title(url):
    """Extracts the title of a YouTube video using yt-dlp."""
    try:
        ydl_opts = {'quiet': True, 'noprogress': True, 'extract_flat': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return info.get("title", "Unknown Title")
    except Exception as e:
        log(f"Error fetching title for {url}: {e}")
        return None

def get_audio_filepath(entry_id, name):
    """Generate a unique file path for the downloaded audio based on video title."""
    sanitized_name = "".join(c for c in name if c.isalnum() or c in " _-").strip()  # Basic filename sanitization
    return os.path.join(AUDIO_DIR, f"{entry_id}_{sanitized_name}.mp3")

def download_audio(entry):
    """Downloads audio using yt-dlp and returns the file path."""
    output_path = get_audio_filepath(entry.id, entry.name)

    # yt-dlp options
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': output_path.rsplit(".", 1)[0],
        'quiet': True,
        'noprogress': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    try:
        log(f"Downloading audio for: {entry.url}")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([entry.url])

        if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            log(f"Download complete: {output_path}")
            return output_path
        else:
            log(f"Download failed: {output_path} is empty")
            return None
    except Exception as e:
        log(f"Error downloading {entry.url}: {e}")
        return None
