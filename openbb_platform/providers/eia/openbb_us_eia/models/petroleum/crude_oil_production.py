"""Crude Oil Production model."""

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


class EiaPetroleumCrudeOilProductionQueryParams(EiaApiQueryParams):
    """Crude Oil Production. EIA petroleum gas survey data

    Source: https://www.eia.gov/opendata/browser/petroleum/crd/crpdn
    """

    __group__ = "petroleum"
    __dataset__ = "crude_oil_production"
    __json_schema_extra__ = {
        "product": {
            "multiple_items_allowed": True,
            "choices": ["ans_crude_oil", "crude_oil"],
        },
        "region": {
            "multiple_items_allowed": True,
            "choices": [
                "california",
                "colorado",
                "florida",
                "na",
                "new_york",
                "ohio",
                "padd_1",
                "padd_2",
                "padd_3",
                "padd_4",
                "padd_5",
                "texas",
                "us",
                "usa_ak",
                "usa_al",
                "usa_ar",
                "usa_az",
                "usa_id",
                "usa_il",
                "usa_in",
                "usa_ks",
                "usa_ky",
                "usa_la",
                "usa_mi",
                "usa_mo",
                "usa_ms",
                "usa_mt",
                "usa_nd",
                "usa_ne",
                "usa_nm",
                "usa_nv",
                "usa_ok",
                "usa_pa",
                "usa_sd",
                "usa_tn",
                "usa_ut",
                "usa_va",
                "usa_wv",
                "usa_wy",
            ],
        },
        "series": {
            "multiple_items_allowed": True,
            "choices": [
                "alabama_field_production_of_crude_oil_thousand_barrels_per_day",
                "alabama_field_production_of_crude_oil_thousand_barrels",
                "alaska_field_production_of_crude_oil_thousand_barrels_per_day",
                "alaska_field_production_of_crude_oil_thousand_barrels",
                "alaska_north_slope_crude_oil_production_thousand_barrels_per_day",
                "alaska_north_slope_crude_oil_production_thousand_barrels",
                "alaska_south_field_production_of_crude_oil_thousand_barrels_per_day",
                "alaska_south_field_production_of_crude_oil_thousand_barrels",
                "arizona_field_production_of_crude_oil_thousand_barrels_per_day",
                "arizona_field_production_of_crude_oil_thousand_barrels",
                "arkansas_field_production_of_crude_oil_thousand_barrels_per_day",
                "arkansas_field_production_of_crude_oil_thousand_barrels",
                "california_field_production_of_crude_oil_thousand_barrels_per_day",
                "california_field_production_of_crude_oil_thousand_barrels",
                "colorado_field_production_of_crude_oil_thousand_barrels_per_day",
                "colorado_field_production_of_crude_oil_thousand_barrels",
                "east_coast_padd_1_field_production_of_crude_oil_thousand_barrels_per_day",
                "east_coast_padd_1_field_production_of_crude_oil_thousand_barrels",
                "federal_offshore_padd_5_field_production_of_crude_oil_thousand_barrels_per_day",
                "federal_offshore_padd_5_field_production_of_crude_oil_thousand_barrels",
                "federal_offshore_gulf_of_america_field_production_of_crude_oil_thousand_barrels_per_day",
                "federal_offshore_gulf_of_america_field_production_of_crude_oil_thousand_barrels",
                "florida_field_production_of_crude_oil_thousand_barrels_per_day",
                "florida_field_production_of_crude_oil_thousand_barrels",
                "gulf_coast_padd_3_field_production_of_crude_oil_thousand_barrels_per_day",
                "gulf_coast_padd_3_field_production_of_crude_oil_thousand_barrels",
                "idaho_field_production_of_crude_oil_thousand_barrels_per_day",
                "idaho_field_production_of_crude_oil_thousand_barrels",
                "illinois_field_production_of_crude_oil_thousand_barrels_per_day",
                "illinois_field_production_of_crude_oil_thousand_barrels",
                "indiana_field_production_of_crude_oil_thousand_barrels_per_day",
                "indiana_field_production_of_crude_oil_thousand_barrels",
                "kansas_field_production_of_crude_oil_thousand_barrels_per_day",
                "kansas_field_production_of_crude_oil_thousand_barrels",
                "kentucky_field_production_of_crude_oil_thousand_barrels_per_day",
                "kentucky_field_production_of_crude_oil_thousand_barrels",
                "louisiana_field_production_of_crude_oil_thousand_barrels_per_day",
                "louisiana_field_production_of_crude_oil_thousand_barrels",
                "michigan_field_production_of_crude_oil_thousand_barrels_per_day",
                "michigan_field_production_of_crude_oil_thousand_barrels",
                "midwest_padd_2_field_production_of_crude_oil_thousand_barrels_per_day",
                "midwest_padd_2_field_production_of_crude_oil_thousand_barrels",
                "mississippi_field_production_of_crude_oil_thousand_barrels_per_day",
                "mississippi_field_production_of_crude_oil_thousand_barrels",
                "missouri_field_production_of_crude_oil_thousand_barrels_per_day",
                "missouri_field_production_of_crude_oil_thousand_barrels",
                "montana_field_production_of_crude_oil_thousand_barrels_per_day",
                "montana_field_production_of_crude_oil_thousand_barrels",
                "nebraska_field_production_of_crude_oil_thousand_barrels_per_day",
                "nebraska_field_production_of_crude_oil_thousand_barrels",
                "nevada_field_production_of_crude_oil_thousand_barrels_per_day",
                "nevada_field_production_of_crude_oil_thousand_barrels",
                "new_mexico_field_production_of_crude_oil_thousand_barrels_per_day",
                "new_mexico_field_production_of_crude_oil_thousand_barrels",
                "new_york_field_production_of_crude_oil_thousand_barrels_per_day",
                "new_york_field_production_of_crude_oil_thousand_barrels",
                "north_dakota_field_production_of_crude_oil_thousand_barrels_per_day",
                "north_dakota_field_production_of_crude_oil_thousand_barrels",
                "ohio_field_production_of_crude_oil_thousand_barrels_per_day",
                "ohio_field_production_of_crude_oil_thousand_barrels",
                "oklahoma_field_production_of_crude_oil_thousand_barrels_per_day",
                "oklahoma_field_production_of_crude_oil_thousand_barrels",
                "pennsylvania_field_production_of_crude_oil_thousand_barrels_per_day",
                "pennsylvania_field_production_of_crude_oil_thousand_barrels",
                "rocky_mountain_padd_4_field_production_of_crude_oil_thousand_barrels_per_day",
                "rocky_mountain_padd_4_field_production_of_crude_oil_thousand_barrels",
                "south_dakota_field_production_of_crude_oil_thousand_barrels_per_day",
                "south_dakota_field_production_of_crude_oil_thousand_barrels",
                "tennessee_field_production_of_crude_oil_thousand_barrels_per_day",
                "tennessee_field_production_of_crude_oil_thousand_barrels",
                "texas_field_production_of_crude_oil_thousand_barrels_per_day",
                "texas_field_production_of_crude_oil_thousand_barrels",
                "us_field_production_of_crude_oil_thousand_barrels_per_day",
                "us_field_production_of_crude_oil_thousand_barrels",
                "utah_field_production_of_crude_oil_thousand_barrels_per_day",
                "utah_field_production_of_crude_oil_thousand_barrels",
                "virginia_field_production_of_crude_oil_thousand_barrels_per_day",
                "virginia_field_production_of_crude_oil_thousand_barrels",
                "west_coast_padd_5_field_production_of_crude_oil_thousand_barrels_per_day",
                "west_coast_padd_5_field_production_of_crude_oil_thousand_barrels",
                "west_virginia_field_production_of_crude_oil_thousand_barrels_per_day",
                "west_virginia_field_production_of_crude_oil_thousand_barrels",
                "wyoming_field_production_of_crude_oil_thousand_barrels_per_day",
                "wyoming_field_production_of_crude_oil_thousand_barrels",
            ],
        },
    }

    frequency: Literal["annual", "monthly"] | None = Field(
        default=None,
        description="The data frequency. The default is 'monthly'.",
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


class EiaPetroleumCrudeOilProductionData(EiaApiData):
    """Crude Oil Production. EIA petroleum gas survey data"""

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


class EiaPetroleumCrudeOilProductionFetcher(
    Fetcher[
        EiaPetroleumCrudeOilProductionQueryParams,
        list[EiaPetroleumCrudeOilProductionData],
    ]
):
    """Crude Oil Production fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> EiaPetroleumCrudeOilProductionQueryParams:
        """Transform the query parameters."""
        return transform_dataset_query(
            EiaPetroleumCrudeOilProductionQueryParams, params
        )

    @staticmethod
    async def aextract_data(
        query: EiaPetroleumCrudeOilProductionQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract the data from the EIA API."""
        return await extract_dataset_data(query, credentials)

    @staticmethod
    def transform_data(
        query: EiaPetroleumCrudeOilProductionQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> list[EiaPetroleumCrudeOilProductionData]:
        """Transform the data."""
        return transform_dataset_data(EiaPetroleumCrudeOilProductionData, query, data)
