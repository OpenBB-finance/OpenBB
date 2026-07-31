"""Prime Supplier Sales Volumes model."""

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


class EiaPetroleumPrimeSupplierSalesVolumesQueryParams(EiaApiQueryParams):
    """Prime Supplier Sales Volumes. EIA petroleum gas survey data

    Source: https://www.eia.gov/opendata/browser/petroleum/cons/prim
    """

    __group__ = "petroleum"
    __dataset__ = "prime_supplier_sales_volumes"
    __json_schema_extra__ = {
        "product": {
            "multiple_items_allowed": True,
            "choices": [
                "aviation_gasoline",
                "conventional_gasoline",
                "conventional_premium_gasoline",
                "conventional_regular_gasoline",
                "gasoline_conventional_midgrade",
                "gasoline_oxygenated_midgrade",
                "gasoline_reformulated_midgrade",
                "kerosene",
                "kerosene_type_jet_fuel",
                "midgrade_gasoline",
                "naphtha_type_jet_fuel",
                "no_1_distillate",
                "no_2_diesel",
                "no_2_diesel_high_sulfur",
                "no_2_diesel_low_sulfur_0_15_ppm",
                "no_2_diesel_low_sulfur_15_500_ppm",
                "no_2_distillate",
                "no_2_fuel_oil_heating_oil",
                "no_4_distillate",
                "oxygenated_gasoline",
                "oxygenated_premium_gasoline",
                "oxygenated_regular_gasoline",
                "premium_gasoline",
                "propane",
                "reformulated_motor_gasoline",
                "reformulated_premium_gasoline",
                "reformulated_regular_gasoline",
                "regular_gasoline",
                "residual_fuel_oil",
                "residual_fuel_oil_0_to_1_0_sulfur",
                "residual_fuel_oil_greater_than_1_sulfur",
                "special_distillate_plus_kerosene",
                "total_gasoline",
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
                "padd_1a",
                "padd_1b",
                "padd_1c",
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
        description="Series filter. Accepts a comma-separated list of values. Use the `facet_options` endpoint for the valid values.",
    )


class EiaPetroleumPrimeSupplierSalesVolumesData(EiaApiData):
    """Prime Supplier Sales Volumes. EIA petroleum gas survey data"""

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


class EiaPetroleumPrimeSupplierSalesVolumesFetcher(
    Fetcher[
        EiaPetroleumPrimeSupplierSalesVolumesQueryParams,
        list[EiaPetroleumPrimeSupplierSalesVolumesData],
    ]
):
    """Prime Supplier Sales Volumes fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> EiaPetroleumPrimeSupplierSalesVolumesQueryParams:
        """Transform the query parameters."""
        return transform_dataset_query(
            EiaPetroleumPrimeSupplierSalesVolumesQueryParams, params
        )

    @staticmethod
    async def aextract_data(
        query: EiaPetroleumPrimeSupplierSalesVolumesQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract the data from the EIA API."""
        return await extract_dataset_data(query, credentials)

    @staticmethod
    def transform_data(
        query: EiaPetroleumPrimeSupplierSalesVolumesQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> list[EiaPetroleumPrimeSupplierSalesVolumesData]:
        """Transform the data."""
        return transform_dataset_data(
            EiaPetroleumPrimeSupplierSalesVolumesData, query, data
        )
