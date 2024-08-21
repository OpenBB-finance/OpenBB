"""Polygon Company News Model."""

# pylint: disable=unused-argument

from typing import Any, Dict, List, Literal, Optional

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.company_news import (
    CompanyNewsData,
    CompanyNewsQueryParams,
)
from pydantic import BaseModel, Field, field_validator


class PolygonCompanyNewsQueryParams(CompanyNewsQueryParams):
    """Polygon Company News Query.

    Source: https://polygon.io/docs/stocks/get_v2_reference_news
    """

    __json_schema_extra__ = {
        "symbol": {"multiple_items_allowed": True},
        "order": {"choices": ["asc", "desc"]},
    }
    __alias_dict__ = {
        "symbol": "ticker",
        "start_date": "published_utc.gte",
        "end_date": "published_utc.lte",
    }

    order: Literal["asc", "desc"] = Field(
        default="desc", description="Sort order of the articles."
    )

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def _symbol_mandatory(cls, v):
        """Symbol mandatory validator."""
        if not v:
            raise OpenBBError("Required field missing -> symbol")
        return v


class PolygonPublisher(BaseModel):
    """PolygonPublisher Data Model."""

    favicon_url: str = Field(description="Favicon URL.")
    homepage_url: str = Field(description="Homepage URL.")
    logo_url: str = Field(description="Logo URL.")
    name: str = Field(description="Publisher Name.")


class PolygonCompanyNewsData(CompanyNewsData):
    """Polygon Company News Data."""

    __alias_dict__ = {
        "symbols": "tickers",
        "url": "article_url",
        "text": "description",
        "date": "published_utc",
        "images": "image_url",
        "source": "author",
        "tags": "keywords",
    }

    source: Optional[str] = Field(default=None, description="Source of the article.")
    tags: Optional[str] = Field(
        default=None, description="Keywords/tags in the article"
    )
    id: str = Field(description="Article ID.")
    amp_url: Optional[str] = Field(default=None, description="AMP URL.")
    publisher: PolygonPublisher = Field(description="Publisher of the article.")

    @field_validator("symbols", "tags", mode="before", check_fields=False)
    @classmethod
    def symbols_string(cls, v):
        """Symbols string validator."""
        return ",".join(v)

    @field_validator("images", mode="before", check_fields=False)
    @classmethod
    def validate_images(cls, v):
        """Images validator."""
        return [{"url": v}] if v else None


class PolygonCompanyNewsFetcher(
    Fetcher[
        PolygonCompanyNewsQueryParams,
        List[PolygonCompanyNewsData],
    ]
):
    """Polygon Company News Fetcher."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> PolygonCompanyNewsQueryParams:
        """Transform query params."""
        return PolygonCompanyNewsQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: PolygonCompanyNewsQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Extract data."""
        # pylint: disable=import-outside-toplevel
        import asyncio  # noqa
        from openbb_core.provider.utils.helpers import (
            amake_request,
            get_querystring,
        )  # noqa

        api_key = credentials.get("polygon_api_key") if credentials else ""

        base_url = "https://api.polygon.io/v2/reference/news"
        query_str = get_querystring(
            query.model_dump(by_alias=True), ["limit", "ticker"]
        )
        results = []

        async def get_one(symbol):
            """Get one symbol."""
            url = (
                f"{base_url}?ticker={symbol}&{query_str}&limit="
                + f"{query.limit if query.limit and query.limit <= 1000 else 1000}"
                + f"&apiKey={api_key}"
            )
            response = await amake_request(url)
            data = response.get("results", [])  # type: ignore
            next_url = response.get("next_url", None)  # type: ignore
            records = len(data)
            while next_url and records < query.limit:  # type: ignore
                url = f"{next_url}&apiKey={api_key}"
                response = await amake_request(url)
                data.extend(response.get("results", []))  # type: ignore
                records = len(data)
                next_url = response.get("next_url", None)  # type: ignore

            if data:
                results.extend(data[: query.limit])

        await asyncio.gather(*[get_one(symbol) for symbol in query.symbol.split(",")])  # type: ignore

        return results

    @staticmethod
    def transform_data(
        query: PolygonCompanyNewsQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> List[PolygonCompanyNewsData]:
        """Transform data."""
        return [PolygonCompanyNewsData.model_validate(d) for d in data]
