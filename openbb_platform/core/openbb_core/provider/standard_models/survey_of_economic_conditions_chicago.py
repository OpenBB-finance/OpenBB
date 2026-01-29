"""芝加哥经济状况调查标准模型。"""

from datetime import (
    date as dateType,
)

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import Field


class SurveyOfEconomicConditionsChicagoQueryParams(QueryParams):
    """芝加哥经济状况调查查询。"""

    start_date: dateType | None = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("start_date", ""),
    )
    end_date: dateType | None = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("end_date", ""),
    )


class SurveyOfEconomicConditionsChicagoData(Data):
    """芝加哥经济状况调查数据。"""

    date: dateType = Field(description=DATA_DESCRIPTIONS.get("date", ""))
    activity_index: float | None = Field(default=None, description="活动指数。")
    one_year_outlook: float | None = Field(
        default=None, description="一年展望指数。"
    )
    manufacturing_activity: float | None = Field(
        default=None, description="制造业活动指数。"
    )
    non_manufacturing_activity: float | None = Field(
        default=None, description="非制造业活动指数。"
    )
    capital_expenditures_expectations: float | None = Field(
        default=None, description="资本支出预期指数。"
    )
    hiring_expectations: float | None = Field(
        default=None, description="招聘预期指数。"
    )
    current_hiring: float | None = Field(
        default=None, description="当前招聘指数。"
    )
    labor_costs: float | None = Field(default=None, description="劳动力成本指数。")
    non_labor_costs: float | None = Field(
        default=None, description="非劳动力成本指数。"
    )
