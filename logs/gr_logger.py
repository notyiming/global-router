"""Custom Logger for Global Router."""

import logging.handlers
import os

LOG_FILENAME = "logs/gr.log"
should_roll_over = os.path.isfile(LOG_FILENAME)

gr_logger = logging.getLogger("gr")

log_formatter = logging.Formatter("%(asctime)s [%(levelname)s]: %(message)s")

file_handler = logging.handlers.RotatingFileHandler(
    LOG_FILENAME, mode="w", backupCount=5, delay=True
)
if should_roll_over:
    file_handler.doRollover()
file_handler.setFormatter(log_formatter)

console_handler = logging.StreamHandler()
console_handler.setFormatter(log_formatter)

gr_logger.setLevel(logging.INFO)
gr_logger.addHandler(file_handler)
gr_logger.addHandler(console_handler)
