import time
from model import Entry
from downloader import download_audio, fetch_video_title, convert_to_wav
from transcriber import transcribe_audio, clean_transcript
from logger import log

def process_entries():
    """Main processing loop."""
    while True:
        entry = Entry.select().where(Entry.status == "not_started").order_by(Entry.insertion_date.asc()).first()
        
        if entry:
            try:
                log(f"Processing: {entry.url}")

                # Fetch and update video title
                video_title = fetch_video_title(entry.url)
                if video_title:
                    log(f"Retrieved video title: {video_title}")
                    entry.name = video_title
                    entry.save()

                entry.status = "downloading"
                entry.save()
                audio_path = download_audio(entry)
                if not audio_path:
                    log(f"Download failed for {entry.url}")
                    entry.status = "not_started"
                    entry.save()
                    continue

                entry.status = "converting"
                entry.save()
                audio_path = convert_to_wav(entry)

                entry.status = "transcribing"
                entry.save()
                transcription = transcribe_audio(audio_path)
                if not transcription:
                    log(f"Transcription failed for {audio_path}")
                    entry.status = "not_started"
                    entry.save()
                    continue

                log("Cleaning transcript...")
                transcription = clean_transcript(transcription)

                entry.transcription = transcription
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
