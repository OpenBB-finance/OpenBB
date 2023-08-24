"""OpenBB SDK."""
# flake8: noqa
# pylint: disable=import-outside-toplevel

import os
from pathlib import Path
from typing import List, Optional, Union

from openbb_core.app.static.app_factory import create_app as __create_app

try:
    # pylint: disable=import-outside-toplevel
    from openbb.package.__extensions__ import Extensions

    obb = sdk = __create_app(Extensions)
except (ImportError, ModuleNotFoundError):
    print("Failed to import extensions. Try `openbb.rebuild_extensions()`.")
    obb = sdk = __create_app()


def rebuild_extensions(
    modules: Optional[Union[str, List[str]]] = None,
    lint: bool = True,
) -> None:
    """Rebuild the Python SDK.

    Parameters
    ----------
    modules : Optional[List[str]], optional
        The modules to rebuild, by default None
        For example: "/news" or ["/news", "/crypto"]
        If None, all modules are rebuilt.
    lint : bool, optional
        Whether to lint the code, by default True
    """
    from openbb_core.app.static.package_builder import PackageBuilder

    current_dir = Path(os.path.dirname(os.path.realpath(__file__)))
    PackageBuilder(current_dir).build(modules=modules, lint=lint)
