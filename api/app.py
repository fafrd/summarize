"""Main entry point for the API and daemon."""

import sys
import threading
import time

from daemon import process_entries  # Import daemon function
from logger import log
from server import app  # Import Flask app from server.py


def run_api() -> None:
    """Run the Flask API."""
    app.run(port=3669, debug=False, use_reloader=False)


def run_daemon() -> None:
    """Run the processing daemon."""
    log("Daemon started, watching for new videos...")
    process_entries()


if __name__ == "__main__":
    api_thread = threading.Thread(target=run_api, daemon=True)
    daemon_thread = threading.Thread(target=run_daemon, daemon=True)

    api_thread.start()
    daemon_thread.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        log("Shutting down...")
        sys.exit(0)
