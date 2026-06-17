"""Row-level value extraction from SEC XBRL facts."""

# pylint: disable=R0912,R0914,R0915,R0917

from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from math import isclose
from typing import Any

from openbb_sec.utils.statement_schema._types import (
    ALL_FORMS,
    ANNUAL_FORMS,
    PRELIMINARY_FORMS,
    SEMI_ANNUAL_FORMS,
    Frequency,
    RowDef,
)


def _get_unit_data(
    tag_data: dict,
    unit_type: str = "monetary",
    currency: str = "USD",
) -> list[dict] | None:
    """Find the best unit data array from a tag's units dict."""
    units = tag_data.get("units", {})

    if unit_type == "shares":
        if "shares" in units:
            return units["shares"]
    elif unit_type == "per_share":
        per_share_key = f"{currency}/shares"
        if per_share_key in units:
            return units[per_share_key]
        for key in units:
            if key.startswith(f"{currency}/"):
                return units[key]
    elif currency in units:
        return units[currency]

    if units:
        return next(iter(units.values()))

    return None


def _get_annual_values(
    facts: dict[str, Any],
    row: RowDef,
    currency: str = "USD",
    include_preliminary: bool = False,
) -> dict[str, tuple[str, float, str]]:
    """Return {fy_end_date: (fy_start_date, value, xbrl_source)} for annual periods."""
    if row.period_type != "duration":
        return {}

    tag_candidates: list[dict[str, dict[str, tuple[str, float]]]] = []

    for xbrl_entry in row.xbrl_tags:
        ns_facts = facts.get(xbrl_entry["namespace"], {})
        tag_data = ns_facts.get(xbrl_entry["tag"])

        if not tag_data:
            tag_candidates.append({})
            continue

        unit_data = _get_unit_data(tag_data, row.unit, currency)

        if not unit_data:
            tag_candidates.append({})
            continue

        entries_by_date: dict[str, dict[str, tuple[str, float]]] = {}

        for entry in unit_data:

            _av_allowed = (
                ANNUAL_FORMS | PRELIMINARY_FORMS
                if include_preliminary
                else ANNUAL_FORMS
            )
            if entry.get("form", "") not in _av_allowed:
                continue
            start, end = entry.get("start", ""), entry.get("end", "")

            if not start or not end or start == end:
                continue

            try:
                days = (
                    datetime.strptime(end, "%Y-%m-%d")
                    - datetime.strptime(start, "%Y-%m-%d")
                ).days
            except (ValueError, TypeError):
                continue

            if not 300 <= days <= 400:
                continue

            val = entry.get("val")

            if val is None:
                continue

            filed = entry.get("filed", "")

            if end not in entries_by_date:
                entries_by_date[end] = {}

            if filed not in entries_by_date[end]:
                entries_by_date[end][filed] = (start, val)

        tag_candidates.append(entries_by_date)

    all_dates: set[str] = set()

    for tc in tag_candidates:
        all_dates.update(tc.keys())

    result: dict[str, tuple[str, float, str]] = {}

    for end_date in all_dates:
        ref_filed = None

        for tc in tag_candidates:
            filings = tc.get(end_date)

            if filings:
                earliest = min(filings)

                if ref_filed is None or earliest < ref_filed:
                    ref_filed = earliest

        if ref_filed is None:
            continue

        for i, tc in enumerate(tag_candidates):
            filings = tc.get(end_date)

            if filings and ref_filed in filings:
                start, val = filings[ref_filed]
                xbrl_e = row.xbrl_tags[i]
                xbrl_src = f"{xbrl_e['namespace']}:{xbrl_e['tag']}"
                result[end_date] = (start, val, xbrl_src)
                break

    return result


def _get_ytd9_values(
    facts: dict[str, Any],
    row: RowDef,
    currency: str = "USD",
) -> dict[str, float]:
    """Return {fy_end_date: Q4_value} derived via FY - YTD_9mo."""
    if row.period_type != "duration":
        return {}

    annual_entries: dict[str, dict[str, tuple[str, float]]] = {}
    ytd9_entries: dict[str, dict[str, float]] = {}

    for xbrl_entry in row.xbrl_tags:
        ns_facts = facts.get(xbrl_entry["namespace"], {})
        tag_data = ns_facts.get(xbrl_entry["tag"])

        if not tag_data:
            continue

        unit_data = _get_unit_data(tag_data, row.unit, currency)

        if not unit_data:
            continue

        for entry in unit_data:
            start = entry.get("start", "")
            end = entry.get("end", "")

            if not start or not end or start == end:
                continue

            try:
                days = (
                    datetime.strptime(end, "%Y-%m-%d")
                    - datetime.strptime(start, "%Y-%m-%d")
                ).days
            except (ValueError, TypeError):
                continue

            val = entry.get("val")

            if val is None:
                continue

            filed = entry.get("filed", "")

            if 300 <= days <= 400:
                if end not in annual_entries:
                    annual_entries[end] = {}
                if filed not in annual_entries[end]:
                    annual_entries[end][filed] = (start, val)
            elif 240 <= days <= 310:
                if end not in ytd9_entries:
                    ytd9_entries[end] = {}
                if filed not in ytd9_entries[end]:
                    ytd9_entries[end][filed] = val

        if annual_entries or ytd9_entries:
            break

    if not annual_entries or not ytd9_entries:
        return {}

    result: dict[str, float] = {}

    for fy_end, fy_filings in annual_entries.items():
        ytd_end_match = None

        for ytd_end in ytd9_entries:
            for filed, (fy_start, _) in fy_filings.items():
                if fy_start < ytd_end < fy_end:
                    ytd_end_match = ytd_end
                    break

            if ytd_end_match:
                break

        if not ytd_end_match:
            continue

        ytd_filings = ytd9_entries[ytd_end_match]

        common = set(fy_filings) & set(ytd_filings)

        if common:
            best = max(common)
            _, fy_val = fy_filings[best]
            ytd_val = ytd_filings[best]
        else:
            latest_fy = max(fy_filings)
            _, fy_val = fy_filings[latest_fy]
            ytd_val = ytd_filings[max(ytd_filings)]

        result[fy_end] = fy_val - ytd_val

    return result


def extract_row_values(  # noqa: PLR0912
    facts: dict[str, Any],
    row: RowDef,
    frequency: Frequency = "annual",
    currency: str = "USD",
    ref_filed_map: dict[str, str] | None = None,
    cross_targets: dict[str, float] | None = None,
    statement: str = "",
    include_preliminary: bool = False,
) -> tuple[dict[str, float], dict[str, str]]:
    """Extract values for a single schema row across all periods."""
    period_type = row.period_type
    values_by_date: dict[str, float] = {}
    sources_by_date: dict[str, str] = {}
    _base_forms = ANNUAL_FORMS if frequency == "annual" else ALL_FORMS
    allowed_forms = (
        _base_forms | PRELIMINARY_FORMS if include_preliminary else _base_forms
    )
    tag_candidates: list[dict[str, dict[str, float]]] = []
    collect_ytd = (
        frequency == "quarterly" and period_type == "duration" and row.unit != "shares"
    )
    ytd_tag_candidates: list[dict[str, dict[str, tuple[str, float]]]] = []

    for xbrl_entry in row.xbrl_tags:
        ns_facts = facts.get(xbrl_entry["namespace"], {})
        tag_data = ns_facts.get(xbrl_entry["tag"])

        if not tag_data:
            tag_candidates.append({})

            if collect_ytd:
                ytd_tag_candidates.append({})

            continue

        unit_data = _get_unit_data(tag_data, row.unit, currency)

        if not unit_data:
            tag_candidates.append({})

            if collect_ytd:
                ytd_tag_candidates.append({})

            continue

        entries_by_date: dict[str, dict[str, float]] = {}
        _dur_by_date: dict[str, dict[str, int]] = {}
        ytd_entries_by_date: dict[str, dict[str, tuple[str, float]]] = {}

        for entry in unit_data:
            form = entry.get("form", "")

            if form not in allowed_forms:
                continue

            end_date = entry.get("end", "")

            if not end_date:
                continue

            days = 0

            if period_type == "duration":
                start_date = entry.get("start", "")

                if not start_date or start_date == end_date:
                    continue
                try:
                    days = (
                        datetime.strptime(end_date, "%Y-%m-%d")
                        - datetime.strptime(start_date, "%Y-%m-%d")
                    ).days
                except (ValueError, TypeError):
                    continue

                if frequency == "annual":
                    if not 300 <= days <= 400:
                        continue
                elif form in SEMI_ANNUAL_FORMS:
                    if not (60 <= days <= 135 or 150 <= days <= 200):
                        continue
                elif not 60 <= days <= 135:
                    if collect_ytd and 136 <= days <= 310:
                        ytd_val = entry.get("val")
                        if ytd_val is not None:
                            filed = entry.get("filed", "")
                            if end_date not in ytd_entries_by_date:
                                ytd_entries_by_date[end_date] = {}
                            if filed not in ytd_entries_by_date[end_date]:
                                ytd_entries_by_date[end_date][filed] = (
                                    start_date,
                                    ytd_val,
                                )
                    continue

            val = entry.get("val")

            if val is None:
                continue

            filed = entry.get("filed", "")

            if end_date not in entries_by_date:
                entries_by_date[end_date] = {}
                _dur_by_date[end_date] = {}
            if filed not in entries_by_date[end_date] or days < _dur_by_date[
                end_date
            ].get(filed, 9999):
                entries_by_date[end_date][filed] = val
                _dur_by_date[end_date][filed] = days

        tag_candidates.append(entries_by_date)

        if collect_ytd:
            ytd_tag_candidates.append(ytd_entries_by_date)

    all_dates: set[str] = set()

    for tc in tag_candidates:
        all_dates.update(tc.keys())

    for end_date in all_dates:
        if ref_filed_map is not None:
            ref_filed = ref_filed_map.get(end_date)
        else:
            ref_filed = None

            for tc in tag_candidates:
                filings = tc.get(end_date)
                if filings:
                    earliest = min(filings)
                    if ref_filed is None or earliest < ref_filed:
                        ref_filed = earliest

        if ref_filed is None:
            continue

        matched_identity = False

        if cross_targets and end_date in cross_targets:
            target_val = cross_targets[end_date]
            for i, tc in enumerate(tag_candidates):
                filings = tc.get(end_date)
                if not filings:
                    continue
                for val in filings.values():
                    if isclose(val, target_val, rel_tol=1e-5, abs_tol=1.0):
                        values_by_date[end_date] = val
                        xbrl_e = row.xbrl_tags[i]
                        sources_by_date[end_date] = (
                            f"{xbrl_e['namespace']}:{xbrl_e['tag']}(identity_lock:{statement})"
                        )
                        matched_identity = True
                        break

                if matched_identity:
                    break

        if matched_identity:
            continue

        if frequency == "quarterly" and period_type == "duration":
            for i, tc in enumerate(tag_candidates):
                filings = tc.get(end_date)

                if not filings:
                    continue

                xbrl_e = row.xbrl_tags[i]

                if ref_filed in filings:
                    values_by_date[end_date] = filings[ref_filed]
                    sources_by_date[end_date] = f"{xbrl_e['namespace']}:{xbrl_e['tag']}"
                else:
                    before = [f for f in filings if f <= ref_filed]
                    best = max(before) if before else min(filings)
                    values_by_date[end_date] = filings[best]
                    sources_by_date[end_date] = (
                        f"{xbrl_e['namespace']}:{xbrl_e['tag']}(fallback)"
                    )
                break
        else:
            for i, tc in enumerate(tag_candidates):
                filings = tc.get(end_date)

                if filings and ref_filed in filings:
                    values_by_date[end_date] = filings[ref_filed]
                    xbrl_e = row.xbrl_tags[i]
                    sources_by_date[end_date] = f"{xbrl_e['namespace']}:{xbrl_e['tag']}"
                    break
            else:
                for i, tc in enumerate(tag_candidates):
                    filings = tc.get(end_date)

                    if filings:
                        before = [f for f in filings if f <= ref_filed]
                        best = max(before) if before else min(filings)
                        values_by_date[end_date] = filings[best]
                        xbrl_e = row.xbrl_tags[i]
                        sources_by_date[end_date] = (
                            f"{xbrl_e['namespace']}:{xbrl_e['tag']}(fallback)"
                        )
                        break

    if frequency == "quarterly" and period_type == "duration":
        annual_vals = _get_annual_values(
            facts, row, currency, include_preliminary=include_preliminary
        )

        if collect_ytd and ytd_tag_candidates:
            ytd_resolved: dict[str, tuple[str, float, str]] = {}
            ytd_all_dates: set[str] = set()

            for ytc in ytd_tag_candidates:
                ytd_all_dates.update(ytc.keys())

            for end_date in ytd_all_dates:
                if ref_filed_map is not None:
                    ref = ref_filed_map.get(end_date)
                else:
                    ref = None
                    for ytc in ytd_tag_candidates:
                        ytd_fdata = ytc.get(end_date)

                        if ytd_fdata:
                            earliest = min(ytd_fdata)
                            if ref is None or earliest < ref:
                                ref = earliest

                if ref is None:
                    continue

                for i, ytc in enumerate(ytd_tag_candidates):
                    ytd_fdata = ytc.get(end_date)

                    if not ytd_fdata:
                        continue

                    if ref in ytd_fdata:
                        start_d, val = ytd_fdata[ref]
                    else:
                        before = [f for f in ytd_fdata if f <= ref]
                        best = max(before) if before else min(ytd_fdata)
                        start_d, val = ytd_fdata[best]

                    xbrl_e = row.xbrl_tags[i]
                    ytd_resolved[end_date] = (
                        start_d,
                        val,
                        f"{xbrl_e['namespace']}:{xbrl_e['tag']}",
                    )
                    break

            if ytd_resolved:
                by_fy_start: dict[str, list[tuple[str, float, str]]] = defaultdict(list)
                for end_d, (start_d, val, src) in ytd_resolved.items():
                    by_fy_start[start_d].append((end_d, val, src))

                fy_boundaries = {
                    fy_start: fy_end for fy_end, (fy_start, _, _) in annual_vals.items()
                }

                for fy_start, ytd_list in by_fy_start.items():
                    ytd_list.sort()
                    ytd_map = {d: (v, s) for d, v, s in ytd_list}
                    fy_end = fy_boundaries.get(fy_start)

                    if fy_end:
                        fy_q_dates = sorted(
                            d for d in values_by_date if fy_start < d < fy_end
                        )
                    else:
                        latest_ytd = ytd_list[-1][0]
                        fy_q_dates = sorted(
                            d for d in values_by_date if fy_start < d <= latest_ytd
                        )

                    all_q_dates = sorted(set(fy_q_dates) | set(ytd_map.keys()))

                    prev_cum = 0.0
                    for d in all_q_dates:
                        has_standalone = d in values_by_date
                        has_ytd = d in ytd_map

                        if not has_standalone and has_ytd:
                            ytd_val, ytd_src = ytd_map[d]
                            values_by_date[d] = ytd_val - prev_cum
                            sources_by_date[d] = f"ytd_derived({ytd_src})"

                        if has_ytd:
                            prev_cum = ytd_map[d][0]
                        elif has_standalone:
                            prev_cum += values_by_date[d]

        if row.unit == "shares":
            for fy_end, (fy_start, fy_val, fy_xbrl_src) in annual_vals.items():
                if fy_end not in values_by_date:
                    values_by_date[fy_end] = fy_val
                    sources_by_date[fy_end] = f"Q4: FY[{fy_xbrl_src}]"

        else:
            for fy_end, (fy_start, fy_val, fy_xbrl_src) in annual_vals.items():
                q_sum = 0.0
                q_count = 0
                for q_end, q_val in values_by_date.items():
                    if fy_start < q_end < fy_end:
                        q_sum += q_val
                        q_count += 1
                if q_count == 3:
                    q_srcs = [
                        sources_by_date.get(q_end, "")
                        for q_end in sorted(values_by_date)
                        if fy_start < q_end < fy_end
                    ]
                    q_labels = "+".join(f"Q{i+1}[{s}]" for i, s in enumerate(q_srcs))
                    values_by_date[fy_end] = fy_val - q_sum
                    sources_by_date[fy_end] = (
                        f"Q4: FY[{fy_xbrl_src}] \u2212 ({q_labels})"
                    )
                elif q_count == 1:
                    interim_date = next(
                        q_end for q_end in values_by_date if fy_start < q_end < fy_end
                    )
                    fy_days = (
                        datetime.strptime(fy_end, "%Y-%m-%d")
                        - datetime.strptime(fy_start, "%Y-%m-%d")
                    ).days
                    interim_days = (
                        datetime.strptime(interim_date, "%Y-%m-%d")
                        - datetime.strptime(fy_start, "%Y-%m-%d")
                    ).days
                    if abs(interim_days - fy_days / 2) <= 45:
                        h1_src = sources_by_date.get(interim_date, "")
                        values_by_date[fy_end] = fy_val - q_sum
                        sources_by_date[fy_end] = (
                            f"H2: FY[{fy_xbrl_src}] \u2212 H1[{h1_src}]"
                        )

    return values_by_date, sources_by_date


def compute_ref_filings(
    facts: dict[str, Any],
    rows_def: list,
    frequency: Frequency,
    currency: str,
    include_preliminary: bool = False,
    pit_mode: bool = False,
) -> dict[str, str]:
    """Compute the reference filing date per end_date across all rows."""
    _base_forms = ANNUAL_FORMS if frequency == "annual" else ALL_FORMS
    allowed_forms = (
        _base_forms | PRELIMINARY_FORMS if include_preliminary else _base_forms
    )
    ref_map: dict[str, str] = {}

    for row_def in rows_def:
        period_type = row_def.period_type

        for xbrl_entry in row_def.xbrl_tags:
            ns_facts = facts.get(xbrl_entry["namespace"], {})
            tag_data = ns_facts.get(xbrl_entry["tag"])

            if not tag_data:
                continue

            unit_data = _get_unit_data(tag_data, row_def.unit, currency)

            if not unit_data:
                continue

            for entry in unit_data:
                form = entry.get("form", "")

                if form not in allowed_forms:
                    continue

                end_date = entry.get("end", "")

                if not end_date:
                    continue

                if period_type == "duration":
                    start_date = entry.get("start", "")

                    if not start_date or start_date == end_date:
                        continue

                    try:
                        days = (
                            datetime.strptime(end_date, "%Y-%m-%d")
                            - datetime.strptime(start_date, "%Y-%m-%d")
                        ).days
                    except (ValueError, TypeError):
                        continue

                    if frequency == "annual":
                        if not 300 <= days <= 400:
                            continue
                    elif form in SEMI_ANNUAL_FORMS:
                        if not (60 <= days <= 135 or 150 <= days <= 200):
                            continue
                    elif not 60 <= days <= 135:
                        continue

                filed = entry.get("filed", "")

                if not filed:
                    continue

                if not pit_mode:
                    try:
                        _gap = (
                            datetime.strptime(filed, "%Y-%m-%d")
                            - datetime.strptime(end_date, "%Y-%m-%d")
                        ).days
                    except (ValueError, TypeError):
                        continue
                    if _gap > 450:
                        continue

                if (
                    end_date not in ref_map
                    or pit_mode
                    and filed < ref_map[end_date]
                    or not pit_mode
                    and filed > ref_map[end_date]
                ):
                    ref_map[end_date] = filed

    return ref_map


def quarterly_ref_filings(
    facts: dict[str, Any],
    base_ref_map: dict[str, str],
) -> dict[str, str]:
    """Override quarterly ref filings to prefer 10-K vintage."""
    fy_filings: dict[str, tuple[str, str]] = {}

    for ns_facts in facts.values():
        for tag_data in ns_facts.values():
            for entries in tag_data.get("units", {}).values():
                for entry in entries:
                    form = entry.get("form", "")

                    if form not in ANNUAL_FORMS:
                        continue

                    start = entry.get("start", "")
                    end = entry.get("end", "")
                    filed = entry.get("filed", "")

                    if not start or not end or not filed or start == end:
                        continue

                    try:
                        days = (
                            datetime.strptime(end, "%Y-%m-%d")
                            - datetime.strptime(start, "%Y-%m-%d")
                        ).days
                    except (ValueError, TypeError):
                        continue

                    if 300 <= days <= 400 and (
                        end not in fy_filings or filed < fy_filings[end][1]
                    ):
                        fy_filings[end] = (start, filed)

    if not fy_filings:
        return base_ref_map

    result = dict(base_ref_map)
    sorted_fys = sorted(fy_filings.keys())

    for date in base_ref_map:
        for fy_end in sorted_fys:
            fy_start, fy_filed = fy_filings[fy_end]
            if fy_start < date <= fy_end:
                result[date] = fy_filed
                break

    return result
