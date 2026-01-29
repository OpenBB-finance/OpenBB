"""贸易方向标准模型。"""

from datetime import date as dateType
from typing import Literal

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import Field


class DirectionOfTradeQueryParams(QueryParams):
    """贸易方向查询。"""

    __json_schema_extra__ = {
        "direction": {
            "choices": ["exports", "imports", "balance", "all"],
        },
        "frequency": {
            "choices": ["month", "quarter", "annual"],
        },
    }

    country: str | None = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("country", "")
        + " None 等同于 'all'。如果使用了 'all'，则对应方字段不能为 'all'。",
    )
    counterpart: str | None = Field(
        default=None,
        description="贸易对应国家。None 等同于 'all'。"
        + " 如果使用了 'all'，则国家字段不能为 'all'。",
    )
    direction: Literal["exports", "imports", "balance", "all"] = Field(
        default="balance",
        description="贸易方向。使用 'all' 获取此维度的所有数据。",
    )
    start_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("start_date", "")
    )
    end_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("end_date", "")
    )
    frequency: Literal["month", "quarter", "annual"] = Field(
        default="month", description=QUERY_DESCRIPTIONS.get("frequency", "")
    )


class DirectionOfTradeData(Data):
    """贸易方向数据。"""

    date: dateType = Field(description=DATA_DESCRIPTIONS.get("date", ""))
    symbol: str | None = Field(
        default=None, description=DATA_DESCRIPTIONS.get("symbol", "")
    )
    country: str = Field(description=DATA_DESCRIPTIONS.get("country", ""))
    counterpart: str = Field(description="贸易对应国家或地区。")
    title: str | None = Field(
        default=None, description="符号对应的标题。"
    )
    value: float = Field(description="贸易值。")
    scale: str | None = Field(default=None, description="值的缩放比例。")
