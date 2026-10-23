"""SEC Filing Exhibit Model."""

from typing import Any

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from pydantic import Field, field_validator

from openbb_sec.models.sec_financials import FilingSectionQueryParams


class SecExhibitQueryParams(FilingSectionQueryParams):
    """SEC Filing Exhibit Query."""

    exhibit: str | None = Field(
        default=None,
        description="Exhibit identifier (e.g. EX-21). Defaults to the first exhibit"
        " attached to the filing.",
    )

    @field_validator("exhibit", mode="before", check_fields=False)
    @classmethod
    def _exhibit_empty_to_none(cls, v):
        """Treat an empty string as None (first exhibit)."""
        return None if v == "" else v


class SecExhibitData(Data):
    """SEC Filing Exhibit Data."""

    content: str = Field(description="The exhibit content rendered as markdown.")


class SecExhibitFetcher(Fetcher[SecExhibitQueryParams, SecExhibitData]):
    """SEC Filing Exhibit Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> SecExhibitQueryParams:
        """Transform the query."""
        return SecExhibitQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: SecExhibitQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract a single attached exhibit document from the filing."""
        from openbb_core.provider.utils.errors import EmptyDataError

        from openbb_sec.models.sec_financials import (
            FinancialStatements,
            no_filing_message,
            resolve_section_url,
        )

        url = await resolve_section_url(query, annual_default=False)
        if not url:
            raise EmptyDataError(no_filing_message(query.symbol))

        statements = FinancialStatements.from_url(url, query.use_cache)
        choices = statements.exhibit_choices()
        if not choices:
            raise EmptyDataError(
                f"No exhibits are attached to the filing for {query.symbol}."
            )
        identifier = query.exhibit or choices[0]["value"]
        content = statements.get_exhibit(identifier)
        if not content:
            raise EmptyDataError(
                f"Exhibit {identifier} was not found in the filing for {query.symbol}."
            )
        return {"content": content}

    @staticmethod
    def transform_data(
        query: SecExhibitQueryParams, data: dict, **kwargs: Any
    ) -> SecExhibitData:
        """Transform the data."""
        return SecExhibitData.model_validate(data)
