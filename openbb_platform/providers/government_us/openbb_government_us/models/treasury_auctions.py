"""US Government Treasury Auctions Model."""

# pylint: disable=unused-argument

from typing import Any, Dict, List, Optional

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.treasury_auctions import (
    USTreasuryAuctionsData,
    USTreasuryAuctionsQueryParams,
)
from pydantic import model_validator


class GovernmentUSTreasuryAuctionsQueryParams(USTreasuryAuctionsQueryParams):
    """US Government Treasury Auctions Query.

    Source: https://www.treasurydirect.gov/
    """

    __alias_dict__ = {
        "security_type": "type",
        "page_size": "pagesize",
        "page_num": "pagenum",
        "start_date": "startDate",
        "end_date": "endDate",
    }


class GovernementUSTreasuryAuctionsData(USTreasuryAuctionsData):
    """US Government Treasury Auctions Data."""

    __alias_dict__ = {
        "issue_date": "issueDate",
        "security_type": "securityType",
        "security_term": "securityTerm",
        "maturity_date": "maturityDate",
        "interest_rate": "interestRate",
        "cpi_on_issue_date": "refCpiOnIssueDate",
        "cpi_on_dated_date": "refCpiOnDatedDate",
        "announcement_date": "announcementDate",
        "auction_date": "auctionDate",
        "auction_date_year": "auctionDateYear",
        "dated_date": "datedDate",
        "first_payment_date": "firstInterestPaymentDate",
        "accrued_interest_per_100": "accruedInterestPer100",
        "accrued_interest_per_1000": "accruedInterestPer1000",
        "adjusted_accrued_interest_per_100": "adjustedAccruedInterestPer100",
        "adjusted_accrued_interest_per_1000": "adjustedAccruedInterestPer1000",
        "adjusted_price": "adjustedPrice",
        "allocation_percentage": "allocationPercentage",
        "allocation_percentage_decimals": "allocationPercentageDecimals",
        "announced_cusip": "announcedCusip",
        "auction_format": "auctionFormat",
        "avg_median_discount_rate": "averageMedianDiscountRate",
        "avg_median_investment_rate": "averageMedianInvestmentRate",
        "avg_median_price": "averageMedianPrice",
        "avg_median_discount_margin": "averageMedianDiscountMargin",
        "avg_median_yield": "averageMedianYield",
        "back_dated": "backDated",
        "back_dated_date": "backDatedDate",
        "bid_to_cover_ratio": "bidToCoverRatio",
        "call_date": "callDate",
        "called_date": "calledDate",
        "cash_management_bill": "cashManagementBillCMB",
        "closing_time_competitive": "closingTimeCompetitive",
        "closing_time_non_competitive": "closingTimeNoncompetitive",
        "competitive_accepted": "competitiveAccepted",
        "competitive_accepted_decimals": "competitiveBidDecimals",
        "competitive_tendered": "competitiveTendered",
        "competitive_tenders_accepted": "competitiveTendersAccepted",
        "corp_us_cusip": "corpusCusip",
        "cpi_base_reference_period": "cpiBaseReferencePeriod",
        "currently_outstanding": "currentlyOutstanding",
        "direct_bidder_accepted": "directBidderAccepted",
        "direct_bidder_tendered": "directBidderTendered",
        "est_amount_of_publicly_held_maturing_security": "estimatedAmountOfPubliclyHeldMaturingSecuritiesByType",
        "fima_included": "fimaIncluded",
        "fima_non_competitive_accepted": "fimaNoncompetitiveAccepted",
        "fima_non_competitive_tendered": "fimaNoncompetitiveTendered",
        "first_interest_period": "firstInterestPeriod",
        "first_interest_payment_date": "firstInterestPaymentDate",
        "floating_rate": "floatingRate",
        "frn_index_determination_date": "frnIndexDeterminationDate",
        "frn_index_determination_rate": "frnIndexDeterminationRate",
        "high_discount_rate": "highDiscountRate",
        "high_investment_rate": "highInvestmentRate",
        "high_price": "highPrice",
        "high_discount_margin": "highDiscountMargin",
        "high_yield": "highYield",
        "index_ratio_on_issue_date": "indexRatioOnIssueDate",
        "indirect_bidder_accepted": "indirectBidderAccepted",
        "indirect_bidder_tendered": "indirectBidderTendered",
        "interest_payment_frequency": "interestPaymentFrequency",
        "low_discount_rate": "lowDiscountRate",
        "low_investment_rate": "lowInvestmentRate",
        "low_price": "lowPrice",
        "low_discount_margin": "lowDiscountMargin",
        "low_yield": "lowYield",
        "maturing_date": "maturingDate",
        "max_competitive_award": "maximumCompetitiveAward",
        "max_non_competitive_award": "maximumNoncompetitiveAward",
        "max_single_bid": "maximumSingleBid",
        "min_bid_amount": "minimumBidAmount",
        "min_strip_amount": "minimumStripAmount",
        "min_to_issue": "minimumToIssue",
        "multiples_to_bid": "multiplesToBid",
        "multiples_to_issue": "multiplesToIssue",
        "nlp_exclusion_amount": "nlpExclusionAmount",
        "nlp_reporting_threshold": "nlpReportingThreshold",
        "non_competitive_accepted": "noncompetitiveAccepted",
        "non_competitive_tenders_accepted": "noncompetitiveTendersAccepted",
        "offering_amount": "offeringAmount",
        "original_cusip": "originalCusip",
        "original_dated_date": "originalDatedDate",
        "original_issue_date": "originalIssueDate",
        "original_security_term": "originalSecurityTerm",
        "pdf_announcement": "pdfFilenameAnnouncement",
        "pdf_competitive_results": "pdfFilenameCompetitiveResults",
        "pdf_non_competitive_results": "pdfFilenameNoncompetitiveResults",
        "pdf_special_announcement": "pdfFilenameSpecialAnnouncement",
        "price_per_100": "pricePer100",
        "primary_dealer_accepted": "primaryDealerAccepted",
        "primary_dealer_tendered": "primaryDealerTendered",
        "security_term_day_month": "securityTermDayMonth",
        "security_term_week_year": "securityTermWeekYear",
        "soma_accepted": "somaAccepted",
        "soma_holdings": "somaHoldings",
        "soma_included": "somaIncluded",
        "soma_tendered": "somaTendered",
        "standard_payment_per_1000": "standardInterestPaymentPer1000",
        "tiin_conversion_factor_per_1000": "tiinConversionFactorPer1000",
        "total_accepted": "totalAccepted",
        "total_tendered": "totalTendered",
        "treasury_retail_accepted": "treasuryRetailAccepted",
        "treasury_retail_tenders_accepted": "treasuryRetailTendersAccepted",
        "unadjusted_accrued_interest_per_1000": "unadjustedAccruedInterestPer1000",
        "unadjusted_price": "unadjustedPrice",
        "updated_timestamp": "updatedTimestamp",
        "xml_announcement": "xmlFilenameAnnouncement",
        "xml_competitive_results": "xmlFilenameCompetitiveResults",
        "xml_special_announcement": "xmlFilenameSpecialAnnouncement",
        "tint_cusip1": "tintCusip1",
        "tint_cusip2": "tintCusip2",
    }

    @model_validator(mode="before")
    @classmethod
    def _normalize_percent(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize percent values."""
        for k, v in data.items():
            if (
                k.endswith("Rate")
                or k.endswith("Yield")
                or k.endswith("Margin")
                or k.endswith("Percentage")
                or "spread" in k.lower()
            ):
                if v not in ["Yes", "No", None, ""]:
                    data[k] = float(v) / 100 if v else None
                else:
                    data[k] = v if v in ["Yes", "No"] else None
        return data


class GovernmentUSTreasuryAuctionsFetcher(
    Fetcher[
        GovernmentUSTreasuryAuctionsQueryParams,
        List[GovernementUSTreasuryAuctionsData],
    ]
):
    """Transform the query, extract and transform the data from the us treasury endpoints."""

    @staticmethod
    def transform_query(
        params: Dict[str, Any]
    ) -> GovernmentUSTreasuryAuctionsQueryParams:
        """Transform query params."""
        return GovernmentUSTreasuryAuctionsQueryParams(**params)

    @staticmethod
    def extract_data(
        query: GovernmentUSTreasuryAuctionsQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Extract the raw data from Treasury Direct API."""
        # pylint: disable=import-outside-toplevel
        from pandas import DataFrame  # noqa
        from openbb_core.provider.utils.helpers import (
            get_querystring,
            make_request,
        )  # noqa

        base_url = "https://www.treasurydirect.gov/TA_WS/securities/search?"

        security_dict = {
            "bill": "Bill",
            "note": "Note",
            "bond": "Bond",
            "cmb": "CMB",
            "tips": "TIPS",
            "frn": "FRN",
        }

        _query = query.model_dump()
        _query["startDate"] = (
            _query["startDate"].strftime("%m/%d/%Y") if query.start_date else None
        )
        _query["endDate"] = (
            _query["endDate"].strftime("%m/%d/%Y") if _query["endDate"] else None
        )
        _query["type"] = security_dict.get(_query["type"], _query["type"])
        query_string = get_querystring(_query, [])

        url = base_url + query_string + "&format=json"
        r = make_request(url)
        if r.status_code != 200:
            raise OpenBBError(f"{r.status_code}")
        data = DataFrame(r.json())
        results = (
            data.fillna("N/A").replace("", None).replace("N/A", None).to_dict("records")
        )

        return results

    @staticmethod
    def transform_data(
        query: GovernmentUSTreasuryAuctionsQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> List[GovernementUSTreasuryAuctionsData]:
        """Transform the data."""
        return [GovernementUSTreasuryAuctionsData.model_validate(d) for d in data]
