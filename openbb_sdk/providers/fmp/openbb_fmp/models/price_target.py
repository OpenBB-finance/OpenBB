"""FMP Stock Ownership fetcher."""


from typing import Any, Dict, List, Optional

from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.price_target import (
    PriceTargetData,
    PriceTargetQueryParams,
)
from pydantic import Field

from openbb_fmp.utils.helpers import create_url, get_data_many


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
        fields = {
            "published_date": "publishedDate",
            "news_url": "newsURL",
            "news_title": "newsTitle",
            "news_base_url": "newsBaseURL",
            "analyst_company": "analystCompany",
            "analyst_name": "analystName",
            "price_target": "priceTarget",
            "adj_price_target": "adjPriceTarget",
            "price_when_posted": "priceWhenPosted",
            "news_publisher": "newsPublisher",
        }

    newGrade: Optional[str] = Field(alias="new_grade", default=None)
    previousGrade: Optional[str] = Field(alias="previous_grade", default=None)
    gradingCompany: Optional[str] = Field(alias="grading_company", default=None)


class FMPPriceTargetFetcher(
    Fetcher[
        FMPPriceTargetQueryParams,
        List[FMPPriceTargetData],
    ]
):
    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FMPPriceTargetQueryParams:
        return FMPPriceTargetQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FMPPriceTargetQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[dict]:
        api_key = credentials.get("fmp_api_key") if credentials else ""
        endpoint = "upgrades-downgrades" if query.with_grade else "price-target"

        url = create_url(4, endpoint, api_key, query)
        return get_data_many(url, **kwargs)

    @staticmethod
    def transform_data(data: List[dict]) -> List[FMPPriceTargetData]:
        return [FMPPriceTargetData(**d) for d in data]
