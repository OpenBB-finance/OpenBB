"""Alpha Vantage Equity Historical Price Model."""

# pylint: disable=unused-argument

import asyncio
from datetime import datetime
from io import BytesIO
from typing import Any, Dict, List, Literal, Optional
from warnings import warn

from dateutil.relativedelta import relativedelta
from openbb_alpha_vantage.utils.helpers import (
    INTERVALS_DICT,
    calculate_adjusted_prices,
    get_interval,
)
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.equity_historical import (
    EquityHistoricalData,
    EquityHistoricalQueryParams,
)
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from openbb_core.provider.utils.helpers import (
    amake_request,
    amake_requests,
    get_querystring,
)
from pandas import date_range, read_csv, to_datetime
from pydantic import (
    Field,
    NonNegativeFloat,
    PositiveFloat,
    model_validator,
)


class AVEquityHistoricalQueryParams(EquityHistoricalQueryParams):
    """Alpha Vantage Equity Historical Price Query.

    Source: https://www.alphavantage.co/documentation/#time-series-data
    """

    __json_schema_extra__ = {"symbol": ["multiple_items_allowed"]}

    interval: Literal["1m", "5m", "15m", "30m", "60m", "1d", "1W", "1M"] = Field(
        default="1d",
        description=QUERY_DESCRIPTIONS.get("interval", ""),
    )
    adjustment: Literal["splits_only", "splits_and_dividends", "unadjusted"] = Field(
        description="The adjustment factor to apply. 'splits_only' is not supported for intraday data.",
        default="splits_only",
    )
    extended_hours: Optional[bool] = Field(
        description="Include Pre and Post market data.",
        default=False,
    )
    adjusted: bool = Field(
        default=False,
        exclude=True,
        description="This field is deprecated (4.1.5) and will be removed in a future version."
        + " Use 'adjustment' set as 'splits_and_dividends' instead.",
        json_schema_extra={"deprecated": True},
    )

    @model_validator(mode="before")
    @classmethod
    def validate_deprecated_params(cls, values):
        """Validate the deprecated parameters."""
        for k, v in values.copy().items():
            if k in ["adjusted"] and v is True:
                warn(
                    f"The '{k}' parameter is deprecated and will be removed in a future version."
                )
                values["adjustment"] = "splits_and_dividends"
        return values


class AVEquityHistoricalData(EquityHistoricalData):
    """Alpha Vantage Equity Historical Price Data."""

    __alias_dict__ = {
        "adj_close": "adjusted_close",
        "dividend": "dividend_amount",
        "split_ratio": "split_factor",
    }

    adj_close: Optional[PositiveFloat] = Field(
        default=None, description=DATA_DESCRIPTIONS.get("adj_close", "")
    )
    dividend: Optional[NonNegativeFloat] = Field(
        default=None,
        description="Dividend amount, if a dividend was paid.",
    )
    split_ratio: Optional[NonNegativeFloat] = Field(
        default=None,
        description="Split coefficient, if a split occurred.",
    )


class AVEquityHistoricalFetcher(
    Fetcher[
        AVEquityHistoricalQueryParams,
        List[AVEquityHistoricalData],
    ]
):
    """Transform the query, extract and transform the data from the AlphaVantage endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> AVEquityHistoricalQueryParams:
        """Transform the query."""
        transformed_params = params

        now = datetime.now().date()
        if params.get("start_date") is None:
            transformed_params["start_date"] = now - relativedelta(years=1)

        if params.get("end_date") is None:
            transformed_params["end_date"] = now

        return AVEquityHistoricalQueryParams(**transformed_params)

    @staticmethod
    async def aextract_data(
        query: AVEquityHistoricalQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the Alpha Vantage endpoint."""
        api_key = credentials.get("alpha_vantage_api_key") if credentials else ""
        intraday = False
        interval = get_interval(query.interval)
        query_str = get_querystring(
            query.model_dump(by_alias=True),
            [
                "start_date",
                "end_date",
                "interval",
                "symbol",
                "adjustment",
                "extended_hours",
            ],
        )

        function = INTERVALS_DICT[query.interval[-1]]

        if query.adjustment != "unadjusted":
            function += "_ADJUSTED"
        query_str += f"&function={function}&outputsize=full&datatype=csv"

        if "INTRADAY" in function:
            query_str += f"&interval={interval}&extended_hours={str(query.extended_hours).lower()}"
            intraday = True

        results = []

        async def callback(response, _):
            """Use callback function to process the response."""
            try:
                result = await response.json()
                if "Information" in result:
                    warn(str(result.get("Information")))
            except Exception as _:
                # TODO: This is hacky, find a better solution.
                return await response.read()
            return await response.read()

        async def intraday_callback(response, _):
            """Use callback function to process the intraday response."""
            symbol = response.url.query.get("symbol", None)
            data = await response.read()
            if data:
                df = read_csv(BytesIO(data))
                if len(df) > 0:
                    df.rename(
                        columns={
                            "timestamp": "date",
                        },
                        inplace=True,
                    )
                if len(query.symbol.split(",")) > 1:
                    df.loc[:, "symbol"] = symbol
                results.extend(df.to_dict("records"))
            if not data:
                warn(f"Symbol Error: No data found for {symbol}")
            return results

        async def get_one(symbol, intraday: bool = False):
            """Get data for one symbol."""
            if intraday is True:
                adjusted = query.adjustment != "unadjusted"
                if query.adjustment == "splits_only":
                    warn(
                        "Intraday does not support 'splits_only'. Using 'splits_and_dividends' instead."
                    )
                url = (
                    f"https://www.alphavantage.co/query?{query_str.replace('_ADJUSTED', '')}"
                    f"&symbol={symbol}&adjusted={str(adjusted).lower()}"
                )
                dates = (
                    date_range(start=query.start_date, end=query.end_date)
                    .strftime("%Y-%m")
                    .unique()
                    .tolist()
                )
                urls = [f"{url}&month={date}&apikey={api_key}" for date in dates]
                return await amake_requests(urls, response_callback=intraday_callback)

            # We will resample the intervals ourselves to get the correct data.
            url = (
                f"https://www.alphavantage.co/query?{query_str.replace('MONTHLY', 'DAILY').replace('WEEKLY', 'DAILY')}"
                f"&symbol={symbol}&apikey={api_key}"
            )
            result = await amake_request(url, response_callback=callback)
            if not result:
                warn(f"Symbol Error: No data found for {symbol}")
            if result:
                data = read_csv(BytesIO(result))  # type: ignore
                if len(data) > 0:
                    data.rename(
                        columns={
                            "timestamp": "date",
                            "dividend_amount": "dividend",
                            "adjusted close": "adj_close",
                            "dividend amount": "dividend",
                            "adjusted_close": "adj_close",
                            "split_coefficient": "split_factor",
                        },
                        inplace=True,
                    )
                    if "date" in data.columns:
                        data["date"] = data["date"].apply(to_datetime)
                        data.set_index("date", inplace=True)
                        # The returned data when 'adjusted=true' from the API does not return a usable OHLCV data set.
                        # We need to calculate the adjusted prices manually.
                        if query.adjustment != "unadjusted":
                            temp = data.copy()
                            temp["dividend_factor"] = (
                                temp["close"] - temp["dividend"]
                            ) / temp["close"]
                            temp["volume_factor"] = temp["split_factor"]
                            temp["split_factor"] = 1 / temp["split_factor"]
                            adj_cols = ["open", "high", "low", "close", "volume"]
                            divs = query.adjustment == "splits_and_dividends"
                            for col in adj_cols:
                                divs = False if col == "volume" else divs
                                if col in temp.columns:
                                    temp = calculate_adjusted_prices(temp, col, divs)
                            temp["adj_dividend"] = (
                                temp["adj_close"] * (1 - temp["dividend_factor"])
                                if query.adjustment == "splits_only"
                                else temp["close"] * (1 - temp["dividend_factor"])
                            )
                            data["open"] = round(temp["adj_open"], 4)
                            data["high"] = round(temp["adj_high"], 4)
                            data["low"] = round(temp["adj_low"], 4)
                            data["close"] = round(temp["adj_close"], 4)
                            data["volume"] = round(temp["adj_volume"]).astype(int)
                            data["dividend"] = round(temp["adj_dividend"], 4)
                            data.drop(columns=["adj_close"], inplace=True)
                        # Resample the daily data for the interval requested.
                        freq = ""
                        agg_dict = {
                            "open": "first",
                            "high": "max",
                            "low": "min",
                            "close": "last",
                            "volume": "sum",
                            "dividend": "sum",
                            "split_factor": "prod",
                        }
                        if query.adjustment == "unadjusted":
                            agg_dict.pop("dividend")
                            agg_dict.pop("split_factor")
                        if query.interval == "1M":
                            freq = "M"
                        if query.interval == "1W":
                            freq = "W-FRI"
                        if freq in ["M", "W-FRI"]:
                            data = data.resample(freq).agg({**agg_dict})
                        if len(query.symbol.split(",")) > 1:
                            data.loc[:, "symbol"] = symbol

                        results.extend(data.reset_index().to_dict("records"))

            return results

        tasks = [get_one(symbol, intraday) for symbol in query.symbol.split(",")]
        await asyncio.gather(*tasks)

        return results

    @staticmethod
    def transform_data(
        query: AVEquityHistoricalQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[AVEquityHistoricalData]:
        """Transform the data to the standard format."""
        if data == []:
            return []
        if "{" in data[0]:
            warn(str(data[0]["{"].strip()))
            return []
        return [
            AVEquityHistoricalData.model_validate(d)
            for d in sorted(
                data,
                key=(
                    lambda x: (x["date"], x["symbol"]) if "symbol" in x else x["date"]
                ),
            )
            if query.start_date <= to_datetime(d["date"]).date() <= query.end_date
        ]
