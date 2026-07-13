"""Natural Gas Plant Liquids Production model."""

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


class EiaNaturalGasNaturalGasPlantLiquidsProductionQueryParams(EiaApiQueryParams):
    """Natural Gas Plant Liquids Production. EIA natural gas survey data

    Source: https://www.eia.gov/opendata/browser/natural-gas/prod/ngpl
    """

    __group__ = "natural_gas"
    __dataset__ = "natural_gas_plant_liquids_production"
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
                "usa_ut",
                "usa_wv",
                "usa_wy",
            ],
        },
        "series": {
            "multiple_items_allowed": True,
            "choices": [
                "alabama_natural_gas_plant_liquids_reserves_based_production",
                "alaska_natural_gas_plant_liquids_reserves_based_production",
                "arkansas_natural_gas_plant_liquids_reserves_based_production",
                "calif_coastal_region_onshore_natural_gas_plant_liquids",
                "calif_los_angeles_basin_onshore_natural_gas_plant_liquids",
                "calif_san_joaquin_basin_onshore_natural_gas_plant_liquids",
                "california_natural_gas_plant_liquids_reserves_based",
                "california_state_offshore_natural_gas_plant_liquids",
                "colorado_natural_gas_plant_liquids_reserves_based_production",
                "federal_offshore_california_natural_gas_plant_liquids",
                "florida_natural_gas_plant_liquids_reserves_based_production",
                "gulf_of_america_federal_offshore_central_and_eastern_natural_gas_plant_liquids_reserves_based_production_million_barrels",
                "gulf_of_america_federal_offshore_western_natural_gas_plant_liquids_reserves_based_production_million_barrels",
                "kansas_natural_gas_plant_liquids_reserves_based_production",
                "kentucky_natural_gas_plant_liquids_reserves_based_production",
                "louisiana_natural_gas_plant_liquids_reserves_based",
                "louisiana_north_natural_gas_plant_liquids_reserves_based",
                "louisiana_south_onshore_natural_gas_plant_liquids_reserves",
                "louisiana_state_offshore_natural_gas_plant_liquids_reserves",
                "lower_48_federal_offshore_natural_gas_plant_liquids",
                "lower_48_states_natural_gas_plant_liquids_reserves_based",
                "michigan_natural_gas_plant_liquids_reserves_based_production",
                "mississippi_natural_gas_plant_liquids_reserves_based",
                "montana_natural_gas_plant_liquids_reserves_based_production",
                "new_mexico_natural_gas_plant_liquids_reserves_based",
                "new_mexico_east_natural_gas_plant_liquids_reserves_based",
                "new_mexico_west_natural_gas_plant_liquids_reserves_based",
                "north_dakota_natural_gas_plant_liquids_reserves_based",
                "ohio_natural_gas_plant_liquids_reserves_based_production",
                "oklahoma_natural_gas_plant_liquids_reserves_based_production",
                "texas_natural_gas_plant_liquids_reserves_based_production",
                "texas_rrc_district_1_natural_gas_plant_liquids_reserves",
                "texas_rrc_district_10_natural_gas_plant_liquids_reserves",
                "texas_rrc_district_2_onshore_natural_gas_plant_liquids",
                "texas_rrc_district_3_onshore_natural_gas_plant_liquids",
                "texas_rrc_district_4_onshore_natural_gas_plant_liquids",
                "texas_rrc_district_5_natural_gas_plant_liquids_reserves",
                "texas_rrc_district_6_natural_gas_plant_liquids_reserves",
                "texas_rrc_district_7b_natural_gas_plant_liquids_reserves",
                "texas_rrc_district_7c_natural_gas_plant_liquids_reserves",
                "texas_rrc_district_8_natural_gas_plant_liquids_reserves",
                "texas_rrc_district_8a_natural_gas_plant_liquids_reserves",
                "texas_rrc_district_9_natural_gas_plant_liquids_reserves",
                "texas_state_offshore_natural_gas_plant_liquids_reserves",
                "us_natural_gas_plant_liquids_reserves_based_production",
                "utah_natural_gas_plant_liquids_reserves_based_production",
                "utah_and_wyoming_natural_gas_plant_liquids_reserves_based",
                "west_virginia_natural_gas_plant_liquids_reserves_based",
                "wyoming_natural_gas_plant_liquids_reserves_based_production",
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


class EiaNaturalGasNaturalGasPlantLiquidsProductionData(EiaApiData):
    """Natural Gas Plant Liquids Production. EIA natural gas survey data"""

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


class EiaNaturalGasNaturalGasPlantLiquidsProductionFetcher(
    Fetcher[
        EiaNaturalGasNaturalGasPlantLiquidsProductionQueryParams,
        list[EiaNaturalGasNaturalGasPlantLiquidsProductionData],
    ]
):
    """Natural Gas Plant Liquids Production fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> EiaNaturalGasNaturalGasPlantLiquidsProductionQueryParams:
        """Transform the query parameters."""
        return transform_dataset_query(
            EiaNaturalGasNaturalGasPlantLiquidsProductionQueryParams, params
        )

    @staticmethod
    async def aextract_data(
        query: EiaNaturalGasNaturalGasPlantLiquidsProductionQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract the data from the EIA API."""
        return await extract_dataset_data(query, credentials)

    @staticmethod
    def transform_data(
        query: EiaNaturalGasNaturalGasPlantLiquidsProductionQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> list[EiaNaturalGasNaturalGasPlantLiquidsProductionData]:
        """Transform the data."""
        return transform_dataset_data(
            EiaNaturalGasNaturalGasPlantLiquidsProductionData, query, data
        )
