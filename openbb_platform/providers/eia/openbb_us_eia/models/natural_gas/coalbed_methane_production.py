"""Coalbed Methane Production model."""

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


class EiaNaturalGasCoalbedMethaneProductionQueryParams(EiaApiQueryParams):
    """Coalbed Methane Production. EIA natural gas survey data

    Source: https://www.eia.gov/opendata/browser/natural-gas/prod/coalbed
    """

    __group__ = "natural_gas"
    __dataset__ = "coalbed_methane_production"
    __json_schema_extra__ = {
        "region": {
            "multiple_items_allowed": True,
            "choices": [
                "california",
                "colorado",
                "florida",
                "na",
                "new_york",
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
                "usa_va",
                "usa_wv",
                "usa_wy",
            ],
        },
        "series": {
            "multiple_items_allowed": True,
            "choices": [
                "alabama_coalbed_methane_production",
                "alaska_coalbed_methane_production",
                "arkansas_coalbed_methane_production",
                "california_coalbed_methane_production",
                "colorado_coalbed_methane_production",
                "eastern_states_coalbed_methane_production",
                "florida_coalbed_methane_production",
                "kansas_coalbed_methane_production",
                "kentucky_coalbed_methane_production",
                "louisiana_coalbed_methane_production",
                "louisiana_north_coalbed_methane_production",
                "louisiana_south_onshore_coalbed_methane_production",
                "louisiana_state_offshore_coalbed_methane_production",
                "lower_48_federal_offshore_coalbed_methane_production",
                "lower_48_states_coalbed_methane_production",
                "michigan_coalbed_methane_production",
                "mississippi_coalbed_methane_production",
                "montana_coalbed_methane_production",
                "new_mexico_coalbed_methane_production",
                "new_mexico_east_coalbed_methane_production",
                "new_mexico_west_coalbed_methane_production",
                "new_york_coalbed_methane_production",
                "north_dakota_coalbed_methane_production",
                "ohio_coalbed_methane_production",
                "oklahoma_coalbed_methane_production",
                "other_states_natural_gas_coalbed_methane_reserves_based",
                "pennsylvania_coalbed_methane_production",
                "texas_coalbed_methane_production",
                "texas_rrc_district_1_coalbed_methane_production",
                "texas_rrc_district_10_coalbed_methane_production",
                "texas_rrc_district_2_onshore_coalbed_methane_production",
                "texas_rrc_district_3_onshore_coalbed_methane_production",
                "texas_rrc_district_4_onshore_coalbed_methane_production",
                "texas_rrc_district_5_coalbed_methane_production",
                "texas_rrc_district_6_coalbed_methane_production",
                "texas_rrc_district_7b_coalbed_methane_production",
                "texas_rrc_district_7c_coalbed_methane_production",
                "texas_rrc_district_8_coalbed_methane_production",
                "texas_rrc_district_8a_coalbed_methane_production",
                "texas_rrc_district_9_coalbed_methane_production",
                "texas_state_offshore_coalbed_methane_production",
                "us_coalbed_methane_production",
                "utah_coalbed_methane_production",
                "virginia_coalbed_methane_production",
                "west_virginia_coalbed_methane_production",
                "western_states_coalbed_methane_production",
                "wyoming_coalbed_methane_production",
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


class EiaNaturalGasCoalbedMethaneProductionData(EiaApiData):
    """Coalbed Methane Production. EIA natural gas survey data"""

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


class EiaNaturalGasCoalbedMethaneProductionFetcher(
    Fetcher[
        EiaNaturalGasCoalbedMethaneProductionQueryParams,
        list[EiaNaturalGasCoalbedMethaneProductionData],
    ]
):
    """Coalbed Methane Production fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> EiaNaturalGasCoalbedMethaneProductionQueryParams:
        """Transform the query parameters."""
        return transform_dataset_query(
            EiaNaturalGasCoalbedMethaneProductionQueryParams, params
        )

    @staticmethod
    async def aextract_data(
        query: EiaNaturalGasCoalbedMethaneProductionQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract the data from the EIA API."""
        return await extract_dataset_data(query, credentials)

    @staticmethod
    def transform_data(
        query: EiaNaturalGasCoalbedMethaneProductionQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> list[EiaNaturalGasCoalbedMethaneProductionData]:
        """Transform the data."""
        return transform_dataset_data(
            EiaNaturalGasCoalbedMethaneProductionData, query, data
        )
