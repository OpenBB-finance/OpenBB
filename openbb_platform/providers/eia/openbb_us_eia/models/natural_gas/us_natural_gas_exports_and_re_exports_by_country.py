"""US Natural Gas Exports and Re-Exports by Country model."""

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


class EiaNaturalGasUsNaturalGasExportsAndReExportsByCountryQueryParams(
    EiaApiQueryParams
):
    """US Natural Gas Exports and Re-Exports by Country. EIA natural gas survey data

    Source: https://www.eia.gov/opendata/browser/natural-gas/move/expc
    """

    __group__ = "natural_gas"
    __dataset__ = "us_natural_gas_exports_and_re_exports_by_country"
    __json_schema_extra__ = {
        "process": {
            "multiple_items_allowed": True,
            "choices": [
                "compressed_natural_gas_exports",
                "compressed_natural_gas_exports_for_price",
                "exports",
                "exports_price",
                "exports_by_truck",
                "exports_by_vessel",
                "exports_by_vessel_and_truck",
                "liquefied_natural_gas_exports",
                "liquefied_natural_gas_exports_price",
                "pipeline_exports",
                "pipeline_exports_price",
                "re_exports",
            ],
        },
        "region": {
            "multiple_items_allowed": True,
            "choices": [
                "are",
                "arg",
                "atg",
                "bel",
                "bgd",
                "bhr",
                "bhs",
                "bra",
                "brb",
                "can",
                "chl",
                "chn",
                "col",
                "deu",
                "dom",
                "egy",
                "esp",
                "fra",
                "gbr",
                "grc",
                "hrv",
                "hti",
                "idn",
                "ind",
                "isr",
                "ita",
                "jam",
                "jor",
                "jpn",
                "kor",
                "kwt",
                "ltu",
                "mex",
                "mrt",
                "mys",
                "na",
                "nic",
                "nld",
                "pak",
                "pan",
                "phl",
                "pol",
                "prt",
                "rus",
                "sen",
                "sgp",
                "slv",
                "tha",
                "tur",
                "twn",
                "us",
            ],
        },
        "series": {"multiple_items_allowed": True},
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
        description="Series filter. Accepts a comma-separated list of values. There are 154 valid values - use the `facet_options` endpoint to list them.",
    )


class EiaNaturalGasUsNaturalGasExportsAndReExportsByCountryData(EiaApiData):
    """US Natural Gas Exports and Re-Exports by Country. EIA natural gas survey data"""

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


class EiaNaturalGasUsNaturalGasExportsAndReExportsByCountryFetcher(
    Fetcher[
        EiaNaturalGasUsNaturalGasExportsAndReExportsByCountryQueryParams,
        list[EiaNaturalGasUsNaturalGasExportsAndReExportsByCountryData],
    ]
):
    """US Natural Gas Exports and Re-Exports by Country fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> EiaNaturalGasUsNaturalGasExportsAndReExportsByCountryQueryParams:
        """Transform the query parameters."""
        return transform_dataset_query(
            EiaNaturalGasUsNaturalGasExportsAndReExportsByCountryQueryParams, params
        )

    @staticmethod
    async def aextract_data(
        query: EiaNaturalGasUsNaturalGasExportsAndReExportsByCountryQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract the data from the EIA API."""
        return await extract_dataset_data(query, credentials)

    @staticmethod
    def transform_data(
        query: EiaNaturalGasUsNaturalGasExportsAndReExportsByCountryQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> list[EiaNaturalGasUsNaturalGasExportsAndReExportsByCountryData]:
        """Transform the data."""
        return transform_dataset_data(
            EiaNaturalGasUsNaturalGasExportsAndReExportsByCountryData, query, data
        )
