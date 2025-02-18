from datetime import datetime, timezone
from flask import Flask, jsonify, request
from flask_cors import CORS
from peewee import IntegrityError
from model import Entry

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
    if data is None or not "url" in data:
        return jsonify({"error": "Missing field 'url'"}), 400
    
    try:
        entry = Entry.create(
            name=data["url"],
            status="not_started",
            url=data["url"],
            transcription=None,
            insertion_date=datetime.now(timezone.utc)
        )
        return jsonify({"id": entry.id, "message": "Entry added successfully."}), 201
    except IntegrityError:
        return jsonify({"error": "A video with this URL already exists."}), 409  # HTTP 409 Conflict