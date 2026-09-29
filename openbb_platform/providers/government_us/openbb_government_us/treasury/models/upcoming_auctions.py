"""Upcoming Treasury Auctions Model."""

from datetime import date as dateType
from typing import Any, Literal

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from pydantic import Field

ENDPOINT = "v1/accounting/od/upcoming_auctions"

SECURITY_TYPE_MAP = {
    "bill": "Bill",
    "note": "Note",
    "bond": "Bond",
    "cmb": "CMB",
    "frn": "FRN Note",
    "tips": "TIPS Note",
}


class UpcomingTreasuryAuctionsQueryParams(QueryParams):
    """Upcoming Treasury Auctions Query Parameters.

    Source: https://fiscaldata.treasury.gov/datasets/upcoming-auctions/treasury-securities-upcoming-auctions
    """

    security_type: Literal["bill", "note", "bond", "cmb", "frn", "tips"] | None = Field(
        default=None,
        description="Filter by the type of security.",
    )


class UpcomingTreasuryAuctionsData(Data):
    """Upcoming Treasury Auctions Data.

    Marketable Treasury securities scheduled to be announced and/or auctioned
    in the upcoming week. Only the latest published snapshot is returned.
    """

    auction_date: dateType = Field(
        description="Date of the auction. Rows read soonest first.",
        json_schema_extra={"x-widget_config": {"pinned": "left"}},
    )
    security_type: str = Field(
        description="Type of security - Bill, Note, Bond, CMB, FRN Note, or TIPS Note.",
    )
    security_term: str = Field(
        description="Term of the security."
        " Reopenings carry the remaining term rather than the original term.",
    )
    cusip: str = Field(
        description="CUSIP of the security.",
    )
    offering_amount: float | None = Field(
        default=None,
        description="Offering amount, in dollars."
        " None when the amount has not yet been announced.",
    )
    reopening: bool = Field(
        description="Whether the auction is a reopening of an existing security.",
    )
    announcement_date: dateType = Field(
        description="Date the terms and conditions notification is made public.",
    )
    issue_date: dateType = Field(
        description="Date the security is delivered to the investor"
        " in exchange for payment.",
    )
    as_of_date: dateType = Field(
        description="Date the published snapshot is current as of.",
        json_schema_extra={"x-widget_config": {"hide": True}},
    )


class UpcomingTreasuryAuctionsFetcher(
    Fetcher[
        UpcomingTreasuryAuctionsQueryParams,
        list[UpcomingTreasuryAuctionsData],
    ]
):
    """Fetch upcoming Treasury auction announcements from the FiscalData API."""

    require_credentials = False

    @staticmethod
    def transform_query(params: dict[str, Any]) -> UpcomingTreasuryAuctionsQueryParams:
        """Transform the query params."""
        return UpcomingTreasuryAuctionsQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: UpcomingTreasuryAuctionsQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Extract the data from the FiscalData API."""
        from openbb_government_us.treasury.utils.fiscal_data import get_fiscal_data

        return await get_fiscal_data(ENDPOINT)

    @staticmethod
    def transform_data(
        query: UpcomingTreasuryAuctionsQueryParams, data: list[dict], **kwargs: Any
    ) -> list[UpcomingTreasuryAuctionsData]:
        """Transform the data."""
        from openbb_core.provider.utils.errors import EmptyDataError

        latest = max(row["record_date"] for row in data)
        rows = [row for row in data if row["record_date"] == latest]
        if query.security_type is not None:
            target = SECURITY_TYPE_MAP[query.security_type]
            rows = [row for row in rows if row["security_type"] == target]
        if not rows:
            raise EmptyDataError(
                f"No upcoming auctions for security_type '{query.security_type}'"
                f" in the {latest} snapshot."
            )
        rows.sort(key=lambda row: (row["auction_date"], row["issue_date"]))
        return [
            UpcomingTreasuryAuctionsData.model_validate(
                {
                    "auction_date": row["auction_date"],
                    "security_type": row["security_type"],
                    "security_term": row["security_term"],
                    "cusip": row["cusip"],
                    "offering_amount": row["offering_amt"],
                    "reopening": row["reopening"] == "Yes",
                    "announcement_date": row["announcemt_date"],
                    "issue_date": row["issue_date"],
                    "as_of_date": row["record_date"],
                }
            )
            for row in rows
        ]
