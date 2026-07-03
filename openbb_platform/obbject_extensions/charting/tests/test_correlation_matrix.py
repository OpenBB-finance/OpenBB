"""Tests for ``openbb_charting.charts.correlation_matrix``."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest
from openbb_core.provider.abstract.data import Data

from openbb_charting.charts.correlation_matrix import correlation_matrix
from openbb_charting.core.openbb_figure import OpenBBFigure


@pytest.fixture
def long_format_close() -> list[Data]:
    """Long-format close-price records for three symbols."""
    rng = np.random.default_rng(0)
    idx = pd.date_range("2023-01-01", periods=40, freq="D")
    rows: list[dict] = []
    for sym in ("AAA", "BBB", "CCC"):
        close = 100 + np.cumsum(rng.normal(0, 1, 40))
        for stamp, value in zip(idx, close):
            rows.append(
                {
                    "date": stamp.strftime("%Y-%m-%d"),
                    "symbol": sym,
                    "close": float(value),
                }
            )
    return [Data.model_validate(row) for row in rows]


class TestCorrelationMatrix:
    """Tests for the rendering paths of ``correlation_matrix``."""

    def test_wide_dataframe_pearson(self, multi_close_df):
        """It builds a Pearson correlation heatmap from a wide frame."""
        fig, content = correlation_matrix(data=multi_close_df)
        assert isinstance(fig, OpenBBFigure)
        assert isinstance(content, dict)
        assert "data" in content

    def test_method_kendall(self, multi_close_df):
        """It honors the Kendall correlation method."""
        fig, _ = correlation_matrix(data=multi_close_df, method="kendall")
        assert isinstance(fig, OpenBBFigure)

    def test_method_spearman(self, multi_close_df):
        """It honors the Spearman correlation method."""
        fig, _ = correlation_matrix(data=multi_close_df, method="spearman")
        assert isinstance(fig, OpenBBFigure)

    def test_long_format_pivot(self, long_format_close):
        """It pivots long-format ``symbol``/``close`` data before correlating."""
        fig, _ = correlation_matrix(obbject_item=long_format_close)
        assert isinstance(fig, OpenBBFigure)

    def test_list_input_via_data_kwarg(self, long_format_close):
        """It accepts a list of ``Data`` via the ``data`` kwarg."""
        fig, _ = correlation_matrix(data=long_format_close)
        assert isinstance(fig, OpenBBFigure)

    def test_custom_title_colorscale_and_layout(self, multi_close_df):
        """It honors a custom title, colorscale, and layout kwargs."""
        fig, _ = correlation_matrix(
            data=multi_close_df,
            title="My Correlations",
            colorscale="Viridis",
            layout_kwargs={"width": 500},
        )
        assert fig.layout.title.text == "My Correlations"
        assert fig.layout.width == 500
