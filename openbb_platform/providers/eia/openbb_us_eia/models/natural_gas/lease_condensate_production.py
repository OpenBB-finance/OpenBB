"""Lease Condensate Production model."""

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


class EiaNaturalGasLeaseCondensateProductionQueryParams(EiaApiQueryParams):
    """Lease Condensate Production. EIA natural gas survey data

    Source: https://www.eia.gov/opendata/browser/natural-gas/prod/lc
    """

    __group__ = "natural_gas"
    __dataset__ = "lease_condensate_production"
    __json_schema_extra__ = {
        "region": {
            "multiple_items_allowed": True,
            "choices": [
                "california",
                "colorado",
                "florida",
                "na",
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
                "alabama_natural_gas_liquids_lease_condensate_reserves_based",
                "alaska_natural_gas_liquids_lease_condensate_reserves_based",
                "arkansas_natural_gas_liquids_lease_condensate_reserves",
                "calif_coastal_region_onshore_natural_gas_liquids_lease",
                "calif_los_angeles_basin_onshore_natural_gas_liquids_lease",
                "calif_san_joaquin_basin_onshore_natural_gas_liquids_lease",
                "california_natural_gas_liquids_lease_condensate_reserves",
                "california_state_offshore_natural_gas_liquids_lease",
                "colorado_natural_gas_liquids_lease_condensate_reserves",
                "federal_offshore_california_natural_gas_liquids_lease",
                "florida_natural_gas_liquids_lease_condensate_reserves_based",
                "gulf_of_america_federal_offshore_central_and_eastern_natural_gas_liquids_lease_condensate_reserves_based_production_million_barrels",
                "gulf_of_america_federal_offshore_western_natural_gas_liquids_lease_condensate_reserves_based_production_million_barrels",
                "kansas_natural_gas_liquids_lease_condensate_reserves_based",
                "kentucky_natural_gas_liquids_lease_condensate_reserves",
                "louisiana_natural_gas_liquids_lease_condensate_reserves",
                "louisiana_north_natural_gas_liquids_lease_condensate",
                "louisiana_south_onshore_natural_gas_liquids_lease",
                "louisiana_state_offshore_natural_gas_liquids_lease",
                "lower_48_federal_offshore_natural_gas_liquids_lease",
                "lower_48_states_natural_gas_liquids_lease_condensate",
                "michigan_natural_gas_liquids_lease_condensate_reserves",
                "mississippi_natural_gas_liquids_lease_condensate_reserves",
                "montana_natural_gas_liquids_lease_condensate_reserves_based",
                "new_mexico_natural_gas_liquids_lease_condensate_reserves",
                "new_mexico_east_natural_gas_liquids_lease_condensate",
                "new_mexico_west_natural_gas_liquids_lease_condensate",
                "north_dakota_natural_gas_liquids_lease_condensate_reserves",
                "oklahoma_natural_gas_liquids_lease_condensate_reserves",
                "texas_natural_gas_liquids_lease_condensate_reserves_based",
                "texas_rrc_district_1_natural_gas_liquids_lease_condensate",
                "texas_rrc_district_10_natural_gas_liquids_lease_condensate",
                "texas_rrc_district_2_onshore_natural_gas_liquids_lease",
                "texas_rrc_district_3_onshore_natural_gas_liquids_lease",
                "texas_rrc_district_4_onshore_natural_gas_liquids_lease",
                "texas_rrc_district_5_natural_gas_liquids_lease_condensate",
                "texas_rrc_district_6_natural_gas_liquids_lease_condensate",
                "texas_rrc_district_7b_natural_gas_liquids_lease_condensate",
                "texas_rrc_district_7c_natural_gas_liquids_lease_condensate",
                "texas_rrc_district_8_natural_gas_liquids_lease_condensate",
                "texas_rrc_district_8a_natural_gas_liquids_lease_condensate",
                "texas_rrc_district_9_natural_gas_liquids_lease_condensate",
                "texas_state_offshore_natural_gas_liquids_lease_condensate",
                "us_natural_gas_liquids_lease_condensate_reserves_based",
                "utah_natural_gas_liquids_lease_condensate_reserves_based",
                "utah_and_wyoming_natural_gas_liquids_lease_condensate",
                "west_virginia_natural_gas_liquids_lease_condensate_reserves",
                "wyoming_natural_gas_liquids_lease_condensate_reserves_based",
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


class EiaNaturalGasLeaseCondensateProductionData(EiaApiData):
    """Lease Condensate Production. EIA natural gas survey data"""

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


class EiaNaturalGasLeaseCondensateProductionFetcher(
    Fetcher[
        EiaNaturalGasLeaseCondensateProductionQueryParams,
        list[EiaNaturalGasLeaseCondensateProductionData],
    ]
):
    """Lease Condensate Production fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> EiaNaturalGasLeaseCondensateProductionQueryParams:
        """Transform the query parameters."""
        return transform_dataset_query(
            EiaNaturalGasLeaseCondensateProductionQueryParams, params
        )

    @staticmethod
    async def aextract_data(
        query: EiaNaturalGasLeaseCondensateProductionQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract the data from the EIA API."""
        return await extract_dataset_data(query, credentials)

    @staticmethod
    def transform_data(
        query: EiaNaturalGasLeaseCondensateProductionQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> list[EiaNaturalGasLeaseCondensateProductionData]:
        """Transform the data."""
        return transform_dataset_data(
            EiaNaturalGasLeaseCondensateProductionData, query, data
        )
