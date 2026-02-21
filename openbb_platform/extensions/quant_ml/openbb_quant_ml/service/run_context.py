"""Run context helpers with stable run uid generation."""

from __future__ import annotations

import secrets
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from openbb_quant_ml.service.storage import load_json, save_json


def generate_run_uid(*, now: datetime | None = None) -> str:
    """Return timestamp-hash run uid."""
    stamp = (now or datetime.now(UTC)).replace(microsecond=0).strftime(
        "%Y-%m-%d_%H%M%SZ"
    )
    return f"{stamp}_{secrets.token_hex(4)}"


def context_path(run_dir: Path) -> Path:
    """Return run context json path."""
    return run_dir / "run_context.json"


def load_run_context(run_dir: Path) -> dict[str, Any]:
    """Load run context payload."""
    payload = load_json(context_path(run_dir), default={})
    return payload if isinstance(payload, dict) else {}


def ensure_run_context(run_dir: Path, run_id: str) -> dict[str, Any]:
    """Load or create run context for one run."""
    payload = load_run_context(run_dir)
    run_uid = str(payload.get("run_uid", "")).strip()
    if run_uid:
        return payload

    out = {
        "run_id": str(run_id),
        "run_uid": generate_run_uid(),
        "created_at": datetime.now(UTC).replace(microsecond=0).isoformat(),
    }
    save_json(context_path(run_dir), out)
    return out


def get_run_uid(run_dir: Path, run_id: str) -> str:
    """Return run uid and create context when absent."""
    payload = ensure_run_context(run_dir, run_id)
    return str(payload.get("run_uid", "")).strip()

