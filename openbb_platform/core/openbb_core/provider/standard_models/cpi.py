"""CPI Standard Model."""

from datetime import date as dateType
from typing import Literal, Optional

from dateutil import parser
from pydantic import Field, field_validator

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from openbb_core.provider.utils.helpers import check_item

CPI_COUNTRIES = [
    "australia",
    "austria",
    "belgium",
    "brazil",
    "bulgaria",
    "canada",
    "chile",
    "china",
    "croatia",
    "cyprus",
    "czech_republic",
    "denmark",
    "estonia",
    "euro_area",
    "finland",
    "france",
    "germany",
    "greece",
    "hungary",
    "iceland",
    "india",
    "indonesia",
    "ireland",
    "israel",
    "italy",
    "japan",
    "korea",
    "latvia",
    "lithuania",
    "luxembourg",
    "malta",
    "mexico",
    "netherlands",
    "new_zealand",
    "norway",
    "poland",
    "portugal",
    "romania",
    "russian_federation",
    "slovak_republic",
    "slovakia",
    "slovenia",
    "south_africa",
    "spain",
    "sweden",
    "switzerland",
    "turkey",
    "united_kingdom",
    "united_states",
]

CPI_UNITS = Literal["growth_previous", "growth_same", "index_2015"]

CPI_FREQUENCY = Literal["monthly", "quarter", "annual"]


class ConsumerPriceIndexQueryParams(QueryParams):
    """CPI Query."""

    country: str = Field(
        description=QUERY_DESCRIPTIONS.get("country"),
        json_schema_extra={"choices": CPI_COUNTRIES},  # type: ignore[dict-item]
    )
    units: CPI_UNITS = Field(
        default="growth_same",
        description=QUERY_DESCRIPTIONS.get("units", "")
        + """
    Options:
    - `growth_previous`: Percent growth from the previous period.
      If monthly data, this is month-over-month, etc
    - `growth_same`: Percent growth from the same period in the previous year.
      If looking at monthly data, this would be year-over-year, etc.
    - `index_2015`: Rescaled index value, such that the value in 2015 is 100.""",
    )
    frequency: CPI_FREQUENCY = Field(
        default="monthly",
        description=QUERY_DESCRIPTIONS.get("frequency", "")
        + """
    Options: `monthly`, `quarter`, and `annual`.""",
    )
    harmonized: bool = Field(
        default=False, description="Whether you wish to obtain harmonized data."
    )
    start_date: Optional[dateType] = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("start_date")
    )
    end_date: Optional[dateType] = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("end_date")
    )

    @field_validator("country", mode="before", check_fields=False)
    def validate_country(cls, c: str):  # pylint: disable=E0213
        """Validate country."""
        result = []
        values = c.replace(" ", "_").split(",")
        for v in values:
            check_item(v.lower(), CPI_COUNTRIES)
            result.append(v.lower())
        return ",".join(result)


class ConsumerPriceIndexData(Data):
    """CPI data."""

    date: dateType = Field(description=DATA_DESCRIPTIONS.get("date"))

    @field_validator("date", mode="before")
    @classmethod
    def date_validate(cls, v):
        """Validate date."""
        return parser.isoparse(v)
