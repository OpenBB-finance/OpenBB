"""CBOE Market Indices Model."""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Literal, Optional

import pandas as pd
from openbb_cboe.utils.helpers import (
    TICKER_EXCEPTIONS,
    get_cboe_index_directory,
    get_ticker_info,
)
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.market_indices import (
    MarketIndicesData,
    MarketIndicesQueryParams,
)
from openbb_core.provider.utils.helpers import make_request
from pydantic import Field


class CboeMarketIndicesQueryParams(MarketIndicesQueryParams):
    """CBOE Market Indices Query.

    Source: https://www.cboe.com/
    """

    interval: Literal["1d", "1m"] = Field(
        description="Use interval, 1m, for intraday prices during the most recent trading period.",
        default="1d",
    )


class CboeMarketIndicesData(MarketIndicesData):
    """CBOE Market Indices Data."""

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


class CboeMarketIndicesFetcher(
    Fetcher[
        CboeMarketIndicesQueryParams,
        List[CboeMarketIndicesData],
    ]
):
    """Transform the query, extract and transform the data from the CBOE endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> CboeMarketIndicesQueryParams:
        """Transform the query. Setting the start and end dates for a 1 year period."""
        return CboeMarketIndicesQueryParams(**params)

    @staticmethod
    def extract_data(
        query: CboeMarketIndicesQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the CBOE endpoint."""
        # Synbol directories are cached for seven days and are used for error handling and URL generation.
        INDEXES = get_cboe_index_directory().index.to_list()
        query.symbol = query.symbol.upper()
        data = pd.DataFrame()
        if "^" in query.symbol:
            query.symbol = query.symbol.replace("^", "")
        query.interval = (
            "1m" if query.symbol == "NDX" and query.interval == "1d" else query.interval
        )

        now = datetime.now()
        query.start_date = (
            query.start_date if query.start_date else now - timedelta(days=50000)
        )
        query.end_date = query.end_date if query.end_date else now

        if query.symbol not in INDEXES and query.symbol not in TICKER_EXCEPTIONS:
            raise RuntimeError(
                f"The symbol, {query.symbol}, was not found in the CBOE index directory. "
                "Use `index_search()` to find supported indices. If the index is European, try `european_index()`."
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
            __generate_historical_prices_url(query.symbol, "intraday")
            if query.interval == "1m"
            else __generate_historical_prices_url(query.symbol)
        )
        r = make_request(url)

        if r.status_code != 200:
            raise RuntimeError(r.status_code)

        if query.interval == "1d":
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
                _today = pd.Series(get_ticker_info(query.symbol))
                today_df = pd.Series(dtype="object")
                today_df["open"] = round(_today["open"], 2)
                today_df["high"] = round(_today["high"], 2)
                today_df["low"] = round(_today["low"], 2)
                today_df["close"] = round(_today["close"], 2)
                if (
                    query.symbol not in INDEXES
                    and query.symbol not in TICKER_EXCEPTIONS
                ):
                    data = data[data["volume"] > 0]
                    today_df["volume"] = _today["volume"]
                today_df["date"] = today.date()
                today_df = pd.DataFrame(today_df).transpose().set_index("date")

                data = pd.concat([data, today_df], axis=0)

            # If ticker is an index there is no volume data and the types must be set.

            if query.symbol in INDEXES or query.symbol in TICKER_EXCEPTIONS:
                data = data[["open", "high", "low", "close", "volume"]]
                data["open"] = round(data.open.astype(float), 2)
                data["high"] = round(data.high.astype(float), 2)
                data["low"] = round(data.low.astype(float), 2)
                data["close"] = round(data.close.astype(float), 2)
                data["volume"] = 0

            data.index = pd.to_datetime(data.index)
            data = data[data["open"] > 0]

            data = data[
                (data.index >= pd.to_datetime(query.start_date))
                & (data.index <= pd.to_datetime(query.end_date))
            ]

        if query.interval == "1m":
            data_list = r.json()["data"]
            date: List[datetime] = []
            open_: List[float] = []
            high: List[float] = []
            low: List[float] = []
            close: List[float] = []
            volume: List[float] = []
            calls_volume: List[float] = []
            puts_volume: List[float] = []
            total_options_volume: List[float] = []

            for i in range(0, len(data_list)):
                date.append(data_list[i]["datetime"])
                open_.append(data_list[i]["price"]["open"])
                high.append(data_list[i]["price"]["high"])
                low.append(data_list[i]["price"]["low"])
                close.append(data_list[i]["price"]["close"])
                volume.append(data_list[i]["volume"]["stock_volume"])
                calls_volume.append(data_list[i]["volume"]["calls_volume"])
                puts_volume.append(data_list[i]["volume"]["puts_volume"])
                total_options_volume.append(
                    data_list[i]["volume"]["total_options_volume"]
                )
            data = pd.DataFrame()
            data["date"] = pd.to_datetime(date)
            data["open"] = open_
            data["high"] = high
            data["low"] = low
            data["close"] = close
            data["volume"] = volume
            data["calls_volume"] = calls_volume
            data["puts_volume"] = puts_volume
            data["total_options_volume"] = total_options_volume
            data = data.set_index("date").sort_index()
            data.index = data.index.astype(str)
            data = data[data["open"] > 0]

        return data.reset_index().to_dict("records")

    @staticmethod
    def transform_data(
        query: CboeMarketIndicesQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[CboeMarketIndicesData]:
        """Transform the data to the standard format."""
        return [CboeMarketIndicesData.model_validate(d) for d in data]
