"""FMP Financial Ratios Model."""

# pylint: disable=unused-argument

from datetime import datetime
from typing import Any, Literal

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.financial_ratios import (
    FinancialRatiosData,
    FinancialRatiosQueryParams,
)
from openbb_core.provider.utils.errors import EmptyDataError
from openbb_fmp.utils.definitions import FinancialPeriods
from pydantic import ConfigDict, Field


class FMPFinancialRatiosQueryParams(FinancialRatiosQueryParams):
    """FMP Financial Ratios Query.

    Source: https://site.financialmodelingprep.com/developer/docs#metrics-ratios
    """

    __json_schema_extra__ = {"symbol": {"multiple_items_allowed": True}}

    ttm: Literal["include", "exclude", "only"] = Field(
        default="only",
        description="Specify whether to include, exclude, or only show TTM (Trailing Twelve Months) data."
        + " The default is 'only'.",
    )
    period: FinancialPeriods = Field(
        default="annual",
        description="Specify the fiscal period for the data.",
    )
    limit: int | None = Field(
        default=None,
        description="Only applicable when TTM is not set to 'only'."
        + " Defines the number of most recent reporting periods to return."
        + " The default is 5.",
        ge=1,
    )


class FMPFinancialRatiosData(FinancialRatiosData):
    """FMP Financial Ratios Data."""

    model_config = ConfigDict(extra="ignore")

    __alias_dict__ = {
        "currency": "reportedCurrency",
        "period_ending": "date",
        "fiscal_period": "period",
        "price_to_earnings": "priceToEarningsRatio",
        "price_to_earnings_growth": "priceToEarningsGrowthRatio",
        "forward_price_to_earnings_growth": "forwardPriceToEarningsGrowthRatio",
        "price_to_book": "priceToBookRatio",
        "price_to_sales": "priceToSalesRatio",
        "price_to_free_cash_flow": "priceToFreeCashFlowRatio",
        "price_to_operating_cash_flow": "priceToOperatingCashFlowRatio",
        "debt_to_assets": "debtToAssetsRatio",
        "debt_to_equity": "debtToEquityRatio",
        "debt_to_capital": "debtToCapitalRatio",
        "debt_to_market_cap": "debtToMarketCap",
        "long_term_debt_to_capital": "longTermDebtToCapitalRatio",
        "net_income_per_ebt": "netIncomePerEBT",
        "ebt_per_ebit": "ebtPerEbit",
        "price_to_fair_value": "priceToFairValue",
        "effective_tax_rate": "effectiveTaxRate",
        "enterprise_value_multiple": "enterpriseValueMultiple",
        "gross_profit_margin": "grossProfitMargin",
        "ebit_margin": "ebitMargin",
        "ebitda_margin": "ebitdaMargin",
        "operating_profit_margin": "operatingProfitMargin",
        "pretax_profit_margin": "pretaxProfitMargin",
        "continuous_operations_profit_margin": "continuousOperationsProfitMargin",
        "net_profit_margin": "netProfitMargin",
        "bottom_line_profit_margin": "bottomLineProfitMargin",
        "receivables_turnover": "receivablesTurnover",
        "payables_turnover": "payablesTurnover",
        "inventory_turnover": "inventoryTurnover",
        "fixed_asset_turnover": "fixedAssetTurnover",
        "asset_turnover": "assetTurnover",
        "current_ratio": "currentRatio",
        "quick_ratio": "quickRatio",
        "solvency_ratio": "solvencyRatio",
        "cash_ratio": "cashRatio",
        "financial_leverage_ratio": "financialLeverageRatio",
        "working_capital_turnover_ratio": "workingCapitalTurnoverRatio",
        "operating_cash_flow_ratio": "operatingCashFlowRatio",
        "operating_cash_flow_sales_ratio": "operatingCashFlowSalesRatio",
        "free_cash_flow_operating_cash_flow_ratio": "freeCashFlowOperatingCashFlowRatio",
        "debt_service_coverage_ratio": "debtServiceCoverageRatio",
        "interest_coverage_ratio": "interestCoverageRatio",
        "short_term_operating_cash_flow_coverage_ratio": "shortTermOperatingCashFlowCoverageRatio",
        "operating_cash_flow_coverage_ratio": "operatingCashFlowCoverageRatio",
        "capital_expenditure_coverage_ratio": "capitalExpenditureCoverageRatio",
        "dividend_paid_and_capex_coverage_ratio": "dividendPaidAndCapexCoverageRatio",
        "dividend_payout_ratio": "dividendPayoutRatio",
        "dividend_yield": "dividendYield",
        "revenue_per_share": "revenuePerShare",
        "net_income_per_share": "netIncomePerShare",
        "interest_debt_per_share": "interestDebtPerShare",
        "cash_per_share": "cashPerShare",
        "book_value_per_share": "bookValuePerShare",
        "tangible_book_value_per_share": "tangibleBookValuePerShare",
        "shareholders_equity_per_share": "shareholdersEquityPerShare",
        "operating_cash_flow_per_share": "operatingCashFlowPerShare",
        "capex_per_share": "capexPerShare",
        "free_cash_flow_per_share": "freeCashFlowPerShare",
        "dividend_per_share": "dividendPerShare",
    }

    currency: str | None = Field(
        default=None,
        description="Currency in which the company reports financials.",
    )
    gross_profit_margin: float | None = Field(
        default=None,
        description="Gross profit margin.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
        alias="grossProfitMarginTTM",
    )
    ebit_margin: float | None = Field(
        default=None,
        description="Earnings before interest and taxes (EBIT) margin.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
        title="EBIT Margin",
        alias="ebitMarginTTM",
    )
    ebitda_margin: float | None = Field(
        default=None,
        description="Earnings before interest, taxes, depreciation, and amortization (EBITDA) margin.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
        title="EBITDA Margin",
        alias="ebitdaMarginTTM",
    )
    operating_profit_margin: float | None = Field(
        default=None,
        description="Operating profit margin.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
        alias="operatingProfitMarginTTM",
    )
    pretax_profit_margin: float | None = Field(
        default=None,
        description="Pretax profit margin.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
        alias="pretaxProfitMarginTTM",
    )
    continuous_operations_profit_margin: float | None = Field(
        default=None,
        description="Continuous operations profit margin.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
        alias="continuousOperationsProfitMarginTTM",
    )
    net_profit_margin: float | None = Field(
        default=None,
        description="Net profit margin.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
        alias="netProfitMarginTTM",
    )
    bottom_line_profit_margin: float | None = Field(
        default=None,
        description="Bottom line profit margin.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
        alias="bottomLineProfitMarginTTM",
    )
    receivables_turnover: float | None = Field(
        default=None,
        description="Receivables turnover ratio.",
        alias="receivablesTurnoverTTM",
    )
    payables_turnover: float | None = Field(
        default=None,
        description="Payables turnover ratio.",
        alias="payablesTurnoverTTM",
    )
    inventory_turnover: float | None = Field(
        default=None,
        description="Inventory turnover ratio.",
        alias="inventoryTurnoverTTM",
    )
    fixed_asset_turnover: float | None = Field(
        default=None,
        description="Fixed asset turnover ratio.",
        alias="fixedAssetTurnoverTTM",
    )
    asset_turnover: float | None = Field(
        default=None, description="Asset turnover ratio.", alias="assetTurnoverTTM"
    )
    current_ratio: float | None = Field(
        default=None, description="Current ratio.", alias="currentRatioTTM"
    )
    quick_ratio: float | None = Field(
        default=None, description="Quick ratio.", alias="quickRatioTTM"
    )
    solvency_ratio: float | None = Field(
        default=None, description="Solvency ratio.", alias="solvencyRatioTTM"
    )
    cash_ratio: float | None = Field(
        default=None, description="Cash ratio.", alias="cashRatioTTM"
    )
    price_to_earnings: float | None = Field(
        default=None,
        description="Price to earnings (P/E) ratio.",
        title="P/E",
        alias="priceToEarningsRatioTTM",
    )
    price_to_earnings_growth: float | None = Field(
        default=None,
        description="Price to earnings growth (PEG) ratio.",
        title="PEG",
        alias="priceToEarningsGrowthRatioTTM",
    )
    forward_price_to_earnings_growth: float | None = Field(
        default=None,
        description="Forward price to earnings growth (PEG) ratio.",
        title="Forward PEG",
        alias="forwardPriceToEarningsGrowthRatioTTM",
    )
    price_to_book: float | None = Field(
        default=None,
        description="Price to book (P/B) ratio.",
        title="P/B",
        alias="priceToBookRatioTTM",
    )
    price_to_sales: float | None = Field(
        default=None,
        description="Price to sales (P/S) ratio.",
        title="P/S",
        alias="priceToSalesRatioTTM",
    )
    price_to_free_cash_flow: float | None = Field(
        default=None,
        description="Price to free cash flow (P/FCF) ratio.",
        title="P/FCF",
        alias="priceToFreeCashFlowRatioTTM",
    )
    price_to_operating_cash_flow: float | None = Field(
        default=None,
        description="Price to operating cash flow (P/OCF) ratio.",
        title="P/OCF",
        alias="priceToOperatingCashFlowRatioTTM",
    )
    debt_to_assets: float | None = Field(
        default=None, description="Debt to assets ratio.", alias="debtToAssetsRatioTTM"
    )
    debt_to_equity: float | None = Field(
        default=None, description="Debt to equity ratio.", alias="debtToEquityRatioTTM"
    )
    debt_to_capital: float | None = Field(
        default=None,
        description="Debt to capital ratio.",
        alias="debtToCapitalRatioTTM",
    )
    long_term_debt_to_capital: float | None = Field(
        default=None,
        description="Long-term debt to capital ratio.",
        alias="longTermDebtToCapitalRatioTTM",
    )
    financial_leverage_ratio: float | None = Field(
        default=None,
        description="Financial leverage ratio.",
        alias="financialLeverageRatioTTM",
    )
    working_capital_turnover_ratio: float | None = Field(
        default=None,
        description="Working capital turnover ratio.",
        alias="workingCapitalTurnoverRatioTTM",
    )
    operating_cash_flow_ratio: float | None = Field(
        default=None,
        description="Operating cash flow ratio.",
        alias="operatingCashFlowRatioTTM",
    )
    operating_cash_flow_sales_ratio: float | None = Field(
        default=None,
        description="Operating cash flow to sales ratio.",
        alias="operatingCashFlowSalesRatioTTM",
    )
    free_cash_flow_operating_cash_flow_ratio: float | None = Field(
        default=None,
        description="Free cash flow to operating cash flow ratio.",
        title="FCF/OCF",
        alias="freeCashFlowOperatingCashFlowRatioTTM",
    )
    debt_service_coverage_ratio: float | None = Field(
        default=None,
        description="Debt service coverage ratio.",
        alias="debtServiceCoverageRatioTTM",
    )
    interest_coverage_ratio: float | None = Field(
        default=None,
        description="Interest coverage ratio.",
        alias="interestCoverageRatioTTM",
    )
    short_term_operating_cash_flow_coverage_ratio: float | None = Field(
        default=None,
        description="Short-term operating cash flow coverage ratio.",
        alias="shortTermOperatingCashFlowCoverageRatioTTM",
    )
    operating_cash_flow_coverage_ratio: float | None = Field(
        default=None,
        description="Operating cash flow coverage ratio.",
        alias="operatingCashFlowCoverageRatioTTM",
    )
    capital_expenditure_coverage_ratio: float | None = Field(
        default=None,
        description="Capital expenditure coverage ratio.",
        alias="capitalExpenditureCoverageRatioTTM",
    )
    dividend_paid_and_capex_coverage_ratio: float | None = Field(
        default=None,
        description="Dividend paid and capital expenditure coverage ratio.",
        alias="dividendPaidAndCapexCoverageRatioTTM",
    )
    dividend_payout_ratio: float | None = Field(
        default=None,
        description="Dividend payout ratio.",
        alias="dividendPayoutRatioTTM",
    )
    dividend_yield: float | None = Field(
        default=None,
        description="Dividend yield.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
        alias="dividendYieldTTM",
    )
    dividend_per_share: float | None = Field(
        default=None, description="Dividend per share.", alias="dividendPerShareTTM"
    )
    revenue_per_share: float | None = Field(
        default=None, description="Revenue per share.", alias="revenuePerShareTTM"
    )
    net_income_per_share: float | None = Field(
        default=None, description="Net income per share.", alias="netIncomePerShareTTM"
    )
    interest_debt_per_share: float | None = Field(
        default=None,
        description="Interest-bearing debt per share.",
        alias="interestDebtPerShareTTM",
    )
    cash_per_share: float | None = Field(
        default=None, description="Cash per share.", alias="cashPerShareTTM"
    )
    book_value_per_share: float | None = Field(
        default=None, description="Book value per share.", alias="bookValuePerShareTTM"
    )
    tangible_book_value_per_share: float | None = Field(
        default=None,
        description="Tangible book value per share.",
        alias="tangibleBookValuePerShareTTM",
    )
    shareholders_equity_per_share: float | None = Field(
        default=None,
        description="Shareholders' equity per share.",
        alias="shareholdersEquityPerShareTTM",
    )
    operating_cash_flow_per_share: float | None = Field(
        default=None,
        description="Operating cash flow per share.",
        alias="operatingCashFlowPerShareTTM",
    )
    capex_per_share: float | None = Field(
        default=None,
        description="Capital expenditure per share.",
        alias="capexPerShareTTM",
    )
    free_cash_flow_per_share: float | None = Field(
        default=None,
        description="Free cash flow per share.",
        title="FCF/Share",
        alias="freeCashFlowPerShareTTM",
    )
    net_income_per_ebt: float | None = Field(
        default=None,
        description="Net income per earnings before tax (EBT).",
        title="Net Income/EBT",
        alias="netIncomePerEBTTTM",
    )
    ebt_per_ebit: float | None = Field(
        default=None,
        description="Earnings before tax (EBT) per earnings before interest and tax (EBIT).",
        title="EBT/EBIT",
        alias="ebtPerEbitTTM",
    )
    price_to_fair_value: float | None = Field(
        default=None,
        description="Price to fair value ratio.",
        alias="priceToFairValueTTM",
    )
    debt_to_market_cap: float | None = Field(
        default=None,
        description="Debt to market capitalization ratio.",
        alias="debtToMarketCapTTM",
    )
    effective_tax_rate: float | None = Field(
        default=None,
        description="Effective tax rate.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
        alias="effectiveTaxRateTTM",
    )
    enterprise_value_multiple: float | None = Field(
        default=None,
        description="Enterprise value multiple (EV/EBITDA).",
        alias="enterpriseValueMultipleTTM",
    )


class FMPFinancialRatiosFetcher(
    Fetcher[
        FMPFinancialRatiosQueryParams,
        list[FMPFinancialRatiosData],
    ]
):
    """FMP Financial Ratios Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> FMPFinancialRatiosQueryParams:
        """Transform the query params."""
        return FMPFinancialRatiosQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: FMPFinancialRatiosQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list:
        """Return the raw data from the FMP endpoint."""
        # pylint: disable=import-outside-toplevel
        import asyncio  # noqa
        import warnings
        from openbb_fmp.utils.helpers import get_data_many

        api_key = credentials.get("fmp_api_key") if credentials else ""
        symbols = query.symbol.split(",")
        results: list = []
        base_url: str = "https://financialmodelingprep.com/stable/ratios"

        async def get_one(symbol):
            """Get data for one symbol."""
            ttm = f"{base_url}-ttm?symbol={symbol}&apikey={api_key}"
            limit = query.limit if query.ttm != "only" else 1
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
                ttm_result["date"] = datetime.today().date().strftime("%Y-%m-%d")
                ttm_result["fiscal_period"] = "TTM"
                ttm_result["fiscal_year"] = datetime.today().year
                if currency:
                    ttm_result["reportedCurrency"] = currency
                result.insert(0, ttm_result)

            if not result:
                warnings.warn(f"Symbol Error: No data found for {symbol}.")

            if not result:
                warnings.warn(f"Symbol Error: No data found for {symbol}.")

            if result:
                results.extend(result)

        await asyncio.gather(*[get_one(symbol) for symbol in symbols])

        if not results:
            raise EmptyDataError("No data found for given symbols.")

        return results

    @staticmethod
    def transform_data(
        query: FMPFinancialRatiosQueryParams, data: list, **kwargs: Any
    ) -> list[FMPFinancialRatiosData]:
        """Return the transformed data."""
        return [
            FMPFinancialRatiosData.model_validate(d)
            for d in sorted(data, key=lambda x: x["date"], reverse=True)
        ]
