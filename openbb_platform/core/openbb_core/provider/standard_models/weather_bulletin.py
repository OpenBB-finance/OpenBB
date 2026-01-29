"""气象公报标准模型。"""

from datetime import datetime

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from pydantic import Field


class WeatherBulletinQueryParams(QueryParams):
    """气象公报查询。"""

    year: int = Field(
        description="数据的年份。默认为当前年份。",
        default=datetime.now().year,
    )
    month: int | None = Field(
        description="数据的月份。如果未提供，则返回全年数据。",
        ge=1,
        le=12,
        default=None,
    )
    week: int | None = Field(
        description="数据的数字周（相对于月份）。"
        + " 如果未提供，则返回全月数据。",
        ge=1,
        le=5,
        default=None,
    )


class WeatherBulletinData(Data):
    """气象公报数据。"""

    label: str | None = Field(
        default=None,
        description="代表气象公报文件的标签。",
    )
    value: str | None = Field(
        default=None,
        description="指向气象公报文档的 URL。",
    )
