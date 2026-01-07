"""End-to-end tests for PyWry theme-coordinated rendering."""

import time
import threading

from typing import Any

import pytest

from pywry import runtime
from pywry.app import PyWry
from pywry.callbacks import get_registry
from pywry.models import HtmlContent, ThemeMode, WindowMode


@pytest.fixture(autouse=True)
def cleanup_runtime():
    """Ensure runtime is fresh for each test - STOP before AND after."""
    # STOP runtime first to ensure clean state (prevents race conditions from previous test)
    runtime.stop()
    time.sleep(0.2)

    # Clear any stale callbacks
    registry = get_registry()
    registry.clear()

    yield

    # Cleanup after test
    runtime.stop()
    registry.clear()
    time.sleep(0.1)


class ReadyWaiter:
    """Helper to wait for window ready event. Must be created BEFORE show()."""

    def __init__(self, timeout: float = 10.0):
        self.timeout = timeout
        self._ready = threading.Event()

    def on_ready(self, data: Any) -> None:
        """Callback for pywry:ready event."""
        self._ready.set()

    def wait(self) -> bool:
        """Wait for window to be ready. Call AFTER show()."""
        return self._ready.wait(timeout=self.timeout)


def show_and_wait_ready(
    app: PyWry,
    content: str | HtmlContent,
    timeout: float = 10.0,
    **kwargs: Any,
) -> str:
    """Show content and wait for window to be ready.

    This registers the ready callback BEFORE calling show().
    """
    waiter = ReadyWaiter(timeout=timeout)

    # Merge callbacks if provided
    callbacks = kwargs.pop("callbacks", {}) or {}
    callbacks["pywry:ready"] = waiter.on_ready

    label = app.show(content, callbacks=callbacks, **kwargs)

    if not waiter.wait():
        raise TimeoutError(f"Window '{label}' did not become ready within {timeout}s")

    return label


def show_dataframe_and_wait_ready(
    app: PyWry,
    data: Any,
    timeout: float = 10.0,
    **kwargs: Any,
) -> str:
    """Show dataframe and wait for window to be ready."""
    waiter = ReadyWaiter(timeout=timeout)
    callbacks = kwargs.pop("callbacks", {}) or {}
    callbacks["pywry:ready"] = waiter.on_ready
    label = app.show_dataframe(data, callbacks=callbacks, **kwargs)
    if not waiter.wait():
        raise TimeoutError(f"Window '{label}' did not become ready within {timeout}s")
    return label


def show_plotly_and_wait_ready(
    app: PyWry,
    figure: Any,
    timeout: float = 10.0,
    **kwargs: Any,
) -> str:
    """Show plotly figure and wait for window to be ready."""
    waiter = ReadyWaiter(timeout=timeout)
    callbacks = kwargs.pop("callbacks", {}) or {}
    callbacks["pywry:ready"] = waiter.on_ready
    label = app.show_plotly(figure, callbacks=callbacks, **kwargs)
    if not waiter.wait():
        raise TimeoutError(f"Window '{label}' did not become ready within {timeout}s")
    return label


def wait_for_result(
    label: str, script: str, timeout: float = 5.0, retries: int = 3
) -> dict[str, Any] | None:
    """Execute JS and wait for pywry.result() callback.

    Args:
        label: Window label to execute script in
        script: JavaScript to execute
        timeout: Timeout per attempt in seconds
        retries: Number of retry attempts for race conditions (macOS)
    """
    registry = get_registry()

    for attempt in range(retries):
        result: dict[str, Any] = {"received": False, "data": None}

        def on_result(data):
            result["received"] = True
            result["data"] = data

        registry.register(label, "pywry:result", on_result)
        runtime.eval_js(label, script)

        start = time.time()
        while not result["received"] and (time.time() - start) < timeout:
            time.sleep(0.05)

        registry.unregister(label, "pywry:result", on_result)

        if result["received"] and result["data"]:
            return result["data"]

        # Retry after brief delay (helps with macOS race conditions)
        if attempt < retries - 1:
            time.sleep(0.5)

    return result["data"]


# pylint: disable=unsubscriptable-object
def verify_theme_and_rendering(label: str, expect_dark: bool) -> dict:
    """Verify window theme, AG Grid theme, and Plotly rendering all match.

    Returns verification data with assertions about theme coordination.
    """
    script = """
    (function() {
        var htmlEl = document.documentElement;
        var isDarkWindow = htmlEl.classList.contains('dark');
        var isLightWindow = htmlEl.classList.contains('light');

        // Check AG Grid
        var gridDiv = document.querySelector('[class*="ag-theme-"]');
        var gridTheme = gridDiv ? gridDiv.className : null;
        var gridIsDark = gridTheme ? gridTheme.includes('-dark') : null;
        var gridRows = gridDiv ? gridDiv.querySelectorAll('.ag-row').length : 0;

        // Check Plotly
        var plotDiv = document.querySelector('.js-plotly-plot, #chart, #plotly-chart');
        var plotlyRendered = plotDiv ? plotDiv.classList.contains('js-plotly-plot') : false;
        var svgCount = plotDiv ? plotDiv.querySelectorAll('svg').length : 0;

        // Get actual Plotly colors from the chart's layout
        // The _fullLayout is only available AFTER Plotly.newPlot completes
        var plotlyPaperBg = null;
        var plotlyPlotBg = null;
        if (plotDiv && plotDiv._fullLayout) {
            plotlyPaperBg = plotDiv._fullLayout.paper_bgcolor;
            plotlyPlotBg = plotDiv._fullLayout.plot_bgcolor;
        }

        // Get expected values from the ACTUAL template definitions
        var templates = window.PYWRY_PLOTLY_TEMPLATES || {};
        var expectedDarkPaperBg = templates.plotly_dark?.layout?.paper_bgcolor || null;
        var expectedDarkPlotBg = templates.plotly_dark?.layout?.plot_bgcolor || null;
        var expectedLightPaperBg = templates.plotly_white?.layout?.paper_bgcolor || null;
        var expectedLightPlotBg = templates.plotly_white?.layout?.plot_bgcolor || null;

        pywry.result({
            // Window theme
            windowIsDark: isDarkWindow,
            windowIsLight: isLightWindow,
            htmlClass: htmlEl.className,

            // AG Grid (if present)
            hasGrid: !!gridDiv,
            gridThemeClass: gridTheme,
            gridIsDark: gridIsDark,
            gridRowCount: gridRows,

            // Plotly (if present)
            hasPlotly: !!plotDiv,
            plotlyRendered: plotlyRendered,
            plotlySvgCount: svgCount,
            plotlyPaperBg: plotlyPaperBg,
            plotlyPlotBg: plotlyPlotBg,

            // Expected values FROM THE TEMPLATE SOURCE
            expectedDarkPaperBg: expectedDarkPaperBg,
            expectedDarkPlotBg: expectedDarkPlotBg,
            expectedLightPaperBg: expectedLightPaperBg,
            expectedLightPlotBg: expectedLightPlotBg
        });
    })();
    """
    result = wait_for_result(label, script)
    if not result:
        return {"error": "No response from window"}

    # Type narrowing - pylint doesn't recognize the guard above
    assert isinstance(result, dict)

    # Validate theme coordination
    if expect_dark:
        assert result["windowIsDark"], f"Window should be DARK! Got: {result['htmlClass']}"
        if result["hasGrid"]:
            assert result["gridIsDark"], (
                f"Grid MUST be dark when window is dark! Got: {result['gridThemeClass']}"
            )
        if result["hasPlotly"]:
            # Verify applied colors match plotly_dark template FROM THE SOURCE
            actual_paper = result.get("plotlyPaperBg")
            actual_plot = result.get("plotlyPlotBg")
            expected_paper = result.get("expectedDarkPaperBg")
            expected_plot = result.get("expectedDarkPlotBg")
            assert expected_paper is not None, "plotly_dark template not loaded!"
            assert actual_paper == expected_paper, (
                f"paper_bgcolor MUST match plotly_dark template! Expected: '{expected_paper}', Got: '{actual_paper}'"
            )
            assert actual_plot == expected_plot, (
                f"plot_bgcolor MUST match plotly_dark template! Expected: '{expected_plot}', Got: '{actual_plot}'"
            )
    else:
        assert result["windowIsLight"], f"Window should be LIGHT! Got: {result['htmlClass']}"
        if result["hasGrid"]:
            assert not result["gridIsDark"], (
                f"Grid MUST be light when window is light! Got: {result['gridThemeClass']}"
            )
        if result["hasPlotly"]:
            # Verify applied colors match plotly_white template FROM THE SOURCE
            actual_paper = result.get("plotlyPaperBg")
            actual_plot = result.get("plotlyPlotBg")
            expected_paper = result.get("expectedLightPaperBg")
            expected_plot = result.get("expectedLightPlotBg")
            assert expected_paper is not None, "plotly_white template not loaded!"
            assert actual_paper == expected_paper, (
                f"paper_bgcolor MUST match plotly_white template! Expected: '{expected_paper}', Got: '{actual_paper}'"
            )
            assert actual_plot == expected_plot, (
                f"plot_bgcolor MUST match plotly_white template! Expected: '{expected_plot}', Got: '{actual_plot}'"
            )

    return result


class TestDarkThemeCoordination:
    """DARK window MUST have DARK sub-elements."""

    def test_dark_dataframe(self):
        """DARK show_dataframe renders with DARK AG Grid theme."""
        app = PyWry(theme=ThemeMode.DARK)
        data = [{"x": 1, "y": 10}, {"x": 2, "y": 15}]
        label = show_dataframe_and_wait_ready(app, data, title="Dark+Grid")
        # AG Grid renders asynchronously after DOM is ready
        time.sleep(0.5)

        result = verify_theme_and_rendering(label, expect_dark=True)
        assert "error" not in result, f"Verification failed: {result.get('error')}"
        assert result["hasGrid"], "AG Grid not found!"
        assert result["gridRowCount"] > 0, "No rows rendered!"
        app.close()

    def test_dark_plotly(self):
        """DARK show_plotly renders with DARK template."""
        app = PyWry(theme=ThemeMode.DARK)
        figure = {"data": [{"x": [1, 2, 3], "y": [10, 15, 13], "type": "scatter"}]}
        label = show_plotly_and_wait_ready(app, figure, title="Dark+Plotly")
        # Plotly renders asynchronously after DOM is ready
        time.sleep(0.5)

        result = verify_theme_and_rendering(label, expect_dark=True)
        assert result["hasPlotly"], "Plotly div not found!"
        assert result["plotlySvgCount"] > 0, "No SVG - chart not drawn!"
        app.close()


class TestLightThemeCoordination:
    """LIGHT window MUST have LIGHT sub-elements."""

    def test_light_dataframe(self):
        """LIGHT show_dataframe renders with LIGHT AG Grid theme."""
        app = PyWry(theme=ThemeMode.LIGHT)
        data = [{"x": 1, "y": 10}, {"x": 2, "y": 15}]
        label = show_dataframe_and_wait_ready(app, data, title="Light+Grid")
        # AG Grid renders asynchronously after DOM is ready
        time.sleep(0.5)

        result = verify_theme_and_rendering(label, expect_dark=False)
        assert "error" not in result, f"Verification failed: {result.get('error')}"
        assert result["hasGrid"], "AG Grid not found!"
        assert result["gridRowCount"] > 0, "No rows rendered!"
        app.close()

    def test_light_plotly(self):
        """LIGHT show_plotly renders with LIGHT template."""
        app = PyWry(theme=ThemeMode.LIGHT)
        figure = {"data": [{"x": [1, 2, 3], "y": [10, 15, 13], "type": "bar"}]}
        label = show_plotly_and_wait_ready(app, figure, title="Light+Plotly")
        # Plotly renders asynchronously after DOM is ready
        time.sleep(0.5)

        result = verify_theme_and_rendering(label, expect_dark=False)
        assert result["hasPlotly"], "Plotly div not found!"
        assert result["plotlySvgCount"] > 0, "No SVG - chart not drawn!"
        app.close()


class TestContentRendering:
    """Verify that content actually renders in windows."""

    # pylint: disable=unsubscriptable-object
    def test_html_content_renders(self):
        """HTML content appears in window with json_data and init_script."""
        app = PyWry(theme=ThemeMode.DARK)
        content = HtmlContent(
            html="<div id='test-div'>Hello World</div>",
            json_data={"key": "value"},
            init_script="window.__INIT_RAN__ = true;",
        )
        label = show_and_wait_ready(app, content, title="Content Test")

        result = wait_for_result(
            label,
            """
            pywry.result({
                divExists: !!document.getElementById('test-div'),
                divText: document.getElementById('test-div')?.textContent || 'NONE',
                initRan: window.__INIT_RAN__ === true,
                hasJsonData: !!window.json_data,
                jsonKey: window.json_data?.key || 'NONE'
            });
        """,
        )
        assert result and isinstance(result, dict), "No response!"
        assert result["divExists"], "Content div not found!"
        assert result["divText"] == "Hello World", f"Wrong content: {result['divText']}"
        assert result["initRan"], "Init script didn't run!"
        assert result["jsonKey"] == "value", f"Wrong json_data: {result['jsonKey']}"
        app.close()

    def test_single_window_mode_reuses(self):
        """SINGLE_WINDOW mode reuses the same window."""
        app = PyWry(mode=WindowMode.SINGLE_WINDOW, theme=ThemeMode.DARK)
        label1 = show_and_wait_ready(app, "<div id='first'>First</div>")
        label2 = show_and_wait_ready(app, "<div id='second'>Second</div>")
        assert label1 == label2, "SINGLE_WINDOW should reuse label!"

        result = wait_for_result(
            label2,
            """
            pywry.result({
                hasSecond: !!document.getElementById('second'),
                hasFirst: !!document.getElementById('first')
            });
        """,
        )
        assert result and isinstance(result, dict) and result["hasSecond"], (
            f"Second content not rendered! Got: {result}"
        )
        app.close()

    def test_new_window_mode_creates_multiple(self):
        """NEW_WINDOW mode creates separate windows."""
        app = PyWry(mode=WindowMode.NEW_WINDOW, theme=ThemeMode.DARK)
        label1 = show_and_wait_ready(app, "<div id='win1'>W1</div>")
        label2 = show_and_wait_ready(app, "<div id='win2'>W2</div>")
        assert label1 != label2, "NEW_WINDOW should create unique labels!"

        r1 = wait_for_result(label1, "pywry.result({ has: !!document.getElementById('win1') });")
        r2 = wait_for_result(label2, "pywry.result({ has: !!document.getElementById('win2') });")
        assert r1 and isinstance(r1, dict) and r1["has"], "Window 1 content missing!"
        assert r2 and isinstance(r2, dict) and r2["has"], "Window 2 content missing!"
        app.close()
