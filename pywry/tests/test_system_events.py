"""Unit tests for built-in pywry system event handlers.

Tests verify that all system event handlers are properly registered across
all rendering paths:
- inline.py (IFrame/browser mode)
- widget.py (anywidget notebook mode)
- scripts.py (native Tauri window mode)

System events tested:
- pywry:update-theme - Toggle dark/light mode
- pywry:inject-css - Inject CSS dynamically
- pywry:set-style - Update element inline styles
- pywry:set-content - Update element innerHTML/textContent
- pywry:download - Trigger file download (IFrame mode only)
"""

from __future__ import annotations

from typing import ClassVar


# =============================================================================
# Test fixtures for generated JS code
# =============================================================================


def _get_inline_widget_js() -> str:
    """Get the JavaScript generated for inline IFrame mode."""
    from pywry.inline import _get_pywry_bridge_js

    # Generate the script that goes into IFrame mode
    return _get_pywry_bridge_js(widget_id="test-widget")


def _get_widget_esm() -> str:
    """Get the ESM JavaScript for PyWryWidget (anywidget mode)."""
    from pywry.widget import _WIDGET_ESM

    return _WIDGET_ESM


def _get_hot_reload_js() -> str:
    """Get the JavaScript for native Tauri window mode (hot reload)."""
    from pywry.scripts import HOT_RELOAD_JS

    return HOT_RELOAD_JS


def _get_system_events_js() -> str:
    """Get the JavaScript for system event handlers (pywry:inject-css, etc.)."""
    from pywry.scripts import PYWRY_SYSTEM_EVENTS_JS

    return PYWRY_SYSTEM_EVENTS_JS


def _get_theme_manager_js() -> str:
    """Get the theme manager JavaScript."""
    from pywry.scripts import THEME_MANAGER_JS

    return THEME_MANAGER_JS


# =============================================================================
# Inline Mode (IFrame) System Event Tests
# =============================================================================


class TestInlineModeSystemEvents:
    """Tests for system event handlers in inline IFrame mode."""

    def test_update_theme_handler_registered(self) -> None:
        """Verify pywry:update-theme handler is registered in IFrame mode."""
        js = _get_inline_widget_js()
        assert "pywry:update-theme" in js

    def test_inject_css_handler_registered(self) -> None:
        """Verify pywry:inject-css handler is registered in IFrame mode."""
        js = _get_inline_widget_js()
        assert "pywry:inject-css" in js

    def test_set_style_handler_registered(self) -> None:
        """Verify pywry:set-style handler is registered in IFrame mode."""
        js = _get_inline_widget_js()
        assert "pywry:set-style" in js

    def test_set_content_handler_registered(self) -> None:
        """Verify pywry:set-content handler is registered in IFrame mode."""
        js = _get_inline_widget_js()
        assert "pywry:set-content" in js

    def test_download_handler_registered(self) -> None:
        """Verify pywry:download handler is registered in IFrame mode."""
        js = _get_inline_widget_js()
        assert "pywry:download" in js

    def test_set_style_supports_id_selector(self) -> None:
        """Verify set_style handler supports targeting by id."""
        js = _get_inline_widget_js()
        assert "getElementById" in js

    def test_set_style_supports_css_selector(self) -> None:
        """Verify set_style handler supports targeting by CSS selector."""
        js = _get_inline_widget_js()
        assert "querySelectorAll" in js

    def test_set_content_supports_html(self) -> None:
        """Verify set_content handler supports innerHTML."""
        js = _get_inline_widget_js()
        assert "innerHTML" in js

    def test_set_content_supports_text(self) -> None:
        """Verify set_content handler supports textContent."""
        js = _get_inline_widget_js()
        assert "textContent" in js


# =============================================================================
# PyWryWidget (anywidget) System Event Tests
# =============================================================================


class TestPyWryWidgetSystemEvents:
    """Tests for system event handlers in PyWryWidget (anywidget mode)."""

    def test_update_theme_handler_registered(self) -> None:
        """Verify pywry:update-theme handler is registered in PyWryWidget."""
        esm = _get_widget_esm()
        assert "pywry:update-theme" in esm

    def test_inject_css_handler_registered(self) -> None:
        """Verify pywry:inject-css handler is registered in PyWryWidget."""
        esm = _get_widget_esm()
        assert "pywry:inject-css" in esm

    def test_set_style_handler_registered(self) -> None:
        """Verify pywry:set-style handler is registered in PyWryWidget."""
        esm = _get_widget_esm()
        assert "pywry:set-style" in esm

    def test_set_content_handler_registered(self) -> None:
        """Verify pywry:set-content handler is registered in PyWryWidget."""
        esm = _get_widget_esm()
        assert "pywry:set-content" in esm

    def test_set_style_supports_id_selector(self) -> None:
        """Verify set_style handler supports targeting by id."""
        esm = _get_widget_esm()
        assert "getElementById" in esm

    def test_set_style_supports_css_selector(self) -> None:
        """Verify set_style handler supports targeting by CSS selector."""
        esm = _get_widget_esm()
        assert "querySelectorAll" in esm

    def test_set_content_supports_html(self) -> None:
        """Verify set_content handler supports innerHTML."""
        esm = _get_widget_esm()
        assert "innerHTML" in esm

    def test_set_content_supports_text(self) -> None:
        """Verify set_content handler supports textContent."""
        esm = _get_widget_esm()
        assert "textContent" in esm


# =============================================================================
# Native Tauri Window Mode System Event Tests
# =============================================================================


class TestNativeModeSystemEvents:
    """Tests for system event handlers in native Tauri window mode."""

    def test_inject_css_listener_registered(self) -> None:
        """Verify pywry:inject-css Tauri listener is registered."""
        js = _get_system_events_js()
        assert "pywry:inject-css" in js

    def test_remove_css_listener_registered(self) -> None:
        """Verify pywry:remove-css Tauri listener is registered."""
        js = _get_system_events_js()
        assert "pywry:remove-css" in js

    def test_set_style_listener_registered(self) -> None:
        """Verify pywry:set-style Tauri listener is registered."""
        js = _get_system_events_js()
        assert "pywry:set-style" in js

    def test_set_content_listener_registered(self) -> None:
        """Verify pywry:set-content Tauri listener is registered."""
        js = _get_system_events_js()
        assert "pywry:set-content" in js

    def test_refresh_listener_registered(self) -> None:
        """Verify pywry:refresh Tauri listener is registered."""
        js = _get_system_events_js()
        assert "pywry:refresh" in js

    def test_set_style_supports_id_selector(self) -> None:
        """Verify set_style handler supports targeting by id."""
        js = _get_system_events_js()
        assert "getElementById" in js

    def test_set_style_supports_css_selector(self) -> None:
        """Verify set_style handler supports targeting by CSS selector."""
        js = _get_system_events_js()
        assert "querySelectorAll" in js

    def test_set_content_supports_html(self) -> None:
        """Verify set_content handler supports innerHTML."""
        js = _get_system_events_js()
        assert "innerHTML" in js

    def test_set_content_supports_text(self) -> None:
        """Verify set_content handler supports textContent."""
        js = _get_system_events_js()
        assert "textContent" in js


# =============================================================================
# Theme Manager System Event Tests
# =============================================================================


class TestThemeManagerSystemEvents:
    """Tests for theme-related system events in theme manager."""

    def test_update_theme_handler_registered(self) -> None:
        """Verify pywry:update-theme handler is registered in theme manager."""
        js = _get_theme_manager_js()
        assert "pywry:update-theme" in js

    def test_theme_classes_applied(self) -> None:
        """Verify theme CSS classes are applied."""
        js = _get_theme_manager_js()
        # Theme manager uses 'dark' and 'light' classes (not pywry- prefixed)
        assert "classList.remove('light', 'dark')" in js
        assert "classList.add(resolvedMode)" in js

    def test_class_list_manipulation(self) -> None:
        """Verify classList is used for theme switching."""
        js = _get_theme_manager_js()
        assert "classList" in js


# =============================================================================
# Cross-Path Consistency Tests
# =============================================================================


class TestSystemEventConsistency:
    """Tests to ensure system events are consistent across all rendering paths."""

    CORE_SYSTEM_EVENTS: ClassVar[list[str]] = [
        "pywry:update-theme",
        "pywry:inject-css",
        "pywry:set-style",
        "pywry:set-content",
        "pywry:download",
        "pywry:navigate",
        "pywry:alert",
        "pywry:update-html",
    ]

    def test_inline_has_all_core_events(self) -> None:
        """Inline mode has all core system events."""
        js = _get_inline_widget_js()
        for event in self.CORE_SYSTEM_EVENTS:
            assert event in js, f"Missing {event} in inline mode"

    def test_widget_has_all_core_events(self) -> None:
        """PyWryWidget has all core system events."""
        esm = _get_widget_esm()
        for event in self.CORE_SYSTEM_EVENTS:
            assert event in esm, f"Missing {event} in PyWryWidget"

    def test_native_mode_has_core_style_events(self) -> None:
        """Native mode has core style system events."""
        js = _get_system_events_js()
        native_events = [
            "pywry:inject-css",
            "pywry:set-style",
            "pywry:set-content",
            "pywry:download",
            "pywry:navigate",
            "pywry:alert",
            "pywry:update-html",
        ]
        for event in native_events:
            assert event in js, f"Missing {event} in native mode"


# =============================================================================
# Bridge JS Core Functions Tests
# =============================================================================


class TestPywryBridgeSystemSupport:
    """Tests for pywry bridge system event support."""

    def test_bridge_defines_on_method(self) -> None:
        """Verify bridge JS defines the on() method for event registration."""
        from pywry.scripts import PYWRY_BRIDGE_JS

        assert ".on" in PYWRY_BRIDGE_JS

    def test_bridge_defines_off_method(self) -> None:
        """Verify bridge JS defines the off() method for event unregistration."""
        from pywry.scripts import PYWRY_BRIDGE_JS

        assert ".off" in PYWRY_BRIDGE_JS

    def test_bridge_defines_handlers_storage(self) -> None:
        """Verify bridge JS defines handlers storage."""
        from pywry.scripts import PYWRY_BRIDGE_JS

        assert "_handlers" in PYWRY_BRIDGE_JS

    def test_theme_manager_update_theme_handler(self) -> None:
        """Verify theme manager registers pywry:update-theme handler."""
        js = _get_theme_manager_js()
        assert "pywry:update-theme" in js

    def test_theme_manager_applies_theme_classes(self) -> None:
        """Verify theme manager applies theme CSS classes."""
        js = _get_theme_manager_js()
        # Theme manager uses 'dark' and 'light' classes
        assert "classList.remove('light', 'dark')" in js
        assert "classList.add(resolvedMode)" in js
