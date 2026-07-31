"""ECB category-scheme and data-portal concept helpers."""

from __future__ import annotations

from openbb_core.app.model.abstract.error import OpenBBError

from openbb_ecb.utils.metadata._typing import MetadataBase


class CategoryMixin(MetadataBase):
    """Group dataflows by ECB topic and data-portal concept."""

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

    def list_concepts(self) -> list[dict]:
        """Return ``[{value, label, name, datasets, count}]`` for portal concepts."""
        out = [
            {
                "value": slug,
                "label": concept.get("name") or slug,
                "name": concept.get("name") or slug,
                "datasets": concept.get("datasets", []),
                "count": len(concept.get("datasets", [])),
            }
            for slug, concept in self.portal_concepts.items()
        ]
        return sorted(out, key=lambda c: c["name"])

    def get_concept(self, slug: str) -> dict:
        """Return the cached data-portal concept or raise."""
        concept = self.portal_concepts.get(slug)
        if concept is None:
            raise OpenBBError(
                f"Unknown ECB concept '{slug}'. Use `list_concepts` to see them."
            )
        return concept

    def get_dataflow_info(self, dataflow_id: str) -> dict | None:
        """Return a dataflow's rich ``data-information`` metadata, if published."""
        return self.dataflow_info.get(dataflow_id)

    def concepts_for_dataflow(self, dataflow_id: str) -> list[str]:
        """Return the names of the concepts that include a dataflow's dataset."""
        return sorted(
            concept.get("name") or slug
            for slug, concept in self.portal_concepts.items()
            if dataflow_id in concept.get("datasets", [])
        )
