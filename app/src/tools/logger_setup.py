# app/src/tools/logger_setup.py

import logging
import os
import datetime
import sys
from colorama import Fore, Back, Style
from app.src.tools.colored_formatter import ColoredFormatter


def setup_logger(
    logger_name: str, folder_name: str, level: str = "INFO"
) -> logging.Logger:
    """Configures and returns a logger."""
    logger = logging.getLogger(logger_name)
    formatter = ColoredFormatter(
        "{asctime} |{color} {levelname:8} {reset}| {name} | {message}",
        style="{",
        datefmt="%Y-%m-%d %H:%M:%S",
        colors={
            "DEBUG": Fore.CYAN,
            "INFO": Fore.GREEN,
            "WARNING": Fore.YELLOW,
            "ERROR": Fore.RED,
            "CRITICAL": Fore.RED + Back.WHITE + Style.BRIGHT,
        },
    )

    log_folder = f"logs/{folder_name}"
    os.makedirs(log_folder, exist_ok=True)

    log_file_name = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".log"
    log_file_path = os.path.join(log_folder, log_file_name)

    logger.setLevel(logging.INFO if level == "INFO" else logging.DEBUG)

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    file_handler = logging.FileHandler(log_file_path)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger
