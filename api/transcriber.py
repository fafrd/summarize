"""Transcribe audio files using whisper.cpp."""

import re
import subprocess
from pathlib import Path

import structlog

from config import (
    WHISPER_BEAM_SIZE,
    WHISPER_BINARY,
    WHISPER_ENTROPY_THRESHOLD,
    WHISPER_MAX_CONTEXT,
    WHISPER_MODEL,
)

log = structlog.get_logger()


def transcribe_audio(audio_path: str) -> str | None:
    """Run whisper.cpp to generate a transcription.

    Args:
        audio_path (str): Path to the audio file.

    Returns:
        str: Transcription of the audio.

    """
    if not Path.exists(audio_path):
        log.error(f"Audio file not found: {audio_path}")
        return None

    transcript_path = Path(f"{audio_path}.txt")

    # Avoid re-transcribing if transcript already exists
    if transcript_path.exists() and transcript_path.stat().st_size > 0:
        log.info(f"Using existing transcript: {transcript_path}")
        with Path.open(transcript_path) as f:
            return f.read()

    log.info("Transcribing audio...")
    transcription_cmd = [
        str(WHISPER_BINARY),
        "-m",
        str(WHISPER_MODEL),
        "-f",
        str(audio_path),
        "--entropy-thold",
        str(WHISPER_ENTROPY_THRESHOLD),
        "--beam-size",
        str(WHISPER_BEAM_SIZE),
        "--max-context",
        str(WHISPER_MAX_CONTEXT),
        "-otxt",
    ]

    try:
        with Path.open(transcript_path, "w") as f:
            result = subprocess.run(
                transcription_cmd,
                stdout=f,
                stderr=subprocess.PIPE,
                text=True,
                check=False,
            )

        if result.returncode != 0:
            log.error(f"Whisper command failed: {result.stderr}")
            return None

        log.info(f"Transcription completed: {transcript_path}")
        with Path.open(transcript_path) as f:
            return f.read()
    except Exception as e:
        log.exception(f"Error during transcription: {e}")
        return None


def clean_transcript(transcript: str) -> str:
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
