"""FMP Forex end of day fetcher."""


from datetime import datetime
from typing import Any, Dict, List, Optional

from dateutil.relativedelta import relativedelta
from openbb_fmp.utils.helpers import get_data_many, get_querystring
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.forex_historical import (
    ForexHistoricalData,
    ForexHistoricalQueryParams,
)
from pydantic import Field, field_validator


class FMPForexHistoricalQueryParams(ForexHistoricalQueryParams):
    """FMP Forex end of day Query.

    Source: https://site.financialmodelingprep.com/developer/docs/#Historical-Forex-Price
    """


class FMPForexHistoricalData(ForexHistoricalData):
    """FMP Forex end of day Data."""

    adj_close: float = Field(description="Adjusted Close Price of the symbol.")
    unadjusted_volume: float = Field(description="Unadjusted volume of the symbol.")
    change: float = Field(
        description="Change in the price of the symbol from the previous day."
    )
    change_percent: float = Field(description=r"Change \% in the price of the symbol.")
    label: str = Field(description="Human readable format of the date.")
    change_over_time: float = Field(
        description=r"Change \% in the price of the symbol over a period of time.",
    )

    @field_validator("date", mode="before", check_fields=False)
    @classmethod
    def date_validate(cls, v):  # pylint: disable=E0213
        """Return the datetime object from the date string"""
        try:
            return datetime.strptime(v, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            return datetime.strptime(v, "%Y-%m-%d")


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
        query_str = get_querystring(query.model_dump(), ["symbol"])
        query_str = query_str.replace("start_date", "from").replace("end_date", "to")
        url = f"{base_url}/historical-price-full/forex/{query.symbol}?{query_str}&apikey={api_key}"

        return get_data_many(url, "historical", **kwargs)

    @staticmethod
    def transform_data(data: List[Dict]) -> List[FMPForexHistoricalData]:
        """Return the transformed data."""
        return [FMPForexHistoricalData(**d) for d in data]
