"""Number and Capacity of Petroleum Refineries model."""

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


class EiaPetroleumNumberAndCapacityOfPetroleumRefineriesQueryParams(EiaApiQueryParams):
    """Number and Capacity of Petroleum Refineries. EIA petroleum gas survey data

    Source: https://www.eia.gov/opendata/browser/petroleum/pnp/cap1
    """

    __group__ = "petroleum"
    __dataset__ = "number_and_capacity_of_petroleum_refineries"
    __json_schema_extra__ = {
        "process": {
            "multiple_items_allowed": True,
            "choices": [
                "atmospheric_crude_distillation_capacity",
                "atmospheric_crude_distillation_capacity_idle",
                "atmospheric_crude_distillation_capacity_operating",
                "catalytic_cracking_recycle",
                "catalytic_hydrocracking",
                "catalytic_hydrocracking_distillate",
                "catalytic_hydrocracking_gas_oil",
                "catalytic_hydrocracking_residual_fuel_oil",
                "catalytic_reforming",
                "catalytic_reforming_high_pressure",
                "catalytic_reforming_low_pressure",
                "downstream_charge_capacity_thermal_cracking_other_gas_oil",
                "downstream_charge_capacity_thermal_cracking_visbreaking",
                "downstream_charge_capacity_vacuum_distillation",
                "fuels_solvent_deaspalting",
                "idle_refineries",
                "operable_refineries",
                "operating_refineries",
                "refinery_catalytic_cracking_fresh_feed_downstream_charge",
                "refinery_catalytic_hydrotreating_diesel_downstream_charge",
                "refinery_catalytic_hydrotreating_distillate_downstream",
                "refinery_catalytic_hydrotreating_heavy_gas_oil_downstream",
                "refinery_catalytic_hydrotreating_kerosene_jet_fuel",
                "refinery_catalytic_hydrotreating_naphtha_reformer_feed",
                "refinery_catalytic_hydrotreating_other_distillate",
                "refinery_catalytic_hydrotreating_other_oils_downstream",
                "refinery_catalytic_hydrotreating_other_residual_fuel_oil",
                "refinery_catalytic_hydrotreating_residual_fuel_oil",
                "refinery_desulfurization_downstream_charge_capacity",
                "refinery_desulfurization_gasoline_downstream_charge_capacity",
                "refinery_thermal_cracking_downstream_charge_capacity",
                "refinery_thermal_cracking_coking_downstream_charge_capacity",
                "refinery_thermal_cracking_delayed_coking_downstream_charge",
                "refinery_thermal_cracking_fluid_coking_downstream_charge",
            ],
        },
        "product": {"multiple_items_allowed": True},
        "region": {
            "multiple_items_allowed": True,
            "choices": [
                "california",
                "colorado",
                "florida",
                "gum",
                "minnesota",
                "new_york",
                "ohio",
                "padd_1",
                "padd_2",
                "padd_3",
                "padd_4",
                "padd_5",
                "pri",
                "texas",
                "us",
                "usa_ak",
                "usa_al",
                "usa_ar",
                "usa_az",
                "usa_de",
                "usa_ga",
                "usa_hi",
                "usa_il",
                "usa_in",
                "usa_ks",
                "usa_ky",
                "usa_la",
                "usa_md",
                "usa_mi",
                "usa_mo",
                "usa_ms",
                "usa_mt",
                "usa_nc",
                "usa_nd",
                "usa_ne",
                "usa_nj",
                "usa_nm",
                "usa_nv",
                "usa_ok",
                "usa_or",
                "usa_pa",
                "usa_tn",
                "usa_ut",
                "usa_va",
                "usa_wi",
                "usa_wv",
                "usa_wy",
                "vir",
                "washington",
            ],
        },
        "series": {"multiple_items_allowed": True},
    }

    process: str | None = Field(
        default=None,
        description="Process filter. Accepts a comma-separated list of values.",
    )
    product: str | None = Field(
        default=None,
        description="Product filter. Accepts a comma-separated list of values. Use the `facet_options` endpoint for the valid values.",
    )
    region: str | None = Field(
        default=None,
        description="DuoArea filter. Accepts a comma-separated list of values.",
    )
    series: str | None = Field(
        default=None,
        description="Series filter. Accepts a comma-separated list of values. Use the `facet_options` endpoint for the valid values.",
    )


class EiaPetroleumNumberAndCapacityOfPetroleumRefineriesData(EiaApiData):
    """Number and Capacity of Petroleum Refineries. EIA petroleum gas survey data"""

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


class EiaPetroleumNumberAndCapacityOfPetroleumRefineriesFetcher(
    Fetcher[
        EiaPetroleumNumberAndCapacityOfPetroleumRefineriesQueryParams,
        list[EiaPetroleumNumberAndCapacityOfPetroleumRefineriesData],
    ]
):
    """Number and Capacity of Petroleum Refineries fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> EiaPetroleumNumberAndCapacityOfPetroleumRefineriesQueryParams:
        """Transform the query parameters."""
        return transform_dataset_query(
            EiaPetroleumNumberAndCapacityOfPetroleumRefineriesQueryParams, params
        )

    @staticmethod
    async def aextract_data(
        query: EiaPetroleumNumberAndCapacityOfPetroleumRefineriesQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract the data from the EIA API."""
        return await extract_dataset_data(query, credentials)

    @staticmethod
    def transform_data(
        query: EiaPetroleumNumberAndCapacityOfPetroleumRefineriesQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> list[EiaPetroleumNumberAndCapacityOfPetroleumRefineriesData]:
        """Transform the data."""
        return transform_dataset_data(
            EiaPetroleumNumberAndCapacityOfPetroleumRefineriesData, query, data
        )
