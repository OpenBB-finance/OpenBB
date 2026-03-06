"""Tests for PurgedGroupKFold support."""

from __future__ import annotations

import numpy as np
import pandas as pd
from openbb_quant_ml.models import WalkForwardConfig
from openbb_quant_ml.service.ranker_modeling import PurgedGroupKFold, _build_splits


def _frame_for_month_groups(n_months: int = 12) -> pd.DataFrame:
    months = pd.date_range("2024-01-31", periods=n_months, freq="ME")
    rows: list[dict[str, object]] = []
    for month in months:
        for symbol in ("AAA", "BBB", "CCC"):
            rows.append(
                {
                    "date": pd.Timestamp(month),
                    "symbol": symbol,
                    "month_id": pd.Timestamp(month).to_period("M").strftime("%Y-%m"),
                    "target_return": 0.01,
                }
            )
    return pd.DataFrame(rows)


def test_purged_group_kfold_applies_embargo() -> None:
    groups = np.array([str(i // 3) for i in range(30)], dtype=str)
    splitter = PurgedGroupKFold(n_splits=5, embargo_pct=0.1)
    folds = splitter.split(x_data=np.zeros((30, 2)), groups=groups)
    assert folds

    for train_idx, test_idx in folds:
        train_groups = {groups[i] for i in train_idx}
        test_groups = {groups[i] for i in test_idx}
        assert train_groups.isdisjoint(test_groups)

        max_test_group = max(int(group) for group in test_groups)
        embargo_group = max_test_group + 1
        if embargo_group <= max(int(item) for item in groups):
            assert str(embargo_group) not in train_groups


def test_build_splits_supports_purged_group_kfold_mode() -> None:
    data = _frame_for_month_groups()
    cfg = WalkForwardConfig(
        train_months=6,
        embargo_months=1,
        val_months=1,
        step_months=1,
        purging_mode="purged_group_kfold",
        purged_n_splits=4,
        purged_embargo_pct=0.1,
    )
    splits = _build_splits(data, cfg, horizon_days=20)
    assert splits
    for train_df, val_df in splits:
        val_start = pd.Timestamp(val_df["date"].min()).tz_localize(None)
        label_end = pd.to_datetime(train_df["date"]).dt.tz_localize(None) + pd.Timedelta(
            days=20
        )
        assert bool((label_end < val_start).all())
