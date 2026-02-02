import logging


class LoggerNameFilter(logging.Filter):
    def __init__(self, name: str):
        super().__init__()
        self.name = name

    def filter(self, record: logging.LogRecord) -> bool:
        return record.name == self.name

class ExactLevelFilter(logging.Filter):
    def __init__(self, level: int):
        super().__init__()
        self.level = level

    def filter(self, record: logging.LogRecord) -> bool:
        return record.levelno == self.level
