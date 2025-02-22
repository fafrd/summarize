"""Logger module for the API."""

import structlog

logger = structlog.get_logger()


def log(message: str) -> None:
    """Log a message with a timestamp.

    Args:
        message (str): Message to log.

    """
    logger.info(message)
