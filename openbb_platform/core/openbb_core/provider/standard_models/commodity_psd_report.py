"""商品供需平衡报告标准模型。"""

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from pydantic import Field


class CommodityPsdReportQueryParams(QueryParams):
    """商品供需平衡报告查询。"""

    commodity: str = Field(
        description="报告的商品。",
    )
    year: int = Field(
        description="报告年份。",
    )
    month: int = Field(
        description="报告月份。",
        ge=1,
        le=12,
    )


class CommodityPsdReportData(Data):
    """商品供需平衡报告数据。"""

    content: str = Field(
        description="Base64 编码的内容。",
    )
