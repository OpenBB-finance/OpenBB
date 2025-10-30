"""FMP Balance Sheet Growth Model."""

# pylint: disable=unused-argument

from typing import Any

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
    limit: int | None = Field(
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
    reported_currency: str | None = Field(
        description="The currency in which the financial data is reported.",
        default=None,
    )
    growth_cash_and_cash_equivalents: float | None = Field(
        default=None,
        description="Growth rate of cash and cash equivalents.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_short_term_investments: float | None = Field(
        default=None,
        description="Growth rate of short-term investments.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_cash_and_short_term_investments: float | None = Field(
        default=None,
        description="Growth rate of cash and short-term investments.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_accounts_receivables: float | None = Field(
        default=None,
        description="Growth rate of accounts receivable.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_other_receivables: float | None = Field(
        default=None,
        description="Growth rate of other receivables.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_net_receivables: float | None = Field(
        default=None,
        description="Growth rate of net receivables.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_inventory: float | None = Field(
        default=None,
        description="Growth rate of inventory.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_other_current_assets: float | None = Field(
        default=None,
        description="Growth rate of other current assets.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_total_current_assets: float | None = Field(
        default=None,
        description="Growth rate of total current assets.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_property_plant_equipment_net: float | None = Field(
        description="Growth rate of net property, plant, and equipment.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_goodwill: float | None = Field(
        description="Growth rate of goodwill.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_intangible_assets: float | None = Field(
        description="Growth rate of intangible assets.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_goodwill_and_intangible_assets: float | None = Field(
        description="Growth rate of goodwill and intangible assets.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_long_term_investments: float | None = Field(
        default=None,
        description="Growth rate of long-term investments.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_tax_assets: float | None = Field(
        default=None,
        description="Growth rate of tax assets.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_other_non_current_assets: float | None = Field(
        default=None,
        description="Growth rate of other non-current assets.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_total_non_current_assets: float | None = Field(
        default=None,
        description="Growth rate of total non-current assets.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_other_assets: float | None = Field(
        default=None,
        description="Growth rate of other assets.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_total_assets: float | None = Field(
        default=None,
        description="Growth rate of total assets.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_account_payables: float | None = Field(
        default=None,
        description="Growth rate of accounts payable.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_other_payables: float | None = Field(
        default=None,
        description="Growth rate of other payables.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_total_payables: float | None = Field(
        default=None,
        description="Growth rate of total payables.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_accrued_expenses: float | None = Field(
        default=None,
        description="Growth rate of accrued expenses.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_prepaid_expenses: float | None = Field(
        default=None,
        description="Growth rate of prepaid expenses.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_capital_lease_obligations_current: float | None = Field(
        default=None,
        description="Growth rate of current capital lease obligations.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_short_term_debt: float | None = Field(
        default=None,
        description="Growth rate of short-term debt.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_tax_payables: float | None = Field(
        default=None,
        description="Growth rate of tax payables.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_deferred_tax_liabilities_non_current: float | None = Field(
        default=None,
        description="Growth rate of non-current deferred tax liabilities.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_deferred_revenue: float | None = Field(
        default=None,
        description="Growth rate of deferred revenue.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_other_current_liabilities: float | None = Field(
        default=None,
        description="Growth rate of other current liabilities.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_total_current_liabilities: float | None = Field(
        default=None,
        description="Growth rate of total current liabilities.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_deferred_revenue_non_current: float | None = Field(
        default=None,
        description="Growth rate of non-current deferred revenue.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_long_term_debt: float | None = Field(
        default=None,
        description="Growth rate of long-term debt.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_deferrred_tax_liabilities_non_current: float | None = Field(
        default=None,
        description="Growth rate of non-current deferred tax liabilities.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_other_non_current_liabilities: float | None = Field(
        default=None,
        description="Growth rate of other non-current liabilities.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_total_non_current_liabilities: float | None = Field(
        default=None,
        description="Growth rate of total non-current liabilities.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_other_liabilities: float | None = Field(
        description="Growth rate of other liabilities.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_total_liabilities: float | None = Field(
        description="Growth rate of total liabilities.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_retained_earnings: float | None = Field(
        description="Growth rate of retained earnings.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_accumulated_other_comprehensive_income: float | None = Field(
        description="Growth rate of accumulated other comprehensive income/loss.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_minority_interest: float | None = Field(
        default=None,
        description="Growth rate of minority interest.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_additional_paid_in_capital: float | None = Field(
        default=None,
        description="Growth rate of additional paid-in capital.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_other_total_shareholders_equity: float | None = Field(
        default=None,
        description="Growth rate of other total stockholders' equity.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_total_shareholders_equity: float | None = Field(
        default=None,
        description="Growth rate of total stockholders' equity.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_common_stock: float | None = Field(
        description="Growth rate of common stock.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_preferred_stock: float | None = Field(
        description="Growth rate of preferred stock.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_treasury_stock: float | None = Field(
        default=None,
        description="Growth rate of treasury stock.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_total_equity: float | None = Field(
        default=None,
        description="Growth rate of total equity.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_total_liabilities_and_shareholders_equity: float | None = Field(
        default=None,
        description="Growth rate of total liabilities and stockholders' equity.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_total_investments: float | None = Field(
        default=None,
        description="Growth rate of total investments.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_total_debt: float | None = Field(
        default=None,
        description="Growth rate of total debt.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_net_debt: float | None = Field(
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
        credentials: dict[str, str] | None,
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
