"""Tests for strict label-overlap purging mode."""

from __future__ import annotations

import pandas as pd
from openbb_quant_ml.models import WalkForwardConfig
from openbb_quant_ml.service.ranker_modeling import _build_splits


def _make_ranker_frame() -> pd.DataFrame:
    dates = pd.date_range("2025-01-31", periods=10, freq="ME")
    rows: list[dict[str, object]] = []
    for date_value in dates:
        for symbol in ("AAA", "BBB", "CCC"):
            rows.append(
                {
                    "date": pd.Timestamp(date_value),
                    "symbol": symbol,
                    "month_id": pd.Timestamp(date_value).to_period("M").strftime("%Y-%m"),
                    "target_return": 0.01,
                }
            )
    return pd.DataFrame(rows)


def test_strict_label_overlap_purging_has_no_overlap() -> None:
    data = _make_ranker_frame()
    cfg = WalkForwardConfig(
        train_months=6,
        embargo_months=1,
        val_months=1,
        step_months=1,
        purging_mode="strict_label_overlap",
    )
    splits = _build_splits(data, cfg, horizon_days=45)
    assert splits
    for train_df, val_df in splits:
        val_start = pd.Timestamp(val_df["date"].min()).tz_localize(None)
        label_end = pd.to_datetime(train_df["date"]).dt.tz_localize(None) + pd.Timedelta(days=45)
        assert bool((label_end < val_start).all())
