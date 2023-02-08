"""Custom Logger for Global Router"""
import logging

gr_logger = logging.getLogger("gr")

log_formatter = logging.Formatter("%(asctime)s [%(levelname)s]: %(message)s")

file_handler = logging.FileHandler("logs/gr.log", mode="w")
file_handler.setFormatter(log_formatter)

console_handler = logging.StreamHandler()
console_handler.setFormatter(log_formatter)

logging.basicConfig(level=logging.INFO, handlers=[file_handler, console_handler])
