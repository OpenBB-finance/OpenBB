"""Tests for the IMF charting-extension dispatchers."""

# ruff: noqa: I001

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from openbb_imf.imf_views import (
    ImfViews,
    _content,
    _dump,
    _standard_params,
    _theme,
)


class _Dumpable:
    """Tiny stand-in for a Pydantic Data model used by ``_dump``."""

    def __init__(self, payload):
        """Store ``payload`` and expose it through ``model_dump``."""
        self._payload = payload

    def model_dump(self, **_):
        """Return the stored payload as a plain dict."""
        return self._payload


class TestPrivateHelpers:
    """Tests for the small private helpers in ``imf_views``."""

    def test_dump_handles_model_objects(self):
        """``_dump`` calls ``model_dump`` on Pydantic-like objects."""
        items = [_Dumpable({"a": 1}), _Dumpable({"a": 2})]
        assert _dump(items) == [{"a": 1}, {"a": 2}]

    def test_dump_handles_dicts(self):
        """``_dump`` passes through plain dicts."""
        assert _dump([{"a": 1}]) == [{"a": 1}]

    def test_dump_skips_unknown_types(self):
        """Items that are neither models nor dicts are ignored."""
        assert _dump([_Dumpable({"a": 1}), 7, "not-a-dict"]) == [{"a": 1}]

    def test_dump_handles_none(self):
        """``None`` collapses to an empty list."""
        assert _dump(None) == []

    def test_standard_params_from_model(self):
        """``_standard_params`` returns the dict form of a model."""
        sp = SimpleNamespace(model_dump=lambda: {"country_code": "USA"})
        assert _standard_params({"standard_params": sp}) == {"country_code": "USA"}

    def test_standard_params_from_dict(self):
        """A dict ``standard_params`` is returned as-is."""
        assert _standard_params({"standard_params": {"k": 1}}) == {"k": 1}

    def test_standard_params_missing(self):
        """Missing ``standard_params`` yields ``{}``."""
        assert _standard_params({}) == {}

    def test_standard_params_unknown_type(self):
        """An unsupported ``standard_params`` type collapses to ``{}``."""
        assert _standard_params({"standard_params": 7}) == {}

    def test_theme_from_standard_params(self):
        """``theme`` from inside ``standard_params`` wins."""
        sp = SimpleNamespace(model_dump=lambda: {"theme": "light"})
        assert _theme({"standard_params": sp}) == "light"

    def test_theme_from_top_level_kwargs(self):
        """A top-level ``theme`` kwarg is honoured when not on standard_params."""
        assert _theme({"theme": "light"}) == "light"

    def test_theme_defaults_to_dark(self):
        """When no theme is supplied, the dispatcher falls back to ``dark``."""
        assert _theme({}) == "dark"

    def test_content_wraps_show_to_plotly_json(self):
        """``_content`` flattens the figure and attaches the config block."""
        fig = MagicMock()
        fig.show.return_value.to_plotly_json.return_value = {"data": [], "layout": {}}
        content = _content(fig)
        assert content["config"] == {"displayModeBar": False}
        assert "data" in content
        fig.show.assert_called_once_with(external=True)


class TestCountryActivityDispatcher:
    """Tests for ``ImfViews.imf_portwatch_country_activity``."""

    def _kwargs(self, **overrides):
        """Build a kwargs dict carrying a fake obbject + standard params."""
        sp = SimpleNamespace(
            model_dump=lambda: {
                "country_code": overrides.get("country_code", "USA"),
                "metric": overrides.get("metric", "portcalls"),
                "theme": overrides.get("theme", "dark"),
            }
        )
        return {
            "obbject_item": [_Dumpable({"date": "2024-01-01", "portcalls": 5})],
            "standard_params": sp,
        }

    @patch("openbb_imf.utils.port_watch_helpers.map_port_country_code")
    @patch("openbb_imf.views.port_watch_charts.plot_country_activity")
    def test_dispatch_passes_title_and_metric(self, mock_plot, mock_map):
        """The dispatcher resolves the country name and forwards the metric."""
        mock_map.return_value = "United States"
        mock_plot.return_value = MagicMock(
            show=lambda external: SimpleNamespace(
                to_plotly_json=lambda: {"data": [], "layout": {}}
            )
        )

        fig, content = ImfViews.imf_portwatch_country_activity(**self._kwargs())

        mock_map.assert_called_once_with("USA")
        args, kwargs = mock_plot.call_args
        assert args[1] == "United States"
        assert args[2] == "portcalls"
        assert kwargs == {"theme": "dark"}
        assert content["config"] == {"displayModeBar": False}
        assert fig is mock_plot.return_value

    @patch("openbb_imf.utils.port_watch_helpers.map_port_country_code")
    @patch("openbb_imf.views.port_watch_charts.plot_country_activity")
    def test_dispatch_falls_back_to_code_when_unknown(self, mock_plot, mock_map):
        """A ``ValueError`` from the name lookup keeps the raw code as the title."""
        mock_map.side_effect = ValueError("unknown")
        mock_plot.return_value = MagicMock(
            show=lambda external: SimpleNamespace(to_plotly_json=lambda: {})
        )

        ImfViews.imf_portwatch_country_activity(**self._kwargs(country_code="ZZZ"))
        args, _ = mock_plot.call_args
        assert args[1] == "ZZZ"

    @patch("openbb_imf.utils.port_watch_helpers.map_port_country_code")
    @patch("openbb_imf.views.port_watch_charts.plot_country_activity")
    def test_dispatch_uses_defaults_when_params_missing(self, mock_plot, mock_map):
        """Missing standard params default to ``USA`` / ``portcalls`` / ``dark``."""
        mock_map.return_value = "United States"
        mock_plot.return_value = MagicMock(
            show=lambda external: SimpleNamespace(to_plotly_json=lambda: {})
        )

        ImfViews.imf_portwatch_country_activity(obbject_item=[])
        mock_map.assert_called_once_with("USA")
        args, kwargs = mock_plot.call_args
        assert args[2] == "portcalls"
        assert kwargs == {"theme": "dark"}


class TestMonthlyTradeDispatcher:
    """Tests for ``ImfViews.imf_portwatch_monthly_trade``."""

    @patch("openbb_imf.utils.port_watch_helpers.map_port_country_code")
    @patch("openbb_imf.views.port_watch_charts.plot_monthly_trade")
    def test_dispatch_with_country_code(self, mock_plot, mock_map):
        """A country code resolves through ``map_port_country_code``."""
        mock_map.return_value = "United States"
        mock_plot.return_value = MagicMock(
            show=lambda external: SimpleNamespace(to_plotly_json=lambda: {})
        )
        sp = SimpleNamespace(
            model_dump=lambda: {"code": "USA", "metric": "trade_value"}
        )

        ImfViews.imf_portwatch_monthly_trade(obbject_item=[], standard_params=sp)
        args, kwargs = mock_plot.call_args
        assert args[1] == "United States"
        assert args[2] == "trade_value"
        assert kwargs == {"theme": "dark"}

    @patch("openbb_imf.utils.port_watch_helpers.map_port_country_code")
    @patch("openbb_imf.views.port_watch_charts.plot_monthly_trade")
    def test_dispatch_falls_back_to_raw_code(self, mock_plot, mock_map):
        """When the lookup fails, the raw region code becomes the chart label."""
        mock_map.side_effect = ValueError
        mock_plot.return_value = MagicMock(
            show=lambda external: SimpleNamespace(to_plotly_json=lambda: {})
        )
        sp = SimpleNamespace(model_dump=lambda: {"code": "X"})
        ImfViews.imf_portwatch_monthly_trade(obbject_item=[], standard_params=sp)
        args, _ = mock_plot.call_args
        assert args[1] == "X"


class TestContainerMetricsDispatcher:
    """Tests for ``ImfViews.imf_portwatch_container_metrics``."""

    @staticmethod
    def _stub_port_name_map(monkeypatch):
        """Stub ``get_container_port_name_map`` to avoid live HTTP + alru cache."""
        from openbb_imf.utils import port_watch_helpers as pwh

        async def _empty() -> dict[str, str]:
            return {"PORT1065": "Busan, Korea"}

        monkeypatch.setattr(pwh, "get_container_port_name_map", _empty)

    @patch("openbb_imf.views.port_watch_charts.plot_container_metrics")
    def test_metric_label_lookup(self, mock_plot, monkeypatch):
        """The dispatcher maps the metric key to a human-readable label."""
        self._stub_port_name_map(monkeypatch)
        mock_plot.return_value = MagicMock(
            show=lambda external: SimpleNamespace(to_plotly_json=lambda: {})
        )
        sp = SimpleNamespace(model_dump=lambda: {"metric": "export_container"})

        ImfViews.imf_portwatch_container_metrics(obbject_item=[], standard_params=sp)
        args, kwargs = mock_plot.call_args
        assert args[1] == "Container Exports"
        assert kwargs["port_name_map"] == {"PORT1065": "Busan, Korea"}

    @patch("openbb_imf.views.port_watch_charts.plot_container_metrics")
    def test_unknown_metric_falls_back(self, mock_plot, monkeypatch):
        """Unknown metrics fall back to the default 'Container Port Calls' label."""
        self._stub_port_name_map(monkeypatch)
        mock_plot.return_value = MagicMock(
            show=lambda external: SimpleNamespace(to_plotly_json=lambda: {})
        )
        sp = SimpleNamespace(model_dump=lambda: {"metric": "weird"})
        ImfViews.imf_portwatch_container_metrics(obbject_item=[], standard_params=sp)
        args, _ = mock_plot.call_args
        assert args[1] == "Container Port Calls"

    @patch("openbb_imf.views.port_watch_charts.plot_container_metrics")
    def test_missing_metric_uses_default(self, mock_plot, monkeypatch):
        """Missing metric keys collapse to the portcalls label."""
        self._stub_port_name_map(monkeypatch)
        mock_plot.return_value = MagicMock(
            show=lambda external: SimpleNamespace(to_plotly_json=lambda: {})
        )
        ImfViews.imf_portwatch_container_metrics(obbject_item=[])
        args, _ = mock_plot.call_args
        assert args[1] == "Container Port Calls"

    @patch("openbb_imf.views.port_watch_charts.plot_container_metrics")
    def test_theme_from_extra_params(self, mock_plot, monkeypatch):
        """``theme`` resolved from ``extra_params`` (model-specific) is honored."""
        self._stub_port_name_map(monkeypatch)
        mock_plot.return_value = MagicMock(
            show=lambda external: SimpleNamespace(to_plotly_json=lambda: {})
        )
        sp = SimpleNamespace(model_dump=lambda: {})
        ep = SimpleNamespace(
            model_dump=lambda: {"theme": "light", "metric": "portcalls"}
        )
        ImfViews.imf_portwatch_container_metrics(
            obbject_item=[], standard_params=sp, extra_params=ep
        )
        _, kwargs = mock_plot.call_args
        assert kwargs["theme"] == "light"


class TestDisruptionsMapDispatcher:
    """Tests for ``ImfViews.imf_portwatch_disruptions_map``."""

    @patch("openbb_imf.views.port_watch_charts.plot_disruptions_map")
    def test_dispatch_passes_rows_and_theme(self, mock_plot):
        """Rows are dumped and the theme is forwarded."""
        mock_plot.return_value = MagicMock(
            show=lambda external: SimpleNamespace(to_plotly_json=lambda: {})
        )
        sp = SimpleNamespace(model_dump=lambda: {"theme": "light"})
        ImfViews.imf_portwatch_disruptions_map(
            obbject_item=[_Dumpable({"lat": 1.0, "long": 2.0})], standard_params=sp
        )
        args, kwargs = mock_plot.call_args
        assert args[0] == [{"lat": 1.0, "long": 2.0}]
        assert kwargs == {"theme": "light"}


class TestDisruptionSankeyDispatcher:
    """Tests for ``ImfViews.imf_portwatch_disruption_sankey``."""

    @patch("openbb_imf.views.port_watch_charts.plot_disruption_sankey")
    def test_latest_event_label(self, mock_plot):
        """``event_id='LATEST'`` becomes 'Latest Disruption' in the chart title."""
        mock_plot.return_value = MagicMock(
            show=lambda external: SimpleNamespace(to_plotly_json=lambda: {})
        )
        sp = SimpleNamespace(model_dump=lambda: {"event_id": "LATEST"})
        ImfViews.imf_portwatch_disruption_sankey(obbject_item=[], standard_params=sp)
        args, _ = mock_plot.call_args
        assert args[1] == "Latest Disruption"

    @patch("openbb_imf.views.port_watch_charts.plot_disruption_sankey")
    def test_numeric_event_label(self, mock_plot):
        """A numeric event id is wrapped in ``'Event {id}'``."""
        mock_plot.return_value = MagicMock(
            show=lambda external: SimpleNamespace(to_plotly_json=lambda: {})
        )
        sp = SimpleNamespace(model_dump=lambda: {"event_id": "1234"})
        ImfViews.imf_portwatch_disruption_sankey(obbject_item=[], standard_params=sp)
        args, _ = mock_plot.call_args
        assert args[1] == "Event 1234"

    @patch("openbb_imf.views.port_watch_charts.plot_disruption_sankey")
    def test_default_event_label(self, mock_plot):
        """A missing ``event_id`` defaults to the plain ``'Event'`` label."""
        mock_plot.return_value = MagicMock(
            show=lambda external: SimpleNamespace(to_plotly_json=lambda: {})
        )
        ImfViews.imf_portwatch_disruption_sankey(obbject_item=[])
        args, _ = mock_plot.call_args
        assert args[1] == "Event Event"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
