"""FMP Balance Sheet Growth Model."""

from typing import Any, Dict, List, Literal, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.balance_sheet_growth import (
    BalanceSheetGrowthData,
    BalanceSheetGrowthQueryParams,
)
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from openbb_fmp.utils.helpers import create_url, get_data_many
from pydantic import Field, model_validator


class FMPBalanceSheetGrowthQueryParams(BalanceSheetGrowthQueryParams):
    """FMP Balance Sheet Growth Query.

    Source:  https://site.financialmodelingprep.com/developer/docs/#Financial-Statements-Growth
    """

    __json_schema_extra__ = {
        "period": {
            "choices": ["annual", "quarter"],
        }
    }

    period: Literal["annual", "quarter"] = Field(
        default="annual",
        description=QUERY_DESCRIPTIONS.get("period", ""),
    )


class FMPBalanceSheetGrowthData(BalanceSheetGrowthData):
    """FMP Balance Sheet Growth Data."""

    __alias_dict__ = {
        "period_ending": "date",
        "fiscal_year": "calendarYear",
        "fiscal_period": "period",
        "growth_other_total_shareholders_equity": "growthOtherTotalStockholdersEquity",
        "growth_total_shareholders_equity": "growthTotalStockholdersEquity",
        "growth_total_liabilities_and_shareholders_equity": "growthTotalLiabilitiesAndStockholdersEquity",
        "growth_accumulated_other_comprehensive_income": "growthAccumulatedOtherComprehensiveIncomeLoss",
    }

    symbol: str = Field(description=DATA_DESCRIPTIONS.get("symbol", ""))
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
    growth_long_term_debt: Optional[float] = Field(
        default=None,
        description="Growth rate of long-term debt.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_deferred_revenue_non_current: Optional[float] = Field(
        default=None,
        description="Growth rate of non-current deferred revenue.",
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
    growth_common_stock: Optional[float] = Field(
        description="Growth rate of common stock.",
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

    @model_validator(mode="before")
    @classmethod
    def replace_zero(cls, values):
        """Check for zero values and replace with None."""
        return (
            {k: None if v == 0 else v for k, v in values.items()}
            if isinstance(values, dict)
            else values
        )


class FMPBalanceSheetGrowthFetcher(
    Fetcher[
        FMPBalanceSheetGrowthQueryParams,
        List[FMPBalanceSheetGrowthData],
    ]
):
    """FMP Balance Sheet Growth Fetcher."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FMPBalanceSheetGrowthQueryParams:
        """Transform the query params."""
        return FMPBalanceSheetGrowthQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: FMPBalanceSheetGrowthQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the FMP endpoint."""
        api_key = credentials.get("fmp_api_key") if credentials else ""

        url = create_url(
            3,
            f"balance-sheet-statement-growth/{query.symbol}",
            api_key,
            query,
            ["symbol"],
        )

        return await get_data_many(url, **kwargs)

    @staticmethod
    def transform_data(
        query: FMPBalanceSheetGrowthQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[FMPBalanceSheetGrowthData]:
        """Return the transformed data."""
        return [FMPBalanceSheetGrowthData.model_validate(d) for d in data]
