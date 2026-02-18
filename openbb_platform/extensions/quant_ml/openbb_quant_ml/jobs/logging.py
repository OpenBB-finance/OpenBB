"""Run-scoped logging helpers for jobs."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

from openbb_quant_ml.service.constants import ARTIFACT_ROOT


def _utc_now() -> datetime:
    return datetime.now(UTC).replace(microsecond=0)


def create_run_dir(job_name: str) -> tuple[str, Path]:
    ts = _utc_now().strftime("%Y%m%d-%H%M%S")
    run_id = f"{ts}-{uuid4().hex[:8]}"
    run_dir = ARTIFACT_ROOT / "runs" / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    return run_id, run_dir


def append_log(run_dir: Path, level: str, step: str, message: str, extra: dict[str, Any] | None = None) -> None:
    row = {
        "timestamp": _utc_now().isoformat(),
        "level": level,
        "step": step,
        "message": message,
    }
    if extra:
        row["extra"] = extra
    path = run_dir / "logs.jsonl"
    with path.open("a", encoding="utf-8") as file:
        file.write(json.dumps(row, ensure_ascii=False) + "\n")


def write_json(run_dir: Path, file_name: str, payload: dict[str, Any]) -> None:
    path = run_dir / file_name
    with path.open("w", encoding="utf-8") as file:
        json.dump(payload, file, ensure_ascii=False, indent=2)
