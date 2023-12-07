"""FMP Analyst Estimates Model."""


from typing import Any, Dict, List, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.analyst_estimates import (
    AnalystEstimatesData,
    AnalystEstimatesQueryParams,
)
from openbb_fmp.utils.helpers import create_url, get_data_many


class FMPAnalystEstimatesQueryParams(AnalystEstimatesQueryParams):
    """FMP Analyst Estimates Query.

    Source: https://site.financialmodelingprep.com/developer/docs/analyst-estimates-api/
    """


class FMPAnalystEstimatesData(AnalystEstimatesData):
    """FMP Analyst Estimates Data."""


class FMPAnalystEstimatesFetcher(
    Fetcher[
        FMPAnalystEstimatesQueryParams,
        List[FMPAnalystEstimatesData],
    ]
):
    """Transform the query, extract and transform the data from the FMP endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FMPAnalystEstimatesQueryParams:
        """Transform the query params."""
        return FMPAnalystEstimatesQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FMPAnalystEstimatesQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the FMP endpoint."""
        api_key = credentials.get("fmp_api_key") if credentials else ""

        url = create_url(
            3, f"analyst-estimates/{query.symbol}", api_key, query, ["symbol"]
        )

        return get_data_many(url, **kwargs)

    @staticmethod
    def transform_data(
        query: FMPAnalystEstimatesQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[FMPAnalystEstimatesData]:
        """Return the transformed data."""
        return [FMPAnalystEstimatesData.model_validate(d) for d in data]
