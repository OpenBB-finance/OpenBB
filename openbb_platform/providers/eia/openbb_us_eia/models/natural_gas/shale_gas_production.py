"""Shale Gas Production model."""

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


class EiaNaturalGasShaleGasProductionQueryParams(EiaApiQueryParams):
    """Shale Gas Production. EIA natural gas survey data

    Source: https://www.eia.gov/opendata/browser/natural-gas/prod/shalegas
    """

    __group__ = "natural_gas"
    __dataset__ = "shale_gas_production"
    __json_schema_extra__ = {
        "region": {
            "multiple_items_allowed": True,
            "choices": [
                "california",
                "colorado",
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
                "alabama_shale_production",
                "alaska_shale_production",
                "arkansas_shale_production",
                "california_shale_production",
                "colorado_shale_production",
                "eastern_states_shale_production",
                "kansas_shale_production",
                "kentucky_shale_production",
                "louisiana_shale_production",
                "louisiana_north_shale_production",
                "louisiana_south_onshore_shale_production",
                "lower_48_federal_offshore_shale_production",
                "michigan_shale_production",
                "mississippi_shale_production",
                "montana_shale_production",
                "new_mexico_shale_production",
                "new_mexico_east_shale_production",
                "new_mexico_west_shale_production",
                "new_york_shale_production",
                "north_dakota_shale_production",
                "ohio_shale_production",
                "oklahoma_shale_production",
                "pennsylvania_shale_production",
                "texas_shale_production",
                "texas_rrc_district_1_shale_production",
                "texas_rrc_district_10_shale_production",
                "texas_rrc_district_2_onsh_shale_production",
                "texas_rrc_district_3_onsh_shale_production",
                "texas_rrc_district_4_onsh_shale_production",
                "texas_rrc_district_5_shale_production",
                "texas_rrc_district_6_shale_production",
                "texas_rrc_district_7b_shale_production",
                "texas_rrc_district_7c_shale_production",
                "texas_rrc_district_8_shale_production",
                "texas_rrc_district_8a_shale_production",
                "texas_rrc_district_9_shale_production",
                "us_shale_production",
                "utah_shale_production",
                "virginia_shale_production",
                "west_virginia_shale_production",
                "western_states_shale_production",
                "wyoming_shale_production",
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


class EiaNaturalGasShaleGasProductionData(EiaApiData):
    """Shale Gas Production. EIA natural gas survey data"""

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


class EiaNaturalGasShaleGasProductionFetcher(
    Fetcher[
        EiaNaturalGasShaleGasProductionQueryParams,
        list[EiaNaturalGasShaleGasProductionData],
    ]
):
    """Shale Gas Production fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> EiaNaturalGasShaleGasProductionQueryParams:
        """Transform the query parameters."""
        return transform_dataset_query(
            EiaNaturalGasShaleGasProductionQueryParams, params
        )

    @staticmethod
    async def aextract_data(
        query: EiaNaturalGasShaleGasProductionQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract the data from the EIA API."""
        return await extract_dataset_data(query, credentials)

    @staticmethod
    def transform_data(
        query: EiaNaturalGasShaleGasProductionQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> list[EiaNaturalGasShaleGasProductionData]:
        """Transform the data."""
        return transform_dataset_data(EiaNaturalGasShaleGasProductionData, query, data)
