"""Flask integration utilities for OpenBB Core."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .detection import flask_available, is_flask_app
    from .loader import merge_flask_openapi, mount_flask_extensions
    from .registry import FlaskMountRegistry

__all__ = [
    "FlaskMountRegistry",
    "flask_available",
    "is_flask_app",
    "merge_flask_openapi",
    "mount_flask_extensions",
]


def __getattr__(name: str):
    """Resolve public attributes lazily."""
    if name in {"mount_flask_extensions", "merge_flask_openapi"}:
        from . import loader

        return getattr(loader, name)
    if name == "FlaskMountRegistry":
        from .registry import FlaskMountRegistry

        return FlaskMountRegistry
    if name in {"is_flask_app", "flask_available"}:
        from . import detection

        return getattr(detection, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
