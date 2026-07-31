"""Adjusted Sales of Residual Fuel Oil by End Use model."""

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


class EiaPetroleumAdjustedSalesOfResidualFuelOilByEndUseQueryParams(EiaApiQueryParams):
    """Adjusted Sales of Residual Fuel Oil by End Use. EIA petroleum gas survey data

    Source: https://www.eia.gov/opendata/browser/petroleum/cons/821rsda
    """

    __group__ = "petroleum"
    __dataset__ = "adjusted_sales_of_residual_fuel_oil_by_end_use"
    __json_schema_extra__ = {
        "process": {
            "multiple_items_allowed": True,
            "choices": [
                "adj_sales_deliveries_total_to_end_users",
                "adj_sales_deliveries_transportation_total",
                "adj_sales_deliveries_to_commercial_consumers",
                "adj_sales_deliveries_to_elect_utility_consumers",
                "adj_sales_deliveries_to_industrial_consumers",
                "adj_sales_deliveries_to_military_consumers",
                "adj_sales_deliveries_to_oil_company_consumers",
                "adj_sales_deliveries_to_other_end_users",
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
        description="Series filter. Accepts a comma-separated list of values. There are 480 valid values - use the `facet_options` endpoint to list them.",
    )


class EiaPetroleumAdjustedSalesOfResidualFuelOilByEndUseData(EiaApiData):
    """Adjusted Sales of Residual Fuel Oil by End Use. EIA petroleum gas survey data"""

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


class EiaPetroleumAdjustedSalesOfResidualFuelOilByEndUseFetcher(
    Fetcher[
        EiaPetroleumAdjustedSalesOfResidualFuelOilByEndUseQueryParams,
        list[EiaPetroleumAdjustedSalesOfResidualFuelOilByEndUseData],
    ]
):
    """Adjusted Sales of Residual Fuel Oil by End Use fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> EiaPetroleumAdjustedSalesOfResidualFuelOilByEndUseQueryParams:
        """Transform the query parameters."""
        return transform_dataset_query(
            EiaPetroleumAdjustedSalesOfResidualFuelOilByEndUseQueryParams, params
        )

    @staticmethod
    async def aextract_data(
        query: EiaPetroleumAdjustedSalesOfResidualFuelOilByEndUseQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract the data from the EIA API."""
        return await extract_dataset_data(query, credentials)

    @staticmethod
    def transform_data(
        query: EiaPetroleumAdjustedSalesOfResidualFuelOilByEndUseQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> list[EiaPetroleumAdjustedSalesOfResidualFuelOilByEndUseData]:
        """Transform the data."""
        return transform_dataset_data(
            EiaPetroleumAdjustedSalesOfResidualFuelOilByEndUseData, query, data
        )
