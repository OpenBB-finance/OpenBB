"""实际 GDP 标准模型。"""

from datetime import date as dateType

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import Field


class GdpRealQueryParams(QueryParams):
    """实际 GDP 查询。"""

    start_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("start_date")
    )
    end_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("end_date")
    )


class GdpRealData(Data):
    """实际 GDP 数据。"""

    date: dateType = Field(description=DATA_DESCRIPTIONS.get("date"))
    country: str = Field(
        default=None, description="由实际 GDP 值代表的国家。"
    )
    value: int | float = Field(
        description="该国家和日期的实际 GDP 值。",
    )
