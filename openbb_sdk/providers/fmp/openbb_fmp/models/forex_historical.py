"""FMP Forex end of day fetcher."""


from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

from dateutil.relativedelta import relativedelta
from openbb_fmp.utils.helpers import get_data_many, get_querystring
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.forex_historical import (
    ForexHistoricalData,
    ForexHistoricalQueryParams,
)
from pydantic import Field


class FMPForexHistoricalQueryParams(ForexHistoricalQueryParams):
    """FMP Forex end of day Query.

    Source: https://site.financialmodelingprep.com/developer/docs/#Historical-Forex-Price
    """

    interval: Literal[
        "1min", "5min", "15min", "30min", "1hour", "4hour", "1day"
    ] = Field(default="1day", description="Data granularity.")


class FMPForexHistoricalData(ForexHistoricalData):
    """FMP Forex end of day Data."""

    adjClose: Optional[float] = Field(
        description="Adjusted Close Price of the symbol.", alias="adj_close"
    )
    unadjustedVolume: Optional[float] = Field(
        description="Unadjusted volume of the symbol.", alias="unadjusted_volume"
    )
    change: Optional[float] = Field(
        description="Change in the price of the symbol from the previous day.",
        alias="change",
    )
    changePercent: Optional[float] = Field(
        description=r"Change % in the price of the symbol.", alias="change_percent"
    )
    label: Optional[str] = Field(description="Human readable format of the date.")
    changeOverTime: Optional[float] = Field(
        description=r"Change % in the price of the symbol over a period of time.",
        alias="change_over_time",
    )


class FMPForexHistoricalFetcher(
    Fetcher[
        FMPForexHistoricalQueryParams,
        List[FMPForexHistoricalData],
    ]
):
    """Transform the query, extract and transform the data from the FMP endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FMPForexHistoricalQueryParams:
        """Transform the query params. Start and end dates are set to a 1 year interval."""
        transformed_params = params

        now = datetime.now().date()
        if params.get("start_date") is None:
            transformed_params["start_date"] = now - relativedelta(years=1)

        if params.get("end_date") is None:
            transformed_params["end_date"] = now

        return FMPForexHistoricalQueryParams(**transformed_params)

    @staticmethod
    def extract_data(
        query: FMPForexHistoricalQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the FMP endpoint."""
        api_key = credentials.get("fmp_api_key") if credentials else ""

        base_url = "https://financialmodelingprep.com/api/v3"
        query_str = (
            get_querystring(query.dict(), ["symbol"])
            .replace("start_date", "from")
            .replace("end_date", "to")
        )

        url_params = f"{query.symbol}?{query_str}&apikey={api_key}"
        url = f"{base_url}/historical-chart/{query.interval}/{url_params}"

        if query.interval == "1day":
            url = f"{base_url}/historical-price-full/forex/{url_params}"

        return get_data_many(url, "historical", **kwargs)

    @staticmethod
    def transform_data(data: List[Dict]) -> List[FMPForexHistoricalData]:
        """Return the transformed data."""
        return [FMPForexHistoricalData.parse_obj(d) for d in data]
