"""Yield Curve Standard Model."""

from datetime import date as dateType

from pydantic import Field, computed_field, field_validator

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)


class YieldCurveQueryParams(QueryParams):
    """Yield Curve Query."""

    date: dateType | str | None = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("date", "")
        + " By default is the current data.",
    )

    @field_validator("date", mode="before", check_fields=False)
    @classmethod
    def _validate_date(cls, v):
        """Validate the date."""
        from openbb_core.app.utils_optional import require_optional

        to_datetime = require_optional("pandas").to_datetime  # type: ignore[union-attr]

        if v is None:
            return None
        if isinstance(v, dateType):
            return v.strftime("%Y-%m-%d")
        new_dates: list = []
        dates: list = []
        if isinstance(v, str):
            dates = v.split(",")
        elif isinstance(v, list):
            dates = v
        for date in dates:
            new_dates.append(to_datetime(date).date().strftime("%Y-%m-%d"))

        return ",".join(new_dates) if new_dates else None


class YieldCurveData(Data):
    """Yield Curve Data."""

    date: dateType | None = Field(
        default=None,
        description=DATA_DESCRIPTIONS.get("date", ""),
    )
    maturity: str = Field(description="Maturity length of the security.")

    @computed_field(
        description="Maturity length, in years, as a decimal.",
        return_type=float | None,
    )
    @property
    def maturity_years(self) -> float | None:
        """Get the maturity in years as a decimal."""
        if "_" not in self.maturity:
            return None

        parts = self.maturity.split("_")
        months = sum(
            int(parts[i + 1]) * (12 if parts[i] == "year" else 1)
            for i in range(0, len(parts), 2)
        )

        return months / 12
