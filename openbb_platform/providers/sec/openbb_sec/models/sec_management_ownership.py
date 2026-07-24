"""SEC Management Ownership Model."""

import re
from typing import Any

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from pydantic import Field, field_validator


class SecManagementOwnershipQueryParams(QueryParams):
    """SEC Management Ownership Query.

    The share ownership of directors and executive officers from the company's
    proxy statement (DEF 14A), Security Ownership of Management.
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


class SecManagementOwnershipData(Data):
    """SEC Management Ownership Data."""

    content: str = Field(
        description="The directors and executive officers ownership table from the"
        " proxy (DEF 14A) as a formatted markdown table."
    )


class SecManagementOwnershipFetcher(
    Fetcher[SecManagementOwnershipQueryParams, SecManagementOwnershipData]
):
    """SEC Management Ownership Fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> SecManagementOwnershipQueryParams:
        """Transform the query."""
        return SecManagementOwnershipQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: SecManagementOwnershipQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract management section content from annual filings."""
        from openbb_core.provider.utils.errors import EmptyDataError

        from openbb_sec.models.sec_financials import (
            FinancialStatements,
            no_filing_message,
            resolve_filing_url,
        )

        url = await resolve_filing_url(
            query.symbol,
            query.calendar_year,
            None,
            query.use_cache,
            annual_default=True,
        )
        if not url:
            raise EmptyDataError(no_filing_message(query.symbol))

        statements = FinancialStatements.from_url(url, query.use_cache)
        doc_type = (statements.document_type or "").upper()

        item = None
        if doc_type.startswith(("20-F", "40-F")):
            item = statements.get_item("6")
        elif doc_type.startswith("10-K"):
            item = statements.get_item("10")

        if not item:
            item = statements._item_by_name("senior management")
        if not item:
            item = statements._item_by_name("executive officer")
        if not item:
            item = statements._item_by_name("director")

        content = (item.get("text") if isinstance(item, dict) else "") or ""

        if doc_type.startswith(("20-F", "40-F")) and content:
            start = re.search(
                r"(?im)^\s*A\.\s*Directors\s+and\s+Senior\s+Management\b",
                content,
            )
            if start:
                section = content[start.start() :]
                end = re.search(
                    r"(?im)^\s*B\.\s*Compensation\b",
                    section,
                )
                content = section[: end.start()].strip() if end else section.strip()

        if not content:
            raise EmptyDataError(
                f"No management section was found in an annual filing for {query.symbol}."
            )

        return {"content": content}

    @staticmethod
    def transform_data(
        query: SecManagementOwnershipQueryParams, data: dict, **kwargs: Any
    ) -> SecManagementOwnershipData:
        """Transform the data."""
        return SecManagementOwnershipData.model_validate(data)
