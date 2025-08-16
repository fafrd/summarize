"""
import time

from downloader import convert_to_wav, download_audio, fetch_video_title
from logger import log
from model import Entry
from summarizer import summarize_transcript
from transcriber import clean_transcript, transcribe_audio


entry = (
    Entry.select()
    .where(Entry.name == "Scrabble: Grandmaster Plays & Explains Every Move!")
    .order_by(Entry.insertion_date.desc())
    .first()
)

breakpoint()

log(f"Processing: {entry.name}")

log("Generating summary...")
summary = summarize_transcript(entry.transcription)

entry.summary = summary
entry.status = "done"
entry.save()

log(f"Completed: {entry.name}")
"""


from datetime import datetime, timezone
from typing import Literal

from peewee import IntegrityError
import structlog

from model import Entry

entries = Entry.select().order_by(Entry.insertion_date.desc()).dicts()
res = list(entries)
breakpoint()

for e in entries:
    del e['transcription']
breakpoint()
