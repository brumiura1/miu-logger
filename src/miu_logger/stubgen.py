from pathlib import Path
from typing import Iterable


REPOSITORY_TEMPLATE = """from typing import Optional
from queue import Queue
from miu_logger.conditional import ConditionalLogger
from miu_logger.config import LogConfig


class LoggingRepository:
    def __init__(
        self,
        config: LogConfig,
        *,
        use_listener: bool = True,
        queue: Optional[Queue] = None
    ) -> None: ...
    
{domains}
    
    def get(self, domain: str) -> ConditionalLogger: ...
    def get_queue(self) -> Queue: ...
    def shutdown(self) -> None: ...
"""

CONDITIONAL_LOGGER_STUB = """from typing import Any
import logging


class ConditionalLogger:
    def __init__(self, logger: logging.Logger, should_log_debug: Any) -> None: ...
    
    def debug(self, msg: str, *args: Any, **kwargs: Any) -> None: ...
    def info(self, msg: str, *args: Any, **kwargs: Any) -> None: ...
    def warning(self, msg: str, *args: Any, **kwargs: Any) -> None: ...
    def error(self, msg: str, *args: Any, **kwargs: Any) -> None: ...
    def critical(self, msg: str, *args: Any, **kwargs: Any) -> None: ...
    def exception(self, msg: str, *args: Any, **kwargs: Any) -> None: ...
"""


def generate_repository_stub(domains: Iterable[str], out_dir: str = "typings") -> None:
    out_path = Path(out_dir) / "miu_logger"
    out_path.mkdir(parents=True, exist_ok=True)

    # Generate repository.pyi
    lines = []
    for d in domains:
        lines.append(f"    @property")
        lines.append(f"    def {d}(self) -> ConditionalLogger: ...")

    content = REPOSITORY_TEMPLATE.format(domains="\n".join(lines))
    
    with open(out_path / "repository.pyi", "w") as f:
        f.write(content)
    
    # Generate conditional.pyi
    with open(out_path / "conditional.pyi", "w") as f:
        f.write(CONDITIONAL_LOGGER_STUB)
    
    print(f"✓ Generated stubs in {out_path}")