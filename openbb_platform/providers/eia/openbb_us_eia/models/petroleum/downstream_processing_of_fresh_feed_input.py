"""Downstream Processing of Fresh Feed Input model."""

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


class EiaPetroleumDownstreamProcessingOfFreshFeedInputQueryParams(EiaApiQueryParams):
    """Downstream Processing of Fresh Feed Input. EIA petroleum gas survey data

    Source: https://www.eia.gov/opendata/browser/petroleum/pnp/dwns
    """

    __group__ = "petroleum"
    __dataset__ = "downstream_processing_of_fresh_feed_input"
    __json_schema_extra__ = {
        "process": {
            "multiple_items_allowed": True,
            "choices": [
                "catalytic_reforming_downstream_capacity",
                "downstream_catalytic_cracking",
                "downstream_catalytic_hydrocracking",
                "downstream_delayed_fluid_coking",
            ],
        },
        "product": {"multiple_items_allowed": True},
        "region": {
            "multiple_items_allowed": True,
            "choices": ["na", "padd_1", "padd_2", "padd_3", "padd_4", "padd_5", "us"],
        },
        "series": {
            "multiple_items_allowed": True,
            "choices": [
                "appalachian_no_1_refining_district_downstream_processing_of_fresh_feed_input_by_catalytic_cracking_units_thousand_barrels_per_day",
                "appalachian_no_1_refining_district_downstream_processing_of_fresh_feed_input_by_catalytic_hydrocracking_units_thousand_barrels_per_day",
                "appalachian_no_1_refining_district_downstream_processing_of_fresh_feed_input_by_delayed_and_fluid_coking_units_thousand_barrels_per_day",
                "east_coast_pad_i_downstream_processing_of_fresh_feed_input_by_catalytic_reforming_units_thousand_barrels_per_day",
                "east_coast_padd_1_downstream_processing_of_fresh_feed_input_by_catalytic_cracking_units_thousand_barrels_per_day",
                "east_coast_padd_1_downstream_processing_of_fresh_feed_input_by_catalytic_hydrocracking_units_thousand_barrels_per_day",
                "east_coast_padd_1_downstream_processing_of_fresh_feed_input_by_delayed_and_fluid_coking_units_thousand_barrels_per_day",
                "east_coast_refining_district_downstream_processing_of_fresh_feed_input_by_catalytic_cracking_units_thousand_barrels_per_day",
                "east_coast_refining_district_downstream_processing_of_fresh_feed_input_by_catalytic_hydrocracking_units_thousand_barrels_per_day",
                "east_coast_refining_district_downstream_processing_of_fresh_feed_input_by_delayed_and_fluid_coking_units_thousand_barrels_per_day",
                "gulf_coast_padd_3_downstream_processing_of_fresh_feed_input_by_catalytic_cracking_units_thousand_barrels_per_day",
                "gulf_coast_padd_3_downstream_processing_of_fresh_feed_input_by_catalytic_hydrocracking_units_thousand_barrels_per_day",
                "gulf_coast_padd_3_downstream_processing_of_fresh_feed_input_by_catalytic_reforming_units_thousand_barrels_per_day",
                "gulf_coast_padd_3_downstream_processing_of_fresh_feed_input_by_delayed_and_fluid_coking_units_thousand_barrels_per_day",
                "midwest_padd_2_downstream_processing_of_fresh_feed_input_by_catalytic_cracking_units_thousand_barrels_per_day",
                "midwest_padd_2_downstream_processing_of_fresh_feed_input_by_catalytic_hydrocracking_units_thousand_barrels_per_day",
                "midwest_padd_2_downstream_processing_of_fresh_feed_input_by_catalytic_reforming_units_thousand_barrels_per_day",
                "midwest_padd_2_downstream_processing_of_fresh_feed_input_by_delayed_and_fluid_coking_units_thousand_barrels_per_day",
                "ref_district_indiana_illinois_kentucky_downstream",
                "ref_district_minnesota_wisconsin_n_and_s_dakota_downstream",
                "refining_district_appalachian_no_1_downstream_processing_of",
                "refining_district_east_coast_downstream_processing_of_fresh",
                "refining_district_indiana_illinois_kentucky_downstream_processing_of_fresh_feed_input_by_catalytic_cracking_units_thousand_barrels_per_day",
                "refining_district_indiana_illinois_kentucky_downstream_processing_of_fresh_feed_input_by_catalytic_hydrocracking_units_thousand_barrels_per_day",
                "refining_district_indiana_illinois_kentucky_downstream_processing_of_fresh_feed_input_by_delayed_and_fluid_coking_units_thousand_barrels_per_day",
                "refining_district_louisiana_gulf_coast_downstream_processing_of_fresh_feed_input_by_catalytic_cracking_units_thousand_barrels_per_day",
                "refining_district_louisiana_gulf_coast_downstream_processing_of_fresh_feed_input_by_catalytic_hydrocracking_units_thousand_barrels_per_day",
                "refining_district_louisiana_gulf_coast_downstream_processing_of_fresh_feed_input_by_catalytic_reforming_units_thousand_barrels_per_day",
                "refining_district_louisiana_gulf_coast_downstream_processing_of_fresh_feed_input_by_delayed_and_fluid_coking_units_thousand_barrels_per_day",
                "refining_district_minnesota_wisconsin_n_and_s_dakota_downstream_processing_of_fresh_feed_input_by_catalytic_cracking_units_thousand_barrels_per_day",
                "refining_district_minnesota_wisconsin_n_and_s_dakota_downstream_processing_of_fresh_feed_input_by_catalytic_hydrocracking_units_thousand_barrels_per_day",
                "refining_district_minnesota_wisconsin_n_and_s_dakota_downstream_processing_of_fresh_feed_input_by_delayed_and_fluid_coking_units_thousand_barrels_per_day",
                "refining_district_new_mexico_downstream_processing_of_fresh_feed_input_by_catalytic_cracking_units_thousand_barrels_per_day",
                "refining_district_new_mexico_downstream_processing_of_fresh_feed_input_by_catalytic_hydrocracking_units_thousand_barrels_per_day",
                "refining_district_new_mexico_downstream_processing_of_fresh_feed_input_by_catalytic_reforming_units_thousand_barrels_per_day",
                "refining_district_new_mexico_downstream_processing_of_fresh_feed_input_by_delayed_and_fluid_coking_units_thousand_barrels_per_day",
                "refining_district_north_louisiana_arkansas_downstream_processing_of_fresh_feed_input_by_catalytic_cracking_units_thousand_barrels_per_day",
                "refining_district_north_louisiana_arkansas_downstream_processing_of_fresh_feed_input_by_catalytic_hydrocracking_units_thousand_barrels_per_day",
                "refining_district_north_louisiana_arkansas_downstream_processing_of_fresh_feed_input_by_catalytic_reforming_units_thousand_barrels_per_day",
                "refining_district_north_louisiana_arkansas_downstream_processing_of_fresh_feed_input_by_delayed_and_fluid_coking_units_thousand_barrels_per_day",
                "refining_district_oklahoma_kansas_missouri_downstream_processing_of_fresh_feed_input_by_catalytic_cracking_units_thousand_barrels_per_day",
                "refining_district_oklahoma_kansas_missouri_downstream_processing_of_fresh_feed_input_by_catalytic_hydrocracking_units_thousand_barrels_per_day",
                "refining_district_oklahoma_kansas_missouri_downstream_processing_of_fresh_feed_input_by_catalytic_reforming_units_thousand_barrels_per_day",
                "refining_district_oklahoma_kansas_missouri_downstream_processing_of_fresh_feed_input_by_delayed_and_fluid_coking_units_thousand_barrels_per_day",
                "refining_district_texas_gulf_coast_downstream_processing_of_fresh_feed_input_by_catalytic_cracking_units_thousand_barrels_per_day",
                "refining_district_texas_gulf_coast_downstream_processing_of_fresh_feed_input_by_catalytic_hydrocracking_units_thousand_barrels_per_day",
                "refining_district_texas_gulf_coast_downstream_processing_of_fresh_feed_input_by_catalytic_reforming_units_thousand_barrels_per_day",
                "refining_district_texas_gulf_coast_downstream_processing_of_fresh_feed_input_by_delayed_and_fluid_coking_units_thousand_barrels_per_day",
                "refining_district_texas_inland_downstream_processing_of_fresh_feed_input_by_catalytic_cracking_units_thousand_barrels_per_day",
                "refining_district_texas_inland_downstream_processing_of_fresh_feed_input_by_catalytic_hydrocracking_units_thousand_barrels_per_day",
                "refining_district_texas_inland_downstream_processing_of_fresh_feed_input_by_catalytic_reforming_units_thousand_barrels_per_day",
                "refining_district_texas_inland_downstream_processing_of_fresh_feed_input_by_delayed_and_fluid_coking_units_thousand_barrels_per_day",
                "rocky_mountain",
                "rocky_mountain_padd_4_downstream_processing_of_fresh_feed_input_by_catalytic_cracking_units_thousand_barrels_per_day",
                "rocky_mountain_padd_4_downstream_processing_of_fresh_feed_input_by_catalytic_hydrocracking_units_thousand_barrels_per_day",
                "rocky_mountain_padd_4_downstream_processing_of_fresh_feed_input_by_delayed_and_fluid_coking_units_thousand_barrels_per_day",
                "us_downstream_processing_of_fresh_feed_input_by_catalytic_cracking_units_thousand_barrels_per_day",
                "us_downstream_processing_of_fresh_feed_input_by_catalytic_hydrocracking_units_thousand_barrels_per_day",
                "us_downstream_processing_of_fresh_feed_input_by_catalytic_reforming_units_thousand_barrels_per_day",
                "us_downstream_processing_of_fresh_feed_input_by_delayed_and",
                "west_coast_padd_5_downstream_processing_of_fresh_feed_input_by_catalytic_cracking_units_thousand_barrels_per_day",
                "west_coast_padd_5_downstream_processing_of_fresh_feed_input_by_catalytic_hydrocracking_units_thousand_barrels_per_day",
                "west_coast_padd_5_downstream_processing_of_fresh_feed_input_by_catalytic_reforming_units_thousand_barrels_per_day",
                "west_coast_padd_5_downstream_processing_of_fresh_feed_input_by_delayed_and_fluid_coking_units_thousand_barrels_per_day",
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
    product: str | None = Field(
        default=None,
        description="Product filter. Accepts a comma-separated list of values. Use the `facet_options` endpoint for the valid values.",
    )
    region: str | None = Field(
        default=None,
        description="DuoArea filter. Accepts a comma-separated list of values.",
    )
    series: str | None = Field(
        default=None,
        description="Series filter. Accepts a comma-separated list of values.",
    )


class EiaPetroleumDownstreamProcessingOfFreshFeedInputData(EiaApiData):
    """Downstream Processing of Fresh Feed Input. EIA petroleum gas survey data"""

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


class EiaPetroleumDownstreamProcessingOfFreshFeedInputFetcher(
    Fetcher[
        EiaPetroleumDownstreamProcessingOfFreshFeedInputQueryParams,
        list[EiaPetroleumDownstreamProcessingOfFreshFeedInputData],
    ]
):
    """Downstream Processing of Fresh Feed Input fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> EiaPetroleumDownstreamProcessingOfFreshFeedInputQueryParams:
        """Transform the query parameters."""
        return transform_dataset_query(
            EiaPetroleumDownstreamProcessingOfFreshFeedInputQueryParams, params
        )

    @staticmethod
    async def aextract_data(
        query: EiaPetroleumDownstreamProcessingOfFreshFeedInputQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract the data from the EIA API."""
        return await extract_dataset_data(query, credentials)

    @staticmethod
    def transform_data(
        query: EiaPetroleumDownstreamProcessingOfFreshFeedInputQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> list[EiaPetroleumDownstreamProcessingOfFreshFeedInputData]:
        """Transform the data."""
        return transform_dataset_data(
            EiaPetroleumDownstreamProcessingOfFreshFeedInputData, query, data
        )
