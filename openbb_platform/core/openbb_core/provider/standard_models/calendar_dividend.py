"""Dividend Calendar Standard Model."""

from datetime import date as dateType

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import Field


class CalendarDividendQueryParams(QueryParams):
    """Dividend Calendar Query."""

    start_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("start_date", "")
    )
    end_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("end_date", "")
    )


class CalendarDividendData(Data):
    """Dividend Calendar Data."""

    ex_dividend_date: dateType = Field(
        description="The ex-dividend date - the date on which the stock begins trading without rights to the dividend."
    )
    symbol: str = Field(description=DATA_DESCRIPTIONS.get("symbol", ""))
    amount: float | None = Field(
        default=None, description="The dividend amount per share."
    )
    name: str | None = Field(default=None, description="Name of the entity.")
    record_date: dateType | None = Field(
        default=None,
        description="The record date of ownership for eligibility.",
    )
    payment_date: dateType | None = Field(
        default=None,
        description="The payment date of the dividend.",
    )
    declaration_date: dateType | None = Field(
        default=None,
        description="Declaration date of the dividend.",
    )
