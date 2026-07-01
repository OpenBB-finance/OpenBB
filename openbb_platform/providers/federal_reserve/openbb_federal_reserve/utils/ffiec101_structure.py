"""FFIEC 101 report structure generator.

Parses the FFIEC 101 Reporting Central user guide PDF (Appendix A, the detailed
field specifications) and reconciles it against the live per-institution CSVs to
produce an ordered, hierarchical list of the report's *public* items so the model
can render the form grouped by schedule and indent depth. The parsed result is
committed as a static asset (``assets/ffiec101/structure.json``); the live model
loads that asset rather than re-parsing the PDF at request time.

The user guide enumerates every cell of every schedule, including the
supervisory-confidential exposure grids (Schedules C-R) whose codes are
suppressed in the public ``ReturnFinancialReportCSV`` listing, and it omits the
filed Schedule B detail cells (the ``AAB[A-H]...`` exposure grid, columns A-H,
rows 1-25) because they are presented as a wide column grid rather than numbered
data-listing rows. The public report's true item set is therefore the *union of
value-bearing codes across sampled filers' CSVs* (excluding identity/admin rows).
The guide supplies the caption, line reference and indent for the codes it
enumerates; the Schedule B grid cells the guide omits are captioned from the CSV
``Description``. No structure is fabricated and no permanently-empty (confidential
or unfiled) form row is carried.

Run as a module to regenerate the asset::

    python -m openbb_federal_reserve.utils.ffiec101_structure

Pass ``--pdf <path>`` to parse a local copy instead of fetching the canonical
URL.
"""

from __future__ import annotations

import csv
import io
import json
import re
from datetime import date
from pathlib import Path
from typing import Any

USER_GUIDE_URL = (
    "https://www.frbservices.org/binaries/content/assets/crsocms/"
    "central-bank/reporting-central/ffiec-101-user-guide.pdf"
)

ASSET_PATH = (
    Path(__file__).resolve().parent.parent / "assets" / "ffiec101" / "structure.json"
)

# The filers and report code sampled to recover the public report's true item
# set: the union of their value-bearing codes is the set of codes the public
# report actually carries.
VALIDATION_RPT = "FFIEC101"
VALIDATION_RSSDS = ("852218", "480228", "451965")

SCHEDULE_COVER = ("COVER", "Cover Page")

# An 8-character MDRM item code: a 4-letter prefix then 4 alphanumerics. The
# user guide flags derived (calculated) cells with a trailing "*"; it is consumed
# (so it does not leak into captions) while only the bare code is recorded.
_MDRM = re.compile(r"\b([A-Z]{4}[A-Z0-9]{4})\*?")

# A leading report-form line reference, e.g. "1.", "1.a.", "8.c.", "1.7a",
# "1.1.", "2.10.", "M.2." (memoranda). FFIEC 101 wholesale-grid rows print the
# reference twice ("1. 1. 0.00 to < 0.15"); the doubled copy is collapsed first.
_LINE_REF = re.compile(r"^(?:M\.)?(?:\d+(?:\.\d+)*[a-z]?(?:\.[a-z])*\.?|[a-z]\.)")

# The PDF prints each grid line's reference twice ("26. 26. Unsettled ...",
# "M.2. 2. Regulated ..."); the second copy may drop the "M." prefix.
_DOUBLED_REF = re.compile(r"^(?:(M)\.)?(\d+(?:\.\d+)*[a-z]?\.?)\s+\1?\.?\s*\2\s")

# Spreadsheet-style column banners ("(Column A)") that head each grid schedule.
_COLUMN_BANNER = re.compile(r"\(Column\s+[A-Z]\)")

# Inline "(x,y)" / "(x, y)" digit-limit annotations and their trailing notes
# ("8,2", "10,4 (effective starting March 31, 2016)", "6,0 (mmyyyy)").
_LIMIT_NOTE = re.compile(
    r"\b\d+\s*,\s*\d+\b(?:\s*\([^)]*\))?|\(effective[^)]*\)|\(mmyyyy\)", re.IGNORECASE
)

# Page running heads and column banners to drop entirely.
_NOISE = {
    "financial data items",
    "report form",
    "line number",
    "row description",
}

_SCHEDULE_HEADER = re.compile(r"^Schedule\s+([A-Z]{1,2})\s*[-–]\s*(.+)$")

# The detailed field specifications open at the Appendix A banner; the preceding
# pages are file-format prose, not report items.
_APPENDIX_BANNER = "ffiec101 report detailed field specifications"

# Standalone section headers that carry no line reference but introduce indented
# blocks; they must each be emitted as their own ``is_header`` item.
_BARE_HEADERS = {
    "memoranda",
    "financial data items",
}

# The cover/admin block's MDRMs are filed under the ``AAXX`` prefix and the guide
# parses them under the trailing operational-risk schedule with a "Cover Page"
# caption and a glued field-length integer ("Cover Page Contact Name 72"). They
# belong to the submission cover, not a data schedule.
_COVER_PREFIX = "AAXX"
_COVER_CAPTION_PREFIX = re.compile(r"^cover page\s+", re.IGNORECASE)

# Trailing field-length / format tokens glued to a parsed cover caption: a bare
# length ("72"), a length pair ("0 or exactly 20"), or a format hint
# ("MM/DD/YYYY").
_COVER_LENGTH_TAIL = re.compile(
    r"\s*(?:\d+\s+or\s+exactly\s+\d+|MM/DD/YYYY|\d{1,3})\s*$", re.IGNORECASE
)

# A redundant numbered/lettered prefix the guide prints inside a sub-item caption
# ("31. a. Credit Valuation Adjustments: Simple"); the line reference already
# carries the number, so the prefix is stripped from the caption.
_REDUNDANT_NUMBER_PREFIX = re.compile(r"^\d+\.\s*[a-z]\.\s*")

# Schedule B grid metadata. The guide's data listing omits the wide exposure grid
# (columns A-H, exposure rows 1-25); those cells are filed and recovered from the
# CSV. The column letter is the fourth character of the MDRM prefix; the metric
# name is the part of the CSV description before the first " - ".
_SCHEDULE_B = "B"
_GRID_PREFIX = re.compile(r"^AAB[A-H]")

# The Schedule B "Other Assets" rows (26-28) the guide enumerates as two-column
# rows ("Unsettled transactions", carrying both the Balance Sheet and RWA cells in
# one item). The model renders only one cell per item, so these flow through the
# grid builder instead and the guide's two-column items are suppressed.
_GRID_TWO_COLUMN_GUIDE_CODES = frozenset({"AABBJ147", "AABBJ148", "AABBJ149"})

# The Schedule B single-column tail rows (29-36) the guide enumerates as numbered
# data-listing rows, so they are not treated as omitted grid cells. Rows 26-28
# ("Other Assets") are two-column grid rows (Balance Sheet and RWA both filed);
# the guide carries only the first column per row, so they flow through the grid
# builder instead, one filed cell per item.
_GRID_TAIL_CODES = frozenset(
    {
        "AABGJ150",
        "AABGJ151",
        "AABGJ152",
        "AABGJ153",
        "AABGJ154",
        "AABGJ198",
        "AABGA223",
        "AABGP925",
        "AABGP926",
    }
)

# Acronyms that must keep their reported casing when a CSV ALL-CAPS description is
# recased to the form's title casing.
_ACRONYMS = {
    "PD": "PD",
    "LGD": "LGD",
    "EAD": "EAD",
    "RWA": "RWA",
    "ECL": "ECL",
    "OTC": "OTC",
    "IPRE": "IPRE",
    "HVCRE": "HVCRE",
    "SRWA": "SRWA",
    "SSFA": "SSFA",
    "SFA": "SFA",
    "GAAP": "GAAP",
    "AOCI": "AOCI",
    "DTAS": "DTAs",
    "DTLS": "DTLs",
    "MSAS": "MSAs",
    "LEI": "LEI",
    "WTD": "Wtd",
    "AVG": "Avg",
}

# Connector words rendered lowercase in title case unless they lead the caption.
_LOWER_WORDS = {
    "a",
    "an",
    "and",
    "as",
    "at",
    "by",
    "for",
    "in",
    "of",
    "on",
    "or",
    "the",
    "to",
    "with",
}


def _fetch_pdf_bytes() -> bytes:
    """Download the canonical FFIEC 101 user guide PDF."""
    import requests

    response = requests.get(USER_GUIDE_URL, timeout=180)
    response.raise_for_status()
    return response.content


def _latest_quarter_end() -> str:
    """Return the most recent completed calendar quarter end as ``YYYYMMDD``."""
    today = date.today()
    ends = (
        date(today.year, 3, 31),
        date(today.year, 6, 30),
        date(today.year, 9, 30),
        date(today.year, 12, 31),
        date(today.year - 1, 12, 31),
    )
    completed = sorted(end for end in ends if end < today)
    return completed[-1].strftime("%Y%m%d")


def _fetch_validation_csv(rssd_id: str) -> str:
    """Fetch one sampled filer's live per-institution CSV for the latest period."""
    from openbb_federal_reserve.utils.ffiec import _fetch_bytes

    dt = _latest_quarter_end()
    raw = _fetch_bytes(
        "FinancialReport/ReturnFinancialReportCSV"
        f"?rpt={VALIDATION_RPT}&id={rssd_id}&dt={dt}",
        referer="https://www.ffiec.gov/npw/FinancialReport/FinancialDataDownload",
    )
    return raw.decode("utf-8", "replace")


# CSV ItemName rows that carry institution identity or submission admin rather
# than a filed financial value; excluded when building the public item union.
_IDENTITY_ROWS = {
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


def _is_identity_row(name: str) -> bool:
    """Return ``True`` for an identity/admin CSV row, not a filed metric."""
    upper = name.strip().upper()
    return upper in _IDENTITY_ROWS or upper == "DT" or upper.startswith("DT_")


def _csv_union(csv_texts: list[str]) -> dict[str, str]:
    """Return the union of value-bearing codes across the sampled CSVs.

    Each CSV is the ``ItemName,Description,Value`` listing for one filer. The
    union of every value-bearing ``ItemName`` (excluding identity/admin rows) is
    the public report's true item set; the first-seen ``Description`` is kept to
    caption codes the guide does not enumerate.

    Parameters
    ----------
    csv_texts : list[str]
        The sampled filers' ``ReturnFinancialReportCSV`` payloads.

    Returns
    -------
    dict[str, str]
        A ``{code: description}`` map of every public, value-bearing code.
    """
    union: dict[str, str] = {}
    for text in csv_texts:
        for row in list(csv.reader(io.StringIO(text)))[1:]:
            if len(row) < 3:
                continue
            name, description, value = row[0].strip(), row[1].strip(), row[2].strip()
            if not value or _is_identity_row(name):
                continue
            if not re.fullmatch(r"[A-Z]{4}[A-Z0-9]{4}", name):
                continue
            union.setdefault(name, description)
    return union


def _pdf_lines(pdf_bytes: bytes) -> list[str]:
    """Extract the appendix text as a flat list of stripped, non-empty lines."""
    from pypdf import PdfReader

    reader = PdfReader(io.BytesIO(pdf_bytes))
    lines: list[str] = []
    in_appendix = False
    for page in reader.pages:
        text = page.extract_text() or ""
        normalized = "".join(char for char in text if char != "­")  # soft hyphens
        for raw in normalized.splitlines():
            stripped = raw.strip()
            if not stripped:
                continue
            if not in_appendix:
                if _norm(stripped) == _APPENDIX_BANNER:
                    in_appendix = True
                continue
            lines.append(stripped)
    return lines


def _norm(line: str) -> str:
    """Lower-case and collapse whitespace for noise/banner comparison."""
    return re.sub(r"\s+", " ", line).strip().lower()


def _is_noise(line: str) -> bool:
    """Return ``True`` for page running heads, banners, and bare page numbers."""
    lowered = _norm(line)
    if lowered in _NOISE:
        return True
    if re.fullmatch(r"\d+", line.strip()):
        return True
    if lowered.startswith("item limits, where applicable"):
        return True
    if lowered.startswith("8-character mdrm"):
        return True
    return lowered.startswith("(derived values are flagged")


def _is_column_label_fragment(line: str) -> bool:
    """Return ``True`` for a wrapped fragment of a grid's column-header labels.

    Each grid schedule prints an eight-to-fourteen-cell header banner whose
    labels word-wrap across many physical lines ("Weighted-", "Average",
    "Probability of", "Default"). These fragments carry neither a line reference
    nor an MDRM and sit between the schedule banner and the first numbered row.
    """
    if _MDRM.search(line) or _LINE_REF.match(line):
        return False
    return bool(line) and not line.startswith("(")


def _level_from_reference(reference: str) -> int:
    """Derive the indent level from a line reference's nesting depth."""
    body = reference.rstrip(".")
    if re.fullmatch(r"[a-z]", body):
        # A bare letter sub-item ("a.", "b.") sits one level under its parent.
        return 2
    depth = 1
    depth += reference.count(".") - (1 if reference.endswith(".") else 0)
    if re.search(r"\d[a-z]$", body):
        depth += 1
    return max(depth, 1)


def _clean_caption(caption: str) -> str:
    """Collapse whitespace and strip digit-limit notes, dashes and stray flags."""
    caption = _LIMIT_NOTE.sub("", caption)
    # Derived-cell "*" flags that the PDF wraps onto their own physical line, or
    # detaches from an MDRM by a space ("AAIIJ035 *"), survive into the joined
    # caption; drop the bare markers.
    caption = re.sub(r"(?:^|\s)\*(?=\s|$)", " ", caption)
    caption = re.sub(r"\s+", " ", caption).strip()
    caption = caption.strip(" -–").strip()
    return caption


def _is_reference_boundary(char: str) -> bool:
    """Return ``True`` when ``char`` legitimately follows a line reference.

    A genuine reference is followed by end-of-line, whitespace, or a period; a
    digit run trailed by ``,``/``)``/``%`` ("4, 15, and 21)", "100%") is caption
    enumeration text, not a reference.
    """
    return char in {"", " ", "."}


def _split_reference(line: str) -> tuple[str | None, str]:
    """Split a logical row into its line reference and caption text."""
    line = _collapse_doubled(line)
    match = _LINE_REF.match(line)
    if (
        not match
        or not match.group(0).rstrip(".")
        or not _is_reference_boundary(line[match.end() : match.end() + 1])
    ):
        return None, line
    reference = match.group(0).rstrip(".")
    caption = line[match.end() :].strip()
    return reference, caption


def _collapse_doubled(line: str) -> str:
    """Collapse a doubled leading line reference into a single reference.

    The grids print each reference twice, optionally dropping an ``M.`` memoranda
    prefix on the second copy ("M.2. 2. Regulated ...", "26. 26. Unsettled ...").
    The canonical (prefixed) reference is kept.
    """
    doubled = _DOUBLED_REF.match(line)
    if not doubled:
        return line
    prefix = f"{doubled.group(1)}." if doubled.group(1) else ""
    ref = f"{prefix}{doubled.group(2)}"
    tail = line[doubled.end() :]
    return f"{ref} {tail}".strip()


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
    is_header = not codes
    level = _level_from_reference(reference) if reference is not None else 1
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


def _codes(text: str) -> list[str]:
    """Return the MDRM codes in a string in order, dropping the derived flag."""
    return [match.group(1) for match in _MDRM.finditer(text)]


def parse_guide(pdf_bytes: bytes) -> list[dict[str, Any]]:
    """Parse the FFIEC 101 user guide PDF into an ordered list of report items.

    Parameters
    ----------
    pdf_bytes : bytes
        The raw FFIEC 101 Reporting Central user guide PDF.

    Returns
    -------
    list[dict[str, Any]]
        One record per logical guide line in form order, each with the keys
        ``schedule``, ``schedule_name``, ``line``, ``caption``, ``mdrm``,
        ``columns``, ``level`` and ``is_header``. The derived-cell ``*`` flag is
        stripped. This is the *guide's* enumeration, not yet reconciled against
        the public CSV item set.
    """
    lines = _pdf_lines(pdf_bytes)
    items: list[dict[str, Any]] = []
    schedule = ""
    schedule_name = ""
    pending: list[str] = []
    in_banner = False

    def flush_pending() -> None:
        """Resolve the buffered physical lines into one logical row."""
        nonlocal pending
        if not pending:
            return
        joined = _collapse_doubled(" ".join(pending))
        codes = _codes(joined)
        reference, caption = _split_reference(_MDRM.sub("", joined).strip())
        _flush_row(schedule, schedule_name, reference, caption, codes, items)
        pending = []

    for raw_line in lines:
        line = re.sub(r"\s+", " ", raw_line).strip()
        if not line or _is_noise(line):
            flush_pending()
            continue

        header_match = _SCHEDULE_HEADER.match(line)
        if header_match and not _MDRM.search(line):
            flush_pending()
            schedule = header_match.group(1)
            schedule_name = _clean_caption(header_match.group(2))
            in_banner = False
            continue

        if _COLUMN_BANNER.search(line) or line.startswith("(Column"):
            # The wide-grid column-header banner opens with "(Column A)"; suppress
            # every wrapped label fragment until the first numbered data row.
            flush_pending()
            in_banner = True
            continue
        if in_banner:
            if _starts_new_row(line):
                in_banner = False
            else:
                continue

        if _is_limit_format_row(line):
            # A bare "(x,y)" digit-limit format row under a grid banner; not data.
            flush_pending()
            continue

        if _norm(line) in _BARE_HEADERS:
            flush_pending()
            _flush_row(schedule, schedule_name, None, line, [], items)
            continue

        codes = _codes(line)

        if codes and not pending and _is_format_variant_row(line, items):
            # The capital-ratio items print a second physical line carrying the
            # same MDRM in its "(effective starting ...)" / alternate-precision
            # format ("AAABP793 10,4 (effective starting March 31, 2016)"). It
            # restates a code already captured; drop it.
            continue

        starts_row = _starts_new_row(line)

        if pending and starts_row:
            # A new logical row begins while the buffer is still open: the buffer
            # never acquired an MDRM, so it was a wrapped section header. Emit it
            # as a header before opening the new row.
            flush_pending()

        if not codes:
            if pending and not starts_row:
                # A wrapped continuation of the buffered caption whose MDRM has
                # not yet appeared.
                pending.append(line)
                continue
            reference, caption = _split_reference(line)
            if reference is not None and not _clean_caption(caption).endswith(":"):
                # A wrapped item whose MDRM lands on a following physical line.
                pending.append(line)
            elif _is_column_label_fragment(line) and not pending:
                # A stray wrapped fragment of the grid column-header banner.
                continue
            else:
                # A code-less, colon-terminated or reference-bearing caption is a
                # standalone section header ("31. Credit Valuation Adjustments:",
                # "Table 1", "Regulatory minimums ...").
                flush_pending()
                _flush_row(schedule, schedule_name, reference, caption, [], items)
            continue

        if _is_codes_only(line) and not pending:
            if items and _belongs_to_previous(  # pragma: no cover
                line, items[-1]
            ):
                # Unreachable defensive guard: any code-only line whose codes are
                # already captured (which includes the previous row's columns) is
                # dropped earlier by the format-variant check, so the buffer is
                # only ever an unseen detached column row by the time we get here.
                continue
            pending.append(line)
            flush_pending()
            continue

        pending.append(line)
        flush_pending()

    flush_pending()
    _dedupe_effective_duplicates(items)
    return items


def _starts_new_row(line: str) -> bool:
    """Return ``True`` when a line opens a new numbered report row.

    A new row begins with a line reference (possibly doubled as the wholesale
    grids print it) immediately followed by caption text or an MDRM, not by a
    bare continuation of a wrapped caption. A digit run followed by a comma
    ("4, 15, and 21)") is enumeration text inside a wrapped caption, not a
    reference, so it does not open a row.
    """
    collapsed = _collapse_doubled(line)
    match = _LINE_REF.match(collapsed)
    if not match or not match.group(0).rstrip("."):
        return False
    return _is_reference_boundary(collapsed[match.end() : match.end() + 1])


def _is_limit_format_row(line: str) -> bool:
    """Return ``True`` for a bare digit-limit format row (e.g. ``8,2 11,0 8,2``).

    These per-column "(x,y)" precision banners head each grid page and may appear
    detached from the "(Column ...)" header after a page break. They consist only
    of comma-joined digit pairs, so a leading digit must not be misread as a line
    reference.
    """
    if _MDRM.search(line):
        return False
    return bool(re.fullmatch(r"(?:\d+\s*,\s*\d+\s+)*\d+\s*,\s*\d+", line.strip()))


def _is_format_variant_row(line: str, items: list[dict[str, Any]]) -> bool:
    """Return ``True`` for a line that only restates an already-captured MDRM.

    The capital-ratio items emit a second physical line whose sole non-code
    content is a digit-limit note ("AAABP793 10,4 (effective starting ...)").
    Such a line carries no caption of its own and repeats an MDRM already held by
    an earlier item, so it must not start a new row.
    """
    line_codes = _codes(line)
    remainder = _MDRM.sub("", line)
    remainder = _LIMIT_NOTE.sub("", remainder).strip(" -–,").strip()
    if remainder:
        return False
    captured = {code for item in items for code in (item["columns"] or [])}
    return all(code in captured for code in line_codes)


def _is_codes_only(line: str) -> bool:
    """Return ``True`` when a line is solely MDRM codes (a detached column row)."""
    if not _MDRM.search(line):
        return False
    return not _MDRM.sub("", line).strip()


def _belongs_to_previous(line: str, previous: dict[str, Any]) -> bool:
    """Return ``True`` when a code-only line repeats the previous row's MDRM.

    The capital-ratio items print a second physical line carrying the same MDRM
    in its "(effective starting ...)" alternate format. That line must not start
    a new row; it duplicates the code already attached to the previous item.
    """
    line_codes = _codes(line)
    previous_codes = previous.get("columns") or []
    return bool(line_codes) and set(line_codes).issubset(set(previous_codes))


def _dedupe_effective_duplicates(items: list[dict[str, Any]]) -> None:
    """Drop consecutive items that repeat a prior item's MDRM and caption."""
    seen: set[str] = set()
    deduped: list[dict[str, Any]] = []
    for item in items:
        mdrm = item.get("mdrm")
        key = f"{item['schedule']}|{mdrm}|{item['caption']}"
        if mdrm and key in seen:
            continue
        if mdrm:
            seen.add(key)
        deduped.append(item)
    items[:] = deduped


def _recase_token(token: str, *, lead: bool) -> str:
    """Recase a single word token, preserving acronyms and connector words."""
    split = re.fullmatch(
        r"([^A-Za-z]*)([A-Za-z].*?[A-Za-z]|[A-Za-z])([^A-Za-z]*)", token
    )
    if split is None:
        return token
    lead_punct, core, trail_punct = split.groups()
    upper = core.upper()
    if upper in _ACRONYMS:
        core = _ACRONYMS[upper]
    elif not lead and core.lower() in _LOWER_WORDS:
        core = core.lower()
    else:
        core = core[:1].upper() + core[1:].lower()
    return f"{lead_punct}{core}{trail_punct}"


def _recase(caption: str) -> str:
    """Recase an ALL-CAPS CSV caption to the form's title casing."""
    parts = re.sub(r"\s+", " ", caption).strip().split(" ")
    out: list[str] = []
    for position, word in enumerate(parts):
        pieces = word.split("-")
        out.append(
            "-".join(
                _recase_token(piece, lead=(position == 0 and idx == 0))
                for idx, piece in enumerate(pieces)
            )
        )
    return " ".join(out)


def _clean_cover_caption(caption: str) -> str:
    """Strip the "Cover Page" prefix and trailing field-length token."""
    caption = _COVER_CAPTION_PREFIX.sub("", caption)
    caption = _COVER_LENGTH_TAIL.sub("", caption)
    return _clean_caption(caption)


def _grid_caption(description: str) -> str:
    """Caption a Schedule B grid cell from its CSV description's exposure part.

    A grid cell's CSV description is ``<column metric> - <exposure row>
    (DERIVED)`` (for example ``RISK WEIGHTED ASSETS - WHOLESALE EXPOSURES:
    CORPORATE (DERIVED)``). The column metric is carried by the sub-section
    header, so the cell caption is the exposure-row remainder, recased.
    """
    body = description.split(" - ", 1)[-1]
    body = re.sub(r"\s*\(DERIVED\)\s*$", "", body, flags=re.IGNORECASE).strip()
    return _recase(body)


def _grid_metric(description: str) -> str:
    """Return the recased column-metric header of a Schedule B grid cell."""
    return _recase(description.split(" - ", 1)[0].strip())


def _build_grid_items(
    union: dict[str, str], schedule_name: str
) -> list[dict[str, Any]]:
    """Build the filed Schedule B grid cells the guide omits, from the CSV.

    The exposure grid (columns A-H, rows 1-25) is filed but absent from the
    guide's data listing. Each filed grid code is emitted as a Schedule B line
    item captioned by its exposure row, grouped under a column-metric sub-header,
    in column order (A through H) then in filing order within each column.

    Parameters
    ----------
    union : dict[str, str]
        The ``{code: description}`` map of public, value-bearing codes.
    schedule_name : str
        The Schedule B schedule name, taken from the guide.

    Returns
    -------
    list[dict[str, Any]]
        The ordered grid sub-header and line-item records.
    """
    grid_codes = sorted(
        code
        for code in union
        if _GRID_PREFIX.match(code) and code not in _GRID_TAIL_CODES
    )
    grid_codes.sort(key=lambda code: (code[3], code))
    items: list[dict[str, Any]] = []
    active_metric: str | None = None
    for code in grid_codes:
        description = union[code]
        metric = _grid_metric(description)
        if metric != active_metric:
            active_metric = metric
            items.append(
                {
                    "schedule": _SCHEDULE_B,
                    "schedule_name": schedule_name,
                    "line": None,
                    "caption": metric,
                    "mdrm": None,
                    "columns": None,
                    "level": 1,
                    "is_header": True,
                }
            )
        items.append(
            {
                "schedule": _SCHEDULE_B,
                "schedule_name": schedule_name,
                "line": None,
                "caption": _grid_caption(description),
                "mdrm": code,
                "columns": [code],
                "level": 2,
                "is_header": False,
            }
        )
    return items


def _reconcile(
    guide_items: list[dict[str, Any]], union: dict[str, str]
) -> list[dict[str, Any]]:
    """Reconcile the guide enumeration against the public CSV item set.

    Keeps only the guide value-items whose MDRM is public (in ``union``),
    relocates the cover/admin block to the ``COVER`` schedule with a clean
    caption, strips redundant numbered prefixes, inserts the filed Schedule B
    grid cells the guide omits, and drops section headers left with no surviving
    value descendant.

    Parameters
    ----------
    guide_items : list[dict[str, Any]]
        The ordered guide enumeration from :func:`parse_guide`.
    union : dict[str, str]
        The ``{code: description}`` map of public, value-bearing codes.

    Returns
    -------
    list[dict[str, Any]]
        The reconciled public report structure in form order.
    """
    schedule_b_name = next(
        (it["schedule_name"] for it in guide_items if it["schedule"] == _SCHEDULE_B),
        "",
    )
    grid_items = _build_grid_items(union, schedule_b_name)

    kept: list[dict[str, Any]] = []
    grid_inserted = False
    for item in guide_items:
        if item["is_header"]:
            kept.append(item)
            continue
        code = item["mdrm"]
        if code and code.startswith(_COVER_PREFIX):
            if code not in union:
                continue
            kept.append(
                {
                    **item,
                    "schedule": SCHEDULE_COVER[0],
                    "schedule_name": SCHEDULE_COVER[1],
                    "line": None,
                    "caption": _clean_cover_caption(item["caption"]),
                    "level": 1,
                }
            )
            continue
        if code not in union or code in _GRID_TWO_COLUMN_GUIDE_CODES:
            continue
        if not grid_inserted and item["schedule"] == _SCHEDULE_B and grid_items:
            # The guide's Schedule B opens at row 26 (the grid totals); the filed
            # exposure grid (rows 1-25) precedes it.
            kept.extend(grid_items)
            grid_inserted = True
        kept.append(
            {**item, "caption": _REDUNDANT_NUMBER_PREFIX.sub("", item["caption"])}
        )

    if not grid_inserted:  # pragma: no cover - sampled filers always file the grid
        kept.extend(grid_items)

    return _drop_orphan_headers(kept)


def _drop_orphan_headers(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Drop section headers with no surviving value item before the next peer.

    A header introduces the block of items indented beneath it. After
    union-filtering removed the confidential value items, a header may be left
    with no value descendant; such a header would render as an empty section, so
    it is dropped. Schedule-banner relocation is not affected: each surviving
    value item still carries its own schedule.
    """
    keep = [True] * len(items)
    for index, item in enumerate(items):
        if not item["is_header"]:
            continue
        level = item["level"]
        has_value = False
        for follower in items[index + 1 :]:
            if follower["is_header"] and follower["level"] <= level:
                break
            if not follower["is_header"] and follower["level"] > level:
                has_value = True
                break
        if not has_value:
            keep[index] = False
    return [item for index, item in enumerate(items) if keep[index]]


def parse_structure(
    pdf_bytes: bytes, csv_texts: list[str] | None = None
) -> list[dict[str, Any]]:
    """Parse the guide and reconcile it against the public CSV item set.

    Parameters
    ----------
    pdf_bytes : bytes
        The raw FFIEC 101 Reporting Central user guide PDF.
    csv_texts : list[str], optional
        The sampled filers' ``ReturnFinancialReportCSV`` payloads. When omitted
        the live CSVs for :data:`VALIDATION_RSSDS` are fetched.

    Returns
    -------
    list[dict[str, Any]]
        The reconciled public report structure: one record per public report
        line in form order, each with the keys ``schedule``, ``schedule_name``,
        ``line``, ``caption``, ``mdrm``, ``columns``, ``level`` and
        ``is_header``. Every value item's ``mdrm`` is a code filed in at least
        one sampled CSV; no confidential or permanently-empty form row is carried.
    """
    if csv_texts is None:
        csv_texts = [_fetch_validation_csv(rssd) for rssd in VALIDATION_RSSDS]
    union = _csv_union(csv_texts)
    guide_items = parse_guide(pdf_bytes)
    return _reconcile(guide_items, union)


def generate(
    pdf_path: str | None = None, csv_paths: list[str] | None = None
) -> dict[str, Any]:
    """Parse the user guide and return the structured asset payload."""
    pdf_bytes = Path(pdf_path).read_bytes() if pdf_path else _fetch_pdf_bytes()
    csv_texts = (
        [Path(path).read_text(encoding="utf-8") for path in csv_paths]
        if csv_paths
        else None
    )
    items = parse_structure(pdf_bytes, csv_texts)
    schedules: list[dict[str, str]] = []
    seen: set[str] = set()
    for item in items:
        code = item["schedule"]
        if code and code not in seen:
            seen.add(code)
            schedules.append({"schedule": code, "name": item["schedule_name"]})
    return {
        "source": USER_GUIDE_URL,
        "schedule_count": len(schedules),
        "item_count": len(items),
        "schedules": schedules,
        "items": items,
    }


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

    parser = argparse.ArgumentParser(description="Regenerate the FFIEC 101 structure.")
    parser.add_argument("--pdf", default=None, help="Local PDF path to parse.")
    parser.add_argument(
        "--csv",
        default=None,
        action="append",
        help="Local sampled-filer CSV path (repeatable).",
    )
    args = parser.parse_args()
    path = write_asset(args.pdf, args.csv)
    payload = json.loads(path.read_text(encoding="utf-8"))
    print(  # noqa: T201
        f"Wrote {path} -> {payload['schedule_count']} schedules, "
        f"{payload['item_count']} items"
    )


if __name__ == "__main__":  # pragma: no cover - module-as-script entry guard
    _main()
