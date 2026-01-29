"""综合领先指标标准模型。"""

from datetime import date as dateType

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import Field


class CompositeLeadingIndicatorQueryParams(QueryParams):
    """综合领先指标查询。"""

    start_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("start_date")
    )
    end_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("end_date")
    )


class CompositeLeadingIndicatorData(Data):
    """综合领先指标数据。"""

    date: dateType = Field(description=DATA_DESCRIPTIONS.get("date"))
    value: float = Field(
        default=None,
        description="CLI 值",
        json_schema_extra={"x-unit_measurement": "index"},
    )
    country: str = Field(description="CLI 值的国家。")
