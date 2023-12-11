"""FMP Financial Ratios Model."""

from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.financial_ratios import (
    FinancialRatiosData,
    FinancialRatiosQueryParams,
)
from openbb_core.provider.utils.helpers import (
    ClientResponse,
    ClientSession,
    amake_requests,
)
from pydantic import Field

PeriodType = Literal["annual", "quarter"]


class FMPFinancialRatiosQueryParams(FinancialRatiosQueryParams):
    """FMP Financial Ratios Query.

    Source: https://financialmodelingprep.com/developer/docs/#Company-Financial-Ratios
    """

    with_ttm: Optional[bool] = Field(
        default=False, description="Include trailing twelve months (TTM) data."
    )


class FMPFinancialRatiosData(FinancialRatiosData):
    """FMP Financial Ratios Data."""

    __alias_dict__ = {
        "net_income_per_ebt": "netIncomePerEBT",
        "dividend_yield": "dividendYiel",
        "dividend_yield_percentage": "dividendYieldPercentage",
        "dividend_per_share": "dividendPerShare",
        "research_and_developement_to_revenue": "researchAndDevelopementToRevenue",
        "debt_to_market_cap": "debtToMarketCap",
    }


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

        async def response_callback(
            response: ClientResponse, session: ClientSession
        ) -> List[Dict]:
            results = await response.json()
            symbol = response.url.parts[-1]

            # TTM data
            ttm_url = f"{base_url}/ratios-ttm/{symbol}?&apikey={api_key}"
            if query.with_ttm and (ratios_ttm := await session.get_one(ttm_url)):
                results.insert(
                    0,
                    {
                        "symbol": symbol,
                        "period": "TTM",
                        "date": datetime.now().strftime("%Y-%m-%d"),
                        **{k.replace("TTM", ""): v for k, v in ratios_ttm.items()},
                    },
                )

            return results

        urls = [
            f"{base_url}/ratios/{symbol}?"
            f"period={query.period}&limit={query.limit}&apikey={api_key}"
            for symbol in query.symbol.split(",")
        ]

        return await amake_requests(urls, response_callback=response_callback, **kwargs)

    @staticmethod
    def transform_data(
        query: FMPFinancialRatiosQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[FMPFinancialRatiosData]:
        """Return the transformed data."""
        return [FMPFinancialRatiosData.model_validate(d) for d in data]
