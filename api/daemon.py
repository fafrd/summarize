"""Daemon to process entries in the database."""
import time
from datetime import datetime, timezone
from pathlib import Path

import structlog

from config import POLLING_INTERVAL, TEMP_DIR
from downloader import convert_to_wav, download_audio, fetch_video_title, get_audio_filepath
from helpers import get_transcript_path
from model import Entry
from summarizer import summarize_transcript
from transcriber import clean_transcript, transcribe_audio

log = structlog.get_logger()


def resume_interrupted_entries() -> None:
    interrupted_statuses = ["downloading", "converting", "transcribing", "summarizing"]
    interrupted_entries = Entry.select().where(Entry.status.in_(interrupted_statuses))

    for entry in interrupted_entries:
        log.info(f"Resuming interrupted entry: {entry.url} (was {entry.status})")

        if entry.status == "transcribing":
            # Always remove transcription file when resuming from transcribing state
            # This ensures incomplete transcriptions are regenerated
            transcript_path = get_transcript_path(entry)
            if transcript_path.exists():
                transcript_path.unlink()
                log.info(f"Removed incomplete transcription: {transcript_path}")
            entry.status = "transcribing"

        entry.save()


def process_entries() -> None:
    resume_interrupted_entries()

    while True:
        entry = (
            Entry.select()
            .where(Entry.status.not_in(["done", "error"]))
            .order_by(Entry.insertion_date.asc())
            .first()
        )

        if entry:
            try:
                log.info(f"Processing: {entry.url}")

                # Fetch and update video title if needed
                if entry.name == entry.url:
                    video_title = fetch_video_title(entry.url)
                    if video_title:
                        log.info(f"Retrieved video title: {video_title}")
                        entry.name = video_title
                        entry.save()

                # Download phase
                if entry.status == "not_started":
                    entry.status = "downloading"
                    entry.save()

                if entry.status == "downloading":
                    audio_path = download_audio(entry)
                    if not audio_path:
                        log.error(f"Download failed for {entry.url}")
                        entry.status = "error"
                        entry.save()
                        continue
                    entry.status = "converting"
                    entry.save()

                # Convert phase
                if entry.status == "converting":
                    audio_path = convert_to_wav(entry)
                    entry.status = "transcribing"
                    entry.save()

                # Transcribe phase
                if entry.status == "transcribing":
                    audio_path = convert_to_wav(entry)

                    # Remove any existing transcript file to ensure fresh transcription
                    # This handles cases where transcription was interrupted
                    transcript_path = get_transcript_path(entry)
                    if transcript_path.exists():
                        transcript_path.unlink()
                        log.info(f"Removed existing transcript file: {transcript_path}")

                    transcription = transcribe_audio(audio_path)
                    if not transcription:
                        log.error(f"Transcription failed for {audio_path}")
                        entry.status = "error"
                        entry.save()
                        continue

                    log.info("Cleaning transcript...")
                    transcription = clean_transcript(transcription)
                    entry.transcription = transcription
                    entry.save()
                    entry.status = "summarizing"
                    entry.save()

                # Summarize phase
                if entry.status == "summarizing":
                    log.info("Generating summary...")
                    summary = summarize_transcript(entry.transcription)
                    entry.summary = summary
                    entry.status = "done"
                    entry.save()
                    log.info(f"Completed: {entry.name}")
            except Exception as e:
                log.exception(f"Error processing entry {entry.id}: {e}")
                entry.status = "error"
                entry.save()

        time.sleep(POLLING_INTERVAL)


if __name__ == "__main__":
    log.info("Daemon started, watching for new videos...")
    process_entries()
