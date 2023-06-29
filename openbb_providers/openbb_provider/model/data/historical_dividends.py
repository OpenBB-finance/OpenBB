"""Historical dividends data model."""

# IMPORT STANDARD
from datetime import date as dateType
from typing import Optional

# IMPORT THIRD-PARTY
# IMPORT INTERNAL
from openbb_provider.model.abstract.data import Data, QueryParams
from openbb_provider.model.data.base import BaseSymbol


class HistoricalDividendsQueryParams(QueryParams, BaseSymbol):
    """Historical dividends query.

    Parameter
    ---------
    symbol : str
        The symbol of the company.
    """

    __name__ = "HistoricalDividendsQueryParams"


class HistoricalDividendsData(Data):
    """Historical dividends data.

    Returns
    -------
    date : date
        The date of the historical dividends.
    label : str
        The label of the historical dividends.
    adj_dividend : float
        The adjusted dividend of the historical dividends.
    dividend : float
        The dividend of the historical dividends.
    record_date : date
        The record date of the historical dividends.
    payment_date : date
        The payment date of the historical dividends.
    declaration_date : date
        The declaration date of the historical dividends.
    """

    date: dateType
    label: str
    adj_dividend: float
    dividend: float
    record_date: Optional[dateType]
    payment_date: Optional[dateType]
    declaration_date: Optional[dateType]
