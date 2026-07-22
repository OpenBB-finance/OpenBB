"""US Agricultural Trade Model."""

from typing import Any

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.app.service.system_service import SystemService
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from pydantic import ConfigDict, Field, field_validator

from openbb_government_us.usda.utils.ers_fatus_trade import (
    DIRECTION_LABELS,
    PERIOD_BASIS_ORDER,
    SPREAD_DIMENSION,
    TABLE_MEASURES,
    TRADE_TABLES,
    classify_period,
    vintage_order,
    within_year_rank,
)
from openbb_government_us.utils.serializers import NullTokenMixin

api_prefix = SystemService().system_settings.api_settings.prefix

DEFAULT_TABLE = "exports_ytd"

DEFAULT_BASIS = {
    "summary": "Fiscal year",
    "monthly": "Monthly",
    "exports_ytd": "Monthly",
    "imports_ytd": "Monthly",
    "top_export_markets": "Monthly",
    "top_import_sources": "Monthly",
}

TABLE_LABELS = {
    "summary": "Summary",
    "monthly": "Monthly total",
    "exports_ytd": "Exports, year-to-date",
    "imports_ytd": "Imports, year-to-date",
    "top_export_markets": "Top export markets",
    "top_import_sources": "Top import sources",
}

TABLE_OPTIONS = [{"label": TABLE_LABELS[slug], "value": slug} for slug in TRADE_TABLES]


def _column_label(spread: str, record: dict) -> str:
    """Build a wide column key with the source unit appended."""
    if spread == "direction":
        base = DIRECTION_LABELS[record["direction"]]
    elif spread == "commodity":
        base = record["commodity"]
    else:
        base = record["country"]
    unit = record["units"]
    return f"{base} ({unit})" if unit else base


def _resolve_commodity(requested: str | None, records: list[dict]) -> str | None:
    """Pick the partner table's row-selected commodity, defaulting to the first."""
    available = list(dict.fromkeys(record["commodity"] for record in records))
    if requested and requested in available:
        return requested
    return available[0] if available else None


class UsAgriculturalTradeQueryParams(QueryParams):
    """US Agricultural Trade Query Parameters.

    Source: https://www.ers.usda.gov/data-products/foreign-agricultural-trade-of-the-united-states-fatus/us-agricultural-trade-data-update
    """

    __json_schema_extra__ = {
        "table": {
            "x-widget_config": {
                "label": "Table",
                "value": DEFAULT_TABLE,
                "multiSelect": False,
                "multiple": False,
                "options": TABLE_OPTIONS,
                "style": {"popupWidth": 320},
            },
        },
        "period_basis": {
            "x-widget_config": {
                "label": "Period basis",
                "type": "endpoint",
                "multiSelect": False,
                "multiple": False,
                "optionsEndpoint": f"{api_prefix}/usda/agricultural_trade_periods",
                "optionsParams": {"table": "$table"},
                "style": {"popupWidth": 300},
            },
        },
        "value_type": {
            "x-widget_config": {
                "label": "Measure",
                "type": "endpoint",
                "value": "value",
                "multiSelect": False,
                "multiple": False,
                "optionsEndpoint": f"{api_prefix}/usda/agricultural_trade_measures",
                "optionsParams": {"table": "$table"},
            },
        },
        "commodity": {
            "x-widget_config": {
                "label": "Commodity (partner tables)",
                "type": "endpoint",
                "multiSelect": False,
                "multiple": False,
                "optionsEndpoint": f"{api_prefix}/usda/agricultural_trade_commodities",
                "optionsParams": {"table": "$table"},
                "style": {"popupWidth": 360},
            },
        },
        "start_year": {"x-widget_config": {"label": "Start year"}},
        "end_year": {"x-widget_config": {"label": "End year"}},
        "latest": {"x-widget_config": {"label": "Latest vintage only"}},
    }

    table: str = Field(
        default=DEFAULT_TABLE,
        description="Table to retrieve, pivoted to a wide layout. The natural"
        + " 'many' dimension spreads into columns (trade direction for the"
        + " summary and monthly tables, commodity for the year-to-date export"
        + " and import tables, trade partner for the top-market tables) while"
        + " a single pinned period column labels the rows. Valid tables are:\n    "
        + ", ".join(TRADE_TABLES)
        + "\n",
    )
    period_basis: str | None = Field(
        default=None,
        description="Reporting basis to keep, one of those the selected table"
        + " publishes: 'Fiscal year', 'Calendar year', 'Fiscal year-to-date',"
        + " 'Calendar year-to-date', or 'Monthly'. Filtering to one basis yields"
        + " a single aligned time series instead of mixing annual totals,"
        + " year-to-date spans, and single months. If None, the table's default"
        + " basis is used.",
    )
    value_type: str | None = Field(
        default=None,
        description="Measure to spread into the wide cells, scoped to the"
        + " table: 'value' (customs value), 'volume', or 'cif' (cost,"
        + " insurance, and freight). If None or invalid for the table, the"
        + " table's first measure is used.",
    )
    commodity: str | None = Field(
        default=None,
        description="Commodity whose trade partners spread into columns, for the"
        + " top-export-market and top-import-source tables only, as a single"
        + " exact name as published, e.g. 'Soybeans'. If None, the table's first"
        + " commodity is used. Ignored by the summary, monthly, and"
        + " year-to-date tables.",
    )
    start_year: int | None = Field(
        default=None,
        description="Start year for filtering the data."
        + " None returns from the beginning of the series.",
    )
    end_year: int | None = Field(
        default=None,
        description="End year for filtering the data."
        + " If None, returns up to the most recent year.",
    )
    latest: bool = Field(
        default=False,
        description="Return only the most recent monthly update vintage for"
        + " tables that retain the marketing year's prior vintages."
        + " No effect on the summary and monthly tables.",
    )

    @field_validator("table", mode="before", check_fields=False)
    @classmethod
    def _validate_table(cls, v):
        """Validate table."""
        if not v:
            return DEFAULT_TABLE
        table = v[0] if isinstance(v, (list, tuple)) else v
        table = table.strip() if isinstance(table, str) else table
        if not table:
            return DEFAULT_TABLE
        if table not in TRADE_TABLES:
            raise OpenBBError(
                f"Invalid table: {table}. Valid tables are: " + ", ".join(TRADE_TABLES)
            )
        return table

    @field_validator(
        "value_type", "commodity", "period_basis", mode="before", check_fields=False
    )
    @classmethod
    def _validate_labels(cls, v):
        """Normalize an optional label to a single stripped string or None."""
        if not v:
            return None
        value = v[0] if isinstance(v, (list, tuple)) else v
        return str(value).strip() or None


class UsAgriculturalTradeData(NullTokenMixin, Data):
    """US Agricultural Trade Data."""

    model_config = ConfigDict(
        json_schema_extra={
            "x-widget_config": {
                "$.name": "USDA ERS U.S. Agricultural Trade",
                "$.description": "Monthly U.S. agricultural exports, imports, and the trade balance by commodity and partner, published by the USDA Economic Research Service.",
                "$.category": "Economy",
                "$.subCategory": "Agriculture",
                "$.source": ["USDA", "ERS"],
            },
        }
    )

    period: str = Field(
        description="Row label of the observation: the year with the published"
        + " time span appended, e.g. '2026 May', '2026 October-May', or"
        + " '2024 Fiscal year, October-September'.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Period",
                "pinned": "left",
                "maxWidth": 240,
            }
        },
    )


class UsAgriculturalTradeFetcher(
    Fetcher[
        UsAgriculturalTradeQueryParams,
        list[UsAgriculturalTradeData],
    ]
):
    """Fetch USDA ERS U.S. Agricultural Trade Data Update."""

    require_credentials = False

    @staticmethod
    def transform_query(params: dict[str, Any]) -> UsAgriculturalTradeQueryParams:
        """Transform the query params."""
        return UsAgriculturalTradeQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: UsAgriculturalTradeQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Extract the selected table's rows from the all-data CSV."""
        from openbb_government_us.usda.utils import ers_fatus_trade

        records = await ers_fatus_trade.afetch_trade_data()
        return [record for record in records if record["table"] == query.table]

    @staticmethod
    def _period_label(basis: str, year: int, period: str) -> str:
        """Label a row: the bare year for annual bases, year plus span otherwise."""
        if basis in ("Fiscal year", "Calendar year"):
            return str(year)
        return f"{year} {period}"

    @staticmethod
    def _resolve_basis(table: str, requested: str | None, records: list[dict]) -> str:
        """Resolve the requested period basis against the table's real bases."""
        present = {classify_period(record["time_period"]) for record in records}
        available = [basis for basis in PERIOD_BASIS_ORDER if basis in present]
        if requested in available:
            return requested
        default = DEFAULT_BASIS.get(table)
        if default in available:
            return default
        return available[0] if available else DEFAULT_BASIS[table]

    @staticmethod
    def transform_data(
        query: UsAgriculturalTradeQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[UsAgriculturalTradeData]:
        """Filter to one period basis and pivot into the single-period layout."""
        from openbb_government_us.usda.utils.ers_fatus_trade import filter_latest

        table = query.table
        measures = TABLE_MEASURES[table]
        measure = query.value_type if query.value_type in measures else measures[0]
        spread = SPREAD_DIMENSION[table]
        records = [record for record in data if record["table"] == table]
        if query.latest:
            records = filter_latest(records)
        records = [record for record in records if record["value_type"] == measure]
        basis = UsAgriculturalTradeFetcher._resolve_basis(
            table, query.period_basis, records
        )
        records = [
            record
            for record in records
            if classify_period(record["time_period"]) == basis
        ]
        if spread == "country":
            commodity = _resolve_commodity(query.commodity, records)
            records = [record for record in records if record["commodity"] == commodity]
        kept: list[tuple[int, dict]] = []
        for record in records:
            year = int(record["year"][:4])
            if query.start_year is not None and year < query.start_year:
                continue
            if query.end_year is not None and year > query.end_year:
                continue
            kept.append((year, record))
        if spread == "direction":
            labels_by_direction: dict[str, str] = {}
            for _, record in kept:
                labels_by_direction.setdefault(
                    record["direction"], _column_label(spread, record)
                )
            column_order = [
                labels_by_direction[direction]
                for direction in DIRECTION_LABELS
                if direction in labels_by_direction
            ]
        else:
            column_order = list(
                dict.fromkeys(_column_label(spread, record) for _, record in kept)
            )
        by_key: dict[tuple, dict] = {}
        for year, record in sorted(
            kept, key=lambda pair: vintage_order(pair[1]["update_version"])
        ):
            key = (year, record["time_period"])
            row = by_key.get(key)
            if row is None:
                row = {
                    "_year": year,
                    "_rank": within_year_rank(basis, record["time_period"]),
                    "period": UsAgriculturalTradeFetcher._period_label(
                        basis, year, record["time_period"]
                    ),
                }
                by_key[key] = row
            row[_column_label(spread, record)] = record["value"]
        ordered = sorted(
            by_key.values(), key=lambda row: (-row["_year"], -row["_rank"])
        )
        results: list[UsAgriculturalTradeData] = []
        for row in ordered:
            payload: dict[str, Any] = {"period": row["period"]}
            for column in column_order:
                payload[column] = row.get(column)
            results.append(UsAgriculturalTradeData.model_validate(payload))
        return results
