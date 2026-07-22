"""USDA ERS Cotton, Wool, and Textile Data Model."""

from typing import Any

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.app.service.system_service import SystemService
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from pydantic import ConfigDict, Field, field_validator

from openbb_government_us.usda.utils.ers_cotton_wool_and_textile_data import (
    COLUMN_DIM_FIELDS,
    CWT_TABLES,
    FREQUENCY_RANK,
    MONTH_NAMES,
    MONTH_ORDER,
    classify_frequency,
)
from openbb_government_us.utils.serializers import NullTokenMixin

api_prefix = SystemService().system_settings.api_settings.prefix

DEFAULT_TABLE = "cotton_supply_and_use"


class CottonWoolAndTextileDataQueryParams(QueryParams):
    """USDA ERS Cotton, Wool, and Textile Data Query Parameters.

    Source: https://www.ers.usda.gov/data-products/cotton-wool-and-textile-data
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
                    for key, config in CWT_TABLES.items()
                ],
                "style": {"popupWidth": 480},
            },
        },
        "frequency": {
            "x-widget_config": {
                "label": "Frequency",
                "type": "endpoint",
                "multiSelect": False,
                "multiple": False,
                "optionsEndpoint": f"{api_prefix}/usda/cotton_frequencies",
                "optionsParams": {"table": "$table"},
            },
        },
        "start_year": {"x-widget_config": {"label": "Start year"}},
        "end_year": {"x-widget_config": {"label": "End year"}},
    }

    table: str = Field(
        default=DEFAULT_TABLE,
        description="Cotton, wool, and textile table to retrieve. Each table is a"
        + " set of named supply-use, price, or trade series indexed by year; the"
        + " series spread into the value columns while time stays in the rows,"
        + " except the by-origin and by-destination cotton textile trade tables,"
        + " which keep the country in the rows and spread years into columns."
        + " Valid tables are:\n    "
        + ", ".join(CWT_TABLES)
        + "\n",
    )
    frequency: str | None = Field(
        default=None,
        description="Reporting frequency to keep, one of the frequencies the"
        + " selected table publishes: 'Annual', 'Quarterly', or 'Monthly'."
        + " Filtering to one frequency yields a single aligned time series."
        + " If None, the finest frequency the table offers is used.",
    )
    start_year: int | None = Field(
        default=None,
        description="Start year for filtering the data, compared against the"
        + " four-digit start year of the observation. If None, returns from the"
        + " beginning of the series.",
    )
    end_year: int | None = Field(
        default=None,
        description="End year for filtering the data, compared against the"
        + " four-digit start year of the observation. If None, returns up to the"
        + " most recent year.",
    )

    @field_validator("table", mode="before", check_fields=False)
    @classmethod
    def _validate_table(cls, v):
        """Validate table."""
        if not v:
            return DEFAULT_TABLE
        table = v.strip() if isinstance(v, str) else v
        if table not in CWT_TABLES:
            raise OpenBBError(
                f"Invalid table: {table}. Valid tables are: " + ", ".join(CWT_TABLES)
            )
        return table

    @field_validator("frequency", mode="before", check_fields=False)
    @classmethod
    def _validate_frequency(cls, v):
        """Normalize frequency to a canonical label or None."""
        if not v:
            return None
        value = v[0] if isinstance(v, (list, tuple)) else v
        return str(value).strip().title() or None


class CottonWoolAndTextileDataData(NullTokenMixin, Data):
    """USDA ERS Cotton, Wool, and Textile Data.

    One selected cotton, wool, or textile table for one reporting frequency,
    pivoted to a wide layout: the table's series and grouping dimensions spread
    into value columns while the period stays in the rows, except the by-origin
    and by-destination cotton textile trade tables, which keep the country in
    the rows and spread years into columns.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "x-widget_config": {
                "$.name": "USDA ERS Cotton, Wool, and Textile Data",
                "$.description": "U.S. and world cotton, wool, and textile-fiber"
                " supply, use, prices, and trade from the Cotton and Wool Yearbook"
                " and the raw-fiber equivalents of U.S. textile trade, published by"
                " the USDA Economic Research Service.",
                "$.category": "Economy",
                "$.subCategory": "Agriculture",
                "$.source": ["USDA", "ERS"],
            },
        }
    )

    period: str = Field(
        description="Row label of the observation: the calendar or marketing year"
        + " ('2020'), the year and month for monthly tables ('2020 Jan'), the"
        + " country for the by-origin and by-destination trade tables, or a"
        + " country prefixed to the year where a table breaks a series out by"
        + " country down the rows.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Period",
                "pinned": "left",
                "maxWidth": 240,
            }
        },
    )


class CottonWoolAndTextileDataFetcher(
    Fetcher[
        CottonWoolAndTextileDataQueryParams,
        list[CottonWoolAndTextileDataData],
    ]
):
    """Fetch USDA ERS Cotton, Wool, and Textile Data."""

    require_credentials = False

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> CottonWoolAndTextileDataQueryParams:
        """Transform the query params."""
        return CottonWoolAndTextileDataQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: CottonWoolAndTextileDataQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Extract the selected table's long-format rows."""
        from openbb_government_us.usda.utils import ers_cotton_wool_and_textile_data

        return await ers_cotton_wool_and_textile_data.afetch_table(query.table)

    @staticmethod
    def _in_range(year: int, query: CottonWoolAndTextileDataQueryParams) -> bool:
        """Return whether a year falls within the query's year window."""
        return (query.start_year is None or year >= query.start_year) and (
            query.end_year is None or year <= query.end_year
        )

    @staticmethod
    def _column_key(record: dict) -> str:
        """Build a wide-column header from a record's grouping dims and series."""
        parts = [
            str(record[field]).replace("_", " ")
            for field in COLUMN_DIM_FIELDS
            if record[field]
        ]
        if record["series"]:
            parts.append(str(record["series"]).replace("_", " "))
        head = " · ".join(parts) if parts else "Value"
        return f"{head} ({record['unit']})" if record["unit"] else head

    @staticmethod
    def _resolve_frequency(
        query: CottonWoolAndTextileDataQueryParams, data: list[dict]
    ) -> tuple[str, list[str]]:
        """Resolve the requested frequency against the table's real frequencies."""
        available = sorted(
            {classify_frequency(record["period"]) for record in data},
            key=lambda freq: FREQUENCY_RANK.get(freq, 9),
        )
        if query.frequency in available:
            return query.frequency, available
        return available[-1], available

    @staticmethod
    def transform_data(
        query: CottonWoolAndTextileDataQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[CottonWoolAndTextileDataData]:
        """Filter to one frequency and pivot the long rows into the wide layout."""
        if not data:
            return []
        frequency, _ = CottonWoolAndTextileDataFetcher._resolve_frequency(query, data)
        years_as_columns = CWT_TABLES[query.table]["pivot"] == "years"
        rows = [
            record
            for record in data
            if classify_frequency(record["period"]) == frequency
            and CottonWoolAndTextileDataFetcher._in_range(record["year"], query)
        ]
        if not rows:
            return []
        if years_as_columns:
            return CottonWoolAndTextileDataFetcher._pivot_years(rows)
        return CottonWoolAndTextileDataFetcher._pivot_series(rows, frequency)

    @staticmethod
    def _pivot_series(
        rows: list[dict], frequency: str
    ) -> list[CottonWoolAndTextileDataData]:
        """Pivot to period rows with the series and grouping dims as columns."""
        pivoted: dict[tuple, dict[str, Any]] = {}
        column_order: list[str] = []
        seen_columns: set[str] = set()
        for source_order, record in enumerate(rows):
            year = record["year"]
            geography = record["geography"]
            month = (
                MONTH_NAMES.get(str(record["period"]))
                if frequency == "Monthly"
                else None
            )
            time_label = f"{year} {month}" if month else str(year)
            label = f"{geography} — {time_label}" if geography else time_label
            key = (geography or "", year, record["period"])
            row = pivoted.get(key)
            if row is None:
                row = {
                    "_geography": geography or "",
                    "_year": year,
                    "_month": MONTH_ORDER.get(month or "", 0),
                    "_order": source_order,
                    "period": label,
                }
                pivoted[key] = row
            column = CottonWoolAndTextileDataFetcher._column_key(record)
            if column not in seen_columns:
                seen_columns.add(column)
                column_order.append(column)
            row[column] = row.get(column, 0.0) + record["value"]
        ordered = sorted(
            pivoted.values(),
            key=lambda row: (
                row["_geography"],
                -row["_year"],
                -row["_month"],
                row["_order"],
            ),
        )
        return CottonWoolAndTextileDataFetcher._validate(ordered, column_order)

    @staticmethod
    def _pivot_years(rows: list[dict]) -> list[CottonWoolAndTextileDataData]:
        """Pivot to country rows with the observation years spread into columns."""
        pivoted: dict[str, dict[str, Any]] = {}
        for source_order, record in enumerate(rows):
            geography = record["geography"] or "Total"
            row = pivoted.get(geography)
            if row is None:
                row = {"_order": source_order, "period": geography}
                pivoted[geography] = row
            column = str(record["year"])
            row[column] = row.get(column, 0.0) + record["value"]
        ordered = sorted(pivoted.values(), key=lambda row: row["_order"])
        year_columns = sorted(
            {key for row in pivoted.values() for key in row if key.isdigit()}, key=int
        )
        return CottonWoolAndTextileDataFetcher._validate(ordered, year_columns)

    @staticmethod
    def _validate(
        ordered: list[dict], column_order: list[str]
    ) -> list[CottonWoolAndTextileDataData]:
        """Assemble each row with the full, identical column set and validate."""
        validated: list[CottonWoolAndTextileDataData] = []
        for row in ordered:
            payload = {"period": row["period"]}
            for column in column_order:
                payload[column] = row.get(column)
            validated.append(CottonWoolAndTextileDataData.model_validate(payload))
        return validated
