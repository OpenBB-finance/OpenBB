"""TMX Equity Profile fetcher."""

# pylint: disable=unused-argument

from datetime import (
    date as dateType,
    datetime,
)
from typing import Any
from warnings import warn

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.equity_quote import (
    EquityQuoteData,
    EquityQuoteQueryParams,
)
from openbb_core.provider.utils.descriptions import DATA_DESCRIPTIONS
from pydantic import Field, field_validator


class TmxEquityQuoteQueryParams(EquityQuoteQueryParams):
    """TMX Equity Profile query params."""

    __json_schema_extra__ = {"symbol": {"multiple_items_allowed": True}}


class TmxEquityQuoteData(EquityQuoteData):
    """TMX Equity Profile Data."""

    __alias_dict__ = {
        "last_price": "price",
        "open": "openPrice",
        "high": "dayHigh",
        "low": "dayLow",
        "change": "priceChange",
        "change_percent": "percentChange",
        "prev_close": "prevClose",
        "stock_exchange": "exchangeCode",
        "industry_category": "industry",
        "industry_group": "qmdescription",
        "exchange": "exchangeCode",
        "security_type": "datatype",
        "year_high": "weeks52high",
        "year_low": "weeks52low",
        "ma_21": "day21MovingAvg",
        "ma_50": "day50MovingAvg",
        "ma_200": "day200MovingAvg",
        "volume_avg_10d": "averageVolume10D",
        "volume_avg_30d": "averageVolume30D",
        "volume_avg_50d": "averageVolume50D",
        "market_cap": "marketCap",
        "market_cap_all_classes": "MarketCapAllClasses",
        "div_amount": "dividendAmount",
        "div_currency": "dividendCurrency",
        "div_yield": "dividendYield",
        "div_freq": "dividendFrequency",
        "div_ex_date": "exDividendDate",
        "div_pay_date": "dividendPayDate",
        "div_growth_3y": "dividend3Years",
        "div_growth_5y": "dividend5Years",
        "pe": "peRatio",
        "debt_to_equity": "totalDebtToEquity",
        "price_to_book": "priceToBook",
        "price_to_cf": "priceToCashFlow",
        "return_on_equity": "returnOnEquity",
        "return_on_assets": "returnOnAssets",
        "shares_outstanding": "shareOutStanding",
        "shares_escrow": "sharesESCROW",
        "shares_total": "totalSharesOutStanding",
    }

    name: str | None = Field(default=None, description="The name of the asset.")
    security_type: str | None = Field(
        description="The issuance type of the asset.", default=None
    )
    exchange: str | None = Field(
        default=None,
        description="The listing exchange code.",
    )
    sector: str | None = Field(default=None, description="The sector of the asset.")
    industry_category: str | None = Field(
        default=None,
        description="The industry category of the asset.",
    )
    industry_group: str | None = Field(
        default=None,
        description="The industry group of the asset.",
    )
    last_price: float | None = Field(
        default=None, description="The last price of the asset."
    )
    open: float | None = Field(
        default=None,
        description=DATA_DESCRIPTIONS.get("open", ""),
    )
    high: float | None = Field(
        default=None,
        description=DATA_DESCRIPTIONS.get("high", ""),
    )
    low: float | None = Field(
        default=None,
        description=DATA_DESCRIPTIONS.get("low", ""),
    )
    close: float | None = Field(
        default=None,
    )
    vwap: float | None = Field(
        default=None, description=DATA_DESCRIPTIONS.get("vwap", "")
    )
    volume: int | None = Field(
        default=None, description=DATA_DESCRIPTIONS.get("vwap", "")
    )
    prev_close: float | None = Field(
        default=None, description=DATA_DESCRIPTIONS.get("prev_close", "")
    )
    change: float | None = Field(
        default=None,
        description="The change in price.",
    )
    change_percent: float | None = Field(
        default=None,
        description="The change in price as a normalized percent.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    year_high: float | None = Field(
        description="Fifty-two week high.",
        default=None,
    )
    year_low: float | None = Field(
        description="Fifty-two week low.",
        default=None,
    )
    ma_21: float | None = Field(
        description="Twenty-one day moving average.",
        default=None,
    )
    ma_50: float | None = Field(
        description="Fifty day moving average.",
        default=None,
    )
    ma_200: float | None = Field(
        description="Two-hundred day moving average.",
        default=None,
    )
    volume_avg_10d: int | None = Field(
        description="Ten day average volume.",
        default=None,
    )
    volume_avg_30d: int | None = Field(
        description="Thirty day average volume.",
        default=None,
    )
    volume_avg_50d: int | None = Field(
        description="Fifty day average volume.",
        default=None,
    )
    market_cap: int | None = Field(
        description="Market capitalization.",
        default=None,
    )
    market_cap_all_classes: int | None = Field(
        description="Market capitalization of all share classes.",
        default=None,
    )
    div_amount: float | None = Field(
        description="The most recent dividend amount.",
        default=None,
    )
    div_currency: str | None = Field(
        description="The currency the dividend is paid in.",
        default=None,
    )
    div_yield: float | None = Field(
        description="The dividend yield as a normalized percentage.",
        default=None,
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    div_freq: str | None = Field(
        description="The frequency of dividend payments.",
        default=None,
    )
    div_ex_date: dateType | None = Field(
        description="The ex-dividend date.",
        default=None,
    )
    div_pay_date: dateType | None = Field(
        description="The next dividend ayment date.",
        default=None,
    )
    div_growth_3y: float | str | None = Field(
        description="The three year dividend growth as a normalized percentage.",
        default=None,
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    div_growth_5y: float | str | None = Field(
        description="The five year dividend growth as a normalized percentage.",
        default=None,
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    pe: float | str | None = Field(
        description="The price to earnings ratio.",
        default=None,
    )
    eps: float | str | None = Field(description="The earnings per share.", default=None)
    debt_to_equity: float | str | None = Field(
        description="The debt to equity ratio.",
        default=None,
    )
    price_to_book: float | str | None = Field(
        description="The price to book ratio.",
        default=None,
    )
    price_to_cf: float | str | None = Field(
        description="The price to cash flow ratio.",
        default=None,
    )
    return_on_equity: float | str | None = Field(
        description="The return on equity, as a normalized percentage.",
        default=None,
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    return_on_assets: float | str | None = Field(
        description="The return on assets, as a normalized percentage.",
        default=None,
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    beta: float | str | None = Field(
        description="The beta relative to the TSX Composite.", default=None
    )
    alpha: float | str | None = Field(
        description="The alpha relative to the TSX Composite.", default=None
    )
    shares_outstanding: int | None = Field(
        description="The number of listed shares outstanding.",
        default=None,
    )
    shares_escrow: int | None = Field(
        description="The number of shares held in escrow.",
        default=None,
    )
    shares_total: int | None = Field(
        description="The total number of shares outstanding from all classes.",
        default=None,
    )

    @field_validator(
        "div_ex_date",
        "div_pay_date",
        mode="before",
        check_fields=False,
    )
    @classmethod
    def date_validate(cls, v):  # pylint: disable=E0213
        """Return the datetime object from the date string."""
        if v:
            try:
                return datetime.strptime(v, "%Y-%m-%d").date()
            except ValueError:
                return datetime.strptime(v, "%Y-%m-%d %H:%M:%S.%f").date()
        return None

    @field_validator(
        "return_on_equity",
        "return_on_assets",
        "div_yield",
        "div_growth_3y",
        "div_growth_5y",
        "change_percent",
        mode="before",
        check_fields=False,
    )
    @classmethod
    def normalize_percent(cls, v):
        """Return percents as normalized percentage points."""
        return round(float(v) / 100, 6) if v else None


async def _quote_batch(symbols: list[str]) -> list[dict]:
    """Quote symbols the single-symbol feed does not serve.

    Parameters
    ----------
    symbols : list[str]
        The symbols to quote.

    Returns
    -------
    list[dict]
        One entry per symbol the batch query priced.
    """
    from openbb_tmx.utils import gql
    from openbb_tmx.utils.cache import amake_gql_request

    response = await amake_gql_request(
        "getQuoteForSymbols",
        gql.QUOTE_FOR_SYMBOLS,
        {"symbols": symbols},
        symbol=",".join(symbols),
    )
    rows = (response or {}).get("getQuoteForSymbols") or []
    quoted = [row for row in rows if row.get("price") is not None]

    for symbol in symbols:
        if symbol not in {row["symbol"] for row in quoted}:
            warn(f"Could not get data for {symbol}.")

    return quoted


class TmxEquityQuoteFetcher(
    Fetcher[
        TmxEquityQuoteQueryParams,
        list[TmxEquityQuoteData],
    ]
):
    """TMX Equity Quote Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> TmxEquityQuoteQueryParams:
        """Transform the query."""
        return TmxEquityQuoteQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: TmxEquityQuoteQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Return the raw data from the TMX endpoint."""
        import asyncio

        from openbb_tmx.utils import gql
        from openbb_tmx.utils.cache import amake_gql_request
        from openbb_tmx.utils.helpers import normalize_symbol

        symbols = query.symbol.split(",")
        results: list[dict] = []
        unquoted: list[str] = []

        async def create_task(symbol: str, results) -> None:
            """Fetch the quote for a single symbol."""
            from openbb_core.app.model.abstract.error import OpenBBError

            symbol = normalize_symbol(symbol)

            try:
                response = await amake_gql_request(
                    "getQuoteBySymbol",
                    gql.QUOTE_BY_SYMBOL,
                    {"symbol": symbol, "locale": "en"},
                    symbol=symbol,
                )
            except OpenBBError:
                response = None

            if response and response.get("getQuoteBySymbol"):
                results.append(response["getQuoteBySymbol"])
            else:
                unquoted.append(symbol)

        await asyncio.gather(*(create_task(symbol, results) for symbol in symbols))

        if unquoted:
            results.extend(await _quote_batch(unquoted))

        return results

    @staticmethod
    def transform_data(
        query: TmxEquityQuoteQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[TmxEquityQuoteData]:
        """Return the transformed data."""
        # pylint: disable=import-outside-toplevel
        from numpy import nan

        items_list = [
            "shortDescription",
            "longDescription",
            "website",
            "phoneNumber",
            "fullAddress",
            "email",
            "issueType",
            "exchangeName",
            "employees",
            "exShortName",
        ]
        data = [{k: v for k, v in d.items() if k not in items_list} for d in data]
        for d in data:
            for k, v in d.items():
                if v in (nan, 0, ""):
                    d[k] = None
        symbols = query.symbol.split(",")
        symbol_to_index = {symbol: index for index, symbol in enumerate(symbols)}
        data = sorted(data, key=lambda d: symbol_to_index[d["symbol"]])

        return [TmxEquityQuoteData.model_validate(d) for d in data]
