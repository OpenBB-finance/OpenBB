"""Tests for ``openbb_charting.core.to_chart``."""

from __future__ import annotations

import pytest

from openbb_charting.core.to_chart import to_chart


class TestToChart:
    """Tests for the ``to_chart`` module-level wrapper."""

    def test_success_returns_figure_and_content(self, ohlcv_df):
        """It returns the figure and a plotly JSON dict for valid OHLCV data."""
        fig, content = to_chart(ohlcv_df, symbol="AAA")
        assert fig is not None
        assert isinstance(content, dict)
        assert "data" in content
        assert "layout" in content

    def test_success_without_volume_or_candles(self, ohlcv_df):
        """It honors the volume and candles flags on the success path."""
        fig, content = to_chart(ohlcv_df, candles=False, volume=False)
        assert fig is not None
        assert isinstance(content, dict)

    def test_invalid_data_raises_wrapped_exception(self):
        """It re-raises a wrapped Exception when conversion fails."""
        with pytest.raises(Exception, match="Failed to convert results to chart"):
            to_chart("not a valid time series")
