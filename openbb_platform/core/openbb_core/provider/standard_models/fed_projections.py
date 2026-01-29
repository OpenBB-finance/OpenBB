"""预测标准模型。"""

from datetime import date as dateType

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import DATA_DESCRIPTIONS
from pydantic import Field


class PROJECTIONQueryParams(QueryParams):
    """预测查询。"""


class PROJECTIONData(Data):
    """预测数据。"""

    date: dateType = Field(description=DATA_DESCRIPTIONS.get("date", ""))
    range_high: float | None = Field(description="利率的高预测值。")
    central_tendency_high: float | None = Field(
        description="利率高预测值的集中趋势。"
    )
    median: float | None = Field(description="利率的中位数预测值。")
    range_midpoint: float | None = Field(description="利率的中点预测值。")
    central_tendency_midpoint: float | None = Field(
        description="利率中点预测值的集中趋势。"
    )
    range_low: float | None = Field(description="利率的低预测值。")
    central_tendency_low: float | None = Field(
        description="利率低预测值的集中趋势。"
    )
