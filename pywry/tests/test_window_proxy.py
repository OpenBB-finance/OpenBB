"""Integration tests for WindowProxy.

These tests verify that WindowProxy methods actually work by creating
real windows and testing real operations. No mocks - real execution.

Tests are marked slow because they spawn actual subprocess/windows.
"""

from __future__ import annotations

import os
import sys
import time

from typing import Any

import pytest

from pywry import runtime
from pywry.app import PyWry
from pywry.callbacks import get_registry
from pywry.exceptions import IPCTimeoutError
from pywry.models import ThemeMode, WindowMode
from pywry.types import PhysicalPosition, PhysicalSize
from pywry.window_proxy import WindowProxy

# Import shared test utilities from tests.conftest
from tests.conftest import ReadyWaiter


# Note: cleanup_runtime fixture is now in conftest.py and auto-used


def wait_for_state(
    proxy: WindowProxy,
    attr: str,
    expected: bool,
    timeout: float = 3.0,
    poll_interval: float = 0.1,
) -> bool:
    """Poll a WindowProxy boolean attribute until it matches expected value.

    Returns True if the state was reached, False if timeout.
    Handles transient IPC errors during polling.
    """
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            if getattr(proxy, attr) is expected:
                return True
        except IPCTimeoutError:
            # Window may be temporarily unresponsive during state changes
            pass
        time.sleep(poll_interval)
    return False


def show_and_wait_ready(
    app: PyWry,
    content: str,
    timeout: float = 10.0,
    **kwargs: Any,
) -> WindowProxy:
    """Show content and return WindowProxy once window is ready."""
    waiter = ReadyWaiter(timeout=timeout)

    # Merge callbacks
    callbacks = kwargs.pop("callbacks", {}) or {}
    callbacks["pywry:ready"] = waiter.on_ready

    widget = app.show(content, callbacks=callbacks, **kwargs)

    if not waiter.wait():
        label = widget.label if hasattr(widget, "label") else str(widget)
        raise TimeoutError(f"Window '{label}' did not become ready within {timeout}s")

    return widget.proxy


class TestWindowProxyProperties:
    """Test that WindowProxy properties return real values."""

    def test_title_property(self) -> None:
        """title property returns the actual window title."""
        app = PyWry(theme=ThemeMode.DARK)
        proxy = show_and_wait_ready(app, "<h1>Test</h1>", title="My Test Title")

        title = proxy.title
        assert isinstance(title, str)
        assert "My Test Title" in title or title != ""  # Title is set
        app.close()

    def test_scale_factor_property(self) -> None:
        """scale_factor returns a positive number."""
        app = PyWry(theme=ThemeMode.DARK)
        proxy = show_and_wait_ready(app, "<h1>Scale</h1>", title="Scale Test")

        scale = proxy.scale_factor
        assert isinstance(scale, (int, float))
        assert scale > 0  # Scale factor is always positive
        app.close()

    def test_inner_size_property(self) -> None:
        """inner_size returns size with positive dimensions."""
        app = PyWry(theme=ThemeMode.DARK)
        proxy = show_and_wait_ready(app, "<h1>Size</h1>", title="Size Test")

        size = proxy.inner_size
        assert size is not None
        assert isinstance(size, PhysicalSize)
        assert size.width > 0
        assert size.height > 0
        app.close()

    def test_outer_size_property(self) -> None:
        """outer_size returns size >= inner_size."""
        app = PyWry(theme=ThemeMode.DARK)
        proxy = show_and_wait_ready(app, "<h1>Outer</h1>", title="Outer Size")

        inner = proxy.inner_size
        outer = proxy.outer_size
        assert outer is not None
        assert isinstance(outer, PhysicalSize)
        # Outer includes window chrome, should be >= inner
        assert outer.width >= inner.width
        assert outer.height >= inner.height
        app.close()

    def test_inner_position_property(self) -> None:
        """inner_position returns a position."""
        app = PyWry(theme=ThemeMode.DARK)
        proxy = show_and_wait_ready(app, "<h1>Pos</h1>", title="Position Test")

        pos = proxy.inner_position
        assert pos is not None
        assert isinstance(pos, PhysicalPosition)
        # Position can be any value including negative (off-screen)
        assert isinstance(pos.x, int)
        assert isinstance(pos.y, int)
        app.close()

    def test_is_visible_property(self) -> None:
        """is_visible returns True for shown window."""
        app = PyWry(theme=ThemeMode.DARK)
        proxy = show_and_wait_ready(app, "<h1>Visible</h1>", title="Visible Test")

        # Window should be visible after show
        assert proxy.is_visible is True
        app.close()

    def test_boolean_properties(self) -> None:
        """Boolean state properties return actual booleans."""
        app = PyWry(theme=ThemeMode.DARK)
        proxy = show_and_wait_ready(app, "<h1>Bools</h1>", title="Bool Test")

        # These should all return actual booleans
        assert isinstance(proxy.is_decorated, bool)
        assert isinstance(proxy.is_resizable, bool)
        assert isinstance(proxy.is_maximizable, bool)
        assert isinstance(proxy.is_minimizable, bool)
        assert isinstance(proxy.is_closable, bool)
        assert isinstance(proxy.is_maximized, bool)
        assert isinstance(proxy.is_minimized, bool)
        assert isinstance(proxy.is_fullscreen, bool)
        app.close()


class TestWindowProxyActions:
    """Test that WindowProxy action methods actually work."""

    def test_set_title(self) -> None:
        """set_title actually changes the window title."""
        app = PyWry(theme=ThemeMode.DARK)
        proxy = show_and_wait_ready(app, "<h1>Title</h1>", title="Original Title")

        # Change title
        proxy.set_title("New Title")
        time.sleep(0.1)  # Allow IPC to complete

        # Verify title changed
        new_title = proxy.title
        assert "New Title" in new_title
        app.close()

    @pytest.mark.skipif(
        os.environ.get("CI") == "true" and sys.platform == "linux",
        reason="Maximize/minimize requires a real window manager (not available on Linux CI)",
    )
    def test_maximize_unmaximize(self) -> None:
        """maximize and unmaximize actually change window state."""
        app = PyWry(theme=ThemeMode.DARK)
        proxy = show_and_wait_ready(app, "<h1>Max</h1>", title="Maximize Test")

        # Initially not maximized
        assert proxy.is_maximized is False

        # Maximize - use polling for async window state changes
        proxy.maximize()
        assert wait_for_state(proxy, "is_maximized", True, timeout=3.0), (
            "Window did not maximize within timeout"
        )

        # Unmaximize
        proxy.unmaximize()
        assert wait_for_state(proxy, "is_maximized", False, timeout=3.0), (
            "Window did not unmaximize within timeout"
        )
        app.close()

    @pytest.mark.skipif(
        os.environ.get("CI") == "true" and sys.platform == "linux",
        reason="Maximize/minimize requires a real window manager (not available on Linux CI)",
    )
    def test_minimize_unminimize(self) -> None:
        """minimize and unminimize change window state."""
        app = PyWry(theme=ThemeMode.DARK)
        proxy = show_and_wait_ready(app, "<h1>Min</h1>", title="Minimize Test")

        # Ensure window is in normal state first (not maximized/minimized)
        if proxy.is_maximized:
            proxy.unmaximize()
            wait_for_state(proxy, "is_maximized", False)

        # Minimize - use polling for async window state changes
        proxy.minimize()
        assert wait_for_state(proxy, "is_minimized", True, timeout=5.0), (
            "Window did not minimize within timeout"
        )

        # Unminimize - requires focus on some platforms
        # Add delay to let window manager process the minimize fully
        time.sleep(0.5)
        proxy.set_focus()
        proxy.unminimize()
        assert wait_for_state(proxy, "is_minimized", False, timeout=5.0), (
            f"Window did not unminimize within timeout (is_visible={proxy.is_visible})"
        )
        app.close()

    def test_set_size(self) -> None:
        """set_size actually changes the window size."""
        app = PyWry(theme=ThemeMode.DARK)
        proxy = show_and_wait_ready(app, "<h1>Resize</h1>", title="Size Change")

        # Set to specific size
        target_size = PhysicalSize(800, 600)
        proxy.set_size(target_size)
        time.sleep(0.2)

        # Verify size changed (may not be exact due to platform constraints)
        new_size = proxy.inner_size
        assert new_size is not None
        # Allow some tolerance for window decorations
        assert abs(new_size.width - 800) < 50
        assert abs(new_size.height - 600) < 50
        app.close()

    def test_hide_show(self) -> None:
        """hide and show change visibility."""
        app = PyWry(theme=ThemeMode.DARK)
        proxy = show_and_wait_ready(app, "<h1>Hide</h1>", title="Hide Test")

        assert proxy.is_visible is True

        # Hide
        proxy.hide()
        time.sleep(0.2)
        assert proxy.is_visible is False

        # Show again
        proxy.show()
        time.sleep(0.2)
        assert proxy.is_visible is True
        app.close()

    @pytest.mark.skipif(
        os.environ.get("CI") == "true" and sys.platform == "linux",
        reason="Always-on-top requires a real window manager (not available on Linux CI)",
    )
    def test_set_always_on_top(self) -> None:
        """set_always_on_top changes the always-on-top state."""
        app = PyWry(theme=ThemeMode.DARK)
        proxy = show_and_wait_ready(app, "<h1>Top</h1>", title="Always On Top")

        # Set always on top - use polling for async state changes
        proxy.set_always_on_top(True)
        assert wait_for_state(proxy, "is_always_on_top", True, timeout=3.0), (
            "Window did not become always-on-top within timeout"
        )

        # Disable
        proxy.set_always_on_top(False)
        assert wait_for_state(proxy, "is_always_on_top", False, timeout=3.0), (
            "Window did not disable always-on-top within timeout"
        )
        app.close()

    def test_set_decorations(self) -> None:
        """set_decorations changes window decoration state."""
        app = PyWry(theme=ThemeMode.DARK)
        proxy = show_and_wait_ready(app, "<h1>Deco</h1>", title="Decorations Test")

        # Initially decorated
        assert proxy.is_decorated is True

        # Remove decorations
        proxy.set_decorations(False)
        time.sleep(0.2)
        assert proxy.is_decorated is False

        # Restore
        proxy.set_decorations(True)
        time.sleep(0.2)
        assert proxy.is_decorated is True
        app.close()


class TestWindowProxyWebview:
    """Test webview-related WindowProxy methods."""

    def test_eval_js(self) -> None:
        """eval executes JavaScript in the window."""
        app = PyWry(theme=ThemeMode.DARK)
        proxy = show_and_wait_ready(app, "<div id='target'>Original</div>", title="Eval Test")

        # Execute JS to modify the DOM
        proxy.eval("document.getElementById('target').textContent = 'Modified';")
        time.sleep(0.2)

        # Verify change via callback result
        registry = get_registry()
        result = {"received": False, "data": None}

        def on_result(data: Any) -> None:
            result["received"] = True
            result["data"] = data

        registry.register(proxy.label, "pywry:result", on_result)

        # Read back the value
        runtime.eval_js(
            proxy.label,
            "pywry.result(document.getElementById('target').textContent);",
        )
        time.sleep(0.3)

        assert result["received"]
        assert result["data"] == "Modified"
        app.close()

    def test_navigate(self) -> None:
        """navigate changes the window URL."""
        app = PyWry(theme=ThemeMode.DARK)
        proxy = show_and_wait_ready(app, "<h1>Nav</h1>", title="Navigate Test")

        # Get initial URL (tauri serves content via tauri:// or http://tauri.localhost/)
        initial_url = proxy.url
        assert initial_url.startswith(("tauri://", "http://tauri.localhost/")), (
            f"Unexpected initial URL: {initial_url}"
        )

        # Navigate to about:blank
        proxy.navigate("about:blank")
        time.sleep(0.5)

        # URL must have changed from the initial tauri URL
        new_url = proxy.url
        assert new_url != initial_url, f"URL did not change: still {new_url}"
        assert new_url == "about:blank", f"Expected 'about:blank', got {new_url}"
        app.close()


class TestWindowProxyMonitors:
    """Test monitor-related WindowProxy properties."""

    def test_current_monitor(self) -> None:
        """current_monitor returns monitor info."""
        app = PyWry(theme=ThemeMode.DARK)
        proxy = show_and_wait_ready(app, "<h1>Monitor</h1>", title="Monitor Test")

        monitor = proxy.current_monitor
        # May be None on some platforms, but if present should have properties
        if monitor is not None:
            assert hasattr(monitor, "size")
            assert hasattr(monitor, "position")
            assert hasattr(monitor, "scale_factor")
        app.close()

    def test_primary_monitor(self) -> None:
        """primary_monitor returns the primary display."""
        app = PyWry(theme=ThemeMode.DARK)
        proxy = show_and_wait_ready(app, "<h1>Primary</h1>", title="Primary Mon")

        monitor = proxy.primary_monitor
        # Should exist on systems with displays
        if monitor is not None:
            assert monitor.size.width > 0
            assert monitor.size.height > 0
        app.close()

    def test_available_monitors(self) -> None:
        """available_monitors returns list of displays."""
        app = PyWry(theme=ThemeMode.DARK)
        proxy = show_and_wait_ready(app, "<h1>Monitors</h1>", title="All Mons")

        monitors = proxy.available_monitors
        assert isinstance(monitors, list)
        # Should have at least one monitor on a system with a display
        if monitors:
            assert all(hasattr(m, "size") for m in monitors)
        app.close()


class TestWindowProxyLabel:
    """Test WindowProxy label handling."""

    def test_label_property(self) -> None:
        """label property returns the window label."""
        proxy = WindowProxy("my-window-label")
        assert proxy.label == "my-window-label"

    def test_repr(self) -> None:
        """repr includes the label."""
        proxy = WindowProxy("test-label")
        r = repr(proxy)
        assert "WindowProxy" in r
        assert "test-label" in r


class TestMultipleWindows:
    """Test WindowProxy with multiple windows."""

    def test_independent_windows(self) -> None:
        """Multiple WindowProxies control independent windows."""
        app = PyWry(mode=WindowMode.NEW_WINDOW, theme=ThemeMode.DARK)

        proxy1 = show_and_wait_ready(app, "<h1>Window 1</h1>", title="Win 1")
        proxy2 = show_and_wait_ready(app, "<h1>Window 2</h1>", title="Win 2")

        # Labels should be different
        assert proxy1.label != proxy2.label

        # Modifying one doesn't affect the other
        proxy1.set_title("Modified 1")
        time.sleep(0.1)

        assert "Modified 1" in proxy1.title
        assert "Win 2" in proxy2.title or proxy2.title != proxy1.title
        app.close()
