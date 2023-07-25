from datetime import date as dateType
from typing import List, Literal, Optional

from pydantic import validator

from openbb_provider.abstract.data import Data, QueryParams

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
    """CPI query.
    When other provders are added, this will probably need less strict types

    Parameter
    ---------
    countries: List[CPI_COUNTRIES]
        The country or countries you want to see.
    units: List[CPI_UNITS]
        The units you want to see, can be "growth_previous", "growth_same" or "index_2015".
    frequency: List[CPI_FREQUENCY]
        The frequency you want to see, either "annual", monthly" or "quarterly".
    harmonized: bool
        Whether you wish to obtain harmonized data.
    start_date: Optional[date]
        Start date, formatted YYYY-MM-DD
    end_date: Optional[date]
        End date, formatted YYYY-MM-DD
    """

    countries: List[CPI_COUNTRIES]
    units: CPI_UNITS = "growth_same"
    frequency: CPI_FREQUENCY = "monthly"
    harmonized: bool = False
    start_date: Optional[dateType]
    end_date: Optional[dateType]


class CPIData(Data):
    date: dateType
    realtime_start: dateType
    realtime_end: dateType
    value: float

    @validator("value", pre=True)
    def value_validate(cls, v: str):  # pylint: disable=E0213
        if v == ".":
            return 0.0
        return float(v)
