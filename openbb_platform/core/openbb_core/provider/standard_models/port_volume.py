"""港口吞吐量标准模型。"""

from datetime import date as dateType

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import Field


class PortVolumeQueryParams(QueryParams):
    """港口吞吐量查询。"""

    start_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("start_date", "")
    )
    end_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("end_date", "")
    )


class PortVolumeData(Data):
    """港口吞吐量数据。"""

    date: dateType = Field(description=DATA_DESCRIPTIONS.get("date", ""))
    port_code: str | None = Field(default=None, description="港口代码。")
    port_name: str | None = Field(default=None, description="港口名称。")
    country: str | None = Field(
        default=None, description="港口所属国家。"
    )
