"""OpenBB SDK."""
# flake8: noqa
# pylint: disable=import-outside-toplevel

from typing import List, Optional, Union

from openbb_core.app.static.app_factory import create_app as __create_app

sdk = __create_app()
obb = sdk


def _rebuild_python_interface(
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

    PackageBuilder.build(modules=modules, lint=lint)
