"""USDA ERS Food Price Outlook Model."""

from datetime import date
from typing import Any

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.app.service.system_service import SystemService
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from pydantic import ConfigDict, Field, field_validator

from openbb_government_us.usda.utils.ers_food_price_outlook import (
    FOOD_PRICE_OUTLOOK_FILES,
    HIERARCHY_FIELDS,
)
from openbb_government_us.utils.serializers import NullTokenMixin

api_prefix = SystemService().system_settings.api_settings.prefix

DEFAULT_TABLE = "cpi_forecast"

TABLE_LABELS: dict[str, str] = {
    "cpi_forecast": "CPI forecast - changes in consumer price indexes",
    "ppi_forecast": "PPI forecast - changes in producer price indexes",
    "cpi_annual": "CPI annual - percent changes since 1974",
    "ppi_annual": "PPI annual - percent changes since 1974",
    "cpi_forecast_history": "CPI forecast history - monthly vintages",
    "ppi_forecast_history": "PPI forecast history - monthly vintages",
}


class FoodPriceOutlookQueryParams(QueryParams):
    """USDA ERS Food Price Outlook Query Parameters.

    Source: https://www.ers.usda.gov/data-products/food-price-outlook
    """

    __json_schema_extra__ = {
        "table": {
            "x-widget_config": {
                "label": "Table",
                "value": DEFAULT_TABLE,
                "multiSelect": False,
                "multiple": False,
                "options": [
                    {"label": TABLE_LABELS[key], "value": key}
                    for key in FOOD_PRICE_OUTLOOK_FILES
                ],
                "style": {"popupWidth": 480},
            },
        },
        "item": {
            "x-widget_config": {
                "label": "Item",
                "type": "endpoint",
                "multiSelect": False,
                "multiple": False,
                "optionsEndpoint": f"{api_prefix}/usda/food_price_outlook_items",
                "optionsParams": {"table": "$table"},
                "style": {"popupWidth": 360},
            },
        },
        "start_year": {"x-widget_config": {"label": "Start year"}},
        "end_year": {"x-widget_config": {"label": "End year"}},
    }

    table: str = Field(
        default=DEFAULT_TABLE,
        description="Food Price Outlook table to retrieve. The forecast tables"
        + " spread each price-index measure into a column, the annual tables"
        + " spread each food category into a column with years as rows, and the"
        + " forecast-history tables spread the prediction-interval bounds into"
        + " columns. Valid tables are:\n    "
        + ", ".join(FOOD_PRICE_OUTLOOK_FILES)
        + "\n",
    )
    item: str | None = Field(
        default=None,
        description="Filter by a single exact price-index item as published, e.g."
        + " 'Beef and veal', scoped to the selected table. Filters rows for the"
        + " forecast and forecast-history tables and value columns for the annual"
        + " tables. If None, all items are included.",
    )
    start_year: int | None = Field(
        default=None,
        description="Start year for filtering the data, applied to the annual"
        + " calendar year and the forecast-history year being forecast. Forecast"
        + " measures with no year, such as month-over-month changes, are always"
        + " kept. If None, returns from the beginning of the series.",
    )
    end_year: int | None = Field(
        default=None,
        description="End year for filtering the data, applied to the annual"
        + " calendar year and the forecast-history year being forecast. Forecast"
        + " measures with no year, such as month-over-month changes, are always"
        + " kept. If None, returns up to the most recent year.",
    )

    @field_validator("table", mode="before", check_fields=False)
    @classmethod
    def _validate_table(cls, v):
        """Validate table."""
        if not v:
            return DEFAULT_TABLE
        table = v.strip() if isinstance(v, str) else v
        if table not in FOOD_PRICE_OUTLOOK_FILES:
            raise OpenBBError(
                f"Invalid table: {table}. Valid tables are: "
                + ", ".join(FOOD_PRICE_OUTLOOK_FILES)
            )
        return table

    @field_validator("item", mode="before", check_fields=False)
    @classmethod
    def _validate_item(cls, v):
        """Normalize the item filter to a single stripped name or None."""
        if not v:
            return None
        value = v[0] if isinstance(v, (list, tuple)) else v
        return str(value).strip() or None


class FoodPriceOutlookData(NullTokenMixin, Data):
    """USDA ERS Food Price Outlook Data.

    One selected Food Price Outlook table pivoted to a wide layout. The
    forecast tables spread each measure into a column with one row per item,
    the annual tables spread each food category into a column with one row per
    year, and the forecast-history tables spread the prediction-interval bounds
    into columns with one row per item, year, and monthly vintage.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "x-widget_config": {
                "$.name": "USDA ERS Food Price Outlook",
                "$.description": "USDA Economic Research Service forecasts and"
                " history of consumer and producer food price index changes,"
                " with prediction intervals and the annual record since 1974.",
                "$.category": "Economy",
                "$.subCategory": "Agriculture",
                "$.source": ["USDA", "ERS"],
            },
        }
    )

    item: str | None = Field(
        default=None,
        description="Row label: the price-index item on the forecast and"
        + " forecast-history tables, e.g. 'All food' or 'Wholesale beef', or the"
        + " calendar year on the annual tables, where each food category is a"
        + " value column instead.",
        json_schema_extra={"x-widget_config": {"headerName": "Item", "pinned": "left"}},
    )
    top_level: str | None = Field(
        default=None,
        description="Top level of the consumer price index hierarchy, as"
        + " published. Only for the consumer forecast table.",
        json_schema_extra={
            "x-widget_config": {"headerName": "Top level", "hide": True}
        },
    )
    aggregate: str | None = Field(
        default=None,
        description="Aggregate level of the consumer price index hierarchy, as"
        + " published. Only for the consumer forecast table.",
        json_schema_extra={
            "x-widget_config": {"headerName": "Aggregate", "hide": True}
        },
    )
    mid_level: str | None = Field(
        default=None,
        description="Mid level of the consumer price index hierarchy, as"
        + " published. Only for the consumer forecast table.",
        json_schema_extra={
            "x-widget_config": {"headerName": "Mid level", "hide": True}
        },
    )
    low_level: str | None = Field(
        default=None,
        description="Low level of the consumer price index hierarchy, as"
        + " published. Only for the consumer forecast table.",
        json_schema_extra={
            "x-widget_config": {"headerName": "Low level", "hide": True}
        },
    )
    disaggregate: str | None = Field(
        default=None,
        description="Disaggregate level of the consumer price index hierarchy,"
        + " as published. Only for the consumer forecast table.",
        json_schema_extra={
            "x-widget_config": {"headerName": "Disaggregate", "hide": True}
        },
    )
    year: int | None = Field(
        default=None,
        description="Year of the row: the calendar year on the annual tables and"
        + " the year being forecast on the forecast-history tables. Absent on the"
        + " forecast tables, whose measures span several reference years.",
        json_schema_extra={
            "x-widget_config": {"headerName": "Year", "maxWidth": 90, "hide": True}
        },
    )
    forecast_date: date | None = Field(
        default=None,
        description="Vintage of the forecast, as the first day of the month the"
        + " forecast was made. Only for the forecast-history tables.",
        json_schema_extra={
            "x-widget_config": {"headerName": "Forecast date", "hide": True}
        },
    )
    unit: str | None = Field(
        default=None,
        description="Unit of the value columns, as published, when a single unit"
        + " applies to the whole row. Absent on the forecast tables, whose"
        + " measures carry differing units per column.",
        json_schema_extra={"x-widget_config": {"headerName": "Unit", "hide": True}},
    )


class FoodPriceOutlookFetcher(
    Fetcher[
        FoodPriceOutlookQueryParams,
        list[FoodPriceOutlookData],
    ]
):
    """Fetch USDA ERS Food Price Outlook Data."""

    require_credentials = False

    @staticmethod
    def transform_query(params: dict[str, Any]) -> FoodPriceOutlookQueryParams:
        """Transform the query params."""
        return FoodPriceOutlookQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: FoodPriceOutlookQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Extract the selected table's tidy rows."""
        from openbb_government_us.usda.utils import ers_food_price_outlook

        return await ers_food_price_outlook.afetch_table(query.table)

    @staticmethod
    def transform_data(
        query: FoodPriceOutlookQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[FoodPriceOutlookData]:
        """Pivot the tidy rows into the wide layout for the selected table's kind."""
        kind = FOOD_PRICE_OUTLOOK_FILES[query.table]["kind"]
        selected = query.item.lower() if query.item else None

        def within_years(year: int | None) -> bool:
            return year is None or (
                (query.start_year is None or year >= query.start_year)
                and (query.end_year is None or year <= query.end_year)
            )

        def item_matches(item: str) -> bool:
            return selected is None or item.lower() == selected

        pivoted: dict[Any, dict] = {}

        if kind == "annual":
            for record in data:
                if not within_years(record["year"]) or not item_matches(record["item"]):
                    continue
                row = pivoted.get(record["year"])
                if row is None:
                    row = {
                        "_year": record["year"],
                        "item": str(record["year"]),
                        "unit": record["unit"],
                    }
                    pivoted[record["year"]] = row
                row[record["item"]] = record["value"]
            results = sorted(pivoted.values(), key=lambda row: row["_year"])
            return [
                FoodPriceOutlookData.model_validate(
                    {k: v for k, v in row.items() if not k.startswith("_")}
                )
                for row in results
            ]

        if kind == "history":
            for order, record in enumerate(data):
                if not within_years(record["year"]) or not item_matches(record["item"]):
                    continue
                key = (record["item"], record["year"], record["forecast_date"])
                row = pivoted.get(key)
                if row is None:
                    row = {
                        "_order": order,
                        "item": record["item"],
                        "year": record["year"],
                        "forecast_date": record["forecast_date"],
                        "unit": record["unit"],
                    }
                    pivoted[key] = row
                row[record["attribute"]] = record["value"]
            results = sorted(
                pivoted.values(),
                key=lambda row: (
                    row["item"],
                    row["year"],
                    row["forecast_date"],
                    row["_order"],
                ),
            )
            return [
                FoodPriceOutlookData.model_validate(
                    {k: v for k, v in row.items() if not k.startswith("_")}
                )
                for row in results
            ]

        for order, record in enumerate(data):
            if not within_years(record["year"]) or not item_matches(record["item"]):
                continue
            key = (record["item"], *(record.get(field) for field in HIERARCHY_FIELDS))
            row = pivoted.get(key)
            if row is None:
                row = {
                    "_order": order,
                    "item": record["item"],
                }
                for field in HIERARCHY_FIELDS:
                    row[field] = record.get(field)
                pivoted[key] = row
            row[record["attribute"]] = record["value"]
        results = sorted(pivoted.values(), key=lambda row: row["_order"])
        return [
            FoodPriceOutlookData.model_validate(
                {k: v for k, v in row.items() if not k.startswith("_")}
            )
            for row in results
        ]
