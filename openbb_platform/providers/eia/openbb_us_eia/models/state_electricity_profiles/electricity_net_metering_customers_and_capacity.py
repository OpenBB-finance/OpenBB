"""Electricity Net Metering: Customers and Capacity model."""

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


class EiaStateElectricityProfilesElectricityNetMeteringCustomersAndCapacityQueryParams(
    EiaApiQueryParams
):
    """Electricity Net Metering: Customers and Capacity. Electricity net metering customer counts and capacity by state, sector, and generating technology. Source: Form EIA-861 Product: State Electricity Profiles, Table 11

    Source: https://www.eia.gov/opendata/browser/electricity/state-electricity-profiles/net-metering
    """

    __group__ = "state_electricity_profiles"
    __dataset__ = "electricity_net_metering_customers_and_capacity"
    __json_schema_extra__ = {
        "data_type": {
            "multiple_items_allowed": True,
            "choices": ["capacity", "customers"],
        },
        "sector": {"multiple_items_allowed": True},
        "state": {"multiple_items_allowed": True},
        "technology": {"multiple_items_allowed": True},
    }

    data_type: str | None = Field(
        default=None,
        description="Data column(s) to return, comma-separated. The default returns every column. Choices: capacity (megawatts); customers = Customer Count (number of customers).",
    )
    sector: str | None = Field(
        default=None,
        description="sector filter. Accepts a comma-separated list of values. Use the `facet_options` endpoint for the valid values.",
    )
    state: str | None = Field(
        default=None,
        description="state filter. Accepts a comma-separated list of values. Use the `facet_options` endpoint for the valid values.",
    )
    technology: str | None = Field(
        default=None,
        description="Technology used to Generate Electricity filter. Accepts a comma-separated list of values. Use the `facet_options` endpoint for the valid values.",
    )


class EiaStateElectricityProfilesElectricityNetMeteringCustomersAndCapacityData(
    EiaApiData
):
    """Electricity Net Metering: Customers and Capacity. Electricity net metering customer counts and capacity by state, sector, and generating technology. Source: Form EIA-861 Product: State Electricity Profiles, Table 11"""

    sector: str | None = Field(
        default=None,
        description="sector code.",
    )
    sector_name: str | None = Field(
        default=None,
        description="sector name.",
    )
    state: str | None = Field(
        default=None,
        description="state code.",
    )
    state_name: str | None = Field(
        default=None,
        description="state name.",
    )
    technology: str | None = Field(
        default=None,
        description="Technology used to Generate Electricity code.",
    )
    technology_name: str | None = Field(
        default=None,
        description="Technology used to Generate Electricity name.",
    )
    capacity: float | None = Field(
        default=None,
        description="Capacity (megawatts). Withheld or unavailable values return as null.",
    )
    customers: float | None = Field(
        default=None,
        description="Customer Count (number of customers). Withheld or unavailable values return as null.",
    )


class EiaStateElectricityProfilesElectricityNetMeteringCustomersAndCapacityFetcher(
    Fetcher[
        EiaStateElectricityProfilesElectricityNetMeteringCustomersAndCapacityQueryParams,
        list[EiaStateElectricityProfilesElectricityNetMeteringCustomersAndCapacityData],
    ]
):
    """Electricity Net Metering: Customers and Capacity fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> (
        EiaStateElectricityProfilesElectricityNetMeteringCustomersAndCapacityQueryParams
    ):
        """Transform the query parameters."""
        return transform_dataset_query(
            EiaStateElectricityProfilesElectricityNetMeteringCustomersAndCapacityQueryParams,
            params,
        )

    @staticmethod
    async def aextract_data(
        query: EiaStateElectricityProfilesElectricityNetMeteringCustomersAndCapacityQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract the data from the EIA API."""
        return await extract_dataset_data(query, credentials)

    @staticmethod
    def transform_data(
        query: EiaStateElectricityProfilesElectricityNetMeteringCustomersAndCapacityQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> list[
        EiaStateElectricityProfilesElectricityNetMeteringCustomersAndCapacityData
    ]:
        """Transform the data."""
        return transform_dataset_data(
            EiaStateElectricityProfilesElectricityNetMeteringCustomersAndCapacityData,
            query,
            data,
        )
