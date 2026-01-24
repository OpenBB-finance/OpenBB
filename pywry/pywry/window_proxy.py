"""WindowProxy - Full WebviewWindow API for PyWry.

Provides a Python interface to control native windows via IPC,
mirroring the complete pytauri.webview.WebviewWindow API.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from . import runtime


if TYPE_CHECKING:
    from .types import (
        Color,
        Cookie,
        CursorIcon,
        Effects,
        Monitor,
        PhysicalPosition,
        PhysicalSize,
        PositionType,
        ProgressBarState,
        SizeType,
        Theme,
        TitleBarStyle,
        UserAttentionType,
    )


# pylint: disable=too-many-public-methods
# WindowProxy mirrors the complete pytauri.webview.WebviewWindow API.
# The large number of methods is intentional to provide full API coverage.
class WindowProxy:
    """Proxy for pytauri.webview.WebviewWindow with full API access.

    Provides transparent IPC to the subprocess, exposing all WebviewWindow
    methods as either blocking (for property getters) or fire-and-forget
    (for actions and setters).

    Parameters
    ----------
    label : str
        The window label to control.

    Examples
    --------
    >>> proxy = WindowProxy("main")
    >>> proxy.set_title("My App")
    >>> proxy.maximize()
    >>> print(proxy.is_maximized)  # True
    >>> proxy.set_background_color((30, 30, 30, 255))
    """

    def __init__(self, label: str) -> None:
        """Initialize the window proxy.

        Parameters
        ----------
        label : str
            The window label to control.
        """
        self._label = label

    # ─────────────────────────────────────────────────────────────────────────
    # Properties (Read-Only) - Blocking calls
    # ─────────────────────────────────────────────────────────────────────────

    @property
    def label(self) -> str:
        """Get window label."""
        return self._label

    @property
    def title(self) -> str:
        """Get window title."""
        result: str = runtime.window_get(self._label, "title")
        return result

    @property
    def url(self) -> str:
        """Get current URL."""
        result: str = runtime.window_get(self._label, "url")
        return result

    @property
    def theme(self) -> Theme:
        """Get current theme."""
        from .types import Theme

        value = runtime.window_get(self._label, "theme")
        return Theme(value)

    @property
    def scale_factor(self) -> float:
        """Get display scale factor."""
        result: float = runtime.window_get(self._label, "scale_factor")
        return result

    @property
    def inner_position(self) -> PhysicalPosition:
        """Get inner position."""
        from .types import PhysicalPosition

        data = runtime.window_get(self._label, "inner_position")
        return PhysicalPosition.from_dict(data)

    @property
    def outer_position(self) -> PhysicalPosition:
        """Get outer position."""
        from .types import PhysicalPosition

        data = runtime.window_get(self._label, "outer_position")
        return PhysicalPosition.from_dict(data)

    @property
    def inner_size(self) -> PhysicalSize:
        """Get inner dimensions."""
        from .types import PhysicalSize

        data = runtime.window_get(self._label, "inner_size")
        return PhysicalSize.from_dict(data)

    @property
    def outer_size(self) -> PhysicalSize:
        """Get outer dimensions."""
        from .types import PhysicalSize

        data = runtime.window_get(self._label, "outer_size")
        return PhysicalSize.from_dict(data)

    @property
    def cursor_position(self) -> PhysicalPosition:
        """Get cursor position relative to window."""
        from .types import PhysicalPosition

        data = runtime.window_get(self._label, "cursor_position")
        return PhysicalPosition.from_dict(data)

    @property
    def current_monitor(self) -> Monitor | None:
        """Get current monitor."""
        from .types import Monitor

        data = runtime.window_get(self._label, "current_monitor")
        return Monitor.from_dict(data) if data else None

    @property
    def primary_monitor(self) -> Monitor | None:
        """Get primary monitor."""
        from .types import Monitor

        data = runtime.window_get(self._label, "primary_monitor")
        return Monitor.from_dict(data) if data else None

    @property
    def available_monitors(self) -> list[Monitor]:
        """Get all available monitors."""
        from .types import Monitor

        data = runtime.window_get(self._label, "available_monitors")
        return [Monitor.from_dict(m) for m in data]

    # ─────────────────────────────────────────────────────────────────────────
    # State Properties (Read-Only Booleans) - Blocking calls
    # ─────────────────────────────────────────────────────────────────────────

    @property
    def is_fullscreen(self) -> bool:
        """Check if window is fullscreen."""
        result: bool = runtime.window_get(self._label, "is_fullscreen")
        return result

    @property
    def is_minimized(self) -> bool:
        """Check if window is minimized."""
        result: bool = runtime.window_get(self._label, "is_minimized")
        return result

    @property
    def is_maximized(self) -> bool:
        """Check if window is maximized."""
        result: bool = runtime.window_get(self._label, "is_maximized")
        return result

    @property
    def is_focused(self) -> bool:
        """Check if window is focused."""
        result: bool = runtime.window_get(self._label, "is_focused")
        return result

    @property
    def is_decorated(self) -> bool:
        """Check if window has decorations."""
        result: bool = runtime.window_get(self._label, "is_decorated")
        return result

    @property
    def is_resizable(self) -> bool:
        """Check if window is resizable."""
        result: bool = runtime.window_get(self._label, "is_resizable")
        return result

    @property
    def is_enabled(self) -> bool:
        """Check if window is enabled."""
        result: bool = runtime.window_get(self._label, "is_enabled")
        return result

    @property
    def is_visible(self) -> bool:
        """Check if window is visible."""
        result: bool = runtime.window_get(self._label, "is_visible")
        return result

    @property
    def is_closable(self) -> bool:
        """Check if window is closable."""
        result: bool = runtime.window_get(self._label, "is_closable")
        return result

    @property
    def is_maximizable(self) -> bool:
        """Check if window is maximizable."""
        result: bool = runtime.window_get(self._label, "is_maximizable")
        return result

    @property
    def is_minimizable(self) -> bool:
        """Check if window is minimizable."""
        result: bool = runtime.window_get(self._label, "is_minimizable")
        return result

    @property
    def is_always_on_top(self) -> bool:
        """Check if window is always on top."""
        result: bool = runtime.window_get(self._label, "is_always_on_top")
        return result

    @property
    def is_devtools_open(self) -> bool:
        """Check if DevTools is open."""
        result: bool = runtime.window_get(self._label, "is_devtools_open")
        return result

    # ─────────────────────────────────────────────────────────────────────────
    # Window Actions (No Parameters) - Fire-and-forget
    # ─────────────────────────────────────────────────────────────────────────

    def show(self) -> None:
        """Show the window."""
        runtime.window_call(self._label, "show")

    def hide(self) -> None:
        """Hide the window."""
        runtime.window_call(self._label, "hide")

    def close(self) -> None:
        """Close the window."""
        runtime.window_call(self._label, "close")

    def destroy(self) -> None:
        """Destroy the window."""
        runtime.window_call(self._label, "destroy")

    def maximize(self) -> None:
        """Maximize the window."""
        runtime.window_call(self._label, "maximize")

    def unmaximize(self) -> None:
        """Restore from maximized."""
        runtime.window_call(self._label, "unmaximize")

    def minimize(self) -> None:
        """Minimize the window."""
        runtime.window_call(self._label, "minimize")

    def unminimize(self) -> None:
        """Restore from minimized."""
        runtime.window_call(self._label, "unminimize")

    def center(self) -> None:
        """Center window on screen."""
        runtime.window_call(self._label, "center")

    def set_focus(self) -> None:
        """Set focus to window."""
        runtime.window_call(self._label, "set_focus")

    def reload(self) -> None:
        """Reload the webview."""
        runtime.window_call(self._label, "reload")

    def print_page(self) -> None:
        """Print the page."""
        runtime.window_call(self._label, "print")

    def open_devtools(self) -> None:
        """Open DevTools."""
        runtime.window_call(self._label, "open_devtools")

    def close_devtools(self) -> None:
        """Close DevTools."""
        runtime.window_call(self._label, "close_devtools")

    def clear_all_browsing_data(self) -> None:
        """Clear all browsing data."""
        runtime.window_call(self._label, "clear_all_browsing_data")

    def start_dragging(self) -> None:
        """Start window dragging."""
        runtime.window_call(self._label, "start_dragging")

    # ─────────────────────────────────────────────────────────────────────────
    # Window Actions (With Parameters) - Fire-and-forget
    # ─────────────────────────────────────────────────────────────────────────

    def request_user_attention(self, attention_type: UserAttentionType | None = None) -> None:
        """Request user attention (flash/bounce)."""
        runtime.window_call(
            self._label,
            "request_user_attention",
            {"attention_type": attention_type.value if attention_type else None},
        )

    def set_title(self, title: str) -> None:
        """Set window title."""
        runtime.window_call(self._label, "set_title", {"title": title})

    def set_size(self, size: SizeType) -> None:
        """Set window size."""
        from .types import serialize_size

        data = serialize_size(size)
        runtime.window_call(
            self._label, "set_size", {"width": data["width"], "height": data["height"]}
        )

    def set_min_size(self, size: SizeType | None) -> None:
        """Set minimum window size."""
        from .types import serialize_size

        if size:
            data = serialize_size(size)
            runtime.window_call(
                self._label,
                "set_min_size",
                {"width": data["width"], "height": data["height"]},
            )
        else:
            runtime.window_call(self._label, "set_min_size", {})

    def set_max_size(self, size: SizeType | None) -> None:
        """Set maximum window size."""
        from .types import serialize_size

        if size:
            data = serialize_size(size)
            runtime.window_call(
                self._label,
                "set_max_size",
                {"width": data["width"], "height": data["height"]},
            )
        else:
            runtime.window_call(self._label, "set_max_size", {})

    def set_position(self, position: PositionType) -> None:
        """Set window position."""
        from .types import serialize_position

        data = serialize_position(position)
        runtime.window_call(self._label, "set_position", {"x": data["x"], "y": data["y"]})

    def set_fullscreen(self, fullscreen: bool) -> None:
        """Toggle fullscreen mode."""
        runtime.window_call(self._label, "set_fullscreen", {"fullscreen": fullscreen})

    def set_decorations(self, decorations: bool) -> None:
        """Toggle window decorations."""
        runtime.window_call(self._label, "set_decorations", {"decorations": decorations})

    def set_always_on_top(self, always_on_top: bool) -> None:
        """Toggle always-on-top."""
        runtime.window_call(self._label, "set_always_on_top", {"always_on_top": always_on_top})

    def set_resizable(self, resizable: bool) -> None:
        """Toggle resizable."""
        runtime.window_call(self._label, "set_resizable", {"resizable": resizable})

    def set_enabled(self, enabled: bool) -> None:
        """Toggle enabled."""
        runtime.window_call(self._label, "set_enabled", {"enabled": enabled})

    def set_closable(self, closable: bool) -> None:
        """Toggle closable."""
        runtime.window_call(self._label, "set_closable", {"closable": closable})

    def set_maximizable(self, maximizable: bool) -> None:
        """Toggle maximizable."""
        runtime.window_call(self._label, "set_maximizable", {"maximizable": maximizable})

    def set_minimizable(self, minimizable: bool) -> None:
        """Toggle minimizable."""
        runtime.window_call(self._label, "set_minimizable", {"minimizable": minimizable})

    def set_visible_on_all_workspaces(self, visible: bool) -> None:
        """Toggle visibility on all workspaces."""
        runtime.window_call(self._label, "set_visible_on_all_workspaces", {"visible": visible})

    def set_skip_taskbar(self, skip: bool) -> None:
        """Toggle skip taskbar."""
        runtime.window_call(self._label, "set_skip_taskbar", {"skip": skip})

    def set_cursor_icon(self, icon: CursorIcon) -> None:
        """Set cursor icon."""
        runtime.window_call(self._label, "set_cursor_icon", {"icon": icon.value})

    def set_cursor_position(self, position: PositionType) -> None:
        """Set cursor position."""
        from .types import serialize_position

        data = serialize_position(position)
        runtime.window_call(
            self._label,
            "set_cursor_position",
            {"x": data["x"], "y": data["y"]},
        )

    def set_cursor_visible(self, visible: bool) -> None:
        """Toggle cursor visibility."""
        runtime.window_call(self._label, "set_cursor_visible", {"visible": visible})

    def set_cursor_grab(self, grab: bool) -> None:
        """Toggle cursor grab."""
        runtime.window_call(self._label, "set_cursor_grab", {"grab": grab})

    def set_icon(self, icon: bytes | None) -> None:
        """Set window icon (PNG bytes or None)."""
        import base64

        runtime.window_call(
            self._label,
            "set_icon",
            {"icon": base64.b64encode(icon).decode() if icon else None},
        )

    def set_shadow(self, enable: bool) -> None:
        """Toggle window shadow."""
        runtime.window_call(self._label, "set_shadow", {"enable": enable})

    def set_title_bar_style(self, style: TitleBarStyle) -> None:
        """Set title bar style."""
        runtime.window_call(self._label, "set_title_bar_style", {"style": style.value})

    def set_theme(self, theme: Theme | None) -> None:
        """Set window theme."""
        runtime.window_call(self._label, "set_theme", {"theme": theme.value if theme else None})

    # ─────────────────────────────────────────────────────────────────────────
    # Webview Operations
    # ─────────────────────────────────────────────────────────────────────────

    def eval(self, script: str) -> None:
        """Execute JavaScript in the webview (fire-and-forget)."""
        runtime.window_call(self._label, "eval", {"script": script})

    def eval_with_result(self, script: str, timeout: float = 5.0) -> Any:
        """Execute JavaScript and return the result (blocking).

        Note: Result serialization depends on the JS return value.
        """
        return runtime.window_call(
            self._label,
            "eval_with_result",
            {"script": script},
            expect_response=True,
            timeout=timeout,
        )

    def navigate(self, url: str) -> None:
        """Navigate to URL."""
        runtime.window_call(self._label, "navigate", {"url": url})

    def set_zoom(self, scale: float) -> None:
        """Set zoom level."""
        runtime.window_call(self._label, "set_zoom", {"scale": scale})

    def set_background_color(self, color: Color) -> None:
        """Set background color (r, g, b, a)."""
        runtime.window_call(self._label, "set_background_color", {"color": list(color)})

    # ─────────────────────────────────────────────────────────────────────────
    # Visual Effects & Progress
    # ─────────────────────────────────────────────────────────────────────────

    def set_effects(self, effects: Effects) -> None:
        """Set visual effects (Mica, Blur, Acrylic, etc.)."""
        from .types import serialize_effects

        runtime.window_call(self._label, "set_effects", {"effects": serialize_effects(effects)})

    def set_progress_bar(self, state: ProgressBarState) -> None:
        """Set progress bar state."""
        from .types import serialize_progress_bar

        runtime.window_call(
            self._label, "set_progress_bar", {"state": serialize_progress_bar(state)}
        )

    def set_badge_count(self, count: int | None) -> None:
        """Set badge count (dock/taskbar)."""
        runtime.window_call(self._label, "set_badge_count", {"count": count})

    def set_overlay_icon(self, icon: bytes | None) -> None:
        """Set overlay icon (Windows taskbar)."""
        import base64

        runtime.window_call(
            self._label,
            "set_overlay_icon",
            {"icon": base64.b64encode(icon).decode() if icon else None},
        )

    # ─────────────────────────────────────────────────────────────────────────
    # Cookie Management - Blocking calls
    # ─────────────────────────────────────────────────────────────────────────

    def cookies(self) -> list[Cookie]:
        """Get all cookies."""
        from .types import Cookie

        data = runtime.window_call(self._label, "cookies", expect_response=True, timeout=5.0)
        return [Cookie.from_dict(c) for c in (data or [])]

    def set_cookie(self, cookie: Cookie) -> None:
        """Set a cookie."""
        runtime.window_call(self._label, "set_cookie", {"cookie": cookie.to_dict()})

    def delete_cookie(self, name: str) -> None:
        """Delete a cookie by name."""
        runtime.window_call(self._label, "delete_cookie", {"name": name})

    # ─────────────────────────────────────────────────────────────────────────
    # String Representation
    # ─────────────────────────────────────────────────────────────────────────

    def __repr__(self) -> str:
        """Return string representation."""
        return f"WindowProxy({self._label!r})"
