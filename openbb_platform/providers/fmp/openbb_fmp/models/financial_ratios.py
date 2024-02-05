"""FMP Financial Ratios Model."""

from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.financial_ratios import (
    FinancialRatiosData,
    FinancialRatiosQueryParams,
)
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.helpers import (
    amake_requests,
    to_snake_case,
)
from pydantic import Field, model_validator


class FMPFinancialRatiosQueryParams(FinancialRatiosQueryParams):
    """FMP Financial Ratios Query.

    Source: https://financialmodelingprep.com/developer/docs/#Company-Financial-Ratios
    """

    period: Literal["annual", "quarter", "ttm"] = Field(
        default="annual", description=QUERY_DESCRIPTIONS.get("period", "")
    )


class FMPFinancialRatiosData(FinancialRatiosData):
    """FMP Financial Ratios Data."""

    __alias_dict__ = {
        "dividend_yield_ttm": "dividend_yiel_ttm",
        "dividend_yield_ttm_percent": "dividend_yiel_percentage_ttm",
        "period_ending": "date",
        "fiscal_period": "period",
        "fiscal_year": "calendar_year",
        "price_to_book": "price_to_book_ratio",
        "price_to_sales": "price_sales_ratio",
        "price_to_earnings": "price_earnings_ratio",
        "price_to_cash_flow": "price_cash_flow_ratio",
        "price_to_operating_cash_flow": "price_to_operating_cash_flows_ratio",
        "price_to_free_cash_flow": "price_to_free_cash_flows_ratio",
        "pe_to_growth": "price_earnings_to_growth_ratio",
        "debt_to_equity": "debt_equity_ratio",
        "cash_flow_to_debt": "cash_flow_to_debt_ratio",
        "operating_cash_flow_to_sales": "operating_cash_flow_sales_ratio",
        "free_cash_flow_to_operating_cash_flow": "free_cash_flow_operating_cash_flow_ratio",
        "short_term_coverage_ratio": "short_term_coverage_ratios",
        "cash_flow_coverage_ratio": "cash_flow_coverage_ratios",
        "gross_margin": "gross_profit_margin",
        "operating_margin": "operating_profit_margin",
        "pre_tax_income_margin": "pretax_profit_margin",
        "return_on_invested_capital": "return_on_capital_employed",
    }

    dividend_yield: Optional[float] = Field(
        default=None,
        description="Dividend yield, as a normalized percent.",
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
    )
    dividend_per_share: Optional[float] = Field(
        default=None, description="Dividend per share."
    )
    cash_per_share: Optional[float] = Field(default=None, description="Cash per share.")
    operating_cash_flow_per_share: Optional[float] = Field(
        default=None, description="Operating cash flow per share."
    )
    free_cash_flow_per_share: Optional[float] = Field(
        default=None, description="Free cash flow per share."
    )
    enterprise_value_multiple: Optional[float] = Field(
        default=None, description="Enterprise value multiple."
    )
    price_fair_value: Optional[float] = Field(
        default=None, description="Price fair value."
    )
    price_to_book: Optional[float] = Field(
        default=None, description="Price to book ratio."
    )
    price_to_sales: Optional[float] = Field(
        default=None, description="Price to sales ratio."
    )
    price_to_earnings: Optional[float] = Field(
        default=None, description="Price to earnings ratio."
    )
    price_to_operating_cash_flow: Optional[float] = Field(
        default=None, description="Price to operating cash flows ratio."
    )
    price_to_cash_flow: Optional[float] = Field(
        default=None, description="Price cash flow ratio."
    )
    price_to_free_cash_flow: Optional[float] = Field(
        default=None, description="Price to free cash flow ratio."
    )
    price_to_sales: Optional[float] = Field(
        default=None, description="Price sales ratio."
    )
    pe_to_growth: Optional[float] = Field(
        default=None, description="PE to growth ratio."
    )
    current_ratio: Optional[float] = Field(default=None, description="Current ratio.")
    quick_ratio: Optional[float] = Field(default=None, description="Quick ratio.")
    cash_ratio: Optional[float] = Field(default=None, description="Cash ratio.")
    days_of_sales_outstanding: Optional[float] = Field(
        default=None, description="Days of sales outstanding."
    )
    days_of_inventory_outstanding: Optional[float] = Field(
        default=None, description="Days of inventory outstanding."
    )
    operating_cycle: Optional[float] = Field(
        default=None, description="Operating cycle."
    )
    days_of_payables_outstanding: Optional[float] = Field(
        default=None, description="Days of payables outstanding."
    )
    cash_conversion_cycle: Optional[float] = Field(
        default=None, description="Cash conversion cycle."
    )
    receivables_turnover: Optional[float] = Field(
        default=None, description="Receivables turnover."
    )
    payables_turnover: Optional[float] = Field(
        default=None, description="Payables turnover."
    )
    inventory_turnover: Optional[float] = Field(
        default=None, description="Inventory turnover."
    )
    fixed_asset_turnover: Optional[float] = Field(
        default=None, description="Fixed asset turnover."
    )
    asset_turnover: Optional[float] = Field(default=None, description="Asset turnover.")
    debt_ratio: Optional[float] = Field(default=None, description="Debt ratio.")
    debt_to_equity: Optional[float] = Field(
        default=None, description="Debt equity ratio."
    )
    long_term_debt_to_capitalization: Optional[float] = Field(
        default=None, description="Long term debt to capitalization."
    )
    total_debt_to_capitalization: Optional[float] = Field(
        default=None, description="Total debt to capitalization."
    )
    cash_flow_to_debt: Optional[float] = Field(
        default=None, description="Cash flow to debt ratio."
    )
    ebit_per_revenue: Optional[float] = Field(
        default=None, description="EBIT per revenue."
    )
    ebt_per_ebit: Optional[float] = Field(default=None, description="EBT per EBIT.")
    net_income_per_ebt: Optional[float] = Field(
        default=None, description="Net income per EBT."
    )
    operating_cash_flow_to_sales: Optional[float] = Field(
        default=None, description="Operating cash flow sales ratio."
    )
    free_cash_flow_to_operating_cash_flow: Optional[float] = Field(
        default=None, description="Free cash flow operating cash flow ratio."
    )
    cash_flow_coverage_ratio: Optional[float] = Field(
        default=None, description="Cash flow coverage ratios."
    )
    short_term_coverage_ratio: Optional[float] = Field(
        default=None, description="Short term coverage ratio."
    )
    capital_expenditure_coverage_ratio: Optional[float] = Field(
        default=None, description="Capital expenditure coverage ratio."
    )
    dividend_paid_and_capex_coverage_ratio: Optional[float] = Field(
        default=None, description="Dividend paid and capex coverage ratio."
    )
    interest_coverage: Optional[float] = Field(
        default=None, description="Interest coverage."
    )
    gross_margin: Optional[float] = Field(
        default=None,
        description="Gross profit, as a normalized percent.",
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
    )
    operating_margin: Optional[float] = Field(
        default=None,
        description="Operating margin, as a normalized percent.",
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
    )
    pre_tax_income_margin: Optional[float] = Field(
        default=None,
        description="Pre tax income margin, as a normalized percent.",
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
    )
    net_profit_margin: Optional[float] = Field(
        default=None,
        description="Net profit margin, as a normalized percent.",
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
    )
    effective_tax_rate: Optional[float] = Field(
        default=None,
        description="Effective tax rate, as a normalized percent.",
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
    )
    return_on_assets: Optional[float] = Field(
        default=None,
        description="Return on assets, as a normalized percent.",
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
    )
    return_on_equity: Optional[float] = Field(
        default=None,
        description="Return on equity, as a normalized percent.",
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
    )
    return_on_invested_capital: Optional[float] = Field(
        default=None,
        description="Return on invested capital, as a normalized percent.",
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
    )
    company_equity_multiplier: Optional[float] = Field(
        default=None, description="Company equity multiplier."
    )
    dividend_payout_ratio: Optional[float] = Field(
        default=None, description="Dividend payout ratio."
    )
    payout_ratio: Optional[float] = Field(default=None, description="Payout ratio.")

    @model_validator(mode="before")
    @classmethod
    def replace_zero(cls, values):  # pylint: disable=no-self-argument
        """Check for zero values and replace with None."""
        return (
            {k: None if v == 0 else v for k, v in values.items()}
            if isinstance(values, dict)
            else values
        )


class FMPFinancialRatiosFetcher(
    Fetcher[
        FMPFinancialRatiosQueryParams,
        List[FMPFinancialRatiosData],
    ]
):
    """Transform the query, extract and transform the data from the FMP endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FMPFinancialRatiosQueryParams:
        """Transform the query params."""
        return FMPFinancialRatiosQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: FMPFinancialRatiosQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the FMP endpoint."""
        api_key = credentials.get("fmp_api_key") if credentials else ""

        base_url = "https://financialmodelingprep.com/api/v3"

        ttm_url = f"{base_url}/ratios-ttm/{query.symbol}?&apikey={api_key}"

        url = (
            f"{base_url}/ratios/{query.symbol}?"
            f"period={query.period}&limit={query.limit}&apikey={api_key}"
            if query.period != "ttm"
            else ttm_url
        )
        results = await amake_requests(url, **kwargs)

        return results

    @staticmethod
    def transform_data(
        query: FMPFinancialRatiosQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[FMPFinancialRatiosData]:
        """Return the transformed data."""
        results: List[FMPFinancialRatiosData] = []

        if query.period == "ttm":
            data[0].update(
                {"period": "TTM", "date": datetime.now().date().strftime("%Y-%m-%d")},
            )
        for item in data:
            new_item = {to_snake_case(k).replace("ttm", ""): v for k, v in item.items()}
            # FMP duplicates quite a few fields for some reason.
            new_item.pop("symbol", None)
            new_item.pop("dividend_yiel_percentage", None)
            new_item.pop("price_to_sales_ratio", None)
            new_item.pop("price_book_value_ratio", None)
            results.append(FMPFinancialRatiosData.model_validate(new_item))

        return results
