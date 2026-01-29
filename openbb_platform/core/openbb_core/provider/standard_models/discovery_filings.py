"""发现备案标准模型。"""

from datetime import (
    date as dateType,
    datetime,
)

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import Field, NonNegativeInt


class DiscoveryFilingsQueryParams(QueryParams):
    """发现备案查询。"""

    start_date: dateType | None = Field(
        default=None,
        description=QUERY_DESCRIPTIONS["start_date"],
    )
    end_date: dateType | None = Field(
        default=None,
        description=QUERY_DESCRIPTIONS["end_date"],
    )
    form_type: str | None = Field(
        default=None,
        description=(
            "按表单类型过滤。访问 https://www.sec.gov/forms 获取支持的表单类型列表。"
        ),
    )
    limit: NonNegativeInt | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("limit", "")
    )


class DiscoveryFilingsData(Data):
    """发现备案数据。"""

    symbol: str = Field(description=DATA_DESCRIPTIONS.get("symbol", ""))
    cik: str = Field(description=DATA_DESCRIPTIONS.get("cik", ""))
    filing_date: dateType = Field(description=DATA_DESCRIPTIONS.get("date", ""))
    accepted_date: datetime = Field(
        description=DATA_DESCRIPTIONS.get("accepted_date", "")
    )
    form_type: str = Field(description="备案的表单类型")
    link: str = Field(description="SEC 网站上备案页面的 URL。")
