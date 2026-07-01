"""FFIEC CDR report-router client for the Executive Summary Report (ESR).

Fetches the full Executive Summary Report (report type 367) from
``POST /Public/router/Search``. The ESR exposes eight generic sections
(``SectionA`` .. ``SectionH``) that are concatenated into a single report, with
one value per reporting period rather than the UBPR bank/peer/percentile
triplet.
"""

from __future__ import annotations

import re
from typing import Any

from openbb_federal_reserve.utils.ubpr_report import (
    _caption,
    _post,
    rectangularize,
    report_cycles,
)

_REPORT_TYPE_ID = 367
_PERIOD = re.compile(r"^\d\d_\d\d_\d{4}$")


def report_sections() -> list[dict[str, str]]:
    """Return the ESR section table-of-contents (sectionid + caption)."""
    from openbb_federal_reserve.utils.cache import cached, seconds_until_next_release

    def _producer() -> list[dict[str, str]]:
        """Fetch the ESR section list."""
        return [
            row
            for row in _post("ReportPageSections", {"ReportTypeID": _REPORT_TYPE_ID})
            if isinstance(row, dict) and row.get("sectionid")
        ]

    return cached(
        "esr_sections",
        lambda: seconds_until_next_release("quarterly"),
        _producer,
    )


def _value(cell: str | None) -> float | None:
    """Parse a single ESR period cell into a number."""
    if not cell:
        return None
    try:
        return float(cell)
    except (TypeError, ValueError):
        return None


def _section_rows(
    section_id: str,
    rssd_id: str,
    period_keys: list[str],
    iso: dict[str, str],
    index: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    """Fetch and shape one ESR section's rows across the recent periods.

    Each line item's ``conceptname`` (a UBPR concept code) keys the concept
    index for its full name and monetary flag; monetary values are scaled out
    of thousands into actual dollars. The per-line concept code, indentation
    caption, MDRM name, and report line id are carried on each non-header row
    under ``_concept``, ``_caption``, ``_meta_name``, and ``_lineid`` so the
    caller can resolve the guide Description (label) and Narrative - addressed by
    the ESR's own line ids - once across every section.
    """
    from openbb_federal_reserve.utils.cache import cached, seconds_until_next_release

    def _producer() -> list[dict]:
        """Fetch the section's raw line rows for the bank."""
        return _post(
            "ReportSectionData",
            {
                "ID_RSSD": str(rssd_id),
                "SectionID": section_id,
                "ShowConfidential": 0,
            },
        )

    raw = cached(
        ("esr_section", str(rssd_id), section_id),
        lambda: seconds_until_next_release("quarterly"),
        _producer,
    )
    rows: list[dict[str, Any]] = []
    for line in sorted(raw, key=lambda r: int(r.get("displayorder") or 0)):
        caption = str(line.get("linecaption", ""))
        if caption == "#BlankLine#":
            continue
        is_header = caption.startswith("#SectionTitle#") or all(
            _value(line.get(k)) is None for k in period_keys
        )
        code = str(line.get("conceptname") or "")
        meta = index.get(code, {})
        caption_label = _caption(caption)
        record: dict[str, Any] = {
            "label": caption_label,
            "is_header": is_header,
            "narrative": None,
        }
        if not is_header:
            record["_concept"] = code
            record["_caption"] = caption_label
            record["_meta_name"] = meta.get("name")
            record["_lineid"] = str(line.get("lineid") or "")
            scale = 1000 if meta.get("monetary") else 1
            for key in period_keys:
                value = _value(line.get(key))
                record[iso[key]] = None if value is None else value * scale
        rows.append(record)
    return rows


def fetch_executive_summary(
    rssd_id: str, *, periods: int = 5, all_periods: bool = False
) -> list[dict[str, Any]]:
    """Fetch the Executive Summary Report as concatenated section rows.

    Returns one row per line item across all eight sections; each row is
    ``{label, is_header, narrative, <ISO date>: value}`` for the most recent
    ``periods`` reporting cycles, newest first. When ``all_periods`` is True the
    recent-periods cap is removed and every reported cycle is returned. Each
    non-header line's ``narrative`` is the FFIEC Interactive User's Guide
    definition of its concept.
    """
    from openbb_federal_reserve.utils.concepts import clean_name, concept_index
    from openbb_federal_reserve.utils.guide import fetch_guide_concepts

    sections = report_sections()
    if not sections:
        return []
    index = concept_index("ubpr_ratio_single", None)
    cycles = report_cycles() if all_periods else report_cycles()[:periods]
    period_keys = [
        f"{c['enddateformatted'][6:]}-{c['enddateformatted'][:2]}-"
        f"{c['enddateformatted'][3:5]}"
        for c in cycles
    ]
    underscore = {iso: f"{iso[5:7]}_{iso[8:10]}_{iso[:4]}" for iso in period_keys}
    keys = list(underscore.values())
    iso = {v: k for k, v in underscore.items()}

    rows: list[dict[str, Any]] = []
    for section in sorted(sections, key=lambda s: int(s.get("displayorder") or 0)):
        rows.extend(_section_rows(section["sectionid"], rssd_id, keys, iso, index))

    from openbb_federal_reserve.utils.concepts import indented_name

    esr_lines = {
        row["_concept"]: row["_lineid"]
        for row in rows
        if row.get("_concept") and row.get("_lineid")
    }
    guide = fetch_guide_concepts(list(esr_lines), lines=esr_lines) if esr_lines else {}
    for row in rows:
        code = row.pop("_concept", None)
        caption_label = row.pop("_caption", None)
        meta_name = row.pop("_meta_name", None)
        row.pop("_lineid", None)
        if code is None:
            continue
        entry = guide.get(code or "", {})
        label_name = clean_name(entry.get("description")) or meta_name
        row["label"] = indented_name(caption_label, label_name)
        row["narrative"] = entry.get("narrative") or index.get(code, {}).get(
            "narrative"
        )

    return rectangularize(rows)
