"""FMP Company News Model."""

from typing import Any, Dict, List, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.company_news import (
    CompanyNewsData,
    CompanyNewsQueryParams,
)
from openbb_core.provider.utils.errors import EmptyDataError
from openbb_core.provider.utils.helpers import filter_by_dates
from openbb_fmp.utils.helpers import get_data_many
from pydantic import Field, field_validator


class FMPCompanyNewsQueryParams(CompanyNewsQueryParams):
    """FMP Company News Query.

    Source: https://site.financialmodelingprep.com/developer/docs/stock-news-api/
    """

    __json_schema_extra__ = {"symbol": {"multiple_items_allowed": True}}

    page: Optional[int] = Field(
        default=0,
        description="Page number of the results. Use in combination with limit.",
    )

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def _symbol_mandatory(cls, v):
        """Symbol mandatory validator."""
        if not v:
            raise ValueError("Required field missing -> symbol")
        return v


class FMPCompanyNewsData(CompanyNewsData):
    """FMP Company News Data."""

    __alias_dict__ = {
        "symbols": "symbol",
        "date": "publishedDate",
        "images": "image",
        "source": "site",
    }

    source: str = Field(description="Name of the news source.")

    @field_validator("images", mode="before", check_fields=False)
    @classmethod
    def validate_images(cls, v):
        """Validate the images field."""
        if v is None:
            return v
        if isinstance(v, str):
            return [{"url": v}]
        if isinstance(v, dict):
            return [v]
        return v


class FMPCompanyNewsFetcher(
    Fetcher[
        FMPCompanyNewsQueryParams,
        List[FMPCompanyNewsData],
    ]
):
    """Transform the query, extract and transform the data from the FMP endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FMPCompanyNewsQueryParams:
        """Transform the query params."""
        return FMPCompanyNewsQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: FMPCompanyNewsQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the FMP endpoint."""
        api_key = credentials.get("fmp_api_key") if credentials else ""

        base_url = "https://financialmodelingprep.com/api/v3/stock_news"
        url = f"{base_url}?page={query.page}&tickers={query.symbol}&limit={query.limit}&apikey={api_key}"
        response = await get_data_many(url, **kwargs)

        if not response:
            raise EmptyDataError()

        return sorted(response, key=lambda x: x["publishedDate"], reverse=True)

    # pylint: disable=unused-argument
    @staticmethod
    def transform_data(
        query: FMPCompanyNewsQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[FMPCompanyNewsData]:
        """Return the transformed data."""
        modeled_data = [FMPCompanyNewsData.model_validate(d) for d in data]
        return filter_by_dates(modeled_data, query.start_date, query.end_date)
