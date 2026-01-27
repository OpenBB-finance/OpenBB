"""End-to-end tests for Marquee component rendering across all paths.

Tests cover:
- Native window rendering with PyWry
- Inline notebook rendering with FastAPI server
- All Marquee features: direction, behavior, speed, pause, clickable, TickerItem
- Dynamic updates via toolbar:marquee-set-content and toolbar:marquee-set-item events
"""

# pylint: disable=too-many-lines

import time

from unittest.mock import patch

import pytest

from pywry.app import PyWry
from pywry.callbacks import get_registry
from pywry.inline import HAS_FASTAPI, _start_server, _state, show, stop_server
from pywry.models import ThemeMode
from pywry.toolbar import Button, Marquee, TickerItem, Toolbar

# Import shared test utilities from tests.conftest
from tests.conftest import show_and_wait_ready, wait_for_result


# Note: cleanup_runtime fixture is now in conftest.py and auto-used


class TestMarqueeNativeWindowRendering:
    """E2E tests for Marquee rendering in native PyWry windows."""

    def test_marquee_renders_with_correct_classes(self):
        """Marquee component renders with expected CSS classes."""
        app = PyWry(theme=ThemeMode.DARK)

        marquee = Marquee(
            text="Breaking news: Markets rally!",
            speed=20,
            direction="left",
            behavior="scroll",
            pause_on_hover=True,
            component_id="news-ticker",
        )
        toolbar = Toolbar(position="header", items=[marquee])

        label = show_and_wait_ready(app, "<div>Marquee Test</div>", toolbars=[toolbar])

        result = wait_for_result(
            label,
            """
            pywry.result({
                hasMarquee: !!document.querySelector('.pywry-marquee'),
                hasTrack: !!document.querySelector('.pywry-marquee-track'),
                hasContent: !!document.querySelector('.pywry-marquee-content'),
                hasHorizontal: !!document.querySelector('.pywry-marquee-horizontal'),
                hasPause: !!document.querySelector('.pywry-marquee-pause'),
                hasBehavior: !!document.querySelector('.pywry-marquee-scroll'),
                id: document.querySelector('.pywry-marquee')?.id
            });
            """,
        )

        assert result is not None, "Result not received"
        assert result["hasMarquee"], "Marquee container not found"
        assert result["hasTrack"], "Marquee track not found"
        assert result["hasContent"], "Marquee content not found"
        assert result["hasHorizontal"], "Horizontal class not found"
        assert result["hasPause"], "Pause class not found"
        assert result["hasBehavior"], "Behavior class not found"
        assert result["id"] == "news-ticker", f"ID mismatch: {result['id']}"
        app.close()

    def test_marquee_contains_text_content(self):
        """Marquee displays the provided text content."""
        app = PyWry(theme=ThemeMode.DARK)

        marquee = Marquee(
            text="AAPL $185.50 • GOOGL $142.20 • MSFT $415.80",
            speed=15,
            component_id="stock-ticker",
        )
        toolbar = Toolbar(position="header", items=[marquee])

        from tests.test_e2e import show_and_wait_ready

        label = show_and_wait_ready(app, "<div>Content Test</div>", toolbars=[toolbar])

        result = wait_for_result(
            label,
            """
            pywry.result({
                textContent: document.querySelector('.pywry-marquee-content')?.textContent,
                hasDuplicate: document.querySelectorAll('.pywry-marquee-content').length === 2
            });
            """,
        )

        assert result is not None, "Result not received"
        assert "AAPL" in result["textContent"], f"Content: {result['textContent']}"
        assert "GOOGL" in result["textContent"], f"Content: {result['textContent']}"
        assert result["hasDuplicate"], "Should have duplicated content for seamless scroll"
        app.close()

    def test_marquee_css_custom_properties(self):
        """Marquee sets CSS custom properties for speed and gap."""
        app = PyWry(theme=ThemeMode.DARK)

        marquee = Marquee(
            text="Test ticker",
            speed=25,
            gap=75,
            component_id="speed-test",
        )
        toolbar = Toolbar(position="header", items=[marquee])

        from tests.test_e2e import show_and_wait_ready

        label = show_and_wait_ready(app, "<div>CSS Props Test</div>", toolbars=[toolbar])

        result = wait_for_result(
            label,
            """
            var el = document.querySelector('.pywry-marquee');
            var style = el ? el.getAttribute('style') : '';
            pywry.result({
                hasSpeed: style.includes('--pywry-marquee-speed'),
                hasGap: style.includes('--pywry-marquee-gap'),
                style: style
            });
            """,
        )

        assert result is not None, "Result not received"
        assert result["hasSpeed"], f"Speed property not found: {result['style']}"
        assert result["hasGap"], f"Gap property not found: {result['style']}"
        assert "25" in result["style"], f"Speed value not found: {result['style']}"
        assert "75px" in result["style"], f"Gap value not found: {result['style']}"
        app.close()

    def test_marquee_vertical_direction(self):
        """Marquee with up/down direction has vertical class."""
        app = PyWry(theme=ThemeMode.DARK)

        marquee = Marquee(
            text="Scrolling up",
            direction="up",
            component_id="vertical-ticker",
        )
        toolbar = Toolbar(position="right", items=[marquee])

        from tests.test_e2e import show_and_wait_ready

        label = show_and_wait_ready(app, "<div>Vertical Test</div>", toolbars=[toolbar])

        result = wait_for_result(
            label,
            """
            pywry.result({
                hasVertical: !!document.querySelector('.pywry-marquee-vertical'),
                hasUp: !!document.querySelector('.pywry-marquee-up')
            });
            """,
        )

        assert result is not None, "Result not received"
        assert result["hasVertical"], "Vertical class not found"
        assert result["hasUp"], "Direction class not found"
        app.close()

    def test_marquee_clickable_emits_event(self):
        """Clickable marquee emits event when clicked."""
        app = PyWry(theme=ThemeMode.DARK)

        events = {"clicked": False, "data": None}

        def on_click(data):
            events["clicked"] = True
            events["data"] = data

        marquee = Marquee(
            text="Click me!",
            event="ticker:click",
            clickable=True,
            component_id="clickable-ticker",
        )
        toolbar = Toolbar(position="header", items=[marquee])

        from tests.test_e2e import show_and_wait_ready

        label = show_and_wait_ready(app, "<div>Click Test</div>", toolbars=[toolbar])
        get_registry().register(label, "ticker:click", on_click)

        # Click the marquee
        app.eval_js(
            "document.querySelector('.pywry-marquee-clickable').click();",
            label=label,
        )

        start = time.time()
        while not events["clicked"] and (time.time() - start) < 3.0:
            time.sleep(0.1)

        assert events["clicked"], "Marquee click event not received"
        app.close()

    def test_ticker_item_renders_with_data_attributes(self):
        """TickerItem renders with data-ticker attribute for targeting."""
        app = PyWry(theme=ThemeMode.DARK)

        items = [
            TickerItem(ticker="AAPL", text="AAPL $185.50", class_name="ticker-up"),
            TickerItem(ticker="GOOGL", text="GOOGL $142.20"),
            TickerItem(ticker="MSFT", text="MSFT $415.80", class_name="ticker-down"),
        ]

        marquee = Marquee(
            text=" • ".join(item.build_html() for item in items),
            speed=20,
            component_id="ticker-items",
        )
        toolbar = Toolbar(position="header", items=[marquee])

        from tests.test_e2e import show_and_wait_ready

        label = show_and_wait_ready(app, "<div>TickerItem Test</div>", toolbars=[toolbar])

        result = wait_for_result(
            label,
            """
            var items = document.querySelectorAll('.pywry-ticker-item');
            var tickers = [];
            items.forEach(function(el) { tickers.push(el.dataset.ticker); });
            pywry.result({
                count: items.length,
                tickers: tickers,
                hasUpClass: !!document.querySelector('.ticker-up'),
                hasDownClass: !!document.querySelector('.ticker-down')
            });
            """,
        )

        assert result is not None, "Result not received"
        # Each content span is duplicated, so we should have 6 ticker items (3 * 2)
        assert result["count"] >= 3, f"Expected at least 3 ticker items, got {result['count']}"
        assert "AAPL" in result["tickers"], f"AAPL not found: {result['tickers']}"
        assert "GOOGL" in result["tickers"], f"GOOGL not found: {result['tickers']}"
        assert result["hasUpClass"], "ticker-up class not found"
        assert result["hasDownClass"], "ticker-down class not found"
        app.close()

    def test_marquee_update_via_set_content_event(self):
        """Marquee content can be updated via toolbar:marquee-set-content event."""
        app = PyWry(theme=ThemeMode.DARK)

        marquee = Marquee(
            text="Initial content",
            speed=15,
            component_id="updatable-ticker",
        )
        button = Button(label="Update", event="update:trigger")
        toolbar = Toolbar(position="header", items=[marquee])
        toolbar2 = Toolbar(position="top", items=[button])

        update_received = {"done": False}

        def on_update(data):
            # Trigger marquee content update via emit (not dispatch)
            app.emit(
                "toolbar:marquee-set-content",
                {"id": "updatable-ticker", "text": "Updated content!"},
            )
            update_received["done"] = True

        from tests.test_e2e import show_and_wait_ready

        label = show_and_wait_ready(app, "<div>Update Test</div>", toolbars=[toolbar, toolbar2])
        get_registry().register(label, "update:trigger", on_update)

        # Click the update button
        app.eval_js("document.querySelector('.pywry-btn').click();", label=label)

        start = time.time()
        while not update_received["done"] and (time.time() - start) < 3.0:
            time.sleep(0.1)

        assert update_received["done"], "Update trigger not received"

        # Wait a bit for DOM update
        time.sleep(0.3)

        result = wait_for_result(
            label,
            """
            pywry.result({
                text: document.querySelector('.pywry-marquee-content')?.textContent
            });
            """,
        )

        assert result is not None, "Result not received"
        assert "Updated content" in result["text"], f"Content not updated: {result['text']}"
        app.close()


# =============================================================================
# Inline Notebook E2E Tests
# =============================================================================


# Skip all inline tests if FastAPI not installed
pytestmark_inline = pytest.mark.skipif(not HAS_FASTAPI, reason="FastAPI not installed")


@pytest.fixture
def server_port():
    """Get a free port that's not in use."""
    import socket

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("0.0.0.0", 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return s.getsockname()[1]


@pytest.fixture(autouse=True)
def clean_inline_state(server_port):  # pylint: disable=redefined-outer-name
    """Clean up inline server state."""
    stop_server()
    _state.widgets.clear()
    _state.connections.clear()
    _state.local_widgets.clear()
    _state.widget_tokens.clear()
    yield
    stop_server()
    _state.widgets.clear()
    _state.connections.clear()
    _state.local_widgets.clear()
    _state.widget_tokens.clear()


def wait_for_server(host: str, port: int, timeout: float = 5.0) -> bool:
    """Wait for inline server to be ready."""
    import socket as sock_mod

    start = time.time()
    while time.time() - start < timeout:
        try:
            with sock_mod.socket(sock_mod.AF_INET, sock_mod.SOCK_STREAM) as s:
                s.settimeout(0.5)
                result = s.connect_ex((host, port))
                if result == 0:
                    return True
        except Exception:  # noqa: S110
            pass
        time.sleep(0.1)
    return False


def http_get(url: str, timeout: float = 5.0) -> tuple[int, str]:
    """Make HTTP GET request."""
    import urllib.error
    import urllib.request

    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:  # noqa: S310
            return resp.status, resp.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8")


class MockOutput:
    """Mock for IPython.display.Output."""

    def __init__(self):
        self.outputs = []

    def append_display_data(self, data):
        self.outputs.append(data)


@pytest.mark.skipif(not HAS_FASTAPI, reason="FastAPI not installed")
class TestMarqueeInlineRendering:
    """E2E tests for Marquee rendering in inline notebook mode."""

    def test_marquee_html_served_via_http(self, server_port):
        """Marquee HTML is correctly served via inline HTTP server."""
        _start_server(port=server_port, host="0.0.0.0")
        assert wait_for_server("127.0.0.1", server_port)

        marquee = Marquee(
            text="Breaking news!",
            speed=20,
            direction="left",
            pause_on_hover=True,
            component_id="inline-ticker",
        )
        toolbar = Toolbar(position="header", items=[marquee])

        with (
            patch("IPython.display.display"),
            patch("IPython.display.IFrame"),
            patch("pywry.inline.Output", MockOutput),
            patch("pywry.inline.HAS_IPYTHON", True),
        ):
            widget = show("<div>Inline Marquee</div>", toolbars=[toolbar], port=server_port)

        status, html = http_get(f"http://127.0.0.1:{server_port}/widget/{widget._widget_id}")

        assert status == 200
        assert "pywry-marquee" in html
        assert "pywry-marquee-track" in html
        assert "pywry-marquee-content" in html
        assert "Breaking news!" in html
        assert "inline-ticker" in html

    def test_marquee_css_custom_properties_in_html(self, server_port):
        """Marquee CSS custom properties are present in served HTML."""
        _start_server(port=server_port, host="0.0.0.0")
        assert wait_for_server("127.0.0.1", server_port)

        marquee = Marquee(
            text="Speed test",
            speed=30,
            gap=100,
            component_id="speed-ticker",
        )
        toolbar = Toolbar(position="header", items=[marquee])

        with (
            patch("IPython.display.display"),
            patch("IPython.display.IFrame"),
            patch("pywry.inline.Output", MockOutput),
            patch("pywry.inline.HAS_IPYTHON", True),
        ):
            widget = show("<div>CSS Test</div>", toolbars=[toolbar], port=server_port)

        status, html = http_get(f"http://127.0.0.1:{server_port}/widget/{widget._widget_id}")

        assert status == 200
        assert "--pywry-marquee-speed: 30" in html
        assert "--pywry-marquee-gap: 100px" in html

    def test_marquee_direction_classes(self, server_port):
        """Marquee direction classes are correctly applied."""
        _start_server(port=server_port, host="0.0.0.0")
        assert wait_for_server("127.0.0.1", server_port)

        # Test vertical direction
        marquee = Marquee(
            text="Vertical scroll",
            direction="up",
            component_id="vertical-ticker",
        )
        toolbar = Toolbar(position="right", items=[marquee])

        with (
            patch("IPython.display.display"),
            patch("IPython.display.IFrame"),
            patch("pywry.inline.Output", MockOutput),
            patch("pywry.inline.HAS_IPYTHON", True),
        ):
            widget = show("<div>Direction Test</div>", toolbars=[toolbar], port=server_port)

        status, html = http_get(f"http://127.0.0.1:{server_port}/widget/{widget._widget_id}")

        assert status == 200
        assert "pywry-marquee-vertical" in html
        assert "pywry-marquee-up" in html

    def test_marquee_behavior_classes(self, server_port):
        """Marquee behavior classes are correctly applied."""
        _start_server(port=server_port, host="0.0.0.0")
        assert wait_for_server("127.0.0.1", server_port)

        marquee = Marquee(
            text="Bouncing text",
            behavior="alternate",
            component_id="bounce-ticker",
        )
        toolbar = Toolbar(position="header", items=[marquee])

        with (
            patch("IPython.display.display"),
            patch("IPython.display.IFrame"),
            patch("pywry.inline.Output", MockOutput),
            patch("pywry.inline.HAS_IPYTHON", True),
        ):
            widget = show("<div>Behavior Test</div>", toolbars=[toolbar], port=server_port)

        status, html = http_get(f"http://127.0.0.1:{server_port}/widget/{widget._widget_id}")

        assert status == 200
        assert "pywry-marquee-alternate" in html

    def test_marquee_clickable_attributes(self, server_port):
        """Clickable marquee has correct data attributes."""
        _start_server(port=server_port, host="0.0.0.0")
        assert wait_for_server("127.0.0.1", server_port)

        marquee = Marquee(
            text="Click me",
            event="ticker:click",
            clickable=True,
            component_id="click-ticker",
        )
        toolbar = Toolbar(position="header", items=[marquee])

        with (
            patch("IPython.display.display"),
            patch("IPython.display.IFrame"),
            patch("pywry.inline.Output", MockOutput),
            patch("pywry.inline.HAS_IPYTHON", True),
        ):
            widget = show("<div>Click Test</div>", toolbars=[toolbar], port=server_port)

        status, html = http_get(f"http://127.0.0.1:{server_port}/widget/{widget._widget_id}")

        assert status == 200
        assert "pywry-marquee-clickable" in html
        assert 'data-event="ticker:click"' in html

    def test_ticker_items_in_marquee(self, server_port):
        """TickerItems render correctly inside Marquee."""
        _start_server(port=server_port, host="0.0.0.0")
        assert wait_for_server("127.0.0.1", server_port)

        items = [
            TickerItem(ticker="AAPL", text="AAPL $185.50", class_name="stock-up"),
            TickerItem(ticker="GOOGL", text="GOOGL $142.20"),
        ]

        marquee = Marquee(
            text=" • ".join(item.build_html() for item in items),
            speed=20,
            component_id="stock-ticker",
        )
        toolbar = Toolbar(position="header", items=[marquee])

        with (
            patch("IPython.display.display"),
            patch("IPython.display.IFrame"),
            patch("pywry.inline.Output", MockOutput),
            patch("pywry.inline.HAS_IPYTHON", True),
        ):
            widget = show("<div>Ticker Items</div>", toolbars=[toolbar], port=server_port)

        status, html = http_get(f"http://127.0.0.1:{server_port}/widget/{widget._widget_id}")

        assert status == 200
        assert "pywry-ticker-item" in html
        assert 'data-ticker="AAPL"' in html
        assert 'data-ticker="GOOGL"' in html
        assert "stock-up" in html
        assert "AAPL $185.50" in html

    def test_marquee_with_separator(self, server_port):
        """Marquee with separator displays separator element."""
        _start_server(port=server_port, host="0.0.0.0")
        assert wait_for_server("127.0.0.1", server_port)

        marquee = Marquee(
            text="Item 1",
            separator=" • ",
            component_id="sep-ticker",
        )
        toolbar = Toolbar(position="header", items=[marquee])

        with (
            patch("IPython.display.display"),
            patch("IPython.display.IFrame"),
            patch("pywry.inline.Output", MockOutput),
            patch("pywry.inline.HAS_IPYTHON", True),
        ):
            widget = show("<div>Separator Test</div>", toolbars=[toolbar], port=server_port)

        status, html = http_get(f"http://127.0.0.1:{server_port}/widget/{widget._widget_id}")

        assert status == 200
        assert "pywry-marquee-separator" in html
        assert " • " in html

    def test_marquee_pause_class_when_enabled(self, server_port):
        """Marquee has pause class when pause_on_hover is True."""
        _start_server(port=server_port, host="0.0.0.0")
        assert wait_for_server("127.0.0.1", server_port)

        marquee = Marquee(
            text="Pausable",
            pause_on_hover=True,
            component_id="pause-ticker",
        )
        toolbar = Toolbar(position="header", items=[marquee])

        with (
            patch("IPython.display.display"),
            patch("IPython.display.IFrame"),
            patch("pywry.inline.Output", MockOutput),
            patch("pywry.inline.HAS_IPYTHON", True),
        ):
            widget = show("<div>Pause Test</div>", toolbars=[toolbar], port=server_port)

        status, html = http_get(f"http://127.0.0.1:{server_port}/widget/{widget._widget_id}")

        assert status == 200
        assert "pywry-marquee-pause" in html

    def test_marquee_no_pause_class_when_disabled(self, server_port):
        """Marquee lacks pause class when pause_on_hover is False."""
        _start_server(port=server_port, host="0.0.0.0")
        assert wait_for_server("127.0.0.1", server_port)

        marquee = Marquee(
            text="No pause",
            pause_on_hover=False,
            component_id="nopause-ticker",
        )
        toolbar = Toolbar(position="header", items=[marquee])

        with (
            patch("IPython.display.display"),
            patch("IPython.display.IFrame"),
            patch("pywry.inline.Output", MockOutput),
            patch("pywry.inline.HAS_IPYTHON", True),
        ):
            widget = show("<div>No Pause Test</div>", toolbars=[toolbar], port=server_port)

        status, html = http_get(f"http://127.0.0.1:{server_port}/widget/{widget._widget_id}")

        assert status == 200
        # Check the marquee element itself doesn't have the pause class
        # (CSS file will contain the class name in <style> tag)
        assert (
            'class="pywry-marquee pywry-marquee-left pywry-marquee-scroll pywry-marquee-horizontal"'
            in html
        )
        assert 'id="nopause-ticker"' in html

    def test_marquee_with_label(self, server_port):
        """Marquee with label renders label element."""
        _start_server(port=server_port, host="0.0.0.0")
        assert wait_for_server("127.0.0.1", server_port)

        marquee = Marquee(
            label="News:",
            text="Breaking headlines",
            component_id="labeled-ticker",
        )
        toolbar = Toolbar(position="header", items=[marquee])

        with (
            patch("IPython.display.display"),
            patch("IPython.display.IFrame"),
            patch("pywry.inline.Output", MockOutput),
            patch("pywry.inline.HAS_IPYTHON", True),
        ):
            widget = show("<div>Label Test</div>", toolbars=[toolbar], port=server_port)

        status, html = http_get(f"http://127.0.0.1:{server_port}/widget/{widget._widget_id}")

        assert status == 200
        assert "News:" in html
        assert "pywry-input-label" in html

    def test_marquee_js_handlers_included(self, server_port):
        """Marquee update JS handlers are included in served HTML."""
        _start_server(port=server_port, host="0.0.0.0")
        assert wait_for_server("127.0.0.1", server_port)

        marquee = Marquee(
            text="Updatable content",
            component_id="handler-ticker",
        )
        toolbar = Toolbar(position="header", items=[marquee])

        with (
            patch("IPython.display.display"),
            patch("IPython.display.IFrame"),
            patch("pywry.inline.Output", MockOutput),
            patch("pywry.inline.HAS_IPYTHON", True),
        ):
            widget = show("<div>Handler Test</div>", toolbars=[toolbar], port=server_port)

        status, html = http_get(f"http://127.0.0.1:{server_port}/widget/{widget._widget_id}")

        assert status == 200
        # Check that marquee update handlers are present in the JS
        assert "toolbar:marquee-set-content" in html
        assert "toolbar:marquee-set-item" in html


@pytest.mark.skipif(not HAS_FASTAPI, reason="FastAPI not installed")
class TestMarqueeUpdatePayload:
    """Test Marquee.update_payload() helper method integration."""

    def test_update_payload_returns_correct_event(self):
        """update_payload() returns correct event name."""
        marquee = Marquee(
            text="Initial",
            component_id="payload-ticker",
        )
        event, payload = marquee.update_payload(text="Updated")

        assert event == "toolbar:marquee-set-content"
        assert payload["id"] == "payload-ticker"
        assert payload["text"] == "Updated"

    def test_update_payload_speed(self):
        """update_payload() includes speed when specified."""
        marquee = Marquee(text="Test", component_id="speed-test")
        event, payload = marquee.update_payload(speed=10.0)

        assert event == "toolbar:marquee-set-content"
        assert payload["speed"] == 10.0

    def test_update_payload_paused(self):
        """update_payload() includes paused state."""
        marquee = Marquee(text="Test", component_id="pause-test")
        event, payload = marquee.update_payload(paused=True)

        assert event == "toolbar:marquee-set-content"
        assert payload["paused"] is True


@pytest.mark.skipif(not HAS_FASTAPI, reason="FastAPI not installed")
class TestTickerItemUpdatePayload:
    """Test TickerItem.update_payload() helper method integration."""

    def test_ticker_item_update_payload_text(self):
        """update_payload() returns correct event for TickerItem."""
        item = TickerItem(ticker="AAPL", text="AAPL $185.50")
        event, payload = item.update_payload(text="AAPL $186.25")

        assert event == "toolbar:marquee-set-item"
        assert payload["ticker"] == "AAPL"
        assert payload["text"] == "AAPL $186.25"

    def test_ticker_item_update_payload_class_add(self):
        """update_payload() includes class_add."""
        item = TickerItem(ticker="AAPL", text="Test")
        _event, payload = item.update_payload(class_add="stock-up")

        assert payload["class_add"] == "stock-up"

    def test_ticker_item_update_payload_class_remove(self):
        """update_payload() includes class_remove."""
        item = TickerItem(ticker="AAPL", text="Test")
        _event, payload = item.update_payload(class_remove="stock-down")

        assert payload["class_remove"] == "stock-down"

    def test_ticker_item_update_payload_styles(self):
        """update_payload() includes styles dict."""
        item = TickerItem(ticker="AAPL", text="Test")
        _event, payload = item.update_payload(styles={"color": "#22c55e"})

        assert payload["styles"]["color"] == "#22c55e"


@pytest.mark.skipif(not HAS_FASTAPI, reason="FastAPI not installed")
class TestMarqueeStaticBehavior:
    """Test static marquee behavior with auto-cycling items."""

    @pytest.fixture(autouse=True)
    def server_setup(self, server_port):
        """Setup server for each test."""
        _start_server(port=server_port, host="0.0.0.0")
        assert wait_for_server("127.0.0.1", server_port)
        yield
        stop_server()

    def test_static_marquee_has_correct_class(self, server_port):
        """Static marquee has pywry-marquee-static class."""
        marquee = Marquee(
            text="Static content",
            behavior="static",
            component_id="static-ticker",
        )
        toolbar = Toolbar(position="header", items=[marquee])

        with (
            patch("IPython.display.display"),
            patch("IPython.display.IFrame"),
            patch("pywry.inline.Output", MockOutput),
            patch("pywry.inline.HAS_IPYTHON", True),
        ):
            widget = show("<div>Static Test</div>", toolbars=[toolbar], port=server_port)

        status, html = http_get(f"http://127.0.0.1:{server_port}/widget/{widget._widget_id}")

        assert status == 200
        assert "pywry-marquee-static" in html

    def test_static_marquee_single_content_span(self, server_port):
        """Static marquee renders single content span (no duplicate for animation)."""
        marquee = Marquee(
            text="Single span",
            behavior="static",
            component_id="single-span-ticker",
        )
        toolbar = Toolbar(position="header", items=[marquee])

        with (
            patch("IPython.display.display"),
            patch("IPython.display.IFrame"),
            patch("pywry.inline.Output", MockOutput),
            patch("pywry.inline.HAS_IPYTHON", True),
        ):
            widget = show("<div>Single Span Test</div>", toolbars=[toolbar], port=server_port)

        status, html = http_get(f"http://127.0.0.1:{server_port}/widget/{widget._widget_id}")

        assert status == 200
        # Static marquee should not have duplicate content span (used for seamless animation loop)
        # Check that there's no content span with aria-hidden="true" within our marquee
        assert 'pywry-marquee-content" aria-hidden="true"' not in html

    def test_static_marquee_with_items_has_data_attributes(self, server_port):
        """Static marquee with items has data-items and data-speed attributes."""
        items = ["News item 1", "News item 2", "News item 3"]
        marquee = Marquee(
            text=items[0],
            items=items,
            speed=5,
            behavior="static",
            component_id="items-ticker",
        )
        toolbar = Toolbar(position="header", items=[marquee])

        with (
            patch("IPython.display.display"),
            patch("IPython.display.IFrame"),
            patch("pywry.inline.Output", MockOutput),
            patch("pywry.inline.HAS_IPYTHON", True),
        ):
            widget = show("<div>Items Test</div>", toolbars=[toolbar], port=server_port)

        status, html = http_get(f"http://127.0.0.1:{server_port}/widget/{widget._widget_id}")

        assert status == 200
        assert "data-items=" in html
        assert "data-speed=" in html
        assert "News item 1" in html
        assert "News item 2" in html
        assert "News item 3" in html

    def test_static_marquee_items_json_escaped(self, server_port):
        """Static marquee items are properly JSON-escaped in data attribute."""
        items = ['Item with "quotes"', "Item with <html>"]
        marquee = Marquee(
            text=items[0],
            items=items,
            speed=3,
            behavior="static",
            component_id="escape-ticker",
        )
        toolbar = Toolbar(position="header", items=[marquee])

        with (
            patch("IPython.display.display"),
            patch("IPython.display.IFrame"),
            patch("pywry.inline.Output", MockOutput),
            patch("pywry.inline.HAS_IPYTHON", True),
        ):
            widget = show("<div>Escape Test</div>", toolbars=[toolbar], port=server_port)

        status, html = http_get(f"http://127.0.0.1:{server_port}/widget/{widget._widget_id}")

        assert status == 200
        # HTML should be valid (not break due to unescaped quotes/brackets)
        assert 'id="escape-ticker"' in html
        assert "data-items=" in html

    def test_static_marquee_without_items_no_data_attributes(self, server_port):
        """Static marquee without items list has no data-items attribute."""
        marquee = Marquee(
            text="Just text, no cycling",
            behavior="static",
            component_id="noitems-ticker",
        )
        toolbar = Toolbar(position="header", items=[marquee])

        with (
            patch("IPython.display.display"),
            patch("IPython.display.IFrame"),
            patch("pywry.inline.Output", MockOutput),
            patch("pywry.inline.HAS_IPYTHON", True),
        ):
            widget = show("<div>No Items Test</div>", toolbars=[toolbar], port=server_port)

        status, html = http_get(f"http://127.0.0.1:{server_port}/widget/{widget._widget_id}")

        assert status == 200
        assert 'id="noitems-ticker"' in html
        # Should not have data-items attribute when items is not provided
        assert "data-items=" not in html.split('id="noitems-ticker"')[1].split(">")[0]


class TestMarqueeStaticBuildHtml:
    """Unit tests for static marquee HTML generation."""

    def test_static_behavior_accepted(self):
        """Static is a valid behavior option."""
        marquee = Marquee(
            text="Test",
            behavior="static",
            component_id="static-test",
        )
        html = marquee.build_html()

        assert "pywry-marquee-static" in html

    def test_items_field_accepted(self):
        """Items list field is accepted."""
        marquee = Marquee(
            text="First item",
            items=["First item", "Second item", "Third item"],
            behavior="static",
            component_id="items-test",
        )
        html = marquee.build_html()

        assert "data-items=" in html
        assert "data-speed=" in html

    def test_items_only_added_for_static_behavior(self):
        """Items data attribute only added when behavior is static."""
        marquee = Marquee(
            text="Scrolling",
            items=["Item 1", "Item 2"],
            behavior="scroll",  # Not static
            component_id="scroll-items-test",
        )
        html = marquee.build_html()

        # Items should NOT be in data attributes for scrolling marquee
        assert "data-items=" not in html

    def test_speed_in_data_attribute_for_static_items(self):
        """Speed value is included in data-speed for static with items."""
        marquee = Marquee(
            text="Test",
            items=["A", "B"],
            speed=7.5,
            behavior="static",
            component_id="speed-test",
        )
        html = marquee.build_html()

        assert 'data-speed="7.5"' in html
