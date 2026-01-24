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
            Event name (e.g., 'plotly:click', 'toggle', 'grid:cell-click').
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
        >>> widget.on("plotly:click", lambda d, t, l: print(f"Clicked: {d}"))
        >>> widget.on("custom-event", my_handler).on("another", other_handler)
        """
        ...  # pylint: disable=unnecessary-ellipsis

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


# pylint: disable=too-many-public-methods
# NativeWindowHandle implements BaseWidget protocol and provides comprehensive
# window control methods. The large number of methods is intentional for full API coverage.
class NativeWindowHandle:
    """Handle for a native window that implements BaseWidget protocol.

    Wraps the window resources and provides the same API as notebook widgets,
    enabling uniform code that works in both native and notebook environments.

    Parameters
    ----------
    label : str
        The window label identifier.
    app : Any
        Reference to the PyWry app instance for emit/send operations.

    Attributes
    ----------
    label : str
        The window label identifier.
    resources : WindowResources
        The window's resources object (content, config, watched files, etc.).

    Examples
    --------
    >>> handle = app.show("<h1>Hello</h1>", title="Test")
    >>> handle.emit("update", {"value": 42})  # Works just like widget.emit()
    >>> handle.on("click", my_handler)  # Register callbacks
    >>> handle.close()  # Close the window
    >>> print(handle.resources.created_at)  # Access window metadata
    """

    def __init__(self, label: str, app: Any) -> None:
        """Initialize the native window handle."""
        self._label = label
        self._app = app

    @property
    def label(self) -> str:
        """Get the window label."""
        return self._label

    @property
    def resources(self) -> Any:
        """Get the window's resources object.

        Returns
        -------
        WindowResources
            The window's tracked resources including content, config,
            creation time, watched files for hot reload, etc.
            Returns None if window has been destroyed.
        """
        from .window_manager import get_lifecycle

        lifecycle = get_lifecycle()
        return lifecycle.get(self._label)

    @property
    def window(self) -> Any:
        """Get the underlying pytauri Window object.

        The actual `pytauri.Window` objects live in that subprocess
        and cannot be directly accessed from the main Python process.

        To interact with the window, use the methods on this handle:
        - `emit()` - Send events to JavaScript
        - `update()` - Update HTML content
        - `close()` / `hide()` / `show_window()` - Control visibility
        - `eval_js()` - Execute JavaScript in the window

        For advanced use cases requiring direct pytauri access, you can:
        1. Use `pywry.runtime` module for low-level IPC commands
        2. Run pywry's `__main__.py` directly in your process

        Returns
        -------
        None
            Always returns None in subprocess mode.

        Raises
        ------
        NotImplementedError
            To remind that direct window access is not available.
        """
        raise NotImplementedError(
            f"Direct pytauri Window access is not available in subprocess mode. "
            f"Use handle methods like emit(), update(), eval_js() instead. "
            f"Window label: {self._label}"
        )

    @property
    def proxy(self) -> Any:
        """Get a WindowProxy for full WebviewWindow API access.

        The WindowProxy provides access to all WebviewWindow methods including:
        - Window state: `is_maximized`, `is_minimized`, `is_fullscreen`, etc.
        - Window actions: `maximize()`, `minimize()`, `center()`, etc.
        - Window properties: `set_title()`, `set_size()`, `set_position()`, etc.
        - Appearance: `set_background_color()`, `set_theme()`, `set_decorations()`, etc.
        - Webview ops: `navigate()`, `reload()`, `open_devtools()`, `set_zoom()`, etc.

        Returns
        -------
        WindowProxy
            A proxy object for full window control.

        Examples
        --------
        >>> handle = app.show("<h1>Hello</h1>")
        >>> # Access window properties
        >>> print(handle.proxy.is_maximized)
        >>> print(handle.proxy.title)
        >>> # Control window
        >>> handle.proxy.maximize()
        >>> handle.proxy.set_background_color((30, 30, 30, 255))
        >>> handle.proxy.set_always_on_top(True)
        >>> # Webview operations
        >>> handle.proxy.open_devtools()
        >>> handle.proxy.set_zoom(1.5)
        """
        from .window_proxy import WindowProxy

        return WindowProxy(self._label)

    def eval_js(self, script: str) -> None:
        """Execute JavaScript in the window.

        Parameters
        ----------
        script : str
            JavaScript code to execute.

        Examples
        --------
        >>> handle.eval_js("console.log('Hello from Python!')")
        >>> handle.eval_js("document.body.style.background = 'red'")
        """
        from . import runtime

        runtime.eval_js(self._label, script)

    def on(
        self, event_type: str, callback: Callable[[dict[str, Any], str, str], Any]
    ) -> NativeWindowHandle:
        """Register a callback for events from JavaScript.

        Parameters
        ----------
        event_type : str
            Event name to listen for.
        callback : Callable
            Handler function receiving (data, event_type, label).

        Returns
        -------
        NativeWindowHandle
            Self for method chaining.
        """
        from .callbacks import get_registry

        registry = get_registry()
        registry.register(self._label, event_type, callback)
        return self

    def emit(self, event_type: str, data: dict[str, Any]) -> None:
        """Send an event from Python to JavaScript.

        Parameters
        ----------
        event_type : str
            Event name that JS listeners can subscribe to.
        data : dict
            JSON-serializable payload to send to JavaScript.
        """
        self._app.emit(event_type, data, self._label)

    def update(self, html: str) -> None:
        """Update the window's HTML content.

        Parameters
        ----------
        html : str
            New HTML content to render.
        """
        from .window_manager import get_lifecycle

        lifecycle = get_lifecycle()
        lifecycle.set_content(self._label, html)

    def display(self) -> None:
        """Show the window (no-op for already-visible native windows)."""
        # Native windows are shown immediately on creation

    def close(self) -> None:
        """Close and destroy the native window."""
        from . import runtime

        runtime.close_window(self._label)

    def hide(self) -> None:
        """Hide the window without destroying it."""
        from . import runtime

        runtime.hide_window(self._label)

    def show_window(self) -> None:
        """Show a previously hidden window."""
        from . import runtime

        runtime.show_window(self._label)

    # ─────────────────────────────────────────────────────────────────────────
    # Convenience methods delegating to WindowProxy
    # ─────────────────────────────────────────────────────────────────────────

    def maximize(self) -> None:
        """Maximize the window."""
        self.proxy.maximize()

    def minimize(self) -> None:
        """Minimize the window."""
        self.proxy.minimize()

    def center(self) -> None:
        """Center the window on screen."""
        self.proxy.center()

    def set_title(self, title: str) -> None:
        """Set the window title.

        Parameters
        ----------
        title : str
            New window title.
        """
        self.proxy.set_title(title)

    def set_size(self, width: int, height: int) -> None:
        """Set the window size.

        Parameters
        ----------
        width : int
            Window width in logical pixels.
        height : int
            Window height in logical pixels.
        """
        from .types import LogicalSize

        self.proxy.set_size(LogicalSize(width, height))

    def set_min_size(self, width: int | None, height: int | None) -> None:
        """Set minimum window size.

        Parameters
        ----------
        width : int or None
            Minimum width, or None to remove constraint.
        height : int or None
            Minimum height, or None to remove constraint.
        """
        if width is None or height is None:
            self.proxy.set_min_size(None)
        else:
            from .types import LogicalSize

            self.proxy.set_min_size(LogicalSize(width, height))

    def set_max_size(self, width: int | None, height: int | None) -> None:
        """Set maximum window size.

        Parameters
        ----------
        width : int or None
            Maximum width, or None to remove constraint.
        height : int or None
            Maximum height, or None to remove constraint.
        """
        if width is None or height is None:
            self.proxy.set_max_size(None)
        else:
            from .types import LogicalSize

            self.proxy.set_max_size(LogicalSize(width, height))

    def set_always_on_top(self, always_on_top: bool) -> None:
        """Set whether the window stays on top of other windows.

        Parameters
        ----------
        always_on_top : bool
            If True, window stays above other windows.
        """
        self.proxy.set_always_on_top(always_on_top)

    def set_decorations(self, decorations: bool) -> None:
        """Set whether the window has decorations (title bar, borders).

        Parameters
        ----------
        decorations : bool
            If True, show window decorations.
        """
        self.proxy.set_decorations(decorations)

    def set_background_color(self, r: int, g: int, b: int, a: int = 255) -> None:
        """Set the window background color.

        This sets both the native window background and injects CSS to override
        the --pywry-bg-primary variable so the content background also changes.

        Parameters
        ----------
        r : int
            Red component (0-255).
        g : int
            Green component (0-255).
        b : int
            Blue component (0-255).
        a : int, optional
            Alpha component (0-255). Default is 255.
        """
        # Set native window background
        self.proxy.set_background_color((r, g, b, a))

        # Also inject CSS to override the content background via CSS variable
        alpha = a / 255.0
        color = f"rgb({r}, {g}, {b})" if alpha >= 1.0 else f"rgba({r}, {g}, {b}, {alpha:.3f})"

        css = f":root {{ --pywry-bg-primary: {color} !important; }}"
        self.emit("pywry:inject-css", {"id": "pywry-bg-override", "css": css})

    def open_devtools(self) -> None:
        """Open the browser developer tools for this window."""
        self.proxy.open_devtools()

    def close_devtools(self) -> None:
        """Close the browser developer tools."""
        self.proxy.close_devtools()

    def set_zoom(self, scale: float) -> None:
        """Set the webview zoom level.

        Parameters
        ----------
        scale : float
            Zoom scale (1.0 = 100%, 1.5 = 150%, etc).
        """
        self.proxy.set_zoom(scale)

    def refresh(self) -> bool:
        """Trigger a full page refresh for the window.

        Preserves scroll position using sessionStorage.

        Returns
        -------
        bool
            True if refresh succeeded.
        """
        from . import runtime

        return runtime.refresh_window(self._label)

    def inject_css(self, css: str, asset_id: str | None = None) -> bool:
        """Inject or update CSS in the window without page reload.

        Parameters
        ----------
        css : str
            CSS content to inject.
        asset_id : str, optional
            ID for the style element. If None, generates a unique ID.
            Use the same ID to update existing styles.

        Returns
        -------
        bool
            True if injection succeeded.

        Examples
        --------
        >>> handle.inject_css("body { background: red; }", "my-theme")
        >>> handle.inject_css("body { background: blue; }", "my-theme")  # Updates
        """
        import uuid

        from . import runtime

        if asset_id is None:
            asset_id = f"pywry-css-{uuid.uuid4().hex[:8]}"
        return runtime.inject_css(self._label, css, asset_id)

    def remove_css(self, asset_id: str) -> bool:
        """Remove a CSS style element from the window.

        Parameters
        ----------
        asset_id : str
            ID of the style element to remove.

        Returns
        -------
        bool
            True if removal succeeded.
        """
        from . import runtime

        return runtime.remove_css(self._label, asset_id)

    def set_content(self, html: str, theme: str = "dark") -> bool:
        """Set the window's HTML content with theme.

        Parameters
        ----------
        html : str
            New HTML content to render.
        theme : str, optional
            Theme mode ('dark' or 'light'). Default is 'dark'.

        Returns
        -------
        bool
            True if content was set successfully.
        """
        from .window_manager import get_lifecycle

        lifecycle = get_lifecycle()
        return lifecycle.set_content(self._label, html, theme)

    def get_data(self, key: str, default: Any = None) -> Any:
        """Get custom data stored on this window.

        Parameters
        ----------
        key : str
            Data key.
        default : Any, optional
            Default value if key not found.

        Returns
        -------
        Any
            The stored value or default.

        Examples
        --------
        >>> handle.set_data("state", {"count": 0})
        >>> handle.get_data("state")
        {'count': 0}
        """
        from .window_manager import get_lifecycle

        lifecycle = get_lifecycle()
        return lifecycle.get_data(self._label, key, default)

    def set_data(self, key: str, value: Any) -> bool:
        """Store custom data on this window.

        Parameters
        ----------
        key : str
            Data key.
        value : Any
            Value to store.

        Returns
        -------
        bool
            True if data was stored.

        Examples
        --------
        >>> handle.set_data("state", {"count": 0})
        >>> handle.set_data("callbacks", [my_func])
        """
        from .window_manager import get_lifecycle

        lifecycle = get_lifecycle()
        return lifecycle.set_data(self._label, key, value)

    @property
    def title(self) -> str | None:
        """Get the window title.

        Returns
        -------
        str or None
            The window title, or None if window not found.
        """
        resources = self.resources
        if resources and resources.last_config:
            return str(resources.last_config.title)
        return None

    @property
    def config(self) -> Any:
        """Get the window's configuration.

        Returns
        -------
        WindowConfig or None
            The window configuration, or None if not found.
        """
        resources = self.resources
        return resources.last_config if resources else None

    @property
    def html_content(self) -> str | None:
        """Get the current HTML content.

        Returns
        -------
        str or None
            The current HTML content, or None if not found.
        """
        resources = self.resources
        return resources.html_content if resources else None

    @property
    def created_at(self) -> Any:
        """Get the window creation timestamp.

        Returns
        -------
        datetime or None
            When the window was created.
        """
        resources = self.resources
        return resources.created_at if resources else None

    @property
    def is_alive(self) -> bool:
        """Check if the window is still open and not destroyed.

        Returns
        -------
        bool
            True if window exists and is not destroyed.
        """
        resources = self.resources
        return resources is not None and not resources.is_destroyed

    def __str__(self) -> str:
        """Return the window label."""
        return self._label

    def __repr__(self) -> str:
        """Return a detailed representation."""
        return f"NativeWindowHandle(label={self._label!r}, alive={self.is_alive})"


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
    return isinstance(obj, (BaseWidget, NativeWindowHandle))
