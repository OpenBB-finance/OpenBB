"""USDA ERS Fertilizer Use and Price Model."""

from typing import Any

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import ConfigDict, Field, field_validator

from openbb_government_us.usda.utils.ers_fertilizer_use_and_price import (
    FERTILIZER_TABLES,
)
from openbb_government_us.utils.serializers import NullTokenMixin, is_null_token

DEFAULT_TABLE = "us_plant_nutrient_consumption"

MONTH_ORDER: dict[str, int] = {
    "Jan.": 1,
    "Feb.": 2,
    "Mar.": 3,
    "Apr.": 4,
    "May": 5,
    "June": 6,
    "July": 7,
    "Aug.": 8,
    "Sept.": 9,
    "Oct.": 10,
    "Nov.": 11,
    "Dec.": 12,
}


class FertilizerUseAndPriceQueryParams(QueryParams):
    """USDA ERS Fertilizer Use and Price Query Parameters.

    Source: https://www.ers.usda.gov/data-products/fertilizer-use-and-price
    """

    __json_schema_extra__ = {
        "table": {
            "x-widget_config": {
                "label": "Table",
                "value": DEFAULT_TABLE,
                "multiSelect": False,
                "multiple": False,
                "options": [
                    {"label": config["label"], "value": key}
                    for key, config in FERTILIZER_TABLES.items()
                ],
                "style": {"popupWidth": 560},
            },
        },
        "start_year": {"x-widget_config": {"label": "Start year"}},
        "end_year": {"x-widget_config": {"label": "End year"}},
    }

    table: str = Field(
        default=DEFAULT_TABLE,
        description="Fertilizer table to retrieve. National tables (1-8) spread"
        + " their nutrient, material, or price measures into the wide columns;"
        + " crop-by-State tables (9-32) spread the surveyed States into the wide"
        + " columns. The period is the pinned row axis. Valid tables are:\n    "
        + ", ".join(FERTILIZER_TABLES)
        + "\n",
    )
    start_year: int | None = Field(
        default=None,
        description="Start year for filtering the data, compared against the"
        + " integer year. If None, returns from the beginning of the series.",
    )
    end_year: int | None = Field(
        default=None,
        description="End year for filtering the data, compared against the"
        + " integer year. If None, returns up to the most recent year.",
    )

    @field_validator("table", mode="before", check_fields=False)
    @classmethod
    def _validate_table(cls, v):
        """Validate table."""
        if not v:
            return DEFAULT_TABLE
        table = v.strip() if isinstance(v, str) else v
        if table not in FERTILIZER_TABLES:
            raise OpenBBError(
                f"Invalid table: {table}. Valid tables are: "
                + ", ".join(FERTILIZER_TABLES)
            )
        return table


class FertilizerUseAndPriceData(NullTokenMixin, Data):
    """USDA ERS Fertilizer Use and Price Data.

    One selected fertilizer table pivoted to a wide layout: the period stays in
    the rows while the table's series dimension - nutrients, materials, price
    measures, or surveyed States - spreads into value columns, whose set varies
    by table. The farm-prices table reports several months per year, so the
    month is folded into the period label to keep every row uniquely labeled.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "x-widget_config": {
                "$.name": "USDA ERS Fertilizer Use and Price",
                "$.description": "U.S. fertilizer consumption, farm prices, price"
                " indexes, and crop-by-State application rates and shares,"
                " published by the USDA Economic Research Service. National"
                " nutrient and material tables are in 1,000 short tons or percent"
                " shares, farm prices in dollars per material short ton, price"
                " indexes on a 2011=100 base, and crop-by-State tables in percent"
                " of acreage or pounds per fertilized acre.",
                "$.category": "Economy",
                "$.subCategory": "Agriculture",
                "$.source": ["USDA", "ERS"],
            },
        }
    )

    period: str = Field(
        description="Row label of the observation: the year for annual tables"
        + " ('2015'), the year and month for the sub-annual farm-prices table"
        + " ('1977 Mar.'), so each row is uniquely labeled.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Period",
                "pinned": "left",
                "maxWidth": 260,
            }
        },
    )


class FertilizerUseAndPriceFetcher(
    Fetcher[
        FertilizerUseAndPriceQueryParams,
        list[FertilizerUseAndPriceData],
    ]
):
    """Fetch USDA ERS Fertilizer Use and Price."""

    require_credentials = False

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> FertilizerUseAndPriceQueryParams:
        """Transform the query params."""
        return FertilizerUseAndPriceQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: FertilizerUseAndPriceQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Extract the selected table's long-format rows."""
        from openbb_government_us.usda.utils import ers_fertilizer_use_and_price

        return await ers_fertilizer_use_and_price.afetch_table(query.table)

    @staticmethod
    def transform_data(
        query: FertilizerUseAndPriceQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[FertilizerUseAndPriceData]:
        """Pivot the long-format rows into period rows with series as columns."""
        unit = FERTILIZER_TABLES[query.table].get("unit")
        pivoted: dict[tuple, dict] = {}
        col_order: list[str] = []
        seen_cols: set[str] = set()
        for record in data:
            year = record["year"]
            if query.start_year is not None and year < query.start_year:
                continue
            if query.end_year is not None and year > query.end_year:
                continue
            token = record["period"]
            month = None if is_null_token(token) else token
            key = (year, month)
            row = pivoted.get(key)
            if row is None:
                row = {
                    "_year": year,
                    "_month_order": MONTH_ORDER.get(month, 0) if month else 0,
                    "period": f"{year} {month}" if month else str(year),
                }
                pivoted[key] = row
            column = record["series"]
            if unit and f"({unit})" not in column:
                column = f"{column} ({unit})"
            if column not in seen_cols:
                seen_cols.add(column)
                col_order.append(column)
            row[column] = record["value"]
        if not pivoted:
            raise EmptyDataError("No records match the given filters.")
        results = sorted(
            pivoted.values(),
            key=lambda row: (row["_year"], row["_month_order"]),
        )
        validated: list[FertilizerUseAndPriceData] = []
        for row in results:
            payload: dict[str, Any] = {"period": row["period"]}
            for column in col_order:
                payload[column] = row.get(column)
            validated.append(FertilizerUseAndPriceData.model_validate(payload))
        return validated
