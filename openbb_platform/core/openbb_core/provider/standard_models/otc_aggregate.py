"""场外交易 (OTC) 汇总标准模型。"""

from datetime import date as dateType

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from pydantic import Field


class OTCAggregateQueryParams(QueryParams):
    """场外交易 (OTC) 汇总查询。"""

    symbol: str | None = Field(
        description=QUERY_DESCRIPTIONS.get("symbol", ""),
        default=None,
    )


class OTCAggregateData(Data):
    """场外交易 (OTC) 汇总数据。"""

    update_date: dateType = Field(
        description="根据从每个 ATS/OTC 接收到的数据更新总交易笔数的最近日期。"
    )
    share_quantity: float = Field(
        description="由每个 ATS 报告的该股票每周累计成交量。"
    )
    trade_quantity: float = Field(
        description="由每个 ATS 报告的该股票每周累计成交笔数"
    )
