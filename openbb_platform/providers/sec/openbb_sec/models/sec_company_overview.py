"""SEC Company Overview Model."""

from typing import Any

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from pydantic import Field, field_validator


class SecCompanyOverviewQueryParams(QueryParams):
    """SEC Company Overview Query.

    The company overview is the Business section (Item 1) of the annual report (10-K).
    """

    symbol: str = Field(description="Symbol to get data for.")
    url: str | None = Field(
        default=None,
        description="Direct URL to a 10-K filing, e.g. from `latest_financial_reports`."
        " When provided, the filing is parsed directly and the other params are ignored.",
    )
    calendar_year: int | None = Field(
        default=None,
        description="Calendar year of the 10-K. Defaults to the most recent.",
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


class SecCompanyOverviewData(Data):
    """SEC Company Overview Data."""

    content: str = Field(
        description="The Business section (Item 1) of the 10-K as formatted markdown."
    )


class SecCompanyOverviewFetcher(
    Fetcher[SecCompanyOverviewQueryParams, SecCompanyOverviewData]
):
    """SEC Company Overview Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> SecCompanyOverviewQueryParams:
        """Transform the query."""
        return SecCompanyOverviewQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: SecCompanyOverviewQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract the Business (Item 1) overview from the 10-K filing."""
        from openbb_core.provider.utils.errors import EmptyDataError

        from openbb_sec.models.sec_financials import (
            FinancialStatements,
            no_filing_message,
            resolve_section_url,
        )

        url = await resolve_section_url(query)
        if not url and query.calendar_year is not None:
            url = await resolve_section_url(
                query.model_copy(update={"calendar_year": None})
            )
        if not url:
            raise EmptyDataError(no_filing_message(query.symbol))

        statements = FinancialStatements.from_url(url, query.use_cache)
        content = statements.business()

        if not content:
            raise EmptyDataError(f"No Business section found for {query.symbol}.")

        return {"content": content}

    @staticmethod
    def transform_data(
        query: SecCompanyOverviewQueryParams, data: dict, **kwargs: Any
    ) -> SecCompanyOverviewData:
        """Transform the data."""
        return SecCompanyOverviewData.model_validate(data)
