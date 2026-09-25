"""Nasdaq Equity Quote Model."""

from datetime import date as dateType
from typing import Any

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.equity_quote import (
    EquityQuoteData,
    EquityQuoteQueryParams,
)
from pydantic import Field

from openbb_nasdaq.utils.constants import SYMBOL_CHOICES_ENDPOINT


class NasdaqEquityQuoteQueryParams(EquityQuoteQueryParams):
    """Nasdaq Equity Quote Query.

    Source: https://www.nasdaq.com/market-activity/stocks
    """

    __json_schema_extra__ = {
        "symbol": {
            "multiple_items_allowed": True,
            "x-widget_config": {
                "type": "endpoint",
                "optionsEndpoint": SYMBOL_CHOICES_ENDPOINT,
                "style": {"popupWidth": 850},
            },
        },
    }


class NasdaqEquityQuoteData(EquityQuoteData):
    """Nasdaq Equity Quote Data."""

    name: str | None = Field(default=None, description="The name of the security.")
    exchange: str | None = Field(
        default=None, description="The exchange the security trades on."
    )
    sector: str | None = Field(default=None, description="The sector of the company.")
    industry: str | None = Field(
        default=None, description="The industry of the company."
    )
    market_cap: float | None = Field(
        default=None, description="The market capitalization of the company."
    )
    average_volume: float | None = Field(
        default=None, description="The average daily share volume."
    )
    price_target: float | None = Field(
        default=None, description="The one-year analyst price target."
    )
    annualized_dividend: float | None = Field(
        default=None, description="The annualized dividend amount."
    )
    dividend_yield: float | None = Field(
        default=None,
        description="The current dividend yield, as a normalized percentage.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    ex_dividend_date: dateType | None = Field(
        default=None, description="The most recent ex-dividend date."
    )
    dividend_payment_date: dateType | None = Field(
        default=None, description="The most recent dividend payment date."
    )
    is_nasdaq_100: bool | None = Field(
        default=None, description="Whether the security is a Nasdaq-100 constituent."
    )
    market_status: str | None = Field(
        default=None, description="The market session status at capture."
    )


class NasdaqEquityQuoteFetcher(
    Fetcher[
        NasdaqEquityQuoteQueryParams,
        list[NasdaqEquityQuoteData],
    ]
):
    """Transform the query, extract and transform the data from the Nasdaq endpoints."""

    require_credentials = False

    @staticmethod
    def transform_query(params: dict[str, Any]) -> NasdaqEquityQuoteQueryParams:
        """Transform the query."""
        return NasdaqEquityQuoteQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: NasdaqEquityQuoteQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Return the raw data from the Nasdaq endpoint."""
        import asyncio
        from warnings import warn

        from openbb_core.provider.utils.errors import EmptyDataError

        from openbb_nasdaq.utils.helpers import get_nasdaq_data

        symbols = [s.strip().upper() for s in query.symbol.split(",") if s.strip()]
        results: list[dict] = []

        async def get_one(symbol: str) -> None:
            """Collect the info and summary payloads for one symbol."""
            try:
                info, summary = await asyncio.gather(
                    get_nasdaq_data(f"quote/{symbol}/info?assetclass=stocks"),
                    get_nasdaq_data(f"quote/{symbol}/summary?assetclass=stocks"),
                )
            except Exception as exc:  # noqa: BLE001
                warn(f"No quote was returned for {symbol}. {exc}")
                return

            results.append({"symbol": symbol, "info": info, "summary": (summary or {})})

        await asyncio.gather(*[get_one(symbol) for symbol in symbols])

        if not results:
            raise EmptyDataError("No quotes were returned for any symbol.")

        return results

    @staticmethod
    def transform_data(
        query: NasdaqEquityQuoteQueryParams, data: list[dict], **kwargs: Any
    ) -> list[NasdaqEquityQuoteData]:
        """Transform the data to the standard format."""
        from openbb_nasdaq.utils.helpers import to_date, to_number, to_percent

        results: list[NasdaqEquityQuoteData] = []

        for item in data:
            info = item["info"] or {}
            primary = info.get("primaryData") or {}
            summary = (item["summary"] or {}).get("summaryData") or {}

            def value(key: str, block: dict = summary) -> Any:
                """Pull the display value out of a label/value block."""
                return (block.get(key) or {}).get("value")

            high, low = _split_range(value("FiftTwoWeekHighLow"))
            day_high, day_low = _split_range(value("TodayHighLow"))

            results.append(
                NasdaqEquityQuoteData.model_validate(
                    {
                        "symbol": item["symbol"],
                        "name": info.get("companyName"),
                        "exchange": info.get("exchange"),
                        "asset_type": info.get("stockType"),
                        "last_price": to_number(primary.get("lastSalePrice")),
                        "change": to_number(primary.get("netChange")),
                        "change_percent": to_percent(primary.get("percentageChange")),
                        "volume": to_number(primary.get("volume")),
                        "bid": to_number(primary.get("bidPrice")),
                        "ask": to_number(primary.get("askPrice")),
                        "bid_size": to_number(primary.get("bidSize")),
                        "ask_size": to_number(primary.get("askSize")),
                        "prev_close": to_number(value("PreviousClose")),
                        "year_high": high,
                        "year_low": low,
                        "high": day_high,
                        "low": day_low,
                        "sector": value("Sector"),
                        "industry": value("Industry"),
                        "market_cap": to_number(value("MarketCap")),
                        "average_volume": to_number(value("AverageVolume")),
                        "price_target": to_number(value("OneYrTarget")),
                        "annualized_dividend": to_number(value("AnnualizedDividend")),
                        "dividend_yield": to_percent(value("Yield")),
                        "ex_dividend_date": to_date(value("ExDividendDate")),
                        "dividend_payment_date": to_date(value("DividendPaymentDate")),
                        "is_nasdaq_100": info.get("isNasdaq100"),
                        "market_status": info.get("marketStatus"),
                        "last_timestamp": to_date(primary.get("lastTradeTimestamp")),
                    }
                )
            )

        return results


def _split_range(value: Any) -> tuple[float | None, float | None]:
    """Split a Nasdaq 'high/low' or 'low - high' display string into two numbers.

    Parameters
    ----------
    value : Any
        The raw range string.

    Returns
    -------
    tuple[float | None, float | None]
        The high and the low, in that order.
    """
    from openbb_nasdaq.utils.helpers import to_number

    if not isinstance(value, str):
        return None, None

    separator = "/" if "/" in value else ("-" if " - " in value else None)

    if separator is None:
        return None, None

    parts = [to_number(p) for p in value.split(separator, 1)]
    numbers = [p for p in parts if p is not None]

    if len(numbers) != 2:
        return None, None

    return max(numbers), min(numbers)
