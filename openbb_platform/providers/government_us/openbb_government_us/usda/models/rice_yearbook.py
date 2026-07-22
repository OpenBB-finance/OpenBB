"""USDA ERS Rice Yearbook Model."""

from typing import Any

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.app.service.system_service import SystemService
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import ConfigDict, Field, field_validator

from openbb_government_us.usda.utils.ers_rice_yearbook import (
    ANNUAL,
    FREQUENCY_ORDER,
    RICE_TABLES,
    _period_sort_key,
    classify_frequency,
    display_period,
)
from openbb_government_us.utils.serializers import NullTokenMixin, is_null_token

api_prefix = SystemService().system_settings.api_settings.prefix

DEFAULT_TABLE = "us_supply_disappearance_price"
MAX_WIDE_COLUMNS = 60

FOLD_DIM_FIELDS = ("rice_class", "location", "rank", "aggregate_level")


class RiceYearbookQueryParams(QueryParams):
    """USDA ERS Rice Yearbook Query Parameters.

    Source: https://www.ers.usda.gov/data-products/rice-yearbook
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
                    for key, config in RICE_TABLES.items()
                ],
                "style": {"popupWidth": 460},
            },
        },
        "frequency": {
            "x-widget_config": {
                "label": "Frequency",
                "type": "endpoint",
                "multiSelect": False,
                "multiple": False,
                "optionsEndpoint": f"{api_prefix}/usda/rice_frequencies",
                "optionsParams": {"table": "$table"},
            },
        },
        "start_year": {"x-widget_config": {"label": "Start year"}},
        "end_year": {"x-widget_config": {"label": "End year"}},
    }

    table: str = Field(
        default=DEFAULT_TABLE,
        description="Rice-yearbook table to retrieve. Each table is a set of"
        + " named acreage, supply-use, price, or trade series indexed by year"
        + " and period; the series become the wide value columns while time"
        + " stays in the rows. Valid tables are:\n    "
        + ", ".join(RICE_TABLES)
        + "\n",
    )
    frequency: str | None = Field(
        default=None,
        description="Observation frequency to keep, one of the frequencies the"
        + " selected table publishes: 'Annual', 'Point-in-time', 'Weekly', or"
        + " 'Monthly'. Filtering to one frequency yields a single aligned time"
        + " series. If None, the finest frequency the table offers is used.",
    )
    start_year: int | None = Field(
        default=None,
        description="Start year for filtering the data, compared against the"
        + " observation year. If None, returns from the beginning of the series.",
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
        if table not in RICE_TABLES:
            raise OpenBBError(
                f"Invalid table: {table}. Valid tables are: " + ", ".join(RICE_TABLES)
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


class RiceYearbookData(NullTokenMixin, Data):
    """USDA ERS Rice Yearbook Data.

    One selected rice-yearbook table for one frequency, pivoted to a wide
    layout: the table's series spread into value columns while the period stays
    in the rows, with any varying class, location, or rank dimension folded into
    the period label. Series columns carry their unit in the header when the
    table reports more than one unit.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "x-widget_config": {
                "$.name": "USDA ERS Rice Yearbook",
                "$.description": "U.S. and world rice acreage, supply, use,"
                " stocks, prices, and trade, published by the USDA Economic"
                " Research Service.",
                "$.category": "Economy",
                "$.subCategory": "Agriculture",
                "$.source": ["USDA", "ERS"],
            },
        }
    )

    period: str = Field(
        description="Row label of the observation: the year for annual tables"
        + " ('2020'), the year and month or stocks date for sub-annual tables"
        + " ('2020 August', '2020 March 1'), with any varying class, location,"
        + " or rank dimension prefixed so each row is uniquely labeled.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Period",
                "pinned": "left",
                "maxWidth": 320,
            }
        },
    )


class RiceYearbookFetcher(
    Fetcher[
        RiceYearbookQueryParams,
        list[RiceYearbookData],
    ]
):
    """Fetch USDA ERS Rice Yearbook Data."""

    require_credentials = False

    @staticmethod
    def transform_query(params: dict[str, Any]) -> RiceYearbookQueryParams:
        """Transform the query params."""
        return RiceYearbookQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: RiceYearbookQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Extract the selected table's long-format rows."""
        from openbb_government_us.usda.utils import ers_rice_yearbook

        return await ers_rice_yearbook.afetch_table(query.table)

    @staticmethod
    def _resolve_frequency(
        query: RiceYearbookQueryParams, data: list[dict]
    ) -> tuple[str, list[str]]:
        """Resolve the requested frequency against the table's real frequencies."""
        present = {classify_frequency(record["period"]) for record in data}
        available = [freq for freq in FREQUENCY_ORDER if freq in present]
        if query.frequency in available:
            return query.frequency, available
        return (available[0] if available else FREQUENCY_ORDER[-1]), available

    @staticmethod
    def transform_data(
        query: RiceYearbookQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[RiceYearbookData]:
        """Filter to one frequency and pivot the series into columns."""
        if not data:
            return []
        frequency, _ = RiceYearbookFetcher._resolve_frequency(query, data)
        rows = [
            record
            for record in data
            if classify_frequency(record["period"]) == frequency
            and (query.start_year is None or record["year"] >= query.start_year)
            and (query.end_year is None or record["year"] <= query.end_year)
        ]
        if not rows:
            raise EmptyDataError("No records match the given filters.")
        return RiceYearbookFetcher._pivot(rows, frequency)

    @staticmethod
    def _dim_value(record: dict, field: str):
        """Return a dimension value, treating placeholder tokens as absent."""
        value = record[field]
        return None if is_null_token(value) else value

    @staticmethod
    def _projected_columns(rows: list[dict], column_dims: list[str]) -> int:
        """Count the wide columns a candidate set of column dims would produce."""
        value = RiceYearbookFetcher._dim_value
        return len(
            {
                (*(value(record, field) for field in column_dims), record["series"])
                for record in rows
            }
        )

    @staticmethod
    def _classify_dims(
        rows: list[dict], fold_dims: list[str]
    ) -> tuple[list[str], list[str]]:
        """Split folding dims into series-partitioning column dims and row dims.

        Parameters
        ----------
        rows : list[dict]
            Long-format records for one table and frequency.
        fold_dims : list[str]
            Dimension fields taking more than one value across the records.

        Returns
        -------
        tuple[list[str], list[str]]
            The dims folded into the column header and the dims folded into the
            row label. A dim becomes a column dim when it partitions the series,
            or when the table publishes no more series than the dim has members
            and spreading it stays within MAX_WIDE_COLUMNS, which would
            otherwise leave one value column repeated down the rows.
        """
        value = RiceYearbookFetcher._dim_value
        column_dims: list[str] = []
        row_dims: list[str] = []
        for field in fold_dims:
            distinct = {
                value(record, field)
                for record in rows
                if value(record, field) is not None
            }
            series_values: dict[str, set] = {}
            for record in rows:
                member = value(record, field)
                if member is not None:
                    series_values.setdefault(record["series"], set()).add(member)
            if not distinct or not series_values:
                row_dims.append(field)
                continue
            spread = sum(len(members) for members in series_values.values()) / len(
                series_values
            )
            partitions = spread <= 0.6 * len(distinct)
            compact = len(series_values) <= len(distinct) and (
                RiceYearbookFetcher._projected_columns(rows, [*column_dims, field])
                <= MAX_WIDE_COLUMNS
            )
            if partitions or compact:
                column_dims.append(field)
            else:
                row_dims.append(field)
        return RiceYearbookFetcher._drop_redundant_dims(rows, column_dims, row_dims)

    @staticmethod
    def _is_determined(rows: list[dict], field: str, others: list[str]) -> bool:
        """Return whether the other dims and the period already fix a dim's value."""
        value = RiceYearbookFetcher._dim_value
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
            if RiceYearbookFetcher._is_determined(rows, field, others):
                columns = [name for name in columns if name != field]
                labels = [name for name in labels if name != field]
        return columns, labels

    @staticmethod
    def _basis_partitions_series(rows: list[dict]) -> bool:
        """Return whether the annual bases each publish their own series."""
        bases = {record["period"] for record in rows}
        if len(bases) < 2:
            return False
        series_bases: dict[str, set] = {}
        for record in rows:
            series_bases.setdefault(record["series"], set()).add(record["period"])
        spread = sum(len(members) for members in series_bases.values()) / len(
            series_bases
        )
        return spread <= 0.6 * len(bases)

    @staticmethod
    def _pivot(rows: list[dict], frequency: str) -> list[RiceYearbookData]:
        """Pivot to period rows with the series as unit-tagged columns."""
        value = RiceYearbookFetcher._dim_value
        fold_dims = [
            field
            for field in FOLD_DIM_FIELDS
            if len({value(record, field) for record in rows}) > 1
        ]
        column_dims, row_dims = RiceYearbookFetcher._classify_dims(rows, fold_dims)
        period_varies = len({record["period"] for record in rows}) > 1
        basis_in_columns = (
            frequency == ANNUAL
            and period_varies
            and RiceYearbookFetcher._basis_partitions_series(rows)
        )
        multi_unit = len({record["unit"] for record in rows}) > 1
        pivoted: dict[tuple, dict[str, Any]] = {}
        column_order: list[str] = []
        seen_columns: set[str] = set()
        for order, record in enumerate(rows):
            year = record["year"]
            display = display_period(record["period"])
            if frequency == ANNUAL:
                labeled_basis = period_varies and display and not basis_in_columns
                time_label = f"{year} — {display}" if labeled_basis else str(year)
            else:
                time_label = f"{year} {display}" if display else str(year)
            dim_values = [
                str(value(record, field))
                for field in row_dims
                if value(record, field) is not None
            ]
            label = " — ".join([*dim_values, time_label])
            key = (
                tuple(value(record, field) for field in row_dims),
                year,
                None if basis_in_columns else record["period"],
            )
            row = pivoted.get(key)
            if row is None:
                row = {
                    "_dims": tuple(dim_values),
                    "_year": year,
                    "_period": _period_sort_key(display, frequency),
                    "_order": order,
                    "period": label,
                }
                pivoted[key] = row
            column_values = [
                str(value(record, field))
                for field in column_dims
                if value(record, field) is not None
            ]
            series = (
                f"{record['series']} — {display}"
                if basis_in_columns and display
                else record["series"]
            )
            base = " — ".join([*column_values, series])
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
        validated: list[RiceYearbookData] = []
        for row in ordered:
            payload = {"period": row["period"]}
            for column in column_order:
                payload[column] = row.get(column)
            validated.append(RiceYearbookData.model_validate(payload))
        return validated
