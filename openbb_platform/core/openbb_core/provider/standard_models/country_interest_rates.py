"""国家利率标准模型。"""

from datetime import date as dateType

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import Field


class CountryInterestRatesQueryParams(QueryParams):
    """国家利率查询。"""

    country: str = Field(
        default="united_states",
        description=QUERY_DESCRIPTIONS.get("country"),
    )
    start_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("start_date")
    )
    end_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("end_date")
    )


class CountryInterestRatesData(Data):
    """国家利率数据。"""

    date: dateType = Field(default=None, description=DATA_DESCRIPTIONS.get("date"))
    value: float = Field(
        default=None,
        description="利率值。",
        json_schema_extra={"x-unit_measurment": "percent", "x-frontend_multiply": 100},
    )
    country: str | None = Field(
        default=None,
        description="给出利率的国家。",
    )
