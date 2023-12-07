"""CBOE Equity Historical Price Model."""


from datetime import datetime, timedelta
from typing import Any, Dict, List, Literal, Optional

import pandas as pd
from openbb_cboe.utils.helpers import (
    TICKER_EXCEPTIONS,
    get_cboe_directory,
    get_cboe_index_directory,
    get_ticker_info,
)
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.equity_historical import (
    EquityHistoricalData,
    EquityHistoricalQueryParams,
)
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.helpers import make_request
from pydantic import Field


class CboeEquityHistoricalQueryParams(EquityHistoricalQueryParams):
    """CBOE Equity Historical Price Query.

    Source: https://www.cboe.com/
    """

    interval: Literal["1m", "1d"] = Field(
        default="1d", description=QUERY_DESCRIPTIONS.get("interval", "")
    )


class CboeEquityHistoricalData(EquityHistoricalData):
    """CBOE Equity Historical Price Data."""

    calls_volume: Optional[float] = Field(
        default=None,
        description="Number of calls traded during the most recent trading period. Only valid if interval is 1m.",
    )
    puts_volume: Optional[float] = Field(
        default=None,
        description="Number of puts traded during the most recent trading period. Only valid if interval is 1m.",
    )
    total_options_volume: Optional[float] = Field(
        default=None,
        description="Total number of options traded during the most recent trading period. Only valid if interval is 1m.",
    )


class CboeEquityHistoricalFetcher(
    Fetcher[
        CboeEquityHistoricalQueryParams,
        List[CboeEquityHistoricalData],
    ]
):
    """Transform the query, extract and transform the data from the CBOE endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> CboeEquityHistoricalQueryParams:
        """Transform the query. Setting the start and end dates for a 1 year period."""
        return CboeEquityHistoricalQueryParams(**params)

    @staticmethod
    def extract_data(
        query: CboeEquityHistoricalQueryParams,  # pylint: disable=unused-argument
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the CBOE endpoint."""
        # Symbol directories are cached for seven days and are used for error handling and URL generation.
        SYMBOLS = get_cboe_directory()
        INDEXES = get_cboe_index_directory().index.to_list()
        multi = pd.DataFrame()
        now = datetime.now()
        tickers = (
            query.symbol.split(",") if "," in query.symbol else [query.symbol.upper()]
        )
        if len(tickers) > 1:
            query.start_date = (
                query.start_date if query.start_date else now - timedelta(days=720)
            )
        if len(tickers) == 1:
            query.start_date = (
                query.start_date if query.start_date else now - timedelta(days=50000)
            )
        query.end_date = query.end_date if query.end_date else now

        def get_one(symbol, start_date, end_date, interval):
            symbol = symbol.upper()
            if "^" in symbol:
                symbol = symbol.replace("^", "")
            if len(tickers) == 1 and symbol == "NDX":
                raise RuntimeError("NDX is not supported by this function.")

            data = pd.DataFrame()

            if symbol not in SYMBOLS.index and symbol not in INDEXES:
                raise RuntimeError(
                    f"The symbol, {symbol}, was not found in the CBOE directory.  Use `search()`."
                )

            def __generate_historical_prices_url(
                symbol,
                data_type: Optional[Literal["intraday", "historical"]] = "historical",
            ) -> str:
                """Generate the final URL for historical prices data."""
                url: str = (
                    f"https://cdn.cboe.com/api/global/delayed_quotes/charts/{data_type}"
                )
                url = (
                    url + f"/_{symbol}.json"
                    if symbol in TICKER_EXCEPTIONS or symbol in INDEXES
                    else url + f"/{symbol}.json"
                )
                return url

            url = (
                __generate_historical_prices_url(symbol, "intraday")
                if interval == "1m"
                else __generate_historical_prices_url(symbol)
            )
            r = make_request(url)

            if r.status_code != 200:
                raise RuntimeError(r.status_code)

            if interval == "1d":
                data = (
                    pd.DataFrame(r.json()["data"])[
                        ["date", "open", "high", "low", "close", "volume"]
                    ]
                ).set_index("date")

                # Fill in missing data from current or most recent trading session.

                today = pd.to_datetime(datetime.now().date())
                if today.weekday() > 4:
                    day_minus = today.weekday() - 4
                    today = pd.to_datetime(today - timedelta(days=day_minus))
                if today != data.index[-1]:
                    _today = pd.Series(get_ticker_info(symbol))
                    today_df = pd.Series(dtype="object")
                    today_df["open"] = round(_today["open"], 2)
                    today_df["high"] = round(_today["high"], 2)
                    today_df["low"] = round(_today["low"], 2)
                    today_df["close"] = round(_today["close"], 2)
                    if symbol not in INDEXES and symbol not in TICKER_EXCEPTIONS:
                        data = data[data["volume"] > 0]
                        today_df["volume"] = _today["volume"]
                    today_df["date"] = today.date()
                    today_df = pd.DataFrame(today_df).transpose().set_index("date")

                    data = pd.concat([data, today_df], axis=0)

                # If ticker is an index there is no volume data and the types must be set.

                if symbol in INDEXES or symbol in TICKER_EXCEPTIONS:
                    data = data[["open", "high", "low", "close", "volume"]]
                    data["open"] = round(data.open.astype(float), 2)
                    data["high"] = round(data.high.astype(float), 2)
                    data["low"] = round(data.low.astype(float), 2)
                    data["close"] = round(data.close.astype(float), 2)
                    data["volume"] = 0

                data.index = pd.to_datetime(data.index)
                data = data[data["open"] > 0]
                data = data[
                    (data.index >= pd.to_datetime(start_date))
                    & (data.index <= pd.to_datetime(end_date))
                ]
            if query.interval == "1m":
                data_list = r.json()["data"]
                date: list[datetime] = []
                open_: list[float] = []
                high: list[float] = []
                low: list[float] = []
                close: list[float] = []
                volume: list[float] = []
                calls_volume: list[float] = []
                puts_volume: list[float] = []
                total_options_volume: list[float] = []

                for data in data_list:
                    date.append(data["datetime"])
                    open_.append(data["price"]["open"])
                    high.append(data["price"]["high"])
                    low.append(data["price"]["low"])
                    close.append(data["price"]["close"])
                    volume.append(data["volume"]["stock_volume"])
                    calls_volume.append(data["volume"]["calls_volume"])
                    puts_volume.append(data["volume"]["puts_volume"])
                    total_options_volume.append(data["volume"]["total_options_volume"])

                data = pd.DataFrame()
                date = [d.replace("T", " ") for d in date]
                date = [datetime.strptime(d, "%Y-%m-%d %H:%M:%S") for d in date]
                data["date"] = date
                data["open"] = open_
                data["high"] = high
                data["low"] = low
                data["close"] = close
                data["volume"] = volume
                data["calls_volume"] = calls_volume
                data["puts_volume"] = puts_volume
                data["total_options_volume"] = total_options_volume
                data = data.set_index("date").sort_index()
                data.index = data.index.strftime("%Y-%m-%d %H:%M:%S")
                data = data[data["open"] > 0]

            data["volume"] = round(data["volume"].astype("int64"))
            data["symbol"] = symbol
            return data.drop_duplicates().reset_index()

        for ticker in tickers:
            if ticker != "NDX":
                data = get_one(
                    ticker,
                    start_date=query.start_date,
                    end_date=query.end_date,
                    interval=query.interval,
                ).set_index(["date", "symbol"])
                multi = pd.concat([multi, data], axis=0)

        multi = multi.sort_index().reset_index()
        if len(tickers) == 1:
            multi = multi.drop(columns=["symbol"])

        return multi.to_dict("records")

    @staticmethod
    def transform_data(
        query: CboeEquityHistoricalQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[CboeEquityHistoricalData]:
        """Transform the data to the standard format."""
        return [CboeEquityHistoricalData.model_validate(d) for d in data]
