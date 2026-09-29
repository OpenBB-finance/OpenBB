"""Production Capacity of Operable Petroleum Refineries model."""

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


class EiaPetroleumProductionCapacityOfOperablePetroleumRefineriesQueryParams(
    EiaApiQueryParams
):
    """Production Capacity of Operable Petroleum Refineries. EIA petroleum gas survey data

    Source: https://www.eia.gov/opendata/browser/petroleum/pnp/capprod
    """

    __group__ = "petroleum"
    __dataset__ = "production_capacity_of_operable_petroleum_refineries"
    __json_schema_extra__ = {
        "process": {
            "multiple_items_allowed": True,
            "choices": [
                "production_capacity_of_alkylates",
                "production_capacity_of_aromatics",
                "production_capacity_of_asphalt_and_road_oil",
                "production_capacity_of_hydrogen",
                "production_capacity_of_isobutane",
                "production_capacity_of_isomers",
                "production_capacity_of_isooctane",
                "production_capacity_of_isopentane_isohexane",
                "production_capacity_of_lubricants",
                "production_capacity_of_marketable_coke",
                "production_capacity_of_sulfur",
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
        description="Series filter. Accepts a comma-separated list of values. There are 539 valid values - use the `facet_options` endpoint to list them.",
    )


class EiaPetroleumProductionCapacityOfOperablePetroleumRefineriesData(EiaApiData):
    """Production Capacity of Operable Petroleum Refineries. EIA petroleum gas survey data"""

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


class EiaPetroleumProductionCapacityOfOperablePetroleumRefineriesFetcher(
    Fetcher[
        EiaPetroleumProductionCapacityOfOperablePetroleumRefineriesQueryParams,
        list[EiaPetroleumProductionCapacityOfOperablePetroleumRefineriesData],
    ]
):
    """Production Capacity of Operable Petroleum Refineries fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> EiaPetroleumProductionCapacityOfOperablePetroleumRefineriesQueryParams:
        """Transform the query parameters."""
        return transform_dataset_query(
            EiaPetroleumProductionCapacityOfOperablePetroleumRefineriesQueryParams,
            params,
        )

    @staticmethod
    async def aextract_data(
        query: EiaPetroleumProductionCapacityOfOperablePetroleumRefineriesQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract the data from the EIA API."""
        return await extract_dataset_data(query, credentials)

    @staticmethod
    def transform_data(
        query: EiaPetroleumProductionCapacityOfOperablePetroleumRefineriesQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> list[EiaPetroleumProductionCapacityOfOperablePetroleumRefineriesData]:
        """Transform the data."""
        return transform_dataset_data(
            EiaPetroleumProductionCapacityOfOperablePetroleumRefineriesData, query, data
        )
