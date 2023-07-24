"""FMP Cryptos end of day fetcher."""

# IMPORT STANDARD
from datetime import date, datetime
from typing import Dict, List, Literal, Optional

# IMPORT INTERNAL
from openbb_provider.abstract.data import Data, QueryParams
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.helpers import data_transformer, get_querystring
from openbb_provider.models.crypto_eod import CryptoEODData, CryptoEODQueryParams

# IMPORT THIRD-PARTY
from pydantic import Field, NonNegativeInt, validator

from openbb_fmp.utils.helpers import get_data_many


class FMPCryptoEODQueryParams(QueryParams):
    """FMP Crypto end of day query.

    Source: https://site.financialmodelingprep.com/developer/docs/#Cryptocurrencies

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


class FMPCryptoEODData(Data):
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


class FMPCryptoEODFetcher(
    Fetcher[
        CryptoEODQueryParams,
        CryptoEODData,
        FMPCryptoEODQueryParams,
        FMPCryptoEODData,
    ]
):
    @staticmethod
    def transform_query(
        query: CryptoEODQueryParams, extra_params: Optional[Dict] = None
    ) -> FMPCryptoEODQueryParams:
        now = datetime.now()
        start_date = query.start_date if query.start_date else now
        end_date = query.end_date if query.end_date else now
        return FMPCryptoEODQueryParams(
            symbol=query.symbol,
            start_date=start_date,
            end_date=end_date,
            **extra_params if extra_params else {},
        )

    @staticmethod
    def extract_data(
        query: FMPCryptoEODQueryParams, credentials: Optional[Dict[str, str]]
    ) -> List[FMPCryptoEODData]:
        if credentials:
            api_key = credentials.get("fmp_api_key")

        base_url = "https://financialmodelingprep.com/api/v3/"
        query_str = get_querystring(query.dict(), ["symbol"])
        query_str = query_str.replace("start_date", "from").replace("end_date", "to")
        url = f"{base_url}historical-price-full/{query.symbol}?{query_str}&apikey={api_key}"
        return get_data_many(url, FMPCryptoEODData, "historical")

    @staticmethod
    def transform_data(data: List[FMPCryptoEODData]) -> List[CryptoEODData]:
        return data_transformer(data, CryptoEODData)
