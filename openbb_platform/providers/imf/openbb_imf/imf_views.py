"""Charting extension dispatchers for the IMF router."""

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from openbb_charting.core.openbb_figure import OpenBBFigure


def _dump(obbject_item: Any) -> list[dict[str, Any]]:
    """Convert a list of Data models to plain dicts."""
    rows: list[dict[str, Any]] = []
    for item in obbject_item or []:
        if hasattr(item, "model_dump"):
            rows.append(item.model_dump(mode="json", exclude_none=False))
        elif isinstance(item, dict):
            rows.append(item)
    return rows


def _coerce_params(obj: Any) -> dict[str, Any]:
    """Convert a QueryParams model (or dict) to a plain dict."""
    if obj is None:
        return {}
    if hasattr(obj, "model_dump"):
        return obj.model_dump()
    if isinstance(obj, dict):
        return obj
    return {}


def _params(kwargs: dict[str, Any]) -> dict[str, Any]:
    """Merge ``standard_params``, ``extra_params``, and top-level kwargs into one dict."""
    merged: dict[str, Any] = {}
    merged.update(_coerce_params(kwargs.get("standard_params")))
    merged.update(_coerce_params(kwargs.get("extra_params")))
    for k, v in kwargs.items():
        if k in (
            "standard_params",
            "extra_params",
            "obbject_item",
            "charting_settings",
            "provider",
            "extra",
        ):
            continue
        merged.setdefault(k, v)
    return merged


def _standard_params(kwargs: dict[str, Any]) -> dict[str, Any]:
    """Backwards-compat shim: return the merged standard+extra param dict."""
    return _params(kwargs)


def _theme(kwargs: dict[str, Any]) -> str:
    """Resolve the chart theme, defaulting to 'dark'."""
    return _params(kwargs).get("theme") or "dark"


def _content(fig: "OpenBBFigure") -> dict[str, Any]:
    """Return the Workspace-ready Plotly content dict."""
    content = fig.show(external=True).to_plotly_json()
    content["config"] = {"displayModeBar": False}
    return content


class ImfViews:
    """Charting dispatchers for ``obb.imf.*`` routes."""

    @staticmethod
    def imf_portwatch_country_activity(
        **kwargs,
    ) -> tuple["OpenBBFigure", dict[str, Any]]:
        """Render the daily country-activity stacked-area chart."""
        from openbb_imf.utils.port_watch_helpers import map_port_country_code
        from openbb_imf.views.port_watch_charts import plot_country_activity

        sp = _standard_params(kwargs)
        country_code = sp.get("country_code") or "USA"
        metric = sp.get("metric") or "portcalls"
        try:
            title = map_port_country_code(country_code)
        except ValueError:
            title = country_code

        fig = plot_country_activity(
            _dump(kwargs.get("obbject_item")), title, metric, theme=_theme(kwargs)
        )
        return fig, _content(fig)

    @staticmethod
    def imf_portwatch_monthly_trade(
        **kwargs,
    ) -> tuple["OpenBBFigure", dict[str, Any]]:
        """Render the monthly TradeNow chart."""
        from openbb_imf.utils.port_watch_helpers import map_port_country_code
        from openbb_imf.views.port_watch_charts import plot_monthly_trade

        sp = _standard_params(kwargs)
        code = sp.get("code") or "USA"
        metric = sp.get("metric") or "trade_value"
        try:
            region_name = map_port_country_code(code)
        except ValueError:
            region_name = code

        fig = plot_monthly_trade(
            _dump(kwargs.get("obbject_item")), region_name, metric, theme=_theme(kwargs)
        )
        return fig, _content(fig)

    @staticmethod
    def imf_portwatch_container_metrics(
        **kwargs,
    ) -> tuple["OpenBBFigure", dict[str, Any]]:
        """Render the container-metrics multi-series chart."""
        import asyncio

        from openbb_imf.utils.port_watch_helpers import get_container_port_name_map
        from openbb_imf.views.port_watch_charts import plot_container_metrics

        sp = _standard_params(kwargs)
        metric_label = {
            "portcalls": "Container Port Calls",
            "import_container": "Container Imports",
            "export_container": "Container Exports",
            "incoming_cargo_container": "Incoming Container Cargo",
            "outgoing_cargo_container": "Outgoing Container Cargo",
        }.get(sp.get("metric") or "portcalls", "Container Port Calls")

        port_name_map = asyncio.run(get_container_port_name_map())

        fig = plot_container_metrics(
            _dump(kwargs.get("obbject_item")),
            metric_label,
            theme=_theme(kwargs),
            port_name_map=port_name_map,
        )
        return fig, _content(fig)

    @staticmethod
    def imf_portwatch_disruptions_map(
        **kwargs,
    ) -> tuple["OpenBBFigure", dict[str, Any]]:
        """Render the disruption Scattergeo map."""
        from openbb_imf.views.port_watch_charts import plot_disruptions_map

        fig = plot_disruptions_map(
            _dump(kwargs.get("obbject_item")), theme=_theme(kwargs)
        )
        return fig, _content(fig)

    @staticmethod
    def imf_portwatch_disruption_sankey(
        **kwargs,
    ) -> tuple["OpenBBFigure", dict[str, Any]]:
        """Render the disruption capacity-spillover Sankey."""
        from openbb_imf.views.port_watch_charts import plot_disruption_sankey

        sp = _standard_params(kwargs)
        event_label = sp.get("event_id") or "Event"
        if event_label.upper() == "LATEST":
            event_label = "Latest Disruption"
        else:
            event_label = f"Event {event_label}"

        fig = plot_disruption_sankey(
            _dump(kwargs.get("obbject_item")), event_label, theme=_theme(kwargs)
        )
        return fig, _content(fig)
