"""International model."""

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


class EiaInternationalQueryParams(EiaApiQueryParams):
    """International. Country level production, consumption, imports, exports by energy source (petroleum, natural gas, electricity, renewable, etc.) Interactive product: https://www.eia.gov/international/data/world

    Source: https://www.eia.gov/opendata/browser/international
    """

    __group__ = "international"
    __dataset__ = "international"
    __json_schema_extra__ = {
        "activity": {
            "multiple_items_allowed": True,
            "choices": ["consumption", "imports", "production", "stocks_oecd"],
        },
        "country": {"multiple_items_allowed": True},
        "country_type": {
            "multiple_items_allowed": True,
            "choices": ["country", "region"],
        },
        "product": {
            "multiple_items_allowed": True,
            "choices": [
                "canada_imports_by_source",
                "crude_oil_including_lease_condensate",
                "crude_oil_ngpl_and_other_liquids",
                "france_imports_by_source",
                "germany_imports_by_source",
                "italy_imports_by_source",
                "japan_imports_by_source",
                "ngpl",
                "oecd_europe_imports_by_source",
                "oecd_imports",
                "other_liquids",
                "petroleum_and_other_liquids",
                "refined_petroleum_products",
                "refinery_processing_gain",
                "south_korea_imports_by_source",
                "total_petroleum_and_other_liquids",
                "us_imports_by_source",
                "united_kingdom_imports_by_source",
            ],
        },
        "unit": {
            "multiple_items_allowed": True,
            "choices": [
                "1000_metric_tons",
                "millions_barrels",
                "thousand_barrels_per_day",
            ],
        },
    }

    frequency: Literal["annual", "monthly", "quarterly"] | None = Field(
        default=None,
        description="The data frequency. The default is 'monthly'.",
    )
    activity: Literal["consumption", "imports", "production", "stocks_oecd"] | None = (
        Field(
            default=None,
            description="Activity filter.",
        )
    )
    country: str | None = Field(
        default=None,
        description="Country/Region filter. Accepts a comma-separated list of values. There are 268 valid values - use the `facet_options` endpoint to list them.",
    )
    country_type: Literal["country", "region"] | None = Field(
        default=None,
        description="Country/Region Type filter.",
    )
    product: str | None = Field(
        default=None,
        description="Product filter. Accepts a comma-separated list of values.",
    )
    unit: (
        Literal["1000_metric_tons", "millions_barrels", "thousand_barrels_per_day"]
        | None
    ) = Field(
        default=None,
        description="Unit filter.",
    )


class EiaInternationalData(EiaApiData):
    """International. Country level production, consumption, imports, exports by energy source (petroleum, natural gas, electricity, renewable, etc.) Interactive product: https://www.eia.gov/international/data/world"""

    activity: str | None = Field(
        default=None,
        description="Activity code.",
    )
    activity_name: str | None = Field(
        default=None,
        description="Activity name.",
    )
    country: str | None = Field(
        default=None,
        description="Country/Region code.",
    )
    country_name: str | None = Field(
        default=None,
        description="Country/Region name.",
    )
    country_type: str | None = Field(
        default=None,
        description="Country/Region Type code.",
    )
    country_type_name: str | None = Field(
        default=None,
        description="Country/Region Type name.",
    )
    data_flag: str | None = Field(
        default=None,
        description="Data flag ID code.",
    )
    data_flag_name: str | None = Field(
        default=None,
        description="Data flag ID name.",
    )
    product: str | None = Field(
        default=None,
        description="Product code.",
    )
    product_name: str | None = Field(
        default=None,
        description="Product name.",
    )
    unit: str | None = Field(
        default=None,
        description="Unit code.",
    )
    unit_name: str | None = Field(
        default=None,
        description="Unit name.",
    )
    value: float | None = Field(
        default=None,
        description="Value. Withheld or unavailable values return as null.",
    )


class EiaInternationalFetcher(
    Fetcher[EiaInternationalQueryParams, list[EiaInternationalData]]
):
    """International fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> EiaInternationalQueryParams:
        """Transform the query parameters."""
        return transform_dataset_query(EiaInternationalQueryParams, params)

    @staticmethod
    async def aextract_data(
        query: EiaInternationalQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract the data from the EIA API."""
        return await extract_dataset_data(query, credentials)

    @staticmethod
    def transform_data(
        query: EiaInternationalQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> list[EiaInternationalData]:
        """Transform the data."""
        return transform_dataset_data(EiaInternationalData, query, data)
