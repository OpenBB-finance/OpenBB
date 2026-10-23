"""Imports by Processing Area model."""

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


class EiaPetroleumImportsByProcessingAreaQueryParams(EiaApiQueryParams):
    """Imports by Processing Area. EIA petroleum gas survey data

    Source: https://www.eia.gov/opendata/browser/petroleum/move/imp2
    """

    __group__ = "petroleum"
    __dataset__ = "imports_by_processing_area"
    __json_schema_extra__ = {
        "product": {
            "multiple_items_allowed": True,
            "choices": [
                "aviation_gasoline_blending_components",
                "crude_oil",
                "heavy_gas_oils",
                "kerosene_and_light_oils",
                "naphthas_and_lighter",
                "residuum",
                "unfinished_oils",
            ],
        },
        "region": {
            "multiple_items_allowed": True,
            "choices": ["padd_1", "padd_2", "padd_3", "padd_4", "padd_5"],
        },
        "series": {
            "multiple_items_allowed": True,
            "choices": [
                "east_coast_padd_1_imports_by_padd_of_processing_of_crude_oil_thousand_barrels_per_day",
                "east_coast_padd_1_imports_by_padd_of_processing_of_crude_oil_thousand_barrels",
                "east_coast_padd_1_imports_by_padd_of_processing_of_heavy_gas_oils_thousand_barrels_per_day",
                "east_coast_padd_1_imports_by_padd_of_processing_of_heavy_gas_oils_thousand_barrels",
                "east_coast_padd_1_imports_by_padd_of_processing_of_kerosene_and_light_oils_thousand_barrels_per_day",
                "east_coast_padd_1_imports_by_padd_of_processing_of_kerosene_and_light_oils_thousand_barrels",
                "east_coast_padd_1_imports_by_padd_of_processing_of_naphthas_and_lighter_thousand_barrels_per_day",
                "east_coast_padd_1_imports_by_padd_of_processing_of_naphthas_and_lighter_thousand_barrels",
                "east_coast_padd_1_imports_by_padd_of_processing_of_residuum_thousand_barrels_per_day",
                "east_coast_padd_1_imports_by_padd_of_processing_of_residuum_thousand_barrels",
                "east_coast_padd_1_imports_by_padd_of_processing_of_unfinished_oils_thousand_barrels_per_day",
                "east_coast_padd_1_imports_by_padd_of_processing_of_unfinished_oils_thousand_barrels",
                "gulf_coast_padd_3_imports_by_padd_of_processing_of_crude_oil_thousand_barrels_per_day",
                "gulf_coast_padd_3_imports_by_padd_of_processing_of_crude_oil_thousand_barrels",
                "gulf_coast_padd_3_imports_by_padd_of_processing_of_heavy_gas_oils_thousand_barrels_per_day",
                "gulf_coast_padd_3_imports_by_padd_of_processing_of_heavy_gas_oils_thousand_barrels",
                "gulf_coast_padd_3_imports_by_padd_of_processing_of_kerosene_and_light_oils_thousand_barrels_per_day",
                "gulf_coast_padd_3_imports_by_padd_of_processing_of_kerosene_and_light_oils_thousand_barrels",
                "gulf_coast_padd_3_imports_by_padd_of_processing_of_naphthas_and_lighter_thousand_barrels_per_day",
                "gulf_coast_padd_3_imports_by_padd_of_processing_of_naphthas_and_lighter_thousand_barrels",
                "gulf_coast_padd_3_imports_by_padd_of_processing_of_residuum_thousand_barrels_per_day",
                "gulf_coast_padd_3_imports_by_padd_of_processing_of_residuum_thousand_barrels",
                "gulf_coast_padd_3_imports_by_padd_of_processing_of_unfinished_oils_thousand_barrels_per_day",
                "gulf_coast_padd_3_imports_by_padd_of_processing_of_unfinished_oils_thousand_barrels",
                "midwest_padd_2_imports_by_padd_of_processing_of_crude_oil_thousand_barrels_per_day",
                "midwest_padd_2_imports_by_padd_of_processing_of_crude_oil_thousand_barrels",
                "midwest_padd_2_imports_by_padd_of_processing_of_heavy_gas_oils_thousand_barrels_per_day",
                "midwest_padd_2_imports_by_padd_of_processing_of_heavy_gas_oils_thousand_barrels",
                "midwest_padd_2_imports_by_padd_of_processing_of_kerosene_and_light_oils_thousand_barrels_per_day",
                "midwest_padd_2_imports_by_padd_of_processing_of_kerosene_and_light_oils_thousand_barrels",
                "midwest_padd_2_imports_by_padd_of_processing_of_naphthas_and_lighter_thousand_barrels_per_day",
                "midwest_padd_2_imports_by_padd_of_processing_of_naphthas_and_lighter_thousand_barrels",
                "midwest_padd_2_imports_by_padd_of_processing_of_residuum_thousand_barrels_per_day",
                "midwest_padd_2_imports_by_padd_of_processing_of_residuum_thousand_barrels",
                "midwest_padd_2_imports_by_padd_of_processing_of_unfinished_oils_thousand_barrels_per_day",
                "midwest_padd_2_imports_by_padd_of_processing_of_unfinished_oils_thousand_barrels",
                "rocky_mountain_padd_4_imports_by_padd_of_processing_of_crude_oil_thousand_barrels_per_day",
                "rocky_mountain_padd_4_imports_by_padd_of_processing_of_crude_oil_thousand_barrels",
                "rocky_mountain_padd_4_imports_by_padd_of_processing_of_heavy_gas_oils_thousand_barrels_per_day",
                "rocky_mountain_padd_4_imports_by_padd_of_processing_of_heavy_gas_oils_thousand_barrels",
                "rocky_mountain_padd_4_imports_by_padd_of_processing_of_kerosene_and_light_oils_thousand_barrels_per_day",
                "rocky_mountain_padd_4_imports_by_padd_of_processing_of_kerosene_and_light_oils_thousand_barrels",
                "rocky_mountain_padd_4_imports_by_padd_of_processing_of_residuum_thousand_barrels_per_day",
                "rocky_mountain_padd_4_imports_by_padd_of_processing_of_residuum_thousand_barrels",
                "rocky_mountain_padd_4_imports_by_padd_of_processing_of_unfinished_oils_thousand_barrels_per_day",
                "rocky_mountain_padd_4_imports_by_padd_of_processing_of_unfinished_oils_thousand_barrels",
                "west_coast_padd_5_imports_by_padd_of_processing_of_crude_oil_thousand_barrels_per_day",
                "west_coast_padd_5_imports_by_padd_of_processing_of_crude_oil_thousand_barrels",
                "west_coast_padd_5_imports_by_padd_of_processing_of_heavy_gas_oils_thousand_barrels_per_day",
                "west_coast_padd_5_imports_by_padd_of_processing_of_heavy_gas_oils_thousand_barrels",
                "west_coast_padd_5_imports_by_padd_of_processing_of_kerosene_and_light_oils_thousand_barrels_per_day",
                "west_coast_padd_5_imports_by_padd_of_processing_of_kerosene_and_light_oils_thousand_barrels",
                "west_coast_padd_5_imports_by_padd_of_processing_of_naphthas_and_lighter_thousand_barrels_per_day",
                "west_coast_padd_5_imports_by_padd_of_processing_of_naphthas_and_lighter_thousand_barrels",
                "west_coast_padd_5_imports_by_padd_of_processing_of_residuum_thousand_barrels_per_day",
                "west_coast_padd_5_imports_by_padd_of_processing_of_residuum_thousand_barrels",
                "west_coast_padd_5_imports_by_padd_of_processing_of_unfinished_oils_thousand_barrels_per_day",
                "west_coast_padd_5_imports_by_padd_of_processing_of_unfinished_oils_thousand_barrels",
                "west_coast_padd_v_blending_components_av_gas_imports_for_processing_thousand_barrels_per_day",
                "west_coast_padd_v_blending_components_av_gas_imports_for_processing_thousand_barrels",
            ],
        },
    }

    frequency: Literal["annual", "monthly"] | None = Field(
        default=None,
        description="The data frequency. The default is 'monthly'.",
    )
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


class EiaPetroleumImportsByProcessingAreaData(EiaApiData):
    """Imports by Processing Area. EIA petroleum gas survey data"""

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


class EiaPetroleumImportsByProcessingAreaFetcher(
    Fetcher[
        EiaPetroleumImportsByProcessingAreaQueryParams,
        list[EiaPetroleumImportsByProcessingAreaData],
    ]
):
    """Imports by Processing Area fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> EiaPetroleumImportsByProcessingAreaQueryParams:
        """Transform the query parameters."""
        return transform_dataset_query(
            EiaPetroleumImportsByProcessingAreaQueryParams, params
        )

    @staticmethod
    async def aextract_data(
        query: EiaPetroleumImportsByProcessingAreaQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract the data from the EIA API."""
        return await extract_dataset_data(query, credentials)

    @staticmethod
    def transform_data(
        query: EiaPetroleumImportsByProcessingAreaQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> list[EiaPetroleumImportsByProcessingAreaData]:
        """Transform the data."""
        return transform_dataset_data(
            EiaPetroleumImportsByProcessingAreaData, query, data
        )
