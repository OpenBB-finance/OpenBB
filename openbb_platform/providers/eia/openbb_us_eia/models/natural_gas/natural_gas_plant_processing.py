"""Natural Gas Plant Processing model."""

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


class EiaNaturalGasNaturalGasPlantProcessingQueryParams(EiaApiQueryParams):
    """Natural Gas Plant Processing. EIA natural gas survey data

    Source: https://www.eia.gov/opendata/browser/natural-gas/prod/pp
    """

    __group__ = "natural_gas"
    __dataset__ = "natural_gas_plant_processing"
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
                "usa_id",
                "usa_il",
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
                "usa_sd",
                "usa_tn",
                "usa_ut",
                "usa_wv",
                "usa_wy",
            ],
        },
        "series": {
            "multiple_items_allowed": True,
            "choices": [
                "alabama_natural_gas_plant_liquids_production",
                "alaska_natural_gas_plant_liquids_production",
                "arkansas_natural_gas_plant_liquids_production",
                "california_natural_gas_plant_liquids_production",
                "colorado_natural_gas_plant_liquids_production",
                "florida_natural_gas_plant_liquids_production",
                "gulf_of_america_natural_gas_plant_liquids_production",
                "idaho_natural_gas_plant_liquids_production",
                "illinois_natural_gas_plant_liquids_production",
                "kansas_natural_gas_plant_liquids_production",
                "kentucky_natural_gas_plant_liquids_production",
                "louisiana_natural_gas_plant_liquids_production",
                "michigan_natural_gas_plant_liquids_production",
                "mississippi_natural_gas_plant_liquids_production",
                "montana_natural_gas_plant_liquids_production",
                "new_mexico_natural_gas_plant_liquids_production",
                "north_dakota_natural_gas_plant_liquids_production",
                "ohio_natural_gas_plant_liquids_production",
                "oklahoma_natural_gas_plant_liquids_production",
                "pennsylvania_natural_gas_plant_liquids_production",
                "south_dakota_natural_gas_plant_liquids_production",
                "tennessee_natural_gas_plant_liquids_production",
                "texas_natural_gas_plant_liquids_production",
                "us_natural_gas_plant_liquids_production",
                "utah_natural_gas_plant_liquids_production",
                "west_virginia_natural_gas_plant_liquids_production",
                "wyoming_natural_gas_plant_liquids_production",
            ],
        },
    }

    frequency: Literal["annual", "monthly"] | None = Field(
        default=None,
        description="The data frequency. The default is 'monthly'.",
    )
    region: str | None = Field(
        default=None,
        description="DuoArea filter. Accepts a comma-separated list of values.",
    )
    series: str | None = Field(
        default=None,
        description="Series filter. Accepts a comma-separated list of values.",
    )


class EiaNaturalGasNaturalGasPlantProcessingData(EiaApiData):
    """Natural Gas Plant Processing. EIA natural gas survey data"""

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


class EiaNaturalGasNaturalGasPlantProcessingFetcher(
    Fetcher[
        EiaNaturalGasNaturalGasPlantProcessingQueryParams,
        list[EiaNaturalGasNaturalGasPlantProcessingData],
    ]
):
    """Natural Gas Plant Processing fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> EiaNaturalGasNaturalGasPlantProcessingQueryParams:
        """Transform the query parameters."""
        return transform_dataset_query(
            EiaNaturalGasNaturalGasPlantProcessingQueryParams, params
        )

    @staticmethod
    async def aextract_data(
        query: EiaNaturalGasNaturalGasPlantProcessingQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract the data from the EIA API."""
        return await extract_dataset_data(query, credentials)

    @staticmethod
    def transform_data(
        query: EiaNaturalGasNaturalGasPlantProcessingQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> list[EiaNaturalGasNaturalGasPlantProcessingData]:
        """Transform the data."""
        return transform_dataset_data(
            EiaNaturalGasNaturalGasPlantProcessingData, query, data
        )
