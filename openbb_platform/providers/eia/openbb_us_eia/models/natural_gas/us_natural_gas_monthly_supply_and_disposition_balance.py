"""US Natural Gas Monthly Supply and Disposition Balance model."""

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


class EiaNaturalGasUsNaturalGasMonthlySupplyAndDispositionBalanceQueryParams(
    EiaApiQueryParams
):
    """US Natural Gas Monthly Supply and Disposition Balance. EIA natural gas survey data

    Source: https://www.eia.gov/opendata/browser/natural-gas/sum/sndm
    """

    __group__ = "natural_gas"
    __dataset__ = "us_natural_gas_monthly_supply_and_disposition_balance"
    __json_schema_extra__ = {
        "process": {
            "multiple_items_allowed": True,
            "choices": [
                "balancing_item",
                "dry_production",
                "extraction_loss",
                "gross_withdrawals",
                "input_supplemental_fuels",
                "marketed_production",
                "net_imports",
                "net_withdrawals_from_storage",
                "total_consumption",
            ],
        },
        "region": {"multiple_items_allowed": True, "choices": ["us"]},
        "series": {
            "multiple_items_allowed": True,
            "choices": [
                "balancing_item",
                "us_dry_natural_gas_production",
                "us_natural_gas_gross_withdrawals",
                "us_natural_gas_marketed_production",
                "us_natural_gas_net_imports",
                "us_natural_gas_net_withdrawals_from_storage",
                "us_natural_gas_plant_liquids_production_gaseous_equivalent",
                "us_natural_gas_total_consumption",
                "us_supplemental_gaseous_fuels",
            ],
        },
    }

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


class EiaNaturalGasUsNaturalGasMonthlySupplyAndDispositionBalanceData(EiaApiData):
    """US Natural Gas Monthly Supply and Disposition Balance. EIA natural gas survey data"""

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


class EiaNaturalGasUsNaturalGasMonthlySupplyAndDispositionBalanceFetcher(
    Fetcher[
        EiaNaturalGasUsNaturalGasMonthlySupplyAndDispositionBalanceQueryParams,
        list[EiaNaturalGasUsNaturalGasMonthlySupplyAndDispositionBalanceData],
    ]
):
    """US Natural Gas Monthly Supply and Disposition Balance fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> EiaNaturalGasUsNaturalGasMonthlySupplyAndDispositionBalanceQueryParams:
        """Transform the query parameters."""
        return transform_dataset_query(
            EiaNaturalGasUsNaturalGasMonthlySupplyAndDispositionBalanceQueryParams,
            params,
        )

    @staticmethod
    async def aextract_data(
        query: EiaNaturalGasUsNaturalGasMonthlySupplyAndDispositionBalanceQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract the data from the EIA API."""
        return await extract_dataset_data(query, credentials)

    @staticmethod
    def transform_data(
        query: EiaNaturalGasUsNaturalGasMonthlySupplyAndDispositionBalanceQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> list[EiaNaturalGasUsNaturalGasMonthlySupplyAndDispositionBalanceData]:
        """Transform the data."""
        return transform_dataset_data(
            EiaNaturalGasUsNaturalGasMonthlySupplyAndDispositionBalanceData, query, data
        )
