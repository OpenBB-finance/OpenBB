"""Consumption and Quality model."""

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


class EiaCoalConsumptionAndQualityQueryParams(EiaApiQueryParams):
    """Consumption and Quality. Coal consumption and quality data by state and sector, including price, reciepts, heat content, sulfur content, ash content, and stocks. Source: EIA Form 7A and MSHA Form 7000-2. Interactive browser: https://www.eia.gov/coal/data/browser/

    Source: https://www.eia.gov/opendata/browser/coal/consumption-and-quality
    """

    __group__ = "coal"
    __dataset__ = "consumption_and_quality"
    __json_schema_extra__ = {
        "data_type": {
            "multiple_items_allowed": True,
            "choices": [
                "ash_content",
                "consumption",
                "heat_content",
                "price",
                "receipts",
                "stocks",
                "sulfur_content",
            ],
        },
        "sector": {
            "multiple_items_allowed": True,
            "choices": [
                "coke_plants",
                "commercial_and_institutional",
                "electric_power",
                "electric_utility",
                "ipp_chp",
                "ipp_non_chp",
                "independent_power_producers",
                "other_industrial",
            ],
        },
        "state_region": {
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
                "pacific",
                "pacific_contiguous",
                "pacific_noncontiguous",
                "pennsylvania",
                "puerto_rico",
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

    frequency: Literal["annual", "quarterly"] | None = Field(
        default=None,
        description="The data frequency. The default is 'annual'.",
    )
    data_type: str | None = Field(
        default=None,
        description="Data column(s) to return, comma-separated. The default returns every column. Choices: ash_content (average ash percent by weight); consumption (short tons); heat_content (average sulfur percent by weight); price (dollars per short ton); receipts (short tons); stocks (short tons); sulfur_content (average sulfur percent by weight).",
    )
    sector: str | None = Field(
        default=None,
        description="Sector filter. Accepts a comma-separated list of values.",
    )
    state_region: str | None = Field(
        default=None,
        description="U.S. Total, States, and Census Regions. filter. Accepts a comma-separated list of values.",
    )


class EiaCoalConsumptionAndQualityData(EiaApiData):
    """Consumption and Quality. Coal consumption and quality data by state and sector, including price, reciepts, heat content, sulfur content, ash content, and stocks. Source: EIA Form 7A and MSHA Form 7000-2. Interactive browser: https://www.eia.gov/coal/data/browser/"""

    sector: str | None = Field(
        default=None,
        description="Sector code.",
    )
    sector_name: str | None = Field(
        default=None,
        description="Sector name.",
    )
    state_region: str | None = Field(
        default=None,
        description="U.S. Total, States, and Census Regions. code.",
    )
    state_region_name: str | None = Field(
        default=None,
        description="U.S. Total, States, and Census Regions. name.",
    )
    ash_content: float | None = Field(
        default=None,
        description="Ash content (average ash percent by weight). Withheld or unavailable values return as null.",
    )
    consumption: float | None = Field(
        default=None,
        description="Consumption (short tons). Withheld or unavailable values return as null.",
    )
    heat_content: float | None = Field(
        default=None,
        description="Heat content (average sulfur percent by weight). Withheld or unavailable values return as null.",
    )
    price: float | None = Field(
        default=None,
        description="Price (dollars per short ton). Withheld or unavailable values return as null.",
    )
    receipts: float | None = Field(
        default=None,
        description="Receipts (short tons). Withheld or unavailable values return as null.",
    )
    stocks: float | None = Field(
        default=None,
        description="Stocks (short tons). Withheld or unavailable values return as null.",
    )
    sulfur_content: float | None = Field(
        default=None,
        description="Sulfur content (average sulfur percent by weight). Withheld or unavailable values return as null.",
    )


class EiaCoalConsumptionAndQualityFetcher(
    Fetcher[
        EiaCoalConsumptionAndQualityQueryParams, list[EiaCoalConsumptionAndQualityData]
    ]
):
    """Consumption and Quality fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> EiaCoalConsumptionAndQualityQueryParams:
        """Transform the query parameters."""
        return transform_dataset_query(EiaCoalConsumptionAndQualityQueryParams, params)

    @staticmethod
    async def aextract_data(
        query: EiaCoalConsumptionAndQualityQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract the data from the EIA API."""
        return await extract_dataset_data(query, credentials)

    @staticmethod
    def transform_data(
        query: EiaCoalConsumptionAndQualityQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> list[EiaCoalConsumptionAndQualityData]:
        """Transform the data."""
        return transform_dataset_data(EiaCoalConsumptionAndQualityData, query, data)
