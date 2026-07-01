"""FR Y-9C report structure generator.

Parses the FR Y-9C Reporting Central user guide PDF (Appendix A, the detailed
field specifications) into an ordered, hierarchical list of report items so the
model can render the form grouped by schedule and indent depth like UBPR, then
reconciles the parsed layout against the public report as actually filed.

The user guide is the caption and ordering authority; a sample of real filings
(see ``SAMPLE_FILERS``) is the truth filter for which items a public FR Y-9C
carries. Reconciliation (:func:`reconcile`) keeps the guide's structure but
drops any value item whose MDRM columns are absent from every sampled filing
(non-applicable form rows and confidential grids), emits the free-text
``TEXTxxxx`` description half of each itemization pair that the filings report,
inserts the handful of filed codes the guide's appendix omits, and repairs the
appendix's mis-OCR'd column codes.

The reconciled result is committed as a static asset
(``assets/fry9c/structure.json``); the live model loads that asset rather than
re-parsing the PDF at request time.

Run as a module to regenerate the asset::

    python -m openbb_federal_reserve.utils.fry9c_structure

Pass ``--pdf <path>`` to parse a local copy instead of fetching the canonical
URL. Reconciliation fetches the sampled filings over the network unless
``--offline`` is given, in which case the raw guide layout is written as-is.
"""

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

# Large top-tier filers whose public FR Y-9C, taken in union, defines the
# report's true item set for reconciliation. JPMorgan Chase & Co. and Bank of
# America Corporation between them populate the broad set of schedules a public
# FR Y-9C carries.
SAMPLE_FILERS = ("1039502", "1073757")

# The reporting period the committed structure is reconciled against: the latest
# filing both sample filers report under the current form revision. Pinned rather
# than tracking the current quarter so the asset is reproducible and stable, but
# advanced to each new revision so the committed structure covers every line the
# form adds (the March 2026 revision introduced the nondepository-financial-
# institution and structured-product breakouts now carried here).
SAMPLE_PERIOD = "20260331"

# ``ItemName`` values in the CSV that are reporting-entity identity or
# administrative metadata, never report line items; excluded from the filed item
# set and never rendered. ``DT`` / ``DT_*`` date stamps are handled separately.
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

# Appendix column codes the guide PDF mis-OCR'd: the printed prefix differs by
# one letter from the MDRM the report actually files. Mapped to the filed code.
_CODE_RENAME = {"BHCTG512": "BHCKG512"}

# ``(code, schedule, line)`` occurrences where the guide appendix repeats a code
# onto a second, wrong row (a PDF column-spacing artifact); dropped so each code
# maps to exactly one item.
_DROP_OCCURRENCE = frozenset(
    {("BHCKF632", "HC-D", "M.1.a.(2)"), ("BHCKG518", "HC-Q", "11")}
)

# ``(schedule, line, code) -> code`` substitutions repairing an appendix grid row
# whose printed column code belongs to a different line. HC-Q item 11's fourth
# printed column is the mis-placed ``BHCKG518`` (Other trading liabilities); the
# filed code for that cell is ``BHCKG522``.
_REPLACE_COLUMN = {("HC-Q", "11", "BHCKG518"): "BHCKG522"}

# Filed codes the guide appendix omits entirely, placed at their schedule line
# with a caption taken from the filing's own ``Description`` column. Keyed by
# code -> ``(schedule, schedule_name, line, level)``.
_MISSING_ITEMS = {
    "BHCKHT67": ("HC-D", "Trading Assets and Liabilities", "M.1.b", 2),
    "BHCKJ458": ("HC-L", "Derivatives and Off-Balance-Sheet Items", "1.e.(2)", 3),
}

# The Schedule HC-M Memoranda item 2 external-auditor block is a run of free-text
# items with no paired numeric amount, so the appendix parser (which keeps only
# the amount half of an itemization pair) drops it wholesale. The filings report
# it out of form order, late in the record, so it is restored from the guide here
# rather than anchored on a filed neighbor. Each entry is the guide's line and
# caption; unfiled members are dropped by the filed-set prune. Inserted before the
# first item of the schedule named by ``_GUIDE_TEXT_BEFORE``.
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

# An 8-character MDRM item code: a 4-letter prefix then 4 alphanumerics.
_MDRM = re.compile(r"\b[A-Z]{4}[A-Z0-9]{4}\b")

# Spreadsheet-style column labels ("Column A", "Column B", ...) that appear
# inline in the HC-R Part II risk-weighting grid alongside the column MDRMs.
_COLUMN_LABEL = re.compile(r"\bColumn\s+[A-Z]\b")

# A leading report-form line reference, e.g. "1.", "1.a.", "1.b.(1)",
# "1.e.(3)(a)", "M.2.", "M.6.a.". The optional single-letter schedule prefix
# (e.g. "A." in Schedule HC-R) is also accepted.
_LINE_REF = re.compile(
    r"^(?:(?:M|[A-Z])\.)?\d+(?:\.[a-z])*(?:\.\(\d+\))*(?:\([a-z]\))*\.?(?:;)?"
)

# Page running heads and column banners to drop entirely.
_NOISE = {
    "report form",
    "line number",
    "item",
    "column a column b column c column d column e column f column g column h column i",
    "appendix a",
    "fr y-9c report detailed field specifications",
}

# The income statement (Schedule HI) has no explicit "Schedule HI -" banner in
# the appendix; it begins immediately after the cover-page contact block.
_FIRST_SCHEDULE = ("HI", "Consolidated Income Statement")
_COVER_SCHEDULE = ("COVER", "Cover Page")

_SCHEDULE_HEADER = re.compile(r"^Schedule\s+([A-Z]{1,2}(?:-[A-Z0-9]+)?)\b[.,]?\s*(.*)$")

_APPENDIX_BANNER = "fr y-9c report detailed field specifications"

# Appendix B is the nonstandard-items / text-character-limits reference table
# that follows the form; it is not part of the report structure.
_APPENDIX_END = "fr y-9c nonstandard financial items and text item character limits"


def _fetch_pdf_bytes() -> bytes:
    """Download the canonical FR Y-9C user guide PDF."""
    import requests

    response = requests.get(USER_GUIDE_URL, timeout=180)
    response.raise_for_status()
    return response.content


def _pdf_lines(pdf_bytes: bytes) -> list[str]:
    """Extract the appendix text as a flat list of stripped, non-empty lines."""
    from pypdf import PdfReader

    reader = PdfReader(io.BytesIO(pdf_bytes))
    lines: list[str] = []
    in_appendix = False
    for page in reader.pages:
        text = page.extract_text() or ""
        for raw in text.splitlines():
            stripped = raw.strip()
            if not stripped:
                continue
            if not in_appendix:
                # The field specifications begin at the Appendix A banner; the
                # preceding pages are submission-process prose, not form items.
                if stripped.lower() == _APPENDIX_BANNER:
                    in_appendix = True
                continue
            if stripped.lower() == _APPENDIX_END:
                # Appendix B (the text-item reference table) follows the form.
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
        # The free-text half of an itemization pair; the paired numeric amount
        # row (BHCxxxx) carries the value we keep.
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
        # Strip the HC-R grid's inline "Column A".."Column S" labels so a line's
        # only meaningful content is its caption and MDRM codes.
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

        # Drop the free-text description half of an itemization pair; the paired
        # numeric amount row carries the BHCxxxx code we keep.
        if re.match(r"^(?:(?:M|[A-Z])\.\S+\s+)?TEXT\b", line) and not re.search(
            r"\b(?:BH|RSSD)", line
        ):
            flush_pending()
            continue

        if not seen_first_line_ref and not re.match(
            r"^(?:TEXT|INTEGER|PERCENT|DATE|NUMBER)\b", line
        ):
            # The cover-page block is the run of TEXT/INTEGER contact fields; the
            # income statement begins at the first non-cover line.
            flush_pending()
            schedule, schedule_name = _FIRST_SCHEDULE
            seen_first_line_ref = True

        codes_only = _is_codes_only(line)
        if codes_only and not pending and items:
            # A wide HC-R grid row whose column MDRMs are emitted on their own
            # physical line(s), detached from the caption; attach these columns
            # to the row just flushed rather than dropping them.
            previous = items[-1]
            previous_columns = list(previous["columns"] or [])
            previous_columns.extend(_MDRM.findall(line))
            previous["columns"] = previous_columns
            previous["mdrm"] = previous_columns[0]
            previous["is_header"] = False
            continue

        if _is_header_line(line):
            # A code-less caption terminated by the PDF's space-dash continuation
            # marker is a standalone section header (e.g. "2. Interest expense -",
            # "a. Interest on deposits: -"). It must be emitted as its own header
            # row, never buffered onto the following line item, so the Schedule HI
            # sub-headers stay distinct from the items they introduce.
            flush_pending()
            reference, caption = _split_reference(line)
            _flush_row(schedule, schedule_name, reference, caption, [], items)
            continue

        if _MDRM.search(line):
            # The terminal physical line of a logical row: append and emit.
            pending.append(line)
            flush_pending()
            continue

        # A code-less line is a section header unless it opens a wrapped item
        # whose MDRM lands on a following physical line. A wrapped item is
        # distinguished by a leading line reference and a non-colon ending; a
        # header has no reference or ends in a colon/qualifier.
        if pending:
            # Already mid-buffer (the open item is still waiting for its code):
            # this is a wrapped continuation line.
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
    """Return ``True`` when a ``Schedule X -`` line is a real schedule banner.

    Excludes in-caption cross references ("Schedule HC, item 7 ...") and page
    sub-banners ("Schedule HC-M Items 1-7 ...", "Schedule HC-R Part II ...").
    """
    keyword = header_match.group(2).strip().lower()
    if keyword.startswith(("item", "items", "table", "part")):
        return False
    return not header_match.group(0).rstrip().endswith((",", ":"))


def _is_header_line(line: str) -> bool:
    """Return ``True`` when a code-less line is a standalone section header.

    The user guide marks a caption that introduces indented sub-items with a
    trailing space-dash (``" -"``) continuation glyph, e.g.
    ``"2. Interest expense -"`` or ``"(1) In domestic offices: -"``. Word-wrap
    hyphens within a continued caption attach to the preceding word with no
    space (``"mortgage-"``, ``"available-"``), so the space distinguishes a
    header from a mid-caption line break. A header therefore never carries an
    MDRM code on its own physical line.
    """
    return bool(re.search(r"\s-$", line)) and not _MDRM.search(line)


def _opens_wrapped_item(line: str) -> bool:
    """Return ``True`` when a code-less line is the first line of a wrapped item.

    A wrapped item carries a leading line reference (its MDRM sits on the next
    physical line) and does not end in a colon, which would mark a section
    header introducing indented sub-items.
    """
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
    """Emit each filed itemization ``TEXTxxxx`` description before its amount row.

    The guide drops the free-text description half of an itemization pair, keeping
    only the paired numeric ``BHCKxxxx`` amount. A filed public report carries
    both, so for every amount row whose ``TEXTxxxx`` sibling appears in the
    filings, a ``Description`` value item is inserted immediately above it.
    """
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
    """Restore the all-text HC-M auditor block the appendix parser drops.

    The block has no numeric amount to anchor on and is filed out of form order,
    so it is rebuilt from the guide and inserted before the first item of
    ``_GUIDE_TEXT_BEFORE``. The filed-set prune then drops any unfiled member.
    """
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
    """Drop value columns and rows absent from every sampled filing.

    A value item keeps only its filed columns; an item left with no filed column
    is removed. A section header is removed when no value item survives beneath it
    before the next header at its level or above.
    """
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
