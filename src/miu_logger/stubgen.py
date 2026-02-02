from pathlib import Path
from typing import Iterable


TEMPLATE = """from typing import Optional
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


def generate_repository_stub(domains: Iterable[str], out_dir: str = "typings") -> None:
    out_path = Path(out_dir) / "miu_logger"
    out_path.mkdir(parents=True, exist_ok=True)

    lines = []
    for d in domains:
        lines.append(f"    @property")
        lines.append(f"    def {d}(self) -> ConditionalLogger: ...")

    content = TEMPLATE.format(domains="\n".join(lines))

    with open(out_path / "repository.pyi", "w") as f:
        f.write(content)