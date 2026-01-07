"""Logging utilities for PyWry.

All operations log warnings instead of raising exceptions for non-fatal errors.
"""

from __future__ import annotations

import logging
import sys


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


def enable_debug() -> None:
    """Enable debug mode for verbose IPC and operation logging.

    This will show all debug messages including:
    - IPC command calls and responses
    - Event routing
    - Template application
    - Asset loading
    """
    set_level(logging.DEBUG)
