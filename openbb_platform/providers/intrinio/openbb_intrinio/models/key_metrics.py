"""Intrinio Key Metrics Model."""

# pylint: disable=unused-argument

import asyncio
from typing import Any, Dict, List, Optional
from warnings import warn

from openbb_core.provider.abstract.data import ForceInt
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.key_metrics import (
    KeyMetricsData,
    KeyMetricsQueryParams,
)
from openbb_core.provider.utils.errors import EmptyDataError
from openbb_core.provider.utils.helpers import (
    ClientResponse,
    amake_requests,
)
from pydantic import Field


class IntrinioKeyMetricsQueryParams(KeyMetricsQueryParams):
    """
    Intrinio Key Metrics Query.

    Source: https://data.intrinio.com/data-tags/
    """

    __json_schema_extra__ = {"symbol": {"multiple_items_allowed": True}}


class IntrinioKeyMetricsData(KeyMetricsData):
    """Intrinio Key Metrics Data."""

    __alias_dict__ = {
        "market_cap": "marketcap",
        "pe_ratio": "pricetoearnings",
        "price_to_book": "pricetobook",
        "price_to_tangible_book": "pricetotangiblebook",
        "price_to_revenue": "pricetorevenue",
        "long_term_debt": "ltdebtandcapleases",
        "total_debt": "debt",
        "total_capital": "totalcapital",
        "enterprise_value": "enterprisevalue",
        "eps_growth": "epsgrowth",
        "ebit_growth": "ebitgrowth",
        "ebitda_growth": "ebitdagrowth",
        "revenue_growth": "revenuegrowth",
        "net_income_growth": "netincomegrowth",
        "free_cash_flow_to_firm_growth": "fcffgrowth",
        "invested_capital_growth": "investedcapitalgrowth",
        "quick_ratio": "quickratio",
        "gross_margin": "grossmargin",
        "ebit_margin": "ebitmargin",
        "profit_margin": "profitmargin",
        "return_on_assets": "roa",
        "return_on_equity": "roe",
        "return_on_invested_capital": "roic",
        "free_cash_flow_to_firm": "freecashflow",
        "altman_z_score": "altmanzscore",
        "earnings_yield": "earningsyield",
        "dividend_yield": "dividendyield",
        "year_high": "52_week_high",
        "year_low": "52_week_low",
        "volume_avg": "average_daily_volume",
        "shares_outstanding": "adjweightedavebasicsharesos",
        "eps": "basiceps",
    }

    price_to_book: Optional[float] = Field(
        default=None,
        description="Price to book ratio.",
    )
    price_to_tangible_book: Optional[float] = Field(
        default=None,
        description="Price to tangible book ratio.",
    )
    price_to_revenue: Optional[float] = Field(
        default=None,
        description="Price to revenue ratio.",
    )
    quick_ratio: Optional[float] = Field(
        default=None,
        description="Quick ratio.",
    )
    gross_margin: Optional[float] = Field(
        default=None,
        description="Gross margin, as a normalized percent.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    ebit_margin: Optional[float] = Field(
        default=None,
        description="EBIT margin, as a normalized percent.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    profit_margin: Optional[float] = Field(
        default=None,
        description="Profit margin, as a normalized percent.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    eps: Optional[float] = Field(
        default=None,
        description="Basic earnings per share.",
    )
    eps_growth: Optional[float] = Field(
        default=None,
        description="EPS growth, as a normalized percent.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    revenue_growth: Optional[float] = Field(
        default=None,
        description="Revenue growth, as a normalized percent.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    ebitda_growth: Optional[float] = Field(
        default=None,
        description="EBITDA growth, as a normalized percent.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    ebit_growth: Optional[float] = Field(
        default=None,
        description="EBIT growth, as a normalized percent.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    net_income_growth: Optional[float] = Field(
        default=None,
        description="Net income growth, as a normalized percent.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    free_cash_flow_to_firm_growth: Optional[float] = Field(
        default=None,
        description="Free cash flow to firm growth, as a normalized percent.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    invested_capital_growth: Optional[float] = Field(
        default=None,
        description="Invested capital growth, as a normalized percent.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    return_on_assets: Optional[float] = Field(
        default=None,
        description="Return on assets, as a normalized percent.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    return_on_equity: Optional[float] = Field(
        default=None,
        description="Return on equity, as a normalized percent.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    return_on_invested_capital: Optional[float] = Field(
        default=None,
        description="Return on invested capital, as a normalized percent.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    ebitda: Optional[ForceInt] = Field(
        default=None,
        description="Earnings before interest, taxes, depreciation, and amortization.",
    )
    ebit: Optional[ForceInt] = Field(
        default=None,
        description="Earnings before interest and taxes.",
    )
    long_term_debt: Optional[ForceInt] = Field(
        default=None,
        description="Long-term debt.",
    )
    total_debt: Optional[ForceInt] = Field(
        default=None,
        description="Total debt.",
    )
    total_capital: Optional[ForceInt] = Field(
        default=None,
        description="The sum of long-term debt and total shareholder equity.",
    )
    enterprise_value: Optional[ForceInt] = Field(
        default=None,
        description="Enterprise value.",
    )
    free_cash_flow_to_firm: Optional[ForceInt] = Field(
        default=None,
        description="Free cash flow to firm.",
    )
    altman_z_score: Optional[float] = Field(
        default=None,
        description="Altman Z-score.",
    )
    beta: Optional[float] = Field(
        default=None,
        description="Beta relative to the broad market (rolling three-year).",
    )
    dividend_yield: Optional[float] = Field(
        default=None,
        description="Dividend yield, as a normalized percent.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    earnings_yield: Optional[float] = Field(
        default=None,
        description="Earnings yield, as a normalized percent.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    last_price: Optional[float] = Field(
        default=None,
        description="Last price of the stock.",
    )
    year_high: Optional[float] = Field(
        default=None,
        description="52 week high",
    )
    year_low: float = Field(default=None, description="52 week low")
    volume_avg: Optional[ForceInt] = Field(
        default=None,
        description="Average daily volume.",
    )
    short_interest: Optional[ForceInt] = Field(
        default=None,
        description="Number of shares reported as sold short.",
    )
    shares_outstanding: Optional[ForceInt] = Field(
        default=None,
        description="Weighted average shares outstanding (TTM).",
    )
    days_to_cover: Optional[float] = Field(
        default=None,
        description="Days to cover short interest, based on average daily volume.",
    )


class IntrinioKeyMetricsFetcher(
    Fetcher[
        IntrinioKeyMetricsQueryParams,
        List[IntrinioKeyMetricsData],
    ]
):
    """Transform the query, extract and transform the data from the Intrinio endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> IntrinioKeyMetricsQueryParams:
        """Transform the query params."""

        if params.get("period") is not None and params.get("period") != "annual":
            warn(
                "The period parameter is not available for this Intrinio endpoint, it will be ignored."
            )
        return IntrinioKeyMetricsQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: IntrinioKeyMetricsQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the Intrinio endpoint."""
        api_key = credentials.get("intrinio_api_key") if credentials else ""
        tags = [
            "beta",
            "average_daily_volume",
            "basiceps",
            "basicdilutedeps",
            "marketcap",
            "last_price",
            "52_week_high",
            "52_week_low",
            "dividendyield",
            "pricetoearnings",
            "pricetorevenue",
            "pricetobook",
            "pricetotangiblebook",
            "grossmargin",
            "ebitmargin",
            "profitmargin",
            "roa",
            "roe",
            "roic",
            "earningsyield",
            "days_to_cover",
            "short_interest",
            "revenuegrowth",
            "ebitgrowth",
            "ebitdagrowth",
            "epsgrowth",
            "netincomegrowth",
            "investedcapitalgrowth",
            "debt",
            "totalcapital",
            "enterprisevalue",
            "freecashflow",
            "fcffgrowth",
            "ltdebtandcapleases",
            "altmanzscore",
            "quickratio",
            "ebit",
            "ebitda",
            "adjweightedavebasicsharesos",
        ]
        results = []
        urls = []
        symbols = query.symbol.split(",")

        async def get_one(symbol: str):
            """Get data for one symbol."""

            _urls = [
                f"https://api-v2.intrinio.com/companies/{symbol}/data_point/{tag}?api_key={api_key}"
                for tag in tags
            ]
            urls.extend(_urls)

            async def callback(response: ClientResponse, _: Any) -> Dict:
                """Return the response."""
                return {response.url.parts[-1]: await response.json()}

            data = {}
            for result in await amake_requests(urls, callback, **kwargs):
                data.update(result)
            if data:
                data["symbol"] = symbol
                results.append(data)

        tasks = [get_one(symbol) for symbol in symbols]

        await asyncio.gather(*tasks)

        if not results:
            raise EmptyDataError()

        return results

    @staticmethod
    def transform_data(
        query: IntrinioKeyMetricsQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> List[IntrinioKeyMetricsData]:
        """Validate and transform the data."""

        # Sort the results by the order of the symbols in the query.
        symbols = query.symbol.split(",")
        data = sorted(
            data,
            key=(
                lambda item: (
                    symbols.index(item["symbol"])
                    if item["symbol"] in symbols
                    else len(symbols)
                )
            ),
        )

        results: List[IntrinioKeyMetricsData] = []
        for item in data:

            if item.get("marketcap") is None or isinstance(item.get("marketcap"), dict):
                warn(f"Symbol Error: No data found for {item.get('symbol')}")
                continue

            for key, value in item.copy().items():
                # A bad response in a field will return a dict here, so we remove it.
                if isinstance(value, dict):
                    _ = item.pop(key)

            results.append(IntrinioKeyMetricsData.model_validate(item))

        return results
