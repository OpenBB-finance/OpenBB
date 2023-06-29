"""Revenue by business line data model."""

# IMPORT STANDARD
from datetime import date
from typing import Dict, Literal

# IMPORT THIRD-PARTY
from pydantic import Field

from openbb_provider.metadata import DESCRIPTIONS

# IMPORT INTERNAL
from openbb_provider.model.abstract.data import Data, QueryParams
from openbb_provider.model.data.base import BaseSymbol


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

    __name__ = "RevenueBusinessLineQueryParams"
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
