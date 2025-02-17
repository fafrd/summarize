import os
import subprocess
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
            if not info or "title" not in info:
                raise Exception("failed to extract")
            return info.get("title")
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

def convert_to_wav(entry):
    """Converts audio using ffmpeg to 16-bit WAV as required by whipser.cpp."""
    input_audio = get_audio_filepath(entry.id, entry.name)
    output_audio = os.path.join(AUDIO_DIR, f"{entry.id}_{entry.name}.wav")

    if not os.path.exists(output_audio):
        log(f"Converting {input_audio} to 16kHz WAV...")
        try:
            subprocess.run(["ffmpeg", "-i", input_audio, "-ar", "16000", "-ac", "1", "-c:a", "pcm_s16le", output_audio], check=True)
            log(f"Conversion complete: {output_audio}")
        except subprocess.CalledProcessError as e:
            log(f"Error converting {input_audio} to WAV: {e}")
            return None

    return output_audio