"""Contains the Flask API server for the video transcription project."""

from datetime import datetime, timezone
from typing import Literal

from flask import Flask, Response, jsonify, request
from flask_cors import CORS
from peewee import IntegrityError
import structlog
import yt_dlp

from model import Entry

log = structlog.get_logger()

server = Flask(__name__)
CORS(server)


@server.route("/entries", methods=["GET"])
def get_entries() -> Response:
    """Return all database entries as JSON.

    Returns:
        Response: JSON response.

    """
    entries = Entry.select().order_by(Entry.insertion_date.desc()).dicts()

    for e in entries:
        # return everything but the transcription
        del e['transcription']
        # format insertion_date as ISO string
        if e['insertion_date'] and hasattr(e['insertion_date'], 'isoformat'):
            e['insertion_date'] = e['insertion_date'].isoformat()

    return jsonify(list(entries))


@server.route("/entries", methods=["POST"])
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

    ydl_opts = {"quiet": True, "noprogress": True, "extract_flat": True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(data["url"], download=False)
    if not info:
        msg = "failed to extract_info from youtube"
        raise Exception(msg)

    if info.get('entries'):
        log.info("Adding playlist")
        urls = [entry['url'] for entry in info['entries']]

        for url in urls:
            log.info(f"Adding video {url} to database")
            try:
                Entry.create(
                    name=url,
                    status="not_started",
                    url=url,
                    transcription=None,
                    insertion_date=datetime.now(timezone.utc),
                )
            except IntegrityError:
                existing_entry = Entry.get(Entry.url == url)
                if existing_entry.status == "error":
                    log.info(f"Resetting error video {url} to not_started")
                    existing_entry.status = "not_started"
                    existing_entry.save()
                else:
                    log.warn(f"A video with URL {url} already exists.")
        return jsonify({"message": "Playlist added successfully."}), 201
    else:
        log.info("Adding video")
        try:
            log.info(f"Adding video {data['url']} to database")
            Entry.create(
                name=data["url"],
                status="not_started",
                url=data["url"],
                transcription=None,
                insertion_date=datetime.now(timezone.utc),
            )
            return jsonify({"message": "Video added successfully."}), 201
        except IntegrityError:
            existing_entry = Entry.get(Entry.url == data["url"])
            if existing_entry.status == "error":
                log.info(f"Resetting error video {data['url']} to not_started")
                existing_entry.status = "not_started"
                existing_entry.save()
                return jsonify({"message": "Video reset and will be retried."}), 200
            else:
                log.warn(f"A video with URL {data['url']} already exists.")
                return (
                    jsonify({"error": "A video with this URL already exists."}),
                    409,
                )  # HTTP 409 Conflict
