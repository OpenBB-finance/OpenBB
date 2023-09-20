"""FMP Share Statistics Fetcher."""


from datetime import (
    date as dateType,
    datetime,
)
from typing import Any, Dict, List, Optional

from openbb_fmp.utils.helpers import create_url, get_data_many
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.share_statistics import (
    ShareStatisticsData,
    ShareStatisticsQueryParams,
)
from pydantic import validator


class FMPShareStatisticsQueryParams(ShareStatisticsQueryParams):
    """FMP Income Statement QueryParams.

    Source: https://site.financialmodelingprep.com/developer/docs/shares-float-api/
    """


class FMPShareStatisticsData(ShareStatisticsData):
    """FMP Share Statistics Data."""

    @validator("date", pre=True)
    def date_validate(cls, v):  # pylint: disable=E0213
        """Return the date as a datetime object."""
        if isinstance(v, dateType):
            return v
        return datetime.strptime(v, "%Y-%m-%d %H:%M:%S")


class FMPShareStatisticsFetcher(
    Fetcher[
        FMPShareStatisticsQueryParams,
        List[FMPShareStatisticsData],
    ]
):
    """Transform the query, extract and transform the data from the FMP endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FMPShareStatisticsQueryParams:
        """Transform the query params."""
        return FMPShareStatisticsQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FMPShareStatisticsQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the FMP endpoint."""
        api_key = credentials.get("fmp_api_key") if credentials else ""

        url = create_url(4, "shares_float", api_key, query)

        return get_data_many(url, **kwargs)

    @staticmethod
    def transform_data(data: List[Dict]) -> List[FMPShareStatisticsData]:
        """Return the transformed data."""
        return [FMPShareStatisticsData.parse_obj(d) for d in data]
