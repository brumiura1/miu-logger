import logging
import colorama
from colorama import Fore, Style
from copy import copy

colorama.init(autoreset=True)


class ColoredFormatter(logging.Formatter):
    LEVEL_COLORS = {
        logging.DEBUG: Fore.BLUE,
        logging.INFO: Fore.GREEN,
        logging.WARNING: Fore.YELLOW,
        logging.ERROR: Fore.RED,
        logging.CRITICAL: Fore.MAGENTA,
    }

    def format(self, record: logging.LogRecord) -> str:
        record_copy = copy(record)

        color = self.LEVEL_COLORS.get(record_copy.levelno, "")
        record_copy.levelname = (
            f"{color}{record_copy.levelname}{Style.RESET_ALL}"
        )

        return super().format(record_copy)
