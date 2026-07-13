"""Natural Gas Gross Withdrawals and Production model."""

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


class EiaNaturalGasNaturalGasGrossWithdrawalsAndProductionQueryParams(
    EiaApiQueryParams
):
    """Natural Gas Gross Withdrawals and Production. EIA natural gas survey data

    Source: https://www.eia.gov/opendata/browser/natural-gas/prod/sum
    """

    __group__ = "natural_gas"
    __dataset__ = "natural_gas_gross_withdrawals_and_production"
    __json_schema_extra__ = {
        "process": {
            "multiple_items_allowed": True,
            "choices": [
                "dry_production",
                "extraction_loss",
                "gross_withdrawals",
                "marketed_production",
                "removed_from_natural_gas",
                "repressuring",
                "vented_and_flared",
                "withdrawals_from_coalbed_wells",
                "withdrawals_from_gas_wells",
                "withdrawals_from_oil_wells",
                "withdrawals_from_shale_gas",
            ],
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
        description="Series filter. Accepts a comma-separated list of values. There are 434 valid values - use the `facet_options` endpoint to list them.",
    )


class EiaNaturalGasNaturalGasGrossWithdrawalsAndProductionData(EiaApiData):
    """Natural Gas Gross Withdrawals and Production. EIA natural gas survey data"""

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


class EiaNaturalGasNaturalGasGrossWithdrawalsAndProductionFetcher(
    Fetcher[
        EiaNaturalGasNaturalGasGrossWithdrawalsAndProductionQueryParams,
        list[EiaNaturalGasNaturalGasGrossWithdrawalsAndProductionData],
    ]
):
    """Natural Gas Gross Withdrawals and Production fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> EiaNaturalGasNaturalGasGrossWithdrawalsAndProductionQueryParams:
        """Transform the query parameters."""
        return transform_dataset_query(
            EiaNaturalGasNaturalGasGrossWithdrawalsAndProductionQueryParams, params
        )

    @staticmethod
    async def aextract_data(
        query: EiaNaturalGasNaturalGasGrossWithdrawalsAndProductionQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract the data from the EIA API."""
        return await extract_dataset_data(query, credentials)

    @staticmethod
    def transform_data(
        query: EiaNaturalGasNaturalGasGrossWithdrawalsAndProductionQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> list[EiaNaturalGasNaturalGasGrossWithdrawalsAndProductionData]:
        """Transform the data."""
        return transform_dataset_data(
            EiaNaturalGasNaturalGasGrossWithdrawalsAndProductionData, query, data
        )
