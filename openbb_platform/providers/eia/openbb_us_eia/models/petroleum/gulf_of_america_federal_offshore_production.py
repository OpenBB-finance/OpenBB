"""Gulf of America Federal Offshore Production model."""

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


class EiaPetroleumGulfOfAmericaFederalOffshoreProductionQueryParams(EiaApiQueryParams):
    """Gulf of America Federal Offshore Production. EIA petroleum gas survey data

    Source: https://www.eia.gov/opendata/browser/petroleum/crd/gom
    """

    __group__ = "petroleum"
    __dataset__ = "gulf_of_america_federal_offshore_production"
    __json_schema_extra__ = {
        "process": {
            "multiple_items_allowed": True,
            "choices": [
                "dry_production_from_reserves",
                "dry_reserves_based_production_deepwater_percentage",
                "dry_reserves_based_production_from_greater_than_200_meters",
                "dry_reserves_based_production_from_less_than_200_meters",
                "lease_condensate_reserves_based_production",
                "lease_condensate_reserves_based_production_deepwater",
                "lease_condensate_reserves_based_production_from_greater",
                "lease_condensate_reserves_based_production_from_less_than",
                "production_from_reserves",
                "reserves_based_production_deepwater_percentage",
                "reserves_based_production_from_greater_than_200_meters",
                "reserves_based_production_from_less_than_200_meters",
                "wet_after_lease_separation_reserves_based_production",
                "wet_after_lease_separation_reserves_based_production_from_greater_than_200_meters",
                "wet_after_lease_separation_reserves_based_production_from_less_than_200_meters",
                "wet_after_lease_separation_reserves_based_production_from_reserves",
            ],
        },
        "product": {
            "multiple_items_allowed": True,
            "choices": [
                "crude_oil",
                "natural_gas",
                "natural_gas_liquids_and_liquid_refinery_gases",
            ],
        },
        "series": {
            "multiple_items_allowed": True,
            "choices": [
                "gulf_of_america_federal_offshore_crude_oil_production",
                "gulf_of_america_federal_offshore_crude_oil_production_from_greater_than_200_meters_deep_million_barrels",
                "gulf_of_america_federal_offshore_crude_oil_production_from_less_than_200_meters_deep_million_barrels",
                "gulf_of_america_federal_offshore_dry_natural_gas_production_billion_cubic_feet",
                "gulf_of_america_federal_offshore_dry_natural_gas_production_from_greater_than_200_meters_deep_billion_cubic_feet",
                "gulf_of_america_federal_offshore_dry_natural_gas_production_from_less_than_200_meters_deep_billion_cubic_feet",
                "gulf_of_america_federal_offshore_natural_gas_liquids_lease_condensate_production_million_barrels",
                "gulf_of_america_federal_offshore_natural_gas_liquids_lease_condensate_production_from_greater_than_200_meters_deep_million_barrels",
                "gulf_of_america_federal_offshore_natural_gas_liquids_lease_condensate_production_from_less_than_200_meters_deep_million_barrels",
                "gulf_of_america_federal_offshore_natural_gas_liquids_production_million_barrels",
                "gulf_of_america_federal_offshore_natural_gas_liquids_production_from_greater_than_200_meters_deep_million_barrels",
                "gulf_of_america_federal_offshore_natural_gas_liquids_production_from_less_than_200_meters_deep_million_barrels",
                "gulf_of_america_federal_offshore_natural_gas_wet_after_lease_separation_production_billion_cubic_feet",
                "gulf_of_america_federal_offshore_natural_gas_wet_after_lease_separation_production_from_greater_than_200_meters_deep_billion_cubic_feet",
                "gulf_of_america_federal_offshore_natural_gas_wet_after_lease_separation_production_from_less_than_200_meters_deep_billion_cubic_feet",
                "gulf_of_america_federal_offshore_percentage_of_crude_oil",
                "gulf_of_america_federal_offshore_percentage_of_dry_natural",
                "gulf_of_america_federal_offshore_percentage_of_natural_gas_liquids_lease_condensate_production_from_greater_than_200_meters_deep",
                "gulf_of_america_federal_offshore_percentage_of_natural_gas_liquids_production_from_greater_than_200_meters_deep",
                "gulf_of_america_federal_offshore_percentage_of_natural_gas_wet_after_lease_separation_production_from_greater_than_200_meters_deep",
            ],
        },
    }

    process: str | None = Field(
        default=None,
        description="Process filter. Accepts a comma-separated list of values.",
    )
    product: str | None = Field(
        default=None,
        description="Product filter. Accepts a comma-separated list of values.",
    )
    series: str | None = Field(
        default=None,
        description="Series filter. Accepts a comma-separated list of values.",
    )


class EiaPetroleumGulfOfAmericaFederalOffshoreProductionData(EiaApiData):
    """Gulf of America Federal Offshore Production. EIA petroleum gas survey data"""

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


class EiaPetroleumGulfOfAmericaFederalOffshoreProductionFetcher(
    Fetcher[
        EiaPetroleumGulfOfAmericaFederalOffshoreProductionQueryParams,
        list[EiaPetroleumGulfOfAmericaFederalOffshoreProductionData],
    ]
):
    """Gulf of America Federal Offshore Production fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> EiaPetroleumGulfOfAmericaFederalOffshoreProductionQueryParams:
        """Transform the query parameters."""
        return transform_dataset_query(
            EiaPetroleumGulfOfAmericaFederalOffshoreProductionQueryParams, params
        )

    @staticmethod
    async def aextract_data(
        query: EiaPetroleumGulfOfAmericaFederalOffshoreProductionQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract the data from the EIA API."""
        return await extract_dataset_data(query, credentials)

    @staticmethod
    def transform_data(
        query: EiaPetroleumGulfOfAmericaFederalOffshoreProductionQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> list[EiaPetroleumGulfOfAmericaFederalOffshoreProductionData]:
        """Transform the data."""
        return transform_dataset_data(
            EiaPetroleumGulfOfAmericaFederalOffshoreProductionData, query, data
        )
