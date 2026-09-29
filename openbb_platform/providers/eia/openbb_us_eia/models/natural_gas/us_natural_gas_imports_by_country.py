"""US Natural Gas Imports by Country model."""

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


class EiaNaturalGasUsNaturalGasImportsByCountryQueryParams(EiaApiQueryParams):
    """US Natural Gas Imports by Country. EIA natural gas survey data

    Source: https://www.eia.gov/opendata/browser/natural-gas/move/impc
    """

    __group__ = "natural_gas"
    __dataset__ = "us_natural_gas_imports_by_country"
    __json_schema_extra__ = {
        "process": {
            "multiple_items_allowed": True,
            "choices": [
                "compressed_natural_gas_imports",
                "compressed_natural_gas_imports_for_price",
                "imports",
                "imports_price",
                "lng_imports",
                "liquefied_natural_gas_imports",
                "pipeline_imports",
                "pipeline_imports_price",
            ],
        },
        "region": {
            "multiple_items_allowed": True,
            "choices": [
                "are",
                "aus",
                "brn",
                "can",
                "dza",
                "egy",
                "fra",
                "gbr",
                "gnq",
                "idn",
                "jam",
                "mex",
                "mys",
                "na",
                "nga",
                "nor",
                "omn",
                "per",
                "qat",
                "tto",
                "us",
                "yem",
            ],
        },
        "series": {
            "multiple_items_allowed": True,
            "choices": [
                "compressed_us_natural_gas_imports",
                "compressed_us_natural_gas_imports_from_canada",
                "price_of_compressed_us_natural_gas_imports",
                "price_of_compressed_us_natural_gas_imports_from_canada",
                "price_of_us_liquefied_natural_gas_imports_from_algeria",
                "price_of_us_liquefied_natural_gas_imports_from_australia",
                "price_of_us_liquefied_natural_gas_imports_from_brunei",
                "price_of_us_liquefied_natural_gas_imports_from_canada",
                "price_of_us_liquefied_natural_gas_imports_from_egypt",
                "price_of_us_liquefied_natural_gas_imports_from_equatorial",
                "price_of_us_liquefied_natural_gas_imports_from_france",
                "price_of_us_liquefied_natural_gas_imports_from_indonesia",
                "price_of_us_liquefied_natural_gas_imports_from_malaysia",
                "price_of_us_liquefied_natural_gas_imports_from_nigeria",
                "price_of_us_liquefied_natural_gas_imports_from_norway",
                "price_of_us_liquefied_natural_gas_imports_from_oman",
                "price_of_us_liquefied_natural_gas_imports_from_other",
                "price_of_us_liquefied_natural_gas_imports_from_peru",
                "price_of_us_liquefied_natural_gas_imports_from_qatar",
                "price_of_us_liquefied_natural_gas_imports_from_the_united",
                "price_of_us_liquefied_natural_gas_imports_from_trinidad_and",
                "price_of_us_liquefied_natural_gas_imports_from_united",
                "price_of_us_liquefied_natural_gas_imports_from_yemen",
                "price_of_us_liquefied_natural_gas_imports_from_jamaica",
                "price_of_us_natural_gas_imports",
                "price_of_us_natural_gas_lng_imports",
                "price_of_us_natural_gas_pipeline_imports_from_canada",
                "price_of_us_natural_gas_pipeline_imports_from_mexico",
                "us_liquefied_natural_gas_imports",
                "us_liquefied_natural_gas_imports_from_algeria",
                "us_liquefied_natural_gas_imports_from_australia",
                "us_liquefied_natural_gas_imports_from_brunei",
                "us_liquefied_natural_gas_imports_from_canada",
                "us_liquefied_natural_gas_imports_from_egypt",
                "us_liquefied_natural_gas_imports_from_equatorial_guinea",
                "us_liquefied_natural_gas_imports_from_france",
                "us_liquefied_natural_gas_imports_from_indonesia",
                "us_liquefied_natural_gas_imports_from_malaysia",
                "us_liquefied_natural_gas_imports_from_nigeria",
                "us_liquefied_natural_gas_imports_from_norway",
                "us_liquefied_natural_gas_imports_from_oman",
                "us_liquefied_natural_gas_imports_from_other_countries",
                "us_liquefied_natural_gas_imports_from_peru",
                "us_liquefied_natural_gas_imports_from_qatar",
                "us_liquefied_natural_gas_imports_from_the_united_arab",
                "us_liquefied_natural_gas_imports_from_trinidad_and_tobago",
                "us_liquefied_natural_gas_imports_from_united_kingdom",
                "us_liquefied_natural_gas_imports_from_yemen",
                "us_liquefied_natural_gas_imports_from_jamaica",
                "us_natural_gas_imports",
                "us_natural_gas_pipeline_imports",
                "us_natural_gas_pipeline_imports_from_canada",
                "us_natural_gas_pipeline_imports_from_mexico",
                "us_natural_gas_pipeline_imports_price",
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


class EiaNaturalGasUsNaturalGasImportsByCountryData(EiaApiData):
    """US Natural Gas Imports by Country. EIA natural gas survey data"""

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


class EiaNaturalGasUsNaturalGasImportsByCountryFetcher(
    Fetcher[
        EiaNaturalGasUsNaturalGasImportsByCountryQueryParams,
        list[EiaNaturalGasUsNaturalGasImportsByCountryData],
    ]
):
    """US Natural Gas Imports by Country fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> EiaNaturalGasUsNaturalGasImportsByCountryQueryParams:
        """Transform the query parameters."""
        return transform_dataset_query(
            EiaNaturalGasUsNaturalGasImportsByCountryQueryParams, params
        )

    @staticmethod
    async def aextract_data(
        query: EiaNaturalGasUsNaturalGasImportsByCountryQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract the data from the EIA API."""
        return await extract_dataset_data(query, credentials)

    @staticmethod
    def transform_data(
        query: EiaNaturalGasUsNaturalGasImportsByCountryQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> list[EiaNaturalGasUsNaturalGasImportsByCountryData]:
        """Transform the data."""
        return transform_dataset_data(
            EiaNaturalGasUsNaturalGasImportsByCountryData, query, data
        )
