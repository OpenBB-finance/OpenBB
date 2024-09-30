"""Export Destinations Standard Model."""

from typing import Union

from pydantic import Field

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS


class ExportDestinationsQueryParams(QueryParams):
    """Export Destinations Query."""

    country: str = Field(description=QUERY_DESCRIPTIONS.get("country", ""))


class ExportDestinationsData(Data):
    """Export Destinations Data."""

    origin_country: str = Field(
        description="The country of origin.",
    )
    destination_country: str = Field(
        description="The destination country.",
    )
    value: Union[float, int] = Field(
        description="The value of the export.",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
