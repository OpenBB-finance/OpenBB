"""The Montreal Exchange derivatives universe."""

from openbb_tmx.utils.cache import get_random_agent
from openbb_tmx.utils.memo import memoize

DOCUMENT_TTL = 60 * 60 * 24

SUMMARY_TTL = 60 * 5

QUOTES_URL = "https://www.m-x.ca/en/trading/data/quotes"
CYCLES_URL = "https://www.m-x.ca/f_publications_en/cycles_opt_en.pdf"
OPTIONS_LIST_URL = "https://www.m-x.ca/en/trading/data/options-list"
COVERED_CALL_URL = "https://www.m-x.ca/en/resources/education/covered-call-screener"
SUMMARY_URL = "https://www.m-x.ca/en/trading/data/intra-session-summary"

LISTING_TABS = (
    "equity_option",
    "cdr_option",
    "cef_option",
    "etf_option",
    "currency_option",
    "index_option",
    "weekly_option",
)
HISTORICAL_URL = "https://www.m-x.ca/en/trading/data/historical"

INSTRUMENT_CLASSES = {
    "symbolOEQ": ("equity_option", "Equity Options", "option"),
    "symbolCDR": ("cdr_option", "CDR Options", "option"),
    "symbolCEF": ("cef_option", "Closed-End Fund Options", "option"),
    "symbolETF": ("etf_option", "ETF Options", "option"),
    "symbolSSF": ("share_future", "Share Futures", "future"),
    "symbolESF": ("etf_future", "ETF Futures", "future"),
    "symbolOCU": ("currency_option", "Currency Options", "option"),
    "symbolID": ("index_derivative", "Index Derivatives", None),
    "symbolIRD": ("interest_rate_derivative", "Interest Rate Derivatives", None),
    "symbolBTC": ("basis_trade_on_close", "Basis Trade on Close", "future"),
}

OPTION_PRODUCTS = {"SXO", "SXJ", "SXV", "OCR", "OGZ", "OGF", "OGB"}

INTEREST_RATE_PRODUCTS = {
    "COA": "One-Month CORRA Futures",
    "CRA": "Three-Month CORRA Futures",
    "BCS": "FTSE Canada Bank Credit Index Futures",
    "CGZ": "Two-Year Government of Canada Bond Futures",
    "CGF": "Five-Year Government of Canada Bond Futures",
    "CGB": "Ten-Year Government of Canada Bond Futures",
    "LGB": "Thirty-Year Government of Canada Bond Futures",
    "OCR": "Options on Three-Month CORRA Futures",
    "OGZ": "Options on Two-Year Government of Canada Bond Futures",
    "OGF": "Options on Five-Year Government of Canada Bond Futures",
    "OGB": "Options on Ten-Year Government of Canada Bond Futures",
}

INDEX_PRODUCTS = {
    "SXF": "S&P/TSX 60 Index Standard Futures",
    "SXM": "S&P/TSX 60 Index Mini Futures",
    "AXF": "Adjusted Interest Rate S&P/TSX 60 Total Return Index Futures",
    "SEG": "S&P/TSX 60 ESG Index Futures",
    "SCG": "S&P/TSX Composite ESG Index Futures",
    "SDV": "S&P/TSX 60 Dividend Index Futures",
    "SCF": "S&P/TSX Composite Index Mini Futures",
    "SXO": "S&P/TSX 60 Index Standard Options",
    "SXJ": "Sector Index Options",
    "SXV": "Sector Index Options",
    "SXA": "S&P/TSX Global Gold Index Futures",
    "SXB": "S&P/TSX Capped Financials Index Futures",
    "SXD": "S&P/TSX Composite Energy GICS Sector Total Return Index Futures",
    "SXG": "S&P/TSX Composite Financials GICS Level Sector Total Return Index Futures",
    "SXH": "S&P/TSX Capped Information Technology Index Futures",
    "SXK": "S&P/TSX Composite Index Banks (Industry Group) Futures",
    "SXR": "S&P/TSX Composite Real Estate GICS Sector Total Return Index Futures",
    "SXT": "S&P/TSX Composite Telecom Services GICS Level Sector"
    + " Total Return Index Futures",
    "SXU": "S&P/TSX Capped Utilities Index Futures",
    "SXW": "S&P/TSX Composite Insurance GICS Industry Group Total Return Index Futures",
    "SXY": "S&P/TSX Capped Energy Index Futures",
}

SUMMARY_COLUMNS = {
    "Open": "open",
    "High": "high",
    "Low": "low",
    "Last": "price",
    "Change": "net_change",
    "Volume": "volume",
    "Open Interest": "open_interest",
    "Transactions": "transactions",
    "Accrued Financing": "accrued_financing",
    "CORRA Rate": "corra_rate",
}

SUMMARY_PRICES = ("open", "high", "low", "price", "accrued_financing")

SETTLEMENT_TTL = 60 * 60

SETTLEMENT_REQUESTS = 10

SETTLEMENT_COLUMN = "Settl. price"

MONTH_CODES = {
    "January": "F",
    "February": "G",
    "March": "H",
    "April": "J",
    "May": "K",
    "June": "M",
    "July": "N",
    "August": "Q",
    "September": "U",
    "October": "V",
    "November": "X",
    "December": "Z",
}

QUOTE_SYMBOLS = {
    "COA": "/COA",
    "CRA": "/CRA",
    "CGZ": "/CGZ",
    "CGF": "/CGF",
    "CGB": "/CGB",
    "LGB": "/LGB",
    "SXF": "/SXF",
}


def _instrument_type(root: str, default: str | None) -> str | None:
    """Classify a product as an option or a future.

    Parameters
    ----------
    root : str
        The product root symbol.
    default : str or None
        The selector's own classification, when it has one.

    Returns
    -------
    str or None
        Either 'option' or 'future'.
    """
    if default is not None:
        return default

    return "option" if root in OPTION_PRODUCTS else "future"


def _parse_selectors(html: str) -> list[dict]:
    """Read every instrument selector out of the quotes page."""
    import re

    results: list[dict] = []

    for match in re.finditer(
        r'<select name="symbol" id="(\w+)"[^>]*>(.*?)</select>', html, re.S
    ):
        selector, body = match.group(1), match.group(2)

        if selector not in INSTRUMENT_CLASSES:
            continue

        asset_class, label, default_type = INSTRUMENT_CLASSES[selector]

        for value, _ in re.findall(
            r'<option value="([^"]*)"[^>]*>(.*?)</option>', body, re.S
        ):
            if not value:
                continue

            root = value.rstrip("*")
            results.append(
                {
                    "symbol": root,
                    "name": INTEREST_RATE_PRODUCTS.get(root)
                    or INDEX_PRODUCTS.get(root),
                    "instrument_type": _instrument_type(root, default_type),
                    "asset_class": asset_class,
                    "asset_class_name": label,
                    "quote_symbol": QUOTE_SYMBOLS.get(root),
                    "option_symbol": value,
                    "underlying_symbol": None,
                    "expiry_cycle": None,
                    "has_long_term_options": None,
                    "has_weekly_options": None,
                }
            )

    return results


@memoize(ttl=DOCUMENT_TTL)
async def get_instrument_universe(use_cache: bool = True) -> tuple[dict, ...]:
    """Get every instrument listed on the Montreal Exchange.

    Parameters
    ----------
    use_cache : bool
        Whether to read and write the on-disk cache.

    Returns
    -------
    tuple[dict, ...]
        One entry per listed derivative, across all ten instrument classes.

    Raises
    ------
    OpenBBError
        If no instruments could be read from the page.
    """
    from openbb_core.app.model.abstract.error import OpenBBError

    from openbb_tmx.utils.cache import amake_request

    html = await amake_request(
        f"{QUOTES_URL}?symbol=AC",
        use_cache=use_cache,
        accept_type="text",
        referer="https://www.m-x.ca/",
    )
    results = _parse_selectors(html or "")

    if not results:
        raise OpenBBError("The Montreal Exchange instrument list came back empty.")

    return tuple(await _add_underlying_names(results, use_cache))


CYCLE_NAMES = {"S": "standard", "SC": "short", "": None}


@memoize(ttl=DOCUMENT_TTL)
async def get_options_listings(use_cache: bool = True) -> dict:
    """Get the listed option classes, by instrument class.

    Parameters
    ----------
    use_cache : bool
        Whether to read and write the on-disk cache.

    Returns
    -------
    dict
        Per-symbol name, underlying symbol, class, and weekly availability.
    """
    from io import StringIO

    from pandas import read_html

    from openbb_tmx.utils.cache import amake_request

    try:
        html = await amake_request(
            OPTIONS_LIST_URL,
            use_cache=use_cache,
            accept_type="text",
            referer="https://www.m-x.ca/",
        )
        tables = (
            read_html(
                StringIO(html),
                flavor="lxml",
                keep_default_na=False,
                na_values=[""],
            )
            if html
            else []
        )
    except Exception:
        return {}
    listings: dict = {}
    weeklies: set = set()

    for tab, table in zip(LISTING_TABS, tables):
        for row in table.to_dict(orient="records"):
            symbol = str(row.get("Option Symbol") or "").strip()

            if not symbol or symbol.lower() == "nan":
                continue

            if tab == "weekly_option":
                weeklies.add(symbol)
                continue

            underlying = str(row.get("Underlying Symbol") or "").strip()
            listings[symbol] = {
                "name": str(row.get("Name of Underlying Instrument") or "").strip()
                or None,
                "underlying_symbol": underlying or None,
                "asset_class": tab,
            }

    for symbol in weeklies:
        listings.setdefault(symbol, {"name": None, "underlying_symbol": None})

    for symbol, listing in listings.items():
        listing["has_weeklies"] = symbol in weeklies

    return listings


def _parse_cycles(content: bytes) -> dict:
    """Read the expiry cycle table out of the published PDF.

    Parameters
    ----------
    content : bytes
        The PDF document.

    Returns
    -------
    dict
        Per-symbol name, cycle, long-term, and weekly availability.
    """
    from io import BytesIO

    import pdfplumber

    listings: dict = {}

    with pdfplumber.open(BytesIO(content)) as pdf:
        for page in pdf.pages:
            for table in page.extract_tables():
                for row in table:
                    if not row or len(row) < 3:
                        continue

                    name, symbol, cycle = row[0], row[1], row[2]

                    if not symbol or not name or symbol == "Symbol":
                        continue

                    flags = [str(cell or "") for cell in row[3:]]
                    listings[symbol.strip()] = {
                        "name": name.strip(),
                        "expiry_cycle": CYCLE_NAMES.get(
                            (cycle or "").strip(), (cycle or "").strip() or None
                        ),
                        "has_long_term": any("X" in c for c in flags[:-1]),
                        "has_weeklies": bool(flags) and "X" in flags[-1],
                    }

    return listings


@memoize(ttl=DOCUMENT_TTL)
async def get_expiry_cycles(use_cache: bool = True) -> dict:
    """Get the expiry cycle, LEAPS, and weekly availability per option class.

    Parameters
    ----------
    use_cache : bool
        Whether to read and write the on-disk cache.

    Returns
    -------
    dict
        Per-symbol listing metadata, empty when the document is unavailable.
    """
    from openbb_tmx.utils.cache import amake_request

    try:
        content = await amake_request(
            CYCLES_URL,
            use_cache=use_cache,
            accept_type="binary",
            referer="https://www.m-x.ca/",
        )

        return _parse_cycles(content) if content else {}
    except Exception:
        return {}


async def _add_underlying_names(
    instruments: list[dict], use_cache: bool = True
) -> list[dict]:
    """Attach the underlying's name and symbol to each listed derivative.

    Parameters
    ----------
    instruments : list[dict]
        The parsed instruments.
    use_cache : bool
        Whether to read and write the on-disk cache.

    Returns
    -------
    list[dict]
        The instruments, with names filled in where TMX publishes one.
    """
    listings = await get_options_listings(use_cache=use_cache)
    cycles = await get_expiry_cycles(use_cache=use_cache)

    for instrument in instruments:
        root = instrument["symbol"]
        listing = listings.get(root, {})
        cycle = cycles.get(root, {})

        instrument["underlying_symbol"] = listing.get("underlying_symbol")
        instrument["expiry_cycle"] = cycle.get("expiry_cycle")
        instrument["has_long_term_options"] = cycle.get("has_long_term")
        instrument["has_weekly_options"] = listing.get("has_weeklies")

        if not instrument["name"]:
            instrument["name"] = listing.get("name") or cycle.get("name")

    return instruments


async def get_instruments_by_class(
    asset_class: str | None = None, use_cache: bool = True
) -> list[dict]:
    """Get the Montreal Exchange universe, optionally for one instrument class.

    Parameters
    ----------
    asset_class : str or None
        Restrict to one class, such as 'interest_rate_derivative'.
    use_cache : bool
        Whether to read and write the on-disk cache.

    Returns
    -------
    list[dict]
        The matching instruments.
    """
    universe = await get_instrument_universe(use_cache=use_cache)

    if not asset_class:
        return list(universe)

    return [i for i in universe if i["asset_class"] == asset_class]


def _plain(html: str) -> str:
    """Return the readable text of a markup fragment."""
    import re
    from html import unescape

    return re.sub(r"\s+", " ", unescape(re.sub(r"<[^>]+>", "", html))).strip()


def _summary_value(value: str | None, field: str):
    """Return a published cell as a number.

    Parameters
    ----------
    value : str or None
        The cell's sort value, as published.
    field : str
        The field the column maps onto.

    Returns
    -------
    float or None
        The published number, or None when nothing was quoted.
    """
    try:
        number = float(value)  # ty: ignore[invalid-argument-type]
    except (TypeError, ValueError):
        return None

    return None if number == 0 and field in SUMMARY_PRICES else number


def _summary_product(title: str, roots: list[str]) -> dict:
    """Name a summary section and the products it reports.

    Parameters
    ----------
    title : str
        The section heading, as published.
    roots : list[str]
        The root symbols named in the heading.

    Returns
    -------
    dict
        The section name, and the name to give each root it covers.
    """
    import re

    product = re.sub(r"\s*\([A-Z0-9]{2,4}(?:,\s*[A-Z0-9]{2,4})*\)\s*$", "", title)

    if len(roots) == 1:
        return {"section": product, "names": {roots[0]: product}}

    return {
        "section": product,
        "names": {
            root: INDEX_PRODUCTS.get(root)
            or INTEREST_RATE_PRODUCTS.get(root)
            or product
            for root in roots
        },
    }


def _summary_rows(headers: list[str], body: str, product: dict) -> list[dict]:
    """Read one summary table into contract or product rows.

    Parameters
    ----------
    headers : list[str]
        The column headings, as published.
    body : str
        The table's row markup.
    product : dict
        The section name and the name of each root it covers.

    Returns
    -------
    list[dict]
        One entry per published row.
    """
    import re

    contract = re.compile(r'symbol=([A-Z0-9]+)\*?#([A-Z]+)([FGHJKMNQUVXZ])(\d{2})"')
    results: list[dict] = []

    for row in re.findall(r"<tr[^>]*>(.*?)</tr>", body, re.S):
        cells = re.findall(r"<td([^>]*)>(.*?)</td>", row, re.S)

        if len(cells) != len(headers):
            continue

        order = re.search(r'data-order="([^"]*)"', cells[0][0])
        listed = contract.search(cells[0][1])

        if headers[0] == "Month":
            if not listed:
                continue

            root, month, year = listed.group(1), listed.group(3), listed.group(4)
            entry = {
                "symbol": f"/{root}{month}{year[-1]}",
                "contract": f"{root}{month}{year}",
                "root": root,
                "expiration": order.group(1) if order else None,
            }
        else:
            root = _plain(cells[0][1])

            if not root:
                continue

            entry = {"symbol": f"/{root}", "contract": None, "root": root}

        entry["name"] = product["names"].get(root) or product["section"]
        entry["exchange"] = "MOE"

        for header, cell in zip(headers[1:], cells[1:]):
            field = SUMMARY_COLUMNS.get(header)

            if not field:
                continue

            found = re.search(r'data-order="([^"]*)"', cell[0])
            entry[field] = _summary_value(
                found.group(1) if found else None,
                field,
            )

        if "net_change" in entry and entry.get("price") is None:
            entry["net_change"] = None

        results.append(entry)

    return results


def _parse_summary(html: str) -> list[dict]:
    """Read every product the intra-session summary reports.

    Parameters
    ----------
    html : str
        The published summary page.

    Returns
    -------
    list[dict]
        One entry per listed contract, and one per product the exchange
        reports at the root level only.
    """
    import re

    section = re.compile(
        r'<li id="[^"]+"[^>]*>\s*<a href="#[^"]*">\s*(.*?)'
        r'(?:<span class="session">.*?</span>)?\s*</a>(.*?)</li>',
        re.S,
    )
    results: list[dict] = []

    for title, content in section.findall(html[html.find("Intra-Session Summary") :]):
        head = re.search(r"<thead>(.*?)</thead>", content, re.S)

        if not head or len(re.findall(r"<tr[^>]*>", head.group(1))) != 1:
            continue

        headers = [_plain(h) for h in re.findall(r"<th[^>]*>(.*?)</th>", head.group(1))]

        if not headers or headers[0] not in ("Month", "Symbol"):
            continue

        heading = _plain(title)
        named = re.search(r"\(([A-Z0-9, ]+)\)\s*$", heading)
        product = _summary_product(
            heading,
            [r.strip() for r in named.group(1).split(",")] if named else [],
        )

        for body in re.findall(r"<tbody[^>]*>(.*?)</tbody>", content, re.S):
            results.extend(_summary_rows(headers, body, product))

    return results


@memoize(ttl=SUMMARY_TTL)
async def get_futures_summary(use_cache: bool = True) -> tuple[dict, ...]:
    """Get every future listed on the Montreal Exchange, with its session.

    Parameters
    ----------
    use_cache : bool
        Whether to read and write the on-disk cache.

    Returns
    -------
    tuple[dict, ...]
        One entry per listed contract month, and one per product the exchange
        reports at the root level only.

    Raises
    ------
    OpenBBError
        If no products could be read from the page.
    """
    from openbb_core.app.model.abstract.error import OpenBBError

    from openbb_tmx.utils.cache import amake_request

    html = await amake_request(
        SUMMARY_URL,
        use_cache=use_cache,
        accept_type="text",
        referer="https://www.m-x.ca/",
    )
    results = _parse_summary(html or "")

    if not results:
        raise OpenBBError("The Montreal Exchange session summary came back empty.")

    return tuple(results)


def _settlement_value(value: str) -> float | None:
    """Return a published settlement cell as a number.

    Parameters
    ----------
    value : str
        The cell, as published.

    Returns
    -------
    float or None
        The settlement price, or None when the contract has none.
    """
    try:
        return float(value.replace(",", "")) or None
    except (AttributeError, ValueError):
        return None


def _contract_symbol(root: str, month: str) -> str | None:
    """Build a contract symbol from a published delivery month.

    Parameters
    ----------
    root : str
        The product root symbol.
    month : str
        The delivery month, as published.

    Returns
    -------
    str or None
        The contract symbol, or None when the cell names no month.
    """
    parts = month.split()

    if len(parts) != 2 or parts[0] not in MONTH_CODES:
        return None

    return f"/{root}{MONTH_CODES[parts[0]]}{parts[1][-1]}"


def _parse_quotes(html: str, root: str) -> dict:
    """Read the settlement price of every month one product lists.

    Parameters
    ----------
    html : str
        The published quotes page.
    root : str
        The product root the page reports.

    Returns
    -------
    dict
        The settlement price per contract symbol, and the front month's
        settlement under the root symbol.
    """
    import re

    results: dict = {}

    for table in re.findall(r"<table[^>]*>(.*?)</table>", html, re.S):
        head = re.search(r"<thead>(.*?)</thead>", table, re.S)

        if not head:
            continue

        headers = [_plain(h) for h in re.findall(r"<th[^>]*>(.*?)</th>", head.group(1))]

        if SETTLEMENT_COLUMN not in headers:
            continue

        column = headers.index(SETTLEMENT_COLUMN)

        for row in re.findall(r"<tr[^>]*>(.*?)</tr>", table, re.S):
            cells = [_plain(c) for c in re.findall(r"<td[^>]*>(.*?)</td>", row, re.S)]

            if len(cells) != len(headers):
                continue

            price = _settlement_value(cells[column])

            if price is None:
                continue

            symbol = _contract_symbol(root, cells[0])

            if symbol:
                results.setdefault(symbol, price)

            results.setdefault(f"/{root}", price)

    return results


@memoize(ttl=SETTLEMENT_TTL)
async def get_root_settlements(root: str, use_cache: bool = True) -> dict:
    """Get the settlement price of every month one product lists.

    Parameters
    ----------
    root : str
        The product root symbol.
    use_cache : bool
        Whether to read and write the on-disk cache.

    Returns
    -------
    dict
        The settlement price per contract symbol, and the front month's
        settlement under the root symbol.
    """
    from openbb_tmx.utils.cache import amake_request

    html = await amake_request(
        f"{QUOTES_URL}?symbol={root}",
        use_cache=use_cache,
        accept_type="text",
        referer="https://www.m-x.ca/",
    )

    return _parse_quotes(html or "", root)


async def get_settlement_prices(roots, use_cache: bool = True) -> dict:
    """Get the settlement price of every contract the named products list.

    Parameters
    ----------
    roots : Iterable[str]
        The product root symbols to read.
    use_cache : bool
        Whether to read and write the on-disk cache.

    Returns
    -------
    dict
        The settlement price per contract symbol, and the front month's
        settlement under each root symbol.
    """
    import asyncio

    allowed = asyncio.Semaphore(SETTLEMENT_REQUESTS)

    async def read(root: str) -> dict:
        """Read one product's quotes page."""
        async with allowed:
            try:
                return await get_root_settlements(root, use_cache=use_cache)
            except Exception:  # noqa: BLE001
                return {}

    pages = await asyncio.gather(*(read(root) for root in sorted(set(roots))))
    results: dict = {}

    for page in pages:
        results.update(page)

    return results


def _parse_series(value: str | None) -> tuple:
    """Split the screener's combined series column.

    Parameters
    ----------
    value : str or None
        The series as published.

    Returns
    -------
    tuple
        The expiration and the strike.
    """
    parts = str(value or "").split()

    if len(parts) < 3:
        return None, None

    try:
        return parts[0], float(parts[2])
    except ValueError:
        return parts[0], None


async def screen_covered_calls(
    symbol: str | None = None,
    expiration: str | None = None,
    premium: float = 5.0,
    gain: float = 5.0,
    use_cache: bool = True,
) -> list[dict]:
    """Screen listed calls for covered-write returns.

    Parameters
    ----------
    symbol : str or None
        Restrict to one underlying.
    expiration : str or None
        Restrict to one expiry month, as YYYY-MM.
    premium : float
        Minimum annualized premium return, in percent.
    gain : float
        Minimum annualized potential capital gain, in percent.
    use_cache : bool
        Whether to read and write the on-disk cache.

    Returns
    -------
    list[dict]
        One entry per contract that clears both thresholds.
    """
    from io import StringIO
    from urllib.parse import urlencode

    from pandas import read_html

    from openbb_tmx.utils.cache import amake_request

    payload = urlencode(
        {
            "symbol": (symbol or "").upper(),
            "month": expiration or "",
            "premium": premium,
            "gain": gain,
        }
    )
    html = await amake_request(
        COVERED_CALL_URL,
        use_cache=use_cache,
        accept_type="text",
        referer=COVERED_CALL_URL,
        method="POST",
        data=payload,
        headers={
            "Accept": "text/html,application/xhtml+xml,*/*",
            "Content-Type": "application/x-www-form-urlencoded",
            "Referer": COVERED_CALL_URL,
            "User-Agent": get_random_agent(),
        },
    )

    if not html:
        return []

    try:
        tables = [
            t
            for t in read_html(
                StringIO(html),
                flavor="lxml",
                keep_default_na=False,
                na_values=[""],
            )
            if "Symbol" in t.columns
        ]
    except ValueError:
        return []

    if not tables:
        return []

    frame = tables[0]
    results: list[dict] = []

    for row in frame.to_dict(orient="records"):
        expiry, strike = _parse_series(row.get("Serie / Strike Price"))

        if not expiry:
            continue

        results.append(
            {
                "symbol": row.get("Symbol"),
                "expiration": expiry,
                "strike": strike,
                "underlying_price": _quoted(row.get("Last Price")),
                "total_return": _percent(row.get("Potential Total Return (%)")),
                "premium_return": _percent(row.get("Premium Return (%)")),
                "capital_gain": _percent(row.get("Potential Capital Gain (%)")),
                "bid": _quoted(row.get("Bid Price")),
                "bid_size": _quoted(row.get("Bid Size")),
                "ask": _quoted(row.get("Ask Price")),
                "ask_size": _quoted(row.get("Ask Size")),
                "volume": row.get("Volume"),
                "open_interest": row.get("Open Int."),
            }
        )

    await _fill_underlying(results, use_cache)

    return results


def _quoted(value):
    """Return a quoted level, treating a zero as an absent quote.

    Parameters
    ----------
    value : Any
        The level as published.

    Returns
    -------
    Any
        The level, or None when nothing was quoted.
    """
    return None if value in (0, 0.0, "", None) else value


async def _fill_underlying(rows: "list[dict]", use_cache: bool = True) -> None:
    """Fill the underlying price from the quote feed, in place.

    Parameters
    ----------
    rows : list[dict]
        The screened contracts.
    use_cache : bool
        Whether to read and write the on-disk cache.
    """
    from openbb_tmx.utils import gql
    from openbb_tmx.utils.cache import amake_gql_request

    roots = sorted({r["symbol"] for r in rows if r.get("symbol")})

    if not roots:
        return

    listings = await get_options_listings(use_cache)
    listed = {
        root: (listings.get(root) or {}).get("underlying_symbol") or root
        for root in roots
    }

    try:
        response = await amake_gql_request(
            "getQuoteForSymbols",
            gql.QUOTE_FOR_SYMBOLS,
            {"symbols": sorted(set(listed.values()))},
            symbol=",".join(sorted(set(listed.values()))),
            use_cache=use_cache,
        )
    except Exception:  # noqa: BLE001
        return

    prices = {
        row["symbol"]: row.get("price")
        for row in (response or {}).get("getQuoteForSymbols") or []
        if row.get("symbol")
    }

    for row in rows:
        if row.get("underlying_price") is None:
            row["underlying_price"] = prices.get(listed.get(row["symbol"], ""))


def _percent(value) -> float | None:
    """Return a published percent as a decimal."""
    try:
        return float(value) / 100
    except (TypeError, ValueError):
        return None
