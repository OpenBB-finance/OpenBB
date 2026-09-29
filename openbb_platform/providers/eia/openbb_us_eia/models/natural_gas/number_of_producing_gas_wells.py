"""Number of Producing Gas Wells model."""

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


class EiaNaturalGasNumberOfProducingGasWellsQueryParams(EiaApiQueryParams):
    """Number of Producing Gas Wells. EIA natural gas survey data

    Source: https://www.eia.gov/opendata/browser/natural-gas/prod/wells
    """

    __group__ = "natural_gas"
    __dataset__ = "number_of_producing_gas_wells"
    __json_schema_extra__ = {
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
                "alabama_natural_gas_number_of_gas_and_gas_condensate_wells",
                "alaska_natural_gas_number_of_gas_and_gas_condensate_wells",
                "arizona_natural_gas_number_of_gas_and_gas_condensate_wells",
                "arkansas_natural_gas_number_of_gas_and_gas_condensate_wells",
                "california_natural_gas_number_of_gas_and_gas_condensate",
                "colorado_natural_gas_number_of_gas_and_gas_condensate_wells",
                "federal_offshore_gulf_of_america_natural_gas_number_of_gas",
                "florida_natural_gas_number_of_gas_and_gas_condensate_wells",
                "idaho_number_of_gas_and_gas_condensate_wells_of_natural_gas",
                "illinois_natural_gas_number_of_gas_and_gas_condensate_wells",
                "indiana_natural_gas_number_of_gas_and_gas_condensate_wells",
                "kansas_natural_gas_number_of_gas_and_gas_condensate_wells",
                "kentucky_natural_gas_number_of_gas_and_gas_condensate_wells",
                "louisiana_natural_gas_number_of_gas_and_gas_condensate_wells",
                "maryland_natural_gas_number_of_gas_and_gas_condensate_wells",
                "michigan_natural_gas_number_of_gas_and_gas_condensate_wells",
                "mississippi_natural_gas_number_of_gas_and_gas_condensate",
                "missouri_natural_gas_number_of_gas_and_gas_condensate_wells",
                "montana_natural_gas_number_of_gas_and_gas_condensate_wells",
                "nebraska_natural_gas_number_of_gas_and_gas_condensate_wells",
                "nevada_natural_gas_number_of_gas_and_gas_condensate_wells",
                "new_mexico_natural_gas_number_of_gas_and_gas_condensate",
                "new_york_natural_gas_number_of_gas_and_gas_condensate_wells",
                "north_dakota_natural_gas_number_of_gas_and_gas_condensate",
                "ohio_natural_gas_number_of_gas_and_gas_condensate_wells",
                "oklahoma_natural_gas_number_of_gas_and_gas_condensate_wells",
                "oregon_natural_gas_number_of_gas_and_gas_condensate_wells",
                "pennsylvania_natural_gas_number_of_gas_and_gas_condensate",
                "south_dakota_natural_gas_number_of_gas_and_gas_condensate",
                "tennessee_natural_gas_number_of_gas_and_gas_condensate_wells",
                "texas_natural_gas_number_of_gas_and_gas_condensate_wells",
                "us_natural_gas_number_of_gas_and_gas_condensate_wells",
                "utah_natural_gas_number_of_gas_and_gas_condensate_wells",
                "virginia_natural_gas_number_of_gas_and_gas_condensate_wells",
                "west_virginia_natural_gas_number_of_gas_and_gas_condensate",
                "wyoming_natural_gas_number_of_gas_and_gas_condensate_wells",
            ],
        },
    }

    region: str | None = Field(
        default=None,
        description="DuoArea filter. Accepts a comma-separated list of values.",
    )
    series: str | None = Field(
        default=None,
        description="Series filter. Accepts a comma-separated list of values.",
    )


class EiaNaturalGasNumberOfProducingGasWellsData(EiaApiData):
    """Number of Producing Gas Wells. EIA natural gas survey data"""

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


class EiaNaturalGasNumberOfProducingGasWellsFetcher(
    Fetcher[
        EiaNaturalGasNumberOfProducingGasWellsQueryParams,
        list[EiaNaturalGasNumberOfProducingGasWellsData],
    ]
):
    """Number of Producing Gas Wells fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> EiaNaturalGasNumberOfProducingGasWellsQueryParams:
        """Transform the query parameters."""
        return transform_dataset_query(
            EiaNaturalGasNumberOfProducingGasWellsQueryParams, params
        )

    @staticmethod
    async def aextract_data(
        query: EiaNaturalGasNumberOfProducingGasWellsQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract the data from the EIA API."""
        return await extract_dataset_data(query, credentials)

    @staticmethod
    def transform_data(
        query: EiaNaturalGasNumberOfProducingGasWellsQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> list[EiaNaturalGasNumberOfProducingGasWellsData]:
        """Transform the data."""
        return transform_dataset_data(
            EiaNaturalGasNumberOfProducingGasWellsData, query, data
        )
