"""Dividend Calendar data model."""


from datetime import (
    date as dateType,
    datetime,
    timedelta,
)
from typing import Optional

from pydantic import Field, NonNegativeFloat

from openbb_provider.abstract.data import Data, QueryParams
from openbb_provider.metadata import QUERY_DESCRIPTIONS


class DividendCalendarQueryParams(QueryParams):
    """Dividend Calendar query.

    The maximum time interval between the start and end date can be 3 months.
    Default value for time interval is 1 month.

    Parameter
    ---------
    start_date : date
        The starting date to fetch the dividend calendar from. Default value is the
        previous day from the last month.
    end_date : date
        The ending date to fetch the dividend calendar till. Default value is the
        previous day from the current month.
    """

    start_date: Optional[dateType] = Field(
        description=QUERY_DESCRIPTIONS.get("start_date", ""),
        default=datetime.now().date() - timedelta(days=31),
    )
    end_date: Optional[dateType] = Field(
        description=QUERY_DESCRIPTIONS.get("end_date", ""),
        default=datetime.now().date() - timedelta(days=1),
    )


class DividendCalendarData(Data):
    """Dividend Calendar data.

    Returns
    -------
    date : dateType
        The date of the dividend in the calendar.
    label : str
        The date in human readable form in the calendar.
    adjDividend : Optional[NonNegativeFloat]
        The adjusted dividend on a date in the calendar.
    symbol : str
        The symbol of the company for which the dividend is returned in the calendar.
    dividend : Optional[NonNegativeFloat]
        The dividend amount in the calendar.
    recordDate : Optional[dateType]
        The record date of the dividend in the calendar.
    paymentDate : Optional[dateType]
        The payment date of the dividend in the calendar.
    declarationDate : Optional[dateType]
        The declaration date of the dividend in the calendar.
    """

    date: dateType
    label: str
    adjDividend: Optional[NonNegativeFloat] = Field(alias="adj_dividend")
    symbol: str
    dividend: Optional[NonNegativeFloat]
    recordDate: Optional[dateType] = Field(alias="record_date")
    paymentDate: Optional[dateType] = Field(alias="payment_date")
    declarationDate: Optional[dateType] = Field(alias="declaration_date")
