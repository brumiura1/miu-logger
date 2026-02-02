import logging
from typing import Callable


class ConditionalLogger:
    def __init__(self, logger: logging.Logger, enabled_predicate: Callable[[], bool]):
        self._logger = logger
        self._enabled = enabled_predicate

    def __getattr__(self, item):
        attr = getattr(self._logger, item)

        if not callable(attr):
            return attr

        def wrapper(*a, **kw):
            if self._enabled():
                return attr(*a, **kw)

        return wrapper

    def get_real_logger(self) -> logging.Logger:
        return self._logger
