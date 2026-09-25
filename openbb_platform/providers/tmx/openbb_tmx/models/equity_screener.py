"""TMX Equity Screener Model."""

from datetime import date as dateType
from typing import Any, Literal

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import DATA_DESCRIPTIONS
from pydantic import Field

from openbb_tmx.utils.choices import (
    api_prefix,
    literal_choices,
    screener_widget_config,
)

EXCHANGES = Literal[
    "TSX", "TSXV", "CSE", "ALPHA", "NEO-L", "NEO-D", "NEO-N", "CMF", "MOE"
]
SYMBOL_TYPES = Literal[
    "Equity", "ETF", "Mutual Fund", "Money Market Fund", "Index", "Future"
]


DIRECTORY_SORT_FIELDS = {
    "market_cap": "marketCap",
    "symbol": "symbol",
    "name": "name",
    "exchange": "exchange",
}

RANGED_FIELDS = {
    "market_cap": "marketCapitalization",
    "price": "stockPrice",
    "price_change": "priceChange",
    "dividend_yield": "divYield",
    "dividend_rate": "divRate",
    "dividend_growth_3y": "divGrowthAvg3y",
    "dividend_growth_5y": "divGrowthAvg5y",
    "pe_ratio": "peRatio",
    "ps_ratio": "psRatio",
    "pb_ratio": "pbRatio",
    "pcf_ratio": "pcfRatio",
    "book_value_per_share": "bvps",
    "current_ratio": "currentRatio",
    "quick_ratio": "quickRatio",
    "debt_to_equity": "debtToEquityRatio",
    "debt_to_capital": "debtCapitalRatio",
    "eps": "latestFiscalEps",
    "gross_margin": "grossMargin",
    "ebitda_margin": "ebitdaMargin",
    "ebit_margin": "ebitMargin",
    "return_on_assets": "roa",
    "return_on_equity": "roe",
    "return_on_capital": "roc",
    "revenue_per_share": "revPs",
    "revenue_ltm": "revenueLtm",
    "total_revenue": "totalRevenue",
    "free_cash_flow": "freeCashFlow",
    "employees": "employees",
    "book_value": "bookValue",
    "total_equity": "totalEquity",
    "total_assets": "totalAssets",
    "current_liabilities": "currentLiabilities",
    "current_assets": "currentAssets",
    "beta": "beta",
    "alpha": "alpha",
    "r_squared": "r2",
    "standard_deviation": "stddev",
    "volume": "intradayVolume",
    "volume_previous_day": "yesterdaysVolume",
    "volume_avg_10d": "averageVolume10d",
    "volume_avg_30d": "averageVolume30d",
    "volume_avg_50d": "averageVolume50d",
    "volume_avg_90d": "averageVolume90d",
    "trade_value_avg_90d": "averageTradeValue90",
    "insider_holdings": "insiderHoldingPct",
    "institutional_holdings": "instHoldingPct",
    "performance_7d": "pricePerfomance7d",
    "performance_30d": "pricePerfomance30d",
    "performance_90d": "pricePerfomance90d",
    "performance_ytd": "pricePerfomanceYtd",
    "change_52w": "change52w",
    "high_52w": "high52weekPrice",
    "low_52w": "low52weekPrice",
    "revenue_growth_3y": "revenueGrowth3yr",
    "revenue_growth_5y": "revenueGrowth5yr",
    "income_growth_3y": "incomeGrowth3yr",
    "income_growth_5y": "incomeGrowth5yr",
}

QUOTE_BATCH = 60

QUOTE_FIELDS = {
    "price": "price",
    "volume": "volume",
    "openPrice": "open",
    "dayHigh": "high",
    "dayLow": "low",
    "prevClose": "prev_close",
    "weeks52high": "high_52w",
    "weeks52low": "low_52w",
    "currency": "currency",
}

NATIVE_RANGES = {
    field: field
    for field in (
        "market_cap",
        "price",
        "price_change",
        "volume",
        "open_interest",
        "high_52w",
        "low_52w",
    )
}

DEFAULT_SORTS = {"Index": "volume", "Future": "open_interest"}


class TmxEquityScreenerQueryParams(QueryParams):
    """TMX Equity Screener Query."""

    __json_schema_extra__ = {
        "exchange": {
            "x-widget_config": {
                "options": literal_choices(
                    (
                        "TSX",
                        "TSXV",
                        "CSE",
                        "ALPHA",
                        "NEO-L",
                        "NEO-D",
                        "NEO-N",
                        "CMF",
                        "MOE",
                    )
                )
            }
        },
        "symbol_type": {
            "x-widget_config": {
                "options": literal_choices(
                    (
                        "Equity",
                        "ETF",
                        "Mutual Fund",
                        "Money Market Fund",
                        "Index",
                        "Future",
                    )
                )
            }
        },
        "country": {
            "x-widget_config": {"options": literal_choices(("CA", "US", "GB"))}
        },
        "sector": {
            "x-widget_config": {
                "options": screener_widget_config()["sector"]["x-widget_config"][
                    "options"
                ]
            }
        },
        "industry_group": {
            "x-widget_config": {
                "type": "endpoint",
                "optionsEndpoint": f"{api_prefix()}/tmx/equity/screener_choices",
                "optionsParams": {"field": "industry_group", "parent": "$sector"},
            }
        },
        "industry": {
            "x-widget_config": {
                "type": "endpoint",
                "optionsEndpoint": f"{api_prefix()}/tmx/equity/screener_choices",
                "optionsParams": {
                    "field": "industry",
                    "parent": "$industry_group",
                },
            }
        },
    }

    exchange: EXCHANGES | None = Field(
        default=None, description="Restrict to one listing venue."
    )
    symbol_type: SYMBOL_TYPES | None = Field(
        default=None, description="Restrict to one instrument type."
    )
    country: Literal["CA", "US", "GB"] | None = Field(
        default="CA",
        description="Two-letter country code, or None for every market.",
    )
    sector: str | None = Field(default=None, description="Restrict to one sector.")
    industry_group: str | None = Field(
        default=None, description="Restrict to one industry group."
    )
    industry: str | None = Field(default=None, description="Restrict to one industry.")
    optionable: bool | None = Field(
        default=None, description="Restrict to instruments with listed options."
    )
    primary_symbol: bool | None = Field(
        default=None, description="Restrict to primary exchange listings."
    )
    filing_current: bool | None = Field(
        default=None, description="Restrict to issuers whose filings are current."
    )
    above_52w_high: bool | None = Field(
        default=None, description="Restrict to issues trading above their 52-week high."
    )
    below_52w_low: bool | None = Field(
        default=None, description="Restrict to issues trading below their 52-week low."
    )
    market_cap_min: float | None = Field(
        default=None, description="Minimum market capitalization."
    )
    market_cap_max: float | None = Field(
        default=None, description="Maximum market capitalization."
    )
    price_min: float | None = Field(default=None, description="Minimum stock price.")
    price_max: float | None = Field(default=None, description="Maximum stock price.")
    price_change_min: float | None = Field(
        default=None, description="Minimum price change, as a normalized percent."
    )
    price_change_max: float | None = Field(
        default=None, description="Maximum price change, as a normalized percent."
    )
    dividend_yield_min: float | None = Field(
        default=None, description="Minimum dividend yield, in percent."
    )
    dividend_yield_max: float | None = Field(
        default=None, description="Maximum dividend yield, in percent."
    )
    dividend_rate_min: float | None = Field(
        default=None, description="Minimum dividend rate."
    )
    dividend_rate_max: float | None = Field(
        default=None, description="Maximum dividend rate."
    )
    dividend_growth_3y_min: float | None = Field(
        default=None, description="Minimum three-year average dividend growth rate."
    )
    dividend_growth_3y_max: float | None = Field(
        default=None, description="Maximum three-year average dividend growth rate."
    )
    dividend_growth_5y_min: float | None = Field(
        default=None, description="Minimum five-year average dividend growth rate."
    )
    dividend_growth_5y_max: float | None = Field(
        default=None, description="Maximum five-year average dividend growth rate."
    )
    pe_ratio_min: float | None = Field(
        default=None, description="Minimum price-to-earnings ratio."
    )
    pe_ratio_max: float | None = Field(
        default=None, description="Maximum price-to-earnings ratio."
    )
    ps_ratio_min: float | None = Field(
        default=None, description="Minimum price-to-sales ratio."
    )
    ps_ratio_max: float | None = Field(
        default=None, description="Maximum price-to-sales ratio."
    )
    pb_ratio_min: float | None = Field(
        default=None, description="Minimum price-to-book ratio."
    )
    pb_ratio_max: float | None = Field(
        default=None, description="Maximum price-to-book ratio."
    )
    pcf_ratio_min: float | None = Field(
        default=None, description="Minimum price-to-cash-flow ratio."
    )
    pcf_ratio_max: float | None = Field(
        default=None, description="Maximum price-to-cash-flow ratio."
    )
    book_value_per_share_min: float | None = Field(
        default=None, description="Minimum book value per share."
    )
    book_value_per_share_max: float | None = Field(
        default=None, description="Maximum book value per share."
    )
    current_ratio_min: float | None = Field(
        default=None, description="Minimum current ratio."
    )
    current_ratio_max: float | None = Field(
        default=None, description="Maximum current ratio."
    )
    quick_ratio_min: float | None = Field(
        default=None, description="Minimum quick ratio."
    )
    quick_ratio_max: float | None = Field(
        default=None, description="Maximum quick ratio."
    )
    debt_to_equity_min: float | None = Field(
        default=None, description="Minimum debt-to-equity ratio."
    )
    debt_to_equity_max: float | None = Field(
        default=None, description="Maximum debt-to-equity ratio."
    )
    debt_to_capital_min: float | None = Field(
        default=None, description="Minimum debt-to-capital ratio."
    )
    debt_to_capital_max: float | None = Field(
        default=None, description="Maximum debt-to-capital ratio."
    )
    eps_min: float | None = Field(
        default=None, description="Minimum latest fiscal earnings per share."
    )
    eps_max: float | None = Field(
        default=None, description="Maximum latest fiscal earnings per share."
    )
    gross_margin_min: float | None = Field(
        default=None, description="Minimum gross margin."
    )
    gross_margin_max: float | None = Field(
        default=None, description="Maximum gross margin."
    )
    ebitda_margin_min: float | None = Field(
        default=None, description="Minimum eBITDA margin."
    )
    ebitda_margin_max: float | None = Field(
        default=None, description="Maximum eBITDA margin."
    )
    ebit_margin_min: float | None = Field(
        default=None, description="Minimum eBIT margin."
    )
    ebit_margin_max: float | None = Field(
        default=None, description="Maximum eBIT margin."
    )
    return_on_assets_min: float | None = Field(
        default=None, description="Minimum return on assets."
    )
    return_on_assets_max: float | None = Field(
        default=None, description="Maximum return on assets."
    )
    return_on_equity_min: float | None = Field(
        default=None, description="Minimum return on equity."
    )
    return_on_equity_max: float | None = Field(
        default=None, description="Maximum return on equity."
    )
    return_on_capital_min: float | None = Field(
        default=None, description="Minimum return on capital."
    )
    return_on_capital_max: float | None = Field(
        default=None, description="Maximum return on capital."
    )
    revenue_per_share_min: float | None = Field(
        default=None, description="Minimum revenue per share."
    )
    revenue_per_share_max: float | None = Field(
        default=None, description="Maximum revenue per share."
    )
    revenue_ltm_min: float | None = Field(
        default=None, description="Minimum revenue over the last twelve months."
    )
    revenue_ltm_max: float | None = Field(
        default=None, description="Maximum revenue over the last twelve months."
    )
    total_revenue_min: float | None = Field(
        default=None, description="Minimum total revenue."
    )
    total_revenue_max: float | None = Field(
        default=None, description="Maximum total revenue."
    )
    free_cash_flow_min: float | None = Field(
        default=None, description="Minimum free cash flow."
    )
    free_cash_flow_max: float | None = Field(
        default=None, description="Maximum free cash flow."
    )
    employees_min: float | None = Field(
        default=None, description="Minimum number of employees."
    )
    employees_max: float | None = Field(
        default=None, description="Maximum number of employees."
    )
    book_value_min: float | None = Field(
        default=None, description="Minimum book value."
    )
    book_value_max: float | None = Field(
        default=None, description="Maximum book value."
    )
    total_equity_min: float | None = Field(
        default=None, description="Minimum total equity."
    )
    total_equity_max: float | None = Field(
        default=None, description="Maximum total equity."
    )
    total_assets_min: float | None = Field(
        default=None, description="Minimum total assets."
    )
    total_assets_max: float | None = Field(
        default=None, description="Maximum total assets."
    )
    current_liabilities_min: float | None = Field(
        default=None, description="Minimum current liabilities."
    )
    current_liabilities_max: float | None = Field(
        default=None, description="Maximum current liabilities."
    )
    current_assets_min: float | None = Field(
        default=None, description="Minimum current assets."
    )
    current_assets_max: float | None = Field(
        default=None, description="Maximum current assets."
    )
    beta_min: float | None = Field(default=None, description="Minimum beta.")
    beta_max: float | None = Field(default=None, description="Maximum beta.")
    alpha_min: float | None = Field(default=None, description="Minimum alpha.")
    alpha_max: float | None = Field(default=None, description="Maximum alpha.")
    r_squared_min: float | None = Field(default=None, description="Minimum r-squared.")
    r_squared_max: float | None = Field(default=None, description="Maximum r-squared.")
    standard_deviation_min: float | None = Field(
        default=None, description="Minimum standard deviation of returns."
    )
    standard_deviation_max: float | None = Field(
        default=None, description="Maximum standard deviation of returns."
    )
    volume_min: float | None = Field(
        default=None, description="Minimum intraday volume."
    )
    volume_max: float | None = Field(
        default=None, description="Maximum intraday volume."
    )
    volume_previous_day_min: float | None = Field(
        default=None, description="Minimum previous session volume."
    )
    volume_previous_day_max: float | None = Field(
        default=None, description="Maximum previous session volume."
    )
    volume_avg_10d_min: float | None = Field(
        default=None, description="Minimum ten-day average volume."
    )
    volume_avg_10d_max: float | None = Field(
        default=None, description="Maximum ten-day average volume."
    )
    volume_avg_30d_min: float | None = Field(
        default=None, description="Minimum thirty-day average volume."
    )
    volume_avg_30d_max: float | None = Field(
        default=None, description="Maximum thirty-day average volume."
    )
    volume_avg_50d_min: float | None = Field(
        default=None, description="Minimum fifty-day average volume."
    )
    volume_avg_50d_max: float | None = Field(
        default=None, description="Maximum fifty-day average volume."
    )
    volume_avg_90d_min: float | None = Field(
        default=None, description="Minimum ninety-day average volume."
    )
    volume_avg_90d_max: float | None = Field(
        default=None, description="Maximum ninety-day average volume."
    )
    trade_value_avg_90d_min: float | None = Field(
        default=None, description="Minimum ninety-day average trade value."
    )
    trade_value_avg_90d_max: float | None = Field(
        default=None, description="Maximum ninety-day average trade value."
    )
    insider_holdings_min: float | None = Field(
        default=None, description="Minimum insider holdings, in percent."
    )
    insider_holdings_max: float | None = Field(
        default=None, description="Maximum insider holdings, in percent."
    )
    institutional_holdings_min: float | None = Field(
        default=None, description="Minimum institutional ownership, in percent."
    )
    institutional_holdings_max: float | None = Field(
        default=None, description="Maximum institutional ownership, in percent."
    )
    performance_7d_min: float | None = Field(
        default=None, description="Minimum seven-day price performance."
    )
    performance_7d_max: float | None = Field(
        default=None, description="Maximum seven-day price performance."
    )
    performance_30d_min: float | None = Field(
        default=None, description="Minimum thirty-day price performance."
    )
    performance_30d_max: float | None = Field(
        default=None, description="Maximum thirty-day price performance."
    )
    performance_90d_min: float | None = Field(
        default=None, description="Minimum ninety-day price performance."
    )
    performance_90d_max: float | None = Field(
        default=None, description="Maximum ninety-day price performance."
    )
    performance_ytd_min: float | None = Field(
        default=None, description="Minimum year-to-date price performance."
    )
    performance_ytd_max: float | None = Field(
        default=None, description="Maximum year-to-date price performance."
    )
    change_52w_min: float | None = Field(
        default=None, description="Minimum fifty-two week change."
    )
    change_52w_max: float | None = Field(
        default=None, description="Maximum fifty-two week change."
    )
    high_52w_min: float | None = Field(
        default=None, description="Minimum fifty-two week high price."
    )
    high_52w_max: float | None = Field(
        default=None, description="Maximum fifty-two week high price."
    )
    low_52w_min: float | None = Field(
        default=None, description="Minimum fifty-two week low price."
    )
    low_52w_max: float | None = Field(
        default=None, description="Maximum fifty-two week low price."
    )
    revenue_growth_3y_min: float | None = Field(
        default=None, description="Minimum three-year annual revenue growth."
    )
    revenue_growth_3y_max: float | None = Field(
        default=None, description="Maximum three-year annual revenue growth."
    )
    revenue_growth_5y_min: float | None = Field(
        default=None, description="Minimum five-year annual revenue growth."
    )
    revenue_growth_5y_max: float | None = Field(
        default=None, description="Maximum five-year annual revenue growth."
    )
    income_growth_3y_min: float | None = Field(
        default=None, description="Minimum three-year annual income growth."
    )
    income_growth_3y_max: float | None = Field(
        default=None, description="Maximum three-year annual income growth."
    )
    income_growth_5y_min: float | None = Field(
        default=None, description="Minimum five-year annual income growth."
    )
    income_growth_5y_max: float | None = Field(
        default=None, description="Maximum five-year annual income growth."
    )
    open_interest_min: float | None = Field(
        default=None, description="Minimum open interest."
    )
    open_interest_max: float | None = Field(
        default=None, description="Maximum open interest."
    )

    sort_by: str | None = Field(
        default="market_cap",
        description="The field to sort by, named as the query parameter.",
    )
    sort_order: Literal["ASC", "DESC"] = Field(
        default="DESC",
        description="The direction to sort in.",
    )
    fundamentals: bool = Field(
        default=True,
        description="Join the screener fundamentals onto the matched universe.",
    )
    limit: int = Field(
        default=100, description="The maximum number of results to return."
    )
    use_cache: bool = Field(
        default=True,
        description="Whether to use the on-disk response cache. Set to False to bypass.",
    )


def _sector_prefix(query) -> str | None:
    """Return the sector code prefix a query selects, if any."""
    from openbb_tmx.utils.choices import screener_code

    for field in ("industry", "industry_group", "sector"):
        code = screener_code(field, getattr(query, field, None))

        if code:
            return code

    return None


def _apply_fixed(rows: list[dict], query) -> list[dict]:
    """Narrow the rows by the screener's true-or-false filters.

    Parameters
    ----------
    rows : list[dict]
        The screener fundamentals.
    query : TmxEquityScreenerQueryParams
        The query carrying the selections.

    Returns
    -------
    list[dict]
        The rows that satisfy every selected filter.
    """
    flags = (
        ("optionable", "optionable"),
        ("primary_symbol", "primarySymbol"),
        ("filing_current", "filingCurrent"),
        ("above_52w_high", "above52wHigh"),
        ("below_52w_low", "below52wLow"),
    )

    for field, source in flags:
        wanted = getattr(query, field, None)

        if wanted is not None:
            rows = [r for r in rows if bool(r.get(source)) is wanted]

    prefix = _sector_prefix(query)

    if prefix:
        rows = [r for r in rows if str(r.get("sector") or "").startswith(prefix)]

    return rows


def _apply_ranges(rows: list[dict], query, sources: dict | None = None) -> list[dict]:
    """Narrow the rows by every minimum and maximum the query carries.

    Parameters
    ----------
    rows : list[dict]
        The rows to narrow.
    query : TmxEquityScreenerQueryParams
        The query carrying the bounds.
    sources : dict or None
        The key each filter reads, defaulting to the screener fundamentals.

    Returns
    -------
    list[dict]
        The rows that fall inside every supplied bound.
    """
    for field, source in (sources or RANGED_FIELDS).items():
        low = getattr(query, f"{field}_min", None)
        high = getattr(query, f"{field}_max", None)

        if low is not None:
            rows = [r for r in rows if r.get(source) is not None and r[source] >= low]

        if high is not None:
            rows = [r for r in rows if r.get(source) is not None and r[source] <= high]

    return rows


async def _quoted(rows: list[dict], use_cache: bool) -> list[dict]:
    """Join the delayed quote onto every instrument in the universe.

    Parameters
    ----------
    rows : list[dict]
        The directory rows to quote.
    use_cache : bool
        Whether to read and write the on-disk cache.

    Returns
    -------
    list[dict]
        One entry per instrument, carrying the session's quote.
    """
    import asyncio

    from openbb_tmx.utils import gql
    from openbb_tmx.utils.cache import amake_gql_request

    symbols = [str(r["symbol"]) for r in rows if r.get("symbol")]
    batches = [
        symbols[index : index + QUOTE_BATCH]
        for index in range(0, len(symbols), QUOTE_BATCH)
    ]

    async def fetch(batch: list) -> list:
        """Read one batch of quotes."""
        response = await amake_gql_request(
            "getQuoteForSymbols",
            gql.QUOTE_FOR_SYMBOLS,
            {"symbols": batch},
            use_cache=use_cache,
        )

        return (response or {}).get("getQuoteForSymbols") or []

    pages = await asyncio.gather(*(fetch(batch) for batch in batches))
    quotes = {q["symbol"]: q for page in pages for q in page if q.get("symbol")}
    results: list[dict] = []

    for row in rows:
        quote = quotes.get(str(row.get("symbol"))) or {}
        change = quote.get("percentChange")
        entry = {
            "symbol": row.get("symbol"),
            "name": quote.get("longname") or row.get("name"),
            "exchange": quote.get("exchange") or row.get("exchangeShortName"),
            "country": row.get("countryCode"),
            "symbol_type": row.get("symbolType"),
            "price_change": change / 100 if change is not None else None,
            "net_change": quote.get("priceChange"),
        }
        entry.update(
            {field: quote.get(source) for source, field in QUOTE_FIELDS.items()}
        )
        results.append(entry)

    return results


async def _listed_futures(query) -> list[dict]:
    """Read the futures the Montreal Exchange lists.

    Parameters
    ----------
    query : TmxEquityScreenerQueryParams
        The query carrying the venue selection.

    Returns
    -------
    list[dict]
        One entry per listed contract, and one per product the exchange
        reports at the root level only.
    """
    from openbb_tmx.utils.mx import get_futures_summary

    if query.exchange not in (None, "MOE") or query.country not in (None, "CA"):
        return []

    return [
        {
            "symbol": row.get("symbol"),
            "name": row.get("name"),
            "exchange": row.get("exchange"),
            "country": "CA",
            "symbol_type": "Future",
            "root": row.get("root"),
            "expiration": row.get("expiration"),
            "price": row.get("price"),
            "open": row.get("open"),
            "high": row.get("high"),
            "low": row.get("low"),
            "net_change": row.get("net_change"),
            "volume": row.get("volume"),
            "open_interest": row.get("open_interest"),
            "transactions": row.get("transactions"),
        }
        for row in await get_futures_summary(use_cache=query.use_cache)
    ]


async def _settled(rows: list[dict], use_cache: bool) -> list[dict]:
    """Join the exchange's settlement price onto every contract, in place.

    Parameters
    ----------
    rows : list[dict]
        The contracts to price.
    use_cache : bool
        Whether to read and write the on-disk cache.

    Returns
    -------
    list[dict]
        The rows, each carrying the settlement its product publishes.
    """
    from openbb_tmx.utils.mx import get_settlement_prices

    roots = {row["root"] for row in rows if row.get("root")}

    if not roots:
        return rows

    settled = await get_settlement_prices(roots, use_cache=use_cache)

    for row in rows:
        row["settlement_price"] = settled.get(str(row.get("symbol")))

    return rows


def _ordered(rows: list[dict], query, sources: dict) -> list[dict]:
    """Order the rows by the field the query sorts on, absent values last.

    Parameters
    ----------
    rows : list[dict]
        The rows to order.
    query : TmxEquityScreenerQueryParams
        The query carrying the sort.
    sources : dict
        The key each sort choice reads.

    Returns
    -------
    list[dict]
        The ordered rows.
    """
    key = sources.get(query.sort_by or "", query.sort_by or "symbol")
    ranked = [r for r in rows if r.get(key) is not None]
    ranked.sort(key=lambda r: r[key], reverse=query.sort_order != "ASC")

    return ranked + [r for r in rows if r.get(key) is None]


class TmxEquityScreenerData(Data):
    """TMX Equity Screener Data."""

    __alias_dict__ = {
        "primary_symbol": "primarySymbol",
        "filing_current": "filingCurrent",
        "market_cap": "marketCapitalization",
        "intraday_market_cap": "intradayMarketCapitalization",
        "price": "stockPrice",
        "intraday_price": "intradayStockPrice",
        "price_change": "priceChange",
        "high_52w": "high52weekPrice",
        "low_52w": "low52weekPrice",
        "above_52w_high": "above52wHigh",
        "below_52w_low": "below52wLow",
        "change_52w": "change52w",
        "performance_7d": "pricePerfomance7d",
        "performance_30d": "pricePerfomance30d",
        "performance_90d": "pricePerfomance90d",
        "performance_ytd": "pricePerfomanceYtd",
        "volume": "intradayVolume",
        "volume_previous_day": "yesterdaysVolume",
        "volume_avg_10d": "averageVolume10d",
        "volume_avg_30d": "averageVolume30d",
        "volume_avg_50d": "averageVolume50d",
        "volume_avg_90d": "averageVolume90d",
        "trade_value_avg_90d": "averageTradeValue90",
        "r_squared": "r2",
        "standard_deviation": "stddev",
        "insider_holdings": "insiderHoldingPct",
        "institutional_holdings": "instHoldingPct",
        "pe_ratio": "peRatio",
        "ps_ratio": "psRatio",
        "pb_ratio": "pbRatio",
        "pcf_ratio": "pcfRatio",
        "book_value_per_share": "bvps",
        "eps": "latestFiscalEps",
        "current_ratio": "currentRatio",
        "quick_ratio": "quickRatio",
        "debt_to_equity": "debtToEquityRatio",
        "debt_to_capital": "debtCapitalRatio",
        "gross_margin": "grossMargin",
        "ebitda_margin": "ebitdaMargin",
        "ebit_margin": "ebitMargin",
        "return_on_assets": "roa",
        "return_on_equity": "roe",
        "return_on_capital": "roc",
        "dividend_yield": "divYield",
        "dividend_rate": "divRate",
        "dividend_growth_3y": "divGrowthAvg3y",
        "dividend_growth_5y": "divGrowthAvg5y",
        "revenue_ltm": "revenueLtm",
        "total_revenue": "totalRevenue",
        "revenue_per_share": "revPs",
        "revenue_growth_3y": "revenueGrowth3yr",
        "revenue_growth_5y": "revenueGrowth5yr",
        "income_growth_3y": "incomeGrowth3yr",
        "income_growth_5y": "incomeGrowth5yr",
        "free_cash_flow": "freeCashFlow",
        "book_value": "bookValue",
        "total_assets": "totalAssets",
        "total_equity": "totalEquity",
        "current_assets": "currentAssets",
        "current_liabilities": "currentLiabilities",
    }

    symbol: str = Field(description=DATA_DESCRIPTIONS.get("symbol", ""))
    name: str | None = Field(default=None, description="Name of the instrument.")
    exchange: str | None = Field(default=None, description="The listing venue.")
    country: str | None = Field(default=None, description="The country of listing.")
    symbol_type: str | None = Field(default=None, description="The instrument type.")
    expiration: dateType | None = Field(
        default=None, description="The delivery month of the contract."
    )
    currency: str | None = Field(
        default=None, description="The currency the instrument trades in."
    )
    sector: int | None = Field(
        default=None,
        description="The published sector, industry group, and industry code.",
    )
    primary_symbol: bool | None = Field(
        default=None, description="Whether this is the primary listing of the issue."
    )
    filing_current: bool | None = Field(
        default=None, description="Whether the issuer's filings are current."
    )
    optionable: bool | None = Field(
        default=None, description="Whether the instrument has listed options."
    )
    market_cap: float | None = Field(
        default=None, description="The market capitalization."
    )
    intraday_market_cap: float | None = Field(
        default=None, description="The intraday market capitalization."
    )
    price: float | None = Field(default=None, description="The last price.")
    settlement_price: float | None = Field(
        default=None, description="The exchange's settlement price for the contract."
    )
    intraday_price: float | None = Field(
        default=None, description="The intraday price."
    )
    open: float | None = Field(default=None, description="The session's opening price.")
    high: float | None = Field(default=None, description="The session's high price.")
    low: float | None = Field(default=None, description="The session's low price.")
    prev_close: float | None = Field(
        default=None, description="The previous session's closing price."
    )
    price_change: float | None = Field(
        default=None,
        description="The price change, as a normalized percent.",
        json_schema_extra={
            "x-unit_measurement": "percent",
            "x-frontend_multiply": 100,
        },
    )
    net_change: float | None = Field(
        default=None,
        description="The change in price from the previous session.",
    )
    high_52w: float | None = Field(
        default=None, description="The fifty-two week high price."
    )
    low_52w: float | None = Field(
        default=None, description="The fifty-two week low price."
    )
    above_52w_high: bool | None = Field(
        default=None,
        description="Whether the issue trades above its fifty-two week high.",
    )
    below_52w_low: bool | None = Field(
        default=None,
        description="Whether the issue trades below its fifty-two week low.",
    )
    change_52w: float | None = Field(
        default=None,
        description="The fifty-two week change, as a normalized percent.",
        json_schema_extra={
            "x-unit_measurement": "percent",
            "x-frontend_multiply": 100,
        },
    )
    performance_7d: float | None = Field(
        default=None,
        description="The seven-day price performance.",
        json_schema_extra={
            "x-unit_measurement": "percent",
            "x-frontend_multiply": 100,
        },
    )
    performance_30d: float | None = Field(
        default=None,
        description="The thirty-day price performance.",
        json_schema_extra={
            "x-unit_measurement": "percent",
            "x-frontend_multiply": 100,
        },
    )
    performance_90d: float | None = Field(
        default=None,
        description="The ninety-day price performance.",
        json_schema_extra={
            "x-unit_measurement": "percent",
            "x-frontend_multiply": 100,
        },
    )
    performance_ytd: float | None = Field(
        default=None,
        description="The year-to-date price performance.",
        json_schema_extra={
            "x-unit_measurement": "percent",
            "x-frontend_multiply": 100,
        },
    )
    volume: int | None = Field(default=None, description="The intraday volume.")
    open_interest: int | None = Field(
        default=None, description="The number of contracts outstanding."
    )
    transactions: int | None = Field(
        default=None, description="The number of transactions in the session."
    )
    volume_previous_day: int | None = Field(
        default=None, description="The previous session volume."
    )
    volume_avg_10d: int | None = Field(
        default=None, description="The ten-day average volume."
    )
    volume_avg_30d: int | None = Field(
        default=None, description="The thirty-day average volume."
    )
    volume_avg_50d: int | None = Field(
        default=None, description="The fifty-day average volume."
    )
    volume_avg_90d: int | None = Field(
        default=None, description="The ninety-day average volume."
    )
    trade_value_avg_90d: float | None = Field(
        default=None, description="The ninety-day average trade value."
    )
    beta: float | None = Field(default=None, description="Beta.")
    alpha: float | None = Field(default=None, description="Alpha.")
    r_squared: float | None = Field(default=None, description="R-squared.")
    standard_deviation: float | None = Field(
        default=None, description="The standard deviation of returns."
    )
    insider_holdings: float | None = Field(
        default=None, description="Insider holdings, in percent."
    )
    institutional_holdings: float | None = Field(
        default=None, description="Institutional ownership, in percent."
    )
    pe_ratio: float | None = Field(
        default=None, description="The price-to-earnings ratio."
    )
    ps_ratio: float | None = Field(
        default=None, description="The price-to-sales ratio."
    )
    pb_ratio: float | None = Field(default=None, description="The price-to-book ratio.")
    pcf_ratio: float | None = Field(
        default=None, description="The price-to-cash-flow ratio."
    )
    book_value_per_share: float | None = Field(
        default=None, description="The book value per share."
    )
    eps: float | None = Field(
        default=None, description="The latest fiscal earnings per share."
    )
    current_ratio: float | None = Field(default=None, description="The current ratio.")
    quick_ratio: float | None = Field(default=None, description="The quick ratio.")
    debt_to_equity: float | None = Field(
        default=None, description="The debt-to-equity ratio."
    )
    debt_to_capital: float | None = Field(
        default=None, description="The debt-to-capital ratio."
    )
    gross_margin: float | None = Field(default=None, description="The gross margin.")
    ebitda_margin: float | None = Field(default=None, description="The EBITDA margin.")
    ebit_margin: float | None = Field(default=None, description="The EBIT margin.")
    return_on_assets: float | None = Field(
        default=None, description="The return on assets."
    )
    return_on_equity: float | None = Field(
        default=None, description="The return on equity."
    )
    return_on_capital: float | None = Field(
        default=None, description="The return on capital."
    )
    dividend_yield: float | None = Field(
        default=None, description="The dividend yield, in percent."
    )
    dividend_rate: float | None = Field(default=None, description="The dividend rate.")
    dividend_growth_3y: float | None = Field(
        default=None, description="The three-year average dividend growth rate."
    )
    dividend_growth_5y: float | None = Field(
        default=None, description="The five-year average dividend growth rate."
    )
    revenue_ltm: float | None = Field(
        default=None, description="The revenue over the last twelve months."
    )
    total_revenue: float | None = Field(default=None, description="The total revenue.")
    revenue_per_share: float | None = Field(
        default=None, description="The revenue per share."
    )
    revenue_growth_3y: float | None = Field(
        default=None, description="The three-year annual revenue growth."
    )
    revenue_growth_5y: float | None = Field(
        default=None, description="The five-year annual revenue growth."
    )
    income_growth_3y: float | None = Field(
        default=None, description="The three-year annual income growth."
    )
    income_growth_5y: float | None = Field(
        default=None, description="The five-year annual income growth."
    )
    free_cash_flow: float | None = Field(
        default=None, description="The free cash flow."
    )
    book_value: float | None = Field(default=None, description="The book value.")
    total_assets: float | None = Field(default=None, description="Total assets.")
    total_equity: float | None = Field(default=None, description="Total equity.")
    current_assets: float | None = Field(default=None, description="Current assets.")
    current_liabilities: float | None = Field(
        default=None, description="Current liabilities."
    )
    employees: int | None = Field(default=None, description="The number of employees.")


class TmxEquityScreenerFetcher(
    Fetcher[TmxEquityScreenerQueryParams, list[TmxEquityScreenerData]]
):
    """TMX Equity Screener Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> TmxEquityScreenerQueryParams:
        """Transform the query."""
        transformed = params.copy()

        if transformed.get("symbol_type") not in (None, "", "Equity"):
            transformed["fundamentals"] = False

        if transformed.get("sort_by") in (None, "", "market_cap"):
            transformed["sort_by"] = DEFAULT_SORTS.get(
                transformed.get("symbol_type"), "market_cap"
            )

        return TmxEquityScreenerQueryParams(**transformed)

    @staticmethod
    async def aextract_data(
        query: TmxEquityScreenerQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Screen the listed universe.

        Raises
        ------
        EmptyDataError
            If nothing matched the screen.
        """
        from openbb_core.provider.utils.errors import EmptyDataError

        from openbb_tmx.utils.directory import get_directory_frame

        if query.symbol_type == "Future":
            rows = _apply_ranges(await _listed_futures(query), query, NATIVE_RANGES)

            if not rows:
                raise EmptyDataError("No instruments matched the screen.")

            return await _settled(
                _ordered(rows, query, NATIVE_RANGES)[: query.limit], query.use_cache
            )

        frame = await get_directory_frame(
            country=query.country,
            symbol_types=[query.symbol_type] if query.symbol_type else None,
            exchanges=[query.exchange] if query.exchange else None,
            use_cache=query.use_cache,
        )

        if query.market_cap_min is not None:
            frame = frame[frame["marketCap"] >= query.market_cap_min]

        if query.market_cap_max is not None:
            frame = frame[frame["marketCap"] <= query.market_cap_max]

        if query.optionable is not None:
            frame = frame[frame["optionable"] == query.optionable]

        if frame.empty:
            raise EmptyDataError("No instruments matched the screen.")

        ascending = query.sort_order == "ASC"
        directory_column = DIRECTORY_SORT_FIELDS.get(query.sort_by or "", "marketCap")
        frame = frame.sort_values(directory_column, ascending=ascending)

        if query.symbol_type == "Index":
            rows = _apply_ranges(
                await _quoted(frame.to_dict(orient="records"), query.use_cache),
                query,
                NATIVE_RANGES,
            )

            if not rows:
                raise EmptyDataError("No instruments matched the screen.")

            return _ordered(rows, query, NATIVE_RANGES)[: query.limit]

        if not query.fundamentals:
            return frame.head(query.limit).to_dict(orient="records")

        from openbb_tmx.utils.quotemedia import get_screener_equities

        universe = [s for s in frame["symbol"].astype(str).tolist() if ":" not in s][
            : max(query.limit * 6, 300)
        ]
        rows = await get_screener_equities(
            universe,
            country=(query.country or "CA").upper(),
            use_cache=query.use_cache,
        )

        rows = _apply_fixed(rows, query)
        rows = _apply_ranges(rows, query)

        if not rows:
            raise EmptyDataError("No instruments matched the screen.")

        if query.sort_by:
            key = RANGED_FIELDS.get(query.sort_by, query.sort_by)
            rows.sort(
                key=lambda r: (r.get(key) is None, r.get(key)),
                reverse=query.sort_order != "ASC",
            )

        return rows[: query.limit]

    @staticmethod
    def transform_data(
        query: TmxEquityScreenerQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[TmxEquityScreenerData]:
        """Transform the data and validate the model."""
        return [
            TmxEquityScreenerData.model_validate(
                {
                    **{
                        k: v
                        for k, v in d.items()
                        if k
                        not in (
                            "symbol",
                            "name",
                            "exchange",
                            "exchangeShortName",
                            "country",
                            "countryCode",
                            "symbolType",
                            "marketCap",
                            "marketCapitalization",
                            "optionable",
                            "root",
                        )
                    },
                    "symbol": d.get("symbol"),
                    "name": d.get("name"),
                    "exchange": d.get("exchange") or d.get("exchangeShortName"),
                    "country": d.get("country") or d.get("countryCode"),
                    "symbol_type": d.get("symbol_type") or d.get("symbolType"),
                    "market_cap": d.get("marketCapitalization") or d.get("marketCap"),
                    "optionable": d.get("optionable"),
                }
            )
            for d in data
        ]
