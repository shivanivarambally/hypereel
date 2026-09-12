"""Local append-only evidence; this journal is not an automatic replay mechanism."""
from datetime import datetime, timezone
import json
import os
from pathlib import Path
from uuid import uuid4


class CheckpointWriteError(RuntimeError):
    """No more requests may start after required evidence storage fails."""


class CallJournal:
    def __init__(self, directory: str, context: dict | None = None):
        self.path = Path(directory).resolve() / f"calls-{uuid4().hex}.jsonl"
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.stream = self.path.open("x", encoding="utf-8")
        self.failed = False
        self.sequence = 0
        try:
            self.append("scope_started", context=context or {})
        except BaseException:
            self.stream.close()
            raise

    def append(self, event: str, **fields):
        if self.failed:
            raise CheckpointWriteError("Checkpoint journal is unavailable")
        self.sequence += 1
        record = {"schema_version": 1, "sequence": self.sequence,
                  "at": datetime.now(timezone.utc).isoformat(), "event": event, **fields}
        try:
            self.stream.write(json.dumps(record, allow_nan=False) + "\n")
            self.stream.flush()
            os.fsync(self.stream.fileno())
        except (OSError, ValueError) as exc:
            self.failed = True
            raise CheckpointWriteError("Cannot persist provider checkpoint") from exc

    def close(self):
        self.stream.close()
