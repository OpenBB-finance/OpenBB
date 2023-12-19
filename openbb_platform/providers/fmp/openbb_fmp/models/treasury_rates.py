"""FMP Treasury Rates Model."""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.treasury_rates import (
    TreasuryRatesData,
    TreasuryRatesQueryParams,
)
from openbb_fmp.utils.helpers import get_data_many, get_querystring
from pydantic import field_validator


class FMPTreasuryRatesQueryParams(TreasuryRatesQueryParams):
    """FMP Treasury Rates Query.

    Source: https://site.financialmodelingprep.com/developer/docs/treasury-rates-api/

    Maximum time interval can be 3 months.
    """


class FMPTreasuryRatesData(TreasuryRatesData):
    """FMP Treasury Rates Data."""

    __alias_dict__ = {
        "month_1": "month1",
        "month_2": "month2",
        "month_3": "month3",
        "month_6": "month6",
        "year_1": "year1",
        "year_2": "year2",
        "year_3": "year3",
        "year_5": "year5",
        "year_7": "year7",
        "year_10": "year10",
        "year_20": "year20",
        "year_30": "year30",
    }

    @field_validator("date", mode="before", check_fields=False)
    @classmethod
    def date_validate(cls, v):  # pylint: disable=E0213
        """Return the date as a datetime object."""
        return datetime.strptime(v, "%Y-%m-%d")


class FMPTreasuryRatesFetcher(
    Fetcher[
        FMPTreasuryRatesQueryParams,
        List[FMPTreasuryRatesData],
    ]
):
    """Transform the query, extract and transform the data from the FMP endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FMPTreasuryRatesQueryParams:
        """Transform the query params. Start and end dates are set to a 90 day interval."""
        transformed_params = params

        now = datetime.now().date()
        if params.get("start_date") is None:
            transformed_params["start_date"] = now - timedelta(90)

        if params.get("end_date") is None:
            transformed_params["end_date"] = now

        return FMPTreasuryRatesQueryParams(**transformed_params)

    @staticmethod
    async def aextract_data(
        query: FMPTreasuryRatesQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the FMP endpoint."""
        api_key = credentials.get("fmp_api_key") if credentials else ""

        base_url = "https://financialmodelingprep.com/api/v4/"
        query_str = get_querystring(query.model_dump(), [])
        query_str = query_str.replace("start_date", "from").replace("end_date", "to")
        url = f"{base_url}treasury?{query_str}&apikey={api_key}"

        return await get_data_many(url, **kwargs)

    @staticmethod
    def transform_data(
        query: FMPTreasuryRatesQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[FMPTreasuryRatesData]:
        """Return the transformed data."""
        return [FMPTreasuryRatesData.model_validate(d) for d in data]
