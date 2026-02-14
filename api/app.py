"""Main entry point for the API and daemon."""

import logging
import sys
import threading
import time

import structlog

from config import API_HOST, API_PORT
from daemon import process_entries
from server import server

log = structlog.get_logger()


def run_api() -> None:
    logging.getLogger('werkzeug').disabled = True
    server.run(host=API_HOST, port=API_PORT, debug=False, use_reloader=False)


def run_daemon() -> None:
    log.info("Daemon started, watching for new videos...")
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
        log.info("Shutting down...")
        sys.exit(0)
