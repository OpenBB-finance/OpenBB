"""FMP Analyst Estimates fetcher."""


from typing import Any, Dict, List, Optional

from openbb_fmp.utils.helpers import create_url, get_data_many
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.analyst_estimates import (
    AnalystEstimatesData,
    AnalystEstimatesQueryParams,
)


class FMPAnalystEstimatesQueryParams(AnalystEstimatesQueryParams):
    """FMP Analysts Estimates Query.

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

        query.period = "quarter" if query.period == "quarterly" else "annual"

        url = create_url(
            3, f"analyst-estimates/{query.symbol}", api_key, query, ["symbol"]
        )

        return get_data_many(url, **kwargs)

    @staticmethod
    def transform_data(data: List[Dict]) -> List[FMPAnalystEstimatesData]:
        """Return the transformed data."""
        return [FMPAnalystEstimatesData.parse_obj(d) for d in data]
