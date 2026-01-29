"""FRED 发布表标准模型。"""

from datetime import date as dateType

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import Field, field_validator


class ReleaseTableQueryParams(QueryParams):
    """FRED 发布表查询。"""

    release_id: str = Field(
        description="发布的 ID。" + " 使用 `fred_search` 寻找发布项目。",
    )
    element_id: str | None = Field(
        default=None,
        description="发布项目中特定表格的元素 ID。",
    )
    date: None | dateType | str = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("date", ""),
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
        if isinstance(v, str):
            dates = v.split(",")
        if isinstance(v, list):
            dates = v
        for date in dates:
            new_dates.append(to_datetime(date).date().strftime("%Y-%m-%d"))

        return ",".join(new_dates) if new_dates else None


class ReleaseTableData(Data):
    """FRED 发布表数据。"""

    date: dateType | None = Field(
        default=None, description=DATA_DESCRIPTIONS.get("date", "")
    )
    level: int | None = Field(
        default=None,
        description="元素的缩进级别。",
    )
    element_type: str | None = Field(
        default=None,
        description="元素类型。",
    )
    line: int | None = Field(
        default=None,
        description="元素的行号。",
    )
    element_id: str | None = Field(
        default=None,
        description="父/子关系中的元素 ID。",
    )
    parent_id: str | None = Field(
        default=None,
        description="父/子关系中的父 ID。",
    )
    children: str | None = Field(
        default=None,
        description="每个子元素的 element_id，以逗号分隔的字符串。",
    )
    symbol: str | None = Field(
        default=None,
        description=DATA_DESCRIPTIONS.get("symbol", ""),
    )
    name: str | None = Field(
        default=None,
        description="系列的名称。",
    )
    value: float | None = Field(
        default=None,
        description="系列的报告值。",
    )
