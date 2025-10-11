"""FMP Cash Flow Statement Growth Model."""

# pylint: disable=unused-argument

from typing import Any

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.cash_flow_growth import (
    CashFlowStatementGrowthData,
    CashFlowStatementGrowthQueryParams,
)
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from openbb_fmp.utils.definitions import FinancialPeriods
from pydantic import Field


class FMPCashFlowStatementGrowthQueryParams(CashFlowStatementGrowthQueryParams):
    """FMP Cash Flow Statement Growth Query.

    Source: https://site.financialmodelingprep.com/developer/docs#cashflow-statement-growth
    """

    period: FinancialPeriods = Field(
        default="annual",
        description=QUERY_DESCRIPTIONS.get("period", ""),
    )


class FMPCashFlowStatementGrowthData(CashFlowStatementGrowthData):
    """FMP Cash Flow Statement Growth Data."""

    __alias_dict__ = {
        "period_ending": "date",
        "fiscal_year": "calendarYear",
        "fiscal_period": "period",
        "reported_currency": "reportedCurrency",
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
        "growth_net_cash_from_financing_activities": "growthNetCashUsedProvidedByFinancingActivities",
        "growth_net_equity_issuance": "growthNetStockIssuance",
        "growth_common_equity_issuance": "growthCommonStockIssued",
        "growth_common_equity_repurchased": "growthCommonStockRepurchased",
    }
    symbol: str = Field(description=DATA_DESCRIPTIONS.get("symbol", ""))
    reported_currency: str | None = Field(
        description="The currency in which the financial data is reported.",
        default=None,
    )
    growth_net_income: float | None = Field(
        default=None,
        description="Growth rate of net income.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_depreciation_and_amortization: float | None = Field(
        default=None,
        description="Growth rate of depreciation and amortization.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_deferred_income_tax: float | None = Field(
        default=None,
        description="Growth rate of deferred income tax.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_stock_based_compensation: float | None = Field(
        default=None,
        description="Growth rate of stock-based compensation.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_change_in_working_capital: float | None = Field(
        default=None,
        description="Growth rate of change in working capital.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_account_receivables: float | None = Field(
        default=None,
        description="Growth rate of accounts receivables.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_inventory: float | None = Field(
        default=None,
        description="Growth rate of inventory.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_account_payable: float | None = Field(
        default=None,
        description="Growth rate of account payable.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_other_working_capital: float | None = Field(
        default=None,
        description="Growth rate of other working capital.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_other_non_cash_items: float | None = Field(
        default=None,
        description="Growth rate of other non-cash items.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_net_cash_from_operating_activities: float | None = Field(
        default=None,
        description="Growth rate of net cash provided by operating activities.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_purchase_of_property_plant_and_equipment: float | None = Field(
        default=None,
        description="Growth rate of investments in property, plant, and equipment.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_acquisitions: float | None = Field(
        default=None,
        description="Growth rate of net acquisitions.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_purchase_of_investment_securities: float | None = Field(
        default=None,
        description="Growth rate of purchases of investments.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_sale_and_maturity_of_investments: float | None = Field(
        default=None,
        description="Growth rate of sales maturities of investments.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_other_investing_activities: float | None = Field(
        default=None,
        description="Growth rate of other investing activities.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_net_cash_from_investing_activities: float | None = Field(
        default=None,
        description="Growth rate of net cash used for investing activities.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_short_term_net_debt_issuance: float | None = Field(
        default=None,
        description="Growth rate of short term net debt issuance.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_long_term_net_debt_issuance: float | None = Field(
        default=None,
        description="Growth rate of long term net debt issuance.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_net_debt_issuance: float | None = Field(
        default=None,
        description="Growth rate of net debt issuance.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_repayment_of_debt: float | None = Field(
        default=None,
        description="Growth rate of debt repayment.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_common_equity_issuance: float | None = Field(
        default=None,
        description="Growth rate of common equity issued.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_common_equity_repurchased: float | None = Field(
        default=None,
        description="Growth rate of common equity repurchased.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_net_equity_issuance: float | None = Field(
        default=None,
        description="Growth rate of net equity issuance.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_dividends_paid: float | None = Field(
        default=None,
        description="Growth rate of dividends paid.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_preferred_dividends_paid: float | None = Field(
        default=None,
        description="Growth rate of preferred dividends paid.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_other_financing_activities: float | None = Field(
        default=None,
        description="Growth rate of other financing activities.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_net_cash_from_financing_activities: float | None = Field(
        default=None,
        description="Growth rate of net cash used/provided by financing activities.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_effect_of_exchange_rate_changes_on_cash: float | None = Field(
        default=None,
        description="Growth rate of the effect of foreign exchange changes on cash.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_net_change_in_cash_and_equivalents: float | None = Field(
        default=None,
        description="Growth rate of net change in cash.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_cash_at_beginning_of_period: float | None = Field(
        default=None,
        description="Growth rate of cash at the beginning of the period.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_cash_at_end_of_period: float | None = Field(
        default=None,
        description="Growth rate of cash at the end of the period.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_operating_cash_flow: float | None = Field(
        default=None,
        description="Growth rate of operating cash flow.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_capital_expenditure: float | None = Field(
        default=None,
        description="Growth rate of capital expenditure.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_income_taxes_paid: float | None = Field(
        default=None,
        description="Growth rate of income taxes paid.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_interest_paid: float | None = Field(
        default=None,
        description="Growth rate of interest paid.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_free_cash_flow: float | None = Field(
        default=None,
        description="Growth rate of free cash flow.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )


class FMPCashFlowStatementGrowthFetcher(
    Fetcher[
        FMPCashFlowStatementGrowthQueryParams,
        list[FMPCashFlowStatementGrowthData],
    ]
):
    """FMP Cash Flow Statement Growth Fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> FMPCashFlowStatementGrowthQueryParams:
        """Transform the query params."""
        return FMPCashFlowStatementGrowthQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: FMPCashFlowStatementGrowthQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Transform the query, extract and transform the data from the FMP endpoints."""
        # pylint: disable=import-outside-toplevel
        from openbb_fmp.utils.helpers import get_data_many

        api_key = credentials.get("fmp_api_key") if credentials else ""

        url = (
            "https://financialmodelingprep.com/stable/cash-flow-statement-growth"
            + f"?symbol={query.symbol}"
            + f"&period={query.period}"
            + f"&limit={query.limit if query.limit else 5}"
            + f"&apikey={api_key}"
        )

        return await get_data_many(url, **kwargs)

    @staticmethod
    def transform_data(
        query: FMPCashFlowStatementGrowthQueryParams, data: list[dict], **kwargs: Any
    ) -> list[FMPCashFlowStatementGrowthData]:
        """Return the transformed data."""
        return [FMPCashFlowStatementGrowthData.model_validate(d) for d in data]
