"""US Treasury Auctions Standard Model."""

from datetime import (
    date as dateType,
    datetime,
    timedelta,
)
from typing import Literal, Optional

from pydantic import Field, model_validator

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS


class USTreasuryAuctionsQueryParams(QueryParams):
    """US Treasury Auctions Query."""

    security_type: Literal["Bill", "Note", "Bond", "CMB", "TIPS", "FRN", None] = Field(
        default=None,
        description="Used to only return securities of a particular type.",
        alias="type",
    )
    cusip: Optional[str] = Field(
        default=None,
        description="Filter securities by CUSIP.",
    )
    page_size: Optional[int] = Field(
        default=None,
        description="Maximum number of results to return; you must also include pagenum when using pagesize.",
        alias="pagesize",
    )
    page_num: Optional[int] = Field(
        default=None,
        description="The first page number to display results for; used in combination with page size.",
        alias="pagenum",
    )
    start_date: Optional[dateType] = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("start_date", "")
        + " The default is 90 days ago.",
    )
    end_date: Optional[dateType] = Field(
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
        description="The issue date of the security.", alias="issueDate"
    )
    security_type: Literal["Bill", "Note", "Bond", "CMB", "TIPS", "FRN"] = Field(
        description="The type of security.", alias="securityType"
    )
    security_term: str = Field(
        description="The term of the security.", alias="securityTerm"
    )
    maturity_date: dateType = Field(
        description="The maturity date of the security.", alias="maturityDate"
    )
    interest_rate: Optional[float] = Field(
        default=None,
        description="The interest rate of the security.",
        alias="interestRate",
    )
    cpi_on_issue_date: Optional[float] = Field(
        default=None,
        description="Reference CPI rate on the issue date of the security.",
        alias="refCpiOnIssueDate",
    )
    cpi_on_dated_date: Optional[float] = Field(
        default=None,
        description="Reference CPI rate on the dated date of the security.",
        alias="refCpiOnDatedDate",
    )
    announcement_date: Optional[dateType] = Field(
        default=None,
        description="The announcement date of the security.",
        alias="announcementDate",
    )
    auction_date: Optional[dateType] = Field(
        default=None,
        description="The auction date of the security.",
        alias="auctionDate",
    )
    auction_date_year: Optional[int] = Field(
        default=None,
        description="The auction date year of the security.",
        alias="auctionDateYear",
    )
    dated_date: Optional[dateType] = Field(
        default=None, description="The dated date of the security.", alias="datedDate"
    )
    first_payment_date: Optional[dateType] = Field(
        default=None,
        description="The first payment date of the security.",
        alias="firstInterestPaymentDate",
    )
    accrued_interest_per_100: Optional[float] = Field(
        default=None,
        description="Accrued interest per $100.",
        alias="accruedInterestPer100",
    )
    accrued_interest_per_1000: Optional[float] = Field(
        default=None,
        description="Accrued interest per $1000.",
        alias="accruedInterestPer1000",
    )
    adjusted_accrued_interest_per_100: Optional[float] = Field(
        default=None,
        description="Adjusted accrued interest per $100.",
        alias="adjustedAccruedInterestPer100",
    )
    adjusted_accrued_interest_per_1000: Optional[float] = Field(
        default=None,
        description="Adjusted accrued interest per $1000.",
        alias="adjustedAccruedInterestPer1000",
    )
    adjusted_price: Optional[float] = Field(
        default=None, description="Adjusted price.", alias="adjustedPrice"
    )
    allocation_percentage: Optional[float] = Field(
        default=None,
        description="Allocation percentage, as normalized percentage points.",
        alias="allocationPercentage",
    )
    allocation_percentage_decimals: Optional[float] = Field(
        default=None,
        description="The number of decimals in the Allocation percentage.",
        alias="allocationPercentageDecimals",
    )
    announced_cusip: Optional[str] = Field(
        default=None,
        description="The announced CUSIP of the security.",
        alias="announcedCusip",
    )
    auction_format: Optional[str] = Field(
        default=None,
        description="The auction format of the security.",
        alias="auctionFormat",
    )
    avg_median_discount_rate: Optional[float] = Field(
        default=None,
        description="The average median discount rate of the security.",
        alias="averageMedianDiscountRate",
    )
    avg_median_investment_rate: Optional[float] = Field(
        default=None,
        description="The average median investment rate of the security.",
        alias="averageMedianInvestmentRate",
    )
    avg_median_price: Optional[float] = Field(
        default=None,
        description="The average median price paid for the security.",
        alias="averageMedianPrice",
    )
    avg_median_discount_margin: Optional[float] = Field(
        default=None,
        description="The average median discount margin of the security.",
        alias="averageMedianDiscountMargin",
    )
    avg_median_yield: Optional[float] = Field(
        default=None,
        description="The average median yield of the security.",
        alias="averageMedianYield",
    )
    back_dated: Literal["Yes", "No", None] = Field(
        default=None,
        description="Whether the security is back dated.",
        alias="backDated",
    )
    back_dated_date: Optional[dateType] = Field(
        default=None,
        description="The back dated date of the security.",
        alias="backDatedDate",
    )
    bid_to_cover_ratio: Optional[float] = Field(
        default=None,
        description="The bid to cover ratio of the security.",
        alias="bidToCoverRatio",
    )
    call_date: Optional[dateType] = Field(
        default=None, description="The call date of the security.", alias="callDate"
    )
    callable: Literal["Yes", "No", None] = Field(
        default=None,
        description="Whether the security is callable.",
    )
    called_date: Optional[dateType] = Field(
        default=None, description="The called date of the security.", alias="calledDate"
    )
    cash_management_bill: Literal["Yes", "No", None] = Field(
        default=None,
        description="Whether the security is a cash management bill.",
        alias="cashManagementBillCMB",
    )
    closing_time_competitive: Optional[str] = Field(
        default=None,
        description="The closing time for competitive bids on the security.",
        alias="closingTimeCompetitive",
    )
    closing_time_non_competitive: Optional[str] = Field(
        default=None,
        description="The closing time for non-competitive bids on the security.",
        alias="closingTimeNoncompetitive",
    )
    competitive_accepted: Optional[int] = Field(
        default=None,
        description="The accepted value for competitive bids on the security.",
        alias="competitiveAccepted",
    )
    competitive_accepted_decimals: Optional[int] = Field(
        default=None,
        description="The number of decimals in the Competitive Accepted.",
        alias="competitiveBidDecimals",
    )
    competitive_tendered: Optional[int] = Field(
        default=None,
        description="The tendered value for competitive bids on the security.",
        alias="competitiveTendered",
    )
    competitive_tenders_accepted: Optional[Literal["Yes", "No", None]] = Field(
        default=None,
        description="Whether competitive tenders are accepted on the security.",
        alias="competitiveTendersAccepted",
    )
    corp_us_cusip: Optional[str] = Field(
        default=None, description="The CUSIP of the security.", alias="corpusCusip"
    )
    cpi_base_reference_period: Optional[str] = Field(
        default=None,
        description="The CPI base reference period of the security.",
        alias="cpiBaseReferencePeriod",
    )
    currently_outstanding: Optional[int] = Field(
        default=None,
        description="The currently outstanding value on the security.",
        alias="currentlyOutstanding",
    )
    direct_bidder_accepted: Optional[int] = Field(
        default=None,
        description="The accepted value from direct bidders on the security.",
        alias="directBidderAccepted",
    )
    direct_bidder_tendered: Optional[int] = Field(
        default=None,
        description="The tendered value from direct bidders on the security.",
        alias="directBidderTendered",
    )
    est_amount_of_publicly_held_maturing_security: Optional[int] = Field(
        default=None,
        description="The estimated amount of publicly held maturing securities on the security.",
        alias="estimatedAmountOfPubliclyHeldMaturingSecuritiesByType",
    )
    fima_included: Literal["Yes", "No", None] = Field(
        default=None,
        description="Whether the security is included in the FIMA (Foreign and International Money Authorities).",
        alias="fimaIncluded",
    )
    fima_non_competitive_accepted: Optional[int] = Field(
        default=None,
        description="The non-competitive accepted value on the security from FIMAs.",
        alias="fimaNoncompetitiveAccepted",
    )
    fima_non_competitive_tendered: Optional[int] = Field(
        default=None,
        description="The non-competitive tendered value on the security from FIMAs.",
        alias="fimaNoncompetitiveTendered",
    )
    first_interest_period: Optional[str] = Field(
        default=None,
        description="The first interest period of the security.",
        alias="firstInterestPeriod",
    )
    first_interest_payment_date: Optional[dateType] = Field(
        default=None,
        description="The first interest payment date of the security.",
        alias="firstInterestPaymentDate",
    )
    floating_rate: Literal["Yes", "No", None] = Field(
        default=None,
        description="Whether the security is a floating rate.",
        alias="floatingRate",
    )
    frn_index_determination_date: Optional[dateType] = Field(
        default=None,
        description="The FRN index determination date of the security.",
        alias="frnIndexDeterminationDate",
    )
    frn_index_determination_rate: Optional[float] = Field(
        default=None,
        description="The FRN index determination rate of the security.",
        alias="frnIndexDeterminationRate",
    )
    high_discount_rate: Optional[float] = Field(
        default=None,
        description="The high discount rate of the security.",
        alias="highDiscountRate",
    )
    high_investment_rate: Optional[float] = Field(
        default=None,
        description="The high investment rate of the security.",
        alias="highInvestmentRate",
    )
    high_price: Optional[float] = Field(
        default=None,
        description="The high price of the security at auction.",
        alias="highPrice",
    )
    high_discount_margin: Optional[float] = Field(
        default=None,
        description="The high discount margin of the security.",
    )
    high_yield: Optional[float] = Field(
        default=None,
        description="The high yield of the security at auction.",
        alias="highYield",
    )
    index_ratio_on_issue_date: Optional[float] = Field(
        default=None,
        description="The index ratio on the issue date of the security.",
        alias="indexRatioOnIssueDate",
    )
    indirect_bidder_accepted: Optional[int] = Field(
        default=None,
        description="The accepted value from indirect bidders on the security.",
        alias="indirectBidderAccepted",
    )
    indirect_bidder_tendered: Optional[int] = Field(
        default=None,
        description="The tendered value from indirect bidders on the security.",
        alias="indirectBidderTendered",
    )
    interest_payment_frequency: Optional[str] = Field(
        default=None,
        description="The interest payment frequency of the security.",
        alias="interestPaymentFrequency",
    )
    low_discount_rate: Optional[float] = Field(
        default=None,
        description="The low discount rate of the security.",
        alias="lowDiscountRate",
    )
    low_investment_rate: Optional[float] = Field(
        default=None,
        description="The low investment rate of the security.",
        alias="lowInvestmentRate",
    )
    low_price: Optional[float] = Field(
        default=None,
        description="The low price of the security at auction.",
        alias="lowPrice",
    )
    low_discount_margin: Optional[float] = Field(
        default=None,
        description="The low discount margin of the security.",
        alias="lowDiscountMargin",
    )
    low_yield: Optional[float] = Field(
        default=None,
        description="The low yield of the security at auction.",
        alias="lowYield",
    )
    maturing_date: Optional[dateType] = Field(
        default=None,
        description="The maturing date of the security.",
        alias="maturingDate",
    )
    max_competitive_award: Optional[int] = Field(
        default=None,
        description="The maximum competitive award at auction.",
        alias="maximumCompetitiveAward",
    )
    max_non_competitive_award: Optional[int] = Field(
        default=None,
        description="The maximum non-competitive award at auction.",
        alias="maximumNoncompetitiveAward",
    )
    max_single_bid: Optional[int] = Field(
        default=None,
        description="The maximum single bid at auction.",
        alias="maximumSingleBid",
    )
    min_bid_amount: Optional[int] = Field(
        default=None,
        description="The minimum bid amount at auction.",
        alias="minimumBidAmount",
    )
    min_strip_amount: Optional[int] = Field(
        default=None,
        description="The minimum strip amount at auction.",
        alias="minimumStripAmount",
    )
    min_to_issue: Optional[int] = Field(
        default=None,
        description="The minimum to issue at auction.",
        alias="minimumToIssue",
    )
    multiples_to_bid: Optional[int] = Field(
        default=None,
        description="The multiples to bid at auction.",
        alias="multiplesToBid",
    )
    multiples_to_issue: Optional[int] = Field(
        default=None,
        description="The multiples to issue at auction.",
        alias="multiplesToIssue",
    )
    nlp_exclusion_amount: Optional[int] = Field(
        default=None,
        description="The NLP exclusion amount at auction.",
        alias="nlpExclusionAmount",
    )
    nlp_reporting_threshold: Optional[int] = Field(
        default=None,
        description="The NLP reporting threshold at auction.",
    )
    non_competitive_accepted: Optional[int] = Field(
        default=None,
        description="The accepted value from non-competitive bidders on the security.",
        alias="noncompetitiveAccepted",
    )
    non_competitive_tenders_accepted: Optional[Literal["Yes", "No", None]] = Field(
        default=None,
        description="Whether or not the auction accepted non-competitive tenders.",
        alias="noncompetitiveTendersAccepted",
    )
    offering_amount: Optional[int] = Field(
        default=None,
        description="The offering amount at auction.",
        alias="offeringAmount",
    )
    original_cusip: Optional[str] = Field(
        default=None,
        description="The original CUSIP of the security.",
        alias="originalCusip",
    )
    original_dated_date: Optional[dateType] = Field(
        default=None,
        description="The original dated date of the security.",
        alias="originalDatedDate",
    )
    original_issue_date: Optional[dateType] = Field(
        default=None,
        description="The original issue date of the security.",
        alias="originalIssueDate",
    )
    original_security_term: Optional[str] = Field(
        default=None,
        description="The original term of the security.",
        alias="originalSecurityTerm",
    )
    pdf_announcement: Optional[str] = Field(
        default=None,
        description="The PDF filename for the announcement of the security.",
        alias="pdfFilenameAnnouncement",
    )
    pdf_competitive_results: Optional[str] = Field(
        default=None,
        description="The PDF filename for the competitive results of the security.",
        alias="pdfFilenameCompetitiveResults",
    )
    pdf_non_competitive_results: Optional[str] = Field(
        default=None,
        description="The PDF filename for the non-competitive results of the security.",
        alias="pdfFilenameNoncompetitiveResults",
    )
    pdf_special_announcement: Optional[str] = Field(
        default=None,
        description="The PDF filename for the special announcements.",
        alias="pdfFilenameSpecialAnnouncement",
    )
    price_per_100: Optional[float] = Field(
        default=None,
        description="The price per 100 of the security.",
        alias="pricePer100",
    )
    primary_dealer_accepted: Optional[int] = Field(
        default=None,
        description="The primary dealer accepted value on the security.",
        alias="primaryDealerAccepted",
    )
    primary_dealer_tendered: Optional[int] = Field(
        default=None,
        description="The primary dealer tendered value on the security.",
        alias="primaryDealerTendered",
    )
    reopening: Optional[Literal["Yes", "No", None]] = Field(
        default=None,
        description="Whether or not the auction was reopened.",
    )
    security_term_day_month: Optional[str] = Field(
        default=None,
        description="The security term in days or months.",
        alias="securityTermDayMonth",
    )
    security_term_week_year: Optional[str] = Field(
        default=None,
        description="The security term in weeks or years.",
        alias="securityTermWeekYear",
    )
    series: Optional[str] = Field(
        default=None,
        description="The series name of the security.",
    )
    soma_accepted: Optional[int] = Field(
        default=None,
        description="The SOMA accepted value on the security.",
        alias="somaAccepted",
    )
    soma_holdings: Optional[int] = Field(
        default=None,
        description="The SOMA holdings on the security.",
        alias="somaHoldings",
    )
    soma_included: Optional[Literal["Yes", "No", None]] = Field(
        default=None,
        description="Whether or not the SOMA (System Open Market Account) was included on the security.",
        alias="somaIncluded",
    )
    soma_tendered: Optional[int] = Field(
        default=None,
        description="The SOMA tendered value on the security.",
        alias="somaTendered",
    )
    spread: Optional[float] = Field(
        default=None,
        description="The spread on the security.",
    )
    standard_payment_per_1000: Optional[float] = Field(
        default=None,
        description="The standard payment per 1000 of the security.",
        alias="standardInterestPaymentPer1000",
    )
    strippable: Optional[Literal["Yes", "No", None]] = Field(
        default=None,
        description="Whether or not the security is strippable.",
    )
    term: Optional[str] = Field(
        default=None,
        description="The term of the security.",
    )
    tiin_conversion_factor_per_1000: Optional[float] = Field(
        default=None,
        description="The TIIN conversion factor per 1000 of the security.",
        alias="tiinConversionFactorPer1000",
    )
    tips: Optional[Literal["Yes", "No", None]] = Field(
        default=None,
        description="Whether or not the security is TIPS.",
    )
    total_accepted: Optional[int] = Field(
        default=None,
        description="The total accepted value at auction.",
        alias="totalAccepted",
    )
    total_tendered: Optional[int] = Field(
        default=None,
        description="The total tendered value at auction.",
        alias="totalTendered",
    )
    treasury_retail_accepted: Optional[int] = Field(
        default=None,
        description="The accepted value on the security from retail.",
        alias="treasuryRetailAccepted",
    )
    treasury_retail_tenders_accepted: Optional[Literal["Yes", "No", None]] = Field(
        default=None,
        description="Whether or not the tender offers from retail are accepted",
        alias="treasuryRetailTendersAccepted",
    )
    type: Optional[str] = Field(
        default=None,
        description="The type of issuance.  This might be different than the security type.",
    )
    unadjusted_accrued_interest_per_1000: Optional[float] = Field(
        default=None,
        description="The unadjusted accrued interest per 1000 of the security.",
        alias="unadjustedAccruedInterestPer1000",
    )
    unadjusted_price: Optional[float] = Field(
        default=None,
        description="The unadjusted price of the security.",
        alias="unadjustedPrice",
    )
    updated_timestamp: Optional[datetime] = Field(
        default=None,
        description="The updated timestamp of the security.",
        alias="updatedTimestamp",
    )
    xml_announcement: Optional[str] = Field(
        default=None,
        description="The XML filename for the announcement of the security.",
        alias="xmlFilenameAnnouncement",
    )
    xml_competitive_results: Optional[str] = Field(
        default=None,
        description="The XML filename for the competitive results of the security.",
        alias="xmlFilenameCompetitiveResults",
    )
    xml_special_announcement: Optional[str] = Field(
        default=None,
        description="The XML filename for special announcements.",
        alias="xmlFilenameSpecialAnnouncement",
    )
    tint_cusip1: Optional[str] = Field(
        default=None, description="Tint CUSIP 1.", alias="tintCusip1"
    )
    tint_cusip2: Optional[str] = Field(
        default=None,
        description="Tint CUSIP 2.",
    )
