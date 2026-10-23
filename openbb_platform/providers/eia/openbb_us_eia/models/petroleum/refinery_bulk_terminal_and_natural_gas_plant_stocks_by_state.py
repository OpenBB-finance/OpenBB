"""Refinery, Bulk Terminal, and Natural Gas Plant Stocks by State model."""

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


class EiaPetroleumRefineryBulkTerminalAndNaturalGasPlantStocksByStateQueryParams(
    EiaApiQueryParams
):
    """Refinery, Bulk Terminal, and Natural Gas Plant Stocks by State. EIA petroleum gas survey data

    Source: https://www.eia.gov/opendata/browser/petroleum/stoc/st
    """

    __group__ = "petroleum"
    __dataset__ = "refinery_bulk_terminal_and_natural_gas_plant_stocks_by_state"
    __json_schema_extra__ = {
        "product": {
            "multiple_items_allowed": True,
            "choices": [
                "conventional_gasoline_blending_components",
                "conventional_motor_gasoline",
                "distillate_fuel_oil",
                "distillate_fuel_oil_0_to_15_ppm_sulfur",
                "distillate_fuel_oil_greater_than_500_ppm_sulfur",
                "distillate_fuel_oil_greater_than_15_to_500_ppm_sulfur",
                "finished_motor_gasoline",
                "gasoline_blending_components",
                "kerosene",
                "propane",
                "reformulated_gasoline_blending_components",
                "reformulated_motor_gasoline",
                "residual_fuel_oil",
            ],
        },
        "region": {
            "multiple_items_allowed": True,
            "choices": [
                "california",
                "colorado",
                "florida",
                "massachusetts",
                "minnesota",
                "new_york",
                "ohio",
                "padd_1",
                "padd_2",
                "padd_3",
                "padd_4",
                "padd_5",
                "texas",
                "us",
                "usa_ak",
                "usa_al",
                "usa_ar",
                "usa_az",
                "usa_ct",
                "usa_dc",
                "usa_de",
                "usa_ga",
                "usa_hi",
                "usa_ia",
                "usa_id",
                "usa_il",
                "usa_in",
                "usa_ks",
                "usa_ky",
                "usa_la",
                "usa_md",
                "usa_me",
                "usa_mi",
                "usa_mo",
                "usa_ms",
                "usa_mt",
                "usa_nc",
                "usa_nd",
                "usa_ne",
                "usa_nh",
                "usa_nj",
                "usa_nm",
                "usa_nv",
                "usa_ok",
                "usa_or",
                "usa_pa",
                "usa_ri",
                "usa_sc",
                "usa_sd",
                "usa_tn",
                "usa_ut",
                "usa_va",
                "usa_vt",
                "usa_wi",
                "usa_wv",
                "usa_wy",
                "washington",
            ],
        },
        "series": {"multiple_items_allowed": True},
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
        description="Series filter. Accepts a comma-separated list of values. There are 691 valid values - use the `facet_options` endpoint to list them.",
    )


class EiaPetroleumRefineryBulkTerminalAndNaturalGasPlantStocksByStateData(EiaApiData):
    """Refinery, Bulk Terminal, and Natural Gas Plant Stocks by State. EIA petroleum gas survey data"""

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


class EiaPetroleumRefineryBulkTerminalAndNaturalGasPlantStocksByStateFetcher(
    Fetcher[
        EiaPetroleumRefineryBulkTerminalAndNaturalGasPlantStocksByStateQueryParams,
        list[EiaPetroleumRefineryBulkTerminalAndNaturalGasPlantStocksByStateData],
    ]
):
    """Refinery, Bulk Terminal, and Natural Gas Plant Stocks by State fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> EiaPetroleumRefineryBulkTerminalAndNaturalGasPlantStocksByStateQueryParams:
        """Transform the query parameters."""
        return transform_dataset_query(
            EiaPetroleumRefineryBulkTerminalAndNaturalGasPlantStocksByStateQueryParams,
            params,
        )

    @staticmethod
    async def aextract_data(
        query: EiaPetroleumRefineryBulkTerminalAndNaturalGasPlantStocksByStateQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract the data from the EIA API."""
        return await extract_dataset_data(query, credentials)

    @staticmethod
    def transform_data(
        query: EiaPetroleumRefineryBulkTerminalAndNaturalGasPlantStocksByStateQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> list[EiaPetroleumRefineryBulkTerminalAndNaturalGasPlantStocksByStateData]:
        """Transform the data."""
        return transform_dataset_data(
            EiaPetroleumRefineryBulkTerminalAndNaturalGasPlantStocksByStateData,
            query,
            data,
        )
