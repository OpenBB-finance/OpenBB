"""Natural Gas Consumption by End Use model."""

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


class EiaNaturalGasNaturalGasConsumptionByEndUseQueryParams(EiaApiQueryParams):
    """Natural Gas Consumption by End Use. EIA natural gas survey data

    Source: https://www.eia.gov/opendata/browser/natural-gas/cons/sum
    """

    __group__ = "natural_gas"
    __dataset__ = "natural_gas_consumption_by_end_use"
    __json_schema_extra__ = {
        "process": {
            "multiple_items_allowed": True,
            "choices": [
                "commercial_consumption",
                "delivered_to_consumers",
                "electric_power_consumption",
                "industrial_consumption",
                "lease_and_plant_fuel_consumption",
                "pipeline_fuel_consumption",
                "residential_consumption",
                "total_consumption",
                "vehicle_fuel_consumption",
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
    process: str | None = Field(
        default=None,
        description="Process filter. Accepts a comma-separated list of values.",
    )
    region: str | None = Field(
        default=None,
        description="DuoArea filter. Accepts a comma-separated list of values.",
    )
    series: str | None = Field(
        default=None,
        description="Series filter. Accepts a comma-separated list of values. There are 315 valid values - use the `facet_options` endpoint to list them.",
    )


class EiaNaturalGasNaturalGasConsumptionByEndUseData(EiaApiData):
    """Natural Gas Consumption by End Use. EIA natural gas survey data"""

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


class EiaNaturalGasNaturalGasConsumptionByEndUseFetcher(
    Fetcher[
        EiaNaturalGasNaturalGasConsumptionByEndUseQueryParams,
        list[EiaNaturalGasNaturalGasConsumptionByEndUseData],
    ]
):
    """Natural Gas Consumption by End Use fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> EiaNaturalGasNaturalGasConsumptionByEndUseQueryParams:
        """Transform the query parameters."""
        return transform_dataset_query(
            EiaNaturalGasNaturalGasConsumptionByEndUseQueryParams, params
        )

    @staticmethod
    async def aextract_data(
        query: EiaNaturalGasNaturalGasConsumptionByEndUseQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract the data from the EIA API."""
        return await extract_dataset_data(query, credentials)

    @staticmethod
    def transform_data(
        query: EiaNaturalGasNaturalGasConsumptionByEndUseQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> list[EiaNaturalGasNaturalGasConsumptionByEndUseData]:
        """Transform the data."""
        return transform_dataset_data(
            EiaNaturalGasNaturalGasConsumptionByEndUseData, query, data
        )
