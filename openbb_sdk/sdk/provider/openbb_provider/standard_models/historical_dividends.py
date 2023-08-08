"""Historical dividends data model."""


from datetime import date as dateType
from typing import Optional

from pydantic import Field

from openbb_provider.abstract.data import Data
from openbb_provider.abstract.query_params import QueryParams
from openbb_provider.standard_models.base import BaseSymbol


class HistoricalDividendsQueryParams(QueryParams, BaseSymbol):
    """Historical dividends query."""


class HistoricalDividendsData(Data):
    """Historical dividends data."""

    date: dateType = Field(description="The date of the historical dividends.")
    label: str = Field(description="The label of the historical dividends.")
    adj_dividend: float = Field(
        description="The adjusted dividend of the historical dividends."
    )
    dividend: float = Field(description="The dividend of the historical dividends.")
    record_date: Optional[dateType] = Field(
        description="The record date of the historical dividends."
    )
    payment_date: Optional[dateType] = Field(
        description="The payment date of the historical dividends."
    )
    declaration_date: Optional[dateType] = Field(
        description="The declaration date of the historical dividends."
    )
