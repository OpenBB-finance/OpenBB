"""ETF 股票敞口标准模型。"""

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from pydantic import Field, field_validator


class EtfEquityExposureQueryParams(QueryParams):
    """ETF 股票敞口查询参数。"""

    symbol: str = Field(
        description=QUERY_DESCRIPTIONS.get("symbol", "") + " (标的股票)"
    )

    @field_validator("symbol")
    @classmethod
    def to_upper(cls, v: str) -> str:
        """将字段转换为大写。"""
        return v.upper()


class EtfEquityExposureData(Data):
    """ETF 股票敞口数据。"""

    equity_symbol: str = Field(description="请求的股票代码。")
    etf_symbol: str = Field(
        description="对请求的股票有风险敞口的 ETF 代码。"
    )
    weight: float | None = Field(
        default=None,
        description="ETF 中股票的权重，作为归一化百分比。",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    market_value: int | float | None = Field(
        default=None,
        description="ETF 中股票头寸的市场价值。",
    )
    shares: int | float | None = Field(
        default=None,
        description="ETF 控制的报告股票数量。",
    )
