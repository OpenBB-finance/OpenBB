"""Window commands for PyTauri IPC.

This module provides functions for handling window-related commands
from the Tauri frontend.
"""

from __future__ import annotations

from typing import Any

# Import handlers from the package __init__.py using relative import
from . import (
    dispatch_command,
    handle_aggrid_event,
    handle_open_file,
    handle_open_url,
    handle_plotly_event,
    handle_pywry_event,
    handle_pywry_result,
    handle_window_close,
)


__all__ = [
    "dispatch_command",
    "handle_aggrid_event",
    "handle_open_file",
    "handle_open_url",
    "handle_plotly_event",
    "handle_pywry_event",
    "handle_pywry_result",
    "handle_window_close",
    "on_aggrid_event",
    "on_open_file",
    "on_open_url",
    "on_plotly_event",
    "on_pywry_event",
    "on_pywry_result",
    "on_window_close",
]


def on_window_close(label: str) -> dict[str, Any]:
    """Handle window close event.

    Parameters
    ----------
    label : str
        The window label.

    Returns
    -------
    dict of str to Any
        Response dict.
    """
    return handle_window_close(label)


def on_pywry_result(label: str, data: dict[str, Any]) -> dict[str, Any]:
    """Handle a result from JavaScript.

    Parameters
    ----------
    label : str
        The window label.
    data : dict of str to Any
        The result data.

    Returns
    -------
    dict of str to Any
        Response dict.
    """
    return handle_pywry_result(label, data)


def on_pywry_event(label: str, event_data: dict[str, Any]) -> dict[str, Any]:
    """Handle a generic event from JavaScript.

    Parameters
    ----------
    label : str
        The window label.
    event_data : dict of str to Any
        The event data.

    Returns
    -------
    dict of str to Any
        Response dict.
    """
    return handle_pywry_event(label, event_data)


def on_plotly_event(label: str, event_data: dict[str, Any]) -> dict[str, Any]:
    """Handle a Plotly event.

    Parameters
    ----------
    label : str
        The window label.
    event_data : dict of str to Any
        The Plotly event data.

    Returns
    -------
    dict of str to Any
        Response dict.
    """
    return handle_plotly_event(label, event_data)


def on_aggrid_event(label: str, event_data: dict[str, Any]) -> dict[str, Any]:
    """Handle an AG Grid event.

    Parameters
    ----------
    label : str
        The window label.
    event_data : dict of str to Any
        The AG Grid event data.

    Returns
    -------
    dict of str to Any
        Response dict.
    """
    return handle_aggrid_event(label, event_data)


def on_open_file(path: str) -> dict[str, Any]:
    """Open a file with system default application.

    Parameters
    ----------
    path : str
        The file path.

    Returns
    -------
    dict of str to Any
        Response dict.
    """
    return handle_open_file(path)


def on_open_url(url: str) -> dict[str, Any]:
    """Open a URL in system browser.

    Parameters
    ----------
    url : str
        The URL to open.

    Returns
    -------
    dict of str to Any
        Response dict.
    """
    return handle_open_url(url)
