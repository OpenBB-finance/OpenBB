"""Total Energy model."""

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


class EiaTotalEnergyQueryParams(EiaApiQueryParams):
    """Total Energy. These data represent the most recent comprehensive energy statistics integrated across all energy sources. The data includes total energy production, consumption, stocks, and trade; energy prices; overviews of petroleum, natural gas, coal, electricity, nuclear energy, renewable energy, and carbon dioxide emissions; and data unit conversions values. Source: https://www.eia.gov/totalenergy/data/monthly/pdf/mer_a_doc.pdf Report: MER (https://www.eia.gov/totalenergy/data/monthly/)

    Source: https://www.eia.gov/opendata/browser/total-energy
    """

    __group__ = "total_energy"
    __dataset__ = "total_energy"
    __json_schema_extra__ = {
        "msn": {"multiple_items_allowed": True},
    }

    frequency: Literal["annual", "monthly"] | None = Field(
        default=None,
        description="The data frequency. The default is 'monthly'.",
    )
    msn: str | None = Field(
        default=None,
        description="Unique series identifier filter. Accepts a comma-separated list of values. There are 984 valid values - use the `facet_options` endpoint to list them.",
    )


class EiaTotalEnergyData(EiaApiData):
    """Total Energy. These data represent the most recent comprehensive energy statistics integrated across all energy sources. The data includes total energy production, consumption, stocks, and trade; energy prices; overviews of petroleum, natural gas, coal, electricity, nuclear energy, renewable energy, and carbon dioxide emissions; and data unit conversions values. Source: https://www.eia.gov/totalenergy/data/monthly/pdf/mer_a_doc.pdf Report: MER (https://www.eia.gov/totalenergy/data/monthly/)"""

    msn: str | None = Field(
        default=None,
        description="Unique series identifier code.",
    )
    msn_name: str | None = Field(
        default=None,
        description="Unique series identifier name.",
    )
    value: float | None = Field(
        default=None,
        description="Value. Withheld or unavailable values return as null.",
    )
    unit: str | None = Field(
        default=None,
        description="Unit of the value.",
    )


class EiaTotalEnergyFetcher(
    Fetcher[EiaTotalEnergyQueryParams, list[EiaTotalEnergyData]]
):
    """Total Energy fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> EiaTotalEnergyQueryParams:
        """Transform the query parameters."""
        return transform_dataset_query(EiaTotalEnergyQueryParams, params)

    @staticmethod
    async def aextract_data(
        query: EiaTotalEnergyQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract the data from the EIA API."""
        return await extract_dataset_data(query, credentials)

    @staticmethod
    def transform_data(
        query: EiaTotalEnergyQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> list[EiaTotalEnergyData]:
        """Transform the data."""
        return transform_dataset_data(EiaTotalEnergyData, query, data)
