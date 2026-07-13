"""Refinery Utilization and Capacity model."""

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


class EiaPetroleumRefineryUtilizationAndCapacityQueryParams(EiaApiQueryParams):
    """Refinery Utilization and Capacity. EIA petroleum gas survey data

    Source: https://www.eia.gov/opendata/browser/petroleum/pnp/unc
    """

    __group__ = "petroleum"
    __dataset__ = "refinery_utilization_and_capacity"
    __json_schema_extra__ = {
        "process": {
            "multiple_items_allowed": True,
            "choices": [
                "utilization_refinery_operable_capacity",
                "refinery_idle_operable_capacity",
                "refinery_net_input",
                "refinery_operable_capacity",
                "refinery_operating_capacity",
            ],
        },
        "region": {
            "multiple_items_allowed": True,
            "choices": ["na", "padd_1", "padd_2", "padd_3", "padd_4", "padd_5", "us"],
        },
        "series": {
            "multiple_items_allowed": True,
            "choices": [
                "appalachian_no_1_refinery_district_gross_inputs_to",
                "appalachian_no_1_refining_district_idle_crude_oil",
                "appalachian_no_1_refining_district_operable_crude_oil",
                "appalachian_no_1_refining_district_operating_crude_oil",
                "appalachian_no_1_refining_district_percent_utilization_of",
                "east_coast_gross_inputs_to_atmospheric_crude_oil",
                "east_coast_idle_crude_oil_distillation_capacity",
                "east_coast_operable_crude_oil_distillation_capacity",
                "east_coast_operating_crude_oil_distillation_capacity",
                "east_coast_percent_utilization_of_refinery_operable_capacity",
                "east_coast_refining_district_idle_crude_oil_distillation",
                "east_coast_refining_district_operable_crude_oil",
                "east_coast_refining_district_operating_crude_oil",
                "east_coast_refining_district_percent_utilization_of",
                "gulf_coast_gross_inputs_to_refineries",
                "gulf_coast_idle_crude_oil_distillation_capacity",
                "gulf_coast_operable_crude_oil_distillation_capacity",
                "gulf_coast_operating_crude_oil_distillation_capacity",
                "gulf_coast_percent_utilization_of_refinery_operable_capacity",
                "indiana_illinois_kentucky_refinery_district_gross_inputs_to",
                "indiana_illinois_and_kentucky_refining_district_idle_crude",
                "indiana_illinois_and_kentucky_refining_district_operable",
                "indiana_illinois_and_kentucky_refining_district_operating",
                "indiana_illinois_and_kentucky_refining_district_percent",
                "louisiana_gulf_coast_refinery_district_gross_inputs_to",
                "louisiana_gulf_coast_refining_district_idle_crude_oil",
                "louisiana_gulf_coast_refining_district_operable_crude_oil",
                "louisiana_gulf_coast_refining_district_operating_crude_oil",
                "louisiana_gulf_coast_refining_district_percent_utilization",
                "midwest_gross_inputs_to_refineries",
                "midwest_idle_crude_oil_distillation_capacity",
                "midwest_operable_crude_oil_distillation_capacity",
                "midwest_operating_crude_oil_distillation_capacity",
                "midwest_percent_utilization_of_refinery_operable_capacity",
                "minnesota_wisconsin_north_and_south_dakota_refinery",
                "minnesota_wisconsin_north_and_south_dakota_refining_district_idle_crude_oil_distillation_capacity_thousand_barrels_per_day",
                "minnesota_wisconsin_north_and_south_dakota_refining_district_operable_crude_oil_distillation_capacity_thousand_barrels_per_calendar_day",
                "minnesota_wisconsin_north_and_south_dakota_refining_district_operating_crude_oil_distillation_capacity_thousand_barrels_per_day",
                "minnesota_wisconsin_north_and_south_dakota_refining_district_percent_utilization_of_refinery_operable_capacity",
                "new_mexico_refining_district_idle_crude_oil_distillation",
                "new_mexico_refining_district_operable_crude_oil",
                "new_mexico_refining_district_operating_crude_oil",
                "new_mexico_refining_district_percent_utilization_of",
                "north_louisiana_and_arkansas_refining_district_idle_crude",
                "north_louisiana_and_arkansas_refining_district_operable",
                "north_louisiana_and_arkansas_refining_district_operating",
                "north_louisiana_arkansas_refining_district_percent",
                "oklahoma_kansas_missouri_refining_district_percent",
                "oklahoma_kansas_and_missouri_refining_district_idle_crude",
                "oklahoma_kansas_and_missouri_refining_district_operable",
                "oklahoma_kansas_and_missouri_refining_district_operating",
                "refining_district_east_coast_refinery_district_gross_inputs",
                "refining_district_new_mexico_gross_inputs_to_atmospheric",
                "refining_district_north_louisiana_arkansas_gross_inputs_to",
                "refining_district_oklahoma_kansas_missouri_gross_inputs_to",
                "refining_district_texas_gulf_coast_gross_inputs_to",
                "rocky_mountains_gross_inputs_to_refineries",
                "rocky_mountains_idle_crude_oil_distillation_capacity",
                "rocky_mountains_operable_crude_oil_distillation_capacity",
                "rocky_mountains_operating_crude_oil_distillation_capacity",
                "rocky_mountains_percent_utilization_of_refinery_operable",
                "texas_gulf_coast_refining_district_idle_crude_oil",
                "texas_gulf_coast_refining_district_operable_crude_oil",
                "texas_gulf_coast_refining_district_operating_crude_oil",
                "texas_gulf_coast_refining_district_percent_utilization_of",
                "texas_inland_refinery_district_gross_inputs_to_refineries",
                "texas_inland_refining_district_idle_crude_oil_distillation",
                "texas_inland_refining_district_operable_crude_oil",
                "texas_inland_refining_district_operating_crude_oil",
                "texas_inland_refining_district_percent_utilization_of",
                "u_s_idle_crude_oil_distillation_capacity",
                "u_s_operable_crude_oil_distillation_capacity",
                "u_s_operating_crude_oil_distillation_capacity",
                "us_gross_inputs_to_refineries",
                "us_percent_utilization_of_refinery_operable_capacity",
                "west_coast_gross_inputs_to_refineries",
                "west_coast_idle_crude_oil_distillation_capacity",
                "west_coast_operable_crude_oil_distillation_capacity",
                "west_coast_operating_crude_oil_distillation_capacity",
                "west_coast_percent_utilization_of_refinery_operable_capacity",
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


class EiaPetroleumRefineryUtilizationAndCapacityData(EiaApiData):
    """Refinery Utilization and Capacity. EIA petroleum gas survey data"""

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


class EiaPetroleumRefineryUtilizationAndCapacityFetcher(
    Fetcher[
        EiaPetroleumRefineryUtilizationAndCapacityQueryParams,
        list[EiaPetroleumRefineryUtilizationAndCapacityData],
    ]
):
    """Refinery Utilization and Capacity fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> EiaPetroleumRefineryUtilizationAndCapacityQueryParams:
        """Transform the query parameters."""
        return transform_dataset_query(
            EiaPetroleumRefineryUtilizationAndCapacityQueryParams, params
        )

    @staticmethod
    async def aextract_data(
        query: EiaPetroleumRefineryUtilizationAndCapacityQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract the data from the EIA API."""
        return await extract_dataset_data(query, credentials)

    @staticmethod
    def transform_data(
        query: EiaPetroleumRefineryUtilizationAndCapacityQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> list[EiaPetroleumRefineryUtilizationAndCapacityData]:
        """Transform the data."""
        return transform_dataset_data(
            EiaPetroleumRefineryUtilizationAndCapacityData, query, data
        )
