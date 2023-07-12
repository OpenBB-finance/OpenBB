"""FMP Forex end of day fetcher."""

# IMPORT STANDARD
from datetime import date, datetime
from typing import Dict, List, Literal, Optional

# IMPORT INTERNAL
from openbb_provider.model.abstract.data import Data, QueryParams
from openbb_provider.model.data.forex_eod import ForexEODData, ForexEODQueryParams
from openbb_provider.provider.abstract.fetcher import Fetcher
from openbb_provider.provider.provider_helpers import data_transformer, get_querystring

# IMPORT THIRD-PARTY
from pydantic import Field, NonNegativeInt, validator

from builtin_providers.fmp.helpers import get_data_many


class FMPForexEODQueryParams(QueryParams):
    """FMP Forex end of day query.

    Source: https://site.financialmodelingprep.com/developer/docs/#Historical-Forex-Price

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
    series_type : Optional[Literal["line"]]
        The type of the series. Only "line" is supported.
    """

    symbol: str = Field(min_length=1)
    series_type: Optional[Literal["line"]] = None
    start_date: date
    end_date: date
    timeseries: Optional[NonNegativeInt] = None  # Number of days to looks back


class FMPForexEODData(Data):
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


class FMPForexEODFetcher(
    Fetcher[
        ForexEODQueryParams,
        ForexEODData,
        FMPForexEODQueryParams,
        FMPForexEODData,
    ]
):
    @staticmethod
    def transform_query(
        query: ForexEODQueryParams, extra_params: Optional[Dict] = None
    ) -> FMPForexEODQueryParams:
        now = datetime.now()
        start_date = query.start_date if query.start_date else now
        end_date = query.end_date if query.end_date else now
        return FMPForexEODQueryParams(
            symbol=query.symbol,
            start_date=start_date,
            end_date=end_date,
        )

    @staticmethod
    def extract_data(
        query: FMPForexEODQueryParams, api_key: str
    ) -> List[FMPForexEODData]:
        base_url = "https://financialmodelingprep.com/api/v3/"
        query_str = get_querystring(query.dict(), ["symbol"])
        query_str = query_str.replace("start_date", "from").replace("end_date", "to")
        url = f"{base_url}historical-price-full/{query.symbol}?{query_str}&apikey={api_key}"
        return get_data_many(url, FMPForexEODData, "historical")

    @staticmethod
    def transform_data(data: List[FMPForexEODData]) -> List[ForexEODData]:
        return data_transformer(data, ForexEODData)
