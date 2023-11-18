"""Historical Dividends Standard Model."""


from datetime import date as dateType
from typing import List, Optional, Set, Union

from pydantic import Field, field_validator

from openbb_provider.abstract.data import Data
from openbb_provider.abstract.query_params import QueryParams
from openbb_provider.utils.descriptions import DATA_DESCRIPTIONS, QUERY_DESCRIPTIONS


class HistoricalDividendsQueryParams(QueryParams):
    """Historical Dividends Query."""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", ""))

    @field_validator("symbol", mode="before", check_fields=False)
    def upper_symbol(cls, v: Union[str, List[str], Set[str]]):  # pylint: disable=E0213
        """Convert symbol to uppercase."""
        if isinstance(v, str):
            return v.upper()
        return ",".join([symbol.upper() for symbol in list(v)])


class HistoricalDividendsData(Data):
    """Historical Dividends Data."""

    date: dateType = Field(description=DATA_DESCRIPTIONS.get("date", ""))
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

    @field_validator("declaration_date", mode="before", check_fields=False)
    @classmethod
    def declaration_date_validate(cls, v: str):  # pylint: disable=E0213
        """Validate declaration date."""
        if not isinstance(v, str):
            return v
        return dateType.fromisoformat(v) if v else None

    @field_validator("record_date", mode="before", check_fields=False)
    @classmethod
    def record_date_validate(cls, v: str):  # pylint: disable=E0213
        """Record date validator."""
        if not isinstance(v, str):
            return v
        return dateType.fromisoformat(v) if v else None

    @field_validator("payment_date", mode="before", check_fields=False)
    @classmethod
    def payment_date_validate(cls, v: str):  # pylint: disable=E0213
        """Payment date validator."""
        if not isinstance(v, str):
            return v
        return dateType.fromisoformat(v) if v else None
