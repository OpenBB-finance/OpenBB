"""CPI Standard Model."""
from datetime import date as dateType
from typing import List, Literal, Optional

from dateutil import parser
from pydantic import Field, field_validator

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)

CPI_COUNTRIES = Literal[
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

    countries: List[CPI_COUNTRIES] = Field(
        description=QUERY_DESCRIPTIONS.get("countries")
    )
    units: CPI_UNITS = Field(
        default="growth_same",
        description=QUERY_DESCRIPTIONS.get("units", "")
        + """
    Options:
    - `growth_previous`: growth from the previous period
    - `growth_same`: growth from the same period in the previous year
    - `index_2015`: index with base year 2015.""",
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


class ConsumerPriceIndexData(Data):
    """CPI data."""

    date: dateType = Field(description=DATA_DESCRIPTIONS.get("date"))

    @field_validator("date", mode="before")
    @classmethod
    def date_validate(cls, v):
        """Validate date."""
        return parser.isoparse(v)
