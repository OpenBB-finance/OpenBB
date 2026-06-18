"""MCP service layer.

Submodule bound explicitly for ``mock.patch`` reliability. The
``import openbb_mcp_server.service.X`` form is required (rather than
``from .X import ...``) so ``mock.patch("openbb_mcp_server.service.X.Y")``
can resolve ``X`` as an attribute on this package — and avoids the
partially-initialized ImportError CPython 3.13 raises against the
``from package import submodule`` form inside the package's own
``__init__.py``.
"""

import openbb_mcp_server.service.mcp_service  # noqa: F401

__all__ = ["mcp_service"]
