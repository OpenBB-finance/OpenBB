"""FR Y-9LP report structure generator.

Parses the FR Y-9LP (Parent Company Only Financial Statements for Large Holding
Companies) Reporting Central user guide PDF (Appendix A, the detailed field
specifications) into an ordered, hierarchical list of report items so the model
can render the form grouped by schedule and indent depth like the FR Y-9C
structure. The parsed result is committed as a static asset
(``assets/fry9lp/structure.json``); the live model loads that asset rather than
re-parsing the PDF at request time.

The FR Y-9LP appendix shares the FR Y-9C single-MDRM-per-line layout (no wide
column grids), so the shared :mod:`report_structure` Appendix A parser is reused
and driven by an FR Y-9LP :class:`~.report_structure.ReportConfig`; only the
report-specific banners, noise lines, schedule pattern and instructional-prose
filter live here. The public report's true item set is the union of the
value-bearing, non-admin codes across the sampled filers' latest-period
``ReturnFinancialReportCSV`` feeds; value-items whose code appears in no sampled
CSV (permanently-empty confidential and cover-page identity rows) are pruned so
the structure carries no dead, always-blank rows.

Run as a module to regenerate the asset::

    python -m openbb_federal_reserve.utils.fry9lp_structure

Pass ``--pdf <path>`` to parse a local copy instead of fetching the canonical
URL, and ``--csv <path>`` (repeatable) to supply saved per-institution CSVs for
the coverage union instead of fetching them live.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from openbb_federal_reserve.utils.report_structure import (
    MDRM,
    ReportConfig,
    parse_structure,
    summarize,
)

USER_GUIDE_URL = (
    "https://www.frbservices.org/binaries/content/assets/crsocms/"
    "central-bank/reporting-central/fry-9lp-user-guide.pdf"
)

# The large holding companies whose latest-period CSVs define the public report's
# true item set: the union of their value-bearing, non-admin codes.
VALIDATION_RPT = "FRY9LP"
VALIDATION_RSSDS = (1039502, 1073757)

# Cover/admin rows that never represent a public report value-item: institution
# identity and the report-date keys. Matched case-insensitively, with any
# ``DT``/``DT_*Q`` reporting-date row excluded by prefix.
_ADMIN_ITEM_NAMES = {
    "INSTITUTION NAME",
    "CITY AND STATE",
    "CITY",
    "STATE",
    "ZIP CODE",
    "STREET ADDRESS",
    "ID_RSSD",
    "REGULATORY DISTRICT",
    "BANK COUNT",
    "TOTAL ASSETS",
    "PEER_GRP",
    "REPORT DATE",
}

ASSET_PATH = (
    Path(__file__).resolve().parent.parent / "assets" / "fry9lp" / "structure.json"
)

# A schedule banner, e.g. "Schedule PI - Parent Company Only Income Statement",
# "Schedule PC-A - Investments in Subsidiaries and Associated Companies".
_SCHEDULE_HEADER = re.compile(r"^Schedule\s+([A-Z]{2}(?:-[A-Z])?)\s*[-–]\s*(.+)$")

_NOISE = {
    "report form",
    "line number",
    "item",
    "mdrm",
    "line number item",
    "financial data items",
    "text items",
}

_CONFIG = ReportConfig(
    appendix_banner="fr y- 9lp report detailed field specifications",
    schedule_header=_SCHEDULE_HEADER,
    noise=_NOISE,
    appendix_end=None,
    first_schedule=None,
    cover_schedule=("PI", "Parent Company Only Income Statement"),
    is_note_prose=lambda text: "to be completed" in text.lower(),
)

_COVER_SCHEDULE = ("COVER", "Cover Page")


def _fetch_pdf_bytes() -> bytes:
    """Download the canonical FR Y-9LP user guide PDF."""
    import requests

    response = requests.get(USER_GUIDE_URL, timeout=180)
    response.raise_for_status()
    return response.content


def _fetch_filer_csv(rssd: int) -> str:
    """Fetch one filer's latest-period per-institution CSV."""
    from openbb_federal_reserve.utils.ffiec import _fetch_bytes

    raw = _fetch_bytes(
        "FinancialReport/ReturnFinancialReportCSV"
        f"?rpt={VALIDATION_RPT}&id={rssd}&dt={_latest_quarter_end()}",
        referer="https://www.ffiec.gov/npw/FinancialReport/FinancialDataDownload",
    )
    return raw.decode("utf-8", "replace")


def _latest_quarter_end() -> str:
    """Return the most recent filed quarter-end as ``YYYYMMDD``."""
    from datetime import date

    today = date.today()
    quarter = (today.month - 1) // 3 + 1
    year = today.year
    # Step back to the prior quarter to land on a filed, available period.
    quarter -= 1
    if quarter == 0:
        quarter, year = 4, year - 1
    month_day = {1: "0331", 2: "0630", 3: "0930", 4: "1231"}[quarter]
    return f"{year}{month_day}"


def _hoist_cover_items(items: list[dict[str, Any]]) -> None:
    """Re-tag the trailing flat ``Cover Page`` block as its own COVER schedule.

    The cover-page contact and identification fields print as a flat
    "Cover Page <caption> <MDRM>" run after the numbered schedules; the shared
    parser leaves them under the active schedule, so move them into a dedicated
    ``COVER`` schedule and strip the redundant "Cover Page" caption prefix.
    """
    code, name = _COVER_SCHEDULE
    for item in items:
        caption = item["caption"]
        if caption.startswith("Cover Page ") and item["mdrm"]:
            item["schedule"] = code
            item["schedule_name"] = name
            item["caption"] = caption[len("Cover Page ") :].strip()
            item["level"] = 1
            item["line"] = None


def build_items(pdf_bytes: bytes) -> list[dict[str, Any]]:
    """Parse the FR Y-9LP user guide PDF into the ordered report structure."""
    items = parse_structure(pdf_bytes, _CONFIG)
    _hoist_cover_items(items)
    return items


def _csv_mdrms(csv_text: str) -> set[str]:
    """Return the value-bearing item codes in one filer's report CSV.

    Identity/admin rows (institution identity, the report-date keys, and any
    ``DT``/``DT_*Q`` row) are excluded, and only rows carrying a non-empty value
    are kept, so the result is the filer's true public value-item set.
    """
    import csv
    import io

    mdrms: set[str] = set()
    rows = list(csv.reader(io.StringIO(csv_text)))
    for row in rows[1:]:
        if len(row) < 3:
            continue
        name = row[0].strip()
        upper = name.upper()
        if upper in _ADMIN_ITEM_NAMES or upper.startswith("DT"):
            continue
        if not row[2].strip():
            continue
        mdrms.add(name)
    return mdrms


def _union_mdrms(csv_texts: list[str]) -> set[str]:
    """Return the union of value-bearing item codes across sampled filers."""
    union: set[str] = set()
    for text in csv_texts:
        union |= _csv_mdrms(text)
    return union


def _prune_permanent_empties(
    items: list[dict[str, Any]], union: set[str]
) -> list[dict[str, Any]]:
    """Drop value-items whose code appears in no sampled CSV.

    These are permanently-empty form rows (confidential indicators and the
    cover-page legal-title/address identity fields), which the public CSV feed
    never returns; keeping them would render dead, always-blank rows.
    """
    return [item for item in items if not (item["mdrm"] and item["mdrm"] not in union)]


def validate(items: list[dict[str, Any]], csv_texts: list[str]) -> dict[str, Any]:
    """Compare the structure's codes against the sampled filers' union.

    Reports both directions: ``coverage`` is the share of the union mapped to a
    structure value-item, and ``permanent_empty`` lists structure codes that
    appear in no sampled CSV (which must be empty).
    """
    structure_mdrms = {item["mdrm"] for item in items if item["mdrm"]}
    union = _union_mdrms(csv_texts)
    covered = union & structure_mdrms
    missing = sorted(union - structure_mdrms)
    permanent_empty = sorted(structure_mdrms - union)
    return {
        "csv_mdrm_count": len(union),
        "covered_count": len(covered),
        "missing": missing,
        "permanent_empty": permanent_empty,
        "coverage": round(100 * len(covered) / len(union), 2) if union else 0.0,
    }


def generate(
    pdf_path: str | None = None, csv_paths: list[str] | None = None
) -> dict[str, Any]:
    """Parse the user guide and return the structured asset payload.

    Permanently-empty value-items (codes absent from every sampled filer CSV)
    are pruned so the structure carries only items the public feed can populate.

    Parameters
    ----------
    pdf_path : str | None
        Local FR Y-9LP user guide PDF; fetched from ``USER_GUIDE_URL`` when
        omitted.
    csv_paths : list[str] | None
        Local per-institution CSVs defining the coverage union; fetched live for
        ``VALIDATION_RSSDS`` when omitted.
    """
    pdf_bytes = Path(pdf_path).read_bytes() if pdf_path else _fetch_pdf_bytes()
    items = build_items(pdf_bytes)
    csv_texts = (
        [Path(path).read_text(encoding="utf-8") for path in csv_paths]
        if csv_paths
        else [_fetch_filer_csv(rssd) for rssd in VALIDATION_RSSDS]
    )
    union = _union_mdrms(csv_texts)
    items = _prune_permanent_empties(items, union)
    payload = summarize(items, USER_GUIDE_URL)
    payload["validation"] = validate(items, csv_texts)
    return payload


def write_asset(
    pdf_path: str | None = None, csv_paths: list[str] | None = None
) -> Path:
    """Generate the structure and write it to the committed static asset."""
    payload = generate(pdf_path, csv_paths)
    ASSET_PATH.parent.mkdir(parents=True, exist_ok=True)
    ASSET_PATH.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return ASSET_PATH


def _main() -> None:
    """Command-line entry point for regenerating the asset."""
    import argparse

    parser = argparse.ArgumentParser(description="Regenerate the FR Y-9LP structure.")
    parser.add_argument("--pdf", default=None, help="Local user-guide PDF path.")
    parser.add_argument(
        "--csv",
        action="append",
        default=None,
        help="Local validation CSV path (repeatable for the coverage union).",
    )
    args = parser.parse_args()
    path = write_asset(args.pdf, args.csv)
    payload = json.loads(path.read_text(encoding="utf-8"))
    validation = payload["validation"]
    print(  # noqa: T201
        f"Wrote {path} -> {payload['schedule_count']} schedules, "
        f"{payload['item_count']} items, "
        f"coverage {validation['coverage']}% "
        f"({validation['covered_count']}/{validation['csv_mdrm_count']}), "
        f"missing {validation['missing']}, "
        f"permanent_empty {validation['permanent_empty']}"
    )


# Re-export for symmetry with the sibling generators and direct test access.
__all__ = [
    "MDRM",
    "USER_GUIDE_URL",
    "build_items",
    "generate",
    "validate",
    "write_asset",
]


if __name__ == "__main__":  # pragma: no cover - module-as-script entry guard
    _main()
