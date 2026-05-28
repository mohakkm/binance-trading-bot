import logging
import os
from logging.handlers import RotatingFileHandler

LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
LOG_FILE = os.path.join(LOG_DIR, "trading_bot.log")

LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def setup_logger(name: str) -> logging.Logger:
    """
    Returns a logger that:
      - writes DEBUG and above to logs/trading_bot.log (rotating, max 5MB x 3 backups)
      - writes INFO and above to the console
    All modules call this with their own __name__ so log lines are traceable.
    """
    # Ensure log directory exists
    os.makedirs(LOG_DIR, exist_ok=True)

    logger = logging.getLogger(name)

    # Avoid adding duplicate handlers if the logger is already configured
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)  # capture everything; handlers filter independently

    # --- File handler (DEBUG+) ---
    file_handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=5 * 1024 * 1024,  # 5 MB
        backupCount=3,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT))

    # --- Console handler (INFO+) ---
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT))

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger