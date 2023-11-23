"""FMP Financial Ratios Model."""

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from itertools import repeat
from typing import Any, Dict, List, Literal, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.financial_ratios import (
    FinancialRatiosData,
    FinancialRatiosQueryParams,
)
from openbb_fmp.utils.helpers import get_data_many, get_data_one
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
    def extract_data(
        query: FMPFinancialRatiosQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the FMP endpoint."""
        api_key = credentials.get("fmp_api_key") if credentials else ""

        base_url = "https://financialmodelingprep.com/api/v3"
        data: List[Dict] = []

        def multiple_symbols(symbol: str, data: List[Dict]) -> None:
            url = (
                f"{base_url}/ratios/{symbol}?"
                f"period={query.period}&limit={query.limit}&apikey={api_key}"
            )

            # TTM data
            ttm_url = f"{base_url}/ratios-ttm/{symbol}?&apikey={api_key}"
            if query.with_ttm and (ratios_ttm := get_data_one(ttm_url, **kwargs)):
                data.append(
                    {
                        "symbol": symbol,
                        "period": "TTM",
                        "date": datetime.now().strftime("%Y-%m-%d"),
                        **{k.replace("TTM", ""): v for k, v in ratios_ttm.items()},
                    }
                )

            return data.extend(get_data_many(url, **kwargs))

        with ThreadPoolExecutor() as executor:
            executor.map(multiple_symbols, query.symbol.split(","), repeat(data))

        return data

    @staticmethod
    def transform_data(
        query: FMPFinancialRatiosQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[FMPFinancialRatiosData]:
        """Return the transformed data."""
        return [FMPFinancialRatiosData.model_validate(d) for d in data]
