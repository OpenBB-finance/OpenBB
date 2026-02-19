"""Runtime promoted-model pointer tests."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from openbb_quant_ml.service import runtime_pointer as rp


def _prepare_lgbm_run(run_dir: Path, *, as_of: str = "2026-02-19") -> None:
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "model_lgbm_ranker.pkl").write_bytes(b"model")
    (run_dir / "model_lgbm_ranker_meta.json").write_text(
        '{"feature_columns":["f1","f2"]}',
        encoding="utf-8",
    )
    pd.DataFrame(
        [{"date": as_of, "symbol": "AAPL", "predicted_return": 0.01}]
    ).to_parquet(run_dir / "predictions_lgbm_ranker.parquet", index=False)


def test_promoted_pointer_runtime_source(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
):
    pointer_path = tmp_path / "runtime" / "promoted_model.json"
    runs_root = tmp_path / "runs"
    _prepare_lgbm_run(runs_root / "trn-260219-001")

    monkeypatch.setattr(rp, "PROMOTED_MODEL_PATH", pointer_path)
    monkeypatch.setattr(rp, "get_run_dir", lambda run_id: runs_root / run_id)
    monkeypatch.setattr(rp, "_latest_completed_run_id", lambda model_name: None)

    payload = rp.set_promoted_model_pointer(
        run_id="trn-260219-001",
        model_name="lgbm_ranker",
        source="test",
    )
    assert payload["ready"] is True

    resolved = rp.get_promoted_model("lgbm_ranker")
    assert resolved["run_id"] == "trn-260219-001"
    assert resolved["source"] == "runtime_pointer"
    assert resolved["ready"] is True


def test_promoted_pointer_registry_fallback(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
):
    pointer_path = tmp_path / "runtime" / "promoted_model.json"
    runs_root = tmp_path / "runs"
    _prepare_lgbm_run(runs_root / "trn-260219-002", as_of="2026-02-20")

    monkeypatch.setattr(rp, "PROMOTED_MODEL_PATH", pointer_path)
    monkeypatch.setattr(rp, "get_run_dir", lambda run_id: runs_root / run_id)
    monkeypatch.setattr(
        rp, "_latest_completed_run_id", lambda model_name: "trn-260219-002"
    )

    resolved = rp.get_promoted_model("lgbm_ranker")
    assert resolved["run_id"] == "trn-260219-002"
    assert resolved["source"] == "fallback_registry"
    assert resolved["ready"] is True
