"""FMP ESG Score fetcher."""

# IMPORT STANDARD
from datetime import date, datetime
from typing import Dict, List, Optional

# IMPORT INTERNAL
from openbb_provider.model.abstract.data import Data
from openbb_provider.model.data.esg_score import ESGScoreData, ESGScoreQueryParams
from openbb_provider.provider.abstract.fetcher import Fetcher
from openbb_provider.provider.provider_helpers import data_transformer
from pydantic import Field

# IMPORT THIRD-PARTY
from builtin_providers.fmp.helpers import create_url, get_data_many


class FMPESGScoreQueryParams(ESGScoreQueryParams):
    """FMP ESG Score query.

    Source: https://site.financialmodelingprep.com/developer/docs/#ESG-SCORE

    Parameter
    ---------
    symbol : str
        The symbol of the company.
    """


class FMPESGScoreData(Data):
    symbol: str
    cik: int
    companyName: str
    formType: str
    acceptedDate: datetime
    date: date
    environmentalScore: float
    socialScore: float
    governanceScore: float
    ESGScore: float = Field(alias="esg_score")
    url: str


class FMPESGScoreFetcher(
    Fetcher[ESGScoreQueryParams, ESGScoreData, FMPESGScoreQueryParams, FMPESGScoreData]
):
    @staticmethod
    def transform_query(
        query: ESGScoreQueryParams, extra_params: Optional[Dict] = None
    ) -> FMPESGScoreQueryParams:
        return FMPESGScoreQueryParams.parse_obj(query)

    @staticmethod
    def extract_data(
        query: FMPESGScoreQueryParams, api_key: str
    ) -> List[FMPESGScoreData]:
        url = create_url(4, "esg-environmental-social-governance-data", api_key, query)
        return get_data_many(url, FMPESGScoreData)

    @staticmethod
    def transform_data(data: List[FMPESGScoreData]) -> List[ESGScoreData]:
        return data_transformer(data, ESGScoreData)
