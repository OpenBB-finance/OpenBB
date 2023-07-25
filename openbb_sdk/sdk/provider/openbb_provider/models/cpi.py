from datetime import date as dateType
from typing import List, Literal, Optional

from pydantic import Field, validator

from openbb_provider.abstract.data import Data, QueryParams
from openbb_provider.metadata import DATA_DESCRIPTIONS, QUERY_DESCRIPTIONS

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

CPI_FREQUENCY = Literal["monthly", "quarterly", "annual"]


class CPIQueryParams(QueryParams):
    """CPI query."""

    countries: List[CPI_COUNTRIES] = Field(
        description=QUERY_DESCRIPTIONS.get("countries")
    )
    units: CPI_UNITS = Field("growth_same", description=QUERY_DESCRIPTIONS.get("units"))
    frequency: CPI_FREQUENCY = Field(
        "monthly", description=QUERY_DESCRIPTIONS.get("frequency")
    )
    harmonized: bool = Field(
        False, description="Whether you wish to obtain harmonized data."
    )
    start_date: Optional[dateType] = Field(
        None, description=QUERY_DESCRIPTIONS.get("start_date")
    )
    end_date: Optional[dateType] = Field(
        None, description=QUERY_DESCRIPTIONS.get("end_date")
    )


class CPIData(Data):
    """CPI data."""

    date: dateType = Field(description=DATA_DESCRIPTIONS.get("date"))
    realtime_start: dateType = Field(
        description="The date the data was updated."
    )  # TODO: What is this?
    realtime_end: dateType = Field(
        description="The date the data was updated."
    )  # TODO: What is this?
    value: float = Field(description="The value of the data.")

    @validator("value", pre=True)
    def value_validate(cls, v: str):  # pylint: disable=E0213
        if v == ".":
            return 0.0
        return float(v)
