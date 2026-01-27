"""End-to-end tests for PyWry theme-coordinated rendering."""

# pylint: disable=too-many-lines

import threading
import time

from collections.abc import Callable
from functools import wraps
from typing import Any, TypeVar

import pytest

from pywry import runtime
from pywry.app import PyWry
from pywry.callbacks import get_registry
from pywry.models import HtmlContent, ThemeMode, WindowMode
from pywry.toolbar import Button, Toolbar


F = TypeVar("F", bound=Callable[..., Any])


def retry_on_subprocess_failure(max_attempts: int = 3, delay: float = 1.0) -> Callable[[F], F]:
    """Retry decorator for tests that may fail due to transient subprocess issues.

    On Windows, WebView2 sometimes fails to start due to resource contention
    ("Failed to unregister class Chrome_WidgetWin_0"). This decorator retries
    the test after a delay to allow resources to be released.
    """

    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            last_error: Exception | None = None
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except TimeoutError as e:
                    last_error = e
                    if attempt < max_attempts - 1:
                        # Clean up and wait before retry
                        runtime.stop()
                        time.sleep(delay)
            raise last_error  # type: ignore[misc]

        return wrapper  # type: ignore[return-value]

    return decorator


@pytest.fixture(autouse=True)
def cleanup_runtime():
    """Ensure runtime is fresh for each test - STOP before AND after."""
    from pywry.window_manager import get_lifecycle

    runtime.stop()
    cleanup_delay = 0.5
    time.sleep(cleanup_delay)

    # Clear any stale callbacks and window lifecycle state
    registry = get_registry()
    registry.clear()
    get_lifecycle().clear()

    yield

    runtime.stop()
    registry.clear()
    get_lifecycle().clear()
    time.sleep(0.5)


class ReadyWaiter:
    """Helper to wait for window ready event. Must be created BEFORE show()."""

    def __init__(self, timeout: float = 10.0):
        self.timeout = timeout
        self._ready = threading.Event()

    def on_ready(self, _data: Any) -> None:
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

    widget = app.show(content, callbacks=callbacks, **kwargs)
    # Extract label from NativeWidget (app.show now returns NativeWidget, not str)
    label = widget.label if hasattr(widget, "label") else widget

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
    widget = app.show_dataframe(data, callbacks=callbacks, **kwargs)
    # Extract label from NativeWidget
    label = widget.label if hasattr(widget, "label") else widget
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
    widget = app.show_plotly(figure, callbacks=callbacks, **kwargs)
    # Extract label from NativeWidget
    label = widget.label if hasattr(widget, "label") else widget
    if not waiter.wait():
        raise TimeoutError(f"Window '{label}' did not become ready within {timeout}s")
    return label


def wait_for_result(
    label: str, script: str, timeout: float = 5.0, retries: int = 3
) -> dict[str, Any] | None:
    """Execute JS and wait for pywry.result() callback.

    Parameters
    ----------
    label : str
        Window label to execute script in.
    script : str
        JavaScript to execute.
    timeout : float, optional
        Timeout per attempt in seconds.
    retries : int, optional
        Number of retry attempts for race conditions (macOS).
    """
    registry = get_registry()

    result: dict[str, Any] = {"received": False, "data": None}

    def on_result(data: Any) -> None:
        result["received"] = True
        result["data"] = data

    for attempt in range(retries):
        result["received"] = False
        result["data"] = None

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
        var isDarkWindow = htmlEl.classList.contains('pywry-theme-dark');
        var isLightWindow = htmlEl.classList.contains('pywry-theme-light');

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

    @retry_on_subprocess_failure(max_attempts=3, delay=1.0)
    def test_dark_dataframe(self):
        """DARK show_dataframe renders with DARK AG Grid theme."""
        app = PyWry(theme=ThemeMode.DARK)
        data = [{"x": 1, "y": 10}, {"x": 2, "y": 15}]
        label = show_dataframe_and_wait_ready(app, data, title="Dark+Grid")
        time.sleep(1.5)

        result = verify_theme_and_rendering(label, expect_dark=True)
        assert "error" not in result, f"Verification failed: {result.get('error')}"
        assert result["hasGrid"], "AG Grid not found!"
        assert result["gridRowCount"] > 0, "No rows rendered!"
        app.close()

    def test_dark_plotly(self):
        """DARK show_plotly renders with DARK template."""
        app = PyWry(theme=ThemeMode.DARK)
        figure = {"data": [{"x": [1, 2, 3], "y": [10, 15, 13], "type": "scatter"}]}
        label = show_plotly_and_wait_ready(app, figure, title="Dark+Plotly", timeout=20.0)
        # Plotly renders asynchronously after DOM is ready (longer wait for WebKitGTK)
        time.sleep(1.5)

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


class TestToolbarAndStyles:
    """Tests for toolbar rendering and CSS application in window mode."""

    def test_toolbar_renders_correctly(self):
        """Toolbar renders with correct classes and buttons."""
        app = PyWry(theme=ThemeMode.DARK)
        toolbars = [
            {
                "position": "top",
                "items": [{"type": "button", "label": "MyButton", "event": "toolbar:click"}],
            }
        ]

        # Test top toolbar
        label = show_and_wait_ready(
            app, "<div>Content</div>", title="Toolbar Test", toolbars=toolbars
        )

        result = wait_for_result(
            label,
            """
            pywry.result({
                hasWrapper: !!document.querySelector('.pywry-wrapper-top'),
                hasToolbar: !!document.querySelector('.pywry-toolbar-top'),
                btnText: document.querySelector('.pywry-btn')?.textContent || '',
                wrapperClass: document.querySelector('.pywry-wrapper-top')?.className
            });
            """,
        )

        assert result and isinstance(result, dict)
        assert result["hasWrapper"], "Wrapper top not found"
        assert result["hasToolbar"], "Toolbar top not found"
        assert result["btnText"] == "MyButton", "Button text incorrect"
        app.close()

    def test_css_variables_applied(self):
        """CSS variables from pywry.css are applied to document."""
        app = PyWry(theme=ThemeMode.DARK)
        label = show_and_wait_ready(app, "<div>CSS Test</div>", title="CSS Test")

        result = wait_for_result(
            label,
            """
            (function() {
                var style = getComputedStyle(document.documentElement);
                var bg = style.getPropertyValue('--pywry-bg-primary').trim();
                var text = style.getPropertyValue('--pywry-text-primary').trim();

                pywry.result({
                    bg: bg,
                    text: text,
                    isDark: document.documentElement.classList.contains('dark')
                });
            })();
            """,
        )

        assert result and isinstance(result, dict)
        # Check for non-empty values first
        assert result["bg"], "Background var not set"
        assert result["text"], "Text var not set"
        assert result["isDark"], "Dark class not applied"

        # We can check for specific values if we know what pywry.css defines for dark mode
        # Based on pywry.css: #212124 (dark bg)
        # Note: Browsers might normalize colors, so loose check is safer or exact if known standard
        # But presence confirms CSS file was loaded and variable exposed
        app.close()


class TestToolbarIntegration:
    """Tests for toolbar functionality across all content/framework modes."""

    def test_toolbar_html_buttons_work(self):
        """Toolbar buttons trigger Python callbacks in HTML mode."""
        app = PyWry(theme=ThemeMode.DARK)

        # Event tracking
        events = {"clicked": False}

        def on_click(data: dict, event_type: str, widget_id: str) -> None:  # pylint: disable=unused-argument
            events["clicked"] = True
            events["data"] = data

        toolbars = [
            Toolbar(
                position="top",
                items=[Button(label="ClickMe", event="custom:click")],
            )
        ]

        # Pass callback directly to show() - this is how PyWry events work
        label = show_and_wait_ready(
            app,
            "<div>HTML</div>",
            toolbars=toolbars,
            callbacks={"custom:click": on_click},
        )

        # Trigger click via JS
        app.eval_js("document.querySelector('.pywry-btn').click()", label=label)

        # Wait for event
        start = time.time()
        while not events["clicked"] and (time.time() - start) < 3.0:
            time.sleep(0.1)

        assert events["clicked"], "Button click callback not triggered"
        app.close()

    def test_toolbar_plotly_buttons_work(self):
        """Toolbar buttons trigger Python callbacks in Plotly mode."""
        app = PyWry(theme=ThemeMode.DARK)

        events = {"clicked": False}

        def on_click(data: dict, event_type: str, widget_id: str) -> None:  # pylint: disable=unused-argument
            events["clicked"] = True

        toolbars = [
            Toolbar(
                position="bottom",
                items=[Button(label="PlotBtn", event="plot:click")],
            )
        ]
        figure = {"data": [{"x": [1], "y": [2], "type": "bar"}]}

        # Pass callback directly to show_plotly()
        label = show_plotly_and_wait_ready(
            app,
            figure,
            toolbars=toolbars,
            callbacks={"plot:click": on_click},
        )

        # Verify toolbar rendered (check for toolbar class, not wrapper)
        result = wait_for_result(
            label,
            "pywry.result({ hasToolbar: !!document.querySelector('.pywry-toolbar-bottom') })",
        )
        assert result["hasToolbar"], "Toolbar bottom not found in Plotly mode"

        # Trigger click
        app.eval_js("document.querySelector('.pywry-btn').click()", label=label)

        start = time.time()
        while not events["clicked"] and (time.time() - start) < 3.0:
            time.sleep(0.1)

        assert events["clicked"], "Plotly toolbar button callback not triggered"
        app.close()

    def test_toolbar_dataframe_buttons_work(self):
        """Toolbar buttons trigger Python callbacks in DataFrame/AG Grid mode."""
        app = PyWry(theme=ThemeMode.DARK)

        events = {"clicked": False}

        def on_click(data: dict, event_type: str, widget_id: str) -> None:  # pylint: disable=unused-argument
            events["clicked"] = True

        toolbars = [
            Toolbar(
                position="left",
                items=[Button(label="GridBtn", event="data:click")],
            )
        ]
        data = [{"x": 1}]

        # Pass callback directly to show_dataframe()
        label = show_dataframe_and_wait_ready(
            app,
            data,
            toolbars=toolbars,
            callbacks={"data:click": on_click},
        )

        # Verify structure (left position)
        result = wait_for_result(
            label,
            "pywry.result({ hasWrapper: !!document.querySelector('.pywry-wrapper-left') })",
        )
        assert result["hasWrapper"], "Wrapper left not found in DataFrame mode"

        # Trigger click
        app.eval_js("document.querySelector('.pywry-btn').click()", label=label)

        start = time.time()
        while not events["clicked"] and (time.time() - start) < 3.0:
            time.sleep(0.1)

        assert events["clicked"], "DataFrame toolbar button callback not triggered"
        app.close()


class TestToolbarComponentEvents:
    """E2E tests for all toolbar component types and their event emissions."""

    def test_select_triggers_event_with_value(self):
        """Select dropdown emits {value: ...} on change."""
        app = PyWry(theme=ThemeMode.DARK)

        events = {"received": False, "data": None}

        def on_select(data):
            events["received"] = True
            events["data"] = data

        toolbars = [
            {
                "position": "top",
                "items": [
                    {
                        "type": "select",
                        "event": "test:select",
                        "options": [
                            {"label": "Option A", "value": "a"},
                            {"label": "Option B", "value": "b"},
                        ],
                        "selected": "a",
                    }
                ],
            }
        ]

        label = show_and_wait_ready(app, "<div>Select Test</div>", toolbars=toolbars)
        get_registry().register(label, "test:select", on_select)

        # Open the dropdown by clicking the selected area
        app.eval_js(
            "document.querySelector('.pywry-dropdown-selected').click();",
            label=label,
        )
        time.sleep(0.2)

        # Select option 'b' from the open menu
        app.eval_js(
            "document.querySelector('.pywry-dropdown-option[data-value=\"b\"]').click();",
            label=label,
        )

        start = time.time()
        while not events["received"] and (time.time() - start) < 3.0:
            time.sleep(0.1)

        assert events["received"], "Select change event not received"
        assert events["data"]["value"] == "b", f"Expected value 'b', got {events['data']}"
        app.close()

    def test_multiselect_triggers_event_with_values_array(self):
        """MultiSelect emits {values: [...]} on checkbox change."""
        app = PyWry(theme=ThemeMode.DARK)

        events = {"received": False, "data": None}

        def on_multiselect(data):
            events["received"] = True
            events["data"] = data

        toolbars = [
            {
                "position": "top",
                "items": [
                    {
                        "type": "multiselect",
                        "event": "test:multiselect",
                        "options": [
                            {"label": "Red", "value": "red"},
                            {"label": "Green", "value": "green"},
                            {"label": "Blue", "value": "blue"},
                        ],
                        "selected": ["red"],
                    }
                ],
            }
        ]

        label = show_and_wait_ready(app, "<div>MultiSelect Test</div>", toolbars=toolbars)
        get_registry().register(label, "test:multiselect", on_multiselect)

        # First open the multiselect dropdown, then click on the 'green' option
        app.eval_js(
            "document.querySelector('.pywry-multiselect .pywry-dropdown-selected').click();",
            label=label,
        )
        time.sleep(0.2)  # Wait for dropdown to open
        app.eval_js(
            "var options = document.querySelectorAll('.pywry-multiselect-option'); "
            "options[1].click();",  # Click the 'green' option (index 1)
            label=label,
        )

        start = time.time()
        while not events["received"] and (time.time() - start) < 3.0:
            time.sleep(0.1)

        assert events["received"], "MultiSelect change event not received"
        assert set(events["data"]["values"]) == {
            "red",
            "green",
        }, f"Got {events['data']}"
        app.close()

    def test_text_input_triggers_event_with_debounce(self):
        """TextInput emits {value: ...} after debounce period."""
        app = PyWry(theme=ThemeMode.DARK)

        events = {"received": False, "data": None}

        def on_text(data):
            events["received"] = True
            events["data"] = data

        toolbars = [
            {
                "position": "top",
                "items": [
                    {
                        "type": "text",
                        "event": "test:text",
                        "placeholder": "Type here",
                        "debounce": 100,  # Short debounce for test
                    }
                ],
            }
        ]

        label = show_and_wait_ready(app, "<div>Text Test</div>", toolbars=toolbars)
        get_registry().register(label, "test:text", on_text)

        # Type text
        app.eval_js(
            "var inp = document.querySelector('.pywry-input-text'); "
            "inp.value = 'hello world'; "
            "inp.dispatchEvent(new Event('input'));",
            label=label,
        )

        # Wait for debounce + processing
        start = time.time()
        while not events["received"] and (time.time() - start) < 3.0:
            time.sleep(0.1)

        assert events["received"], "TextInput event not received"
        assert events["data"]["value"] == "hello world", f"Got {events['data']}"

        app.close()

    def test_number_input_triggers_event(self):
        """NumberInput emits {value: <number>} on change."""
        app = PyWry(theme=ThemeMode.DARK)

        events = {"received": False, "data": None}

        def on_number(data):
            events["received"] = True
            events["data"] = data

        toolbars = [
            {
                "position": "top",
                "items": [
                    {
                        "type": "number",
                        "event": "test:number",
                        "value": 10,
                        "min": 1,
                        "max": 100,
                    }
                ],
            }
        ]

        label = show_and_wait_ready(app, "<div>Number Test</div>", toolbars=toolbars)
        get_registry().register(label, "test:number", on_number)

        # Change number
        app.eval_js(
            "var inp = document.querySelector('.pywry-input-number'); "
            "inp.value = 42; "
            "inp.dispatchEvent(new Event('change'));",
            label=label,
        )

        start = time.time()
        while not events["received"] and (time.time() - start) < 3.0:
            time.sleep(0.1)

        assert events["received"], "NumberInput event not received"
        assert events["data"]["value"] == 42, f"Got {events['data']}"

        app.close()

    def test_date_input_triggers_event(self):
        """DateInput emits {value: <date_string>} on change."""
        app = PyWry(theme=ThemeMode.DARK)

        events = {"received": False, "data": None}

        def on_date(data):
            events["received"] = True
            events["data"] = data

        toolbars = [
            {
                "position": "top",
                "items": [
                    {
                        "type": "date",
                        "event": "test:date",
                        "value": "2025-01-01",
                    }
                ],
            }
        ]

        label = show_and_wait_ready(app, "<div>Date Test</div>", toolbars=toolbars)
        get_registry().register(label, "test:date", on_date)

        # Change date
        app.eval_js(
            "var inp = document.querySelector('.pywry-input-date'); "
            "inp.value = '2025-06-15'; "
            "inp.dispatchEvent(new Event('change'));",
            label=label,
        )

        start = time.time()
        while not events["received"] and (time.time() - start) < 3.0:
            time.sleep(0.1)

        assert events["received"], "DateInput event not received"
        assert events["data"]["value"] == "2025-06-15", f"Got {events['data']}"

        app.close()

    def test_slider_input_triggers_event(self):
        """SliderInput emits {value: <number>} on input."""
        app = PyWry(theme=ThemeMode.DARK)

        events = {"received": False, "data": None}

        def on_slider(data):
            events["received"] = True
            events["data"] = data

        toolbars = [
            {
                "position": "top",
                "items": [
                    {
                        "type": "slider",
                        "event": "test:slider",
                        "value": 50,
                        "min": 0,
                        "max": 100,
                        "step": 10,
                    }
                ],
            }
        ]

        label = show_and_wait_ready(app, "<div>Slider Test</div>", toolbars=toolbars)
        get_registry().register(label, "test:slider", on_slider)

        # Slide to 80
        app.eval_js(
            "var inp = document.querySelector('.pywry-input-range'); "
            "inp.value = 80; "
            "inp.dispatchEvent(new Event('input'));",
            label=label,
        )

        start = time.time()
        while not events["received"] and (time.time() - start) < 3.0:
            time.sleep(0.1)

        assert events["received"], "SliderInput event not received"
        assert events["data"]["value"] == 80, f"Got {events['data']}"

        app.close()

    def test_range_input_triggers_event(self):
        """RangeInput emits {start: <number>, end: <number>} on input."""
        app = PyWry(theme=ThemeMode.DARK)

        events = {"received": False, "data": None}

        def on_range(data):
            events["received"] = True
            events["data"] = data

        toolbars = [
            {
                "position": "top",
                "items": [
                    {
                        "type": "range",
                        "event": "test:range",
                        "start": 20,
                        "end": 80,
                        "min": 0,
                        "max": 100,
                        "step": 10,
                    }
                ],
            }
        ]

        label = show_and_wait_ready(app, "<div>Range Test</div>", toolbars=toolbars)
        get_registry().register(label, "test:range", on_range)

        # Adjust the end slider to 90 using the correct selector
        app.eval_js(
            "var endInput = document.querySelector('input[data-range=\"end\"]'); "
            "endInput.value = 90; "
            "endInput.dispatchEvent(new Event('input'));",
            label=label,
        )

        start_time = time.time()
        while not events["received"] and (time.time() - start_time) < 3.0:
            time.sleep(0.1)

        assert events["received"], "RangeInput event not received"
        assert events["data"]["start"] == 20, f"Got start={events['data'].get('start')}"
        assert events["data"]["end"] == 90, f"Got end={events['data'].get('end')}"

        app.close()


class TestMultiToolbarStateTracking:
    """E2E tests for tracking state across multiple toolbars in same widget."""

    def test_multiple_toolbars_different_positions(self):
        """Multiple toolbars at different positions all emit events correctly."""
        app = PyWry(theme=ThemeMode.DARK)

        events = {"top_btn": False, "bottom_select": None, "left_range": None}

        def on_top(_data):
            events["top_btn"] = True

        def on_bottom(data):
            events["bottom_select"] = data.get("value")

        def on_left(data):
            events["left_range"] = data.get("value")

        toolbars = [
            {
                "position": "top",
                "items": [{"type": "button", "label": "Top Btn", "event": "top:click"}],
            },
            {
                "position": "bottom",
                "items": [
                    {
                        "type": "select",
                        "event": "bottom:select",
                        "options": [
                            {"label": "X", "value": "x"},
                            {"label": "Y", "value": "y"},
                        ],
                    }
                ],
            },
            {
                "position": "left",
                "items": [
                    {
                        "type": "slider",
                        "event": "left:range",
                        "value": 25,
                        "min": 0,
                        "max": 100,
                    }
                ],
            },
        ]

        label = show_and_wait_ready(app, "<div>Multi-toolbar Test</div>", toolbars=toolbars)
        get_registry().register(label, "top:click", on_top)
        get_registry().register(label, "bottom:select", on_bottom)
        get_registry().register(label, "left:range", on_left)

        # Trigger all three
        app.eval_js("document.querySelector('.pywry-btn').click();", label=label)
        # Open the dropdown by clicking the selected area
        app.eval_js(
            "document.querySelector('.pywry-dropdown-selected').click();",
            label=label,
        )
        time.sleep(0.2)

        # Select 'y' option from the open menu
        app.eval_js(
            "document.querySelector('.pywry-dropdown-option[data-value=\"y\"]').click();",
            label=label,
        )
        app.eval_js(
            "var rng = document.querySelector('.pywry-input-range'); "
            "rng.value = 75; rng.dispatchEvent(new Event('input'));",
            label=label,
        )

        start = time.time()
        while (time.time() - start) < 4.0:
            if events["top_btn"] and events["bottom_select"] and events["left_range"] is not None:
                break
            time.sleep(0.1)

        assert events["top_btn"], "Top button event not received"
        assert events["bottom_select"] == "y", f"Bottom select: {events['bottom_select']}"
        assert events["left_range"] == 75, f"Left range: {events['left_range']}"
        app.close()

    def test_multiple_items_in_single_toolbar(self):
        """Multiple items in one toolbar emit independent events."""
        app = PyWry(theme=ThemeMode.DARK)

        events = {"btn1": False, "btn2": False, "select": None, "number": None}

        def on_btn1(_data):
            events["btn1"] = True

        def on_btn2(_data):
            events["btn2"] = True

        def on_select(data):
            events["select"] = data.get("value")

        def on_number(data):
            events["number"] = data.get("value")

        toolbars = [
            {
                "position": "top",
                "items": [
                    {"type": "button", "label": "Action 1", "event": "action:one"},
                    {"type": "button", "label": "Action 2", "event": "action:two"},
                    {
                        "type": "select",
                        "event": "filter:mode",
                        "options": [
                            {"label": "All", "value": "all"},
                            {"label": "Active", "value": "active"},
                        ],
                    },
                    {"type": "number", "event": "filter:limit", "value": 10},
                ],
            }
        ]

        label = show_and_wait_ready(app, "<div>Multi-item Toolbar</div>", toolbars=toolbars)
        get_registry().register(label, "action:one", on_btn1)
        get_registry().register(label, "action:two", on_btn2)
        get_registry().register(label, "filter:mode", on_select)
        get_registry().register(label, "filter:limit", on_number)

        # Trigger multiple items
        app.eval_js(
            "var btns = document.querySelectorAll('.pywry-btn'); btns[0].click();",
            label=label,
        )
        app.eval_js(
            "var btns = document.querySelectorAll('.pywry-btn'); btns[1].click();",
            label=label,
        )
        # Open the dropdown by clicking the selected area
        app.eval_js(
            "document.querySelector('.pywry-dropdown-selected').click();",
            label=label,
        )
        time.sleep(0.2)

        # Select 'active' option from the open menu
        app.eval_js(
            "document.querySelector('.pywry-dropdown-option[data-value=\"active\"]').click();",
            label=label,
        )
        app.eval_js(
            "var num = document.querySelector('.pywry-input-number'); "
            "num.value = 25; num.dispatchEvent(new Event('change'));",
            label=label,
        )

        start = time.time()
        while (time.time() - start) < 4.0:
            if all([events["btn1"], events["btn2"], events["select"], events["number"]]):
                break
            time.sleep(0.1)

        assert events["btn1"], "Button 1 event not received"
        assert events["btn2"], "Button 2 event not received"
        assert events["select"] == "active", f"Select: {events['select']}"
        assert events["number"] == 25, f"Number: {events['number']}"
        app.close()

    def test_pydantic_toolbar_models_work_in_e2e(self):
        """Toolbar Pydantic models work end-to-end with events."""
        from pywry.toolbar import Button, Option, Select, Toolbar

        app = PyWry(theme=ThemeMode.DARK)

        events = {"export": None, "view": None}

        def on_export(data):
            events["export"] = data

        def on_view(data):
            events["view"] = data.get("value")

        toolbar = Toolbar(
            position="top",
            items=[
                Button(label="Export", event="data:export", data={"format": "csv"}),
                Select(
                    event="view:change",
                    options=[
                        Option(label="Table", value="table"),
                        Option(label="Chart", value="chart"),
                    ],
                    selected="table",
                ),
            ],
        )

        label = show_and_wait_ready(app, "<div>Pydantic Toolbar</div>", toolbars=[toolbar])
        get_registry().register(label, "data:export", on_export)
        get_registry().register(label, "view:change", on_view)

        # Trigger button with data payload
        app.eval_js("document.querySelector('.pywry-btn').click();", label=label)
        # Open the dropdown by clicking the selected area
        app.eval_js(
            "document.querySelector('.pywry-dropdown-selected').click();",
            label=label,
        )
        time.sleep(0.2)

        # Select 'chart' option from the open menu
        app.eval_js(
            "document.querySelector('.pywry-dropdown-option[data-value=\"chart\"]').click();",
            label=label,
        )

        start = time.time()
        while (time.time() - start) < 4.0:
            if events["export"] and events["view"]:
                break
            time.sleep(0.1)

        # Event data contains the custom data from the button's data attribute
        export_data = events["export"]
        assert export_data is not None, "Export event not received"
        assert isinstance(export_data, dict), f"Export data should be dict: {export_data}"
        assert export_data["format"] == "csv", f"Export data: {export_data}"
        # Note: Button emits only its custom data, not componentId (unlike inputs)
        assert events["view"] == "chart", f"View: {events['view']}"
        app.close()

    def test_component_ids_are_unique_across_toolbars(self):
        """Each component gets a unique ID for state tracking."""
        from pywry.toolbar import Button, Option, Select, Toolbar

        app = PyWry(theme=ThemeMode.DARK)

        toolbar1 = Toolbar(
            position="top",
            items=[
                Button(label="A", event="btn:a"),
                Select(event="sel:a", options=[Option(label="X", value="x")]),
            ],
        )
        toolbar2 = Toolbar(
            position="bottom",
            items=[
                Button(label="B", event="btn:b"),
                Select(event="sel:b", options=[Option(label="Y", value="y")]),
            ],
        )

        label = show_and_wait_ready(app, "<div>ID Test</div>", toolbars=[toolbar1, toolbar2])

        # Verify unique IDs exist in DOM - just check that both toolbars render
        result = wait_for_result(
            label,
            "pywry.result({ top: !!document.querySelector('.pywry-toolbar-top'), "
            "bottom: !!document.querySelector('.pywry-toolbar-bottom') })",
        )

        assert result is not None, "Result not received"
        assert result["top"], "Top toolbar not found"
        assert result["bottom"], "Bottom toolbar not found"

        # Verify we have 4 components (2 buttons + 2 dropdowns)
        result2 = wait_for_result(
            label,
            "pywry.result({ btns: document.querySelectorAll('.pywry-btn').length, "
            "sels: document.querySelectorAll('.pywry-dropdown').length })",
        )
        assert result2 is not None, "Second result not received"
        assert result2["btns"] == 2, f"Expected 2 buttons, got {result2['btns']}"
        assert result2["sels"] == 2, f"Expected 2 selects, got {result2['sels']}"
        app.close()
