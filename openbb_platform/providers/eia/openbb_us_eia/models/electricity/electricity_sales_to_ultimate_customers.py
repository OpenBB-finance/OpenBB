"""Electricity Sales to Ultimate Customers model."""

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


class EiaElectricityElectricitySalesToUltimateCustomersQueryParams(EiaApiQueryParams):
    """Electricity Sales to Ultimate Customers. Electricity sales to ultimate customer by state and sector (number of customers, average price, revenue, and megawatthours of sales). Sources: Forms EIA-826, EIA-861, EIA-861M

    Source: https://www.eia.gov/opendata/browser/electricity/retail-sales
    """

    __group__ = "electricity"
    __dataset__ = "electricity_sales_to_ultimate_customers"
    __json_schema_extra__ = {
        "data_type": {
            "multiple_items_allowed": True,
            "choices": ["customers", "price", "revenue", "sales"],
        },
        "sector": {
            "multiple_items_allowed": True,
            "choices": [
                "all_sectors",
                "commercial",
                "industrial",
                "other",
                "residential",
                "transportation",
            ],
        },
        "state": {
            "multiple_items_allowed": True,
            "choices": [
                "alabama",
                "alaska",
                "arizona",
                "arkansas",
                "california",
                "colorado",
                "connecticut",
                "delaware",
                "district_of_columbia",
                "east_north_central",
                "east_south_central",
                "florida",
                "georgia",
                "hawaii",
                "idaho",
                "illinois",
                "indiana",
                "iowa",
                "kansas",
                "kentucky",
                "louisiana",
                "maine",
                "maryland",
                "massachusetts",
                "michigan",
                "middle_atlantic",
                "minnesota",
                "mississippi",
                "missouri",
                "montana",
                "mountain",
                "nebraska",
                "nevada",
                "new_england",
                "new_hampshire",
                "new_jersey",
                "new_mexico",
                "new_york",
                "north_carolina",
                "north_dakota",
                "ohio",
                "oklahoma",
                "oregon",
                "pacific_contiguous",
                "pacific_noncontiguous",
                "pennsylvania",
                "rhode_island",
                "south_atlantic",
                "south_carolina",
                "south_dakota",
                "tennessee",
                "texas",
                "us_total",
                "utah",
                "vermont",
                "virginia",
                "washington",
                "west_north_central",
                "west_south_central",
                "west_virginia",
                "wisconsin",
                "wyoming",
            ],
        },
    }

    frequency: Literal["annual", "monthly", "quarterly"] | None = Field(
        default=None,
        description="The data frequency. The default is 'monthly'.",
    )
    data_type: str | None = Field(
        default=None,
        description="Data column(s) to return, comma-separated. The default returns every column. Choices: customers = Number of Ultimate Customers (number of customers); price = Average Price of Electricity to Ultimate Customers (cents per kilowatt-hour); revenue = Revenue from Sales to Ultimate Customers (million dollars); sales = Megawatt-hours Sold to Ultimate Customers (million kilowatt hours).",
    )
    sector: str | None = Field(
        default=None,
        description="Sector filter. Accepts a comma-separated list of values.",
    )
    state: str | None = Field(
        default=None,
        description="State / Census Region filter. Accepts a comma-separated list of values.",
    )


class EiaElectricityElectricitySalesToUltimateCustomersData(EiaApiData):
    """Electricity Sales to Ultimate Customers. Electricity sales to ultimate customer by state and sector (number of customers, average price, revenue, and megawatthours of sales). Sources: Forms EIA-826, EIA-861, EIA-861M"""

    sector: str | None = Field(
        default=None,
        description="Sector code.",
    )
    sector_name: str | None = Field(
        default=None,
        description="Sector name.",
    )
    state: str | None = Field(
        default=None,
        description="State / Census Region code.",
    )
    state_name: str | None = Field(
        default=None,
        description="State / Census Region name.",
    )
    customers: float | None = Field(
        default=None,
        description="Number of Ultimate Customers (number of customers). Withheld or unavailable values return as null.",
    )
    price: float | None = Field(
        default=None,
        description="Average Price of Electricity to Ultimate Customers (cents per kilowatt-hour). Withheld or unavailable values return as null.",
    )
    revenue: float | None = Field(
        default=None,
        description="Revenue from Sales to Ultimate Customers (million dollars). Withheld or unavailable values return as null.",
    )
    sales: float | None = Field(
        default=None,
        description="Megawatt-hours Sold to Ultimate Customers (million kilowatt hours). Withheld or unavailable values return as null.",
    )


class EiaElectricityElectricitySalesToUltimateCustomersFetcher(
    Fetcher[
        EiaElectricityElectricitySalesToUltimateCustomersQueryParams,
        list[EiaElectricityElectricitySalesToUltimateCustomersData],
    ]
):
    """Electricity Sales to Ultimate Customers fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> EiaElectricityElectricitySalesToUltimateCustomersQueryParams:
        """Transform the query parameters."""
        return transform_dataset_query(
            EiaElectricityElectricitySalesToUltimateCustomersQueryParams, params
        )

    @staticmethod
    async def aextract_data(
        query: EiaElectricityElectricitySalesToUltimateCustomersQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract the data from the EIA API."""
        return await extract_dataset_data(query, credentials)

    @staticmethod
    def transform_data(
        query: EiaElectricityElectricitySalesToUltimateCustomersQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> list[EiaElectricityElectricitySalesToUltimateCustomersData]:
        """Transform the data."""
        return transform_dataset_data(
            EiaElectricityElectricitySalesToUltimateCustomersData, query, data
        )
