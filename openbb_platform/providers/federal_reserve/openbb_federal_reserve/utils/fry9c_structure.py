"""FR Y-9C report structure generator."""

from __future__ import annotations

import csv
import io
import json
import re
from pathlib import Path
from typing import Any

USER_GUIDE_URL = (
    "https://www.frbservices.org/binaries/content/assets/crsocms/"
    "central-bank/reporting-central/fr-y-9c-user-guide.pdf"
)

ASSET_PATH = (
    Path(__file__).resolve().parent.parent / "assets" / "fry9c" / "structure.json"
)

# FR Y-9C carries.
SAMPLE_FILERS = ("1039502", "1073757")

SAMPLE_PERIOD = "20260331"

_ADMIN_ITEMS = frozenset(
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
        "REPORT DATE",
    }
)

_CODE_RENAME = {"BHCTG512": "BHCKG512"}

_DROP_OCCURRENCE = frozenset(
    {("BHCKF632", "HC-D", "M.1.a.(2)"), ("BHCKG518", "HC-Q", "11")}
)

_REPLACE_COLUMN = {("HC-Q", "11", "BHCKG518"): "BHCKG522"}

_MISSING_ITEMS = {
    "BHCKHT67": ("HC-D", "Trading Assets and Liabilities", "M.1.b", 2),
    "BHCKJ458": ("HC-L", "Derivatives and Off-Balance-Sheet Items", "1.e.(2)", 3),
}

_GUIDE_TEXT_SCHEDULE = ("HC-M", "Memoranda")
_GUIDE_TEXT_BEFORE = "HC-B"
_GUIDE_TEXT_ITEMS = (
    ("M.2.a.(1)", "a. (1) Name of External Auditing Firm", "TEXTC703", 3),
    ("M.2.a.(2)", "(2) City", "TEXTC708", 4),
    ("M.2.a.(3)", "(3) State Abbreviation", "TEXTC714", 4),
    ("M.2.a.(4)", "(4) Zip Code", "TEXTC715", 4),
    ("M.2.b.(1)", "b. (1) Name of Engagement Partner", "TEXTC704", 3),
    ("M.2.b.(2)", "(2) E-mail Address", "TEXTC705", 4),
)

_MDRM = re.compile(r"\b[A-Z]{4}[A-Z0-9]{4}\b")

_COLUMN_LABEL = re.compile(r"\bColumn\s+[A-Z]\b")

_LINE_REF = re.compile(
    r"^(?:(?:M|[A-Z])\.)?\d+(?:\.[a-z])*(?:\.\(\d+\))*(?:\([a-z]\))*\.?(?:;)?"
)

_NOISE = {
    "report form",
    "line number",
    "item",
    "column a column b column c column d column e column f column g column h column i",
    "appendix a",
    "fr y-9c report detailed field specifications",
}

_FIRST_SCHEDULE = ("HI", "Consolidated Income Statement")
_COVER_SCHEDULE = ("COVER", "Cover Page")

_SCHEDULE_HEADER = re.compile(r"^Schedule\s+([A-Z]{1,2}(?:-[A-Z0-9]+)?)\b[.,]?\s*(.*)$")

_APPENDIX_BANNER = "fr y-9c report detailed field specifications"

_APPENDIX_END = "fr y-9c nonstandard financial items and text item character limits"


def _fetch_pdf_bytes() -> bytes:
    """Download the canonical FR Y-9C user guide PDF."""
    import requests

    response = requests.get(USER_GUIDE_URL, timeout=180)
    response.raise_for_status()
    return response.content


def _pdf_lines(pdf_bytes: bytes) -> list[str]:
    """Extract the appendix text as a flat list of stripped, non-empty lines."""
    from openbb_federal_reserve.utils.report_structure import read_pdf_pages

    lines: list[str] = []
    in_appendix = False
    for text in read_pdf_pages(pdf_bytes):
        for raw in text.splitlines():
            stripped = raw.strip()
            if not stripped:
                continue
            if not in_appendix:
                if stripped.lower() == _APPENDIX_BANNER:
                    in_appendix = True
                continue
            if stripped.lower() == _APPENDIX_END:
                return lines
            lines.append(stripped)
    return lines


def _is_noise(line: str) -> bool:
    """Return ``True`` for page running heads, banners, and bare page numbers."""
    lowered = line.lower()
    if lowered in _NOISE:
        return True
    if re.fullmatch(r"\d+", line):
        return True
    if lowered.startswith("8-character mdrm"):
        return True
    return line == "-"


def _level_from_reference(reference: str) -> int:
    """Derive the indent level from a line reference's nesting depth."""
    body = reference
    if body.startswith("M.") or re.match(r"^[A-Z]\.\d", body):
        body = body[2:]
    depth = 1
    depth += len(re.findall(r"\.[a-z](?![a-z])", body))
    depth += len(re.findall(r"\(\d+\)", body))
    depth += len(re.findall(r"\([a-z]\)", body))
    return depth


def _level_from_caption(caption: str) -> int:
    """Infer an indent level for an unreferenced section header from its bullet."""
    token = caption.split(" ", 1)[0]
    if re.match(r"^\([a-z]\)", token):
        return 4
    if re.match(r"^\(\d+\)", token):
        return 3
    if re.match(r"^[a-z]\.", token):
        return 2
    return 1


def _split_reference(line: str) -> tuple[str | None, str]:
    """Split a logical row into its line reference and caption text."""
    match = _LINE_REF.match(line)
    if not match or not match.group(0).rstrip(".;"):
        return None, line
    reference = match.group(0).rstrip(";").rstrip(".")
    caption = line[match.end() :].strip()
    return reference, caption


def _clean_caption(caption: str) -> str:
    """Collapse whitespace and strip data-type prefixes and filler dashes."""
    caption = re.sub(r"\s+", " ", caption).strip()
    caption = re.sub(r"^(?:TEXT|INTEGER|PERCENT|DATE|NUMBER)\s+", "", caption)
    caption = caption.rstrip(" -").strip()
    return caption


def _flush_row(  # noqa: PLR0913
    schedule: str,
    schedule_name: str,
    reference: str | None,
    caption: str,
    codes: list[str],
    items: list[dict[str, Any]],
) -> None:
    """Append one parsed logical row to ``items``."""
    caption = _clean_caption(caption)
    if not caption:
        return
    if (
        codes
        and all(code.startswith("TEXT") for code in codes)
        and re.search(r"\bDescription\b", caption)
    ):
        return
    is_header = not codes
    if reference is not None:
        level = _level_from_reference(reference)
    else:
        level = _level_from_caption(caption)
    items.append(
        {
            "schedule": schedule,
            "schedule_name": schedule_name,
            "line": reference,
            "caption": caption,
            "mdrm": codes[0] if codes else None,
            "columns": codes or None,
            "level": level,
            "is_header": is_header,
        }
    )


def parse_structure(pdf_bytes: bytes) -> list[dict[str, Any]]:
    """Parse the FR Y-9C user guide PDF into an ordered list of report items.

    Parameters
    ----------
    pdf_bytes : bytes
        The raw FR Y-9C Reporting Central user guide PDF.

    Returns
    -------
    list[dict[str, Any]]
        One record per logical report line in form order, each with the keys
        ``schedule``, ``schedule_name``, ``line``, ``caption``, ``mdrm``,
        ``columns``, ``level`` and ``is_header``. Itemization free-text
        ``TEXTxxxx`` descriptions are dropped; their paired numeric ``BHCxxxx``
        amount rows are kept.
    """
    lines = _pdf_lines(pdf_bytes)
    items: list[dict[str, Any]] = []

    schedule, schedule_name = _COVER_SCHEDULE
    seen_first_line_ref = False
    pending: list[str] = []

    def flush_pending() -> None:
        """Resolve the buffered physical lines into one logical row."""
        nonlocal pending
        if not pending:
            return
        joined = " ".join(pending)
        codes = _MDRM.findall(joined)
        reference, caption = _split_reference(_MDRM.sub("", joined).strip())
        _flush_row(schedule, schedule_name, reference, caption, codes, items)
        pending = []

    for raw_line in lines:
        line = _COLUMN_LABEL.sub("", raw_line).strip()
        line = re.sub(r"\s+", " ", line)
        if not line:
            continue
        if _is_noise(line):
            flush_pending()
            continue

        header_match = _SCHEDULE_HEADER.match(line)
        if (
            header_match
            and not _MDRM.search(line)
            and _is_schedule_banner(header_match)
        ):
            flush_pending()
            schedule = header_match.group(1)
            name = _clean_caption(header_match.group(2)).lstrip("- ").strip()
            schedule_name = name or schedule
            continue

        if re.match(r"^(?:(?:M|[A-Z])\.\S+\s+)?TEXT\b", line) and not re.search(
            r"\b(?:BH|RSSD)", line
        ):
            flush_pending()
            continue

        if not seen_first_line_ref and not re.match(
            r"^(?:TEXT|INTEGER|PERCENT|DATE|NUMBER)\b", line
        ):
            flush_pending()
            schedule, schedule_name = _FIRST_SCHEDULE
            seen_first_line_ref = True

        codes_only = _is_codes_only(line)
        if codes_only and not pending and items:
            previous = items[-1]
            previous_columns = list(previous["columns"] or [])
            previous_columns.extend(_MDRM.findall(line))
            previous["columns"] = previous_columns
            previous["mdrm"] = previous_columns[0]
            previous["is_header"] = False
            continue

        if _is_header_line(line):
            flush_pending()
            reference, caption = _split_reference(line)
            _flush_row(schedule, schedule_name, reference, caption, [], items)
            continue

        if _MDRM.search(line):
            pending.append(line)
            flush_pending()
            continue

        if pending:
            pending.append(line)
            continue
        if _opens_wrapped_item(line):
            pending.append(line)
        else:
            pending.append(line)
            flush_pending()

    flush_pending()
    return items


def _is_codes_only(line: str) -> bool:
    """Return ``True`` when a line is solely MDRM codes (a detached column row)."""
    if not _MDRM.search(line):
        return False
    return not _MDRM.sub("", line).strip()


def _is_schedule_banner(header_match: re.Match[str]) -> bool:
    """Return ``True`` when a ``Schedule X -`` line is a real schedule banner."""
    keyword = header_match.group(2).strip().lower()
    if keyword.startswith(("item", "items", "table", "part")):
        return False
    return not header_match.group(0).rstrip().endswith((",", ":"))


def _is_header_line(line: str) -> bool:
    """Return ``True`` when a code-less line is a standalone section header."""
    return bool(re.search(r"\s-$", line)) and not _MDRM.search(line)


def _opens_wrapped_item(line: str) -> bool:
    """Return ``True`` when a code-less line is the first line of a wrapped item."""
    reference, _ = _split_reference(line)
    return reference is not None and not line.rstrip().endswith(":")


def _is_admin_item(item_name: str) -> bool:
    """Return ``True`` for an identity/administrative CSV row, never a line item."""
    upper = item_name.upper().strip()
    return upper in _ADMIN_ITEMS or upper == "DT" or upper.startswith("DT_")


def _codes_of(item: dict[str, Any]) -> list[str]:
    """Return an item's MDRM column codes (``columns`` or the lone ``mdrm``)."""
    columns = item.get("columns")
    if columns:
        return list(columns)
    return [item["mdrm"]] if item.get("mdrm") else []


def collect_filed_set(
    filers: tuple[str, ...], date_str: str
) -> tuple[set[str], dict[str, str], list[str]]:
    """Fetch the sampled filings and return the public report's true item set.

    Parameters
    ----------
    filers : tuple[str, ...]
        RSSD identifiers of the filers to union.
    date_str : str
        The reporting period as ``YYYYMMDD``.

    Returns
    -------
    tuple[set[str], dict[str, str], list[str]]
        The union of value-bearing item codes across the filings excluding
        identity/administrative rows; a ``code -> Description`` map taken from
        the filings; and the first filer's value-bearing code sequence in filed
        order (used to anchor codes the guide appendix omits).
    """
    from openbb_federal_reserve.utils.structure_common import fetch_report_csv

    filed: set[str] = set()
    descriptions: dict[str, str] = {}
    first_order: list[str] = []
    for index, rssd in enumerate(filers):
        text = fetch_report_csv("FRY9C", int(rssd), date_str)
        for row in csv.reader(io.StringIO(text)):
            if len(row) < 3:
                continue
            name, description, value = row[0], row[1], row[2]
            if name == "ItemName" or _is_admin_item(name) or not value.strip():
                continue
            filed.add(name)
            if description.strip():
                descriptions[name] = description.strip()
            if index == 0:
                first_order.append(name)
    return filed, descriptions, first_order


def _caption_from_description(description: str) -> str:
    """Render an all-caps filing ``Description`` as a clean mixed-case caption."""
    text = re.sub(r"\s*\(BHC CONSOLIDATED\)\s*$", "", description, flags=re.IGNORECASE)
    text = re.sub(r"\s+", " ", text).strip().title()
    text = re.sub(r"\bHc\b", "HC", text)
    text = re.sub(r"\bHc-([A-Za-z])\b", lambda m: "HC-" + m.group(1).upper(), text)
    text = re.sub(r"\bHi\b", "HI", text)
    text = re.sub(r"\bHi-([A-Za-z])\b", lambda m: "HI-" + m.group(1).upper(), text)
    return re.sub(
        r"(\d)\.([A-Z])\.", lambda m: f"{m.group(1)}.{m.group(2).lower()}.", text
    )


def _apply_code_repairs(items: list[dict[str, Any]]) -> None:
    """Rename mis-OCR'd codes, repair grid cells, and drop duplicate occurrences."""
    for item in items:
        columns = item.get("columns")
        if not columns:
            continue
        repaired: list[str] = []
        for original in columns:
            code = _CODE_RENAME.get(original, original)
            code = _REPLACE_COLUMN.get((item["schedule"], item["line"], code), code)
            if (code, item["schedule"], item["line"]) in _DROP_OCCURRENCE:
                continue
            repaired.append(code)
        item["columns"] = repaired
        item["mdrm"] = repaired[0] if repaired else None


def _insert_text_descriptions(
    items: list[dict[str, Any]], filed: set[str]
) -> list[dict[str, Any]]:
    """Emit each filed itemization ``TEXTxxxx`` description before its amount row."""
    out: list[dict[str, Any]] = []
    for item in items:
        codes = _codes_of(item)
        if len(codes) == 1 and codes[0].startswith("BHCK"):
            text_code = "TEXT" + codes[0][4:]
            if text_code in filed:
                description = dict(item)
                description["caption"] = "Description"
                description["mdrm"] = text_code
                description["columns"] = [text_code]
                out.append(description)
        out.append(item)
    return out


def _insert_missing_items(
    items: list[dict[str, Any]],
    filed: set[str],
    descriptions: dict[str, str],
    first_order: list[str],
) -> None:
    """Insert filed codes the guide omits at their filed position with a caption."""
    for code, (schedule, schedule_name, line, level) in _MISSING_ITEMS.items():
        if code not in filed or code not in first_order:
            continue
        index = {c: i for i, item in enumerate(items) for c in _codes_of(item)}
        anchor = None
        position = first_order.index(code)
        for prior in range(position - 1, -1, -1):
            if first_order[prior] in index:
                anchor = index[first_order[prior]]
                break
        if anchor is None:
            continue
        items.insert(
            anchor + 1,
            {
                "schedule": schedule,
                "schedule_name": schedule_name,
                "line": line,
                "caption": _caption_from_description(descriptions.get(code, code)),
                "mdrm": code,
                "columns": [code],
                "level": level,
                "is_header": False,
            },
        )


def _insert_guide_text_block(items: list[dict[str, Any]]) -> None:
    """Restore the all-text HC-M auditor block the appendix parser drops."""
    schedule, schedule_name = _GUIDE_TEXT_SCHEDULE
    anchor = next(
        (i for i, item in enumerate(items) if item["schedule"] == _GUIDE_TEXT_BEFORE),
        None,
    )
    if anchor is None:
        return
    block = [
        {
            "schedule": schedule,
            "schedule_name": schedule_name,
            "line": line,
            "caption": caption,
            "mdrm": code,
            "columns": [code],
            "level": level,
            "is_header": False,
        }
        for line, caption, code, level in _GUIDE_TEXT_ITEMS
    ]
    items[anchor:anchor] = block


def _prune_to_filed(
    items: list[dict[str, Any]], filed: set[str]
) -> list[dict[str, Any]]:
    """Drop value columns and rows absent from every sampled filing."""
    kept: list[dict[str, Any]] = []
    for item in items:
        if item.get("is_header"):
            kept.append(item)
            continue
        columns = _codes_of(item)
        if not columns:
            kept.append(item)
            continue
        filed_columns = [code for code in columns if code in filed]
        if not filed_columns:
            continue
        item["columns"] = filed_columns
        item["mdrm"] = filed_columns[0]
        kept.append(item)

    final: list[dict[str, Any]] = []
    for position, item in enumerate(kept):
        if item.get("is_header") and not _header_has_child(kept, position):
            continue
        final.append(item)
    return final


def _header_has_child(items: list[dict[str, Any]], position: int) -> bool:
    """Return ``True`` when a header at ``position`` has a value item beneath it."""
    level = items[position]["level"]
    for item in items[position + 1 :]:
        if item.get("is_header") and item["level"] <= level:
            return False
        if not item.get("is_header"):
            return True
    return False


def reconcile(
    items: list[dict[str, Any]],
    filers: tuple[str, ...] = SAMPLE_FILERS,
    date_str: str | None = None,
) -> list[dict[str, Any]]:
    """Reconcile the parsed guide layout against the report as actually filed.

    Parameters
    ----------
    items : list[dict[str, Any]]
        The ordered items parsed from the user guide.
    filers : tuple[str, ...], optional
        RSSD identifiers whose union defines the filed item set.
    date_str : str, optional
        The reporting period as ``YYYYMMDD``; defaults to :data:`SAMPLE_PERIOD`.

    Returns
    -------
    list[dict[str, Any]]
        The reconciled items: appendix code repairs applied, filed itemization
        descriptions and guide-omitted codes inserted, and every value item whose
        columns are absent from all sampled filings removed.
    """
    date_str = date_str or SAMPLE_PERIOD
    filed, descriptions, first_order = collect_filed_set(filers, date_str)
    items = [dict(item) for item in items]
    _apply_code_repairs(items)
    items = _insert_text_descriptions(items, filed)
    _insert_missing_items(items, filed, descriptions, first_order)
    _insert_guide_text_block(items)
    return _prune_to_filed(items, filed)


def generate(pdf_path: str | None = None, offline: bool = False) -> dict[str, Any]:
    """Parse the user guide, reconcile against filings, and return the payload."""
    pdf_bytes = Path(pdf_path).read_bytes() if pdf_path else _fetch_pdf_bytes()
    items = parse_structure(pdf_bytes)
    if not offline:
        items = reconcile(items)
    schedules: list[dict[str, str]] = []
    seen: set[str] = set()
    for item in items:
        code = item["schedule"]
        if code not in seen:
            seen.add(code)
            schedules.append({"schedule": code, "name": item["schedule_name"]})
    return {
        "source": USER_GUIDE_URL,
        "schedule_count": len(schedules),
        "item_count": len(items),
        "schedules": schedules,
        "items": items,
    }


def write_asset(pdf_path: str | None = None, offline: bool = False) -> Path:
    """Generate the structure and write it to the committed static asset."""
    payload = generate(pdf_path, offline=offline)
    ASSET_PATH.parent.mkdir(parents=True, exist_ok=True)
    ASSET_PATH.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return ASSET_PATH


def _main() -> None:
    """Command-line entry point for regenerating the asset."""
    import argparse

    parser = argparse.ArgumentParser(description="Regenerate the FR Y-9C structure.")
    parser.add_argument("--pdf", default=None, help="Local PDF path to parse.")
    parser.add_argument(
        "--offline",
        action="store_true",
        help="Skip reconciliation against live filings.",
    )
    args = parser.parse_args()
    path = write_asset(args.pdf, offline=args.offline)
    payload = json.loads(path.read_text(encoding="utf-8"))
    print(  # noqa: T201
        f"Wrote {path} -> {payload['schedule_count']} schedules, "
        f"{payload['item_count']} items"
    )


if __name__ == "__main__":  # pragma: no cover - module-as-script entry guard
    _main()
