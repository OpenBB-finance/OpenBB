"""FMP Stock Ownership fetcher."""


from datetime import datetime
from typing import Any, Dict, List, Optional

from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.models.price_target import PriceTargetData, PriceTargetQueryParams
from pydantic import validator

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


class FMPPriceTargetData(PriceTargetData):
    """FMP Price Target Data."""

    class Config:
        fields = {
            "published_date": "publishedDate",
            "news_url": "newsURL",
            "news_title": "newsTitle",
            "analyst_name": "analystName",
            "price_target": "priceTarget",
            "adj_price_target": "adjPriceTarget",
            "price_when_posted": "priceWhenPosted",
            "news_publisher": "newsPublisher",
            "news_base_url": "newsBaseURL",
            "analyst_company": "analystCompany",
        }

    @validator("publishedDate", pre=True, check_fields=False)
    def published_date_validate(cls, v: str):  # pylint: disable=E0213
        return datetime.strptime(v, "%Y-%m-%d") if v else None


class FMPPriceTargetFetcher(
    Fetcher[
        PriceTargetQueryParams,
        List[PriceTargetData],
        FMPPriceTargetQueryParams,
        List[FMPPriceTargetData],
    ]
):
    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FMPPriceTargetQueryParams:
        return FMPPriceTargetQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FMPPriceTargetQueryParams, credentials: Optional[Dict[str, str]]
    ) -> List[FMPPriceTargetData]:
        api_key = credentials.get("fmp_api_key") if credentials else ""

        url = create_url(4, "price-target", api_key, query)

        return get_data_many(url, FMPPriceTargetData)

    @staticmethod
    def transform_data(data: List[FMPPriceTargetData]) -> List[FMPPriceTargetData]:
        return data
