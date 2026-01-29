"""最新财务报告标准模型。"""

from datetime import date as dateType

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import DATA_DESCRIPTIONS
from pydantic import Field


class LatestFinancialReportsQueryParams(QueryParams):
    """最新财务报告查询。"""


class LatestFinancialReportsData(Data):
    """最新财务报告数据。"""

    filing_date: dateType = Field(description="文件备案日期。")
    period_ending: dateType | None = Field(
        default=None, description="报告期截止日期。"
    )
    symbol: str | None = Field(
        default=None, description=DATA_DESCRIPTIONS.get("symbol")
    )
    name: str | None = Field(default=None, description="公司名称。")
    cik: str | None = Field(default=None, description=DATA_DESCRIPTIONS.get("cik"))
    sic: str | None = Field(
        default=None, description="标准工业分类代码。"
    )
    report_type: str | None = Field(default=None, description="备案类型。")
    description: str | None = Field(
        default=None, description="报告描述。"
    )
    url: str = Field(description="文件备案页面的 URL。")
