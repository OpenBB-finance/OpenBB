"""FMP Share Statistics Fetcher."""

# IMPORT STANDARD
from datetime import (
    date as dateType,
    datetime,
)
from typing import Dict, List, Optional

# IMPORT INTERNAL
from openbb_provider.abstract.data import Data, QueryParams
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provideropenbb_fmp.utils.helpers import data_transformer
from openbb_provider.models.base import BaseSymbol
from openbb_provider.models.share_statistics import (
    ShareStatisticsData,
    ShareStatisticsQueryParams,
)

# IMPORT THIRD-PARTY
from pydantic import validator

from openbb_fmp.utils.helpers import create_url, get_data_many


class FMPShareStatisticsQueryParams(QueryParams, BaseSymbol):
    """FMP Income Statement QueryParams.

    Source: https://site.financialmodelingprep.com/developer/docs/shares-float-api/

    Parameter
    ---------
    symbol : str
        The symbol of the company.
    """


class FMPShareStatisticsData(Data):
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
        query: FMPShareStatisticsQueryParams, credentials: Optional[Dict[str, str]]
    ) -> List[FMPShareStatisticsData]:
        if credentials:
            api_key = credentials.get("fmp_api_key")

        url = create_url(4, "shares_float", api_key, query)
        return get_data_many(url, FMPShareStatisticsData)

    @staticmethod
    def transform_data(
        data: List[FMPShareStatisticsData],
    ) -> List[ShareStatisticsData]:
        return data_transformer(data, ShareStatisticsData)
