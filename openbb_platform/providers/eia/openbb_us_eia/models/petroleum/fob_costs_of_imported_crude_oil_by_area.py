"""FOB Costs of Imported Crude Oil by Area model."""

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


class EiaPetroleumFobCostsOfImportedCrudeOilByAreaQueryParams(EiaApiQueryParams):
    """FOB Costs of Imported Crude Oil by Area. EIA petroleum gas survey data

    Source: https://www.eia.gov/opendata/browser/petroleum/pri/imc1
    """

    __group__ = "petroleum"
    __dataset__ = "fob_costs_of_imported_crude_oil_by_area"
    __json_schema_extra__ = {
        "region": {
            "multiple_items_allowed": True,
            "choices": ["ago", "col", "gbr", "mex", "na", "nga", "sau", "ven"],
        },
        "series": {
            "multiple_items_allowed": True,
            "choices": [
                "us_fob_costs_of_angola_crude_oil",
                "us_fob_costs_of_colombia_crude_oil",
                "us_fob_costs_of_crude_oil",
                "us_fob_costs_of_mexico_crude_oil",
                "us_fob_costs_of_nigeria_crude_oil",
                "us_fob_costs_of_non_opec_countries_crude_oil",
                "us_fob_costs_of_opec_countries_crude_oil",
                "us_fob_costs_of_persian_gulf_countries_crude_oil",
                "us_fob_costs_of_saudi_arabia_crude_oil",
                "us_fob_costs_of_united_kingdom_crude_oil",
                "us_fob_costs_of_venezuela_crude_oil",
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


class EiaPetroleumFobCostsOfImportedCrudeOilByAreaData(EiaApiData):
    """FOB Costs of Imported Crude Oil by Area. EIA petroleum gas survey data"""

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


class EiaPetroleumFobCostsOfImportedCrudeOilByAreaFetcher(
    Fetcher[
        EiaPetroleumFobCostsOfImportedCrudeOilByAreaQueryParams,
        list[EiaPetroleumFobCostsOfImportedCrudeOilByAreaData],
    ]
):
    """FOB Costs of Imported Crude Oil by Area fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> EiaPetroleumFobCostsOfImportedCrudeOilByAreaQueryParams:
        """Transform the query parameters."""
        return transform_dataset_query(
            EiaPetroleumFobCostsOfImportedCrudeOilByAreaQueryParams, params
        )

    @staticmethod
    async def aextract_data(
        query: EiaPetroleumFobCostsOfImportedCrudeOilByAreaQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract the data from the EIA API."""
        return await extract_dataset_data(query, credentials)

    @staticmethod
    def transform_data(
        query: EiaPetroleumFobCostsOfImportedCrudeOilByAreaQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> list[EiaPetroleumFobCostsOfImportedCrudeOilByAreaData]:
        """Transform the data."""
        return transform_dataset_data(
            EiaPetroleumFobCostsOfImportedCrudeOilByAreaData, query, data
        )
