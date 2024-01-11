"""FMP Analyst Ratings Model."""

from typing import Any, Dict, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.analyst_ratings import (
    AnalystRatingsData,
    AnalystRatingsQueryParams,
)
from openbb_fmp.utils.helpers import create_url, get_data_one


class FMPAnalystRatingsQueryParams(AnalystRatingsQueryParams):
    """FMP Analyst Ratings Query.

    Source: https://site.financialmodelingprep.com/developer/docs/price-target-consensus-api/
    """


class FMPAnalystRatingsData(AnalystRatingsData):
    """FMP Analyst Ratings Data."""


class FMPAnalystRatingsFetcher(
    Fetcher[
        FMPAnalystRatingsQueryParams,
        FMPAnalystRatingsData,
    ]
):
    """Transform the query, extract and transform the data from the FMP endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FMPAnalystRatingsQueryParams:
        """Transform the query params."""
        return FMPAnalystRatingsQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: FMPAnalystRatingsQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> Dict:
        """Return the raw data from the FMP endpoint."""
        api_key = credentials.get("fmp_api_key") if credentials else ""

        url = create_url(4, "price-target-consensus", api_key, query)

        return await get_data_one(url, **kwargs)

    @staticmethod
    # pylint: disable=unused-argument
    def transform_data(
        query: FMPAnalystRatingsQueryParams,
        data: Dict,
        **kwargs: Any,
    ) -> FMPAnalystRatingsData:
        """Return the transformed data."""
        return FMPAnalystRatingsData.model_validate(data)
