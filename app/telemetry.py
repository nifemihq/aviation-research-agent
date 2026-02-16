from __future__ import annotations
import json
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional


LOG_PATH = Path("logs/events.jsonl")


@dataclass
class Event:
    event: str
    ts_utc: str
    data: dict[str, Any]


def log_event(event: str, data: dict[str, Any]) -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    e = Event(
        event=event,
        ts_utc=datetime.now(timezone.utc).isoformat(),
        data=data,
    )
    with LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(asdict(e), ensure_ascii=False) + "\n")
