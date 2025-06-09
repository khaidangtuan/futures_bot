# utils/logger.py

import os
import logging
from datetime import datetime

def get_logger(name: str) -> logging.Logger:
    """
    Returns a logger instance that logs to both a timestamped file and console.
    
    :param name: Logger name (e.g., __name__)
    :return: Configured logger
    """
    os.makedirs("logs", exist_ok=True)
    log_filename = datetime.now().strftime("logs/%Y-%m-%d_%H-%M-%S.log")

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Prevent adding multiple handlers if already configured
    if not logger.handlers:
        file_handler = logging.FileHandler(log_filename, encoding="utf-8")
        console_handler = logging.StreamHandler()

        formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger
