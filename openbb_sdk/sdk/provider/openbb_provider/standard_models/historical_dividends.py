"""Historical dividends data model."""


from datetime import date as dateType
from typing import Optional

from pydantic import Field, validator

from openbb_provider.abstract.data import Data
from openbb_provider.abstract.query_params import QueryParams
from openbb_provider.standard_models.base import BaseSymbol


class HistoricalDividendsQueryParams(QueryParams, BaseSymbol):
    """Historical dividends query."""


class HistoricalDividendsData(Data):
    """Historical dividends data."""

    date: dateType = Field(description="Date of the historical dividends.")
    label: str = Field(description="Label of the historical dividends.")
    adj_dividend: float = Field(
        description="Adjusted dividend of the historical dividends."
    )
    dividend: float = Field(description="Dividend of the historical dividends.")
    record_date: Optional[dateType] = Field(
        description="Record date of the historical dividends.", default=None
    )
    payment_date: Optional[dateType] = Field(
        description="Payment date of the historical dividends.", default=None
    )
    declaration_date: Optional[dateType] = Field(
        description="Declaration date of the historical dividends.", default=None
    )

    @validator("declaration_date", pre=True, check_fields=False)
    def declaration_date_validate(cls, v: str):  # pylint: disable=E0213
        """Validate declaration date."""
        if not isinstance(v, str):
            return v
        return dateType.fromisoformat(v) if v else None

    @validator("record_date", pre=True, check_fields=False)
    def record_date_validate(cls, v: str):  # pylint: disable=E0213
        """Record date validator."""
        if not isinstance(v, str):
            return v
        return dateType.fromisoformat(v) if v else None

    @validator("payment_date", pre=True, check_fields=False)
    def payment_date_validate(cls, v: str):  # pylint: disable=E0213
        """Payment date validator."""
        if not isinstance(v, str):
            return v
        return dateType.fromisoformat(v) if v else None
