"""USDA ERS Feed Grains Database Model."""

from typing import Any

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from pydantic import ConfigDict, Field, field_validator

from openbb_government_us.usda.utils.ers_feed_grains import FEED_GRAINS_TABLES
from openbb_government_us.utils.serializers import NullTokenMixin, is_null_token

DEFAULT_TABLE = "corn_supply_and_use"

ROW_DIM_CANDIDATES = ("commodity_group", "commodity", "geography")


class FeedGrainsDatabaseQueryParams(QueryParams):
    """USDA ERS Feed Grains Database Query Parameters.

    Source: https://www.ers.usda.gov/data-products/feed-grains-database
    """

    __json_schema_extra__ = {
        "table": {
            "x-widget_config": {
                "label": "Table",
                "value": DEFAULT_TABLE,
                "multiSelect": False,
                "multiple": False,
                "options": [
                    {"label": config["name"], "value": slug}
                    for slug, config in FEED_GRAINS_TABLES.items()
                ],
                "style": {"popupWidth": 460},
            },
        },
        "start_year": {"x-widget_config": {"label": "Start year"}},
        "end_year": {"x-widget_config": {"label": "End year"}},
    }

    table: str = Field(
        default=DEFAULT_TABLE,
        description="Feed Grains Yearbook table to retrieve. Each table is a set"
        + " of named balance-sheet, price, or trade series indexed by year and"
        + " period; the series become the wide value columns while any varying"
        + " commodity, geography, and period are folded into a single pinned"
        + " period label so each row is uniquely identified. Valid tables are:"
        + "\n    "
        + ", ".join(FEED_GRAINS_TABLES)
        + "\n",
    )
    start_year: int | None = Field(
        default=None,
        description="Start year for filtering the data, compared against the"
        + " integer year of the observation. If None, returns from the"
        + " beginning of the series.",
    )
    end_year: int | None = Field(
        default=None,
        description="End year for filtering the data, compared against the"
        + " integer year of the observation. If None, returns up to the most"
        + " recent year.",
    )

    @field_validator("table", mode="before", check_fields=False)
    @classmethod
    def _validate_table(cls, v):
        """Validate table."""
        if not v:
            return DEFAULT_TABLE
        table = v.strip() if isinstance(v, str) else v
        if table not in FEED_GRAINS_TABLES:
            raise OpenBBError(
                f"Invalid table: {table}. Valid tables are: "
                + ", ".join(FEED_GRAINS_TABLES)
            )
        return table


class FeedGrainsDatabaseData(NullTokenMixin, Data):
    """USDA ERS Feed Grains Database.

    One selected Feed Grains Yearbook table pivoted to a wide layout: the
    period stays in the rows while the table's series dimension spreads into
    value columns, whose set varies by table. Any varying commodity group,
    commodity, or geography is folded into the period label so each row is
    uniquely labeled, and a single row unit is folded into the column headers.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "x-widget_config": {
                "$.name": "USDA ERS Feed Grains Database",
                "$.description": "U.S. and world corn, sorghum, barley, oats, and"
                " hay acreage, supply, use, prices, and trade from the Feed"
                " Grains Yearbook, published by the USDA Economic Research"
                " Service.",
                "$.category": "Economy",
                "$.subCategory": "Agriculture",
                "$.source": ["USDA", "ERS"],
            },
        }
    )

    period: str = Field(
        description="Row label of the observation: the year and published period"
        + " token ('1975 Marketing year Sep-Aug', '2020 Sep', '2019 Marketing"
        + " year Q1 Sep-Nov'), with any varying commodity group, commodity, or"
        + " geography prefixed so each row is uniquely labeled.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Period",
                "pinned": "left",
                "maxWidth": 320,
            }
        },
    )


class FeedGrainsDatabaseFetcher(
    Fetcher[
        FeedGrainsDatabaseQueryParams,
        list[FeedGrainsDatabaseData],
    ]
):
    """Fetch USDA ERS Feed Grains Database."""

    require_credentials = False

    @staticmethod
    def transform_query(params: dict[str, Any]) -> FeedGrainsDatabaseQueryParams:
        """Transform the query params."""
        return FeedGrainsDatabaseQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: FeedGrainsDatabaseQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Extract the selected table's long-format rows."""
        from openbb_government_us.usda.utils import ers_feed_grains

        records = await ers_feed_grains.afetch_yearbook()
        return [record for record in records if record["table"] == query.table]

    @staticmethod
    def transform_data(
        query: FeedGrainsDatabaseQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[FeedGrainsDatabaseData]:
        """Pivot the long-format rows into period rows with series as columns."""
        filtered = [
            record
            for record in data
            if (query.start_year is None or record["year"] >= query.start_year)
            and (query.end_year is None or record["year"] <= query.end_year)
        ]
        if not filtered:
            return []
        if len({record["attribute"] for record in filtered}) > 1:
            series_field: str | None = "attribute"
        elif len({record["commodity"] for record in filtered}) > 1:
            series_field = "commodity"
        else:
            series_field = None

        def series_value(record: dict) -> str:
            return record[series_field] if series_field else record["attribute"]

        series_values = {series_value(record) for record in filtered}
        fold_dims: list[str] = []
        for dim in ROW_DIM_CANDIDATES:
            if dim == series_field:
                continue
            distinct = {
                record[dim] for record in filtered if not is_null_token(record[dim])
            }
            if len(distinct) <= 1:
                continue
            if dim == "commodity_group" and all(
                record["commodity_group"] == record["commodity"] for record in filtered
            ):
                continue
            pairs = {(series_value(record), record[dim]) for record in filtered}
            if len(pairs) == len(series_values):
                continue
            fold_dims.append(dim)

        pivoted: dict[tuple, dict] = {}
        column_order: list[str] = []
        seen_columns: set[str] = set()
        for order, record in enumerate(filtered):
            dim_values = tuple(record[dim] for dim in fold_dims)
            key = (*dim_values, record["year"], record["timeperiod"])
            row = pivoted.get(key)
            if row is None:
                labels = [
                    value for value in dim_values if value and not is_null_token(value)
                ]
                time_label = (
                    f"{record['year']} {record['timeperiod']}"
                    if record["timeperiod"]
                    else str(record["year"])
                )
                row = {
                    "_sort": tuple((value or "") for value in dim_values),
                    "_year": record["year"],
                    "_order": order,
                    "period": " — ".join([*labels, time_label]),
                }
                pivoted[key] = row
            column = series_value(record)
            unit = record["unit"]
            if unit and not is_null_token(unit) and unit not in column:
                column = f"{column} ({unit})"
            if column not in seen_columns:
                seen_columns.add(column)
                column_order.append(column)
            row[column] = record["value"]
        results = sorted(
            pivoted.values(),
            key=lambda row: (row["_sort"], row["_year"], row["_order"]),
        )
        validated: list[FeedGrainsDatabaseData] = []
        for row in results:
            payload: dict[str, Any] = {"period": row["period"]}
            for column in column_order:
                payload[column] = row.get(column)
            validated.append(FeedGrainsDatabaseData.model_validate(payload))
        return validated
