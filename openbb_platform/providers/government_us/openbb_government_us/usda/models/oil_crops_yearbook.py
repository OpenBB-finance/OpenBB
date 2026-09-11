"""USDA ERS Oil Crops Yearbook Model."""

from typing import Any

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.app.service.system_service import SystemService
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import ConfigDict, Field, field_validator

from openbb_government_us.usda.utils.ers_oil_crops_yearbook import (
    DEFAULT_FREQUENCY,
    DEFAULT_TABLE,
    FREQUENCIES_BY_TABLE,
    FREQUENCY_LABELS,
    OIL_CROPS_TABLES,
    format_period,
    period_ordinal,
)
from openbb_government_us.utils.serializers import NullTokenMixin, is_null_token

api_prefix = SystemService().system_settings.api_settings.prefix

FOLD_DIM_FIELDS = ("commodity", "geography")


class OilCropsYearbookQueryParams(QueryParams):
    """USDA ERS Oil Crops Yearbook Query Parameters.

    Source: https://www.ers.usda.gov/data-products/oil-crops-yearbook
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
                    for key, config in OIL_CROPS_TABLES.items()
                ],
                "style": {"popupWidth": 520},
            },
        },
        "frequency": {
            "x-widget_config": {
                "label": "Frequency",
                "type": "endpoint",
                "multiSelect": False,
                "multiple": False,
                "optionsEndpoint": f"{api_prefix}/usda/oil_crops_frequencies",
                "optionsParams": {"table": "$table"},
            },
        },
        "start_year": {"x-widget_config": {"label": "Start year"}},
        "end_year": {"x-widget_config": {"label": "End year"}},
    }

    table: str = Field(
        default=DEFAULT_TABLE,
        description="Oil Crops Yearbook table to retrieve. Each table is a set"
        + " of named supply, use, price, or trade series indexed by year, and"
        + " sometimes by month or quarter; the series spread into value columns"
        + " while time stays in the rows. Valid tables are:\n    "
        + ", ".join(OIL_CROPS_TABLES)
        + "\n",
    )
    frequency: str | None = Field(
        default=None,
        description="Observation frequency to keep, one of the frequencies the"
        + " selected table publishes: 'point_in_time', 'annual', 'quarterly',"
        + " or 'monthly'. Filtering to one frequency yields a single aligned"
        + " time series. If None, the table's default frequency is used.",
    )
    start_year: int | None = Field(
        default=None,
        description="Start year for filtering the data, compared against the"
        + " first four digits of the marketing or calendar year."
        + " If None, returns from the beginning of the series.",
    )
    end_year: int | None = Field(
        default=None,
        description="End year for filtering the data, compared against the"
        + " first four digits of the marketing or calendar year."
        + " If None, returns up to the most recent year.",
    )

    @field_validator("table", mode="before", check_fields=False)
    @classmethod
    def _validate_table(cls, v):
        """Validate table."""
        if not v:
            return DEFAULT_TABLE
        table = v.strip() if isinstance(v, str) else v
        if table not in OIL_CROPS_TABLES:
            raise OpenBBError(
                f"Invalid table: {table}. Valid tables are: "
                + ", ".join(OIL_CROPS_TABLES)
            )
        return table

    @field_validator("frequency", mode="before", check_fields=False)
    @classmethod
    def _validate_frequency(cls, v):
        """Validate frequency."""
        if not v:
            return None
        frequency = v.strip().lower() if isinstance(v, str) else v
        if frequency not in FREQUENCY_LABELS:
            raise OpenBBError(
                f"Invalid frequency: {v}. Valid frequencies are: "
                + ", ".join(FREQUENCY_LABELS)
            )
        return frequency


class OilCropsYearbookData(NullTokenMixin, Data):
    """USDA ERS Oil Crops Yearbook Data.

    One selected Oil Crops Yearbook table for one frequency, pivoted to a wide
    layout: the table's series spread into value columns while the period stays
    in the rows, with any varying commodity or geography folded into the period
    label. Series columns carry their unit in the header when the table reports
    more than one unit.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "x-widget_config": {
                "$.name": "USDA ERS Oil Crops Yearbook",
                "$.description": "U.S. and world oilseed, oilmeal, and vegetable"
                " oil supply, use, prices, and trade for soybeans, peanuts,"
                " cottonseed, sunflowerseed, canola, and flaxseed, published by"
                " the USDA Economic Research Service.",
                "$.category": "Economy",
                "$.subCategory": "Agriculture",
                "$.source": ["USDA", "ERS"],
            },
        }
    )

    period: str = Field(
        description="Row label of the observation: the marketing or calendar"
        + " year for annual tables ('2024/25'), the year and month, quarter, or"
        + " stocks date for sub-annual tables ('2024/25 October', '2024/25"
        + " March 1'), with any varying commodity or geography prefixed so each"
        + " row is uniquely labeled.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Period",
                "pinned": "left",
                "maxWidth": 320,
            }
        },
    )


class OilCropsYearbookFetcher(
    Fetcher[
        OilCropsYearbookQueryParams,
        list[OilCropsYearbookData],
    ]
):
    """Fetch USDA ERS Oil Crops Yearbook Data."""

    require_credentials = False

    @staticmethod
    def transform_query(params: dict[str, Any]) -> OilCropsYearbookQueryParams:
        """Transform the query params."""
        return OilCropsYearbookQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: OilCropsYearbookQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Extract the selected table's long-format rows."""
        from openbb_government_us.usda.utils import ers_oil_crops_yearbook

        return await ers_oil_crops_yearbook.afetch_table(query.table)

    @staticmethod
    def _resolve_frequency(query: OilCropsYearbookQueryParams) -> str:
        """Resolve the requested frequency against the table's frequencies."""
        available = FREQUENCIES_BY_TABLE[query.table]
        requested = query.frequency
        if requested is not None and requested in available:
            return requested
        return DEFAULT_FREQUENCY[query.table]

    @staticmethod
    def transform_data(
        query: OilCropsYearbookQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[OilCropsYearbookData]:
        """Filter to one frequency and pivot the series into columns."""
        if not data:
            return []
        frequency = OilCropsYearbookFetcher._resolve_frequency(query)
        rows = [
            record
            for record in data
            if record["frequency"] == frequency
            and (query.start_year is None or record["year"] >= query.start_year)
            and (query.end_year is None or record["year"] <= query.end_year)
        ]
        if not rows:
            raise EmptyDataError("No records match the given filters.")
        return OilCropsYearbookFetcher._pivot(rows, frequency)

    @staticmethod
    def _dim_value(record: dict, field: str):
        """Return a dimension value, treating placeholder tokens as absent."""
        value = record[field]
        return None if is_null_token(value) else value

    @staticmethod
    def _classify_dims(
        rows: list[dict], fold_dims: list[str]
    ) -> tuple[list[str], list[str]]:
        """Split folding dims into series-partitioning column dims and row dims."""
        value = OilCropsYearbookFetcher._dim_value
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
            spread = (
                sum(len(members) for members in series_values.values())
                / len(series_values)
                if series_values
                else 0.0
            )
            if distinct and series_values and spread <= 0.6 * len(distinct):
                column_dims.append(field)
            else:
                row_dims.append(field)
        return column_dims, row_dims

    @staticmethod
    def _pivot(rows: list[dict], frequency: str) -> list[OilCropsYearbookData]:
        """Pivot to period rows with the series as unit-tagged columns."""
        value = OilCropsYearbookFetcher._dim_value
        fold_dims = [
            field
            for field in FOLD_DIM_FIELDS
            if len({value(record, field) for record in rows}) > 1
        ]
        column_dims, row_dims = OilCropsYearbookFetcher._classify_dims(rows, fold_dims)
        multi_unit = len({record["unit_desc"] for record in rows}) > 1
        pivoted: dict[tuple, dict[str, Any]] = {}
        column_order: list[str] = []
        seen_columns: set[str] = set()
        for order, record in enumerate(rows):
            marketing_year = record["marketing_year"]
            if record["period"]:
                display = format_period(
                    record["period"], frequency, record["my_definition"]
                )
                time_label = f"{marketing_year} {display}"
            else:
                time_label = marketing_year
            dim_values = [
                str(value(record, field))
                for field in row_dims
                if value(record, field) is not None
            ]
            label = " — ".join([*dim_values, time_label])
            key = (
                tuple(value(record, field) for field in row_dims),
                marketing_year,
                record["period"],
            )
            row = pivoted.get(key)
            if row is None:
                row = {
                    "_dims": tuple(dim_values),
                    "_year": record["year"],
                    "_ord": period_ordinal(
                        record["period"], frequency, record["my_definition"]
                    ),
                    "_order": order,
                    "period": label,
                }
                pivoted[key] = row
            column_values = [
                str(value(record, field))
                for field in column_dims
                if value(record, field) is not None
            ]
            base = " — ".join([*column_values, record["series"]])
            column = (
                f"{base} ({record['unit_desc']})"
                if multi_unit and record["unit_desc"]
                else base
            )
            if column not in seen_columns:
                seen_columns.add(column)
                column_order.append(column)
            row[column] = record["amount"]
        ordered = sorted(
            pivoted.values(),
            key=lambda row: (
                row["_dims"],
                -row["_year"],
                -row["_ord"],
                row["_order"],
            ),
        )
        validated: list[OilCropsYearbookData] = []
        for row in ordered:
            payload = {"period": row["period"]}
            for column in column_order:
                payload[column] = row.get(column)
            validated.append(OilCropsYearbookData.model_validate(payload))
        return validated
