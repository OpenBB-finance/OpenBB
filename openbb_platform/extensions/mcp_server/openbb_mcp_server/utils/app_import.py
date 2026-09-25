"""Backwards-compatible lazy aliases for ``import_app`` and ``parse_args``."""

from importlib import import_module

_LAZY_TARGETS: dict[str, tuple[str, str]] = {
    "import_app": ("openbb_mcp_server.app.bootstrap", "import_app"),
    "parse_args": ("openbb_mcp_server.app.args", "parse_args"),
    "cl_doc": ("openbb_mcp_server.app.args", "LAUNCH_SCRIPT_DESCRIPTION"),
}


def __getattr__(name):
    """Resolve a legacy name against its current source module."""
    target = _LAZY_TARGETS.get(name)
    if target is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    module_path, attr = target
    return getattr(import_module(module_path), attr)


def __dir__() -> list[str]:
    """Surface the lazy names for ``dir()`` and IDE autocomplete."""
    return sorted(_LAZY_TARGETS)


__all__ = [  # noqa: F822
    "cl_doc",
    "import_app",
    "parse_args",
]
