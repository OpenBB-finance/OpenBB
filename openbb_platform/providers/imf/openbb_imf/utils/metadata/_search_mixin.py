"""Search mixin."""

from __future__ import annotations

import warnings

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.app.model.abstract.warning import OpenBBWarning

from openbb_imf.utils.metadata._typing import _MixinBase


class SearchMixin(_MixinBase):
    """Listing, dataflow search, and indicator search."""

    def list_dataflows(self: _MixinBase) -> list[dict]:
        """Return ``[{label, value}]`` for every cached dataflow."""
        dfs: list = []
        for key in sorted(self.dataflows.keys()):
            label = self.dataflows[key].get("name", key)
            value = self.dataflows[key].get("id", key)
            dfs.append({"label": label.strip(), "value": value.strip()})
        return dfs

    def search_dataflows(self: _MixinBase, query: str) -> list[dict]:
        """Search dataflows by id, name, and description.

        Parameters
        ----------
        query : str
            Search string. Supports AND (+), OR (|), and quoted phrases.

        Returns
        -------
        list[dict]
            Matches grouped by structureRef id.
        """
        parsed_query = self._parse_query(query)
        if not parsed_query:
            raise OpenBBError(
                ValueError(f"Query string is empty or invalid -> '{query}'")
            )

        grouped: dict = {}
        for dataflow_obj in self.dataflows.values():
            haystack = (
                dataflow_obj.get("id", "").lower()
                + " "
                + dataflow_obj.get("name", "").lower()
                + " "
                + dataflow_obj.get("description", "").lower()
            )
            if not _matches_query(haystack, parsed_query):
                continue

            structure_ref_id = dataflow_obj.get("structureRef", {}).get("id")
            if not structure_ref_id:
                continue
            grouped.setdefault(structure_ref_id, []).append(
                {
                    "id": dataflow_obj.get("id"),
                    "name": dataflow_obj.get("name"),
                    "description": dataflow_obj.get("description", ""),
                }
            )

        return [
            {"group_id": group_id, "dataflows": dataflows}
            for group_id, dataflows in grouped.items()
        ]

    def search_indicators(
        self: _MixinBase,
        query: str,
        dataflows: list[str] | str | None = None,
        keywords: list[str] | None = None,
    ) -> list[dict]:
        """Search indicators across one or more dataflows.

        Parameters
        ----------
        query : str
            Semicolon-separated search phrases. Each phrase supports AND (+),
            OR (|), and quoted exact matches.
        dataflows : list[str] | str | None
            Restrict to specific dataflow ids.
        keywords : list[str] | None
            Token-level filters; ``"not <word>"`` excludes.

        Returns
        -------
        list[dict]
            Matching indicators enriched with ``tables`` and ``member_of``.
        """
        target_dataflow_ids: list = []
        if dataflows:
            target_dataflow_ids = (
                [dataflows] if isinstance(dataflows, str) else dataflows
            )
        else:
            if not query and not keywords:
                raise OpenBBError(
                    "A query must be provided when no dataflows and "
                    "keywords are specified."
                )
            target_dataflow_ids = list(self.dataflows.keys())

        if not target_dataflow_ids:
            raise OpenBBError(
                "No valid dataflows found to search indicators in. "
                "This might be due to incorrect dataflow IDs."
            )

        indicator_to_tables, indicator_table_text = self._build_indicator_table_maps(
            set(target_dataflow_ids)
        )
        all_indicators = self._collect_indicators(
            set(target_dataflow_ids), indicator_to_tables, indicator_table_text
        )
        search_results = self._filter_indicators_by_query(all_indicators, query)
        return self._filter_indicators_by_keywords(search_results, keywords)

    def _build_indicator_table_maps(
        self: _MixinBase, dataflow_ids: set[str]
    ) -> tuple[dict[str, list[dict]], dict[str, str]]:
        """Return (tables-per-indicator, search-text-per-indicator)."""
        indicator_to_tables: dict[str, list[dict]] = {}
        indicator_table_text: dict[str, str] = {}

        for df_id in dataflow_ids:
            try:
                hierarchies = self.get_dataflow_hierarchies(df_id)
            except Exception:  # noqa: BLE001, S110
                continue
            for hierarchy in hierarchies:
                try:
                    structure = self.get_dataflow_table_structure(
                        df_id, hierarchy["id"]
                    )
                except Exception:  # noqa: BLE001, S112
                    continue
                table_search_text = (
                    hierarchy.get("name", "").lower()
                    + " "
                    + hierarchy.get("description", "").lower()
                )
                for ind in structure.get("indicators", []):
                    if ind.get("is_group"):
                        continue
                    indicator_code = ind.get("indicator_code") or ind.get("code")
                    if not indicator_code:
                        continue
                    key = f"{df_id}_{indicator_code}"
                    if key not in indicator_to_tables:
                        indicator_to_tables[key] = []
                        indicator_table_text[key] = ""
                    table_entry = {
                        "table_id": hierarchy["id"],
                        "table_name": hierarchy["name"],
                    }
                    if table_entry not in indicator_to_tables[key]:
                        indicator_to_tables[key].append(table_entry)
                        indicator_table_text[key] += " " + table_search_text

        return indicator_to_tables, indicator_table_text

    def _collect_indicators(
        self: _MixinBase,
        dataflow_ids: set[str],
        indicator_to_tables: dict[str, list[dict]],
        indicator_table_text: dict[str, str],
    ) -> list[dict]:
        """Aggregate indicators from each dataflow."""
        all_indicators: list = []
        for df_id in dataflow_ids:
            try:
                indicators = self.get_indicators_in(df_id)
            except (KeyError, ValueError, OpenBBError) as e:
                warnings.warn(
                    f"Could not retrieve indicators for dataflow '{df_id}': {e}",
                    OpenBBWarning,
                )
                continue
            for ind in indicators:
                key = f"{df_id}_{ind['indicator']}"
                ind["tables"] = indicator_to_tables.get(key, [])
                ind["member_of"] = [f"{df_id}::{t['table_id']}" for t in ind["tables"]]
                ind["_table_search_text"] = indicator_table_text.get(key, "")
            all_indicators.extend(indicators)
        return all_indicators

    def _filter_indicators_by_query(
        self: _MixinBase, indicators: list[dict], query: str
    ) -> list[dict]:
        """Apply the semicolon-separated phrase filter."""
        if not query:
            return indicators

        phrases = [p.strip() for p in query.split(";") if p.strip()]
        if not phrases:
            return indicators

        results: list = []
        for indicator in indicators:
            text = (
                indicator.get("label", "").lower()
                + " "
                + indicator.get("description", "").lower()
                + " "
                + indicator.get("dataflow_name", "").lower()
                + " "
                + indicator.get("dataflow_id", "").lower()
                + " "
                + indicator.get("indicator", "").lower()
                + " "
                + indicator.get("_table_search_text", "")
            )
            for phrase in phrases:
                parsed_phrase = self._parse_query(phrase)
                if not parsed_phrase:
                    if phrase.lower() in text:
                        results.append(indicator)
                        break
                elif any(
                    all(term in text for term in or_group) for or_group in parsed_phrase
                ):
                    results.append(indicator)
                    break
        return results

    def _filter_indicators_by_keywords(
        self: _MixinBase, indicators: list[dict], keywords: list[str] | None
    ) -> list[dict]:
        """Apply per-keyword include / ``not <word>`` exclude filters."""
        if not keywords:
            for indicator in indicators:
                indicator.pop("_table_search_text", None)
            return indicators

        kept: list = []
        for indicator in indicators:
            text = (
                indicator.get("indicator", "")
                + " "
                + indicator.get("label", "")
                + " "
                + indicator.get("description", "")
                + " "
                + indicator.get("_table_search_text", "")
            ).lower()
            include = True
            for keyword in keywords:
                kw = keyword.strip()
                if kw.lower().startswith("not "):
                    exclude_word = kw[4:].lower()
                    if exclude_word and exclude_word in text:
                        include = False
                        break
                elif kw.lower() not in text:
                    include = False
                    break
            if include:
                kept.append(indicator)

        for indicator in kept:
            indicator.pop("_table_search_text", None)
        return kept


def _matches_query(haystack: str, parsed_query: list[list[str]]) -> bool:
    """Match ``haystack`` against an OR-of-AND-of-terms query."""
    return any(all(term in haystack for term in or_group) for or_group in parsed_query)
