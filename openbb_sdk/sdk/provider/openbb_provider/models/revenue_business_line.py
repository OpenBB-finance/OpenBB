"""Revenue by business line data model."""


from datetime import date
from typing import Dict, Literal

from pydantic import Field

from openbb_provider.abstract.data import Data, QueryParams
from openbb_provider.metadata import DESCRIPTIONS
from openbb_provider.models.base import BaseSymbol


class RevenueBusinessLineQueryParams(QueryParams, BaseSymbol):
    """Revenue business line query.


    Parameter
    ---------
    symbol : str
        The symbol of the company.
    period : Literal["quarterly", "annually"]
        The period of the income statement.
    structure : Literal["hierarchical", "flat"]
        The structure of the revenue business line. Should always be flat.
    """

    period: Literal["quarterly", "annually"] = Field(
        default="quarterly", description=DESCRIPTIONS.get("period", "")
    )
    structure: Literal["hierarchical", "flat"] = Field(
        default="flat"
    )  # should always be flat


class RevenueBusinessLineData(Data):
    """Revenue by business line data.

    Returns
    -------
    date : date
        The date of the revenue.
    data_and_service : Dict[str, int]
        The data and service of the revenue.
    """

    date: date
    data_and_service: Dict[str, int]
