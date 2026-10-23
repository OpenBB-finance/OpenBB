"""Display Plotly figure JSON returned by chart commands."""

from __future__ import annotations

import html
import json
import re
import tempfile
import webbrowser
from pathlib import Path
from typing import Any

from openbb_cli.session import Session

session = Session()

FIGURE_TEMPLATE = Path(__file__).parent.parent / "assets" / "figure.html"
PLOTLYJS_CDN = "https://cdn.jsdelivr.net/npm/plotly.js-dist-min@4/plotly.min.js"
_TEMPLATE_TOKEN_RE = re.compile(r"__(TITLE|PLOTLYJS|FIGURE)__")


def is_plotly_figure(data: Any) -> bool:
    """Return whether a command result is Plotly figure JSON.

    Parameters
    ----------
    data : Any
        The command result.

    Returns
    -------
    bool
        True for a dict with a ``data`` list and a ``layout`` dict.
    """
    return (
        isinstance(data, dict)
        and isinstance(data.get("data"), list)
        and isinstance(data.get("layout"), dict)
    )


def strip_theme_colors(layout: Any) -> Any:
    """Remove the server-side theme from a figure layout.

    Parameters
    ----------
    layout : Any
        A Plotly layout, or any value nested inside one.

    Returns
    -------
    Any
        A copy without the embedded ``template`` or any ``*color`` setting, so
        the displaying window's own light and dark templates style the chart.
    """
    if isinstance(layout, dict):
        return {
            key: strip_theme_colors(value)
            for key, value in layout.items()
            if key != "template" and not key.lower().endswith("color")
        }
    if isinstance(layout, list):
        return [strip_theme_colors(value) for value in layout]
    return layout


def _plotlyjs_tag() -> str:
    """Return the script tag that loads plotly.js, inlined when plotly is installed.

    Returns
    -------
    str
        An inline ``<script>`` with the local plotly.js bundle, or a CDN reference.
    """
    try:
        from plotly.offline import get_plotlyjs
    except ImportError:
        return f'<script src="{PLOTLYJS_CDN}"></script>'
    return f"<script>{get_plotlyjs()}</script>"


def render_figure_html(figure: dict, title: str) -> str:
    """Render figure JSON as a standalone HTML page.

    Parameters
    ----------
    figure : dict
        Plotly figure JSON with ``data``, ``layout``, and optional ``config``.
    title : str
        The page title.

    Returns
    -------
    str
        The HTML document.
    """
    values = {
        "TITLE": html.escape(title),
        "PLOTLYJS": _plotlyjs_tag(),
        "FIGURE": json.dumps(figure).replace("</", "<\\/"),
    }
    template = FIGURE_TEMPLATE.read_text(encoding="utf-8")
    return _TEMPLATE_TOKEN_RE.sub(lambda match: values[match.group(1)], template)


def show_figure(figure: dict, title: str = "") -> None:
    """Show figure JSON in the charting window, or in the browser without one.

    Parameters
    ----------
    figure : dict
        Plotly figure JSON with ``data``, ``layout``, and optional ``config``.
    title : str
        The command location shown with the chart.
    """
    backend = session.backend
    if backend is not None:
        try:
            from plotly.graph_objects import Figure

            backend.send_figure(
                Figure(
                    data=figure["data"], layout=strip_theme_colors(figure["layout"])
                ),
                command_location=title,
            )
            return
        except Exception as e:
            session.console.print(
                f"[yellow]Chart window not available, opening in browser: {e}[/yellow]"
            )

    with tempfile.NamedTemporaryFile(
        mode="w", delete=False, suffix=".html", encoding="utf-8"
    ) as f:
        f.write(render_figure_html(figure, title))
        path = Path(f.name)

    webbrowser.open(path.as_uri())
    session.console.print(f"[green]Opened chart in browser: {path}[/green]")
