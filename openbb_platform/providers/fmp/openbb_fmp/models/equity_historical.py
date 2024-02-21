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
from pydantic import Field, NonNegativeInt, field_validator


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
        default=None,
        description="Change in price as a normalized percent.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    label: Optional[str] = Field(
        default=None, description="Human readable format of the date."
    )

    @field_validator("change_percent", mode="before", check_fields=False)
    @classmethod
    def normalize_percent(cls, v):  # pylint: disable=E0213
        """Return the percent value as a normalized value."""
        return float(v) / 100 if v else None


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
            """Callback function."""
            result = []
            data: Dict = await response.json()
            symbol = response.url.parts[-1]

            if isinstance(data, Dict):
                result = data.get("historical", [])

            if "," in query.symbol:
                for d in result:
                    d["symbol"] = symbol

            return result

        urls = [get_url_params(symbol) for symbol in query.symbol.split(",")]

        return await amake_requests(urls, callback, **kwargs)

    @staticmethod
    def transform_data(
        query: FMPEquityHistoricalQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[FMPEquityHistoricalData]:
        """Return the transformed data."""
        # remove a duplicated fields.
        results: List[FMPEquityHistoricalData] = []
        for d in sorted(data, key=lambda x: x["date"], reverse=False):
            _ = d.pop("changeOverTime")
            results.append(FMPEquityHistoricalData.model_validate(d))
        return results
