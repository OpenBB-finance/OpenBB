"""USDA ERS Fruit and Tree Nuts Data Model."""

from typing import Any

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.app.service.system_service import SystemService
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from pydantic import ConfigDict, Field, field_validator

from openbb_government_us.usda.utils.ers_fruit_and_tree_nuts_data import (
    CATEGORY_LABELS,
    MONTH_NUMBERS,
    TABLE_TITLES,
)
from openbb_government_us.utils.serializers import NullTokenMixin

api_prefix = SystemService().system_settings.api_settings.prefix

DEFAULT_CATEGORY = "A"
DEFAULT_TABLE = "A-1"
SERIES_DIMS = ("variable", "market_segment", "geography")


def column_label(
    record: dict, series_dims: list[str], commodity_is_column: bool
) -> str:
    """Build the wide-column header for one long-format record.

    Parameters
    ----------
    record : dict
        A long-format record from the parser.
    series_dims : list[str]
        The measure dimensions that vary within the table.
    commodity_is_column : bool
        Whether the commodity dimension is the sole varying dimension and so
        becomes the column axis.

    Returns
    -------
    str
        The header text, a comma-joined set of the varying dimension values
        with the unit in parentheses.
    """
    if commodity_is_column:
        head = record["commodity"]
    else:
        parts = [record[dim] for dim in SERIES_DIMS if dim in series_dims]
        head = ", ".join(parts) if parts else record["variable"]
    return f"{head} ({record['unit']})"


class FruitAndTreeNutsDataQueryParams(QueryParams):
    """USDA ERS Fruit and Tree Nuts Data Query Parameters.

    Source: https://www.ers.usda.gov/data-products/fruit-and-tree-nuts-data
    """

    __json_schema_extra__ = {
        "category": {
            "x-widget_config": {
                "label": "Category",
                "value": DEFAULT_CATEGORY,
                "multiSelect": False,
                "multiple": False,
                "options": [
                    {"label": f"{letter} - {label}", "value": letter}
                    for letter, label in CATEGORY_LABELS.items()
                ],
                "style": {"popupWidth": 420},
            },
        },
        "table": {
            "x-widget_config": {
                "label": "Table",
                "value": DEFAULT_TABLE,
                "type": "endpoint",
                "multiSelect": False,
                "multiple": False,
                "optionsEndpoint": f"{api_prefix}/usda/fruit_yearbook_tables",
                "optionsParams": {"category": "$category"},
                "style": {"popupWidth": 640},
            },
        },
        "start_year": {"x-widget_config": {"label": "Start year"}},
        "end_year": {"x-widget_config": {"label": "End year"}},
    }

    category: str | None = Field(
        default=DEFAULT_CATEGORY,
        description="Yearbook table category, used to narrow the table list."
        + " Valid categories are:\n    "
        + ", ".join(f"{letter} ({label})" for letter, label in CATEGORY_LABELS.items())
        + "\n",
    )
    table: str = Field(
        default=DEFAULT_TABLE,
        description="Yearbook table to retrieve, by its short code. Each of the"
        + " 152 tables shares one long schema and is pivoted to a wide layout"
        + " where the measure dimensions become value columns, with the unit"
        + " in each column header. Valid tables are:\n    "
        + ", ".join(TABLE_TITLES)
        + "\n",
    )
    start_year: int | None = Field(
        default=None,
        description="Start year for filtering the data, compared against the"
        + " first four digits of the calendar or marketing year label."
        + " If None, returns from the beginning of the series.",
    )
    end_year: int | None = Field(
        default=None,
        description="End year for filtering the data, compared against the"
        + " first four digits of the calendar or marketing year label."
        + " If None, returns up to the most recent year.",
    )

    @field_validator("category", mode="before", check_fields=False)
    @classmethod
    def _validate_category(cls, v):
        """Validate category."""
        if not v:
            return None
        value = v[0] if isinstance(v, (list, tuple)) else v
        value = str(value).strip().upper()
        if value not in CATEGORY_LABELS:
            raise OpenBBError(
                f"Invalid category: {value}. Valid categories are: "
                + ", ".join(CATEGORY_LABELS)
            )
        return value

    @field_validator("table", mode="before", check_fields=False)
    @classmethod
    def _validate_table(cls, v):
        """Validate table."""
        if not v:
            return DEFAULT_TABLE
        value = v[0] if isinstance(v, (list, tuple)) else v
        value = str(value).strip().upper()
        if value not in TABLE_TITLES:
            raise OpenBBError(
                f"Invalid table: {value}. Valid tables are: " + ", ".join(TABLE_TITLES)
            )
        return value


class FruitAndTreeNutsData(NullTokenMixin, Data):
    """USDA ERS Fruit and Tree Nuts Data.

    One selected Fruit and Tree Nuts Yearbook table pivoted to a wide layout.
    Time stays in the rows while the table's measure dimensions spread into
    value columns, whose set varies by table.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "x-widget_config": {
                "$.name": "USDA ERS Fruit and Tree Nuts Data",
                "$.description": "U.S. fruit, tree nut, and melon area, production,"
                " price, value, supply, per-capita availability, and import-share"
                " tables from the Fruit and Tree Nuts Yearbook, published by the"
                " USDA Economic Research Service.",
                "$.category": "Economy",
                "$.subCategory": "Agriculture",
                "$.source": ["USDA", "ERS"],
            },
        }
    )

    year: str = Field(
        description="Period label of the observation, as published: a calendar"
        + " year such as '1980', a marketing year such as '1980/81', or, on the"
        + " tables that break a measure out by commodity down the rows, the"
        + " commodity prefixed to that period.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Period",
                "pinned": "left",
                "maxWidth": 260,
            }
        },
    )
    commodity: str | None = Field(
        default=None,
        description="Commodity of the observation, as published. Present only"
        + " when the table breaks a measure out by commodity down the rows;"
        + " otherwise the commodities are the value columns.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Commodity",
                "pinned": "left",
                "hide": True,
            }
        },
    )
    month: str | None = Field(
        default=None,
        description="Month of the observation, for the monthly price tables."
        + " Absent on the annual tables.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Month",
                "pinned": "left",
                "maxWidth": 120,
                "hide": True,
            }
        },
    )


class FruitAndTreeNutsDataFetcher(
    Fetcher[
        FruitAndTreeNutsDataQueryParams,
        list[FruitAndTreeNutsData],
    ]
):
    """Fetch USDA ERS Fruit and Tree Nuts Data."""

    require_credentials = False

    @staticmethod
    def transform_query(params: dict[str, Any]) -> FruitAndTreeNutsDataQueryParams:
        """Transform the query params."""
        return FruitAndTreeNutsDataQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: FruitAndTreeNutsDataQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Extract the selected table's long-format rows."""
        from openbb_government_us.usda.utils import ers_fruit_and_tree_nuts_data

        return await ers_fruit_and_tree_nuts_data.afetch_table(query.table)

    @staticmethod
    def transform_data(
        query: FruitAndTreeNutsDataQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[FruitAndTreeNutsData]:
        """Pivot the long-format rows into the table's adaptive wide layout."""
        distinct: dict[str, set] = {
            dim: {record[dim] for record in data} for dim in (*SERIES_DIMS, "commodity")
        }
        series_dims = [dim for dim in SERIES_DIMS if len(distinct[dim]) > 1]
        commodity_varies = len(distinct["commodity"]) > 1
        commodity_is_column = commodity_varies and not series_dims
        commodity_is_row = commodity_varies and bool(series_dims)
        monthly = any(record["month"] for record in data)

        column_order: list[str] = []
        seen_columns: set[str] = set()
        commodity_index: dict[str, int] = {}
        for record in data:
            commodity_index.setdefault(record["commodity"], len(commodity_index))
            label = column_label(record, series_dims, commodity_is_column)
            if label not in seen_columns:
                seen_columns.add(label)
                column_order.append(label)

        pivoted: dict[tuple, dict] = {}
        for order, record in enumerate(data):
            year = record["year"]
            if query.start_year is not None and year < query.start_year:
                continue
            if query.end_year is not None and year > query.end_year:
                continue
            key = (
                record["year_label"],
                record["month"] if monthly else None,
                record["commodity"] if commodity_is_row else None,
            )
            row = pivoted.get(key)
            if row is None:
                row = {
                    "_commodity_index": (
                        commodity_index[record["commodity"]] if commodity_is_row else 0
                    ),
                    "_year": year,
                    "_month": MONTH_NUMBERS.get((record["month"] or "").casefold(), 0),
                    "_order": order,
                    "year": (
                        f"{record['commodity']} — {record['year_label']}"
                        if commodity_is_row
                        else record["year_label"]
                    ),
                    "commodity": (record["commodity"] if commodity_is_row else None),
                    "month": record["month"] if monthly else None,
                }
                for label in column_order:
                    row[label] = None
                pivoted[key] = row
            row[column_label(record, series_dims, commodity_is_column)] = record[
                "value"
            ]

        results = sorted(
            pivoted.values(),
            key=lambda row: (
                row["_commodity_index"],
                row["_year"],
                row["_month"],
                row["_order"],
            ),
        )
        return [
            FruitAndTreeNutsData.model_validate(
                {k: v for k, v in row.items() if not k.startswith("_")}
            )
            for row in results
        ]
