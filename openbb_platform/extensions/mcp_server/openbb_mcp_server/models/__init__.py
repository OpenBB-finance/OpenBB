"""Pydantic models + indexes for ``openbb-mcp``.

Submodules bound explicitly via ``import openbb_mcp_server.models.X``
for ``mock.patch`` reliability — and to avoid CPython 3.13's
partially-initialized-module ImportError on the ``from package
import submodule`` form inside the package's own ``__init__.py``.
"""

import openbb_mcp_server.models.category_index  # noqa: F401
import openbb_mcp_server.models.mcp_config  # noqa: F401
import openbb_mcp_server.models.prompts  # noqa: F401
import openbb_mcp_server.models.settings  # noqa: F401
import openbb_mcp_server.models.tools  # noqa: F401

__all__ = [
    "category_index",
    "mcp_config",
    "prompts",
    "settings",
    "tools",
]
