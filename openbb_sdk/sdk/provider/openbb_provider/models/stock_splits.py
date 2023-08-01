"""Stock Split Calendar data model."""


from datetime import date as dateType
from typing import Optional

from pydantic import Field

from openbb_provider.abstract.data import Data
from openbb_provider.abstract.query_params import QueryParams
from openbb_provider.descriptions import QUERY_DESCRIPTIONS


class StockSplitCalendarQueryParams(QueryParams):
    """Stock Split Calendar query model.

    Parameter
    ---------
    start_date : date
        The start date of the stock splits from which to retrieve the data.
    end_date : date
        The end date of the stock splits up to which to retrieve the data.
    """

    start_date: Optional[dateType] = Field(
        description=QUERY_DESCRIPTIONS.get("start_date", ""), default=None
    )
    end_date: Optional[dateType] = Field(
        description=QUERY_DESCRIPTIONS.get("end_date", ""), default=None
    )


class StockSplitCalendarData(Data):
    """Stock Split Calendar data.

    Returns
    -------
    date : date
        The date of the stock splits.
    label : str
        The label of the stock splits.
    symbol : str
        The symbol of the company.
    numerator : float
        The numerator of the stock splits.
    denominator : float
        The denominator of the stock splits.
    """

    date: dateType
    label: str
    symbol: str
    numerator: float
    denominator: float
