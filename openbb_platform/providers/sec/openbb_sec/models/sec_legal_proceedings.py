"""SEC Filing Legal Proceedings Model."""

from typing import Any

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from pydantic import Field

from openbb_sec.models.sec_financials import FilingSectionQueryParams


class SecLegalProceedingsQueryParams(FilingSectionQueryParams):
    """SEC Filing Legal Proceedings Query."""


class SecLegalProceedingsData(Data):
    """SEC Filing Legal Proceedings Data."""

    name: str = Field(description="Section name.")
    item_num: str | None = Field(default=None, description="Filing item number.")
    text: str = Field(description="Legal Proceedings section text.")


class SecLegalProceedingsFetcher(
    Fetcher[SecLegalProceedingsQueryParams, list[SecLegalProceedingsData]]
):
    """SEC Filing Legal Proceedings Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> SecLegalProceedingsQueryParams:
        """Transform the query."""
        return SecLegalProceedingsQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: SecLegalProceedingsQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Extract the Legal Proceedings section from the filing."""
        from openbb_core.provider.utils.errors import EmptyDataError

        from openbb_sec.models.sec_financials import (
            FinancialStatements,
            no_filing_message,
            resolve_section_url,
        )

        url = await resolve_section_url(query, annual_default=True)
        if not url:
            raise EmptyDataError(no_filing_message(query.symbol))

        statements = FinancialStatements.from_url(url, query.use_cache)
        item = statements.legal_proceedings()

        if not item or not (item.get("text") or "").strip():
            raise EmptyDataError(
                f"No Legal Proceedings section found for {query.symbol}."
            )

        return [
            {
                "name": item.get("name") or "Legal Proceedings",
                "item_num": item.get("item_num"),
                "text": item["text"],
            }
        ]

    @staticmethod
    def transform_data(
        query: SecLegalProceedingsQueryParams, data: list[dict], **kwargs: Any
    ) -> list[SecLegalProceedingsData]:
        """Transform the data."""
        return [SecLegalProceedingsData.model_validate(d) for d in data]
