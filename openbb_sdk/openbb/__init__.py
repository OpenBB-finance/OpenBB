"""OpenBB SDK."""
# flake8: noqa

from typing import List, Optional, Union

from openbb_core.app.static.app_factory import (
    create_app as _create_app,
    BaseApp as _BaseApp,
)

try:
    # pylint: disable=import-outside-toplevel
    from openbb.package.__extensions__ import Extensions as _Extensions

    obb: Union[_BaseApp, _Extensions] = _create_app(_Extensions)
    sdk = obb
except (ImportError, ModuleNotFoundError):
    print("Failed to import extensions. Run `openbb.build()` to build extensions code.")
    obb = sdk = _create_app()


def build(
    modules: Optional[Union[str, List[str]]] = None,
    lint: bool = True,
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
    """
    # pylint: disable=import-outside-toplevel
    import os
    from pathlib import Path
    from multiprocessing import Pool
    from openbb_core.app.static.package_builder import PackageBuilder

    current_dir = Path(os.path.dirname(os.path.realpath(__file__)))

    # `build` is running in a separate process. This avoids consecutive calls to this
    # function in the same interpreter to reuse objects already in memory. Not doing
    # this was causing docstrings to have repeated sections, for example.
    with Pool(processes=1) as pool:
        pool.apply(
            PackageBuilder(current_dir).build,
            args=(modules, lint),
        )
