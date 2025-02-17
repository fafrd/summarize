from peewee import SqliteDatabase, Model, CharField, TextField, DateTimeField, IntegrityError
import os
from datetime import datetime, timezone
from logger import log

# Database setup
DB_PATH = "summarize.db"
db = SqliteDatabase(DB_PATH)

class BaseModel(Model):
    class Meta:
        database = db

class Entry(BaseModel):
    name = CharField()
    status = CharField()
    url = CharField(unique=True)
    transcription = TextField(null=True)
    insertion_date = DateTimeField(default=datetime.now(timezone.utc))

# Ensure database exists
def initialize_db():
    if not os.path.exists(DB_PATH):
        log("Database does not exist, initializing...")
        db.connect()
        db.create_tables([Entry])
        db.close()

initialize_db()
