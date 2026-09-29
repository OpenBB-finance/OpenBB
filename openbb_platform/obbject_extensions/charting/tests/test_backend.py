"""Tests for ``openbb_charting.core.backend``."""

from __future__ import annotations

import builtins

import pandas as pd
import plotly.graph_objects as go
import pytest
from openbb_core.app.model.charts.charting_settings import ChartingSettings

from openbb_charting.core.backend import Backend

# pylint: disable=protected-access


class RecorderApp:
    """A real stand-in for the PyWry GUI app that records dispatched calls."""

    def __init__(self):
        """Initialize the recorder with empty call logs."""
        self.events: list[str] = []
        self.calls: list[tuple[str, dict]] = []
        self.theme = None

    def emit(self, event, payload, label):
        """Record an emitted event name."""
        self.events.append(event)

    def show_plotly(self, **kwargs):
        """Record a ``show_plotly`` call and its kwargs."""
        self.calls.append(("show_plotly", kwargs))
        return "plotly"

    def show_dataframe(self, **kwargs):
        """Record a ``show_dataframe`` call and its kwargs."""
        self.calls.append(("show_dataframe", kwargs))
        return "dataframe"

    def show(self, **kwargs):
        """Record a ``show`` call and its kwargs."""
        self.calls.append(("show", kwargs))
        return "show"

    def close(self, **kwargs):
        """Record a ``close`` call."""
        self.calls.append(("close", kwargs))


@pytest.fixture
def reset_singleton():
    """Reset the ``Backend`` singleton around each test."""
    Backend.instance = None
    yield
    Backend.instance = None


@pytest.fixture
def light_settings() -> ChartingSettings:
    """A ``ChartingSettings`` instance configured for light mode."""
    settings = ChartingSettings()
    settings.chart_style = "light"
    return settings


@pytest.fixture
def dark_settings() -> ChartingSettings:
    """A ``ChartingSettings`` instance configured for dark mode."""
    settings = ChartingSettings()
    settings.chart_style = "dark"
    return settings


@pytest.fixture
def backend_with_recorder(reset_singleton, dark_settings):
    """A real ``Backend`` whose GUI app is replaced with a recorder."""
    backend = Backend(dark_settings)
    backend._app = RecorderApp()
    return backend


class TestBackendConstruction:
    """Tests for ``Backend`` construction and template registration."""

    def test_singleton_returns_same_instance(self, reset_singleton, light_settings):
        """Two constructions return the same singleton instance."""
        first = Backend(light_settings)
        second = Backend(light_settings)
        assert first is second

    def test_light_mode_sets_is_dark_false(self, reset_singleton, light_settings):
        """Light chart style yields ``_is_dark`` False."""
        backend = Backend(light_settings)
        assert backend._is_dark is False

    def test_dark_mode_sets_is_dark_true(self, reset_singleton, dark_settings):
        """Dark chart style yields ``_is_dark`` True."""
        backend = Backend(dark_settings)
        assert backend._is_dark is True

    def test_templates_registered(self, reset_singleton, dark_settings):
        """Template dicts are produced during construction."""
        backend = Backend(dark_settings)
        assert isinstance(backend._template_dark, dict)
        assert isinstance(backend._template_light, dict)

    def test_register_templates_returns_two_dicts(self):
        """The static template registrar returns a dark/light dict pair."""
        dark, light = Backend._register_templates()
        assert isinstance(dark, dict)
        assert isinstance(light, dict)

    def test_import_error_falls_back_to_dummy_backend(
        self, reset_singleton, light_settings
    ):
        """A failed ``pywry`` import swaps in the headless ``DummyBackend``."""
        from openbb_charting.core.dummy_backend import DummyBackend

        real_import = builtins.__import__

        def fake_import(name, *args, **kwargs):
            if name == "pywry":
                raise ImportError("forced for test")
            return real_import(name, *args, **kwargs)

        builtins.__import__ = fake_import
        try:
            backend = Backend(light_settings)
            assert isinstance(backend._app, DummyBackend)
        finally:
            builtins.__import__ = real_import


class TestToolbarsAndCallbacks:
    """Tests for the headless toolbar and callback builders."""

    def test_header_toolbar_builds(self, backend_with_recorder):
        """The header toolbar builds and has items."""
        toolbar = backend_with_recorder._header_toolbar()
        assert toolbar.items

    def test_query_toolbar_builds(self, backend_with_recorder):
        """The query toolbar builds and has items."""
        toolbar = backend_with_recorder._query_toolbar()
        assert toolbar.items

    def test_callbacks_registers_theme_toggle(self, backend_with_recorder):
        """The base callbacks map registers the theme toggle handler."""
        callbacks = backend_with_recorder._callbacks()
        assert "app:toggle-theme" in callbacks

    def test_table_callbacks_registers_query_handlers(self, backend_with_recorder):
        """The table callbacks map registers the query handlers."""
        callbacks = backend_with_recorder._table_callbacks()
        assert {"query:submit", "query:input", "query:reset"} <= set(callbacks)


class TestThemeToggle:
    """Tests for the theme-toggle handler."""

    def test_toggle_without_current_figure(self, backend_with_recorder):
        """Toggling flips ``_is_dark`` and emits update events with no figure."""
        backend_with_recorder._current_fig = None
        before = backend_with_recorder._is_dark
        backend_with_recorder._handle_theme_toggle({}, "event", "label")
        assert backend_with_recorder._is_dark is not before
        assert "pywry:update-theme" in backend_with_recorder._app.events

    def test_toggle_with_current_figure(self, backend_with_recorder):
        """Toggling updates the layout of the current figure when present."""
        fig = go.Figure()
        fig.add_scatter(x=[1, 2], y=[1, 2])
        backend_with_recorder._current_fig = fig
        backend_with_recorder._handle_theme_toggle({}, "event", "label")
        assert "toolbar:set-value" in backend_with_recorder._app.events


class TestQueryHandlers:
    """Tests for the Pandas query toolbar handlers."""

    @pytest.fixture
    def loaded_backend(self, backend_with_recorder):
        """A backend with a source DataFrame loaded for queries."""
        backend_with_recorder._original_df = pd.DataFrame(
            {"close": [1, 2, 3], "volume": [10, 20, 30]}
        )
        return backend_with_recorder

    def test_empty_query_does_nothing(self, loaded_backend):
        """An empty pending query short-circuits without emitting."""
        loaded_backend._pending_query = "   "
        loaded_backend._handle_query_submit({}, "event", "label")
        assert loaded_backend._app.events == []

    def test_blocked_token_emits_alert(self, loaded_backend):
        """A blocked token in the query emits an alert and aborts."""
        loaded_backend._pending_query = "import os"
        loaded_backend._handle_query_submit({}, "event", "label")
        assert "pywry:alert" in loaded_backend._app.events

    def test_valid_query_updates_grid(self, loaded_backend):
        """A valid DataFrame query updates the grid columns and data."""
        loaded_backend._pending_query = "df.query('close > 1')"
        loaded_backend._handle_query_submit({}, "event", "label")
        assert "grid:update-columns" in loaded_backend._app.events
        assert "grid:update-data" in loaded_backend._app.events

    def test_query_with_named_index_resets_index(self, loaded_backend):
        """A result carrying a named index is reset before normalization."""
        loaded_backend._original_df = loaded_backend._original_df.set_index("close")
        loaded_backend._pending_query = "df"
        loaded_backend._handle_query_submit({}, "event", "label")
        assert "grid:update-data" in loaded_backend._app.events

    def test_non_dataframe_result_emits_alert(self, loaded_backend):
        """A query that does not yield a DataFrame emits an alert."""
        loaded_backend._pending_query = "df.close.sum()"
        loaded_backend._handle_query_submit({}, "event", "label")
        assert "pywry:alert" in loaded_backend._app.events

    def test_query_error_emits_alert(self, loaded_backend):
        """A raising query expression emits an alert."""
        loaded_backend._pending_query = "df.no_such_method()"
        loaded_backend._handle_query_submit({}, "event", "label")
        assert "pywry:alert" in loaded_backend._app.events

    def test_query_input_records_value(self, loaded_backend):
        """The input handler records the pending query value."""
        loaded_backend._handle_query_input({"value": "df.head()"}, "event", "label")
        assert loaded_backend._pending_query == "df.head()"

    def test_query_reset_restores_grid(self, loaded_backend):
        """The reset handler clears the query and restores the grid."""
        loaded_backend._pending_query = "df.query('close > 2')"
        loaded_backend._handle_query_reset({}, "event", "label")
        assert loaded_backend._pending_query == ""
        assert "grid:reset-state" in loaded_backend._app.events


class TestSendMethods:
    """Tests for the figure/table/url dispatch methods."""

    def test_send_figure_strips_html_title(self, backend_with_recorder):
        """``send_figure`` strips HTML tags from the figure title and dispatches."""
        fig = go.Figure()
        fig.add_scatter(x=[1, 2], y=[1, 2])
        fig.layout.title.text = "<b>Hello</b>"
        backend_with_recorder.send_figure(fig, command_location="/equity/price")
        assert fig.layout.title.text == "Hello"
        assert ("show_plotly", backend_with_recorder._app.calls[0][1]) == (
            "show_plotly",
            backend_with_recorder._app.calls[0][1],
        )

    def test_send_figure_uses_default_title_when_missing(self, backend_with_recorder):
        """``send_figure`` falls back to the default title when none is set."""
        fig = go.Figure()
        backend_with_recorder.send_figure(fig)
        assert backend_with_recorder._app.calls[0][0] == "show_plotly"

    def test_send_table_with_query_toolbar(self, backend_with_recorder):
        """``send_table`` dispatches a dataframe with the query toolbar by default."""
        df = pd.DataFrame({"a": [1, 2], "b": [3, 4]})
        backend_with_recorder.send_table(df, title="<b>My [/b]Title")
        assert backend_with_recorder._app.calls[0][0] == "show_dataframe"

    def test_send_table_without_query_toolbar(self, backend_with_recorder):
        """``send_table`` omits the query toolbar when disabled."""
        df = pd.DataFrame({"a": [1, 2]})
        backend_with_recorder.send_table(df, include_query_toolbar=False)
        assert backend_with_recorder._app.calls[0][0] == "show_dataframe"

    def test_send_table_empty_title(self, backend_with_recorder):
        """``send_table`` accepts an empty title without sanitization."""
        df = pd.DataFrame({"a": [1, 2]})
        backend_with_recorder.send_table(df)
        assert backend_with_recorder._app.calls[0][0] == "show_dataframe"

    def test_send_url_with_dimensions(self, backend_with_recorder):
        """``send_url`` dispatches a redirect document with explicit dimensions."""
        backend_with_recorder.send_url(
            "https://example.com", title="Docs", width=100, height=200
        )
        name, kwargs = backend_with_recorder._app.calls[0]
        assert name == "show"
        assert kwargs["width"] == 100
        assert kwargs["height"] == 200

    def test_send_url_escapes_and_uses_defaults(self, backend_with_recorder):
        """``send_url`` escapes the URL and falls back to default dimensions."""
        backend_with_recorder.send_url('https://example.com/?a="b"&c=1')
        name, kwargs = backend_with_recorder._app.calls[0]
        assert name == "show"
        assert kwargs["width"] == 1400
        assert kwargs["height"] == 762
        assert "&quot;" in kwargs["content"] or "%22" in kwargs["content"]

    def test_close_delegates_to_app(self, backend_with_recorder):
        """``close`` delegates to the underlying app."""
        backend_with_recorder.close()
        assert backend_with_recorder._app.calls[0][0] == "close"
