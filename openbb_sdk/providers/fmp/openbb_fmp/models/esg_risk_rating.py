"""FMP ESG Risk Rating fetcher."""


from datetime import date
from typing import Any, Dict, List, Literal, Optional

from openbb_provider.abstract.data import Data
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.models.esg_risk_rating import (
    ESGRiskRatingData,
    ESGRiskRatingQueryParams,
)
from pydantic import Field

from openbb_fmp.utils.helpers import create_url, get_data_many

current_year = date.today().year
ratings = Literal[
    "A+", "A", "A-", "B+", "B", "B-", "C+", "C", "C-", "D+", "D", "D-", "F"
]


class FMPESGRiskRatingQueryParams(ESGRiskRatingQueryParams):
    """FMP ESG Risk Rating query.

    Source: https://site.financialmodelingprep.com/developer/docs/#Company-ESG-Risk-Ratings

    Parameter
    ---------
    symbol : str
        The symbol of the company.
    """


class FMPESGRiskRatingData(Data):
    symbol: str
    cik: int
    companyName: str
    industry: str
    year: int
    ESGRiskRating: ratings = Field(alias="esg_risk_rating")
    industryRank: str


class FMPESGRiskRatingFetcher(
    Fetcher[
        ESGRiskRatingQueryParams,
        ESGRiskRatingData,
        FMPESGRiskRatingQueryParams,
        FMPESGRiskRatingData,
    ]
):
    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FMPESGRiskRatingQueryParams:
        return FMPESGRiskRatingQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FMPESGRiskRatingQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any
    ) -> List[FMPESGRiskRatingData]:
        api_key = credentials.get("fmp_api_key") if credentials else ""

        url = create_url(
            4, "esg-environmental-social-governance-data-ratings", api_key, query
        )
        return get_data_many(url, FMPESGRiskRatingData, **kwargs)

    @staticmethod
    def transform_data(data: List[FMPESGRiskRatingData]) -> List[FMPESGRiskRatingData]:
        return data
