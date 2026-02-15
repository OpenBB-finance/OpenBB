"""Step: promote model candidate placeholder."""

from __future__ import annotations

from typing import Any


def run(config: dict[str, Any]) -> dict[str, Any]:
    run_id = config.get("run_id")
    if not run_id:
        return {"status": "skipped", "message": "run_id is not configured"}
    return {"status": "ok", "run_id": run_id}
