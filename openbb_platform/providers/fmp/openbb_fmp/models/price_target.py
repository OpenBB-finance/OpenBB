"""FMP Equity Ownership Model."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.price_target import (
    PriceTargetData,
    PriceTargetQueryParams,
)
from openbb_fmp.utils.helpers import create_url, get_data_many
from pydantic import Field, field_validator


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

    __alias_dict__ = {"news_url": "newsURL", "news_base_url": "newsBaseURL"}

    new_grade: Optional[str] = Field(description="New grade", default=None)
    previous_grade: Optional[str] = Field(description="Previous grade", default=None)
    grading_company: Optional[str] = Field(description="Grading company", default=None)

    @field_validator("published_date", mode="before", check_fields=False)
    def fiscal_date_ending_validate(cls, v: str):  # pylint: disable=E0213
        """Return the fiscal date ending as a datetime object."""
        v = v.replace("\n", "")
        return datetime.strptime(v, "%Y-%m-%dT%H:%M:%S.%fZ")  # type: ignore


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
    def transform_data(
        query: FMPPriceTargetQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[FMPPriceTargetData]:
        """Return the transformed data."""
        return [FMPPriceTargetData.model_validate(d) for d in data]
