"""Lightweight category index for tool discovery.

Maintains a read-only hierarchical mapping of
``category → subcategory → [tool_name]`` so that discovery admin tools
can present a browsable catalogue.  All enable/disable and visibility
state is delegated to FastMCP's native visibility system.
"""

import re
from collections import defaultdict
from collections.abc import Mapping
from dataclasses import dataclass, field


def _first_sentence(text: str) -> str:
    """Extract the first sentence from *text* for use as a short summary.

    Strips everything after API documentation headers (**Query Parameters,
    **Responses), then returns the first sentence (delimited by newline,
    period, or end-of-string).  Falls back to the first line if no period
    is found.
    """
    if not text:
        return ""
    # Strip API doc sections first
    brief, *_ = re.split(r"\n{2,}\*\*(?:Query Parameters|Responses):", text, maxsplit=1)
    brief = brief.strip()
    if not brief:
        return ""
    # Take first sentence  (period followed by whitespace or end)
    m = re.search(r"^(.+?\.)(\s|$)", brief, re.DOTALL)
    if m:
        return m.group(1).strip()
    # No period — take first line
    return brief.split("\n", 1)[0].strip()


@dataclass
class CategoryIndex:
    """Maps tools to their category/subcategory for discovery browsing.

    This is a **read-only index** populated once at startup.  It carries no
    enable/disable state — that responsibility belongs to FastMCP's
    mcp.enable() / mcp.disable() and per-session
    ctx.enable_components() / ctx.disable_components().
    """

    _by_category: dict[str, dict[str, set[str]]] = field(
        default_factory=lambda: defaultdict(lambda: defaultdict(set))
    )
    _all_names: set[str] = field(default_factory=set)
    _descriptions: dict[str, str] = field(default_factory=dict)

    # ------------------------------------------------------------------
    # Population (called once per tool during server creation)
    # ------------------------------------------------------------------

    def register(
        self,
        *,
        category: str,
        subcategory: str,
        tool_name: str,
        description: str = "",
    ) -> None:
        """Register a tool name under ``category / subcategory``.

        *description* is stored as a short one-line summary for use in
        discovery listings when the tool is not active.
        """
        self._by_category[category][subcategory].add(tool_name)
        self._all_names.add(tool_name)
        self._descriptions[tool_name] = _first_sentence(description)

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def get_categories(self) -> Mapping[str, Mapping[str, set[str]]]:
        """Return the full ``category → subcategory → {tool_names}`` mapping."""
        return self._by_category

    def get_category_names(self, category: str) -> set[str]:
        """Return all tool names belonging to *category* (across all subcategories)."""
        return {
            name
            for subcat_names in self._by_category.get(category, {}).values()
            for name in subcat_names
        }

    def get_subcategory_names(self, category: str, subcategory: str) -> set[str]:
        """Return tool names in a specific subcategory."""
        return self._by_category.get(category, {}).get(subcategory, set())

    def get_subcategories(self, category: str) -> Mapping[str, set[str]] | None:
        """Return all subcategories for *category*, or *None* if absent."""
        return self._by_category.get(category)

    def all_tool_names(self) -> set[str]:
        """Return every registered tool name."""
        return set(self._all_names)

    def has_tool(self, tool_name: str) -> bool:
        """Return *True* if *tool_name* was registered."""
        return tool_name in self._all_names

    def get_description(self, tool_name: str) -> str:
        """Return the cached short description, or a fallback."""
        return self._descriptions.get(tool_name, "No description available")

    def clear(self) -> None:
        """Clear the index."""
        self._by_category.clear()
        self._all_names.clear()
        self._descriptions.clear()
