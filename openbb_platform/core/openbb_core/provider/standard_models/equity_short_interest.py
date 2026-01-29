"""股票卖空利息标准模型。"""

from datetime import date as dateType

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import Field


class ShortInterestQueryParams(QueryParams):
    """股票卖空利息查询。"""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", ""))


class ShortInterestData(Data):
    """股票卖空利息数据。"""

    settlement_date: dateType = Field(
        description=(
            "月中卖空利息报告基于成员在每月 15 日结算日持有的卖空头寸。"
            "如果 15 日是周末或其他非结算日，则指定的结算日将是交易结算的前一个工作日。"
            "月底卖空利息报告基于交易结算月最后一个工作日持有的卖空头寸。"
            "一旦收到卖空头寸报告，就会汇编每只股票的卖空利息数据，"
            "并在报告结算日后的第 7 个工作日公布。"
        )
    )
    symbol: str = Field(description=DATA_DESCRIPTIONS.get("symbol", ""))
    issue_name: str = Field(description="发行的唯一标识符。")
    market_class: str = Field(description="主要上市市场。")
    current_short_position: float = Field(
        description=(
            "截至当前周期指定结算日，报告公司账簿和记录中反映的发行股票总数，"
            "根据 SHO 条例第 200 条定义为卖空。"
        )
    )
    previous_short_position: float = Field(
        description=(
            "截至上一周期指定结算日，报告公司账簿和记录中反映的发行股票总数，"
            "根据 SHO 条例第 200 条定义为卖空。"
        )
    )
    avg_daily_volume: float = Field(
        description=(
            "总成交量或拆分情况下的调整成交量 / （上一结算日 + 1）至（当前结算日）之间的总交易天数。"
            "NULL 值转换为零。"
        )
    )

    days_to_cover: float = Field(
        description=(
            "购买报告周期内所有卖空股票所需的平均每日成交量的天数。公式：卖空利息 / 平均每日成交量，四舍五入到百分位。"
            "任何等于或小于 1 的值（即平均每日成交量等于或大于卖空利息）都将显示为 1.00。"
            "如果回补天数为零（即平均每日成交量为零），将显示 N/A。"
        )
    )
    change: float = Field(
        description=(
            "较上一周期卖空股票的变化：当前周期与上一周期卖空利息的差额。"
        )
    )
    change_pct: float = Field(
        description="较上一周期卖空股票变化的百分比。"
    )
