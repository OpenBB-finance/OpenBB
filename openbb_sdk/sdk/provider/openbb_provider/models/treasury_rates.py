"""Treasury Rates Data Model."""


from datetime import (
    date as dateType,
    datetime,
)
from typing import Optional

from pydantic import Field

from openbb_provider.abstract.data import Data, QueryParams
from openbb_provider.metadata import DESCRIPTIONS


class TreasuryRatesQueryParams(QueryParams):
    """Treasury Rates query.

    Parameter
    ---------
    start_date : Optional[str]
        Start date of the data, default is None.
    end_date : Optional[str]
        End date of the data, default is today.
    """

    start_date: Optional[str] = Field(
        default=None, description=DESCRIPTIONS["start_date"]
    )
    end_date: Optional[str] = Field(
        default=datetime.today().strftime("%Y-%m-%d"),
        description=DESCRIPTIONS["end_date"],
    )


class TreasuryRatesData(Data):
    """Return Treasury Rates Data.

    Returns
    -------
    date : dateType
        The date of the treasury rates.
    month_1 : float
        The 1 month treasury rate.
    month_2 : float
        The 2 month treasury rate.
    month_3 : float
        The 3 month treasury rate.
    month_6 : float
        The 6 month treasury rate.
    year_1 : float
        The 1 year treasury rate.
    year_2 : float
        The 2 year treasury rate.
    year_3 : float
        The 3 year treasury rate.
    year_5 : float
        The 5 year treasury rate.
    year_7 : float
        The 7 year treasury rate.
    year_10 : float
        The 10 year treasury rate.
    year_20 : float
        The 20 year treasury rate.
    year_30 : float
        The 30 year treasury rate.
    """

    date: dateType
    month_1: float
    month_2: float
    month_3: float
    month_6: float
    year_1: float
    year_2: float
    year_3: float
    year_5: float
    year_7: float
    year_10: float
    year_20: float
    year_30: float
