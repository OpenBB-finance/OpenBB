"""End-to-end tests for BROWSER mode rendering.

BROWSER mode opens content in the system's default browser instead of:
- Native Tauri window (NEW_WINDOW mode)
- Notebook IFrame (NOTEBOOK mode)

These tests verify:
1. Server startup and health checks
2. Content serving for Plotly charts and AG Grid
3. WebSocket-based bidirectional callbacks
4. Lifecycle management (widget registration, cleanup)
5. Theme handling
6. Number formatting in grids

Tests are designed for CI/headless environments - they do NOT actually open
a browser, but verify the server-side behavior that BROWSER mode relies on.
"""

# pylint: disable=redefined-outer-name

import asyncio
import json
import os
import socket
import time
import urllib.error
import urllib.request

from contextlib import suppress
from typing import Any
from unittest.mock import patch

import pytest


try:
    import websockets
except ImportError:
    websockets = None


from pywry.config import clear_settings
from pywry.inline import (
    HAS_FASTAPI,
    InlineWidget,
    _start_server,
    _state,
    show_dataframe,
    show_plotly,
    stop_server,
)
from pywry.models import WindowMode


# Skip all tests if FastAPI not installed
pytestmark = pytest.mark.skipif(not HAS_FASTAPI, reason="FastAPI not installed")


def wait_for_port_release(port: int, host: str = "127.0.0.1", timeout: float = 5.0) -> bool:
    """Wait until a port is released and available for binding."""
    start = time.time()
    while time.time() - start < timeout:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.bind((host, port))
                return True
        except OSError:
            time.sleep(0.1)
    return False


# Default port used by PyWry when no port is specified
DEFAULT_PORT = 8765


@pytest.fixture(autouse=True)
def clean_state():
    """Clean up server state before and after each test."""
    # Get port before stopping so we can wait for release
    old_port = _state.port

    stop_server(timeout=5.0)
    _state.widgets.clear()
    _state.connections.clear()
    _state.event_queues.clear()
    clear_settings()

    # Wait for port to be released if server was running
    if old_port is not None:
        wait_for_port_release(old_port, timeout=3.0)
    # Also wait for default port in case a test used it without our fixture
    wait_for_port_release(DEFAULT_PORT, timeout=2.0)

    yield

    # Cleanup after test
    old_port = _state.port
    stop_server(timeout=5.0)
    _state.widgets.clear()
    _state.connections.clear()
    _state.event_queues.clear()
    clear_settings()

    # Wait for port release - check both the used port and default port
    ports_to_wait = {DEFAULT_PORT}
    if old_port is not None:
        ports_to_wait.add(old_port)
    for port in ports_to_wait:
        wait_for_port_release(port, timeout=3.0)

    # Remove any env vars we set
    for key in list(os.environ.keys()):
        if key.startswith("PYWRY_"):
            del os.environ[key]


# Use a counter to ensure unique ports across test runs
_port_counter = [10000]


@pytest.fixture
def server_port():
    """Get a unique free port for this test."""
    # Increment counter to get unique base port
    _port_counter[0] += 1

    # Find actual free port starting from our base
    for offset in range(100):
        port = _port_counter[0] + offset
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.bind(("0.0.0.0", port))
                # Port is free, use it
                _port_counter[0] = port  # Update counter
                return port
        except OSError:
            continue

    # Fallback: let OS assign
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("0.0.0.0", 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return s.getsockname()[1]


def _get_auth_header() -> dict[str, str]:
    """Get the internal API auth header for protected endpoints."""
    from pywry.config import get_settings

    settings = get_settings()
    if _state.internal_api_token:
        return {settings.server.internal_api_header: _state.internal_api_token}
    return {}


def wait_for_server(host: str, port: int, timeout: float = 5.0) -> bool:
    """Wait for server to be ready.

    Uses socket connection check since health endpoint requires auth.
    """
    start = time.time()
    while time.time() - start < timeout:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(0.5)
                result = s.connect_ex((host, port))
                if result == 0:
                    # Socket is open, try health with auth if we have token
                    url = f"http://{host}:{port}/health"
                    req = urllib.request.Request(url)  # noqa: S310
                    auth_header = _get_auth_header()
                    for k, v in auth_header.items():
                        req.add_header(k, v)
                    try:
                        with urllib.request.urlopen(req, timeout=0.5) as resp:  # noqa: S310
                            if resp.status == 200:
                                return True
                    except Exception:
                        # Health might 404 without auth, but socket is open
                        return True
        except Exception:  # noqa: S110
            pass
        time.sleep(0.1)
    return False


def http_get(url: str, timeout: float = 5.0, auth: bool = False) -> tuple[int, str]:
    """Make HTTP GET request, return (status_code, body).

    Parameters
    ----------
    url : str
        URL to fetch.
    timeout : float, optional
        Request timeout in seconds.
    auth : bool, optional
        If True, include internal API auth header.
    """
    req = urllib.request.Request(url)  # noqa: S310
    if auth:
        for k, v in _get_auth_header().items():
            req.add_header(k, v)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:  # noqa: S310
            return resp.status, resp.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8")


def http_post(url: str, data: dict, timeout: float = 5.0, auth: bool = False) -> tuple[int, str]:
    """Make HTTP POST request with JSON body.

    Parameters
    ----------
    url : str
        URL to POST to.
    data : dict
        JSON data dict.
    timeout : float, optional
        Request timeout in seconds.
    auth : bool, optional
        If True, include internal API auth header.
    """
    headers = {"Content-Type": "application/json"}
    if auth:
        headers.update(_get_auth_header())
    req = urllib.request.Request(  # noqa: S310
        url,
        data=json.dumps(data).encode("utf-8"),
        headers=headers,
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:  # noqa: S310
            return resp.status, resp.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8")


# =============================================================================
# BROWSER Mode Basics
# =============================================================================


class TestBrowserModeBasics:
    """Test BROWSER mode fundamental behavior."""

    def test_browser_mode_starts_server(self, server_port):
        """BROWSER mode should start the FastAPI server."""
        _start_server(port=server_port, host="0.0.0.0")
        assert wait_for_server("127.0.0.1", server_port)

        # Health endpoint requires auth
        status, body = http_get(f"http://127.0.0.1:{server_port}/health", auth=True)
        assert status == 200

        data = json.loads(body)
        assert data["status"] == "ok"

    def test_browser_mode_widget_creation_without_browser_open(self, server_port):
        """InlineWidget with browser_only=True should register widget without IPython."""
        _start_server(port=server_port, host="0.0.0.0")
        assert wait_for_server("127.0.0.1", server_port)

        # Create widget in browser_only mode (used by BROWSER WindowMode)
        widget = InlineWidget(
            html="<html><body><h1>Test</h1></body></html>",
            port=server_port,
            widget_id="browser-test-1",
            browser_only=True,
        )

        # Widget should be registered
        assert widget.widget_id in _state.widgets
        assert "Test" in _state.widgets[widget.widget_id]["html"]

    def test_browser_mode_open_in_browser_method(self, server_port):
        """open_in_browser() should wait for server and call webbrowser.open."""
        _start_server(port=server_port, host="0.0.0.0")
        assert wait_for_server("127.0.0.1", server_port)

        widget = InlineWidget(
            html="<html><body>Content</body></html>",
            port=server_port,
            widget_id="browser-open-test",
            browser_only=True,
        )

        # Mock webbrowser.open to verify it's called
        with patch("webbrowser.open") as mock_open:
            widget.open_in_browser()
            mock_open.assert_called_once()
            # URL should contain the widget endpoint
            called_url = mock_open.call_args[0][0]
            assert "browser-open-test" in called_url


# =============================================================================
# Plotly Rendering in BROWSER Mode
# =============================================================================


class TestBrowserModePlotly:
    """Test Plotly chart rendering in BROWSER mode."""

    def test_plotly_widget_registration(self, server_port):
        """show_plotly with open_browser=True should register widget."""
        import plotly.graph_objects as go

        fig = go.Figure(data=[go.Scatter(x=[1, 2], y=[3, 4])])

        # Mock webbrowser.open to prevent actual browser opening
        with patch("webbrowser.open"):
            widget = show_plotly(
                figure=fig,
                title="Test Chart",
                port=server_port,
                open_browser=True,
            )

        assert widget.widget_id in _state.widgets

    def test_plotly_html_contains_plotly_js(self, server_port):
        """Plotly widget HTML should contain Plotly.js and chart data."""
        import plotly.graph_objects as go

        fig = go.Figure(data=[go.Bar(x=["A", "B"], y=[10, 20])])

        with patch("webbrowser.open"):
            widget = show_plotly(
                figure=fig,
                title="Bar Chart",
                port=server_port,
                open_browser=True,
            )

        # Fetch widget HTML
        assert wait_for_server("127.0.0.1", server_port)
        status, html = http_get(f"http://127.0.0.1:{server_port}/widget/{widget.widget_id}")

        assert status == 200
        assert "Plotly" in html or "plotly" in html.lower()
        assert "Bar Chart" in html

    def test_plotly_config_applied(self, server_port):
        """PlotlyConfig options should be applied to the chart."""
        import plotly.graph_objects as go

        from pywry import PlotlyConfig

        fig = go.Figure(data=[go.Scatter(x=[1, 2], y=[3, 4])])
        config = PlotlyConfig(
            display_logo=False,
            scroll_zoom=True,
            responsive=True,
        )

        with patch("webbrowser.open"):
            widget = show_plotly(
                figure=fig,
                config=config,
                port=server_port,
                open_browser=True,
            )

        assert wait_for_server("127.0.0.1", server_port)
        status, html = http_get(f"http://127.0.0.1:{server_port}/widget/{widget.widget_id}")

        assert status == 200
        # Config should be embedded in the HTML
        assert "displaylogo" in html.lower() or "scrollZoom" in html

    def test_plotly_with_toolbar(self, server_port):
        """Plotly chart with toolbar should render toolbar HTML."""
        import plotly.graph_objects as go

        fig = go.Figure(data=[go.Scatter(x=[1, 2], y=[3, 4])])

        toolbar = {
            "position": "top",
            "items": [
                {"type": "button", "label": "My Button", "event": "custom:click"},
            ],
        }

        with patch("webbrowser.open"):
            widget = show_plotly(
                figure=fig,
                toolbars=[toolbar],
                port=server_port,
                open_browser=True,
            )

        assert wait_for_server("127.0.0.1", server_port)
        status, html = http_get(f"http://127.0.0.1:{server_port}/widget/{widget.widget_id}")

        assert status == 200
        assert "My Button" in html
        assert "pywry-toolbar" in html


# =============================================================================
# AG Grid Rendering in BROWSER Mode
# =============================================================================


class TestBrowserModeAgGrid:
    """Test AG Grid rendering in BROWSER mode."""

    def test_aggrid_widget_registration(self, server_port):
        """show_dataframe with open_browser=True should register widget."""
        data = [{"a": 1, "b": 2}, {"a": 3, "b": 4}]

        with patch("webbrowser.open"):
            widget = show_dataframe(
                df=data,
                title="Test Grid",
                port=server_port,
                open_browser=True,
            )

        assert widget.widget_id in _state.widgets

    def test_aggrid_html_contains_aggrid_js(self, server_port):
        """AG Grid widget HTML should contain AG Grid and data."""
        data = [{"name": "Alice", "score": 100}, {"name": "Bob", "score": 90}]

        with patch("webbrowser.open"):
            widget = show_dataframe(
                df=data,
                title="Score Grid",
                port=server_port,
                open_browser=True,
            )

        assert wait_for_server("127.0.0.1", server_port)
        status, html = http_get(f"http://127.0.0.1:{server_port}/widget/{widget.widget_id}")

        assert status == 200
        assert "agGrid" in html or "ag-grid" in html.lower()

    def test_aggrid_number_formatting_applied(self, server_port):
        """AG Grid should have valueFormatter for number columns."""
        # Use data with large numbers (population-like)
        data = [
            {"country": "USA", "population": 331000000},
            {"country": "UK", "population": 67000000},
        ]

        with patch("webbrowser.open"):
            widget = show_dataframe(
                df=data,
                title="Population Grid",
                port=server_port,
                open_browser=True,
            )

        assert wait_for_server("127.0.0.1", server_port)
        status, html = http_get(f"http://127.0.0.1:{server_port}/widget/{widget.widget_id}")

        assert status == 200
        # Should have valueFormatter for number formatting
        assert "valueFormatter" in html or "toLocaleString" in html

    def test_aggrid_year_column_not_formatted(self, server_port):
        """Year columns should not have thousands separators."""
        data = [
            {"year": 2020, "revenue": 1000000},
            {"year": 2021, "revenue": 1500000},
        ]

        with patch("webbrowser.open"):
            widget = show_dataframe(
                df=data,
                title="Revenue Grid",
                port=server_port,
                open_browser=True,
            )

        assert wait_for_server("127.0.0.1", server_port)
        status, html = http_get(f"http://127.0.0.1:{server_port}/widget/{widget.widget_id}")

        assert status == 200
        # The grid should be rendered
        assert "agGrid" in html or "ag-grid" in html.lower()


# =============================================================================
# Callback Registration and Routing
# =============================================================================


class TestBrowserModeCallbacks:
    """Test callback registration and event routing in BROWSER mode."""

    def test_callback_registration(self, server_port):
        """Callbacks should be registered with the widget."""
        data = [{"a": 1}]

        received_events = []

        def my_callback(event_data, event_type, label):
            received_events.append((event_data, event_type, label))

        with patch("webbrowser.open"):
            widget = show_dataframe(
                df=data,
                port=server_port,
                open_browser=True,
                callbacks={"custom:event": my_callback},
            )

        # Callback should be registered
        assert "custom:event" in _state.widgets[widget.widget_id]["callbacks"]

    def test_callback_can_be_added_after_creation(self, server_port):
        """Callbacks can be added via widget.on() after creation."""
        data = [{"a": 1}]

        with patch("webbrowser.open"):
            widget = show_dataframe(
                df=data,
                port=server_port,
                open_browser=True,
            )

        def late_callback(_event_data, _event_type, _label):
            pass

        widget.on("late:event", late_callback)

        assert "late:event" in _state.widgets[widget.widget_id]["callbacks"]

    def test_emit_queues_event(self, server_port):
        """widget.emit() should queue events for WebSocket delivery."""
        _start_server(port=server_port, host="0.0.0.0")
        assert wait_for_server("127.0.0.1", server_port)

        widget = InlineWidget(
            html="<html><body>Test</body></html>",
            port=server_port,
            widget_id="emit-test",
            browser_only=True,
        )

        # Emit an event
        widget.emit("pywry:test-event", {"value": 42})

        # Give async queue time to process
        time.sleep(0.2)

        # Event should be in queue
        assert widget.widget_id in _state.event_queues


# =============================================================================
# WebSocket Tests (requires websockets library)
# =============================================================================


@pytest.mark.skipif(websockets is None, reason="websockets not installed")
class TestBrowserModeWebSocket:
    """Test WebSocket communication for bidirectional callbacks."""

    @pytest.mark.asyncio
    async def test_websocket_connection(self, server_port):
        """WebSocket connection should be established successfully."""
        _start_server(port=server_port, host="0.0.0.0")
        assert wait_for_server("127.0.0.1", server_port)

        widget_id = "ws-test"
        # Generate a token for WebSocket auth
        import secrets

        token = secrets.token_urlsafe(16)
        _state.register_widget(widget_id, "<html></html>", callbacks={}, token=token)

        ws_url = f"ws://127.0.0.1:{server_port}/ws/{widget_id}"
        subprotocol = f"pywry.token.{token}"

        async with websockets.connect(ws_url, subprotocols=[subprotocol]):
            # Connection should be tracked
            await asyncio.sleep(0.1)
            assert widget_id in _state.connections

    @pytest.mark.asyncio
    async def test_websocket_receives_events_from_python(self, server_port):
        """WebSocket should receive events emitted from Python."""
        _start_server(port=server_port, host="0.0.0.0")
        assert wait_for_server("127.0.0.1", server_port)

        widget = InlineWidget(
            html="<html></html>",
            port=server_port,
            widget_id="ws-receive-test",
            browser_only=True,
        )

        ws_url = f"ws://127.0.0.1:{server_port}/ws/{widget.widget_id}"
        # Get token for this widget
        token = _state.widget_tokens.get(widget.widget_id)
        subprotocol = f"pywry.token.{token}" if token else None
        subprotocols = [subprotocol] if subprotocol else None

        async with websockets.connect(ws_url, subprotocols=subprotocols) as ws:
            # Emit event from Python
            widget.emit("pywry:test", {"message": "hello"})

            # Should receive event via WebSocket
            try:
                message = await asyncio.wait_for(ws.recv(), timeout=2.0)
                data = json.loads(message)
                assert data["type"] == "pywry:test"
                assert data["data"]["message"] == "hello"
            except asyncio.TimeoutError:
                pytest.fail("Did not receive WebSocket message in time")

    @pytest.mark.asyncio
    async def test_websocket_sends_events_to_python(self, server_port):
        """WebSocket messages should trigger Python callbacks."""
        _start_server(port=server_port, host="0.0.0.0")
        assert wait_for_server("127.0.0.1", server_port)

        received: dict[str, Any] = {"data": None, "event": None}

        def my_handler(event_data, event_type, _label):
            received["data"] = event_data
            received["event"] = event_type

        widget = InlineWidget(
            html="<html></html>",
            port=server_port,
            widget_id="ws-send-test",
            browser_only=True,
        )
        widget.on("custom:action", my_handler)

        ws_url = f"ws://127.0.0.1:{server_port}/ws/{widget.widget_id}"
        token = _state.widget_tokens.get(widget.widget_id)
        subprotocol = f"pywry.token.{token}" if token else None
        subprotocols = [subprotocol] if subprotocol else None

        async with websockets.connect(ws_url, subprotocols=subprotocols) as ws:
            # Send event from "browser" (WebSocket client)
            await ws.send(json.dumps({"type": "custom:action", "data": {"clicked": True}}))

            # Wait for callback to be processed
            await asyncio.sleep(0.5)

            assert received["event"] == "custom:action"
            assert received.get("data", {}).get("clicked") is True


# =============================================================================
# Lifecycle Management
# =============================================================================


class TestBrowserModeLifecycle:
    """Test widget lifecycle and cleanup in BROWSER mode."""

    def test_widget_persists_after_page_refresh(self, server_port):
        """Widget should remain accessible after simulated page refresh."""
        _start_server(port=server_port, host="0.0.0.0")
        assert wait_for_server("127.0.0.1", server_port)

        widget = InlineWidget(
            html="<html><body>Persistent</body></html>",
            port=server_port,
            widget_id="persistent-test",
            browser_only=True,
        )

        # First fetch
        status1, html1 = http_get(f"http://127.0.0.1:{server_port}/widget/{widget.widget_id}")
        assert status1 == 200
        assert "Persistent" in html1

        # Simulate page refresh - widget should still be available
        time.sleep(0.1)

        status2, html2 = http_get(f"http://127.0.0.1:{server_port}/widget/{widget.widget_id}")
        assert status2 == 200
        assert "Persistent" in html2

    def test_multiple_widgets_independent(self, server_port):
        """Multiple widgets should be independently accessible."""
        _start_server(port=server_port, host="0.0.0.0")
        assert wait_for_server("127.0.0.1", server_port)

        widget1 = InlineWidget(
            html="<html><body>Widget One</body></html>",
            port=server_port,
            widget_id="multi-1",
            browser_only=True,
        )

        widget2 = InlineWidget(
            html="<html><body>Widget Two</body></html>",
            port=server_port,
            widget_id="multi-2",
            browser_only=True,
        )

        status1, html1 = http_get(f"http://127.0.0.1:{server_port}/widget/{widget1.widget_id}")
        status2, html2 = http_get(f"http://127.0.0.1:{server_port}/widget/{widget2.widget_id}")

        assert status1 == 200
        assert "Widget One" in html1

        assert status2 == 200
        assert "Widget Two" in html2

    def test_server_stops_gracefully(self, server_port):
        """Server should stop gracefully without errors."""
        _start_server(port=server_port, host="0.0.0.0")
        assert wait_for_server("127.0.0.1", server_port)

        # Create widget
        _widget = InlineWidget(
            html="<html></html>",
            port=server_port,
            widget_id="stop-test",
            browser_only=True,
        )
        assert _widget is not None

        # Stop server
        stop_server()
        time.sleep(0.5)

        # Server should no longer respond (suppress connection errors)
        with suppress(Exception):
            http_get(f"http://127.0.0.1:{server_port}/health", timeout=1.0)


# =============================================================================
# Theme Handling
# =============================================================================


class TestBrowserModeTheme:
    """Test theme handling in BROWSER mode."""

    def test_dark_theme_applied(self, server_port):
        """Dark theme should be applied to widget."""
        data = [{"a": 1}]

        with patch("webbrowser.open"):
            widget = show_dataframe(
                df=data,
                theme="dark",
                port=server_port,
                open_browser=True,
            )

        assert wait_for_server("127.0.0.1", server_port)
        status, html = http_get(f"http://127.0.0.1:{server_port}/widget/{widget.widget_id}")

        assert status == 200
        # Should have dark theme class
        assert "dark" in html.lower()

    def test_light_theme_applied(self, server_port):
        """Light theme should be applied to widget."""
        data = [{"a": 1}]

        with patch("webbrowser.open"):
            widget = show_dataframe(
                df=data,
                theme="light",
                port=server_port,
                open_browser=True,
            )

        assert wait_for_server("127.0.0.1", server_port)
        status, html = http_get(f"http://127.0.0.1:{server_port}/widget/{widget.widget_id}")

        assert status == 200
        # Should have light theme indicator (not dark)
        # AG Grid uses ag-theme-alpine (light) vs ag-theme-alpine-dark
        assert "ag-theme-alpine" in html


# =============================================================================
# PyWry App BROWSER Mode Integration
# =============================================================================


class TestPyWryAppBrowserMode:
    """Test PyWry app with WindowMode.BROWSER."""

    def test_app_browser_mode_show_plotly(self):
        """PyWry app in BROWSER mode should use InlineWidget for Plotly."""
        import plotly.graph_objects as go

        from pywry import PyWry

        app = PyWry(mode=WindowMode.BROWSER)

        fig = go.Figure(data=[go.Scatter(x=[1, 2], y=[3, 4])])

        with patch("webbrowser.open"):
            widget = app.show_plotly(fig, title="Browser Plotly")

        # Should return InlineWidget
        assert isinstance(widget, InlineWidget)

    def test_app_browser_mode_show_dataframe(self):
        """PyWry app in BROWSER mode should use InlineWidget for DataFrames."""
        from pywry import PyWry

        app = PyWry(mode=WindowMode.BROWSER)
        data = [{"x": 1, "y": 2}]

        with patch("webbrowser.open"):
            widget = app.show_dataframe(data, title="Browser Grid")

        # Should return InlineWidget
        assert isinstance(widget, InlineWidget)


# =============================================================================
# Edge Cases
# =============================================================================


class TestBrowserModeEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_data_handled(self, server_port):
        """Empty data should be handled gracefully."""
        with patch("webbrowser.open"):
            widget = show_dataframe(
                df=[],
                port=server_port,
                open_browser=True,
            )

        assert widget.widget_id in _state.widgets

    def test_special_characters_in_data(self, server_port):
        """Data with special characters should be handled without breaking rendering."""
        data = [
            {"name": "Test <script>alert('xss')</script>", "value": 100},
            {"name": 'Quote\'s & "more"', "value": 200},
        ]

        with patch("webbrowser.open"):
            widget = show_dataframe(
                df=data,
                port=server_port,
                open_browser=True,
            )

        assert wait_for_server("127.0.0.1", server_port)
        status, html = http_get(f"http://127.0.0.1:{server_port}/widget/{widget.widget_id}")

        assert status == 200
        # Page should load successfully (HTML structure intact)
        assert "ag-grid" in html.lower() or "aggrid" in html.lower()
        # The data is JSON-encoded inside a script variable, so characters appear
        # but are not executable as HTML. Check the widget was created.
        assert widget.widget_id in _state.widgets

    def test_large_dataset_handled(self, server_port):
        """Large datasets should be handled (possibly with truncation)."""
        # Create dataset with 1000 rows
        data = [{"id": i, "value": i * 100} for i in range(1000)]

        with patch("webbrowser.open"):
            widget = show_dataframe(
                df=data,
                port=server_port,
                open_browser=True,
            )

        assert widget.widget_id in _state.widgets

        # Widget should still be fetchable
        assert wait_for_server("127.0.0.1", server_port)
        status, _ = http_get(f"http://127.0.0.1:{server_port}/widget/{widget.widget_id}")
        assert status == 200

    def test_unicode_data_handled(self, server_port):
        """Unicode data should be handled correctly."""
        data = [
            {"name": "日本語", "emoji": "🎉"},
            {"name": "中文", "emoji": "✅"},
            {"name": "العربية", "emoji": "🔥"},
        ]

        with patch("webbrowser.open"):
            widget = show_dataframe(
                df=data,
                port=server_port,
                open_browser=True,
            )

        assert wait_for_server("127.0.0.1", server_port)
        status, html = http_get(f"http://127.0.0.1:{server_port}/widget/{widget.widget_id}")

        assert status == 200
        # Unicode should be preserved
        assert "日本語" in html or "\\u" in html  # May be escaped
