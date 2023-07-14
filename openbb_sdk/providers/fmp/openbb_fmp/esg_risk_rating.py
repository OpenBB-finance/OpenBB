"""FMP ESG Risk Rating fetcher."""

# IMPORT STANDARD
from datetime import date
from typing import Dict, List, Literal, Optional

# IMPORT INTERNAL
from openbb_provider.abstract.data import Data
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.helpers import data_transformer
from openbb_provider.models.esg_risk_rating import (
    ESGRiskRatingData,
    ESGRiskRatingQueryParams,
)
from pydantic import Field

# IMPORT THIRD-PARTY
from .helpers import create_url, get_data_many

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
    def transform_query(
        query: ESGRiskRatingQueryParams, extra_params: Optional[Dict] = None
    ) -> FMPESGRiskRatingQueryParams:
        return FMPESGRiskRatingQueryParams.parse_obj(query)

    @staticmethod
    def extract_data(
        query: FMPESGRiskRatingQueryParams, api_key: str
    ) -> List[FMPESGRiskRatingData]:
        url = create_url(
            4, "esg-environmental-social-governance-data-ratings", api_key, query
        )
        return get_data_many(url, FMPESGRiskRatingData)

    @staticmethod
    def transform_data(data: List[FMPESGRiskRatingData]) -> List[ESGRiskRatingData]:
        return data_transformer(data, ESGRiskRatingData)
