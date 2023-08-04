"""FMP Treasury Rates fetcher."""


from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.models.treasury_rates import (
    TreasuryRatesData,
    TreasuryRatesQueryParams,
)
from pydantic import validator

from openbb_fmp.utils.helpers import get_data_many, get_querystring


class FMPTreasuryRatesQueryParams(TreasuryRatesQueryParams):
    """FMP Stock News Query.

    Source: https://site.financialmodelingprep.com/developer/docs/treasury-rates-api/

    Maximum time interval can be 3 months.
    """


class FMPTreasuryRatesData(TreasuryRatesData):
    """FMP Treasury Rates Data."""

    class Config:
        fields = {
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

    @validator("date", pre=True, check_fields=False)
    def date_validate(cls, v):  # pylint: disable=E0213
        return datetime.strptime(v, "%Y-%m-%d")


class FMPTreasuryRatesFetcher(
    Fetcher[
        TreasuryRatesQueryParams,
        TreasuryRatesData,
        FMPTreasuryRatesQueryParams,
        FMPTreasuryRatesData,
    ]
):
    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FMPTreasuryRatesQueryParams:
        return FMPTreasuryRatesQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FMPTreasuryRatesQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[FMPTreasuryRatesData]:
        api_key = credentials.get("fmp_api_key") if credentials else ""

        query.start_date = (datetime.now() - timedelta(91)).date()
        query.end_date = (datetime.now() - timedelta(1)).date()

        base_url = "https://financialmodelingprep.com/api/v4/"
        # query_str = get_querystring(query.dict(by_alias=True), [])
        query_str = get_querystring(query.dict(), [])
        query_str = query_str.replace("start_date", "from").replace("end_date", "to")
        url = f"{base_url}treasury?{query_str}&apikey={api_key}"

        return get_data_many(url, FMPTreasuryRatesData, **kwargs)

    @staticmethod
    def transform_data(data: List[FMPTreasuryRatesData]) -> List[FMPTreasuryRatesData]:
        return data
