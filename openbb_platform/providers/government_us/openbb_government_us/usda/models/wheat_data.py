"""USDA ERS Wheat Data Model."""

from typing import Any

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from pydantic import ConfigDict, Field, field_validator

from openbb_government_us.usda.utils.ers_wheat_data import (
    ROW_DIM_FIELDS,
    WHEAT_DATA_FILES,
)
from openbb_government_us.utils.serializers import NullTokenMixin, is_null_token

DEFAULT_TABLE = "us_supply_and_disappearance"

LABEL_DIM_ORDER = ("commodity_group", "wheat_class", "product", "geography", "unit")


class WheatDataQueryParams(QueryParams):
    """USDA ERS Wheat Data Query Parameters.

    Source: https://www.ers.usda.gov/data-products/wheat-data
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
                    for key, config in WHEAT_DATA_FILES.items()
                ],
                "style": {"popupWidth": 420},
            },
        },
        "start_year": {"x-widget_config": {"label": "Start year"}},
        "end_year": {"x-widget_config": {"label": "End year"}},
    }

    table: str = Field(
        default=DEFAULT_TABLE,
        description="Wheat-data table to retrieve. Each table is a set of"
        + " named balance-sheet, price, or trade series indexed by year and"
        + " period; the series become the wide value columns while any varying"
        + " wheat class, destination, market, product, or unit is folded into"
        + " the pinned period label. Valid tables are:\n    "
        + ", ".join(WHEAT_DATA_FILES)
        + "\n",
    )
    start_year: int | None = Field(
        default=None,
        description="Start year for filtering the data, compared against the"
        + " first four digits of the marketing, calendar, or fiscal year."
        + " If None, returns from the beginning of the series.",
    )
    end_year: int | None = Field(
        default=None,
        description="End year for filtering the data, compared against the"
        + " first four digits of the marketing, calendar, or fiscal year."
        + " If None, returns up to the most recent year.",
    )

    @field_validator("table", mode="before", check_fields=False)
    @classmethod
    def _validate_table(cls, v):
        """Validate table."""
        if not v:
            return DEFAULT_TABLE
        table = v.strip() if isinstance(v, str) else v
        if table not in WHEAT_DATA_FILES:
            raise OpenBBError(
                f"Invalid table: {table}. Valid tables are: "
                + ", ".join(WHEAT_DATA_FILES)
            )
        return table


class WheatDataData(NullTokenMixin, Data):
    """USDA ERS Wheat Data.

    One selected wheat-data table pivoted to a wide layout: the period stays in
    the rows while the table's series dimension spreads into value columns, whose
    set varies by table. Any varying wheat class, destination, market, product,
    or unit is folded into the period label so every row is uniquely labeled.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "x-widget_config": {
                "$.name": "USDA ERS Wheat Data",
                "$.description": "U.S. and world wheat supply, use, trade, prices,"
                " and by-class balance sheets, published by the USDA Economic"
                " Research Service.",
                "$.category": "Economy",
                "$.subCategory": "Agriculture",
                "$.source": ["USDA", "ERS"],
            },
        }
    )

    period: str = Field(
        description="Row label of the observation: the marketing, calendar, or"
        + " fiscal year and its within-year period ('2024/25 MY Jun-May',"
        + " '1989/90 Apr'), with any varying wheat class, destination, market,"
        + " product, or unit prefixed so each row is uniquely labeled.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Period",
                "pinned": "left",
                "maxWidth": 300,
            }
        },
    )


class WheatDataFetcher(
    Fetcher[
        WheatDataQueryParams,
        list[WheatDataData],
    ]
):
    """Fetch USDA ERS Wheat Data."""

    require_credentials = False

    @staticmethod
    def transform_query(params: dict[str, Any]) -> WheatDataQueryParams:
        """Transform the query params."""
        return WheatDataQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: WheatDataQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Extract the selected table's long-format rows."""
        from openbb_government_us.usda.utils import ers_wheat_data

        return await ers_wheat_data.afetch_table(query.table)

    @staticmethod
    def _time_label(marketing_year: str, period: str | None) -> str:
        """Fold the year label and within-year period into one time label."""
        if period:
            return f"{marketing_year} {period}"
        return marketing_year

    @staticmethod
    def transform_data(
        query: WheatDataQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[WheatDataData]:
        """Pivot the long-format rows into uniquely labeled period rows."""
        filtered: list[dict] = []
        for order, record in enumerate(data):
            year = record["year"]
            if query.start_year is not None and year < query.start_year:
                continue
            if query.end_year is not None and year > query.end_year:
                continue
            clean = dict(record)
            for field in ROW_DIM_FIELDS:
                if is_null_token(clean.get(field)):
                    clean[field] = None
            clean["_order"] = order
            filtered.append(clean)
        if not filtered:
            return []
        distinct: dict[str, set] = {
            field: {r[field] for r in filtered if r[field] is not None}
            for field in ROW_DIM_FIELDS
        }
        varying = {field for field in ROW_DIM_FIELDS if len(distinct[field]) > 1}
        table_unit = (
            next(iter(distinct["unit"]))
            if "unit" not in varying and len(distinct["unit"]) == 1
            else None
        )
        pivoted: dict[tuple, dict] = {}
        col_order: list[str] = []
        seen_cols: set[str] = set()
        for record in filtered:
            key = (
                record["marketing_year"],
                record["period"],
                *(record[field] for field in ROW_DIM_FIELDS),
            )
            row = pivoted.get(key)
            if row is None:
                dim_parts = [
                    record[field]
                    for field in LABEL_DIM_ORDER
                    if field in varying and record[field] is not None
                ]
                time_label = WheatDataFetcher._time_label(
                    record["marketing_year"], record["period"]
                )
                row = {
                    "_sort": tuple(record[field] or "" for field in LABEL_DIM_ORDER),
                    "_year": record["year"],
                    "_order": record["_order"],
                    "period": " — ".join([*dim_parts, time_label]),
                }
                pivoted[key] = row
            series = record["series"]
            column = (
                f"{series} ({table_unit})"
                if table_unit and f"({table_unit})" not in series
                else series
            )
            if column not in seen_cols:
                seen_cols.add(column)
                col_order.append(column)
            row[column] = row.get(column, 0.0) + record["amount"]
        results = sorted(
            pivoted.values(),
            key=lambda row: (row["_sort"], row["_year"], row["_order"]),
        )
        validated: list[WheatDataData] = []
        for row in results:
            payload: dict[str, Any] = {"period": row["period"]}
            for column in col_order:
                payload[column] = row.get(column)
            validated.append(WheatDataData.model_validate(payload))
        return validated
