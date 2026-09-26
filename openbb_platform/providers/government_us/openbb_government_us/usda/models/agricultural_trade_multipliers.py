"""USDA ERS Agricultural Trade Multipliers Model."""

from typing import Any

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from pydantic import ConfigDict, Field

from openbb_government_us.utils.serializers import NullTokenMixin


class AgriculturalTradeMultipliersQueryParams(QueryParams):
    """USDA ERS Agricultural Trade Multipliers Query Parameters.

    Source: https://www.ers.usda.gov/data-products/agricultural-trade-multipliers
    """


class AgriculturalTradeMultipliersData(NullTokenMixin, Data):
    """USDA ERS Agricultural Trade Multipliers Data.

    One wide row per commodity, with the USDA ERS agricultural trade multiplier
    measures spread across columns: producer- and port-level output and
    employment multipliers and the commodity's export value.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "x-widget_config": {
                "$.name": "USDA ERS Agricultural Trade Multipliers",
                "$.description": "Producer- and port-level output and employment"
                " multipliers estimating the U.S. economic output and jobs"
                " supported by agricultural exports, by commodity, published by"
                " the USDA Economic Research Service.",
                "$.category": "Economy",
                "$.subCategory": "Agriculture",
                "$.source": ["USDA", "ERS"],
            },
        }
    )

    commodity_id: int | None = Field(
        default=None,
        description="Numeric commodity identifier, as published (COMMID)."
        + " None on the aggregate all-exports row.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Commodity ID",
                "cellDataType": "number",
                "hide": True,
                "maxWidth": 120,
            }
        },
    )
    commodity: str = Field(
        description="Commodity name, as published, or the aggregate"
        + " 'All agricultural exports'.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Commodity",
                "cellDataType": "text",
                "pinned": "left",
            }
        },
    )
    year: int = Field(
        description="Reference year of the multipliers and export value.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Year",
                "cellDataType": "number",
                "maxWidth": 90,
            }
        },
    )
    producer_output_multiplier: float | None = Field(
        default=None,
        description="Producer output multiplier: total U.S. dollar economic"
        + " output supported per U.S. dollar of the commodity's export value.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Producer Output Multiplier (USD output per USD export)",
                "cellDataType": "number",
            }
        },
    )
    producer_employment_multiplier: float | None = Field(
        default=None,
        description="Producer employment multiplier: jobs supported per 1"
        + " billion U.S. dollars of the commodity's export value.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Producer Employment Multiplier (jobs per $1B export)",
                "cellDataType": "number",
            }
        },
    )
    port_output_multiplier: float | None = Field(
        default=None,
        description="Port output multiplier: total U.S. dollar economic output"
        + " supported per U.S. dollar of the commodity's export value.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Port Output Multiplier (USD output per USD export)",
                "cellDataType": "number",
            }
        },
    )
    port_employment_multiplier: float | None = Field(
        default=None,
        description="Port employment multiplier: jobs supported per 1 billion"
        + " U.S. dollars of the commodity's export value.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Port Employment Multiplier (jobs per $1B export)",
                "cellDataType": "number",
            }
        },
    )
    export_value: float | None = Field(
        default=None,
        description="Commodity export value, in thousands of U.S. dollars.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Export Value ($1,000)",
                "cellDataType": "number",
            }
        },
    )


class AgriculturalTradeMultipliersFetcher(
    Fetcher[
        AgriculturalTradeMultipliersQueryParams,
        list[AgriculturalTradeMultipliersData],
    ]
):
    """Fetch USDA ERS Agricultural Trade Multipliers."""

    require_credentials = False

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> AgriculturalTradeMultipliersQueryParams:
        """Transform the query params."""
        return AgriculturalTradeMultipliersQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: AgriculturalTradeMultipliersQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Extract the long CSV rows."""
        from openbb_government_us.usda.utils import ers_agricultural_trade_multipliers

        return await ers_agricultural_trade_multipliers.afetch_table()

    @staticmethod
    def transform_data(
        query: AgriculturalTradeMultipliersQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[AgriculturalTradeMultipliersData]:
        """Pivot the long rows into one wide row per commodity."""
        pivoted: dict[tuple, dict] = {}
        for order, record in enumerate(data):
            commodity = record["commodity"]
            key = (record["commodity_id"], commodity, record["year"])
            row = pivoted.get(key)
            if row is None:
                row = {
                    "_order": order,
                    "commodity_id": record["commodity_id"],
                    "commodity": commodity,
                    "year": record["year"],
                }
                pivoted[key] = row
            row[record["field"]] = record["value"]
        results = sorted(pivoted.values(), key=lambda r: r["_order"])
        return [
            AgriculturalTradeMultipliersData.model_validate(
                {k: v for k, v in row.items() if not k.startswith("_")}
            )
            for row in results
        ]
