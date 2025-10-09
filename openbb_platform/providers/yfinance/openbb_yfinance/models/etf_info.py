"""YFinance ETF Info Model."""

# pylint: disable=unused-argument

from typing import Any

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.etf_info import (
    EtfInfoData,
    EtfInfoQueryParams,
)
from pydantic import Field, field_validator


class YFinanceEtfInfoQueryParams(EtfInfoQueryParams):
    """YFinance ETF Info Query."""

    __json_schema_extra__ = {"symbol": {"multiple_items_allowed": True}}


class YFinanceEtfInfoData(EtfInfoData):
    """YFinance ETF Info Data."""

    __alias_dict__ = {
        "name": "longName",
        "inception_date": "fundInceptionDate",
        "description": "longBusinessSummary",
        "fund_type": "legalType",
        "fund_family": "fundFamily",
        "exchange_timezone": "timeZoneFullName",
        "nav_price": "navPrice",
        "total_assets": "totalAssets",
        "trailing_pe": "trailingPE",
        "dividend_yield": "yield",
        "dividend_rate_ttm": "trailingAnnualDividendRate",
        "dividend_yield_ttm": "trailingAnnualDividendYield",
        "year_high": "fiftyTwoWeekHigh",
        "year_low": "fiftyTwoWeekLow",
        "ma_50d": "fiftyDayAverage",
        "ma_200d": "twoHundredDayAverage",
        "return_ytd": "ytdReturn",
        "return_3y_avg": "threeYearAverageReturn",
        "return_5y_avg": "fiveYearAverageReturn",
        "beta_3y_avg": "beta3Year",
        "volume_avg": "averageVolume",
        "volume_avg_10d": "averageDailyVolume10Day",
        "bid_size": "bidSize",
        "ask_size": "askSize",
        "high": "dayHigh",
        "low": "dayLow",
        "prev_close": "previousClose",
    }

    fund_type: str | None = Field(
        default=None,
        description="The legal type of fund.",
    )
    fund_family: str | None = Field(
        default=None,
        description="The fund family.",
    )
    category: str | None = Field(
        default=None,
        description="The fund category.",
    )
    exchange: str | None = Field(
        default=None,
        description="The exchange the fund is listed on.",
    )
    exchange_timezone: str | None = Field(
        default=None,
        description="The timezone of the exchange.",
    )
    currency: str | None = Field(
        default=None,
        description="The currency in which the fund is listed.",
    )
    nav_price: float | None = Field(
        default=None,
        description="The net asset value per unit of the fund.",
    )
    total_assets: int | None = Field(
        default=None,
        description="The total value of assets held by the fund.",
    )
    trailing_pe: float | None = Field(
        default=None,
        description="The trailing twelve month P/E ratio of the fund's assets.",
    )
    dividend_yield: float | None = Field(
        default=None,
        description="The dividend yield of the fund, as a normalized percent.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    dividend_rate_ttm: float | None = Field(
        default=None,
        description="The trailing twelve month annual dividend rate of the fund, in currency units.",
    )
    dividend_yield_ttm: float | None = Field(
        default=None,
        description="The trailing twelve month annual dividend yield of the fund, as a normalized percent.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    year_high: float | None = Field(
        default=None,
        description="The fifty-two week high price.",
    )
    year_low: float | None = Field(
        default=None,
        description="The fifty-two week low price.",
    )
    ma_50d: float | None = Field(
        default=None,
        description="50-day moving average price.",
    )
    ma_200d: float | None = Field(
        default=None,
        description="200-day moving average price.",
    )
    return_ytd: float | None = Field(
        default=None,
        description="The year-to-date return of the fund, as a normalized percent.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    return_3y_avg: float | None = Field(
        default=None,
        description="The three year average return of the fund, as a normalized percent.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    return_5y_avg: float | None = Field(
        default=None,
        description="The five year average return of the fund, as a normalized percent.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    beta_3y_avg: float | None = Field(
        default=None,
        description="The three year average beta of the fund.",
    )
    volume_avg: float | None = Field(
        default=None,
        description="The average daily trading volume of the fund.",
    )
    volume_avg_10d: float | None = Field(
        default=None,
        description="The average daily trading volume of the fund over the past ten days.",
    )
    bid: float | None = Field(
        default=None,
        description="The current bid price.",
    )
    bid_size: float | None = Field(
        default=None,
        description="The current bid size.",
    )
    ask: float | None = Field(
        default=None,
        description="The current ask price.",
    )
    ask_size: float | None = Field(
        default=None,
        description="The current ask size.",
    )
    open: float | None = Field(
        default=None,
        description="The open price of the most recent trading session.",
    )
    high: float | None = Field(
        default=None,
        description="The highest price of the most recent trading session.",
    )
    low: float | None = Field(
        default=None,
        description="The lowest price of the most recent trading session.",
    )
    volume: int | None = Field(
        default=None,
        description="The trading volume of the most recent trading session.",
    )
    prev_close: float | None = Field(
        default=None,
        description="The previous closing price.",
    )

    @field_validator("inception_date", mode="before", check_fields=False)
    @classmethod
    def validate_date(cls, v):
        """Validate first stock price date."""
        from datetime import datetime  # pylint: disable=import-outside-toplevel

        if isinstance(v, datetime):
            return v.date().strftime("%Y-%m-%d")
        return datetime.fromtimestamp(v).date().strftime("%Y-%m-%d") if v else None


class YFinanceEtfInfoFetcher(
    Fetcher[YFinanceEtfInfoQueryParams, list[YFinanceEtfInfoData]]
):
    """YFinance ETF Info fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> YFinanceEtfInfoQueryParams:
        """Transform the query."""
        return YFinanceEtfInfoQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: YFinanceEtfInfoQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Extract the raw data from YFinance."""
        # pylint: disable=import-outside-toplevel
        import asyncio  # noqa
        from curl_adapter import CurlCffiAdapter
        from openbb_core.app.model.abstract.error import OpenBBError
        from openbb_core.provider.utils.errors import EmptyDataError
        from openbb_core.provider.utils.helpers import (
            get_requests_session,
            safe_fromtimestamp,
        )
        from warnings import warn
        from yfinance import Ticker

        symbols = query.symbol.split(",")
        results: list = []
        fields = [
            "symbol",
            "quoteType",
            "legalType",
            "longName",
            "fundFamily",
            "category",
            "exchange",
            "timeZoneFullName",
            "fundInceptionDate",
            "currency",
            "navPrice",
            "totalAssets",
            "trailingPE",
            "yield",
            "trailingAnnualDividendRate",
            "trailingAnnualDividendYield",
            "bid",
            "bidSize",
            "ask",
            "askSize",
            "open",
            "dayHigh",
            "dayLow",
            "previousClose",
            "volume",
            "averageVolume",
            "averageDailyVolume10Day",
            "fiftyTwoWeekHigh",
            "fiftyTwoWeekLow",
            "fiftyDayAverage",
            "twoHundredDayAverage",
            "ytdReturn",
            "threeYearAverageReturn",
            "fiveYearAverageReturn",
            "beta3Year",
            "longBusinessSummary",
            "firstTradeDateEpochUtc",
        ]
        messages: list = []
        session = get_requests_session()
        session.mount("https://", CurlCffiAdapter())
        session.mount("http://", CurlCffiAdapter())

        async def get_one(symbol):
            """Get the data for one ticker symbol."""
            result: dict = {}
            ticker: dict = {}
            try:
                ticker = Ticker(
                    symbol,
                    session=session,
                ).get_info()
            except Exception as e:
                messages.append(
                    f"Error getting data for {symbol} -> {e.__class__.__name__}: {e}"
                )
            if ticker:
                quote_type = ticker.pop("quoteType", "")
                if quote_type == "ETF":
                    try:
                        for field in fields:
                            if field in ticker and ticker.get(field) is not None:
                                result[field] = ticker.get(field, None)
                        if "firstTradeDateEpochUtc" in result:
                            _first_trade = result.pop("firstTradeDateEpochUtc")
                            if (
                                "fundInceptionDate" not in result
                                and _first_trade is not None
                            ):
                                result["fundInceptionDate"] = safe_fromtimestamp(
                                    _first_trade
                                )
                    except Exception as e:
                        messages.append(
                            f"Error processing data for {symbol} -> {e.__class__.__name__}: {e}"
                        )
                        result = {}
                if quote_type != "ETF":
                    messages.append(f"{symbol} is not an ETF.")
                if result:
                    results.append(result)

        tasks = [get_one(symbol) for symbol in symbols]

        await asyncio.gather(*tasks)

        if not results and not messages:
            raise EmptyDataError("No data was returned for the given symbol(s).")

        if not results and messages:
            raise OpenBBError("\n".join(messages))

        if results and messages:
            for message in messages:
                warn(message)

        return results

    @staticmethod
    def transform_data(
        query: YFinanceEtfInfoQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[YFinanceEtfInfoData]:
        """Transform the data."""
        return [YFinanceEtfInfoData.model_validate(d) for d in data]
