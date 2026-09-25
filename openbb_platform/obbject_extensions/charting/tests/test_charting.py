"""Tests for the ``openbb_charting.charting.Charting`` accessor class."""

from __future__ import annotations

import warnings
from types import SimpleNamespace

import numpy as np
import pandas as pd
import pytest
from openbb_core.app.model.charts.chart import Chart
from openbb_core.app.model.obbject import OBBject
from openbb_core.provider.abstract.data import Data

from openbb_charting.charting import Charting
from openbb_charting.core.backend import Backend
from openbb_charting.core.openbb_figure import OpenBBFigure
from openbb_charting.query_params import EquityPriceHistoricalChartQueryParams

# pylint: disable=protected-access,redefined-outer-name


class LocalChartingViews:
    """A real charting-view class registered for the duration of the tests."""

    @staticmethod
    def equity_price_historical(**kwargs):
        """Render the real price-historical chart (returns a (fig, content) tuple)."""
        from openbb_charting.charts.price_historical import price_historical

        return price_historical(**kwargs)

    @staticmethod
    def custom_help_view(**kwargs):
        """A charted route with no ChartParams entry, to drive the help fallback."""
        from openbb_charting.charts.price_historical import price_historical

        return price_historical(**kwargs)

    @staticmethod
    def raise_runtime(**kwargs):
        """A view that raises ``RuntimeError`` to drive the re-raise branch."""
        raise RuntimeError("charting does not support test")


class RecorderApp:
    """A real stand-in for the PyWry GUI app that records dispatched calls."""

    def __init__(self):
        """Initialize the recorder with empty call logs."""
        self.calls: list[str] = []
        self.theme = None

    def emit(self, *args, **kwargs):
        """Record an emit call."""
        self.calls.append("emit")

    def show_plotly(self, **kwargs):
        """Record a ``show_plotly`` call."""
        self.calls.append("show_plotly")
        return "plotly"

    def show_dataframe(self, **kwargs):
        """Record a ``show_dataframe`` call."""
        self.calls.append("show_dataframe")
        return "dataframe"

    def show(self, **kwargs):
        """Record a ``show`` call."""
        self.calls.append("show")
        return "show"

    def close(self, **kwargs):
        """Record a ``close`` call."""
        self.calls.append("close")


class RecorderBackend:
    """A real stand-in for ``Backend.send_table`` / ``send_url`` delegation."""

    def __init__(self):
        """Initialize the recorder with empty call logs."""
        self.tables: list[dict] = []
        self.urls: list[dict] = []

    def send_table(self, **kwargs):
        """Record a table dispatch."""
        self.tables.append(kwargs)

    def send_url(self, **kwargs):
        """Record a URL dispatch."""
        self.urls.append(kwargs)


class RaisingBackend:
    """A real backend whose dispatch methods raise, to drive warn branches."""

    def send_table(self, **kwargs):
        """Raise to trigger the table warn branch."""
        raise RuntimeError("table boom")

    def send_url(self, **kwargs):
        """Raise to trigger the URL warn branch."""
        raise RuntimeError("url boom")


def _make_ohlcv(seed: int = 7, periods: int = 60) -> pd.DataFrame:
    """Build a deterministic OHLCV frame indexed by date."""
    rng = np.random.default_rng(seed)
    idx = pd.date_range("2023-01-01", periods=periods, freq="D")
    close = 100 + np.cumsum(rng.normal(0, 1, periods))
    frame = pd.DataFrame(
        {
            "open": close + rng.normal(0, 0.5, periods),
            "high": close + 1,
            "low": close - 1,
            "close": close,
            "volume": rng.integers(1_000_000, 5_000_000, periods),
        },
        index=idx,
    )
    frame.index.name = "date"
    return frame


def _df_to_data(frame: pd.DataFrame) -> list[Data]:
    """Convert an OHLCV frame to date-stamped ``Data`` records."""
    records = frame.reset_index()
    records["date"] = records["date"].dt.strftime("%Y-%m-%d")
    return [Data.model_validate(row) for row in records.to_dict(orient="records")]


@pytest.fixture(autouse=True)
def local_views():
    """Register the local real view class for the duration of each test."""
    original = Charting._extension_views_cache
    Charting._extension_views_cache = [LocalChartingViews]
    try:
        yield
    finally:
        Charting._extension_views_cache = original


@pytest.fixture(autouse=True)
def reset_backend_singleton():
    """Reset the ``Backend`` singleton around each test to avoid state leakage."""
    Backend.instance = None
    yield
    Backend.instance = None


def _obbject(route: str, results=None) -> OBBject:
    """Build a real ``OBBject`` with the given route and OHLCV results."""
    obj = OBBject(
        results=_df_to_data(_make_ohlcv()) if results is None else results,
        provider="test",
    )
    obj._route = route
    obj._standard_params = {"symbol": "AAA"}
    obj._extra_params = {}
    return obj


@pytest.fixture
def equity_obbject() -> OBBject:
    """A real ``OBBject`` shaped like equity price history with a resolvable view."""
    return _obbject("/equity/price/historical")


class TestConstruction:
    """Tests for ``Charting`` construction and class accessors."""

    def test_construct_from_real_obbject(self, equity_obbject):
        """It constructs from a real ``OBBject`` with a real backend."""
        charting = Charting(equity_obbject)
        assert isinstance(charting, Charting)
        assert charting._functions

    def test_get_backend_class(self):
        """``get_backend_class`` returns the built-in PyWry backend."""
        assert Charting.get_backend_class() is Backend

    def test_get_figure_class(self):
        """``get_figure_class`` returns ``OpenBBFigure``."""
        assert Charting.get_figure_class() is OpenBBFigure

    def test_functions_lists_registered_views(self):
        """``functions`` lists charting functions from the registered views."""
        functions = Charting.functions()
        assert "equity_price_historical" in functions

    def test_extension_views_loaded_from_entry_points(self):
        """``_get_extension_views`` loads real entry points when uncached."""
        Charting._extension_views_cache = None
        views = Charting._get_extension_views()
        assert isinstance(views, list)

    def test_indicators_returns_params(self):
        """``indicators`` returns the aggregate indicators-params model."""
        keys = list(Charting.indicators().model_dump().keys())
        assert "sma" in keys
        assert "macd" in keys


class TestChartFunctionResolution:
    """Tests for ``_get_chart_function`` route resolution."""

    def test_resolves_known_route(self, equity_obbject):
        """It resolves a known route to a callable."""
        charting = Charting(equity_obbject)
        func = charting._get_chart_function("/equity/price/historical")
        assert callable(func)

    def test_none_route_raises(self, equity_obbject):
        """A ``None`` route raises a ``ValueError``."""
        charting = Charting(equity_obbject)
        with pytest.raises(ValueError, match="no function route"):
            charting._get_chart_function(None)

    def test_unknown_route_raises(self, equity_obbject):
        """An unknown route raises a ``ValueError``."""
        charting = Charting(equity_obbject)
        with pytest.raises(ValueError, match="Could not find the route"):
            charting._get_chart_function("/does/not/exist")


class TestGetParams:
    """Tests for the ``get_params`` accessor."""

    def test_known_route_returns_params_class(self, equity_obbject):
        """A registered route returns its instantiated query-params class."""
        params = Charting(equity_obbject).get_params()
        assert isinstance(params, EquityPriceHistoricalChartQueryParams)

    def test_unregistered_route_returns_help(self):
        """A charted route with no ChartParams entry routes through ``help``."""
        obj = _obbject("/custom/help/view")
        obj.extra = {"metadata": SimpleNamespace(route="/custom/help/view")}
        assert Charting(obj).get_params() is None

    def test_none_route_raises(self, equity_obbject):
        """A ``None`` route raises a ``ValueError``."""
        equity_obbject._route = None
        with pytest.raises(ValueError, match="no function route"):
            Charting(equity_obbject).get_params()


class TestPrepareDataAsDf:
    """Tests for ``_prepare_data_as_df``."""

    def test_with_external_dataframe(self, equity_obbject):
        """It returns the supplied DataFrame and a True ``has_data`` flag."""
        frame = _make_ohlcv()
        data_df, has_data = Charting(equity_obbject)._prepare_data_as_df(frame)
        assert has_data is True
        assert "close" in data_df.columns

    def test_without_data_uses_obbject(self, equity_obbject):
        """With no data it falls back to the OBBject contents."""
        data_df, has_data = Charting(equity_obbject)._prepare_data_as_df(None)
        assert has_data is False
        assert "close" in data_df.columns

    def test_drops_provider_column(self, equity_obbject):
        """A ``provider`` column present in the data is dropped."""
        records = [
            Data.model_validate({"date": "2023-01-01", "close": 1.0, "provider": "x"}),
            Data.model_validate({"date": "2023-01-02", "close": 2.0, "provider": "x"}),
        ]
        data_df, _ = Charting(equity_obbject)._prepare_data_as_df(records)
        assert "provider" not in data_df.columns


class TestCreateCharts:
    """Tests for the generic chart constructors."""

    def test_create_line_chart_returns_figure(self, equity_obbject):
        """``create_line_chart`` returns an ``OpenBBFigure`` when not rendering."""
        frame = _make_ohlcv()
        fig = Charting(equity_obbject).create_line_chart(frame, render=False)
        assert isinstance(fig, OpenBBFigure)

    def test_create_line_chart_render_dispatches(self, equity_obbject):
        """``create_line_chart`` with render dispatches through the GUI boundary."""
        charting = Charting(equity_obbject)
        charting._backend._app = RecorderApp()
        frame = pd.DataFrame({"a": np.arange(10.0), "b": np.arange(10.0)})
        charting.create_line_chart(frame, render=True)
        assert "show_plotly" in charting._backend._app.calls

    def test_create_bar_chart_returns_figure(self, equity_obbject):
        """``create_bar_chart`` returns an ``OpenBBFigure`` when not rendering."""
        frame = pd.DataFrame(
            {"label": ["a", "b", "c"], "value": [1, 2, 3], "other": [3, 2, 1]}
        )
        fig = Charting(equity_obbject).create_bar_chart(
            frame, x="label", y=["value", "other"], render=False
        )
        assert isinstance(fig, OpenBBFigure)

    def test_create_bar_chart_render_dispatches(self, equity_obbject):
        """``create_bar_chart`` with render dispatches through the GUI boundary."""
        charting = Charting(equity_obbject)
        charting._backend._app = RecorderApp()
        frame = pd.DataFrame({"label": ["a", "b"], "value": [1, 2]})
        charting.create_bar_chart(frame, x="label", y="value", render=True)
        assert "show_plotly" in charting._backend._app.calls

    def test_create_3d_surface(self, equity_obbject):
        """``create_3d_surface`` returns an ``OpenBBFigure``."""
        x = pd.Series([1, 2, 3, 1, 2, 3])
        y = pd.Series([1, 1, 1, 2, 2, 2])
        z = pd.Series([1.0, 2.0, 3.0, 4.0, 5.0, 6.0])
        fig = Charting(equity_obbject).create_3d_surface(x, y, z)
        assert isinstance(fig, OpenBBFigure)

    def test_create_correlation_matrix(self, equity_obbject):
        """``create_correlation_matrix`` returns an ``OpenBBFigure``."""
        rng = np.random.default_rng(3)
        frame = pd.DataFrame(
            {
                "a": rng.normal(0, 1, 30),
                "b": rng.normal(0, 1, 30),
                "c": rng.normal(0, 1, 30),
            }
        )
        fig = Charting(equity_obbject).create_correlation_matrix(frame)
        assert isinstance(fig, OpenBBFigure)


class TestNormalizeChartResponse:
    """Tests for ``_normalize_chart_response`` branch coverage."""

    @pytest.fixture
    def charting(self, equity_obbject) -> Charting:
        """A constructed ``Charting`` instance."""
        return Charting(equity_obbject)

    @pytest.fixture
    def figure(self) -> OpenBBFigure:
        """A simple populated ``OpenBBFigure``."""
        fig = OpenBBFigure()
        fig.add_scatter(x=[1, 2, 3], y=[1, 2, 3])
        return fig

    def test_chart_passthrough(self, charting, figure):
        """A ``Chart`` instance is returned as-is."""
        chart = Chart(fig=figure, content=None, format="plotly")
        _, result = charting._normalize_chart_response(chart, {})
        assert result is chart

    def test_openbbfigure_serialized(self, charting, figure):
        """An ``OpenBBFigure`` is serialized into a plotly ``Chart``."""
        fig, chart = charting._normalize_chart_response(figure, {})
        assert fig is figure
        assert chart.format == "plotly"
        assert chart.content is not None

    def test_tuple_with_openbbfigure(self, charting, figure):
        """A ``(OpenBBFigure, content)`` tuple is serialized to a plotly ``Chart``."""
        _, chart = charting._normalize_chart_response((figure, {"x": 1}), {})
        assert chart.format == "plotly"

    def test_tuple_with_plain_figure(self, charting):
        """A ``(non-figure, content)`` tuple keeps the supplied content."""
        _, chart = charting._normalize_chart_response(("not a fig", {"x": 1}), {})
        assert chart.format == "str"
        assert chart.content == {"x": 1}

    def test_unknown_response(self, charting):
        """An unrecognized response yields an ``unknown`` format ``Chart``."""
        _, chart = charting._normalize_chart_response("nonsense", {})
        assert chart.format == "unknown"


class TestShow:
    """Tests for the ``show`` method."""

    def test_show_resolves_real_view(self, equity_obbject):
        """``show`` resolves the registered view and stores a plotly chart."""
        charting = Charting(equity_obbject)
        charting.show(render=False)
        assert equity_obbject.chart is not None
        assert equity_obbject.chart.format == "plotly"

    def test_show_render_dispatches(self, equity_obbject):
        """``show`` with render dispatches the figure through the GUI boundary."""
        charting = Charting(equity_obbject)
        charting._backend._app = RecorderApp()
        charting.show(render=True)
        assert "show_plotly" in charting._backend._app.calls

    def test_show_applies_extra_params(self, equity_obbject):
        """``show`` merges OBBject extra params into the supplied extra_params."""
        equity_obbject._extra_params = {"target": "close"}
        charting = Charting(equity_obbject)
        charting.show(render=False, extra_params={})
        assert equity_obbject.chart is not None

    def test_show_generic_fallback_for_unknown_route(self):
        """A route without a view falls back to the generic line chart."""
        obj = _obbject("/made/up/route")
        charting = Charting(obj)
        charting.show(render=False)
        assert obj.chart is not None
        assert obj.chart.format == "plotly"

    def test_show_reraises_runtime_error(self):
        """A ``RuntimeError`` raised by the view is re-raised unchanged."""
        obj = _obbject("/raise/runtime")
        charting = Charting(obj)
        with pytest.raises(RuntimeError, match="does not support test"):
            charting.show(render=False)

    def test_show_fallback_failure_raises_runtime_error(self):
        """When even the generic fallback fails, a ``RuntimeError`` is raised."""
        obj = _obbject("/made/up/route", results="not-a-time-series")
        charting = Charting(obj)
        with pytest.raises(RuntimeError, match="Failed to automatically create"):
            charting.show(render=False)

    def test_show_generic_fallback_render_dispatches(self):
        """The generic fallback with render dispatches through the GUI boundary."""
        obj = _obbject("/made/up/route")
        charting = Charting(obj)
        charting._backend._app = RecorderApp()
        charting.show(render=True)
        assert "show_plotly" in charting._backend._app.calls


class TestHookContext:
    """Tests for hook-context construction."""

    def test_make_hook_context_applies_overrides(self, equity_obbject):
        """Overrides supplied to ``_make_hook_context`` are set on the context."""
        from openbb_core.app.charting import ChartLifecycle

        charting = Charting(equity_obbject)
        context = charting._make_hook_context(
            ChartLifecycle.PRE_FIGURE, figure="FIG", content="CONTENT"
        )
        assert context.figure == "FIG"
        assert context.content == "CONTENT"


class TestToChart:
    """Tests for the ``to_chart`` method."""

    def test_to_chart_without_data(self, equity_obbject):
        """``to_chart`` with no data uses the OBBject contents."""
        charting = Charting(equity_obbject)
        charting.to_chart(render=False)
        assert equity_obbject.chart is not None
        assert equity_obbject.chart.format == "plotly"

    def test_to_chart_with_external_data(self, equity_obbject):
        """``to_chart`` honors external data and a target column."""
        charting = Charting(equity_obbject)
        charting.to_chart(data=_make_ohlcv(), target="close", render=False)
        assert equity_obbject.chart is not None

    def test_to_chart_render_dispatches(self, equity_obbject):
        """``to_chart`` with render dispatches through the GUI boundary."""
        charting = Charting(equity_obbject)
        charting._backend._app = RecorderApp()
        charting.to_chart(render=True)
        assert "show_plotly" in charting._backend._app.calls

    def test_to_chart_fallback(self):
        """``to_chart`` falls back to a generic line chart for a viewless route."""
        obj = _obbject("/made/up/route")
        charting = Charting(obj)
        charting.to_chart(render=False)
        assert obj.chart is not None

    def test_to_chart_fallback_when_show_raises(self):
        """``to_chart`` recovers via its own generic chart when ``show`` raises."""
        obj = _obbject("/raise/runtime")
        charting = Charting(obj)
        charting.to_chart(render=False)
        assert obj.chart is not None
        assert obj.chart.format == "plotly"

    def test_to_chart_fallback_render_dispatches(self):
        """``to_chart`` fallback with render dispatches through the GUI boundary."""
        obj = _obbject("/raise/runtime")
        charting = Charting(obj)
        charting._backend._app = RecorderApp()
        charting.to_chart(render=True)
        assert "show_plotly" in charting._backend._app.calls

    def test_to_chart_fallback_failure_raises_runtime_error(self):
        """``to_chart`` raises a ``RuntimeError`` when its fallback also fails."""
        obj = _obbject("/raise/runtime")
        charting = Charting(obj)
        with pytest.raises(RuntimeError, match="Failed to automatically create"):
            charting.to_chart(
                data=pd.DataFrame({"label": ["x", "y", "z"]}), render=False
            )


class TestTable:
    """Tests for the ``table`` method."""

    def test_table_with_query_toolbar(self, equity_obbject):
        """``table`` dispatches with the query toolbar enabled by default."""
        charting = Charting(equity_obbject)
        recorder = RecorderBackend()
        charting._backend = recorder
        charting.table()
        assert len(recorder.tables) == 1
        assert "include_query_toolbar" not in recorder.tables[0]

    def test_table_without_query_toolbar(self, equity_obbject):
        """``table`` forwards the disabled query-toolbar flag."""
        charting = Charting(equity_obbject)
        recorder = RecorderBackend()
        charting._backend = recorder
        charting.table(include_query_toolbar=False)
        assert recorder.tables[0]["include_query_toolbar"] is False

    def test_table_with_named_index_and_title(self, equity_obbject):
        """``table`` resets a named index and uses the explicit title."""
        charting = Charting(equity_obbject)
        recorder = RecorderBackend()
        charting._backend = recorder
        charting.table(data=_make_ohlcv(), title="My Title")
        assert recorder.tables[0]["title"] == "My Title"

    def test_table_with_range_index(self, equity_obbject):
        """``table`` handles a default ``RangeIndex`` DataFrame."""
        charting = Charting(equity_obbject)
        recorder = RecorderBackend()
        charting._backend = recorder
        charting.table(data=pd.DataFrame({"a": [1, 2, 3]}))
        assert len(recorder.tables) == 1

    def test_table_warns_on_backend_failure(self, equity_obbject):
        """``table`` warns when the backend dispatch raises."""
        charting = Charting(equity_obbject)
        charting._backend = RaisingBackend()
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            charting.table()
        assert any("Failed to show table" in str(w.message) for w in caught)


class TestUrl:
    """Tests for the ``url`` method."""

    def test_url_delegates_to_backend(self, equity_obbject):
        """``url`` forwards its arguments to the backend dispatch."""
        charting = Charting(equity_obbject)
        recorder = RecorderBackend()
        charting._backend = recorder
        charting.url("https://example.com", title="Docs", width=100, height=200)
        assert recorder.urls[0]["url"] == "https://example.com"
        assert recorder.urls[0]["width"] == 100

    def test_url_warns_on_backend_failure(self, equity_obbject):
        """``url`` warns when the backend dispatch raises."""
        charting = Charting(equity_obbject)
        charting._backend = RaisingBackend()
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            charting.url("https://example.com")
        assert any("Failed to show figure" in str(w.message) for w in caught)


class TestToggleAndStyle:
    """Tests for chart-style helpers."""

    def test_toggle_chart_style_without_chart_raises(self, equity_obbject):
        """Toggling style with no chart present raises a ``ValueError``."""
        charting = Charting(equity_obbject)
        with pytest.raises(ValueError, match="No chart has been created"):
            charting.toggle_chart_style()

    def test_toggle_chart_style_flips_style(self, equity_obbject):
        """Toggling style flips the configured chart style and updates the chart."""
        charting = Charting(equity_obbject)
        charting.show(render=False)
        before = charting._charting_settings.chart_style
        charting.toggle_chart_style()
        assert charting._charting_settings.chart_style != before
        assert equity_obbject.chart.content is not None

    def test_set_chart_style_is_passthrough(self, equity_obbject):
        """``_set_chart_style`` returns the figure unchanged."""
        charting = Charting(equity_obbject)
        fig = OpenBBFigure()
        assert charting._set_chart_style(fig) is fig


class TestConvertToString:
    """Tests for the static ``_convert_to_string`` sanitizer."""

    def test_finite_number_passes_through(self):
        """A finite number is returned unchanged."""
        assert Charting._convert_to_string(1.5) == 1.5

    def test_nan_becomes_empty_string(self):
        """A NaN float renders as an empty string."""
        assert Charting._convert_to_string(float("nan")) == ""

    def test_dict_joins_values(self):
        """A dict is rendered as a comma-joined list of its values."""
        assert Charting._convert_to_string({"a": 1, "b": 2}) == "1, 2"

    def test_list_of_dicts_joins_values(self):
        """A list of dicts joins each dict's values."""
        assert Charting._convert_to_string([{"a": 1}, {"b": 2}]) == "1, 2"

    def test_plain_list_joins_items(self):
        """A plain list joins its items with commas."""
        assert Charting._convert_to_string([1, 2, 3]) == "1, 2, 3"

    def test_string_strips_brackets(self):
        """A string value strips bracket characters."""
        assert Charting._convert_to_string("[hello]") == "hello"
