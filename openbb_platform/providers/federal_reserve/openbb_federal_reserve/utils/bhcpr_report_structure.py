"""FR BHCPR performance-report PDF parser.

Parses the FFIEC ``ReturnFinancialReportPDF?rpt=BHCPR`` document into an ordered,
hierarchical list of report rows so the model can render the Bank Holding Company
Performance Report exactly as the official PDF lays it out, grouped by section and
indent depth like the UBPR report.

The PDF is a fixed-width performance report. Page 0 is the cover plus a Table of
Contents (``Section .... PageNumber``). Each subsequent page is one report section
made of one or more horizontal *bands*. A band starts with a date-header row
carrying the five period-end dates (current quarter, same quarter prior year, and
three calendar year-ends) and is either a *ratio* band (a ``BHC Peer # <n> Pct``
label row, fifteen value columns -- bank value, peer-group average, and percentile
rank per period) or an *amount* band (dollar figures, one bank value per period,
flagged ``Dollar Amount in Thousands`` or ``($000)`` and therefore expanded to true
dollars). Value columns are recovered from word geometry rather than the flattened
text so blank cells stay aligned to their period.

The committed section list (``assets/bhcpr/sections.json``) drives the report
dropdown; the live model parses the PDF at request time.

Run as a module to regenerate the asset::

    python -m openbb_federal_reserve.utils.bhcpr_report_structure --id 1039502 --dt 20260331
"""

from __future__ import annotations

import io
import re
from pathlib import Path
from typing import Any

ASSET_PATH = (
    Path(__file__).resolve().parent.parent / "assets" / "bhcpr" / "sections.json"
)

# A period-end date as printed in a band header, e.g. ``03/31/2026``.
_DATE = re.compile(r"^\d{2}/\d{2}/\d{4}$")

# A numeric cell: optional sign, thousands-separated digits, optional decimals;
# also a bare leading-dot decimal such as ``.18``.
_NUMBER = re.compile(r"^-?[\d,]+\.?\d*$|^-?\.\d+$")

# The dotted leader that joins a row caption to its value columns. Two or more
# dots so a single period inside a caption (``($000).`` etc.) is not mistaken for
# the leader.
_LEADER = re.compile(r"\.{2,}")

# A Table-of-Contents entry: caption, dotted leader, then a page label that may
# carry a letter suffix (``7A``, ``13B``).
_TOC_ENTRY = re.compile(r"^(.*?)\.{2,}\s*(\d{1,3}[A-Z]?)\s*$")

# Marks a dollar-denominated band or caption whose bank/peer amounts are printed
# in thousands and must be expanded to true dollars.
_THOUSANDS = re.compile(r"dollar amount in thousands|\(\$000\)|in thousands", re.I)

# Trailing aggregate columns that some amount bands append after the five period
# columns. They are percent-change figures, not per-period values.
_GROWTH_LABELS = ("1-Year", "5-Year")

# The horizontal span of the value area; tokens left of this are caption text and
# tokens right of the page edge are page furniture.
_VALUE_X0 = 270.0
_VALUE_X1 = 760.0

# Body rows sit between the section banner and the page footer in PDF ``top``
# coordinates; the footer date stamp and page number live below this.
_FOOTER_TOP = 540.0

# Maximum horizontal gap (points) within a single value column when clustering
# numeric word right-edges into columns.
_COLUMN_GAP = 12.0

# Words whose ``top`` differs by no more than this share a baseline; a caption's
# dotted leader and its right-aligned value digits print a fraction of a point
# apart and must group into one line.
_LINE_TOL = 2.5


def _line_words(page: Any) -> list[tuple[float, list[dict[str, Any]]]]:
    """Group a page's words into baseline-clustered lines, left-to-right.

    Words are clustered by ``top`` within ``_LINE_TOL`` so a caption and its
    right-aligned value cells -- printed a fraction of a point apart -- stay on one
    line. Each line is keyed by its minimum ``top``.
    """
    words = sorted(
        page.extract_words(use_text_flow=False, keep_blank_chars=False),
        key=lambda w: (w["top"], w["x0"]),
    )
    lines: list[tuple[float, list[dict[str, Any]]]] = []
    current: list[dict[str, Any]] = []
    anchor: float | None = None
    for word in words:
        if anchor is None or word["top"] - anchor <= _LINE_TOL:
            if anchor is None:
                anchor = word["top"]
            current.append(word)
        else:
            lines.append((current[0]["top"], sorted(current, key=lambda w: w["x0"])))
            current = [word]
            anchor = word["top"]
    if current:
        lines.append((current[0]["top"], sorted(current, key=lambda w: w["x0"])))
    return lines


def _cluster_right_edges(edges: list[float]) -> list[float]:
    """Cluster numeric word right-edges into column anchors (max per cluster)."""
    ordered = sorted(edges)
    clusters: list[list[float]] = [[ordered[0]]]
    for edge in ordered[1:]:
        if edge - clusters[-1][-1] > _COLUMN_GAP:
            clusters.append([edge])
        else:
            clusters[-1].append(edge)
    return [max(cluster) for cluster in clusters]


def _to_number(text: str) -> float | int:
    """Convert a value cell to ``int`` or ``float``, stripping thousands commas."""
    cleaned = text.replace(",", "")
    value = float(cleaned)
    return int(value) if value.is_integer() and "." not in cleaned else value


def _parse_toc(page: Any) -> list[dict[str, str]]:
    """Parse the Table-of-Contents page into ordered ``{section, page}`` entries.

    The cover's two-column layout interleaves section entries with unrelated
    descriptive text; only lines that match ``caption .... page`` are kept, in the
    order printed.
    """
    entries: list[dict[str, str]] = []
    for line in (page.extract_text() or "").splitlines():
        match = _TOC_ENTRY.match(line.strip())
        if not match:
            continue
        caption = match.group(1).strip()
        if not caption or caption.lower() == "section":
            continue
        entries.append({"section": caption, "page": match.group(2)})
    return entries


def _page_label(lines: list[tuple[float, list[dict[str, Any]]]]) -> str | None:
    """Return the ``Page <n> of <m>`` label (the section's TOC page number)."""
    for _, words in lines:
        text = " ".join(w["text"] for w in words)
        match = re.match(r"Page\s+(\d{1,3}[A-Z]?)\s+of\s+\d", text)
        if match:
            return match.group(1)
    return None


def _section_title(lines: list[tuple[float, list[dict[str, Any]]]]) -> str | None:
    """Return the section title printed below the banner and above the first band.

    The page banner ends with a staggered ``BHC Name City/State`` / ``RSSD Number
    ...`` column-label pair; the section title is the single line printed below it
    and immediately above the first date-header band.
    """
    first_band = next(
        (
            top
            for top, words in lines
            if sum(1 for w in words if _DATE.match(w["text"])) >= 5
        ),
        None,
    )
    if first_band is None:
        return None
    banner_bottom = max(
        (
            top
            for top, words in lines
            if top < first_band
            and (
                " ".join(w["text"] for w in words).startswith("BHC Name")
                or "RSSD Number" in " ".join(w["text"] for w in words)
            )
        ),
        default=None,
    )
    if banner_bottom is None:
        return None
    candidates = [
        " ".join(w["text"] for w in words).strip()
        for top, words in lines
        if banner_bottom < top < first_band
    ]
    return candidates[0] if candidates else None


def _band_starts(
    lines: list[tuple[float, list[dict[str, Any]]]],
) -> list[tuple[float, list[dict[str, Any]]]]:
    """Return each date-header row (band start) as ``(top, header_words)``."""
    starts: list[tuple[float, list[dict[str, Any]]]] = []
    for top, words in lines:
        if sum(1 for w in words if _DATE.match(w["text"])) >= 5:
            starts.append((top, words))
    return starts


def _column_grid(
    lines: list[tuple[float, list[dict[str, Any]]]],
    top: float,
    bottom: float,
) -> list[float]:
    """Cluster every value cell in a band's body into column right-edges."""
    edges: list[float] = []
    for line_top, words in lines:
        if not (top < line_top < min(bottom, _FOOTER_TOP)):
            continue
        for word in words:
            if _NUMBER.match(word["text"]) and _VALUE_X0 < word["x1"] < _VALUE_X1:
                edges.append(word["x1"])
    return _cluster_right_edges(edges) if edges else []


def _period_dates(header_words: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return the five period dates in a band header, left-to-right with x-edges."""
    dates = [w for w in header_words if _DATE.match(w["text"])]
    dates.sort(key=lambda w: w["x1"])
    return dates[:5]


def _assign_columns(words: list[dict[str, Any]], grid: list[float]) -> list[str | None]:
    """Place each numeric word into the grid column whose right-edge is nearest."""
    cells: list[str | None] = [None] * len(grid)
    for word in words:
        if not (_NUMBER.match(word["text"]) and _VALUE_X0 < word["x1"] < _VALUE_X1):
            continue
        index = min(range(len(grid)), key=lambda i: abs(grid[i] - word["x1"]))
        if cells[index] is None:
            cells[index] = word["text"]
    return cells


def _amount_period_columns(
    grid: list[float], date_words: list[dict[str, Any]]
) -> list[list[int]]:
    """Map each period to its dollar value column in an amount sub-band.

    Dollar amounts right-align just right of their period's date and left of the
    next period's date, so a period's value column is the first grid cluster whose
    right-edge falls at or after that date's left edge and before the next date's
    left edge. Taking the first such cluster (rather than the rightmost) ignores
    trailing ``1-Year`` / ``5-Year`` growth columns that share the final period's
    window. The right-alignment offset varies between bands, so a positional window
    is used rather than a fixed distance tolerance.
    """
    columns: list[list[int]] = []
    for position, date_word in enumerate(date_words):
        lower = date_word["x0"] - 4.0
        upper = (
            date_words[position + 1]["x0"] - 4.0
            if position + 1 < len(date_words)
            else _VALUE_X1
        )
        candidates = [i for i, edge in enumerate(grid) if lower <= edge < upper]
        columns.append([min(candidates, key=lambda i: grid[i])] if candidates else [])
    return columns


def _empty_values(dates: list[str]) -> dict[str, dict[str, Any]]:
    """Return a blank ``{date: {bhc, peer, pct}}`` map for the band's periods."""
    return {date: {"bhc": None, "peer": None, "pct": None} for date in dates}


def _caption_and_words(
    words: list[dict[str, Any]],
) -> tuple[str, list[dict[str, Any]]]:
    """Split a body line into its caption text and its trailing numeric words."""
    text = " ".join(w["text"] for w in words)
    leader = _LEADER.search(text)
    if leader:
        caption = text[: leader.start()].strip()
    else:
        caption = " ".join(
            w["text"] for w in words if not _NUMBER.match(w["text"])
        ).strip()
    numeric = [w for w in words if _NUMBER.match(w["text"])]
    return caption, numeric


def _caption_level(x0: float) -> int:
    """Return a caption's indent level from its left margin."""
    if x0 <= 40:
        return 0
    if x0 <= 60:
        return 1
    return 2


def _marks_thousands(*texts: str) -> bool:
    """Return whether any governing text marks a thousands-dollar unit."""
    return any(_THOUSANDS.search(t or "") for t in texts)


def _build_rows(
    page: Any,
    section: str,
    section_page: str,
) -> list[dict[str, Any]]:
    """Parse a single section page into its ordered header and metric rows.

    The page is split into horizontal bands at each date-header row. Indent
    sub-headers and the thousands-dollar unit are tracked per band so a dollar
    sub-section above a ratio band never rescales the ratio band's percentages.
    """
    lines = _line_words(page)
    starts = _band_starts(lines)
    if not starts:
        return []
    rows: list[dict[str, Any]] = []
    boundaries = [t for t, _ in starts] + [10**6]

    for band_index, (band_top, header_words) in enumerate(starts):
        band_bottom = min(boundaries[band_index + 1], _FOOTER_TOP)
        dates = [w["text"] for w in _period_dates(header_words)]
        header_text = " ".join(w["text"] for w in header_words)
        pct_top = _pct_label_top(lines, band_top, band_bottom)
        if pct_top is None:
            rows.extend(
                _build_sub_band(
                    lines,
                    band_top,
                    band_bottom,
                    header_words,
                    header_text,
                    dates,
                    section,
                    section_page,
                    is_ratio=False,
                )
            )
        else:
            rows.extend(
                _build_sub_band(
                    lines,
                    band_top,
                    pct_top,
                    header_words,
                    header_text,
                    dates,
                    section,
                    section_page,
                    is_ratio=False,
                )
            )
            rows.extend(
                _build_sub_band(
                    lines,
                    pct_top,
                    band_bottom,
                    header_words,
                    header_text,
                    dates,
                    section,
                    section_page,
                    is_ratio=True,
                )
            )
    return rows


def _pct_label_top(
    lines: list[tuple[float, list[dict[str, Any]]]],
    top: float,
    bottom: float,
) -> float | None:
    """Return the ``top`` of the ``BHC Peer # Pct`` label row within a date-band.

    A single date-band may carry a dollar-amount region above the ratio label row
    and the ratio grid below it; the label row's position splits the two so each
    is parsed against its own column grid.
    """
    for line_top, words in lines:
        if top < line_top < bottom and sum(1 for w in words if w["text"] == "Pct") >= 5:
            return line_top
    return None


def _build_sub_band(
    lines: list[tuple[float, list[dict[str, Any]]]],
    top: float,
    bottom: float,
    header_words: list[dict[str, Any]],
    header_text: str,
    dates: list[str],
    section: str,
    section_page: str,
    *,
    is_ratio: bool,
) -> list[dict[str, Any]]:
    """Parse one sub-band (a dollar region or a ratio region) into its rows.

    A ratio sub-band reads fifteen value columns as bank/peer/percentile per
    period; a dollar sub-band reads one bank amount per period (its column matched
    to each period date) and expands thousands to true dollars. Sub-header rows and
    the thousands-dollar unit are tracked locally so they never leak across bands.
    """
    grid = _column_grid(lines, top, bottom)
    if not grid:
        return []
    rows: list[dict[str, Any]] = []
    sub_header: str | None = None
    band_dollars = not is_ratio and _marks_thousands(header_text)
    if is_ratio:
        period_columns = [[3 * p, 3 * p + 1, 3 * p + 2] for p in range(5)]
    else:
        period_columns = _amount_period_columns(grid, _period_dates(header_words))

    for line_top, words in lines:
        if not (top < line_top < bottom):
            continue
        text = " ".join(w["text"] for w in words)
        if not text or _DATE.search(text):
            continue
        if text.startswith(_GROWTH_LABELS) or text.strip() in {
            "Percent Change",
            "Dollar Amount in Thousands",
        }:
            continue
        if sum(1 for w in words if w["text"] == "Pct") >= 5:
            continue
        caption, numeric = _caption_and_words(words)
        x0 = words[0]["x0"]
        if not numeric:
            rows.append(
                {
                    "section": section,
                    "section_page": section_page,
                    "sub_header": None if caption.endswith(":") else sub_header,
                    "caption": caption.rstrip(":"),
                    "level": _caption_level(x0),
                    "is_header": True,
                    "unit": None,
                    "values_by_period": _empty_values(dates),
                }
            )
            sub_header = caption.rstrip(":")
            continue
        cells = _assign_columns(numeric, grid)
        scale = (
            1000
            if not is_ratio
            and (band_dollars or _marks_thousands(sub_header or "", caption))
            else 1
        )
        values = _empty_values(dates)
        for period, date in enumerate(dates):
            columns = period_columns[period]
            if is_ratio:
                if columns[2] >= len(cells):
                    continue
                bhc, peer, pct = (cells[c] for c in columns)
                values[date]["bhc"] = (
                    _to_number(bhc) * scale if bhc is not None else None
                )
                values[date]["peer"] = (
                    _to_number(peer) * scale if peer is not None else None
                )
                values[date]["pct"] = _to_number(pct) if pct is not None else None
            elif columns:
                bhc = cells[columns[0]]
                values[date]["bhc"] = (
                    _to_number(bhc) * scale if bhc is not None else None
                )
        rows.append(
            {
                "section": section,
                "section_page": section_page,
                "sub_header": sub_header,
                "caption": caption,
                "level": _caption_level(x0),
                "is_header": False,
                "unit": "dollars" if scale == 1000 else "ratio",
                "values_by_period": values,
            }
        )
    return rows


def parse_bhcpr_pdf(content: bytes) -> dict[str, Any]:
    """Parse a FR BHCPR PDF into its ordered sections and rows.

    Parameters
    ----------
    content : bytes
        The raw ``ReturnFinancialReportPDF?rpt=BHCPR`` document.

    Returns
    -------
    dict[str, Any]
        ``{"toc", "sections", "rows"}`` where ``toc`` is the parsed Table of
        Contents (``[{section, page}]``), ``sections`` is the ordered list of
        section titles as printed on the data pages paired with their page label,
        and ``rows`` is the flat ordered list of report rows. Each row carries
        ``section``, ``section_page``, ``sub_header`` (``None`` for top-level
        captions and sub-header rows themselves), ``caption``, ``level``,
        ``is_header``, and ``values_by_period`` -- a map of each period-end date to
        ``{"bhc", "peer", "pct"}`` (numbers, ``None`` where a cell is blank; dollar
        bank and peer amounts expanded from thousands to true dollars).
    """
    import pdfplumber

    pdf = pdfplumber.open(io.BytesIO(content))
    toc = _parse_toc(pdf.pages[0])
    sections: list[dict[str, str]] = []
    rows: list[dict[str, Any]] = []
    for page in pdf.pages[1:]:
        lines = _line_words(page)
        title = _section_title(lines)
        label = _page_label(lines)
        if not title or not label:
            continue
        sections.append({"section": title, "page": label})
        rows.extend(_build_rows(page, title, label))
    return {"toc": toc, "sections": sections, "rows": rows}


def _write_sections_asset(sections: list[dict[str, str]]) -> None:
    """Write the ordered section list to the committed dropdown asset."""
    import json

    ASSET_PATH.parent.mkdir(parents=True, exist_ok=True)
    ASSET_PATH.write_text(json.dumps(sections, indent=2) + "\n", encoding="utf-8")


def _main() -> None:
    """Regenerate ``assets/bhcpr/sections.json`` from a fetched or local PDF."""
    import argparse

    parser = argparse.ArgumentParser(description="Generate the BHCPR section list.")
    parser.add_argument("--id", default="1039502", help="The holding company RSSD.")
    parser.add_argument("--dt", default="20260331", help="The period as YYYYMMDD.")
    parser.add_argument("--pdf", help="Parse a local PDF instead of fetching.")
    args = parser.parse_args()

    if args.pdf:
        content = Path(args.pdf).read_bytes()
    else:
        from openbb_federal_reserve.utils import ffiec

        content = ffiec._fetch_bytes(
            f"FinancialReport/ReturnFinancialReportPDF?rpt=BHCPR&id={args.id}&dt={args.dt}",
            referer=f"{ffiec.BASE_URL}/FinancialReport/FinancialDataDownload",
        )
    parsed = parse_bhcpr_pdf(content)
    _write_sections_asset(parsed["sections"])
    print(f"Wrote {len(parsed['sections'])} sections to {ASSET_PATH}")  # noqa: T201


if __name__ == "__main__":  # pragma: no cover - module-as-script entry guard
    _main()
