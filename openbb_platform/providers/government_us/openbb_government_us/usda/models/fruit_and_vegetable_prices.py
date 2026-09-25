"""USDA ERS Fruit and Vegetable Prices Model."""

from typing import Any, Literal

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import ConfigDict, Field, field_validator

from openbb_government_us.usda.utils.ers_fruit_and_vegetable_prices import (
    DATA_YEAR,
    FVP_TABLES,
)
from openbb_government_us.utils.serializers import NullTokenMixin

DEFAULT_TABLE = "fruit"

Table = Literal["fruit", "vegetable"]


class FruitAndVegetablePricesQueryParams(QueryParams):
    """USDA ERS Fruit and Vegetable Prices Query Parameters.

    Source: https://www.ers.usda.gov/data-products/fruit-and-vegetable-prices
    """

    __json_schema_extra__ = {
        "table": {
            "x-widget_config": {
                "label": "Table",
                "value": DEFAULT_TABLE,
                "multiSelect": False,
                "multiple": False,
                "options": [
                    {"label": entry["item_label"], "value": key}
                    for key, entry in FVP_TABLES.items()
                ],
            },
        },
    }

    table: Table = Field(
        default=DEFAULT_TABLE,
        description="Commodity group to retrieve. Each group is one tidy table"
        + " of average retail and cup-equivalent prices, with one row per item"
        + " and form. Valid tables are:\n    "
        + ", ".join(FVP_TABLES)
        + "\n",
    )

    @field_validator("table", mode="before", check_fields=False)
    @classmethod
    def _validate_table(cls, v):
        """Validate the selected table key."""
        if isinstance(v, (list, tuple)):
            v = next((item for item in v if item), None)
        if not v:
            return DEFAULT_TABLE
        table = str(v).strip().lower()
        if table not in FVP_TABLES:
            raise OpenBBError(
                f"Invalid table: {table}. Valid tables are: " + ", ".join(FVP_TABLES)
            )
        return table


class FruitAndVegetablePricesData(NullTokenMixin, Data):
    """USDA ERS Fruit and Vegetable Prices Data.

    One selected commodity group's average retail prices and cup-equivalent
    prices, with one row per item and form and a fixed set of measure columns.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "x-widget_config": {
                "$.name": "USDA ERS Fruit & Vegetable Prices",
                "$.description": "Average retail price, preparation yield factor,"
                " cup-equivalent size, and average price per edible cup-equivalent"
                f" for fresh, canned, frozen, dried, and juice forms, for {DATA_YEAR}"
                " (Circana OmniMarket Core Outlets), published by the USDA Economic"
                " Research Service.",
                "$.category": "Economy",
                "$.subCategory": "Agriculture",
                "$.source": ["USDA", "ERS"],
            },
        }
    )

    item: str = Field(
        description="Fruit or vegetable commodity, as published.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Commodity",
                "cellDataType": "text",
                "pinned": "left",
            }
        },
    )
    form: str = Field(
        description="Marketed form of the item, e.g. Fresh, Canned, Frozen,"
        + " Dried, or Juice.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Form",
                "cellDataType": "text",
                "pinned": "left",
                "maxWidth": 120,
            }
        },
    )
    average_retail_price: float | None = Field(
        default=None,
        description="Average retail price of the item in its retail unit.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Average Retail Price",
                "cellDataType": "number",
            }
        },
    )
    average_retail_price_unit: str | None = Field(
        default=None,
        description="Retail unit the average retail price is measured in, e.g."
        + " 'per pound' or 'per pint (16 fluid ounces ready to drink)'.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Retail Price Unit",
                "cellDataType": "text",
            }
        },
    )
    preparation_yield_factor: float | None = Field(
        default=None,
        description="Share of the purchased item that is edible after"
        + " preparation, as a fraction.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Preparation Yield Factor",
                "cellDataType": "number",
            }
        },
    )
    cup_equivalent_size: float | None = Field(
        default=None,
        description="Size of one cup-equivalent of the edible item, in the"
        + " cup-equivalent unit.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Cup-Equivalent Size",
                "cellDataType": "number",
            }
        },
    )
    cup_equivalent_unit: str | None = Field(
        default=None,
        description="Unit the cup-equivalent size is measured in, e.g. 'pounds'"
        + " or 'pints'.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Cup-Equivalent Unit",
                "cellDataType": "text",
            }
        },
    )
    average_price_per_cup_equivalent: float | None = Field(
        default=None,
        description="Average price of one edible cup-equivalent of the item, in"
        + " U.S. dollars.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Average Price per Cup-Equivalent",
                "cellDataType": "number",
            }
        },
    )


class FruitAndVegetablePricesFetcher(
    Fetcher[
        FruitAndVegetablePricesQueryParams,
        list[FruitAndVegetablePricesData],
    ]
):
    """Fetch USDA ERS Fruit and Vegetable Prices."""

    require_credentials = False

    @staticmethod
    def transform_query(params: dict[str, Any]) -> FruitAndVegetablePricesQueryParams:
        """Transform the query params."""
        return FruitAndVegetablePricesQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: FruitAndVegetablePricesQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Extract the selected table's tidy CSV rows."""
        from openbb_government_us.usda.utils import ers_fruit_and_vegetable_prices

        return await ers_fruit_and_vegetable_prices.afetch_table(query.table)

    @staticmethod
    def transform_data(
        query: FruitAndVegetablePricesQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[FruitAndVegetablePricesData]:
        """Order the wide-on-measure rows by item and form."""
        if not data:
            raise EmptyDataError("No records returned for the given table.")
        results = sorted(data, key=lambda row: (row["item"], row["form"] or ""))
        return [FruitAndVegetablePricesData.model_validate(row) for row in results]
