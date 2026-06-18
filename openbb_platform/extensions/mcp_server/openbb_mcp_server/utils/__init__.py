"""Utility helpers for ``openbb-mcp``.

Submodules bound explicitly via ``import openbb_mcp_server.utils.X``
so ``mock.patch`` finds them as attributes on this package
(CPython 3.10 namespace-package quirk) and so the package's own
init doesn't trip CPython 3.13's partially-initialized-module
ImportError on the ``from package import submodule`` form.
"""

import openbb_mcp_server.utils.app_import  # noqa: F401
import openbb_mcp_server.utils.fastapi  # noqa: F401

__all__ = [
    "app_import",
    "fastapi",
]
