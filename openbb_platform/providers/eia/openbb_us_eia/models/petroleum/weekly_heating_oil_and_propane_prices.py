"""Weekly Heating Oil and Propane Prices model."""

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


class EiaPetroleumWeeklyHeatingOilAndPropanePricesQueryParams(EiaApiQueryParams):
    """Weekly Heating Oil and Propane Prices. EIA petroleum gas survey data

    Source: https://www.eia.gov/opendata/browser/petroleum/pri/wfr
    """

    __group__ = "petroleum"
    __dataset__ = "weekly_heating_oil_and_propane_prices"
    __json_schema_extra__ = {
        "process": {
            "multiple_items_allowed": True,
            "choices": [
                "price_delivered_to_residential_consumers",
                "wholesale_resale_price",
            ],
        },
        "product": {
            "multiple_items_allowed": True,
            "choices": ["no_2_fuel_oil_heating_oil", "propane"],
        },
        "region": {
            "multiple_items_allowed": True,
            "choices": [
                "colorado",
                "florida",
                "massachusetts",
                "minnesota",
                "new_york",
                "ohio",
                "padd_1",
                "padd_1a",
                "padd_1b",
                "padd_1c",
                "padd_2",
                "padd_3",
                "padd_4",
                "texas",
                "us",
                "usa_al",
                "usa_ar",
                "usa_ct",
                "usa_dc",
                "usa_de",
                "usa_ga",
                "usa_ia",
                "usa_id",
                "usa_il",
                "usa_in",
                "usa_ks",
                "usa_ky",
                "usa_md",
                "usa_me",
                "usa_mi",
                "usa_mo",
                "usa_ms",
                "usa_mt",
                "usa_nc",
                "usa_nd",
                "usa_ne",
                "usa_nh",
                "usa_nj",
                "usa_ok",
                "usa_pa",
                "usa_ri",
                "usa_sd",
                "usa_tn",
                "usa_ut",
                "usa_va",
                "usa_vt",
                "usa_wi",
            ],
        },
        "series": {"multiple_items_allowed": True},
    }

    frequency: Literal["monthly", "weekly"] | None = Field(
        default=None,
        description="The data frequency. The default is 'weekly'.",
    )
    process: str | None = Field(
        default=None,
        description="Process filter. Accepts a comma-separated list of values.",
    )
    product: str | None = Field(
        default=None,
        description="Product filter. Accepts a comma-separated list of values.",
    )
    region: str | None = Field(
        default=None,
        description="DuoArea filter. Accepts a comma-separated list of values.",
    )
    series: str | None = Field(
        default=None,
        description="Series filter. Accepts a comma-separated list of values. There are 141 valid values - use the `facet_options` endpoint to list them.",
    )


class EiaPetroleumWeeklyHeatingOilAndPropanePricesData(EiaApiData):
    """Weekly Heating Oil and Propane Prices. EIA petroleum gas survey data"""

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


class EiaPetroleumWeeklyHeatingOilAndPropanePricesFetcher(
    Fetcher[
        EiaPetroleumWeeklyHeatingOilAndPropanePricesQueryParams,
        list[EiaPetroleumWeeklyHeatingOilAndPropanePricesData],
    ]
):
    """Weekly Heating Oil and Propane Prices fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> EiaPetroleumWeeklyHeatingOilAndPropanePricesQueryParams:
        """Transform the query parameters."""
        return transform_dataset_query(
            EiaPetroleumWeeklyHeatingOilAndPropanePricesQueryParams, params
        )

    @staticmethod
    async def aextract_data(
        query: EiaPetroleumWeeklyHeatingOilAndPropanePricesQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract the data from the EIA API."""
        return await extract_dataset_data(query, credentials)

    @staticmethod
    def transform_data(
        query: EiaPetroleumWeeklyHeatingOilAndPropanePricesQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> list[EiaPetroleumWeeklyHeatingOilAndPropanePricesData]:
        """Transform the data."""
        return transform_dataset_data(
            EiaPetroleumWeeklyHeatingOilAndPropanePricesData, query, data
        )
