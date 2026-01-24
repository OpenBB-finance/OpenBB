"""PyWry exception hierarchy.

All PyWry-specific exceptions inherit from PyWryException, enabling
catch-all handling while supporting specific error types.
"""

from __future__ import annotations

from typing import Any


class PyWryException(Exception):
    """Base exception for all PyWry errors."""

    def __init__(self, message: str, **context: Any) -> None:
        """Initialize PyWry exception.

        Parameters
        ----------
        message : str
            Human-readable error message.
        **context : Any
            Additional context (label, method, request_id, etc.).
        """
        super().__init__(message)
        self.message = message
        self.context = context

    def __str__(self) -> str:
        """Format exception with context."""
        if self.context:
            ctx = ", ".join(f"{k}={v!r}" for k, v in self.context.items())
            return f"{self.message} ({ctx})"
        return self.message


class WindowError(PyWryException):
    """Window operation failed.

    Raised when a window is not found, already destroyed,
    or an operation cannot be performed on it.
    """

    def __init__(self, message: str, label: str | None = None, **context: Any) -> None:
        """Initialize window error.

        Parameters
        ----------
        message : str
            Human-readable error message.
        label : str, optional
            The window label that caused the error.
        **context : Any
            Additional context.
        """
        super().__init__(message, label=label, **context)
        self.label = label


class IPCError(PyWryException):
    """IPC communication failed.

    Raised when communication with the subprocess fails,
    including encoding/decoding errors and pipe failures.
    """

    def __init__(
        self,
        message: str,
        action: str | None = None,
        label: str | None = None,
        **context: Any,
    ) -> None:
        """Initialize IPC error.

        Parameters
        ----------
        message : str
            Human-readable error message.
        action : str, optional
            The IPC action that failed.
        label : str, optional
            The window label involved.
        **context : Any
            Additional context.
        """
        super().__init__(message, action=action, label=label, **context)
        self.action = action
        self.label = label


class IPCTimeoutError(IPCError):
    """IPC response timeout.

    Raised when waiting for a subprocess response exceeds
    the configured timeout.
    """

    def __init__(
        self,
        message: str,
        timeout: float,
        action: str | None = None,
        label: str | None = None,
        **context: Any,
    ) -> None:
        """Initialize timeout error.

        Parameters
        ----------
        message : str
            Human-readable error message.
        timeout : float
            The timeout value in seconds.
        action : str, optional
            The IPC action that timed out.
        label : str, optional
            The window label involved.
        **context : Any
            Additional context.
        """
        super().__init__(message, action=action, label=label, timeout=timeout, **context)
        self.timeout = timeout


class PropertyError(PyWryException):
    """Failed to get or set a window property.

    Raised when a property access or modification fails,
    typically due to the property not existing or being read-only.
    """

    def __init__(
        self,
        message: str,
        property_name: str,
        label: str | None = None,
        **context: Any,
    ) -> None:
        """Initialize property error.

        Parameters
        ----------
        message : str
            Human-readable error message.
        property_name : str
            The property that caused the error.
        label : str, optional
            The window label involved.
        **context : Any
            Additional context.
        """
        super().__init__(message, property_name=property_name, label=label, **context)
        self.property_name = property_name
        self.label = label


class SubprocessError(PyWryException):
    """Subprocess-related error.

    Raised when the pytauri subprocess fails to start,
    crashes unexpectedly, or returns an error.
    """

    def __init__(self, message: str, exit_code: int | None = None, **context: Any) -> None:
        """Initialize subprocess error.

        Parameters
        ----------
        message : str
            Human-readable error message.
        exit_code : int, optional
            The subprocess exit code if available.
        **context : Any
            Additional context.
        """
        super().__init__(message, exit_code=exit_code, **context)
        self.exit_code = exit_code
