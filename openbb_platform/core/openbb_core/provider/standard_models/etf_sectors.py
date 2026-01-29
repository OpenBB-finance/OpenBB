"""ETF 行业标准模型。"""

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import Field, field_validator


class EtfSectorsQueryParams(QueryParams):
    """ETF 行业查询。"""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", "") + " (ETF)")

    @field_validator("symbol")
    @classmethod
    def to_upper(cls, v: str) -> str:
        """将字段转换为大写。"""
        return v.upper()


class EtfSectorsData(Data):
    """ETF 行业数据。"""

    symbol: str | None = Field(
        default=None, description=DATA_DESCRIPTIONS.get("symbol", "")
    )
    sector: str = Field(description="风险敞口行业。")
    weight: float = Field(
        description="ETF 的行业敞口占总资产的百分比。",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
