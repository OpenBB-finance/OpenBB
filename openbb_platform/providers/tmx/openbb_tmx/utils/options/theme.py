"""Shared Plotly theming for the TMX options charts."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from openbb_charting.core.openbb_figure import OpenBBFigure

CHART_CONFIG = {"scrollZoom": True, "displayModeBar": False, "responsive": True}


def new_figure(theme: str) -> tuple[OpenBBFigure, str, str]:
    """Create a themed ``OpenBBFigure`` with its text and background colors.

    Parameters
    ----------
    theme : str
        Either 'dark' or 'light'.

    Returns
    -------
    tuple[OpenBBFigure, str, str]
        The figure, the text color, and the transparent background color.
    """
    from openbb_charting.core.chart_style import ChartStyle
    from openbb_charting.core.openbb_figure import OpenBBFigure

    fig = OpenBBFigure(create_backend=True)
    fig.update_layout(ChartStyle().plotly_template.get("layout", {}))
    text_color = "white" if theme == "dark" else "black"
    background = "rgba(0,0,0,0)" if theme == "dark" else "rgba(255,255,255,0)"

    return fig, text_color, background


def finalize(output: Any, fig: OpenBBFigure, theme: str) -> Any:
    """Apply the chart style and attach the Plotly chart to the OBBject.

    Parameters
    ----------
    output : Any
        The OBBject carrying the tabular results.
    fig : OpenBBFigure
        The figure to attach.
    theme : str
        Either 'dark' or 'light'.

    Returns
    -------
    Any
        The same OBBject, with ``chart`` populated.
    """
    from openbb_core.app.model.charts.chart import Chart

    text_color = "white" if theme == "dark" else "black"
    output.charting._charting_settings.chart_style = theme
    fig = output.charting._set_chart_style(fig)
    fig.update_layout(
        hoverlabel=dict(
            bgcolor="#0E0E0E" if theme == "dark" else "#FFFFFF",
            bordercolor=text_color,
            font=dict(color=text_color, size=12),
        )
    )
    content = fig.show(config=CHART_CONFIG, external=True).to_plotly_json()
    output.chart = Chart(fig=fig, content=content, format="plotly")

    return output
