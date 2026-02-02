import atexit
from typing import Dict
import logging

from .config import LogConfig
from .listener import setup_main_listener
from .logger_factory import get_logger
from .conditional import ConditionalLogger


class LoggingRepository:
    def __init__(self, config: LogConfig, *, use_listener: bool = True, queue=None):
        self._is_shutdown = False
        self.config = config
        self.listener = None

        self._domains = set(config.domains)
        self._loggers: Dict[str, ConditionalLogger] = {}

        if use_listener:
            self.queue, self.listener = setup_main_listener(config)
        else:
            if queue is None:
                raise ValueError("queue required when use_listener=False")
            self.queue = queue

        atexit.register(self.shutdown)

    # ---------- domain access ----------

    def _create_domain_logger(self, domain: str) -> ConditionalLogger:
        if domain in self._loggers:
            return self._loggers[domain]

        base = get_logger(domain, logging.DEBUG, self.queue)
        wrapped = ConditionalLogger(base, lambda: self.config.debug_enabled)

        self._loggers[domain] = wrapped
        return wrapped

    def __getattr__(self, item: str) -> ConditionalLogger:
        if item in self._domains:
            logger = self._create_domain_logger(item)
            setattr(self, item, logger)
            return logger
        raise AttributeError(item)

    def get(self, domain: str) -> ConditionalLogger:
        if domain not in self._domains:
            raise ValueError(f"Unknown log domain: {domain}")
        return self._create_domain_logger(domain)

    # ---------- infra ----------

    def get_queue(self):
        return self.queue

    def shutdown(self):
        if getattr(self, "_is_shutdown", False):
            return

        self._is_shutdown = True

        if self.listener and getattr(self.listener, "_thread", None):
            try:
                self.listener.stop()
            except Exception:
                pass

    # ---------- pickle support ----------

    def __getstate__(self):
        return {"config": self.config, "queue": self.queue}

    def __setstate__(self, state):
        self._is_shutdown = False
        self.config = state["config"]
        self.queue = state["queue"]
        self.listener = None
        self._domains = set(self.config.domains)
        self._loggers = {}
        atexit.register(self.shutdown)