"""Tests for merge-safe run registry writes."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
from openbb_quant_ml.service import run_registry as rr


def test_update_run_preserves_unknown_registry_fields(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    registry_payload: dict[str, Any] = {"runs": {}}

    def _read_registry() -> dict[str, Any]:
        return {"runs": dict(registry_payload["runs"])}

    def _write_registry(payload: dict[str, Any]) -> None:
        registry_payload["runs"] = dict(payload.get("runs", {}))

    monkeypatch.setattr(rr, "read_registry", _read_registry)
    monkeypatch.setattr(rr, "write_registry", _write_registry)
    monkeypatch.setattr(rr, "build_training_run_id", lambda **kwargs: "trn-260221-001")
    monkeypatch.setattr(rr, "rebuild_runs_index", lambda: None)
    monkeypatch.setattr(rr, "upsert_run_index_entry", lambda *args, **kwargs: None)
    monkeypatch.setattr(rr, "get_run_dir", lambda run_id: tmp_path / run_id)

    rr._RUN_STATES.clear()
    created = rr.create_run()
    row = dict(registry_payload["runs"][created.run_id])
    row["external_note"] = "keep_me"
    registry_payload["runs"][created.run_id] = row

    rr.update_run(created.run_id, progress=33, stage="step_x")

    updated = registry_payload["runs"][created.run_id]
    assert updated.get("external_note") == "keep_me"
    assert int(updated.get("progress", 0)) == 33
