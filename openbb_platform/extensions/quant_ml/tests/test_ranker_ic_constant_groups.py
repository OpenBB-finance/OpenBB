"""Tests for ranker IC constant-input handling."""

from __future__ import annotations

import pandas as pd
from openbb_quant_ml.service.ranker_modeling import _group_ic


def test_group_ic_skips_constant_groups() -> None:
    frame = pd.DataFrame(
        {
            "date": [
                "2026-01-01",
                "2026-01-01",
                "2026-01-01",
                "2026-01-02",
                "2026-01-02",
                "2026-01-02",
            ],
            "score": [1.0, 1.0, 1.0, 0.1, 0.2, 0.3],
            "target_return": [0.5, 0.5, 0.5, 0.3, 0.2, 0.1],
        }
    )

    ic, stats = _group_ic(
        frame,
        "score",
        "target_return",
        return_stats=True,
    )

    assert isinstance(ic, float)
    assert stats["ic_skipped_constant_groups"] >= 1
    assert stats["ic_valid_groups"] >= 1
