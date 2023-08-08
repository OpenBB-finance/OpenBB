"""ESG Risk Rating data model."""


from typing import Literal

from openbb_provider.abstract.data import Data
from openbb_provider.abstract.query_params import QueryParams
from openbb_provider.standard_models.base import BaseSymbol


class ESGRiskRatingQueryParams(QueryParams, BaseSymbol):
    """ESG risk rating query model.

    Parameter
    ---------
    symbol : str
        The symbol of the company.
    """


class ESGRiskRatingData(Data, BaseSymbol):
    """ESG Risk Rating data.

    Returns
    -------
    symbol : str
        The symbol of the asset.
    cik : int
        The CIK of the ESG Risk Rating.
    company_name : str
        The company name of the ESG Risk Rating.
    industry : str
        The industry of the ESG Risk Rating.
    year : int
        The year of the ESG Risk Rating.
    esg_risk_rating : str
        The ESG Risk Rating of the ESG Risk Rating.
    industry_rank : str
        The industry rank of the ESG Risk Rating.
    """

    cik: int
    company_name: str
    industry: str
    year: int
    esg_risk_rating: Literal[
        "A+", "A", "A-", "B+", "B", "B-", "C+", "C", "C-", "D+", "D", "D-", "F"
    ]
    industry_rank: str
