"""Nasdaq Nordic Company Fact Sheet Parsing.

The Morningstar fundamentals Nasdaq serves for Nordic shares are published only
as a co-branded PDF; the JSON sections that would carry them return empty. The
fact sheet is a fixed two-page layout, so the tables are recovered from glyph
positions rather than from the reading order, which interleaves the columns.
"""

from __future__ import annotations

import re
from itertools import takewhile
from typing import TYPE_CHECKING, Any

from async_lru import alru_cache

if TYPE_CHECKING:
    from pdfplumber.page import Page

FACTSHEET_URL = "https://lt.morningstar.com/gj8uge2g9k/stockprofile/default.aspx"

MIC_CODES = {
    "STO": "XSTO",
    "CPH": "XCSE",
    "HEL": "XHEL",
    "ICE": "XICE",
}

# Any run of digits, separators, and a sign - deliberately looser than a
# well-formed number so that two columns rendered without a gap survive as one
# token and can be split apart on glyph positions rather than silently dropped.
NUMBER = re.compile(r"-?(?=[\d,.]*\d)[\d,.]+%?")

X_TOLERANCE = 1.5

LINE_TOLERANCE = 2.5

PAGE_ONE_SPLIT = 360

PAGE_TWO_LEFT = 225

PAGE_TWO_LABEL = 478

PAGE_TWO_FOOTER = 640

AVERAGE_PERIODS = ("Current", "3 Yr Avg", "5 Yr Avg", "10 Yr Avg")

PEER_PERIODS = ("Mkt Cap (Mil)", "P/E", "ROE%")

EDGE_SLACK = 2.0

HEADER_LABEL = re.compile(r"Years\b|Instrument\b")

HEADER_ROW = re.compile(r"Yr Avg|^Mkt Cap|^Instrument")

HORIZON_PATTERNS = [
    re.compile(r"\d+ (?:Week|Month|Months|Year|Years)|YTD"),
    re.compile(r"Current|\d+ Yr Avg|\d+ Yr Avg\b|\d+ Yr"),
    re.compile(r"Q[1-4]"),
    re.compile(r"\d+Y"),
]

SECTION_TITLES = {
    "Yearly Performance",
    "Trailing Returns",
    "Financials",
    "Profitability and Valuation",
    "Compound Annual Growth Rates",
    "Profitability Analysis",
    "Financial Position",
    "Quarterly Results",
    "Valuation Analysis",
}


def build_factsheet_url(isin: str, currency: str, exchange: str) -> str:
    """Build the Morningstar fact sheet URL for a Nasdaq Nordic listing.

    Parameters
    ----------
    isin : str
        The instrument ISIN.
    currency : str
        The base currency to report in - i.e., 'SEK'.
    exchange : str
        The venue MIC, or the Nasdaq Nordic prefix - i.e., 'XSTO' or 'STO'.

    Returns
    -------
    str
        The fully-qualified fact sheet URL.
    """
    mic = MIC_CODES.get(exchange.upper(), exchange.upper())

    return (
        f"{FACTSHEET_URL}?LanguageId=en-GB&externalid={isin}"
        f"&BaseCurrencyId={currency.upper()}"
        f"&externalidexchange=EX%24%24%24%24{mic}&externalidtype=ISIN"
    )


@alru_cache(maxsize=256)
async def fetch_factsheet(isin: str, currency: str, exchange: str) -> bytes:
    """Download a Morningstar fact sheet PDF.

    Results are memoized for the life of the process; the sheet is regenerated
    daily upstream and a single PDF backs both the profile and the statements.

    Parameters
    ----------
    isin : str
        The instrument ISIN.
    currency : str
        The base currency to report in.
    exchange : str
        The venue MIC, or the Nasdaq Nordic prefix.

    Returns
    -------
    bytes
        The PDF payload.

    Raises
    ------
    OpenBBError
        If the response is not a PDF.
    """
    from openbb_core.app.model.abstract.error import OpenBBError
    from openbb_core.provider.utils.helpers import amake_request

    from openbb_nasdaq.utils.helpers import get_headers

    async def return_bytes(response, _):
        """Return the raw response body."""
        return await response.read()

    payload = await amake_request(
        build_factsheet_url(isin, currency, exchange),
        headers=get_headers("pdf"),
        response_callback=return_bytes,
    )

    if not isinstance(payload, bytes) or not payload.startswith(b"%PDF"):
        raise OpenBBError(f"No fact sheet was published for {isin}.")

    return payload


def _lines(
    page: Page,
    left: float,
    right: float,
    top: float = 0,
    bottom: float = 10_000,
) -> list[list[dict]]:
    """Cluster the words in a rectangular region into lines, top to bottom."""
    words = [
        w
        for w in page.extract_words(x_tolerance=X_TOLERANCE)
        if left <= w["x0"] < right and top <= w["top"] < bottom
    ]
    rows: dict[float, list[dict]] = {}

    for word in sorted(words, key=lambda w: w["top"]):
        key = next(
            (k for k in rows if abs(k - word["top"]) <= LINE_TOLERANCE), word["top"]
        )
        rows.setdefault(key, []).append(word)

    return [sorted(rows[k], key=lambda w: w["x0"]) for k in sorted(rows)]


def _values(words: list[dict], cells: list[dict]) -> list[str | None]:
    """Return one value per header column for a data row.

    Fact sheet figures are right-aligned under their period, so the right edge
    of each header cell is the reliable anchor - centres drift because headers
    and figures differ in width. A row may carry fewer values than the header
    has periods, and adjacent columns can render with no gap at all, so a token
    reaching back past the previous column is broken apart on glyph positions.
    """
    if not cells:
        return []

    edges = [c["x1"] for c in cells]
    tokens = [w for w in words if _is_number(w["text"]) or w["text"] == "-"]
    buckets: list[list[str]] = [[] for _ in edges]

    def column_of(position: float) -> int:
        """Return the column whose right edge the position falls within."""
        return next(
            (i for i, edge in enumerate(edges) if position <= edge + EDGE_SLACK),
            len(edges) - 1,
        )

    for word in tokens:
        index = column_of(word["x1"])

        if index and word["x0"] < edges[index - 1] - EDGE_SLACK:
            width = (word["x1"] - word["x0"]) / max(len(word["text"]), 1)

            for offset, char in enumerate(word["text"]):
                buckets[column_of(word["x0"] + width * (offset + 0.5))].append(char)

            continue

        buckets[index].append(word["text"])

    return ["".join(b).strip() or None for b in buckets]


def _is_number(text: str) -> bool:
    """Return True when the token reads as a number."""
    return bool(NUMBER.fullmatch(text))


def _label_and_values(
    line: list[dict], cells: list[dict], label_first: bool = True
) -> tuple[str, list[str | None]]:
    """Split a row into its label and its per-column values."""
    if label_first:
        label_words = list(takewhile(lambda w: not _is_number(w["text"]), line))
        value_words = line[len(label_words) :]
    else:
        trailing = list(takewhile(lambda w: not _is_number(w["text"]), reversed(line)))
        label_words = list(reversed(trailing))
        value_words = line[: len(line) - len(label_words)]

    label = " ".join(w["text"] for w in label_words).strip(" ,")

    return label, _values(value_words, cells)


def _section_name(section: str) -> str | None:
    """Return a readable section name, naming the bare-currency block."""
    if not section:
        return None

    return "Market Summary" if re.fullmatch(r"\(?[A-Z]{3}\)?", section) else section


def _year_header(line: list[dict]) -> list[dict]:
    """Return the cells of a line when it reads as a calendar period header."""
    cells = [w for w in line if re.fullmatch(r"(19|20)\d{2}(-\d{2})?", w["text"])]

    return cells if len(cells) >= 2 else []


def _merge_cells(line: list[dict], pattern: re.Pattern) -> list[dict]:
    """Group the words of a header line into cells matching a period pattern.

    The horizon headers - '1 Week', '3 Yr Avg', 'Q3' - are laid out as separate
    words, so adjacent words are joined before the pattern is applied.
    """
    cells: list[dict] = []
    current: list[dict] = []

    for word in line:
        if current and word["x0"] - current[-1]["x1"] > 4:
            cells.append(_join(current))
            current = []

        current.append(word)

    if current:
        cells.append(_join(current))

    return [c for c in cells if pattern.fullmatch(c["text"])]


def _join(words: list[dict]) -> dict:
    """Join adjacent words into one cell spanning their combined extent."""
    return {
        "text": " ".join(w["text"] for w in words),
        "x0": words[0]["x0"],
        "x1": words[-1]["x1"],
        "top": words[0]["top"],
    }


def _horizon_header(line: list[dict]) -> list[dict]:
    """Return the cells of a line when it reads as a horizon period header."""
    for pattern in HORIZON_PATTERNS:
        cells = _merge_cells(line, pattern)

        if len(cells) >= 2:
            return cells

    return []


def _period_header(line: list[dict]) -> list[dict]:
    """Return the cells of any recognised period header."""
    return _year_header(line) or _horizon_header(line)


def _parse_banded(
    page: Page, left: float, right: float, label_first: bool
) -> list[dict]:
    """Read every labelled period series in one vertical band of a page."""
    rows: list[dict] = []
    section = ""
    subsection = ""
    cells: list[dict] = []
    periods: list[str] = []

    for line in _lines(page, left, right):
        text = " ".join(w["text"] for w in line)
        title = next((t for t in SECTION_TITLES if text.startswith(t)), None)

        if title and not _period_header(line):
            section = title
            subsection = ""
            cells, periods = [], []

            continue

        header = _period_header(line)

        if header:
            cells = header
            periods = [w["text"] for w in header]
            trailing = [w for w in line if w["x0"] > header[-1]["x1"] + 4]
            leading = [w for w in line if w["x1"] < header[0]["x0"] - 4]

            if trailing and label_first is False:
                section = " ".join(w["text"] for w in trailing).strip(" ,")
            elif leading and label_first:
                heading = " ".join(w["text"] for w in leading).strip(" ,")
                subsection = "" if HEADER_LABEL.match(heading) else heading

            continue

        if not cells:
            continue

        label, values = _label_and_values(line, cells, label_first)
        label = label or subsection or section

        if not label or not any(values):
            continue

        for period, value in zip(periods, values):
            if value is not None:
                rows.append(
                    {
                        "section": _section_name(section),
                        "label": (
                            f"{subsection}: {label}"
                            if subsection and subsection != label
                            else label
                        ),
                        "period": period,
                        "value": value,
                    }
                )

    return rows


def _parse_key_stats(page: Page) -> list[dict]:
    """Read the profile block from the right-hand column of page one."""
    rows: list[dict] = []
    capture = False

    for line in _lines(page, PAGE_ONE_SPLIT, 9999):
        text = " ".join(w["text"] for w in line)

        if text.startswith("Key Stats"):
            capture = True

            continue

        if text.startswith(("Yearly Performance", "Dividends", "Source:")):
            capture = False

        if not capture or len(line) < 2:
            continue

        gaps = [i for i in range(1, len(line)) if line[i]["x0"] - line[i - 1]["x1"] > 6]

        if not gaps:
            continue

        split = gaps[-1]
        label = " ".join(w["text"] for w in line[:split]).strip(" ,")
        value = " ".join(w["text"] for w in line[split:]).strip()

        if label and value:
            rows.append({"section": "Key Stats", "label": label, "value": value})

    return rows


def parse_factsheet(payload: bytes) -> dict[str, Any]:
    """Parse a Morningstar fact sheet into long-format records.

    Parameters
    ----------
    payload : bytes
        The PDF payload.

    Returns
    -------
    dict
        'profile' holds the label/value stats and the company description,
        'series' holds one record per label, period, and value across every
        table, and 'dividends' holds the declared distributions.
    """
    from io import BytesIO

    import pdfplumber

    series: list[dict] = []
    profile: list[dict] = []
    dividends: list[dict] = []

    with pdfplumber.open(BytesIO(payload)) as pdf:
        first, second = pdf.pages[0], pdf.pages[1]
        profile.extend(_parse_description(first))
        profile.extend(_parse_key_stats(first))
        profile.extend(_parse_options_futures(second))
        dividends.extend(_parse_dividends(first))
        series.extend(_parse_banded(first, 0, PAGE_ONE_SPLIT, label_first=True))
        series.extend(_parse_banded(second, 0, PAGE_TWO_LEFT, label_first=True))
        series.extend(_parse_banded(second, PAGE_TWO_LEFT, 9999, label_first=False))
        series.extend(
            _parse_averages(second, "Profitability Analysis", 0, PAGE_TWO_LEFT)
        )
        series.extend(_parse_averages(second, "Valuation Analysis", 225, 396))
        series.extend(_parse_peers(second))

    seen: set = set()
    unique: list[dict] = []

    for row in series:
        key = (row["section"], row["label"], row["period"])

        if key in seen:
            continue

        seen.add(key)
        unique.append(row)

    return {"profile": profile, "series": unique, "dividends": dividends}


def _text(line: list[dict]) -> str:
    """Return the joined text of a line."""
    return " ".join(w["text"] for w in line)


def _anchor_edges(lines: list[list[dict]], count: int) -> list[dict]:
    """Derive column anchors from the first data row carrying every column.

    The average and peer blocks head their columns with wrapped, run-together
    text - 'Current3 Yr Avg5 Yr Avg 10 Yr' over 'Avg' - which no tokenizer
    recovers. The figures beneath are right-aligned and regular, so the columns
    are taken from the data instead.
    """
    for line in lines:
        tokens = [w for w in line if _is_number(w["text"])]

        if len(tokens) == count:
            return [{"x1": w["x1"]} for w in tokens]

    return []


def _parse_fixed_table(
    lines: list[list[dict]], periods: tuple[str, ...], section: str
) -> list[dict]:
    """Read a block whose columns are fixed and whose header does not tokenize."""
    cells = _anchor_edges(lines, len(periods))

    if not cells:
        return []

    rows: list[dict] = []

    for line in lines:
        label, values = _label_and_values(line, cells, label_first=True)

        if not label or not any(values) or HEADER_ROW.search(label):
            continue

        for period, value in zip(periods, values):
            if value is not None:
                rows.append(
                    {
                        "section": section,
                        "label": label,
                        "period": period,
                        "value": value,
                    }
                )

    return rows


def _parse_averages(page: Page, title: str, left: float, right: float) -> list[dict]:
    """Read one Current / 3 Yr / 5 Yr / 10 Yr average block."""
    lines = _lines(page, left, right)
    start = next((i for i, ln in enumerate(lines) if _text(ln).startswith(title)), None)

    if start is None:
        return []

    block: list[list[dict]] = []

    for line in lines[start + 1 :]:
        text = _text(line)

        if text.startswith(
            ("Financial Position", "Quarterly Results", "Nasdaq Disclaimer")
        ):
            break

        block.append(line)

    return _parse_fixed_table(block, AVERAGE_PERIODS, title)


def _parse_peers(page: Page) -> list[dict]:
    """Read the industry peer table from the foot of page two."""
    lines = _lines(page, 396, 9999, top=PAGE_TWO_FOOTER, bottom=760)
    block = [ln for ln in lines if not _text(ln).startswith(("Industry", "Mkt"))]

    return _parse_fixed_table(block, PEER_PERIODS, "Industry Peers")


def _parse_options_futures(page: Page) -> list[dict]:
    """Read the derivative availability flags from the foot of page two."""
    rows: list[dict] = []

    for line in _lines(page, 0, 225, top=PAGE_TWO_FOOTER, bottom=745):
        text = _text(line)

        if not text.startswith(("Options ", "Forwards ", "Futures ")):
            continue

        label, _, value = text.partition(" ")

        if value not in ("Yes", "No"):
            continue

        rows.append({"section": "Options & Futures", "label": label, "value": value})

    return rows


def _parse_description(page: Page) -> list[dict]:
    """Read the company profile prose from the head of page one."""
    lines = _lines(page, PAGE_ONE_SPLIT, 9999)
    start = next(
        (i for i, ln in enumerate(lines) if _text(ln).startswith("Company Profile")),
        None,
    )

    if start is None:
        return []

    prose: list[str] = []

    for line in lines[start + 1 :]:
        text = _text(line)

        if text.startswith("Key Stats"):
            break

        prose.append(text)

    body = " ".join(prose).strip()

    if not body:
        return []

    return [{"section": "Company Profile", "label": "Description", "value": body}]


def _parse_dividends(page: Page) -> list[dict]:
    """Read the declared dividend table from the right of page one."""
    lines = _lines(page, PAGE_ONE_SPLIT, 9999)
    start = next(
        (i for i, ln in enumerate(lines) if _text(ln).startswith("Ex Date")), None
    )

    if start is None:
        return []

    rows: list[dict] = []

    for line in lines[start + 1 :]:
        cells = [w["text"] for w in line]

        if len(cells) < 5 or not re.fullmatch(r"\d{2}/\d{2}/\d{4}", cells[0]):
            break

        rows.append(
            {
                "ex_date": cells[0],
                "payment_date": cells[1],
                "type": cells[2],
                "currency": cells[3],
                "amount": cells[-1],
            }
        )

    return rows


EXCHANGE_NAMES = {
    "stockholm": "XSTO",
    "copenhagen": "XCSE",
    "helsinki": "XHEL",
    "iceland": "XICE",
}


async def get_instrument_factsheet(symbol: str) -> dict[str, Any]:
    """Resolve a Nasdaq Nordic symbol and parse its Morningstar fact sheet.

    Parameters
    ----------
    symbol : str
        The Nasdaq Nordic instrument symbol.

    Returns
    -------
    dict
        The parsed fact sheet, or empty sections when none is published.
    """
    from openbb_nasdaq.utils.helpers import get_nasdaq_data
    from openbb_nasdaq.utils.nordic import resolve_nordic_instrument

    empty: dict[str, Any] = {"profile": [], "series": [], "dividends": []}
    instrument = await resolve_nordic_instrument(symbol)
    isin = instrument.get("isin")

    if not isin:
        return empty

    info = await get_nasdaq_data(
        f"nordic/instruments/{instrument['orderbook_id']}/info"
        f"?assetClass={instrument['asset_class']}&lang=en"
    )
    header = (info or {}).get("qdHeader") or {}
    exchange = str(header.get("exchange") or "").lower()
    mic = next(
        (code for name, code in EXCHANGE_NAMES.items() if name in exchange), "XSTO"
    )

    try:
        payload = await fetch_factsheet(isin, header.get("currency") or "SEK", mic)
    except Exception:  # noqa: BLE001
        return empty

    return parse_factsheet(payload)
