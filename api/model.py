"""Database model for the summarize API."""

from pathlib import Path

import structlog
from peewee import (
    CharField,
    DateTimeField,
    Model,
    SqliteDatabase,
    TextField,
)

from config import DATABASE_PATH

log = structlog.get_logger()

# Database setup
db = SqliteDatabase(DATABASE_PATH)


class BaseModel(Model):
    class Meta:
        database = db


class Entry(BaseModel):
    """Model for storing video entries."""

    name = CharField()
    status = CharField()
    url = CharField(unique=True)
    transcription = TextField(null=True)
    summary = TextField(null=True)
    insertion_date = DateTimeField(null=False)


# Ensure database exists
def initialize_db() -> None:
    if not Path.exists(DATABASE_PATH):
        log.info("Database does not exist, initializing...")
        db.connect()
        db.create_tables([Entry])
        db.close()


initialize_db()
