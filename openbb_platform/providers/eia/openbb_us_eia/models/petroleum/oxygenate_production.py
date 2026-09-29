"""Oxygenate Production model."""

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


class EiaPetroleumOxygenateProductionQueryParams(EiaApiQueryParams):
    """Oxygenate Production. EIA petroleum gas survey data

    Source: https://www.eia.gov/opendata/browser/petroleum/pnp/oxy
    """

    __group__ = "petroleum"
    __dataset__ = "oxygenate_production"
    __json_schema_extra__ = {
        "process": {
            "multiple_items_allowed": True,
            "choices": [
                "captive_plants",
                "merchant_plants",
                "oxygenate_plant_production",
                "renewable_fuels_plant_and_oxygenate_plant_net_production",
            ],
        },
        "product": {
            "multiple_items_allowed": True,
            "choices": ["fuel_ethanol", "mtbe", "other_oxygenates", "oxygenates"],
        },
        "region": {
            "multiple_items_allowed": True,
            "choices": ["padd_1", "padd_2", "padd_3", "padd_4", "padd_5", "us"],
        },
        "series": {
            "multiple_items_allowed": True,
            "choices": [
                "east_coast_padd_1_mtbe_oxygenate_captive_facilities_production_thousand_barrels_per_day",
                "east_coast_padd_1_mtbe_oxygenate_captive_facilities_production_thousand_barrels",
                "east_coast_padd_1_mtbe_oxygenate_merchant_facilities_production_thousand_barrels_per_day",
                "east_coast_padd_1_mtbe_oxygenate_merchant_facilities_production_thousand_barrels",
                "east_coast_padd_1_oxygenate_plant_production_of_fuel_ethanol_thousand_barrels_per_day",
                "east_coast_padd_1_oxygenate_plant_production_of_fuel_ethanol_thousand_barrels",
                "east_coast_padd_1_oxygenate_plant_production_of_mtbe_thousand_barrels_per_day",
                "east_coast_padd_1_oxygenate_plant_production_of_mtbe_thousand_barrels",
                "gulf_coast_padd_3_biofuels_plant_net_production_of_other_oxygenates_thousand_barrels_per_day",
                "gulf_coast_padd_3_biofuels_plant_net_production_of_other_oxygenates_thousand_barrels",
                "gulf_coast_padd_3_mtbe_oxygenate_captive_facilities_production_thousand_barrels_per_day",
                "gulf_coast_padd_3_mtbe_oxygenate_captive_facilities_production_thousand_barrels",
                "gulf_coast_padd_3_mtbe_oxygenate_merchant_facilities_production_thousand_barrels_per_day",
                "gulf_coast_padd_3_mtbe_oxygenate_merchant_facilities_production_thousand_barrels",
                "gulf_coast_padd_3_oxygenate_plant_production_of_fuel_ethanol_thousand_barrels_per_day",
                "gulf_coast_padd_3_oxygenate_plant_production_of_fuel_ethanol_thousand_barrels",
                "gulf_coast_padd_3_oxygenate_plant_production_of_mtbe_thousand_barrels_per_day",
                "gulf_coast_padd_3_oxygenate_plant_production_of_mtbe_thousand_barrels",
                "gulf_coast_padd_3_oxygenate_plant_production_of_oxygenates_excluding_fuel_ethanol_thousand_barrels_per_day",
                "gulf_coast_padd_3_oxygenate_plant_production_of_oxygenates_excluding_fuel_ethanol_thousand_barrels",
                "midwest_padd_2_biofuels_plant_net_production_of_other_oxygenates_thousand_barrels_per_day",
                "midwest_padd_2_biofuels_plant_net_production_of_other_oxygenates_thousand_barrels",
                "midwest_padd_2_mtbe_oxygenate_captive_facilities_production_thousand_barrels_per_day",
                "midwest_padd_2_mtbe_oxygenate_captive_facilities_production_thousand_barrels",
                "midwest_padd_2_mtbe_oxygenate_merchant_facilities_production_thousand_barrels_per_day",
                "midwest_padd_2_mtbe_oxygenate_merchant_facilities_production_thousand_barrels",
                "midwest_padd_2_oxygenate_plant_production_of_fuel_ethanol_thousand_barrels_per_day",
                "midwest_padd_2_oxygenate_plant_production_of_fuel_ethanol_thousand_barrels",
                "midwest_padd_2_oxygenate_plant_production_of_oxygenates_excluding_fuel_ethanol_thousand_barrels_per_day",
                "midwest_padd_2_oxygenate_plant_production_of_oxygenates_excluding_fuel_ethanol_thousand_barrels",
                "rocky_mountain_padd_4_mtbe_oxygenate_captive_facilities_production_thousand_barrels_per_day",
                "rocky_mountain_padd_4_mtbe_oxygenate_captive_facilities_production_thousand_barrels",
                "rocky_mountain_padd_4_mtbe_oxygenate_merchant_facilities_production_thousand_barrels_per_day",
                "rocky_mountain_padd_4_mtbe_oxygenate_merchant_facilities_production_thousand_barrels",
                "rocky_mountain_padd_4_oxygenate_plant_production_of_fuel_ethanol_thousand_barrels_per_day",
                "rocky_mountain_padd_4_oxygenate_plant_production_of_fuel_ethanol_thousand_barrels",
                "us_biofuels_plant_net_production_of_other_oxygenates_thousand_barrels_per_day",
                "us_biofuels_plant_net_production_of_other_oxygenates_thousand_barrels",
                "us_mtbe_oxygenate_captive_facilities_production_thousand_barrels_per_day",
                "us_mtbe_oxygenate_captive_facilities_production_thousand_barrels",
                "us_mtbe_oxygenate_merchant_facilities_production_thousand_barrels_per_day",
                "us_mtbe_oxygenate_merchant_facilities_production_thousand_barrels",
                "us_oxygenate_plant_production_of_fuel_ethanol_thousand_barrels_per_day",
                "us_oxygenate_plant_production_of_fuel_ethanol_thousand_barrels",
                "us_oxygenate_plant_production_of_mtbe_thousand_barrels_per_day",
                "us_oxygenate_plant_production_of_mtbe_thousand_barrels",
                "us_oxygenate_plant_production_of_oxygenates_excluding_fuel_ethanol_thousand_barrels_per_day",
                "us_oxygenate_plant_production_of_oxygenates_excluding_fuel_ethanol_thousand_barrels",
                "west_coast_padd_5_mtbe_oxygenate_captive_facilities_production_thousand_barrels_per_day",
                "west_coast_padd_5_mtbe_oxygenate_captive_facilities_production_thousand_barrels",
                "west_coast_padd_5_mtbe_oxygenate_merchant_facilities_production_thousand_barrels_per_day",
                "west_coast_padd_5_mtbe_oxygenate_merchant_facilities_production_thousand_barrels",
                "west_coast_padd_5_oxygenate_plant_production_of_fuel_ethanol_thousand_barrels_per_day",
                "west_coast_padd_5_oxygenate_plant_production_of_fuel_ethanol_thousand_barrels",
            ],
        },
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
        description="Series filter. Accepts a comma-separated list of values.",
    )


class EiaPetroleumOxygenateProductionData(EiaApiData):
    """Oxygenate Production. EIA petroleum gas survey data"""

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


class EiaPetroleumOxygenateProductionFetcher(
    Fetcher[
        EiaPetroleumOxygenateProductionQueryParams,
        list[EiaPetroleumOxygenateProductionData],
    ]
):
    """Oxygenate Production fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> EiaPetroleumOxygenateProductionQueryParams:
        """Transform the query parameters."""
        return transform_dataset_query(
            EiaPetroleumOxygenateProductionQueryParams, params
        )

    @staticmethod
    async def aextract_data(
        query: EiaPetroleumOxygenateProductionQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract the data from the EIA API."""
        return await extract_dataset_data(query, credentials)

    @staticmethod
    def transform_data(
        query: EiaPetroleumOxygenateProductionQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> list[EiaPetroleumOxygenateProductionData]:
        """Transform the data."""
        return transform_dataset_data(EiaPetroleumOxygenateProductionData, query, data)
