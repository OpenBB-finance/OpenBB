"""FMP Balance Sheet Growth Model."""

# pylint: disable=unused-argument

from typing import Any, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.balance_sheet_growth import (
    BalanceSheetGrowthData,
    BalanceSheetGrowthQueryParams,
)
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from openbb_fmp.utils.definitions import FinancialPeriods
from pydantic import Field


class FMPBalanceSheetGrowthQueryParams(BalanceSheetGrowthQueryParams):
    """FMP Balance Sheet Growth Query.

    Source: https://site.financialmodelingprep.com/developer/docs#balance-sheet-statement-growth
    """

    period: FinancialPeriods = Field(
        default="annual",
        description=QUERY_DESCRIPTIONS.get("period", ""),
    )
    limit: Optional[int] = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("limit", "") + " (default 5)"
    )


class FMPBalanceSheetGrowthData(BalanceSheetGrowthData):
    """FMP Balance Sheet Growth Data."""

    __alias_dict__ = {
        "period_ending": "date",
        "fiscal_year": "calendarYear",
        "fiscal_period": "period",
        "currency": "reportedCurrency",
        "growth_other_total_shareholders_equity": "growthOthertotalStockholdersEquity",
        "growth_total_shareholders_equity": "growthTotalStockholdersEquity",
        "growth_total_liabilities_and_shareholders_equity": "growthTotalLiabilitiesAndStockholdersEquity",
        "growth_accumulated_other_comprehensive_income": "growthAccumulatedOtherComprehensiveIncomeLoss",
        "growth_prepaid_expenses": "growthPrepaids",
    }

    symbol: str = Field(description=DATA_DESCRIPTIONS.get("symbol", ""))
    reported_currency: Optional[str] = Field(
        description="The currency in which the financial data is reported.",
        default=None,
    )
    growth_cash_and_cash_equivalents: Optional[float] = Field(
        default=None,
        description="Growth rate of cash and cash equivalents.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_short_term_investments: Optional[float] = Field(
        default=None,
        description="Growth rate of short-term investments.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_cash_and_short_term_investments: Optional[float] = Field(
        default=None,
        description="Growth rate of cash and short-term investments.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_accounts_receivables: Optional[float] = Field(
        default=None,
        description="Growth rate of accounts receivable.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_other_receivables: Optional[float] = Field(
        default=None,
        description="Growth rate of other receivables.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_net_receivables: Optional[float] = Field(
        default=None,
        description="Growth rate of net receivables.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_inventory: Optional[float] = Field(
        default=None,
        description="Growth rate of inventory.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_other_current_assets: Optional[float] = Field(
        default=None,
        description="Growth rate of other current assets.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_total_current_assets: Optional[float] = Field(
        default=None,
        description="Growth rate of total current assets.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_property_plant_equipment_net: Optional[float] = Field(
        description="Growth rate of net property, plant, and equipment.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_goodwill: Optional[float] = Field(
        description="Growth rate of goodwill.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_intangible_assets: Optional[float] = Field(
        description="Growth rate of intangible assets.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_goodwill_and_intangible_assets: Optional[float] = Field(
        description="Growth rate of goodwill and intangible assets.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_long_term_investments: Optional[float] = Field(
        default=None,
        description="Growth rate of long-term investments.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_tax_assets: Optional[float] = Field(
        default=None,
        description="Growth rate of tax assets.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_other_non_current_assets: Optional[float] = Field(
        default=None,
        description="Growth rate of other non-current assets.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_total_non_current_assets: Optional[float] = Field(
        default=None,
        description="Growth rate of total non-current assets.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_other_assets: Optional[float] = Field(
        default=None,
        description="Growth rate of other assets.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_total_assets: Optional[float] = Field(
        default=None,
        description="Growth rate of total assets.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_account_payables: Optional[float] = Field(
        default=None,
        description="Growth rate of accounts payable.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_other_payables: Optional[float] = Field(
        default=None,
        description="Growth rate of other payables.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_total_payables: Optional[float] = Field(
        default=None,
        description="Growth rate of total payables.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_accrued_expenses: Optional[float] = Field(
        default=None,
        description="Growth rate of accrued expenses.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_prepaid_expenses: Optional[float] = Field(
        default=None,
        description="Growth rate of prepaid expenses.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_capital_lease_obligations_current: Optional[float] = Field(
        default=None,
        description="Growth rate of current capital lease obligations.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_short_term_debt: Optional[float] = Field(
        default=None,
        description="Growth rate of short-term debt.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_tax_payables: Optional[float] = Field(
        default=None,
        description="Growth rate of tax payables.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_deferred_tax_liabilities_non_current: Optional[float] = Field(
        default=None,
        description="Growth rate of non-current deferred tax liabilities.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_deferred_revenue: Optional[float] = Field(
        default=None,
        description="Growth rate of deferred revenue.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_other_current_liabilities: Optional[float] = Field(
        default=None,
        description="Growth rate of other current liabilities.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_total_current_liabilities: Optional[float] = Field(
        default=None,
        description="Growth rate of total current liabilities.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_deferred_revenue_non_current: Optional[float] = Field(
        default=None,
        description="Growth rate of non-current deferred revenue.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_long_term_debt: Optional[float] = Field(
        default=None,
        description="Growth rate of long-term debt.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_deferrred_tax_liabilities_non_current: Optional[float] = Field(
        default=None,
        description="Growth rate of non-current deferred tax liabilities.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_other_non_current_liabilities: Optional[float] = Field(
        default=None,
        description="Growth rate of other non-current liabilities.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_total_non_current_liabilities: Optional[float] = Field(
        default=None,
        description="Growth rate of total non-current liabilities.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_other_liabilities: Optional[float] = Field(
        description="Growth rate of other liabilities.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_total_liabilities: Optional[float] = Field(
        description="Growth rate of total liabilities.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_retained_earnings: Optional[float] = Field(
        description="Growth rate of retained earnings.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_accumulated_other_comprehensive_income: Optional[float] = Field(
        description="Growth rate of accumulated other comprehensive income/loss.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_minority_interest: Optional[float] = Field(
        default=None,
        description="Growth rate of minority interest.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_additional_paid_in_capital: Optional[float] = Field(
        default=None,
        description="Growth rate of additional paid-in capital.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_other_total_shareholders_equity: Optional[float] = Field(
        default=None,
        description="Growth rate of other total stockholders' equity.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_total_shareholders_equity: Optional[float] = Field(
        default=None,
        description="Growth rate of total stockholders' equity.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_common_stock: Optional[float] = Field(
        description="Growth rate of common stock.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_preferred_stock: Optional[float] = Field(
        description="Growth rate of preferred stock.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_treasury_stock: Optional[float] = Field(
        default=None,
        description="Growth rate of treasury stock.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_total_equity: Optional[float] = Field(
        default=None,
        description="Growth rate of total equity.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_total_liabilities_and_shareholders_equity: Optional[float] = Field(
        default=None,
        description="Growth rate of total liabilities and stockholders' equity.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_total_investments: Optional[float] = Field(
        default=None,
        description="Growth rate of total investments.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_total_debt: Optional[float] = Field(
        default=None,
        description="Growth rate of total debt.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_net_debt: Optional[float] = Field(
        default=None,
        description="Growth rate of net debt.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )


class FMPBalanceSheetGrowthFetcher(
    Fetcher[
        FMPBalanceSheetGrowthQueryParams,
        list[FMPBalanceSheetGrowthData],
    ]
):
    """FMP Balance Sheet Growth Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> FMPBalanceSheetGrowthQueryParams:
        """Transform the query params."""
        return FMPBalanceSheetGrowthQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: FMPBalanceSheetGrowthQueryParams,
        credentials: Optional[dict[str, str]],
        **kwargs: Any,
    ) -> list[dict]:
        """Return the raw data from the FMP endpoint."""
        # pylint: disable=import-outside-toplevel
        from openbb_fmp.utils.helpers import get_data_many

        api_key = credentials.get("fmp_api_key") if credentials else ""

        url = (
            "https://financialmodelingprep.com/stable/balance-sheet-statement-growth"
            + f"?symbol={query.symbol}"
            + f"&period={query.period}"
            + f"&limit={query.limit if query.limit else 5}"
            + f"&apikey={api_key}"
        )

        return await get_data_many(url, **kwargs)

    @staticmethod
    def transform_data(
        query: FMPBalanceSheetGrowthQueryParams, data: list[dict], **kwargs: Any
    ) -> list[FMPBalanceSheetGrowthData]:
        """Return the transformed data."""
        return [FMPBalanceSheetGrowthData.model_validate(d) for d in data]
