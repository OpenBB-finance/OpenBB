"""Dataflow search, indicator search, table listing mixin."""

from openbb_core.app.model.abstract.error import OpenBBError

from openbb_oecd.utils.metadata._constants import _TABLE_GROUP_CANDIDATES
from openbb_oecd.utils.metadata._helpers import (
    _matches_query,
    _parse_search_query,
)
from openbb_oecd.utils.metadata._typing import _MixinBase


class SearchMixin(_MixinBase):
    """Dataflow and indicator search methods."""

    _search_index: list[tuple[str, dict]] | None

    def search_dataflows(self, query: str) -> list[dict]:
        """Search dataflows by keyword."""
        self._ensure_dataflows()
        terms = [t.lower() for t in query.strip().split() if t.strip()]
        if not terms:
            return list(self.dataflows.values())

        results: list[dict] = []
        for fid, entry in self.dataflows.items():
            text = " ".join(
                [
                    fid,
                    entry.get("name", ""),
                    entry.get("description", ""),
                    entry.get("short_id", ""),
                ]
            ).lower()
            if all(t in text for t in terms):
                results.append(entry)
        return results

    def describe_dataflow(self, dataflow_id: str) -> dict:
        """Return a comprehensive description of a dataflow and its parameters."""
        full_id = self._resolve_dataflow_id(dataflow_id)
        self._ensure_description(full_id)
        df_meta = self.dataflows.get(full_id, {})
        dim_info = self.get_dimension_info(full_id)
        table_groups = self.get_table_groups(full_id)
        indicator_dim = self._find_indicator_dimension(full_id)
        indicator_tree = self.get_indicator_tree(full_id)

        def _count_leaves(nodes: list[dict]) -> int:
            total = 0
            for n in nodes:
                children = n.get("children", [])
                if children:
                    total += _count_leaves(children)
                else:
                    total += 1
            return total

        return {
            "dataflow_id": full_id,
            "short_id": df_meta.get("short_id", full_id.split("@")[-1]),
            "name": df_meta.get("name", full_id),
            "description": df_meta.get("description", ""),
            "dimensions": dim_info,
            "table_groups": table_groups,
            "indicator_dimension": indicator_dim or "",
            "indicator_count": _count_leaves(indicator_tree) if indicator_tree else 0,
            "indicator_tree": indicator_tree,
        }

    def search_indicators(
        self,
        query: str | None = None,
        dataflows: str | list[str] | None = None,
        keywords: str | list[str] | None = None,
    ) -> list[dict]:
        """Full-text search across dataflow indicators."""
        self._ensure_dataflows()

        target_ids: list[str] | None = None
        if dataflows:
            target_ids = (
                [d.strip() for d in dataflows.split(",")]
                if isinstance(dataflows, str)
                else dataflows
            )
        elif not query and not keywords:
            raise OpenBBError(
                "At least one of 'query', 'dataflows', or 'keywords' is required."
            )

        _table_dims = set(_TABLE_GROUP_CANDIDATES)
        if target_ids is not None:
            all_indicators: list[dict] = []
            for df_id in target_ids:
                full_id = None
                if df_id in self._dataflow_indicators_cache:
                    full_id = df_id
                else:
                    resolved = self._short_id_map.get(df_id)
                    if resolved and resolved in self._dataflow_indicators_cache:
                        full_id = resolved
                if full_id is None:
                    continue
                cached = self._dataflow_indicators_cache[full_id]
                constraints = self._dataflow_constraints.get(full_id, {})
                ind_dim = self._get_indicator_dim(full_id)
                if constraints and cached:
                    allowed_sets: dict[str, set[str]] = {
                        k: set(v) for k, v in constraints.items()
                    }
                    for ind in cached:
                        dim_id = ind.get("dimension_id", "")
                        if dim_id in _table_dims:
                            continue
                        if ind_dim and dim_id and dim_id != ind_dim:
                            continue
                        if (
                            not dim_id
                            or dim_id not in allowed_sets
                            or ind.get("indicator") in allowed_sets[dim_id]
                        ):
                            all_indicators.append(ind)
                else:
                    all_indicators.extend(
                        ind
                        for ind in cached
                        if ind.get("dimension_id", "") not in _table_dims
                        and not (
                            ind_dim
                            and ind.get("dimension_id", "")
                            and ind.get("dimension_id", "") != ind_dim
                        )
                    )

            if query:
                phrases = _parse_search_query(query)
                all_indicators = [
                    ind
                    for ind in all_indicators
                    if _matches_query(
                        f"{ind.get('label', '')} {ind.get('description', '')} "
                        f"{ind.get('dataflow_name', '')} {ind.get('dataflow_id', '')} "
                        f"{ind.get('indicator', '')}".lower(),
                        phrases,
                    )
                ]
        else:
            search_index = self._get_search_index()
            phrases = _parse_search_query(query) if query else []
            all_indicators = []

            for search_text, ind in search_index:
                if phrases and not _matches_query(search_text, phrases):
                    continue
                all_indicators.append(ind)

        if keywords:
            if isinstance(keywords, str):
                keywords = [keywords]

            for raw_kw in keywords:
                kw = raw_kw.strip()

                if kw.lower().startswith("not "):
                    exclude_word = kw[4:].strip().lower()
                    all_indicators = [
                        i
                        for i in all_indicators
                        if exclude_word
                        not in f"{i.get('label', '')} {i.get('description', '')} {i.get('indicator', '')}".lower()
                    ]
                else:
                    include_word = kw.lower()
                    all_indicators = [
                        i
                        for i in all_indicators
                        if include_word
                        in f"{i.get('label', '')} {i.get('description', '')} {i.get('indicator', '')}".lower()
                    ]

        return all_indicators

    def _get_search_index(self) -> list[tuple[str, dict]]:
        """Return a lazily-built search index: [(search_text, indicator_dict), ...]."""
        if hasattr(self, "_search_index") and self._search_index is not None:
            return self._search_index

        _table_dims = set(_TABLE_GROUP_CANDIDATES)
        index: list[tuple[str, dict]] = []
        for full_id, cached in self._dataflow_indicators_cache.items():
            constraints = self._dataflow_constraints.get(full_id, {})
            allowed_sets: dict[str, set[str]] = (
                {k: set(v) for k, v in constraints.items()} if constraints else {}
            )
            ind_dim = self._get_indicator_dim(full_id)
            for ind in cached:
                dim_id = ind.get("dimension_id", "")
                if dim_id in _table_dims:
                    continue
                if ind_dim and dim_id and dim_id != ind_dim:
                    continue
                if (
                    allowed_sets
                    and dim_id
                    and dim_id in allowed_sets
                    and ind.get("indicator") not in allowed_sets[dim_id]
                ):
                    continue
                text = (
                    f"{ind.get('label', '')} {ind.get('description', '')} "
                    f"{ind.get('dataflow_name', '')} {ind.get('dataflow_id', '')} "
                    f"{ind.get('indicator', '')}"
                ).lower()
                index.append((text, ind))

        self._search_index = index

        return index

    def list_tables(
        self,
        query: str | None = None,
        topic: str | None = None,
        subtopic: str | None = None,
    ) -> list[dict]:
        """List all OECD tables (dataflows) with names and topics."""
        rows = self.find_tables(query) if query else self.table_map()

        if topic:
            t = topic.upper()
            rows = [r for r in rows if r.get("topic_id", "").upper() == t]

        if subtopic:
            s = subtopic.upper()
            rows = [r for r in rows if r.get("subtopic_id", "").upper() == s]

        return [
            {
                "table_id": row["short_id"],
                "name": row["table"],
                "topic": row["topic"],
                "topic_id": row.get("topic_id", ""),
                "subtopic": row.get("subtopic", ""),
                "subtopic_id": row.get("subtopic_id", ""),
                "dataflow_id": row["dataflow_id"],
            }
            for row in rows
        ]

    def get_table(self, table_id: str) -> dict:
        """Get full metadata for a single table (dataflow)."""
        return self.describe_dataflow(table_id)

    def get_dataflow_hierarchies(self, dataflow_id: str) -> list[dict]:
        """Return available table / hierarchy identifiers for a dataflow."""
        full_id = self._resolve_dataflow_id(dataflow_id)
        self._ensure_structure(full_id)
        dsd = self.datastructures.get(full_id, {})

        table_dim = None
        for candidate in _TABLE_GROUP_CANDIDATES:
            for dim in dsd.get("dimensions", []):
                if dim["id"] == candidate:
                    table_dim = dim
                    break
            if table_dim is not None:
                break

        if table_dim is None:
            return []

        cl_id = table_dim.get("codelist_id", "")
        table_groups = self.get_table_groups(dataflow_id)

        return [
            {
                "id": g["value"],
                "name": g["label"],
                "description": g.get("description", g["label"]),
                "codelist_id": cl_id,
            }
            for g in table_groups
        ]

    def get_dataflow_table_structure(self, dataflow_id: str, table_id: str) -> dict:
        """Return the hierarchy structure for a specific table."""
        full_id = self._resolve_dataflow_id(dataflow_id)
        self._ensure_structure(full_id)

        groups = self.get_table_groups(dataflow_id)
        table_meta = next((g for g in groups if g["value"] == table_id), None)
        hierarchy_name = table_meta["label"] if table_meta else table_id

        tree = self.get_indicator_tree(dataflow_id)

        flat: list[dict] = []
        counter = [0]

        def _walk(nodes: list[dict], level: int, parent: str | None) -> None:
            for node in nodes:
                children_codes = [c["code"] for c in node.get("children", [])]
                flat.append(
                    {
                        "code": node["code"],
                        "label": node.get("label", node["code"]),
                        "order": counter[0],
                        "level": level,
                        "parent": parent,
                        "children": children_codes,
                    }
                )
                counter[0] += 1
                _walk(node.get("children", []), level + 1, node["code"])

        _walk(tree, 0, None)

        return {
            "hierarchy_id": table_id,
            "hierarchy_name": hierarchy_name,
            "indicators": flat,
        }
