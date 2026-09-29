"""Natural Gas Wellhead Value and Marketed Production model."""

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


class EiaNaturalGasNaturalGasWellheadValueAndMarketedProductionQueryParams(
    EiaApiQueryParams
):
    """Natural Gas Wellhead Value and Marketed Production. EIA natural gas survey data

    Source: https://www.eia.gov/opendata/browser/natural-gas/prod/whv
    """

    __group__ = "natural_gas"
    __dataset__ = "natural_gas_wellhead_value_and_marketed_production"
    __json_schema_extra__ = {
        "process": {
            "multiple_items_allowed": True,
            "choices": ["marketed_production", "wellhead_acquisition_price"],
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
                "usa_md",
                "usa_mi",
                "usa_mo",
                "usa_ms",
                "usa_mt",
                "usa_nd",
                "usa_ne",
                "usa_nm",
                "usa_nv",
                "usa_ok",
                "usa_or",
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
                "alabama_natural_gas_marketed_production",
                "alaska_natural_gas_marketed_production",
                "arizona_natural_gas_marketed_production",
                "arkansas_natural_gas_marketed_production",
                "california_natural_gas_marketed_production",
                "colorado_natural_gas_marketed_production",
                "federal_offshore_gulf_of_america_natural_gas_marketed",
                "florida_natural_gas_marketed_production",
                "idaho_marketed_production_of_natural_gas",
                "illinois_natural_gas_marketed_production",
                "indiana_natural_gas_marketed_production",
                "kansas_natural_gas_marketed_production",
                "kentucky_natural_gas_marketed_production",
                "louisiana_natural_gas_marketed_production",
                "maryland_natural_gas_marketed_production",
                "michigan_natural_gas_marketed_production",
                "mississippi_natural_gas_marketed_production",
                "missouri_natural_gas_marketed_production",
                "montana_natural_gas_marketed_production",
                "nebraska_natural_gas_marketed_production",
                "nevada_natural_gas_marketed_production",
                "new_mexico_natural_gas_marketed_production",
                "new_york_natural_gas_marketed_production",
                "north_dakota_natural_gas_marketed_production",
                "ohio_natural_gas_marketed_production",
                "oklahoma_natural_gas_marketed_production",
                "oregon_natural_gas_marketed_production",
                "pennsylvania_natural_gas_marketed_production",
                "south_dakota_natural_gas_marketed_production",
                "tennessee_natural_gas_marketed_production",
                "texas_natural_gas_marketed_production",
                "us_natural_gas_marketed_production",
                "us_natural_gas_wellhead_price",
                "utah_natural_gas_marketed_production",
                "virginia_natural_gas_marketed_production",
                "west_virginia_natural_gas_marketed_production",
                "wyoming_natural_gas_marketed_production",
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
    region: str | None = Field(
        default=None,
        description="DuoArea filter. Accepts a comma-separated list of values.",
    )
    series: str | None = Field(
        default=None,
        description="Series filter. Accepts a comma-separated list of values.",
    )


class EiaNaturalGasNaturalGasWellheadValueAndMarketedProductionData(EiaApiData):
    """Natural Gas Wellhead Value and Marketed Production. EIA natural gas survey data"""

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


class EiaNaturalGasNaturalGasWellheadValueAndMarketedProductionFetcher(
    Fetcher[
        EiaNaturalGasNaturalGasWellheadValueAndMarketedProductionQueryParams,
        list[EiaNaturalGasNaturalGasWellheadValueAndMarketedProductionData],
    ]
):
    """Natural Gas Wellhead Value and Marketed Production fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> EiaNaturalGasNaturalGasWellheadValueAndMarketedProductionQueryParams:
        """Transform the query parameters."""
        return transform_dataset_query(
            EiaNaturalGasNaturalGasWellheadValueAndMarketedProductionQueryParams, params
        )

    @staticmethod
    async def aextract_data(
        query: EiaNaturalGasNaturalGasWellheadValueAndMarketedProductionQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract the data from the EIA API."""
        return await extract_dataset_data(query, credentials)

    @staticmethod
    def transform_data(
        query: EiaNaturalGasNaturalGasWellheadValueAndMarketedProductionQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> list[EiaNaturalGasNaturalGasWellheadValueAndMarketedProductionData]:
        """Transform the data."""
        return transform_dataset_data(
            EiaNaturalGasNaturalGasWellheadValueAndMarketedProductionData, query, data
        )
