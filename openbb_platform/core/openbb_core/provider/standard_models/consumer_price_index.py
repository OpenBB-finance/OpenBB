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

CPI_STANDARD_COUNTRIES = [
    "israel",
    "portugal",
    "chile",
    "finland",
    "japan",
    "czech_republic",
    "denmark",
    "poland",
    "indonesia",
    "italy",
    "spain",
    "korea",
    "iceland",
    "slovak_republic",
    "latvia",
    "turkey",
    "hungary",
    "united_kingdom",
    "india",
    "norway",
    "australia",
    "estonia",
    "netherlands",
    "germany",
    "greece",
    "china",
    "lithuania",
    "united_states",
    "luxembourg",
    "france",
    "sweden",
    "switzerland",
    "slovenia",
    "mexico",
    "new_zealand",
    "canada",
    "austria",
    "belgium",
    "ireland",
    "brazil",
    "south_africa",
]


CPI_FREQUENCY = Literal["monthly", "quarter", "annual"]


class ConsumerPriceIndexQueryParams(QueryParams):
    """CPI Query."""

    country: str = Field(
        description=QUERY_DESCRIPTIONS.get("country"),
        default="united_states",
        json_schema_extra={"choices": CPI_COUNTRIES},  # type: ignore[dict-item]
    )
    units: Literal["index", "yoy", "mom"] = Field(
        description="Units to get CPI for. Either index, month over month or year over year. Defaults to year over year.",
        default="yoy",
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
            check_item(v.lower(), CPI_STANDARD_COUNTRIES)
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
