"""OpenBB Platform."""

# flake8: noqa

from pathlib import Path
from importlib import import_module
from typing import List, Optional, Union

from openbb_core.app.static.app_factory import (
    BaseApp as _BaseApp,
    create_app as _create_app,
)
from openbb_core.app.static.package_builder import PackageBuilder as _PackageBuilder
from openbb_core.app.static.reference_loader import ReferenceLoader as _ReferenceLoader

_this_dir = Path(__file__).parent.resolve()


def build(
    modules: Optional[Union[str, List[str]]] = None,
    lint: bool = True,
    verbose: bool = False,
) -> None:
    """Build extension modules.

    Parameters
    ----------
    modules : Optional[List[str]], optional
        The modules to rebuild, by default None
        For example: "/news" or ["/news", "/crypto"]
        If None, all modules are rebuilt.
    lint : bool, optional
        Whether to lint the code, by default True
    verbose : bool, optional
        Enable/disable verbose mode
    """
    _PackageBuilder(_this_dir, lint, verbose).build(modules)


_PackageBuilder(_this_dir).auto_build()
_ReferenceLoader(_this_dir)

try:
    _extensions_module = import_module("openbb.package.__extensions__")
    _Extensions = _extensions_module.Extensions

    obb = _create_app(_Extensions)
    sdk = obb
except (AttributeError, ImportError, ModuleNotFoundError):
    print("Failed to import extensions. Are any installed?")
    obb = sdk = _create_app()
