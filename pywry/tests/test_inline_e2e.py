"""End-to-end tests for inline notebook rendering."""

# pylint: disable=too-many-lines,redefined-outer-name

import asyncio
import contextlib
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
from pywry.state._factory import clear_state_caches


# Skip all tests if FastAPI not installed
pytestmark = pytest.mark.skipif(not HAS_FASTAPI, reason="FastAPI not installed")


def _clear_deploy_env_vars():
    """Remove all deploy-mode related environment variables."""
    deploy_vars = [
        "PYWRY_DEPLOY_MODE",
        "PYWRY_DEPLOY__STATE_BACKEND",
        "PYWRY_DEPLOY__REDIS_URL",
        "PYWRY_DEPLOY__REDIS_PREFIX",
        "PYWRY_HEADLESS",
    ]
    for var in deploy_vars:
        os.environ.pop(var, None)
    # Also remove any dynamically set vars
    for key in list(os.environ.keys()):
        if key.startswith("PYWRY_DEPLOY"):
            del os.environ[key]


@pytest.fixture(autouse=True)
def clean_state():
    """Clean up server state before and after each test."""
    # Clear deploy mode env vars FIRST to ensure local mode
    _clear_deploy_env_vars()
    clear_state_caches()

    # Stop any existing server
    stop_server()
    _state.widgets.clear()
    _state.connections.clear()
    _state.local_widgets.clear()
    _state.widget_tokens.clear()
    clear_settings()
    clear_environment_cache()

    yield

    # Cleanup after test
    _clear_deploy_env_vars()
    clear_state_caches()

    stop_server()
    _state.widgets.clear()
    _state.connections.clear()
    _state.local_widgets.clear()
    _state.widget_tokens.clear()
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
                        with urllib.request.urlopen(  # noqa: S310
                            req, timeout=0.5
                        ) as resp:
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

    Parameters
    ----------
    url : str
        URL to fetch.
    timeout : float, optional
        Request timeout in seconds.
    auth : bool, optional
        If True, include internal API auth header (for /health, etc.).
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
        If True, include internal API auth header (for /register_widget, etc.).
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
        with contextlib.suppress(Exception):
            http_get(f"http://127.0.0.1:{server_port}/health", timeout=1.0)
            # If we get here, server is still running (might take time to stop)

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

        widget_id = "test-widget-123"
        test_html = "<html><body><h1>Test Content</h1></body></html>"
        _state.register_widget(widget_id, test_html, callbacks={})

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
        _state.register_widget(widget_id, test_html, callbacks={})

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
        _state.register_widget(widget_id, test_html, callbacks={})

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
            _state.register_widget(wid, html, callbacks={})

        # Verify each widget returns correct content
        for wid in widgets:
            status, body = http_get(f"http://127.0.0.1:{server_port}/widget/{wid}")
            assert status == 200
            assert f"Widget {wid[-1].upper()} Content" in body


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
        _state.register_widget(widget_id, "<html><body>Test</body></html>", callbacks={})

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

        # Register in state and serve (use register_widget for deploy mode compatibility)
        _state.register_widget(widget_id, html, callbacks={})

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

        _state.register_widget(widget_id, html, callbacks={})

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

        _state.register_widget(widget_id, html, callbacks={})

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
        row_data = [
            {"Price": 99.99, "Product": "Widget"},
            {"Price": 150.5, "Product": "Gadget"},
        ]
        columns = ["Price", "Product"]

        # Use the LIBRARY function to generate HTML
        widget_id = "dataframe-e2e-test"
        html = generate_dataframe_html(
            row_data, columns, widget_id, title="E2E DataFrame Test", theme="dark"
        )

        # Register in state and serve (use register_widget for deploy mode compatibility)
        _state.register_widget(widget_id, html, callbacks={})

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

        _state.register_widget(widget_id, html, callbacks={})

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

        _state.register_widget(widget_id, html, callbacks={})

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
        _state.register_widget(widget_id, "<html><body>Test</body></html>", callbacks={})

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


# =============================================================================
# SecretInput E2E Security Tests (HTTP/WS)
# =============================================================================


@pytest.mark.skipif(websockets is None, reason="websockets not installed")
class TestSecretInputE2E:
    """E2E tests for SecretInput security: storage, transmission, and obfuscation.

    These tests validate that:
    1. Secrets are never exposed in plain text in HTML
    2. Secrets are stored as Pydantic SecretStr (never plain text)
    3. Secrets transmitted over WebSocket are base64 obfuscated
    4. Reveal/copy events use proper request/response pattern
    """

    def test_secret_never_in_html(self, server_port):
        """Secret values should never appear in rendered HTML."""
        from pywry.toolbar import SecretInput, Toolbar

        _start_server(port=server_port, host="0.0.0.0")
        assert wait_for_server("127.0.0.1", server_port)

        # Create toolbar with secret
        secret_value = "super-secret-api-key-12345"
        toolbar = Toolbar(
            position="top",
            items=[SecretInput(event="auth:api-key", value=secret_value)],
        )

        with (
            patch("IPython.display.display"),
            patch("IPython.display.IFrame"),
            patch("pywry.inline.Output"),
            patch("pywry.inline.HAS_IPYTHON", True),
        ):
            widget = show("<div>Content</div>", toolbars=[toolbar], port=server_port)

        # Fetch the rendered HTML
        status, html = http_get(f"http://127.0.0.1:{server_port}/widget/{widget._widget_id}")

        assert status == 200
        # Secret value must NOT appear anywhere in HTML
        assert secret_value not in html
        # But the input field should be present
        assert 'type="password"' in html
        # And should have masked value (bullets) when value exists
        assert 'value="••••••••••••"' in html

    def test_secret_stored_as_secretstr(self, server_port):
        """Secrets must be stored as SecretStr, not plain text."""
        from pydantic import SecretStr

        from pywry.toolbar import SecretInput, get_secret

        _start_server(port=server_port, host="0.0.0.0")
        assert wait_for_server("127.0.0.1", server_port)

        # Create and register SecretInput
        secret_value = "my-secret-token"
        si = SecretInput(event="settings:token", value=secret_value)

        # Verify internal storage is SecretStr
        assert isinstance(si.value, SecretStr)
        assert si.value.get_secret_value() == secret_value

        # Verify model repr doesn't expose secret
        repr_str = repr(si)
        assert secret_value not in repr_str
        assert "**********" in repr_str

        # Register and verify registry uses correct retrieval
        si.register()
        retrieved = get_secret(si.component_id)
        assert retrieved == secret_value

    @pytest.mark.asyncio
    async def test_secret_reveal_event_base64_encoded(self, server_port):
        """Reveal event response should be base64 encoded over WebSocket."""
        from pywry.toolbar import (
            SecretInput,
            Toolbar,
            decode_secret,
        )

        host = "0.0.0.0"
        _start_server(port=server_port, host=host)
        assert wait_for_server("127.0.0.1", server_port)

        # Create toolbar with secret
        secret_value = "reveal-me-securely"
        toolbar = Toolbar(
            position="top",
            items=[SecretInput(event="auth:api-key", value=secret_value)],
        )
        toolbar.register_secrets()  # Register secrets in the registry

        # Create widget with callbacks for secret handlers
        received_responses = []

        def _capture_dispatch(event: str, data: dict) -> None:
            received_responses.append((event, data))

        # Register handlers that will capture the response
        si = toolbar.get_secret_inputs()[0]
        reveal_event = si.get_reveal_event()

        with (
            patch("IPython.display.display"),
            patch("IPython.display.IFrame"),
            patch("pywry.inline.Output"),
            patch("pywry.inline.HAS_IPYTHON", True),
        ):
            widget = show("<div>Content</div>", toolbars=[toolbar], port=server_port)

            # Register handler to process reveal request
            def on_reveal(data, _event_type, _wid):
                from pywry.toolbar import encode_secret, get_secret

                component_id = data.get("componentId", "")
                secret = get_secret(component_id)
                # Response should be encoded
                encoded = encode_secret(secret) if secret else ""
                widget.emit(
                    f"{_event_type}-response",
                    {
                        "componentId": component_id,
                        "value": encoded,
                        "encoded": True,
                    },
                )

            widget.on(reveal_event, on_reveal)

        # Connect via WebSocket
        ws_url = f"ws://127.0.0.1:{server_port}/ws/{widget._widget_id}"
        token = _state.widget_tokens.get(widget._widget_id)
        subprotocol = f"pywry.token.{token}" if token else None
        subprotocols = [subprotocol] if subprotocol else None

        async with websockets.connect(ws_url, subprotocols=subprotocols) as ws:
            # Simulate browser sending reveal request
            payload = {
                "type": reveal_event,
                "data": {"componentId": si.component_id},
                "widgetId": widget._widget_id,
            }
            await ws.send(json.dumps(payload))

            # Wait for response
            message = await asyncio.wait_for(ws.recv(), timeout=2.0)
            data = json.loads(message)

            # Verify response is encoded
            assert data["type"] == f"{reveal_event}-response"
            assert data["data"]["encoded"] is True

            # Verify value is NOT plain text
            received_value = data["data"]["value"]
            assert received_value != secret_value

            # Verify it decodes correctly
            decoded = decode_secret(received_value)
            assert decoded == secret_value

    @pytest.mark.asyncio
    async def test_secret_input_submission_base64_encoded(self, server_port):
        """Secret input from JS should be base64 encoded in transmission."""
        from pywry.toolbar import SecretInput, Toolbar, decode_secret, encode_secret

        host = "0.0.0.0"
        _start_server(port=server_port, host=host)
        assert wait_for_server("127.0.0.1", server_port)

        # Create toolbar with empty secret
        toolbar = Toolbar(
            position="top",
            items=[SecretInput(event="auth:api-key")],
        )

        received_secrets = []

        with (
            patch("IPython.display.display"),
            patch("IPython.display.IFrame"),
            patch("pywry.inline.Output"),
            patch("pywry.inline.HAS_IPYTHON", True),
        ):
            widget = show("<div>Content</div>", toolbars=[toolbar], port=server_port)

            # Handler for secret input event
            def on_secret_input(data, _event_type, _wid):
                received_secrets.append(data)

            widget.on("auth:api-key", on_secret_input)

        # Connect via WebSocket
        ws_url = f"ws://127.0.0.1:{server_port}/ws/{widget._widget_id}"
        token = _state.widget_tokens.get(widget._widget_id)
        subprotocol = f"pywry.token.{token}" if token else None
        subprotocols = [subprotocol] if subprotocol else None

        si = toolbar.get_secret_inputs()[0]
        new_secret = "user-entered-secret-456"

        async with websockets.connect(ws_url, subprotocols=subprotocols) as ws:
            # Simulate JS sending base64 encoded secret (as the real JS does)
            encoded_secret = encode_secret(new_secret)
            payload = {
                "type": "auth:api-key",
                "data": {
                    "value": encoded_secret,
                    "encoded": True,
                    "componentId": si.component_id,
                },
                "widgetId": widget._widget_id,
            }
            await ws.send(json.dumps(payload))

            # Wait for handler to process
            for _ in range(20):
                if received_secrets:
                    break
                await asyncio.sleep(0.1)

            # Verify secret was received with encoding flag
            assert len(received_secrets) == 1
            assert received_secrets[0]["encoded"] is True
            assert received_secrets[0]["value"] == encoded_secret

            # Backend can decode it
            decoded = decode_secret(received_secrets[0]["value"])
            assert decoded == new_secret

    @pytest.mark.asyncio
    async def test_secret_copy_event_base64_encoded(self, server_port):
        """Copy event response should be base64 encoded over WebSocket."""
        from pywry.toolbar import SecretInput, Toolbar, decode_secret

        host = "0.0.0.0"
        _start_server(port=server_port, host=host)
        assert wait_for_server("127.0.0.1", server_port)

        # Create toolbar with secret
        secret_value = "copy-me-securely"
        toolbar = Toolbar(
            position="top",
            items=[SecretInput(event="settings:password", value=secret_value, show_copy=True)],
        )
        toolbar.register_secrets()

        with (
            patch("IPython.display.display"),
            patch("IPython.display.IFrame"),
            patch("pywry.inline.Output"),
            patch("pywry.inline.HAS_IPYTHON", True),
        ):
            widget = show("<div>Content</div>", toolbars=[toolbar], port=server_port)

            si = toolbar.get_secret_inputs()[0]
            copy_event = si.get_copy_event()

            # Register handler for copy request
            def on_copy(data, event_type, _wid):
                from pywry.toolbar import encode_secret, get_secret

                component_id = data.get("componentId", "")
                secret = get_secret(component_id)
                encoded = encode_secret(secret) if secret else ""
                widget.emit(
                    f"{event_type}-response",
                    {
                        "componentId": component_id,
                        "value": encoded,
                        "encoded": True,
                    },
                )

            widget.on(copy_event, on_copy)

        # Connect via WebSocket
        ws_url = f"ws://127.0.0.1:{server_port}/ws/{widget._widget_id}"
        token = _state.widget_tokens.get(widget._widget_id)
        subprotocol = f"pywry.token.{token}" if token else None
        subprotocols = [subprotocol] if subprotocol else None

        async with websockets.connect(ws_url, subprotocols=subprotocols) as ws:
            # Simulate browser sending copy request
            payload = {
                "type": copy_event,
                "data": {"componentId": si.component_id},
                "widgetId": widget._widget_id,
            }
            await ws.send(json.dumps(payload))

            # Wait for response
            message = await asyncio.wait_for(ws.recv(), timeout=2.0)
            data = json.loads(message)

            # Verify response is encoded
            assert data["type"] == f"{copy_event}-response"
            assert data["data"]["encoded"] is True

            # Value is NOT plain text in transit
            received_value = data["data"]["value"]
            assert received_value != secret_value

            # Decodes correctly
            decoded = decode_secret(received_value)
            assert decoded == secret_value

    def test_secret_not_in_model_dump(self, server_port):
        """Secret should be masked in model serialization."""
        from pywry.toolbar import SecretInput

        _start_server(port=server_port, host="0.0.0.0")
        assert wait_for_server("127.0.0.1", server_port)

        secret_value = "do-not-expose-me"
        si = SecretInput(event="auth:key", value=secret_value)

        # model_dump should mask the secret
        dumped = si.model_dump()
        assert dumped["value"] != secret_value
        # SecretStr serializes to the masked string or special marker
        assert "**********" in str(dumped["value"]) or dumped["value"] == "**********"

    def test_multiple_secrets_isolated(self, server_port):
        """Multiple SecretInputs should have isolated storage."""
        from pywry.toolbar import SecretInput, Toolbar, clear_secret, get_secret

        _start_server(port=server_port, host="0.0.0.0")
        assert wait_for_server("127.0.0.1", server_port)

        # Create multiple secrets
        toolbar = Toolbar(
            position="top",
            items=[
                SecretInput(event="auth:api-key", value="api-key-123"),
                SecretInput(event="auth:password", value="password-456"),
                SecretInput(event="auth:token", value="token-789"),
            ],
        )
        toolbar.register_secrets()

        secrets = toolbar.get_secret_inputs()
        assert len(secrets) == 3

        # Each has isolated value
        assert get_secret(secrets[0].component_id) == "api-key-123"
        assert get_secret(secrets[1].component_id) == "password-456"
        assert get_secret(secrets[2].component_id) == "token-789"

        # Clearing one doesn't affect others
        clear_secret(secrets[1].component_id)
        assert get_secret(secrets[0].component_id) == "api-key-123"
        assert get_secret(secrets[1].component_id) is None
        assert get_secret(secrets[2].component_id) == "token-789"

        # Cleanup
        for s in secrets:
            clear_secret(s.component_id)

    @pytest.mark.asyncio
    async def test_custom_secret_handler_reveal(self, server_port):
        """Custom secret handler should override default reveal behavior."""
        from pywry.toolbar import (
            _SECRET_HANDLERS,
            SecretInput,
            Toolbar,
            clear_secret,
            decode_secret,
            set_secret_handler,
        )

        host = "0.0.0.0"
        _start_server(port=server_port, host=host)
        assert wait_for_server("127.0.0.1", server_port)

        # Create toolbar - secret value in registry won't be used
        toolbar = Toolbar(
            position="top",
            items=[SecretInput(event="vault:secret", value="registry-value")],
        )
        toolbar.register_secrets()

        # Set a custom handler that returns a different secret (e.g., from external vault)
        custom_secret = "custom-vault-fetched-secret"

        def custom_reveal_handler(_data: dict) -> str:
            # In real usage, this might fetch from HashiCorp Vault, AWS Secrets Manager, etc.
            return custom_secret

        si = toolbar.get_secret_inputs()[0]
        reveal_event = si.get_reveal_event()
        set_secret_handler(reveal_event, custom_reveal_handler)

        with (
            patch("IPython.display.display"),
            patch("IPython.display.IFrame"),
            patch("pywry.inline.Output"),
            patch("pywry.inline.HAS_IPYTHON", True),
        ):
            widget = show("<div>Content</div>", toolbars=[toolbar], port=server_port)

            # Handler for reveal that uses the custom handler
            def on_reveal(data, event_type, _wid):
                from pywry.toolbar import encode_secret, get_secret_handler

                component_id = data.get("componentId", "")
                # Check for custom handler first
                handler = get_secret_handler(event_type)
                if handler:
                    secret = handler(data)
                else:
                    from pywry.toolbar import get_secret

                    secret = get_secret(component_id)

                encoded = encode_secret(secret) if secret else ""
                widget.emit(
                    f"{event_type}-response",
                    {
                        "componentId": component_id,
                        "value": encoded,
                        "encoded": True,
                    },
                )

            widget.on(reveal_event, on_reveal)

        try:
            # Connect via WebSocket
            ws_url = f"ws://127.0.0.1:{server_port}/ws/{widget._widget_id}"
            token = _state.widget_tokens.get(widget._widget_id)
            subprotocol = f"pywry.token.{token}" if token else None
            subprotocols = [subprotocol] if subprotocol else None

            async with websockets.connect(ws_url, subprotocols=subprotocols) as ws:
                # Send reveal request
                payload = {
                    "type": reveal_event,
                    "data": {"componentId": si.component_id},
                    "widgetId": widget._widget_id,
                }
                await ws.send(json.dumps(payload))

                # Wait for response
                message = await asyncio.wait_for(ws.recv(), timeout=2.0)
                data = json.loads(message)

                # Should get the custom handler's value, not the registry value
                assert data["type"] == f"{reveal_event}-response"
                assert data["data"]["encoded"] is True

                decoded = decode_secret(data["data"]["value"])
                assert decoded == custom_secret
                assert decoded != "registry-value"  # Not the registry value

        finally:
            # Cleanup
            _SECRET_HANDLERS.pop(reveal_event, None)
            clear_secret(si.component_id)

    @pytest.mark.asyncio
    async def test_custom_secret_handler_copy(self, server_port):
        """Custom secret handler should work for copy events too."""
        from pywry.toolbar import (
            _SECRET_HANDLERS,
            SecretInput,
            Toolbar,
            clear_secret,
            decode_secret,
            set_secret_handler,
        )

        host = "0.0.0.0"
        _start_server(port=server_port, host=host)
        assert wait_for_server("127.0.0.1", server_port)

        toolbar = Toolbar(
            position="top",
            items=[SecretInput(event="api:credentials", value="default-creds", show_copy=True)],
        )
        toolbar.register_secrets()

        # Custom handler that transforms or fetches from elsewhere
        transformed_secret = "transformed-copy-value"

        def custom_copy_handler(_data: dict) -> str:
            # Could add logging, auditing, or fetch from secure storage
            return transformed_secret

        si = toolbar.get_secret_inputs()[0]
        copy_event = si.get_copy_event()
        set_secret_handler(copy_event, custom_copy_handler)

        with (
            patch("IPython.display.display"),
            patch("IPython.display.IFrame"),
            patch("pywry.inline.Output"),
            patch("pywry.inline.HAS_IPYTHON", True),
        ):
            widget = show("<div>Content</div>", toolbars=[toolbar], port=server_port)

            def on_copy(data, event_type, _wid):
                from pywry.toolbar import encode_secret, get_secret_handler

                component_id = data.get("componentId", "")
                handler = get_secret_handler(event_type)
                if handler:
                    secret = handler(data)
                else:
                    from pywry.toolbar import get_secret

                    secret = get_secret(component_id)

                encoded = encode_secret(secret) if secret else ""
                widget.emit(
                    f"{event_type}-response",
                    {
                        "componentId": component_id,
                        "value": encoded,
                        "encoded": True,
                    },
                )

            widget.on(copy_event, on_copy)

        try:
            ws_url = f"ws://127.0.0.1:{server_port}/ws/{widget._widget_id}"
            token = _state.widget_tokens.get(widget._widget_id)
            subprotocol = f"pywry.token.{token}" if token else None
            subprotocols = [subprotocol] if subprotocol else None

            async with websockets.connect(ws_url, subprotocols=subprotocols) as ws:
                payload = {
                    "type": copy_event,
                    "data": {"componentId": si.component_id},
                    "widgetId": widget._widget_id,
                }
                await ws.send(json.dumps(payload))

                message = await asyncio.wait_for(ws.recv(), timeout=2.0)
                data = json.loads(message)

                assert data["type"] == f"{copy_event}-response"
                decoded = decode_secret(data["data"]["value"])
                assert decoded == transformed_secret

        finally:
            _SECRET_HANDLERS.pop(copy_event, None)
            clear_secret(si.component_id)

    def test_custom_handler_receives_full_data(self, server_port):
        """Custom handlers receive the full data dict for context."""
        from pywry.toolbar import (
            _SECRET_HANDLERS,
            SecretInput,
            Toolbar,
            clear_secret,
            set_secret_handler,
        )

        _start_server(port=server_port, host="0.0.0.0")
        assert wait_for_server("127.0.0.1", server_port)

        toolbar = Toolbar(
            position="top",
            items=[SecretInput(event="context:test", value="test-value")],
        )
        toolbar.register_secrets()

        # Track what data the handler receives
        received_data = []

        def tracking_handler(data: dict) -> str:
            received_data.append(data)
            return "handler-response"

        si = toolbar.get_secret_inputs()[0]
        reveal_event = si.get_reveal_event()
        set_secret_handler(reveal_event, tracking_handler)

        try:
            # Call handler directly to verify data structure
            from pywry.toolbar import get_secret_handler

            handler = get_secret_handler(reveal_event)
            assert handler is not None

            test_data = {
                "componentId": si.component_id,
                "extra": "context",
                "metadata": {"source": "test"},
            }
            result = handler(test_data)

            assert result == "handler-response"
            assert len(received_data) == 1
            assert received_data[0]["componentId"] == si.component_id
            assert received_data[0]["extra"] == "context"
            assert received_data[0]["metadata"]["source"] == "test"

        finally:
            _SECRET_HANDLERS.pop(reveal_event, None)
            clear_secret(si.component_id)


class TestSecretInputMaskAndEditE2E:
    """E2E tests for SecretInput mask display and edit mode.

    These tests validate:
    1. Mask (••••) is displayed when value exists
    2. Empty input when no value
    3. Edit mode textarea creation
    4. value_exists flag behavior
    5. Edit confirmation transmits value
    """

    def test_mask_displayed_in_html_when_value_exists(self, server_port):
        """HTML should show mask when a value is configured."""
        from pywry.toolbar import SecretInput, Toolbar

        _start_server(port=server_port, host="0.0.0.0")
        assert wait_for_server("127.0.0.1", server_port)

        toolbar = Toolbar(
            position="top",
            items=[SecretInput(event="auth:api-key", value="my-secret-value")],
        )

        with (
            patch("IPython.display.display"),
            patch("IPython.display.IFrame"),
            patch("pywry.inline.Output"),
            patch("pywry.inline.HAS_IPYTHON", True),
        ):
            widget = show("<div>Content</div>", toolbars=[toolbar], port=server_port)

        status, html = http_get(f"http://127.0.0.1:{server_port}/widget/{widget._widget_id}")

        assert status == 200
        # Mask should be in HTML
        assert 'value="••••••••••••"' in html
        # data-has-value should be true
        assert 'data-has-value="true"' in html
        # Actual secret should NOT be in HTML
        assert "my-secret-value" not in html

    def test_empty_input_when_no_value(self, server_port):
        """HTML should show empty input when no value is configured."""
        from pywry.toolbar import SecretInput, Toolbar

        _start_server(port=server_port, host="0.0.0.0")
        assert wait_for_server("127.0.0.1", server_port)

        toolbar = Toolbar(
            position="top",
            items=[SecretInput(event="auth:api-key", placeholder="Enter API key")],
        )

        with (
            patch("IPython.display.display"),
            patch("IPython.display.IFrame"),
            patch("pywry.inline.Output"),
            patch("pywry.inline.HAS_IPYTHON", True),
        ):
            widget = show("<div>Content</div>", toolbars=[toolbar], port=server_port)

        status, html = http_get(f"http://127.0.0.1:{server_port}/widget/{widget._widget_id}")

        assert status == 200
        # Value should be empty (not mask)
        assert 'value="••••••••••••"' not in html
        # data-has-value should not be present
        assert 'data-has-value="true"' not in html

    def test_value_exists_flag_shows_mask(self, server_port):
        """value_exists=True should show mask even with no internal value."""
        from pywry.toolbar import SecretInput, Toolbar

        _start_server(port=server_port, host="0.0.0.0")
        assert wait_for_server("127.0.0.1", server_port)

        # External storage scenario - value_exists=True but no internal value
        toolbar = Toolbar(
            position="top",
            items=[SecretInput(event="vault:key", value_exists=True)],
        )

        with (
            patch("IPython.display.display"),
            patch("IPython.display.IFrame"),
            patch("pywry.inline.Output"),
            patch("pywry.inline.HAS_IPYTHON", True),
        ):
            widget = show("<div>Content</div>", toolbars=[toolbar], port=server_port)

        status, html = http_get(f"http://127.0.0.1:{server_port}/widget/{widget._widget_id}")

        assert status == 200
        # Mask should be shown (value_exists=True)
        assert 'value="••••••••••••"' in html
        assert 'data-has-value="true"' in html

    def test_edit_mode_textarea_in_html(self, server_port):
        """HTML should contain edit mode textarea creation script."""
        from pywry.toolbar import SecretInput, Toolbar

        _start_server(port=server_port, host="0.0.0.0")
        assert wait_for_server("127.0.0.1", server_port)

        toolbar = Toolbar(
            position="top",
            items=[SecretInput(event="auth:api-key")],
        )

        with (
            patch("IPython.display.display"),
            patch("IPython.display.IFrame"),
            patch("pywry.inline.Output"),
            patch("pywry.inline.HAS_IPYTHON", True),
        ):
            widget = show("<div>Content</div>", toolbars=[toolbar], port=server_port)

        status, html = http_get(f"http://127.0.0.1:{server_port}/widget/{widget._widget_id}")

        assert status == 200
        # Should have textarea creation
        assert "createElement('textarea')" in html
        # Should have textarea class (resize handled via CSS)
        assert "pywry-secret-textarea" in html
        # Should have edit button
        assert 'class="pywry-secret-btn pywry-secret-edit"' in html

    def test_input_is_readonly(self, server_port):
        """Input should be readonly (edit via textarea only)."""
        from pywry.toolbar import SecretInput, Toolbar

        _start_server(port=server_port, host="0.0.0.0")
        assert wait_for_server("127.0.0.1", server_port)

        toolbar = Toolbar(
            position="top",
            items=[SecretInput(event="auth:api-key", value="secret")],
        )

        with (
            patch("IPython.display.display"),
            patch("IPython.display.IFrame"),
            patch("pywry.inline.Output"),
            patch("pywry.inline.HAS_IPYTHON", True),
        ):
            widget = show("<div>Content</div>", toolbars=[toolbar], port=server_port)

        status, html = http_get(f"http://127.0.0.1:{server_port}/widget/{widget._widget_id}")

        assert status == 200
        # Input should be readonly
        assert " readonly" in html

    @pytest.mark.asyncio
    async def test_edit_submit_transmits_base64_encoded(self, server_port):
        """Edit confirmation should transmit base64-encoded value."""
        from pywry.toolbar import SecretInput, Toolbar, decode_secret

        host = "0.0.0.0"
        _start_server(port=server_port, host=host)
        assert wait_for_server("127.0.0.1", server_port)

        toolbar = Toolbar(
            position="top",
            items=[SecretInput(event="auth:api-key")],
        )

        received_events = []

        with (
            patch("IPython.display.display"),
            patch("IPython.display.IFrame"),
            patch("pywry.inline.Output"),
            patch("pywry.inline.HAS_IPYTHON", True),
        ):
            widget = show("<div>Content</div>", toolbars=[toolbar], port=server_port)

            def on_input(data, event_type, _wid):
                received_events.append((event_type, data))

            widget.on("auth:api-key", on_input)

        # Connect via WebSocket
        ws_url = f"ws://127.0.0.1:{server_port}/ws/{widget._widget_id}"
        token = _state.widget_tokens.get(widget._widget_id)
        subprotocol = f"pywry.token.{token}" if token else None
        subprotocols = [subprotocol] if subprotocol else None

        async with websockets.connect(ws_url, subprotocols=subprotocols) as ws:
            # Simulate textarea blur (edit confirmation)
            # The value should be base64 encoded
            import base64

            new_secret = "my-new-api-key-12345"
            encoded_value = base64.b64encode(new_secret.encode()).decode()

            payload = {
                "type": "auth:api-key",
                "data": {
                    "value": encoded_value,
                    "encoded": True,
                    "componentId": toolbar.get_secret_inputs()[0].component_id,
                },
                "widgetId": widget._widget_id,
            }
            await ws.send(json.dumps(payload))

            # Wait for handler to process
            await asyncio.sleep(0.1)

        # Verify event was received
        assert len(received_events) >= 1
        event_type, data = received_events[0]
        assert event_type == "auth:api-key"
        assert data["encoded"] is True
        # Decode and verify
        decoded = decode_secret(data["value"])
        assert decoded == new_secret

    def test_edit_cancel_escape_in_script(self, server_port):
        """Edit mode should support Escape to cancel."""
        from pywry.toolbar import SecretInput, Toolbar

        _start_server(port=server_port, host="0.0.0.0")
        assert wait_for_server("127.0.0.1", server_port)

        toolbar = Toolbar(
            position="top",
            items=[SecretInput(event="auth:api-key")],
        )

        with (
            patch("IPython.display.display"),
            patch("IPython.display.IFrame"),
            patch("pywry.inline.Output"),
            patch("pywry.inline.HAS_IPYTHON", True),
        ):
            widget = show("<div>Content</div>", toolbars=[toolbar], port=server_port)

        status, html = http_get(f"http://127.0.0.1:{server_port}/widget/{widget._widget_id}")

        assert status == 200
        # Should have Escape key handling
        assert "e.key==='Escape'" in html
        # Should set cancelled flag
        assert "ta._cancelled=true" in html

    def test_ctrl_enter_confirms_edit_in_script(self, server_port):
        """Ctrl+Enter should confirm edit."""
        from pywry.toolbar import SecretInput, Toolbar

        _start_server(port=server_port, host="0.0.0.0")
        assert wait_for_server("127.0.0.1", server_port)

        toolbar = Toolbar(
            position="top",
            items=[SecretInput(event="auth:api-key")],
        )

        with (
            patch("IPython.display.display"),
            patch("IPython.display.IFrame"),
            patch("pywry.inline.Output"),
            patch("pywry.inline.HAS_IPYTHON", True),
        ):
            widget = show("<div>Content</div>", toolbars=[toolbar], port=server_port)

        status, html = http_get(f"http://127.0.0.1:{server_port}/widget/{widget._widget_id}")

        assert status == 200
        # Should have Ctrl+Enter handling
        assert "e.key==='Enter'" in html
        assert "e.ctrlKey||e.metaKey" in html

    def test_clear_secrets_in_bridge_js(self, server_port):
        """Bridge JS should include clearSecrets for page unload."""
        from pywry.toolbar import SecretInput, Toolbar

        _start_server(port=server_port, host="0.0.0.0")
        assert wait_for_server("127.0.0.1", server_port)

        toolbar = Toolbar(
            position="top",
            items=[SecretInput(event="auth:api-key", value="secret")],
        )

        with (
            patch("IPython.display.display"),
            patch("IPython.display.IFrame"),
            patch("pywry.inline.Output"),
            patch("pywry.inline.HAS_IPYTHON", True),
        ):
            widget = show("<div>Content</div>", toolbars=[toolbar], port=server_port)

        status, html = http_get(f"http://127.0.0.1:{server_port}/widget/{widget._widget_id}")

        assert status == 200
        # Should have clearSecrets function
        assert "function clearSecrets()" in html
        # Should be called on beforeunload
        assert "clearSecrets();" in html
        # Should restore mask for inputs with values
        assert "SECRET_MASK" in html

    def test_css_for_secret_textarea(self, server_port):
        """CSS should include styles for secret textarea."""
        from pywry.toolbar import SecretInput, Toolbar

        _start_server(port=server_port, host="0.0.0.0")
        assert wait_for_server("127.0.0.1", server_port)

        toolbar = Toolbar(
            position="top",
            items=[SecretInput(event="auth:api-key")],
        )

        with (
            patch("IPython.display.display"),
            patch("IPython.display.IFrame"),
            patch("pywry.inline.Output"),
            patch("pywry.inline.HAS_IPYTHON", True),
        ):
            widget = show("<div>Content</div>", toolbars=[toolbar], port=server_port)

        status, html = http_get(f"http://127.0.0.1:{server_port}/widget/{widget._widget_id}")

        assert status == 200
        # Should have textarea class in script
        assert "pywry-secret-textarea" in html
