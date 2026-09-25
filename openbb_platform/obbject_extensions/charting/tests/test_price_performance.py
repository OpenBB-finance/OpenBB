"""Tests for ``openbb_charting.charts.price_performance``."""

from __future__ import annotations

import pandas as pd
import pytest
from openbb_core.provider.abstract.data import Data

from openbb_charting.charts.price_performance import price_performance
from openbb_charting.core.openbb_figure import OpenBBFigure

_COLS = (
    "one_day",
    "one_week",
    "one_month",
    "three_month",
    "six_month",
    "ytd",
    "one_year",
    "two_year",
    "three_year",
    "four_year",
    "five_year",
)


def _perf_row(symbol: str, sign: float) -> dict:
    """Build a single price-performance record for ``symbol``."""
    values = {col: round(sign * (i + 1) / 100, 4) for i, col in enumerate(_COLS)}
    return {"symbol": symbol, **values}


@pytest.fixture
def performance_data() -> list[Data]:
    """Two-symbol price-performance records as ``Data`` models."""
    rows = [_perf_row("AAA", 1.0), _perf_row("BBB", -1.0)]
    return [Data.model_validate(row) for row in rows]


class TestPricePerformance:
    """Tests for the happy paths of ``price_performance``."""

    def test_vertical_orientation(self, performance_data):
        """It draws a vertical bar chart and returns plotly JSON."""
        fig, content = price_performance(obbject_item=performance_data)
        assert isinstance(fig, OpenBBFigure)
        assert isinstance(content, dict)
        assert "data" in content

    def test_horizontal_orientation(self, performance_data):
        """It swaps the axis titles for horizontal orientation."""
        fig, _ = price_performance(obbject_item=performance_data, orientation="h")
        assert isinstance(fig, OpenBBFigure)

    def test_dataframe_input(self, performance_data):
        """It accepts a pre-built DataFrame via the ``data`` kwarg."""
        df = pd.DataFrame([_perf_row("AAA", 1.0), _perf_row("BBB", -1.0)])
        fig, _ = price_performance(data=df)
        assert isinstance(fig, OpenBBFigure)

    def test_list_input_via_data_kwarg(self, performance_data):
        """It accepts a list of ``Data`` via the ``data`` kwarg."""
        fig, _ = price_performance(data=performance_data)
        assert isinstance(fig, OpenBBFigure)

    def test_custom_title_and_layout(self, performance_data):
        """It honors a custom title and extra layout kwargs."""
        fig, _ = price_performance(
            obbject_item=performance_data,
            title="My Performance",
            layout_kwargs={"showlegend": False},
        )
        assert fig.layout.title.text == "My Performance"
        assert fig.layout.showlegend is False

    def test_limit_trims_rows(self, performance_data):
        """It limits the number of plotted periods when ``limit`` is given."""
        fig, _ = price_performance(obbject_item=performance_data, limit=3)
        assert isinstance(fig, OpenBBFigure)

    def test_drops_duplicate_rows(self):
        """It de-duplicates identical rows before plotting."""
        rows = [_perf_row("AAA", 1.0), _perf_row("AAA", 1.0)]
        data = [Data.model_validate(row) for row in rows]
        fig, _ = price_performance(data=data)
        assert isinstance(fig, OpenBBFigure)

    def test_none_value_cell(self):
        """It tolerates a ``None`` value in a performance column."""
        row = _perf_row("AAA", 1.0)
        row["one_day"] = None
        df = pd.DataFrame([row, _perf_row("BBB", 1.0)])
        fig, _ = price_performance(data=df)
        assert isinstance(fig, OpenBBFigure)


class TestPricePerformanceErrors:
    """Tests for the error branches of ``price_performance``."""

    def test_empty_data_raises(self):
        """It raises when the input frame has no rows."""
        with pytest.raises(ValueError, match="No data was found"):
            price_performance(data=pd.DataFrame())

    def test_no_matching_columns_raises(self):
        """It raises when none of the expected performance columns exist."""
        df = pd.DataFrame({"symbol": ["AAA"], "unrelated": [1.0]})
        with pytest.raises(ValueError, match="No columns matching"):
            price_performance(data=df)
