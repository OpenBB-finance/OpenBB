"""FMP Equity Historical Price Model."""

from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

from dateutil.relativedelta import relativedelta
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.equity_historical import (
    EquityHistoricalData,
    EquityHistoricalQueryParams,
)
from openbb_core.provider.utils.descriptions import DATA_DESCRIPTIONS
from openbb_core.provider.utils.helpers import (
    ClientResponse,
    amake_requests,
    get_querystring,
)
from openbb_fmp.utils.helpers import get_interval
from pydantic import Field, NonNegativeInt


class FMPEquityHistoricalQueryParams(EquityHistoricalQueryParams):
    """FMP Equity Historical Price Query.

    Source: https://financialmodelingprep.com/developer/docs/#Stock-Historical-Price
    """

    __alias_dict__ = {"start_date": "from", "end_date": "to"}
    __json_schema_extra__ = {"symbol": ["multiple_items_allowed"]}

    limit: Optional[NonNegativeInt] = Field(
        default=None,
        description="Number of days to look back (Only for interval 1d).",
        alias="timeseries",
    )
    interval: Literal["1m", "5m", "15m", "30m", "1h", "4h", "1d"] = Field(
        default="1d", description="Time granularity to fetch data for."
    )


class FMPEquityHistoricalData(EquityHistoricalData):
    """FMP Equity Historical Price Data."""

    label: Optional[str] = Field(
        default=None, description="Human readable format of the date."
    )
    adj_close: Optional[float] = Field(
        default=None, description=DATA_DESCRIPTIONS.get("adj_close", "")
    )
    unadjusted_volume: Optional[float] = Field(
        default=None, description="Unadjusted volume of the symbol."
    )
    change: Optional[float] = Field(
        default=None,
        description="Change in the price of the symbol from the previous day.",
    )
    change_percent: Optional[float] = Field(
        default=None, description="Change % in the price of the symbol."
    )
    change_over_time: Optional[float] = Field(
        default=None,
        description="Change % in the price of the symbol over a period of time.",
    )


class FMPEquityHistoricalFetcher(
    Fetcher[
        FMPEquityHistoricalQueryParams,
        List[FMPEquityHistoricalData],
    ]
):
    """Transform the query, extract and transform the data from the FMP endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FMPEquityHistoricalQueryParams:
        """Transform the query params."""
        transformed_params = params

        now = datetime.now().date()
        if params.get("start_date") is None:
            transformed_params["start_date"] = now - relativedelta(years=1)

        if params.get("end_date") is None:
            transformed_params["end_date"] = now

        return FMPEquityHistoricalQueryParams(**transformed_params)

    @staticmethod
    async def aextract_data(
        query: FMPEquityHistoricalQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the FMP endpoint."""
        api_key = credentials.get("fmp_api_key") if credentials else ""

        interval = get_interval(query.interval)

        base_url = "https://financialmodelingprep.com/api/v3"
        query_str = get_querystring(query.model_dump(), ["symbol", "interval"])

        def get_url_params(symbol: str) -> str:
            url_params = f"{symbol}?{query_str}&apikey={api_key}"
            url = f"{base_url}/historical-chart/{interval}/{url_params}"
            if interval == "1day":
                url = f"{base_url}/historical-price-full/{url_params}"
            return url

        # if there are more than 20 symbols, we need to increase the timeout
        if len(query.symbol.split(",")) > 20:
            kwargs.update({"preferences": {"request_timeout": 30}})

        async def callback(response: ClientResponse, _: Any) -> List[Dict]:
            data: dict = await response.json()
            symbol = response.url.parts[-1]

            if isinstance(data, dict):
                data = data.get("historical", [])

            if "," in query.symbol:
                for d in data:
                    d["symbol"] = symbol

            return data

        urls = [get_url_params(symbol) for symbol in query.symbol.split(",")]

        return await amake_requests(urls, callback, **kwargs)

    @staticmethod
    def transform_data(
        query: FMPEquityHistoricalQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[FMPEquityHistoricalData]:
        """Return the transformed data."""
        return [FMPEquityHistoricalData.model_validate(d) for d in data]
