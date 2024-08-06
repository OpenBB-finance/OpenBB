"""FMP Cash Flow Statement Growth Model."""

from typing import Any, Dict, List, Literal, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.cash_flow_growth import (
    CashFlowStatementGrowthData,
    CashFlowStatementGrowthQueryParams,
)
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from openbb_fmp.utils.helpers import create_url, get_data_many
from pydantic import Field


class FMPCashFlowStatementGrowthQueryParams(CashFlowStatementGrowthQueryParams):
    """FMP Cash Flow Statement Growth Query.

    Source: https://site.financialmodelingprep.com/developer/docs/financial-statements-growth-api/
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


class FMPCashFlowStatementGrowthData(CashFlowStatementGrowthData):
    """FMP Cash Flow Statement Growth Data."""

    __alias_dict__ = {
        "period_ending": "date",
        "fiscal_year": "calendarYear",
        "fiscal_period": "period",
        "growth_acquisitions": "growthAcquisitionsNet",
        "growth_sale_and_maturity_of_investments": "growthSalesMaturitiesOfInvestments",
        "growth_net_cash_from_operating_activities": "growthNetCashProvidedByOperatingActivites",
        "growth_other_investing_activities": "growthOtherInvestingActivites",
        "growth_net_cash_from_investing_activities": "growthNetCashUsedForInvestingActivites",
        "growth_other_financing_activities": "growthOtherFinancingActivites",
        "growth_purchase_of_investment_securities": "growthPurchasesOfInvestments",
        "growth_account_receivables": "growthAccountsReceivables",
        "growth_account_payable": "growthAccountsPayables",
        "growth_purchase_of_property_plant_and_equipment": "growthInvestmentsInPropertyPlantAndEquipment",
        "growth_repayment_of_debt": "growthDebtRepayment",
        "growth_net_change_in_cash_and_equivalents": "growthNetChangeInCash",
        "growth_effect_of_exchange_rate_changes_on_cash": "growthEffectOfForexChangesOnCash",
    }
    symbol: str = Field(description=DATA_DESCRIPTIONS.get("symbol", ""))
    growth_net_income: Optional[float] = Field(
        default=None,
        description="Growth rate of net income.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_depreciation_and_amortization: Optional[float] = Field(
        default=None,
        description="Growth rate of depreciation and amortization.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_deferred_income_tax: Optional[float] = Field(
        default=None,
        description="Growth rate of deferred income tax.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_stock_based_compensation: Optional[float] = Field(
        default=None,
        description="Growth rate of stock-based compensation.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_change_in_working_capital: Optional[float] = Field(
        default=None,
        description="Growth rate of change in working capital.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_account_receivables: Optional[float] = Field(
        default=None,
        description="Growth rate of accounts receivables.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_inventory: Optional[float] = Field(
        default=None,
        description="Growth rate of inventory.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_account_payable: Optional[float] = Field(
        default=None,
        description="Growth rate of account payable.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_other_working_capital: Optional[float] = Field(
        default=None,
        description="Growth rate of other working capital.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_other_non_cash_items: Optional[float] = Field(
        default=None,
        description="Growth rate of other non-cash items.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_net_cash_from_operating_activities: Optional[float] = Field(
        default=None,
        description="Growth rate of net cash provided by operating activities.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_purchase_of_property_plant_and_equipment: Optional[float] = Field(
        default=None,
        description="Growth rate of investments in property, plant, and equipment.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_acquisitions: Optional[float] = Field(
        default=None,
        description="Growth rate of net acquisitions.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_purchase_of_investment_securities: Optional[float] = Field(
        default=None,
        description="Growth rate of purchases of investments.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_sale_and_maturity_of_investments: Optional[float] = Field(
        default=None,
        description="Growth rate of sales maturities of investments.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_other_investing_activities: Optional[float] = Field(
        default=None,
        description="Growth rate of other investing activities.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_net_cash_from_investing_activities: Optional[float] = Field(
        default=None,
        description="Growth rate of net cash used for investing activities.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_repayment_of_debt: Optional[float] = Field(
        default=None,
        description="Growth rate of debt repayment.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_common_stock_issued: Optional[float] = Field(
        default=None,
        description="Growth rate of common stock issued.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_common_stock_repurchased: Optional[float] = Field(
        default=None,
        description="Growth rate of common stock repurchased.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_dividends_paid: Optional[float] = Field(
        default=None,
        description="Growth rate of dividends paid.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_other_financing_activities: Optional[float] = Field(
        default=None,
        description="Growth rate of other financing activities.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_net_cash_from_financing_activities: Optional[float] = Field(
        default=None,
        description="Growth rate of net cash used/provided by financing activities.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_effect_of_exchange_rate_changes_on_cash: Optional[float] = Field(
        default=None,
        description="Growth rate of the effect of foreign exchange changes on cash.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_net_change_in_cash_and_equivalents: Optional[float] = Field(
        default=None,
        description="Growth rate of net change in cash.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_cash_at_beginning_of_period: Optional[float] = Field(
        default=None,
        description="Growth rate of cash at the beginning of the period.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_cash_at_end_of_period: Optional[float] = Field(
        default=None,
        description="Growth rate of cash at the end of the period.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_operating_cash_flow: Optional[float] = Field(
        default=None,
        description="Growth rate of operating cash flow.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_capital_expenditure: Optional[float] = Field(
        default=None,
        description="Growth rate of capital expenditure.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_free_cash_flow: Optional[float] = Field(
        default=None,
        description="Growth rate of free cash flow.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )


class FMPCashFlowStatementGrowthFetcher(
    Fetcher[
        FMPCashFlowStatementGrowthQueryParams,
        List[FMPCashFlowStatementGrowthData],
    ]
):
    """FMP Cash Flow Statement Growth Fetcher."""

    @staticmethod
    def transform_query(
        params: Dict[str, Any]
    ) -> FMPCashFlowStatementGrowthQueryParams:
        """Transform the query params."""
        return FMPCashFlowStatementGrowthQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: FMPCashFlowStatementGrowthQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Transform the query, extract and transform the data from the FMP endpoints."""
        api_key = credentials.get("fmp_api_key") if credentials else ""

        url = create_url(
            3, f"cash-flow-statement-growth/{query.symbol}", api_key, query, ["symbol"]
        )

        return await get_data_many(url, **kwargs)

    @staticmethod
    def transform_data(
        query: FMPCashFlowStatementGrowthQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[FMPCashFlowStatementGrowthData]:
        """Return the transformed data."""
        return [FMPCashFlowStatementGrowthData.model_validate(d) for d in data]
