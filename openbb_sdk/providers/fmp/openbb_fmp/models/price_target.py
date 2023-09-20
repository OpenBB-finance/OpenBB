"""FMP Stock Ownership fetcher."""


from typing import Any, Dict, List, Optional

from openbb_fmp.utils.helpers import create_url, get_data_many
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.price_target import (
    PriceTargetData,
    PriceTargetQueryParams,
)
from pydantic import Field


class FMPPriceTargetQueryParams(PriceTargetQueryParams):
    """FMP Price Target Query.

    Source: https://site.financialmodelingprep.com/developer/docs/#Price-Target
    """

    with_grade: bool = Field(
        False,
        description="Include upgrades and downgrades in the response.",
    )


class FMPPriceTargetData(PriceTargetData):
    """FMP Price Target Data."""

    class Config:
        """Pydantic alias config using fields dict."""

        fields = {"news_url": "newsURL", "news_base_url": "newsBaseURL"}

    new_grade: Optional[str]
    previous_grade: Optional[str]
    grading_company: Optional[str]


class FMPPriceTargetFetcher(
    Fetcher[
        FMPPriceTargetQueryParams,
        List[FMPPriceTargetData],
    ]
):
    """Transform the query, extract and transform the data from the FMP endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FMPPriceTargetQueryParams:
        """Transform the query params."""
        return FMPPriceTargetQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FMPPriceTargetQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the FMP endpoint."""
        api_key = credentials.get("fmp_api_key") if credentials else ""
        endpoint = "upgrades-downgrades" if query.with_grade else "price-target"

        url = create_url(4, endpoint, api_key, query)

        return get_data_many(url, **kwargs)

    @staticmethod
    def transform_data(data: List[Dict]) -> List[FMPPriceTargetData]:
        """Return the transformed data."""
        return [FMPPriceTargetData.parse_obj(d) for d in data]
