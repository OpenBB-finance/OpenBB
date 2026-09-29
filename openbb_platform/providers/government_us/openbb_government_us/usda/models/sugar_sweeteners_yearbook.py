"""USDA ERS Sugar and Sweeteners Yearbook Model."""

from typing import Any

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.app.service.system_service import SystemService
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import ConfigDict, Field, field_validator

from openbb_government_us.usda.utils.ers_sugar_sweeteners_yearbook import (
    FOLD_DIM_FIELDS,
    SUGAR_SWEETENERS_FILES,
    frequency_rank,
    period_sort_num,
    within_year_label,
)
from openbb_government_us.utils.serializers import NullTokenMixin, is_null_token

api_prefix = SystemService().system_settings.api_settings.prefix

DEFAULT_TABLE = "table_24a"
MAX_WIDE_COLUMNS = 60


class SugarSweetenersYearbookQueryParams(QueryParams):
    """USDA ERS Sugar and Sweeteners Yearbook Query Parameters.

    Source: https://www.ers.usda.gov/data-products/sugar-and-sweeteners-yearbook-tables
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
                    for key, config in SUGAR_SWEETENERS_FILES.items()
                ],
                "style": {"popupWidth": 740},
            },
        },
        "frequency": {
            "x-widget_config": {
                "label": "Frequency",
                "type": "endpoint",
                "multiSelect": False,
                "multiple": False,
                "optionsEndpoint": f"{api_prefix}/usda/sugar_frequencies",
                "optionsParams": {"table": "$table"},
                "style": {"popupWidth": 320},
            },
        },
        "start_year": {"x-widget_config": {"label": "Start year"}},
        "end_year": {"x-widget_config": {"label": "End year"}},
    }

    table: str = Field(
        default=DEFAULT_TABLE,
        description="Sugar and Sweeteners Yearbook table to retrieve. Each table"
        + " is a set of named price, supply-and-use, production, or trade series"
        + " indexed by year and period; the attributes become the wide value"
        + " columns while time stays in the rows. Valid tables are:\n    "
        + ", ".join(SUGAR_SWEETENERS_FILES)
        + "\n",
    )
    frequency: str | None = Field(
        default=None,
        description="Period basis to keep, one of the bases the selected table"
        + " publishes, e.g. 'Calendar year', 'Fiscal year', 'Calendar year"
        + " quarter', or 'Month'. Filtering to one basis yields a single"
        + " aligned time series. If None, the table's first annual basis is"
        + " used.",
    )
    start_year: int | None = Field(
        default=None,
        description="Start year for filtering the data, compared against the"
        + " observation year. If None, returns from the beginning of the"
        + " series.",
    )
    end_year: int | None = Field(
        default=None,
        description="End year for filtering the data, compared against the"
        + " observation year. If None, returns up to the most recent year.",
    )

    @field_validator("table", mode="before", check_fields=False)
    @classmethod
    def _validate_table(cls, v):
        """Validate table."""
        if not v:
            return DEFAULT_TABLE
        table = v.strip() if isinstance(v, str) else v
        if table not in SUGAR_SWEETENERS_FILES:
            raise OpenBBError(
                f"Invalid table: {table}. Valid tables are: "
                + ", ".join(SUGAR_SWEETENERS_FILES)
            )
        return table

    @field_validator("frequency", mode="before", check_fields=False)
    @classmethod
    def _validate_frequency(cls, v):
        """Normalize frequency to a stripped string or None."""
        if not v:
            return None
        value = v[0] if isinstance(v, (list, tuple)) else v
        return str(value).strip() or None


class SugarSweetenersYearbookData(NullTokenMixin, Data):
    """USDA ERS Sugar and Sweeteners Yearbook Data.

    One selected yearbook table for one period basis, pivoted to a wide layout:
    the table's attributes spread into value columns while the period stays in
    the rows, with any varying commodity, geography, or source dimension folded
    into the period label. Attribute columns carry their unit in the header when
    the table reports more than one unit.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "x-widget_config": {
                "$.name": "USDA ERS Sugar & Sweeteners Yearbook",
                "$.description": "U.S., Mexican, and world sugar and sweetener"
                " prices, supply and use, production, consumption, and trade"
                " from the Sugar and Sweeteners Yearbook tables, published by"
                " the USDA Economic Research Service.",
                "$.category": "Economy",
                "$.subCategory": "Agriculture",
                "$.source": ["USDA", "ERS"],
            },
        }
    )

    period: str = Field(
        description="Row label of the observation: the year for annual bases"
        + " ('2020'), the year and month or quarter for sub-annual bases"
        + " ('2020 Jan', '2020 Q1'), with any varying commodity, geography, or"
        + " source dimension prefixed so each row is uniquely labeled.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Period",
                "pinned": "left",
                "maxWidth": 320,
            }
        },
    )


class SugarSweetenersYearbookFetcher(
    Fetcher[
        SugarSweetenersYearbookQueryParams,
        list[SugarSweetenersYearbookData],
    ]
):
    """Fetch USDA ERS Sugar and Sweeteners Yearbook data."""

    require_credentials = False

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> SugarSweetenersYearbookQueryParams:
        """Transform the query params."""
        return SugarSweetenersYearbookQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: SugarSweetenersYearbookQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Extract the selected table's long-format rows."""
        from openbb_government_us.usda.utils import ers_sugar_sweeteners_yearbook

        return await ers_sugar_sweeteners_yearbook.afetch_table(query.table)

    @staticmethod
    def _resolve_frequency(
        query: SugarSweetenersYearbookQueryParams, data: list[dict]
    ) -> tuple[str | None, list[str]]:
        """Resolve the requested period basis against the table's real bases."""
        available = sorted(
            {record["period_cat"] for record in data if record["period_cat"]},
            key=lambda cat: (frequency_rank(cat), cat),
        )
        if query.frequency in available:
            return query.frequency, available
        return (available[0] if available else None), available

    @staticmethod
    def transform_data(
        query: SugarSweetenersYearbookQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[SugarSweetenersYearbookData]:
        """Filter to one period basis and pivot the attributes into columns."""
        if not data:
            return []
        frequency, _ = SugarSweetenersYearbookFetcher._resolve_frequency(query, data)
        rows = [
            record
            for record in data
            if record["period_cat"] == frequency
            and (query.start_year is None or record["year"] >= query.start_year)
            and (query.end_year is None or record["year"] <= query.end_year)
        ]
        vintages = {r["forecast_yearmonth"] for r in rows if r["forecast_yearmonth"]}
        if len(vintages) > 1:
            latest = max(vintages)
            rows = [r for r in rows if r["forecast_yearmonth"] == latest]
        if not rows:
            raise EmptyDataError("No records match the given filters.")
        return SugarSweetenersYearbookFetcher._pivot(rows)

    @staticmethod
    def _dim_value(record: dict, field: str) -> str | None:
        """Return a dimension value, treating source placeholders as absent."""
        value = record[field]
        return None if is_null_token(value) else value

    @staticmethod
    def _projected_columns(rows: list[dict], column_dims: list[str]) -> int:
        """Count the wide columns a candidate set of column dims would produce."""
        value = SugarSweetenersYearbookFetcher._dim_value
        return len(
            {
                (*(value(record, field) for field in column_dims), record["attribute"])
                for record in rows
            }
        )

    @staticmethod
    def _classify_dims(
        rows: list[dict], fold_dims: list[str]
    ) -> tuple[list[str], list[str]]:
        """Split folding dims into attribute-partitioning column dims and row dims.

        Parameters
        ----------
        rows : list[dict]
            Long-format records for one table and period basis.
        fold_dims : list[str]
            Dimension fields taking more than one value across the records.

        Returns
        -------
        tuple[list[str], list[str]]
            The dims folded into the column header and the dims folded into the
            row label. A dim becomes a column dim when it partitions the
            attributes, or when the table publishes no more attributes than the
            dim has members and spreading it stays within MAX_WIDE_COLUMNS,
            which would otherwise leave one value column repeated down the rows.
        """
        value = SugarSweetenersYearbookFetcher._dim_value
        column_dims: list[str] = []
        row_dims: list[str] = []
        for field in fold_dims:
            distinct = {
                value(record, field)
                for record in rows
                if value(record, field) is not None
            }
            attr_values: dict[str, set] = {}
            for record in rows:
                member = value(record, field)
                if member is not None:
                    attr_values.setdefault(record["attribute"], set()).add(member)
            if not distinct or not attr_values:
                row_dims.append(field)
                continue
            spread = sum(len(members) for members in attr_values.values()) / len(
                attr_values
            )
            partitions = spread <= 0.6 * len(distinct)
            compact = len(attr_values) <= len(distinct) and (
                SugarSweetenersYearbookFetcher._projected_columns(
                    rows, [*column_dims, field]
                )
                <= MAX_WIDE_COLUMNS
            )
            if partitions or compact:
                column_dims.append(field)
            else:
                row_dims.append(field)
        return SugarSweetenersYearbookFetcher._drop_redundant_dims(
            rows, column_dims, row_dims
        )

    @staticmethod
    def _is_determined(rows: list[dict], field: str, others: list[str]) -> bool:
        """Return whether the other dims and the period already fix a dim's value."""
        value = SugarSweetenersYearbookFetcher._dim_value
        seen: dict[tuple, Any] = {}
        for record in rows:
            key = (
                *(value(record, name) for name in others),
                record["year"],
                record["period"],
            )
            member = value(record, field)
            if seen.setdefault(key, member) != member:
                return False
        return True

    @staticmethod
    def _drop_redundant_dims(
        rows: list[dict], column_dims: list[str], row_dims: list[str]
    ) -> tuple[list[str], list[str]]:
        """Drop dims whose value the remaining dims and the period already fix."""
        columns, labels = list(column_dims), list(row_dims)
        for field in [*column_dims, *row_dims]:
            others = [name for name in [*columns, *labels] if name != field]
            if SugarSweetenersYearbookFetcher._is_determined(rows, field, others):
                columns = [name for name in columns if name != field]
                labels = [name for name in labels if name != field]
        return columns, labels

    @staticmethod
    def _pivot(rows: list[dict]) -> list[SugarSweetenersYearbookData]:
        """Pivot to period rows with the attributes as unit-tagged columns."""
        value = SugarSweetenersYearbookFetcher._dim_value
        fold_dims = [
            field
            for field in FOLD_DIM_FIELDS
            if len({value(record, field) for record in rows}) > 1
        ]
        column_dims, row_dims = SugarSweetenersYearbookFetcher._classify_dims(
            rows, fold_dims
        )
        multi_unit = len({record["unit"] for record in rows}) > 1
        pivoted: dict[tuple, dict[str, Any]] = {}
        column_order: list[str] = []
        seen_columns: set[str] = set()
        for order, record in enumerate(rows):
            year = record["year"]
            within = within_year_label(record["period_cat"], record["period_desc"])
            time_label = f"{year} {within}" if within else str(year)
            row_values = [
                str(value(record, field))
                for field in row_dims
                if value(record, field) is not None
            ]
            label = " — ".join([*row_values, time_label])
            key = (
                tuple(value(record, field) for field in row_dims),
                year,
                record["period"],
            )
            row = pivoted.get(key)
            if row is None:
                row = {
                    "_dims": tuple(row_values),
                    "_year": year,
                    "_period": period_sort_num(record["period"]),
                    "_order": order,
                    "period": label,
                }
                pivoted[key] = row
            column_values = [
                str(value(record, field))
                for field in column_dims
                if value(record, field) is not None
            ]
            base = " — ".join([*column_values, record["attribute"]])
            column = (
                f"{base} ({record['unit']})" if multi_unit and record["unit"] else base
            )
            if column not in seen_columns:
                seen_columns.add(column)
                column_order.append(column)
            row[column] = record["value"]
        ordered = sorted(
            pivoted.values(),
            key=lambda row: (
                row["_dims"],
                -row["_year"],
                -row["_period"],
                row["_order"],
            ),
        )
        validated: list[SugarSweetenersYearbookData] = []
        for row in ordered:
            payload = {"period": row["period"]}
            for column in column_order:
                payload[column] = row.get(column)
            validated.append(SugarSweetenersYearbookData.model_validate(payload))
        return validated
