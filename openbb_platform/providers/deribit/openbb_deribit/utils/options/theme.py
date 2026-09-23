"""Shared Plotly theming for the Deribit options charts."""

from typing import Any

CHART_CONFIG = {"scrollZoom": True, "displayModeBar": False, "responsive": True}


class Unplotted:
    """Accept every drawing call and draw nothing."""

    def __getattr__(self, name: str):
        """Return a call that does nothing and keeps the chain going."""

        def drawn(*args, **kwargs):
            return self

        return drawn


def supported_layout(layout: dict) -> dict:
    """Drop the layout keys the installed Plotly no longer accepts.

    Parameters
    ----------
    layout : dict
        The template layout to filter.

    Returns
    -------
    dict
        Only the keys the installed Plotly's ``Layout`` accepts.
    """
    from plotly.graph_objects import Layout

    valid = getattr(Layout, "_valid_props", None)

    if not valid:
        return layout

    return {key: value for key, value in layout.items() if key in valid}


def new_figure(theme: str) -> "tuple[Any, str, str]":
    """Create a themed figure with its text and background colors.

    Parameters
    ----------
    theme : str
        Either 'dark' or 'light'.

    Returns
    -------
    tuple[Any, str, str]
        The figure, the text color, and the transparent background color. The
        figure draws nothing when the charting extension is absent.
    """
    from openbb_deribit import CHARTING_INSTALLED

    text_color = "white" if theme == "dark" else "black"
    background = "rgba(0,0,0,0)" if theme == "dark" else "rgba(255,255,255,0)"

    if not CHARTING_INSTALLED:
        return Unplotted(), text_color, background

    from openbb_charting.core.chart_style import ChartStyle
    from openbb_charting.core.openbb_figure import OpenBBFigure

    figure = OpenBBFigure(create_backend=True)
    figure.update_layout(
        supported_layout(ChartStyle().plotly_template.get("layout", {}))
    )

    return figure, text_color, background


def finalize(output: Any, figure: Any, theme: str) -> Any:
    """Apply the chart style and attach the chart to the result.

    Parameters
    ----------
    output : Any
        The OBBject carrying the tabular results.
    figure : Any
        The figure to attach.
    theme : str
        Either 'dark' or 'light'.

    Returns
    -------
    Any
        The same result, with a chart attached, or unchanged when there is no
        charting extension to draw with.
    """
    from openbb_core.app.model.charts.chart import Chart

    from openbb_deribit import CHARTING_INSTALLED

    if not CHARTING_INSTALLED:
        return output

    text_color = "white" if theme == "dark" else "black"
    output.charting._charting_settings.chart_style = theme
    figure = output.charting._set_chart_style(figure)
    figure.update_layout(
        hoverlabel=dict(
            bgcolor="#0E0E0E" if theme == "dark" else "#FFFFFF",
            bordercolor=text_color,
            font=dict(color=text_color, size=12),
        )
    )
    figure = figure.show(config=CHART_CONFIG, external=True)

    for trace in figure.data:
        if getattr(trace, "hoverinfo", None) == "skip":
            trace.hovertemplate = None

    output.chart = Chart(fig=figure, content=figure.to_plotly_json(), format="plotly")

    return output
