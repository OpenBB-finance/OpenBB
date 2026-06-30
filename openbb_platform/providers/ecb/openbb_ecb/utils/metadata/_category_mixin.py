"""ECB category-scheme (topic) helpers."""

from __future__ import annotations

from openbb_ecb.utils.metadata._typing import MetadataBase


class CategoryMixin(MetadataBase):
    """Group dataflows by ECB topic (category scheme)."""

    def list_topics(self) -> list[dict]:
        """Return ``[{label, value, count}]`` for topics that have dataflows."""
        out: list[dict] = []
        for cat_id, cat in self.categories.items():
            flows = self.category_dataflows.get(cat_id, [])
            if not flows:
                continue
            name = cat.get("name") or cat_id
            out.append(
                {
                    "label": f"{name} ({len(flows)})",
                    "value": cat_id,
                    "name": name,
                    "description": cat.get("description", ""),
                    "count": len(flows),
                }
            )
        return sorted(out, key=lambda d: d["name"])

    def get_topic_dataflows(self, category_id: str) -> list[str]:
        """Return the dataflow ids categorised under ``category_id``."""
        return sorted(self.category_dataflows.get(category_id, []))

    def topics_for_dataflow(self, dataflow_id: str) -> list[str]:
        """Return the topic names a dataflow belongs to."""
        names: list[str] = []
        for cat_id in self.dataflow_categories.get(dataflow_id, []):
            cat = self.categories.get(cat_id)
            if cat and cat.get("name"):
                names.append(cat["name"])
        return names
