"""SEC Filings fetcher."""

# IMPORT STANDARD
from datetime import (
    date as dateType,
    datetime,
)
from typing import Dict, List, Optional

# IMPORT INTERNAL
from openbb_provider.model.abstract.data import Data
from openbb_provider.model.data.sec_filings import SECFilingsData, SECFilingsQueryParams
from openbb_provider.provider.abstract.fetcher import Fetcher
from openbb_provider.provider.provider_helpers import data_transformer
from pydantic import validator

# IMPORT THIRD-PARTY
from openbb_fmp.helpers import create_url, get_data_many


class FMPSECFilingsQueryParams(SECFilingsQueryParams):
    """FMP SEC Filings QueryParams.

    Source: https://site.financialmodelingprep.com/developer/docs/sec-filings-api/

    Parameter
    ---------
    symbol : str
        The symbol of the company.
    type : str
        The type of the SEC filing form. (full list: https://www.sec.gov/forms)
    page : int
        The page of the results.
    limit : int
        The limit of the results.
    """


class FMPSECFilingsData(Data):
    symbol: str
    fillingDate: dateType
    acceptedDate: dateType
    cik: str
    type: str
    link: str
    finalLink: str

    @validator("fillingDate", "acceptedDate", pre=True)
    def convert_date(cls, v):  # pylint: disable=no-self-argument
        return datetime.strptime(v, "%Y-%m-%d %H:%M:%S").date()


class FMPSECFilingsFetcher(
    Fetcher[
        SECFilingsQueryParams,
        SECFilingsData,
        FMPSECFilingsQueryParams,
        FMPSECFilingsData,
    ]
):
    @staticmethod
    def transform_query(
        query: SECFilingsQueryParams, extra_params: Optional[Dict] = None
    ) -> FMPSECFilingsQueryParams:
        return FMPSECFilingsQueryParams(
            symbol=query.symbol, page=query.page, limit=query.limit, type=query.type
        )

    @staticmethod
    def extract_data(
        query: FMPSECFilingsQueryParams, api_key: str
    ) -> List[FMPSECFilingsData]:
        url = create_url(
            3, f"sec_filings/{query.symbol}", api_key, query, exclude=["symbol"]
        )
        return get_data_many(url, FMPSECFilingsData)

    @staticmethod
    def transform_data(data: List[FMPSECFilingsData]) -> List[SECFilingsData]:
        return data_transformer(data, SECFilingsData)
