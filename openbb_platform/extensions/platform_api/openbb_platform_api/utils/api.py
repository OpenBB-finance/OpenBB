"""Backwards-compatibility shim.

The launcher's helpers were split across purpose-specific modules in
the V5 layout reorganization:

* ``parse_args`` and ``LAUNCH_SCRIPT_DESCRIPTION`` moved to
  ``openbb_platform_api.app.args``.
* ``import_app`` moved to ``openbb_platform_api.app.bootstrap``.
* ``check_port`` and ``get_user_settings`` moved to
  ``openbb_platform_api.utils.network``.
* ``get_widgets_json`` plus its module-level ``FIRST_RUN`` /
  ``PATH_WIDGETS`` state moved to
  ``openbb_platform_api.service.widgets_service``.

This module preserves every legacy import path so external callers
keep working — new code should import from the dedicated modules.
"""

from importlib import import_module

#: ``shim_attr -> (source_module, source_attr)`` mapping. Every legacy
#: name lives here; ``__getattr__`` consults this on each access.
_LAZY_TARGETS: dict[str, tuple[str, str]] = {
    "LAUNCH_SCRIPT_DESCRIPTION": (
        "openbb_platform_api.app.args",
        "LAUNCH_SCRIPT_DESCRIPTION",
    ),
    "parse_args": ("openbb_platform_api.app.args", "parse_args"),
    "import_app": ("openbb_platform_api.app.bootstrap", "import_app"),
    "get_widgets_json": (
        "openbb_platform_api.service.widgets_service",
        "get_widgets_json",
    ),
    "logger": ("openbb_platform_api.service.widgets_service", "logger"),
    "FIRST_RUN": ("openbb_platform_api.service.widgets_service", "FIRST_RUN"),
    "PATH_WIDGETS": (
        "openbb_platform_api.service.widgets_service",
        "PATH_WIDGETS",
    ),
    "check_port": ("openbb_platform_api.utils.network", "check_port"),
    "get_user_settings": (
        "openbb_platform_api.utils.network",
        "get_user_settings",
    ),
}


def __getattr__(name):
    """Resolve a legacy name against its current source module.

    Each access re-imports the source module and returns the fresh
    attribute. ``importlib.import_module`` returns the cached module
    when nothing's been mutated, so the cost is a dict lookup in the
    common case — and a real re-import in the test-pollution case
    (which is exactly when the lazy resolution matters).
    """
    target = _LAZY_TARGETS.get(name)
    if target is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    module_path, attr = target
    return getattr(import_module(module_path), attr)


def __dir__() -> list[str]:
    """Surface the lazy names for ``dir()`` and IDE autocomplete."""
    return sorted(_LAZY_TARGETS)


# ``noqa: F822`` because every name is provided lazily through
# ``__getattr__`` — ruff's static check doesn't see the indirection,
# but ``import openbb_platform_api.utils.api as api; api.parse_args``
# resolves correctly at runtime.
__all__ = [  # noqa: F822
    "FIRST_RUN",
    "LAUNCH_SCRIPT_DESCRIPTION",
    "PATH_WIDGETS",
    "check_port",
    "get_user_settings",
    "get_widgets_json",
    "import_app",
    "logger",
    "parse_args",
]
