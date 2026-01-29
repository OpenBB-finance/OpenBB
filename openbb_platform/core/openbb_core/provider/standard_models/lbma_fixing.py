"""LBMA 定盘价标准模型。"""

from datetime import date as dateType
from typing import Literal

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import Field


class LbmaFixingQueryParams(QueryParams):
    """
    LBMA 定盘价查询。

    数据来源: https://www.lbma.org.uk/prices-and-data/precious-metal-prices#/table
    """

    asset: Literal["gold", "silver"] = Field(
        description="获取定盘价利率的金属。",
        default="gold",
    )
    start_date: dateType | None = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("start_date", ""),
    )
    end_date: dateType | None = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("end_date", ""),
    )


class LbmaFixingData(Data):
    """LBMA 定盘价数据。以美元、英镑和欧元计价的历史定盘价。"""

    date: dateType = Field(description=DATA_DESCRIPTIONS.get("date", ""))
    usd_am: float | None = Field(
        default=None,
        description="以美元计价的上午定盘价。",
    )
    usd_pm: float | None = Field(
        default=None,
        description="以美元计价的下午定盘价。",
    )
    gbp_am: float | None = Field(
        default=None,
        description="以英镑计价的上午定盘价。",
    )
    gbp_pm: float | None = Field(
        default=None,
        description="以英镑计价的下午定盘价。",
    )
    euro_am: float | None = Field(
        default=None,
        description="以欧元计价的上午定盘价。",
    )
    euro_pm: float | None = Field(
        default=None,
        description="以欧元计价的下午定盘价。",
    )
    usd: float | None = Field(
        default=None,
        description="以美元计价的每日定盘价。",
    )
    gbp: float | None = Field(
        default=None,
        description="以英镑计价的每日定盘价。",
    )
    eur: float | None = Field(
        default=None,
        description="以欧元计价的每日定盘价。",
    )
