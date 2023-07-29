"""FMP Share Statistics Fetcher."""


from datetime import (
    date as dateType,
    datetime,
)
from typing import Any, Dict, List, Optional

from openbb_provider.abstract.data import Data
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.abstract.query_params import QueryParams
from openbb_provider.models.base import BaseSymbol
from openbb_provider.models.share_statistics import (
    ShareStatisticsData,
    ShareStatisticsQueryParams,
)
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
    def transform_query(params: Dict[str, Any]) -> FMPShareStatisticsQueryParams:
        return FMPShareStatisticsQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FMPShareStatisticsQueryParams, credentials: Optional[Dict[str, str]]
    ) -> List[FMPShareStatisticsData]:
        api_key = credentials.get("fmp_api_key") if credentials else ""

        url = create_url(4, "shares_float", api_key, query)
        return get_data_many(url, FMPShareStatisticsData)

    @staticmethod
    def transform_data(
        data: List[FMPShareStatisticsData],
    ) -> List[FMPShareStatisticsData]:
        return data
