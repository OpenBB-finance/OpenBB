"""Backwards-compatibility shim.

The launcher's helpers were split across purpose-specific modules in
the V5 layout reorganization:

* ``import_app`` moved to ``openbb_mcp_server.app.bootstrap``.
* ``parse_args`` moved to ``openbb_mcp_server.app.args``.

Every symbol is resolved lazily through ``__getattr__`` so the shim
always reflects the current source-module state — important when test
helpers (or hot-reload loops) pop the source module from
``sys.modules`` and re-import it.
"""

from importlib import import_module

#: ``shim_attr -> (source_module, source_attr)`` mapping.
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
