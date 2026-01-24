"""Tests for pywry.exceptions module.

These tests verify the exception hierarchy, message formatting,
context storage, and inheritance relationships. No mocks needed -
we're testing actual exception behavior.
"""

from __future__ import annotations

import pytest

from pywry.exceptions import (
    IPCError,
    IPCTimeoutError,
    PropertyError,
    PyWryException,
    SubprocessError,
    WindowError,
)


class TestPyWryException:
    """Test base exception class behavior."""

    def test_message_only(self) -> None:
        """Exception with just a message stores it correctly."""
        exc = PyWryException("Something went wrong")
        assert exc.message == "Something went wrong"
        assert not exc.context
        assert str(exc) == "Something went wrong"

    def test_with_context(self) -> None:
        """Exception with context includes it in string representation."""
        exc = PyWryException("Failed", label="main", request_id=42)
        assert exc.message == "Failed"
        assert exc.context == {"label": "main", "request_id": 42}
        # Context should appear in string representation
        exc_str = str(exc)
        assert "Failed" in exc_str
        assert "label='main'" in exc_str
        assert "request_id=42" in exc_str

    def test_is_standard_exception(self) -> None:
        """PyWryException inherits from Exception and can be caught."""
        exc = PyWryException("test")
        assert isinstance(exc, Exception)

        # Can be raised and caught as PyWryException
        with pytest.raises(PyWryException):
            raise exc

        with pytest.raises(PyWryException):
            raise PyWryException("another test")

    def test_args_preserved(self) -> None:
        """Standard exception args are preserved."""
        exc = PyWryException("message")
        assert exc.args == ("message",)


class TestWindowError:
    """Test window-specific exception behavior."""

    def test_with_label(self) -> None:
        """WindowError stores label as attribute and in context."""
        exc = WindowError("Window not found", label="my-window")
        assert exc.label == "my-window"
        assert exc.message == "Window not found"
        assert exc.context["label"] == "my-window"
        assert "my-window" in str(exc)

    def test_without_label(self) -> None:
        """WindowError works without label."""
        exc = WindowError("Generic window error")
        assert exc.label is None
        assert "label=None" in str(exc)

    def test_with_extra_context(self) -> None:
        """WindowError accepts additional context."""
        exc = WindowError("Failed", label="w1", operation="close", retry=True)
        assert exc.label == "w1"
        assert exc.context["operation"] == "close"
        assert exc.context["retry"] is True

    def test_inheritance(self) -> None:
        """WindowError inherits from PyWryException."""
        exc = WindowError("test")
        assert isinstance(exc, PyWryException)
        assert isinstance(exc, Exception)

        # Can catch as either type
        with pytest.raises(PyWryException):
            raise WindowError("test", label="x")


class TestIPCError:
    """Test IPC error behavior."""

    def test_with_action_and_label(self) -> None:
        """IPCError stores action and label."""
        exc = IPCError("Send failed", action="window_call", label="main")
        assert exc.action == "window_call"
        assert exc.label == "main"
        assert exc.context["action"] == "window_call"
        assert exc.context["label"] == "main"

    def test_message_formatting(self) -> None:
        """IPCError formats message with context."""
        exc = IPCError("Pipe broken", action="read")
        exc_str = str(exc)
        assert "Pipe broken" in exc_str
        assert "action='read'" in exc_str

    def test_without_action(self) -> None:
        """IPCError works without action/label."""
        exc = IPCError("Connection lost")
        assert exc.action is None
        assert exc.label is None

    def test_inheritance(self) -> None:
        """IPCError inherits from PyWryException."""
        exc = IPCError("test")
        assert isinstance(exc, PyWryException)


class TestIPCTimeoutError:
    """Test timeout-specific error behavior."""

    def test_stores_timeout_value(self) -> None:
        """IPCTimeoutError stores the timeout value."""
        exc = IPCTimeoutError("Timed out", timeout=5.0)
        assert exc.timeout == 5.0
        assert exc.context["timeout"] == 5.0
        assert "5.0" in str(exc)

    def test_with_action_and_label(self) -> None:
        """IPCTimeoutError inherits IPCError attributes."""
        exc = IPCTimeoutError("No response", timeout=10.0, action="window_get", label="chart")
        assert exc.timeout == 10.0
        assert exc.action == "window_get"
        assert exc.label == "chart"

    def test_inheritance_chain(self) -> None:
        """IPCTimeoutError inherits from IPCError and PyWryException."""
        exc = IPCTimeoutError("test", timeout=1.0)
        assert isinstance(exc, IPCTimeoutError)
        assert isinstance(exc, IPCError)
        assert isinstance(exc, PyWryException)
        assert isinstance(exc, Exception)

        # Can catch at any level
        with pytest.raises(IPCError):
            raise IPCTimeoutError("timeout", timeout=2.0)

        with pytest.raises(PyWryException):
            raise IPCTimeoutError("timeout", timeout=2.0)


class TestPropertyError:
    """Test property error behavior."""

    def test_stores_property_name(self) -> None:
        """PropertyError stores the property name."""
        exc = PropertyError("Cannot read property", property_name="is_visible")
        assert exc.property_name == "is_visible"
        assert exc.context["property_name"] == "is_visible"
        assert "is_visible" in str(exc)

    def test_with_label(self) -> None:
        """PropertyError stores label."""
        exc = PropertyError("Read-only", property_name="title", label="win-1")
        assert exc.property_name == "title"
        assert exc.label == "win-1"
        assert exc.context["label"] == "win-1"

    def test_inheritance(self) -> None:
        """PropertyError inherits from PyWryException."""
        exc = PropertyError("test", property_name="x")
        assert isinstance(exc, PyWryException)


class TestSubprocessError:
    """Test subprocess error behavior."""

    def test_with_exit_code(self) -> None:
        """SubprocessError stores exit code."""
        exc = SubprocessError("Process crashed", exit_code=1)
        assert exc.exit_code == 1
        assert exc.context["exit_code"] == 1
        assert "1" in str(exc)

    def test_without_exit_code(self) -> None:
        """SubprocessError works without exit code."""
        exc = SubprocessError("Failed to start")
        assert exc.exit_code is None

    def test_with_context(self) -> None:
        """SubprocessError accepts additional context."""
        exc = SubprocessError("Crash", exit_code=137, signal="SIGKILL", pid=12345)
        assert exc.exit_code == 137
        assert exc.context["signal"] == "SIGKILL"
        assert exc.context["pid"] == 12345

    def test_inheritance(self) -> None:
        """SubprocessError inherits from PyWryException."""
        exc = SubprocessError("test")
        assert isinstance(exc, PyWryException)


class TestExceptionHierarchy:
    """Test that the exception hierarchy enables flexible catching."""

    def test_catch_all_pywry_exceptions(self) -> None:
        """All exception types can be caught by PyWryException."""
        exceptions = [
            PyWryException("base"),
            WindowError("window", label="x"),
            IPCError("ipc", action="test"),
            IPCTimeoutError("timeout", timeout=1.0),
            PropertyError("prop", property_name="x"),
            SubprocessError("subprocess"),
        ]

        for exc in exceptions:
            with pytest.raises(PyWryException):
                raise exc

    def test_catch_ipc_errors_including_timeout(self) -> None:
        """IPCTimeoutError can be caught as IPCError."""

        def raise_timeout() -> None:
            raise IPCTimeoutError("test", timeout=5.0)

        with pytest.raises(IPCError) as exc_info:
            raise_timeout()

        # But we can still access timeout-specific attributes
        assert exc_info.value.timeout == 5.0

    def test_exception_types_are_distinct(self) -> None:
        """Each exception type can be caught specifically."""
        with pytest.raises(WindowError):
            raise WindowError("test")

        with pytest.raises(IPCError):
            raise IPCError("test")

        with pytest.raises(PropertyError):
            raise PropertyError("test", property_name="x")

        with pytest.raises(SubprocessError):
            raise SubprocessError("test")

    def test_wrong_type_not_caught(self) -> None:
        """Exceptions are not caught by unrelated types."""
        with pytest.raises(WindowError):
            try:
                raise WindowError("test")
            except IPCError:
                pytest.fail("WindowError should not be caught by IPCError")
