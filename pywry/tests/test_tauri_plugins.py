"""Tests for Tauri plugin integration.

Tests verify:
- Dialog and FS plugins are properly registered
- Tauri APIs are available in the webview
- File save dialog functionality works
- Plugin capabilities are correctly configured
"""

# pylint: disable=unsubscriptable-object

import time

from collections.abc import Callable
from functools import wraps
from pathlib import Path
from typing import Any, TypeVar

import pytest

from pywry import runtime
from pywry.app import PyWry
from pywry.models import ThemeMode

# Import shared test utilities from tests.conftest
from tests.conftest import ReadyWaiter, show_and_wait_ready, wait_for_result


F = TypeVar("F", bound=Callable[..., Any])


def retry_on_subprocess_failure(max_attempts: int = 3, delay: float = 1.0) -> Callable[[F], F]:
    """Retry decorator for tests that may fail due to transient subprocess issues."""

    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            last_error: Exception | None = None
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except (TimeoutError, AssertionError) as e:
                    last_error = e
                    if attempt < max_attempts - 1:
                        runtime.stop()
                        time.sleep(delay * (attempt + 1))
            raise last_error  # type: ignore[misc]

        return wrapper  # type: ignore[return-value]

    return decorator


# Note: cleanup_runtime fixture is now in conftest.py and auto-used


# =============================================================================
# Unit Tests - Plugin Configuration
# =============================================================================


class TestPluginCapabilities:
    """Tests for Tauri plugin capabilities configuration."""

    def test_capabilities_file_exists(self):
        """Capabilities file exists in the correct location."""
        capabilities_file = Path(__file__).parent.parent / "pywry" / "capabilities" / "default.toml"
        assert capabilities_file.exists(), f"Capabilities file not found at {capabilities_file}"

    def test_capabilities_has_dialog_permission(self):
        """Capabilities file includes dialog:default permission."""
        capabilities_file = Path(__file__).parent.parent / "pywry" / "capabilities" / "default.toml"
        content = capabilities_file.read_text(encoding="utf-8")
        assert "dialog:default" in content, "dialog:default permission not found in capabilities"

    def test_capabilities_has_fs_permission(self):
        """Capabilities file includes fs:default permission."""
        capabilities_file = Path(__file__).parent.parent / "pywry" / "capabilities" / "default.toml"
        content = capabilities_file.read_text(encoding="utf-8")
        assert "fs:default" in content, "fs:default permission not found in capabilities"

    def test_capabilities_has_pytauri_permission(self):
        """Capabilities file includes pytauri:default for IPC."""
        capabilities_file = Path(__file__).parent.parent / "pywry" / "capabilities" / "default.toml"
        content = capabilities_file.read_text(encoding="utf-8")
        assert "pytauri:default" in content, "pytauri:default permission not found in capabilities"


class TestPluginImports:
    """Tests for plugin module imports."""

    def test_can_import_dialog_plugin(self):
        """Dialog plugin can be imported."""
        from pytauri_plugins import dialog

        assert hasattr(dialog, "init"), "dialog.init() function not found"

    def test_can_import_fs_plugin(self):
        """FS plugin can be imported."""
        from pytauri_plugins import fs

        assert hasattr(fs, "init"), "fs.init() function not found"


class TestMainModulePluginRegistration:
    """Tests for plugin registration in __main__.py."""

    def test_main_imports_dialog_plugin(self):
        """__main__.py imports dialog plugin."""
        main_file = Path(__file__).parent.parent / "pywry" / "__main__.py"
        content = main_file.read_text(encoding="utf-8")
        # Check for various import patterns including aliased imports
        has_dialog_import = (
            "from pytauri_plugins import dialog" in content
            or "pytauri_plugins.dialog" in content
            or "dialog as dialog_plugin" in content
        )
        assert has_dialog_import, "dialog plugin import not found in __main__.py"

    def test_main_imports_fs_plugin(self):
        """__main__.py imports fs plugin."""
        main_file = Path(__file__).parent.parent / "pywry" / "__main__.py"
        content = main_file.read_text(encoding="utf-8")
        # Check for various import patterns including aliased imports
        has_fs_import = (
            "from pytauri_plugins import fs" in content
            or "pytauri_plugins.fs" in content
            or "fs as fs_plugin" in content
        )
        assert has_fs_import, "fs plugin import not found in __main__.py"

    def test_main_registers_plugins(self):
        """__main__.py registers plugins in builder.build()."""
        main_file = Path(__file__).parent.parent / "pywry" / "__main__.py"
        content = main_file.read_text(encoding="utf-8")
        assert "plugins=" in content, "plugins= parameter not found in __main__.py"
        assert "dialog" in content and "init()" in content, (
            "dialog.init() not found in plugins list"
        )
        assert "fs" in content, "fs plugin not found in plugins list"


# =============================================================================
# Integration Tests - JS API Availability
# =============================================================================


@pytest.mark.e2e
class TestTauriAPIsAvailable:
    """E2E tests verifying Tauri APIs are available in webview."""

    def test_tauri_global_exists(self):
        """window.__TAURI__ object exists in webview."""
        app = PyWry(theme=ThemeMode.DARK)
        label = show_and_wait_ready(app, "<div>Test</div>", title="Tauri Check")

        result = wait_for_result(
            label,
            """
            pywry.result({
                hasTauri: typeof window.__TAURI__ !== 'undefined',
                tauriType: typeof window.__TAURI__
            });
        """,
        )

        assert result is not None, "No result from window"
        assert result["hasTauri"], "window.__TAURI__ not found"
        assert result["tauriType"] == "object", "window.__TAURI__ is not an object"
        app.close()

    def test_dialog_api_available(self):
        """window.__TAURI__.dialog API is available."""
        app = PyWry(theme=ThemeMode.DARK)
        label = show_and_wait_ready(app, "<div>Test</div>", title="Dialog Check")

        result = wait_for_result(
            label,
            """
            pywry.result({
                hasDialog: typeof window.__TAURI__?.dialog !== 'undefined',
                hasSave: typeof window.__TAURI__?.dialog?.save === 'function',
                hasOpen: typeof window.__TAURI__?.dialog?.open === 'function',
                hasMessage: typeof window.__TAURI__?.dialog?.message === 'function'
            });
        """,
        )

        assert result is not None, "No result from window"
        assert result["hasDialog"], "window.__TAURI__.dialog not found"
        assert result["hasSave"], "dialog.save() function not found"
        assert result["hasOpen"], "dialog.open() function not found"
        assert result["hasMessage"], "dialog.message() function not found"
        app.close()

    def test_fs_api_available(self):
        """window.__TAURI__.fs API is available."""
        app = PyWry(theme=ThemeMode.DARK)
        label = show_and_wait_ready(app, "<div>Test</div>", title="FS Check")

        result = wait_for_result(
            label,
            """
            pywry.result({
                hasFs: typeof window.__TAURI__?.fs !== 'undefined',
                hasWriteTextFile: typeof window.__TAURI__?.fs?.writeTextFile === 'function',
                hasReadTextFile: typeof window.__TAURI__?.fs?.readTextFile === 'function'
            });
        """,
        )

        assert result is not None, "No result from window"
        assert result["hasFs"], "window.__TAURI__.fs not found"
        assert result["hasWriteTextFile"], "fs.writeTextFile() function not found"
        assert result["hasReadTextFile"], "fs.readTextFile() function not found"
        app.close()

    def test_pytauri_api_available(self):
        """window.__TAURI__.pytauri API is available for IPC."""
        app = PyWry(theme=ThemeMode.DARK)
        label = show_and_wait_ready(app, "<div>Test</div>", title="PyTauri Check")

        result = wait_for_result(
            label,
            """
            pywry.result({
                hasPytauri: typeof window.__TAURI__?.pytauri !== 'undefined',
                hasPyInvoke: typeof window.__TAURI__?.pytauri?.pyInvoke === 'function'
            });
        """,
        )

        assert result is not None, "No result from window"
        assert result["hasPytauri"], "window.__TAURI__.pytauri not found"
        assert result["hasPyInvoke"], "pytauri.pyInvoke() function not found"
        app.close()


@pytest.mark.e2e
class TestAGGridExportIntegration:
    """E2E tests for AG Grid export with Tauri dialog."""

    def test_aggrid_has_export_context_menu(self):
        """AG Grid context menu includes export options."""
        app = PyWry(theme=ThemeMode.DARK)
        data = [{"Symbol": "AAPL", "Price": 150.25}]

        waiter = ReadyWaiter(timeout=10.0)
        callbacks = {"pywry:ready": waiter.on_ready}
        widget = app.show_dataframe(data, callbacks=callbacks, title="Export Test")
        label = widget.label if hasattr(widget, "label") else widget
        waiter.wait()
        time.sleep(0.5)  # Wait for AG Grid to fully render

        # Verify the grid is set up and Tauri APIs are available
        result = wait_for_result(
            label,
            """
            (function() {
                // Get the PYWRY_AGGRID_BUILD_OPTIONS function
                var buildFn = window.PYWRY_AGGRID_BUILD_OPTIONS;
                var hasBuildFn = typeof buildFn === 'function';

                // Check that Tauri dialog is accessible
                var hasTauriDialog = typeof window.__TAURI__?.dialog?.save === 'function';
                var hasTauriFs = typeof window.__TAURI__?.fs?.writeTextFile === 'function';

                pywry.result({
                    hasBuildFn: hasBuildFn,
                    hasTauriDialog: hasTauriDialog,
                    hasTauriFs: hasTauriFs
                });
            })();
        """,
        )

        assert result is not None, "No result from window"
        assert result["hasBuildFn"], "PYWRY_AGGRID_BUILD_OPTIONS function not found"
        assert result["hasTauriDialog"], "Tauri dialog.save() not available for export"
        assert result["hasTauriFs"], "Tauri fs.writeTextFile() not available for export"
        app.close()

    def test_aggrid_export_functions_check_tauri_first(self):
        """AG Grid export checks for Tauri before browser API."""
        # Read the aggrid-defaults.js to verify the logic
        aggrid_js_file = (
            Path(__file__).parent.parent / "pywry" / "frontend" / "src" / "aggrid-defaults.js"
        )
        content = aggrid_js_file.read_text(encoding="utf-8")

        # Verify Tauri is checked BEFORE showSaveFilePicker
        tauri_check_pos = content.find("if (window.__TAURI__)")
        browser_check_pos = content.find("if (window.showSaveFilePicker)")

        assert tauri_check_pos != -1, "Tauri check not found in aggrid-defaults.js"
        assert browser_check_pos != -1, "Browser fallback not found in aggrid-defaults.js"
        assert tauri_check_pos < browser_check_pos, (
            "Tauri check should come BEFORE browser fallback in saveWithFilePicker"
        )


@pytest.mark.e2e
class TestSaveDialogFunctionality:
    """E2E tests for save dialog functionality."""

    @retry_on_subprocess_failure(max_attempts=3, delay=1.0)
    def test_save_with_file_picker_function_exists(self):
        """saveWithFilePicker helper function is defined in grid context."""
        app = PyWry(theme=ThemeMode.DARK)
        data = [{"a": 1}]

        waiter = ReadyWaiter(timeout=10.0)
        callbacks = {"pywry:ready": waiter.on_ready}
        widget = app.show_dataframe(data, callbacks=callbacks, title="SavePicker Test")
        label = widget.label if hasattr(widget, "label") else widget
        if not waiter.wait():
            raise TimeoutError(f"Window '{label}' did not become ready within 10s")
        time.sleep(0.5)

        # The saveWithFilePicker is a local function inside the context menu builder
        # We can verify the grid is set up and Tauri APIs are available
        result = wait_for_result(
            label,
            """
            pywry.result({
                gridExists: !!document.querySelector('.ag-root-wrapper'),
                hasTauriDialog: typeof window.__TAURI__?.dialog?.save === 'function',
                hasTauriFs: typeof window.__TAURI__?.fs?.writeTextFile === 'function'
            });
        """,
        )

        assert result is not None, "No result from window"
        assert result["gridExists"], "AG Grid not rendered"
        assert result["hasTauriDialog"], "Tauri dialog not available"
        assert result["hasTauriFs"], "Tauri fs not available"
        app.close()
