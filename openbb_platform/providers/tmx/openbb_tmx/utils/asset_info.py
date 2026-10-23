"""The asset overview served as an iframe page."""

from html import escape
from pathlib import Path
from typing import Any

_ASSETS = Path(__file__).resolve().parent.parent / "assets"
_CSS = _ASSETS / "asset_info.css"
_CONNECT = _ASSETS / "openbb_connect.js"


def _price(value: Any, digits: int = 2) -> str:
    """Render a price at a fixed precision."""
    return "-" if value is None else f"{float(value):,.{digits}f}"


def _percent(value: Any, scale: float = 100.0) -> str:
    """Render a normalized percent as percentage points."""
    return "-" if value is None else f"{float(value) * scale:,.2f}%"


def _compact(value: Any) -> str:
    """Render a large number in a compact form."""
    if value is None:
        return "-"

    number = float(value)

    for suffix, size in (("T", 1e12), ("B", 1e9), ("M", 1e6), ("K", 1e3)):
        if abs(number) >= size:
            return f"{number / size:,.2f}{suffix}"

    return f"{number:,.0f}"


def _plain(value: Any) -> str:
    """Render a value as it stands."""
    return "-" if value in (None, "") else escape(str(value))


def _stat(label: str, value: str) -> str:
    """Render one label and value row, or nothing when there is no value."""
    if value in ("-", "", None):
        return ""

    return (
        f'<div class="ai-stat"><span class="ai-stat-label">{escape(label)}</span>'
        f'<span class="ai-stat-value">{escape(str(value))}</span></div>'
    )


def _range(label: str, low: Any, high: Any, last: Any) -> str:
    """Render a low-to-high range with the last level marked on it."""
    if low is None or high is None:
        return ""

    row = _stat(label, f"{_price(low)} – {_price(high)}")

    if last is None or float(high) <= float(low):
        return row

    at = (float(last) - float(low)) / (float(high) - float(low))
    at = min(max(at, 0.0), 1.0)

    return row + f'<div class="ai-bar"><span style="left:{at * 100:.1f}%"></span></div>'


def _range_row(label: str, low: Any, high: Any) -> str:
    """Render a low-to-high pair, or nothing when either end is absent."""
    if low is None or high is None:
        return ""

    return _stat(label, f"{_price(low)} – {_price(high)}")


def _card(title: str, body: str) -> str:
    """Render one card, or nothing when it carries no rows."""
    return (
        f'<section class="ai-card"><h2>{escape(title)}</h2>{body}</section>'
        if body
        else ""
    )


def _empty_payload() -> dict:
    """Return the shape a symbol with nothing published would produce."""
    return {
        "quote": {},
        "profile": {},
        "history": [],
        "targets": {},
        "insiders": [],
        "shorts": {},
        "dividends": [],
        "earnings": [],
        "fund": {},
        "holdings": [],
        "sectors": [],
        "countries": [],
    }


async def _gather(symbol: str) -> dict:
    """Read everything the symbol publishes, tolerating what it does not.

    Parameters
    ----------
    symbol : str
        The symbol to describe.

    Returns
    -------
    dict
        One entry per dataset, absent datasets left empty.
    """
    import asyncio

    from openbb_tmx.models.calendar_earnings import TmxCalendarEarningsFetcher
    from openbb_tmx.models.equity_historical import TmxEquityHistoricalFetcher
    from openbb_tmx.models.equity_profile import TmxEquityProfileFetcher
    from openbb_tmx.models.equity_quote import TmxEquityQuoteFetcher
    from openbb_tmx.models.equity_short_interest import TmxShortInterestFetcher
    from openbb_tmx.models.etf_countries import TmxEtfCountriesFetcher
    from openbb_tmx.models.etf_holdings import TmxEtfHoldingsFetcher
    from openbb_tmx.models.etf_info import TmxEtfInfoFetcher
    from openbb_tmx.models.etf_sectors import TmxEtfSectorsFetcher
    from openbb_tmx.models.historical_dividends import TmxHistoricalDividendsFetcher
    from openbb_tmx.models.insider_trading import TmxInsiderTradingFetcher
    from openbb_tmx.models.price_target_consensus import (
        TmxPriceTargetConsensusFetcher,
    )

    async def rows(fetcher, params: dict) -> list[dict]:
        try:
            found = await fetcher.fetch_data(params, {})
        except Exception:  # noqa: BLE001
            return []

        found = found if isinstance(found, list) else [found]

        return [
            r.model_dump(exclude_none=True) for r in found if hasattr(r, "model_dump")
        ]

    one = {"symbol": symbol}
    (
        quote,
        profile,
        history,
        targets,
        insiders,
        shorts,
        dividends,
        earnings,
        fund,
        holdings,
        sectors,
        countries,
    ) = await asyncio.gather(
        rows(TmxEquityQuoteFetcher, one),
        rows(TmxEquityProfileFetcher, one),
        rows(TmxEquityHistoricalFetcher, one),
        rows(TmxPriceTargetConsensusFetcher, one),
        rows(TmxInsiderTradingFetcher, {**one, "summary": True}),
        rows(TmxShortInterestFetcher, one),
        rows(TmxHistoricalDividendsFetcher, one),
        rows(TmxCalendarEarningsFetcher, {}),
        rows(TmxEtfInfoFetcher, one),
        rows(TmxEtfHoldingsFetcher, one),
        rows(TmxEtfSectorsFetcher, one),
        rows(TmxEtfCountriesFetcher, one),
    )

    return {
        "quote": quote[0] if quote else {},
        "profile": profile[0] if profile else {},
        "history": history,
        "targets": targets[0] if targets else {},
        "insiders": insiders,
        "shorts": shorts[0] if shorts else {},
        "dividends": dividends,
        "earnings": [e for e in earnings if e.get("symbol") == symbol],
        "fund": fund[0] if fund else {},
        "holdings": holdings,
        "sectors": sectors,
        "countries": countries,
    }


def _header(symbol: str, quote: dict, profile: dict, fund: dict | None = None) -> str:
    """Render the symbol, its name, venue, and last level."""
    fund = fund or {}
    change = quote.get("change")
    direction = "ai-up" if (change or 0) >= 0 else "ai-down"
    percent = quote.get("change_percent")
    moved = (
        f'<div class="ai-change {direction}">{_price(change)}'
        f" ({_percent(percent)})</div>"
        if change is not None
        else ""
    )
    venue = quote.get("exchange") or profile.get("stock_exchange") or ""
    currency = quote.get("currency") or fund.get("currency") or ""
    name = quote.get("name") or profile.get("name") or fund.get("name")

    return (
        '<div class="ai-head"><div class="ai-title">'
        f'<div class="ai-symbol">{escape(symbol)}</div>'
        f'<div class="ai-name">{_plain(name)}</div>'
        f'<div class="ai-venue">{escape(venue)} {escape(currency)}</div>'
        "</div>"
        f'<div class="ai-price"><div class="ai-last">{_price(quote.get("last_price"))}'
        f"</div>{moved}</div></div>"
    )


def _cards(payload: dict) -> str:
    """Render every card the symbol carries data for.

    Parameters
    ----------
    payload : dict
        Everything the symbol publishes.

    Returns
    -------
    str
        The card grid.
    """
    quote = payload["quote"]
    session = "".join(
        filter(
            None,
            [
                _stat("Open", _price(quote.get("open"))),
                _stat("Previous Close", _price(quote.get("prev_close"))),
                _range(
                    "Day Range",
                    quote.get("low"),
                    quote.get("high"),
                    quote.get("last_price"),
                ),
                _range(
                    "52-Week Range",
                    quote.get("year_low"),
                    quote.get("year_high"),
                    quote.get("last_price"),
                ),
                _stat("VWAP", _price(quote.get("vwap"))),
                _stat("Volume", _compact(quote.get("volume"))),
                _stat("Volume 30D", _compact(quote.get("volume_avg_30d"))),
            ],
        )
    )
    valuation = "".join(
        filter(
            None,
            [
                _stat("Market Cap", _compact(quote.get("MarketCap"))),
                _stat("Shares Outstanding", _compact(quote.get("shares_outstanding"))),
                _stat("P/E", _price(quote.get("pe"))),
                _stat("EPS", _price(quote.get("eps"))),
                _stat("Price to Book", _price(quote.get("price_to_book"))),
                _stat("Price to Cash Flow", _price(quote.get("price_to_cf"))),
                _stat("Debt to Equity", _price(quote.get("debt_to_equity"))),
                _stat("Return on Equity", _percent(quote.get("return_on_equity"))),
                _stat("Return on Assets", _percent(quote.get("return_on_assets"))),
            ],
        )
    )
    technicals = "".join(
        filter(
            None,
            [
                _stat("21-Day Average", _price(quote.get("ma_21"))),
                _stat("50-Day Average", _price(quote.get("ma_50"))),
                _stat("200-Day Average", _price(quote.get("ma_200"))),
                _stat("Beta", _price(quote.get("beta"))),
                _stat("Alpha", _price(quote.get("alpha"))),
            ],
        )
    )
    fund = payload["fund"]
    insiders = [] if fund else payload["insiders"]
    earnings = [] if fund else payload["earnings"]

    return (
        '<div class="ai-cards">'
        + _card("Session", session)
        + _card("Performance", _returns(payload["history"]))
        + _card("Fund Facts", _fund_facts(fund))
        + _card("Valuation", "" if fund else valuation)
        + _card("Technicals", technicals)
        + _card("Analyst Coverage", _analysts(payload["targets"]))
        + _card("Ownership", _ownership(insiders, payload["shorts"]))
        + _card("Calendar", _calendar(earnings, payload["dividends"]))
        + _card("Top Holdings", _holdings(payload["holdings"]))
        + _card("Sector Weightings", _weights(payload["sectors"], "sector", "weight"))
        + _card("Countries", _weights(payload["countries"], "country", "weight"))
        + "</div>"
    )


def _intro(quote: dict, profile: dict, fund: dict) -> str:
    """Render the description beside what classifies the asset."""
    about = _about(profile, fund)
    classification = _card(
        "Fund Profile" if fund else "Company",
        _fund_classification(fund) if fund else _company_profile(quote, profile),
    )

    if not about and not classification:
        return ""

    solo = "" if about and classification else " ai-intro-solo"

    return f'<div class="ai-intro{solo}">{about}{classification}</div>'


def _company_profile(quote: dict, profile: dict) -> str:
    """Render what classifies a listed company."""
    return "".join(
        filter(
            None,
            [
                _stat("Sector", _plain(quote.get("sector") or profile.get("sector"))),
                _stat("Industry", _plain(profile.get("industry_category"))),
                _stat("Industry Group", _plain(profile.get("industry_group"))),
                _stat(
                    "Issue Type",
                    _plain(profile.get("issue_type") or quote.get("security_type")),
                ),
                _stat("Employees", _compact(profile.get("employees"))),
            ],
        )
    )


def _fund_classification(fund: dict) -> str:
    """Render what classifies a fund - issuer, mandate, and coverage."""
    esg = fund.get("esg")

    return "".join(
        filter(
            None,
            [
                _stat("Issuer", _plain(fund.get("issuer"))),
                _stat("Asset Class", _plain(fund.get("asset_class"))),
                _stat("Investment Style", _plain(fund.get("investment_style"))),
                _stat("Region", _plain(fund.get("region"))),
                _stat("Management", _plain(fund.get("index_fund"))),
                _stat("Domicile", _plain(fund.get("domicile"))),
                _stat("ESG", "" if esg is None else ("Yes" if esg else "No")),
            ],
        )
    )


def _about(profile: dict, fund: dict) -> str:
    """Render the description and the issuer's links."""
    description = profile.get("long_description") or fund.get("description")

    if not description:
        return ""

    from openbb_tmx.utils.helpers import normalize_url

    links = []
    website = normalize_url(profile.get("company_url") or fund.get("website"))

    for label, href in (
        ("Website", website),
        ("Email", f"mailto:{profile['email']}" if profile.get("email") else None),
    ):
        if href:
            links.append(f'<a href="{escape(href)}" target="_blank">{label}</a>')

    tail = f'<div class="ai-links">{"".join(links)}</div>' if links else ""

    return _card("About", f'<div class="ai-about">{escape(description)}</div>{tail}')


async def asset_info_html(symbol: str, theme: str = "dark") -> str:
    """Build the asset overview page.

    Parameters
    ----------
    symbol : str
        The symbol to describe.
    theme : str
        Either 'dark' or 'light'.

    Returns
    -------
    str
        The complete HTML document.
    """
    from openbb_tmx.utils.helpers import normalize_symbol

    symbol = normalize_symbol(symbol or "")
    payload = await _gather(symbol) if symbol else _empty_payload()
    quote: dict = payload["quote"]
    profile: dict = payload["profile"]
    style = _CSS.read_text(encoding="utf-8")
    connect = _CONNECT.read_text(encoding="utf-8")
    mode = "light" if str(theme).lower() == "light" else "dark"

    if not quote and not profile and not payload["fund"]:
        body = (
            f'<div class="ai-missing">Nothing is published for {escape(symbol)}.</div>'
        )
    else:
        body = (
            '<div class="ai-wrap">'
            + _header(symbol, quote, profile, payload["fund"])
            + _intro(quote, profile, payload["fund"])
            + _cards(payload)
            + "</div>"
        )

    return (
        f'<!doctype html><html lang="en" data-theme="{mode}"><head>'
        '<meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        f"<title>{escape(symbol)}</title><style>{style}</style></head>"
        f"<body>{body}<script>{connect}</script></body></html>"
    )


def _returns(history: "list[dict]") -> str:
    """Render the trailing returns the price history supports."""
    from datetime import date as date_type

    closes: list[tuple[Any, float]] = [
        (row.get("date"), float(row["close"]))
        for row in history
        if row.get("close") is not None
    ]

    if len(closes) < 2:
        return ""

    closes.sort(key=lambda pair: str(pair[0]))
    last_date, last = closes[-1]
    today = last_date if isinstance(last_date, date_type) else date_type.today()
    rows = []

    for label, days in (
        ("1 Month", 30),
        ("3 Months", 91),
        ("6 Months", 182),
        ("1 Year", 365),
        ("3 Years", 1095),
        ("5 Years", 1825),
    ):
        cutoff = today.toordinal() - days
        earlier = [
            close
            for when, close in closes
            if isinstance(when, date_type) and when.toordinal() <= cutoff
        ]

        if earlier:
            rows.append(_stat(label, _percent(last / earlier[-1] - 1)))

    first_of_year = [
        close
        for when, close in closes
        if isinstance(when, date_type) and when.year == today.year
    ]

    if first_of_year:
        rows.insert(0, _stat("Year to Date", _percent(last / first_of_year[0] - 1)))

    return "".join(rows)


def _analysts(targets: dict) -> str:
    """Render the analyst consensus."""
    return "".join(
        filter(
            None,
            [
                _stat("Consensus", _plain(targets.get("consensus_action"))),
                _stat("Target", _price(targets.get("target_consensus"))),
                _range_row(
                    "Target Range",
                    targets.get("target_low"),
                    targets.get("target_high"),
                ),
                _stat("Upside", _percent(targets.get("target_upside"))),
                _stat("Buy", _plain(targets.get("buy_ratings"))),
                _stat("Hold", _plain(targets.get("hold_ratings"))),
                _stat("Sell", _plain(targets.get("sell_ratings"))),
            ],
        )
    )


def _ownership(insiders: "list[dict]", shorts: dict) -> str:
    """Render the insider activity and the short interest."""
    rows = [
        _stat(
            _plain(entry.get("period")),
            f"{_compact(entry.get('net_activity'))} net",
        )
        for entry in insiders
        if entry.get("period")
    ]

    for label, key in (
        ("Shares Short", "short_interest"),
        ("Short Change", "change"),
        ("Days to Cover", "days_to_cover"),
    ):
        if shorts.get(key) is not None:
            rows.append(_stat(label, _compact(shorts[key])))

    return "".join(rows)


def _calendar(earnings: "list[dict]", dividends: "list[dict]") -> str:
    """Render the latest reporting and distribution dates, most recent first."""
    rows = []
    dividends = sorted(
        dividends,
        key=lambda entry: str(entry.get("ex_dividend_date") or ""),
        reverse=True,
    )

    for entry in earnings[:2]:
        rows.append(
            _stat(
                "Earnings",
                f"{_plain(entry.get('report_date'))}"
                + (
                    f" · {_price(entry.get('eps_consensus'))} est"
                    if entry.get("eps_consensus") is not None
                    else ""
                ),
            )
        )

    for entry in dividends[:3]:
        rows.append(
            _stat(
                f"Ex-Dividend {_plain(entry.get('ex_dividend_date'))}",
                _price(entry.get("amount"), 4),
            )
        )

    return "".join(rows)


def _fund_facts(fund: dict) -> str:
    """Render the facts a fund publishes."""
    return "".join(
        filter(
            None,
            [
                _stat("Assets", _compact(fund.get("aum"))),
                _stat("Management Fee", _percent(fund.get("management_fee"))),
                _stat("Distribution Yield", _percent(fund.get("distribution_yield"))),
                _stat("Distribution Frequency", _plain(fund.get("dividend_frequency"))),
                _stat("Inception", _plain(fund.get("inception_date"))),
                _stat("Volume 30D", _compact(fund.get("avg_volume_30d"))),
                _stat("Currency", _plain(fund.get("currency"))),
            ],
        )
    )


def _weights(rows: "list[dict]", label_key: str, weight_key: str) -> str:
    """Render a weighted breakdown, heaviest first."""
    entries = [r for r in rows if r.get(label_key) and r.get(weight_key) is not None]
    entries.sort(key=lambda r: float(r[weight_key]), reverse=True)

    return "".join(
        _stat(str(entry[label_key]), _percent(entry[weight_key]))
        for entry in entries[:12]
    )


def _holdings(rows: "list[dict]") -> str:
    """Render the largest holdings."""
    entries = [r for r in rows if r.get("name") or r.get("symbol")]

    return "".join(
        _stat(
            str(entry.get("name") or entry.get("symbol")),
            _percent(entry.get("share_percentage")),
        )
        for entry in entries[:12]
    )
