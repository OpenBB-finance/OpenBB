"""Tests for run-level exclusions aggregation."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pandas as pd

from openbb_quant_ml.service.exclusions_logger import append_exclusions


def test_append_exclusions_aggregates_and_deduplicates(
    monkeypatch, tmp_path: Path
) -> None:
    def _fake_run_dir(run_id: str) -> Path:
        path = tmp_path / run_id
        path.mkdir(parents=True, exist_ok=True)
        return path

    monkeypatch.setattr(
        "openbb_quant_ml.service.exclusions_logger.get_run_dir", _fake_run_dir
    )
    rows = [
        {
            "symbol": "AAPL",
            "stage": "u0",
            "company_id": "AAPL",
            "reasons": ["price_below_min", "price_below_min"],
        }
    ]
    append_exclusions("trn-260221-001", date(2026, 2, 21), rows)
    append_exclusions("trn-260221-001", date(2026, 2, 21), rows)
    frame = pd.read_parquet(tmp_path / "trn-260221-001" / "exclusions.parquet")
    assert frame.shape[0] == 1
    assert frame.iloc[0]["ticker"] == "AAPL"
    assert frame.iloc[0]["reason_code"] == "price_below_min"

