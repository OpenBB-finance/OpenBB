"""SEC Beneficial Ownership Model."""

from typing import Any

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from pydantic import Field, field_validator


class SecBeneficialOwnershipQueryParams(QueryParams):
    """SEC Beneficial Ownership Query.

    The table of 5%+ beneficial owners from the company's proxy statement
    (DEF 14A), Security Ownership of Certain Beneficial Owners.
    """

    symbol: str = Field(description="Symbol to get data for.")
    calendar_year: int | None = Field(
        default=None,
        description="Calendar year the proxy was filed. Defaults to the most recent.",
    )
    use_cache: bool = Field(
        default=True,
        description="Use the cache for downloaded filings. Default is True.",
    )

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def _to_upper(cls, v):
        """Upper-case the symbol."""
        return v.upper() if isinstance(v, str) else v

    @field_validator("calendar_year", mode="before", check_fields=False)
    @classmethod
    def _empty_to_none(cls, v):
        """Treat an empty string as None (most recent filing)."""
        return None if v == "" else v


class SecBeneficialOwnershipData(Data):
    """SEC Beneficial Ownership Data."""

    content: str = Field(
        description="The 5%+ beneficial owners table from the proxy (DEF 14A)"
        " as a formatted markdown table."
    )


class SecBeneficialOwnershipFetcher(
    Fetcher[SecBeneficialOwnershipQueryParams, SecBeneficialOwnershipData]
):
    """SEC Beneficial Ownership Fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> SecBeneficialOwnershipQueryParams:
        """Transform the query."""
        return SecBeneficialOwnershipQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: SecBeneficialOwnershipQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract the 5%+ beneficial owners table from the proxy (DEF 14A)."""
        from openbb_core.provider.utils.errors import EmptyDataError

        from openbb_sec.models.sec_filing import Filing
        from openbb_sec.utils.proxy_statement import (
            beneficial_owners_table,
            resolve_proxy_url,
        )

        url = await resolve_proxy_url(
            query.symbol, query.calendar_year, query.use_cache
        )
        if not url and query.calendar_year is not None:
            url = await resolve_proxy_url(query.symbol, None, query.use_cache)
        if not url:
            raise EmptyDataError(
                f"No proxy statement (DEF 14A) was found for {query.symbol}."
            )

        html = await Filing._adownload_file(url, query.use_cache)
        content = beneficial_owners_table(html or "")
        if not content:
            raise EmptyDataError(
                "No beneficial ownership table was found in the proxy statement for"
                f" {query.symbol}."
            )

        return {"content": content}

    @staticmethod
    def transform_data(
        query: SecBeneficialOwnershipQueryParams, data: dict, **kwargs: Any
    ) -> SecBeneficialOwnershipData:
        """Transform the data."""
        return SecBeneficialOwnershipData.model_validate(data)
