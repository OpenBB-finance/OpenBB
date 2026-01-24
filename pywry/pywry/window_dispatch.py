"""Window dispatch handlers for IPC commands.

This module contains the dispatch logic for getting window properties
and calling window methods. Uses dictionary-based dispatch instead of
if/elif chains for better maintainability.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any


if TYPE_CHECKING:
    from collections.abc import Callable

    # Window type from pytauri - using Any for runtime flexibility
    Window = Any


# =============================================================================
# Property Getters
# =============================================================================


def _get_title(window: Window) -> str:
    """Get window title."""
    result: str = window.title()
    return result


def _get_url(window: Window) -> str:
    """Get current URL."""
    result = window.url()
    return str(result) if result else ""


def _get_theme(window: Window) -> str:
    """Get current theme as string."""
    theme = window.theme()
    return theme.name if hasattr(theme, "name") else str(theme)


def _get_scale_factor(window: Window) -> float:
    """Get display scale factor."""
    result: float = window.scale_factor()
    return result


def _extract_position(pos: Any) -> dict[str, int] | None:
    """Extract position from pytauri wrapper or tuple.

    pytauri returns Position.Physical/Logical wrappers that store
    the actual (x, y) tuple in ._0 attribute.
    """
    if pos is None:
        return None
    # pytauri wrappers use _0 for the inner tuple
    if hasattr(pos, "_0"):
        inner = pos._0
        return {"x": inner[0], "y": inner[1]}
    # Direct tuple
    if isinstance(pos, tuple) and len(pos) >= 2:
        return {"x": pos[0], "y": pos[1]}
    # Object with .x, .y attributes
    if hasattr(pos, "x") and hasattr(pos, "y"):
        return {"x": pos.x, "y": pos.y}
    return None


def _extract_size(size: Any) -> dict[str, int] | None:
    """Extract size from pytauri wrapper or tuple.

    pytauri returns Size.Physical/Logical wrappers that store
    the actual (width, height) tuple in ._0 attribute.
    """
    if size is None:
        return None
    # pytauri wrappers use _0 for the inner tuple
    if hasattr(size, "_0"):
        inner = size._0
        return {"width": inner[0], "height": inner[1]}
    # Direct tuple
    if isinstance(size, tuple) and len(size) >= 2:
        return {"width": size[0], "height": size[1]}
    # Object with .width, .height attributes
    if hasattr(size, "width") and hasattr(size, "height"):
        return {"width": size.width, "height": size.height}
    return None


def _get_inner_position(window: Window) -> dict[str, int] | None:
    """Get inner position."""
    pos = window.inner_position()
    return _extract_position(pos)


def _get_outer_position(window: Window) -> dict[str, int] | None:
    """Get outer position."""
    pos = window.outer_position()
    return _extract_position(pos)


def _get_inner_size(window: Window) -> dict[str, int] | None:
    """Get inner size."""
    size = window.inner_size()
    return _extract_size(size)


def _get_outer_size(window: Window) -> dict[str, int] | None:
    """Get outer size."""
    size = window.outer_size()
    return _extract_size(size)


def _serialize_monitor(monitor: Any) -> dict[str, Any] | None:
    """Serialize a Monitor object for IPC.

    Monitor objects from pytauri may have various attribute styles.
    """
    if monitor is None:
        return None

    # Get name - may be callable or attribute
    name = None
    if hasattr(monitor, "name"):
        name_attr = monitor.name
        name = name_attr() if callable(name_attr) else name_attr

    # Get position
    position = None
    if hasattr(monitor, "position"):
        pos_attr = monitor.position
        pos = pos_attr() if callable(pos_attr) else pos_attr
        position = _extract_position(pos)

    # Get size
    size = None
    if hasattr(monitor, "size"):
        size_attr = monitor.size
        sz = size_attr() if callable(size_attr) else size_attr
        size = _extract_size(sz)

    # Get scale factor
    scale_factor = 1.0
    if hasattr(monitor, "scale_factor"):
        sf_attr = monitor.scale_factor
        scale_factor = sf_attr() if callable(sf_attr) else sf_attr

    return {
        "name": name,
        "position": position,
        "size": size,
        "scale_factor": scale_factor,
    }


def _get_current_monitor(window: Window) -> dict[str, Any] | None:
    """Get current monitor."""
    monitor = window.current_monitor()
    return _serialize_monitor(monitor)


def _get_primary_monitor(window: Window) -> dict[str, Any] | None:
    """Get primary monitor."""
    monitor = window.primary_monitor()
    return _serialize_monitor(monitor)


def _get_available_monitors(window: Window) -> list[dict[str, Any]]:
    """Get all available monitors."""
    monitors = window.available_monitors()
    if not monitors:
        return []
    return [m for m in (_serialize_monitor(mon) for mon in monitors) if m is not None]


# Property dispatch table: property name -> getter function
PROPERTY_GETTERS: dict[str, Callable[[Window], Any]] = {
    # Simple value properties
    "title": _get_title,
    "url": _get_url,
    "theme": _get_theme,
    "scale_factor": _get_scale_factor,
    # Position/size properties
    "inner_position": _get_inner_position,
    "outer_position": _get_outer_position,
    "inner_size": _get_inner_size,
    "outer_size": _get_outer_size,
    # Monitor properties
    "current_monitor": _get_current_monitor,
    "primary_monitor": _get_primary_monitor,
    "available_monitors": _get_available_monitors,
    # Boolean state properties - direct method calls
    "is_visible": lambda w: w.is_visible(),
    "is_focused": lambda w: w.is_focused(),
    "is_decorated": lambda w: w.is_decorated(),
    "is_resizable": lambda w: w.is_resizable(),
    "is_enabled": lambda w: w.is_enabled(),
    "is_maximizable": lambda w: w.is_maximizable(),
    "is_minimizable": lambda w: w.is_minimizable(),
    "is_closable": lambda w: w.is_closable(),
    "is_maximized": lambda w: w.is_maximized(),
    "is_minimized": lambda w: w.is_minimized(),
    "is_fullscreen": lambda w: w.is_fullscreen(),
    "is_always_on_top": lambda w: w.is_always_on_top(),
    "is_always_on_bottom": lambda w: w.is_always_on_bottom(),
    "is_devtools_open": lambda w: (
        w.is_devtools_open() if hasattr(w, "is_devtools_open") else False
    ),
}


def get_window_property(window: Window, prop: str) -> Any:
    """Get a specific property from a WebviewWindow.

    Parameters
    ----------
    window : Any
        The WebviewWindow instance.
    prop : str
        Property name to get.

    Returns
    -------
    Any
        The property value.

    Raises
    ------
    ValueError
        If property name is unknown.
    """
    if prop == "monitor_from_point":
        raise ValueError("monitor_from_point requires x, y parameters")

    getter = PROPERTY_GETTERS.get(prop)
    if getter is None:
        raise ValueError(f"Unknown property: {prop}")

    return getter(window)


# =============================================================================
# Method Callers - Organized by category
# =============================================================================


def _call_visibility_method(window: Window, method: str, args: dict[str, Any]) -> None:
    """Handle window visibility and focus methods."""
    if method == "show":
        window.show()
    elif method == "hide":
        window.hide()
    elif method == "set_focus":
        window.set_focus()
    elif method == "close":
        window.close()
    elif method == "destroy":
        window.destroy()
    elif method == "set_visible":
        if args.get("visible", True):
            window.show()
        else:
            window.hide()


def _call_state_method(window: Window, method: str, args: dict[str, Any]) -> None:
    """Handle window state methods (minimize, maximize, fullscreen)."""
    if method == "minimize":
        window.minimize()
    elif method == "unminimize":
        window.unminimize()
    elif method == "maximize":
        window.maximize()
    elif method == "unmaximize":
        window.unmaximize()
    elif method == "toggle_maximize":
        window.toggle_maximize()
    elif method == "set_fullscreen":
        window.set_fullscreen(args.get("fullscreen", True))
    elif method == "center":
        window.center()
    elif method == "request_user_attention":
        attention_type = args.get("attention_type")
        if attention_type is not None:
            from pytauri import UserAttentionType

            if isinstance(attention_type, str):
                attention_type = getattr(UserAttentionType, attention_type)
            window.request_user_attention(attention_type)
        else:
            window.request_user_attention(None)


def _call_property_setter(window: Window, method: str, args: dict[str, Any]) -> None:
    """Handle window property setters."""
    setters = {
        "set_title": lambda: window.set_title(args.get("title", "")),
        "set_enabled": lambda: window.set_enabled(args.get("enabled", True)),
        "set_decorations": lambda: window.set_decorations(args.get("decorations", True)),
        "set_resizable": lambda: window.set_resizable(args.get("resizable", True)),
        "set_maximizable": lambda: window.set_maximizable(args.get("maximizable", True)),
        "set_minimizable": lambda: window.set_minimizable(args.get("minimizable", True)),
        "set_closable": lambda: window.set_closable(args.get("closable", True)),
        "set_always_on_top": lambda: window.set_always_on_top(args.get("always_on_top", True)),
        "set_always_on_bottom": lambda: window.set_always_on_bottom(
            args.get("always_on_bottom", True)
        ),
    }
    if method in setters:
        setters[method]()


def _call_size_position_method(window: Window, method: str, args: dict[str, Any]) -> None:
    """Handle size and position methods.

    Note: pytauri requires Size.Physical/Logical and Position.Physical/Logical
    wrappers instead of raw tuples.
    """
    from pytauri.ffi import Position, Size

    if method == "set_size":
        width = args.get("width", 800)
        height = args.get("height", 600)
        size = Size.Physical((int(width), int(height)))
        window.set_size(size)
    elif method == "set_min_size":
        width, height = args.get("width"), args.get("height")
        if width is not None and height is not None:
            size = Size.Physical((int(width), int(height)))
            window.set_min_size(size)
        else:
            window.set_min_size(None)
    elif method == "set_max_size":
        width, height = args.get("width"), args.get("height")
        if width is not None and height is not None:
            size = Size.Physical((int(width), int(height)))
            window.set_max_size(size)
        else:
            window.set_max_size(None)
    elif method == "set_size_constraints":
        min_size, max_size = args.get("min_size"), args.get("max_size")
        if min_size:
            size = Size.Physical((int(min_size["width"]), int(min_size["height"])))
            window.set_min_size(size)
        if max_size:
            size = Size.Physical((int(max_size["width"]), int(max_size["height"])))
            window.set_max_size(size)
    elif method == "set_position":
        x, y = args.get("x", 0), args.get("y", 0)
        pos = Position.Physical((int(x), int(y)))
        window.set_position(pos)


def _set_background_color(window: Any, args: dict[str, Any]) -> None:
    """Set window background color."""
    color = args.get("color", args)
    if isinstance(color, dict):
        rgba = (
            color.get("r", 0),
            color.get("g", 0),
            color.get("b", 0),
            color.get("a", 255),
        )
    elif isinstance(color, (list, tuple)):
        rgba = tuple(color)
    else:
        rgba = (0, 0, 0, 255)
    window.set_background_color(rgba)


def _set_theme(window: Any, args: dict[str, Any]) -> None:
    """Set window theme."""
    theme = args.get("theme")
    if theme is not None:
        from pytauri import Theme

        if isinstance(theme, str):
            theme = Theme[theme.capitalize()]
    window.set_theme(theme)


def _set_title_bar_style(window: Any, args: dict[str, Any]) -> None:
    """Set title bar style."""
    style = args.get("style", "Visible")
    if hasattr(window, "set_title_bar_style"):
        from pytauri.window import TitleBarStyle

        if isinstance(style, str):
            style = getattr(TitleBarStyle, style)
        window.set_title_bar_style(style)


def _set_effects(window: Any, args: dict[str, Any]) -> None:
    """Set window effects."""
    effects_data = args.get("effects")
    if effects_data and hasattr(window, "set_effects"):
        from pytauri.window import Effect, Effects, EffectState

        effect_list = effects_data.get("effects", [])
        converted = [getattr(Effect, e) if isinstance(e, str) else e for e in effect_list]
        state = effects_data.get("state")
        if isinstance(state, str):
            state = getattr(EffectState, state)
        effects = Effects(
            effects=converted,
            state=state,
            radius=effects_data.get("radius"),
            color=effects_data.get("color"),
        )
        window.set_effects(effects)


# Dispatch table for appearance methods
_APPEARANCE_DISPATCH: dict[str, Any] = {
    "set_background_color": _set_background_color,
    "set_theme": _set_theme,
    "set_title_bar_style": _set_title_bar_style,
    "set_content_protected": lambda w, a: w.set_content_protected(a.get("protected", True)),
    "set_shadow": lambda w, a: w.set_shadow(a.get("shadow", True)),
    "set_effects": _set_effects,
}


def _call_appearance_method(window: Any, method: str, args: dict[str, Any]) -> None:
    """Handle appearance methods (color, theme, effects)."""
    handler = _APPEARANCE_DISPATCH.get(method)
    if handler:
        handler(window, args)


def _call_cursor_method(window: Window, method: str, args: dict[str, Any]) -> None:
    """Handle cursor-related methods."""
    if method == "set_cursor_icon":
        icon = args.get("icon", "Default")
        if hasattr(window, "set_cursor_icon"):
            from pytauri import CursorIcon

            if isinstance(icon, str):
                icon = getattr(CursorIcon, icon)
            window.set_cursor_icon(icon)
    elif method == "set_cursor_position":
        if hasattr(window, "set_cursor_position"):
            x, y = args.get("x", 0), args.get("y", 0)
            window.set_cursor_position((float(x), float(y)))
    elif method == "set_cursor_visible":
        if hasattr(window, "set_cursor_visible"):
            window.set_cursor_visible(args.get("visible", True))
    elif method == "set_cursor_grab":
        if hasattr(window, "set_cursor_grab"):
            window.set_cursor_grab(args.get("grab", False))


def _call_behavior_method(window: Window, method: str, args: dict[str, Any]) -> None:
    """Handle window behavior methods."""
    if method == "set_ignore_cursor_events" and hasattr(window, "set_ignore_cursor_events"):
        window.set_ignore_cursor_events(args.get("ignore", False))
    elif method == "set_progress_bar":
        state = args.get("state")
        if state and hasattr(window, "set_progress_bar"):
            from pytauri.window import ProgressBarState, ProgressBarStatus

            status = state.get("status", "None")
            if isinstance(status, str):
                status = getattr(ProgressBarStatus, status)
            window.set_progress_bar(ProgressBarState(status=status, progress=state.get("progress")))
    elif method == "set_visible_on_all_workspaces" and hasattr(
        window, "set_visible_on_all_workspaces"
    ):
        window.set_visible_on_all_workspaces(args.get("visible", True))
    elif method == "set_traffic_light_position" and hasattr(window, "set_traffic_light_position"):
        x, y = args.get("x", 0), args.get("y", 0)
        window.set_traffic_light_position((float(x), float(y)))


def _webview_navigate(window: Any, args: dict[str, Any]) -> None:
    """Navigate to URL."""
    if hasattr(window, "navigate"):
        window.navigate(args.get("url", ""))


def _webview_eval(window: Any, args: dict[str, Any]) -> None:
    """Evaluate JavaScript."""
    window.eval(args.get("script", ""))


def _webview_open_devtools(window: Any, _args: dict[str, Any]) -> None:
    """Open developer tools."""
    if hasattr(window, "open_devtools"):
        window.open_devtools()


def _webview_close_devtools(window: Any, _args: dict[str, Any]) -> None:
    """Close developer tools."""
    if hasattr(window, "close_devtools"):
        window.close_devtools()


def _webview_is_devtools_open(window: Any, _args: dict[str, Any]) -> bool:
    """Check if devtools is open."""
    return window.is_devtools_open() if hasattr(window, "is_devtools_open") else False


def _webview_set_zoom(window: Any, args: dict[str, Any]) -> None:
    """Set zoom level."""
    if hasattr(window, "set_zoom"):
        window.set_zoom(args.get("scale", 1.0))


def _webview_zoom(window: Any, _args: dict[str, Any]) -> float:
    """Get zoom level."""
    return window.zoom() if hasattr(window, "zoom") else 1.0


def _webview_clear_browsing_data(window: Any, _args: dict[str, Any]) -> None:
    """Clear all browsing data."""
    if hasattr(window, "clear_all_browsing_data"):
        window.clear_all_browsing_data()


def _webview_reload(window: Any, _args: dict[str, Any]) -> None:
    """Reload the page."""
    if hasattr(window, "reload"):
        window.reload()


def _webview_print(window: Any, _args: dict[str, Any]) -> None:
    """Print the page."""
    if hasattr(window, "print"):
        window.print()


# Dispatch table for webview methods - maps method name to (handler, returns_value)
_WEBVIEW_DISPATCH: dict[str, tuple[Any, bool]] = {
    "navigate": (_webview_navigate, False),
    "eval": (_webview_eval, False),
    "open_devtools": (_webview_open_devtools, False),
    "close_devtools": (_webview_close_devtools, False),
    "is_devtools_open": (_webview_is_devtools_open, True),
    "set_zoom": (_webview_set_zoom, False),
    "zoom": (_webview_zoom, True),
    "clear_all_browsing_data": (_webview_clear_browsing_data, False),
    "reload": (_webview_reload, False),
    "print": (_webview_print, False),
}


def _call_webview_method(window: Any, method: str, args: dict[str, Any]) -> Any:
    """Handle webview operations. Returns value for methods that have return values."""
    entry = _WEBVIEW_DISPATCH.get(method)
    if entry is None:
        return None
    handler, returns_value = entry
    result = handler(window, args)
    return result if returns_value else None


def _serialize_cookie(cookie: Any) -> dict[str, Any]:
    """Serialize a Cookie object for IPC."""
    if cookie is None:
        return {}
    return {
        "name": getattr(cookie, "name", ""),
        "value": getattr(cookie, "value", ""),
        "domain": getattr(cookie, "domain", None),
        "path": getattr(cookie, "path", None),
        "expires": getattr(cookie, "expires", None),
        "http_only": getattr(cookie, "http_only", False),
        "secure": getattr(cookie, "secure", False),
        "same_site": getattr(cookie, "same_site", None),
    }


def _cookie_set(window: Any, args: dict[str, Any]) -> None:
    """Set a cookie."""
    if hasattr(window, "set_cookie"):
        window.set_cookie(args.get("cookie", {}))


def _cookie_get(window: Any, args: dict[str, Any]) -> list[dict[str, Any]]:
    """Get cookies."""
    if hasattr(window, "get_cookies"):
        cookies = window.get_cookies(args.get("url"))
        return [_serialize_cookie(c) for c in cookies] if cookies else []
    return []


def _cookie_remove(window: Any, args: dict[str, Any]) -> None:
    """Remove a cookie."""
    if hasattr(window, "remove_cookie"):
        window.remove_cookie(args.get("name", ""), args.get("url"))


def _cookie_remove_all(window: Any, _args: dict[str, Any]) -> None:
    """Remove all cookies."""
    if hasattr(window, "remove_all_cookies"):
        window.remove_all_cookies()


# Dispatch table for cookie methods - maps method name to (handler, returns_value)
_COOKIE_DISPATCH: dict[str, tuple[Any, bool]] = {
    "set_cookie": (_cookie_set, False),
    "get_cookies": (_cookie_get, True),
    "remove_cookie": (_cookie_remove, False),
    "remove_all_cookies": (_cookie_remove_all, False),
}


def _call_cookie_method(window: Any, method: str, args: dict[str, Any]) -> Any:
    """Handle cookie operations. Returns value for methods that have return values."""
    entry = _COOKIE_DISPATCH.get(method)
    if entry is None:
        return None
    handler, returns_value = entry
    result = handler(window, args)
    return result if returns_value else None


# Method categories for dispatch
VISIBILITY_METHODS = {"show", "hide", "set_focus", "close", "destroy", "set_visible"}
STATE_METHODS = {
    "minimize",
    "unminimize",
    "maximize",
    "unmaximize",
    "toggle_maximize",
    "set_fullscreen",
    "center",
    "request_user_attention",
}
PROPERTY_METHODS = {
    "set_title",
    "set_enabled",
    "set_decorations",
    "set_resizable",
    "set_maximizable",
    "set_minimizable",
    "set_closable",
    "set_always_on_top",
    "set_always_on_bottom",
}
SIZE_POSITION_METHODS = {
    "set_size",
    "set_min_size",
    "set_max_size",
    "set_size_constraints",
    "set_position",
}
APPEARANCE_METHODS = {
    "set_background_color",
    "set_theme",
    "set_title_bar_style",
    "set_content_protected",
    "set_shadow",
    "set_effects",
}
CURSOR_METHODS = {
    "set_cursor_icon",
    "set_cursor_position",
    "set_cursor_visible",
    "set_cursor_grab",
}
BEHAVIOR_METHODS = {
    "set_ignore_cursor_events",
    "set_progress_bar",
    "set_visible_on_all_workspaces",
    "set_traffic_light_position",
}
WEBVIEW_METHODS = {
    "navigate",
    "eval",
    "open_devtools",
    "close_devtools",
    "is_devtools_open",
    "set_zoom",
    "zoom",
    "clear_all_browsing_data",
    "reload",
    "print",
}
COOKIE_METHODS = {"set_cookie", "get_cookies", "remove_cookie", "remove_all_cookies"}

# Master dispatch table: category set -> (handler, returns_value)
# This allows the main dispatcher to be simple and maintainable
_METHOD_CATEGORIES: list[tuple[set[str], Any, bool]] = [
    (VISIBILITY_METHODS, _call_visibility_method, False),
    (STATE_METHODS, _call_state_method, False),
    (PROPERTY_METHODS, _call_property_setter, False),
    (SIZE_POSITION_METHODS, _call_size_position_method, False),
    (APPEARANCE_METHODS, _call_appearance_method, False),
    (CURSOR_METHODS, _call_cursor_method, False),
    (BEHAVIOR_METHODS, _call_behavior_method, False),
    (WEBVIEW_METHODS, _call_webview_method, True),
    (COOKIE_METHODS, _call_cookie_method, True),
]


def call_window_method(window: Any, method: str, args: dict[str, Any]) -> Any:
    """Call a specific method on a WebviewWindow.

    Parameters
    ----------
    window : Any
        The WebviewWindow instance.
    method : str
        Method name to call.
    args : dict[str, Any]
        Dict with named parameters, e.g.:
        - {"title": "New Title"} for set_title
        - {"value": True} for boolean setters
        - {"width": 800, "height": 600} for set_size

    Returns
    -------
    Any
        Method result (usually None for setters, value for getters).

    Raises
    ------
    ValueError
        If method name is unknown.
    """
    for method_set, handler, returns_value in _METHOD_CATEGORIES:
        if method in method_set:
            if returns_value:
                return handler(window, method, args)
            handler(window, method, args)
            return None

    raise ValueError(f"Unknown method: {method}")
