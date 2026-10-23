"""Offshore Gross Withdrawals of Natural Gas model."""

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


class EiaNaturalGasOffshoreGrossWithdrawalsOfNaturalGasQueryParams(EiaApiQueryParams):
    """Offshore Gross Withdrawals of Natural Gas. EIA natural gas survey data

    Source: https://www.eia.gov/opendata/browser/natural-gas/prod/off
    """

    __group__ = "natural_gas"
    __dataset__ = "offshore_gross_withdrawals_of_natural_gas"
    __json_schema_extra__ = {
        "process": {
            "multiple_items_allowed": True,
            "choices": [
                "gross_withdrawals",
                "withdrawals_from_gas_wells",
                "withdrawals_from_oil_wells",
            ],
        },
        "series": {
            "multiple_items_allowed": True,
            "choices": [
                "federal_offshore_gulf_of_america_natural_gas_gross_withdrawals_mmcf",
                "federal_offshore_gulf_of_america_natural_gas_gross_withdrawals_from_gas_wells_mmcf",
                "federal_offshore_gulf_of_america_natural_gas_gross_withdrawals_from_oil_wells_mmcf",
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
    series: str | None = Field(
        default=None,
        description="Series filter. Accepts a comma-separated list of values.",
    )


class EiaNaturalGasOffshoreGrossWithdrawalsOfNaturalGasData(EiaApiData):
    """Offshore Gross Withdrawals of Natural Gas. EIA natural gas survey data"""

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


class EiaNaturalGasOffshoreGrossWithdrawalsOfNaturalGasFetcher(
    Fetcher[
        EiaNaturalGasOffshoreGrossWithdrawalsOfNaturalGasQueryParams,
        list[EiaNaturalGasOffshoreGrossWithdrawalsOfNaturalGasData],
    ]
):
    """Offshore Gross Withdrawals of Natural Gas fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> EiaNaturalGasOffshoreGrossWithdrawalsOfNaturalGasQueryParams:
        """Transform the query parameters."""
        return transform_dataset_query(
            EiaNaturalGasOffshoreGrossWithdrawalsOfNaturalGasQueryParams, params
        )

    @staticmethod
    async def aextract_data(
        query: EiaNaturalGasOffshoreGrossWithdrawalsOfNaturalGasQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract the data from the EIA API."""
        return await extract_dataset_data(query, credentials)

    @staticmethod
    def transform_data(
        query: EiaNaturalGasOffshoreGrossWithdrawalsOfNaturalGasQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> list[EiaNaturalGasOffshoreGrossWithdrawalsOfNaturalGasData]:
        """Transform the data."""
        return transform_dataset_data(
            EiaNaturalGasOffshoreGrossWithdrawalsOfNaturalGasData, query, data
        )
