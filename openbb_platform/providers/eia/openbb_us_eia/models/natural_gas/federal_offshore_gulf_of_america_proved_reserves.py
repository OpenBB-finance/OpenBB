"""Federal Offshore Gulf of America Proved Reserves model."""

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


class EiaNaturalGasFederalOffshoreGulfOfAmericaProvedReservesQueryParams(
    EiaApiQueryParams
):
    """Federal Offshore Gulf of America Proved Reserves. EIA natural gas survey data

    Source: https://www.eia.gov/opendata/browser/natural-gas/enr/deep
    """

    __group__ = "natural_gas"
    __dataset__ = "federal_offshore_gulf_of_america_proved_reserves"
    __json_schema_extra__ = {
        "process": {
            "multiple_items_allowed": True,
            "choices": [
                "dry_expected_future_production",
                "dry_reserves_deepwater_percentage",
                "dry_reserves_from_greater_than_200_meters",
                "dry_reserves_from_less_than_200_meters",
                "lease_condensate_proved_reserves",
                "lease_condensate_reserves_deepwater_percentage",
                "lease_condensate_reserves_from_greater_than_200_meters",
                "lease_condensate_reserves_from_less_than_200_meters",
                "proved_reserves",
                "reserves_deepwater_percentage",
                "reserves_greater_than_200_meters",
                "reserves_less_than_200_meters",
                "wet_after_lease_separation_proved_reserves",
                "wet_after_lease_separation_reserves_deepwater_percentage",
                "wet_after_lease_separation_reserves_from_greater_than_200",
                "wet_after_lease_separation_reserves_from_less_than_200",
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
                "gulf_of_america_federal_offshore_crude_oil_proved_reserves_million_barrels",
                "gulf_of_america_federal_offshore_crude_oil_proved_reserves_from_greater_than_200_meters_deep_million_barrels",
                "gulf_of_america_federal_offshore_crude_oil_proved_reserves_from_less_than_200_meters_deep_million_barrels",
                "gulf_of_america_federal_offshore_dry_natural_gas_expected",
                "gulf_of_america_federal_offshore_dry_natural_gas_proved_reserves_from_greater_than_200_meters_deep_billion_cubic_feet",
                "gulf_of_america_federal_offshore_dry_natural_gas_proved_reserves_from_less_than_200_meters_deep_billion_cubic_feet",
                "gulf_of_america_federal_offshore_natural_gas_liquids_lease_condensate_proved_reserves_million_barrels",
                "gulf_of_america_federal_offshore_natural_gas_liquids_lease_condensate_proved_reserves_from_greater_than_200_meters_deep_million_barrels",
                "gulf_of_america_federal_offshore_natural_gas_liquids_lease_condensate_proved_reserves_from_less_than_200_meters_deep_million_barrels",
                "gulf_of_america_federal_offshore_natural_gas_liquids_proved_reserves_million_barrels",
                "gulf_of_america_federal_offshore_natural_gas_liquids_proved_reserves_from_greater_than_200_meters_deep_million_barrels",
                "gulf_of_america_federal_offshore_natural_gas_liquids_proved_reserves_from_less_than_200_meters_deep_million_barrels",
                "gulf_of_america_federal_offshore_natural_gas_wet_after_lease_separation_proved_reserves_billion_cubic_feet",
                "gulf_of_america_federal_offshore_natural_gas_wet_after_lease_separation_proved_reserves_from_greater_than_200_meters_deep_billion_cubic_feet",
                "gulf_of_america_federal_offshore_natural_gas_wet_after_lease_separation_proved_reserves_from_less_than_200_meters_deep_billion_cubic_feet",
                "gulf_of_america_federal_offshore_percentage_of_crude_oil",
                "gulf_of_america_federal_offshore_percentage_of_dry_natural",
                "gulf_of_america_federal_offshore_percentage_of_natural_gas_liquids_lease_condensate_proved_reserves_from_greater_than_200_meters_deep",
                "gulf_of_america_federal_offshore_percentage_of_natural_gas_liquids_proved_reserves_from_greater_than_200_meters_deep",
                "gulf_of_america_federal_offshore_percentage_of_natural_gas_wet_after_lease_separation_proved_reserves_from_greater_than_200_meters_deep",
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


class EiaNaturalGasFederalOffshoreGulfOfAmericaProvedReservesData(EiaApiData):
    """Federal Offshore Gulf of America Proved Reserves. EIA natural gas survey data"""

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


class EiaNaturalGasFederalOffshoreGulfOfAmericaProvedReservesFetcher(
    Fetcher[
        EiaNaturalGasFederalOffshoreGulfOfAmericaProvedReservesQueryParams,
        list[EiaNaturalGasFederalOffshoreGulfOfAmericaProvedReservesData],
    ]
):
    """Federal Offshore Gulf of America Proved Reserves fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> EiaNaturalGasFederalOffshoreGulfOfAmericaProvedReservesQueryParams:
        """Transform the query parameters."""
        return transform_dataset_query(
            EiaNaturalGasFederalOffshoreGulfOfAmericaProvedReservesQueryParams, params
        )

    @staticmethod
    async def aextract_data(
        query: EiaNaturalGasFederalOffshoreGulfOfAmericaProvedReservesQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract the data from the EIA API."""
        return await extract_dataset_data(query, credentials)

    @staticmethod
    def transform_data(
        query: EiaNaturalGasFederalOffshoreGulfOfAmericaProvedReservesQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> list[EiaNaturalGasFederalOffshoreGulfOfAmericaProvedReservesData]:
        """Transform the data."""
        return transform_dataset_data(
            EiaNaturalGasFederalOffshoreGulfOfAmericaProvedReservesData, query, data
        )
