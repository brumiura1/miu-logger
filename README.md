# miu-logger

**Multiprocessing-safe, domain-driven structured logging for Python services**

`miu-logger` is a logging framework designed for **real systems**:

* Multiprocessing- and multithreading-safe
* Domain-separated loggers (`app`, `db`, `task`, etc.)
* Per-level log files (`debug.log`, `info.log`, `error.log`, …)
* Central queue listener to avoid file collisions
* Clean IDE autocomplete for both domains and log levels
* Minimal setup in application code

---

## Why use `miu-logger`

Python's standard logging is powerful but breaks down when:

* Multiple processes or threads write to the same log files
* You want **domain-specific log files**
* You want **centralized log routing**
* You want IDE autocomplete for domains and levels

`miu-logger` solves this by:

> Logging through a **central queue listener**, separating **domains** and **levels**, while exposing a **typed repository** for IDE-friendly access.

---

## Installation

```bash
uv add miu-logger
# or
pip install miu-logger
```

---

## Configuring Logging Domains

Domains represent **areas of your system** (not log levels). Examples: `app`, `db`, `redis`, `task`.

Define them in `LogConfig`:

```python
import logging
from miu_logger.config import LogConfig
from miu_logger.repository import LoggingRepository

config = LogConfig(
    log_dir="logs",                     # folder to store logs
    domains=["app", "db", "redis"],     # your custom domains
    level=logging.DEBUG,                # base log level for all domains
    debug_enabled=True,                 # toggle debug messages
)

repo = LoggingRepository(config)
```

### Accessing Domain Loggers

```python
repo.app.info("Application started")
repo.db.error("Database connection failed")
repo.redis.debug("Cache initialized")
```

* Accessing a domain not defined in `config.domains` raises a `ValueError`:

```python
repo.get("api")  # ❌ ValueError if "api" not in config.domains
```

* Domains can also be dynamically retrieved:

```python
task_logger = repo.get("task")  # Must be defined in config.domains
task_logger.info("Task started")
```

---

## IDE Autocomplete with Stub Generation

Domains are dynamic, so editors cannot know them automatically.
Use the **stub generator** to enable autocomplete:

```python
from miu_logger.stubgen import generate_repository_stub

generate_repository_stub(
    domains=["app", "db", "redis", "task"],  # all your domains
    out_dir="typings",                       # directory for generated stubs
)
```

This creates:

```
typings/miu_logger/repository.pyi
```

Tell your editor where the typings are:

* **VSCode / Pyright**:

```json
{
  "python.analysis.extraPaths": ["typings"]
}
```

* **pyproject.toml (Pyright)**:

```toml
[tool.pyright]
extraPaths = ["typings"]
```

After this, your IDE knows both:

* Domains: `repo.app`, `repo.db`, …
* Log methods: `.debug()`, `.info()`, `.warning()`, `.error()`, `.exception()`

Regenerate stubs whenever you add new domains.

---

## Multiprocessing Usage

The repository uses a **central QueueListener** for safe multiprocessing logging.

**Main process:**

```python
repo = LoggingRepository(config)
queue = repo.get_queue()
```

**Worker processes:**

```python
worker_repo = LoggingRepository(config, use_listener=False, queue=queue)
worker_repo.task.info("Worker started")
```

All processes log safely to the same listener and files.

---

## Debug Control

Only `.debug()` messages are conditional via `debug_enabled`:

```python
config.debug_enabled = False
repo.app.debug("Won't appear")
repo.app.info("Will appear")
```

Useful for toggling debug messages in production.

---

## Output Structure

Logs are written in:

```
logs/
 ├─ app.log         # domain logs
 ├─ db.log
 ├─ redis.log
 ├─ debug.log       # per-level logs
 ├─ info.log
 ├─ warning.log
 └─ error.log
```

Console output is **colorized** by level:

* DEBUG → blue
* INFO → green
* WARNING → yellow
* ERROR → red

Files remain clean.

---

## Graceful Shutdown

The repository automatically shuts down on process exit and supports manual shutdown:

```python
repo.shutdown()
```

---

## Typical Usage Example

```python
repo.app.info("Service starting")

try:
    connect_db()
except Exception:
    repo.db.exception("DB connection failed")

repo.redis.debug("Cache size: %d", cache_size)
```

**Multiprocessing workers:**

```python
def worker(queue):
    repo = LoggingRepository(config, use_listener=False, queue=queue)
    repo.task.info("Worker task started")
```

---

## Project Structure

```
miu_logger/
 ├─ repository.py         # main LoggingRepository
 ├─ listener.py           # QueueListener and handler setup
 ├─ logger_factory.py     # logger creation functions
 ├─ conditional.py        # ConditionalLogger
 ├─ filters.py            # Logger filters
 ├─ formatters.py         # ColoredFormatter
 ├─ config.py             # LogConfig definition
 └─ stubgen.py            # stub generator for IDE autocomplete
```

---

## When to Use

* Services with many subsystems
* Multiprocessing ingestion pipelines
* Long-running daemons
* Kubernetes / systemd services
* Need for clear operational logs

---

## When Not to Use

* Single-file scripts
* No multiprocessing
* No domain separation required

Plain `logging` is sufficient in those cases.

---

## License

MIT

---

## Author

**Bruno Miura**