"""Tests for ``openbb_charting.charts.relative_rotation``."""

from __future__ import annotations

import datetime

import numpy as np
import pandas as pd
import pytest
from plotly.graph_objects import Figure

from openbb_charting.charts.relative_rotation import (
    create_rrg_with_tails,
    create_rrg_without_tails,
)


def _rrg_frame(seed: int, columns: list[str], periods: int = 90) -> pd.DataFrame:
    """Build a deterministic RS-ratio/momentum frame with a ``date`` index."""
    rng = np.random.default_rng(seed)
    idx = [stamp.date() for stamp in pd.date_range("2023-01-01", periods=periods)]
    data = {col: 100 + rng.normal(0, 2, periods) for col in columns}
    frame = pd.DataFrame(data, index=idx)
    frame.index.name = "date"
    return frame


@pytest.fixture
def ratios_momentum() -> tuple[pd.DataFrame, pd.DataFrame]:
    """A pair of RS-ratio and RS-momentum frames sharing the same columns."""
    columns = ["AAA", "BBBBBBBB", "C-D"]
    return _rrg_frame(1, columns), _rrg_frame(2, columns)


class TestCreateRrgWithTails:
    """Tests for ``create_rrg_with_tails``."""

    def test_daily_tails(self, ratios_momentum):
        """It builds daily tails without resampling."""
        ratios, momentum = ratios_momentum
        fig = create_rrg_with_tails(
            ratios.copy(), momentum.copy(), "price", "^GSPC", 16, "day"
        )
        assert isinstance(fig, Figure)
        assert len(fig.frames) == 16

    def test_weekly_tails(self, ratios_momentum):
        """It resamples to weekly tails."""
        ratios, momentum = ratios_momentum
        fig = create_rrg_with_tails(
            ratios.copy(), momentum.copy(), "price", "^GSPC", 16, "week"
        )
        assert isinstance(fig, Figure)
        assert fig.layout.title.text is not None

    def test_monthly_tails(self, ratios_momentum):
        """It resamples to monthly tails."""
        ratios, momentum = ratios_momentum
        fig = create_rrg_with_tails(
            ratios.copy(), momentum.copy(), "price", "^GSPC", 16, "month"
        )
        assert isinstance(fig, Figure)

    def test_short_symbol_names(self):
        """It uses the larger text font for short symbol names."""
        columns = ["A", "BB", "CC"]
        ratios = _rrg_frame(3, columns)
        momentum = _rrg_frame(4, columns)
        fig = create_rrg_with_tails(ratios, momentum, "price", "^GSPC", 10, "day")
        assert isinstance(fig, Figure)


class TestCreateRrgWithoutTails:
    """Tests for ``create_rrg_without_tails``."""

    def test_default_last_date(self, ratios_momentum):
        """It defaults to the last available date when none is supplied."""
        ratios, momentum = ratios_momentum
        fig = create_rrg_without_tails(
            ratios.copy(), momentum.copy(), "^GSPC", "price", None
        )
        assert isinstance(fig, Figure)
        assert len(fig.data) == 3

    def test_specific_date_found(self, ratios_momentum):
        """It targets a specific date present in the index."""
        ratios, momentum = ratios_momentum
        target = str(ratios.index[-5])
        fig = create_rrg_without_tails(
            ratios.copy(), momentum.copy(), "^GSPC", "price", target
        )
        assert isinstance(fig, Figure)

    def test_date_not_found_warns(self, ratios_momentum):
        """It warns and falls back to the last date for an absent date."""
        ratios, momentum = ratios_momentum
        with pytest.warns(UserWarning, match="not found in data"):
            fig = create_rrg_without_tails(
                ratios.copy(),
                momentum.copy(),
                "^GSPC",
                "price",
                datetime.date(1999, 1, 1),
            )
        assert isinstance(fig, Figure)

    def test_short_symbol_names(self):
        """It uses the larger text font for short symbol names."""
        columns = ["A", "BB", "CC"]
        ratios = _rrg_frame(5, columns)
        momentum = _rrg_frame(6, columns)
        fig = create_rrg_without_tails(ratios, momentum, "^GSPC", "price", None)
        assert isinstance(fig, Figure)
