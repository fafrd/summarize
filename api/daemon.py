"""Daemon to process entries in the database."""
import time
from datetime import datetime, timezone

from downloader import convert_to_wav, download_audio, fetch_video_title
from logger import log
from model import Entry
from summarizer import summarize_transcript
from transcriber import clean_transcript, transcribe_audio


def resume_interrupted_entries() -> None:
    interrupted_statuses = ["downloading", "converting", "transcribing", "summarizing"]
    interrupted_entries = Entry.select().where(Entry.status.in_(interrupted_statuses))

    for entry in interrupted_entries:
        log(f"Resuming interrupted entry: {entry.url} (was {entry.status})")
        entry.insertion_date = datetime.now(timezone.utc)
        
        if entry.transcription:
            entry.status = "summarizing"
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
                log(f"Processing: {entry.url}")

                # Fetch and update video title if needed
                if entry.name == entry.url:
                    video_title = fetch_video_title(entry.url)
                    if video_title:
                        log(f"Retrieved video title: {video_title}")
                        entry.name = video_title
                        entry.save()

                # Download phase
                if entry.status == "not_started":
                    entry.status = "downloading"
                    entry.save()

                if entry.status == "downloading":
                    audio_path = download_audio(entry)
                    if not audio_path:
                        log(f"Download failed for {entry.url}")
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
                    transcription = transcribe_audio(audio_path)
                    if not transcription:
                        log(f"Transcription failed for {audio_path}")
                        entry.status = "error"
                        entry.save()
                        continue

                    log("Cleaning transcript...")
                    transcription = clean_transcript(transcription)
                    entry.transcription = transcription
                    entry.save()
                    entry.status = "summarizing"
                    entry.save()

                # Summarize phase
                if entry.status == "summarizing":
                    log("Generating summary...")
                    summary = summarize_transcript(entry.transcription)
                    entry.summary = summary
                    entry.status = "done"
                    entry.save()
                    log(f"Completed: {entry.name}")
            except Exception as e:
                log(f"Error processing entry {entry.id}: {e}")
                entry.status = "error"
                entry.save()

        time.sleep(5)  # Polling interval


if __name__ == "__main__":
    log("Daemon started, watching for new videos...")
    process_entries()
