"""Feedstocks Consumed for Production of Biofuels model."""

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


class EiaPetroleumFeedstocksConsumedForProductionOfBiofuelsQueryParams(
    EiaApiQueryParams
):
    """Feedstocks Consumed for Production of Biofuels. EIA petroleum gas survey data

    Source: https://www.eia.gov/opendata/browser/petroleum/pnp/feedbiofuel
    """

    __group__ = "petroleum"
    __dataset__ = "feedstocks_consumed_for_production_of_biofuels"
    __json_schema_extra__ = {
        "product": {
            "multiple_items_allowed": True,
            "choices": [
                "agriculture_and_forestry_residues",
                "algae_inputs_to_biodiesel_production",
                "biogas",
                "canola_oil_inputs_to_biodiesel_production",
                "canola_oil_for_biodiesel_plants",
                "canola_oil_for_renewable_diesels_plants",
                "corn",
                "corn_oil_inputs_to_biodiesel_production",
                "corn_oil_for_biodiesel_plants",
                "corn_oil_for_renewable_diesel_plants",
                "dedicated_energy_crops",
                "grain_sorghum",
                "municipal_solid_waste",
                "other_biofuel_feedstocks",
                "other_agriculture_and_forestry_products",
                "other_animal_fats_inputs_to_biodiesel_production",
                "other_recycled_feeds",
                "other_vegetable_oil_inputs_to_biodiesel_production",
                "poultry_inputs_to_biodiesel_production",
                "soybean_oil_inputs_to_biodiesel_production",
                "soybean_oill_biodiesel_plants",
                "soybean_oill_renewable_diesel_plants",
                "tallow_inputs_to_biodiesel_production",
                "white_grease_inputs_to_biodiesel_production",
                "yard_and_food_waste",
                "yellow_grease_inputs_to_biodiesel_production",
            ],
        },
        "series": {
            "multiple_items_allowed": True,
            "choices": [
                "agriculture_and_forestry_residues_inputs_to_biofuels",
                "biogas_inputs_to_biofuels_production",
                "canola_oil_inputs_to_biofuels_production_at_biodiesel_plants",
                "canola_oil_inputs_to_biofuels_production_at_renewable",
                "corn_inputs_to_biofuels_production",
                "corn_oil_inputs_to_biofuels_production_at_biodiesel_plants",
                "corn_oil_inputs_to_biofuels_production_at_renewable_diesel",
                "dedicated_energy_crops_inputs_to_biofuels_production",
                "grain_sorghum_inputs_to_biofuels_production",
                "municipal_solid_waste_inputs_to_biofules_production",
                "oil_from_algae_inputs_to_biofuels_production",
                "other_biofuel_feedstocks_inputs_to_biofuels_production",
                "other_recycled_feed_inputs_to_biofuels_production",
                "other_vegetable_oil_inputs_to_biofuels_production",
                "other_waste_oil_fat_and_grease_inputs_to_biofuels_production",
                "other_agriculture_and_forestry_products_inputs_to_biofuels",
                "poultry_inputs_to_biofuels_production",
                "soybean_oil_inputs_to_biofuels_production_at_biodiesel",
                "soybean_oil_inputs_to_biofuels_production_at_renewable",
                "tallow_inputs_to_biofuels_production",
                "total_canola_oil_inputs_to_biofuels_production",
                "total_corn_oil_inputs_to_biofuels_production",
                "total_soybean_oil_inputs_to_biofuels_production",
                "white_grease_inputs_to_biofuels_production",
                "yard_and_food_waste_inputs_to_biofuels_production",
                "yellow_grease_inputs_to_biofuels_production",
            ],
        },
    }

    product: str | None = Field(
        default=None,
        description="Product filter. Accepts a comma-separated list of values.",
    )
    series: str | None = Field(
        default=None,
        description="Series filter. Accepts a comma-separated list of values.",
    )


class EiaPetroleumFeedstocksConsumedForProductionOfBiofuelsData(EiaApiData):
    """Feedstocks Consumed for Production of Biofuels. EIA petroleum gas survey data"""

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


class EiaPetroleumFeedstocksConsumedForProductionOfBiofuelsFetcher(
    Fetcher[
        EiaPetroleumFeedstocksConsumedForProductionOfBiofuelsQueryParams,
        list[EiaPetroleumFeedstocksConsumedForProductionOfBiofuelsData],
    ]
):
    """Feedstocks Consumed for Production of Biofuels fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> EiaPetroleumFeedstocksConsumedForProductionOfBiofuelsQueryParams:
        """Transform the query parameters."""
        return transform_dataset_query(
            EiaPetroleumFeedstocksConsumedForProductionOfBiofuelsQueryParams, params
        )

    @staticmethod
    async def aextract_data(
        query: EiaPetroleumFeedstocksConsumedForProductionOfBiofuelsQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract the data from the EIA API."""
        return await extract_dataset_data(query, credentials)

    @staticmethod
    def transform_data(
        query: EiaPetroleumFeedstocksConsumedForProductionOfBiofuelsQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> list[EiaPetroleumFeedstocksConsumedForProductionOfBiofuelsData]:
        """Transform the data."""
        return transform_dataset_data(
            EiaPetroleumFeedstocksConsumedForProductionOfBiofuelsData, query, data
        )
