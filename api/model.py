"""Database model for the summarize API."""

from pathlib import Path

from peewee import (
    CharField,
    DateTimeField,
    Model,
    SqliteDatabase,
    TextField,
)

from logger import log

# Database setup
DB_PATH = Path("summarize.db")
db = SqliteDatabase(DB_PATH)


class BaseModel(Model):
    """Base model for other models to inherit from."""

    class Meta:
        """Meta class for the base model."""

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
    """Initialize the database."""
    if not Path.exists(DB_PATH):
        log("Database does not exist, initializing...")
        db.connect()
        db.create_tables([Entry])
        db.close()


initialize_db()
