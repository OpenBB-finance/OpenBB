"""Survey Of Economic Conditions - Chicago - Standard Model."""

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
    """Survey Of Economic Conditions - Chicago - Query."""

    start_date: dateType | None = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("start_date", ""),
    )
    end_date: dateType | None = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("end_date", ""),
    )


class SurveyOfEconomicConditionsChicagoData(Data):
    """Survey Of Economic Conditions - Chicago - Data."""

    date: dateType = Field(description=DATA_DESCRIPTIONS.get("date", ""))
    activity_index: float | None = Field(default=None, description="Activity Index.")
    one_year_outlook: float | None = Field(
        default=None, description="One Year Outlook Index."
    )
    manufacturing_activity: float | None = Field(
        default=None, description="Manufacturing Activity Index."
    )
    non_manufacturing_activity: float | None = Field(
        default=None, description="Non-Manufacturing Activity Index."
    )
    capital_expenditures_expectations: float | None = Field(
        default=None, description="Capital Expenditures Expectations Index."
    )
    hiring_expectations: float | None = Field(
        default=None, description="Hiring Expectations Index."
    )
    current_hiring: float | None = Field(
        default=None, description="Current Hiring Index."
    )
    labor_costs: float | None = Field(default=None, description="Labor Costs Index.")
    non_labor_costs: float | None = Field(
        default=None, description="Non-Labor Costs Index."
    )
