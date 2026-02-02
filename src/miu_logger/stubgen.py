from pathlib import Path
from typing import Iterable


TEMPLATE = """from typing import Any
from miu_logger.conditional import ConditionalLogger


class LoggingRepository:
{domains}
"""


def generate_repository_stub(domains: Iterable[str], out_dir: str = "typings") -> None:
    out_path = Path(out_dir) / "miu_logger"
    out_path.mkdir(parents=True, exist_ok=True)

    lines = []
    for d in domains:
        lines.append(f"    {d}: ConditionalLogger")

    content = TEMPLATE.format(domains="\n".join(lines))

    with open(out_path / "repository.pyi", "w") as f:
        f.write(content)
