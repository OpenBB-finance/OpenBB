"""FMP Index Historical Model."""

from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

from dateutil.relativedelta import relativedelta
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.index_historical import (
    IndexHistoricalData,
    IndexHistoricalQueryParams,
)
from openbb_core.provider.utils.descriptions import DATA_DESCRIPTIONS
from openbb_core.provider.utils.helpers import get_querystring
from openbb_fmp.utils.helpers import get_data_many
from pydantic import Field, NonNegativeInt, field_validator


class FMPIndexHistoricalQueryParams(IndexHistoricalQueryParams):
    """FMP Index Historical Query.

    Source: https://site.financialmodelingprep.com/developer/docs/historical-index-price-api/
    """

    __alias_dict__ = {"start_date": "from", "end_date": "to"}

    timeseries: Optional[NonNegativeInt] = Field(
        default=None, description="Number of days to look back."
    )
    interval: Literal["1min", "5min", "15min", "30min", "1hour", "4hour", "1day"] = (
        Field(default="1day", description="Data granularity.")
    )

    @field_validator("interval")
    @classmethod
    def map_interval(cls, v):
        """Map the interval from standard to the FMP format."""
        return "1day" if v == "1d" else v


class FMPIndexHistoricalData(IndexHistoricalData):
    """FMP Index Historical Data."""

    adj_close: Optional[float] = Field(
        description=DATA_DESCRIPTIONS.get("adj_close", ""),
        default=None,
    )
    unadjusted_volume: Optional[float] = Field(
        description="Unadjusted volume of the symbol.",
        default=None,
    )
    change: Optional[float] = Field(
        description="Change in the price of the symbol from the previous day.",
        default=None,
    )
    change_percent: Optional[float] = Field(
        description="Change % in the price of the symbol.",
        default=None,
    )
    label: Optional[str] = Field(
        description="Human readable format of the date.", default=None
    )
    change_over_time: Optional[float] = Field(
        description="Change % in the price of the symbol over a period of time.",
        default=None,
    )


class FMPIndexHistoricalFetcher(
    Fetcher[
        FMPIndexHistoricalQueryParams,
        List[FMPIndexHistoricalData],
    ]
):
    """Transform the query, extract and transform the data from the FMP endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FMPIndexHistoricalQueryParams:
        """Transform the query params."""
        transformed_params = params

        now = datetime.now().date()
        if params.get("start_date") is None:
            transformed_params["start_date"] = now - relativedelta(years=1)

        if params.get("end_date") is None:
            transformed_params["end_date"] = now

        return FMPIndexHistoricalQueryParams.model_validate(transformed_params)

    @staticmethod
    async def aextract_data(
        query: FMPIndexHistoricalQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the FMP endpoint."""
        api_key = credentials.get("fmp_api_key") if credentials else ""

        base_url = "https://financialmodelingprep.com/api/v3"
        query_str = get_querystring(query.model_dump(), ["symbol", "interval", "sort"])

        url_params = f"{query.symbol}?{query_str}&apikey={api_key}"
        url = f"{base_url}/historical-chart/{query.interval}/{url_params}"

        return await get_data_many(url, "historical", **kwargs)

    @staticmethod
    def transform_data(
        query: FMPIndexHistoricalQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[FMPIndexHistoricalData]:
        """Return the transformed data."""
        if query.sort == "asc":
            data = sorted(data, key=lambda x: x["date"], reverse=True)

        return [FMPIndexHistoricalData.model_validate(d) for d in data]
