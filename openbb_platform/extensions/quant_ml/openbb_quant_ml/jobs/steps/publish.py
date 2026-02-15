"""Step: publish artifacts marker."""

from __future__ import annotations

from typing import Any

from openbb_quant_ml.service.constants import ARTIFACT_ROOT
from openbb_quant_ml.service.storage import save_json


def run(config: dict[str, Any]) -> dict[str, Any]:
    payload = {
        "job": str(config.get("job", "unknown")),
        "run_id": config.get("run_id"),
        "updated_at": config.get("updated_at"),
    }
    path = ARTIFACT_ROOT / "jobs" / "latest_publish.json"
    save_json(path, payload)
    return {"status": "ok", "path": str(path)}
