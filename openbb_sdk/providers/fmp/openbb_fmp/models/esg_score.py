"""FMP ESG Score fetcher."""


from datetime import date, datetime
from typing import Any, Dict, List, Optional

from openbb_provider.abstract.data import Data
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.models.esg_score import ESGScoreQueryParams
from pydantic import Field

from openbb_fmp.utils.helpers import create_url, get_data_many


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


class FMPESGScoreFetcher(Fetcher[FMPESGScoreQueryParams, FMPESGScoreData]):
    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FMPESGScoreQueryParams:
        return FMPESGScoreQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FMPESGScoreQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any
    ) -> List[FMPESGScoreData]:
        api_key = credentials.get("fmp_api_key") if credentials else ""

        url = create_url(4, "esg-environmental-social-governance-data", api_key, query)
        return get_data_many(url, FMPESGScoreData, **kwargs)

    @staticmethod
    def transform_data(data: List[FMPESGScoreData]) -> List[FMPESGScoreData]:
        return data
