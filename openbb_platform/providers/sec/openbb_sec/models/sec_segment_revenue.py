"""SEC Segment and Geographic Revenue Model."""

from typing import Any

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from pydantic import Field

from openbb_sec.models.sec_financials import FilingSectionQueryParams


class SecSegmentRevenueQueryParams(FilingSectionQueryParams):
    """SEC Segment and Geographic Revenue Query."""


class SecSegmentRevenueData(Data):
    """SEC Segment and Geographic Revenue Data."""

    name: str = Field(description="Disclosure name.")
    text: str | None = Field(
        default=None,
        description="Disclosure text, with the segment/revenue tables as markdown.",
    )


class SecSegmentRevenueFetcher(
    Fetcher[SecSegmentRevenueQueryParams, list[SecSegmentRevenueData]]
):
    """SEC Segment and Geographic Revenue Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> SecSegmentRevenueQueryParams:
        """Transform the query."""
        return SecSegmentRevenueQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: SecSegmentRevenueQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Extract the segment and geographic revenue breakdown from the filing."""
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
        results = statements.segment_revenue()

        if not results:
            raise EmptyDataError(
                f"No segment or geographic revenue data found for {query.symbol}."
            )

        return results

    @staticmethod
    def transform_data(
        query: SecSegmentRevenueQueryParams, data: list[dict], **kwargs: Any
    ) -> list[SecSegmentRevenueData]:
        """Transform the data."""
        return [SecSegmentRevenueData.model_validate(d) for d in data]
