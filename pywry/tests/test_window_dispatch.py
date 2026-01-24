"""Tests for pywry.window_dispatch module.

These tests verify the dispatch table logic and method routing.
We use minimal stub objects that implement the same interface
as pytauri windows to test the dispatch logic directly.

Note: These are NOT mock tests that just verify "method was called".
They verify that the dispatch logic:
1. Routes to the correct handler
2. Extracts correct return values
3. Raises appropriate errors for unknown properties/methods
4. Handles argument transformation correctly
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pytest

from pywry.window_dispatch import (
    APPEARANCE_METHODS,
    BEHAVIOR_METHODS,
    COOKIE_METHODS,
    CURSOR_METHODS,
    PROPERTY_GETTERS,
    PROPERTY_METHODS,
    SIZE_POSITION_METHODS,
    STATE_METHODS,
    VISIBILITY_METHODS,
    WEBVIEW_METHODS,
    _serialize_monitor,
    call_window_method,
    get_window_property,
)


# =============================================================================
# Stub Classes - Real objects that behave like pytauri types
# =============================================================================


@dataclass
class StubPosition:
    """Stub for position types."""

    x: int
    y: int


@dataclass
class StubSize:
    """Stub for size types."""

    width: int
    height: int


class StubMonitor:
    """Stub for pytauri Monitor."""

    def __init__(
        self,
        name: str | None = "Test Monitor",
        width: int = 1920,
        height: int = 1080,
        x: int = 0,
        y: int = 0,
        scale: float = 1.0,
    ):
        """Initialize monitor with dimensions and position."""
        self._name = name
        self._size = StubSize(width, height)
        self._position = StubPosition(x, y)
        self._scale = scale

    def name(self) -> str | None:
        """Return monitor name."""
        return self._name

    def size(self) -> StubSize:
        """Return monitor size."""
        return self._size

    def position(self) -> StubPosition:
        """Return monitor position."""
        return self._position

    def scale_factor(self) -> float:
        """Return monitor scale factor."""
        return self._scale


class StubTheme:
    """Stub for pytauri Theme enum."""

    def __init__(self, name: str = "Dark"):
        """Initialize theme with name."""
        self.name = name


@dataclass
class WindowGeometry:
    """Grouped geometry state for StubWindow."""

    inner_pos: StubPosition
    outer_pos: StubPosition
    inner_size: StubSize
    outer_size: StubSize
    scale_factor: float = 2.0


@dataclass
class WindowVisibility:
    """Window visibility and focus state."""

    visible: bool = True
    focused: bool = False
    maximized: bool = False
    minimized: bool = False
    fullscreen: bool = False


@dataclass
class WindowCapabilities:
    """Window capability flags."""

    decorated: bool = True
    resizable: bool = True
    enabled: bool = True
    maximizable: bool = True
    minimizable: bool = True
    closable: bool = True
    always_on_top: bool = False
    always_on_bottom: bool = False
    shadow: bool = True
    content_protected: bool = False


@dataclass
class WindowCursor:
    """Cursor state for window."""

    visible: bool = True
    grab: bool = False
    ignore_events: bool = False


@dataclass
class WindowMonitors:
    """Grouped monitor info for StubWindow."""

    primary: StubMonitor
    current: StubMonitor
    available: list[StubMonitor]


# pylint: disable=too-many-public-methods
class StubWindow:
    """Stub window that implements pytauri WebviewWindow interface.

    This is a REAL object with REAL state, not a mock.
    Methods actually change state that can be verified.
    Uses composition to group related state.

    Note: The many public methods here mirror the real pytauri interface.
    """

    def __init__(self) -> None:
        """Initialize window with default state."""
        # Basic properties
        self._title = "Default Title"
        self._url = "https://example.com"
        self._theme = StubTheme("Dark")
        self._zoom = 1.0
        self._devtools_open = False

        # Grouped state via composition
        self._geometry = WindowGeometry(
            inner_pos=StubPosition(100, 200),
            outer_pos=StubPosition(95, 175),
            inner_size=StubSize(800, 600),
            outer_size=StubSize(850, 650),
        )
        self._visibility = WindowVisibility()
        self._capabilities = WindowCapabilities()
        self._cursor = WindowCursor()
        primary = StubMonitor("Primary", 2560, 1440)
        current = StubMonitor("Current", 1920, 1080)
        self._monitors = WindowMonitors(
            primary=primary,
            current=current,
            available=[primary, current],
        )

        # Track method calls for verification
        self._calls: list[tuple[str, tuple[Any, ...]]] = []

    def _record(self, method: str, *args: Any) -> None:
        """Record method call for verification."""
        self._calls.append((method, args))

    # Property getters
    def title(self) -> str:
        """Return window title."""
        return self._title

    def url(self) -> str:
        """Return current URL."""
        return self._url

    def theme(self) -> StubTheme:
        """Return current theme."""
        return self._theme

    def scale_factor(self) -> float:
        """Return scale factor."""
        return self._geometry.scale_factor

    def inner_position(self) -> StubPosition:
        """Return inner position."""
        return self._geometry.inner_pos

    def outer_position(self) -> StubPosition:
        """Return outer position."""
        return self._geometry.outer_pos

    def inner_size(self) -> StubSize:
        """Return inner size."""
        return self._geometry.inner_size

    def outer_size(self) -> StubSize:
        """Return outer size."""
        return self._geometry.outer_size

    def current_monitor(self) -> StubMonitor:
        """Return current monitor."""
        return self._monitors.current

    def primary_monitor(self) -> StubMonitor:
        """Return primary monitor."""
        return self._monitors.primary

    def available_monitors(self) -> list[StubMonitor]:
        """Return available monitors."""
        return self._monitors.available

    # Boolean state getters
    def is_visible(self) -> bool:
        """Return visibility state."""
        return self._visibility.visible

    def is_focused(self) -> bool:
        """Return focus state."""
        return self._visibility.focused

    def is_decorated(self) -> bool:
        """Return decoration state."""
        return self._capabilities.decorated

    def is_resizable(self) -> bool:
        """Return resizable state."""
        return self._capabilities.resizable

    def is_enabled(self) -> bool:
        """Return enabled state."""
        return self._capabilities.enabled

    def is_maximizable(self) -> bool:
        """Return maximizable state."""
        return self._capabilities.maximizable

    def is_minimizable(self) -> bool:
        """Return minimizable state."""
        return self._capabilities.minimizable

    def is_closable(self) -> bool:
        """Return closable state."""
        return self._capabilities.closable

    def is_maximized(self) -> bool:
        """Return maximized state."""
        return self._visibility.maximized

    def is_minimized(self) -> bool:
        """Return minimized state."""
        return self._visibility.minimized

    def is_fullscreen(self) -> bool:
        """Return fullscreen state."""
        return self._visibility.fullscreen

    def is_always_on_top(self) -> bool:
        """Return always-on-top state."""
        return self._capabilities.always_on_top

    def is_always_on_bottom(self) -> bool:
        """Return always-on-bottom state."""
        return self._capabilities.always_on_bottom

    def is_devtools_open(self) -> bool:
        """Return devtools open state."""
        return self._devtools_open

    # Visibility methods
    def show(self) -> None:
        """Show the window."""
        self._record("show")
        self._visibility.visible = True

    def hide(self) -> None:
        """Hide the window."""
        self._record("hide")
        self._visibility.visible = False

    def set_focus(self) -> None:
        """Focus the window."""
        self._record("set_focus")
        self._visibility.focused = True

    def close(self) -> None:
        """Close the window."""
        self._record("close")
        self._visibility.visible = False

    def destroy(self) -> None:
        """Destroy the window."""
        self._record("destroy")
        self._visibility.visible = False

    # State methods
    def minimize(self) -> None:
        """Minimize the window."""
        self._record("minimize")
        self._visibility.minimized = True

    def unminimize(self) -> None:
        """Unminimize the window."""
        self._record("unminimize")
        self._visibility.minimized = False

    def maximize(self) -> None:
        """Maximize the window."""
        self._record("maximize")
        self._visibility.maximized = True

    def unmaximize(self) -> None:
        """Unmaximize the window."""
        self._record("unmaximize")
        self._visibility.maximized = False

    def toggle_maximize(self) -> None:
        """Toggle maximize state."""
        self._record("toggle_maximize")
        self._visibility.maximized = not self._visibility.maximized

    def set_fullscreen(self, fullscreen: bool) -> None:
        """Set fullscreen state."""
        self._record("set_fullscreen", fullscreen)
        self._visibility.fullscreen = fullscreen

    def center(self) -> None:
        """Center the window."""
        self._record("center")

    def request_user_attention(self, attention_type: Any) -> None:
        """Request user attention."""
        self._record("request_user_attention", attention_type)

    # Property setters
    def set_title(self, title: str) -> None:
        """Set window title."""
        self._record("set_title", title)
        self._title = title

    def set_enabled(self, enabled: bool) -> None:
        """Set enabled state."""
        self._record("set_enabled", enabled)
        self._capabilities.enabled = enabled

    def set_decorations(self, decorations: bool) -> None:
        """Set decoration state."""
        self._record("set_decorations", decorations)
        self._capabilities.decorated = decorations

    def set_resizable(self, resizable: bool) -> None:
        """Set resizable state."""
        self._record("set_resizable", resizable)
        self._capabilities.resizable = resizable

    def set_maximizable(self, maximizable: bool) -> None:
        """Set maximizable state."""
        self._record("set_maximizable", maximizable)
        self._capabilities.maximizable = maximizable

    def set_minimizable(self, minimizable: bool) -> None:
        """Set minimizable state."""
        self._record("set_minimizable", minimizable)
        self._capabilities.minimizable = minimizable

    def set_closable(self, closable: bool) -> None:
        """Set closable state."""
        self._record("set_closable", closable)
        self._capabilities.closable = closable

    def set_always_on_top(self, always: bool) -> None:
        """Set always-on-top state."""
        self._record("set_always_on_top", always)
        self._capabilities.always_on_top = always

    def set_always_on_bottom(self, always: bool) -> None:
        """Set always-on-bottom state."""
        self._record("set_always_on_bottom", always)
        self._capabilities.always_on_bottom = always

    # Size/position methods
    def set_size(self, size: Any) -> None:
        """Set window size."""
        self._record("set_size", size)
        # Handle pytauri wrapper (has _0) or plain tuple
        if hasattr(size, "_0"):
            w, h = size._0
        else:
            w, h = size[0], size[1]
        self._geometry.inner_size = StubSize(int(w), int(h))

    def set_min_size(self, size: Any) -> None:
        """Set minimum size."""
        self._record("set_min_size", size)

    def set_max_size(self, size: Any) -> None:
        """Set maximum size."""
        self._record("set_max_size", size)

    def set_position(self, pos: Any) -> None:
        """Set window position."""
        self._record("set_position", pos)
        # Handle pytauri wrapper (has _0) or plain tuple
        if hasattr(pos, "_0"):
            x, y = pos._0
        else:
            x, y = pos[0], pos[1]
        self._geometry.inner_pos = StubPosition(int(x), int(y))

    # Appearance methods
    def set_background_color(self, color: tuple[int, ...]) -> None:
        """Set background color."""
        self._record("set_background_color", color)

    def set_theme(self, theme: Any) -> None:
        """Set window theme."""
        self._record("set_theme", theme)
        self._theme = StubTheme(str(theme))

    def set_title_bar_style(self, style: Any) -> None:
        """Set title bar style."""
        self._record("set_title_bar_style", style)

    def set_content_protected(self, protected: bool) -> None:
        """Set content protection."""
        self._record("set_content_protected", protected)
        self._capabilities.content_protected = protected

    def set_shadow(self, shadow: bool) -> None:
        """Set window shadow."""
        self._record("set_shadow", shadow)
        self._capabilities.shadow = shadow

    def set_effects(self, effects: Any) -> None:
        """Set window effects."""
        self._record("set_effects", effects)

    # Cursor methods
    def set_cursor_icon(self, icon: Any) -> None:
        """Set cursor icon."""
        self._record("set_cursor_icon", icon)

    def set_cursor_position(self, pos: Any) -> None:
        """Set cursor position."""
        self._record("set_cursor_position", pos)

    def set_cursor_visible(self, visible: bool) -> None:
        """Set cursor visibility."""
        self._record("set_cursor_visible", visible)
        self._cursor.visible = visible

    def set_cursor_grab(self, grab: bool) -> None:
        """Set cursor grab state."""
        self._record("set_cursor_grab", grab)
        self._cursor.grab = grab

    # Behavior methods
    def set_ignore_cursor_events(self, ignore: bool) -> None:
        """Set ignore cursor events state."""
        self._record("set_ignore_cursor_events", ignore)
        self._cursor.ignore_events = ignore

    def set_progress_bar(self, state: Any) -> None:
        """Set progress bar state."""
        self._record("set_progress_bar", state)

    def set_visible_on_all_workspaces(self, visible: bool) -> None:
        """Set visible on all workspaces."""
        self._record("set_visible_on_all_workspaces", visible)

    def set_traffic_light_position(self, pos: Any) -> None:
        """Set traffic light position."""
        self._record("set_traffic_light_position", pos)

    # Webview methods
    def navigate(self, url: str) -> None:
        """Navigate to URL."""
        self._record("navigate", url)
        self._url = url

    def eval(self, script: str) -> None:
        """Evaluate JavaScript."""
        self._record("eval", script)

    def open_devtools(self) -> None:
        """Open devtools."""
        self._record("open_devtools")
        self._devtools_open = True

    def close_devtools(self) -> None:
        """Close devtools."""
        self._record("close_devtools")
        self._devtools_open = False

    def set_zoom(self, zoom: float) -> None:
        """Set zoom level."""
        self._record("set_zoom", zoom)
        self._zoom = zoom

    def zoom(self, zoom: float) -> None:
        """Set zoom level (alias)."""
        self._record("zoom", zoom)
        self._zoom = zoom

    def clear_all_browsing_data(self) -> None:
        """Clear all browsing data."""
        self._record("clear_all_browsing_data")

    def reload(self) -> None:
        """Reload the page."""
        self._record("reload")

    def print(self) -> None:
        """Print the page."""
        self._record("print")


# =============================================================================
# Tests for get_window_property
# =============================================================================


class TestGetWindowProperty:
    """Test property getter dispatch."""

    def test_title_property(self) -> None:
        """title returns window title."""
        window = StubWindow()
        window._title = "Test Title"

        result = get_window_property(window, "title")
        assert result == "Test Title"

    def test_url_property(self) -> None:
        """url returns current URL."""
        window = StubWindow()
        window._url = "https://test.com"

        result = get_window_property(window, "url")
        assert result == "https://test.com"

    def test_theme_property(self) -> None:
        """theme returns theme name."""
        window = StubWindow()
        window._theme = StubTheme("Light")

        result = get_window_property(window, "theme")
        assert result == "Light"

    def test_scale_factor_property(self) -> None:
        """scale_factor returns numeric value."""
        window = StubWindow()
        window._geometry.scale_factor = 1.5

        result = get_window_property(window, "scale_factor")
        assert result == 1.5

    def test_inner_position_returns_dict(self) -> None:
        """inner_position returns {x, y} dict."""
        window = StubWindow()
        window._geometry.inner_pos = StubPosition(150, 250)

        result = get_window_property(window, "inner_position")
        assert result == {"x": 150, "y": 250}

    def test_outer_position_returns_dict(self) -> None:
        """outer_position returns {x, y} dict."""
        window = StubWindow()
        window._geometry.outer_pos = StubPosition(145, 225)

        result = get_window_property(window, "outer_position")
        assert result == {"x": 145, "y": 225}

    def test_inner_size_returns_dict(self) -> None:
        """inner_size returns {width, height} dict."""
        window = StubWindow()
        window._geometry.inner_size = StubSize(1024, 768)

        result = get_window_property(window, "inner_size")
        assert result == {"width": 1024, "height": 768}

    def test_outer_size_returns_dict(self) -> None:
        """outer_size returns {width, height} dict."""
        window = StubWindow()
        window._geometry.outer_size = StubSize(1050, 800)

        result = get_window_property(window, "outer_size")
        assert result == {"width": 1050, "height": 800}

    def test_current_monitor_returns_serialized(self) -> None:
        """current_monitor returns serialized monitor data."""
        window = StubWindow()

        result = get_window_property(window, "current_monitor")
        assert isinstance(result, dict)
        assert result["name"] == "Current"
        assert result["size"] == {"width": 1920, "height": 1080}
        assert result["position"] == {"x": 0, "y": 0}
        assert result["scale_factor"] == 1.0

    def test_primary_monitor_returns_serialized(self) -> None:
        """primary_monitor returns serialized monitor data."""
        window = StubWindow()

        result = get_window_property(window, "primary_monitor")
        assert isinstance(result, dict)
        assert result["name"] == "Primary"
        assert result["size"] == {"width": 2560, "height": 1440}

    def test_available_monitors_returns_list(self) -> None:
        """available_monitors returns list of serialized monitors."""
        window = StubWindow()

        result = get_window_property(window, "available_monitors")
        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0]["name"] == "Primary"
        assert result[1]["name"] == "Current"

    def test_boolean_properties(self) -> None:
        """Boolean state properties return actual values."""
        window = StubWindow()
        window._visibility.visible = True
        window._visibility.maximized = False
        window._visibility.fullscreen = False
        window._capabilities.decorated = True

        assert get_window_property(window, "is_visible") is True
        assert get_window_property(window, "is_maximized") is False
        assert get_window_property(window, "is_fullscreen") is False
        assert get_window_property(window, "is_decorated") is True

    def test_unknown_property_raises(self) -> None:
        """Unknown property name raises ValueError."""
        window = StubWindow()

        with pytest.raises(ValueError, match="Unknown property"):
            get_window_property(window, "nonexistent_property")

    def test_monitor_from_point_raises(self) -> None:
        """monitor_from_point requires parameters, raises error."""
        window = StubWindow()

        with pytest.raises(ValueError, match="requires x, y parameters"):
            get_window_property(window, "monitor_from_point")


class TestSerializeMonitor:
    """Test monitor serialization helper."""

    def test_none_input(self) -> None:
        """None monitor returns None."""
        result = _serialize_monitor(None)
        assert result is None

    def test_full_monitor(self) -> None:
        """Full monitor is serialized correctly."""
        monitor = StubMonitor("Display 1", 2560, 1440, 100, 50, 2.0)

        result = _serialize_monitor(monitor)
        assert result == {
            "name": "Display 1",
            "position": {"x": 100, "y": 50},
            "size": {"width": 2560, "height": 1440},
            "scale_factor": 2.0,
        }


# =============================================================================
# Tests for call_window_method
# =============================================================================


class TestCallWindowMethodVisibility:
    """Test visibility method dispatch."""

    def test_show(self) -> None:
        """show() makes window visible."""
        window = StubWindow()
        window._visibility.visible = False

        call_window_method(window, "show", {})
        assert window._visibility.visible is True

    def test_hide(self) -> None:
        """hide() hides window."""
        window = StubWindow()
        window._visibility.visible = True

        call_window_method(window, "hide", {})
        assert window._visibility.visible is False

    def test_set_focus(self) -> None:
        """set_focus() sets focus."""
        window = StubWindow()

        call_window_method(window, "set_focus", {})
        assert window._visibility.focused is True

    def test_set_visible_true(self) -> None:
        """set_visible with visible=True calls show."""
        window = StubWindow()
        window._visibility.visible = False

        call_window_method(window, "set_visible", {"visible": True})
        assert window._visibility.visible is True

    def test_set_visible_false(self) -> None:
        """set_visible with visible=False calls hide."""
        window = StubWindow()
        window._visibility.visible = True

        call_window_method(window, "set_visible", {"visible": False})
        assert window._visibility.visible is False


class TestCallWindowMethodState:
    """Test window state method dispatch."""

    def test_minimize(self) -> None:
        """minimize() minimizes window."""
        window = StubWindow()

        call_window_method(window, "minimize", {})
        assert window._visibility.minimized is True

    def test_unminimize(self) -> None:
        """unminimize() restores window."""
        window = StubWindow()
        window._visibility.minimized = True

        call_window_method(window, "unminimize", {})
        assert window._visibility.minimized is False

    def test_maximize(self) -> None:
        """maximize() maximizes window."""
        window = StubWindow()

        call_window_method(window, "maximize", {})
        assert window._visibility.maximized is True

    def test_unmaximize(self) -> None:
        """unmaximize() restores window."""
        window = StubWindow()
        window._visibility.maximized = True

        call_window_method(window, "unmaximize", {})
        assert window._visibility.maximized is False

    def test_toggle_maximize(self) -> None:
        """toggle_maximize() toggles state."""
        window = StubWindow()
        window._visibility.maximized = False

        call_window_method(window, "toggle_maximize", {})
        assert window._visibility.maximized is True

        call_window_method(window, "toggle_maximize", {})
        assert window._visibility.maximized is False

    def test_set_fullscreen(self) -> None:
        """set_fullscreen() sets fullscreen state."""
        window = StubWindow()

        call_window_method(window, "set_fullscreen", {"fullscreen": True})
        assert window._visibility.fullscreen is True

        call_window_method(window, "set_fullscreen", {"fullscreen": False})
        assert window._visibility.fullscreen is False


class TestCallWindowMethodPropertySetters:
    """Test property setter method dispatch."""

    def test_set_title(self) -> None:
        """set_title() changes title."""
        window = StubWindow()

        call_window_method(window, "set_title", {"title": "New Title"})
        assert window._title == "New Title"

    def test_set_decorations(self) -> None:
        """set_decorations() changes decoration state."""
        window = StubWindow()
        window._capabilities.decorated = True

        call_window_method(window, "set_decorations", {"decorations": False})
        assert window._capabilities.decorated is False

    def test_set_resizable(self) -> None:
        """set_resizable() changes resizable state."""
        window = StubWindow()
        window._capabilities.resizable = True

        call_window_method(window, "set_resizable", {"resizable": False})
        assert window._capabilities.resizable is False

    def test_set_always_on_top(self) -> None:
        """set_always_on_top() changes always-on-top state."""
        window = StubWindow()

        call_window_method(window, "set_always_on_top", {"always_on_top": True})
        assert window._capabilities.always_on_top is True


class TestCallWindowMethodSizePosition:
    """Test size/position method dispatch."""

    def test_set_size(self) -> None:
        """set_size() changes window size."""
        window = StubWindow()

        call_window_method(window, "set_size", {"width": 1024, "height": 768})
        assert window._geometry.inner_size.width == 1024
        assert window._geometry.inner_size.height == 768

    def test_set_position(self) -> None:
        """set_position() changes window position."""
        window = StubWindow()

        call_window_method(window, "set_position", {"x": 200, "y": 150})
        assert window._geometry.inner_pos.x == 200
        assert window._geometry.inner_pos.y == 150


class TestCallWindowMethodWebview:
    """Test webview method dispatch."""

    def test_navigate(self) -> None:
        """navigate() changes URL."""
        window = StubWindow()

        call_window_method(window, "navigate", {"url": "https://new.com"})
        assert window._url == "https://new.com"

    def test_eval(self) -> None:
        """eval() executes script."""
        window = StubWindow()

        call_window_method(window, "eval", {"script": "console.log('test')"})
        assert ("eval", ("console.log('test')",)) in window._calls

    def test_open_devtools(self) -> None:
        """open_devtools() opens developer tools."""
        window = StubWindow()

        call_window_method(window, "open_devtools", {})
        assert window._devtools_open is True

    def test_close_devtools(self) -> None:
        """close_devtools() closes developer tools."""
        window = StubWindow()
        window._devtools_open = True

        call_window_method(window, "close_devtools", {})
        assert window._devtools_open is False

    def test_reload(self) -> None:
        """reload() reloads page."""
        window = StubWindow()

        call_window_method(window, "reload", {})
        assert ("reload", ()) in window._calls


class TestCallWindowMethodUnknown:
    """Test error handling for unknown methods."""

    def test_unknown_method_raises(self) -> None:
        """Unknown method name raises ValueError."""
        window = StubWindow()

        with pytest.raises(ValueError, match="Unknown method"):
            call_window_method(window, "nonexistent_method", {})


class TestDispatchTableCompleteness:
    """Verify dispatch tables are complete and well-formed."""

    def test_property_getters_all_callable(self) -> None:
        """All property getters are callable."""
        for prop_name, getter in PROPERTY_GETTERS.items():
            assert callable(getter), f"Getter for {prop_name} is not callable"

    def test_method_categories_non_overlapping(self) -> None:
        """Method categories don't overlap."""
        all_methods = [
            VISIBILITY_METHODS,
            STATE_METHODS,
            PROPERTY_METHODS,
            SIZE_POSITION_METHODS,
            APPEARANCE_METHODS,
            CURSOR_METHODS,
            BEHAVIOR_METHODS,
            WEBVIEW_METHODS,
            COOKIE_METHODS,
        ]

        seen: set[str] = set()
        for category in all_methods:
            for method in category:
                assert method not in seen, f"Method {method} appears in multiple categories"
                seen.add(method)

    def test_method_categories_non_empty(self) -> None:
        """All method categories have at least one method."""
        assert len(VISIBILITY_METHODS) > 0
        assert len(STATE_METHODS) > 0
        assert len(PROPERTY_METHODS) > 0
        assert len(SIZE_POSITION_METHODS) > 0
        assert len(APPEARANCE_METHODS) > 0
        assert len(CURSOR_METHODS) > 0
        assert len(BEHAVIOR_METHODS) > 0
        assert len(WEBVIEW_METHODS) > 0
        assert len(COOKIE_METHODS) > 0
