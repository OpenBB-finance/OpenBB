"""收益率曲线标准模型。"""

from datetime import date as dateType

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import Field, computed_field, field_validator


class YieldCurveQueryParams(QueryParams):
    """收益率曲线查询。"""

    date: dateType | str | None = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("date", "")
        + " 默认是当前数据。",
    )

    @field_validator("date", mode="before", check_fields=False)
    @classmethod
    def _validate_date(cls, v):
        """验证日期。"""
        # pylint: disable=import-outside-toplevel
        from pandas import to_datetime

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
    """收益率曲线数据。"""

    date: dateType | None = Field(
        default=None,
        description=DATA_DESCRIPTIONS.get("date", ""),
    )
    maturity: str = Field(description="证券的到期时长。")

    @computed_field(  # type: ignore
        description="到期时长，以年为单位，表示为小数。",
        return_type=float | None,
    )
    @property
    def maturity_years(self) -> float | None:
        """获取以年为单位的到期时长小数。"""
        if "_" not in self.maturity:  # pylint: disable=E1135
            return None

        parts = self.maturity.split("_")  # pylint: disable=E1101
        months = sum(
            int(parts[i + 1]) * (12 if parts[i] == "year" else 1)
            for i in range(0, len(parts), 2)
        )

        return months / 12
