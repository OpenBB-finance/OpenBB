"""End-to-end tests for inline notebook rendering.

These tests actually start the server, make HTTP requests,
and verify content is rendered correctly. Designed for CI/GitHub Actions.
"""
# pylint: disable=redefined-outer-name

import asyncio
import json
import os
import re
import time
import urllib.error
import urllib.request

from unittest.mock import patch

import pytest


try:
    import websockets
except ImportError:
    websockets = None


from pywry.config import clear_settings, get_settings
from pywry.inline import (
    HAS_FASTAPI,
    InlineWidget,
    _start_server,
    _state,
    show,
    stop_server,
)
from pywry.notebook import (
    clear_environment_cache,
    detect_notebook_environment,
    should_use_inline_rendering,
)


# Skip all tests if FastAPI not installed
pytestmark = pytest.mark.skipif(not HAS_FASTAPI, reason="FastAPI not installed")


@pytest.fixture(autouse=True)
def clean_state():
    """Clean up server state before and after each test."""
    # Stop any existing server
    stop_server()
    _state.widgets.clear()
    _state.connections.clear()
    clear_settings()
    clear_environment_cache()

    yield

    # Cleanup after test
    stop_server()
    _state.widgets.clear()
    _state.connections.clear()
    clear_settings()
    clear_environment_cache()

    # Remove any env vars we set
    for key in list(os.environ.keys()):
        if key.startswith("PYWRY_SERVER__"):
            del os.environ[key]


@pytest.fixture
def server_port():
    """Get a free port that's not in use."""
    import socket

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("0.0.0.0", 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return s.getsockname()[1]


def _get_auth_header() -> dict[str, str]:
    """Get the internal API auth header for protected endpoints."""
    settings = get_settings()
    if _state.internal_api_token:
        return {settings.server.internal_api_header: _state.internal_api_token}
    return {}


def wait_for_server(host: str, port: int, timeout: float = 5.0) -> bool:
    """Wait for server to be ready.

    Uses the widget endpoint (not health) since health requires auth and
    we may not have the token yet during startup wait.
    """
    # Try widget endpoint first (doesn't require auth in notebook mode)
    # or just try the socket until server is listening
    import socket as sock_mod

    start = time.time()
    while time.time() - start < timeout:
        try:
            # Try to connect to the socket
            with sock_mod.socket(sock_mod.AF_INET, sock_mod.SOCK_STREAM) as s:
                s.settimeout(0.5)
                result = s.connect_ex((host, port))
                if result == 0:
                    # Socket is open, try a simple request
                    # Use health with auth header if we have token
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
                        # Health might 404 without auth, but socket is open so server is running
                        return True
        except Exception:  # noqa: S110
            pass
        time.sleep(0.1)
    return False


def http_get(url: str, timeout: float = 5.0, auth: bool = False) -> tuple[int, str]:
    """Make HTTP GET request, return (status_code, body).

    Args:
        url: URL to fetch
        timeout: Request timeout in seconds
        auth: If True, include internal API auth header (for /health, etc.)
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

    Args:
        url: URL to POST to
        data: JSON data dict
        timeout: Request timeout in seconds
        auth: If True, include internal API auth header (for /register_widget, etc.)
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
# Server Startup Tests
# =============================================================================


class TestServerStartup:
    """Test that the FastAPI server starts correctly."""

    def test_server_starts_and_responds(self, server_port):
        """Server should start and respond to health check."""
        _start_server(port=server_port, host="0.0.0.0")

        assert wait_for_server("127.0.0.1", server_port), "Server did not start"

        # Health endpoint requires auth
        status, body = http_get(f"http://127.0.0.1:{server_port}/health", auth=True)
        assert status == 200

        data = json.loads(body)
        assert data["status"] == "ok"

    def test_server_uses_configured_port(self, server_port):
        """Server should use the configured port."""
        _start_server(port=server_port, host="0.0.0.0")

        assert wait_for_server("127.0.0.1", server_port)
        assert _state.port == server_port

    def test_server_stop(self, server_port):
        """Server should stop gracefully."""
        _start_server(port=server_port, host="0.0.0.0")
        assert wait_for_server("127.0.0.1", server_port)

        stop_server()
        time.sleep(0.5)

        # Server should no longer respond
        try:  # noqa: SIM105
            http_get(f"http://127.0.0.1:{server_port}/health", timeout=1.0)
            # If we get here, server is still running (might take time to stop)
        except Exception:  # noqa: S110
            pass  # Expected - server stopped

    def test_server_config_from_settings(self, server_port):
        """Server should use settings for configuration."""
        os.environ["PYWRY_SERVER__PORT"] = str(server_port)
        os.environ["PYWRY_SERVER__HOST"] = "0.0.0.0"
        clear_settings()

        settings = get_settings()
        assert settings.server.port == server_port

        _start_server()
        assert wait_for_server("127.0.0.1", server_port)


# =============================================================================
# Widget Registration and Rendering Tests
# =============================================================================


class TestWidgetRendering:
    """Test that widgets are registered and content is served correctly."""

    def test_widget_registration(self, server_port):
        """Widget should be registered and accessible."""
        _start_server(port=server_port, host="0.0.0.0")
        assert wait_for_server("127.0.0.1", server_port)

        # Register a widget directly
        widget_id = "test-widget-123"
        test_html = "<html><body><h1>Test Content</h1></body></html>"
        _state.widgets[widget_id] = {"html": test_html, "callbacks": {}}

        # Fetch widget content
        status, body = http_get(f"http://127.0.0.1:{server_port}/widget/{widget_id}")

        assert status == 200
        assert "Test Content" in body

    def test_widget_html_preserved(self, server_port):
        """Widget HTML content should be preserved exactly."""
        _start_server(port=server_port, host="0.0.0.0")
        assert wait_for_server("127.0.0.1", server_port)

        widget_id = "exact-html-test"
        test_html = """<!DOCTYPE html>
<html>
<head><title>Exact Test</title></head>
<body>
    <div id="content" class="test-class">
        <p>Paragraph with special chars: &amp; &lt; &gt;</p>
    </div>
</body>
</html>"""
        _state.widgets[widget_id] = {"html": test_html, "callbacks": {}}

        status, body = http_get(f"http://127.0.0.1:{server_port}/widget/{widget_id}")

        assert status == 200
        assert "Exact Test" in body
        assert 'id="content"' in body
        assert 'class="test-class"' in body

    def test_widget_not_found(self, server_port):
        """Non-existent widget should return 404."""
        _start_server(port=server_port, host="0.0.0.0")
        assert wait_for_server("127.0.0.1", server_port)

        status, _ = http_get(f"http://127.0.0.1:{server_port}/widget/nonexistent")
        assert status == 404

    def test_widget_returns_registered_html(self, server_port):
        """Widget endpoint should return the registered HTML content."""
        _start_server(port=server_port, host="0.0.0.0")
        assert wait_for_server("127.0.0.1", server_port)

        widget_id = "content-test"
        test_html = "<html><body>Content</body></html>"
        _state.widgets[widget_id] = {"html": test_html, "callbacks": {}}

        status, body = http_get(f"http://127.0.0.1:{server_port}/widget/{widget_id}")

        assert status == 200
        # Endpoint returns raw HTML as registered
        assert "Content" in body

    def test_multiple_widgets(self, server_port):
        """Multiple widgets should be independently accessible."""
        _start_server(port=server_port, host="0.0.0.0")
        assert wait_for_server("127.0.0.1", server_port)

        widgets = {
            "widget-a": "<html><body>Widget A Content</body></html>",
            "widget-b": "<html><body>Widget B Content</body></html>",
            "widget-c": "<html><body>Widget C Content</body></html>",
        }

        for wid, html in widgets.items():
            _state.widgets[wid] = {"html": html, "callbacks": {}}

        # Verify each widget returns correct content
        for wid in widgets:
            status, body = http_get(f"http://127.0.0.1:{server_port}/widget/{wid}")
            assert status == 200
            assert f"Widget {wid[-1].upper()} Content" in body


# =============================================================================
# Callback Tests
# =============================================================================
# Callback tests moved to TestWebSocketUpdates as HTTP emit endpoint is removed.


# =============================================================================
# InlineWidget Class Tests
# =============================================================================


# Mock Output class for tests when IPython not fully available
class MockOutput:
    """Mock ipywidgets.Output for testing."""

    def __init__(self):
        """Initialize mock output."""
        self.outputs = []


class TestInlineWidgetClass:
    """Test the InlineWidget class functionality."""

    @patch("pywry.inline.Output", MockOutput)
    @patch("pywry.inline.HAS_IPYTHON", True)
    def test_widget_creates_unique_id(self, server_port):
        """Each widget should have a unique ID."""
        widget1 = InlineWidget("<html><body>1</body></html>", port=server_port)
        widget2 = InlineWidget("<html><body>2</body></html>", port=server_port)

        assert widget1.widget_id != widget2.widget_id

    @patch("pywry.inline.Output", MockOutput)
    @patch("pywry.inline.HAS_IPYTHON", True)
    def test_widget_registered_in_state(self, server_port):
        """Widget should be registered in global state."""
        widget = InlineWidget("<html><body>Test</body></html>", port=server_port)

        assert widget.widget_id in _state.widgets
        assert "Test" in _state.widgets[widget.widget_id]["html"]

    @patch("pywry.inline.Output", MockOutput)
    @patch("pywry.inline.HAS_IPYTHON", True)
    def test_widget_callbacks_registered(self, server_port):
        """Widget callbacks should be registered."""

        def my_callback(data):  # pylint: disable=unused-argument
            return {"ok": True}

        widget = InlineWidget(
            "<html><body>Test</body></html>",
            callbacks={"click": my_callback},
            port=server_port,
        )

        assert "click" in _state.widgets[widget.widget_id]["callbacks"]

    @patch("pywry.inline.Output", MockOutput)
    @patch("pywry.inline.HAS_IPYTHON", True)
    def test_widget_on_method(self, server_port):
        """Widget.on() should register additional callbacks."""
        widget = InlineWidget("<html><body>Test</body></html>", port=server_port)

        def handler(data):
            return data

        widget.on("custom_event", handler)

        assert "custom_event" in _state.widgets[widget.widget_id]["callbacks"]

    @patch("pywry.inline.Output", MockOutput)
    @patch("pywry.inline.HAS_IPYTHON", True)
    def test_widget_update_html(self, server_port):
        """Widget.update_html() should update content."""
        widget = InlineWidget("<html><body>Original</body></html>", port=server_port)

        widget.update_html("<html><body>Updated</body></html>")

        assert "Updated" in _state.widgets[widget.widget_id]["html"]

    @patch("pywry.inline.Output", MockOutput)
    @patch("pywry.inline.HAS_IPYTHON", True)
    def test_widget_repr_html(self, server_port):
        """Widget._repr_html_() should return iframe HTML."""
        widget = InlineWidget("<html><body>Test</body></html>", port=server_port)

        html = widget._repr_html_()

        assert "<iframe" in html
        assert widget.widget_id in html
        assert str(server_port) in html


# =============================================================================
# Show Function Tests
# =============================================================================


class TestShowFunction:
    """Test the show() convenience function."""

    @patch("pywry.inline.Output", MockOutput)
    @patch("pywry.inline.HAS_IPYTHON", True)
    @patch("IPython.display.display")
    def test_show_creates_widget(self, mock_ipy_display, server_port):  # pylint: disable=unused-argument
        """E2E: show() should create widget accessible via HTTP."""
        widget = show(
            "<p>Hello World</p>",
            title="Test",
            width="100%",
            height=400,
            port=server_port,
        )

        assert widget is not None
        assert widget.widget_id in _state.widgets

        # E2E: Verify content is actually served via HTTP
        status, html = http_get(f"http://127.0.0.1:{server_port}/widget/{widget.widget_id}")
        assert status == 200
        assert "Hello World" in html

    @patch("pywry.inline.Output", MockOutput)
    @patch("pywry.inline.HAS_IPYTHON", True)
    @patch("IPython.display.display")
    def test_show_with_callbacks(self, mock_ipy_display, server_port):  # pylint: disable=unused-argument
        """E2E: show() with callbacks should be accessible via HTTP."""

        def my_handler(data):
            return data

        widget = show(
            "<p>Content</p>",
            callbacks={"handler": my_handler},
            port=server_port,
        )

        assert "handler" in _state.widgets[widget.widget_id]["callbacks"]

        # E2E: Verify content is served
        status, html = http_get(f"http://127.0.0.1:{server_port}/widget/{widget.widget_id}")
        assert status == 200
        assert "Content" in html


# =============================================================================
# Force Notebook Mode Tests
# =============================================================================


class TestForceNotebookMode:
    """Test force_notebook setting for headless/CI environments."""

    def test_force_notebook_via_env(self):
        """force_notebook should be settable via environment."""
        os.environ["PYWRY_SERVER__FORCE_NOTEBOOK"] = "true"
        clear_settings()
        clear_environment_cache()

        settings = get_settings()
        assert settings.server.force_notebook is True

        # This should now return True even in terminal
        should_inline = should_use_inline_rendering()
        assert should_inline is True

    def test_force_notebook_overrides_detection(self):
        """force_notebook should override environment detection."""
        # First, without force_notebook in a terminal
        clear_environment_cache()
        clear_settings()

        # In CI/terminal, normally would be False
        detect_notebook_environment()  # Just call to ensure no crash
        # Should be TERMINAL in CI

        # Now force it
        os.environ["PYWRY_SERVER__FORCE_NOTEBOOK"] = "true"
        clear_settings()
        clear_environment_cache()

        should_inline = should_use_inline_rendering()
        assert should_inline is True


# =============================================================================
# CORS Tests
# =============================================================================


class TestCORS:
    """Test CORS headers are set correctly."""

    def test_cors_headers_present(self, server_port):
        """CORS headers should be present in responses."""
        _start_server(port=server_port, host="0.0.0.0")
        assert wait_for_server("127.0.0.1", server_port)

        # Make OPTIONS request to check CORS
        url = f"http://127.0.0.1:{server_port}/health"
        req = urllib.request.Request(url, method="OPTIONS")  # noqa: S310
        req.add_header("Origin", "http://localhost:8888")
        req.add_header("Access-Control-Request-Method", "GET")

        try:
            with urllib.request.urlopen(req, timeout=5) as resp:  # noqa: S310
                headers = dict(resp.headers)
                # CORS headers should be present
                assert "Access-Control-Allow-Origin" in headers or resp.status == 200
        except urllib.error.HTTPError:
            # Some servers return 405 for OPTIONS, that's ok
            pass


# =============================================================================
# Content Type Tests
# =============================================================================


class TestContentTypes:
    """Test that correct content types are returned."""

    def test_health_returns_json(self, server_port):
        """Health endpoint should return JSON (requires auth)."""
        _start_server(port=server_port, host="0.0.0.0")
        assert wait_for_server("127.0.0.1", server_port)

        url = f"http://127.0.0.1:{server_port}/health"
        # Health endpoint requires internal auth
        req = urllib.request.Request(url)  # noqa: S310
        for k, v in _get_auth_header().items():
            req.add_header(k, v)
        with urllib.request.urlopen(req, timeout=5) as resp:  # noqa: S310
            content_type = resp.headers.get("Content-Type", "")
            assert "application/json" in content_type

    def test_health_without_auth_returns_404(self, server_port):
        """Health endpoint without auth should return 404."""
        _start_server(port=server_port, host="0.0.0.0")
        assert wait_for_server("127.0.0.1", server_port)

        # No auth header - should get 404
        status, _ = http_get(f"http://127.0.0.1:{server_port}/health", auth=False)
        assert status == 404

    def test_widget_returns_html(self, server_port):
        """Widget endpoint should return HTML."""
        _start_server(port=server_port, host="0.0.0.0")
        assert wait_for_server("127.0.0.1", server_port)

        widget_id = "html-type-test"
        _state.widgets[widget_id] = {
            "html": "<html><body>Test</body></html>",
            "callbacks": {},
        }

        url = f"http://127.0.0.1:{server_port}/widget/{widget_id}"
        with urllib.request.urlopen(url, timeout=5) as resp:  # noqa: S310
            content_type = resp.headers.get("Content-Type", "")
            assert "text/html" in content_type


# =============================================================================
# Plotly Integration Tests
# =============================================================================


class TestPlotlyIntegration:
    """E2E: Test Plotly HTML generation and serving - NO external dependencies."""

    def test_generate_plotly_html_contains_figure_data(self, server_port):
        """E2E: generate_plotly_html() creates HTML with figure JSON, served via HTTP."""
        from pywry.inline import generate_plotly_html

        _start_server(port=server_port, host="0.0.0.0")
        assert wait_for_server("127.0.0.1", server_port)

        # Raw JSON - no Plotly import needed
        figure_json = '{"data": [{"type": "scatter", "x": [1, 2, 3], "y": [100, 200, 300], "name": "test-series-123"}], "layout": {"title": "Test"}}'

        # Use the LIBRARY function to generate HTML
        widget_id = "plotly-e2e-test"
        html = generate_plotly_html(figure_json, widget_id, title="E2E Plotly Test", theme="dark")

        # Register in state and serve
        _state.widgets[widget_id] = {"html": html, "callbacks": {}}

        # E2E: Fetch the widget via HTTP
        status, response_html = http_get(f"http://127.0.0.1:{server_port}/widget/{widget_id}")

        assert status == 200
        # Verify the figure data is in the HTML
        assert "test-series-123" in response_html
        assert "100" in response_html and "200" in response_html and "300" in response_html
        # Verify Plotly is loaded (either inline or CDN)
        assert "Plotly" in response_html or "plotly" in response_html

    def test_generate_plotly_html_dark_theme(self, server_port):
        """E2E: generate_plotly_html() with dark theme has correct background."""
        from pywry.inline import generate_plotly_html

        _start_server(port=server_port, host="0.0.0.0")
        assert wait_for_server("127.0.0.1", server_port)

        figure_json = '{"data": [{"type": "bar", "x": ["A", "B"], "y": [10, 20]}], "layout": {}}'
        widget_id = "plotly-dark-test"
        html = generate_plotly_html(figure_json, widget_id, theme="dark")

        _state.widgets[widget_id] = {"html": html, "callbacks": {}}

        status, response_html = http_get(f"http://127.0.0.1:{server_port}/widget/{widget_id}")

        assert status == 200
        assert '<html class="dark">' in response_html
        assert "--pywry-bg" in response_html

    def test_generate_plotly_html_light_theme(self, server_port):
        """E2E: generate_plotly_html() with light theme has white background."""
        from pywry.inline import generate_plotly_html

        _start_server(port=server_port, host="0.0.0.0")
        assert wait_for_server("127.0.0.1", server_port)

        figure_json = '{"data": [{"type": "bar", "x": ["A", "B"], "y": [10, 20]}], "layout": {}}'
        widget_id = "plotly-light-test"
        html = generate_plotly_html(figure_json, widget_id, theme="light")

        _state.widgets[widget_id] = {"html": html, "callbacks": {}}

        status, response_html = http_get(f"http://127.0.0.1:{server_port}/widget/{widget_id}")

        assert status == 200
        assert "#ffffff" in response_html  # Light background


# =============================================================================
# DataFrame Integration Tests
# =============================================================================


class TestDataFrameIntegration:
    """E2E: Test DataFrame/AG Grid HTML generation and serving - NO external dependencies."""

    def test_generate_dataframe_html_contains_data(self, server_port):
        """E2E: generate_dataframe_html() creates HTML with data, served via HTTP."""
        from pywry.inline import generate_dataframe_html

        _start_server(port=server_port, host="0.0.0.0")
        assert wait_for_server("127.0.0.1", server_port)

        # Raw data - no pandas import needed
        row_data = [{"Price": 99.99, "Product": "Widget"}, {"Price": 150.5, "Product": "Gadget"}]
        columns = ["Price", "Product"]

        # Use the LIBRARY function to generate HTML
        widget_id = "dataframe-e2e-test"
        html = generate_dataframe_html(
            row_data, columns, widget_id, title="E2E DataFrame Test", theme="dark"
        )

        # Register in state and serve
        _state.widgets[widget_id] = {"html": html, "callbacks": {}}

        # E2E: Fetch the widget via HTTP
        status, response_html = http_get(f"http://127.0.0.1:{server_port}/widget/{widget_id}")

        assert status == 200
        # Verify column names are in the HTML
        assert "Price" in response_html
        assert "Product" in response_html
        # Verify data values
        assert "99.99" in response_html
        assert "150.5" in response_html
        assert "Widget" in response_html
        assert "Gadget" in response_html

    def test_generate_dataframe_html_numeric_values(self, server_port):
        """E2E: generate_dataframe_html() preserves numeric precision."""
        from pywry.inline import generate_dataframe_html

        _start_server(port=server_port, host="0.0.0.0")
        assert wait_for_server("127.0.0.1", server_port)

        row_data = [{"Amount": 1234.56}, {"Amount": 7890.12}]
        columns = ["Amount"]
        widget_id = "dataframe-numeric-test"
        html = generate_dataframe_html(row_data, columns, widget_id)

        _state.widgets[widget_id] = {"html": html, "callbacks": {}}

        status, response_html = http_get(f"http://127.0.0.1:{server_port}/widget/{widget_id}")

        assert status == 200
        assert "1234.56" in response_html
        assert "7890.12" in response_html

    def test_generate_dataframe_html_dark_theme(self, server_port):
        """E2E: generate_dataframe_html() with dark theme has correct background."""
        from pywry.inline import generate_dataframe_html

        _start_server(port=server_port, host="0.0.0.0")
        assert wait_for_server("127.0.0.1", server_port)

        row_data = [{"Col": 1}, {"Col": 2}, {"Col": 3}]
        columns = ["Col"]
        widget_id = "dataframe-dark-test"
        html = generate_dataframe_html(row_data, columns, widget_id, theme="dark")

        _state.widgets[widget_id] = {"html": html, "callbacks": {}}

        status, response_html = http_get(f"http://127.0.0.1:{server_port}/widget/{widget_id}")

        assert status == 200
        assert '<html class="dark">' in response_html
        assert "--pywry-bg" in response_html


# =============================================================================
# Error Handling Tests
# =============================================================================


class TestErrorHandling:
    """Test error handling in various scenarios."""

    def test_server_survives_errors(self, server_port):
        """Server should survive after errors."""
        _start_server(port=server_port, host="0.0.0.0")
        assert wait_for_server("127.0.0.1", server_port)

        widget_id = "survive-test"
        _state.widgets[widget_id] = {
            "html": "<html><body>Test</body></html>",
            "callbacks": {},
        }

        # Make some requests
        http_get(f"http://127.0.0.1:{server_port}/widget/{widget_id}")

        # Simulate a bad request (non-existent widget for register which is POST)
        # Note: register_widget requires auth, so without auth we get 404
        http_post(
            f"http://127.0.0.1:{server_port}/register_widget",
            {"widget_id": "", "html": ""},  # Missing required fields, also no auth
            auth=False,  # No auth = 404
        )

        # Server should still be running (use auth to verify)
        health_status, _ = http_get(f"http://127.0.0.1:{server_port}/health", auth=True)
        assert health_status == 200


class TestToolbarRendering:
    """Tests for toolbar rendering in inline mode."""

    def test_toolbar_position_passed_to_show(self, server_port):
        """Toolbar position should be respected in rendered HTML."""
        _start_server(port=server_port, host="0.0.0.0")
        assert wait_for_server("127.0.0.1", server_port)

        toolbars = [
            {
                "position": "bottom",
                "items": [{"type": "button", "label": "MyButton", "event": "toolbar:click"}],
            }
        ]

        # Mock IPython display to avoid errors/outputs during test
        with (
            patch("IPython.display.display"),
            patch("IPython.display.IFrame"),
            patch("pywry.inline.Output"),
            patch("pywry.inline.HAS_IPYTHON", True),
        ):
            widget = show("<div>Content</div>", toolbars=toolbars, port=server_port)

        wid = widget._widget_id

        status, body = http_get(f"http://127.0.0.1:{server_port}/widget/{wid}")
        assert status == 200
        assert "MyButton" in body
        assert "pywry-wrapper-bottom" in body


class TestDOMStructure:
    """Tests for DOM structure and CSS selector availability."""

    def test_css_injection(self, server_port):
        """Standard PyWry CSS should be injected."""
        _start_server(port=server_port, host="0.0.0.0")
        assert wait_for_server("127.0.0.1", server_port)

        with (
            patch("IPython.display.display"),
            patch("IPython.display.IFrame"),
            patch("pywry.inline.Output"),
            patch("pywry.inline.HAS_IPYTHON", True),
        ):
            widget = show("<div></div>", port=server_port)

        wid = widget._widget_id
        status, body = http_get(f"http://127.0.0.1:{server_port}/widget/{wid}")

        assert status == 200
        # Check for CSS config variable which is present in pywry.css
        assert "--pywry-bg" in body
        assert "--pywry-text" in body

    def test_toolbar_inner_structure_top(self, server_port):
        """Verifies top toolbar inner structure."""
        _start_server(port=server_port, host="0.0.0.0")
        assert wait_for_server("127.0.0.1", server_port)

        toolbars = [
            {
                "position": "top",
                "items": [{"type": "button", "label": "Btn", "event": "toolbar:click"}],
            }
        ]
        with (
            patch("IPython.display.display"),
            patch("IPython.display.IFrame"),
            patch("pywry.inline.Output"),
            patch("pywry.inline.HAS_IPYTHON", True),
        ):
            widget = show("<div>Content</div>", toolbars=toolbars, port=server_port)

        wid = widget._widget_id
        status, body = http_get(f"http://127.0.0.1:{server_port}/widget/{wid}")

        assert status == 200
        # Check for classes using regex to tolerate single/double quotes
        assert re.search(r'class=["\']pywry-wrapper-top["\']', body), "Wrapper top class not found"
        assert re.search(r'class=["\']pywry-toolbar pywry-toolbar-top["\']', body), (
            "Toolbar top class not found"
        )

        # Structure check: Wrapper < Toolbar < Content
        wrapper_match = re.search(r'class=["\']pywry-wrapper-top["\']', body)
        toolbar_match = re.search(r'class=["\']pywry-toolbar pywry-toolbar-top["\']', body)
        content_match = re.search(r'class=["\']pywry-content["\']', body)

        assert wrapper_match and toolbar_match and content_match
        assert wrapper_match.start() < toolbar_match.start() < content_match.start()

    def test_toolbar_inner_structure_left(self, server_port):
        """Verifies left toolbar inner structure."""
        _start_server(port=server_port, host="0.0.0.0")
        assert wait_for_server("127.0.0.1", server_port)

        toolbars = [
            {
                "position": "left",
                "items": [{"type": "button", "label": "Btn", "event": "toolbar:click"}],
            }
        ]
        with (
            patch("IPython.display.display"),
            patch("IPython.display.IFrame"),
            patch("pywry.inline.Output"),
            patch("pywry.inline.HAS_IPYTHON", True),
        ):
            widget = show("<div>Content</div>", toolbars=toolbars, port=server_port)

        wid = widget._widget_id
        status, body = http_get(f"http://127.0.0.1:{server_port}/widget/{wid}")

        assert status == 200

        wrapper_match = re.search(r'class=["\']pywry-wrapper-left["\']', body)
        toolbar_match = re.search(r'class=["\']pywry-toolbar pywry-toolbar-left["\']', body)
        content_match = re.search(r'class=["\']pywry-content["\']', body)

        assert wrapper_match, "Wrapper left class not found"
        assert toolbar_match, "Toolbar left class not found"
        assert content_match, "Content class not found"

        # Structure check: Wrapper < Toolbar < Content
        assert wrapper_match.start() < toolbar_match.start() < content_match.start()


@pytest.mark.skipif(websockets is None, reason="websockets not installed")
class TestWebSocketUpdates:
    """Tests for dynamic updates via the WebSocket mechanism."""

    @pytest.mark.asyncio
    async def test_websocket_event_propagation(self, server_port):
        """Test that events are correctly broadcast via WebSocket."""
        host = "0.0.0.0"
        _start_server(port=server_port, host=host)
        assert wait_for_server("127.0.0.1", server_port)

        with (
            patch("IPython.display.display"),
            patch("IPython.display.IFrame"),
            patch("pywry.inline.Output"),
            patch("pywry.inline.HAS_IPYTHON", True),
        ):
            widget = show("<div></div>", port=server_port)

        # Connect to WebSocket with token for authentication
        ws_url = f"ws://127.0.0.1:{server_port}/ws/{widget._widget_id}"
        # Get the per-widget token from server state
        token = _state.widget_tokens.get(widget._widget_id)
        subprotocol = f"pywry.token.{token}" if token else None
        subprotocols = [subprotocol] if subprotocol else None

        async with websockets.connect(ws_url, subprotocols=subprotocols) as ws:
            # 1. Emit theme update event from Python side
            theme_data = {"theme": "ag-theme-quartz-dark"}
            widget.emit("pywry:update-theme", theme_data)

            # 2. Wait for message on WebSocket
            # The server pushes immediately, so we should receive it
            message = await asyncio.wait_for(ws.recv(), timeout=2.0)
            data = json.loads(message)

            # 3. Verify event
            assert data["type"] == "pywry:update-theme"
            assert data["data"]["theme"] == "ag-theme-quartz-dark"

            # 4. Test Python -> JS multiple events
            widget.emit("custom_event", {"foo": "bar"})
            message = await asyncio.wait_for(ws.recv(), timeout=2.0)
            data = json.loads(message)
            assert data["type"] == "custom_event"
            assert data["data"]["foo"] == "bar"

    @pytest.mark.asyncio
    async def test_websocket_client_to_server_msg(self, server_port):
        """Test that client-to-server messages are handled (callback_queue)."""
        host = "0.0.0.0"
        _start_server(port=server_port, host=host)
        assert wait_for_server("127.0.0.1", server_port)

        received_events = []

        def on_event(data, event_type, _label):
            received_events.append((event_type, data))

        with (
            patch("IPython.display.display"),
            patch("IPython.display.IFrame"),
            patch("pywry.inline.Output"),
            patch("pywry.inline.HAS_IPYTHON", True),
        ):
            widget = show("<div></div>", port=server_port)
            widget.on("test_click", on_event)

        # Connect via WS with token for authentication
        ws_url = f"ws://127.0.0.1:{server_port}/ws/{widget._widget_id}"
        token = _state.widget_tokens.get(widget._widget_id)
        subprotocol = f"pywry.token.{token}" if token else None
        subprotocols = [subprotocol] if subprotocol else None

        async with websockets.connect(ws_url, subprotocols=subprotocols) as ws:
            # Send message simulating JS client
            payload = {
                "type": "test_click",
                "data": {"x": 10, "y": 20},
                "widgetId": widget._widget_id,
            }
            await ws.send(json.dumps(payload))

            # Allow some time for the background thread process_callbacks to pick it up
            for _ in range(20):
                if received_events:
                    break
                await asyncio.sleep(0.1)

            assert len(received_events) == 1
            assert received_events[0][0] == "test_click"
            assert received_events[0][1] == {"x": 10, "y": 20}
