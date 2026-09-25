"""FINRA Equity Info Model."""

from datetime import date as dateType
from typing import Any

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.equity_info import (
    EquityInfoData,
    EquityInfoQueryParams,
)
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field

LOOKUP_BATCH = 100
STATIC_BATCH = 10


class FinraEquityInfoQueryParams(EquityInfoQueryParams):
    """FINRA Equity Info Query."""

    __json_schema_extra__ = {"symbol": {"multiple_items_allowed": True}}


class FinraEquityInfoData(EquityInfoData):
    """FINRA Equity Info Data."""

    security_type: str | None = Field(
        default=None,
        description="The Morningstar security type - Stock, ETF, Closed-End Fund,"
        + " Open-End Fund, or Index.",
    )
    security_description: str | None = Field(
        default=None,
        description="The share class, or the Morningstar category of a fund.",
    )
    security_id: str | None = Field(
        default=None, description="The Morningstar security id."
    )
    performance_id: str | None = Field(
        default=None, description="The Morningstar performance id."
    )
    company_id: str | None = Field(
        default=None, description="The Morningstar company or fund id."
    )
    quote_symbol: str | None = Field(
        default=None,
        description="The real-time quote key - composite market, type, and symbol.",
    )
    exchange_name: str | None = Field(
        default=None, description="The name of the listing exchange."
    )
    region: str | None = Field(
        default=None, description="The ISO 3166 alpha-3 code of the listing region."
    )
    domicile: str | None = Field(
        default=None, description="The ISO 3166 alpha-3 code of the domicile."
    )
    currency: str | None = Field(default=None, description="The trading currency.")
    is_adr: bool | None = Field(
        default=None, description="Whether the security is a depositary receipt."
    )
    ipo_date: dateType | None = Field(
        default=None,
        description="The IPO date of a stock, or the inception date of a fund.",
    )
    fiscal_year_end_month: str | None = Field(
        default=None, description="The month the fiscal year ends."
    )
    gics_sector: str | None = Field(default=None, description="The GICS sector.")
    gics_industry: str | None = Field(default=None, description="The GICS industry.")
    gics_sub_industry: str | None = Field(
        default=None, description="The GICS sub-industry."
    )
    fund_category: str | None = Field(
        default=None, description="The Morningstar category of a fund."
    )
    last_price: float | None = Field(
        default=None, description="The last closing price."
    )
    last_price_date: dateType | None = Field(
        default=None, description="The date of the last closing price."
    )
    price_one_week_ago: float | None = Field(
        default=None, description="The closing price one week before."
    )
    nav: float | None = Field(
        default=None, description="The net asset value per share of a fund."
    )
    year_high: float | None = Field(default=None, description="The 52-week high.")
    year_high_date: dateType | None = Field(
        default=None, description="The date of the 52-week high."
    )
    year_low: float | None = Field(default=None, description="The 52-week low.")
    year_low_date: dateType | None = Field(
        default=None, description="The date of the 52-week low."
    )
    shares_outstanding: float | None = Field(
        default=None, description="The number of shares outstanding."
    )
    market_cap: float | None = Field(
        default=None, description="The market capitalization."
    )
    net_assets: float | None = Field(
        default=None, description="The total net assets of a fund."
    )
    average_volume: float | None = Field(
        default=None, description="The average daily share volume."
    )
    last_dividend: float | None = Field(
        default=None, description="The most recent dividend per share."
    )
    trailing_dividend: float | None = Field(
        default=None, description="The dividends per share over the trailing year."
    )
    dividend_yield: float | None = Field(
        default=None,
        description="The trailing dividend yield, as a percent.",
        json_schema_extra={"x-unit_measurement": "percent"},
    )
    forward_dividend_yield: float | None = Field(
        default=None,
        description="The forward dividend yield, as a percent.",
        json_schema_extra={"x-unit_measurement": "percent"},
    )
    dividend_frequency: str | None = Field(
        default=None, description="How often the dividend is paid."
    )
    ex_dividend_date: dateType | None = Field(
        default=None, description="The ex-date of the most recent dividend."
    )
    dividend_declaration_date: dateType | None = Field(
        default=None, description="The declaration date of the most recent dividend."
    )
    dividend_payment_date: dateType | None = Field(
        default=None, description="The payment date of the most recent dividend."
    )
    eps_ttm: float | None = Field(
        default=None, description="The trailing twelve-month earnings per share."
    )
    pe_ratio: float | None = Field(
        default=None, description="The trailing price-to-earnings ratio."
    )
    price_to_book: float | None = Field(
        default=None, description="The price-to-book ratio."
    )
    price_to_sales: float | None = Field(
        default=None, description="The price-to-sales ratio."
    )
    price_to_cash_flow: float | None = Field(
        default=None, description="The price-to-cash-flow ratio."
    )
    price_to_free_cash_flow: float | None = Field(
        default=None, description="The price-to-free-cash-flow ratio."
    )
    expense_ratio: float | None = Field(
        default=None,
        description="The net expense ratio of a fund, as a percent.",
        json_schema_extra={"x-unit_measurement": "percent"},
    )
    morningstar_rating: int | None = Field(
        default=None, description="The Morningstar star rating, from 1 to 5."
    )
    valuation: str | None = Field(
        default=None, description="The Morningstar quantitative valuation."
    )
    volatility_1y: float | None = Field(
        default=None,
        description="The standard deviation of returns over one year, as a percent.",
        json_schema_extra={"x-unit_measurement": "percent"},
    )
    volatility_3y: float | None = Field(
        default=None,
        description="The standard deviation of returns over three years, as a percent.",
        json_schema_extra={"x-unit_measurement": "percent"},
    )
    url: str | None = Field(
        default=None, description="The security's page on the FINRA Market Data Center."
    )


def _profile(record: dict, static: dict) -> dict:
    """Return one profile from a lookup record and its static data."""
    from openbb_finra.utils.constants import (
        MARKET_DATA_DETAIL_URL,
        MONTHS,
        SECURITY_TYPES,
    )
    from openbb_finra.utils.helpers import (
        clean,
        decode,
        first,
        to_bool,
        to_date,
        to_float,
    )

    fund = clean(static.get("secType")) not in (None, "ST")
    listing_market = clean(record.get("ListingMarket"))
    performance_id = clean(record.get("PID"))
    rating = to_float(static.get("st200"))
    fiscal_month = to_float(static.get("os378"))

    return {
        "symbol": clean(first(record.get("Ticker"), record.get("Symbol"))),
        "name": clean(
            first(
                static.get("MstarStandardName"),
                record.get("OS01W"),
                record.get("Name"),
            )
        ),
        "cusip": clean(static.get("S1012")),
        "isin": clean(record.get("ISIN")),
        "stock_exchange": clean(first(static.get("MicCode"), record.get("Exch"))),
        "exchange_name": clean(static.get("os01x")),
        "company_url": clean(static.get("of00b")),
        "sector": clean(static.get("st152")),
        "industry_category": clean(first(static.get("st153"), record.get("ST153"))),
        "industry_group": clean(static.get("sta4l")),
        "gics_sector": clean(static.get("sta4n")),
        "gics_industry": clean(static.get("sta4j")),
        "gics_sub_industry": clean(static.get("sta4h")),
        "fund_category": clean(static.get("of028")),
        "security_type": decode(
            SECURITY_TYPES, first(static.get("secType"), record.get("Type"))
        ),
        "security_description": clean(first(static.get("S13"), record.get("AC021"))),
        "security_id": clean(first(record.get("SecId"), static.get("secId"))),
        "performance_id": performance_id,
        "company_id": clean(record.get("CFID")),
        "quote_symbol": clean(static.get("tfTicker")),
        "region": clean(record.get("Region")),
        "domicile": clean(record.get("DomicileCountry")),
        "currency": clean(first(static.get("S9"), record.get("Currency"))),
        "is_adr": to_bool(record.get("AA0A6")),
        "ipo_date": to_date(first(static.get("IPODATE"), record.get("IPODate"))),
        "fiscal_year_end_month": (
            decode(MONTHS, str(int(fiscal_month))) if fiscal_month else None
        ),
        "last_price": to_float(first(static.get("D20"), static.get("os065"))),
        "last_price_date": to_date(
            first(static.get("pd001"), static.get("priceLastTradeDate"))
        ),
        "price_one_week_ago": to_float(static.get("Price1Week")),
        "nav": to_float(static.get("os060")),
        "year_high": to_float(static.get("os70c" if fund else "st168")),
        "year_high_date": to_date(static.get("os70d" if fund else "st109")),
        "year_low": to_float(static.get("os70e" if fund else "st169")),
        "year_low_date": to_date(static.get("os70f" if fund else "st106")),
        "shares_outstanding": to_float(static.get("S1314")),
        "market_cap": to_float(static.get("S1315")),
        "net_assets": to_float(static.get("of009")),
        "average_volume": to_float(static.get("os02w")),
        "last_dividend": to_float(static.get("NetDividend")),
        "trailing_dividend": to_float(static.get("ar112")),
        "dividend_yield": to_float(first(static.get("pm032"), static.get("st299"))),
        "forward_dividend_yield": to_float(static.get("sta65")),
        "dividend_frequency": clean(static.get("DividendFrequency")),
        "ex_dividend_date": to_date(first(static.get("EXDate"), static.get("ub170"))),
        "dividend_declaration_date": to_date(
            first(static.get("st468"), static.get("ub171"))
        ),
        "dividend_payment_date": to_date(
            first(static.get("st470"), static.get("ub172"))
        ),
        "eps_ttm": to_float(static.get("st263")),
        "pe_ratio": to_float(static.get("S1077")),
        "price_to_book": to_float(static.get("st408")),
        "price_to_sales": to_float(static.get("st415")),
        "price_to_cash_flow": to_float(static.get("PC_RATIO")),
        "price_to_free_cash_flow": to_float(static.get("P_FCF_RATIO")),
        "expense_ratio": to_float(static.get("NETEXPENSERATIO")),
        "morningstar_rating": int(rating) if rating else None,
        "valuation": clean(static.get("qv004")),
        "volatility_1y": to_float(static.get("STANDARDDEVIATION1YR")),
        "volatility_3y": to_float(static.get("STANDARDDEVIATION3YR")),
        "url": (
            f"{MARKET_DATA_DETAIL_URL}?query={listing_market}:{performance_id}"
            if listing_market and performance_id
            else None
        ),
    }


class FinraEquityInfoFetcher(
    Fetcher[FinraEquityInfoQueryParams, list[FinraEquityInfoData]]
):
    """Transform the query, extract and transform the data from the FINRA Market Data Center."""

    require_credentials = False

    @staticmethod
    def transform_query(params: dict[str, Any]) -> FinraEquityInfoQueryParams:
        """Transform the query."""
        return FinraEquityInfoQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: FinraEquityInfoQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Return the profiles from the FINRA Market Data Center.

        Raises
        ------
        EmptyDataError
            If none of the symbols resolved to a security.
        """
        from openbb_finra.utils.client import market_data_session
        from openbb_finra.utils.helpers import clean, drop_none, first, split_symbols

        symbols = [symbol.replace("-", ".") for symbol in split_symbols(query.symbol)]

        async with market_data_session() as market_data:
            records: list[dict] = []

            for start in range(0, len(symbols), LOOKUP_BATCH):
                records.extend(
                    await market_data.lookup(symbols[start : start + LOOKUP_BATCH])
                )

            ids = [
                security_id
                for record in records
                if (security_id := clean(first(record.get("SecId"), record.get("PID"))))
            ]
            static: dict[str, dict] = {}

            for start in range(0, len(ids), STATIC_BATCH):
                for row in await market_data.static_data(
                    ids[start : start + STATIC_BATCH]
                ):
                    static[str(row.get("secId"))] = row

        profiles = [
            drop_none(
                _profile(
                    record,
                    static.get(
                        str(clean(first(record.get("SecId"), record.get("PID")))), {}
                    ),
                )
            )
            for record in records
        ]
        profiles = [profile for profile in profiles if profile.get("symbol")]

        if not profiles:
            raise EmptyDataError(f"No security resolved for {query.symbol}.")

        return profiles

    @staticmethod
    def transform_data(
        query: FinraEquityInfoQueryParams, data: list[dict], **kwargs: Any
    ) -> list[FinraEquityInfoData]:
        """Transform the data to the model."""
        return [FinraEquityInfoData.model_validate(profile) for profile in data]
