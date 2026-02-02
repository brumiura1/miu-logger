import logging
from logging.handlers import QueueHandler


def get_logger(name: str, level: int, queue) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.handlers.clear()
    logger.propagate = False

    qh = QueueHandler(queue)
    logger.addHandler(qh)

    return logger
