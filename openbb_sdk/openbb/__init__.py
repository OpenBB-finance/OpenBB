"""OpenBB SDK."""
# flake8: noqa

import os
from pathlib import Path
from typing import List, Optional, Union

from openbb_core.app.static.app_factory import (
    BaseApp as _BaseApp,
    create_app as _create_app,
)
from openbb_core.app.static.build_utils import (
    auto_build as _auto_build,
    build as _build,
)

_this_dir = Path(os.path.dirname(os.path.realpath(__file__)))
from openbb_core.app.model.obbject import OBBject


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
    _build(directory=_this_dir, modules=modules, lint=lint, verbose=verbose)


_auto_build(directory=_this_dir)

try:
    # pylint: disable=import-outside-toplevel
    from openbb.package.__extensions__ import Extensions as _Extensions

    obb: Union[_BaseApp, _Extensions] = _create_app(_Extensions)  # type: ignore
    sdk = obb
except (ImportError, ModuleNotFoundError):
    print("Failed to import extensions.")
    obb = sdk = _create_app()  # type: ignore


import importlib
import pkgutil


def discover_and_load_plugins():
    for finder, name, ispkg in pkgutil.iter_modules():
        # We need to pick a naming convention for this
        if name.startswith("openbb_obbject"):
            print(f"Loading plugin: {name}")
            module = importlib.import_module(name)
            plugin = getattr(module, "OBBjectPlugin")
            # This can probably be more intuitive.  Technically this can extend anything
            plugin().extend_myobject(OBBject)


try:
    # Extensions for OBBject
    # This should go in the obb so that we dont need to do import openbb separately
    discover_and_load_plugins()


except Exception as e:
    print("Failed to import OBBject extensions.")
    # Debugging
    print(e)
