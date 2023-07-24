"""FMP Analyst Estimates fetcher."""

# IMPORT STANDARD
from datetime import date as dateType
from typing import Dict, List, Optional

from openbb_provider.abstract.data import Data
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.helpers import data_transformer

# IMPORT INTERNAL
from openbb_provider.models.analyst_estimates import (
    AnalystEstimatesData,
    AnalystEstimatesQueryParams,
)

# IMPORT THIRD-PARTY
from openbb_fmp.utils.helpers import create_url, get_data_many


class FMPAnalystEstimatesQueryParams(AnalystEstimatesQueryParams):
    """FMP Analysts Estimates query.

    Source: https://site.financialmodelingprep.com/developer/docs/analyst-estimates-api/

    Parameter
    ---------
    symbol : str
        The symbol of the company.
    period: Literal["quarter", "annual"]
        The period of the analyst estimates.
    limit : int
        The limit number of the amount of returned estimates.
    """


class FMPAnalystEstimatesData(Data):
    symbol: str
    date: dateType
    estimatedRevenueLow: int
    estimatedRevenueHigh: int
    estimatedRevenueAvg: int
    estimatedEbitdaLow: int
    estimatedEbitdaHigh: int
    estimatedEbitdaAvg: int
    estimatedEbitLow: int
    estimatedEbitHigh: int
    estimatedEbitAvg: int
    estimatedNetIncomeLow: int
    estimatedNetIncomeHigh: int
    estimatedNetIncomeAvg: int
    estimatedSgaExpenseLow: int
    estimatedSgaExpenseHigh: int
    estimatedSgaExpenseAvg: int
    estimatedEpsAvg: float
    estimatedEpsHigh: float
    estimatedEpsLow: float
    numberAnalystEstimatedRevenue: int
    numberAnalystsEstimatedEps: int


class FMPAnalystEstimatesFetcher(
    Fetcher[
        AnalystEstimatesQueryParams,
        AnalystEstimatesData,
        FMPAnalystEstimatesQueryParams,
        FMPAnalystEstimatesData,
    ]
):
    @staticmethod
    def transform_query(
        query: AnalystEstimatesQueryParams, extra_params: Optional[Dict] = None
    ) -> FMPAnalystEstimatesQueryParams:
        return FMPAnalystEstimatesQueryParams(
            symbol=query.symbol, period=query.period, limit=query.limit
        )

    @staticmethod
    def extract_data(
        query: FMPAnalystEstimatesQueryParams, credentials: Optional[Dict[str, str]]
    ) -> List[FMPAnalystEstimatesData]:
        if credentials:
            api_key = credentials.get("fmp_api_key")

        url = create_url(
            3, f"analyst-estimates/{query.symbol}", api_key, query, ["symbol"]
        )
        return get_data_many(url, FMPAnalystEstimatesData)

    @staticmethod
    def transform_data(
        data: List[FMPAnalystEstimatesData],
    ) -> List[AnalystEstimatesData]:
        return data_transformer(data, AnalystEstimatesData)
