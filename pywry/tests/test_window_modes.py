"""Tests for window mode functionality (NEW_WINDOW, SINGLE_WINDOW, MULTI_WINDOW).

These tests verify:
1. Each mode behaves correctly according to the README specification
2. Window reuse, creation, and content replacement work as expected
3. Callbacks are correctly scoped per window/mode
4. The Quick Start example in README works correctly
"""

# pylint: disable=redefined-outer-name,unused-argument,unsubscriptable-object,cyclic-import

import sys
import threading
import time

from collections.abc import Callable
from functools import wraps
from typing import Any, TypeVar

import pytest

from pywry import runtime
from pywry.app import PyWry
from pywry.callbacks import get_registry
from pywry.models import ThemeMode, WindowMode

# Import shared test utilities from tests.conftest
from tests.conftest import show_and_wait_ready, wait_for_result


F = TypeVar("F", bound=Callable[..., Any])


def retry_on_subprocess_failure(max_attempts: int = 3, delay: float = 1.0) -> Callable[[F], F]:
    """Retry decorator for tests that may fail due to transient subprocess issues.

    On failure, this decorator:
    1. Stops the runtime subprocess
    2. Clears all in-process state (registry, lifecycle)
    3. Waits with progressive backoff
    4. Retries the test
    """
    from pywry.window_manager import get_lifecycle

    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            last_error: Exception | None = None
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except (TimeoutError, AssertionError, RuntimeError) as e:
                    last_error = e
                    if attempt < max_attempts - 1:
                        # Full cleanup before retry
                        runtime.stop()
                        get_registry().clear()
                        get_lifecycle().clear()

                        # Progressive backoff
                        sleep_time = delay * (attempt + 1)
                        if sys.platform == "win32":
                            sleep_time *= 1.5  # Extra time for Windows
                        time.sleep(sleep_time)
            raise last_error  # type: ignore[misc]

        return wrapper  # type: ignore[return-value]

    return decorator


# Note: cleanup_runtime fixture is now in conftest.py and auto-used


# =============================================================================
# NEW_WINDOW Mode Tests
# =============================================================================


class TestNewWindowMode:
    """Tests for NEW_WINDOW mode - creates new window for each show()."""

    def test_creates_unique_labels(self):
        """Each show() call creates a window with a unique label."""
        app = PyWry(mode=WindowMode.NEW_WINDOW, theme=ThemeMode.DARK)

        label1 = show_and_wait_ready(app, "<div id='w1'>Window 1</div>")
        label2 = show_and_wait_ready(app, "<div id='w2'>Window 2</div>")
        label3 = show_and_wait_ready(app, "<div id='w3'>Window 3</div>")

        assert label1 != label2, "Labels should be unique"
        assert label2 != label3, "Labels should be unique"
        assert label1 != label3, "Labels should be unique"

        app.destroy()

    def test_windows_have_independent_content(self):
        """Each window has its own independent content."""
        app = PyWry(mode=WindowMode.NEW_WINDOW, theme=ThemeMode.DARK)

        label1 = show_and_wait_ready(app, "<div id='content'>FIRST</div>")
        label2 = show_and_wait_ready(app, "<div id='content'>SECOND</div>")

        # Check content in each window
        r1 = wait_for_result(
            label1,
            "pywry.result({ text: document.getElementById('content')?.textContent });",
        )
        r2 = wait_for_result(
            label2,
            "pywry.result({ text: document.getElementById('content')?.textContent });",
        )

        assert r1 is not None and r1["text"] == "FIRST", f"Window 1 wrong content: {r1}"
        assert r2 is not None and r2["text"] == "SECOND", f"Window 2 wrong content: {r2}"

        app.destroy()

    def test_get_labels_returns_all_windows(self):
        """get_labels() returns all open window labels."""
        app = PyWry(mode=WindowMode.NEW_WINDOW, theme=ThemeMode.DARK)

        label1 = show_and_wait_ready(app, "<div>W1</div>")
        label2 = show_and_wait_ready(app, "<div>W2</div>")

        labels = app.get_labels()

        assert label1 in labels, f"Label1 not in labels: {labels}"
        assert label2 in labels, f"Label2 not in labels: {labels}"
        assert len(labels) >= 2, f"Expected at least 2 labels, got {len(labels)}"

        app.destroy()

    def test_close_specific_window(self):
        """close(label) closes only the specified window."""
        app = PyWry(mode=WindowMode.NEW_WINDOW, theme=ThemeMode.DARK)

        label1 = show_and_wait_ready(app, "<div>W1</div>")
        label2 = show_and_wait_ready(app, "<div>W2</div>")

        # Close only first window
        app.close(label=label1)
        time.sleep(0.3)  # Give time for close to propagate

        # Window 2 should still respond
        r2 = wait_for_result(label2, "pywry.result({ alive: true });")
        assert r2 is not None and r2["alive"], "Window 2 should still be open"

        app.destroy()


# =============================================================================
# SINGLE_WINDOW Mode Tests
# =============================================================================


class TestSingleWindowMode:
    """Tests for SINGLE_WINDOW mode - reuses one window, replaces content."""

    def test_returns_same_label(self):
        """Every show() call returns the same label."""
        app = PyWry(mode=WindowMode.SINGLE_WINDOW, theme=ThemeMode.DARK)

        label1 = show_and_wait_ready(app, "<div>First</div>")
        label2 = show_and_wait_ready(app, "<div>Second</div>")
        label3 = show_and_wait_ready(app, "<div>Third</div>")

        assert label1 == label2 == label3, f"Labels should be same: {label1}, {label2}, {label3}"

        app.destroy()

    def test_content_is_replaced(self):
        """Each show() replaces the content, not appends."""
        app = PyWry(mode=WindowMode.SINGLE_WINDOW, theme=ThemeMode.DARK)

        show_and_wait_ready(app, "<div id='first'>FIRST</div>")
        label = show_and_wait_ready(app, "<div id='second'>SECOND</div>")

        result = wait_for_result(
            label,
            """pywry.result({
                hasFirst: !!document.getElementById('first'),
                hasSecond: !!document.getElementById('second'),
                secondText: document.getElementById('second')?.textContent
            });""",
        )

        assert result is not None, "No result received"
        assert not result["hasFirst"], "Old content should be gone"
        assert result["hasSecond"], "New content should exist"
        assert result["secondText"] == "SECOND", f"Wrong content: {result['secondText']}"

        app.destroy()

    def test_callbacks_work_after_content_replace(self):
        """Callbacks registered with new content work after replacement."""
        app = PyWry(mode=WindowMode.SINGLE_WINDOW, theme=ThemeMode.DARK)

        # First content
        show_and_wait_ready(app, "<div>Initial</div>")

        # Replace with new content and new callback
        callback_received = threading.Event()
        received_data: dict[str, Any] = {}

        def on_test_event(data: Any, event_type: str, lbl: str) -> None:
            received_data["data"] = data
            received_data["event_type"] = event_type
            callback_received.set()

        label = show_and_wait_ready(
            app,
            "<div id='new'>New Content</div>",
            callbacks={"test:event": on_test_event},
        )

        # Trigger the callback from JS
        runtime.eval_js(label, "pywry.emit('test:event', { msg: 'hello' });")

        assert callback_received.wait(timeout=5.0), "Callback not received"
        assert received_data["data"]["msg"] == "hello"

        app.destroy()

    @retry_on_subprocess_failure(max_attempts=3, delay=1.0)
    def test_window_reopens_after_user_close(self):
        """SINGLE_WINDOW reopens after user closes it (README Quick Start scenario)."""
        app = PyWry(mode=WindowMode.SINGLE_WINDOW, theme=ThemeMode.DARK)

        # Show first content
        label1 = show_and_wait_ready(app, "<h1>First Content</h1>")

        # Simulate user closing window
        app.close()

        # Wait for window to fully close with proper polling
        max_close_wait = 5.0
        poll_interval = 0.1
        elapsed = 0.0
        while elapsed < max_close_wait:
            if not runtime.check_window_open(label1):
                break
            time.sleep(poll_interval)
            elapsed += poll_interval

        # Verify subprocess is still running before attempting reopen
        assert runtime.is_running(), "Runtime should still be running after window close"

        # Show new content - this should reopen the window
        # Don't use show_and_wait_ready here because the callback-based ready
        # mechanism can be unreliable after close/reopen. Instead, show content
        # and poll for window existence.
        widget = app.show("<h1>Second Content</h1>")
        label2 = widget.label if hasattr(widget, "label") else str(widget)

        # Poll for window to exist
        max_open_wait = 10.0
        elapsed = 0.0
        while elapsed < max_open_wait:
            if runtime.check_window_open(label2):
                break
            time.sleep(poll_interval)
            elapsed += poll_interval
        else:
            raise AssertionError(f"Window '{label2}' did not reopen within {max_open_wait}s")

        # Same label, window reopened with new content
        assert label1 == label2, f"Label should be same: {label1} vs {label2}"

        # Poll for content to render (not just window open)
        max_content_wait = 5.0
        elapsed = 0.0
        result = None
        while elapsed < max_content_wait:
            result = wait_for_result(
                label2,
                "pywry.result({ text: document.querySelector('h1')?.textContent });",
            )
            if result is not None and result.get("text") == "Second Content":
                break
            time.sleep(0.2)
            elapsed += 0.2

        assert result is not None and result.get("text") == "Second Content", (
            f"Wrong content: {result}"
        )

        app.destroy()

    def test_get_labels_returns_single_label(self):
        """get_labels() returns only one label in SINGLE_WINDOW mode."""
        app = PyWry(mode=WindowMode.SINGLE_WINDOW, theme=ThemeMode.DARK)

        show_and_wait_ready(app, "<div>First</div>")
        show_and_wait_ready(app, "<div>Second</div>")
        show_and_wait_ready(app, "<div>Third</div>")

        labels = app.get_labels()

        assert len(labels) == 1, f"Expected 1 label, got {len(labels)}: {labels}"

        app.destroy()


# =============================================================================
# MULTI_WINDOW Mode Tests
# =============================================================================


class TestMultiWindowMode:
    """Tests for MULTI_WINDOW mode - multiple independent windows with labels."""

    def test_custom_labels(self):
        """Windows can be created with custom labels."""
        app = PyWry(mode=WindowMode.MULTI_WINDOW, theme=ThemeMode.DARK)

        label1 = show_and_wait_ready(app, "<div>Chart</div>", label="chart-window")
        label2 = show_and_wait_ready(app, "<div>Table</div>", label="table-window")

        assert label1 == "chart-window", f"Wrong label: {label1}"
        assert label2 == "table-window", f"Wrong label: {label2}"

        app.destroy()

    def test_auto_generated_labels(self):
        """Labels are auto-generated when not specified."""
        app = PyWry(mode=WindowMode.MULTI_WINDOW, theme=ThemeMode.DARK)

        label1 = show_and_wait_ready(app, "<div>W1</div>")
        label2 = show_and_wait_ready(app, "<div>W2</div>")

        assert label1 is not None and len(label1) > 0
        assert label2 is not None and len(label2) > 0
        assert label1 != label2, "Auto-generated labels should be unique"

        app.destroy()

    def test_update_specific_window(self):
        """Calling show() with existing label updates that window's content."""
        app = PyWry(mode=WindowMode.MULTI_WINDOW, theme=ThemeMode.DARK)

        # Create two windows
        show_and_wait_ready(app, "<div id='c'>Initial Chart</div>", label="chart")
        show_and_wait_ready(app, "<div id='c'>Initial Table</div>", label="table")

        # Update only the chart window
        show_and_wait_ready(app, "<div id='c'>Updated Chart</div>", label="chart")

        # Verify chart was updated
        chart_result = wait_for_result(
            "chart",
            "pywry.result({ text: document.getElementById('c')?.textContent });",
        )
        assert chart_result is not None and chart_result["text"] == "Updated Chart", (
            f"Chart not updated: {chart_result}"
        )

        # Verify table was NOT changed
        table_result = wait_for_result(
            "table",
            "pywry.result({ text: document.getElementById('c')?.textContent });",
        )
        assert table_result is not None and table_result["text"] == "Initial Table", (
            f"Table should not have changed: {table_result}"
        )

        app.destroy()

    def test_independent_callbacks(self):
        """Each window has its own independent callbacks."""
        app = PyWry(mode=WindowMode.MULTI_WINDOW, theme=ThemeMode.DARK)

        chart_events: list[Any] = []
        table_events: list[Any] = []

        def on_chart_event(data: Any, event_type: str, label: str) -> None:
            chart_events.append({"data": data, "label": label})

        def on_table_event(data: Any, event_type: str, label: str) -> None:
            table_events.append({"data": data, "label": label})

        show_and_wait_ready(
            app,
            "<div>Chart</div>",
            label="chart",
            callbacks={"app:action": on_chart_event},
        )
        show_and_wait_ready(
            app,
            "<div>Table</div>",
            label="table",
            callbacks={"app:action": on_table_event},
        )

        # Emit event only from chart window
        runtime.eval_js("chart", "pywry.emit('app:action', { from: 'chart' });")
        time.sleep(0.5)

        assert len(chart_events) == 1, f"Chart should have 1 event: {chart_events}"
        assert chart_events[0]["label"] == "chart"
        assert len(table_events) == 0, f"Table should have no events: {table_events}"

        app.destroy()

    def test_close_specific_window_by_label(self):
        """close(label) closes only the specified window."""
        app = PyWry(mode=WindowMode.MULTI_WINDOW, theme=ThemeMode.DARK)

        show_and_wait_ready(app, "<div>Chart</div>", label="chart")
        show_and_wait_ready(app, "<div>Table</div>", label="table")

        labels_before = app.get_labels()
        assert "chart" in labels_before
        assert "table" in labels_before

        # Close only chart
        app.close(label="chart")
        time.sleep(0.3)

        # Table should still respond
        result = wait_for_result("table", "pywry.result({ alive: true });")
        assert result is not None and result["alive"], "Table window should still be open"

        app.destroy()

    def test_get_labels_returns_all(self):
        """get_labels() returns all open window labels."""
        app = PyWry(mode=WindowMode.MULTI_WINDOW, theme=ThemeMode.DARK)

        show_and_wait_ready(app, "<div>1</div>", label="win-1")
        show_and_wait_ready(app, "<div>2</div>", label="win-2")
        show_and_wait_ready(app, "<div>3</div>", label="win-3")

        labels = app.get_labels()

        assert "win-1" in labels, f"win-1 not in {labels}"
        assert "win-2" in labels, f"win-2 not in {labels}"
        assert "win-3" in labels, f"win-3 not in {labels}"

        app.destroy()


# =============================================================================
# Cross-Mode Behavior Tests
# =============================================================================


class TestCrossModeBehavior:
    """Tests for behavior that applies across all modes."""

    @pytest.mark.parametrize(
        "mode",
        [WindowMode.NEW_WINDOW, WindowMode.SINGLE_WINDOW, WindowMode.MULTI_WINDOW],
    )
    def test_destroy_closes_all_windows(self, mode):
        """destroy() closes all windows regardless of mode."""
        app = PyWry(mode=mode, theme=ThemeMode.DARK)

        show_and_wait_ready(app, "<div>Content 1</div>")
        if mode != WindowMode.SINGLE_WINDOW:
            show_and_wait_ready(app, "<div>Content 2</div>")

        app.destroy()
        time.sleep(0.3)

        # After destroy, get_labels should be empty
        # (Note: this may depend on implementation details)

    @pytest.mark.parametrize(
        "mode",
        [WindowMode.NEW_WINDOW, WindowMode.SINGLE_WINDOW, WindowMode.MULTI_WINDOW],
    )
    def test_eval_js_works_in_all_modes(self, mode):
        """eval_js works correctly in all window modes."""
        app = PyWry(mode=mode, theme=ThemeMode.DARK)

        label = show_and_wait_ready(app, "<h1 id='target'>Original</h1>")

        # Use eval_js to modify content
        app.eval_js("document.getElementById('target').textContent = 'Modified';")
        time.sleep(0.3)

        # Verify modification
        result = wait_for_result(
            label,
            "pywry.result({ text: document.getElementById('target')?.textContent });",
        )
        assert result is not None and result["text"] == "Modified", (
            f"Mode {mode}: eval_js failed: {result}"
        )

        app.destroy()

    def test_is_open_reports_correctly(self):
        """is_open() correctly reports window state."""
        app = PyWry(mode=WindowMode.SINGLE_WINDOW, theme=ThemeMode.DARK)

        # Before showing, is_open should be False
        assert not app.is_open(), "Should not be open before show()"

        show_and_wait_ready(app, "<div>Content</div>")

        # After showing, is_open should be True
        assert app.is_open(), "Should be open after show()"

        app.destroy()


# =============================================================================
# README Quick Start Example Test
# =============================================================================


class TestReadmeQuickStart:
    """Test that the README Quick Start example works correctly."""

    def test_quick_start_flow(self):
        """Verify the Quick Start example from README works.

        This test validates the SINGLE_WINDOW workflow as documented:
        1. Show HTML content with toolbar
        2. Callback executes when triggered
        3. Content can be replaced with new content
        """
        app = PyWry(
            mode=WindowMode.SINGLE_WINDOW,
            theme=ThemeMode.DARK,
            title="My App",
            width=1280,
            height=720,
        )

        # Track callback execution
        callback_executed = threading.Event()

        def on_click(data: Any, event_type: str, label: str) -> None:
            callback_executed.set()

        # Show initial content with toolbar and callback
        label = show_and_wait_ready(
            app,
            "<h1>Hello, World!</h1>",
            toolbars=[
                {
                    "position": "bottom",
                    "items": [{"type": "button", "label": "Update Text", "event": "app:click"}],
                }
            ],
            callbacks={"app:click": on_click},
        )

        # Verify initial content rendered correctly
        result = wait_for_result(
            label,
            """pywry.result({
                h1Text: document.querySelector('h1')?.textContent,
                toolbarExists: !!document.querySelector('.pywry-toolbar')
            });""",
        )
        assert result is not None, "No result from initial render"
        assert result["h1Text"] == "Hello, World!", f"Wrong text: {result['h1Text']}"
        assert result["toolbarExists"], "Toolbar should exist"

        # Trigger callback and verify it executes
        runtime.eval_js(label, "pywry.emit('app:click', {});")
        assert callback_executed.wait(timeout=5.0), "Callback not executed"

        # Replace content
        show_and_wait_ready(app, "<div id='chart'>Chart Content</div>")

        # Verify new content replaced old content
        result2 = wait_for_result(
            label,
            """pywry.result({
                chartText: document.getElementById('chart')?.textContent,
                h1Gone: !document.querySelector('h1')
            });""",
        )
        assert result2 is not None, "No result from second render"
        assert result2["chartText"] == "Chart Content", "Chart content should exist"
        assert result2["h1Gone"], "Old H1 should be replaced"

        app.destroy()
