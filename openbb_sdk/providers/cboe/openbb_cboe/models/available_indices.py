"""Available Indices fetcher for CBOE"""

from typing import Any, Dict, List, Optional

from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.available_indices import (
    AvailableIndicesData,
    AvailableIndicesQueryParams,
)
from pydantic import Field

from openbb_cboe.utils.helpers import Europe


class CboeAvailableIndicesQueryParams(AvailableIndicesQueryParams):
    """CBOE Available Indices query.

    Source: https://www.cboe.com/europe/indices/
    """


class CboeAvailableIndicesData(AvailableIndicesData):
    """CBOE Available Indices data.

    Source: https://www.cboe.com/europe/indices/
    """

    isin: Optional[str] = Field(description="ISIN code for the index.")

    region: Optional[str] = Field(description="Region for the index.")


class CboeAvailableIndicesFetcher(
    Fetcher[
        CboeAvailableIndicesQueryParams,
        CboeAvailableIndicesData,
    ]
):
    """Transform the query, extract and transform the data from the CBOE endpoints"""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> CboeAvailableIndicesQueryParams:
        """Transform the query params."""

        return CboeAvailableIndicesQueryParams(**params)

    @staticmethod
    def extract_data(
        query: CboeAvailableIndicesQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the CBOE endpoint"""

        return Europe.list_indices()

    @staticmethod
    def transform_data(data: List[Dict]) -> List[CboeAvailableIndicesData]:
        """Transform the data to the standard format"""

        return [CboeAvailableIndicesData.parse_obj(d) for d in data]
