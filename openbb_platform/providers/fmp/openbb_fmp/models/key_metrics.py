"""FMP Key Metrics Model."""

# pylint: disable=unused-argument

import asyncio
from datetime import (
    date as dateType,
    datetime,
)
from typing import Any, Dict, List, Literal, Optional
from warnings import warn

from openbb_core.provider.abstract.data import ForceInt
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.key_metrics import (
    KeyMetricsData,
    KeyMetricsQueryParams,
)
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError
from openbb_core.provider.utils.helpers import amake_request
from openbb_fmp.utils.helpers import response_callback
from pydantic import Field


class FMPKeyMetricsQueryParams(KeyMetricsQueryParams):
    """FMP Key Metrics Query.

    Source: https://site.financialmodelingprep.com/developer/docs/company-key-metrics-api/
    """

    __json_schema_extra__ = {
        "symbol": {"multiple_items_allowed": True},
        "period": {
            "choices": ["annual", "quarter"],
        },
    }

    period: Literal["annual", "quarter"] = Field(
        default="annual",
        description=QUERY_DESCRIPTIONS.get("period", ""),
    )
    with_ttm: bool = Field(
        default=False, description="Include trailing twelve months (TTM) data."
    )


class FMPKeyMetricsData(KeyMetricsData):
    """FMP Key Metrics Data."""

    __alias_dict__ = {
        "dividend_yield": "dividend_yiel",
        "market_cap": "marketCap",
        "research_and_development_to_revenue": "researchAndDdevelopementToRevenue",
        "fiscal_period": "period",
        "period_ending": "date",
        "price_to_sales": "priceToSalesRatio",
        "price_to_operating_cash_flow": "pocfratio",
        "price_to_free_cash_flow": "pfcfRatio",
        "price_to_book": "pbRatio",
        "price_to_tangible_book": "ptbRatio",
        "ev_to_sales": "evToSales",
        "ev_to_ebitda": "enterpriseValueOverEBITDA",
        "net_debt_to_ebitda": "netDebtToEBITDA",
        "return_on_equity": "roe",
        "return_on_invested_capital": "roic",
    }
    period_ending: dateType = Field(description="Period ending date.")
    fiscal_period: str = Field(description="Period of the data.")
    calendar_year: Optional[ForceInt] = Field(
        default=None, description="Calendar year for the fiscal period."
    )
    revenue_per_share: Optional[float] = Field(
        default=None, description="Revenue per share"
    )
    capex_per_share: Optional[float] = Field(
        default=None, description="Capital expenditures per share"
    )
    net_income_per_share: Optional[float] = Field(
        default=None, description="Net income per share"
    )
    operating_cash_flow_per_share: Optional[float] = Field(
        default=None, description="Operating cash flow per share"
    )
    free_cash_flow_per_share: Optional[float] = Field(
        default=None, description="Free cash flow per share"
    )
    cash_per_share: Optional[float] = Field(default=None, description="Cash per share")
    book_value_per_share: Optional[float] = Field(
        default=None, description="Book value per share"
    )
    tangible_book_value_per_share: Optional[float] = Field(
        default=None, description="Tangible book value per share"
    )
    shareholders_equity_per_share: Optional[float] = Field(
        default=None, description="Shareholders equity per share"
    )
    interest_debt_per_share: Optional[float] = Field(
        default=None, description="Interest debt per share"
    )
    price_to_sales: Optional[float] = Field(
        default=None,
        description="Price-to-sales ratio",
    )
    price_to_operating_cash_flow: Optional[float] = Field(
        default=None,
        description="Price-to-operating cash flow ratio",
    )
    price_to_free_cash_flow: Optional[float] = Field(
        default=None,
        description="Price-to-free cash flow ratio",
    )
    price_to_book: Optional[float] = Field(
        default=None,
        description="Price-to-book ratio",
    )
    price_to_tangible_book: Optional[float] = Field(
        default=None,
        description="Price-to-tangible book ratio",
    )
    ev_to_sales: Optional[float] = Field(
        default=None,
        description="Enterprise value-to-sales ratio",
    )
    ev_to_ebitda: Optional[float] = Field(
        default=None,
        description="Enterprise value-to-EBITDA ratio",
    )
    ev_to_operating_cash_flow: Optional[float] = Field(
        default=None, description="Enterprise value-to-operating cash flow ratio"
    )
    ev_to_free_cash_flow: Optional[float] = Field(
        default=None, description="Enterprise value-to-free cash flow ratio"
    )
    earnings_yield: Optional[float] = Field(
        default=None,
        description="Earnings yield",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    free_cash_flow_yield: Optional[float] = Field(
        default=None,
        description="Free cash flow yield",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    debt_to_market_cap: Optional[float] = Field(
        default=None, description="Debt-to-market capitalization ratio"
    )
    debt_to_equity: Optional[float] = Field(
        default=None, description="Debt-to-equity ratio"
    )
    debt_to_assets: Optional[float] = Field(
        default=None, description="Debt-to-assets ratio"
    )
    net_debt_to_ebitda: Optional[float] = Field(
        default=None,
        description="Net debt-to-EBITDA ratio",
    )
    current_ratio: Optional[float] = Field(default=None, description="Current ratio")
    interest_coverage: Optional[float] = Field(
        default=None, description="Interest coverage"
    )
    income_quality: Optional[float] = Field(default=None, description="Income quality")
    payout_ratio: Optional[float] = Field(default=None, description="Payout ratio")
    sales_general_and_administrative_to_revenue: Optional[float] = Field(
        default=None,
        description="Sales general and administrative expenses-to-revenue ratio",
    )
    research_and_development_to_revenue: Optional[float] = Field(
        default=None,
        description="Research and development expenses-to-revenue ratio",
        alias="researchAndDevelopementToRevenue",
    )
    intangibles_to_total_assets: Optional[float] = Field(
        default=None, description="Intangibles-to-total assets ratio"
    )
    capex_to_operating_cash_flow: Optional[float] = Field(
        default=None, description="Capital expenditures-to-operating cash flow ratio"
    )
    capex_to_revenue: Optional[float] = Field(
        default=None, description="Capital expenditures-to-revenue ratio"
    )
    capex_to_depreciation: Optional[float] = Field(
        default=None, description="Capital expenditures-to-depreciation ratio"
    )
    stock_based_compensation_to_revenue: Optional[float] = Field(
        default=None, description="Stock-based compensation-to-revenue ratio"
    )
    working_capital: Optional[float] = Field(
        default=None, description="Working capital"
    )
    tangible_asset_value: Optional[float] = Field(
        default=None, description="Tangible asset value"
    )
    net_current_asset_value: Optional[float] = Field(
        default=None, description="Net current asset value"
    )
    enterprise_value: Optional[float] = Field(
        default=None, description="Enterprise value"
    )
    invested_capital: Optional[float] = Field(
        default=None, description="Invested capital"
    )
    average_receivables: Optional[float] = Field(
        default=None, description="Average receivables"
    )
    average_payables: Optional[float] = Field(
        default=None, description="Average payables"
    )
    average_inventory: Optional[float] = Field(
        default=None, description="Average inventory"
    )
    days_sales_outstanding: Optional[float] = Field(
        default=None, description="Days sales outstanding"
    )
    days_payables_outstanding: Optional[float] = Field(
        default=None, description="Days payables outstanding"
    )
    days_of_inventory_on_hand: Optional[float] = Field(
        default=None, description="Days of inventory on hand"
    )
    receivables_turnover: Optional[float] = Field(
        default=None, description="Receivables turnover"
    )
    payables_turnover: Optional[float] = Field(
        default=None, description="Payables turnover"
    )
    inventory_turnover: Optional[float] = Field(
        default=None, description="Inventory turnover"
    )
    return_on_equity: Optional[float] = Field(
        default=None,
        description="Return on equity",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    return_on_invested_capital: Optional[float] = Field(
        default=None,
        description="Return on invested capital",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    return_on_tangible_assets: Optional[float] = Field(
        default=None,
        description="Return on tangible assets",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    dividend_yield: Optional[float] = Field(
        default=None,
        description="Dividend yield, as a normalized percent.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
        alias="dividendYield",
    )
    graham_number: Optional[float] = Field(default=None, description="Graham number")
    graham_net_net: Optional[float] = Field(
        default=None, description="Graham net-net working capital"
    )


class FMPKeyMetricsFetcher(
    Fetcher[
        FMPKeyMetricsQueryParams,
        List[FMPKeyMetricsData],
    ]
):
    """FMP Key Metrics Fetcher."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FMPKeyMetricsQueryParams:
        """Transform the query params."""
        return FMPKeyMetricsQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: FMPKeyMetricsQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the FMP endpoint."""
        api_key = credentials.get("fmp_api_key") if credentials else ""
        base_url = "https://financialmodelingprep.com/api/v3"
        symbols = query.symbol.split(",")
        results: List = []

        async def get_one(symbol):
            """Get data for one symbol."""
            url = (
                f"{base_url}/key-metrics/{symbol}?period={query.period}"
                + f"&limit={query.limit}&apikey={api_key}"
            )
            result = await amake_request(
                url, response_callback=response_callback, **kwargs
            )
            if not result:
                warn(f"Symbol Error: No data found for {symbol}.")

            if result:
                ttm_url = f"{base_url}/key-metrics-ttm/{symbol}?&apikey={api_key}"
                if query.with_ttm and (
                    metrics_ttm := await amake_request(
                        ttm_url, response_callback=response_callback, **kwargs
                    )
                ):
                    metrics_ttm_data = {
                        k: v
                        for k, v in metrics_ttm[0].items()
                        if k
                        not in ("dividendYieldPercentageTTM", "dividendPerShareTTM")
                    }
                    result.insert(  # type: ignore
                        0,
                        {
                            "symbol": symbol,
                            "period": "TTM",
                            "date": datetime.now().strftime("%Y-%m-%d"),
                            "calendar_year": datetime.now().year,
                            **{
                                k.replace("TTM", ""): v
                                for k, v in metrics_ttm_data.items()
                            },
                        },
                    )
                results.extend(result)

        await asyncio.gather(*[get_one(symbol) for symbol in symbols])

        if not results:
            raise EmptyDataError(f"No data found for given symbols -> {query.symbol}.")

        return results

    @staticmethod
    def transform_data(
        query: FMPKeyMetricsQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[FMPKeyMetricsData]:
        """Return the transformed data."""
        return [FMPKeyMetricsData.model_validate(d) for d in data]
