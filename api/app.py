"""Main entry point for the API and daemon."""

import logging
import sys
import threading
import time

from daemon import process_entries
from logger import log
from server import server


def run_api() -> None:
    logging.getLogger('werkzeug').disabled = True
    server.run(host="0.0.0.0", port=3669, debug=False, use_reloader=False)


def run_daemon() -> None:
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
