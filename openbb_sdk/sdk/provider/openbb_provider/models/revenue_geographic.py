"""Revenue by geographic segments data model."""


from datetime import date
from typing import Literal, Optional

from pydantic import Field

from openbb_provider.abstract.data import Data, QueryParams
from openbb_provider.metadata import QUERY_DESCRIPTIONS
from openbb_provider.models.base import BaseSymbol


class RevenueGeographicQueryParams(QueryParams, BaseSymbol):
    """Revenue geographic query.

    Parameter
    ---------
    symbol : str
        The symbol of the company.
    period : Literal["quarterly", "annually"]
        The period of the income statement.
    structure : Literal["hierarchical", "flat"]
        The structure of the revenue geographic. Should always be flat.
    """

    period: Literal["quarterly", "annually"] = Field(
        default="quarterly", description=QUERY_DESCRIPTIONS.get("period", "")
    )
    structure: Literal["hierarchical", "flat"] = Field(
        default="flat"
    )  # should always be flat


class RevenueGeographicData(Data):
    """Revenue by geographic segments data.

    Returns
    -------
    date : date
        The date of the revenue.
    americas : Optional[int]
        The revenue of the America segment.
    europe : Optional[int]
        The revenue of the Europe segment.
    greater_china : Optional[int]
        The revenue of the Greater China segment.
    japan : Optional[int]
        The revenue of the Japan segment.
    rest_of_asia_pacific : Optional[int]
        The revenue of the Rest of Asia Pacific segment.
    """

    date: date
    americas: Optional[int]
    europe: Optional[int]
    greater_china: Optional[int]
    japan: Optional[int]
    rest_of_asia_pacific: Optional[int]
