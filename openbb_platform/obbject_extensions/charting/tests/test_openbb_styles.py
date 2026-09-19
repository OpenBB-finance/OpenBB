"""Tests for ``openbb_charting.core.config.openbb_styles``."""

import pandas as pd

from openbb_charting.core.config import openbb_styles
from openbb_charting.core.config.openbb_styles import (
    PLOTLY_THEME,
    PLT_CANDLESTICKS,
    PLT_COLORWAY,
    PLT_DECREASING_COLORWAY,
    PLT_FIB_COLORWAY,
    PLT_INCREASING_COLORWAY,
    PLT_STYLE_DECREASING,
    PLT_STYLE_INCREASING,
    PLT_TBL_ROW_COLORS,
    de_increasing_color_list,
)


class TestModuleConstants:
    """Validate the structure of the exported style constants."""

    def test_colorway_lengths(self):
        """Increasing and decreasing colorways have matching lengths."""
        assert len(PLT_INCREASING_COLORWAY) == len(PLT_DECREASING_COLORWAY)
        assert len(PLT_COLORWAY) == 12

    def test_fib_colorway_mixed_types(self):
        """PLT_FIB_COLORWAY ends with dict styling entries."""
        assert isinstance(PLT_FIB_COLORWAY[-1], dict)
        assert isinstance(PLT_FIB_COLORWAY[0], str)

    def test_candlesticks_colors(self):
        """Candlestick config wires the increasing/decreasing colors."""
        assert PLT_CANDLESTICKS["increasing"]["line_color"] == PLT_STYLE_INCREASING
        assert PLT_CANDLESTICKS["decreasing"]["line_color"] == PLT_STYLE_DECREASING

    def test_table_row_colors_pair(self):
        """Table row colors are a two-element tuple."""
        assert isinstance(PLT_TBL_ROW_COLORS, tuple)
        assert len(PLT_TBL_ROW_COLORS) == 2

    def test_plotly_theme_layout(self):
        """PLOTLY_THEME exposes layout colorway and candlestick data."""
        assert PLOTLY_THEME["layout"]["colorway"] == PLT_COLORWAY
        assert "candlestick" in PLOTLY_THEME["data"]

    def test_module_level_aliases(self):
        """Module-level template and font aliases are present."""
        assert openbb_styles.PLT_STYLE_TEMPLATE == "plotly_dark"
        assert openbb_styles.PLT_FONT == openbb_styles.PLOTLY_FONT


class TestDeIncreasingColorList:
    """Exercise both branches of ``de_increasing_color_list``."""

    def test_text_branch_decreasing(self):
        """A text containing the marker yields the decreasing color."""
        result = de_increasing_color_list(text="-5%")
        assert result == [PLT_STYLE_DECREASING]

    def test_text_branch_increasing(self):
        """A text without the marker yields the increasing color."""
        result = de_increasing_color_list(text="5%")
        assert result == [PLT_STYLE_INCREASING]

    def test_dataframe_column_branch(self):
        """A column produces a per-row list keyed on the marker substring."""
        column = pd.Series(["-1", "2", "-3", "4"])
        result = de_increasing_color_list(df_column=column)
        assert result == [
            PLT_STYLE_DECREASING,
            PLT_STYLE_INCREASING,
            PLT_STYLE_DECREASING,
            PLT_STYLE_INCREASING,
        ]

    def test_custom_colors_and_contains_str(self):
        """Custom colors and contains string override the defaults."""
        column = pd.Series(["downX", "up"])
        result = de_increasing_color_list(
            df_column=column,
            contains_str="X",
            increasing_color="green",
            decreasing_color="red",
        )
        assert result == ["red", "green"]
