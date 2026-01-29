"""期权快照标准模型。"""

from datetime import (
    date as dateType,
    datetime,
)

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import DATA_DESCRIPTIONS
from pydantic import Field


class OptionsSnapshotsQueryParams(QueryParams):
    """期权快照查询。"""


class OptionsSnapshotsData(Data):
    """期权快照数据。"""

    underlying_symbol: list[str] = Field(
        description="标的资产的股票代码。"
    )
    contract_symbol: list[str] = Field(description="期权合约代码。")
    expiration: list[dateType] = Field(
        description="期权合约到期日。"
    )
    dte: list[int | None] = Field(
        default_factory=list,
        description="期权合约距离到期天数。",
    )
    strike: list[float] = Field(
        description="期权合约执行价。",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    option_type: list[str] = Field(description="期权类型。")
    volume: list[int | None] = Field(
        default_factory=list,
        description=DATA_DESCRIPTIONS.get("volume", ""),
    )
    open_interest: list[int | None] = Field(
        default_factory=list,
        description="当时的持仓量。",
    )
    last_price: list[float | None] = Field(
        default_factory=list,
        description="当时的最新成交价。",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    last_size: list[int | None] = Field(
        default_factory=list,
        description="最新成交的批量大小。",
    )
    last_timestamp: list[datetime | None] = Field(
        default_factory=list,
        description="最新价格的时间戳。",
    )
    open: list[float | None] = Field(
        default_factory=list,
        description=DATA_DESCRIPTIONS.get("open", ""),
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    high: list[float | None] = Field(
        default_factory=list,
        description=DATA_DESCRIPTIONS.get("high", ""),
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    low: list[float | None] = Field(
        default_factory=list,
        description=DATA_DESCRIPTIONS.get("low", ""),
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    close: list[float | None] = Field(
        default_factory=list,
        description=DATA_DESCRIPTIONS.get("close", ""),
        json_schema_extra={"x-unit_measurement": "currency"},
    )
