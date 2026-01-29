"""货币快照标准模型。"""

from typing import Literal

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import DATA_DESCRIPTIONS
from pydantic import Field, field_validator


class CurrencySnapshotsQueryParams(QueryParams):
    """货币快照查询参数。"""

    base: str = Field(description="基础货币符号。", default="usd")
    quote_type: Literal["direct", "indirect"] = Field(
        description="报价是直接还是间接。"
        + " 选择 'direct' 将返回汇率"
        + " 即购买一单位外币所需的本国货币数量。"
        + " 选择 'indirect' (默认) 将返回汇率"
        + " 即购买一单位本国货币所需的外币数量。",
        default="indirect",
    )
    counter_currencies: str | list[str] | None = Field(
        description="可选的计价货币符号列表，用于筛选。"
        + " None 返回所有。",
        default=None,
    )

    @field_validator("base", mode="before", check_fields=False)
    @classmethod
    def to_upper(cls, v):
        """将基础货币转换为大写。"""
        return v.upper()

    @field_validator("counter_currencies", mode="before", check_fields=False)
    @classmethod
    def convert_string(cls, v):
        """将计价货币转换为大写字符串列表。"""
        if v is not None:
            return ",".join(v).upper() if isinstance(v, list) else v.upper()
        return None


class CurrencySnapshotsData(Data):
    """货币快照数据。"""

    base_currency: str = Field(description="基础货币或本国货币。")
    counter_currency: str = Field(description="计价货币或外币。")
    last_rate: float = Field(
        description="相对于基础货币的汇率。"
        + " 汇率表示为出售一单位基础货币收到的外币数量，"
        + " 或购买一单位本国货币所需的外币数量。"
        + " 要反转视角，请将 'quote_type' 参数设置为 'direct'。",
    )
    open: float | None = Field(
        description=DATA_DESCRIPTIONS.get("open", ""),
        default=None,
    )
    high: float | None = Field(
        description=DATA_DESCRIPTIONS.get("high", ""),
        default=None,
    )
    low: float | None = Field(
        description=DATA_DESCRIPTIONS.get("low", ""),
        default=None,
    )
    close: float | None = Field(
        description=DATA_DESCRIPTIONS.get("close", ""),
        default=None,
    )
    volume: int | None = Field(
        description=DATA_DESCRIPTIONS.get("volume", ""), default=None
    )
    prev_close: float | None = Field(
        description=DATA_DESCRIPTIONS.get("prev_close", ""),
        default=None,
    )
