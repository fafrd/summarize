"""Contains the Flask API server for the video transcription project."""

from datetime import datetime, timezone
from typing import Literal

from flask import Flask, Response, jsonify, request
from flask_cors import CORS
from peewee import IntegrityError

from model import Entry

app = Flask(__name__)
CORS(app)


@app.route("/entries", methods=["GET"])
def get_entries() -> Response:
    """Return all database entries as JSON.

    Returns:
        Response: JSON response.

    """
    entries = Entry.select().order_by(Entry.insertion_date.desc()).dicts()
    return jsonify(list(entries))


@app.route("/entries", methods=["POST"])
def add_entry() -> (
    tuple[Response, Literal[400]]
    | tuple[Response, Literal[201]]
    | tuple[Response, Literal[409]]
):
    """Insert a new entry into the database.

    Returns:
        Response: JSON response.
        Literal[400]: HTTP 400 status code.
        Literal[201]: HTTP 201 status code.
        Literal[409]: HTTP 409 status code.

    """
    data = request.json
    if data is None or "url" not in data:
        return jsonify({"error": "Missing field 'url'"}), 400

    try:
        entry = Entry.create(
            name=data["url"],
            status="not_started",
            url=data["url"],
            transcription=None,
            insertion_date=datetime.now(timezone.utc),
        )
        return jsonify({"id": entry.id, "message": "Entry added successfully."}), 201
    except IntegrityError:
        return (
            jsonify({"error": "A video with this URL already exists."}),
            409,
        )  # HTTP 409 Conflict
