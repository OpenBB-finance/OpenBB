"""Stock Split Calendar data model."""


from datetime import (
    date as dateType,
    datetime,
    timedelta,
)

from pydantic import Field

from openbb_provider.metadata import DESCRIPTIONS
from openbb_provider.model.abstract.data import Data, QueryParams


class StockSplitCalendarQueryParams(QueryParams):
    """Stock Split Calendar query model.

    Parameter
    ---------
    start_date : date
        The start date of the stock splits from which to retrieve the data.
    end_date : date
        The end date of the stock splits up to which to retrieve the data.
    """

    start_date: dateType = Field(
        description=DESCRIPTIONS.get("start_date", ""),
        default=(datetime.now() - timedelta(days=90)).date(),
    )
    end_date: dateType = Field(
        description=DESCRIPTIONS.get("end_date", ""),
        default=datetime.now().date(),
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
