"""Shared helper functions for the summarize API."""

from datetime import datetime, timezone
from pathlib import Path

import structlog
from peewee import IntegrityError

from config import TEMP_DIR
from model import Entry

log = structlog.get_logger()


def get_transcript_path(entry: Entry) -> Path:
    """Get the path to the transcript file for an entry.

    Args:
        entry: Entry object representing the video.

    Returns:
        Path to the transcript file.

    """
    return TEMP_DIR / f"{entry.id}_{entry.name}.wav.txt"


def create_or_reset_entry(url: str) -> tuple[Entry, bool]:
    """Create a new entry or reset an existing error entry.

    Args:
        url: YouTube video URL.

    Returns:
        tuple: (Entry object, is_new: bool)

    Raises:
        IntegrityError: If entry already exists with non-error status.

    """
    try:
        entry = Entry.create(
            name=url,
            status="not_started",
            url=url,
            transcription=None,
            insertion_date=datetime.now(timezone.utc),
        )
        log.info(f"Created new entry for {url}")
        return entry, True
    except IntegrityError:
        existing_entry = Entry.get(Entry.url == url)
        if existing_entry.status == "error":
            log.info(f"Resetting error video {url} to not_started")
            existing_entry.status = "not_started"
            existing_entry.save()
            return existing_entry, False
        else:
            log.warning(f"Entry with URL {url} already exists with status {existing_entry.status}")
            raise


def sanitize_filename(name: str) -> str:
    """Sanitize a string for use in filenames.

    Args:
        name: String to sanitize.

    Returns:
        Sanitized string safe for use in filenames.

    """
    sanitized = "".join(c for c in name if c.isalnum() or c in " _-").strip()
    return sanitized or "unnamed"
