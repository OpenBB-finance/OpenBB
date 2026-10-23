"""Tests for ``openbb_charting.charts.generic_charts``."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from openbb_charting.charts.generic_charts import (
    bar_chart,
    bar_increasing_decreasing,
    line_chart,
    surface3d,
)


@pytest.fixture
def category_bar_df() -> pd.DataFrame:
    """A small categorical frame for bar-chart tests."""
    return pd.DataFrame(
        {
            "label": ["a", "b", "c", "d"],
            "value": [10, 20, 30, 40],
            "other": [5, 15, 25, 35],
        }
    )


@pytest.fixture
def surface_points() -> tuple[pd.Series, pd.Series, pd.Series]:
    """A grid of points sufficient to triangulate a 3D surface."""
    rng = np.random.default_rng(0)
    xs, ys, zs = [], [], []
    for i in range(6):
        for j in range(6):
            xs.append(float(i))
            ys.append(float(j))
            zs.append(float(rng.uniform(0, 1)))
    return pd.Series(xs), pd.Series(ys), pd.Series(zs)


class TestLineChartInputs:
    """Tests for the accepted input types of ``line_chart``."""

    def test_none_data_raises(self):
        """It raises ValueError when data is None."""
        with pytest.raises(ValueError, match="Data is a required field"):
            line_chart(None)

    def test_dataframe_input(self, ohlcv_df):
        """It plots a single-symbol OHLCV DataFrame."""
        fig = line_chart(ohlcv_df)
        assert fig.data

    def test_series_input(self, ohlcv_df):
        """It plots a pandas Series input."""
        fig = line_chart(ohlcv_df["close"])
        assert fig.data

    def test_records_list_input(self, ohlcv_records):
        """It plots a list of record dicts."""
        fig = line_chart(ohlcv_records)
        assert fig.data

    def test_data_models_input(self, ohlcv_data):
        """It plots a list of Data models."""
        fig = line_chart(ohlcv_data)
        assert fig.data

    def test_ndarray_input(self):
        """It plots a numpy ndarray, falling back to a positional index."""
        arr = np.column_stack([np.arange(10), np.arange(10) * 2.0])
        fig = line_chart(arr)
        assert fig.data

    def test_multi_symbol_pivot(self, ohlcv_records):
        """It pivots when a multi-symbol 'symbol' column is present."""
        recs_a = [dict(r, symbol="AAA") for r in ohlcv_records]
        recs_b = [dict(r, symbol="BBB", close=r["close"] + 5) for r in ohlcv_records]
        fig = line_chart(recs_a + recs_b)
        assert len(fig.data) >= 2

    def test_date_column_promoted_to_index(self):
        """It promotes a non-index 'date' column to the datetime index."""
        df = pd.DataFrame(
            {
                "date": ["2023-01-01", "2023-01-02", "2023-01-03"],
                "close": [1.0, 2.0, 3.0],
            }
        )
        fig = line_chart(df)
        assert fig.data
        assert fig.layout.xaxis.type is None

    def test_no_date_column_falls_back_to_first_column(self):
        """It falls back to the first column when no date index is found."""
        df = pd.DataFrame({"id": [1, 2, 3], "close": [10.0, 11.0, 12.0]})
        df.index.name = None
        fig = line_chart(df)
        assert fig.data


class TestLineChartParams:
    """Tests for the parameter branches of ``line_chart``."""

    def test_normalize(self, multi_close_df):
        """It applies z-score normalization and sets the Z-Score title."""
        fig = line_chart(multi_close_df, normalize=True)
        assert "Z-Score" in fig.layout.title.text

    def test_returns(self, multi_close_df):
        """It applies cumulative returns and sets the Cumulative Returns title."""
        fig = line_chart(multi_close_df, returns=True)
        assert "Cumulative Returns" in fig.layout.title.text

    def test_returns_with_title(self, multi_close_df):
        """It appends the returns suffix to a provided title."""
        fig = line_chart(multi_close_df, returns=True, title="My Title")
        assert fig.layout.title.text == "My Title - Cumulative Returns"

    def test_normalize_with_title(self, multi_close_df):
        """It appends the z-score suffix to a provided title."""
        fig = line_chart(multi_close_df, normalize=True, title="My Title")
        assert fig.layout.title.text == "My Title - Z-Score"

    def test_same_axis(self, multi_close_df):
        """It plots all columns on a single shared axis."""
        fig = line_chart(multi_close_df, same_axis=True)
        assert len(fig.data) == len(multi_close_df.columns)
        assert all(tr.yaxis == "y" for tr in fig.data)

    def test_auto_layout_multi_axis(self, multi_close_df):
        """It auto-lays out divergent series across multiple y-axes."""
        wide = multi_close_df.copy()
        wide["BBB"] = wide["BBB"] * 1000
        wide["CCC"] = wide["CCC"] * 1_000_000
        fig = line_chart(wide)
        used_axes = {tr.yaxis for tr in fig.data}
        assert len(used_axes) >= 2

    def test_y_string_split(self, multi_close_df):
        """It splits a comma-separated y string into multiple columns."""
        fig = line_chart(multi_close_df, y="AAA,BBB", same_axis=False)
        names = {tr.name for tr in fig.data}
        assert {"AAA", "BBB"}.issubset(names)

    def test_y_and_y2_lists(self, multi_close_df):
        """It places y on the primary and y2 on the secondary axis."""
        fig = line_chart(multi_close_df, y=["AAA", "BBB"], y2=["CCC"])
        axes = {tr.name: tr.yaxis for tr in fig.data}
        assert axes["AAA"] == "y"
        assert axes["CCC"] == "y2"

    def test_titles_applied(self, multi_close_df):
        """It applies the provided axis titles to the layout."""
        fig = line_chart(
            multi_close_df,
            y=["AAA"],
            y2=["BBB"],
            ytitle="Primary",
            y2title="Secondary",
            xtitle="Time",
            title="Chart",
        )
        assert fig.layout.yaxis.title.text == "Primary"
        assert fig.layout.yaxis2.title.text == "Secondary"
        assert fig.layout.xaxis.title.text == "Time"

    def test_layout_and_scatter_kwargs(self, multi_close_df):
        """It applies layout_kwargs and scatter_kwargs overrides."""
        fig = line_chart(
            multi_close_df,
            y=["AAA"],
            layout_kwargs={"width": 1234},
            scatter_kwargs={"mode": "lines+markers"},
        )
        assert fig.layout.width == 1234
        assert any("markers" in (tr.mode or "") for tr in fig.data)

    def test_custom_hovertemplate(self, multi_close_df):
        """It honors a custom hovertemplate supplied via scatter_kwargs."""
        fig = line_chart(
            multi_close_df,
            y=["AAA"],
            scatter_kwargs={"hovertemplate": "custom<extra></extra>"},
        )
        assert any(tr.hovertemplate == "custom<extra></extra>" for tr in fig.data)

    def test_target_default_title(self, ohlcv_df):
        """It titles the chart from the default target when none is given."""
        fig = line_chart(ohlcv_df)
        assert fig.layout.title.text == "Close"

    def test_target_selection(self, ohlcv_df):
        """It selects the requested target column."""
        fig = line_chart(ohlcv_df, target="open")
        assert fig.layout.title.text == "Open"

    def test_category_xaxis_for_non_date_index(self):
        """It uses a category x-axis when the index is not date/timestamp."""
        df = pd.DataFrame({"id": [1, 2, 3], "close": [10.0, 11.0, 12.0]})
        df.index.name = None
        fig = line_chart(df)
        assert fig.layout.xaxis.type == "category"

    def test_non_numeric_data_raises(self):
        """It raises ValueError when auto-layout finds no numeric columns."""
        df = pd.DataFrame(
            {"date": pd.date_range("2023-01-01", periods=3), "close": ["x", "y", "z"]}
        ).set_index("date")
        with pytest.raises(ValueError, match="expected data with numeric values"):
            line_chart(df)

    def test_auto_layout_three_axes(self):
        """It allocates a third y-axis when three divergent series exist."""
        idx = pd.date_range("2023-01-01", periods=50, freq="D")
        df = pd.DataFrame(
            {
                "small": np.linspace(1, 2, 50),
                "medium": np.linspace(100, 200, 50),
                "large": np.linspace(10_000, 50_000, 50),
            },
            index=idx,
        )
        df.index.name = "date"
        fig = line_chart(df)
        used_axes = {tr.yaxis for tr in fig.data}
        assert "y3" in used_axes


class TestBarChart:
    """Tests for ``bar_chart``."""

    def test_vertical_single_y(self, category_bar_df):
        """It renders a vertical bar chart for a single y column."""
        fig = bar_chart(category_bar_df, x="label", y="value")
        assert fig.data
        assert fig.layout.barmode == "group"

    def test_horizontal_orientation(self, category_bar_df):
        """It renders a horizontal bar chart and a linear x-axis."""
        fig = bar_chart(category_bar_df, x="label", y="value", orientation="h")
        assert fig.data[0].orientation == "h"
        assert fig.layout.yaxis.type == "category"

    def test_multiple_y_list(self, category_bar_df):
        """It renders multiple y columns with legend shown."""
        fig = bar_chart(category_bar_df, x="label", y=["value", "other"])
        assert len(fig.data) == 2
        assert fig.data[0].showlegend is True

    def test_y_string_split(self, category_bar_df):
        """It splits a comma-separated y string into multiple bars."""
        fig = bar_chart(category_bar_df, x="label", y="value,other")
        assert len(fig.data) == 2

    def test_barmode_stack(self, category_bar_df):
        """It honors a non-group barmode."""
        fig = bar_chart(category_bar_df, x="label", y="value", barmode="stack")
        assert fig.layout.barmode == "stack"

    def test_xtype_variants(self, category_bar_df):
        """It applies the requested x-axis type for vertical bars."""
        fig = bar_chart(category_bar_df, x="label", y="value", xtype="log")
        assert fig.layout.xaxis.type == "log"

    def test_colors_applied(self, category_bar_df):
        """It applies a custom colorway when colors are provided."""
        fig = bar_chart(
            category_bar_df, x="label", y="value", colors=["#111111", "#222222"]
        )
        assert tuple(fig.layout.colorway) == ("#111111", "#222222")

    def test_titles_applied(self, category_bar_df):
        """It applies the title and axis titles."""
        fig = bar_chart(
            category_bar_df,
            x="label",
            y="value",
            title="T",
            xtitle="X",
            ytitle="Y",
        )
        assert fig.layout.title.text == "T"
        assert fig.layout.xaxis.title.text == "X"
        assert fig.layout.yaxis.title.text == "Y"

    def test_bar_kwargs_width_and_hovertemplate(self, category_bar_df):
        """It honors width and hovertemplate supplied via bar_kwargs."""
        fig = bar_chart(
            category_bar_df,
            x="label",
            y="value",
            bar_kwargs={"width": 0.5, "hovertemplate": "h<extra></extra>"},
        )
        assert fig.data[0].width == 0.5
        assert fig.data[0].hovertemplate == "h<extra></extra>"

    def test_layout_kwargs(self, category_bar_df):
        """It applies layout_kwargs overrides."""
        fig = bar_chart(
            category_bar_df, x="label", y="value", layout_kwargs={"width": 999}
        )
        assert fig.layout.width == 999

    def test_data_model_input(self, category_bar_df):
        """It accepts Data-model/list inputs and converts internally."""
        records = category_bar_df.to_dict(orient="records")
        fig = bar_chart(records, x="label", y="value")
        assert fig.data

    def test_horizontal_group_multi_width(self, category_bar_df):
        """It computes a divided width for grouped multi-series bars."""
        fig = bar_chart(
            category_bar_df,
            x="label",
            y=["value", "other"],
            orientation="h",
            barmode="group",
        )
        assert len(fig.data) == 2


class TestBarIncreasingDecreasing:
    """Tests for ``bar_increasing_decreasing``."""

    def test_horizontal_default(self):
        """It renders increasing and decreasing bars horizontally."""
        fig = bar_increasing_decreasing(
            keys=["a", "b", "c", "d"], values=[1, -2, 3, -4]
        )
        assert len(fig.data) == 2

    def test_vertical_orientation(self):
        """It renders increasing and decreasing bars vertically."""
        fig = bar_increasing_decreasing(
            keys=["a", "b", "c", "d"], values=[1, -2, 3, -4], orientation="v"
        )
        assert fig.data[0].orientation == "v"

    def test_only_increasing(self):
        """It renders a single trace when all values are positive."""
        fig = bar_increasing_decreasing(keys=["a", "b"], values=[1, 2])
        assert len(fig.data) == 1

    def test_only_decreasing(self):
        """It renders a single trace when all values are negative."""
        fig = bar_increasing_decreasing(keys=["a", "b"], values=[-1, -2])
        assert len(fig.data) == 1

    def test_group_barmode_width(self):
        """It computes a divided width for the group barmode."""
        fig = bar_increasing_decreasing(
            keys=["a", "b", "c"], values=[1, -2, 3], barmode="group"
        )
        assert fig.data

    def test_titles_and_layout_kwargs(self):
        """It applies titles and layout_kwargs overrides."""
        fig = bar_increasing_decreasing(
            keys=["a", "b"],
            values=[1, -1],
            title="T",
            xtitle="X",
            ytitle="Y",
            layout_kwargs={"width": 777},
        )
        assert fig.layout.title.text == "T"
        assert fig.layout.width == 777

    def test_invalid_values_raise(self):
        """It raises ValueError when Series construction fails."""
        with pytest.raises(ValueError, match="Error:"):
            bar_increasing_decreasing(keys=["a", "b"], values=[1])


class TestSurface3d:
    """Tests for ``surface3d``."""

    def test_basic_surface(self, surface_points):
        """It renders a 3D mesh surface from a point cloud."""
        x, y, z = surface_points
        fig = surface3d(x, y, z)
        assert fig.data

    def test_title_set(self, surface_points):
        """It sets the chart title when a non-default title is provided."""
        x, y, z = surface_points
        fig = surface3d(x, y, z, title="My Surface")
        assert fig.layout.title.text == "My Surface"

    def test_openbb_platform_title_blanked(self, surface_points):
        """It blanks the placeholder 'OpenBB Platform' title."""
        x, y, z = surface_points
        fig = surface3d(x, y, z, title="OpenBB Platform")
        assert fig.layout.title.text == ""

    def test_custom_colorscale(self, surface_points):
        """It honors a custom colorscale."""
        x, y, z = surface_points
        fig = surface3d(x, y, z, colorscale="Viridis")
        assert fig.data[0].colorscale is not None

    def test_theme_override(self, surface_points):
        """It applies a theme override without error."""
        x, y, z = surface_points
        fig = surface3d(x, y, z, theme="light")
        assert fig.data

    def test_custom_axis_titles(self, surface_points):
        """It applies custom axis titles to the scene."""
        x, y, z = surface_points
        fig = surface3d(x, y, z, xtitle="Days", ytitle="K", ztitle="Vol")
        assert fig.layout.scene.xaxis.title.text == "Days"
        assert fig.layout.scene.yaxis.title.text == "K"
        assert fig.layout.scene.zaxis.title.text == "Vol"

    def test_empty_axis_titles_default(self, surface_points):
        """It falls back to default scene titles when titles are empty."""
        x, y, z = surface_points
        fig = surface3d(x, y, z, xtitle="", ytitle="", ztitle="")
        assert fig.layout.scene.xaxis.title.text == "DTE"
        assert fig.layout.scene.yaxis.title.text == "Strike"
        assert fig.layout.scene.zaxis.title.text == "IV"

    def test_layout_kwargs(self, surface_points):
        """It applies layout_kwargs overrides."""
        x, y, z = surface_points
        fig = surface3d(x, y, z, layout_kwargs={"width": 888})
        assert fig.layout.width == 888

    def test_insufficient_points_raises(self):
        """It raises OpenBBError when too few points to triangulate."""
        from openbb_core.app.model.abstract.error import OpenBBError

        x = pd.Series([1.0, 2.0])
        y = pd.Series([1.0, 2.0])
        z = pd.Series([1.0, 2.0])
        with pytest.raises(OpenBBError, match="Not enough points"):
            surface3d(x, y, z)
