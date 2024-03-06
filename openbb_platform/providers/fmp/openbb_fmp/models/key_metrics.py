"""FMP Key Metrics Model."""

from datetime import (
    date as dateType,
    datetime,
)
from typing import Any, Dict, List, Optional

from openbb_core.provider.abstract.data import ForceInt
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.key_metrics import (
    KeyMetricsData,
    KeyMetricsQueryParams,
)
from openbb_core.provider.utils.descriptions import DATA_DESCRIPTIONS
from openbb_core.provider.utils.helpers import (
    ClientResponse,
    ClientSession,
    amake_requests,
)
from pydantic import Field


class FMPKeyMetricsQueryParams(KeyMetricsQueryParams):
    """FMP Key Metrics Query.

    Source: https://site.financialmodelingprep.com/developer/docs/company-key-metrics-api/
    """

    __json_schema_extra__ = {"symbol": ["multiple_items_allowed"]}

    with_ttm: Optional[bool] = Field(
        default=False, description="Include trailing twelve months (TTM) data."
    )


class FMPKeyMetricsData(KeyMetricsData):
    """FMP Key Metrics Data."""

    date: dateType = Field(description=DATA_DESCRIPTIONS.get("date", ""))
    period: str = Field(description="Period of the data.")
    calendar_year: Optional[ForceInt] = Field(
        default=None, description="Calendar year."
    )
    revenue_per_share: Optional[float] = Field(
        default=None, description="Revenue per share"
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
    enterprise_value: Optional[float] = Field(
        default=None, description="Enterprise value"
    )
    price_to_sales_ratio: Optional[float] = Field(
        default=None, description="Price-to-sales ratio"
    )
    pocf_ratio: Optional[float] = Field(
        default=None,
        description="Price-to-operating cash flow ratio",
        alias="pocfratio",
    )
    pfcf_ratio: Optional[float] = Field(
        default=None, description="Price-to-free cash flow ratio"
    )
    pb_ratio: Optional[float] = Field(default=None, description="Price-to-book ratio")
    ptb_ratio: Optional[float] = Field(
        default=None, description="Price-to-tangible book ratio"
    )
    ev_to_sales: Optional[float] = Field(
        default=None, description="Enterprise value-to-sales ratio"
    )
    enterprise_value_over_ebitda: Optional[float] = Field(
        default=None,
        description="Enterprise value-to-EBITDA ratio",
        alias="enterpriseValueOverEBITDA",
    )
    ev_to_operating_cash_flow: Optional[float] = Field(
        default=None, description="Enterprise value-to-operating cash flow ratio"
    )
    ev_to_free_cash_flow: Optional[float] = Field(
        default=None, description="Enterprise value-to-free cash flow ratio"
    )
    earnings_yield: Optional[float] = Field(default=None, description="Earnings yield")
    free_cash_flow_yield: Optional[float] = Field(
        default=None, description="Free cash flow yield"
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
        alias="netDebtToEBITDA",
    )
    current_ratio: Optional[float] = Field(default=None, description="Current ratio")
    interest_coverage: Optional[float] = Field(
        default=None, description="Interest coverage"
    )
    income_quality: Optional[float] = Field(default=None, description="Income quality")
    dividend_yield: Optional[float] = Field(
        default=None,
        description="Dividend yield, as a normalized percent.",
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
    )
    payout_ratio: Optional[float] = Field(default=None, description="Payout ratio")
    sales_general_and_administrative_to_revenue: Optional[float] = Field(
        default=None,
        description="Sales general and administrative expenses-to-revenue ratio",
    )
    research_and_development_to_revenue: Optional[float] = Field(
        default=None,
        description="Research and development expenses-to-revenue ratio",
        alias="researchAndDdevelopementToRevenue",
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
    graham_number: Optional[float] = Field(default=None, description="Graham number")
    roic: Optional[float] = Field(
        default=None, description="Return on invested capital"
    )
    return_on_tangible_assets: Optional[float] = Field(
        default=None, description="Return on tangible assets"
    )
    graham_net_net: Optional[float] = Field(
        default=None, description="Graham net-net working capital"
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
    roe: Optional[float] = Field(default=None, description="Return on equity")
    capex_per_share: Optional[float] = Field(
        default=None, description="Capital expenditures per share"
    )


class FMPKeyMetricsFetcher(
    Fetcher[
        FMPKeyMetricsQueryParams,
        List[FMPKeyMetricsData],
    ]
):
    """Transform the query, extract and transform the data from the FMP endpoints."""

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

        async def response_callback(
            response: ClientResponse, session: ClientSession
        ) -> List[Dict]:
            results = await response.json()
            symbol = response.url.parts[-1]

            # TTM data
            ttm_url = f"{base_url}/key-metrics-ttm/{symbol}?&apikey={api_key}"
            if query.with_ttm and (metrics_ttm := await session.get_one(ttm_url)):
                results.insert(
                    0,
                    {
                        "symbol": symbol,
                        "period": "TTM",
                        "date": datetime.now().strftime("%Y-%m-%d"),
                        "calendar_year": datetime.now().year,
                        **{k.replace("TTM", ""): v for k, v in metrics_ttm.items()},
                    },
                )

            return results

        urls = [
            f"{base_url}/key-metrics/{symbol}?"
            f"period={query.period}&limit={query.limit}&apikey={api_key}"
            for symbol in query.symbol.split(",")
        ]

        return await amake_requests(urls, response_callback=response_callback, **kwargs)

    @staticmethod
    def transform_data(
        query: FMPKeyMetricsQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[FMPKeyMetricsData]:
        """Return the transformed data."""
        return [FMPKeyMetricsData.model_validate(d) for d in data]
