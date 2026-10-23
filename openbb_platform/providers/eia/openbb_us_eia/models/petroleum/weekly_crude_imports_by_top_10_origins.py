"""Weekly Preliminary Crude Imports by Top 10 Countries of Origin (ranking based on 2024 Petroleum Supply Monthly data) model."""

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


class EiaPetroleumWeeklyCrudeImportsByTop10OriginsQueryParams(EiaApiQueryParams):
    """Weekly Preliminary Crude Imports by Top 10 Countries of Origin (ranking based on 2024 Petroleum Supply Monthly data). EIA petroleum gas survey data

    Source: https://www.eia.gov/opendata/browser/petroleum/move/wimpc
    """

    __group__ = "petroleum"
    __dataset__ = "weekly_crude_imports_by_top_10_origins"
    __json_schema_extra__ = {
        "region": {
            "multiple_items_allowed": True,
            "choices": [
                "ago",
                "bra",
                "can",
                "cog",
                "col",
                "dza",
                "ecu",
                "gbr",
                "gnq",
                "irq",
                "kwt",
                "lby",
                "mex",
                "nga",
                "nor",
                "rus",
                "sau",
                "tto",
                "ven",
            ],
        },
        "series": {
            "multiple_items_allowed": True,
            "choices": [
                "us_imports_from_algeria_of_crude_oil",
                "us_imports_from_angola_of_crude_oil",
                "us_imports_from_brazil_of_crude_oil",
                "us_imports_from_canada_of_crude_oil",
                "us_imports_from_colombia_of_crude_oil",
                "us_imports_from_congo_of_crude_oil",
                "us_imports_from_ecuador_of_crude_oil",
                "us_imports_from_equatorial_guinea_of_crude_oil",
                "us_imports_from_iraq_of_crude_oil",
                "us_imports_from_kuwait_of_crude_oil",
                "us_imports_from_libya_of_crude_oil",
                "us_imports_from_mexico_of_crude_oil",
                "us_imports_from_nigeria_of_crude_oil",
                "us_imports_from_norway_of_crude_oil",
                "us_imports_from_russia_of_crude_oil",
                "us_imports_from_saudi_arabia_of_crude_oil",
                "us_imports_from_trinidad_and_tobago_of_crude_oil",
                "us_imports_from_united_kingdom_of_crude_oil",
                "us_imports_from_venezuela_of_crude_oil",
            ],
        },
    }

    frequency: Literal["four-week-average", "weekly"] | None = Field(
        default=None,
        description="The data frequency. The default is 'weekly'.",
    )
    region: str | None = Field(
        default=None,
        description="DuoArea filter. Accepts a comma-separated list of values.",
    )
    series: str | None = Field(
        default=None,
        description="Series filter. Accepts a comma-separated list of values.",
    )


class EiaPetroleumWeeklyCrudeImportsByTop10OriginsData(EiaApiData):
    """Weekly Preliminary Crude Imports by Top 10 Countries of Origin (ranking based on 2024 Petroleum Supply Monthly data). EIA petroleum gas survey data"""

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


class EiaPetroleumWeeklyCrudeImportsByTop10OriginsFetcher(
    Fetcher[
        EiaPetroleumWeeklyCrudeImportsByTop10OriginsQueryParams,
        list[EiaPetroleumWeeklyCrudeImportsByTop10OriginsData],
    ]
):
    """Weekly Preliminary Crude Imports by Top 10 Countries of Origin (ranking based on 2024 Petroleum Supply Monthly data) fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> EiaPetroleumWeeklyCrudeImportsByTop10OriginsQueryParams:
        """Transform the query parameters."""
        return transform_dataset_query(
            EiaPetroleumWeeklyCrudeImportsByTop10OriginsQueryParams, params
        )

    @staticmethod
    async def aextract_data(
        query: EiaPetroleumWeeklyCrudeImportsByTop10OriginsQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract the data from the EIA API."""
        return await extract_dataset_data(query, credentials)

    @staticmethod
    def transform_data(
        query: EiaPetroleumWeeklyCrudeImportsByTop10OriginsQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> list[EiaPetroleumWeeklyCrudeImportsByTop10OriginsData]:
        """Transform the data."""
        return transform_dataset_data(
            EiaPetroleumWeeklyCrudeImportsByTop10OriginsData, query, data
        )
