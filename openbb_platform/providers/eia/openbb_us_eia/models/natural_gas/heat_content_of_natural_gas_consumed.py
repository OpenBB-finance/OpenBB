"""Heat Content of Natural Gas Consumed model."""

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


class EiaNaturalGasHeatContentOfNaturalGasConsumedQueryParams(EiaApiQueryParams):
    """Heat Content of Natural Gas Consumed. EIA natural gas survey data

    Source: https://www.eia.gov/opendata/browser/natural-gas/cons/heat
    """

    __group__ = "natural_gas"
    __dataset__ = "heat_content_of_natural_gas_consumed"
    __json_schema_extra__ = {
        "region": {
            "multiple_items_allowed": True,
            "choices": [
                "california",
                "colorado",
                "florida",
                "massachusetts",
                "minnesota",
                "new_york",
                "ohio",
                "texas",
                "us",
                "usa_ak",
                "usa_al",
                "usa_ar",
                "usa_az",
                "usa_ct",
                "usa_dc",
                "usa_de",
                "usa_ga",
                "usa_hi",
                "usa_ia",
                "usa_id",
                "usa_il",
                "usa_in",
                "usa_ks",
                "usa_ky",
                "usa_la",
                "usa_md",
                "usa_me",
                "usa_mi",
                "usa_mo",
                "usa_ms",
                "usa_mt",
                "usa_nc",
                "usa_nd",
                "usa_ne",
                "usa_nh",
                "usa_nj",
                "usa_nm",
                "usa_nv",
                "usa_ok",
                "usa_or",
                "usa_pa",
                "usa_ri",
                "usa_sc",
                "usa_sd",
                "usa_tn",
                "usa_ut",
                "usa_va",
                "usa_vt",
                "usa_wi",
                "usa_wv",
                "usa_wy",
                "washington",
            ],
        },
        "series": {
            "multiple_items_allowed": True,
            "choices": [
                "alabama_heat_content_of_natural_gas_deliveries_to_consumers",
                "alaska_heat_content_of_natural_gas_deliveries_to_consumers",
                "arizona_heat_content_of_natural_gas_deliveries_to_consumers",
                "arkansas_heat_content_of_natural_gas_deliveries_to_consumers",
                "california_heat_content_of_natural_gas_deliveries_to",
                "colorado_heat_content_of_natural_gas_deliveries_to_consumers",
                "connecticut_heat_content_of_natural_gas_deliveries_to",
                "delaware_heat_content_of_natural_gas_deliveries_to_consumers",
                "district_of_columbia_heat_content_of_natural_gas_deliveries",
                "florida_heat_content_of_natural_gas_deliveries_to_consumers",
                "georgia_heat_content_of_natural_gas_deliveries_to_consumers",
                "hawaii_heat_content_of_natural_gas_deliveries_to_consumers",
                "idaho_heat_content_of_natural_gas_deliveries_to_consumers",
                "illinois_heat_content_of_natural_gas_deliveries_to_consumers",
                "indiana_heat_content_of_natural_gas_deliveries_to_consumers",
                "iowa_heat_content_of_natural_gas_deliveries_to_consumers",
                "kansas_heat_content_of_natural_gas_deliveries_to_consumers",
                "kentucky_heat_content_of_natural_gas_deliveries_to_consumers",
                "louisiana_heat_content_of_natural_gas_deliveries_to",
                "maine_heat_content_of_natural_gas_deliveries_to_consumers",
                "maryland_heat_content_of_natural_gas_deliveries_to_consumers",
                "massachusetts_heat_content_of_natural_gas_deliveries_to",
                "michigan_heat_content_of_natural_gas_deliveries_to_consumers",
                "minnesota_heat_content_of_natural_gas_deliveries_to",
                "mississippi_heat_content_of_natural_gas_deliveries_to",
                "missouri_heat_content_of_natural_gas_deliveries_to_consumers",
                "montana_heat_content_of_natural_gas_deliveries_to_consumers",
                "nebraska_heat_content_of_natural_gas_deliveries_to_consumers",
                "nevada_heat_content_of_natural_gas_deliveries_to_consumers",
                "new_hampshire_heat_content_of_natural_gas_deliveries_to",
                "new_jersey_heat_content_of_natural_gas_deliveries_to",
                "new_mexico_heat_content_of_natural_gas_deliveries_to",
                "new_york_heat_content_of_natural_gas_deliveries_to_consumers",
                "north_carolina_heat_content_of_natural_gas_deliveries_to",
                "north_dakota_heat_content_of_natural_gas_deliveries_to",
                "ohio_heat_content_of_natural_gas_deliveries_to_consumers",
                "oklahoma_heat_content_of_natural_gas_deliveries_to_consumers",
                "oregon_heat_content_of_natural_gas_deliveries_to_consumers",
                "pennsylvania_heat_content_of_natural_gas_deliveries_to",
                "rhode_island_heat_content_of_natural_gas_deliveries_to",
                "south_carolina_heat_content_of_natural_gas_deliveries_to",
                "south_dakota_heat_content_of_natural_gas_deliveries_to",
                "tennessee_heat_content_of_natural_gas_deliveries_to",
                "texas_heat_content_of_natural_gas_deliveries_to_consumers",
                "us_heat_content_of_natural_gas_deliveries_to_consumers",
                "utah_heat_content_of_natural_gas_deliveries_to_consumers",
                "vermont_heat_content_of_natural_gas_deliveries_to_consumers",
                "virginia_heat_content_of_natural_gas_deliveries_to_consumers",
                "washington_heat_content_of_natural_gas_deliveries_to",
                "west_virginia_heat_content_of_natural_gas_deliveries_to",
                "wisconsin_heat_content_of_natural_gas_deliveries_to",
                "wyoming_heat_content_of_natural_gas_deliveries_to_consumers",
            ],
        },
    }

    frequency: Literal["annual", "monthly"] | None = Field(
        default=None,
        description="The data frequency. The default is 'monthly'.",
    )
    region: str | None = Field(
        default=None,
        description="DuoArea filter. Accepts a comma-separated list of values.",
    )
    series: str | None = Field(
        default=None,
        description="Series filter. Accepts a comma-separated list of values.",
    )


class EiaNaturalGasHeatContentOfNaturalGasConsumedData(EiaApiData):
    """Heat Content of Natural Gas Consumed. EIA natural gas survey data"""

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


class EiaNaturalGasHeatContentOfNaturalGasConsumedFetcher(
    Fetcher[
        EiaNaturalGasHeatContentOfNaturalGasConsumedQueryParams,
        list[EiaNaturalGasHeatContentOfNaturalGasConsumedData],
    ]
):
    """Heat Content of Natural Gas Consumed fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> EiaNaturalGasHeatContentOfNaturalGasConsumedQueryParams:
        """Transform the query parameters."""
        return transform_dataset_query(
            EiaNaturalGasHeatContentOfNaturalGasConsumedQueryParams, params
        )

    @staticmethod
    async def aextract_data(
        query: EiaNaturalGasHeatContentOfNaturalGasConsumedQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract the data from the EIA API."""
        return await extract_dataset_data(query, credentials)

    @staticmethod
    def transform_data(
        query: EiaNaturalGasHeatContentOfNaturalGasConsumedQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> list[EiaNaturalGasHeatContentOfNaturalGasConsumedData]:
        """Transform the data."""
        return transform_dataset_data(
            EiaNaturalGasHeatContentOfNaturalGasConsumedData, query, data
        )
