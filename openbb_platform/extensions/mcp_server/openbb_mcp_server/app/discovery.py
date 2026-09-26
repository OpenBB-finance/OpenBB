"""Stateless tool-discovery transform for the OpenBB MCP server."""

from collections.abc import Sequence

from fastmcp.server.transforms.search import BM25SearchTransform
from fastmcp.tools.base import Tool

from openbb_mcp_server.models.category_index import CategoryIndex


class OpenBBToolCatalog(BM25SearchTransform):
    """Fold the OpenBB route tools behind ``search_tools`` and ``call_tool``.

    Parameters
    ----------
    category_index : CategoryIndex
        Index of the OpenBB route tools that are hidden from ``list_tools``.
    max_results : int
        Maximum number of tools returned by one ``search_tools`` call.
    """

    def __init__(self, category_index: CategoryIndex, *, max_results: int = 5) -> None:
        super().__init__(max_results=max_results)
        self._category_index = category_index

    async def transform_tools(self, tools: Sequence[Tool]) -> Sequence[Tool]:
        """List every non-catalog tool plus the synthetic search and call tools."""
        catalog = self._category_index.all_tool_names()
        listed = [tool for tool in tools if tool.name not in catalog]
        return [*listed, self._make_search_tool(), self._make_call_tool()]

    async def _search(self, tools: Sequence[Tool], query: str) -> Sequence[Tool]:
        catalog = self._category_index.all_tool_names()
        return await super()._search(
            [tool for tool in tools if tool.name in catalog], query
        )
