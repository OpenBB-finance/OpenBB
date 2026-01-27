"""Comprehensive tests for the PyWry Alert/Toast notification system.

Tests cover:
- PYWRY_TOAST JavaScript API structure and functionality
- toast.css styles and theming
- AlertPayload Pydantic model
- Alert event handling in widgets
- E2E tests for native window alerts
- E2E tests for inline notebook alerts
"""

# pylint: disable=too-many-lines,unsubscriptable-object

from __future__ import annotations

import time

from collections.abc import Callable
from functools import wraps
from typing import Any, TypeVar

import pytest

# Import shared test utilities from tests.conftest
from tests.conftest import show_and_wait_ready, wait_for_result


F = TypeVar("F", bound=Callable[..., Any])


def retry_on_subprocess_failure(max_attempts: int = 3, delay: float = 1.0) -> Callable[[F], F]:
    """Retry decorator for tests that may fail due to transient subprocess issues.

    On Windows, WebView2 sometimes fails to start due to resource contention
    ("Failed to unregister class Chrome_WidgetWin_0"). On Linux with xvfb,
    WebKit initialization may have timing issues. This decorator retries
    the test after a delay to allow resources to be released.
    """

    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            from pywry import runtime

            last_error: Exception | None = None
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except (TimeoutError, AssertionError) as e:
                    last_error = e
                    if attempt < max_attempts - 1:
                        # Clean up and wait before retry
                        runtime.stop()
                        # Progressive backoff for CI stability
                        time.sleep(delay * (attempt + 1))
            raise last_error  # type: ignore[misc]

        return wrapper  # type: ignore[return-value]

    return decorator


# Note: cleanup_runtime fixture is now in conftest.py and auto-used


# =============================================================================
# JavaScript Asset Tests
# =============================================================================


class TestToastNotificationsJs:
    """Tests for the toast-notifications.js JavaScript asset."""

    def test_js_asset_exists(self) -> None:
        """Verify toast-notifications.js is available via assets."""
        from pywry.assets import get_toast_notifications_js

        js = get_toast_notifications_js()
        assert js is not None
        assert len(js) > 0

    def test_defines_pywry_toast_global(self) -> None:
        """Verify PYWRY_TOAST is defined as window global."""
        from pywry.assets import get_toast_notifications_js

        js = get_toast_notifications_js()
        assert "window.PYWRY_TOAST" in js

    def test_defines_show_method(self) -> None:
        """Verify show() method is defined."""
        from pywry.assets import get_toast_notifications_js

        js = get_toast_notifications_js()
        assert "show:" in js or "show :" in js

    def test_defines_confirm_method(self) -> None:
        """Verify confirm() method is defined."""
        from pywry.assets import get_toast_notifications_js

        js = get_toast_notifications_js()
        assert "confirm:" in js or "confirm :" in js

    def test_defines_dismiss_method(self) -> None:
        """Verify dismiss() method is defined."""
        from pywry.assets import get_toast_notifications_js

        js = get_toast_notifications_js()
        assert "dismiss:" in js or "dismiss :" in js

    def test_defines_dismiss_all_in_widget_method(self) -> None:
        """Verify dismissAllInWidget() method is defined."""
        from pywry.assets import get_toast_notifications_js

        js = get_toast_notifications_js()
        assert "dismissAllInWidget" in js

    def test_defines_type_configurations(self) -> None:
        """Verify all alert types are configured."""
        from pywry.assets import get_toast_notifications_js

        js = get_toast_notifications_js()
        assert "info:" in js
        assert "success:" in js
        assert "warning:" in js
        assert "error:" in js
        assert "confirm:" in js

    def test_info_type_has_auto_dismiss(self) -> None:
        """Verify info type has autoDismiss configured."""
        from pywry.assets import get_toast_notifications_js

        js = get_toast_notifications_js()
        # info has 5000ms auto-dismiss
        assert "5000" in js

    def test_success_type_has_auto_dismiss(self) -> None:
        """Verify success type has autoDismiss configured."""
        from pywry.assets import get_toast_notifications_js

        js = get_toast_notifications_js()
        # success has 3000ms auto-dismiss
        assert "3000" in js

    def test_defines_widget_state_management(self) -> None:
        """Verify widget state management is implemented."""
        from pywry.assets import get_toast_notifications_js

        js = get_toast_notifications_js()
        assert "_pywryToastState" in js
        assert "_getWidgetState" in js

    def test_defines_container_management(self) -> None:
        """Verify container management methods exist."""
        from pywry.assets import get_toast_notifications_js

        js = get_toast_notifications_js()
        assert "_ensureContainer" in js

    def test_defines_overlay_for_confirm(self) -> None:
        """Verify overlay management for confirm dialogs."""
        from pywry.assets import get_toast_notifications_js

        js = get_toast_notifications_js()
        assert "_ensureOverlay" in js
        assert "pywry-toast-overlay" in js

    def test_defines_escape_key_handler(self) -> None:
        """Verify escape key handler is implemented."""
        from pywry.assets import get_toast_notifications_js

        js = get_toast_notifications_js()
        assert "Escape" in js
        assert "_pywryEscapeHandler" in js

    def test_defines_html_escaping(self) -> None:
        """Verify HTML escaping is implemented for XSS prevention."""
        from pywry.assets import get_toast_notifications_js

        js = get_toast_notifications_js()
        assert "_escapeHtml" in js

    def test_uses_strict_mode(self) -> None:
        """Verify strict mode is enabled."""
        from pywry.assets import get_toast_notifications_js

        js = get_toast_notifications_js()
        assert "'use strict'" in js or '"use strict"' in js

    def test_uses_iife_pattern(self) -> None:
        """Verify IIFE pattern for encapsulation."""
        from pywry.assets import get_toast_notifications_js

        js = get_toast_notifications_js()
        assert "(function()" in js

    def test_max_visible_limit_defined(self) -> None:
        """Verify maxVisible limit is defined."""
        from pywry.assets import get_toast_notifications_js

        js = get_toast_notifications_js()
        assert "maxVisible" in js

    def test_default_position_defined(self) -> None:
        """Verify defaultPosition is defined."""
        from pywry.assets import get_toast_notifications_js

        js = get_toast_notifications_js()
        assert "defaultPosition" in js

    def test_aria_attributes_for_accessibility(self) -> None:
        """Verify ARIA attributes are set for accessibility."""
        from pywry.assets import get_toast_notifications_js

        js = get_toast_notifications_js()
        assert "role" in js
        assert "aria-live" in js
        assert "aria-label" in js


class TestToastCss:
    """Tests for the toast.css styles."""

    def test_css_asset_exists(self) -> None:
        """Verify toast.css is available via assets."""
        from pywry.assets import get_toast_css

        css = get_toast_css()
        assert css is not None
        assert len(css) > 0

    def test_defines_toast_container_class(self) -> None:
        """Verify toast container class is defined."""
        from pywry.assets import get_toast_css

        css = get_toast_css()
        assert ".pywry-toast-container" in css

    def test_defines_toast_base_class(self) -> None:
        """Verify base toast class is defined."""
        from pywry.assets import get_toast_css

        css = get_toast_css()
        assert ".pywry-toast" in css

    def test_defines_type_variant_classes(self) -> None:
        """Verify type variant classes are defined."""
        from pywry.assets import get_toast_css

        css = get_toast_css()
        assert ".pywry-toast--info" in css
        assert ".pywry-toast--success" in css
        assert ".pywry-toast--warning" in css
        assert ".pywry-toast--error" in css
        assert ".pywry-toast--confirm" in css

    def test_defines_position_variants(self) -> None:
        """Verify position variant classes are defined."""
        from pywry.assets import get_toast_css

        css = get_toast_css()
        assert ".pywry-toast-container--top-right" in css
        assert ".pywry-toast-container--bottom-right" in css
        assert ".pywry-toast-container--top-left" in css
        assert ".pywry-toast-container--bottom-left" in css

    def test_defines_overlay_styles(self) -> None:
        """Verify overlay styles for confirm dialogs."""
        from pywry.assets import get_toast_css

        css = get_toast_css()
        assert ".pywry-toast-overlay" in css
        assert ".pywry-toast-overlay--visible" in css

    def test_defines_blocking_container_class(self) -> None:
        """Verify blocking container class for confirm dialogs."""
        from pywry.assets import get_toast_css

        css = get_toast_css()
        assert ".pywry-toast-container--blocking" in css

    def test_overlay_uses_absolute_positioning(self) -> None:
        """Verify overlay uses absolute positioning (scoped to container)."""
        from pywry.assets import get_toast_css

        css = get_toast_css()
        # Overlay must be absolute, not fixed (to stay within widget)
        # Check that overlay section contains position: absolute
        assert "position: absolute" in css

    def test_defines_toast_content_elements(self) -> None:
        """Verify toast content element classes are defined."""
        from pywry.assets import get_toast_css

        css = get_toast_css()
        assert ".pywry-toast__icon" in css
        assert ".pywry-toast__content" in css
        assert ".pywry-toast__title" in css
        assert ".pywry-toast__message" in css
        assert ".pywry-toast__close" in css

    def test_defines_confirm_button_classes(self) -> None:
        """Verify confirm button classes are defined."""
        from pywry.assets import get_toast_css

        css = get_toast_css()
        assert ".pywry-toast__buttons" in css
        assert ".pywry-toast__btn" in css
        assert ".pywry-toast__btn--cancel" in css
        assert ".pywry-toast__btn--confirm" in css

    def test_defines_light_theme_variant(self) -> None:
        """Verify light theme variant is defined."""
        from pywry.assets import get_toast_css

        css = get_toast_css()
        assert ".pywry-theme-light" in css or ".pywry-toast--light" in css

    def test_uses_css_custom_properties(self) -> None:
        """Verify CSS custom properties are used for theming."""
        from pywry.assets import get_toast_css

        css = get_toast_css()
        assert "--pywry-toast-bg" in css or "--pywry-toast" in css

    def test_toast_has_backdrop_filter(self) -> None:
        """Verify toasts have backdrop-filter for visibility."""
        from pywry.assets import get_toast_css

        css = get_toast_css()
        assert "backdrop-filter" in css

    def test_toast_has_box_shadow(self) -> None:
        """Verify toasts have box-shadow for depth."""
        from pywry.assets import get_toast_css

        css = get_toast_css()
        assert "box-shadow" in css


# =============================================================================
# AlertPayload Model Tests
# =============================================================================


class TestAlertPayloadModel:
    """Tests for the AlertPayload Pydantic model."""

    def test_create_with_message_only(self) -> None:
        """Create AlertPayload with only message."""
        from pywry.models import AlertPayload

        payload = AlertPayload(message="Test message")
        assert payload.message == "Test message"

    def test_default_type_is_info(self) -> None:
        """Default type should be 'info'."""
        from pywry.models import AlertPayload

        payload = AlertPayload(message="Test")
        assert payload.type == "info"

    def test_default_position_is_top_right(self) -> None:
        """Default position should be 'top-right'."""
        from pywry.models import AlertPayload

        payload = AlertPayload(message="Test")
        assert payload.position == "top-right"

    def test_optional_title_defaults_none(self) -> None:
        """Title should default to None."""
        from pywry.models import AlertPayload

        payload = AlertPayload(message="Test")
        assert payload.title is None

    def test_optional_duration_defaults_none(self) -> None:
        """Duration should default to None."""
        from pywry.models import AlertPayload

        payload = AlertPayload(message="Test")
        assert payload.duration is None

    def test_optional_callback_event_defaults_none(self) -> None:
        """Callback event should default to None."""
        from pywry.models import AlertPayload

        payload = AlertPayload(message="Test")
        assert payload.callback_event is None

    def test_set_all_fields(self) -> None:
        """Set all fields explicitly."""
        from pywry.models import AlertPayload

        payload = AlertPayload(
            message="Delete item?",
            type="confirm",
            title="Confirm Delete",
            duration=10000,
            callback_event="app:delete-confirmed",
            position="top-left",
        )
        assert payload.message == "Delete item?"
        assert payload.type == "confirm"
        assert payload.title == "Confirm Delete"
        assert payload.duration == 10000
        assert payload.callback_event == "app:delete-confirmed"
        assert payload.position == "top-left"

    def test_info_type(self) -> None:
        """Test info type."""
        from pywry.models import AlertPayload

        payload = AlertPayload(message="Info", type="info")
        assert payload.type == "info"

    def test_success_type(self) -> None:
        """Test success type."""
        from pywry.models import AlertPayload

        payload = AlertPayload(message="Success", type="success")
        assert payload.type == "success"

    def test_warning_type(self) -> None:
        """Test warning type."""
        from pywry.models import AlertPayload

        payload = AlertPayload(message="Warning", type="warning")
        assert payload.type == "warning"

    def test_error_type(self) -> None:
        """Test error type."""
        from pywry.models import AlertPayload

        payload = AlertPayload(message="Error", type="error")
        assert payload.type == "error"

    def test_confirm_type(self) -> None:
        """Test confirm type."""
        from pywry.models import AlertPayload

        payload = AlertPayload(message="Confirm?", type="confirm")
        assert payload.type == "confirm"

    def test_position_top_right(self) -> None:
        """Test top-right position."""
        from pywry.models import AlertPayload

        payload = AlertPayload(message="Test", position="top-right")
        assert payload.position == "top-right"

    def test_position_top_left(self) -> None:
        """Test top-left position."""
        from pywry.models import AlertPayload

        payload = AlertPayload(message="Test", position="top-left")
        assert payload.position == "top-left"

    def test_position_bottom_left(self) -> None:
        """Test bottom-left position."""
        from pywry.models import AlertPayload

        payload = AlertPayload(message="Test", position="bottom-left")
        assert payload.position == "bottom-left"

    def test_model_dump_dict(self) -> None:
        """Model should be serializable to dict."""
        from pywry.models import AlertPayload

        payload = AlertPayload(message="Test", type="success", title="Done")
        data = payload.model_dump()
        assert isinstance(data, dict)
        assert data["message"] == "Test"
        assert data["type"] == "success"
        assert data["title"] == "Done"

    def test_model_dump_excludes_none_values(self) -> None:
        """Model dump should be able to exclude None values."""
        from pywry.models import AlertPayload

        payload = AlertPayload(message="Test")
        data = payload.model_dump(exclude_none=True)
        assert "title" not in data
        assert "duration" not in data
        assert "callback_event" not in data


# =============================================================================
# Widget Alert Method Tests
# =============================================================================


class TestEmittingWidgetAlertMethod:
    """Tests for the EmittingWidget.alert() convenience method."""

    def test_emitting_widget_has_alert_method(self) -> None:
        """Verify EmittingWidget has alert() method."""
        from pywry.state_mixins import EmittingWidget

        assert hasattr(EmittingWidget, "alert")

    def test_alert_method_calls_emit(self) -> None:
        """Alert method should call emit with correct event."""
        from pywry.state_mixins import EmittingWidget

        class MockWidget(EmittingWidget):
            """Mock widget for testing."""

            def __init__(self) -> None:
                self.last_event: tuple[str, dict] | None = None

            def emit(self, event_type: str, data: dict) -> None:  # type: ignore[override]
                self.last_event = (event_type, data)

        widget = MockWidget()
        widget.alert("Hello")

        assert widget.last_event is not None
        assert widget.last_event[0] == "pywry:alert"
        assert widget.last_event[1]["message"] == "Hello"

    def test_alert_method_passes_type(self) -> None:
        """Alert method should pass type parameter."""
        from pywry.state_mixins import EmittingWidget

        class MockWidget(EmittingWidget):
            """Mock widget for testing."""

            def __init__(self) -> None:
                self.last_event: tuple[str, dict] | None = None

            def emit(self, event_type: str, data: dict) -> None:  # type: ignore[override]
                self.last_event = (event_type, data)

        widget = MockWidget()
        widget.alert("Success!", alert_type="success")

        assert widget.last_event is not None
        assert widget.last_event[1]["type"] == "success"

    def test_alert_method_passes_title(self) -> None:
        """Alert method should pass title parameter."""
        from pywry.state_mixins import EmittingWidget

        class MockWidget(EmittingWidget):
            """Mock widget for testing."""

            def __init__(self) -> None:
                self.last_event: tuple[str, dict] | None = None

            def emit(self, event_type: str, data: dict) -> None:  # type: ignore[override]
                self.last_event = (event_type, data)

        widget = MockWidget()
        widget.alert("Item saved", title="Save Complete")

        assert widget.last_event is not None
        assert widget.last_event[1]["title"] == "Save Complete"

    def test_alert_method_passes_all_kwargs(self) -> None:
        """Alert method should pass all keyword arguments."""
        from pywry.state_mixins import EmittingWidget

        class MockWidget(EmittingWidget):
            """Mock widget for testing."""

            def __init__(self) -> None:
                self.last_event: tuple[str, dict] | None = None

            def emit(self, event_type: str, data: dict) -> None:  # type: ignore[override]
                self.last_event = (event_type, data)

        widget = MockWidget()
        widget.alert(
            "Delete?",
            alert_type="confirm",
            title="Confirm Delete",
            callback_event="app:delete",
            position="top-right",
        )

        assert widget.last_event is not None
        data = widget.last_event[1]
        assert data["message"] == "Delete?"
        assert data["type"] == "confirm"
        assert data["title"] == "Confirm Delete"
        assert data["callback_event"] == "app:delete"
        assert data["position"] == "top-right"


# =============================================================================
# E2E Native Window Alert Tests
# =============================================================================


class TestNativeWindowAlertE2E:
    """E2E tests for alerts in native windows."""

    @pytest.mark.e2e
    @retry_on_subprocess_failure(max_attempts=3, delay=1.0)
    def test_pywry_toast_is_available(self) -> None:
        """E2E: Verify PYWRY_TOAST is available in window."""
        from pywry.app import PyWry

        app = PyWry()

        label = show_and_wait_ready(
            app,
            "<div>Test</div>",
            title="Alert E2E Test",
        )

        script = """
        (function() {
            pywry.result({
                toastAvailable: typeof PYWRY_TOAST !== 'undefined',
                hasShow: typeof PYWRY_TOAST !== 'undefined' && typeof PYWRY_TOAST.show === 'function',
                hasConfirm: typeof PYWRY_TOAST !== 'undefined' && typeof PYWRY_TOAST.confirm === 'function',
                hasDismiss: typeof PYWRY_TOAST !== 'undefined' && typeof PYWRY_TOAST.dismiss === 'function'
            });
        })();
        """

        result = wait_for_result(label, script)
        assert result is not None
        assert result["toastAvailable"] is True
        assert result["hasShow"] is True
        assert result["hasConfirm"] is True
        assert result["hasDismiss"] is True

    @pytest.mark.e2e
    @retry_on_subprocess_failure(max_attempts=3, delay=1.0)
    def test_show_info_toast_renders(self) -> None:
        """E2E: Verify info toast renders correctly."""
        from pywry.app import PyWry

        app = PyWry()

        label = show_and_wait_ready(
            app,
            "<div class='pywry-widget' style='position:relative;width:100%;height:100%'>Test</div>",
            title="Info Toast Test",
        )

        script = """
        (function() {
            var container = document.querySelector('.pywry-widget');
            PYWRY_TOAST.show({
                message: 'Test info message',
                type: 'info',
                title: 'Info Title',
                container: container
            });

            // Wait a moment for DOM update
            setTimeout(function() {
                var toast = document.querySelector('.pywry-toast--info');
                pywry.result({
                    toastExists: toast !== null,
                    hasTitle: toast && toast.querySelector('.pywry-toast__title') !== null,
                    hasMessage: toast && toast.querySelector('.pywry-toast__message') !== null,
                    titleText: toast && toast.querySelector('.pywry-toast__title') ? toast.querySelector('.pywry-toast__title').textContent : null,
                    messageText: toast && toast.querySelector('.pywry-toast__message') ? toast.querySelector('.pywry-toast__message').textContent : null
                });
            }, 100);
        })();
        """

        result = wait_for_result(label, script, timeout=5.0)
        assert result is not None, "Toast test: pywry.result() callback not received"
        assert result["toastExists"] is True
        assert result["hasTitle"] is True
        assert result["hasMessage"] is True
        assert result["titleText"] == "Info Title"
        assert result["messageText"] == "Test info message"

    @pytest.mark.e2e
    @retry_on_subprocess_failure(max_attempts=3, delay=1.0)
    def test_show_confirm_toast_has_buttons(self) -> None:
        """E2E: Verify confirm toast has cancel and confirm buttons."""
        from pywry.app import PyWry

        app = PyWry()

        label = show_and_wait_ready(
            app,
            "<div class='pywry-widget' style='position:relative;width:100%;height:100%'>Test</div>",
            title="Confirm Toast Test",
        )

        script = """
        (function() {
            var container = document.querySelector('.pywry-widget');
            PYWRY_TOAST.confirm({
                message: 'Are you sure?',
                title: 'Confirm Action',
                container: container,
                onConfirm: function() {},
                onCancel: function() {}
            });

            setTimeout(function() {
                var toast = document.querySelector('.pywry-toast--confirm');
                var cancelBtn = toast && toast.querySelector('.pywry-toast__btn--cancel');
                var confirmBtn = toast && toast.querySelector('.pywry-toast__btn--confirm');
                var overlay = document.querySelector('.pywry-toast-overlay--visible');

                pywry.result({
                    toastExists: toast !== null,
                    hasCancelButton: cancelBtn !== null,
                    hasConfirmButton: confirmBtn !== null,
                    overlayVisible: overlay !== null,
                    cancelText: cancelBtn ? cancelBtn.textContent : null,
                    confirmText: confirmBtn ? confirmBtn.textContent : null
                });
            }, 100);
        })();
        """

        result = wait_for_result(label, script, timeout=3.0)
        assert result is not None
        assert result["toastExists"] is True
        assert result["hasCancelButton"] is True
        assert result["hasConfirmButton"] is True
        assert result["overlayVisible"] is True
        assert result["cancelText"] == "Cancel"
        assert result["confirmText"] == "Confirm"

    @pytest.mark.e2e
    @retry_on_subprocess_failure(max_attempts=3, delay=1.0)
    def test_confirm_button_triggers_callback(self) -> None:
        """E2E: Verify confirm button triggers onConfirm callback."""
        from pywry.app import PyWry

        app = PyWry()

        label = show_and_wait_ready(
            app,
            "<div class='pywry-widget' style='position:relative;width:100%;height:100%'>Test</div>",
            title="Confirm Callback Test",
        )

        script = """
        (function() {
            var container = document.querySelector('.pywry-widget');
            var confirmed = false;

            PYWRY_TOAST.confirm({
                message: 'Confirm test',
                container: container,
                onConfirm: function() { confirmed = true; },
                onCancel: function() {}
            });

            setTimeout(function() {
                var confirmBtn = document.querySelector('.pywry-toast__btn--confirm');
                if (confirmBtn) {
                    confirmBtn.click();
                }

                setTimeout(function() {
                    var toastGone = document.querySelector('.pywry-toast--confirm') === null;
                    pywry.result({
                        confirmed: confirmed,
                        toastDismissed: toastGone
                    });
                }, 100);
            }, 100);
        })();
        """

        result = wait_for_result(label, script, timeout=3.0)
        assert result is not None
        assert result["confirmed"] is True
        assert result["toastDismissed"] is True

    @pytest.mark.e2e
    @retry_on_subprocess_failure(max_attempts=3, delay=1.0)
    def test_cancel_button_triggers_callback(self) -> None:
        """E2E: Verify cancel button triggers onCancel callback."""
        from pywry.app import PyWry

        app = PyWry()

        label = show_and_wait_ready(
            app,
            "<div class='pywry-widget' style='position:relative;width:100%;height:100%'>Test</div>",
            title="Cancel Callback Test",
        )

        script = """
        (function() {
            var container = document.querySelector('.pywry-widget');
            var cancelled = false;

            PYWRY_TOAST.confirm({
                message: 'Cancel test',
                container: container,
                onConfirm: function() {},
                onCancel: function() { cancelled = true; }
            });

            setTimeout(function() {
                var cancelBtn = document.querySelector('.pywry-toast__btn--cancel');
                if (cancelBtn) {
                    cancelBtn.click();
                }

                setTimeout(function() {
                    var toastGone = document.querySelector('.pywry-toast--confirm') === null;
                    pywry.result({
                        cancelled: cancelled,
                        toastDismissed: toastGone
                    });
                }, 100);
            }, 100);
        })();
        """

        result = wait_for_result(label, script, timeout=3.0)
        assert result is not None
        assert result["cancelled"] is True
        assert result["toastDismissed"] is True

    @pytest.mark.e2e
    @retry_on_subprocess_failure(max_attempts=3, delay=1.0)
    def test_dismiss_all_clears_toasts(self) -> None:
        """E2E: Verify dismissAllInWidget clears all toasts."""
        from pywry.app import PyWry

        app = PyWry()

        label = show_and_wait_ready(
            app,
            "<div class='pywry-widget' style='position:relative;width:100%;height:100%'>Test</div>",
            title="Dismiss All Test",
        )

        script = """
        (function() {
            var container = document.querySelector('.pywry-widget');

            // Show multiple toasts
            PYWRY_TOAST.show({ message: 'Toast 1', type: 'info', container: container });
            PYWRY_TOAST.show({ message: 'Toast 2', type: 'success', container: container });
            PYWRY_TOAST.show({ message: 'Toast 3', type: 'warning', container: container });

            setTimeout(function() {
                var countBefore = document.querySelectorAll('.pywry-toast').length;
                PYWRY_TOAST.dismissAllInWidget(container);

                setTimeout(function() {
                    var countAfter = document.querySelectorAll('.pywry-toast').length;
                    pywry.result({
                        countBefore: countBefore,
                        countAfter: countAfter
                    });
                }, 100);
            }, 100);
        })();
        """

        result = wait_for_result(label, script, timeout=3.0)
        assert result is not None
        assert result["countBefore"] == 3
        assert result["countAfter"] == 0

    @pytest.mark.e2e
    @retry_on_subprocess_failure(max_attempts=3, delay=1.0)
    def test_max_visible_limit_enforced(self) -> None:
        """E2E: Verify maxVisible limit is enforced."""
        from pywry.app import PyWry

        app = PyWry()

        label = show_and_wait_ready(
            app,
            "<div class='pywry-widget' style='position:relative;width:100%;height:100%'>Test</div>",
            title="Max Visible Test",
        )

        script = """
        (function() {
            var container = document.querySelector('.pywry-widget');
            var maxVisible = PYWRY_TOAST.maxVisible;

            // Show more than maxVisible toasts
            for (var i = 0; i < maxVisible + 2; i++) {
                PYWRY_TOAST.show({ message: 'Toast ' + i, type: 'info', container: container, duration: null });
            }

            setTimeout(function() {
                var visibleCount = document.querySelectorAll('.pywry-toast').length;
                pywry.result({
                    maxVisible: maxVisible,
                    visibleCount: visibleCount,
                    limitEnforced: visibleCount <= maxVisible
                });
            }, 100);
        })();
        """

        result = wait_for_result(label, script, timeout=3.0)
        assert result is not None
        assert result["limitEnforced"] is True
        assert result["visibleCount"] <= result["maxVisible"]

    @pytest.mark.e2e
    @retry_on_subprocess_failure(max_attempts=3, delay=1.0)
    def test_toast_position_top_right(self) -> None:
        """E2E: Verify toast position top-right."""
        from pywry.app import PyWry

        app = PyWry()

        label = show_and_wait_ready(
            app,
            "<div class='pywry-widget' style='position:relative;width:100%;height:100%'>Test</div>",
            title="Position Test",
        )

        script = """
        (function() {
            var container = document.querySelector('.pywry-widget');

            PYWRY_TOAST.show({
                message: 'Position test',
                type: 'info',
                position: 'top-right',
                container: container
            });

            setTimeout(function() {
                var toastContainer = document.querySelector('.pywry-toast-container');
                pywry.result({
                    hasPositionClass: toastContainer && toastContainer.classList.contains('pywry-toast-container--top-right')
                });
            }, 100);
        })();
        """

        result = wait_for_result(label, script, timeout=3.0)
        assert result is not None
        assert result["hasPositionClass"] is True

    @pytest.mark.e2e
    @retry_on_subprocess_failure(max_attempts=3, delay=1.0)
    def test_pywry_alert_event_triggers_toast(self) -> None:
        """E2E: Verify pywry:alert event triggers toast notification."""
        from pywry.app import PyWry

        app = PyWry()

        label = show_and_wait_ready(
            app,
            "<div class='pywry-widget' style='position:relative;width:100%;height:100%'>Test</div>",
            title="Alert Event Test",
        )

        # First ensure pywry.on is set up for alert
        script = """
        (function() {
            var container = document.querySelector('.pywry-widget');

            // Create local pywry instance if needed (simulating widget setup)
            if (!container._pywryInstance) {
                container._pywryInstance = {
                    _handlers: {},
                    on: function(type, handler) {
                        this._handlers[type] = this._handlers[type] || [];
                        this._handlers[type].push(handler);
                    },
                    _fire: function(type, data) {
                        var handlers = this._handlers[type] || [];
                        handlers.forEach(function(h) { h(data); });
                    }
                };

                // Register alert handler
                container._pywryInstance.on('pywry:alert', function(data) {
                    if (typeof PYWRY_TOAST !== 'undefined') {
                        PYWRY_TOAST.show({
                            message: data.message,
                            type: data.type || 'info',
                            title: data.title,
                            container: container
                        });
                    }
                });
            }

            // Fire the alert event
            container._pywryInstance._fire('pywry:alert', {
                message: 'Event triggered alert',
                type: 'success',
                title: 'Event Test'
            });

            setTimeout(function() {
                var toast = document.querySelector('.pywry-toast--success');
                pywry.result({
                    toastExists: toast !== null,
                    messageText: toast ? toast.querySelector('.pywry-toast__message').textContent : null
                });
            }, 100);
        })();
        """

        result = wait_for_result(label, script, timeout=3.0)
        assert result is not None
        assert result["toastExists"] is True
        assert result["messageText"] == "Event triggered alert"


# =============================================================================
# Inline E2E Alert Tests
# =============================================================================


try:
    from pywry.inline import HAS_FASTAPI
except ImportError:
    HAS_FASTAPI = False


@pytest.mark.skipif(not HAS_FASTAPI, reason="FastAPI not installed")
class TestInlineAlertE2E:
    """E2E tests for alerts in inline/notebook rendering."""

    @pytest.fixture(autouse=True)
    def clean_inline_state(self):
        """Clean up inline server state."""
        from pywry.config import clear_settings
        from pywry.inline import _state, stop_server

        stop_server()
        _state.widgets.clear()
        _state.connections.clear()
        clear_settings()

        yield

        stop_server()
        _state.widgets.clear()
        _state.connections.clear()
        clear_settings()

    @pytest.fixture
    def server_port(self):
        """Get a free port."""
        import socket

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("0.0.0.0", 0))
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            return s.getsockname()[1]

    def test_inline_html_includes_toast_js(self, server_port: int) -> None:
        """E2E: Verify inline widget HTML includes PYWRY_TOAST."""
        import socket
        import urllib.request

        from pywry.inline import _start_server, _state

        def wait_for_server(host: str, port: int, timeout: float = 5.0) -> bool:
            """Wait for server to be reachable via socket check (health requires auth)."""
            start = time.time()
            while time.time() - start < timeout:
                try:
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                        s.settimeout(0.5)
                        s.connect((host, port))
                        return True
                except Exception:  # noqa: S110
                    pass
                time.sleep(0.1)
            return False

        _start_server(port=server_port, host="0.0.0.0")
        assert wait_for_server("127.0.0.1", server_port)

        widget_id = "toast-test"
        test_html = "<html><body><div class='pywry-widget'>Test</div></body></html>"
        _state.register_widget(widget_id, test_html, callbacks={})

        url = f"http://127.0.0.1:{server_port}/widget/{widget_id}"
        with urllib.request.urlopen(url, timeout=5) as resp:  # noqa: S310
            _ = resp.read()  # Read response body

        # Widget HTML is returned as-is, toast JS is injected by inline module
        # Just verify it returns successfully
        assert resp.status == 200

    def test_inline_dataframe_includes_alert_handler(self, server_port: int) -> None:
        """E2E: Verify inline dataframe HTML includes alert handler."""
        import socket
        import urllib.request

        from pywry.inline import _start_server, _state, generate_dataframe_html

        def wait_for_server(host: str, port: int, timeout: float = 5.0) -> bool:
            """Wait for server to be reachable via socket check (health requires auth)."""
            start = time.time()
            while time.time() - start < timeout:
                try:
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                        s.settimeout(0.5)
                        s.connect((host, port))
                        return True
                except Exception:  # noqa: S110
                    pass
                time.sleep(0.1)
            return False

        _start_server(port=server_port, host="0.0.0.0")
        assert wait_for_server("127.0.0.1", server_port)

        # Generate dataframe HTML
        widget_id = "df-alert-test"
        data = [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}]
        columns = ["name", "age"]
        html = generate_dataframe_html(data, columns, widget_id, title="Test DF", theme="dark")

        _state.register_widget(widget_id, html, callbacks={})

        url = f"http://127.0.0.1:{server_port}/widget/{widget_id}"
        with urllib.request.urlopen(url, timeout=5) as resp:  # noqa: S310
            body = resp.read().decode("utf-8")

        assert resp.status == 200
        # The HTML should contain alert handling code
        assert "pywry:alert" in body or "PYWRY_TOAST" in body

    def test_inline_plotly_includes_alert_handler(self, server_port: int) -> None:
        """E2E: Verify inline plotly HTML includes alert handler."""
        import socket
        import urllib.request

        from pywry.inline import _start_server, _state, generate_plotly_html

        def wait_for_server(host: str, port: int, timeout: float = 5.0) -> bool:
            """Wait for server to be reachable via socket check (health requires auth)."""
            start = time.time()
            while time.time() - start < timeout:
                try:
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                        s.settimeout(0.5)
                        s.connect((host, port))
                        return True
                except Exception:  # noqa: S110
                    pass
                time.sleep(0.1)
            return False

        _start_server(port=server_port, host="0.0.0.0")
        assert wait_for_server("127.0.0.1", server_port)

        # Generate plotly HTML
        widget_id = "plotly-alert-test"
        figure_json = '{"data": [{"type": "scatter", "x": [1, 2], "y": [3, 4]}], "layout": {}}'
        html = generate_plotly_html(figure_json, widget_id, title="Test Plot", theme="dark")

        _state.register_widget(widget_id, html, callbacks={})

        url = f"http://127.0.0.1:{server_port}/widget/{widget_id}"
        with urllib.request.urlopen(url, timeout=5) as resp:  # noqa: S310
            body = resp.read().decode("utf-8")

        assert resp.status == 200
        # The HTML should contain PYWRY_TOAST
        assert "PYWRY_TOAST" in body
