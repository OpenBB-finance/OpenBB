"""SEC Filing Disclosures Model."""

from typing import Any

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from pydantic import Field

from openbb_sec.models.sec_financials import FilingSectionQueryParams


class SecDisclosuresQueryParams(FilingSectionQueryParams):
    """SEC Filing Disclosures Query."""


class SecDisclosuresData(Data):
    """SEC Filing Disclosures Data."""

    key: str = Field(description="Disclosure identifier.")
    name: str = Field(description="Disclosure name.")
    text: str | None = Field(
        default=None, description="Disclosure text content, with tables as markdown."
    )
    tables: list | None = Field(
        default=None, description="Structured tables extracted from the disclosure."
    )


class SecDisclosuresFetcher(
    Fetcher[SecDisclosuresQueryParams, list[SecDisclosuresData]]
):
    """SEC Filing Disclosures Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> SecDisclosuresQueryParams:
        """Transform the query."""
        return SecDisclosuresQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: SecDisclosuresQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Extract disclosure text blocks from the filing."""
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
        disclosures = statements.disclosures
        results: list = []
        for key in disclosures:
            info = disclosures[key]
            if not isinstance(info, dict):
                continue
            text = info.get("text") or ""
            if not text:
                continue
            results.append(
                {
                    "key": key,
                    "name": info.get("name") or info.get("long_name") or key,
                    "text": text,
                    "tables": info.get("tables"),
                }
            )

        if not results:
            raise EmptyDataError(
                f"No disclosures found in the filing for {query.symbol}."
            )

        return results

    @staticmethod
    def transform_data(
        query: SecDisclosuresQueryParams, data: list[dict], **kwargs: Any
    ) -> list[SecDisclosuresData]:
        """Transform the data."""
        return [SecDisclosuresData.model_validate(d) for d in data]
