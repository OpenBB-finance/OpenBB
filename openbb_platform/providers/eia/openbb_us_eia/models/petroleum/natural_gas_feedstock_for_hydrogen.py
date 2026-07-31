"""Natural Gas Used as Feedstock for Hydrogen Production at Refineries model."""

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


class EiaPetroleumNaturalGasFeedstockForHydrogenQueryParams(EiaApiQueryParams):
    """Natural Gas Used as Feedstock for Hydrogen Production at Refineries. EIA petroleum gas survey data

    Source: https://www.eia.gov/opendata/browser/petroleum/pnp/feedng
    """

    __group__ = "petroleum"
    __dataset__ = "natural_gas_feedstock_for_hydrogen"
    __json_schema_extra__ = {
        "product": {"multiple_items_allowed": True},
        "region": {
            "multiple_items_allowed": True,
            "choices": ["padd_1", "padd_2", "padd_3", "padd_4", "padd_5", "us"],
        },
        "series": {
            "multiple_items_allowed": True,
            "choices": [
                "east_coast_natural_gas_used_as_feedstock_for_hydrogen",
                "gulf_coast_natural_gas_used_as_feedstock_for_hydrogen",
                "midwest_natural_gas_used_as_feedstock_for_hydrogen",
                "rocky_mountain_natural_gas_used_as_feedstock_for_hydrogen",
                "us_natural_gas_used_as_feedstock_for_hydrogen_production",
                "west_coast_natural_gas_used_as_feedstock_for_hydrogen",
            ],
        },
    }

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
        description="Series filter. Accepts a comma-separated list of values.",
    )


class EiaPetroleumNaturalGasFeedstockForHydrogenData(EiaApiData):
    """Natural Gas Used as Feedstock for Hydrogen Production at Refineries. EIA petroleum gas survey data"""

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


class EiaPetroleumNaturalGasFeedstockForHydrogenFetcher(
    Fetcher[
        EiaPetroleumNaturalGasFeedstockForHydrogenQueryParams,
        list[EiaPetroleumNaturalGasFeedstockForHydrogenData],
    ]
):
    """Natural Gas Used as Feedstock for Hydrogen Production at Refineries fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> EiaPetroleumNaturalGasFeedstockForHydrogenQueryParams:
        """Transform the query parameters."""
        return transform_dataset_query(
            EiaPetroleumNaturalGasFeedstockForHydrogenQueryParams, params
        )

    @staticmethod
    async def aextract_data(
        query: EiaPetroleumNaturalGasFeedstockForHydrogenQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract the data from the EIA API."""
        return await extract_dataset_data(query, credentials)

    @staticmethod
    def transform_data(
        query: EiaPetroleumNaturalGasFeedstockForHydrogenQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> list[EiaPetroleumNaturalGasFeedstockForHydrogenData]:
        """Transform the data."""
        return transform_dataset_data(
            EiaPetroleumNaturalGasFeedstockForHydrogenData, query, data
        )
