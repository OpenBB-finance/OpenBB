"""SEC filings data model."""


from datetime import date as dateType
from typing import Optional

from openbb_provider.abstract.data import Data, QueryParams
from openbb_provider.models.base import BaseSymbol


class SECFilingsQueryParams(QueryParams, BaseSymbol):
    """SEC Filings query model.
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

    symbol: str
    type: Optional[str] = None
    page: Optional[int] = 0
    limit: Optional[int] = None


class SECFilingsData(Data):
    """SEC filings data.

    Returns
    -------
    symbol : str
        The symbol of the stock.
    filling_date : date
        The filling date of the SEC filing.
    accepted_date : date
        The accepted date of the SEC filing.
    cik : str
        The CIK of the SEC filing.
    type : str
        The type of the SEC filing.
    link : str
        The link of the SEC filing.
    final_link : str
        The final link of the SEC filing.
    """

    symbol: str
    filling_date: dateType
    accepted_date: dateType
    cik: Optional[str]
    type: str
    link: str
    final_link: str
