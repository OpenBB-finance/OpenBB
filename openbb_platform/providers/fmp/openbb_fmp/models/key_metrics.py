"""FMP Equity Valuation Multiples Model."""

# pylint: disable=unused-argument

from datetime import datetime
from typing import Any, Literal

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.key_metrics import (
    KeyMetricsData,
    KeyMetricsQueryParams,
)
from openbb_core.provider.utils.errors import EmptyDataError
from openbb_fmp.utils.definitions import FinancialPeriods
from pydantic import Field


class FMPKeyMetricsQueryParams(KeyMetricsQueryParams):
    """FMP Equity Valuation Multiples Query.

    Source: https://site.financialmodelingprep.com/developer/docs#key-metrics
    """

    __json_schema_extra__ = {"symbol": {"multiple_items_allowed": True}}

    ttm: Literal["include", "exclude", "only"] = Field(
        default="only",
        description="Specify whether to include, exclude, or only show TTM (Trailing Twelve Months) data."
        + " The default is 'only'.",
    )
    period: FinancialPeriods = Field(
        default="annual",
        description="Specify the fiscal period for the data. Ignored when TTM is set to 'only'.",
    )
    limit: int | None = Field(
        default=None,
        description="Only applicable when TTM is not set to 'only'."
        + " Defines the number of most recent reporting periods to return."
        + " The default is 5.",
    )


class FMPKeyMetricsData(KeyMetricsData):
    """FMP Equity Valuation Multiples Data."""

    __alias_dict__ = {
        "period_ending": "date",
        "fiscal_period": "period",
        "currency": "reportedCurrency",
        "enterprise_value": "enterpriseValueTTM",
        "ev_to_sales": "evToSalesTTM",
        "ev_to_operating_cash_flow": "evToOperatingCashFlowTTM",
        "ev_to_free_cash_flow": "evToFreeCashFlowTTM",
        "ev_to_ebitda": "evToEBITDATTM",
        "net_debt_to_ebitda": "netDebtToEBITDATTM",
        "current_ratio": "currentRatioTTM",
        "income_quality": "incomeQualityTTM",
        "graham_number": "grahamNumberTTM",
        "graham_net_net": "grahamNetNetTTM",
        "tax_burden": "taxBurdenTTM",
        "interest_burden": "interestBurdenTTM",
        "working_capital": "workingCapitalTTM",
        "invested_capital": "investedCapitalTTM",
        "return_on_assets": "returnOnAssetsTTM",
        "operating_return_on_assets": "operatingReturnOnAssetsTTM",
        "return_on_tangible_assets": "returnOnTangibleAssetsTTM",
        "return_on_equity": "returnOnEquityTTM",
        "return_on_invested_capital": "returnOnInvestedCapitalTTM",
        "return_on_capital_employed": "returnOnCapitalEmployedTTM",
        "earnings_yield": "earningsYieldTTM",
        "free_cash_flow_yield": "freeCashFlowYieldTTM",
        "capex_to_operating_cash_flow": "capexToOperatingCashFlowTTM",
        "capex_to_depreciation": "capexToDepreciationTTM",
        "capex_to_revenue": "capexToRevenueTTM",
        "sales_general_and_administrative_to_revenue": "salesGeneralAndAdministrativeToRevenueTTM",
        "research_and_developement_to_revenue": "researchAndDevelopementToRevenueTTM",
        "stock_based_compensation_to_revenue": "stockBasedCompensationToRevenueTTM",
        "intangibles_to_total_assets": "intangiblesToTotalAssetsTTM",
        "average_receivables": "averageReceivablesTTM",
        "average_payables": "averagePayablesTTM",
        "average_inventory": "averageInventoryTTM",
        "days_of_sales_outstanding": "daysOfSalesOutstandingTTM",
        "days_of_payables_outstanding": "daysOfPayablesOutstandingTTM",
        "days_of_inventory_outstanding": "daysOfInventoryOutstandingTTM",
        "operating_cycle": "operatingCycleTTM",
        "cash_conversion_cycle": "cashConversionCycleTTM",
        "free_cash_flow_to_equity": "freeCashFlowToEquityTTM",
        "free_cash_flow_to_firm": "freeCashFlowToFirmTTM",
        "tangible_asset_value": "tangibleAssetValueTTM",
        "net_current_asset_value": "netCurrentAssetValueTTM",
    }

    enterprise_value: int | float | None = Field(
        default=None, description="Enterprise Value."
    )
    ev_to_sales: float | None = Field(
        default=None, description="Enterprise Value to Sales ratio.", title="EV/Sales"
    )
    ev_to_operating_cash_flow: float | None = Field(
        default=None,
        description="Enterprise Value to Operating Cash Flow ratio.",
        title="EV/Operating Cash Flow",
    )
    ev_to_free_cash_flow: float | None = Field(
        default=None,
        description="Enterprise Value to Free Cash Flow ratio.",
        title="EV/Free Cash Flow",
    )
    ev_to_ebitda: float | None = Field(
        default=None,
        description="Enterprise Value to EBITDA ratio.",
        title="EV/EBITDA",
        alias="evToEBITDA",
    )
    net_debt_to_ebitda: float | None = Field(
        default=None,
        description="Net Debt to EBITDA ratio.",
        title="Net Debt/EBITDA",
        alias="netDebtToEBITDA",
    )
    current_ratio: float | None = Field(default=None, description="Current Ratio.")
    income_quality: float | None = Field(default=None, description="Income Quality.")
    graham_number: float | None = Field(default=None, description="Graham Number.")
    graham_net_net: float | None = Field(default=None, description="Graham Net Net.")
    tax_burden: float | None = Field(default=None, description="Tax Burden.")
    interest_burden: float | None = Field(default=None, description="Interest Burden.")
    working_capital: int | float | None = Field(
        default=None, description="Working Capital."
    )
    invested_capital: int | float | None = Field(
        default=None, description="Invested Capital."
    )
    return_on_assets: float | None = Field(
        default=None,
        description="Return on Assets.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    operating_return_on_assets: float | None = Field(
        default=None,
        description="Operating Return on Assets.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    return_on_tangible_assets: float | None = Field(
        default=None,
        description="Return on Tangible Assets.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    return_on_equity: float | None = Field(
        default=None,
        description="Return on Equity.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    return_on_invested_capital: float | None = Field(
        default=None,
        description="Return on Invested Capital.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    return_on_capital_employed: float | None = Field(
        default=None,
        description="Return on Capital Employed.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    earnings_yield: float | None = Field(
        default=None,
        description="Earnings Yield.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    free_cash_flow_yield: float | None = Field(
        default=None,
        description="Free Cash Flow Yield.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    capex_to_operating_cash_flow: float | None = Field(
        default=None, description="Capex to Operating Cash Flow."
    )
    capex_to_depreciation: float | None = Field(
        default=None, description="Capex to Depreciation."
    )
    capex_to_revenue: float | None = Field(
        default=None, description="Capex to Revenue."
    )
    sales_general_and_administrative_to_revenue: float | None = Field(
        default=None,
        description="Sales, General and Administrative to Revenue.",
        title="SG&A to Revenue",
    )
    research_and_developement_to_revenue: float | None = Field(
        default=None,
        description="Research and Development to Revenue.",
        title="R&D to Revenue",
    )
    stock_based_compensation_to_revenue: float | None = Field(
        default=None, description="Stock Based Compensation to Revenue."
    )
    intangibles_to_total_assets: float | None = Field(
        default=None, description="Intangibles to Total Assets."
    )
    average_receivables: int | float | None = Field(
        default=None, description="Average Receivables."
    )
    average_payables: int | float | None = Field(
        default=None, description="Average Payables."
    )
    average_inventory: int | float | None = Field(
        default=None, description="Average Inventory."
    )
    days_of_sales_outstanding: float | None = Field(
        default=None, description="Days of Sales Outstanding."
    )
    days_of_payables_outstanding: float | None = Field(
        default=None, description="Days of Payables Outstanding."
    )
    days_of_inventory_outstanding: float | None = Field(
        default=None, description="Days of Inventory Outstanding."
    )
    operating_cycle: float | None = Field(default=None, description="Operating Cycle.")
    cash_conversion_cycle: float | None = Field(
        default=None, description="Cash Conversion Cycle."
    )
    free_cash_flow_to_equity: float | None = Field(
        default=None, description="Free Cash Flow to Equity."
    )
    free_cash_flow_to_firm: float | None = Field(
        default=None, description="Free Cash Flow to Firm."
    )
    tangible_asset_value: int | float | None = Field(
        default=None, description="Tangible Asset Value."
    )
    net_current_asset_value: int | float | None = Field(
        default=None, description="Net Current Asset Value."
    )


class FMPKeyMetricsFetcher(
    Fetcher[
        FMPKeyMetricsQueryParams,
        list[FMPKeyMetricsData],
    ]
):
    """FMP Key Metrics Fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> FMPKeyMetricsQueryParams:
        """Transform the query params."""
        return FMPKeyMetricsQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: FMPKeyMetricsQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Return the raw data from the FMP endpoint."""
        # pylint: disable=import-outside-toplevel
        import asyncio  # noqa
        import warnings
        from openbb_fmp.utils.helpers import get_data_many

        api_key = credentials.get("fmp_api_key") if credentials else ""
        symbols = query.symbol.split(",")
        results: list = []
        base_url: str = "https://financialmodelingprep.com/stable/key-metrics"
        limit = query.limit if query.limit and query.ttm != "only" else 1

        async def get_one(symbol):
            """Get data for one symbol."""
            ttm = f"{base_url}-ttm?symbol={symbol}&apikey={api_key}"
            metrics = f"{base_url}?symbol={symbol}&period={query.period}&limit={limit}&apikey={api_key}"
            result: list = []
            ttm_data = await get_data_many(ttm, **kwargs)
            metrics_data = await get_data_many(metrics, **kwargs)
            currency = None

            if metrics_data:
                if query.ttm != "only":
                    result.extend(metrics_data)
                currency = metrics_data[0].get("reportedCurrency")

            if ttm_data and query.ttm != "exclude":
                ttm_result = ttm_data[0]
                ttm_result["date"] = datetime.today().date().isoformat()
                ttm_result["fiscal_period"] = "TTM"
                ttm_result["fiscal_year"] = datetime.today().year
                if currency:
                    ttm_result["reportedCurrency"] = currency
                result.insert(0, ttm_result)

            if not result:
                warnings.warn(f"Symbol Error: No data found for {symbol}.")

            if result:
                results.extend(result)

        tasks = [get_one(symbol) for symbol in symbols]

        await asyncio.gather(*tasks)

        if not results:
            raise EmptyDataError("No data found for given symbols.")

        return results

    @staticmethod
    def transform_data(
        query: FMPKeyMetricsQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[FMPKeyMetricsData]:
        """Return the transformed data."""
        return [
            FMPKeyMetricsData.model_validate(d)
            for d in sorted(data, key=lambda x: x["date"], reverse=True)
        ]
