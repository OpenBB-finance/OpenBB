"""Estimated Natural Gas Plant Liquids contained in Total Natural Gas Proved Reserves model."""

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


class EiaNaturalGasPlantLiquidsInProvedReservesQueryParams(EiaApiQueryParams):
    """Estimated Natural Gas Plant Liquids contained in Total Natural Gas Proved Reserves. EIA natural gas survey data

    Source: https://www.eia.gov/opendata/browser/natural-gas/enr/ngpl
    """

    __group__ = "natural_gas"
    __dataset__ = "plant_liquids_in_proved_reserves"
    __json_schema_extra__ = {
        "region": {
            "multiple_items_allowed": True,
            "choices": [
                "california",
                "colorado",
                "florida",
                "na",
                "ohio",
                "texas",
                "us",
                "usa_ak",
                "usa_al",
                "usa_ar",
                "usa_ks",
                "usa_ky",
                "usa_la",
                "usa_mi",
                "usa_ms",
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
                "alabama_natural_gas_plant_liquids_expected_future_production",
                "alaska_natural_gas_plant_liquids_expected_future_production",
                "arkansas_natural_gas_plant_liquids_expected_future",
                "california_natural_gas_plant_liquids_expected_future",
                "california_coastal_region_onshore_natural_gas_plant_liquids",
                "california_los_angeles_basin_onshore_natural_gas_plant",
                "california_san_joaquin_basin_onshore_natural_gas_plant",
                "california_state_offshore_natural_gas_plant_liquids",
                "colorado_natural_gas_plant_liquids_expected_future",
                "federal_offshore_california_natural_gas_plant_liquids",
                "florida_natural_gas_plant_liquids_expected_future_production",
                "gulf_of_america_federal_offshore_central_and_eastern_natural_gas_plant_liquids_expected_future_production_million_barrels",
                "gulf_of_america_federal_offshore_western_natural_gas_plant_liquids_expected_future_production_million_barrels",
                "kansas_natural_gas_plant_liquids_expected_future_production",
                "kentucky_natural_gas_plant_liquids_expected_future",
                "louisiana_natural_gas_plant_liquids_expected_future",
                "louisiana_north_natural_gas_plant_liquids_expected_future",
                "louisiana_south_onshore_natural_gas_plant_liquids_expected",
                "louisiana_state_offshore_natural_gas_plant_liquids_expected",
                "lower_48_federal_offshore_natural_gas_plant_liquids",
                "lower_48_states_natural_gas_plant_liquids_expected_future",
                "michigan_natural_gas_plant_liquids_expected_future",
                "mississippi_natural_gas_plant_liquids_expected_future",
                "montana_natural_gas_plant_liquids_expected_future_production",
                "new_mexico_natural_gas_plant_liquids_expected_future",
                "new_mexico_east_natural_gas_plant_liquids_expected_future",
                "new_mexico_west_natural_gas_plant_liquids_expected_future",
                "north_dakota_natural_gas_plant_liquids_expected_future",
                "ohio_natural_gas_plant_liquids_expected_future_production",
                "oklahoma_natural_gas_plant_liquids_expected_future",
                "pennsylvania_natural_gas_plant_liquids_expected_future",
                "texas_natural_gas_plant_liquids_expected_future_production",
                "texas_rrc_district_1_natural_gas_plant_liquids_expected",
                "texas_rrc_district_10_natural_gas_plant_liquids_expected",
                "texas_rrc_district_2_onshore_natural_gas_plant_liquids",
                "texas_rrc_district_3_onshore_natural_gas_plant_liquids",
                "texas_rrc_district_4_onshore_natural_gas_plant_liquids",
                "texas_rrc_district_5_natural_gas_plant_liquids_expected",
                "texas_rrc_district_6_natural_gas_plant_liquids_expected",
                "texas_rrc_district_7b_natural_gas_plant_liquids_expected",
                "texas_rrc_district_7c_natural_gas_plant_liquids_expected",
                "texas_rrc_district_8_natural_gas_plant_liquids_expected",
                "texas_rrc_district_8a_natural_gas_plant_liquids_expected",
                "texas_rrc_district_9_natural_gas_plant_liquids_expected",
                "texas_state_offshore_natural_gas_plant_liquids_expected",
                "us_natural_gas_plant_liquids_expected_future_production",
                "utah_natural_gas_plant_liquids_expected_future_production",
                "utah_and_wyoming_natural_gas_plant_liquids_expected_future",
                "west_virginia_natural_gas_plant_liquids_expected_future",
                "wyoming_natural_gas_plant_liquids_expected_future_production",
            ],
        },
    }

    region: str | None = Field(
        default=None,
        description="DuoArea filter. Accepts a comma-separated list of values.",
    )
    series: str | None = Field(
        default=None,
        description="Series filter. Accepts a comma-separated list of values.",
    )


class EiaNaturalGasPlantLiquidsInProvedReservesData(EiaApiData):
    """Estimated Natural Gas Plant Liquids contained in Total Natural Gas Proved Reserves. EIA natural gas survey data"""

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


class EiaNaturalGasPlantLiquidsInProvedReservesFetcher(
    Fetcher[
        EiaNaturalGasPlantLiquidsInProvedReservesQueryParams,
        list[EiaNaturalGasPlantLiquidsInProvedReservesData],
    ]
):
    """Estimated Natural Gas Plant Liquids contained in Total Natural Gas Proved Reserves fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> EiaNaturalGasPlantLiquidsInProvedReservesQueryParams:
        """Transform the query parameters."""
        return transform_dataset_query(
            EiaNaturalGasPlantLiquidsInProvedReservesQueryParams, params
        )

    @staticmethod
    async def aextract_data(
        query: EiaNaturalGasPlantLiquidsInProvedReservesQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract the data from the EIA API."""
        return await extract_dataset_data(query, credentials)

    @staticmethod
    def transform_data(
        query: EiaNaturalGasPlantLiquidsInProvedReservesQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> list[EiaNaturalGasPlantLiquidsInProvedReservesData]:
        """Transform the data."""
        return transform_dataset_data(
            EiaNaturalGasPlantLiquidsInProvedReservesData, query, data
        )
