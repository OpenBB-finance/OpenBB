"""ETF 信息标准模型。"""

from datetime import date as dateType

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import Field, field_validator


class EtfInfoQueryParams(QueryParams):
    """ETF 信息查询。"""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", "") + " (ETF)")

    @field_validator("symbol")
    @classmethod
    def to_upper(cls, v: str) -> str:
        """将字段转换为大写。"""
        return v.upper()


class EtfInfoData(Data):
    """ETF 信息数据。"""

    symbol: str = Field(description=DATA_DESCRIPTIONS.get("symbol", "") + " (ETF)")
    name: str | None = Field(description="ETF 名称。")
    issuer: str | None = Field(default=None, description="ETF 发行人。")
    domicile: str | None = Field(default=None, description="ETF 注册地。")
    website: str | None = Field(default=None, description="ETF 网站。")
    description: str | None = Field(
        default=None, description="基金描述。"
    )
    inception_date: dateType | None = Field(
        default=None, description="ETF 成立日期。"
    )
