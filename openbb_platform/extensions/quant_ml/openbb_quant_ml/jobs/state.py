"""Checkpoint state for operational jobs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from openbb_quant_ml.service.constants import ARTIFACT_ROOT

STATE_PATH = ARTIFACT_ROOT / "jobs" / "job_state.json"


class JobState:
    """Simple JSON-backed state store."""

    def __init__(self, data: dict[str, Any]):
        self.data = data

    @classmethod
    def load(cls, path: Path = STATE_PATH) -> JobState:
        if not path.exists():
            return cls({})
        with path.open(encoding="utf-8") as file:
            payload = json.load(file)
        return cls(payload if isinstance(payload, dict) else {})

    def save(self, path: Path = STATE_PATH) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as file:
            json.dump(self.data, file, ensure_ascii=False, indent=2)

    def get(self, key: str, default: Any = None) -> Any:
        return self.data.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self.data[key] = value

    def delete(self, key: str) -> None:
        self.data.pop(key, None)
