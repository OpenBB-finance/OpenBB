"""Yield Curve Standard Model."""

from datetime import date as dateType
from typing import Optional, Union

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import Field, computed_field, field_validator


class YieldCurveQueryParams(QueryParams):
    """Yield Curve Query."""

    date: Optional[Union[dateType, str]] = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("date", "")
        + " By default is the current data.",
    )

    @field_validator("date", mode="before", check_fields=False)
    @classmethod
    def _validate_date(cls, v):
        """Validate the date."""
        # pylint: disable=import-outside-toplevel
        from pandas import to_datetime

        if v is None:
            return None
        if isinstance(v, dateType):
            return v.strftime("%Y-%m-%d")
        new_dates: list = []
        if isinstance(v, str):
            dates = v.split(",")
        if isinstance(v, list):
            dates = v
        for date in dates:
            new_dates.append(to_datetime(date).date().strftime("%Y-%m-%d"))

        return ",".join(new_dates) if new_dates else None


class YieldCurveData(Data):
    """Yield Curve Data."""

    date: Optional[dateType] = Field(
        default=None,
        description=DATA_DESCRIPTIONS.get("date", ""),
    )
    maturity: str = Field(description="Maturity length of the security.")

    @computed_field(
        description="Maturity length as a decimal.",
        return_type=Optional[float],
    )
    @property
    def maturity_years(self) -> Optional[float]:
        """Get the maturity in years as a decimal."""
        if self.maturity is None or "_" not in self.maturity:
            return None

        parts = self.maturity.split("_")
        months = 0
        for i in range(0, len(parts), 2):
            number = int(parts[i + 1])
            if parts[i] == "year":
                number *= 12
            months += number

        return months / 12
