"""FMP Share Statistics Model."""

from datetime import (
    date as dateType,
    datetime,
)
from typing import Any, Dict, List, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.share_statistics import (
    ShareStatisticsData,
    ShareStatisticsQueryParams,
)
from openbb_fmp.utils.helpers import create_url, get_data_many
from pydantic import field_validator


class FMPShareStatisticsQueryParams(ShareStatisticsQueryParams):
    """FMP Share Statistics Query.

    Source: https://site.financialmodelingprep.com/developer/docs/shares-float-api/
    """


class FMPShareStatisticsData(ShareStatisticsData):
    """FMP Share Statistics Data."""

    @field_validator("date", mode="before")
    @classmethod
    def date_validate(cls, v):  # pylint: disable=E0213
        """Return the date as a datetime object."""
        if isinstance(v, dateType) or v is None:
            return v
        return datetime.strptime(v, "%Y-%m-%d %H:%M:%S").date()


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
    async def aextract_data(
        query: FMPShareStatisticsQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the FMP endpoint."""
        api_key = credentials.get("fmp_api_key") if credentials else ""

        url = create_url(4, "shares_float", api_key, query)

        return await get_data_many(url, **kwargs)

    @staticmethod
    def transform_data(
        query: FMPShareStatisticsQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[FMPShareStatisticsData]:
        """Return the transformed data."""
        return [FMPShareStatisticsData.model_validate(d) for d in data]
