import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
import pytest
from openbb_core.app.model.charts.charting_settings import ChartingSettings

from openbb_charting.core.openbb_figure import OpenBBFigure


@pytest.fixture
def daily_index() -> pd.DatetimeIndex:
    return pd.date_range("2023-01-01", periods=60, freq="D")


@pytest.fixture
def daily_close(daily_index) -> pd.Series:
    rng = np.random.default_rng(7)
    values = 100 + np.cumsum(rng.normal(0, 1, len(daily_index)))
    return pd.Series(values, index=daily_index, name="close")


@pytest.fixture
def intraday_df() -> pd.DataFrame:
    idx = pd.date_range("2023-01-02 09:30", periods=80, freq="1h")
    rng = np.random.default_rng(11)
    close = 100 + np.cumsum(rng.normal(0, 1, len(idx)))
    frame = pd.DataFrame(
        {
            "open": close,
            "high": close + 1,
            "low": close - 1,
            "close": close,
            "volume": rng.integers(1_000_000, 5_000_000, len(idx)),
        },
        index=idx,
    )
    frame.index.name = "date"
    return frame


class _ReturningBackend:
    def __init__(self):
        self.called = False

    def send_figure(self, fig, command_location=""):
        self.called = True
        return fig


class _RaisingBackend:
    def send_figure(self, fig, command_location=""):
        raise RuntimeError("backend boom")


class TestInit:
    def test_default_construction(self):
        fig = OpenBBFigure()
        assert fig.theme is not None
        assert fig.bar_width == 0.15
        assert fig.cmd_xshift == 0
        assert fig.subplots_kwargs == {}
        assert fig.has_subplots is False

    def test_copy_from_existing_figure(self):
        base = go.Figure()
        base.add_scatter(x=[1, 2], y=[3, 4], name="base")
        fig = OpenBBFigure(base)
        assert len(fig.data) == 1

    def test_copy_from_dict(self):
        spec = {"data": [{"type": "scatter", "x": [1, 2], "y": [3, 4]}]}
        fig = OpenBBFigure(spec)
        assert len(fig.data) == 1

    def test_xaxis_yaxis_kwargs_applied(self):
        fig = OpenBBFigure(xaxis=dict(title="X"), yaxis=dict(title="Y"))
        assert fig.layout.xaxis.title.text == "X"
        assert fig.layout.yaxis.title.text == "Y"

    def test_property_setters(self):
        fig = OpenBBFigure()
        fig.bar_width = 0.3
        fig.cmd_xshift = 12
        fig.subplots_kwargs = {"rows": 2}
        assert fig.bar_width == 0.3
        assert fig.cmd_xshift == 12
        assert fig.subplots_kwargs == {"rows": 2}

    def test_create_backend_kwarg(self):
        from openbb_charting.core.backend import Backend

        saved = Backend.instance
        Backend.instance = None
        try:
            settings = ChartingSettings()
            fig = OpenBBFigure(charting_settings=settings, create_backend=True)
            assert Backend.instance is not None
            assert fig._backend is not None
        finally:
            Backend.instance = saved


class TestCreateSubplots:
    def test_basic_subplots(self):
        fig = OpenBBFigure.create_subplots(rows=2, cols=1)
        assert fig.has_subplots is True
        assert fig._multi_rows is True
        assert fig.subplots_kwargs["rows"] == 2

    def test_secondary_y_specs(self):
        fig = OpenBBFigure.create_subplots(
            rows=1, cols=1, specs=[[{"secondary_y": True}]]
        )
        assert fig._has_secondary_y is True

    def test_single_row_not_multi(self):
        fig = OpenBBFigure.create_subplots(rows=1, cols=1)
        assert fig._multi_rows is False


class TestTitlesAndAxes:
    def test_set_title_plain(self):
        fig = OpenBBFigure().set_title("Hello")
        assert fig.layout.title.text == "Hello"

    def test_set_title_wrap(self):
        fig = OpenBBFigure().set_title("word " * 40, wrap=True, wrap_width=20)
        assert "<br>" in fig.layout.title.text

    def test_set_title_with_row_col_adds_annotation(self):
        fig = OpenBBFigure.create_subplots(rows=1, cols=1)
        fig.set_title("Sub", row=1, col=1)
        assert len(fig.layout.annotations) == 1

    def test_set_xaxis_and_yaxis_title(self):
        fig = OpenBBFigure()
        assert fig.set_xaxis_title("X") is fig
        assert fig.set_yaxis_title("Y") is fig
        assert fig.layout.xaxis.title.text == "X"
        assert fig.layout.yaxis.title.text == "Y"


class TestLegendHelpers:
    def test_horizontal_legend(self):
        fig = OpenBBFigure()
        fig.horizontal_legend()
        assert fig.layout.legend.orientation == "h"

    def test_add_hline_legend(self):
        fig = OpenBBFigure()
        fig.add_scatter(x=[1, 2, 3], y=[4, 5, 6], name="series")
        fig.add_hline_legend(y=5, name="hl", line=dict(color="red", dash="dash"))
        assert any(t.name == "hl" for t in fig.data)

    def test_add_hline_legend_default_line(self):
        fig = OpenBBFigure()
        fig.add_scatter(x=[1, 2, 3], y=[4, 5, 6], name="series")
        fig.add_hline_legend(y=5, name="hl2")
        assert any(t.name == "hl2" for t in fig.data)

    def test_add_vline_legend_default_line(self):
        fig = OpenBBFigure()
        fig.add_scatter(x=[1, 2, 3], y=[4, 5, 6], name="series")
        fig.add_vline_legend(x=2, name="vl")
        assert any(t.name == "vl" for t in fig.data)

    def test_add_legend_label_only(self):
        fig = OpenBBFigure()
        fig.add_legend_label(label="X")
        assert any(t.name == "X" for t in fig.data)

    def test_add_legend_label_trace_template_raises(self):
        fig = OpenBBFigure()
        fig.add_scatter(x=[1, 2], y=[3, 4], name="AAPL", mode="lines")
        with pytest.raises(AttributeError):
            fig.add_legend_label(trace="AAPL")

    def test_add_legend_label_trace_not_found(self):
        fig = OpenBBFigure()
        with pytest.raises(ValueError, match="not found"):
            fig.add_legend_label(trace="NOPE")

    def test_add_legend_label_no_label(self):
        fig = OpenBBFigure()
        with pytest.raises(ValueError, match="Label must be specified"):
            fig.add_legend_label()


class TestTrend:
    def test_add_trend_creates_shapes(self, daily_index):
        rng = np.random.default_rng(3)
        base = 100 + np.cumsum(rng.normal(0, 1, len(daily_index)))
        df = pd.DataFrame(
            {"OC_High_trend": base + 5, "OC_Low_trend": base - 5}, index=daily_index
        )
        fig = OpenBBFigure.create_subplots(rows=1, cols=1)
        fig.add_trend(df)
        assert len(fig.layout.shapes) == 2

    def test_add_trend_error_wrapped(self, daily_index):
        df = pd.DataFrame(
            {"OC_High_trend": [np.nan] * len(daily_index)}, index=daily_index
        )
        fig = OpenBBFigure.create_subplots(rows=1, cols=1)
        with pytest.raises(ValueError, match="Error adding trend line"):
            fig.add_trend(df)


class TestHistPlot:
    def test_kde_curve_with_hist(self, daily_close):
        fig = OpenBBFigure.create_subplots(rows=1, cols=1)
        fig.add_histplot(daily_close, name="dist", curve="kde", show_rug=False)
        assert len(fig.data) >= 2

    def test_normal_curve_raises_on_array_max(self, daily_close):
        fig = OpenBBFigure.create_subplots(rows=1, cols=1)
        with pytest.raises(ValueError):
            fig.add_histplot(daily_close.to_numpy(), name="dist", curve="normal")

    def test_rug_only_with_str_color(self, daily_close):
        fig = OpenBBFigure.create_subplots(rows=1, cols=1)
        fig.add_histplot(
            daily_close.to_numpy(),
            name="dist",
            colors="blue",
            show_curve=False,
            show_hist=False,
            show_rug=True,
        )
        assert len(fig.data) == 1

    def test_rug_with_two_names(self, daily_close):
        fig = OpenBBFigure.create_subplots(rows=1, cols=1)
        fig.add_histplot(
            [daily_close.to_numpy()],
            name=["a", "b"],
            show_curve=False,
            show_hist=False,
            show_rug=True,
        )
        assert len(fig.data) == 1

    def test_hist_only_default_colors(self, daily_close):
        fig = OpenBBFigure.create_subplots(rows=1, cols=1)
        fig.add_histplot(
            daily_close.to_numpy(),
            show_curve=False,
            show_rug=False,
            show_hist=True,
        )
        assert len(fig.data) == 1


class TestVolume:
    def test_chart_volume_scaling_large(self):
        rng = np.random.default_rng(2)
        vol = pd.Series(rng.integers(1_000_000, 50_000_000, 40))
        out = OpenBBFigure.chart_volume_scaling(vol)
        assert set(out) == {"range", "ticks"}
        assert len(out["ticks"]) == 4

    def test_chart_volume_scaling_small(self):
        rng = np.random.default_rng(2)
        vol = pd.Series(rng.integers(100, 900, 40))
        out = OpenBBFigure.chart_volume_scaling(vol)
        assert len(out["ticks"]) == 4

    def test_add_inchart_volume(self, intraday_df):
        fig = OpenBBFigure.create_subplots(
            rows=2, cols=1, specs=[[{"secondary_y": True}], [{}]]
        )
        fig.add_inchart_volume(intraday_df)
        assert any(t.type == "bar" for t in fig.data)


class TestDateHandling:
    def test_get_dateindex_pandas(self, daily_index, daily_close):
        fig = OpenBBFigure()
        fig.add_scatter(x=daily_index, y=daily_close, name="close")
        out = fig.get_dateindex()
        assert out is not None
        assert len(out) == len(daily_index)

    def test_get_dateindex_numpy_datetime64(self, daily_index, daily_close):
        fig = OpenBBFigure()
        fig.add_scatter(
            x=daily_index.to_numpy(), y=daily_close.to_numpy(), name="close"
        )
        out = fig.get_dateindex()
        assert out is not None
        from datetime import datetime

        assert isinstance(out[0], datetime)

    def test_get_dateindex_non_date(self):
        fig = OpenBBFigure()
        fig.add_scatter(x=list(range(10)), y=list(range(10)), name="num")
        assert fig.get_dateindex() is None

    def test_get_dateindex_secondary_y(self, daily_index, daily_close):
        fig = OpenBBFigure.create_subplots(
            rows=1, cols=1, specs=[[{"secondary_y": True}]]
        )
        fig.add_scatter(x=daily_index, y=daily_close, name="primary")
        fig.add_scatter(
            x=daily_index, y=daily_close, name="secondary", secondary_y=True
        )
        out = fig.get_dateindex()
        assert out is not None
        assert len(out) == len(daily_index)

    def test_get_dateindex_skips_trace_without_xaxis(self, daily_index, daily_close):
        fig = OpenBBFigure()
        fig.add_pie(labels=["a", "b"], values=[1, 2])
        fig.add_scatter(x=daily_index, y=daily_close, name="close")
        out = fig.get_dateindex()
        assert out is not None
        assert len(out) == len(daily_index)

    def test_hide_date_gaps_daily(self, daily_index):
        df = pd.DataFrame(index=daily_index)
        df.index.name = "date"
        fig = OpenBBFigure()
        fig.hide_date_gaps(df)
        assert fig.layout.xaxis.rangebreaks is not None

    def test_hide_date_gaps_intraday_with_gap(self):
        session_a = pd.date_range("2023-01-02 09:30", periods=20, freq="30min")
        session_b = pd.date_range("2023-01-03 09:30", periods=20, freq="30min")
        df = pd.DataFrame(index=session_a.append(session_b))
        fig = OpenBBFigure()
        fig.hide_date_gaps(df)
        assert fig.layout.xaxis.rangebreaks is not None

    def test_hide_date_gaps_weekly_returns_early(self):
        idx = pd.date_range("2023-01-01", periods=40, freq="W")
        df = pd.DataFrame(index=idx)
        fig = OpenBBFigure()
        fig.hide_date_gaps(df)
        assert not fig.layout.xaxis.rangebreaks

    def test_add_rangebreaks_with_dates(self, daily_index, daily_close):
        fig = OpenBBFigure()
        fig.add_scatter(x=daily_index, y=daily_close, name="close")
        fig.get_dateindex()
        fig.add_rangebreaks()
        assert fig.layout.xaxis.rangebreaks is not None

    def test_add_rangebreaks_no_dates_returns(self):
        fig = OpenBBFigure()
        fig.add_scatter(x=[1, 2, 3], y=[4, 5, 6], name="num")
        fig.add_rangebreaks()
        assert not fig.layout.xaxis.rangebreaks

    def test_add_rangebreaks_value_error_continues(self, daily_index, daily_close):
        fig = OpenBBFigure()
        fig.add_scatter(x=daily_index, y=daily_close, name="close")
        fig.get_dateindex()
        fig._subplot_xdates = {1: {1: []}}
        fig.add_rangebreaks()
        assert fig is not None


class TestTickFormatStops:
    def test_daily_tickformatstops(self, daily_index, daily_close):
        fig = OpenBBFigure()
        fig.add_scatter(x=daily_index, y=daily_close, name="daily")
        fig.get_dateindex()
        fig._xaxis_tickformatstops()
        assert fig is not None

    def test_intraday_tickformatstops(self, intraday_df):
        fig = OpenBBFigure()
        fig.add_scatter(x=intraday_df.index, y=intraday_df["close"], name="intraday")
        fig.get_dateindex()
        fig._xaxis_tickformatstops()
        assert fig is not None

    def test_no_dateindex_returns_early(self):
        fig = OpenBBFigure()
        fig.add_scatter(x=[1, 2, 3], y=[4, 5, 6], name="num")
        fig._xaxis_tickformatstops()
        assert fig is not None

    def test_existing_tickformat_returns_early(self, daily_index, daily_close):
        fig = OpenBBFigure()
        fig.add_scatter(x=daily_index, y=daily_close, name="daily")
        fig.update_xaxes(tickformat="%Y")
        fig._xaxis_tickformatstops()
        assert fig.layout.xaxis.tickformat == "%Y"


class TestSubplotsDict:
    def test_subplots_dict_populated(self):
        fig = OpenBBFigure.create_subplots(rows=2, cols=1)
        fig.add_scatter(x=[1, 2], y=[3, 4], name="a", row=1, col=1)
        out = fig.get_subplots_dict()
        assert out

    def test_subplots_dict_empty_without_subplots(self):
        fig = OpenBBFigure()
        assert fig.get_subplots_dict() == {}

    def test_subplots_dict_skips_empty_cell(self):
        fig = OpenBBFigure.create_subplots(rows=2, cols=2, specs=[[{}, None], [{}, {}]])
        fig.add_scatter(x=[1, 2], y=[3, 4], name="a", row=1, col=1)
        assert fig.get_subplots_dict()


class TestToSubplot:
    def test_to_subplot_with_kwargs(self):
        sub = OpenBBFigure.create_subplots(rows=2, cols=1)
        src = OpenBBFigure()
        src.add_scatter(x=[1, 2, 3], y=[4, 5, 6], name="line")
        src.set_xaxis_title("X")
        src.set_yaxis_title("Y")
        out = src.to_subplot(sub, row=1, col=1, line_width=2)
        assert len(out.data) == 1

    def test_to_subplot_without_kwargs(self):
        sub = OpenBBFigure.create_subplots(rows=1, cols=1)
        src = OpenBBFigure()
        src.add_scatter(x=[1, 2, 3], y=[4, 5, 6], name="line")
        out = src.to_subplot(sub, row=1, col=1)
        assert len(out.data) == 1


class TestSerialization:
    def test_to_html(self, daily_index, daily_close):
        fig = OpenBBFigure()
        fig.add_scatter(x=daily_index, y=daily_close, name="daily")
        html = fig.to_html()
        assert isinstance(html, str)
        assert html

    def test_to_plotly_json_sets_missing_margin(self):
        fig = OpenBBFigure()
        fig.add_scatter(x=[1, 2], y=[3, 4], name="x")
        out = fig.to_plotly_json()
        assert out["layout"]["margin"]["t"] == 50
        assert out["config"]["scrollZoom"] is True

    def test_to_plotly_json_keeps_large_margin(self):
        fig = OpenBBFigure()
        fig.add_scatter(x=[1, 2], y=[3, 4], name="x")
        fig.update_layout(margin=dict(t=120))
        out = fig.to_plotly_json()
        assert out["layout"]["margin"]["t"] == 120


class TestTable:
    @pytest.fixture
    def small_df(self) -> pd.DataFrame:
        idx = pd.date_range("2023-01-01", periods=6, freq="D")
        rng = np.random.default_rng(5)
        df = pd.DataFrame(
            {"open": rng.normal(100, 1, 6), "close": rng.normal(100, 1, 6)},
            index=idx,
        )
        df.index.name = "date"
        return df

    def test_row_colors_even(self, small_df):
        colors = OpenBBFigure.row_colors(small_df.head(4))
        assert len(colors) == 4

    def test_row_colors_odd(self, small_df):
        colors = OpenBBFigure.row_colors(small_df.head(5))
        assert len(colors) == 5

    def test_tbl_values_with_index(self, small_df):
        header, cells = OpenBBFigure._tbl_values(small_df, print_index=True)
        assert header[0] == "<b>date</b>"
        assert len(cells) == 3

    def test_tbl_values_without_index(self, small_df):
        header, cells = OpenBBFigure._tbl_values(small_df, print_index=False)
        assert len(header) == 2
        assert len(cells) == 2

    def test_to_table_auto_columnwidth(self, small_df):
        fig = OpenBBFigure.to_table(small_df)
        assert any(t.type == "table" for t in fig.data)
        assert fig.layout.height > 0

    def test_to_table_no_index(self, small_df):
        fig = OpenBBFigure.to_table(small_df, print_index=False)
        assert any(t.type == "table" for t in fig.data)

    def test_to_table_small_height_width_popped(self, small_df):
        fig = OpenBBFigure.to_table(
            small_df, columnwidth=[10, 10, 10], height=1, width=1
        )
        assert fig.layout.height > 1
        assert fig.layout.width > 1

    def test_to_table_large_height_width_kept(self, small_df):
        fig = OpenBBFigure.to_table(small_df, height=100_000, width=100_000)
        assert fig.layout.height == 100_000


class TestMarginsAndAnnotations:
    def test_adjust_margins_default(self):
        fig = OpenBBFigure()
        fig._adjust_margins()
        assert fig.layout.margin.l == 80
        assert fig._margin_adjusted is True

    def test_adjust_margins_idempotent(self):
        fig = OpenBBFigure()
        fig._adjust_margins()
        first = fig.layout.margin.l
        fig._adjust_margins()
        assert fig.layout.margin.l == first

    def test_adjust_margins_existing_values(self):
        fig = OpenBBFigure()
        fig.update_layout(margin=dict(l=10, r=10, b=10, t=10, pad=2))
        fig._adjust_margins()
        assert fig.layout.margin.l == 90
        assert fig.layout.margin.pad == 2

    def test_adjust_margins_secondary_y_subplots(self):
        fig = OpenBBFigure.create_subplots(
            rows=2, cols=1, specs=[[{"secondary_y": True}], [{}]]
        )
        fig._adjust_margins()
        assert fig.layout.margin.l == 60

    def test_add_cmd_source_right_side(self):
        fig = OpenBBFigure()
        fig.add_scatter(x=[1, 2, 3], y=[4, 5, 6], name="x")
        fig.update_yaxes(side="right", title="Price")
        fig._adjust_margins()
        fig._add_cmd_source("/equity/price/historical")
        assert len(fig.layout.annotations) == 1

    def test_add_cmd_source_left_side(self):
        fig = OpenBBFigure()
        fig.add_scatter(x=[1, 2, 3], y=[4, 5, 6], name="x")
        fig.update_yaxes(side="left", title="Price")
        fig._adjust_margins()
        fig._add_cmd_source("/test")
        assert len(fig.layout.annotations) == 1

    def test_add_cmd_source_wide_margin_logscale(self):
        fig = OpenBBFigure()
        fig.add_scatter(x=[1, 2, 3], y=[4, 5, 6], name="x")
        fig.update_layout(margin=dict(l=150))
        fig._added_logscale = True
        fig.update_yaxes(side="right")
        fig._add_cmd_source("/test")
        assert len(fig.layout.annotations) == 1

    def test_add_cmd_source_secondary_axis_left(self):
        fig = OpenBBFigure.create_subplots(
            rows=1, cols=1, specs=[[{"secondary_y": True}]]
        )
        fig.add_scatter(x=[1, 2, 3], y=[4, 5, 6], name="a")
        fig.add_scatter(x=[1, 2, 3], y=[6, 5, 4], name="b", secondary_y=True)
        fig.update_yaxes(title="Left", side="left")
        fig.update_layout(yaxis2=dict(title="Right2", side="left"))
        fig._adjust_margins()
        fig._add_cmd_source("/test")
        assert len(fig.layout.annotations) == 1

    def test_add_cmd_source_no_location_noop(self):
        fig = OpenBBFigure()
        fig.add_scatter(x=[1, 2, 3], y=[4, 5, 6], name="x")
        fig._add_cmd_source("")
        assert len(fig.layout.annotations) == 0

    def test_apply_feature_flags_idempotent(self):
        fig = OpenBBFigure()
        fig._apply_feature_flags()
        assert fig._feature_flags_applied is True
        fig._apply_feature_flags()
        assert fig._feature_flags_applied is True


class TestLogScaleMenus:
    def test_add_logscale_menus(self):
        fig = OpenBBFigure()
        fig.add_logscale_menus()
        assert fig._added_logscale is True
        assert len(fig.layout.updatemenus) == 1


class TestCorrPlot:
    def test_acf_plot(self, daily_close):
        fig = OpenBBFigure()
        fig.add_corr_plot(daily_close, max_lag=10)
        assert len(fig.data) > 1

    def test_acf_plot_with_marker(self, daily_close):
        fig = OpenBBFigure()
        fig.add_corr_plot(daily_close, max_lag=10, m=3, marker={"color": "red"})
        assert len(fig.data) > 1

    def test_pacf_plot(self, daily_close):
        fig = OpenBBFigure()
        fig.add_corr_plot(daily_close, max_lag=10, pacf=True)
        assert len(fig.data) > 1

    @pytest.mark.parametrize("pacf", [False, True])
    def test_corr_plot_without_alpha_raises(self, daily_close, pacf):
        fig = OpenBBFigure()
        with pytest.raises(ValueError, match="`alpha` is required"):
            fig.add_corr_plot(daily_close, max_lag=10, alpha=None, pacf=pacf)

    def test_corr_plot_default_max_lag(self, daily_close):
        fig = OpenBBFigure()
        with pytest.raises(TypeError):
            fig.add_corr_plot(daily_close, max_lag=None)

    def test_corr_plot_irregular_lags(self, daily_close):
        fig = OpenBBFigure()
        with pytest.raises(TypeError):
            fig.add_corr_plot(daily_close, max_lag=[1, 2, 3, 4, 5])


class TestShow:
    def test_show_external_returns_self(self, daily_index, daily_close):
        fig = OpenBBFigure()
        fig.add_scatter(x=daily_index, y=daily_close, name="close")
        result = fig.show(external=True, cmd_xshift=5, bar_width=0.1)
        assert result is fig
        assert fig.cmd_xshift == 5

    def test_show_external_no_margin_no_dates(self):
        fig = OpenBBFigure()
        fig.add_scatter(x=[1, 2, 3], y=[4, 5, 6], name="x")
        result = fig.show(external=True, margin=False, date_xaxis=False)
        assert result is fig

    def test_show_headless_returns_json(self):
        settings = ChartingSettings()
        settings.headless = True
        fig = OpenBBFigure(charting_settings=settings)
        fig.add_scatter(x=[1, 2, 3], y=[4, 5, 6], name="x")
        out = fig.show()
        assert isinstance(out, str)

    def test_show_backend_success(self, monkeypatch):
        backend = _ReturningBackend()
        fig = OpenBBFigure()
        fig.add_scatter(x=[1, 2, 3], y=[4, 5, 6], name="x")
        fig._backend = backend
        result = fig.show(command_location="/route")
        assert backend.called is True
        assert result is fig

    def test_show_backend_failure_falls_back(self, monkeypatch):
        shown = {}
        monkeypatch.setattr(
            pio, "show", lambda *a, **k: shown.setdefault("called", True)
        )
        fig = OpenBBFigure()
        fig.add_scatter(x=[1, 2, 3], y=[4, 5, 6], name="x")
        fig._backend = _RaisingBackend()
        with pytest.warns(UserWarning, match="Failed to show figure"):
            fig.show()
        assert shown["called"] is True

    def test_show_no_backend_uses_pio(self, monkeypatch):
        shown = {}
        monkeypatch.setattr(
            pio, "show", lambda *a, **k: shown.setdefault("called", True)
        )
        fig = OpenBBFigure()
        fig.add_scatter(x=[1, 2, 3], y=[4, 5, 6], name="x")
        fig._backend = None
        fig.show()
        assert shown["called"] is True
