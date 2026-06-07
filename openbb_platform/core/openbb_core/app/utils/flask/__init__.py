"""Flask integration utilities for OpenBB Core.

This module provides Flask app integration capabilities.
All imports are lazy to avoid ImportError when Flask is not installed.
"""


def __getattr__(name: str):
    """Lazy import to avoid ImportError when Flask is not installed."""
    if name == "FlaskExtensionLoader":
        from .loader import FlaskExtensionLoader

        return FlaskExtensionLoader
    if name == "FlaskIntrospector":
        from .introspection import FlaskIntrospector

        return FlaskIntrospector
    if name == "OpenAPISpecGenerator":
        from .adapter import OpenAPISpecGenerator

        return OpenAPISpecGenerator
    if name == "FlaskMountRegistry":
        from .registry import FlaskMountRegistry

        return FlaskMountRegistry
    if name == "_check_flask_available":
        from .introspection import _check_flask_available

        return _check_flask_available
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    "FlaskIntrospector",
    "FlaskExtensionLoader",
    "OpenAPISpecGenerator",
    "FlaskMountRegistry",
    "_check_flask_available",
]
