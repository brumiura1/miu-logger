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
