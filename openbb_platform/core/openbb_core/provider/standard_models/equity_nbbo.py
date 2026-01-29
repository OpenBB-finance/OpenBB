"""股票 NBBO 标准模型。"""

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from pydantic import Field, field_validator


class EquityNBBOQueryParams(QueryParams):
    """股票 NBBO 查询。"""

    symbol: str = Field(
        description=QUERY_DESCRIPTIONS.get("symbol", ""),
    )

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def to_upper(cls, v: str):
        """将字段转换为大写。"""
        return v.upper()


class EquityNBBOData(Data):
    """股票 NBBO 数据。"""

    ask_exchange: str = Field(
        description="卖出交易所 ID。",
    )
    ask: float = Field(
        description="最新卖出价。",
    )
    ask_size: int = Field(
        description="""
        卖出数量。代表给定卖出价下的整手订单数量。
        正常的整手大小为 100 股。
        卖出数量为 2 意味着在给定卖出价下有 200 股可供购买。
        """,
    )
    bid_size: int = Field(
        description="以整手为单位的买入数量。",
    )
    bid: float = Field(
        description="最新买入价。",
    )
    bid_exchange: str = Field(
        description="买入交易所 ID。",
    )
