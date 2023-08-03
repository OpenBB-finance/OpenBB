"""FMP Balance Sheet Growth Fetcher."""


from datetime import datetime
from typing import Any, Dict, List, Optional

from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.models.balance_sheet_growth import (
    BalanceSheetGrowthData,
    BalanceSheetGrowthQueryParams,
)
from pydantic import validator

from openbb_fmp.utils.helpers import create_url, get_data_many


class FMPBalanceSheetGrowthQueryParams(BalanceSheetGrowthQueryParams):
    """FMP Balance Sheet Growth QueryParams.

    Source:  https://site.financialmodelingprep.com/developer/docs/#Financial-Statements-Growth
    """


class FMPBalanceSheetGrowthData(BalanceSheetGrowthData):
    """FMP Balance Sheet Growth Data."""

    class Config:
        fields = {
            "growth_cash_and_cash_equivalents": "growthCashAndCashEquivalents",
            "growth_short_term_investments": "growthShortTermInvestments",
            "growth_cash_and_short_term_investments": "growthCashAndShortTermInvestments",
            "growth_net_receivables": "growthNetReceivables",
            "growth_inventory": "growthInventory",
            "growth_other_current_assets": "growthOtherCurrentAssets",
            "growth_total_current_assets": "growthTotalCurrentAssets",
            "growth_property_plant_equipment_net": "growthPropertyPlantEquipmentNet",
            "growth_goodwill": "growthGoodwill",
            "growth_intangible_assets": "growthIntangibleAssets",
            "growth_goodwill_and_intangible_assets": "growthGoodwillAndIntangibleAssets",
            "growth_long_term_investments": "growthLongTermInvestments",
            "growth_tax_assets": "growthTaxAssets",
            "growth_other_non_current_assets": "growthOtherNonCurrentAssets",
            "growth_total_non_current_assets": "growthTotalNonCurrentAssets",
            "growth_other_assets": "growthOtherAssets",
            "growth_total_assets": "growthTotalAssets",
            "growth_account_payables": "growthAccountPayables",
            "growth_short_term_debt": "growthShortTermDebt",
            "growth_tax_payables": "growthTaxPayables",
            "growth_deferred_revenue": "growthDeferredRevenue",
            "growth_other_current_liabilities": "growthOtherCurrentLiabilities",
            "growth_total_current_liabilities": "growthTotalCurrentLiabilities",
            "growth_long_term_debt": "growthLongTermDebt",
            "growth_deferred_revenue_non_current": "growthDeferredRevenueNonCurrent",
            "growth_deferrred_tax_liabilities_non_current": "growthDeferrredTaxLiabilitiesNonCurrent",
            "growth_other_non_current_liabilities": "growthOtherNonCurrentLiabilities",
            "growth_total_non_current_liabilities": "growthTotalNonCurrentLiabilities",
            "growth_other_liabilities": "growthOtherLiabilities",
            "growth_total_liabilities": "growthTotalLiabilities",
            "growth_common_stock": "growthCommonStock",
            "growth_retained_earnings": "growthRetainedEarnings",
            "growth_accumulated_other_comprehensive_income_loss": "growthAccumulatedOtherComprehensiveIncomeLoss",
            "growth_othertotal_stockholders_equity": "growthOthertotalStockholdersEquity",
            "growth_total_stockholders_equity": "growthTotalStockholdersEquity",
            "growth_total_liabilities_and_stockholders_equity": "growthTotalLiabilitiesAndStockholdersEquity",
            "growth_total_investments": "growthTotalInvestments",
            "growth_total_debt": "growthTotalDebt",
            "growth_net_debt": "growthNetDebt",
        }

    @validator("date", pre=True, check_fields=False)
    def date_validate(cls, v):  # pylint: disable=E0213
        return datetime.strptime(v, "%Y-%m-%d")


class FMPBalanceSheetGrowthFetcher(
    Fetcher[
        BalanceSheetGrowthQueryParams,
        BalanceSheetGrowthData,
        FMPBalanceSheetGrowthQueryParams,
        FMPBalanceSheetGrowthData,
    ]
):
    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FMPBalanceSheetGrowthQueryParams:
        return FMPBalanceSheetGrowthQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FMPBalanceSheetGrowthQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[FMPBalanceSheetGrowthData]:
        api_key = credentials.get("fmp_api_key") if credentials else ""

        url = create_url(
            3,
            f"balance-sheet-statement-growth/{query.symbol}",
            api_key,
            query,
            ["symbol"],
        )
        return get_data_many(url, FMPBalanceSheetGrowthData)

    @staticmethod
    def transform_data(
        data: List[FMPBalanceSheetGrowthData],
    ) -> List[FMPBalanceSheetGrowthData]:
        return data
