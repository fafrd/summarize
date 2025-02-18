import os
import re
import subprocess
from logger import log

# Base directory where whisper.cpp is located
BASE_DIR = os.path.abspath("whisper.cpp")
WHISPER_PATH = os.path.join(BASE_DIR, "build/bin/whisper-cli")
WHISPER_MODEL_PATH = os.path.join(BASE_DIR, "models/ggml-large-v3-turbo.bin")

def transcribe_audio(audio_path):
    """Runs whisper.cpp to generate a transcription."""
    if not os.path.exists(audio_path):
        log(f"Audio file not found: {audio_path}")
        return None

    transcript_path = f"{audio_path}.txt"

    # Avoid re-transcribing if transcript already exists
    if os.path.exists(transcript_path) and os.path.getsize(transcript_path) > 0:
        log(f"Using existing transcript: {transcript_path}")
        with open(transcript_path, "r") as f:
            return f.read()
    
    log("Transcribing audio...")
    transcription_cmd = [
        WHISPER_PATH,
        "-m", WHISPER_MODEL_PATH,
        "-f", audio_path,
        "--entropy-thold", "2.8",
        "--beam-size", "5",
        "--max-context", "64",
        "-otxt"
    ]

    try:
        with open(transcript_path, "w") as f:
            result = subprocess.run(transcription_cmd, stdout=f, stderr=subprocess.PIPE, text=True)
            
        if result.returncode != 0:
            log(f"Whisper command failed: {result.stderr}")
            return None
        
        log(f"Transcription completed: {transcript_path}")
        with open(transcript_path, "r") as f:
            return f.read()
    except Exception as e:
        log(f"Error during transcription: {e}")
        return None


def clean_transcript(transcript: str) -> str:
    """Cleans up the transcript by removing timestamps, duplicate lines, and null bytes."""
    cleaned_lines = []
    previous_line = None

    for line in transcript.splitlines():
        # Remove null bytes
        line = line.replace("\x00", "")
        # Remove timestamps (e.g., [00:00:00.000])
        line = re.sub(r"\[.*?\]\s*", "", line)
        # Skip if it's the same as the previous line
        if line != previous_line:
            cleaned_lines.append(line)
        previous_line = line

    return "\n".join(cleaned_lines)
