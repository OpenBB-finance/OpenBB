"""Tiingo Equity Historical Price Model."""

# pylint: disable=unused-argument

import warnings
from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

from dateutil.relativedelta import relativedelta
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
    ClientResponse,
    amake_requests,
    get_querystring,
)
from pydantic import Field, PrivateAttr, model_validator

_warn = warnings.warn


class TiingoEquityHistoricalQueryParams(EquityHistoricalQueryParams):
    """Tiingo Equity Historical Price Query.

    Source: https://www.tiingo.com/documentation/end-of-day
    """

    __alias_dict__ = {
        "start_date": "startDate",
        "end_date": "endDate",
    }
    __json_schema_extra__ = {"symbol": ["multiple_items_allowed"]}

    interval: Literal["1d", "1W", "1M", "1Y"] = Field(
        default="1d", description=QUERY_DESCRIPTIONS.get("interval", "")
    )
    _frequency: Literal["daily", "weekly", "monthly", "annually"] = PrivateAttr(
        default=None
    )

    # pylint: disable=protected-access
    @model_validator(mode="after")  # type: ignore[arg-type]
    @classmethod
    def set_time_params(cls, values: "TiingoEquityHistoricalQueryParams"):
        """Set the default start & end date and time params for Tiingo API."""
        frequency_dict = {
            "1d": "daily",
            "1W": "weekly",
            "1M": "monthly",
            "1Y": "annually",
        }

        values._frequency = frequency_dict[values.interval]  # type: ignore[assignment]

        return values


class TiingoEquityHistoricalData(EquityHistoricalData):
    """Tiingo Equity Historical Price Data."""

    adj_open: Optional[float] = Field(
        default=None,
        description="The adjusted open price.",
        alias="adjOpen",
    )
    adj_high: Optional[float] = Field(
        default=None,
        description="The adjusted high price.",
        alias="adjHigh",
    )
    adj_low: Optional[float] = Field(
        default=None,
        description="The adjusted low price.",
        alias="adjLow",
    )
    adj_close: Optional[float] = Field(
        default=None,
        description=DATA_DESCRIPTIONS.get("adj_close", ""),
        alias="adjClose",
    )
    adj_volume: Optional[float] = Field(
        default=None,
        description="The adjusted volume.",
        alias="adjVolume",
    )
    split_ratio: Optional[float] = Field(
        default=None,
        description="Ratio of the equity split, if a split occurred.",
        alias="splitFactor",
    )
    dividend: Optional[float] = Field(
        default=None,
        description="Dividend amount, if a dividend was paid.",
        alias="divCash",
    )


class TiingoEquityHistoricalFetcher(
    Fetcher[
        TiingoEquityHistoricalQueryParams,
        List[TiingoEquityHistoricalData],
    ]
):
    """Transform the query, extract and transform the data from the Tiingo endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> TiingoEquityHistoricalQueryParams:
        """Transform the query params."""
        transformed_params = params

        now = datetime.now().date()
        if params.get("start_date") is None:
            transformed_params["start_date"] = now - relativedelta(years=1)

        if params.get("end_date") is None:
            transformed_params["end_date"] = now

        return TiingoEquityHistoricalQueryParams(**transformed_params)

    # pylint: disable=protected-access
    @staticmethod
    async def aextract_data(
        query: TiingoEquityHistoricalQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the Tiingo endpoint."""
        api_key = credentials.get("tiingo_token") if credentials else ""

        base_url = "https://api.tiingo.com/tiingo/daily"
        query_str = get_querystring(
            query.model_dump(by_alias=True), ["symbol", "interval"]
        )

        async def callback(response: ClientResponse, _: Any) -> List[Dict]:
            data = await response.json()
            symbol = response.url.parts[-2]
            results = []
            if not data:
                _warn(f"No data found the the symbol: {symbol}")
                return results

            if isinstance(data, List):
                results = data

            if "," in query.symbol:
                for d in results:
                    d["symbol"] = symbol
            return results

        urls = [
            f"{base_url}/{symbol}/prices?{query_str}&resampleFreq={query._frequency}&token={api_key}"
            for symbol in query.symbol.split(",")
        ]

        return await amake_requests(urls, callback, **kwargs)

    @staticmethod
    def transform_data(
        query: TiingoEquityHistoricalQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> List[TiingoEquityHistoricalData]:
        """Return the transformed data."""
        return [TiingoEquityHistoricalData.model_validate(d) for d in data]
