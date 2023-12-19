"""FMP Balance Sheet Model."""

from datetime import (
    date as dateType,
    datetime,
)
from typing import Any, Dict, List, Literal, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.balance_sheet import (
    BalanceSheetData,
    BalanceSheetQueryParams,
)
from openbb_fmp.utils.helpers import create_url, get_data_many
from pydantic import Field, model_validator


class FMPBalanceSheetQueryParams(BalanceSheetQueryParams):
    """FMP Balance Sheet Query.

    Source: https://financialmodelingprep.com/developer/docs/#Balance-Sheet
    """

    period: Optional[Literal["annual", "quarter"]] = Field(default="annual")


class FMPBalanceSheetData(BalanceSheetData):
    """FMP Balance Sheet Data."""

    __alias_dict__ = {
        "period_ending": "date",
        "fiscal_period": "period",
        "fiscal_year": "calendarYear",
        "filing_date": "fillingDate",
        "accepted_date": "acceptedDate",
        "currency": "reportedCurrency",
        "cash_and_cash_equivalents": "cashAndCashEquivalents",
        "short_term_investments": "shortTermInvestments",
        "cash_and_short_term_investments": "cashAndShortTermInvestments",
        "net_receivables": "netReceivables",
        "inventory": "inventories",
        "other_current_assets": "otherCurrentAssets",
        "total_current_assets": "totalCurrentAssets",
        "plant_property_equipment_net": "propertyPlantEquipmentNet",
        "goodwill": "goodwill",
        "intangible_assets": "intangibleAssets",
        "goodwill_and_intangible_assets": "goodwillAndIntangibleAssets",
        "long_term_investments": "longTermInvestments",
        "tax_assets": "taxAssets",
        "other_non_current_assets": "otherNonCurrentAssets",
        "non_current_assets": "totalNonCurrentAssets",
        "other_assets": "otherAssets",
        "total_assets": "totalAssets",
        "accounts_payable": "accountPayables",
        "short_term_debt": "shortTermDebt",
        "tax_payables": "taxPayables",
        "current_deferred_revenue": "deferredRevenue",
        "other_current_liabilities": "otherCurrentLiabilities",
        "total_current_liabilities": "totalCurrentLiabilities",
        "long_term_debt": "longTermDebt",
        "deferred_revenue_non_current": "deferredRevenueNonCurrent",
        "deferred_tax_liabilities_non_current": "deferredTaxLiabilitiesNonCurrent",
        "other_non_current_liabilities": "otherNonCurrentLiabilities",
        "total_non_current_liabilities": "totalNonCurrentLiabilities",
        "other_liabilities": "otherLiabilities",
        "capital_lease_obligations": "capitalLeaseObligations",
        "total_liabilities": "totalLiabilities",
        "preferred_stock": "preferredStock",
        "common_stock": "commonStock",
        "retained_earnings": "retainedEarnings",
        "accumulated_other_comprehensive_income": "accumulatedOtherComprehensiveIncomeLoss",
        "other_stock_holders_equity": "otherStockholdersEquity",
        "other_total_stock_holders_equity": "othertotalStockholdersEquity",
        "total_common_equity": "totalStockholdersEquity",
        "total_equity_non_controlling_interests": "totalEquity",
        "total_liabilities_shareholders_equity": "totalLiabilitiesAndStockholdersEquity",
        "minority_interest": "minorityInterest",
        "total_liabilities_and_total_equity": "totalLiabilitiesAndTotalEquity",
        "total_investments": "totalInvestments",
        "total_debt": "totalDebt",
        "net_debt": "netDebt",
        "link": "link",
        "final_link": "finalLink",
    }

    filing_date: Optional[dateType] = Field(
        default=None,
        description="The date when the filing was made.",
    )
    accepted_date: Optional[datetime] = Field(
        default=None,
        description="The date and time when the filing was accepted.",
    )

    @model_validator(mode="before")
    @classmethod
    def replace_zero(cls, values):  # pylint: disable=no-self-argument
        """Check for zero values and replace with None."""
        return {k: None if v == 0 else v for k, v in values.items()}


class FMPBalanceSheetFetcher(
    Fetcher[
        FMPBalanceSheetQueryParams,
        List[FMPBalanceSheetData],
    ]
):
    """Transform the query, extract and transform the data from the FMP endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FMPBalanceSheetQueryParams:
        """Transform the query params."""
        return FMPBalanceSheetQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: FMPBalanceSheetQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the FMP endpoint."""
        api_key = credentials.get("fmp_api_key") if credentials else ""

        url = create_url(
            3, f"balance-sheet-statement/{query.symbol}", api_key, query, ["symbol"]
        )

        return await get_data_many(url, **kwargs)

    @staticmethod
    def transform_data(
        query: FMPBalanceSheetQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[FMPBalanceSheetData]:
        """Return the transformed data."""
        for result in data:
            result.pop("symbol", None)
            result.pop("cik", None)
        return [FMPBalanceSheetData.model_validate(d) for d in data]
