"""US Weekly Product Supplied model."""

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


class EiaPetroleumUsWeeklyProductSuppliedQueryParams(EiaApiQueryParams):
    """US Weekly Product Supplied. EIA petroleum gas survey data

    Source: https://www.eia.gov/opendata/browser/petroleum/cons/wpsup
    """

    __group__ = "petroleum"
    __dataset__ = "us_weekly_product_supplied"
    __json_schema_extra__ = {
        "product": {
            "multiple_items_allowed": True,
            "choices": [
                "distillate_fuel_oil",
                "finished_motor_gasoline",
                "kerosene_type_jet_fuel",
                "other_oils",
                "propane_and_propylene",
                "residual_fuel_oil",
                "total_petroleum_products",
            ],
        },
        "series": {
            "multiple_items_allowed": True,
            "choices": [
                "us_product_supplied_of_distillate_fuel_oil",
                "us_product_supplied_of_finished_motor_gasoline",
                "us_product_supplied_of_kerosene_type_jet_fuel",
                "us_product_supplied_of_other_oils",
                "us_product_supplied_of_petroleum_products",
                "us_product_supplied_of_propane_and_propylene",
                "us_product_supplied_of_residual_fuel_oil",
            ],
        },
    }

    frequency: Literal["four-week-average", "weekly"] | None = Field(
        default=None,
        description="The data frequency. The default is 'weekly'.",
    )
    product: str | None = Field(
        default=None,
        description="Product filter. Accepts a comma-separated list of values.",
    )
    series: str | None = Field(
        default=None,
        description="Series filter. Accepts a comma-separated list of values.",
    )


class EiaPetroleumUsWeeklyProductSuppliedData(EiaApiData):
    """US Weekly Product Supplied. EIA petroleum gas survey data"""

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


class EiaPetroleumUsWeeklyProductSuppliedFetcher(
    Fetcher[
        EiaPetroleumUsWeeklyProductSuppliedQueryParams,
        list[EiaPetroleumUsWeeklyProductSuppliedData],
    ]
):
    """US Weekly Product Supplied fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> EiaPetroleumUsWeeklyProductSuppliedQueryParams:
        """Transform the query parameters."""
        return transform_dataset_query(
            EiaPetroleumUsWeeklyProductSuppliedQueryParams, params
        )

    @staticmethod
    async def aextract_data(
        query: EiaPetroleumUsWeeklyProductSuppliedQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract the data from the EIA API."""
        return await extract_dataset_data(query, credentials)

    @staticmethod
    def transform_data(
        query: EiaPetroleumUsWeeklyProductSuppliedQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> list[EiaPetroleumUsWeeklyProductSuppliedData]:
        """Transform the data."""
        return transform_dataset_data(
            EiaPetroleumUsWeeklyProductSuppliedData, query, data
        )
