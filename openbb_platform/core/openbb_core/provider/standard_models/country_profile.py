"""国家概况标准模型。"""

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import Field, field_validator


class CountryProfileQueryParams(QueryParams):
    """国家概况查询。"""

    country: str = Field(description=QUERY_DESCRIPTIONS.get("country", ""))

    @field_validator("country", mode="before", check_fields=False)
    @classmethod
    def to_lower(cls, v: str) -> str:
        """将国家/地区转换为小写。"""
        return v.lower().replace(" ", "_")


class CountryProfileData(Data):
    """国家概况数据。"""

    country: str = Field(description=DATA_DESCRIPTIONS.get("country", ""))
    population: int | None = Field(default=None, description="人口。")
    gdp_usd: float | None = Field(
        default=None, description="国内生产总值（十亿美元）。"
    )
    gdp_qoq: float | None = Field(
        default=None,
        description="GDP 增长季度环比变化，归一化百分比。",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    gdp_yoy: float | None = Field(
        default=None,
        description="GDP 增长同比变化，归一化百分比。",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    cpi_yoy: float | None = Field(
        default=None,
        description="消费者价格指数同比变化，归一化百分比。",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    core_yoy: float | None = Field(
        default=None,
        description="核心消费者价格指数同比变化，归一化百分比。",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    retail_sales_yoy: float | None = Field(
        default=None,
        description="零售销售同比变化，归一化百分比。",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    industrial_production_yoy: float | None = Field(
        default=None,
        description="工业生产同比变化，归一化百分比。",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    policy_rate: float | None = Field(
        default=None,
        description="短期政策利率，归一化百分比。",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    yield_10y: float | None = Field(
        default=None,
        description="10 年期政府债券收益率，归一化百分比。",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    govt_debt_gdp: float | None = Field(
        default=None,
        description="政府债务占 GDP 的百分比（归一化）。",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    current_account_gdp: float | None = Field(
        default=None,
        description="经常账户余额占 GDP 的百分比（归一化）。",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    jobless_rate: float | None = Field(
        default=None,
        description="失业率，归一化百分比。",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
