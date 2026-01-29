"""目标价共识标准模型。"""

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import Field, field_validator


class PriceTargetConsensusQueryParams(QueryParams):
    """目标价共识查询。"""

    symbol: str | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("symbol", "")
    )

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def to_upper(cls, v):
        """将字段转换为大写。"""
        return v.upper() if v else None


class PriceTargetConsensusData(Data):
    """目标价共识数据。"""

    symbol: str = Field(description=DATA_DESCRIPTIONS.get("symbol", ""))
    name: str | None = Field(default=None, description="公司名称")
    target_high: float | None = Field(
        default=None, description="目标价共识中的最高目标价。"
    )
    target_low: float | None = Field(
        default=None, description="目标价共识中的最低目标价。"
    )
    target_consensus: float | None = Field(
        default=None, description="目标价共识中的共识目标价。"
    )
    target_median: float | None = Field(
        default=None, description="目标价共识中的中数目标价。"
    )
