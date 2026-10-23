"""Dataflow listing and text search over the cached catalog."""

from __future__ import annotations

from openbb_ecb.utils.metadata._helpers import matches_query, parse_search_query
from openbb_ecb.utils.metadata._typing import MetadataBase


class SearchMixin(MetadataBase):
    """List and search the ECB dataflow catalog."""

    def list_dataflows(self) -> list[dict]:
        """Return ``[{label, value, name, description, topics}]`` for all dataflows."""
        out: list[dict] = []
        for df_id, df in self.dataflows.items():
            name = df.get("name") or df_id
            out.append(
                {
                    "label": f"{name} ({df_id})",
                    "value": df_id,
                    "name": name,
                    "description": df.get("description", ""),
                    "topics": self.topics_for_dataflow(df_id),
                }
            )
        return sorted(out, key=lambda d: d["value"])

    def search_dataflows(self, query: str) -> list[dict]:
        """Return dataflows whose id/name/description match ``query``."""
        parsed = parse_search_query(query)
        results: list[dict] = []
        for df_id, df in self.dataflows.items():
            name = df.get("name") or df_id
            haystack = f"{df_id} {name} {df.get('description', '')}"
            if matches_query(haystack, parsed):
                results.append(
                    {
                        "label": f"{name} ({df_id})",
                        "value": df_id,
                        "name": name,
                        "description": df.get("description", ""),
                        "topics": self.topics_for_dataflow(df_id),
                    }
                )
        return sorted(results, key=lambda d: d["value"])
