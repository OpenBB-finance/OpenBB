"""FMP Major Indices end of day fetcher."""


from datetime import date, datetime
from typing import Dict, List, Literal, Optional


from openbb_provider.abstract.data import Data, QueryParams
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.helpers import data_transformer, get_querystring
from openbb_provider.models.major_indices_eod import (
    MajorIndicesEODData,
    MajorIndicesEODQueryParams,
)

# IMPORT THIRD-PARTY
from pydantic import Field, NonNegativeInt, validator

from openbb_fmp.utils.helpers import get_data_many


class FMPMajorIndicesEODQueryParams(QueryParams):
    """FMP Major Indices end of day query.

    Source: https://site.financialmodelingprep.com/developer/docs/#Historical-stock-index-prices

    Parameter
    ---------
    symbol : str
        The symbol of the company.
    start_date : date
        The start date of the stock data from which to retrieve the data.
    end_date : date
        The end date of the stock data up to which to retrieve the data.
    timeseries : Optional[int]
        The number of days to look back.
    serietype : Optional[Literal["line"]]
        The type of the series. Only "line" is supported.
    """

    symbol: str = Field(min_length=1)
    serietype: Optional[Literal["line"]]
    start_date: date
    end_date: date
    timeseries: Optional[NonNegativeInt]  # Number of days to looks back


class FMPMajorIndicesEODData(Data):
    date: datetime
    open: float
    high: float
    low: float
    close: float
    adjClose: float = Field(alias="adj_close")
    volume: float
    unadjustedVolume: float
    change: float
    changePercent: float
    vwap: float
    label: str
    changeOverTime: float

    @validator("date", pre=True)
    def time_validate(cls, v):  # pylint: disable=E0213
        return datetime.strptime(v, "%Y-%m-%d")


class FMPMajorIndicesEODFetcher(
    Fetcher[
        MajorIndicesEODQueryParams,
        MajorIndicesEODData,
        FMPMajorIndicesEODQueryParams,
        FMPMajorIndicesEODData,
    ]
):
    @staticmethod
    def transform_query(
        query: MajorIndicesEODQueryParams, extra_params: Optional[Dict] = None
    ) -> FMPMajorIndicesEODQueryParams:
        raw_end = query.end_date if query.end_date else datetime.now()
        return FMPMajorIndicesEODQueryParams(
            symbol=query.symbol,
            start_date=query.start_date,
            end_date=raw_end,
            **extra_params if extra_params else {},
        )

    @staticmethod
    def extract_data(
        query: FMPMajorIndicesEODQueryParams, credentials: Optional[Dict[str, str]]
    ) -> List[FMPMajorIndicesEODData]:
        if credentials:
            api_key = credentials.get("fmp_api_key")

        base_url = "https://financialmodelingprep.com/api/v3/"
        query_str = get_querystring(query.dict(), ["symbol"])
        query_str = query_str.replace("start_date", "from").replace("end_date", "to")
        url = f"{base_url}historical-price-full/{query.symbol}?{query_str}&apikey={api_key}"
        return get_data_many(url, FMPMajorIndicesEODData, "historical")

    @staticmethod
    def transform_data(data: List[FMPMajorIndicesEODData]) -> List[MajorIndicesEODData]:
        return data_transformer(data, MajorIndicesEODData)
