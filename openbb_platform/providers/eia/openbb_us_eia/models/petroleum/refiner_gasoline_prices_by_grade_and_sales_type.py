"""Refiner Gasoline Prices by Grade and Sales Type model."""

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


class EiaPetroleumRefinerGasolinePricesByGradeAndSalesTypeQueryParams(
    EiaApiQueryParams
):
    """Refiner Gasoline Prices by Grade and Sales Type. EIA petroleum gas survey data

    Source: https://www.eia.gov/opendata/browser/petroleum/pri/refmg
    """

    __group__ = "petroleum"
    __dataset__ = "refiner_gasoline_prices_by_grade_and_sales_type"
    __json_schema_extra__ = {
        "process": {
            "multiple_items_allowed": True,
            "choices": [
                "bulk_sales_by_refiners_and_gas_plants",
                "dtw_sales_price_by_refiners_and_gas_plants",
                "other_end_users_by_refiners_and_gas_plants",
                "rack_sales_price_by_refiners_and_gas_plants",
                "retail_sales_by_refiners_and_gas_plants",
                "through_company_outlets_price_by_refiners_and_gas_plants",
                "wholesale_resale_price_by_refiners_and_gas_plants",
            ],
        },
        "product": {
            "multiple_items_allowed": True,
            "choices": [
                "midgrade_gasoline",
                "premium_gasoline",
                "regular_gasoline",
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
    process: str | None = Field(
        default=None,
        description="Process filter. Accepts a comma-separated list of values.",
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
        description="Series filter. Accepts a comma-separated list of values. There are 736 valid values - use the `facet_options` endpoint to list them.",
    )


class EiaPetroleumRefinerGasolinePricesByGradeAndSalesTypeData(EiaApiData):
    """Refiner Gasoline Prices by Grade and Sales Type. EIA petroleum gas survey data"""

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


class EiaPetroleumRefinerGasolinePricesByGradeAndSalesTypeFetcher(
    Fetcher[
        EiaPetroleumRefinerGasolinePricesByGradeAndSalesTypeQueryParams,
        list[EiaPetroleumRefinerGasolinePricesByGradeAndSalesTypeData],
    ]
):
    """Refiner Gasoline Prices by Grade and Sales Type fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> EiaPetroleumRefinerGasolinePricesByGradeAndSalesTypeQueryParams:
        """Transform the query parameters."""
        return transform_dataset_query(
            EiaPetroleumRefinerGasolinePricesByGradeAndSalesTypeQueryParams, params
        )

    @staticmethod
    async def aextract_data(
        query: EiaPetroleumRefinerGasolinePricesByGradeAndSalesTypeQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract the data from the EIA API."""
        return await extract_dataset_data(query, credentials)

    @staticmethod
    def transform_data(
        query: EiaPetroleumRefinerGasolinePricesByGradeAndSalesTypeQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> list[EiaPetroleumRefinerGasolinePricesByGradeAndSalesTypeData]:
        """Transform the data."""
        return transform_dataset_data(
            EiaPetroleumRefinerGasolinePricesByGradeAndSalesTypeData, query, data
        )
