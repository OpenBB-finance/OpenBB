"""USDA ERS Livestock and Meat Domestic Data Model."""

from typing import Any

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from pydantic import ConfigDict, Field, field_validator

from openbb_government_us.usda.utils.ers_livestock_and_meat_domestic_data import (
    FOLD_DIM_FIELDS,
    LIVESTOCK_AND_MEAT_FILES,
)
from openbb_government_us.utils.serializers import NullTokenMixin

DEFAULT_TABLE = "supply_and_disappearance"


class LivestockAndMeatDomesticDataQueryParams(QueryParams):
    """USDA ERS Livestock and Meat Domestic Data Query Parameters.

    Source: https://www.ers.usda.gov/data-products/livestock-and-meat-domestic-data
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
                    for key, config in LIVESTOCK_AND_MEAT_FILES.items()
                ],
                "style": {"popupWidth": 420},
            },
        },
        "start_year": {"x-widget_config": {"label": "Start year"}},
        "end_year": {"x-widget_config": {"label": "End year"}},
    }

    table: str = Field(
        default=DEFAULT_TABLE,
        description="Livestock and meat table to retrieve. Each table is a set"
        + " of named slaughter, production, weight, cold-storage, supply-and-use,"
        + " or price series indexed by year and period; the attributes become the"
        + " wide value columns, prefixed by commodity or sub-table where that"
        + " dimension splits the series. Valid tables are:\n    "
        + ", ".join(LIVESTOCK_AND_MEAT_FILES)
        + "\n",
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
        if table not in LIVESTOCK_AND_MEAT_FILES:
            raise OpenBBError(
                f"Invalid table: {table}. Valid tables are: "
                + ", ".join(LIVESTOCK_AND_MEAT_FILES)
            )
        return table


class LivestockAndMeatDomesticData(NullTokenMixin, Data):
    """USDA ERS Livestock and Meat Domestic Data.

    One selected livestock-and-meat table pivoted to a wide layout: the period
    stays in the rows while the table's attribute dimension spreads into value
    columns, whose set varies by table. A commodity, sub-table, or geography
    dimension is prefixed onto the column headers when it splits the series,
    and folded into the period label otherwise.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "x-widget_config": {
                "$.name": "USDA ERS Livestock & Meat Domestic Data",
                "$.description": "U.S. livestock and meat slaughter, production,"
                " weights, cold storage, supply and disappearance, and livestock"
                " and wholesale prices, published by the USDA Economic Research"
                " Service.",
                "$.category": "Economy",
                "$.subCategory": "Agriculture",
                "$.source": ["USDA", "ERS"],
            },
        }
    )

    period: str = Field(
        description="Row label of the observation: the year for annual tables"
        + " ('2020'), the year and month, quarter, or feeding window for"
        + " sub-annual tables ('2020 January', '2020 Q1 Jan-Mar'), with any"
        + " commodity, sub-table, or geography that is not carried in the"
        + " column headers prefixed so each row is uniquely labeled.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Period",
                "pinned": "left",
                "maxWidth": 260,
            }
        },
    )


class LivestockAndMeatDomesticDataFetcher(
    Fetcher[
        LivestockAndMeatDomesticDataQueryParams,
        list[LivestockAndMeatDomesticData],
    ]
):
    """Fetch USDA ERS Livestock and Meat Domestic Data."""

    require_credentials = False

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> LivestockAndMeatDomesticDataQueryParams:
        """Transform the query params."""
        return LivestockAndMeatDomesticDataQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: LivestockAndMeatDomesticDataQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Extract the selected table's long-format rows."""
        from openbb_government_us.usda.utils import ers_livestock_and_meat_domestic_data

        return await ers_livestock_and_meat_domestic_data.afetch_table(query.table)

    @staticmethod
    def _period_label(year: int, period: str | None) -> str:
        """Fold the year and within-year period into one readable time label."""
        if not period or period.startswith("Yr"):
            return str(year)
        if " to " in period:
            return period
        return f"{year} {period}"

    @staticmethod
    def _classify_dims(
        rows: list[dict], fold_dims: list[str]
    ) -> tuple[list[str], list[str]]:
        """Split folding dims into series-partitioning column dims and row dims.

        Parameters
        ----------
        rows : list[dict]
            Long-format records for one table.
        fold_dims : list[str]
            Dimension fields that take more than one value across the records.

        Returns
        -------
        tuple[list[str], list[str]]
            The dims folded into the column header and the dims folded into the
            row label. A dim goes to the header when it partitions the series,
            or when the table publishes no more series than the dim has
            members, which would otherwise leave a near-single value column
            repeated down the rows.
        """
        column_dims: list[str] = []
        row_dims: list[str] = []
        for field in fold_dims:
            distinct = {record[field] for record in rows if record[field]}
            series_values: dict[str, set] = {}
            for record in rows:
                if record[field]:
                    series_values.setdefault(record["column"], set()).add(record[field])
            if not distinct or not series_values:
                row_dims.append(field)
                continue
            spread = sum(len(members) for members in series_values.values()) / len(
                series_values
            )
            partitions = spread <= 0.6 * len(distinct)
            if partitions or len(series_values) <= len(distinct):
                column_dims.append(field)
            else:
                row_dims.append(field)
        return column_dims, row_dims

    @staticmethod
    def transform_data(
        query: LivestockAndMeatDomesticDataQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[LivestockAndMeatDomesticData]:
        """Filter to the requested years and pivot into the wide layout."""
        rows = [
            record
            for record in data
            if (query.start_year is None or record["year"] >= query.start_year)
            and (query.end_year is None or record["year"] <= query.end_year)
        ]
        if not rows:
            return []
        return LivestockAndMeatDomesticDataFetcher._pivot(rows)

    @staticmethod
    def _pivot(rows: list[dict]) -> list[LivestockAndMeatDomesticData]:
        """Pivot the long-format rows into newest-first periods with series columns."""
        fold_dims = [
            field
            for field in FOLD_DIM_FIELDS
            if len({record[field] for record in rows}) > 1
        ]
        column_dims, row_dims = LivestockAndMeatDomesticDataFetcher._classify_dims(
            rows, fold_dims
        )
        pivoted: dict[tuple, dict] = {}
        combo_order: dict[tuple, int] = {}
        group_order: dict[tuple, int] = {}
        series_order: dict[str, int] = {}
        col_rank: dict[str, tuple[int, int]] = {}
        for order, record in enumerate(rows):
            dims = tuple(record[field] for field in row_dims)
            key = (*dims, record["year"], record["period"])
            row = pivoted.get(key)
            if row is None:
                combo_order.setdefault(dims, len(combo_order))
                time_label = LivestockAndMeatDomesticDataFetcher._period_label(
                    record["year"], record["period"]
                )
                dim_values = [value for value in dims if value]
                row = {
                    "_combo": combo_order[dims],
                    "_order": order,
                    "_year": record["year"],
                    "_period_sort": record["period_sort"],
                    "period": " — ".join([*dim_values, time_label]),
                }
                pivoted[key] = row
            column_values = tuple(
                str(record[field]) for field in column_dims if record[field]
            )
            base = " — ".join([*column_values, record["column"]])
            column = f"{base} ({record['unit']})" if record["unit"] else base
            if column not in col_rank:
                group_order.setdefault(column_values, len(group_order))
                series_order.setdefault(record["column"], len(series_order))
                col_rank[column] = (
                    group_order[column_values],
                    series_order[record["column"]],
                )
            row[column] = record["amount"]
        col_order = sorted(col_rank, key=lambda column: col_rank[column])
        results = sorted(
            pivoted.values(),
            key=lambda row: (
                row["_combo"],
                -row["_year"],
                -row["_period_sort"],
                -row["_order"],
            ),
        )
        validated: list[LivestockAndMeatDomesticData] = []
        for row in results:
            payload = {"period": row["period"]}
            for column in col_order:
                payload[column] = row.get(column)
            validated.append(LivestockAndMeatDomesticData.model_validate(payload))
        return validated
