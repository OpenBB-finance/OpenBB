"""Code Mode and search-mode helpers for OpenBB MCP."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Awaitable, Callable, Sequence
from dataclasses import dataclass
from typing import Annotated, Any, Literal

from fastmcp.experimental.transforms.code_mode import CodeMode, GetSchemas
from fastmcp.server.context import Context
from fastmcp.server.transforms import GetToolNext
from fastmcp.server.transforms.search import (
    serialize_tools_for_output_json,
    serialize_tools_for_output_markdown,
)
from fastmcp.server.transforms.search.base import _extract_searchable_text
from fastmcp.server.transforms.search.bm25 import (
    BM25SearchTransform,
    _BM25Index,
    _catalog_hash,
)
from fastmcp.tools.tool import Tool
from fastmcp.utilities.logging import get_logger
from fastmcp.utilities.versions import VersionSpec

logger = get_logger(__name__)

GetToolCatalog = Callable[[Context], Awaitable[Sequence[Tool]]]
FilterArg = str | list[str] | None


@dataclass(frozen=True, slots=True)
class _ToolMeta:
    """Precomputed metadata for efficient filtering and category aggregation."""

    tool: Tool
    tags: frozenset[str]
    category: str | None
    subcategory: str | None


def _normalize_filter_values(values: FilterArg) -> set[str]:
    """Normalize string-or-list filter values into lowercase set members."""
    if values is None:
        return set()
    raw: Sequence[str] = [values] if isinstance(values, str) else values
    return {v.strip().lower() for v in raw if v.strip()}


def _catalog_signature(tools: Sequence[Tool]) -> str:
    """Deterministic name-based signature for meta-row cache invalidation."""
    return "|".join(sorted(t.name for t in tools))


def _tool_category_from_name(tool_name: str) -> str | None:
    """Infer top-level category from OpenBB tool name convention."""
    if "_" not in tool_name:
        return None
    return tool_name.split("_", maxsplit=1)[0].strip().lower() or None


def _tool_subcategory_from_name(tool_name: str) -> str | None:
    """Infer subcategory from OpenBB tool name convention (second segment)."""
    parts = tool_name.split("_", maxsplit=2)
    if len(parts) < 3:
        return None
    return parts[1].strip().lower() or None


def _tool_searchable_tags(tool: Tool) -> set[str]:
    """Collect normalized tags including category/subcategory inferred from name."""
    tags = {str(t).strip().lower() for t in (tool.tags or set()) if str(t).strip()}
    if category := _tool_category_from_name(tool.name):
        tags.add(category)
    if subcategory := _tool_subcategory_from_name(tool.name):
        tags.add(subcategory)
    return tags


def _render_category_tree_as_markdown(rows: Sequence[dict[str, Any]]) -> str:
    """Render nested category/subcategory tree as compact markdown."""
    if not rows:
        return "No categories matched the query filters."
    lines = ["### Categories"]
    for row in rows:
        cat, count = row.get("category"), row.get("tool_count")
        if not isinstance(cat, str) or not isinstance(count, int):
            continue
        lines.append("")
        lines.append(f"- `{cat}` ({count} tools)")
        for sub in row.get("subcategories", []):
            name, cnt = sub.get("subcategory"), sub.get("tool_count")
            if isinstance(name, str) and isinstance(cnt, int):
                lines.append(f"  - `{name}` ({cnt} tools)")
    return "\n".join(lines)


class OpenBBBM25SearchTransform(BM25SearchTransform):
    """BM25 search with stable full-catalog index and category/provider filters.

    Maintains two caches:
    - Meta cache (name-based): tag/category metadata per tool, keyed by tool names.
    - BM25 cache (content-based): full-catalog index rebuilt only when tool content
      changes. Filtering is applied post-ranking so the index stays stable across
      different category/subcategory/provider filter combinations.
    """

    def __init__(
        self,
        *,
        max_results: int = 5,
        output_format: Literal["json", "markdown"] = "markdown",
        always_visible: list[str] | None = None,
        search_tool_name: str = "search",
        call_tool_name: str = "call_tool",
        list_categories_tool_name: str = "list_categories",
        search_result_serializer=None,
    ) -> None:
        """Initialize the OpenBB BM25 search transform."""
        serializer = search_result_serializer or (
            serialize_tools_for_output_markdown
            if output_format == "markdown"
            else serialize_tools_for_output_json
        )
        super().__init__(
            max_results=max_results,
            always_visible=always_visible,
            search_tool_name=search_tool_name,
            call_tool_name=call_tool_name,
            search_result_serializer=serializer,
        )
        self.output_format: Literal["json", "markdown"] = output_format
        self._list_categories_tool_name = list_categories_tool_name
        self._get_schema_tool_name = "get_schema"
        # Meta cache (name-based invalidation)
        self._meta_sig = ""
        self._meta: tuple[_ToolMeta, ...] = ()
        # BM25 cache (content-based invalidation, built on full catalog)
        self._bm25 = _BM25Index()
        self._bm25_tools: list[Tool] = []
        self._bm25_hash = ""
        # Tool instance caches
        self._cached_list_categories_tool: Tool | None = None
        self._cached_get_schema_tool: Tool | None = None

    # ------------------------------------------------------------------
    # Internal caches
    # ------------------------------------------------------------------

    def _get_meta(self, tools: Sequence[Tool]) -> tuple[_ToolMeta, ...]:
        """Return cached per-tool metadata, rebuilding when names change."""
        sig = _catalog_signature(tools)
        if sig != self._meta_sig:
            self._meta = tuple(
                _ToolMeta(
                    tool=t,
                    tags=frozenset(_tool_searchable_tags(t)),
                    category=_tool_category_from_name(t.name),
                    subcategory=_tool_subcategory_from_name(t.name),
                )
                for t in tools
            )
            self._meta_sig = sig
        return self._meta

    def _rebuild_bm25(self, tools: Sequence[Tool]) -> None:
        """Rebuild BM25 index on the full catalog when tool content changes."""
        h = _catalog_hash(tools)
        if h != self._bm25_hash:
            idx = _BM25Index(self._bm25.k1, self._bm25.b)
            idx.build([_extract_searchable_text(t) for t in tools])
            self._bm25, self._bm25_tools, self._bm25_hash = idx, list(tools), h

    def _filter_meta(
        self,
        tools: Sequence[Tool],
        *,
        categories: set[str],
        subcategories: set[str],
        providers: set[str],
    ) -> list[_ToolMeta]:
        """Filter meta rows by category/subcategory/provider tag sets."""
        meta = self._get_meta(tools)
        if not (categories or subcategories or providers):
            return list(meta)
        results = []
        for row in meta:
            if categories and not row.tags.intersection(categories):
                continue
            if subcategories and not row.tags.intersection(subcategories):
                continue
            if providers and not row.tags.intersection(providers):
                continue
            results.append(row)
        return results

    async def render_results(self, tools: Sequence[Tool]) -> Any:
        """Render search results using the configured serializer.

        Public surface for ``_render_results`` (inherited from
        ``BaseSearchTransform``) so closures in ``build_search_tool`` can call
        it without triggering pylint W0212 (protected-access on a client class).
        """
        return await self._render_results(tools)

    # ------------------------------------------------------------------
    # Public search/category API
    # ------------------------------------------------------------------

    def list_categories(
        self,
        tools: Sequence[Tool],
        *,
        categories: FilterArg = None,
        subcategories: FilterArg = None,
        providers: FilterArg = None,
    ) -> list[dict[str, Any]]:
        """Return nested category/subcategory counts for filtered tools."""
        filtered = self._filter_meta(
            tools,
            categories=_normalize_filter_values(categories),
            subcategories=_normalize_filter_values(subcategories),
            providers=_normalize_filter_values(providers),
        )
        tree: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
        for row in filtered:
            tree[row.category or "uncategorized"][row.subcategory or "general"] += 1
        return [
            {
                "category": cat,
                "tool_count": sum(counts.values()),
                "subcategories": [
                    {"subcategory": name, "tool_count": cnt}
                    for name, cnt in sorted(counts.items(), key=lambda x: (-x[1], x[0]))
                ],
            }
            for cat, counts in sorted(
                tree.items(), key=lambda x: (-sum(x[1].values()), x[0])
            )
        ]

    async def search_tools(
        self,
        tools: Sequence[Tool],
        query: str,
        *,
        categories: FilterArg = None,
        subcategories: FilterArg = None,
        providers: FilterArg = None,
        requested_max_results: int | None = None,
    ) -> Sequence[Tool]:
        """BM25 search on full catalog with post-ranking filter.

        The BM25 index is built once per catalog snapshot (not per filter
        combination), so repeated searches with different filters don't
        trigger index rebuilds.
        """
        max_k = (
            self._max_results
            if requested_max_results is None
            else max(1, min(requested_max_results, self._max_results))
        )
        filtered = self._filter_meta(
            tools,
            categories=_normalize_filter_values(categories),
            subcategories=_normalize_filter_values(subcategories),
            providers=_normalize_filter_values(providers),
        )
        if not filtered:
            return []
        if not query:
            return sorted((r.tool for r in filtered), key=lambda t: t.name)[:max_k]

        # BM25 score the full catalog; filter results to the allowed set.
        self._rebuild_bm25(tools)
        ranked_indices = self._bm25.query(query, len(self._bm25_tools))
        ranked = [self._bm25_tools[i] for i in ranked_indices]
        allowed = {row.tool.name for row in filtered}
        return [t for t in ranked if t.name in allowed][:max_k]

    # ------------------------------------------------------------------
    # Shared tool builders (used by both standalone and CodeMode)
    # ------------------------------------------------------------------

    def build_search_tool(
        self,
        get_catalog: GetToolCatalog,
        *,
        name: str,
        brief: bool = False,
    ) -> Tool:
        """Build a search tool backed by this transform's search_tools method."""
        transform = self

        async def search(
            query: Annotated[str, "Natural-language text search query."] = "",
            categories: Annotated[
                FilterArg,
                "Top-level category filter (string or list, e.g. 'equity' or ['equity', 'economy']).",
            ] = None,
            subcategories: Annotated[
                FilterArg,
                "Subcategory filter (string or list, e.g. 'price' or ['price', 'fundamental']).",
            ] = None,
            providers: Annotated[
                FilterArg,
                "Provider filter (string or list, e.g. 'yfinance' or ['yfinance', 'fmp']).",
            ] = None,
            *,
            max_results: Annotated[
                int | None,
                "Optional per-query result count. Clamped to server-configured cap.",
            ] = None,
            ctx: Context = None,  # type: ignore[assignment]
        ) -> Any:
            """Search OpenBB tools with optional category/subcategory/provider filters."""
            all_tools = await get_catalog(ctx)
            results = await transform.search_tools(
                all_tools,
                query,
                categories=categories,
                subcategories=subcategories,
                providers=providers,
                requested_max_results=max_results,
            )
            if brief:
                lines = [
                    f"- `{t.name}`"
                    + (f": {t.description.splitlines()[0]}" if t.description else "")
                    for t in results
                ]
                return "\n".join(lines) if lines else "No tools matched the query."
            return await transform.render_results(results)

        return Tool.from_function(fn=search, name=name)

    def build_list_categories_tool(
        self,
        get_catalog: GetToolCatalog,
        *,
        name: str,
    ) -> Tool:
        """Build a list_categories tool backed by this transform's list_categories method."""
        transform = self

        async def list_categories(
            categories: Annotated[
                FilterArg,
                "Category filter before aggregation (string or list).",
            ] = None,
            subcategories: Annotated[
                FilterArg,
                "Subcategory filter before aggregation (string or list).",
            ] = None,
            providers: Annotated[
                FilterArg,
                "Provider filter before aggregation (string or list).",
            ] = None,
            ctx: Context = None,  # type: ignore[assignment]
        ) -> str | list[dict[str, Any]]:
            """List categories with tool counts and nested subcategory counts."""
            all_tools = await get_catalog(ctx)
            rows = transform.list_categories(
                all_tools,
                categories=categories,
                subcategories=subcategories,
                providers=providers,
            )
            return (
                _render_category_tree_as_markdown(rows)
                if transform.output_format == "markdown"
                else rows
            )

        return Tool.from_function(fn=list_categories, name=name)

    def build_get_schema_tool(self, get_catalog: GetToolCatalog, *, name: str) -> Tool:
        """Build a get_schema tool that returns full parameter schemas by tool name."""
        transform = self

        async def get_schema(
            names: Annotated[
                list[str],
                "One or more tool names to retrieve full parameter schemas for.",
            ],
            ctx: Context = None,  # type: ignore[assignment]
        ) -> str | list[dict[str, Any]]:
            """Get full parameter schemas for tools discovered via search."""
            all_tools = await get_catalog(ctx)
            tool_map = {t.name: t for t in all_tools}
            found = [tool_map[n] for n in names if n in tool_map]
            return (
                serialize_tools_for_output_markdown(found)
                if transform.output_format == "markdown"
                else serialize_tools_for_output_json(found)
            )

        return Tool.from_function(fn=get_schema, name=name)

    # ------------------------------------------------------------------
    # Standalone search mode (BaseSearchTransform overrides)
    # ------------------------------------------------------------------

    def _make_search_tool(self) -> Tool:
        return self.build_search_tool(
            self.get_tool_catalog, name=self._search_tool_name, brief=True
        )

    def _make_list_categories_tool(self) -> Tool:
        if self._cached_list_categories_tool is None:
            self._cached_list_categories_tool = self.build_list_categories_tool(
                self.get_tool_catalog, name=self._list_categories_tool_name
            )
        return self._cached_list_categories_tool

    def _make_get_schema_tool(self) -> Tool:
        if self._cached_get_schema_tool is None:
            self._cached_get_schema_tool = self.build_get_schema_tool(
                self.get_tool_catalog, name=self._get_schema_tool_name
            )
        return self._cached_get_schema_tool

    async def transform_tools(self, tools: Sequence[Tool]) -> Sequence[Tool]:
        """Expose list_categories + get_schema alongside search/call_tool."""
        transformed = list(await super().transform_tools(tools))
        synthetic_names = {t.name for t in transformed}
        if self._list_categories_tool_name not in synthetic_names:
            transformed.insert(0, self._make_list_categories_tool())
        if self._get_schema_tool_name not in synthetic_names:
            transformed.insert(1, self._make_get_schema_tool())
        return transformed

    async def get_tool(
        self, name: str, call_next: GetToolNext, *, version: VersionSpec | None = None
    ) -> Tool | None:
        """Intercept synthetic tool names for list_categories and get_schema."""
        if name == self._list_categories_tool_name:
            return self._make_list_categories_tool()
        if name == self._get_schema_tool_name:
            return self._make_get_schema_tool()
        return await super().get_tool(name, call_next, version=version)


# ------------------------------------------------------------------
# Factory functions
# ------------------------------------------------------------------


def build_openbb_code_mode_transform(
    *,
    sandbox_provider: Any,
    search_max_results: int = 30,
    search_output_format: Literal["json", "markdown"] = "markdown",
    execute_tool_name: str = "execute",
) -> CodeMode:
    """Build a FastMCP CodeMode transform for OpenBB.

    Discovery flow: ``list_categories → search → get_schema → execute``.

    ``search`` returns brief (name + description) results to minimise token
    usage; call ``get_schema`` with a tool name to retrieve the full
    parameter schema before calling ``execute``.
    """
    engine = OpenBBBM25SearchTransform(
        max_results=search_max_results,
        output_format=search_output_format,
    )
    detail: Literal["full", "detailed"] = (
        "detailed" if search_output_format == "markdown" else "full"
    )
    return CodeMode(
        sandbox_provider=sandbox_provider,
        execute_tool_name=execute_tool_name,
        discovery_tools=[
            lambda get_catalog: engine.build_list_categories_tool(
                get_catalog, name="list_categories"
            ),
            lambda get_catalog: engine.build_search_tool(
                get_catalog, name="search", brief=True
            ),
            GetSchemas(name="get_schema", default_detail=detail),
        ],
    )


def build_openbb_search_transform(
    *,
    max_results: int = 30,
    output_format: Literal["json", "markdown"] = "markdown",
    search_tool_name: str = "search",
    call_tool_name: str = "call_tool",
) -> BM25SearchTransform:
    """Build standalone search mode (without CodeMode execute sandbox)."""
    return OpenBBBM25SearchTransform(
        max_results=max_results,
        output_format=output_format,
        search_tool_name=search_tool_name,
        call_tool_name=call_tool_name,
        list_categories_tool_name="list_categories",
    )
