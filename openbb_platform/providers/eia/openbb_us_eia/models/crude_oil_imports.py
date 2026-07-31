"""Crude Oil Imports model."""

from typing import Any, Literal

from openbb_core.provider.abstract.fetcher import Fetcher
from pydantic import Field

from openbb_us_eia.utils.api_query import (
    EiaApiData,
    EiaApiQueryParams,
    extract_dataset_data,
    transform_dataset_data,
    transform_dataset_query,
)


class EiaCrudeOilImportsQueryParams(EiaApiQueryParams):
    """Crude Oil Imports. Crude oil imports by country to destination, includes type, grade, quantity. Source: EIA-814 Interactive data product: www.eia.gov/petroleum/imports/companylevel/

    Source: https://www.eia.gov/opendata/browser/crude-oil-imports
    """

    __group__ = "crude_oil_imports"
    __dataset__ = "crude_oil_imports"
    __json_schema_extra__ = {
        "destination": {"multiple_items_allowed": True},
        "destination_type": {
            "multiple_items_allowed": True,
            "choices": [
                "port",
                "port_padd",
                "port_state",
                "refinery",
                "refinery_padd",
                "refinery_state",
                "united_states",
            ],
        },
        "grade": {
            "multiple_items_allowed": True,
            "choices": [
                "heavy_sour",
                "heavy_sweet",
                "light_sour",
                "light_sweet",
                "medium",
            ],
        },
        "origin": {
            "multiple_items_allowed": True,
            "choices": [
                "africa",
                "albania",
                "algeria",
                "angola",
                "argentina",
                "asia_pacific",
                "australia",
                "azerbaijan",
                "barbados",
                "belize",
                "bolivia",
                "brazil",
                "brunei",
                "cameroon",
                "canada",
                "canada_region",
                "chad",
                "china",
                "colombia",
                "congo_brazzaville",
                "congo_kinshasa",
                "cote_d_ivoire",
                "denmark",
                "ecuador",
                "egypt",
                "equatorial_guinea",
                "eurasia",
                "europe",
                "gabon",
                "ghana",
                "guatemala",
                "guyana",
                "indonesia",
                "iran",
                "iraq",
                "italy",
                "kazakhstan",
                "kuwait",
                "libya",
                "malaysia",
                "mauritania",
                "mexico",
                "middle_east",
                "netherlands",
                "nigeria",
                "non_opec",
                "norway",
                "opec",
                "oman",
                "other_americas",
                "panama",
                "papua_new_guinea",
                "peru",
                "qatar",
                "russia",
                "saudi_arabia",
                "senegal",
                "south_africa",
                "south_sudan",
                "spain",
                "syria",
                "thailand",
                "the_bahamas",
                "trinidad_and_tobago",
                "tunisia",
                "united_arab_emirates",
                "united_kingdom",
                "venezuela",
                "vietnam",
                "world",
                "yemen",
            ],
        },
        "origin_type": {
            "multiple_items_allowed": True,
            "choices": ["country", "opec_non_opec", "region", "world"],
        },
    }

    frequency: Literal["annual", "monthly"] | None = Field(
        default=None,
        description="The data frequency. The default is 'monthly'.",
    )
    destination: str | None = Field(
        default=None,
        description="Destination Id filter. Accepts a comma-separated list of values. There are 513 valid values - use the `facet_options` endpoint to list them.",
    )
    destination_type: (
        Literal[
            "port",
            "port_padd",
            "port_state",
            "refinery",
            "refinery_padd",
            "refinery_state",
            "united_states",
        ]
        | None
    ) = Field(
        default=None,
        description="Destination Type filter.",
    )
    grade: (
        Literal["heavy_sour", "heavy_sweet", "light_sour", "light_sweet", "medium"]
        | None
    ) = Field(
        default=None,
        description="Grade Id filter.",
    )
    origin: str | None = Field(
        default=None,
        description="Origin Id filter. Accepts a comma-separated list of values.",
    )
    origin_type: Literal["country", "opec_non_opec", "region", "world"] | None = Field(
        default=None,
        description="Origin Type filter.",
    )


class EiaCrudeOilImportsData(EiaApiData):
    """Crude Oil Imports. Crude oil imports by country to destination, includes type, grade, quantity. Source: EIA-814 Interactive data product: www.eia.gov/petroleum/imports/companylevel/"""

    destination: str | None = Field(
        default=None,
        description="Destination Id code.",
    )
    destination_name: str | None = Field(
        default=None,
        description="Destination Id name.",
    )
    destination_type: str | None = Field(
        default=None,
        description="Destination Type code.",
    )
    destination_type_name: str | None = Field(
        default=None,
        description="Destination Type name.",
    )
    grade: str | None = Field(
        default=None,
        description="Grade Id code.",
    )
    grade_name: str | None = Field(
        default=None,
        description="Grade Id name.",
    )
    origin: str | None = Field(
        default=None,
        description="Origin Id code.",
    )
    origin_name: str | None = Field(
        default=None,
        description="Origin Id name.",
    )
    origin_type: str | None = Field(
        default=None,
        description="Origin Type code.",
    )
    origin_type_name: str | None = Field(
        default=None,
        description="Origin Type name.",
    )
    quantity: float | None = Field(
        default=None,
        description="Quantity (thousand barrels). Withheld or unavailable values return as null.",
    )


class EiaCrudeOilImportsFetcher(
    Fetcher[EiaCrudeOilImportsQueryParams, list[EiaCrudeOilImportsData]]
):
    """Crude Oil Imports fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> EiaCrudeOilImportsQueryParams:
        """Transform the query parameters."""
        return transform_dataset_query(EiaCrudeOilImportsQueryParams, params)

    @staticmethod
    async def aextract_data(
        query: EiaCrudeOilImportsQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract the data from the EIA API."""
        return await extract_dataset_data(query, credentials)

    @staticmethod
    def transform_data(
        query: EiaCrudeOilImportsQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> list[EiaCrudeOilImportsData]:
        """Transform the data."""
        return transform_dataset_data(EiaCrudeOilImportsData, query, data)
