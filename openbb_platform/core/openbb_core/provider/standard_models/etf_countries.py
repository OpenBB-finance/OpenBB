"""ETF 国家标准模型。"""

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import Field, field_validator


class EtfCountriesQueryParams(QueryParams):
    """ETF 国家查询。"""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", ""))

    @field_validator("symbol")
    @classmethod
    def to_upper(cls, v: str) -> str:
        """将字段转换为大写。"""
        return v.upper()


class EtfCountriesData(Data):
    """ETF 国家数据。"""

    symbol: str | None = Field(
        default=None, description=DATA_DESCRIPTIONS.get("symbol", "")
    )
    country: str = Field(
        description="风险敞口所在的国家/地区。对应的值是归一化的百分比点数。"
    )
    weight: float = Field(
        description="ETF 对该国家/地区的净敞口，占 ETF 总资产的百分比。",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
