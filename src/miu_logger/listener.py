import logging
import os
import sys
import traceback
from multiprocessing import Queue
from logging.handlers import RotatingFileHandler, QueueListener

from .formatters import ColoredFormatter
from .filters import LoggerNameFilter, ExactLevelFilter
from .config import LogConfig


DEFAULT_FORMATTER = logging.Formatter(
    fmt="%(asctime)s - %(processName)s - %(threadName)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

FILE_MAX_BYTES = 10 * 1024 * 1024
FILE_BACKUP_COUNT = 5


def _make_file_handler(path: str, level: int) -> logging.Handler:
    handler = RotatingFileHandler(
        path,
        maxBytes=FILE_MAX_BYTES,
        backupCount=FILE_BACKUP_COUNT,
        encoding="utf-8",
    )
    handler.setLevel(level)
    handler.setFormatter(DEFAULT_FORMATTER)
    return handler


def _make_stream_handler(level: int) -> logging.Handler:
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)
    handler.setFormatter(
        ColoredFormatter(DEFAULT_FORMATTER._fmt, DEFAULT_FORMATTER.datefmt)
    )
    return handler


class SafeQueueListener(QueueListener):
    def _monitor(self):
        try:
            super()._monitor()
        except (EOFError, OSError):
            return
        except Exception:
            traceback.print_exc()
            raise


def setup_main_listener(config: LogConfig):
    os.makedirs(config.log_dir, exist_ok=True)

    queue = Queue(-1)
    handlers: list[logging.Handler] = []

    # ─────────────────────────────
    # Domain log files
    # ─────────────────────────────
    for domain in config.domains:
        filename = (
            f"{config.file_prefix}.{domain}.log"
            if config.file_prefix
            else f"{domain}.log"
        )

        path = os.path.join(config.log_dir, filename)
        fh = _make_file_handler(path, logging.DEBUG)
        fh.addFilter(LoggerNameFilter(domain))
        handlers.append(fh)

    # ─────────────────────────────
    # Level log files
    # ─────────────────────────────
    for lvl in (logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR):
        level_name = logging.getLevelName(lvl).lower()

        filename = (
            f"{config.file_prefix}.{level_name}.log"
            if config.file_prefix
            else f"{level_name}.log"
        )

        path = os.path.join(config.log_dir, filename)
        fh = _make_file_handler(path, lvl)
        fh.addFilter(ExactLevelFilter(lvl))
        handlers.append(fh)

    # ─────────────────────────────
    # Console
    # ─────────────────────────────
    handlers.append(_make_stream_handler(logging.DEBUG))

    listener = SafeQueueListener(queue, *handlers, respect_handler_level=True)
    listener.start()

    return queue, listener


def clear_logs(config: LogConfig):
    for file in os.listdir(config.log_dir):
        if file.endswith(".log"):
            open(os.path.join(config.log_dir, file), "w").close()
