"""Public API mixin: listing, table map, dimension info for OecdMetadata."""

import re

from openbb_oecd.utils.metadata._constants import (
    _TABLE_GROUP_CANDIDATES,
)
from openbb_oecd.utils.metadata._typing import _MixinBase


class PublicApiMixin(_MixinBase):
    """Public dataflow listing, table map, dimension info methods."""

    def list_dataflows(self, topic: str | None = None) -> list[dict]:
        """Return OECD dataflows as [{label, value, topic, subtopic, all_subtopics}, ...]."""
        self._ensure_dataflows()
        self._ensure_taxonomy()

        topic_upper = topic.upper() if topic else ""

        result: list[dict] = []
        for full_id, v in self.dataflows.items():
            cats = self._df_to_categories.get(full_id, [])

            primary_topic = ""
            primary_subtopic = ""
            all_subtopics: list[str] = []

            if cats:
                for cat_path in cats:
                    parts = cat_path.split(".")
                    t = parts[0] if parts else ""
                    s = parts[1] if len(parts) > 1 else ""
                    if not primary_topic:
                        primary_topic = t
                    if topic_upper:
                        if t == topic_upper and s:
                            all_subtopics.append(s)
                            if not primary_subtopic:
                                primary_subtopic = s
                    else:
                        if s and not primary_subtopic:
                            primary_subtopic = s
                        if s:
                            all_subtopics.append(s)

            if topic_upper and not any(c.split(".")[0] == topic_upper for c in cats):
                continue

            all_subtopics = sorted(set(all_subtopics))

            result.append(
                {
                    "label": v["name"],
                    "value": full_id,
                    "topic": topic_upper if topic_upper else primary_topic,
                    "topic_name": self._category_names.get(
                        topic_upper or primary_topic, ""
                    ),
                    "subtopic": primary_subtopic,
                    "subtopic_name": (
                        self._category_names.get(
                            f"{topic_upper or primary_topic}.{primary_subtopic}", ""
                        )
                        if primary_subtopic
                        else ""
                    ),
                    "all_subtopics": all_subtopics,
                }
            )

        return sorted(result, key=lambda d: d["value"])

    def list_topics(self) -> list[dict]:
        """Return the OECD topic taxonomy as a hierarchical tree."""
        self._ensure_taxonomy()

        def _annotate(node: dict) -> dict:
            path = node["path"]
            direct = len(self._category_to_dfs.get(path, []))
            children = [_annotate(c) for c in node.get("children", [])]
            children = [c for c in children if c["dataflow_count"] > 0]
            child_total = sum(c["dataflow_count"] for c in children)

            return {
                "id": node["id"],
                "name": node["name"],
                "dataflow_count": direct + child_total,
                "subtopics": children,
            }

        return [_annotate(t) for t in self._taxonomy_tree]

    def list_dataflows_by_topic(self) -> list[dict]:
        """Return all dataflows organised by topic -> subtopic hierarchy."""
        self._ensure_dataflows()
        self._ensure_taxonomy()

        def _df_entry(full_id: str) -> dict:
            v = self.dataflows.get(full_id, {})

            return {"label": v.get("name", full_id), "value": full_id}

        def _build(node: dict) -> dict:
            path = node["path"]
            dfs = [
                _df_entry(fid) for fid in sorted(self._category_to_dfs.get(path, []))
            ]
            children = [_build(c) for c in node.get("children", [])]
            children = [c for c in children if c["dataflows"] or c["subtopics"]]

            return {
                "id": node["id"],
                "name": node["name"],
                "dataflows": dfs,
                "subtopics": children,
            }

        return [_build(t) for t in self._taxonomy_tree]

    def get_dataflow_info(self, dataflow_id: str) -> dict:
        """Return metadata dict for a single dataflow."""
        full_id = self._resolve_dataflow_id(dataflow_id)
        return self.dataflows[full_id]

    _COUNTRY_SUFFIX_RE = re.compile(r"^_?([A-Z]{2,3})$")

    def _detect_country_families(self) -> dict[str, dict]:
        """Detect dataflow families that are per-country splits of the same table."""
        from collections import defaultdict

        dsd_groups: dict[str, list[str]] = defaultdict(list)

        for full_id in self.dataflows:
            dsd = full_id.split("@")[0] if "@" in full_id else full_id
            dsd_groups[dsd].append(full_id)

        family_map: dict[str, dict] = {}

        for dsd, fids in dsd_groups.items():
            if len(fids) < 5:
                continue

            shorts = {
                fid: self.dataflows[fid].get("short_id", fid.split("@")[-1])
                for fid in fids
            }
            # Manual shortest-string selection: ``min(iter, key=len)``
            # collapses to ``Sized`` under ty's overload resolution
            # because ``len`` is typed as ``Callable[[Sized], int]``.
            # An explicit loop keeps the iterable's element type (``str``).
            short_values = list(shorts.values())
            prefix = short_values[0]
            for s in short_values[1:]:
                if len(s) < len(prefix):
                    prefix = s

            for sid in shorts.values():
                while prefix and not sid.startswith(prefix):
                    prefix = prefix[:-1]

            if len(prefix) < 4:
                continue

            suffixes = {fid: sid[len(prefix) :] for fid, sid in shorts.items()}
            country_members = {
                fid
                for fid, sfx in suffixes.items()
                if self._COUNTRY_SUFFIX_RE.match(sfx)
            }

            if len(country_members) / len(fids) < 0.7:
                continue

            representative = None

            for fid, sfx in suffixes.items():
                if sfx.upper() in ("ALL", "_ALL"):
                    representative = fid
                    break

            if not representative:
                for fid, sfx in suffixes.items():
                    if sfx == "":
                        representative = fid
                        break

            if not representative:
                non_country = [fid for fid in fids if fid not in country_members]
                representative = (
                    non_country[0]
                    if non_country
                    else min(fids, key=lambda f: shorts[f])  # noqa: B023
                )

            rep_name = self.dataflows[representative].get("name", "")
            info = {
                "dsd": dsd,
                "representative": representative,
                "rep_short_id": shorts.get(
                    representative,
                    representative.split("@")[-1],
                ),
                "family_name": rep_name,
                "member_count": len(fids),
                "members": sorted(fids),
            }

            for fid in fids:
                family_map[fid] = info

        return family_map

    def _detect_section_families(self) -> dict[str, str]:
        """Map section dataflows to their root within the same DSD family.

        Returns a dict ``{section_full_id: root_full_id}`` for every
        dataflow whose short_id is a strict extension of another
        dataflow in the same DSD (e.g. ``DF_TABLE1_EXPENDITURE`` is a
        section of ``DF_TABLE1``).  Root dataflows are **not** included
        as keys — only subordinate sections.
        """
        from collections import defaultdict

        dsd_groups: dict[str, list[str]] = defaultdict(list)
        for full_id in self.dataflows:
            dsd = full_id.split("@")[0] if "@" in full_id else full_id
            dsd_groups[dsd].append(full_id)

        section_map: dict[str, str] = {}

        for fids in dsd_groups.values():
            if len(fids) < 2:
                continue

            shorts = {
                fid: self.dataflows[fid].get("short_id", fid.split("@")[-1])
                for fid in fids
            }
            sorted_fids = sorted(
                fids,
                key=lambda f, s=shorts: (len(s[f]), s[f]),  # type: ignore[misc]
            )

            roots: list[str] = []
            for fid in sorted_fids:
                sid = shorts[fid]
                parent = None
                for r in roots:
                    if sid.startswith(shorts[r] + "_"):
                        parent = r
                        break
                if parent is None:
                    roots.append(fid)
                else:
                    section_map[fid] = parent

        return section_map

    def table_map(self, *, include_empty: bool = False) -> list[dict]:
        """Return a flat, navigable map of every OECD presentation table."""
        self._ensure_dataflows()
        self._ensure_taxonomy()
        family_map = self._detect_country_families()
        section_map = self._detect_section_families()

        emitted: set[tuple[str, str]] = set()
        rows: list[dict] = []

        def _make_row(
            crumb: list[str],
            id_crumb: list[str],
            table_name: str,
            dataflow_id: str,
            short_id: str,
            countries: int,
        ) -> dict:
            return {
                "topic": crumb[0] if crumb else "",
                "topic_id": id_crumb[0] if id_crumb else "",
                "subtopic": crumb[1] if len(crumb) > 1 else "",
                "subtopic_id": id_crumb[1] if len(id_crumb) > 1 else "",
                "sub_subtopic": (" > ".join(crumb[2:]) if len(crumb) > 2 else ""),
                "path": " > ".join(crumb),
                "table": table_name,
                "dataflow_id": dataflow_id,
                "short_id": short_id,
                "countries": countries,
            }

        def _walk(
            nodes: list[dict],
            breadcrumb: list[str],
            id_breadcrumb: list[str],
        ) -> None:
            for node in nodes:
                crumb = breadcrumb + [node["name"]]
                ids = id_breadcrumb + [node["id"]]
                cat_path = node["path"]

                for fid in sorted(self._category_to_dfs.get(cat_path, [])):
                    entry = self.dataflows.get(fid)

                    if not entry:
                        continue

                    if fid in section_map:
                        continue

                    family = family_map.get(fid)

                    if family:
                        rep = family["representative"]
                        key = (cat_path, rep)

                        if key in emitted:
                            continue

                        emitted.add(key)
                        rows.append(
                            _make_row(
                                crumb,
                                ids,
                                family["family_name"],
                                rep,
                                family["rep_short_id"],
                                family["member_count"],
                            )
                        )
                    else:
                        rows.append(
                            _make_row(
                                crumb,
                                ids,
                                entry.get("name", fid),
                                fid,
                                entry.get("short_id", fid.split("@")[-1]),
                                0,
                            )
                        )

                _walk(node.get("children", []), crumb, ids)

        _walk(self._taxonomy_tree, [], [])

        if include_empty:
            categorised = set(self._df_to_categories.keys())

            for fid, entry in sorted(self.dataflows.items()):
                if (
                    fid not in categorised
                    and fid not in family_map
                    and fid not in section_map
                ):
                    rows.append(
                        {
                            "topic": "(Uncategorised)",
                            "topic_id": "",
                            "subtopic": "",
                            "subtopic_id": "",
                            "sub_subtopic": "",
                            "path": "(Uncategorised)",
                            "table": entry.get("name", fid),
                            "dataflow_id": fid,
                            "short_id": entry.get("short_id", fid.split("@")[-1]),
                            "countries": 0,
                        }
                    )

        rows.sort(key=lambda r: (r["path"], r["table"]))

        return rows

    def find_tables(self, query: str) -> list[dict]:
        """Search the table map by keyword."""
        full_map = self.table_map()
        tokens = [t.lower() for t in query.strip().split() if t.strip()]

        if not tokens:
            return full_map

        def _tok(token: str, text: str) -> bool:
            return any(alt in text for alt in token.split("|"))

        matched: dict[str, dict] = {}

        for row in full_map:
            text = " ".join(
                [
                    row["topic"],
                    row["subtopic"],
                    row["sub_subtopic"],
                    row["path"],
                    row["table"],
                    row["dataflow_id"],
                    row["short_id"],
                ]
            ).lower()

            if all(_tok(t, text) for t in tokens):
                fid = row["dataflow_id"]
                prev = matched.get(fid)

                if prev is None or len(row["path"]) > len(prev["path"]):
                    matched[fid] = row

        results = sorted(matched.values(), key=lambda r: (r["path"], r["table"]))

        return results

    def print_table_map(
        self,
        query: str | None = None,
        *,
        topic: str | None = None,
    ) -> str:
        """Return a human-readable string of the table map."""
        from collections import OrderedDict

        rows = self.find_tables(query) if query else self.table_map()

        if topic:
            t = topic.lower()
            rows = [
                r for r in rows if t in r["topic"].lower() or t in r["path"].lower()
            ]

        if not rows:
            return "(no matching tables)"

        groups: OrderedDict[str, list[dict]] = OrderedDict()

        for row in rows:
            groups.setdefault(row["path"], []).append(row)

        lines: list[str] = []
        current_topic = ""

        for group_rows in groups.values():
            top = group_rows[0]["topic"]

            if top != current_topic:
                if current_topic:
                    lines.append("")

                lines.append(f"{'=' * 60}")
                lines.append(f" {top}")
                lines.append(f"{'=' * 60}")
                current_topic = top

            sub_parts = [group_rows[0]["subtopic"]]

            if group_rows[0]["sub_subtopic"]:
                sub_parts.append(group_rows[0]["sub_subtopic"])

            sub_label = " > ".join(p for p in sub_parts if p)

            if sub_label:
                lines.append(f"  [{sub_label}]")

            for row in group_rows:
                ccount = row.get("countries", 0)
                suffix = f"  ({ccount} countries)" if ccount else ""
                lines.append(f"    {row['table']:<60s}  {row['short_id']}{suffix}")

        return "\n".join(lines)

    def get_dimension_order(self, dataflow_id: str) -> list[str]:
        """Return the DSD-defined dimension IDs in position order."""
        full_id = self._resolve_dataflow_id(dataflow_id)
        self._ensure_structure(full_id)
        dsd = self.datastructures.get(full_id, {})

        return [d["id"] for d in dsd.get("dimensions", []) if d["id"] != "TIME_PERIOD"]

    def get_dataflow_parameters(self, dataflow_id: str) -> dict[str, list[dict]]:
        """Return queryable parameters for *dataflow_id*."""
        if dataflow_id in self._dataflow_parameters_cache:
            return self._dataflow_parameters_cache[dataflow_id]

        full_id = self._resolve_dataflow_id(dataflow_id)
        if full_id in self._dataflow_parameters_cache:
            return self._dataflow_parameters_cache[full_id]

        self._ensure_structure(full_id)
        dsd = self.datastructures.get(full_id, {})
        params: dict[str, list[dict]] = {}

        for dim in dsd.get("dimensions", []):
            dim_id = dim["id"]

            if dim_id == "TIME_PERIOD":
                continue

            cl_id = dim.get("codelist_id", "")

            if cl_id:
                cl = self._get_codelist(cl_id, dataflow_id)
                params[dim_id] = [
                    {"label": label, "value": code}
                    for code, label in sorted(cl.items())
                ]
            else:
                params[dim_id] = []

        if params:
            self._dataflow_parameters_cache[dataflow_id] = params
            self._dataflow_parameters_cache[full_id] = params

        return params

    def get_dimension_info(self, dataflow_id: str) -> list[dict]:
        """Return rich metadata for every dimension in a dataflow."""
        full_id = self._resolve_dataflow_id(dataflow_id)
        self._ensure_structure(full_id)
        dsd = self.datastructures.get(full_id, {})
        constraints = self._dataflow_constraints.get(full_id, {})
        params = self.get_dataflow_parameters(full_id)

        result: list[dict] = []

        for dim in dsd.get("dimensions", []):
            dim_id = dim["id"]

            if dim_id == "TIME_PERIOD":
                continue

            cl_id = dim.get("codelist_id", "")
            codelist = self._get_codelist(cl_id, dataflow_id) if cl_id else {}
            cl_size = len(codelist)
            parents = self._codelist_parents.get(cl_id, {})

            if not parents:
                m_pref = self._CL_KEY_RE.match(cl_id) if cl_id else None

                if m_pref:
                    prefix = f"{m_pref.group(1)}:{m_pref.group(2)}("
                    for pk, pv in self._codelist_parents.items():
                        if pk.startswith(prefix) and pv:
                            parents = pv
                            break

            descriptions = self._codelist_descriptions.get(cl_id, {})

            if not descriptions:
                m_pref = self._CL_KEY_RE.match(cl_id) if cl_id else None

                if m_pref:
                    prefix = f"{m_pref.group(1)}:{m_pref.group(2)}("

                    for dk, dv in self._codelist_descriptions.items():
                        if dk.startswith(prefix) and dv:
                            descriptions = dv
                            break

            entries = params.get(dim_id, [])

            if dim_id in constraints:
                allowed = set(constraints[dim_id])
                constrained_entries = [e for e in entries if e["value"] in allowed]

                if not constrained_entries and allowed:
                    constrained_entries = [
                        {"value": code, "label": codelist.get(code, code)}
                        for code in sorted(allowed)
                    ]
            else:
                constrained_entries = entries

            values = []

            for e in constrained_entries:
                v: dict = {
                    "value": e["value"],
                    "label": e["label"],
                    "description": descriptions.get(e["value"], e["label"]),
                }

                if e["value"] in parents:
                    v["parent"] = parents[e["value"]]

                values.append(v)

            result.append(
                {
                    "id": dim_id,
                    "position": dim["position"],
                    "name": dim.get("name", dim_id),
                    "codelist_id": cl_id,
                    "total_codes": cl_size,
                    "constrained_codes": len(constrained_entries),
                    "has_hierarchy": bool(parents),
                    "values": values,
                }
            )

        return result

    def get_table_groups(self, dataflow_id: str) -> list[dict]:
        """Return table groups within a dataflow."""
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

        dim_id = table_dim["id"]
        cl_id = table_dim.get("codelist_id", "")
        params = self.get_dataflow_parameters(full_id)
        entries = params.get(dim_id, [])
        constraints = self._dataflow_constraints.get(full_id, {})

        if dim_id in constraints:
            allowed = set(constraints[dim_id])
            entries = [e for e in entries if e["value"] in allowed]

        descriptions = self._codelist_descriptions.get(cl_id, {})

        return [
            {
                "value": e["value"],
                "label": e["label"],
                "description": descriptions.get(e["value"], e["label"]),
            }
            for e in entries
        ]

    def get_constrained_values(self, dataflow_id: str) -> dict[str, list[dict]]:
        """Return dimension values filtered by embedded content constraints."""
        full_id = self._resolve_dataflow_id(dataflow_id)
        self._ensure_structure(full_id)
        constraints = self._dataflow_constraints.get(full_id, {})
        params = self.get_dataflow_parameters(full_id)

        result: dict[str, list[dict]] = {}
        dsd = self.datastructures.get(full_id, {})

        for dim in dsd.get("dimensions", []):
            dim_id = dim["id"]

            if dim_id == "TIME_PERIOD":
                continue

            cl_id = dim.get("codelist_id", "")
            descriptions = self._codelist_descriptions.get(cl_id, {})
            entries = params.get(dim_id, [])

            if dim_id in constraints:
                allowed = set(constraints[dim_id])
                entries = [e for e in entries if e["value"] in allowed]

            result[dim_id] = [
                {
                    "value": e["value"],
                    "label": e["label"],
                    "description": descriptions.get(e["value"], e["label"]),
                }
                for e in entries
            ]

        self._save_cache()
        return result
