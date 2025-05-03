"""YFinance Options Chains Model."""

# pylint: disable=unused-argument

from datetime import datetime
from typing import Any, Dict, List, Optional, Union

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

    in_the_money: List[Union[bool, None]] = Field(
        default_factory=list,
        description="Whether the option is in the money.",
    )
    currency: List[Union[str, None]] = Field(
        default_factory=list,
        description="Currency of the option.",
    )


class YFinanceOptionsChainsFetcher(
    Fetcher[YFinanceOptionsChainsQueryParams, YFinanceOptionsChainsData]
):
    """YFinance Options Chains Fetcher."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> YFinanceOptionsChainsQueryParams:
        """Transform the query."""
        return YFinanceOptionsChainsQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: YFinanceOptionsChainsQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> Dict:
        """Extract the raw data from YFinance."""
        # pylint: disable=import-outside-toplevel
        import asyncio  # noqa
        from curl_adapter import CurlCffiAdapter
        from openbb_core.provider.utils.helpers import get_requests_session
        from pandas import concat
        from yfinance import Ticker
        from pytz import timezone

        symbol = query.symbol.upper()
        symbol = "^" + symbol if symbol in ["VIX", "RUT", "SPX", "NDX"] else symbol
        session = get_requests_session()
        session.mount("https://", CurlCffiAdapter())
        session.mount("http://", CurlCffiAdapter())
        ticker = Ticker(
            symbol,
            session=session,
        )
        expirations = list(ticker.options)

        if not expirations or len(expirations) == 0:
            raise OpenBBError(f"No options found for {symbol}")

        chains_output: List = []
        underlying = ticker.option_chain(expirations[0])[2]
        underlying_output: Dict = {
            "symbol": symbol,
            "name": underlying.get("longName"),
            "exchange": underlying.get("fullExchangeName"),
            "exchange_tz": underlying.get("exchangeTimezoneName"),
            "currency": underlying.get("currency"),
            "bid": underlying.get("bid"),
            "bid_size": underlying.get("bidSize"),
            "ask": underlying.get("ask"),
            "ask_size": underlying.get("askSize"),
            "last_price": underlying.get(
                "postMarketPrice", underlying.get("regularMarketPrice")
            ),
            "open": underlying.get("regularMarketOpen"),
            "high": underlying.get("regularMarketDayHigh"),
            "low": underlying.get("regularMarketDayLow"),
            "close": underlying.get("regularMarketPrice"),
            "prev_close": underlying.get("regularMarketPreviousClose"),
            "change": underlying.get("regularMarketChange"),
            "change_percent": underlying.get("regularMarketChangePercent"),
            "volume": underlying.get("regularMarketVolume"),
            "dividend_yield": float(underlying.get("dividendYield", 0)) / 100,
            "dividend_yield_ttm": underlying.get("trailingAnnualDividendYield"),
            "year_high": underlying.get("fiftyTwoWeekHigh"),
            "year_low": underlying.get("fiftyTwoWeekLow"),
            "ma_50": underlying.get("fiftyDayAverage"),
            "ma_200": underlying.get("twoHundredDayAverage"),
            "volume_avg_10d": underlying.get("averageDailyVolume10Day"),
            "volume_avg_3m": underlying.get("averageDailyVolume3Month"),
            "market_cap": underlying.get("marketCap"),
            "shares_outstanding": underlying.get("sharesOutstanding"),
        }
        tz = timezone(underlying_output.get("exchange_tz", "UTC"))

        underlying_price = underlying_output.get("last_price")

        async def get_chain(ticker, expiration, tz, underlying_price):
            """Get the data for one expiration."""
            exp = datetime.strptime(expiration, "%Y-%m-%d").date()
            now = datetime.now().date()
            dte = (exp - now).days
            calls = ticker.option_chain(expiration, tz=tz)[0]
            calls["option_type"] = "call"
            calls["expiration"] = expiration
            puts = ticker.option_chain(expiration, tz=tz)[1]
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
            if underlying_price is not None:
                chain["underlying_price"] = underlying_price
                chain["underlying_symbol"] = symbol
            chain["percentChange"] = chain["percentChange"] / 100

            if len(chain) > 0:
                chains_output.extend(
                    chain.fillna("N/A").replace("N/A", None).to_dict("records")
                )

        await asyncio.gather(
            *[
                get_chain(ticker, expiration, tz, underlying_price)
                for expiration in expirations
            ]
        )

        if not chains_output:
            raise EmptyDataError(f"No data was returned for {symbol}")

        return {"underlying": underlying_output, "chains": chains_output}

    @staticmethod
    def transform_data(
        query: YFinanceOptionsChainsQueryParams,
        data: Dict,
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
            output[col] = (
                output[col].infer_objects(copy=False).replace({nan: 0}).astype("int64")
            )

        output = output.replace({nan: None})

        return AnnotatedResult(
            result=YFinanceOptionsChainsData.model_validate(output.to_dict("list")),
            metadata=metadata,
        )
