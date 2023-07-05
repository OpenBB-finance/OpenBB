"""FMP Analyst Estimates fetcher."""

# IMPORT STANDARD
from datetime import date as dateType
from typing import Dict, List, Optional

from openbb_provider.model.abstract.data import Data

# IMPORT INTERNAL
from openbb_provider.model.data.analyst_estimates import (
    AnalystEstimatesData,
    AnalystEstimatesQueryParams,
)
from openbb_provider.provider.abstract.fetcher import Fetcher
from openbb_provider.provider.provider_helpers import data_transformer

# IMPORT THIRD-PARTY
from builtin_providers.fmp.helpers import create_url, get_data_many


class FMPAnalystEstimatesQueryParams(AnalystEstimatesQueryParams):
    """FMP Analysts Estimates query.

    Source: https://site.financialmodelingprep.com/developer/docs/analyst-estimates-api/

    Parameter
    ---------
    symbol : str
        The symbol of the company.
    limit : int
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
        return FMPAnalystEstimatesQueryParams.parse_obj(query)

    @staticmethod
    def extract_data(
        query: FMPAnalystEstimatesQueryParams, api_key: str
    ) -> List[FMPAnalystEstimatesData]:
        url = create_url(
            3, f"analyst-estimates/{query.symbol}", api_key, query, ["symbol"]
        )
        return get_data_many(url, FMPAnalystEstimatesData)

    @staticmethod
    def transform_data(
        data: List[FMPAnalystEstimatesData],
    ) -> List[AnalystEstimatesData]:
        return data_transformer(data, AnalystEstimatesData)
