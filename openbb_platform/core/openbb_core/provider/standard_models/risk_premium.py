"""风险溢价标准模型。"""

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from pydantic import Field, NonNegativeFloat, PositiveFloat


class RiskPremiumQueryParams(QueryParams):
    """风险溢价查询。"""


class RiskPremiumData(Data):
    """风险溢价数据。"""

    country: str = Field(description="市场所在国家。")
    continent: str | None = Field(default=None, description="该国家所属大洲。")
    total_equity_risk_premium: PositiveFloat | None = Field(
        default=None, description="该国家的总股权风险溢价。"
    )
    country_risk_premium: NonNegativeFloat | None = Field(
        default=None, description="国家特定的风险溢价。"
    )
