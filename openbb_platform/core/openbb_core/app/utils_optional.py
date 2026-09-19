"""Helpers for handling optional runtime dependencies uniformly."""

import builtins
import sys
from importlib.util import find_spec
from types import ModuleType
from typing import overload

from openbb_core.app.model.abstract.error import OpenBBError

__all__ = ["is_installed", "require_optional"]


_INSTALL_HINTS: dict[str, str] = {
    "pandas": "pip install 'openbb-core[pandas]'",
    "numpy": "pip install 'openbb-core[pandas]'",
    "polars": "pip install polars pyarrow",
    "pyarrow": "pip install pyarrow",
    "openbb_charting": "pip install openbb-charting",
    "pycountry": "pip install pycountry",
    "bs4": "pip install beautifulsoup4",
}


def _install_hint(module_name: str) -> str:
    """Return the install command for *module_name* (top-level package)."""
    top = module_name.split(".", 1)[0]
    return _INSTALL_HINTS.get(top, f"pip install {top}")


def _format_error(missing: list[str]) -> str:
    """Format a user-facing error for one or more missing optional modules."""
    if len(missing) == 1:
        name = missing[0]
        return (
            f"Optional dependency '{name}' is required for this feature. "
            f"Install with: {_install_hint(name)}"
        )
    hints = "; ".join(f"{name}: {_install_hint(name)}" for name in missing)
    names = ", ".join(f"'{name}'" for name in missing)
    return (
        f"Optional dependencies {names} are required for this feature. "
        f"Install with — {hints}"
    )


def is_installed(module_name: str) -> bool:
    """Return True if *module_name* can be imported without actually importing it."""
    try:
        return find_spec(module_name) is not None
    except (ImportError, ValueError):
        return False


@overload
def require_optional(module_name: str, /) -> ModuleType: ...
@overload
def require_optional(
    module_name: str, /, *module_names: str
) -> tuple[ModuleType, ...]: ...
def require_optional(*module_names: str) -> ModuleType | tuple[ModuleType, ...]:
    """Import optional modules or raise a uniform OpenBBError with install hints.

    Returns the module when called with one name, or a tuple of modules in the
    same order as the arguments when called with multiple names.
    """
    if not module_names:
        raise ValueError("require_optional requires at least one module name")

    modules: list[ModuleType] = []
    missing: list[str] = []
    for name in module_names:
        try:
            # Use ``builtins.__import__`` (rather than ``importlib.import_module``)
            # so that test suites which monkeypatch ``__import__`` to simulate a
            # missing optional dependency are honored.
            builtins.__import__(name)
            modules.append(sys.modules[name])
        except ImportError:
            missing.append(name)

    if missing:
        # ``from None`` suppresses the chained ``ImportError`` context so the
        # user sees a single, clean OpenBBError with the install hint.
        raise OpenBBError(_format_error(missing)) from None

    if len(modules) == 1:
        return modules[0]
    return tuple(modules)
