"""US Crude Oil Supply & Disposition model."""

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


class EiaPetroleumUsCrudeOilSupplyDispositionQueryParams(EiaApiQueryParams):
    """US Crude Oil Supply & Disposition. EIA petroleum gas survey data

    Source: https://www.eia.gov/opendata/browser/petroleum/sum/crdsnd
    """

    __group__ = "petroleum"
    __dataset__ = "us_crude_oil_supply_disposition"
    __json_schema_extra__ = {
        "process": {
            "multiple_items_allowed": True,
            "choices": [
                "days_of_petroleum_net_imports",
                "ending_stocks",
                "ending_stocks_excluding_spr",
                "ending_stocks_spr",
                "exports",
                "field_production",
                "imports",
                "imports_excluding_spr",
                "imports_spr",
                "imports_by_others_for_spr",
                "percent_of_crude_oil_stocks",
                "percent_of_total_petroleum_stocks",
                "product_supplied",
                "refinery_and_blender_net_input",
                "spr_receipts_detail_domestic",
                "spr_receipts_detail_receipts",
                "spr_stock_change",
                "stock_change",
                "stock_change_excluding_spr",
                "stocks_at_leases",
                "stocks_at_refineries",
                "stocks_at_tank_farms",
                "stocks_in_transit_from_alaska",
                "supply_adjustment",
            ],
        },
        "region": {"multiple_items_allowed": True, "choices": ["na", "us", "usa_ak"]},
        "series": {
            "multiple_items_allowed": True,
            "choices": [
                "alaska_field_production_of_crude_oil",
                "cushing_ok_ending_stocks_of_crude_oil",
                "lower_48_states_field_production_of_crude_oil",
                "us_crude_oil_imports_excluding_spr",
                "us_crude_oil_imports_for_spr_by_others_from_all_countries",
                "us_crude_oil_spr_imports_from_all_countries",
                "us_crude_oil_spr_stock_change",
                "us_crude_oil_stock_change",
                "us_crude_oil_stock_change_excluding_spr",
                "us_crude_oil_stocks_at_leases",
                "us_crude_oil_stocks_at_refineries",
                "us_crude_oil_stocks_at_tank_farms_and_pipelines",
                "us_crude_oil_stocks_in_transit_from_alaska",
                "us_crude_oil_spr_receipts_detail_domestic",
                "us_crude_oil_spr_receipts_detail_receipts",
                "us_ending_stocks_excluding_spr_of_crude_oil",
                "us_ending_stocks_of_crude_oil",
                "us_ending_stocks_of_crude_oil_in_spr",
                "us_exports_of_crude_oil",
                "us_field_production_of_crude_oil",
                "us_imports_of_crude_oil",
                "us_percent_of_crude_oil_stocks_held_in_spr",
                "us_percent_of_total_petroleum_stocks_held_in_spr",
                "us_product_supplied_of_crude_oil",
                "us_refinery_and_blender_net_input_of_crude_oil",
                "us_spr_stocks_as_days_of_supply_of_total_petroleum_net",
                "us_supply_adjustment_of_crude_oil",
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


class EiaPetroleumUsCrudeOilSupplyDispositionData(EiaApiData):
    """US Crude Oil Supply & Disposition. EIA petroleum gas survey data"""

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


class EiaPetroleumUsCrudeOilSupplyDispositionFetcher(
    Fetcher[
        EiaPetroleumUsCrudeOilSupplyDispositionQueryParams,
        list[EiaPetroleumUsCrudeOilSupplyDispositionData],
    ]
):
    """US Crude Oil Supply & Disposition fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> EiaPetroleumUsCrudeOilSupplyDispositionQueryParams:
        """Transform the query parameters."""
        return transform_dataset_query(
            EiaPetroleumUsCrudeOilSupplyDispositionQueryParams, params
        )

    @staticmethod
    async def aextract_data(
        query: EiaPetroleumUsCrudeOilSupplyDispositionQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract the data from the EIA API."""
        return await extract_dataset_data(query, credentials)

    @staticmethod
    def transform_data(
        query: EiaPetroleumUsCrudeOilSupplyDispositionQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> list[EiaPetroleumUsCrudeOilSupplyDispositionData]:
        """Transform the data."""
        return transform_dataset_data(
            EiaPetroleumUsCrudeOilSupplyDispositionData, query, data
        )
