"""OECD Table Builder — hierarchical table data fetching with validation."""

# pylint: disable=C0302,R0912,R0913,R0914,R0915,R1702,W0212,W0640

from __future__ import annotations

import warnings
from typing import TYPE_CHECKING, Any

from openbb_core.app.model.abstract.warning import OpenBBWarning
from openbb_core.provider.utils.errors import OpenBBError

if TYPE_CHECKING:
    from openbb_oecd.utils.metadata import OecdMetadata
    from openbb_oecd.utils.query_builder import OecdQueryBuilder


def _calculate_depth(
    node: dict,
    indicator_by_code: dict[str, dict],
    visited: set | None = None,
) -> int:
    """Trace the parent chain to find tree depth (0 for roots)."""
    if visited is None:
        visited = set()
    code = node.get("code", "")
    if not code or code in visited:
        return 0
    visited.add(code)
    parent = node.get("parent")
    if parent is None or parent not in indicator_by_code:
        return 0
    return 1 + _calculate_depth(indicator_by_code[parent], indicator_by_code, visited)


class OecdTableBuilder:
    """Fetch and organise OECD data according to hierarchical table structures.

    Mirrors IMF's ``ImfTableBuilder`` interface while using OECD-specific
    metadata (``OecdMetadata``) and data access (``OecdQueryBuilder``).
    """

    def __init__(
        self,
        metadata: OecdMetadata | None = None,
        query_builder: OecdQueryBuilder | None = None,
    ) -> None:
        # Lazy imports to avoid circular dependencies.
        from openbb_oecd.utils.metadata import OecdMetadata as _Meta
        from openbb_oecd.utils.query_builder import OecdQueryBuilder as _QB

        self.metadata: _Meta = metadata or _Meta()
        self.query_builder: _QB = query_builder or _QB()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_table(  # noqa: PLR0912
        self,
        dataflow: str | None = None,
        table_id: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        limit: int | None = None,
        depth: int | None = None,
        parent_id: str | None = None,
        indicators: list[str] | str | None = None,
        country: str | None = None,
        frequency: str | None = None,
        use_labels: bool = True,
        **kwargs: Any,
    ) -> dict:
        """Fetch hierarchical table data.

        Parameters
        ----------
        dataflow : str | None
            Dataflow short ID (e.g. ``"DF_EO"``).  Can be omitted when
            *table_id* uses the ``"DATAFLOW::TABLE"`` format.
        table_id : str | None
            ``TABLE_IDENTIFIER`` value (e.g. ``"T101"``), or combined
            ``"DF_EO::T101"`` format.  When ``None``, auto-selects the
            first available table for the dataflow (if there is only one).
        start_date, end_date : str | None
            Date bounds (ISO or SDMX period like ``"2024-Q3"``).
        limit : int | None
            ``lastNObservations`` (limit time series depth).
        depth : int | None
            Restrict hierarchy to items at this depth (``0`` = top level).
        parent_id : str | None
            Restrict to children of this parent indicator code.
        indicators : list | str | None
            Restrict to specific indicator codes.
        country : str | None
            Country name / ISO code (``"AUT"``).  Multi-select:
            ``"AUT,DEU"`` or ``"austria,germany"``.
        frequency : str | None
            Frequency code (``"Q"``, ``"A"``, ``"M"``).
        use_labels : bool
            Use human-readable labels for dimension columns (default).
        **kwargs
            Extra dimension filters (e.g. ``MEASURE="CPI"``).

        Returns
        -------
        dict
            ``{table_metadata, structure, data, series_metadata}``
        """
        # pylint: disable=import-outside-toplevel
        from openbb_oecd.utils.metadata import (
            _NON_INDICATOR_DIMENSIONS,
            _TABLE_GROUP_CANDIDATES,
        )

        # ---- Parse combined "DATAFLOW::TABLE" format ----
        if table_id and "::" in table_id:
            parsed_df, parsed_tid = table_id.split("::", 1)
            if dataflow is not None and dataflow != parsed_df:
                raise OpenBBError(
                    f"Dataflow mismatch: provided '{dataflow}' but table_id specifies '{parsed_df}'."
                )
            dataflow = parsed_df
            table_id = parsed_tid
        elif table_id and dataflow is None:
            # Bare dataflow ID (e.g. "DF_FDI_FLOW_AGGR") — treat as
            # dataflow with no specific table selection.
            dataflow = table_id
            table_id = None

        if dataflow is None:
            raise OpenBBError(
                "dataflow is required.  Provide it directly or use table_id in 'DATAFLOW::TABLE' format."
            )

        # ---- Resolve dataflow + ensure structure loaded ----
        full_id = self.metadata._resolve_dataflow_id(dataflow)
        self.metadata._ensure_structure(full_id)
        dsd = self.metadata.datastructures.get(full_id, {})
        dims = sorted(dsd.get("dimensions", []), key=lambda d: d["position"])

        # ---- Auto-select table_id if not given ----
        if table_id is None:
            available = self.metadata.get_dataflow_hierarchies(dataflow)
            if len(available) == 1:
                table_id = available[0]["id"]
            elif len(available) == 0:
                # No TABLE_IDENTIFIER — treat the whole dataflow as one table.
                table_id = None
            # else: multiple tables exist but caller didn't choose → we'll
            # fetch without a TABLE_IDENTIFIER filter (entire dataflow).

        # ---- Build hierarchy structure ----
        table_structure = self.metadata.get_dataflow_table_structure(
            dataflow, table_id or ""
        )
        all_hierarchy_entries: list[dict] = table_structure.get("indicators", [])

        # ---- Filter by user request ----
        filtered = list(all_hierarchy_entries)

        if indicators is not None:
            ind_set = {indicators} if isinstance(indicators, str) else set(indicators)
            filtered = [e for e in filtered if e["code"] in ind_set]
        elif parent_id is not None:
            filtered = [e for e in filtered if e.get("parent") == parent_id]
        elif depth is not None:
            filtered = [e for e in filtered if e.get("level") == depth]

        if not filtered:
            raise OpenBBError(
                f"No indicators match filters (depth={depth}, "
                f"parent_id={parent_id}, indicators={indicators}).  "
                f"Total in hierarchy: {len(all_hierarchy_entries)}"
            )

        # ---- Identify the indicator dimension ----
        indicator_dim = self.metadata._find_indicator_dimension(full_id)
        if not indicator_dim:
            # Fallback: pick the dimension with the most unique codes.
            best_dim, best_count = None, 0
            for dim in dims:
                if dim["id"] == "TIME_PERIOD":
                    continue
                cl = self.metadata.codelists.get(dim.get("codelist_id", ""), {})
                if len(cl) > best_count:
                    best_count = len(cl)
                    best_dim = dim["id"]
            indicator_dim = best_dim or "MEASURE"

        # ---- Map hierarchy codes to the indicator dimension ----
        hierarchy_codes = [e["code"] for e in filtered if e.get("code")]

        # ---- Resolve country / frequency ----
        country_dim = self.query_builder.get_country_dimension(dataflow)
        if country and country_dim and country_dim not in kwargs:
            codes = self.metadata.resolve_country_codes(
                dataflow, country.replace("+", ",")
            )
            if codes:
                kwargs[country_dim] = "+".join(codes)

        if frequency:
            freq_dim = self.query_builder.get_frequency_dimension(dataflow)
            if freq_dim and freq_dim not in kwargs:
                kwargs[freq_dim] = frequency.upper()

        # ---- Set table-grouping dimension if present ----
        # TABLE_IDENTIFIER is the standard; CHAPTER and others act as
        # alternatives (see _TABLE_GROUP_CANDIDATES in metadata.py).
        table_group_dim: str | None = None  # which dim carries the table_id
        if table_id:
            for candidate in _TABLE_GROUP_CANDIDATES:
                dim_present = any(d["id"] == candidate for d in dims)
                if dim_present and candidate not in kwargs:
                    kwargs[candidate] = table_id
                    table_group_dim = candidate
                    break

        # ---- Build indicator post-filter ----
        # For TABLE_IDENTIFIER-based dataflows the indicator codelist is
        # partitioned per table, so the hierarchy codes are accurate.
        # For dimension-based grouping (e.g. CHAPTER) the hierarchy
        # covers the *entire* dataflow — using it as a post-filter would
        # wrongly discard indicators.  In that case the API query already
        # constrains the results via the pinned dimension.
        codes_for_post_filter: set[str] | None = None
        if hierarchy_codes and (
            table_group_dim is None or table_group_dim == "TABLE_IDENTIFIER"
        ):
            codes_for_post_filter = set(hierarchy_codes)

        # ---- Pin dimensions ----
        # Metadata dims are parameters (like country / frequency) — they
        # describe HOW the data is measured, not WHAT is being measured.
        # Pin them in the request using a preference list so we only
        # request the data we actually want.

        _SKIP_DIMS = {
            "TIME_PERIOD",
            indicator_dim,
            *(k for k in kwargs),  # Already pinned by caller / above logic
        }

        # Structural dims — pin to neutral/aggregate value.
        _STRUCTURAL_PIN_PREFERENCES: dict[str, list[str]] = {
            "SECTOR": ["S1", "_Z", "_T"],
            "COUNTERPART_SECTOR": ["S1"],
            "INSTR_ASSET": ["_Z"],
        }
        _NEUTRAL_CODES = {"_Z", "_T"}

        # Country-like dimensions (for secondary country pin logic).
        _COUNTRY_DIMS = {
            "REF_AREA",
            "COUNTERPART_AREA",
            "JURISDICTION",
            "COUNTRY",
            "AREA",
        }

        # Metadata / measurement parameter dims — pin to preferred value.
        _METADATA_PIN_PREFERENCES: dict[str, list[str]] = {
            "ADJUSTMENT": ["Y", "N"],
            "UNIT_MEASURE": ["XDC", "USD_EXC", "USD_PPP", "PB", "PS"],
            "PRICE_BASE": ["V", "_Z"],
            "TRANSFORMATION": ["N", "LA"],
        }

        try:
            avail = self.metadata.fetch_availability(dataflow, pinned=kwargs)

            # Identify dimensions needing auto-selection.
            auto_dims: list[str] = []
            for dim_id, available_vals in avail.items():
                if dim_id in _SKIP_DIMS:
                    continue
                if codes_for_post_filter and (
                    set(available_vals) & codes_for_post_filter
                ):
                    continue
                auto_dims.append(dim_id)

            # First pass: pin single-value dimensions (unambiguous).
            for dim_id in auto_dims:
                vals = avail.get(dim_id, [])
                if len(vals) == 1:
                    kwargs[dim_id] = vals[0]

            # Second pass: progressively pin remaining dimensions,
            # re-fetching availability after each new pin so that
            # cross-dimension constraints are respected.
            remaining = [d for d in auto_dims if d not in kwargs]
            _refresh = bool(remaining)
            for dim_id in remaining:
                if _refresh:
                    avail = self.metadata.fetch_availability(dataflow, pinned=kwargs)
                    _refresh = False
                available_vals = avail.get(dim_id, [])
                if not available_vals:
                    continue
                _old_len = len(kwargs)
                if len(available_vals) == 1:
                    kwargs[dim_id] = available_vals[0]
                # Metadata parameter dims → pin to best available value.
                elif dim_id in _METADATA_PIN_PREFERENCES:
                    prefs = _METADATA_PIN_PREFERENCES[dim_id]
                    for pref in prefs:
                        if pref in available_vals:
                            kwargs[dim_id] = pref
                            break
                    else:
                        kwargs[dim_id] = available_vals[0]
                # Structural dims → pin to preferred aggregate value.
                elif dim_id in _STRUCTURAL_PIN_PREFERENCES:
                    prefs = _STRUCTURAL_PIN_PREFERENCES[dim_id]
                    if (
                        set(prefs) <= _NEUTRAL_CODES
                        and len(available_vals) > len(prefs) + 1
                    ):
                        pass  # data-carrying dimension — wildcard
                    else:
                        for pref in prefs:
                            if pref in available_vals:
                                kwargs[dim_id] = pref
                                break
                # ACTIVITY / EXPENDITURE may carry real series data.
                elif dim_id in ("ACTIVITY", "EXPENDITURE"):
                    pass
                # Secondary country dims (e.g. COUNTERPART_AREA) — pin
                # to aggregate / world value so queries don't explode.
                elif dim_id in _COUNTRY_DIMS and dim_id != country_dim:
                    for pref in ("W", "WLD", "_T", "_Z"):
                        if pref in available_vals:
                            kwargs[dim_id] = pref
                            break
                    else:
                        # No known aggregate — take first value.
                        kwargs[dim_id] = available_vals[0]
                if len(kwargs) > _old_len:
                    _refresh = True
        except Exception:  # noqa: BLE001
            avail = {}

        # ---- Validate constraints ----
        if kwargs or start_date or end_date:
            try:
                self.query_builder.validate_dimension_constraints(
                    dataflow,
                    start_date=start_date,
                    end_date=end_date,
                    **kwargs,
                )
            except ValueError:
                raise
            except Exception as exc:  # noqa: BLE001
                warnings.warn(
                    f"Constraint validation failed: {exc}",
                    OpenBBWarning,
                    stacklevel=2,
                )

        # ---- Fetch data ----
        raw = self.query_builder.fetch_data(
            dataflow=dataflow,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
            _skip_validation=True,
            **kwargs,
        )
        data_rows: list[dict] = raw.get("data", [])

        # Post-fetch filter to hierarchy codes.
        if codes_for_post_filter:
            data_rows = [
                row
                for row in data_rows
                if row.get(indicator_dim) in codes_for_post_filter
            ]

        # ---- Build hierarchy lookup maps ----
        indicator_by_code: dict[str, dict] = {}
        for entry in all_hierarchy_entries:
            code = entry.get("code")
            if code:
                indicator_by_code[code] = entry

        hierarchy_order_map: dict[str, dict] = {}
        for entry in all_hierarchy_entries:
            code = entry.get("code")
            if not code:
                continue
            depth_val = entry.get("level")
            if depth_val is None:
                depth_val = _calculate_depth(entry, indicator_by_code)
            hierarchy_order_map[code] = {
                "order": entry.get("order", 0),
                "level": depth_val,
                "parent": entry.get("parent"),
                "parent_code": entry.get("parent"),
                "label": entry.get("label", code),
                "children": entry.get("children", []),
            }

        # ---- Canonical root ordering ----
        # Ensure Current Account (CA) sorts before Capital Account (KA)
        # when both exist as root indicators.
        if "CA" in hierarchy_order_map and "KA" in hierarchy_order_map:
            _ca = hierarchy_order_map["CA"]
            _ka = hierarchy_order_map["KA"]
            if (
                _ca.get("parent") is None
                and _ka.get("parent") is None
                and _ca["order"] > _ka["order"]
            ):
                _ca["order"], _ka["order"] = _ka["order"], _ca["order"]

        # ---- Enrich data rows ----
        dim_ids = [d["id"] for d in dims if d["id"] != "TIME_PERIOD"]

        # Determine varying / fixed dimensions.
        # ACCOUNTING_ENTRY is handled specially as sub-hierarchy — never
        # treat it as a generic "varying dim" column.
        varying_dims: list[str] = []
        fixed_values: dict[str, dict[str, str]] = {}
        _has_acct_entry = any("ACCOUNTING_ENTRY" in r for r in data_rows)
        for did in dim_ids:
            unique = {row.get(did) for row in data_rows if did in row}
            unique.discard(None)
            if len(unique) > 1:
                if did == "ACCOUNTING_ENTRY" and _has_acct_entry:
                    continue  # handled as sub-hierarchy below
                varying_dims.append(did)
            elif unique:
                code = next(iter(unique))
                label = next(
                    (
                        row.get(f"{did}_label", code)
                        for row in data_rows
                        if f"{did}_label" in row
                    ),
                    code,
                )
                fixed_values[did] = {"code": code, "label": label or code}  # type: ignore

        # ---- Compound symbol treatment ----
        # Split varying dims into *content* dims (part of what is being
        # measured, e.g. EXPENDITURE, SECTOR) and *metadata* dims (how
        # it is measured, e.g. UNIT_MEASURE).  Content dims are folded
        # into a compound code + label; metadata dims remain as columns.
        _COUNTRY_DIMS = {
            "REF_AREA",
            "COUNTERPART_AREA",
            "JURISDICTION",
            "COUNTRY",
            "AREA",
        }
        _compound_dims: list[str] = []  # content-varying (join into code)
        _meta_varying: list[str] = []  # metadata-varying (keep as columns)
        for did in varying_dims:
            if (
                did == indicator_dim
                or did in _NON_INDICATOR_DIMENSIONS
                or did in _COUNTRY_DIMS
                or did in _TABLE_GROUP_CANDIDATES
            ):
                _meta_varying.append(did)
            else:
                _compound_dims.append(did)
        # Replace varying_dims with only the metadata-varying ones.
        varying_dims = _meta_varying

        # ACCOUNTING_ENTRY sort order: Balance/Net first (parent level),
        # then the breakdown entries grouped under the parent.
        _ACCT_SORT: dict[str, int] = {
            "B": 0,
            "N": 0,  # Balance / Net → indicator's own level
            "C": 1,
            "D": 2,  # Revenue / Expenditure
            "A": 1,
            "L": 2,  # Assets / Liabilities
        }
        _BN_ENTRIES = {"B", "N", ""}

        # ---- Build parent-grouped hierarchy ----
        # When a parent indicator has children AND their data contains
        # matching accounting entries (A/L or C/D), the parent's entries
        # become sub-parent rows with the children's entries nested under
        # them.  Example:
        #   Financial account (Balance)
        #     Assets (FA total)          ← sub-parent
        #       Direct investment        ← child's asset portion
        #       Portfolio investment
        #     Liabilities (FA total)     ← sub-parent
        #       Direct investment        ← child's liability portion

        if _has_acct_entry:
            from collections import defaultdict as _dd

            # (indicator_code, acct_entry) → [rows]
            _ind_acct: dict[tuple[str, str], list[dict]] = _dd(list)
            # indicator_code → set of acct entries
            _ind_accts: dict[str, set[str]] = _dd(set)
            for _r in data_rows:
                _c = _r.get(indicator_dim, "")
                _a = _r.get("ACCOUNTING_ENTRY", "")
                _ind_acct[(_c, _a)].append(_r)
                if _c:
                    _ind_accts[_c].add(_a)

            # Get a representative accounting-entry label from data rows.
            _acct_labels: dict[str, str] = {}
            for _r in data_rows:
                _a = _r.get("ACCOUNTING_ENTRY", "")
                if _a and _a not in _acct_labels:
                    _acct_labels[_a] = _r.get("ACCOUNTING_ENTRY_label", _a)

            all_rows: list[dict] = []
            _consumed: set[tuple[str, str]] = set()

            def _enrich_row(
                row: dict,
                order: int,
                level: int,
                asort: int,
                child_order: int,
                label: str,
                is_header: bool,
            ) -> None:
                row["order"] = order
                row["level"] = level
                row["_acct_sort"] = asort
                row["_child_order"] = child_order
                row["label"] = label
                row["is_category_header"] = is_header
                _info = hierarchy_order_map.get(row.get(indicator_dim, ""), {})
                row["parent_id"] = _info.get("parent")
                row["parent_code"] = _info.get("parent_code")
                all_rows.append(row)

            def _synthetic_header(
                code: str,
                order: int,
                level: int,
                asort: int,
                child_order: int,
                label: str,
            ) -> None:
                all_rows.append(
                    {
                        indicator_dim: code,
                        "order": order,
                        "level": level,
                        "_acct_sort": asort,
                        "_child_order": child_order,
                        "label": label,
                        "is_category_header": True,
                        "parent_id": hierarchy_order_map.get(code, {}).get("parent"),
                        "parent_code": hierarchy_order_map.get(code, {}).get(
                            "parent_code"
                        ),
                        "TIME_PERIOD": "",
                        "OBS_VALUE": None,
                    }
                )

            def _emit_indicator(  # noqa: PLR0912
                code: str,
                base_level: int,
                parent_order: int | None = None,
                acct_filter: str | None = None,
                child_order: int = 0,
            ) -> None:
                """Recursively emit enriched rows for *code*."""
                info = hierarchy_order_map.get(code)
                if not info:
                    return
                order = parent_order if parent_order is not None else info["order"]
                children = [
                    c for c in info.get("children", []) if c in hierarchy_order_map
                ]
                accts = _ind_accts.get(code, set())

                # --- Filtered emit (child under parent's acct group) ---
                if acct_filter is not None:
                    rows = _ind_acct.get((code, acct_filter), [])
                    for row in rows:
                        _enrich_row(
                            row,
                            order,
                            base_level,
                            _ACCT_SORT.get(acct_filter, 3),
                            child_order,
                            info["label"],
                            is_header=bool(children),
                        )
                    if not rows:
                        _synthetic_header(
                            code,
                            order,
                            base_level,
                            _ACCT_SORT.get(acct_filter, 3),
                            child_order,
                            info["label"],
                        )
                    _consumed.add((code, acct_filter))
                    # Recurse into children for the same acct entry.
                    for ch in sorted(
                        children,
                        key=lambda c: hierarchy_order_map[c]["order"],
                    ):
                        if acct_filter in _ind_accts.get(ch, set()):
                            _emit_indicator(
                                ch,
                                base_level + 1,
                                parent_order=order,
                                acct_filter=acct_filter,
                                child_order=hierarchy_order_map[ch]["order"],
                            )
                    return

                # --- Full emit (top-level or unfiltered) ---
                bn = sorted(accts & _BN_ENTRIES)
                non_bn = sorted(
                    accts - _BN_ENTRIES,
                    key=lambda a: _ACCT_SORT.get(a, 3),
                )

                # Determine which non-B/N entries can group children.
                grouped: list[str] = []
                ungrouped: list[str] = []
                if children:
                    for acct in non_bn:
                        if any(acct in _ind_accts.get(ch, set()) for ch in children):
                            grouped.append(acct)
                        else:
                            ungrouped.append(acct)
                else:
                    ungrouped = list(non_bn)

                has_sub = bool(grouped) or bool(ungrouped) or bool(children)

                # Emit B/N rows.
                for b in bn:
                    for row in _ind_acct.get((code, b), []):
                        _enrich_row(
                            row,
                            info["order"],
                            base_level,
                            0,
                            0,
                            info["label"],
                            is_header=has_sub,
                        )
                    _consumed.add((code, b))

                # Synthetic B/N header when indicator has sub-rows but
                # no balance/net data.
                if not bn and has_sub:
                    _synthetic_header(
                        code,
                        info["order"],
                        base_level,
                        0,
                        0,
                        info["label"],
                    )

                # Grouped accounting entries — children nest under them.
                for acct in grouped:
                    asort = _ACCT_SORT.get(acct, 3)
                    parent_rows = _ind_acct.get((code, acct), [])
                    lbl = _acct_labels.get(acct, acct)
                    for row in parent_rows:
                        lbl = row.get("ACCOUNTING_ENTRY_label", lbl)
                        _enrich_row(
                            row,
                            info["order"],
                            base_level + 1,
                            asort,
                            0,
                            lbl,
                            is_header=True,
                        )
                    if not parent_rows:
                        _synthetic_header(
                            code,
                            info["order"],
                            base_level + 1,
                            asort,
                            0,
                            lbl,
                        )
                    _consumed.add((code, acct))
                    # Children's matching entries.
                    for ch in sorted(
                        children,
                        key=lambda c: hierarchy_order_map[c]["order"],
                    ):
                        if acct in _ind_accts.get(ch, set()):
                            _emit_indicator(
                                ch,
                                base_level + 2,
                                parent_order=info["order"],
                                acct_filter=acct,
                                child_order=hierarchy_order_map[ch]["order"],
                            )
                # Consume children's B/N (redundant once grouped).
                if grouped:
                    for ch in children:
                        for b in _BN_ENTRIES:
                            _consumed.add((ch, b))

                # Ungrouped accounting entries — simple sub-children.
                for acct in ungrouped:
                    asort = _ACCT_SORT.get(acct, 3)
                    for row in _ind_acct.get((code, acct), []):
                        _enrich_row(
                            row,
                            info["order"],
                            base_level + 1,
                            asort,
                            0,
                            row.get("ACCOUNTING_ENTRY_label", acct),
                            is_header=False,
                        )
                    _consumed.add((code, acct))

                # Recurse into children that have unconsumed entries.
                if children:
                    for ch in sorted(
                        children,
                        key=lambda c: hierarchy_order_map[c]["order"],
                    ):
                        ch_accts = _ind_accts.get(ch, set())
                        if ch_accts and not all((ch, a) in _consumed for a in ch_accts):
                            _emit_indicator(ch, base_level + 1)

            # Walk root indicators in hierarchy order.
            roots = sorted(
                [
                    c
                    for c, inf in hierarchy_order_map.items()
                    if inf.get("parent") is None
                ],
                key=lambda c: hierarchy_order_map[c]["order"],
            )
            for root_code in roots:
                _emit_indicator(root_code, hierarchy_order_map[root_code]["level"])
        else:
            # No ACCOUNTING_ENTRY dimension — simple enrichment.
            all_rows = []
            for row in data_rows:
                ind_code = row.get(indicator_dim, "")
                hier_info = hierarchy_order_map.get(ind_code)
                if not hier_info and ind_code:
                    for h_code, h_value in hierarchy_order_map.items():
                        if ind_code.startswith(h_code + "_") or h_code.startswith(
                            ind_code + "_"
                        ):
                            hier_info = h_value
                            break
                if hier_info:
                    row["order"] = hier_info["order"]
                    row["level"] = hier_info["level"]
                    row["_acct_sort"] = 0
                    row["_child_order"] = 0
                    row["label"] = hier_info["label"]
                    row["is_category_header"] = bool(hier_info["children"])
                    row["parent_id"] = hier_info["parent"]
                    row["parent_code"] = hier_info["parent_code"]
                    all_rows.append(row)

        # ---- Build clean flat output rows (one per observation) ----
        # Placeholder labels from codelists that carry no useful meaning.
        _USELESS_LABELS = {
            "not applicable",
            "not specified",
            "no breakdown",
            "total",
            "all items",
            "all activities",
            "total economy",
            "non transformed data",
            "nan",
        }

        def _clean_label(val: Any) -> str:
            """Return a clean string label, or empty string for NaN/useless values."""
            if val is None:
                return ""
            if isinstance(val, float) and val != val:
                return ""
            s = str(val).strip()
            if s.lower() in _USELESS_LABELS:
                return ""
            return s

        clean_rows: list[dict] = []
        for row in all_rows:
            clean: dict[str, Any] = {}
            # Hierarchy fields.
            clean["order"] = row.get("order", 9999)
            clean["level"] = row.get("level", 0)
            clean["_acct_sort"] = row.get("_acct_sort", 0)
            clean["_child_order"] = row.get("_child_order", 0)
            clean["parent_id"] = row.get("parent_id")
            clean["parent_code"] = row.get("parent_code")
            base_label = _clean_label(row.get("label", ""))
            _base_from_compounds = False

            # When the hierarchy label is a useless placeholder, derive a
            # meaningful label from the data row's dimension labels.
            if not base_label or base_label.startswith("_"):
                # Try the indicator dimension's own label first.
                alt = _clean_label(row.get(f"{indicator_dim}_label", ""))
                if alt:
                    base_label = alt
                else:
                    # Build from all content dimension labels on the row.
                    parts: list[str] = []
                    for cdim in _compound_dims:
                        lbl = _clean_label(row.get(f"{cdim}_label", ""))
                        if lbl:
                            parts.append(lbl)
                    if parts:
                        base_label = " - ".join(parts)
                        _base_from_compounds = True
                    elif not base_label:
                        base_label = row.get(indicator_dim, "") or ""

            # Raw neutral dimension codes are never useful labels.
            if base_label.startswith("_"):
                base_label = ""

            clean["is_category_header"] = row.get("is_category_header", False)
            base_code = row.get(indicator_dim, "")
            clean["_acct_code"] = row.get("ACCOUNTING_ENTRY", "")
            clean["_sub_order"] = 0

            # ---- Compound symbol: fold content-varying dims into
            #      code and label so each row has a unique identity. ----
            if _compound_dims:
                _code_parts = [base_code]
                _label_parts = []
                _is_compound_total = True
                _NEUTRAL = {"_Z", "_T", "_X", ""}
                _comp_codes: dict[str, str] = {}
                for cdim in _compound_dims:
                    cv = row.get(cdim, "")
                    if cv in _NEUTRAL:
                        continue  # skip both code and label for neutral values
                    _code_parts.append(cv)
                    _comp_codes[cdim] = cv
                    _is_compound_total = False
                    cl = _clean_label(row.get(f"{cdim}_label", cv))
                    if cl:
                        _label_parts.append(str(cl))
                clean["code"] = "_".join(p for p in _code_parts if p)
                # Build label: when the indicator hierarchy is flat (no
                # parent/child nesting), prepend the base indicator label
                # for context.  When a nested hierarchy exists, the
                # parent row already provides that context.
                _hierarchy_is_flat = not any(
                    e.get("parent") for e in all_hierarchy_entries
                )
                if _label_parts:
                    if (
                        base_label
                        and not _is_compound_total
                        and _hierarchy_is_flat
                        and not _base_from_compounds
                    ):
                        clean["label"] = base_label + " - " + " - ".join(_label_parts)
                    else:
                        clean["label"] = " - ".join(_label_parts)
                else:
                    clean["label"] = base_label
                # Track which base indicator this row belongs to.
                clean["_base_indicator"] = base_code
                clean["_compound_codes"] = _comp_codes
                # Total/aggregate rows sort first; detail rows indent
                # one level below as children.
                if _is_compound_total:
                    clean["_sub_order"] = 0
                else:
                    clean["_sub_order"] = 1
                    clean["level"] = clean.get("level", 0) + 1
            else:
                clean["code"] = base_code
                clean["label"] = base_label

            # Varying dimension columns.
            for did in varying_dims:
                key = did.lower()
                if use_labels:
                    clean[key] = row.get(f"{did}_label", row.get(did, ""))
                else:
                    clean[key] = row.get(did, "")

            # Core data.
            clean["time_period"] = row.get("TIME_PERIOD", "")
            _obs = row.get("OBS_VALUE")
            # Expand by UNIT_MULT (power-of-10 code) so values are in units.
            _um = row.get("UNIT_MULT")
            if _obs is not None and _um is not None:
                try:
                    _exp = int(str(_um).strip())
                    if _exp > 0:
                        _obs = _obs * (10**_exp)
                except (ValueError, TypeError):
                    pass
            clean["value"] = _obs

            # Unit metadata from fixed dimensions.
            for unit_key in (
                "UNIT_MEASURE",
                "CURRENCY_DENOM",
                "CURRENCY",
                "UNIT_MULT",
                "PRICE_BASE",
            ):
                if unit_key in fixed_values:
                    clean[unit_key.lower()] = fixed_values[unit_key]["label"]

            clean_rows.append(clean)

        # When compound dims are present, undo the level bump for
        # indicators that have no "total" aggregate row — there's no
        # parent to nest under, so compound details should stay at
        # the indicator's natural hierarchy level.
        if _compound_dims:
            _indicators_with_total: set[str] = set()
            for cr in clean_rows:
                if cr.get("_sub_order", 0) == 0 and cr.get("_base_indicator"):
                    _indicators_with_total.add(cr["_base_indicator"])
            for cr in clean_rows:
                base = cr.get("_base_indicator", "")
                if (
                    cr.get("_sub_order", 0) == 1
                    and base
                    and base not in _indicators_with_total
                ):
                    cr["level"] = max(cr["level"] - 1, 0)
                    cr["_sub_order"] = 0

        # ---- Compound-dimension hierarchy from codelist parents ----
        # When a compound dim has codelist parent-child relationships,
        # use them to assign proper depth levels and tree-order sorting
        # so nested categories (e.g. Transport → Sea transport) display
        # correctly instead of appearing flat.
        if _compound_dims and clean_rows:
            _compound_hier: dict[str, dict[str, dict]] = {}
            for cdim in _compound_dims:
                # Find the codelist ID for this dimension.
                _cl_id = ""
                for _d in dims:
                    if _d["id"] == cdim:
                        _cl_id = _d.get("codelist_id", "")
                        break
                if not _cl_id:
                    continue
                _parents = self.metadata._codelist_parents.get(_cl_id, {})
                if not _parents:
                    continue
                # Collect codes actually present in the data.
                _present = {row.get(cdim) for row in all_rows if row.get(cdim)}
                _present.discard(None)
                _present.discard("")
                if not _present:
                    continue

                def _cdepth(code: str, depth_cache: dict[str, int]) -> int:
                    if code in depth_cache:
                        return depth_cache[code]
                    p = _parents.get(code)
                    if p is None or p not in _present:
                        depth_cache[code] = 0
                        return 0
                    d = 1 + _cdepth(p, depth_cache)
                    depth_cache[code] = d
                    return d

                _dc: dict[str, int] = {}
                # Build children map for DFS traversal.
                _children: dict[str, list[str]] = {}
                for c in _present:
                    p = _parents.get(c)
                    # Effective parent: must also be present in data.
                    while p and p not in _present:
                        p = _parents.get(p)
                    if p and p in _present:
                        _children.setdefault(p, []).append(c)  # type: ignore
                # Determine effective roots: codes whose effective parent
                # (after skipping absent ancestors) is not in _present.
                _effective_roots: list = []
                for c in sorted(_present):  # type: ignore
                    p = _parents.get(c)
                    while p and p not in _present:
                        p = _parents.get(p)
                    if not p or p not in _present:
                        _effective_roots.append(c)

                # DFS traversal to assign hierarchy order.
                _hier: dict[str, dict] = {}
                _ord = [0]

                def _visit(code: str) -> None:
                    kids = sorted(_children.get(code, []))
                    _hier[code] = {
                        "depth": _cdepth(code, _dc),
                        "order": _ord[0],
                        "has_children": bool(kids),
                    }
                    _ord[0] += 1
                    for kid in kids:
                        _visit(kid)

                for root in _effective_roots:
                    _visit(root)
                if _hier:
                    _compound_hier[cdim] = _hier

            # Apply hierarchy info to clean_rows.
            if _compound_hier:
                for cr in clean_rows:
                    _extra_depth = 0
                    _hier_order = 0
                    _is_header = cr.get("is_category_header", False)
                    _codes = cr.get("_compound_codes", {})
                    for cdim in _compound_dims:
                        if cdim not in _compound_hier:
                            continue
                        _cdim_code = _codes.get(cdim, "")
                        if not _cdim_code:
                            continue
                        _h = _compound_hier[cdim].get(_cdim_code)
                        if _h:
                            _extra_depth += _h["depth"]
                            _hier_order = _h["order"]
                            if _h["has_children"]:
                                _is_header = True
                    if _extra_depth or _hier_order:
                        cr["level"] = cr.get("level", 0) + _extra_depth
                        cr["_compound_order"] = _hier_order
                        cr["is_category_header"] = _is_header
                    else:
                        cr["_compound_order"] = -1  # totals sort first

        # Sort by hierarchy order, accounting entry, sub-order, compound
        # hierarchy order, then time period.
        clean_rows.sort(
            key=lambda r: (
                r.get("order", 9999),
                r.get("_acct_sort", 0),
                r.get("_child_order", 0),
                r.get("_sub_order", 0),
                r.get("_compound_order", 0),
                r.get("code", ""),
                r.get("time_period", ""),
            )
        )

        # ---- Supplementary % of GDP rows ----
        # If PT_B1GQ is available and isn't the primary unit already,
        # fetch it and insert as sub-rows beneath each indicator.
        _primary_unit = kwargs.get("UNIT_MEASURE", "")
        _pct_gdp_available = (
            "PT_B1GQ" in avail.get("UNIT_MEASURE", []) and _primary_unit != "PT_B1GQ"
        )
        if _pct_gdp_available:
            try:
                _pct_kwargs = dict(kwargs)
                _pct_kwargs["UNIT_MEASURE"] = "PT_B1GQ"
                _pct_raw = self.query_builder.fetch_data(
                    dataflow=dataflow,
                    start_date=start_date,
                    end_date=end_date,
                    limit=limit,
                    _skip_validation=True,
                    **_pct_kwargs,
                )
                _pct_rows = _pct_raw.get("data", [])
                # Build lookup: (indicator, acct_entry, time) → value
                _pct_lookup: dict[tuple[str, str, str], float] = {}
                for _pr in _pct_rows:
                    _pk = (
                        _pr.get(indicator_dim, ""),
                        _pr.get("ACCOUNTING_ENTRY", ""),
                        _pr.get("TIME_PERIOD", ""),
                    )
                    val = _pr.get("OBS_VALUE")
                    if val is not None:
                        # Expand by UNIT_MULT for % of GDP too.
                        _pum = _pr.get("UNIT_MULT")
                        if _pum is not None:
                            try:
                                _pexp = int(str(_pum).strip())
                                if _pexp > 0:
                                    val = val * (10**_pexp)
                            except (ValueError, TypeError):
                                pass
                        _pct_lookup[_pk] = val
                # Create % of GDP sub-rows.
                pct_sub_rows: list[dict] = []
                for cr in clean_rows:
                    _ck = (
                        cr.get("code", ""),
                        cr.get("_acct_code", ""),
                        cr.get("time_period", ""),
                    )
                    if _ck in _pct_lookup:
                        pct_row: dict[str, Any] = {
                            "order": cr["order"],
                            "level": cr["level"] + 1,
                            "_acct_sort": cr["_acct_sort"],
                            "_child_order": cr["_child_order"],
                            "_sub_order": 1,
                            "parent_id": cr.get("parent_id"),
                            "parent_code": cr.get("parent_code"),
                            "label": "% of GDP",
                            "is_category_header": False,
                            "code": cr.get("code", "") + "_PCTGDP",
                            "_acct_code": cr.get("_acct_code", ""),
                            "time_period": cr["time_period"],
                            "value": _pct_lookup[_ck],
                        }
                        # Copy varying dim columns.
                        for did in varying_dims:
                            key = did.lower()
                            if key in cr:
                                pct_row[key] = cr[key]
                        pct_sub_rows.append(pct_row)
                if pct_sub_rows:
                    clean_rows.extend(pct_sub_rows)
                    clean_rows.sort(
                        key=lambda r: (
                            r.get("order", 9999),
                            r.get("_acct_sort", 0),
                            r.get("_child_order", 0),
                            r.get("_sub_order", 0),
                            r.get("code", ""),
                            r.get("time_period", ""),
                        )
                    )
            except Exception:  # noqa: BLE001, S110
                pass  # Supplementary fetch failure is non-fatal.

        # ---- Metadata ----
        df_meta = self.metadata.dataflows.get(full_id, {})

        def _fixed_label(dim_candidates: list[str]) -> str:
            for d in dim_candidates:
                if d in fixed_values:
                    return fixed_values[d]["label"]
            return ""

        # Extract unit metadata from data-level attributes when not
        # available as fixed dimensions (UNIT_MULT, CURRENCY are often
        # observation-level attributes, not DSD dimensions).
        def _attr_label(attr: str) -> str:
            """Get the most common label for a data-level attribute."""
            label_key = f"{attr}_label"
            for row in data_rows:
                if label_key in row:
                    v = _clean_label(row[label_key])
                    if v:
                        return v
                if attr in row:
                    v = _clean_label(row[attr])
                    if v:
                        return v
            return ""

        unit_measure = _fixed_label(["UNIT_MEASURE"]) or _attr_label("UNIT_MEASURE")
        unit_mult = _fixed_label(["UNIT_MULT"]) or _attr_label("UNIT_MULT")

        # Also get the raw UNIT_MULT code for consumers.
        def _attr_code(attr: str) -> str:
            for row in data_rows:
                if attr in row and row[attr]:
                    return str(row[attr])
            return ""

        unit_mult_code = (
            fixed_values["UNIT_MULT"]["code"]
            if "UNIT_MULT" in fixed_values
            else _attr_code("UNIT_MULT")
        )
        currency = _fixed_label(["CURRENCY_DENOM", "CURRENCY"]) or _attr_label(
            "CURRENCY"
        )
        price_base = _fixed_label(["PRICE_BASE"]) or _attr_label("PRICE_BASE")

        table_metadata = {
            "table_id": table_id or df_meta.get("short_id", dataflow),
            "table_name": table_structure.get("hierarchy_name", ""),
            "dataflow_id": full_id,
            "dataflow_name": df_meta.get("name", dataflow),
            "url": raw.get("metadata", {}).get("url", ""),
            "row_count": len(clean_rows),
            "total_indicators": len(hierarchy_codes),
            "unit_measure": unit_measure,
            "unit_multiplier": unit_mult,
            "unit_multiplier_code": unit_mult_code,
            "currency": currency,
            "price_base": price_base,
            "fixed_dimensions": fixed_values,
        }

        return {
            "table_metadata": table_metadata,
            "structure": table_structure,
            "data": clean_rows,
            "series_metadata": raw.get("metadata", {}),
        }
