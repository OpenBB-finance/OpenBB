"""Crude Oil and Lease Condensate Production by API Gravity model."""

from typing import Any

from openbb_core.provider.abstract.fetcher import Fetcher
from pydantic import Field

from openbb_us_eia.utils.api_query import (
    EiaApiData,
    EiaApiQueryParams,
    extract_dataset_data,
    transform_dataset_data,
    transform_dataset_query,
)


class EiaPetroleumCrudeOilAndLeaseCondensateProductionByApiGravityQueryParams(
    EiaApiQueryParams
):
    """Crude Oil and Lease Condensate Production by API Gravity. EIA petroleum gas survey data

    Source: https://www.eia.gov/opendata/browser/petroleum/crd/api
    """

    __group__ = "petroleum"
    __dataset__ = "crude_oil_and_lease_condensate_production_by_api_gravity"
    __json_schema_extra__ = {
        "product": {
            "multiple_items_allowed": True,
            "choices": [
                "crude_gravity_20_0_percent_or_less",
                "crude_gravity_20_1_to_25_0_percent",
                "crude_gravity_25_1_to_30_0_percent",
                "crude_gravity_30_0_percent_or_less",
                "crude_gravity_30_1_to_35_0_percent",
                "crude_gravity_30_1_to_40_0_percent",
                "crude_gravity_35_1_to_40_0_percent",
                "crude_gravity_40_1_to_45_0_percent",
                "crude_gravity_40_1_to_50_0_percent",
                "crude_gravity_45_1_to_50_0_percent",
                "crude_gravity_50_1_percent_or_more",
                "crude_gravity_50_1_to_55_0_percent",
                "crude_gravity_55_1_percent_or_more",
                "crude_gravity_of_all",
                "crude_gravity_of_unkown",
            ],
        },
        "region": {
            "multiple_items_allowed": True,
            "choices": [
                "california",
                "colorado",
                "na",
                "ohio",
                "texas",
                "usa_ar",
                "usa_ks",
                "usa_la",
                "usa_mt",
                "usa_nd",
                "usa_nm",
                "usa_ok",
                "usa_pa",
                "usa_ut",
                "usa_wv",
                "usa_wy",
            ],
        },
        "series": {
            "multiple_items_allowed": True,
            "choices": [
                "arkansas_crude_oil_and_lease_condensate_production_for_30_0",
                "arkansas_crude_oil_and_lease_condensate_production_for_30_1",
                "arkansas_crude_oil_and_lease_condensate_production_for_40_1",
                "arkansas_crude_oil_and_lease_condensate_production_for_50_1",
                "arkansas_crude_oil_and_lease_condensate_production_for_all",
                "california_crude_oil_and_lease_condensate_production_for_30_0_or_lower_degrees_api_gravity_thousand_barrels_per_day",
                "california_crude_oil_and_lease_condensate_production_for_30_1_to_40_0_degrees_api_gravity_thousand_barrels_per_day",
                "california_crude_oil_and_lease_condensate_production_for_40",
                "california_crude_oil_and_lease_condensate_production_for_50",
                "california_crude_oil_and_lease_condensate_production_for",
                "colorado_crude_oil_and_lease_condensate_production_for_30_0",
                "colorado_crude_oil_and_lease_condensate_production_for_30_1",
                "colorado_crude_oil_and_lease_condensate_production_for_40_1",
                "colorado_crude_oil_and_lease_condensate_production_for_50_1",
                "colorado_crude_oil_and_lease_condensate_production_for_all",
                "federal_offshore_gulf_of_america_crude_oil_and_lease_condensate_production_for_30_0_or_lower_degrees_api_gravity_thousand_barrels_per_day",
                "federal_offshore_gulf_of_america_crude_oil_and_lease_condensate_production_for_30_1_to_40_0_degrees_api_gravity_thousand_barrels_per_day",
                "federal_offshore_gulf_of_america_crude_oil_and_lease_condensate_production_for_40_1_to_50_0_degrees_api_gravity_thousand_barrels_per_day",
                "federal_offshore_gulf_of_america_crude_oil_and_lease_condensate_production_for_50_1_or_higher_degrees_api_gravity_thousand_barrels_per_day",
                "federal_offshore_gulf_of_america_crude_oil_and_lease_condensate_production_for_all_api_gravity_thousand_barrels_per_day",
                "kansas_crude_oil_and_lease_condensate_production_for_30_0",
                "kansas_crude_oil_and_lease_condensate_production_for_30_1",
                "kansas_crude_oil_and_lease_condensate_production_for_40_1",
                "kansas_crude_oil_and_lease_condensate_production_for_50_1",
                "kansas_crude_oil_and_lease_condensate_production_for_all",
                "louisiana_crude_oil_and_lease_condensate_production_for_30_0_or_lower_degrees_api_gravity_thousand_barrels_per_day",
                "louisiana_crude_oil_and_lease_condensate_production_for_30_1_to_40_0_degrees_api_gravity_thousand_barrels_per_day",
                "louisiana_crude_oil_and_lease_condensate_production_for_40",
                "louisiana_crude_oil_and_lease_condensate_production_for_50",
                "louisiana_crude_oil_and_lease_condensate_production_for_all",
                "lower_48_states_crude_oil_and_lease_condensate_production_for_20_0_or_lower_degrees_api_gravity_thousand_barrels_per_day",
                "lower_48_states_crude_oil_and_lease_condensate_production_for_20_1_to_25_0_degrees_api_gravity_thousand_barrels_per_day",
                "lower_48_states_crude_oil_and_lease_condensate_production_for_25_1_to_30_0_degrees_api_gravity_thousand_barrels_per_day",
                "lower_48_states_crude_oil_and_lease_condensate_production_for_30_1_to_35_0_degrees_api_gravity_thousand_barrels_per_day",
                "lower_48_states_crude_oil_and_lease_condensate_production_for_35_1_to_40_0_degrees_api_gravity_thousand_barrels_per_day",
                "lower_48_states_crude_oil_and_lease_condensate_production_for_40_1_to_45_0_degrees_api_gravity_thousand_barrels_per_day",
                "lower_48_states_crude_oil_and_lease_condensate_production_for_45_1_to_50_0_degrees_api_gravity_thousand_barrels_per_day",
                "lower_48_states_crude_oil_and_lease_condensate_production_for_50_1_to_55_0_degrees_api_gravity_thousand_barrels_per_day",
                "lower_48_states_crude_oil_and_lease_condensate_production_for_55_1_or_higher_degrees_api_gravity_thousand_barrels_per_day",
                "lower_48_states_crude_oil_and_lease_condensate_production_for_unknown_api_gravity_thousand_barrels_per_day",
                "lower_48_states_crude_oil_and_lease_condensate_production_for_all_api_gravity_thousand_barrels_per_day",
                "montana_crude_oil_and_lease_condensate_production_for_30_0",
                "montana_crude_oil_and_lease_condensate_production_for_30_1",
                "montana_crude_oil_and_lease_condensate_production_for_40_1",
                "montana_crude_oil_and_lease_condensate_production_for_50_1",
                "montana_crude_oil_and_lease_condensate_production_for_all",
                "new_mexico_crude_oil_and_lease_condensate_production_for_30_0_or_lower_degrees_api_gravity_thousand_barrels_per_day",
                "new_mexico_crude_oil_and_lease_condensate_production_for_30_1_to_40_0_degrees_api_gravity_thousand_barrels_per_day",
                "new_mexico_crude_oil_and_lease_condensate_production_for_40",
                "new_mexico_crude_oil_and_lease_condensate_production_for_50",
                "new_mexico_crude_oil_and_lease_condensate_production_for",
                "north_dakota_crude_oil_and_lease_condensate_production_for_30_0_or_lower_degrees_api_gravity_thousand_barrels_per_day",
                "north_dakota_crude_oil_and_lease_condensate_production_for_30_1_to_40_0_degrees_api_gravity_thousand_barrels_per_day",
                "north_dakota_crude_oil_and_lease_condensate_production_for_40_1_to_50_0_degrees_api_gravity_thousand_barrels_per_day",
                "north_dakota_crude_oil_and_lease_condensate_production_for_50_1_or_higher_degrees_api_gravity_thousand_barrels_per_day",
                "north_dakota_crude_oil_and_lease_condensate_production_for_all_api_gravity_thousand_barrels_per_day",
                "ohio_crude_oil_and_lease_condensate_production_for_30_0_or",
                "ohio_crude_oil_and_lease_condensate_production_for_30_1_to",
                "ohio_crude_oil_and_lease_condensate_production_for_40_1_to",
                "ohio_crude_oil_and_lease_condensate_production_for_50_1_or",
                "ohio_crude_oil_and_lease_condensate_production_for_all_api",
                "oklahoma_crude_oil_and_lease_condensate_production_for_30_0",
                "oklahoma_crude_oil_and_lease_condensate_production_for_30_1",
                "oklahoma_crude_oil_and_lease_condensate_production_for_40_1",
                "oklahoma_crude_oil_and_lease_condensate_production_for_50_1",
                "oklahoma_crude_oil_and_lease_condensate_production_for_all",
                "other_states_crude_oil_and_lease_condensate_production_for_30_0_or_lower_degrees_api_gravity_thousand_barrels_per_day",
                "other_states_crude_oil_and_lease_condensate_production_for_30_1_to_40_0_degrees_api_gravity_thousand_barrels_per_day",
                "other_states_crude_oil_and_lease_condensate_production_for_40_1_to_50_0_degrees_api_gravity_thousand_barrels_per_day",
                "other_states_crude_oil_and_lease_condensate_production_for_50_1_or_higher_degrees_api_gravity_thousand_barrels_per_day_ull",
                "other_states_crude_oil_and_lease_condensate_production_for_all_api_gravity_thousand_barrels_per_day",
                "pennsylvania_crude_oil_and_lease_condensate_production_for_30_0_or_lower_degrees_api_gravity_thousand_barrels_per_day",
                "pennsylvania_crude_oil_and_lease_condensate_production_for_30_1_to_40_0_degrees_api_gravity_thousand_barrels_per_day",
                "pennsylvania_crude_oil_and_lease_condensate_production_for_40_1_to_50_0_degrees_api_gravity_thousand_barrels_per_day",
                "pennsylvania_crude_oil_and_lease_condensate_production_for_50_1_or_higher_degrees_api_gravity_thousand_barrels_per_day",
                "pennsylvania_crude_oil_and_lease_condensate_production_for_all_api_gravity_thousand_barrels_per_day",
                "texas_crude_oil_and_lease_condensate_production_for_30_0_or",
                "texas_crude_oil_and_lease_condensate_production_for_30_1_to",
                "texas_crude_oil_and_lease_condensate_production_for_40_1_to",
                "texas_crude_oil_and_lease_condensate_production_for_50_1_or",
                "texas_crude_oil_and_lease_condensate_production_for_all_api",
                "utah_crude_oil_and_lease_condensate_production_for_30_0_or",
                "utah_crude_oil_and_lease_condensate_production_for_30_1_to",
                "utah_crude_oil_and_lease_condensate_production_for_40_1_to",
                "utah_crude_oil_and_lease_condensate_production_for_50_1_or",
                "utah_crude_oil_and_lease_condensate_production_for_all_api",
                "west_virginia_crude_oil_and_lease_condensate_production_for_30_0_or_lower_degrees_api_gravity_thousand_barrels_per_day",
                "west_virginia_crude_oil_and_lease_condensate_production_for_30_1_to_40_0_degrees_api_gravity_thousand_barrels_per_day",
                "west_virginia_crude_oil_and_lease_condensate_production_for_40_1_to_50_0_degrees_api_gravity_thousand_barrels_per_day",
                "west_virginia_crude_oil_and_lease_condensate_production_for_50_1_or_higher_degrees_api_gravity_thousand_barrels_per_day",
                "west_virginia_crude_oil_and_lease_condensate_production_for_all_api_gravity_thousand_barrels_per_day",
                "wyoming_crude_oil_and_lease_condensate_production_for_30_0",
                "wyoming_crude_oil_and_lease_condensate_production_for_30_1",
                "wyoming_crude_oil_and_lease_condensate_production_for_40_1",
                "wyoming_crude_oil_and_lease_condensate_production_for_50_1",
                "wyoming_crude_oil_and_lease_condensate_production_for_all",
            ],
        },
    }

    product: str | None = Field(
        default=None,
        description="Product filter. Accepts a comma-separated list of values.",
    )
    region: str | None = Field(
        default=None,
        description="DuoArea filter. Accepts a comma-separated list of values.",
    )
    series: str | None = Field(
        default=None,
        description="Series filter. Accepts a comma-separated list of values.",
    )


class EiaPetroleumCrudeOilAndLeaseCondensateProductionByApiGravityData(EiaApiData):
    """Crude Oil and Lease Condensate Production by API Gravity. EIA petroleum gas survey data"""

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


class EiaPetroleumCrudeOilAndLeaseCondensateProductionByApiGravityFetcher(
    Fetcher[
        EiaPetroleumCrudeOilAndLeaseCondensateProductionByApiGravityQueryParams,
        list[EiaPetroleumCrudeOilAndLeaseCondensateProductionByApiGravityData],
    ]
):
    """Crude Oil and Lease Condensate Production by API Gravity fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> EiaPetroleumCrudeOilAndLeaseCondensateProductionByApiGravityQueryParams:
        """Transform the query parameters."""
        return transform_dataset_query(
            EiaPetroleumCrudeOilAndLeaseCondensateProductionByApiGravityQueryParams,
            params,
        )

    @staticmethod
    async def aextract_data(
        query: EiaPetroleumCrudeOilAndLeaseCondensateProductionByApiGravityQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract the data from the EIA API."""
        return await extract_dataset_data(query, credentials)

    @staticmethod
    def transform_data(
        query: EiaPetroleumCrudeOilAndLeaseCondensateProductionByApiGravityQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> list[EiaPetroleumCrudeOilAndLeaseCondensateProductionByApiGravityData]:
        """Transform the data."""
        return transform_dataset_data(
            EiaPetroleumCrudeOilAndLeaseCondensateProductionByApiGravityData,
            query,
            data,
        )
