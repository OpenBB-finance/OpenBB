"""ESG Score data model."""


from datetime import date, datetime

from openbb_provider.abstract.data import Data
from openbb_provider.abstract.query_params import QueryParams
from openbb_provider.standard_models.base import BaseSymbol


class ESGScoreQueryParams(QueryParams, BaseSymbol):
    """ESG score query model.

    Parameter
    ---------
    symbol : str
        The symbol of the company.
    """


class ESGScoreData(Data):
    """ESG Score data.

    Returns
    -------
    symbol : str
        The symbol of the asset.
    cik : int
        The CIK of the ESG Score.
    company_name : str
        The company name of the ESG Score.
    form_type : str
        The form type of the ESG Score.
    accepted_date : datetime
        The accepted date of the ESG Score.
    date : date
        The date of the ESG Score.
    environmental_score : float
        The environmental score of the ESG Score.
    social_score : float
        The social score of the ESG Score.
    governance_score : float
        The governance score of the ESG Score.
    esg_score : float
        The ESG score of the ESG Score.
    url : str
        The URL of the ESG Score.
    """

    symbol: str
    cik: int
    company_name: str
    form_type: str
    accepted_date: datetime
    date: date
    environmental_score: float
    social_score: float
    governance_score: float
    esg_score: float
    url: str
