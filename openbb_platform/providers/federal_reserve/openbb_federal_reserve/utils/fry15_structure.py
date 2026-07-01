"""FR Y-15 report structure generator.

Parses the FR Y-15 (Banking Organization Systemic Risk Report) Reporting
Central transfer user guide PDF into an ordered, hierarchical list of report
items so the model can render the form grouped by schedule and indent depth like
the FR Y-9C structure. Three sources are combined:

* The user guide's *Line Identifiers to be used for FRY15* table supplies the
  ordered ``schedule``/``line``/``mdrm`` mapping for every directly reported
  cell.
* The user guide's *FR Y-15 Items NOT to Include in the XML File* table supplies
  the calculated / auto-populated MDRMs that are excluded from the line table
  but still appear in a filer's report (their cell values are derived by
  Reporting Central or pulled from FFIEC 009 / FFIEC 101 / FR Y-9C / FR Y-9LP).
* The official FR Y-15 blank report form PDF supplies the schedule titles, and
  the live per-institution ``ReturnFinancialReportCSV`` feed supplies the
  per-MDRM captions (the user guide's line table carries no captions for the
  numbered schedule lines).

The committed structure is filtered to the union of value-bearing codes the
sampled filers actually report: a code no sampled filer reports (an IHC/FBO
Schedule H-N column, a confidential grid, or a cover-page identity field) is a
permanently-empty form row and is excluded.

The parsed result is committed as a static asset
(``assets/fry15/structure.json``); the live model loads that asset rather than
re-parsing the PDFs at request time.

Run as a module to regenerate the asset::

    python -m openbb_federal_reserve.utils.fry15_structure

Pass ``--guide``/``--form``/``--csv`` to parse local copies instead of fetching
the canonical URLs.
"""

from __future__ import annotations

import csv
import io
import json
import re
from pathlib import Path
from typing import Any

GUIDE_URL = (
    "https://www.frbservices.org/binaries/content/assets/crsocms/"
    "central-bank/reporting-central/fry15-transfer-user-guide.pdf"
)

FORM_URL = (
    "https://www.federalreserve.gov/apps/reportingforms/Download/"
    "DownloadAttachment?guid=3395b1c6-6204-4954-813e-1f52136bf572"
)

CSV_URL = (
    "https://www.ffiec.gov/npw/FinancialReport/ReturnFinancialReportCSV"
    "?rpt=FRY15&id={rssd}&dt={date}"
)

# The domestic-HC filers sampled to define the public item set and source the
# ``RISK``/``RSSD`` captions. Both are large domestic holding companies whose
# filings carry the Schedule A-G and cover-page columns; codes neither filer
# reports (the IHC/FBO Schedule H-N columns and confidential grids) are
# permanently empty and excluded from the committed structure.
VALIDATION_RSSD = 1039502
VALIDATION_DATE = "20260331"
CAPTION_RSSDS = (1039502, 1073757)

ASSET_PATH = (
    Path(__file__).resolve().parent.parent / "assets" / "fry15" / "structure.json"
)

# An 8-character MDRM item code: a 4-letter prefix then 4 alphanumerics.
_MDRM = re.compile(r"^[A-Z]{4}[A-Z0-9]{4}$")

# One row of the *Line Identifiers* table: the reported MDRM (optionally
# footnote-starred), the "Schedule X, line" / "Cover Page, ..." descriptor, the
# ``L``-prefixed line identifier (whose 8 trailing characters are the canonical
# MDRM), and the data-value length.
_LINE_ROW = re.compile(
    r"^([A-Z]{4}[A-Z0-9]{4})\s*\**\s+"
    r"(Schedule [A-Z][^L]*?|Cover Page,.*?|Optional Narrative Statement)\s+"
    r"L([A-Z]{4}[A-Z0-9]{4})\s+\d+\s*$"
)

# One row of the *Items NOT to Include in the XML File* table: the calculated
# MDRM and its source series, followed by an effective start/end date pair.
_CALC_ROW = re.compile(
    r"^([A-Z]{4}[A-Z0-9]{4})\s+"
    r"(FR Y-9C|FR Y-9LP|FFIEC 101|FFIEC 009|FR Y-15)\s+"
    r"\d+/\d+/\d+\s+\d+/\d+/\d+$"
)

# A schedule heading in the blank form, e.g. "Schedule A—Size Indicator".
_FORM_SCHEDULE = re.compile(r"Schedule\s+([A-N])[—–-]\s*([A-Z][A-Za-z \-]+)")

# The schedule/line descriptor split, e.g. "Schedule A, 1.a." or
# "Schedule N, Part I, 2.b" or "Cover Page, Name of CFO".
_DESCRIPTOR = re.compile(
    r"^(Schedule [A-Z](?:, Part [IVX]+)?|Cover Page|Optional Narrative Statement)"
    r"(?:,\s*(.*))?$"
)

# The reported-cell column the per-entity-type MDRM prefix denotes: domestic HC
# (``RISK``), the IHC column (``RISI``), the FBO column (``RISO``), and the
# cover-page identification fields (``RSSD``).
_COLUMN_BY_PREFIX = {
    "RISK": None,
    "RISI": "IHC",
    "RISO": "FBO",
    "RSSD": None,
}

# CSV ``ItemName`` rows carrying institution identity or administrative metadata
# rather than a reported value; these never become structure value-items and are
# excluded from the value-bearing-code union that defines the public item set.
_IDENTITY_ITEM_NAMES = frozenset(
    {
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
    }
)

# CSV ``Description`` values flagging an administrative or total-asset row whose
# MDRM-shaped ``ItemName`` still must be excluded from the value-bearing union.
_IDENTITY_DESCRIPTIONS = frozenset({"TOTAL ASSETS"})


def _fetch_bytes(url: str) -> bytes:
    """Download a canonical source URL as raw bytes.

    The FFIEC per-institution CSV endpoint sits behind Cloudflare and is fetched
    through the shared browser-impersonating session; the public PDFs are served
    by ordinary clients.
    """
    if "ffiec.gov" in url:
        from openbb_federal_reserve.utils.curl_session import get_session

        def warmup(session: Any) -> None:
            session.get("https://www.ffiec.gov/npw/", timeout=30)

        session = get_session("ffiec_nic", warmup)
        response = session.get(
            url, headers={"Referer": "https://www.ffiec.gov/npw/"}, timeout=180
        )
        response.raise_for_status()
        return response.content

    import requests

    response = requests.get(url, timeout=180)
    response.raise_for_status()
    return response.content


def _pdf_lines(pdf_bytes: bytes) -> list[list[str]]:
    """Return each page's collapsed-whitespace, non-empty lines."""
    from pypdf import PdfReader

    reader = PdfReader(io.BytesIO(pdf_bytes))
    pages: list[list[str]] = []
    for page in reader.pages:
        text = page.extract_text() or ""
        lines = [re.sub(r"\s+", " ", raw).strip() for raw in text.splitlines()]
        pages.append([line for line in lines if line])
    return pages


# A numbered/lettered form caption whose trailing colon marks a sub-header that
# introduces indented child lines, e.g. "1. Derivative exposures:".
_FORM_SUBHEADER = re.compile(r"^(?:M\.)?\d+\.\s+(.*\S):$|^[a-z]\.\s+(.*\S):$")


def _schedule_titles(form_bytes: bytes) -> dict[str, str]:
    """Extract the schedule-letter to title map from the blank form PDF."""
    pages = _pdf_lines(form_bytes)
    text = "\n".join(line for page in pages for line in page)
    titles: dict[str, str] = {}
    for match in _FORM_SCHEDULE.finditer(text):
        title = re.sub(r"\s+", " ", match.group(2)).strip()
        if title.lower().startswith("continued"):
            continue
        titles.setdefault(match.group(1), title.replace("Short-T erm", "Short-Term"))
    return titles


def _normalize(text: str) -> str:
    """Lowercase and collapse a caption for whitespace-insensitive matching."""
    return re.sub(r"\s+", " ", text).strip().lower()


def _form_subheaders(form_bytes: bytes) -> dict[str, str]:
    """Map normalized sub-header text to its canonical form caption.

    The blank form marks a section sub-header with a numbered/lettered caption
    that ends in a colon (``"1. Derivative exposures:"``). This whitelist is used
    to confirm which CSV-description colon-prefixes are genuine sub-headers,
    filtering out source-data typos and spurious all-caps prefixes that would
    otherwise be misread as headers.
    """
    headers: dict[str, str] = {}
    for line in (line for page in _pdf_lines(form_bytes) for line in page):
        clean = re.sub(r"\.{2,}.*$", "", line).strip()
        match = _FORM_SUBHEADER.match(clean)
        if match:
            caption = (match.group(1) or match.group(2)).strip()
            headers.setdefault(_normalize(caption), caption)
    return headers


def _parse_line_table(guide_pages: list[list[str]]) -> list[dict[str, str]]:
    """Parse the *Line Identifiers* table into ordered MDRM/descriptor rows.

    A descriptor caption can wrap across two or three physical lines (the
    ``L``-prefixed identifier always terminates the row), so physical lines are
    buffered until they resolve into one complete table row.
    """
    rows: list[dict[str, str]] = []
    buffer: list[str] = []
    for page in guide_pages:
        for line in page:
            candidate = " ".join([*buffer, line]).strip()
            match = _LINE_ROW.match(candidate)
            if match:
                rows.append(
                    {
                        "mdrm": match.group(3),
                        "descriptor": match.group(2).strip(),
                    }
                )
                buffer = []
            elif _MDRM.match(line.split(" ", 1)[0]):
                buffer = [line]
            elif buffer:
                buffer.append(line)
    return rows


def _parse_calc_table(guide_pages: list[list[str]]) -> list[dict[str, str]]:
    """Parse the *Items NOT to Include in the XML File* table.

    These calculated / auto-populated MDRMs are excluded from the line table but
    still appear in a filer's report; each row pairs an MDRM with its source
    series.
    """
    rows: list[dict[str, str]] = []
    for page in guide_pages:
        for line in page:
            match = _CALC_ROW.match(line)
            if match:
                rows.append({"mdrm": match.group(1), "source": match.group(2)})
    return rows


def _csv_descriptions(csv_bytes: bytes) -> dict[str, str]:
    """Map each MDRM to its caption from the per-institution report CSV."""
    reader = csv.reader(io.StringIO(csv_bytes.decode("utf-8-sig", "ignore")))
    descriptions: dict[str, str] = {}
    for row in reader:
        if len(row) >= 2 and _MDRM.match(row[0]):
            descriptions[row[0]] = re.sub(r"\s+", " ", row[1]).strip()
    return descriptions


def _split_descriptor(descriptor: str) -> tuple[str, str | None, str | None]:
    """Split a table descriptor into ``schedule``, ``part`` and ``line``."""
    match = _DESCRIPTOR.match(descriptor)
    if not match:
        return descriptor, None, None
    head, line = match.group(1), match.group(2)
    part = None
    schedule_match = re.match(r"Schedule ([A-Z])(?:, Part ([IVX]+))?", head)
    if schedule_match:
        schedule = schedule_match.group(1)
        part = schedule_match.group(2)
    else:
        schedule = head
    line = re.sub(r"\.\s+", ".", (line or "").strip()).rstrip(".") or None
    return schedule, part, line


def _level_from_line(line: str | None) -> int:
    """Derive the indent level from a form line reference's nesting depth."""
    if not line:
        return 1
    body = re.sub(r"^(?:M|[A-Z])\.", "", line)
    depth = 1
    depth += len(re.findall(r"\.[a-z](?![a-z])", body))
    depth += len(re.findall(r"\(\d+\)", body))
    depth += len(re.findall(r"\([a-z]\)", body))
    return depth


def _split_caption_header(
    caption: str, subheaders: dict[str, str]
) -> tuple[str | None, str]:
    """Split a ``Header: leaf`` caption into its sub-header and leaf text.

    Many FR Y-15 captions embed the section sub-header before a colon
    (``"Derivative exposures: Current exposure of derivative contracts"``). The
    sub-header is surfaced as a separate ``is_header`` item rather than
    concatenated onto every leaf caption, but only when the prefix matches a
    sub-header confirmed by the blank form's ``subheaders`` whitelist; otherwise
    the colon is part of the leaf caption and is kept intact.
    """
    head, sep, tail = caption.partition(":")
    if not sep or not tail.strip():
        return None, caption
    canonical = subheaders.get(_normalize(head))
    if canonical is None:
        return None, caption
    return canonical, tail.strip()


def _merge_descriptions(caption_csvs: list[bytes]) -> dict[str, str]:
    """Merge per-institution CSV captions, first non-empty caption winning."""
    descriptions: dict[str, str] = {}
    for csv_bytes in caption_csvs:
        for code, caption in _csv_descriptions(csv_bytes).items():
            descriptions.setdefault(code, caption)
    return descriptions


def _value_codes(csv_bytes: bytes) -> set[str]:
    """Return one CSV's value-bearing MDRM codes, excluding identity rows.

    A value-bearing row has an MDRM-shaped ``ItemName`` and is neither an
    identity/administrative item name nor a total-asset/administrative
    description; the resulting set is the filer's reported public item set.
    """
    reader = csv.reader(io.StringIO(csv_bytes.decode("utf-8-sig", "ignore")))
    codes: set[str] = set()
    for row in reader:
        if len(row) < 3:
            continue
        name, description = row[0].strip(), row[1].strip()
        if not _MDRM.match(name):
            continue
        if name.upper() in _IDENTITY_ITEM_NAMES or name.upper().startswith("DT"):
            continue
        if description.upper() in _IDENTITY_DESCRIPTIONS:
            continue
        codes.add(name)
    return codes


def _value_codes_union(caption_csvs: list[bytes]) -> set[str]:
    """Return the union of value-bearing codes across the sampled filers.

    This union is the public report's true item set: a code that no sampled
    filer reports is a permanently-empty form row (a confidential grid or an
    other-entity-type column) and is excluded from the committed structure.
    """
    union: set[str] = set()
    for csv_bytes in caption_csvs:
        union |= _value_codes(csv_bytes)
    return union


def _clean_caption(caption: str) -> str:
    """Strip source artifacts from a CSV-sourced caption.

    A handful of FFIEC ``Description`` cells carry a stray leading capital glued
    to the first word (``"DOther off-balance sheet exposures: ..."``); the stray
    letter is removed when the remainder begins a normally-capitalised word.
    """
    match = re.match(r"^[A-Z]([A-Z][a-z].*)$", caption)
    if match:
        return match.group(1)
    return caption


def build_items(  # noqa: PLR0912
    guide_bytes: bytes,
    form_bytes: bytes,
    caption_csvs: list[bytes],
) -> tuple[list[dict[str, Any]], dict[str, str]]:
    """Assemble the ordered FR Y-15 structure and the schedule-title map."""
    guide_pages = _pdf_lines(guide_bytes)
    titles = _schedule_titles(form_bytes)
    subheaders = _form_subheaders(form_bytes)
    descriptions = _merge_descriptions(caption_csvs)
    union = _value_codes_union(caption_csvs)
    line_rows = _parse_line_table(guide_pages)
    calc_rows = _parse_calc_table(guide_pages)

    titles.setdefault("COVER", "Cover Page")
    titles.setdefault("NARRATIVE", "Optional Narrative Statement")
    titles.setdefault("CALCULATED", "Calculated and Auto-Populated Items")

    items: list[dict[str, Any]] = []
    emitted_header: dict[tuple[str, str | None, str], bool] = {}

    def append_item(  # noqa: PLR0913
        schedule: str,
        schedule_name: str,
        line: str | None,
        caption: str,
        mdrm: str | None,
        level: int,
        is_header: bool,
        source: str | None = None,
    ) -> None:
        item: dict[str, Any] = {
            "schedule": schedule,
            "schedule_name": schedule_name,
            "line": line,
            "caption": caption,
            "mdrm": mdrm,
            "columns": [mdrm] if mdrm else None,
            "level": level,
            "is_header": is_header,
        }
        if source is not None:
            item["source"] = source
        items.append(item)

    for row in line_rows:
        if row["mdrm"] not in union:
            continue
        schedule, part, line = _split_descriptor(row["descriptor"])
        prefix = row["mdrm"][:4]
        if schedule == "Cover Page":
            schedule_code, schedule_name = "COVER", titles["COVER"]
        elif schedule == "Optional Narrative Statement":
            schedule_code, schedule_name = "NARRATIVE", titles["NARRATIVE"]
        else:
            schedule_code = f"{schedule}-{part}" if part else schedule
            schedule_name = titles.get(schedule, schedule)
            if part:
                schedule_name = f"{schedule_name} - Part {part}"
        caption = _clean_caption(descriptions.get(row["mdrm"], line or row["mdrm"]))
        sub_header, leaf = _split_caption_header(caption, subheaders)
        level = _level_from_line(line)
        if sub_header is not None:
            header_key = (schedule_code, None, sub_header)
            if header_key not in emitted_header:
                emitted_header[header_key] = True
                append_item(
                    schedule_code,
                    schedule_name,
                    None,
                    sub_header,
                    None,
                    max(level - 1, 1),
                    True,
                )
        column = _COLUMN_BY_PREFIX.get(prefix)
        if column:
            leaf = f"{leaf} ({column})"
        append_item(
            schedule_code,
            schedule_name,
            line,
            leaf,
            row["mdrm"],
            level + (1 if sub_header is not None else 0),
            False,
        )

    seen = {item["mdrm"] for item in items if item["mdrm"]}
    for row in calc_rows:
        if row["mdrm"] not in union or row["mdrm"] in seen:
            continue
        seen.add(row["mdrm"])
        caption = _clean_caption(descriptions.get(row["mdrm"], row["mdrm"]))
        _, leaf = _split_caption_header(caption, subheaders)
        append_item(
            "CALCULATED",
            titles["CALCULATED"],
            None,
            leaf,
            row["mdrm"],
            1,
            False,
            source=row["source"],
        )

    for code in sorted(union - seen):
        seen.add(code)
        caption = _clean_caption(descriptions.get(code, code))
        _, leaf = _split_caption_header(caption, subheaders)
        append_item("COVER", titles["COVER"], None, leaf, code, 1, False)

    items = _prune_empty_headers(items)

    return items, titles


def _prune_empty_headers(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Drop sub-section headers left without any surviving valued descendant.

    Filtering value-items to the sampled union can leave a ``is_header`` row
    whose children were all permanently-empty other-entity-type columns; such a
    header introduces no value and is removed so no orphan header survives.
    """
    kept: list[dict[str, Any]] = []
    for index, item in enumerate(items):
        if not item["is_header"]:
            kept.append(item)
            continue
        has_child = False
        for follower in items[index + 1 :]:
            if follower["schedule"] != item["schedule"]:
                break
            if follower["is_header"] and follower["level"] <= item["level"]:
                break
            if not follower["is_header"] and follower["level"] > item["level"]:
                has_child = True
                break
        if has_child:
            kept.append(item)
    return kept


def validate(items: list[dict[str, Any]], caption_csvs: list[bytes]) -> dict[str, Any]:
    """Compare the structure's MDRMs against the sampled filers' value codes.

    The ``union`` is every value-bearing code across the sampled CSVs (the public
    item set); ``coverage`` is the share of that union mapped to a structure
    value-item, and ``permanent_empty`` is the count of structure value-items
    carrying a code no sampled filer reports.
    """
    union = _value_codes_union(caption_csvs)
    structure_mdrms = {item["mdrm"] for item in items if item["mdrm"]}
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
    guide_path: str | None = None,
    form_path: str | None = None,
    csv_paths: list[str] | None = None,
) -> dict[str, Any]:
    """Parse the sources and return the structured asset payload.

    Parameters
    ----------
    guide_path : str | None
        Local FR Y-15 transfer user guide PDF; fetched from ``GUIDE_URL`` when
        omitted.
    form_path : str | None
        Local FR Y-15 blank form PDF; fetched from ``FORM_URL`` when omitted.
    csv_paths : list[str] | None
        Local per-institution CSVs supplying captions and the value-bearing-code
        union. Fetched for ``CAPTION_RSSDS`` when omitted.
    """
    guide_bytes = (
        Path(guide_path).read_bytes() if guide_path else _fetch_bytes(GUIDE_URL)
    )
    form_bytes = Path(form_path).read_bytes() if form_path else _fetch_bytes(FORM_URL)
    if csv_paths:
        caption_csvs = [Path(path).read_bytes() for path in csv_paths]
    else:
        caption_csvs = [
            _fetch_bytes(CSV_URL.format(rssd=rssd, date=VALIDATION_DATE))
            for rssd in CAPTION_RSSDS
        ]
    items, _ = build_items(guide_bytes, form_bytes, caption_csvs)
    schedules: list[dict[str, str]] = []
    seen: set[str] = set()
    for item in items:
        code = item["schedule"]
        if code not in seen:
            seen.add(code)
            schedules.append({"schedule": code, "name": item["schedule_name"]})
    validation = validate(items, caption_csvs)
    return {
        "source": GUIDE_URL,
        "form_source": FORM_URL,
        "caption_source": CSV_URL.format(rssd=VALIDATION_RSSD, date=VALIDATION_DATE),
        "schedule_count": len(schedules),
        "item_count": len(items),
        "validation": validation,
        "schedules": schedules,
        "items": items,
    }


def write_asset(
    guide_path: str | None = None,
    form_path: str | None = None,
    csv_paths: list[str] | None = None,
) -> Path:
    """Generate the structure and write it to the committed static asset."""
    payload = generate(guide_path, form_path, csv_paths)
    ASSET_PATH.parent.mkdir(parents=True, exist_ok=True)
    ASSET_PATH.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return ASSET_PATH


def _main() -> None:
    """Command-line entry point for regenerating the asset."""
    import argparse

    parser = argparse.ArgumentParser(description="Regenerate the FR Y-15 structure.")
    parser.add_argument("--guide", default=None, help="Local user-guide PDF path.")
    parser.add_argument("--form", default=None, help="Local blank-form PDF path.")
    parser.add_argument(
        "--csv",
        action="append",
        default=None,
        help="Local per-institution caption CSV (repeatable; the sampled union).",
    )
    args = parser.parse_args()
    path = write_asset(args.guide, args.form, args.csv)
    payload = json.loads(path.read_text(encoding="utf-8"))
    validation = payload["validation"]
    print(  # noqa: T201
        f"Wrote {path} -> {payload['schedule_count']} schedules, "
        f"{payload['item_count']} items, "
        f"coverage {validation['coverage']}% "
        f"({validation['covered_count']}/{validation['csv_mdrm_count']}), "
        f"missing {validation['missing']}, "
        f"permanent_empty {len(validation['permanent_empty'])}"
    )


if __name__ == "__main__":  # pragma: no cover - module-as-script entry guard
    _main()
