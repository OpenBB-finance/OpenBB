"""Treasury Auction Results Model."""

from datetime import date as dateType
from typing import Any, Literal

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from pydantic import Field

ENDPOINT = "v1/accounting/od/auctions_query"

PERCENT_FIELDS = frozenset(
    {
        "allocation_pctage",
        "avg_med_discnt_rate",
        "avg_med_investment_rate",
        "avg_med_discnt_margin",
        "avg_med_yield",
        "frn_index_determination_rate",
        "high_discnt_rate",
        "high_investment_rate",
        "high_discnt_margin",
        "high_yield",
        "int_rate",
        "low_discnt_rate",
        "low_investment_rate",
        "low_discnt_margin",
        "low_yield",
        "spread",
    }
)


class TreasuryAuctionResultsQueryParams(QueryParams):
    """Treasury Auction Results Query Parameters.

    Source: https://fiscaldata.treasury.gov/datasets/treasury-securities-auctions-data/treasury-securities-auctions-data
    """

    start_date: dateType | None = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("start_date", "")
        + " Filters on the auction date. Data begins 1979-11-15."
        + " When None, defaults to the trailing 365 days rather than the full"
        + " history; set it explicitly to reach further back.",
    )
    end_date: dateType | None = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("end_date", "")
        + " Filters on the auction date.",
    )
    security_type: Literal["bill", "note", "bond"] | None = Field(
        default=None,
        description="Filter by security type. TIPS, FRNs, and cash management"
        + " bills are flagged in the output, not separate types.",
    )
    cusip: str | None = Field(
        default=None,
        description="Filter by CUSIP. Accepts a comma-separated list.",
    )


class TreasuryAuctionResultsData(Data):
    """Treasury Auction Results Data.

    One row per announced or auctioned marketable Treasury security, with
    reopenings as separate rows sharing the CUSIP. Announced-but-not-yet
    auctioned securities appear with null result fields until the auction
    settles, and many bidder-detail fields are only published from
    2008-04-10, TIPS fields from 1997-02-06, and FRN fields from 2014-01-31.
    """

    __alias_dict__ = {
        "announcement_date": "announcemt_date",
        "price_per_100": "price_per100",
        "accrued_interest_per_100": "accrued_int_per100",
        "accrued_interest_per_1000": "accrued_int_per1000",
        "adjusted_accrued_interest_per_1000": "adj_accrued_int_per1000",
        "adjusted_price": "adj_price",
        "allocation_percentage": "allocation_pctage",
        "allocation_percentage_decimals": "allocation_pctage_decimals",
        "announced_cusip": "announcemtd_cusip",
        "avg_median_discount_rate": "avg_med_discnt_rate",
        "avg_median_investment_rate": "avg_med_investment_rate",
        "avg_median_price": "avg_med_price",
        "avg_median_discount_margin": "avg_med_discnt_margin",
        "avg_median_yield": "avg_med_yield",
        "cash_management_bill": "cash_management_bill_cmb",
        "closing_time_competitive": "closing_time_comp",
        "closing_time_noncompetitive": "closing_time_noncomp",
        "competitive_accepted": "comp_accepted",
        "competitive_bid_decimals": "comp_bid_decimals",
        "competitive_tendered": "comp_tendered",
        "competitive_tenders_accepted": "comp_tenders_accepted",
        "estimated_amount_of_publicly_held_maturing_securities": "est_pub_held_mat_by_type_amt",
        "fima_noncompetitive_accepted": "fima_noncomp_accepted",
        "fima_noncompetitive_tendered": "fima_noncomp_tendered",
        "first_interest_period": "first_int_period",
        "first_interest_payment_date": "first_int_payment_date",
        "high_discount_rate": "high_discnt_rate",
        "high_discount_margin": "high_discnt_margin",
        "interest_payment_frequency": "int_payment_frequency",
        "interest_rate": "int_rate",
        "low_discount_rate": "low_discnt_rate",
        "low_discount_margin": "low_discnt_margin",
        "maturing_date": "mat_date",
        "maximum_competitive_award": "max_comp_award",
        "maximum_noncompetitive_award": "max_noncomp_award",
        "maximum_single_bid": "max_single_bid",
        "minimum_bid_amount": "min_bid_amt",
        "minimum_strip_amount": "min_strip_amt",
        "minimum_to_issue": "min_to_issue",
        "nlp_exclusion_amount": "nlp_exclusion_amt",
        "noncompetitive_accepted": "noncomp_accepted",
        "noncompetitive_tenders_accepted": "noncomp_tenders_accepted",
        "offering_amount": "offering_amt",
        "pdf_announcement": "pdf_filenm_announcemt",
        "pdf_competitive_results": "pdf_filenm_comp_results",
        "pdf_noncompetitive_results": "pdf_filenm_noncomp_results",
        "reference_cpi_on_dated_date": "ref_cpi_on_dated_date",
        "reference_cpi_on_issue_date": "ref_cpi_on_issue_date",
        "standard_interest_payment_per_1000": "std_int_payment_per1000",
        "tiin_conversion_factor_per_1000": "tiin_conversion_factor_per1000",
        "treasury_retail_accepted": "treas_retail_accepted",
        "treasury_retail_tenders_accepted": "treas_retail_tenders_accepted",
        "unadjusted_accrued_interest_per_1000": "unadj_accrued_int_per1000",
        "unadjusted_price": "unadj_price",
        "xml_announcement": "xml_filenm_announcemt",
        "xml_competitive_results": "xml_filenm_comp_results",
        "pdf_special_announcement": "pdf_filenm_spec_announcemt",
    }

    auction_date: dateType = Field(
        description="Date of the auction. This is the observation axis of the"
        + " series, and rows read newest first.",
        json_schema_extra={"x-widget_config": {"pinned": "left"}},
    )
    security_type: str = Field(
        description="Type of the security: Bill, Note, or Bond.",
    )
    security_term: str = Field(
        description="Term of the security, e.g. 13-Week or 29-Year 9-Month.",
    )
    cusip: str = Field(
        description="CUSIP of the security. Repeats across reopenings;"
        + " (cusip, issue_date) is the unique key.",
    )
    issue_date: dateType = Field(
        description="Date the security is issued.",
    )
    maturity_date: dateType = Field(
        description="Date the security matures.",
    )
    announcement_date: dateType = Field(
        description="Date the auction was announced.",
    )
    price_per_100: float | None = Field(
        default=None,
        description="Settlement price per $100 face value.",
    )
    accrued_interest_per_100: float | None = Field(
        default=None,
        description="Accrued interest per $100 face value, on FRN reopenings.",
    )
    accrued_interest_per_1000: float | None = Field(
        default=None,
        description="Accrued interest per $1,000 face value, on coupon"
        + " reopenings and back-dated issues.",
    )
    adjusted_accrued_interest_per_1000: float | None = Field(
        default=None,
        description="Inflation-adjusted accrued interest per $1,000 face"
        + " value, on TIPS.",
    )
    adjusted_price: float | None = Field(
        default=None,
        description="Inflation-adjusted price per $100 face value, on TIPS.",
    )
    allocation_percentage: float | None = Field(
        default=None,
        description="Share of bids at the high rate or yield that was"
        + " awarded, as a normalized decimal (percent / 100).",
    )
    allocation_percentage_decimals: int | None = Field(
        default=None,
        description="Number of decimals in the allocation percentage.",
        json_schema_extra={"x-widget_config": {"hide": True}},
    )
    announced_cusip: str | None = Field(
        default=None,
        description="CUSIP announced for an unscheduled reopening.",
    )
    auction_format: str | None = Field(
        default=None,
        description="Auction format: Single-Price, Multi-Price, or" + " Price-Based.",
    )
    avg_median_discount_rate: float | None = Field(
        default=None,
        description="Weighted-average or median discount rate of accepted"
        + " bill bids, as a normalized decimal (percent / 100).",
    )
    avg_median_investment_rate: float | None = Field(
        default=None,
        description="Weighted-average or median investment rate of accepted"
        + " bill bids, as a normalized decimal (percent / 100)."
        + " Discontinued after 1998-10-29.",
        json_schema_extra={"x-widget_config": {"hide": True}},
    )
    avg_median_price: float | None = Field(
        default=None,
        description="Weighted-average or median accepted price per $100 face"
        + " value, on multi-price auctions. Discontinued after 2008-04-03.",
        json_schema_extra={"x-widget_config": {"hide": True}},
    )
    avg_median_discount_margin: float | None = Field(
        default=None,
        description="Weighted-average or median discount margin of accepted"
        + " FRN bids, as a normalized decimal (percent / 100).",
    )
    avg_median_yield: float | None = Field(
        default=None,
        description="Weighted-average or median yield of accepted bids on"
        + " notes and bonds, as a normalized decimal (percent / 100).",
    )
    back_dated: bool | None = Field(
        default=None,
        description="Whether the issue is back-dated.",
    )
    back_dated_date: dateType | None = Field(
        default=None,
        description="Date to which the issue is back-dated.",
    )
    bid_to_cover_ratio: float | None = Field(
        default=None,
        description="Ratio of total tendered to total accepted.",
    )
    callable: bool | None = Field(
        default=None,
        description="Whether the security is callable.",
    )
    call_date: dateType | None = Field(
        default=None,
        description="Earliest call date, on pre-1985 callable bonds.",
        json_schema_extra={"x-widget_config": {"hide": True}},
    )
    called_date: dateType | None = Field(
        default=None,
        description="Date the security was called, on pre-1985 callable" + " bonds.",
        json_schema_extra={"x-widget_config": {"hide": True}},
    )
    cash_management_bill: bool = Field(
        description="Whether the security is a cash management bill.",
    )
    closing_time_competitive: str | None = Field(
        default=None,
        description="Closing time for competitive tenders, Eastern Time.",
    )
    closing_time_noncompetitive: str | None = Field(
        default=None,
        description="Closing time for noncompetitive tenders, Eastern Time.",
    )
    competitive_accepted: float | None = Field(
        default=None,
        description="Competitive bids accepted, in dollars.",
    )
    competitive_bid_decimals: int | None = Field(
        default=None,
        description="Number of decimals allowed in competitive bids.",
        json_schema_extra={"x-widget_config": {"hide": True}},
    )
    competitive_tendered: float | None = Field(
        default=None,
        description="Competitive bids tendered, in dollars.",
    )
    competitive_tenders_accepted: bool | None = Field(
        default=None,
        description="Whether competitive tenders were accepted.",
    )
    corpus_cusip: str | None = Field(
        default=None,
        description="CUSIP of the stripped principal component.",
    )
    cpi_base_reference_period: str | None = Field(
        default=None,
        description="CPI base reference period, on TIPS.",
    )
    currently_outstanding: float | None = Field(
        default=None,
        description="Amount currently outstanding before a reopening, in" + " dollars.",
    )
    dated_date: dateType | None = Field(
        default=None,
        description="Date from which interest accrues, on coupon securities.",
    )
    direct_bidder_accepted: float | None = Field(
        default=None,
        description="Direct bidder tenders accepted, in dollars.",
    )
    direct_bidder_tendered: float | None = Field(
        default=None,
        description="Direct bidder tenders submitted, in dollars.",
    )
    estimated_amount_of_publicly_held_maturing_securities: float | None = Field(
        default=None,
        description="Estimated amount of publicly held maturing securities of"
        + " the same type, in dollars.",
    )
    fima_included: bool | None = Field(
        default=None,
        description="Whether FIMA noncompetitive tenders were included.",
    )
    fima_noncompetitive_accepted: float | None = Field(
        default=None,
        description="FIMA noncompetitive tenders accepted, in dollars.",
    )
    fima_noncompetitive_tendered: float | None = Field(
        default=None,
        description="FIMA noncompetitive tenders submitted, in dollars.",
    )
    first_interest_period: str | None = Field(
        default=None,
        description="First interest period: Long, Normal, or Short.",
    )
    first_interest_payment_date: dateType | None = Field(
        default=None,
        description="Date of the first interest payment, on coupon" + " securities.",
    )
    floating_rate: bool = Field(
        description="Whether the security is a floating rate note.",
    )
    frn_index_determination_date: dateType | None = Field(
        default=None,
        description="Date the FRN index rate was determined.",
    )
    frn_index_determination_rate: float | None = Field(
        default=None,
        description="FRN index rate on the determination date, as a"
        + " normalized decimal (percent / 100).",
    )
    high_discount_rate: float | None = Field(
        default=None,
        description="Highest accepted discount rate on bills, as a normalized"
        + " decimal (percent / 100).",
    )
    high_investment_rate: float | None = Field(
        default=None,
        description="Coupon-equivalent yield of the high discount rate, as a"
        + " normalized decimal (percent / 100).",
    )
    high_price: float | None = Field(
        default=None,
        description="Price at the highest accepted rate or yield, per $100"
        + " face value.",
    )
    high_discount_margin: float | None = Field(
        default=None,
        description="Highest accepted discount margin on FRNs, as a"
        + " normalized decimal (percent / 100).",
    )
    high_yield: float | None = Field(
        default=None,
        description="Highest accepted yield on notes and bonds, as a"
        + " normalized decimal (percent / 100).",
    )
    index_ratio_on_issue_date: float | None = Field(
        default=None,
        description="Inflation index ratio on the issue date, on TIPS.",
    )
    indirect_bidder_accepted: float | None = Field(
        default=None,
        description="Indirect bidder tenders accepted, in dollars.",
    )
    indirect_bidder_tendered: float | None = Field(
        default=None,
        description="Indirect bidder tenders submitted, in dollars.",
    )
    interest_payment_frequency: str | None = Field(
        default=None,
        description="Interest payment frequency: Annual, Quarterly,"
        + " Semi-Annual, or None.",
    )
    interest_rate: float | None = Field(
        default=None,
        description="Coupon rate of the security, as a normalized decimal"
        + " (percent / 100).",
    )
    low_discount_rate: float | None = Field(
        default=None,
        description="Lowest accepted discount rate on bills, as a normalized"
        + " decimal (percent / 100).",
    )
    low_investment_rate: float | None = Field(
        default=None,
        description="Lowest accepted investment rate on multi-price bill"
        + " auctions, as a normalized decimal (percent / 100)."
        + " Discontinued after 1998-10-29.",
        json_schema_extra={"x-widget_config": {"hide": True}},
    )
    low_price: float | None = Field(
        default=None,
        description="Lowest accepted price per $100 face value, on"
        + " multi-price auctions. Discontinued after 2008-04-03.",
        json_schema_extra={"x-widget_config": {"hide": True}},
    )
    low_discount_margin: float | None = Field(
        default=None,
        description="Lowest accepted discount margin on FRNs, as a normalized"
        + " decimal (percent / 100).",
    )
    low_yield: float | None = Field(
        default=None,
        description="Lowest accepted yield on notes and bonds, as a"
        + " normalized decimal (percent / 100).",
    )
    maturing_date: dateType | None = Field(
        default=None,
        description="Date of the maturing securities being refunded, not the"
        + " maturity of the offered security.",
    )
    maximum_competitive_award: float | None = Field(
        default=None,
        description="Maximum competitive award to a single bidder, in" + " dollars.",
    )
    maximum_noncompetitive_award: float | None = Field(
        default=None,
        description="Maximum noncompetitive award to a single bidder, in" + " dollars.",
    )
    maximum_single_bid: float | None = Field(
        default=None,
        description="Maximum single bid, in dollars.",
    )
    minimum_bid_amount: float | None = Field(
        default=None,
        description="Minimum bid amount, in dollars.",
    )
    minimum_strip_amount: float | None = Field(
        default=None,
        description="Minimum amount that can be stripped, in dollars.",
    )
    minimum_to_issue: float | None = Field(
        default=None,
        description="Minimum amount to issue, in dollars.",
    )
    multiples_to_bid: float | None = Field(
        default=None,
        description="Bid multiples, in dollars.",
    )
    multiples_to_issue: float | None = Field(
        default=None,
        description="Issue multiples, in dollars.",
    )
    nlp_exclusion_amount: float | None = Field(
        default=None,
        description="Net long position exclusion amount, in dollars.",
    )
    nlp_reporting_threshold: float | None = Field(
        default=None,
        description="Net long position reporting threshold, in dollars.",
    )
    noncompetitive_accepted: float | None = Field(
        default=None,
        description="Noncompetitive tenders accepted, in dollars.",
    )
    noncompetitive_tenders_accepted: bool | None = Field(
        default=None,
        description="Whether noncompetitive tenders were accepted.",
    )
    offering_amount: float | None = Field(
        default=None,
        description="Announced offering amount, in dollars.",
    )
    original_cusip: str | None = Field(
        default=None,
        description="Original CUSIP for an unscheduled reopening.",
    )
    original_dated_date: dateType | None = Field(
        default=None,
        description="Dated date of the original issue, on reopenings.",
    )
    original_issue_date: dateType | None = Field(
        default=None,
        description="Issue date of the original issue, on reopenings.",
    )
    original_security_term: str | None = Field(
        default=None,
        description="Term of the security at original issuance.",
    )
    pdf_announcement: str | None = Field(
        default=None,
        description="PDF filename of the announcement, on treasurydirect.gov.",
        json_schema_extra={"x-widget_config": {"hide": True}},
    )
    pdf_competitive_results: str | None = Field(
        default=None,
        description="PDF filename of the competitive results, on"
        + " treasurydirect.gov.",
        json_schema_extra={"x-widget_config": {"hide": True}},
    )
    pdf_noncompetitive_results: str | None = Field(
        default=None,
        description="PDF filename of the noncompetitive results, on"
        + " treasurydirect.gov.",
        json_schema_extra={"x-widget_config": {"hide": True}},
    )
    primary_dealer_accepted: float | None = Field(
        default=None,
        description="Primary dealer tenders accepted, in dollars.",
    )
    primary_dealer_tendered: float | None = Field(
        default=None,
        description="Primary dealer tenders submitted, in dollars.",
    )
    reference_cpi_on_dated_date: float | None = Field(
        default=None,
        description="Reference CPI on the dated date, on TIPS.",
    )
    reference_cpi_on_issue_date: float | None = Field(
        default=None,
        description="Reference CPI on the issue date, on TIPS.",
    )
    reopening: bool = Field(
        description="Whether the auction reopens an existing security.",
    )
    security_term_day_month: str | None = Field(
        default=None,
        description="Security term expressed in days or months.",
    )
    security_term_week_year: str | None = Field(
        default=None,
        description="Security term expressed in weeks or years.",
    )
    series: str | None = Field(
        default=None,
        description="Series of the security, on coupon securities.",
    )
    soma_accepted: float | None = Field(
        default=None,
        description="SOMA tenders accepted, in dollars.",
    )
    soma_holdings: float | None = Field(
        default=None,
        description="SOMA holdings of maturing securities, in dollars.",
    )
    soma_included: bool | None = Field(
        default=None,
        description="Whether SOMA tenders were included in the offering" + " amount.",
    )
    soma_tendered: float | None = Field(
        default=None,
        description="SOMA tenders submitted, in dollars.",
    )
    spread: float | None = Field(
        default=None,
        description="FRN spread over the index rate, as a normalized decimal"
        + " (percent / 100).",
    )
    standard_interest_payment_per_1000: float | None = Field(
        default=None,
        description="Standard interest payment per $1,000 face value, on"
        + " coupon securities.",
    )
    strippable: bool | None = Field(
        default=None,
        description="Whether the security can be stripped.",
    )
    tiin_conversion_factor_per_1000: float | None = Field(
        default=None,
        description="TIIN conversion factor per $1,000 face value, on TIPS.",
    )
    total_accepted: float | None = Field(
        default=None,
        description="Total tenders accepted, in dollars.",
    )
    total_tendered: float | None = Field(
        default=None,
        description="Total tenders submitted, in dollars.",
    )
    treasury_retail_accepted: float | None = Field(
        default=None,
        description="Treasury retail tenders accepted, in dollars.",
    )
    treasury_retail_tenders_accepted: bool | None = Field(
        default=None,
        description="Whether Treasury retail tenders were accepted.",
    )
    unadjusted_accrued_interest_per_1000: float | None = Field(
        default=None,
        description="Unadjusted accrued interest per $1,000 face value, on" + " TIPS.",
    )
    unadjusted_price: float | None = Field(
        default=None,
        description="Unadjusted price per $100 face value, on TIPS.",
    )
    xml_announcement: str | None = Field(
        default=None,
        description="XML filename of the announcement, on treasurydirect.gov.",
        json_schema_extra={"x-widget_config": {"hide": True}},
    )
    xml_competitive_results: str | None = Field(
        default=None,
        description="XML filename of the competitive results, on"
        + " treasurydirect.gov.",
        json_schema_extra={"x-widget_config": {"hide": True}},
    )
    inflation_index_security: bool = Field(
        description="Whether the security is a TIPS.",
    )
    tint_cusip_1: str | None = Field(
        default=None,
        description="CUSIP of the first stripped interest component.",
    )
    tint_cusip_2: str | None = Field(
        default=None,
        description="CUSIP of the second stripped interest component.",
    )
    pdf_special_announcement: str | None = Field(
        default=None,
        description="PDF filename of a special announcement, on"
        + " treasurydirect.gov.",
        json_schema_extra={"x-widget_config": {"hide": True}},
    )


FIELDS = frozenset(
    {
        *TreasuryAuctionResultsData.model_fields,
        *TreasuryAuctionResultsData.__alias_dict__.values(),
    }
)


class TreasuryAuctionResultsFetcher(
    Fetcher[
        TreasuryAuctionResultsQueryParams,
        list[TreasuryAuctionResultsData],
    ]
):
    """Fetch Treasury securities auction results from the FiscalData API."""

    require_credentials = False

    @staticmethod
    def transform_query(params: dict[str, Any]) -> TreasuryAuctionResultsQueryParams:
        """Transform the query params."""
        return TreasuryAuctionResultsQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: TreasuryAuctionResultsQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Extract the data from the FiscalData API."""
        from openbb_government_us.treasury.utils.fiscal_data import (
            build_filters,
            default_start_date,
            get_fiscal_data,
        )

        cusip_eq: str | None = None
        cusip_in: str | None = None
        if query.cusip:
            cusips = ",".join(item.strip() for item in query.cusip.split(","))
            if "," in cusips:
                cusip_in = f"({cusips})"
            else:
                cusip_eq = cusips

        start_date = query.start_date
        if start_date is None and not query.cusip:
            start_date = default_start_date(None, query.end_date, 365)
        filters = build_filters(
            [
                ("auction_date", "gte", start_date),
                ("auction_date", "lte", query.end_date),
                (
                    "security_type",
                    "eq",
                    query.security_type.capitalize() if query.security_type else None,
                ),
                ("cusip", "eq", cusip_eq),
                ("cusip", "in", cusip_in),
            ]
        )

        return await get_fiscal_data(ENDPOINT, filters=filters, sort="auction_date")

    @staticmethod
    def transform_data(
        query: TreasuryAuctionResultsQueryParams, data: list[dict], **kwargs: Any
    ) -> list[TreasuryAuctionResultsData]:
        """Transform the data, newest auction first."""
        results: list[TreasuryAuctionResultsData] = []
        for row in data:
            record = {key: value for key, value in row.items() if key in FIELDS}
            for key in PERCENT_FIELDS:
                value = record.get(key)
                if value is not None:
                    record[key] = float(value) / 100
            if record.get("auction_format") == "Single Price":
                record["auction_format"] = "Single-Price"
            results.append(TreasuryAuctionResultsData.model_validate(record))
        return sorted(
            results,
            key=lambda row: (row.auction_date, row.issue_date),
            reverse=True,
        )
