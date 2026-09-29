"""Presentation table mixin."""

from __future__ import annotations

import re
from collections import defaultdict

from openbb_imf.utils.metadata._constants import (
    DEPTH_OVERRIDE_DATAFLOWS,
    INDICATOR_DIMENSION_CANDIDATES,
    INDICATOR_DIMENSION_SUBSTRINGS,
)
from openbb_imf.utils.metadata._typing import _MixinBase

_IRFCL_PATH_PATTERNS: tuple[str, ...] = (
    "Options in foreign currencies",
    "Up to 1 month",
    "More than 1 and up to",
    "More than 3 months",
    "In-the-money",
    "Long positions",
    "Short positions",
)

_HIERARCHY_INDICATOR_CANDIDATES: tuple[str, ...] = (
    "INDICATOR",
    "COICOP_1999",
    "PRODUCTION_INDEX",
    "ACTIVITY",
    "PRODUCT",
    "SERIES",
    "ITEM",
    "ACCOUNTING_ENTRY",
    "SECTOR",
)


class TableMixin(_MixinBase):
    """Presentation table resolution and rendering."""

    def _validate_hierarchy_queryable(
        self: _MixinBase, dataflow_id: str, codes: list
    ) -> bool:
        """Return True if a sample of ``codes`` maps to queryable dimensions."""
        if not codes:
            return False

        sample_size = min(10, len(codes))
        valid_count = 0
        for code_entry in codes[:sample_size]:
            code_urn = code_entry.get("code", "")
            if not code_urn:
                continue
            codelist_id = self._parse_codelist_id_from_urn(code_urn)
            if not codelist_id:
                continue
            if self._get_dimension_for_codelist(dataflow_id, codelist_id):
                valid_count += 1
        return valid_count >= (sample_size * 0.5)

    def get_dataflow_hierarchies(self: _MixinBase, dataflow_id: str) -> list[dict]:
        """List presentation tables attached to a dataflow."""
        if dataflow_id not in self.dataflows:
            raise ValueError(f"Dataflow '{dataflow_id}' not found.")

        dataflow_obj = self.dataflows[dataflow_id]
        result: list = []

        dsd_id = dataflow_obj.get("structureRef", {}).get("id")
        if not dsd_id or dsd_id not in self.datastructures:
            return result

        dsd = self.datastructures[dsd_id]
        dimensions = dsd.get("dimensions", [])

        indicator_codelist_id = self._find_indicator_codelist_for_hierarchies(
            dataflow_id, dsd_id, dimensions
        )
        if not indicator_codelist_id:
            return result

        hierarchy_ids = self._codelist_to_hierarchies_map.get(indicator_codelist_id, [])

        available_indicator_values: set[str] = set()
        try:
            params = self.get_dataflow_parameters(dataflow_id)
            if "INDICATOR" in params:
                available_indicator_values.update(
                    opt.get("value", "") for opt in params["INDICATOR"]
                )
        except Exception:  # noqa: BLE001, S110
            pass

        for hier_id in hierarchy_ids:
            hier_obj = self.hierarchies.get(hier_id)
            if not hier_obj:
                continue
            if available_indicator_values and not _hierarchy_overlaps_dataflow(
                hier_obj, available_indicator_values
            ):
                continue

            top_level_codes = hier_obj.get("hierarchicalCodes", [])
            if len(top_level_codes) > 1 and dataflow_id == "IRFCL":
                result.extend(
                    self._split_irfcl_hierarchy(
                        dataflow_id,
                        hier_id,
                        hier_obj,
                        top_level_codes,
                        indicator_codelist_id,
                    )
                )
            else:
                descriptions = hier_obj.get("descriptions", {})
                result.append(
                    {
                        "id": hier_id,
                        "name": hier_obj.get("name", ""),
                        "description": descriptions.get("en", "")
                        if descriptions
                        else "",
                        "codelist_id": indicator_codelist_id,
                        "agency_id": hier_obj.get("agencyID", ""),
                        "version": hier_obj.get("version", ""),
                        "type": "hierarchy",
                    }
                )

        return result

    def _find_indicator_codelist_for_hierarchies(
        self: _MixinBase,
        dataflow_id: str,
        dsd_id: str,
        dimensions: list,
    ) -> str | None:
        """Pick the dimension whose codelist owns the dataflow's hierarchies."""
        dim_lookup = {d.get("id", ""): d for d in dimensions}

        for candidate in _HIERARCHY_INDICATOR_CANDIDATES:
            if candidate not in dim_lookup:
                continue
            dim = dim_lookup[candidate]
            cl_id = self._resolve_codelist_id(dataflow_id, dsd_id, candidate, dim)
            if cl_id and self._codelist_to_hierarchies_map.get(cl_id):
                return cl_id

        for dim in dimensions:
            dim_id = dim.get("id", "")
            if "INDICATOR" in dim_id and dim_id not in _HIERARCHY_INDICATOR_CANDIDATES:
                cl_id = self._resolve_codelist_id(dataflow_id, dsd_id, dim_id, dim)
                if cl_id:
                    return cl_id
        return None

    def _split_irfcl_hierarchy(
        self: _MixinBase,
        dataflow_id: str,
        hier_id: str,
        hier_obj: dict,
        top_level_codes: list[dict],
        indicator_codelist_id: str,
    ) -> list[dict]:
        """Generate one table entry per top-level code in an IRFCL hierarchy."""
        section_codes = self._codelist_cache.get(f"CL_{dataflow_id}_SECTION", {})
        out: list = []
        for idx, top_code in enumerate(top_level_codes):
            top_code_id = top_code.get("id", "")
            top_code_urn = top_code.get("code", "")
            actual_code = (
                top_code_urn.rsplit(".", 1)[-1] if "." in top_code_urn else top_code_id
            )
            urn_codelist_id = self._parse_codelist_id_from_urn(top_code_urn)
            table_label = self._codelist_cache.get(
                urn_codelist_id or indicator_codelist_id, {}
            ).get(actual_code, actual_code)
            for section_code, section_label in section_codes.items():
                if actual_code.startswith(section_code):
                    table_label = section_label
                    break
            out.append(
                {
                    "id": f"{hier_id}:{top_code_id}",
                    "name": table_label,
                    "description": "",
                    "codelist_id": indicator_codelist_id,
                    "agency_id": hier_obj.get("agencyID", ""),
                    "version": hier_obj.get("version", ""),
                    "type": "hierarchy",
                    "table_index": idx,
                    "top_level_code_id": top_code_id,
                    "indicator_code": actual_code,
                }
            )
        return out

    def get_dataflow_table_structure(
        self: _MixinBase, dataflow_id: str, table_id: str | None = None
    ) -> dict:
        """Return the resolved indicator tree for a presentation table."""
        available_hierarchies = self.get_dataflow_hierarchies(dataflow_id)
        if not available_hierarchies:
            raise ValueError(
                f"No presentation hierarchies found for dataflow '{dataflow_id}'"
            )

        top_level_code_filter, base_hierarchy_id, selected_table, table_id = (
            self._select_hierarchy(table_id, available_hierarchies)
        )

        hierarchy = self.hierarchies.get(base_hierarchy_id or table_id)
        if not hierarchy:
            raise ValueError(
                f"Hierarchy '{base_hierarchy_id or table_id}' not found in cache"
            )
        if not table_id:
            raise ValueError("table_id cannot be None")

        codelist_id = self._hierarchy_to_codelist_map.get(base_hierarchy_id or table_id)

        dataflow_obj = self.dataflows.get(dataflow_id, {})
        agency_id = dataflow_obj.get("agencyID", "IMF")
        agency_clean = agency_id.replace(".", "_")

        structure_ref = dataflow_obj.get("structureRef", {})
        dsd_id = structure_ref.get("id")
        dsd_obj = self.datastructures.get(dsd_id, {}) if dsd_id else {}
        dimensions = dsd_obj.get("dimensions", []) if isinstance(dsd_obj, dict) else []

        indicator_dimension_order: dict[str, int] = {}
        for idx, dim in enumerate(dimensions):
            dim_id = dim.get("id", "")
            if not dim_id:
                continue
            is_indicator = dim_id in INDICATOR_DIMENSION_CANDIDATES or any(
                token in dim_id for token in INDICATOR_DIMENSION_SUBSTRINGS
            )
            if is_indicator:
                indicator_dimension_order[dim_id] = idx

        codelist_dimension_cache: dict[str, str | None] = {}
        codelist_labels_cache: dict[str, dict] = {}
        codelist_desc_cache: dict[str, dict] = {}

        hierarchical_codes = hierarchy.get("hierarchicalCodes", [])
        if top_level_code_filter:
            filtered = [
                c for c in hierarchical_codes if c.get("id") == top_level_code_filter
            ]
            if filtered:
                hierarchical_codes = filtered

        indicators = self._process_hierarchical_codes(
            hierarchical_codes,
            dataflow_id=dataflow_id,
            agency_clean=agency_clean,
            indicator_dimension_order=indicator_dimension_order,
            codelist_dimension_cache=codelist_dimension_cache,
            codelist_labels_cache=codelist_labels_cache,
            codelist_desc_cache=codelist_desc_cache,
        )

        if dataflow_id == "IRFCL":
            indicators = self._fix_irfcl_hierarchy(indicators)

        table_name = (
            selected_table.get("name", hierarchy.get("name"))
            if selected_table
            else hierarchy.get("name")
        )
        return {
            "hierarchy_id": table_id,
            "hierarchy_name": table_name,
            "hierarchy_description": hierarchy.get("description", ""),
            "dataflow_id": dataflow_id,
            "codelist_id": codelist_id,
            "agency_id": hierarchy.get("agencyID"),
            "version": hierarchy.get("version"),
            "indicators": indicators,
            "total_indicators": len([i for i in indicators if not i["is_group"]]),
            "total_groups": len([i for i in indicators if i["is_group"]]),
            "type": "hierarchy",
        }

    @staticmethod
    def _select_hierarchy(
        table_id: str | None, available_hierarchies: list[dict]
    ) -> tuple[str | None, str | None, dict | None, str]:
        """Resolve ``table_id`` to (filter, base, table-dict, normalized-id)."""
        if table_id:
            selected_table = next(
                (h for h in available_hierarchies if h["id"] == table_id), None
            )
            if not selected_table:
                raise ValueError(
                    f"Hierarchy '{table_id}' not found. Available: "
                    f"{[h['id'] for h in available_hierarchies]}"
                )
            if ":" in table_id:
                base, top = table_id.split(":", 1)
                return top, base, selected_table, table_id
            return None, table_id, selected_table, table_id

        selected_table = available_hierarchies[0]
        table_id = selected_table.get("id", "") or ""
        if table_id and ":" in table_id:
            base, top = table_id.split(":", 1)
            return top, base, selected_table, table_id
        return None, table_id, selected_table, table_id

    def _process_hierarchical_codes(
        self: _MixinBase,
        codes: list,
        *,
        dataflow_id: str,
        agency_clean: str,
        indicator_dimension_order: dict[str, int],
        codelist_dimension_cache: dict[str, str | None],
        codelist_labels_cache: dict[str, dict],
        codelist_desc_cache: dict[str, dict],
        parent_id: str | None = None,
        depth: int = 0,
        parent_codes: list | None = None,
        parent_dimension_codes: dict[str, str] | None = None,
        order_counter: list | None = None,
        parent_full_label: str | None = None,
        ancestor_labels: list | None = None,
    ) -> list[dict]:
        """Recursive descent into ``hierarchicalCodes``."""
        indicators: list = []

        if parent_codes is None:
            parent_codes = []
        if parent_dimension_codes is None:
            parent_dimension_codes = {}
        if order_counter is None:
            order_counter = [0]
        if ancestor_labels is None:
            ancestor_labels = []

        for code_entry in codes:
            code_id = code_entry.get("id")
            code_urn = code_entry.get("code", "")
            level = code_entry.get("level", "0")
            indicator_code = self._parse_indicator_code_from_urn(code_urn)
            codelist_id_for_code = self._parse_codelist_id_from_urn(code_urn)

            dimension_id = self._resolve_dimension_for_code(
                dataflow_id,
                codelist_id_for_code,
                code_urn,
                codelist_dimension_cache,
                codelist_labels_cache,
                codelist_desc_cache,
            )

            code_labels = (
                codelist_labels_cache.get(codelist_id_for_code, {})
                if codelist_id_for_code
                else {}
            )
            code_descs = (
                codelist_desc_cache.get(codelist_id_for_code, {})
                if codelist_id_for_code
                else {}
            )
            full_label = (
                code_labels.get(indicator_code, code_id) if indicator_code else code_id
            )
            label = _derive_node_label(
                codelist_id_for_code=codelist_id_for_code,
                full_label=full_label,
                parent_full_label=parent_full_label,
                ancestor_labels=ancestor_labels,
            )
            description = code_descs.get(indicator_code, "") if indicator_code else ""

            children = code_entry.get("hierarchicalCodes", [])
            is_group = len(children) > 0

            current_dimension_codes = parent_dimension_codes.copy()
            if dimension_id and indicator_code:
                current_dimension_codes[dimension_id] = indicator_code

            clean_parent_id = parent_id
            if parent_id and "___" in parent_id:
                clean_parent_id = parent_id.split("___")[-1]

            order_counter[0] += 1
            current_order = order_counter[0]

            use_depth = dataflow_id in DEPTH_OVERRIDE_DATAFLOWS
            node_level = depth if use_depth else (int(level) if level else depth)

            indicator_info: dict = {
                "id": code_id,
                "indicator_code": indicator_code,
                "label": label,
                "description": description,
                "order": current_order,
                "level": node_level,
                "depth": depth,
                "parent_id": clean_parent_id,
                "is_group": is_group,
                "code_urn": code_urn,
                "dimension_id": dimension_id,
            }
            if indicator_code and dimension_id:
                indicator_info["series_id"] = _build_series_id(
                    agency_clean=agency_clean,
                    dataflow_id=dataflow_id,
                    current_dimension_codes=current_dimension_codes,
                    indicator_dimension_order=indicator_dimension_order,
                    parent_codes=parent_codes,
                    indicator_code=indicator_code,
                )

            indicators.append(indicator_info)

            if children:
                child_parent_codes = parent_codes + (
                    [indicator_code] if indicator_code else []
                )
                child_indicators = self._process_hierarchical_codes(
                    children,
                    dataflow_id=dataflow_id,
                    agency_clean=agency_clean,
                    indicator_dimension_order=indicator_dimension_order,
                    codelist_dimension_cache=codelist_dimension_cache,
                    codelist_labels_cache=codelist_labels_cache,
                    codelist_desc_cache=codelist_desc_cache,
                    parent_id=code_id,
                    depth=depth + 1,
                    parent_codes=child_parent_codes,
                    parent_dimension_codes=current_dimension_codes.copy(),
                    order_counter=order_counter,
                    parent_full_label=full_label,
                    ancestor_labels=ancestor_labels + [full_label],
                )
                indicators.extend(child_indicators)

        return indicators

    def _resolve_dimension_for_code(
        self: _MixinBase,
        dataflow_id: str,
        codelist_id_for_code: str | None,
        code_urn: str,
        codelist_dimension_cache: dict[str, str | None],
        codelist_labels_cache: dict[str, dict],
        codelist_desc_cache: dict[str, dict],
    ) -> str | None:
        """Memoize the dimension + labels + descriptions for a codelist."""
        if not codelist_id_for_code:
            return None
        if codelist_id_for_code not in codelist_dimension_cache:
            codelist_dimension_cache[codelist_id_for_code] = (
                self._get_dimension_for_codelist(dataflow_id, codelist_id_for_code)
            )

        cached_is_empty = not codelist_labels_cache.get(codelist_id_for_code)
        if codelist_id_for_code not in codelist_labels_cache or cached_is_empty:
            cached_labels = self._codelist_cache.get(codelist_id_for_code, {})
            cached_descs = self._codelist_descriptions.get(codelist_id_for_code, {})
            if not cached_labels and code_urn:
                urn_agency = self._parse_agency_from_urn(code_urn)
                if urn_agency:
                    self._fetch_single_codelist(urn_agency, codelist_id_for_code)
                    cached_labels = self._codelist_cache.get(codelist_id_for_code, {})
                    cached_descs = self._codelist_descriptions.get(
                        codelist_id_for_code, {}
                    )
            codelist_labels_cache[codelist_id_for_code] = cached_labels
            codelist_desc_cache[codelist_id_for_code] = cached_descs

        return codelist_dimension_cache[codelist_id_for_code]

    def _fix_irfcl_hierarchy(self: _MixinBase, indicators: list[dict]) -> list[dict]:
        """Re-parent IRFCL ``forwards`` children to be siblings."""
        forwards_node = next(
            (i for i in indicators if i.get("label", "").lower() == "forwards"),
            None,
        )
        if not forwards_node:
            return indicators

        forwards_id = forwards_node.get("id")
        forwards_parent_id = forwards_node.get("parent_id")
        forwards_depth = forwards_node.get("depth", 0)

        instrument_labels = {"futures", "swaps", "options", "other"}
        for ind in indicators:
            if ind.get("parent_id") != forwards_id:
                continue
            if ind.get("label", "").lower() in instrument_labels:
                ind["parent_id"] = forwards_parent_id
                ind["depth"] = forwards_depth
        return indicators

    def _create_synthetic_groups_for_shared_prefixes(
        self: _MixinBase, indicators: list[dict]
    ) -> list[dict]:
        """Wrap IRFCL siblings with shared path components under synthetic groups."""
        by_parent: dict[str | None, list[dict]] = defaultdict(list)
        for ind in indicators:
            by_parent[ind.get("parent_id")].append(ind)

        synthetic_groups: list[dict] = []

        for parent_id, children in by_parent.items():
            path_children = [
                c
                for c in children
                if ", " in c.get("label", "")
                and c.get("id")
                and _is_irfcl_path_label(c.get("label", ""))
            ]
            if len(path_children) < 2:
                continue

            labels = [c["label"] for c in path_children]
            split_labels = [lbl.split(", ") for lbl in labels]
            if not all(
                split_labels
            ):  # pragma: no cover -- unreachable: ``str.split(", ")`` always returns a non-empty list, so every element of ``split_labels`` is truthy
                continue

            min_parts = min(len(parts) for parts in split_labels)
            shared_prefix_count = 0
            for i in range(min_parts - 1):
                first_part = split_labels[0][i]
                if all(parts[i] == first_part for parts in split_labels):
                    shared_prefix_count += 1
                else:
                    break

            shared_suffix_count = 0
            for i in range(1, min_parts):
                last_part = split_labels[0][-i]
                if all(parts[-i] == last_part for parts in split_labels):
                    shared_suffix_count += 1
                else:
                    break

            if shared_suffix_count > 0 and shared_suffix_count >= shared_prefix_count:
                self._wrap_with_suffix_groups(
                    path_children,
                    split_labels,
                    shared_suffix_count,
                    parent_id,
                    synthetic_groups,
                )
            elif shared_prefix_count > 0:
                self._wrap_with_prefix_group(
                    path_children,
                    split_labels,
                    shared_prefix_count,
                    parent_id,
                    synthetic_groups,
                )

        if synthetic_groups:
            all_indicators = indicators + synthetic_groups
            all_indicators.sort(key=lambda x: x.get("order", 0))
            for i, ind in enumerate(all_indicators):
                ind["order"] = i + 1
            return self._create_synthetic_groups_for_shared_prefixes(all_indicators)

        return indicators

    @staticmethod
    def _wrap_with_suffix_groups(
        path_children: list[dict],
        split_labels: list[list[str]],
        shared_suffix_count: int,
        parent_id: str | None,
        synthetic_groups: list[dict],
    ) -> None:
        """Build nested synthetic groups from a shared label suffix."""
        suffix_parts = split_labels[0][-shared_suffix_count:]
        suffix_parts_reversed = list(reversed(suffix_parts))
        first_child_order = min(c.get("order", 0) for c in path_children)
        first_child_depth = path_children[0].get("depth", 0)

        current_parent_id = parent_id
        current_depth = first_child_depth
        innermost_synthetic_id: str | None = None

        for i, suffix_part in enumerate(suffix_parts_reversed):
            synthetic_id = (
                f"_SYNTH_{current_parent_id}_"
                f"{re.sub(r'[^a-zA-Z0-9]', '_', suffix_part[:30])}_{i}"
            )
            synthetic_groups.append(
                {
                    "id": synthetic_id,
                    "indicator_code": None,
                    "label": suffix_part,
                    "description": "",
                    "order": first_child_order - 0.5 + (i * 0.01),
                    "level": current_depth,
                    "depth": current_depth,
                    "parent_id": current_parent_id,
                    "is_group": True,
                    "code_urn": None,
                    "dimension_id": None,
                    "series_id": None,
                }
            )
            current_parent_id = synthetic_id
            current_depth += 1
            innermost_synthetic_id = synthetic_id

        for child in path_children:
            child_parts = child["label"].split(", ")
            remaining = child_parts[:-shared_suffix_count]
            if remaining:
                child["label"] = ", ".join(remaining)
            child["parent_id"] = innermost_synthetic_id
            child["depth"] = first_child_depth + 1

    @staticmethod
    def _wrap_with_prefix_group(
        path_children: list[dict],
        split_labels: list[list[str]],
        shared_prefix_count: int,
        parent_id: str | None,
        synthetic_groups: list[dict],
    ) -> None:
        """Build a single synthetic group from a shared label prefix."""
        shared_prefix = ", ".join(split_labels[0][:shared_prefix_count])
        synthetic_id = (
            f"_SYNTH_{parent_id}_{re.sub(r'[^a-zA-Z0-9]', '_', shared_prefix[:30])}"
        )
        first_child_order = min(c.get("order", 0) for c in path_children)
        first_child_depth = path_children[0].get("depth", 0)
        synthetic_groups.append(
            {
                "id": synthetic_id,
                "indicator_code": None,
                "label": shared_prefix,
                "description": "",
                "order": first_child_order - 0.5,
                "level": first_child_depth,
                "depth": first_child_depth,
                "parent_id": parent_id,
                "is_group": True,
                "code_urn": None,
                "dimension_id": None,
                "series_id": None,
            }
        )
        for child in path_children:
            child_parts = child["label"].split(", ")
            remaining = child_parts[shared_prefix_count:]
            if remaining:
                child["label"] = ", ".join(remaining)
            child["parent_id"] = synthetic_id
            child["depth"] = first_child_depth + 1

    def list_all_dataflow_tables(self: _MixinBase) -> dict[str, list[dict]]:
        """Map curated dataflow ids to their validated presentation tables."""
        from openbb_imf.utils.constants import PRESENTATION_TABLES

        result: dict[str, list[dict]] = {}
        for friendly_name, table_spec in PRESENTATION_TABLES.items():
            parts = table_spec.split("::")
            if len(parts) != 2:
                continue
            dataflow_id, table_id = parts
            if dataflow_id not in self.dataflows:
                continue
            try:
                all_hierarchies = self.get_dataflow_hierarchies(dataflow_id)
            except Exception:  # noqa: BLE001
                continue
            matching = next(
                (h for h in all_hierarchies if h.get("id") == table_id), None
            )
            if not matching:
                continue
            enriched = matching.copy()
            enriched["friendly_name"] = friendly_name
            enriched["dataflow_id"] = dataflow_id
            result.setdefault(dataflow_id, []).append(enriched)
        return result


def _is_irfcl_path_label(label: str) -> bool:
    """Return True if ``label`` contains an IRFCL path-pattern phrase."""
    return any(p.lower() in label.lower() for p in _IRFCL_PATH_PATTERNS)


def _hierarchy_overlaps_dataflow(
    hier_obj: dict, available_indicator_values: set[str]
) -> bool:
    """Return True if the hierarchy references at least one dataflow code."""
    hier_codes_raw = hier_obj.get("hierarchicalCodes", [])
    hier_code_values: set[str] = set()

    def _extract(codes_list: list) -> None:
        for c in codes_list:
            code_urn = c.get("code", "")
            if code_urn and "INDICATOR" in code_urn and "." in code_urn:
                actual_code = code_urn.rsplit(".", 1)[-1]
                if actual_code:
                    hier_code_values.add(actual_code)
            nested = c.get("hierarchicalCodes", [])
            if nested:
                _extract(nested)

    _extract(hier_codes_raw)
    if not hier_code_values:
        return True
    if hier_code_values & available_indicator_values:
        return True
    return any(
        avail.startswith(hier)
        for hier in hier_code_values
        for avail in available_indicator_values
    )


def _derive_node_label(
    *,
    codelist_id_for_code: str | None,
    full_label: str,
    parent_full_label: str | None,
    ancestor_labels: list[str],
) -> str:
    """Strip ancestor-redundant prefixes from a path-style codelist label."""
    label = full_label or ""
    is_path_style = codelist_id_for_code and (
        "_INDICATOR_PUB" in codelist_id_for_code
        or codelist_id_for_code == "CL_DIP_INDICATOR"
    )

    if is_path_style:
        if codelist_id_for_code == "CL_DIP_INDICATOR" and ", " in full_label:
            parts = full_label.split(", ")
            if len(parts) > 1 and (
                parts[0].startswith("Inward") or parts[0].startswith("Outward")
            ):
                return ", ".join(parts[1:])

        if parent_full_label and full_label.startswith(parent_full_label):
            relative = full_label[len(parent_full_label) :].lstrip(", :")
            if relative:
                return relative
            if ", " in full_label or ": " in full_label:
                parts = re.split(r", |: ", full_label)
                return parts[-1] if parts else full_label
            return label

        if ancestor_labels and (", " in full_label or ": " in full_label):
            return _strip_known_ancestors(
                codelist_id_for_code, full_label, ancestor_labels
            )

        if ", " in full_label:
            parts = full_label.split(", ")
            return parts[-1] if parts else full_label

    elif (
        parent_full_label
        and ", " in full_label
        and full_label.startswith(parent_full_label)
    ):
        return full_label.rsplit(", ", 1)[-1]

    return label


def _strip_known_ancestors(
    codelist_id_for_code: str | None,
    full_label: str,
    ancestor_labels: list[str],
) -> str:
    """Remove label parts that match normalised ancestor labels."""

    def normalize(s: str) -> str:
        return re.sub(r"[^a-z0-9]", "", s.lower())

    def split(lbl: str) -> list[str]:
        out: list[str] = []
        for p in lbl.split(", "):
            if ":" in p:
                out.extend(sp.strip() for sp in p.split(":") if sp.strip())
            else:
                out.append(p)
        return out

    all_ancestor_parts: list[str] = []
    for ancestor in ancestor_labels:
        all_ancestor_parts.extend(split(ancestor))
    ancestor_normalised = {normalize(p) for p in all_ancestor_parts}

    child_parts = split(full_label)
    new_parts: list[str] = []
    for part in child_parts:
        part_norm = normalize(part)
        if part_norm in ancestor_normalised:
            continue
        is_in_ancestor = False
        for pn in ancestor_normalised:
            if pn.startswith("total") and pn[5:] == part_norm:
                is_in_ancestor = True
                break
            if len(pn) >= 6 and pn in part_norm:
                is_in_ancestor = True
                break
            if len(part_norm) >= 15 and len(pn) >= 15:
                shorter, longer = (
                    (part_norm, pn) if len(part_norm) <= len(pn) else (pn, part_norm)
                )
                if shorter in longer or (
                    len(shorter) > 30
                    and any(
                        shorter[i : i + 30] in longer for i in range(len(shorter) - 30)
                    )
                ):
                    is_in_ancestor = True
                    break
        if not is_in_ancestor:
            new_parts.append(part)

    if not new_parts:
        return child_parts[-1] if child_parts else full_label
    if codelist_id_for_code and "IRFCL" in codelist_id_for_code and len(new_parts) >= 3:
        return ", ".join(new_parts)
    return (
        ", ".join(new_parts)
        if new_parts
        else (child_parts[-1] if child_parts else full_label)
    )


def _build_series_id(
    *,
    agency_clean: str,
    dataflow_id: str,
    current_dimension_codes: dict[str, str],
    indicator_dimension_order: dict[str, int],
    parent_codes: list[str],
    indicator_code: str,
) -> str:
    """Compose ``<agency>_<dataflow>_<dim_codes>``, ordered by dimension position."""
    ordered_dims = sorted(
        [
            (dim_id, indicator_dimension_order[dim_id])
            for dim_id in current_dimension_codes
            if dim_id in indicator_dimension_order
            and current_dimension_codes.get(dim_id)
        ],
        key=lambda item: item[1],
    )
    ordered_codes = [current_dimension_codes[dim_id] for dim_id, _ in ordered_dims]
    unordered_dims = sorted(
        dim_id
        for dim_id in current_dimension_codes
        if dim_id not in indicator_dimension_order
        and current_dimension_codes.get(dim_id)
    )
    ordered_codes.extend(current_dimension_codes[dim_id] for dim_id in unordered_dims)

    if ordered_codes:
        return f"{agency_clean}_{dataflow_id}_{'_'.join(ordered_codes)}"
    fallback_codes = parent_codes + [indicator_code]
    return f"{agency_clean}_{dataflow_id}_{'_'.join(fallback_codes)}"
