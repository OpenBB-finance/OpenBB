"""Unit tests for widget protocol.

Tests cover:
- NativeWindowHandle: constructor, properties, and methods
- BaseWidget protocol checking via is_base_widget
- All handle operations with mocked runtime/lifecycle/callbacks
"""

# pylint: disable=redefined-outer-name
# Pytest fixtures are designed to be used as function parameters with the same name.
# This is the standard pytest pattern and is not a code smell.

from __future__ import annotations

from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from pywry.widget_protocol import BaseWidget, NativeWindowHandle, is_base_widget


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def mock_app():
    """Create a mock app with emit method."""
    app = MagicMock()
    app.emit = MagicMock()
    return app


@pytest.fixture
def mock_resources():
    """Create mock WindowResources."""
    resources = MagicMock()
    resources.label = "test-window"
    resources.html_content = "<h1>Test</h1>"
    resources.created_at = datetime(2026, 1, 22, 12, 0, 0)
    resources.is_destroyed = False
    resources.last_config = MagicMock()
    resources.last_config.title = "Test Window"
    resources.custom_data = {}
    return resources


@pytest.fixture
def native_handle(mock_app):
    """Create a NativeWindowHandle instance."""
    return NativeWindowHandle(label="test-window", app=mock_app)


# =============================================================================
# NativeWindowHandle Constructor Tests
# =============================================================================


class TestNativeWindowHandleConstructor:
    """Tests for NativeWindowHandle initialization."""

    def test_init_stores_label(self, mock_app):
        """Test that constructor stores the label."""
        handle = NativeWindowHandle(label="my-window", app=mock_app)
        assert handle._label == "my-window"

    def test_init_stores_app(self, mock_app):
        """Test that constructor stores the app reference."""
        handle = NativeWindowHandle(label="my-window", app=mock_app)
        assert handle._app is mock_app

    def test_label_property(self, native_handle):
        """Test that label property returns the label."""
        assert native_handle.label == "test-window"


# =============================================================================
# NativeWindowHandle Property Tests
# =============================================================================


class TestNativeWindowHandleProperties:
    """Tests for NativeWindowHandle properties."""

    def test_resources_property_returns_lifecycle_resources(self, native_handle, mock_resources):
        """Test that resources property gets from lifecycle."""
        with patch("pywry.window_manager.get_lifecycle") as mock_get_lifecycle:
            mock_lifecycle = MagicMock()
            mock_lifecycle.get.return_value = mock_resources
            mock_get_lifecycle.return_value = mock_lifecycle

            result = native_handle.resources
            assert result is mock_resources
            mock_lifecycle.get.assert_called_once_with("test-window")

    def test_resources_property_returns_none_when_not_found(self, native_handle):
        """Test that resources property returns None if window not found."""
        with patch("pywry.window_manager.get_lifecycle") as mock_get_lifecycle:
            mock_lifecycle = MagicMock()
            mock_lifecycle.get.return_value = None
            mock_get_lifecycle.return_value = mock_lifecycle

            result = native_handle.resources
            assert result is None

    def test_window_property_raises_not_implemented(self, native_handle):
        """Test that window property raises NotImplementedError."""
        with pytest.raises(NotImplementedError) as exc_info:
            _ = native_handle.window

        assert "subprocess mode" in str(exc_info.value)
        assert "test-window" in str(exc_info.value)

    def test_title_property_with_config(self, native_handle, mock_resources):
        """Test title property returns config title."""
        with patch("pywry.window_manager.get_lifecycle") as mock_get_lifecycle:
            mock_lifecycle = MagicMock()
            mock_lifecycle.get.return_value = mock_resources
            mock_get_lifecycle.return_value = mock_lifecycle

            assert native_handle.title == "Test Window"

    def test_title_property_without_resources(self, native_handle):
        """Test title property returns None if no resources."""
        with patch("pywry.window_manager.get_lifecycle") as mock_get_lifecycle:
            mock_lifecycle = MagicMock()
            mock_lifecycle.get.return_value = None
            mock_get_lifecycle.return_value = mock_lifecycle

            assert native_handle.title is None

    def test_title_property_without_config(self, native_handle, mock_resources):
        """Test title property returns None if no config."""
        mock_resources.last_config = None
        with patch("pywry.window_manager.get_lifecycle") as mock_get_lifecycle:
            mock_lifecycle = MagicMock()
            mock_lifecycle.get.return_value = mock_resources
            mock_get_lifecycle.return_value = mock_lifecycle

            assert native_handle.title is None

    def test_config_property(self, native_handle, mock_resources):
        """Test config property returns last_config."""
        with patch("pywry.window_manager.get_lifecycle") as mock_get_lifecycle:
            mock_lifecycle = MagicMock()
            mock_lifecycle.get.return_value = mock_resources
            mock_get_lifecycle.return_value = mock_lifecycle

            assert native_handle.config is mock_resources.last_config

    def test_config_property_none_when_no_resources(self, native_handle):
        """Test config property returns None if no resources."""
        with patch("pywry.window_manager.get_lifecycle") as mock_get_lifecycle:
            mock_lifecycle = MagicMock()
            mock_lifecycle.get.return_value = None
            mock_get_lifecycle.return_value = mock_lifecycle

            assert native_handle.config is None

    def test_html_content_property(self, native_handle, mock_resources):
        """Test html_content property returns content."""
        with patch("pywry.window_manager.get_lifecycle") as mock_get_lifecycle:
            mock_lifecycle = MagicMock()
            mock_lifecycle.get.return_value = mock_resources
            mock_get_lifecycle.return_value = mock_lifecycle

            assert native_handle.html_content == "<h1>Test</h1>"

    def test_html_content_property_none_when_no_resources(self, native_handle):
        """Test html_content property returns None if no resources."""
        with patch("pywry.window_manager.get_lifecycle") as mock_get_lifecycle:
            mock_lifecycle = MagicMock()
            mock_lifecycle.get.return_value = None
            mock_get_lifecycle.return_value = mock_lifecycle

            assert native_handle.html_content is None

    def test_created_at_property(self, native_handle, mock_resources):
        """Test created_at property returns timestamp."""
        with patch("pywry.window_manager.get_lifecycle") as mock_get_lifecycle:
            mock_lifecycle = MagicMock()
            mock_lifecycle.get.return_value = mock_resources
            mock_get_lifecycle.return_value = mock_lifecycle

            assert native_handle.created_at == datetime(2026, 1, 22, 12, 0, 0)

    def test_created_at_property_none_when_no_resources(self, native_handle):
        """Test created_at property returns None if no resources."""
        with patch("pywry.window_manager.get_lifecycle") as mock_get_lifecycle:
            mock_lifecycle = MagicMock()
            mock_lifecycle.get.return_value = None
            mock_get_lifecycle.return_value = mock_lifecycle

            assert native_handle.created_at is None

    def test_is_alive_true_when_exists_and_not_destroyed(self, native_handle, mock_resources):
        """Test is_alive returns True when window exists and not destroyed."""
        mock_resources.is_destroyed = False
        with patch("pywry.window_manager.get_lifecycle") as mock_get_lifecycle:
            mock_lifecycle = MagicMock()
            mock_lifecycle.get.return_value = mock_resources
            mock_get_lifecycle.return_value = mock_lifecycle

            assert native_handle.is_alive is True

    def test_is_alive_false_when_destroyed(self, native_handle, mock_resources):
        """Test is_alive returns False when window is destroyed."""
        mock_resources.is_destroyed = True
        with patch("pywry.window_manager.get_lifecycle") as mock_get_lifecycle:
            mock_lifecycle = MagicMock()
            mock_lifecycle.get.return_value = mock_resources
            mock_get_lifecycle.return_value = mock_lifecycle

            assert native_handle.is_alive is False

    def test_is_alive_false_when_no_resources(self, native_handle):
        """Test is_alive returns False when no resources."""
        with patch("pywry.window_manager.get_lifecycle") as mock_get_lifecycle:
            mock_lifecycle = MagicMock()
            mock_lifecycle.get.return_value = None
            mock_get_lifecycle.return_value = mock_lifecycle

            assert native_handle.is_alive is False


# =============================================================================
# NativeWindowHandle Method Tests
# =============================================================================


class TestNativeWindowHandleMethods:
    """Tests for NativeWindowHandle methods."""

    def test_eval_js_calls_runtime(self, native_handle):
        """Test eval_js calls runtime.eval_js."""
        with patch("pywry.runtime.eval_js") as mock_eval_js:
            native_handle.eval_js("console.log('test')")
            mock_eval_js.assert_called_once_with("test-window", "console.log('test')")

    def test_on_registers_callback(self, native_handle):
        """Test on() registers callback with registry."""
        with patch("pywry.callbacks.get_registry") as mock_get_registry:
            mock_registry = MagicMock()
            mock_get_registry.return_value = mock_registry

            callback = MagicMock()
            result = native_handle.on("click", callback)

            mock_registry.register.assert_called_once_with("test-window", "click", callback)
            assert result is native_handle  # Method chaining

    def test_on_returns_self_for_chaining(self, native_handle):
        """Test on() returns self for method chaining."""
        with patch("pywry.callbacks.get_registry") as mock_get_registry:
            mock_registry = MagicMock()
            mock_get_registry.return_value = mock_registry
            result = native_handle.on("event1", lambda d, t, lbl: None)
            assert result is native_handle

    def test_emit_calls_app_emit(self, native_handle, mock_app):
        """Test emit() calls app.emit with correct args."""
        data = {"value": 42}
        native_handle.emit("update", data)
        mock_app.emit.assert_called_once_with("update", data, "test-window")

    def test_update_calls_lifecycle_set_content(self, native_handle):
        """Test update() calls lifecycle.set_content."""
        with patch("pywry.window_manager.get_lifecycle") as mock_get_lifecycle:
            mock_lifecycle = MagicMock()
            mock_get_lifecycle.return_value = mock_lifecycle

            native_handle.update("<h2>New Content</h2>")
            mock_lifecycle.set_content.assert_called_once_with(
                "test-window", "<h2>New Content</h2>"
            )

    def test_display_is_noop(self, native_handle):
        """Test display() is a no-op for native windows."""
        # Should not raise, just do nothing
        native_handle.display()

    def test_close_calls_runtime(self, native_handle):
        """Test close() calls runtime.close_window."""
        with patch("pywry.runtime.close_window") as mock_close:
            native_handle.close()
            mock_close.assert_called_once_with("test-window")

    def test_hide_calls_runtime(self, native_handle):
        """Test hide() calls runtime.hide_window."""
        with patch("pywry.runtime.hide_window") as mock_hide:
            native_handle.hide()
            mock_hide.assert_called_once_with("test-window")

    def test_show_window_calls_runtime(self, native_handle):
        """Test show_window() calls runtime.show_window."""
        with patch("pywry.runtime.show_window") as mock_show:
            native_handle.show_window()
            mock_show.assert_called_once_with("test-window")

    def test_refresh_calls_runtime(self, native_handle):
        """Test refresh() calls runtime.refresh_window."""
        with patch("pywry.runtime.refresh_window") as mock_refresh:
            mock_refresh.return_value = True
            result = native_handle.refresh()
            mock_refresh.assert_called_once_with("test-window")
            assert result is True

    def test_inject_css_with_asset_id(self, native_handle):
        """Test inject_css() with provided asset_id."""
        with patch("pywry.runtime.inject_css") as mock_inject:
            mock_inject.return_value = True
            result = native_handle.inject_css("body { color: red; }", "my-theme")
            mock_inject.assert_called_once_with("test-window", "body { color: red; }", "my-theme")
            assert result is True

    def test_inject_css_generates_asset_id(self, native_handle):
        """Test inject_css() generates asset_id when not provided."""
        with patch("pywry.runtime.inject_css") as mock_inject:
            mock_inject.return_value = True
            result = native_handle.inject_css("body { color: blue; }")

            # Check that inject_css was called with a generated asset_id
            call_args = mock_inject.call_args
            assert call_args[0][0] == "test-window"
            assert call_args[0][1] == "body { color: blue; }"
            assert call_args[0][2].startswith("pywry-css-")
            assert result is True

    def test_remove_css_calls_runtime(self, native_handle):
        """Test remove_css() calls runtime.remove_css."""
        with patch("pywry.runtime.remove_css") as mock_remove:
            mock_remove.return_value = True
            result = native_handle.remove_css("my-theme")
            mock_remove.assert_called_once_with("test-window", "my-theme")
            assert result is True

    def test_set_content_calls_lifecycle(self, native_handle):
        """Test set_content() calls lifecycle.set_content with theme."""
        with patch("pywry.window_manager.get_lifecycle") as mock_get_lifecycle:
            mock_lifecycle = MagicMock()
            mock_lifecycle.set_content.return_value = True
            mock_get_lifecycle.return_value = mock_lifecycle

            result = native_handle.set_content("<h1>Hello</h1>", "light")
            mock_lifecycle.set_content.assert_called_once_with(
                "test-window", "<h1>Hello</h1>", "light"
            )
            assert result is True

    def test_set_content_default_theme(self, native_handle):
        """Test set_content() uses dark theme by default."""
        with patch("pywry.window_manager.get_lifecycle") as mock_get_lifecycle:
            mock_lifecycle = MagicMock()
            mock_lifecycle.set_content.return_value = True
            mock_get_lifecycle.return_value = mock_lifecycle

            native_handle.set_content("<h1>Hello</h1>")
            mock_lifecycle.set_content.assert_called_once_with(
                "test-window", "<h1>Hello</h1>", "dark"
            )

    def test_get_data_calls_lifecycle(self, native_handle):
        """Test get_data() calls lifecycle.get_data."""
        with patch("pywry.window_manager.get_lifecycle") as mock_get_lifecycle:
            mock_lifecycle = MagicMock()
            mock_lifecycle.get_data.return_value = {"count": 5}
            mock_get_lifecycle.return_value = mock_lifecycle

            result = native_handle.get_data("state")
            mock_lifecycle.get_data.assert_called_once_with("test-window", "state", None)
            assert result == {"count": 5}

    def test_get_data_with_default(self, native_handle):
        """Test get_data() passes default to lifecycle."""
        with patch("pywry.window_manager.get_lifecycle") as mock_get_lifecycle:
            mock_lifecycle = MagicMock()
            mock_lifecycle.get_data.return_value = "default_value"
            mock_get_lifecycle.return_value = mock_lifecycle

            result = native_handle.get_data("missing", "default_value")
            mock_lifecycle.get_data.assert_called_once_with(
                "test-window", "missing", "default_value"
            )
            assert result == "default_value"

    def test_set_data_calls_lifecycle(self, native_handle):
        """Test set_data() calls lifecycle.set_data."""
        with patch("pywry.window_manager.get_lifecycle") as mock_get_lifecycle:
            mock_lifecycle = MagicMock()
            mock_lifecycle.set_data.return_value = True
            mock_get_lifecycle.return_value = mock_lifecycle

            result = native_handle.set_data("state", {"count": 10})
            mock_lifecycle.set_data.assert_called_once_with("test-window", "state", {"count": 10})
            assert result is True


# =============================================================================
# NativeWindowHandle String Representation Tests
# =============================================================================


class TestNativeWindowHandleStringRepresentation:
    """Tests for NativeWindowHandle string methods."""

    def test_str_returns_label(self, native_handle):
        """Test __str__ returns the window label."""
        assert str(native_handle) == "test-window"

    def test_repr_includes_label_and_alive_status(self, native_handle, mock_resources):
        """Test __repr__ includes label and is_alive status."""
        with patch("pywry.window_manager.get_lifecycle") as mock_get_lifecycle:
            mock_lifecycle = MagicMock()
            mock_lifecycle.get.return_value = mock_resources
            mock_get_lifecycle.return_value = mock_lifecycle

            result = repr(native_handle)
            assert "NativeWindowHandle" in result
            assert "test-window" in result
            assert "alive=True" in result

    def test_repr_shows_alive_false_when_destroyed(self, native_handle, mock_resources):
        """Test __repr__ shows alive=False when destroyed."""
        mock_resources.is_destroyed = True
        with patch("pywry.window_manager.get_lifecycle") as mock_get_lifecycle:
            mock_lifecycle = MagicMock()
            mock_lifecycle.get.return_value = mock_resources
            mock_get_lifecycle.return_value = mock_lifecycle

            result = repr(native_handle)
            assert "alive=False" in result


# =============================================================================
# BaseWidget Protocol Tests
# =============================================================================


class TestBaseWidgetProtocol:
    """Tests for BaseWidget protocol and is_base_widget function."""

    def test_native_window_handle_is_base_widget(self, native_handle):
        """Test NativeWindowHandle is recognized as BaseWidget."""
        assert is_base_widget(native_handle) is True

    def test_mock_protocol_implementation_is_base_widget(self):
        """Test that a mock implementing all methods is recognized."""

        class MockWidget:
            """Mock widget implementing BaseWidget protocol for testing."""

            def on(self, event_type, callback):
                """Register event handler."""
                del event_type, callback  # Unused - protocol stub
                return self

            def emit(self, event_type, data):
                """Emit event."""
                del event_type, data  # Unused - protocol stub

            def update(self, html):
                """Update content."""
                del html  # Unused - protocol stub

            def display(self):
                """Display widget."""

        widget = MockWidget()
        assert is_base_widget(widget) is True

    def test_incomplete_implementation_is_not_base_widget(self):
        """Test that incomplete implementations are not recognized."""

        class IncompleteWidget:
            """Incomplete widget missing required methods."""

            def on(self, event_type, callback):
                """Register event handler."""
                del event_type, callback  # Unused - protocol stub
                return self

            # Missing emit, update, display

        widget = IncompleteWidget()
        assert is_base_widget(widget) is False

    def test_plain_object_is_not_base_widget(self):
        """Test that plain objects are not recognized."""
        assert is_base_widget({}) is False
        assert is_base_widget("string") is False
        assert is_base_widget(123) is False
        assert is_base_widget(None) is False

    def test_protocol_type_checking(self):
        """Test that BaseWidget protocol can be used for type checking."""
        # Protocol should be runtime checkable
        assert hasattr(BaseWidget, "__protocol_attrs__") or hasattr(BaseWidget, "__subclasshook__")


# =============================================================================
# NativeWindowHandle Method Chaining Tests
# =============================================================================


class TestNativeWindowHandleMethodChaining:
    """Tests for method chaining support."""

    def test_multiple_on_calls_chain(self, native_handle):
        """Test that multiple on() calls can be chained."""
        with patch("pywry.callbacks.get_registry") as mock_get_registry:
            mock_registry = MagicMock()
            mock_get_registry.return_value = mock_registry
            cb1 = MagicMock()
            cb2 = MagicMock()
            cb3 = MagicMock()

            result = native_handle.on("click", cb1).on("hover", cb2).on("submit", cb3)
            assert result is native_handle


# =============================================================================
# NativeWindowHandle Edge Cases
# =============================================================================


class TestNativeWindowHandleEdgeCases:
    """Edge case tests for NativeWindowHandle."""

    def test_empty_label(self, mock_app):
        """Test handle with empty label."""
        handle = NativeWindowHandle(label="", app=mock_app)
        assert handle.label == ""
        assert str(handle) == ""

    def test_special_characters_in_label(self, mock_app):
        """Test handle with special characters in label."""
        handle = NativeWindowHandle(label="window-123_test", app=mock_app)
        assert handle.label == "window-123_test"

    def test_emit_with_empty_data(self, native_handle, mock_app):
        """Test emit with empty data dict."""
        native_handle.emit("event", {})
        mock_app.emit.assert_called_once_with("event", {}, "test-window")

    def test_emit_with_nested_data(self, native_handle, mock_app):
        """Test emit with nested data structures."""
        nested_data = {
            "level1": {
                "level2": {"value": 42},
                "list": [1, 2, 3],
            }
        }
        native_handle.emit("complex_event", nested_data)
        mock_app.emit.assert_called_once_with("complex_event", nested_data, "test-window")

    def test_eval_js_with_complex_script(self, native_handle):
        """Test eval_js with multi-line script."""
        with patch("pywry.runtime.eval_js") as mock_eval_js:
            script = """
            const x = 1;
            const y = 2;
            console.log(x + y);
            """
            native_handle.eval_js(script)
            mock_eval_js.assert_called_once_with("test-window", script)

    def test_inject_css_with_complex_styles(self, native_handle):
        """Test inject_css with complex CSS content."""
        with patch("pywry.runtime.inject_css") as mock_inject:
            mock_inject.return_value = True
            css = """
            .container {
                display: flex;
                flex-direction: column;
            }
            .item:hover {
                background-color: #f0f0f0;
            }
            @media (max-width: 768px) {
                .container { flex-direction: row; }
            }
            """
            result = native_handle.inject_css(css, "complex-styles")
            assert result is True
            mock_inject.assert_called_once()
