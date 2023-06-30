"""FMP Share Statistics Fetcher."""

# IMPORT STANDARD
from datetime import date as dateType
from datetime import datetime
from typing import Dict, List, Optional

# IMPORT THIRD-PARTY
from pydantic import validator

from builtin_providers.fmp.helpers import create_url, get_data_many

# IMPORT INTERNAL
from openbb_provider.model.abstract.data import Data, QueryParams
from openbb_provider.model.data.base import BaseSymbol
from openbb_provider.model.data.share_statistics import (
    ShareStatisticsData,
    ShareStatisticsQueryParams,
)
from openbb_provider.provider.abstract.fetcher import Fetcher
from openbb_provider.provider.provider_helpers import data_transformer


class FMPShareStatisticsQueryParams(QueryParams, BaseSymbol):
    """FMP Income Statement QueryParams.

    Source: https://site.financialmodelingprep.com/developer/docs/shares-float-api/

    Parameter
    ---------
    symbol : str
        The symbol of the company.
    """

    __name__ = "FMPShareStatisticsQueryParams"


class FMPShareStatisticsData(Data):
    __name__ = "FMPShareStatisticsData"
    symbol: str
    date: dateType
    freeFloat: float
    floatShares: float
    outstandingShares: float
    source: str

    @validator("date", pre=True)
    def time_validate(cls, v):  # pylint: disable=E0213
        return datetime.strptime(v, "%Y-%m-%d %H:%M:%S")


class FMPShareStatisticsFetcher(
    Fetcher[
        ShareStatisticsQueryParams,
        ShareStatisticsData,
        FMPShareStatisticsQueryParams,
        FMPShareStatisticsData,
    ]
):
    @staticmethod
    def transform_query(
        query: ShareStatisticsQueryParams, extra_params: Optional[Dict] = None
    ) -> FMPShareStatisticsQueryParams:
        return FMPShareStatisticsQueryParams(symbol=query.symbol)

    @staticmethod
    def extract_data(
        query: FMPShareStatisticsQueryParams, api_key: str
    ) -> List[FMPShareStatisticsData]:
        url = create_url(4, "shares_float", api_key, query)
        return get_data_many(url, FMPShareStatisticsData)

    @staticmethod
    def transform_data(
        data: List[FMPShareStatisticsData],
    ) -> List[ShareStatisticsData]:
        return data_transformer(data, ShareStatisticsData)
