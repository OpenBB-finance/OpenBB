"""Natural Gas Summary model."""

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


class EiaNaturalGasNaturalGasSummaryQueryParams(EiaApiQueryParams):
    """Natural Gas Summary. EIA natural gas survey data

    Source: https://www.eia.gov/opendata/browser/natural-gas/sum/lsum
    """

    __group__ = "natural_gas"
    __dataset__ = "natural_gas_summary"
    __json_schema_extra__ = {
        "process": {
            "multiple_items_allowed": True,
            "choices": [
                "city_gate_price",
                "commercial_consumption",
                "delivered_to_consumers",
                "dry_production",
                "electric_power_consumption",
                "electric_power_price",
                "exports",
                "exports_price",
                "extraction_loss",
                "gross_withdrawals",
                "imports",
                "imports_price",
                "industrial_consumption",
                "industrial_price",
                "lng_imports",
                "lease_and_plant_fuel_consumption",
                "liquefied_natural_gas_exports",
                "liquefied_natural_gas_exports_price",
                "liquefied_natural_gas_imports",
                "marketed_production",
                "pipeline_exports",
                "pipeline_exports_price",
                "pipeline_fuel_consumption",
                "pipeline_imports",
                "pipeline_imports_price",
                "price_delivered_to_commercial_sectors",
                "price_delivered_to_residential_consumers",
                "removed_from_natural_gas",
                "repressuring",
                "residential_consumption",
                "total_consumption",
                "total_underground_storage",
                "total_underground_storage_capacity",
                "underground_storage_base_gas",
                "underground_storage_injections",
                "underground_storage_net_withdrawals",
                "underground_storage_withdrawals",
                "underground_storage_working_gas",
                "vehicle_fuel_consumption",
                "vented_and_flared",
                "wellhead_acquisition_price",
                "withdrawals_from_coalbed_wells",
                "withdrawals_from_gas_wells",
                "withdrawals_from_oil_wells",
                "withdrawals_from_shale_gas",
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
                "na",
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
        description="Series filter. Accepts a comma-separated list of values. Use the `facet_options` endpoint for the valid values.",
    )


class EiaNaturalGasNaturalGasSummaryData(EiaApiData):
    """Natural Gas Summary. EIA natural gas survey data"""

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


class EiaNaturalGasNaturalGasSummaryFetcher(
    Fetcher[
        EiaNaturalGasNaturalGasSummaryQueryParams,
        list[EiaNaturalGasNaturalGasSummaryData],
    ]
):
    """Natural Gas Summary fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> EiaNaturalGasNaturalGasSummaryQueryParams:
        """Transform the query parameters."""
        return transform_dataset_query(
            EiaNaturalGasNaturalGasSummaryQueryParams, params
        )

    @staticmethod
    async def aextract_data(
        query: EiaNaturalGasNaturalGasSummaryQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract the data from the EIA API."""
        return await extract_dataset_data(query, credentials)

    @staticmethod
    def transform_data(
        query: EiaNaturalGasNaturalGasSummaryQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> list[EiaNaturalGasNaturalGasSummaryData]:
        """Transform the data."""
        return transform_dataset_data(EiaNaturalGasNaturalGasSummaryData, query, data)
