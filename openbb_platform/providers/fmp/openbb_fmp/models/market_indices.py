"""FMP Market Indices Model."""

# pylint: disable=unused-argument

from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

from dateutil.relativedelta import relativedelta
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.market_indices import (
    MarketIndicesData,
    MarketIndicesQueryParams,
)
from openbb_core.provider.utils.descriptions import DATA_DESCRIPTIONS
from openbb_core.provider.utils.helpers import get_querystring
from openbb_fmp.utils.helpers import get_data_many
from pydantic import Field, NonNegativeInt


class FMPMarketIndicesQueryParams(MarketIndicesQueryParams):
    """FMP Market Indices Query.

    Source: https://site.financialmodelingprep.com/developer/docs/historical-index-price-api/
    """

    __alias_dict__ = {"start_date": "from", "end_date": "to"}

    timeseries: Optional[NonNegativeInt] = Field(
        default=None, description="Number of days to look back."
    )
    interval: Literal["1min", "5min", "15min", "30min", "1hour", "4hour", "1day"] = (
        Field(default="1day", description="Data granularity.")
    )
    sort: Literal["asc", "desc"] = Field(
        default="desc", description="Sort the data in ascending or descending order."
    )


class FMPMarketIndicesData(MarketIndicesData):
    """FMP Market Indices Data."""

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


class FMPMarketIndicesFetcher(
    Fetcher[
        FMPMarketIndicesQueryParams,
        List[FMPMarketIndicesData],
    ]
):
    """Transform the query, extract and transform the data from the FMP endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FMPMarketIndicesQueryParams:
        """Transform the query params."""
        transformed_params = params

        now = datetime.now().date()
        if params.get("start_date") is None:
            transformed_params["start_date"] = now - relativedelta(years=1)

        if params.get("end_date") is None:
            transformed_params["end_date"] = now

        return FMPMarketIndicesQueryParams.model_validate(transformed_params)

    @staticmethod
    async def aextract_data(
        query: FMPMarketIndicesQueryParams,
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
        query: FMPMarketIndicesQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[FMPMarketIndicesData]:
        """Return the transformed data."""
        if query.sort == "asc":
            data = sorted(data, key=lambda x: x["date"], reverse=True)

        return [FMPMarketIndicesData.model_validate(d) for d in data]
