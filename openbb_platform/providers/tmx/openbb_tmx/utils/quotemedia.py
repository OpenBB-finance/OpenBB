"""QuoteMedia transport for the datasets TMX serves through it."""

from typing import Any

from openbb_tmx.utils.memo import memoize

WEBMASTER_ID = "101020"
APP_URL = "https://app.quotemedia.com"
TOKEN_TTL = 60 * 25

STATEMENT_TYPES = ("IncomeStatement", "BalanceSheet", "CashFlow")


def _headers(token: str | None = None) -> dict:
    """Build the headers the QuoteMedia datatool requires."""
    from openbb_tmx.utils.cache import get_random_agent

    headers = {
        "Accept": "*/*",
        "Accept-Language": "en",
        "Origin": "https://money.tmx.com",
        "Referer": "https://money.tmx.com/",
        "User-Agent": get_random_agent(),
    }

    if token:
        headers["Datatool-Token"] = token

    return headers


async def _mint_token(tool: str) -> str:
    """Mint a datatool token for one QuoteMedia tool.

    Parameters
    ----------
    tool : str
        The tool name, or a session id already in digest form.

    Returns
    -------
    str
        The datatool token.

    Raises
    ------
    OpenBBError
        If QuoteMedia declines to issue a token.
    """
    import hashlib

    from openbb_core.app.model.abstract.error import OpenBBError

    from openbb_tmx.utils.session import get_session

    sid = (
        tool
        if len(tool) == 64 and all(c in "0123456789abcdef" for c in tool)
        else hashlib.sha256(tool.encode()).hexdigest()
    )
    url = f"{APP_URL}/auth/g/authenticate/dataTool/v0/{WEBMASTER_ID}/{sid}"
    session = await get_session()
    response = await session.post(url, data=b"", headers=_headers(), timeout=60)
    payload = await response.json(content_type=None)
    response.release()

    token = (payload or {}).get("token")

    if not token:
        raise OpenBBError(f"QuoteMedia did not authorize the {tool} tool.")

    return token


@memoize(ttl=TOKEN_TTL)
async def get_token(tool: str) -> str:
    """Return a cached datatool token for one QuoteMedia tool.

    Parameters
    ----------
    tool : str
        The tool name.

    Returns
    -------
    str
        The datatool token, reused until it expires.
    """
    return await _mint_token(tool)


async def get_datatool(
    endpoint: str, tool: str, use_cache: bool = True, **params: Any
) -> dict:
    """Call a QuoteMedia datatool endpoint and return its results.

    Parameters
    ----------
    endpoint : str
        The endpoint file name, such as 'getOptionQuotes.json'.
    tool : str
        The tool the token is scoped to.
    use_cache : bool
        Whether to read and write the on-disk cache.
    **params : Any
        Query parameters, merged with the webmaster id and tool.

    Returns
    -------
    dict
        The ``results`` member of the response.

    Raises
    ------
    OpenBBError
        If the response carries no results.
    """
    from urllib.parse import urlencode

    from openbb_core.app.model.abstract.error import OpenBBError

    from openbb_tmx.utils.cache import amake_request

    query = {"webmasterId": WEBMASTER_ID, "qmodTool": tool, **params}
    query = {
        key: ("true" if value is True else "false" if value is False else value)
        for key, value in query.items()
        if value is not None
    }
    url = f"{APP_URL}/datatool/{endpoint}?{urlencode(query, safe=',')}"
    token = await get_token(tool)
    response = await amake_request(url, use_cache=use_cache, headers=_headers(token))

    if not isinstance(response, dict) or "results" not in response:
        raise OpenBBError(f"No QuoteMedia results for {endpoint}.")

    return response["results"]


async def get_option_chain(symbol: str, use_cache: bool = True) -> dict:
    """Get the complete option chain for a symbol, with greeks.

    Parameters
    ----------
    symbol : str
        The underlying symbol.
    use_cache : bool
        Whether to read and write the on-disk cache.

    Returns
    -------
    dict
        The chain results, covering every listed expiry.
    """
    base_params = {
        "symbol": symbol,
        "greeks": True,
        "callput": "group",
        "groupDate": True,
        "inclExpired": False,
        "adjOptions": True,
        "money": "All",
        "optionSize": "all",
    }
    results = await get_datatool(
        "getOptionQuotes.json", "options", use_cache=use_cache, **base_params
    )
    dates = [
        entry["date"]
        for entry in results.get("expiryDates", {}).get("expiryDate", [])
        if entry.get("date")
    ]

    if len(dates) <= len(results.get("expiryGroup", [])):
        return results

    return await get_datatool(
        "getOptionQuotes.json",
        "options",
        use_cache=use_cache,
        expiryDates=",".join(dates),
        **base_params,
    )


ALL_REPORTS = 500


async def get_financials(
    symbol: str,
    period: str = "annual",
    limit: int = ALL_REPORTS,
    use_cache: bool = True,
) -> list[dict]:
    """Get the financial statement reports for a symbol.

    Parameters
    ----------
    symbol : str
        The company symbol.
    period : str
        Either 'annual' or 'quarter'.
    limit : int
        The number of reports to request. The feed returns every report it
        holds when asked for more than it has.
    use_cache : bool
        Whether to read and write the on-disk cache.

    Returns
    -------
    list[dict]
        One entry per reporting period.
    """
    results = await get_datatool(
        "getFinancialsEnhancedBySymbol.json",
        "Financials",
        use_cache=use_cache,
        symbol=symbol,
        lang="en",
        reportType="A" if period == "annual" else "Q",
        reportOrder="D",
        numberOfReports=limit,
        latestfiscaldate=True,
        currency=True,
        typeList=",".join(STATEMENT_TYPES),
    )
    reports = results.get("Company", {}).get("Report", [])

    return reports if isinstance(reports, list) else [reports]


SCREENER_TOOL = "5bce4b128f9078f167181cd08afb1d38aa34941e20629b8df36f902dfcf13fa0"
SCREENER_SECTIONS = (
    "companyBasics",
    "performance",
    "keyRatios",
    "dividends",
    "profitability",
    "trading",
    "balanceSheet",
)
SCREENER_BATCH = 100


async def get_screener_criteria(country: str = "CA", use_cache: bool = True) -> dict:
    """Get the screener's filter catalogue.

    Parameters
    ----------
    country : str
        The screener country, 'CA' or 'US'.
    use_cache : bool
        Whether to read and write the on-disk cache.

    Returns
    -------
    dict
        The criteria groups, each carrying its ranged and fixed filters.
    """
    from openbb_tmx.utils.cache import amake_request

    token = await get_token(SCREENER_TOOL)
    url = (
        f"{APP_URL}/screener/equity/datatool/criteria/{country}/"
        f"?webmaster_id={WEBMASTER_ID}&token={token}&language=en"
    )

    return await amake_request(url, use_cache=use_cache, headers=_headers()) or {}


async def get_screener_equities(
    symbols: "list[str]", country: str = "CA", use_cache: bool = True
) -> list[dict]:
    """Get the screener's fundamentals for a list of symbols.

    Parameters
    ----------
    symbols : list[str]
        The symbols to look up.
    country : str
        The screener country, 'CA' or 'US'.
    use_cache : bool
        Whether to read and write the on-disk cache.

    Returns
    -------
    list[dict]
        One entry per symbol, with the seven screener sections flattened.
    """
    import asyncio

    from openbb_tmx.utils.cache import amake_request

    token = await get_token(SCREENER_TOOL)
    batches = [
        symbols[i : i + SCREENER_BATCH] for i in range(0, len(symbols), SCREENER_BATCH)
    ]
    results: list[dict] = []
    semaphore = asyncio.Semaphore(4)

    async def fetch(batch: list) -> None:
        async with semaphore:
            url = (
                f"{APP_URL}/v2/screener/equities?country={country}&module=datatool"
                f"&webmaster_id={WEBMASTER_ID}&token={token}"
                f"&symbols={','.join(batch)}"
            )
            response = await amake_request(url, use_cache=use_cache, headers=_headers())
            equities = ((response or {}).get("results") or {}).get("equities") or []

            for entry in equities:
                flat: dict = {}

                for section in SCREENER_SECTIONS:
                    flat.update(entry.get(section) or {})

                if flat.get("symbol"):
                    results.append(flat)

    await asyncio.gather(*(fetch(b) for b in batches))

    return results


async def validate_symbols(symbols: "list[str]", use_cache: bool = True) -> list[dict]:
    """Resolve symbols to their canonical form and listing venue.

    Parameters
    ----------
    symbols : list[str]
        The symbols to resolve.
    use_cache : bool
        Whether to read and write the on-disk cache.

    Returns
    -------
    list[dict]
        One entry per symbol, carrying validity, the canonical symbol, and the
        exchange it resolves to.
    """
    results = await get_datatool(
        "getValidSymbols.json",
        "InteractiveChart",
        use_cache=use_cache,
        symbols=",".join(symbols),
    )
    entries = results.get("validatesymbol") or []

    return entries if isinstance(entries, list) else [entries]
