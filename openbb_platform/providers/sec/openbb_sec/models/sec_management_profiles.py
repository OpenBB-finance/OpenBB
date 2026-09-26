"""SEC Management Profiles Model."""

import re
from typing import Any

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from pydantic import Field, field_validator


class SecManagementProfilesQueryParams(QueryParams):
    """SEC Management Profiles Query.

    The management section from the company's annual filing.
    """

    symbol: str = Field(description="Symbol to get data for.")
    calendar_year: int | None = Field(
        default=None,
        description="Calendar year of the filing. Defaults to the most recent.",
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


class SecManagementProfilesData(Data):
    """SEC Management Profiles Data."""

    content: str = Field(
        description="Management profiles and governance information as formatted markdown."
    )


class SecManagementProfilesFetcher(
    Fetcher[SecManagementProfilesQueryParams, SecManagementProfilesData]
):
    """SEC Management Profiles Fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> SecManagementProfilesQueryParams:
        """Transform the query."""
        return SecManagementProfilesQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: SecManagementProfilesQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract the management section from the annual filing."""
        from openbb_core.provider.utils.errors import EmptyDataError

        from openbb_sec.models.sec_filing import Filing
        from openbb_sec.models.sec_financials import (
            FinancialStatements,
            no_filing_message,
            resolve_section_url,
        )
        from openbb_sec.utils.proxy_statement import (
            management_information_from_proxy,
            resolve_proxy_url,
        )

        url = await resolve_section_url(query, annual_default=True)
        if not url and query.calendar_year is not None:
            url = await resolve_section_url(
                query.model_copy(update={"calendar_year": None}), annual_default=True
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

        if re.search(r"(?i)proxy\s+statement", content):
            proxy_url = await resolve_proxy_url(
                query.symbol,
                query.calendar_year,
                query.use_cache,
            )
            if not proxy_url and query.calendar_year is not None:
                proxy_url = await resolve_proxy_url(
                    query.symbol,
                    None,
                    query.use_cache,
                )
            if proxy_url:
                proxy_html = await Filing._adownload_file(proxy_url, query.use_cache)
                proxy_content = management_information_from_proxy(proxy_html or "")
                if proxy_content and (
                    "incorporated by reference" in content.lower()
                    or len(proxy_content) > len(content)
                ):
                    content = proxy_content

        if not content:
            raise EmptyDataError(
                f"No management section was found in an annual filing for {query.symbol}."
            )

        return {"content": content}

    @staticmethod
    def transform_data(
        query: SecManagementProfilesQueryParams, data: dict, **kwargs: Any
    ) -> SecManagementProfilesData:
        """Transform the data."""
        return SecManagementProfilesData.model_validate(data)
