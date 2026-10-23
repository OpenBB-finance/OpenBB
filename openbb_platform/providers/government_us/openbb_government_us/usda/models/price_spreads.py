"""Farm To Consumer Price Spreads Model."""

from typing import Any, Literal

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.app.service.system_service import SystemService
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from pydantic import ConfigDict, Field, field_validator

from openbb_government_us.usda.utils.ers_price_spreads import PRICE_SPREADS_FILES
from openbb_government_us.utils.serializers import NullTokenMixin

api_prefix = SystemService().system_settings.api_settings.prefix

Category = Literal[
    "dairy", "fresh_fruit", "fresh_vegetables", "processed", "field_crops"
]


class FarmToConsumerPriceSpreadsQueryParams(QueryParams):
    """Farm To Consumer Price Spreads Query Parameters.

    Source: https://www.ers.usda.gov/data-products/price-spreads-from-farm-to-consumer
    """

    __json_schema_extra__ = {
        "category": {
            "x-widget_config": {
                "label": "Category",
                "value": "dairy",
                "options": [
                    {"label": "Dairy", "value": "dairy"},
                    {"label": "Fresh fruit", "value": "fresh_fruit"},
                    {"label": "Fresh vegetables", "value": "fresh_vegetables"},
                    {"label": "Processed", "value": "processed"},
                    {"label": "Field crops", "value": "field_crops"},
                ],
            },
        },
        "item": {
            "multiple_items_allowed": True,
            "x-widget_config": {
                "label": "Item",
                "type": "endpoint",
                "multiSelect": False,
                "multiple": False,
                "value": "whole_milk",
                "optionsEndpoint": f"{api_prefix}/usda/price_spread_items",
                "optionsParams": {"category": "$category"},
                "style": {"popupWidth": 320},
            },
        },
        "start_year": {"x-widget_config": {"label": "Start year"}},
        "end_year": {"x-widget_config": {"label": "End year"}},
    }

    category: Category | None = Field(
        default=None,
        description="Filter items by data product category."
        + " If None, all categories are included.",
    )
    item: str | None = Field(
        default=None,
        description="Item(s) to retrieve, as a comma-separated list of slugs."
        + " If None, all items are returned. Valid items are:\n    "
        + ", ".join(sorted(PRICE_SPREADS_FILES))
        + "\n",
    )
    start_year: int | None = Field(
        default=None,
        description="Start year for filtering the data."
        + " None returns from the beginning of each series."
        + " Marketing-year series filter on the first year of the marketing year.",
    )
    end_year: int | None = Field(
        default=None,
        description="End year for filtering the data."
        + " If None, returns up to the most recent year."
        + " Marketing-year series filter on the first year of the marketing year.",
    )

    @field_validator("item", mode="before", check_fields=False)
    @classmethod
    def _validate_item(cls, v):
        """Validate item."""
        if not v:
            return None
        items = v.split(",") if isinstance(v, str) else list(v)
        items = [item.strip() for item in items if item and item.strip()]
        if not items:
            return None
        unknown = [item for item in items if item not in PRICE_SPREADS_FILES]
        if unknown:
            raise OpenBBError(
                f"Invalid item(s): {', '.join(unknown)}. Valid items are: "
                + ", ".join(sorted(PRICE_SPREADS_FILES))
            )
        return ",".join(items)


class FarmToConsumerPriceSpreadsData(NullTokenMixin, Data):
    """Farm To Consumer Price Spreads Data.

    Annual national-average comparisons of retail food prices with the value
    of the farm commodities used to produce them, published by USDA ERS.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "x-widget_config": {
                "$.name": "USDA ERS Price Spreads",
                "$.description": "Retail prices, farm values, and the farm-to-retail price spread for food items and market baskets, published by the USDA Economic Research Service.",
                "$.category": "Economy",
                "$.subCategory": "Agriculture",
                "$.source": ["USDA", "ERS"],
            },
        }
    )

    commodity: str = Field(
        description="Commodity name, as published.",
        json_schema_extra={
            "x-widget_config": {"headerName": "Commodity", "pinned": "left"}
        },
    )
    category: str = Field(
        description="Data product category of the item.",
        json_schema_extra={"x-widget_config": {"headerName": "Category", "hide": True}},
    )
    year: int = Field(
        description="Calendar year of the observation."
        + " For marketing-year series, the first year of the marketing year.",
        json_schema_extra={"x-widget_config": {"headerName": "Year", "maxWidth": 90}},
    )
    marketing_year: str | None = Field(
        default=None,
        description="Marketing year of the observation, as published,"
        + " e.g. '2024/25'. Only present for marketing-year series.",
        json_schema_extra={
            "x-widget_config": {"headerName": "Marketing year", "hide": True}
        },
    )
    retail_price: float | None = Field(
        default=None,
        description="Retail price, in dollars per published unit.",
        json_schema_extra={
            "x-widget_config": {"headerName": "Retail price", "cellDataType": "number"}
        },
    )
    farm_value: float | None = Field(
        default=None,
        description="Farm value, in dollars per published unit.",
        json_schema_extra={
            "x-widget_config": {"headerName": "Farm value", "cellDataType": "number"}
        },
    )
    farm_price: float | None = Field(
        default=None,
        description="Farm price, in dollars per published unit.",
        json_schema_extra={
            "x-widget_config": {"headerName": "Farm price", "cellDataType": "number"}
        },
    )
    farm_share: float | None = Field(
        default=None,
        description="Farm share of the retail price, in percent.",
        json_schema_extra={
            "x-widget_config": {"headerName": "Farm share %", "cellDataType": "number"}
        },
    )
    retail_cost_index: float | None = Field(
        default=None,
        description="Retail cost index.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Retail cost index",
                "cellDataType": "number",
                "hide": True,
            }
        },
    )
    farm_value_index: float | None = Field(
        default=None,
        description="Farm value index.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Farm value index",
                "cellDataType": "number",
                "hide": True,
            }
        },
    )
    farm_to_retail_spread_index: float | None = Field(
        default=None,
        description="Farm-to-retail spread index.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Spread index",
                "cellDataType": "number",
                "hide": True,
            }
        },
    )


class FarmToConsumerPriceSpreadsFetcher(
    Fetcher[
        FarmToConsumerPriceSpreadsQueryParams,
        list[FarmToConsumerPriceSpreadsData],
    ]
):
    """Fetch USDA ERS Price Spreads from Farm to Consumer."""

    require_credentials = False

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> FarmToConsumerPriceSpreadsQueryParams:
        """Transform the query params."""
        return FarmToConsumerPriceSpreadsQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: FarmToConsumerPriceSpreadsQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Extract the selected items' tidy CSV rows."""
        import asyncio

        from openbb_government_us.usda.utils import ers_price_spreads

        selected = (
            sorted(PRICE_SPREADS_FILES) if query.item is None else query.item.split(",")
        )
        if query.category is not None:
            selected = [
                item
                for item in selected
                if PRICE_SPREADS_FILES[item]["category"] == query.category
            ]
        if not selected:
            raise OpenBBError(
                "No items match the combination of 'item' and 'category' filters."
            )
        results = await asyncio.gather(
            *(ers_price_spreads.afetch_item(item) for item in selected)
        )
        records: list[dict] = []
        for item, rows in zip(selected, results):
            category = PRICE_SPREADS_FILES[item]["category"]
            for row in rows:
                records.append({**row, "item": item, "category": category})
        return records

    @staticmethod
    def transform_data(
        query: FarmToConsumerPriceSpreadsQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[FarmToConsumerPriceSpreadsData]:
        """Transform the data."""
        from openbb_government_us.usda.utils.ers_price_spreads import parse_attribute

        pivoted: dict[tuple, dict] = {}
        for record in data:
            raw_year = str(record["year"])
            marketing_year = raw_year if "/" in raw_year else None
            year = int(raw_year[:4]) if marketing_year else int(raw_year)
            if query.start_year is not None and year < query.start_year:
                continue
            if query.end_year is not None and year > query.end_year:
                continue
            measure, _ = parse_attribute(record["attribute"])
            key = (record["item"], year, marketing_year)
            row = pivoted.get(key)
            if row is None:
                row = {
                    "_item": record["item"],
                    "commodity": record["commodity"],
                    "category": record["category"],
                    "year": year,
                    "marketing_year": marketing_year,
                }
                pivoted[key] = row
            row[measure] = record["value"]
        results = sorted(pivoted.values(), key=lambda row: (row["_item"], row["year"]))
        return [
            FarmToConsumerPriceSpreadsData.model_validate(
                {k: v for k, v in row.items() if not k.startswith("_")}
            )
            for row in results
        ]
