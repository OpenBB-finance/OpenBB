"""YFinance Options Chains Model."""

# pylint: disable=unused-argument

from datetime import datetime
from typing import Any

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.annotated_result import AnnotatedResult
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.options_chains import (
    OptionsChainsData,
    OptionsChainsQueryParams,
)
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field


class YFinanceOptionsChainsQueryParams(OptionsChainsQueryParams):
    """YFinance Options Chains Query Parameters."""


class YFinanceOptionsChainsData(OptionsChainsData):
    """YFinance Options Chains Data."""

    __doc__ = OptionsChainsData.__doc__
    __alias_dict__ = {
        "contract_symbol": "contractSymbol",
        "last_trade_time": "lastTradeDate",
        "last_trade_price": "lastPrice",
        "change_percent": "percentChange",
        "open_interest": "openInterest",
        "implied_volatility": "impliedVolatility",
        "in_the_money": "inTheMoney",
    }

    in_the_money: list[bool | None] = Field(
        default_factory=list,
        description="Whether the option is in the money.",
    )
    currency: list[str | None] = Field(
        default_factory=list,
        description="Currency of the option.",
    )


class YFinanceOptionsChainsFetcher(
    Fetcher[YFinanceOptionsChainsQueryParams, YFinanceOptionsChainsData]
):
    """YFinance Options Chains Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> YFinanceOptionsChainsQueryParams:
        """Transform the query."""
        return YFinanceOptionsChainsQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: YFinanceOptionsChainsQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract the raw data from YFinance."""
        # pylint: disable=import-outside-toplevel
        import asyncio  # noqa
        from pandas import concat
        from yfinance import Ticker
        from pytz import timezone

        symbol = query.symbol.upper()
        symbol = "^" + symbol if symbol in ["VIX", "RUT", "SPX", "NDX"] else symbol

        def _get_all_data(symbol: str):
            """Get all options data in a single thread-safe operation."""
            t = Ticker(symbol)
            expirations = list(t.options)

            if not expirations or len(expirations) == 0:
                return None, None, []

            underlying = t.option_chain(expirations[0])[2]
            chains_output: list = []
            tz = timezone(underlying.get("exchangeTimezoneName", "UTC"))

            for expiration in expirations:
                exp = datetime.strptime(expiration, "%Y-%m-%d").date()
                now = datetime.now().date()
                dte = (exp - now).days
                chain_data = t.option_chain(expiration, tz=tz)
                calls = chain_data[0]
                calls["option_type"] = "call"
                calls["expiration"] = expiration
                puts = chain_data[1]
                puts["option_type"] = "put"
                puts["expiration"] = expiration
                chain = concat([calls, puts])
                chain = (
                    chain.set_index(["strike", "option_type", "contractSymbol"])
                    .sort_index()
                    .reset_index()
                )
                chain = chain.drop(columns=["contractSize"])
                chain["dte"] = dte
                underlying_price = underlying.get(
                    "postMarketPrice", underlying.get("regularMarketPrice")
                )
                if underlying_price is not None:
                    chain["underlying_price"] = underlying_price
                    chain["underlying_symbol"] = symbol
                chain["percentChange"] = chain["percentChange"] / 100

                if len(chain) > 0:
                    chains_output.extend(
                        chain.fillna("N/A").replace("N/A", None).to_dict("records")
                    )

            return underlying, chains_output, expirations

        underlying, chains_output, expirations = await asyncio.to_thread(
            _get_all_data, symbol
        )

        if not expirations or len(expirations) == 0:
            raise OpenBBError(f"No options found for {symbol}")

        if not chains_output:
            raise EmptyDataError(f"No data was returned for {symbol}")

        underlying_output: dict = {
            "symbol": symbol,
            "name": underlying.get("longName"),  # type: ignore
            "exchange": underlying.get("fullExchangeName"),  # type: ignore
            "exchange_tz": underlying.get("exchangeTimezoneName"),  # type: ignore
            "currency": underlying.get("currency"),  # type: ignore
            "bid": underlying.get("bid"),  # type: ignore
            "bid_size": underlying.get("bidSize"),  # type: ignore
            "ask": underlying.get("ask"),  # type: ignore
            "ask_size": underlying.get("askSize"),  # type: ignore
            "last_price": underlying.get(  # type: ignore
                "postMarketPrice", underlying.get("regularMarketPrice")  # type: ignore
            ),
            "open": underlying.get("regularMarketOpen"),  # type: ignore
            "high": underlying.get("regularMarketDayHigh"),  # type: ignore
            "low": underlying.get("regularMarketDayLow"),  # type: ignore
            "close": underlying.get("regularMarketPrice"),  # type: ignore
            "prev_close": underlying.get("regularMarketPreviousClose"),  # type: ignore
            "change": underlying.get("regularMarketChange"),  # type: ignore
            "change_percent": underlying.get("regularMarketChangePercent"),  # type: ignore
            "volume": underlying.get("regularMarketVolume"),  # type: ignore
            "dividend_yield": float(underlying.get("dividendYield", 0)) / 100,  # type: ignore
            "dividend_yield_ttm": underlying.get("trailingAnnualDividendYield"),  # type: ignore
            "year_high": underlying.get("fiftyTwoWeekHigh"),  # type: ignore
            "year_low": underlying.get("fiftyTwoWeekLow"),  # type: ignore
            "ma_50": underlying.get("fiftyDayAverage"),  # type: ignore
            "ma_200": underlying.get("twoHundredDayAverage"),  # type: ignore
            "volume_avg_10d": underlying.get("averageDailyVolume10Day"),  # type: ignore
            "volume_avg_3m": underlying.get("averageDailyVolume3Month"),  # type: ignore
            "market_cap": underlying.get("marketCap"),  # type: ignore
            "shares_outstanding": underlying.get("sharesOutstanding"),  # type: ignore
        }

        return {"underlying": underlying_output, "chains": chains_output}

    @staticmethod
    def transform_data(
        query: YFinanceOptionsChainsQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> AnnotatedResult[YFinanceOptionsChainsData]:
        """Transform the data."""
        # pylint: disable=import-outside-toplevel
        from numpy import nan
        from pandas import DataFrame

        if not data:
            raise EmptyDataError()
        metadata = data.get("underlying", {})
        records = data.get("chains", [])
        output = DataFrame(records)
        for col in ["volume", "openInterest"]:
            output[col] = output[col].infer_objects().replace({nan: 0}).astype("int64")

        output = output.replace({nan: None})

        return AnnotatedResult(
            result=YFinanceOptionsChainsData.model_validate(output.to_dict("list")),
            metadata=metadata,
        )
