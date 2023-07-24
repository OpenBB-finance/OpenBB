"""FMP Company Overview Fetcher."""


from typing import Dict, Optional

from openbb_provider.abstract.data import Data
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.helpers import data_transformer
from openbb_provider.models.company_overview import (
    CompanyOverviewData,
    CompanyOverviewQueryParams,
)

from openbb_fmp.utils.helpers import get_data

# IMPORT THIRD-PARTY


# This part is only provided by FMP and not by the other providers for now.


class FMPCompanyOverviewQueryParams(CompanyOverviewQueryParams):
    """FMP Company Overview query.

    Source: https://site.financialmodelingprep.com/developer/docs/companies-key-stats-free-api/

    Parameter
    ---------
    symbol : str
        The symbol of the company.
    """


class FMPCompanyOverviewData(Data):
    symbol: str
    price: float
    beta: float
    volAvg: int
    mktCap: int
    lastDiv: float
    range: str
    changes: float
    companyName: str
    currency: str
    cik: Optional[str]
    isin: Optional[str]
    cusip: Optional[str]
    exchange: str
    exchangeShortName: str
    industry: str
    website: str
    description: str
    ceo: str
    sector: str
    country: str
    fullTimeEmployees: str
    phone: str
    address: str
    city: str
    state: str
    zip: str
    dcfDiff: float
    dcf: float
    image: str
    ipoDate: str
    defaultImage: bool
    isEtf: bool
    isActivelyTrading: bool
    isAdr: bool
    isFund: bool


class FMPCompanyProfileFetcher(
    Fetcher[  # type: ignore
        CompanyOverviewQueryParams,
        CompanyOverviewData,
        FMPCompanyOverviewQueryParams,
        FMPCompanyOverviewData,
    ]
):
    @staticmethod
    def transform_query(
        query: CompanyOverviewQueryParams, extra_params: Optional[Dict] = None
    ) -> FMPCompanyOverviewQueryParams:
        return FMPCompanyOverviewQueryParams(symbol=query.symbol)

    @staticmethod
    def extract_data(
        query: FMPCompanyOverviewQueryParams, credentials: Optional[Dict[str, str]]
    ) -> FMPCompanyOverviewData:
        if credentials:
            api_key = credentials.get("fmp_api_key")

        base_url = "https://financialmodelingprep.com/api/v3/"
        request_url = f"{base_url}profile/{query.symbol}?apikey={api_key}"
        data = get_data(request_url)
        if isinstance(data, dict):
            raise ValueError("Expected list of dicts, got dict")

        return FMPCompanyOverviewData.parse_obj(data[0])

    @staticmethod
    def transform_data(  # type: ignore
        data: FMPCompanyOverviewData,
    ) -> CompanyOverviewData:
        # Need to update transform_data to return a non list version of list isn't used
        return data_transformer(data, CompanyOverviewData)  # type: ignore
