"""Crude Oil Input Qualities model."""

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


class EiaPetroleumCrudeOilInputQualitiesQueryParams(EiaApiQueryParams):
    """Crude Oil Input Qualities. EIA petroleum gas survey data

    Source: https://www.eia.gov/opendata/browser/petroleum/pnp/crq
    """

    __group__ = "petroleum"
    __dataset__ = "crude_oil_input_qualities"
    __json_schema_extra__ = {
        "process": {
            "multiple_items_allowed": True,
            "choices": [
                "oil_refinery_inputs_average_sulfur_content",
                "refinery_inputs_average_api_gravity",
            ],
        },
        "region": {
            "multiple_items_allowed": True,
            "choices": ["na", "padd_1", "padd_2", "padd_3", "padd_4", "padd_5", "us"],
        },
        "series": {
            "multiple_items_allowed": True,
            "choices": [
                "appalachian_no_1_refinery_district_api_gravity_of_crude_oil",
                "appalachian_no_1_refinery_district_sulfur_content_of_crude",
                "east_coast_api_gravity_of_crude_oil_input_to_refineries",
                "east_coast_sulfur_content_of_crude_oil_input_to_refineries",
                "east_coast_refinery_district_api_gravity_of_crude_oil_input",
                "east_coast_refinery_district_sulfur_content_of_crude_oil",
                "gulf_coast_api_gravity_of_crude_oil_input_to_refineries",
                "gulf_coast_sulfur_content_of_crude_oil_input_to_refineries",
                "indiana_illinois_kentucky_refinery_district_api_gravity_of",
                "indiana_illinois_kentucky_refinery_district_sulfur_content",
                "louisiana_gulf_coast_refinery_district_api_gravity_of_crude",
                "louisiana_gulf_coast_refinery_district_sulfur_content_of",
                "midwest_api_gravity_of_crude_oil_input_to_refineries",
                "midwest_sulfur_content_of_crude_oil_input_to_refineries",
                "minnesota_wisconsin_north_and_south_dakota_refinery_district_api_gravity_weighted_average_of_crude_oil_input_to_refineries_degrees",
                "minnesota_wisconsin_north_and_south_dakota_refinery_district_sulfur_content_weighted_average_of_crude_oil_input_to_refineries_percent",
                "new_mexico_refinery_district_api_gravity_of_crude_oil_input",
                "new_mexico_refinery_district_sulfur_content_of_crude_oil",
                "north_louisiana_arkansas_refinery_district_api_gravity_of",
                "north_louisiana_arkansas_refinery_district_sulfur_content",
                "oklahoma_kansas_missouri_refinery_district_api_gravity_of",
                "oklahoma_kansas_missouri_refinery_district_sulfur_content",
                "rocky_mountains_api_gravity_of_crude_oil_input_to_refineries",
                "rocky_mountains_sulfur_content_of_crude_oil_input_to",
                "texas_gulf_coast_refinery_district_api_gravity_of_crude_oil",
                "texas_gulf_coast_refinery_district_sulfur_content_of_crude",
                "texas_inland_refinery_district_api_gravity_of_crude_oil",
                "texas_inland_refinery_district_sulfur_content_of_crude_oil",
                "us_api_gravity_of_crude_oil_input_to_refineries",
                "us_sulfur_content_of_crude_oil_input_to_refineries",
                "west_coast_api_gravity_of_crude_oil_input_to_refineries",
                "west_coast_sulfur_content_of_crude_oil_input_to_refineries",
            ],
        },
    }

    frequency: Literal["annual", "monthly"] | None = Field(
        default=None,
        description="The data frequency. The default is 'monthly'.",
    )
    process: str | None = Field(
        default=None,
        description="Process filter. Accepts a comma-separated list of values.",
    )
    region: str | None = Field(
        default=None,
        description="DuoArea filter. Accepts a comma-separated list of values.",
    )
    series: str | None = Field(
        default=None,
        description="Series filter. Accepts a comma-separated list of values.",
    )


class EiaPetroleumCrudeOilInputQualitiesData(EiaApiData):
    """Crude Oil Input Qualities. EIA petroleum gas survey data"""

    process: str | None = Field(
        default=None,
        description="Process code.",
    )
    process_name: str | None = Field(
        default=None,
        description="Process name.",
    )
    product: str | None = Field(
        default=None,
        description="Product code.",
    )
    product_name: str | None = Field(
        default=None,
        description="Product name.",
    )
    region: str | None = Field(
        default=None,
        description="DuoArea code.",
    )
    region_name: str | None = Field(
        default=None,
        description="DuoArea name.",
    )
    series: str | None = Field(
        default=None,
        description="Series code.",
    )
    series_name: str | None = Field(
        default=None,
        description="Series name.",
    )
    value: float | None = Field(
        default=None,
        description="Value. Withheld or unavailable values return as null.",
    )
    units: str | None = Field(
        default=None,
        description="Unit of the value.",
    )


class EiaPetroleumCrudeOilInputQualitiesFetcher(
    Fetcher[
        EiaPetroleumCrudeOilInputQualitiesQueryParams,
        list[EiaPetroleumCrudeOilInputQualitiesData],
    ]
):
    """Crude Oil Input Qualities fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> EiaPetroleumCrudeOilInputQualitiesQueryParams:
        """Transform the query parameters."""
        return transform_dataset_query(
            EiaPetroleumCrudeOilInputQualitiesQueryParams, params
        )

    @staticmethod
    async def aextract_data(
        query: EiaPetroleumCrudeOilInputQualitiesQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract the data from the EIA API."""
        return await extract_dataset_data(query, credentials)

    @staticmethod
    def transform_data(
        query: EiaPetroleumCrudeOilInputQualitiesQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> list[EiaPetroleumCrudeOilInputQualitiesData]:
        """Transform the data."""
        return transform_dataset_data(
            EiaPetroleumCrudeOilInputQualitiesData, query, data
        )
