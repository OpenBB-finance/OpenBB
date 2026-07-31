"""Imports of Residual Fuel model."""

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


class EiaPetroleumImportsOfResidualFuelQueryParams(EiaApiQueryParams):
    """Imports of Residual Fuel. EIA petroleum gas survey data

    Source: https://www.eia.gov/opendata/browser/petroleum/move/res
    """

    __group__ = "petroleum"
    __dataset__ = "imports_of_residual_fuel"
    __json_schema_extra__ = {
        "product": {
            "multiple_items_allowed": True,
            "choices": [
                "residual_fuel_oil",
                "residual_fuel_oil_0_31_to_1_00_sulfur",
                "residual_fuel_oil_greater_than_1_sulfur",
                "residual_fuel_oil_less_than_0_31_sulfur",
            ],
        },
        "region": {
            "multiple_items_allowed": True,
            "choices": [
                "california",
                "florida",
                "massachusetts",
                "minnesota",
                "na",
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
                "usa_ct",
                "usa_de",
                "usa_ga",
                "usa_hi",
                "usa_id",
                "usa_il",
                "usa_in",
                "usa_la",
                "usa_md",
                "usa_me",
                "usa_mi",
                "usa_ms",
                "usa_mt",
                "usa_nc",
                "usa_nd",
                "usa_nh",
                "usa_nj",
                "usa_or",
                "usa_pa",
                "usa_ri",
                "usa_sc",
                "usa_va",
                "usa_vt",
                "usa_wi",
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
        description="Series filter. Accepts a comma-separated list of values. There are 313 valid values - use the `facet_options` endpoint to list them.",
    )


class EiaPetroleumImportsOfResidualFuelData(EiaApiData):
    """Imports of Residual Fuel. EIA petroleum gas survey data"""

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


class EiaPetroleumImportsOfResidualFuelFetcher(
    Fetcher[
        EiaPetroleumImportsOfResidualFuelQueryParams,
        list[EiaPetroleumImportsOfResidualFuelData],
    ]
):
    """Imports of Residual Fuel fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> EiaPetroleumImportsOfResidualFuelQueryParams:
        """Transform the query parameters."""
        return transform_dataset_query(
            EiaPetroleumImportsOfResidualFuelQueryParams, params
        )

    @staticmethod
    async def aextract_data(
        query: EiaPetroleumImportsOfResidualFuelQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract the data from the EIA API."""
        return await extract_dataset_data(query, credentials)

    @staticmethod
    def transform_data(
        query: EiaPetroleumImportsOfResidualFuelQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> list[EiaPetroleumImportsOfResidualFuelData]:
        """Transform the data."""
        return transform_dataset_data(
            EiaPetroleumImportsOfResidualFuelData, query, data
        )
