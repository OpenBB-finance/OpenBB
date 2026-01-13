"""Tests for JavaScript bridge scripts.

Tests the PyWry JavaScript bridge and event system scripts.
"""

from pywry.scripts import PYWRY_BRIDGE_JS, build_init_script


class TestPywryBridgeJs:
    """Tests for PYWRY_BRIDGE_JS constant."""

    def test_defines_window_pywry(self):
        """Defines window.pywry object."""
        assert "window.pywry" in PYWRY_BRIDGE_JS

    def test_defines_result_function(self):
        """Defines result function."""
        assert "result" in PYWRY_BRIDGE_JS

    def test_defines_emit_function(self):
        """Defines emit function."""
        assert "emit" in PYWRY_BRIDGE_JS

    def test_defines_on_function(self):
        """Defines on function for event handling."""
        assert ".on" in PYWRY_BRIDGE_JS

    def test_defines_off_function(self):
        """Defines off function for event handling."""
        assert ".off" in PYWRY_BRIDGE_JS

    def test_defines_dispatch_function(self):
        """Defines dispatch function."""
        assert "dispatch" in PYWRY_BRIDGE_JS

    def test_is_string(self):
        """Bridge JS is a string."""
        assert isinstance(PYWRY_BRIDGE_JS, str)

    def test_is_not_empty(self):
        """Bridge JS is not empty."""
        assert len(PYWRY_BRIDGE_JS) > 0


class TestBuildInitScript:
    """Tests for build_init_script function."""

    def test_returns_string(self):
        """Returns a string."""
        script = build_init_script(window_label="main")
        assert isinstance(script, str)

    def test_includes_window_label(self):
        """Includes window label."""
        script = build_init_script(window_label="test-window")
        assert "test-window" in script

    def test_includes_pywry_bridge(self):
        """Includes pywry bridge code."""
        script = build_init_script(window_label="main")
        assert "pywry" in script

    def test_different_labels_produce_different_scripts(self):
        """Different labels produce different scripts."""
        script1 = build_init_script(window_label="window-1")
        script2 = build_init_script(window_label="window-2")
        assert "window-1" in script1
        assert "window-2" in script2


class TestBridgeJsStructure:
    """Tests for bridge JS structure and content."""

    def test_uses_strict_mode(self):
        """Uses strict mode."""
        assert "'use strict'" in PYWRY_BRIDGE_JS or '"use strict"' in PYWRY_BRIDGE_JS

    def test_uses_iife(self):
        """Uses IIFE pattern."""
        assert "(function()" in PYWRY_BRIDGE_JS

    def test_handles_json_payload(self):
        """Handles JSON payload structure."""
        # Should create payload objects
        assert "payload" in PYWRY_BRIDGE_JS


class TestBridgeJsResultFunction:
    """Tests for result function in bridge JS."""

    def test_result_sends_data(self):
        """Result function sends data field."""
        assert "data:" in PYWRY_BRIDGE_JS or "data :" in PYWRY_BRIDGE_JS

    def test_result_sends_window_label(self):
        """Result function sends window_label field."""
        assert "window_label" in PYWRY_BRIDGE_JS


class TestBridgeJsEmitFunction:
    """Tests for emit function in bridge JS."""

    def test_emit_validates_event_type(self):
        """Emit function validates event type."""
        # Should have regex validation
        assert "Invalid" in PYWRY_BRIDGE_JS

    def test_emit_sends_event_type(self):
        """Emit function sends event_type field."""
        assert "event_type" in PYWRY_BRIDGE_JS

    def test_emit_sends_label(self):
        """Emit function sends label field."""
        # Uses label for emit
        assert "label:" in PYWRY_BRIDGE_JS or "label :" in PYWRY_BRIDGE_JS


class TestBridgeJsEventHandlers:
    """Tests for event handler functions in bridge JS."""

    def test_on_creates_handlers_array(self):
        """On function creates handlers array."""
        assert "_handlers" in PYWRY_BRIDGE_JS

    def test_trigger_calls_handlers(self):
        """Trigger function calls handlers."""
        assert "_trigger" in PYWRY_BRIDGE_JS or "trigger" in PYWRY_BRIDGE_JS

    def test_wildcard_handlers_supported(self):
        """Wildcard handlers are supported."""
        assert "'*'" in PYWRY_BRIDGE_JS or '"*"' in PYWRY_BRIDGE_JS


class TestBridgeJsTauriIntegration:
    """Tests for Tauri integration in bridge JS."""

    def test_checks_for_tauri(self):
        """Checks for __TAURI__ object."""
        assert "__TAURI__" in PYWRY_BRIDGE_JS

    def test_uses_pytauri_invoke(self):
        """Uses pytauri.pyInvoke for IPC."""
        assert "pytauri" in PYWRY_BRIDGE_JS
        assert "pyInvoke" in PYWRY_BRIDGE_JS

    def test_invokes_pywry_result(self):
        """Invokes pywry_result command."""
        assert "pywry_result" in PYWRY_BRIDGE_JS

    def test_invokes_pywry_event(self):
        """Invokes pywry_event command."""
        assert "pywry_event" in PYWRY_BRIDGE_JS


class TestBridgeJsHelperFunctions:
    """Tests for helper functions in bridge JS."""

    def test_open_file_function(self):
        """openFile function exists."""
        assert "openFile" in PYWRY_BRIDGE_JS

    def test_devtools_function(self):
        """devtools function exists."""
        assert "devtools" in PYWRY_BRIDGE_JS
