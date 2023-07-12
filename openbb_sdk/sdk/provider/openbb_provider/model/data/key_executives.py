"""Key Executives Data Model."""


from datetime import datetime
from typing import Optional

from openbb_provider.model.abstract.data import Data, QueryParams
from openbb_provider.model.data.base import BaseSymbol


class KeyExecutivesQueryParams(QueryParams, BaseSymbol):
    """Key executives query.

    Parameter
    ---------
    symbol : str
        The symbol of the company.
    key_executive_name : Optional[str]
        The name of the key executive to be retrieved.
    key_executive_title : Optional[str]
        The title of the key executive to be retrieved.
    key_executive_title_since : Optional[datetime]
        The period since the position of the key executive to be retrieved.
    key_executive_year_born : Optional[datetime]
        The year born of the key executive to be retrieved.
    key_executive_gender: Optional[str]
        The gender of the key executive to be retrieved.
    """

    key_executive_name: Optional[str]
    key_executive_title: Optional[str]
    key_executive_title_since: Optional[datetime]
    key_executive_year_born: Optional[datetime]
    key_executive_gender: Optional[str]


class KeyExecutivesData(Data):
    """Key Executives Data.

    Returns
    -------
    name : Optional[str]
        The name of the key executive.
    title : Optional[str]
        The title of the key executive.
    title_since : Optional[datetime]
        The title since of the key executive.
    year_born : Optional[datetime]
        The year born of the key executive.
    gender : Optional[str]
        The gender of the key executive.
    """

    name: Optional[str]
    title: Optional[str]
    title_since: Optional[datetime]
    year_born: Optional[datetime]
    gender: Optional[str]
