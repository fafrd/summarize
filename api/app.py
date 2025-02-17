from flask import Flask, jsonify, request
from flask_cors import CORS
from peewee import SqliteDatabase, Model, CharField, TextField, DateTimeField, IntegrityError
import os
from datetime import datetime

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
    insertion_date = DateTimeField(default=datetime.utcnow)

# Ensure database exists
if not os.path.exists(DB_PATH):
    db.connect()
    db.create_tables([Entry])
    # Adding a sample row
    Entry.create(
        name="Sample Meeting",
        status="done",
        url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        transcription="Example transcription text...",
    )
    db.close()

# Flask app setup
app = Flask(__name__)
CORS(app)

@app.route("/entries", methods=["GET"])
def get_entries():
    """Returns all database entries as JSON."""
    entries = Entry.select().order_by(Entry.insertion_date.desc()).dicts()
    return jsonify(list(entries))

@app.route("/entries", methods=["POST"])
def add_entry():
    """Inserts a new entry into the database."""
    data = request.json
    if data is None or not all(k in data for k in ("name", "status", "url", "transcription")):
        return jsonify({"error": "Missing required fields"}), 400
    
    try:
        entry = Entry.create(
            name=data["name"],
            status=data["status"],
            url=data["url"],
            transcription=data["transcription"],
        )
        return jsonify({"id": entry.id, "message": "Entry added successfully."}), 201

    except IntegrityError:
        return jsonify({"error": "A video with this URL already exists."}), 409  # HTTP 409 Conflict

if __name__ == "__main__":
    app.run(port=3669, debug=True)
