"""货币参考汇率模型。"""

from datetime import (
    date as dateType,
)

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import DATA_DESCRIPTIONS
from pydantic import Field


class CurrencyReferenceRatesQueryParams(QueryParams):
    """货币参考汇率查询。"""


class CurrencyReferenceRatesData(Data):
    """货币参考汇率数据。"""

    date: dateType = Field(description=DATA_DESCRIPTIONS.get("date", ""))
    EUR: float | None = Field(description="欧元。", default=None)
    USD: float | None = Field(description="美元。", default=None)
    JPY: float | None = Field(description="日元。", default=None)
    BGN: float | None = Field(description="保加利亚列弗。", default=None)
    CZK: float | None = Field(description="捷克克朗。", default=None)
    DKK: float | None = Field(description="丹麦克朗。", default=None)
    GBP: float | None = Field(description="英镑。", default=None)
    HUF: float | None = Field(description="匈牙利福林。", default=None)
    PLN: float | None = Field(description="波兰兹罗提。", default=None)
    RON: float | None = Field(description="罗马尼亚列伊。", default=None)
    SEK: float | None = Field(description="瑞典克朗。", default=None)
    CHF: float | None = Field(description="瑞士法郎。", default=None)
    ISK: float | None = Field(description="冰岛克朗。", default=None)
    NOK: float | None = Field(description="挪威克朗。", default=None)
    TRY: float | None = Field(description="土耳其里拉。", default=None)
    AUD: float | None = Field(description="澳元。", default=None)
    BRL: float | None = Field(description="巴西雷亚尔。", default=None)
    CAD: float | None = Field(description="加元。", default=None)
    CNY: float | None = Field(description="人民币。", default=None)
    HKD: float | None = Field(description="港元。", default=None)
    IDR: float | None = Field(description="印尼盾。", default=None)
    ILS: float | None = Field(description="以色列新谢克尔。", default=None)
    INR: float | None = Field(description="印度卢比。", default=None)
    KRW: float | None = Field(description="韩元。", default=None)
    MXN: float | None = Field(description="墨西哥比索。", default=None)
    MYR: float | None = Field(description="马来西亚林吉特。", default=None)
    NZD: float | None = Field(description="新西兰元。", default=None)
    PHP: float | None = Field(description="菲律宾比索。", default=None)
    SGD: float | None = Field(description="新加坡元。", default=None)
    THB: float | None = Field(description="泰铢。", default=None)
    ZAR: float | None = Field(description="南非兰特。", default=None)
