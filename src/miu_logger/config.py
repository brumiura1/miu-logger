# config.py

from dataclasses import dataclass
from typing import List

@dataclass
class LogConfig:
    log_dir: str
    debug_enabled: bool
    domains: List[str]
    file_prefix: str = "logfile"
