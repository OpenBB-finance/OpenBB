"""CME product catalog model."""

from typing import Any, Literal

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field, field_validator

from openbb_cme.utils.catalog import search_products
from openbb_cme.utils.client import CMEHttpClient


class CMEProductsQueryParams(QueryParams):
    """Filters for the CME Group product slate."""

    symbol: str | None = Field(
        default=None,
        description="Exact Globex, clearing, ClearPort, floor, or product code.",
    )
    product_type: Literal["Futures", "Options"] | None = Field(
        default=None,
        description="Filter by futures or options on futures.",
    )
    asset_class: str | None = Field(
        default=None,
        description="CME asset class, such as Energy, Equities, FX, or Metals.",
    )
    exchange: str | None = Field(
        default=None,
        description="CME exchange: CME, CBOT, NYMEX, or COMEX.",
    )
    query: str | None = Field(
        default=None,
        description="Case-insensitive product-name or symbol search.",
    )

    @field_validator("symbol", mode="before")
    @classmethod
    def uppercase_symbol(cls, value: str | None) -> str | None:
        """Normalize a supplied product code."""
        return value.strip().upper() if value else None


class CMEProductsData(Data):
    """One product from the public CME Group product slate."""

    product_id: int = Field(description="CME website product identifier.")
    guid: str | None = Field(default=None, description="CME product GUID.")
    symbol: str = Field(description="Preferred Globex or clearing product code.")
    name: str = Field(description="Exchange-published product name.")
    product_type: str = Field(description="Futures or Options.")
    asset_class: str = Field(description="CME product group or asset class.")
    subgroup: str | None = Field(default=None, description="CME product subgroup.")
    category: str | None = Field(default=None, description="CME product category.")
    subcategory: str | None = Field(
        default=None, description="CME product subcategory."
    )
    exchange: str = Field(description="Listing exchange.")
    venues: list[str] = Field(default_factory=list, description="Trading venues.")
    globex_traded: bool = Field(description="Whether the product trades on Globex.")
    floor_traded: bool = Field(description="Whether the product trades on the floor.")
    volume: int | None = Field(default=None, description="Previous-day volume.")
    open_interest: int | None = Field(
        default=None, description="Previous-day open interest."
    )
    codes: dict[str, str] = Field(description="Published product-code variants.")
    specification_url: str | None = Field(
        default=None, description="Official CME contract-specification URL."
    )


class CMEProductsFetcher(Fetcher[CMEProductsQueryParams, list[CMEProductsData]]):
    """Fetch the exchange-wide CME product catalog."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> CMEProductsQueryParams:
        """Transform query parameters."""
        return CMEProductsQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: CMEProductsQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Fetch and filter the public product slate."""
        async with CMEHttpClient() as client:
            results = await search_products(
                symbol=query.symbol,
                product_type=query.product_type,
                asset_class=query.asset_class,
                exchange=query.exchange,
                query=query.query,
                client=client,
            )
        if not results:
            raise EmptyDataError("No CME products matched the supplied filters.")
        return results

    @staticmethod
    def transform_data(
        query: CMEProductsQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[CMEProductsData]:
        """Validate product catalog rows."""
        return [CMEProductsData.model_validate(row) for row in data]
