"""Read-only category index of the OpenBB route tools."""

import re
from collections import defaultdict
from collections.abc import Mapping
from dataclasses import dataclass, field


def _first_sentence(text: str) -> str:
    """Return the first sentence of the text before any API documentation section."""
    if not text:
        return ""
    brief, *_ = re.split(r"\n{2,}\*\*(?:Query Parameters|Responses):", text, maxsplit=1)
    brief = brief.strip()
    if not brief:
        return ""
    m = re.search(r"^(.+?\.)(\s|$)", brief, re.DOTALL)
    if m:
        return m.group(1).strip()
    return brief.split("\n", 1)[0].strip()


@dataclass
class CategoryIndex:
    """Map each tool to its category and subcategory for discovery browsing."""

    _by_category: dict[str, dict[str, set[str]]] = field(
        default_factory=lambda: defaultdict(lambda: defaultdict(set))
    )
    _all_names: set[str] = field(default_factory=set)
    _descriptions: dict[str, str] = field(default_factory=dict)

    def register(
        self,
        *,
        category: str,
        subcategory: str,
        tool_name: str,
        description: str = "",
    ) -> None:
        """Register a tool under its category and subcategory with a one-sentence summary."""
        self._by_category[category][subcategory].add(tool_name)
        self._all_names.add(tool_name)
        self._descriptions[tool_name] = _first_sentence(description)

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

    def get_description(self, tool_name: str) -> str:
        """Return the cached short description, or a fallback."""
        return self._descriptions.get(tool_name, "No description available")

    def clear(self) -> None:
        """Clear the index."""
        self._by_category.clear()
        self._all_names.clear()
        self._descriptions.clear()
