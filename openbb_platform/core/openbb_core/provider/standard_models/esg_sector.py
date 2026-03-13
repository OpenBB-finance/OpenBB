"""ESG Sector Standard Model."""

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams


class ESGSectorQueryParams(QueryParams):
    """ESG Sector Query.

    Parameter
    ---------
    year : int
        The year to get ESG information for
    """

    year: int


class ESGSectorData(Data):
    """ESG Sector Data.

    Returns
    -------
    year : int
        The year of the ESG Sector.
    sector : str
        The sector of the ESG Sector.
    environmental_score : float
        The environmental score of the ESG Sector.
    social_score : float
        The social score of the ESG Sector.
    governance_score : float
        The governance score of the ESG Sector.
    esg_score : float
        The ESG score of the ESG Sector.
    """

    year: int
    sector: str
    environmental_score: float
    social_score: float
    governance_score: float
    esg_score: float
