"""Tests for integration functionality.

Tests inter-module communication including:
- IPC protocol
- Callback registry
- Event dispatching
- Window lifecycle events
"""

from unittest.mock import MagicMock

from pywry.callbacks import CallbackRegistry, get_registry
from pywry.config import PyWrySettings
from pywry.models import (
    HtmlContent,
    ThemeMode,
    WindowConfig,
)


class TestCallbackRegistry:
    """Tests for callback registration and invocation."""

    def test_creates_registry(self):
        """Creates callback registry."""
        registry = CallbackRegistry()
        assert registry is not None

    def test_singleton_pattern(self):
        """CallbackRegistry uses singleton pattern."""
        registry1 = CallbackRegistry()
        registry2 = CallbackRegistry()
        assert registry1 is registry2

    def test_get_registry_returns_singleton(self):
        """get_registry returns singleton instance."""
        registry1 = get_registry()
        registry2 = get_registry()
        assert registry1 is registry2

    def test_registers_callback(self):
        """Registers a callback function."""
        registry = get_registry()
        registry.clear()
        callback = MagicMock()
        result = registry.register("main", "test:event", callback)
        assert result is True
        assert "main" in registry._callbacks

    def test_unregisters_callback(self):
        """Unregisters a callback function."""
        registry = get_registry()
        registry.clear()
        callback = MagicMock()
        registry.register("main", "test:event", callback)
        result = registry.unregister("main", "test:event", callback)
        assert result is True

    def test_unregisters_all_for_label(self):
        """Unregisters all callbacks for a label."""
        registry = get_registry()
        registry.clear()
        registry.register("main", "event1:test", MagicMock())
        registry.register("main", "event2:test", MagicMock())
        result = registry.unregister("main")
        assert result is True
        assert "main" not in registry._callbacks

    def test_dispatches_to_callback(self):
        """Dispatches event to registered callback."""
        registry = get_registry()
        registry.clear()
        callback = MagicMock()
        registry.register("main", "test:event", callback)
        registry.dispatch("main", "test:event", {"data": "value"})
        callback.assert_called_once()

    def test_dispatches_multiple_callbacks(self):
        """Dispatches to all callbacks for an event."""
        registry = get_registry()
        registry.clear()
        callback1 = MagicMock()
        callback2 = MagicMock()
        registry.register("main", "test:event", callback1)
        registry.register("main", "test:event", callback2)
        registry.dispatch("main", "test:event", {"data": "value"})
        callback1.assert_called_once()
        callback2.assert_called_once()

    def test_passes_data_to_callback(self):
        """Passes event data to callback."""
        registry = get_registry()
        registry.clear()
        received_data = {}

        def callback(data):
            received_data.update(data)

        registry.register("main", "test:event", callback)
        registry.dispatch("main", "test:event", {"key": "value"})
        assert received_data.get("key") == "value"

    def test_handles_missing_event(self):
        """Handles dispatch of non-existent event."""
        registry = get_registry()
        registry.clear()
        # Should not raise
        result = registry.dispatch("main", "nonexistent:event", {})
        assert result is False

    def test_handles_missing_label(self):
        """Handles dispatch for non-existent label."""
        registry = get_registry()
        registry.clear()
        result = registry.dispatch("nonexistent", "test:event", {})
        assert result is False

    def test_clears_all_callbacks(self):
        """Clears all registered callbacks."""
        registry = get_registry()
        registry.register("win1", "test:event", MagicMock())
        registry.register("win2", "test:event", MagicMock())
        registry.clear()
        assert len(registry._callbacks) == 0

    def test_wildcard_callback(self):
        """Wildcard callback receives all events."""
        registry = get_registry()
        registry.clear()
        calls = []

        def callback(_data, event_type):
            calls.append(event_type)

        registry.register("main", "*", callback)
        registry.dispatch("main", "event1:test", {})
        registry.dispatch("main", "event2:test", {})
        assert len(calls) == 2


class TestEventTypeValidation:
    """Tests for event type validation in registry."""

    def test_valid_event_type(self):
        """Valid event types are accepted."""
        registry = get_registry()
        registry.clear()
        result = registry.register("main", "test:event", MagicMock())
        assert result is True

    def test_invalid_event_type(self):
        """Invalid event types are rejected."""
        registry = get_registry()
        registry.clear()
        result = registry.register("main", "invalid", MagicMock())
        assert result is False


class TestWindowLifecycleCallbacks:
    """Tests for window lifecycle callbacks."""

    def test_window_created_callback(self):
        """Window created callback is invoked."""
        registry = get_registry()
        registry.clear()
        callback = MagicMock()
        registry.register("main", "pywry:created", callback)
        registry.dispatch("main", "pywry:created", {"label": "main"})
        callback.assert_called_once()

    def test_window_closed_callback(self):
        """Window closed callback is invoked."""
        registry = get_registry()
        registry.clear()
        callback = MagicMock()
        registry.register("main", "pywry:closed", callback)
        registry.dispatch("main", "pywry:closed", {"label": "main"})
        callback.assert_called_once()


class TestConfigIntegration:
    """Tests for configuration integration."""

    def test_loads_default_config(self):
        """Loads default configuration."""
        config = PyWrySettings()
        assert config is not None

    def test_loads_config_from_dict(self):
        """Loads configuration from dictionary."""
        config = PyWrySettings(
            window={"width": 800, "height": 600},
        )
        assert config.window.width == 800


class TestModelIntegration:
    """Tests for model integration across modules."""

    def test_html_content_with_all_options(self):
        """HtmlContent with all options."""
        content = HtmlContent(
            html="<div id='app'></div>",
            json_data={"key": "value"},
            init_script="console.log('init');",
            inline_css="body { margin: 0; }",
            watch=True,
        )
        assert content.html == "<div id='app'></div>"
        assert content.json_data == {"key": "value"}
        assert content.init_script == "console.log('init');"
        assert content.inline_css == "body { margin: 0; }"
        assert content.watch is True

    def test_window_config_with_all_options(self):
        """WindowConfig with all options."""
        config = WindowConfig(
            title="Test Window",
            width=1024,
            height=768,
            theme=ThemeMode.LIGHT,
            enable_plotly=True,
            enable_aggrid=True,
            devtools=True,
        )
        assert config.title == "Test Window"
        assert config.width == 1024
        assert config.height == 768
        assert config.theme == ThemeMode.LIGHT
        assert config.enable_plotly is True
        assert config.enable_aggrid is True
        assert config.devtools is True
