"""US Treasury Auctions Standard Model."""

from datetime import (
    date as dateType,
    datetime,
    timedelta,
)
from typing import Literal

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from pydantic import Field, model_validator


class USTreasuryAuctionsQueryParams(QueryParams):
    """US Treasury Auctions Query."""

    __json_schema_extra__ = {
        "security_type": {
            "choices": ["bill", "note", "bond", "cmb", "tips", "frn"],
        }
    }

    security_type: Literal["bill", "note", "bond", "cmb", "tips", "frn"] | None = Field(
        default=None,
        description="Used to only return securities of a particular type.",
    )
    cusip: str | None = Field(
        default=None,
        description="Filter securities by CUSIP.",
    )
    page_size: int | None = Field(
        default=None,
        description="Maximum number of results to return; you must also include pagenum when using pagesize.",
    )
    page_num: int | None = Field(
        default=None,
        description="The first page number to display results for; used in combination with page size.",
    )
    start_date: dateType | None = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("start_date", "")
        + " The default is 90 days ago.",
    )
    end_date: dateType | None = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("end_date", "") + " The default is today.",
    )

    @model_validator(mode="before")
    @classmethod
    def validate_dates(cls, values) -> dict:
        """Validate the query parameters."""
        if not isinstance(values, dict):
            return values

        if values.get("start_date") is None:
            values["start_date"] = (datetime.now() - timedelta(days=90)).strftime(
                "%Y-%m-%d"
            )
        if values.get("end_date") is None:
            values["end_date"] = datetime.now().strftime("%Y-%m-%d")
        return values


class USTreasuryAuctionsData(Data):
    """US Treasury Auctions Data."""

    cusip: str = Field(description="CUSIP of the Security.")
    issue_date: dateType = Field(
        description="The issue date of the security.",
    )
    security_type: Literal["Bill", "Note", "Bond", "CMB", "TIPS", "FRN"] = Field(
        description="The type of security.",
    )
    security_term: str = Field(
        description="The term of the security.",
    )
    maturity_date: dateType = Field(
        description="The maturity date of the security.",
    )
    interest_rate: float | None = Field(
        default=None,
        description="The interest rate of the security.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    cpi_on_issue_date: float | None = Field(
        default=None,
        description="Reference CPI rate on the issue date of the security.",
    )
    cpi_on_dated_date: float | None = Field(
        default=None,
        description="Reference CPI rate on the dated date of the security.",
    )
    announcement_date: dateType | None = Field(
        default=None,
        description="The announcement date of the security.",
    )
    auction_date: dateType | None = Field(
        default=None,
        description="The auction date of the security.",
    )
    auction_date_year: int | None = Field(
        default=None,
        description="The auction date year of the security.",
    )
    dated_date: dateType | None = Field(
        default=None,
        description="The dated date of the security.",
    )
    first_payment_date: dateType | None = Field(
        default=None,
        description="The first payment date of the security.",
    )
    accrued_interest_per_100: float | None = Field(
        default=None,
        description="Accrued interest per $100.",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    accrued_interest_per_1000: float | None = Field(
        default=None,
        description="Accrued interest per $1000.",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    adjusted_accrued_interest_per_100: float | None = Field(
        default=None,
        description="Adjusted accrued interest per $100.",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    adjusted_accrued_interest_per_1000: float | None = Field(
        default=None,
        description="Adjusted accrued interest per $1000.",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    adjusted_price: float | None = Field(
        default=None,
        description="Adjusted price.",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    allocation_percentage: float | None = Field(
        default=None,
        description="Allocation percentage, as normalized percentage points.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    allocation_percentage_decimals: float | None = Field(
        default=None,
        description="The number of decimals in the Allocation percentage.",
    )
    announced_cusip: str | None = Field(
        default=None,
        description="The announced CUSIP of the security.",
    )
    auction_format: str | None = Field(
        default=None,
        description="The auction format of the security.",
    )
    avg_median_discount_rate: float | None = Field(
        default=None,
        description="The average median discount rate of the security.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    avg_median_investment_rate: float | None = Field(
        default=None,
        description="The average median investment rate of the security.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    avg_median_price: float | None = Field(
        default=None,
        description="The average median price paid for the security.",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    avg_median_discount_margin: float | None = Field(
        default=None,
        description="The average median discount margin of the security.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    avg_median_yield: float | None = Field(
        default=None,
        description="The average median yield of the security.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    back_dated: Literal["Yes", "No"] | None = Field(
        default=None,
        description="Whether the security is back dated.",
    )
    back_dated_date: dateType | None = Field(
        default=None,
        description="The back dated date of the security.",
    )
    bid_to_cover_ratio: float | None = Field(
        default=None,
        description="The bid to cover ratio of the security.",
    )
    call_date: dateType | None = Field(
        default=None,
        description="The call date of the security.",
    )
    callable: Literal["Yes", "No"] | None = Field(
        default=None,
        description="Whether the security is callable.",
    )
    called_date: dateType | None = Field(
        default=None,
        description="The called date of the security.",
    )
    cash_management_bill: Literal["Yes", "No"] | None = Field(
        default=None,
        description="Whether the security is a cash management bill.",
    )
    closing_time_competitive: str | None = Field(
        default=None,
        description="The closing time for competitive bids on the security.",
    )
    closing_time_non_competitive: str | None = Field(
        default=None,
        description="The closing time for non-competitive bids on the security.",
    )
    competitive_accepted: int | None = Field(
        default=None,
        description="The accepted value for competitive bids on the security.",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    competitive_accepted_decimals: int | None = Field(
        default=None,
        description="The number of decimals in the Competitive Accepted.",
    )
    competitive_tendered: int | None = Field(
        default=None,
        description="The tendered value for competitive bids on the security.",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    competitive_tenders_accepted: Literal["Yes", "No"] | None = Field(
        default=None,
        description="Whether competitive tenders are accepted on the security.",
    )
    corp_us_cusip: str | None = Field(
        default=None,
        description="The CUSIP of the security.",
    )
    cpi_base_reference_period: str | None = Field(
        default=None,
        description="The CPI base reference period of the security.",
    )
    currently_outstanding: int | None = Field(
        default=None,
        description="The currently outstanding value on the security.",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    direct_bidder_accepted: int | None = Field(
        default=None,
        description="The accepted value from direct bidders on the security.",
    )
    direct_bidder_tendered: int | None = Field(
        default=None,
        description="The tendered value from direct bidders on the security.",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    est_amount_of_publicly_held_maturing_security: int | None = Field(
        default=None,
        description="The estimated amount of publicly held maturing securities on the security.",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    fima_included: Literal["Yes", "No"] | None = Field(
        default=None,
        description="Whether the security is included in the FIMA (Foreign and International Money Authorities).",
    )
    fima_non_competitive_accepted: int | None = Field(
        default=None,
        description="The non-competitive accepted value on the security from FIMAs.",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    fima_non_competitive_tendered: int | None = Field(
        default=None,
        description="The non-competitive tendered value on the security from FIMAs.",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    first_interest_period: str | None = Field(
        default=None,
        description="The first interest period of the security.",
    )
    first_interest_payment_date: dateType | None = Field(
        default=None,
        description="The first interest payment date of the security.",
    )
    floating_rate: Literal["Yes", "No"] | None = Field(
        default=None,
        description="Whether the security is a floating rate.",
    )
    frn_index_determination_date: dateType | None = Field(
        default=None,
        description="The FRN index determination date of the security.",
    )
    frn_index_determination_rate: float | None = Field(
        default=None,
        description="The FRN index determination rate of the security.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    high_discount_rate: float | None = Field(
        default=None,
        description="The high discount rate of the security.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    high_investment_rate: float | None = Field(
        default=None,
        description="The high investment rate of the security.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    high_price: float | None = Field(
        default=None,
        description="The high price of the security at auction.",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    high_discount_margin: float | None = Field(
        default=None,
        description="The high discount margin of the security.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    high_yield: float | None = Field(
        default=None,
        description="The high yield of the security at auction.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    index_ratio_on_issue_date: float | None = Field(
        default=None,
        description="The index ratio on the issue date of the security.",
    )
    indirect_bidder_accepted: int | None = Field(
        default=None,
        description="The accepted value from indirect bidders on the security.",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    indirect_bidder_tendered: int | None = Field(
        default=None,
        description="The tendered value from indirect bidders on the security.",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    interest_payment_frequency: str | None = Field(
        default=None,
        description="The interest payment frequency of the security.",
    )
    low_discount_rate: float | None = Field(
        default=None,
        description="The low discount rate of the security.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    low_investment_rate: float | None = Field(
        default=None,
        description="The low investment rate of the security.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    low_price: float | None = Field(
        default=None,
        description="The low price of the security at auction.",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    low_discount_margin: float | None = Field(
        default=None,
        description="The low discount margin of the security.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    low_yield: float | None = Field(
        default=None,
        description="The low yield of the security at auction.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    maturing_date: dateType | None = Field(
        default=None,
        description="The maturing date of the security.",
    )
    max_competitive_award: int | None = Field(
        default=None,
        description="The maximum competitive award at auction.",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    max_non_competitive_award: int | None = Field(
        default=None,
        description="The maximum non-competitive award at auction.",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    max_single_bid: int | None = Field(
        default=None,
        description="The maximum single bid at auction.",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    min_bid_amount: int | None = Field(
        default=None,
        description="The minimum bid amount at auction.",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    min_strip_amount: int | None = Field(
        default=None,
        description="The minimum strip amount at auction.",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    min_to_issue: int | None = Field(
        default=None,
        description="The minimum to issue at auction.",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    multiples_to_bid: int | None = Field(
        default=None,
        description="The multiples to bid at auction.",
    )
    multiples_to_issue: int | None = Field(
        default=None,
        description="The multiples to issue at auction.",
    )
    nlp_exclusion_amount: int | None = Field(
        default=None,
        description="The NLP exclusion amount at auction.",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    nlp_reporting_threshold: int | None = Field(
        default=None,
        description="The NLP reporting threshold at auction.",
    )
    non_competitive_accepted: int | None = Field(
        default=None,
        description="The accepted value from non-competitive bidders on the security.",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    non_competitive_tenders_accepted: Literal["Yes", "No"] | None = Field(
        default=None,
        description="Whether or not the auction accepted non-competitive tenders.",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    offering_amount: int | None = Field(
        default=None,
        description="The offering amount at auction.",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    original_cusip: str | None = Field(
        default=None,
        description="The original CUSIP of the security.",
    )
    original_dated_date: dateType | None = Field(
        default=None,
        description="The original dated date of the security.",
    )
    original_issue_date: dateType | None = Field(
        default=None,
        description="The original issue date of the security.",
    )
    original_security_term: str | None = Field(
        default=None,
        description="The original term of the security.",
    )
    pdf_announcement: str | None = Field(
        default=None,
        description="The PDF filename for the announcement of the security.",
    )
    pdf_competitive_results: str | None = Field(
        default=None,
        description="The PDF filename for the competitive results of the security.",
    )
    pdf_non_competitive_results: str | None = Field(
        default=None,
        description="The PDF filename for the non-competitive results of the security.",
    )
    pdf_special_announcement: str | None = Field(
        default=None,
        description="The PDF filename for the special announcements.",
    )
    price_per_100: float | None = Field(
        default=None,
        description="The price per 100 of the security.",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    primary_dealer_accepted: int | None = Field(
        default=None,
        description="The primary dealer accepted value on the security.",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    primary_dealer_tendered: int | None = Field(
        default=None,
        description="The primary dealer tendered value on the security.",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    reopening: Literal["Yes", "No"] | None = Field(
        default=None,
        description="Whether or not the auction was reopened.",
    )
    security_term_day_month: str | None = Field(
        default=None,
        description="The security term in days or months.",
    )
    security_term_week_year: str | None = Field(
        default=None,
        description="The security term in weeks or years.",
    )
    series: str | None = Field(
        default=None,
        description="The series name of the security.",
    )
    soma_accepted: int | None = Field(
        default=None,
        description="The SOMA accepted value on the security.",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    soma_holdings: int | None = Field(
        default=None,
        description="The SOMA holdings on the security.",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    soma_included: Literal["Yes", "No"] | None = Field(
        default=None,
        description="Whether or not the SOMA (System Open Market Account) was included on the security.",
    )
    soma_tendered: int | None = Field(
        default=None,
        description="The SOMA tendered value on the security.",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    spread: float | None = Field(
        default=None,
        description="The spread on the security.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    standard_payment_per_1000: float | None = Field(
        default=None,
        description="The standard payment per 1000 of the security.",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    strippable: Literal["Yes", "No"] | None = Field(
        default=None,
        description="Whether or not the security is strippable.",
    )
    term: str | None = Field(
        default=None,
        description="The term of the security.",
    )
    tiin_conversion_factor_per_1000: float | None = Field(
        default=None,
        description="The TIIN conversion factor per 1000 of the security.",
    )
    tips: Literal["Yes", "No"] | None = Field(
        default=None,
        description="Whether or not the security is TIPS.",
    )
    total_accepted: int | None = Field(
        default=None,
        description="The total accepted value at auction.",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    total_tendered: int | None = Field(
        default=None,
        description="The total tendered value at auction.",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    treasury_retail_accepted: int | None = Field(
        default=None,
        description="The accepted value on the security from retail.",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    treasury_retail_tenders_accepted: Literal["Yes", "No"] | None = Field(
        default=None,
        description="Whether or not the tender offers from retail are accepted",
    )
    type: str | None = Field(
        default=None,
        description="The type of issuance.  This might be different than the security type.",
    )
    unadjusted_accrued_interest_per_1000: float | None = Field(
        default=None,
        description="The unadjusted accrued interest per 1000 of the security.",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    unadjusted_price: float | None = Field(
        default=None,
        description="The unadjusted price of the security.",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    updated_timestamp: datetime | None = Field(
        default=None,
        description="The updated timestamp of the security.",
    )
    xml_announcement: str | None = Field(
        default=None,
        description="The XML filename for the announcement of the security.",
    )
    xml_competitive_results: str | None = Field(
        default=None,
        description="The XML filename for the competitive results of the security.",
    )
    xml_special_announcement: str | None = Field(
        default=None,
        description="The XML filename for special announcements.",
    )
    tint_cusip1: str | None = Field(
        default=None,
        description="Tint CUSIP 1.",
    )
    tint_cusip2: str | None = Field(
        default=None,
        description="Tint CUSIP 2.",
    )
