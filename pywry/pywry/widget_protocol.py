"""Widget protocol for unified PyWry widget API.

Defines the common interface that all PyWry widget backends must implement,
enabling seamless switching between InlineWidget (FastAPI), PyWryWidget (anywidget),
and native window rendering.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable


if TYPE_CHECKING:
    from collections.abc import Callable


@runtime_checkable
class BaseWidget(Protocol):
    """Protocol that all PyWry widgets must implement.

    This enables a unified API across different rendering backends:
    - InlineWidget: FastAPI server + IFrame (notebook fallback)
    - PyWryWidget: anywidget with traitlet sync (best notebook performance)
    - Native windows: Desktop application rendering

    Examples
    --------
    >>> widget = create_widget(...)  # Returns any BaseWidget implementation
    >>> widget.on("click", lambda data, event_type, label: print(data))
    >>> widget.emit("update", {"value": 42})
    >>> widget.display()
    """

    def on(
        self, event_type: str, callback: Callable[[dict[str, Any], str, str], Any]
    ) -> BaseWidget:
        """Register a callback for events from JavaScript.

        Parameters
        ----------
        event_type : str
            Event name (e.g., 'plotly_click', 'toggle', 'cell_click').
        callback : Callable[[dict, str, str], Any]
            Handler function receiving (data, event_type, label).
            - data: Event payload from JavaScript
            - event_type: Same as event_type parameter
            - label: Widget identifier

        Returns
        -------
        BaseWidget
            Self for method chaining.

        Examples
        --------
        >>> widget.on("plotly_click", lambda d, t, l: print(f"Clicked: {d}"))
        >>> widget.on("custom_event", my_handler).on("another", other_handler)
        """

    def emit(self, event_type: str, data: dict[str, Any]) -> None:
        """Send an event from Python to JavaScript.

        Parameters
        ----------
        event_type : str
            Event name that JS listeners can subscribe to.
        data : dict
            JSON-serializable payload to send to JavaScript.

        Examples
        --------
        >>> widget.emit("update_chart", {"x": [1, 2, 3], "y": [4, 5, 6]})
        >>> widget.emit("set_theme", {"theme": "dark"})
        """

    def update(self, html: str) -> None:
        """Update the widget's HTML content.

        Parameters
        ----------
        html : str
            New HTML content to render. Should include necessary <script> tags.

        Examples
        --------
        >>> new_html = generate_plotly_html(fig.to_json(), widget_id, "dark")
        >>> widget.update(new_html)
        """

    def display(self) -> None:
        """Display the widget in the current output context.

        For Jupyter notebooks, this calls IPython.display.display().
        For native windows, this may be a no-op or show the window.
        """


def is_base_widget(obj: Any) -> bool:
    """Check if an object implements the BaseWidget protocol.

    Parameters
    ----------
    obj : Any
        Object to check.

    Returns
    -------
    bool
        True if obj implements all required BaseWidget methods.

    Examples
    --------
    >>> widget = InlineWidget(...)
    >>> assert is_base_widget(widget)
    """
    return isinstance(obj, BaseWidget)
