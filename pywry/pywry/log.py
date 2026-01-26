"""Logging utilities for PyWry.

All operations log warnings instead of raising exceptions for non-fatal errors.
"""

from __future__ import annotations

import logging
import sys

from typing import Any


class _LoggerHolder:
    """Holder for the global logger instance."""

    instance: logging.Logger | None = None


def get_logger() -> logging.Logger:
    """Get the pywry logger instance.

    Returns
    -------
    logging.Logger
        The pywry logger configured with a stream handler.
    """
    if _LoggerHolder.instance is None:
        logger = logging.getLogger("pywry")
        logger.setLevel(logging.WARNING)

        # Only add handler if none exists
        if not logger.handlers:
            handler = logging.StreamHandler(sys.stderr)
            handler.setLevel(logging.DEBUG)
            formatter = logging.Formatter("%(name)s - %(levelname)s - %(message)s")
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        _LoggerHolder.instance = logger

    return _LoggerHolder.instance


def debug(msg: str) -> None:
    """Log a debug message.

    Parameters
    ----------
    msg : str
        The message to log.
    """
    get_logger().debug(msg)


def info(msg: str) -> None:
    """Log an info message.

    Parameters
    ----------
    msg : str
        The message to log.
    """
    get_logger().info(msg)


def warn(msg: str) -> None:
    """Log a warning message. Never raises exceptions.

    Parameters
    ----------
    msg : str
        The warning message to log.
    """
    get_logger().warning(msg)


def error(msg: str) -> None:
    """Log an error message. Never raises exceptions.

    Parameters
    ----------
    msg : str
        The error message to log.
    """
    get_logger().error(msg)


def set_level(level: int | str) -> None:
    """Set the logging level.

    Parameters
    ----------
    level : int or str
        The logging level (e.g., logging.DEBUG, "DEBUG").
    """
    if isinstance(level, str):
        level = getattr(logging, level.upper())
    get_logger().setLevel(level)


def exception(msg: str) -> None:
    """Log an exception with full traceback.

    Call this from within an except block to log the exception
    message along with the full stack trace.

    Parameters
    ----------
    msg : str
        The error message to log alongside the traceback.
    """
    get_logger().exception(msg)


def log_callback_error(event_type: str, label: str, exc: BaseException) -> None:
    """Log a callback error with standardized format.

    Parameters
    ----------
    event_type : str
        The event type that triggered the callback.
    label : str
        The window label where the event occurred.
    exc : BaseException
        The exception that was raised.
    """
    get_logger().exception(f"Callback error for '{event_type}' on window '{label}': {exc}")


def enable_debug() -> None:
    """Enable debug mode for verbose IPC and operation logging.

    This will show all debug messages including:
    - IPC command calls and responses
    - Event routing
    - Template application
    - Asset loading
    """
    set_level(logging.DEBUG)


# Keys that should be redacted in log output for security
_SENSITIVE_KEYS = frozenset(
    {
        "value",  # SecretInput, TextInput values
        "secret",
        "password",
        "api_key",
        "apiKey",
        "token",
        "auth",
        "credential",
        "key",
    }
)


def redact_sensitive_data(
    data: dict[str, Any] | list[Any] | str | None, max_depth: int = 5
) -> dict[str, Any] | list[Any] | str | None:
    """Redact sensitive values from data for safe logging.

    Recursively traverses dicts/lists and replaces values for keys
    that match sensitive patterns with "[REDACTED]".

    Parameters
    ----------
    data : dict or list or str or None
        The data to redact.
    max_depth : int, optional
        Maximum recursion depth to prevent infinite loops (default: 5).

    Returns
    -------
    dict or list or str or None
        A copy of the data with sensitive values redacted.
    """
    if max_depth <= 0:
        return "[MAX_DEPTH]"

    if data is None:
        return None

    if isinstance(data, dict):
        result: dict[str, Any] = {}
        for k, v in data.items():
            key_lower = k.lower() if isinstance(k, str) else str(k).lower()
            # Check if any sensitive key pattern is in the key name
            if any(sensitive in key_lower for sensitive in _SENSITIVE_KEYS):
                result[k] = "[REDACTED]"
            else:
                result[k] = redact_sensitive_data(v, max_depth - 1)
        return result

    if isinstance(data, list):
        return [redact_sensitive_data(item, max_depth - 1) for item in data]

    # For strings and other primitives, return as-is
    return data
