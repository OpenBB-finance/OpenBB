"""FMP Financial Ratios Fetcher."""


from concurrent.futures import ThreadPoolExecutor
from itertools import repeat
from typing import Any, Dict, List, Literal, Optional

from openbb_fmp.utils.helpers import get_data_many
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.financial_ratios import (
    FinancialRatiosData,
    FinancialRatiosQueryParams,
)

PeriodType = Literal["annual", "quarter"]


class FMPFinancialRatiosQueryParams(FinancialRatiosQueryParams):
    """FMP Financial Ratios QueryParams.

    Source: https://financialmodelingprep.com/developer/docs/#Company-Financial-Ratios
    """


class FMPFinancialRatiosData(FinancialRatiosData):
    """FMP Financial Ratios Data."""


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
            return data.extend(get_data_many(url, **kwargs))

        with ThreadPoolExecutor() as executor:
            executor.map(multiple_symbols, query.symbol.split(","), repeat(data))

        return data

    @staticmethod
    def transform_data(data: List[Dict]) -> List[FMPFinancialRatiosData]:
        """Return the transformed data."""
        return [FMPFinancialRatiosData.parse_obj(d) for d in data]
