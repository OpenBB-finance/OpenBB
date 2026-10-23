"""Treasury Bill Offerings Model."""

from datetime import date as dateType
from typing import Any

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from pydantic import Field

ENDPOINT = "v1/accounting/tb/pdo1_offerings_regular_weekly_treasury_bills"

FIELD_MAP = {
    "issue_date": "issue_date",
    "maturity_date": "maturity_date",
    "days_to_maturity": "days_to_maturity",
    "bids_tendered_mil_amt": "bids_tendered",
    "bids_acc_total_mil_amt": "bids_accepted_total",
    "bids_acc_comp_basis_mil_amt": "bids_accepted_competitive",
    "bids_acc_noncomp_basis_mil_amt": "bids_accepted_noncompetitive",
    "high_price_per_hundred": "high_price_per_hundred",
    "high_discount_rate": "high_discount_rate",
    "high_investment_rate": "high_investment_rate",
    "record_date": "record_date",
}

MILLION_FIELDS = frozenset(
    {
        "bids_tendered",
        "bids_accepted_total",
        "bids_accepted_competitive",
        "bids_accepted_noncompetitive",
    }
)

PERCENT_FIELDS = frozenset({"high_discount_rate", "high_investment_rate"})


class TreasuryBillOfferingsQueryParams(QueryParams):
    """Treasury Bill Offerings Query Parameters.

    Source: https://fiscaldata.treasury.gov/datasets/treasury-bulletin/pdo-1-offerings-of-regular-weekly-treasury-bills
    """

    start_date: dateType | None = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("start_date", "")
        + " Filters on the bill issue date. Data covers issues from"
        + " 2020-10-01 onward. When None, defaults to the trailing 365 days rather than the full history; set it explicitly to reach further back.",
    )
    end_date: dateType | None = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("end_date", "")
        + " Filters on the bill issue date.",
    )


class TreasuryBillOfferingsData(Data):
    """Treasury Bill Offerings Data.

    Results of weekly auctions of regular Treasury bills (4-, 6-, 8-, 13-,
    17-, and 26-week tenors) as printed in table PDO-1 of the quarterly
    Treasury Bulletin. Each auction appears in exactly one bulletin edition,
    so the combined editions form a continuous auction history.
    """

    issue_date: dateType = Field(
        description="Date the bills were issued. This is the observation axis"
        + " of the series.",
        json_schema_extra={"x-widget_config": {"pinned": "left"}},
    )
    maturity_date: dateType = Field(
        description="Date the bills mature.",
    )
    days_to_maturity: int = Field(
        description="Number of days from issue to maturity, identifying the"
        + " bill tenor.",
    )
    bids_tendered: float = Field(
        description="Amount of bids tendered, in dollars.",
    )
    bids_accepted_total: float = Field(
        description="Total amount of bids accepted, in dollars."
        + " Includes amounts awarded to the Federal Reserve System.",
    )
    bids_accepted_competitive: float = Field(
        description="Amount of bids accepted on a competitive basis, in dollars.",
    )
    bids_accepted_noncompetitive: float = Field(
        description="Amount of bids accepted on a non-competitive basis,"
        + " in dollars.",
    )
    high_price_per_hundred: float = Field(
        description="High price per hundred on competitive bids accepted.",
    )
    high_discount_rate: float = Field(
        description="High discount rate on competitive bids accepted,"
        + " as a normalized decimal (percent / 100).",
    )
    high_investment_rate: float = Field(
        description="High investment rate (equivalent coupon-issue yield) on"
        + " competitive bids accepted, as a normalized decimal (percent / 100).",
    )
    record_date: dateType = Field(
        description="Publication date of the quarterly Treasury Bulletin edition"
        + " reporting the auction, not the auction date.",
    )


class TreasuryBillOfferingsFetcher(
    Fetcher[
        TreasuryBillOfferingsQueryParams,
        list[TreasuryBillOfferingsData],
    ]
):
    """Fetch weekly Treasury bill auction results from the FiscalData API."""

    require_credentials = False

    @staticmethod
    def transform_query(params: dict[str, Any]) -> TreasuryBillOfferingsQueryParams:
        """Transform the query params."""
        return TreasuryBillOfferingsQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: TreasuryBillOfferingsQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Extract the data from the FiscalData API."""
        from openbb_government_us.treasury.utils.fiscal_data import (
            build_filters,
            default_start_date,
            get_fiscal_data,
        )

        start_date = default_start_date(query.start_date, query.end_date, 365)
        filters = build_filters(
            [
                ("issue_date", "gte", start_date),
                ("issue_date", "lte", query.end_date),
            ]
        )

        return await get_fiscal_data(
            ENDPOINT, filters=filters, sort="issue_date,src_line_nbr"
        )

    @staticmethod
    def transform_data(
        query: TreasuryBillOfferingsQueryParams, data: list[dict], **kwargs: Any
    ) -> list[TreasuryBillOfferingsData]:
        """Transform the data, newest issue date first."""
        results: list[TreasuryBillOfferingsData] = []

        for row in data:
            record: dict[str, Any] = {}

            for source, target in FIELD_MAP.items():
                value = row[source]

                if target in MILLION_FIELDS:
                    value = float(value) * 1_000_000
                elif target in PERCENT_FIELDS:
                    value = float(value) / 100

                record[target] = value

            results.append(TreasuryBillOfferingsData.model_validate(record))

        return sorted(
            results,
            key=lambda row: (row.issue_date, row.days_to_maturity),
            reverse=True,
        )
