"""USDA ERS U.S. Bioenergy Statistics Model."""

from typing import Any

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from pydantic import ConfigDict, Field, field_validator

from openbb_government_us.usda.utils.ers_us_bioenergy_statistics import BIOENERGY_TABLES
from openbb_government_us.utils.serializers import NullTokenMixin

DEFAULT_TABLE = "ethanol_supply_marketing_year"

SUBANNUAL_CADENCES = frozenset({"Marketing year and quarter", "Monthly"})


class UsBioenergyStatisticsQueryParams(QueryParams):
    """USDA ERS U.S. Bioenergy Statistics Query Parameters.

    Source: https://www.ers.usda.gov/data-products/us-bioenergy-statistics
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
                    for key, config in BIOENERGY_TABLES.items()
                ],
                "style": {"popupWidth": 520},
            },
        },
        "start_year": {"x-widget_config": {"label": "Start year"}},
        "end_year": {"x-widget_config": {"label": "End year"}},
    }

    table: str = Field(
        default=DEFAULT_TABLE,
        description="Bioenergy-statistics table to retrieve. Each table is a"
        + " set of named supply, use, capacity, or price series indexed by"
        + " year and period; the series become the wide value columns while a"
        + " single period column, with any varying location folded in, stays"
        + " as the pinned row column. Valid tables are:\n    "
        + ", ".join(BIOENERGY_TABLES)
        + "\n",
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
        if table not in BIOENERGY_TABLES:
            raise OpenBBError(
                f"Invalid table: {table}. Valid tables are: "
                + ", ".join(BIOENERGY_TABLES)
            )
        return table


class UsBioenergyStatisticsData(NullTokenMixin, Data):
    """USDA ERS U.S. Bioenergy Statistics, one table pivoted to a wide layout."""

    model_config = ConfigDict(
        json_schema_extra={
            "x-widget_config": {
                "$.name": "USDA ERS U.S. Bioenergy Statistics",
                "$.description": "U.S. ethanol, biodiesel, and renewable diesel"
                " supply, use, capacity, consumption, and prices, with related"
                " feedstock and co-product balances, published by the USDA"
                " Economic Research Service.",
                "$.category": "Economy",
                "$.subCategory": "Agriculture",
                "$.source": ["USDA", "ERS"],
            },
        }
    )

    period: str = Field(
        description="Row label of the observation: the year for annual tables"
        + " ('2020'), the year and month or quarter for sub-annual tables"
        + " ('2020 Jan', '2020 Q1 Sep-Nov'), with any varying State or market"
        + " city folded in so each row is uniquely labeled ('Texas — 2025').",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Period",
                "pinned": "left",
                "maxWidth": 240,
            }
        },
    )


class UsBioenergyStatisticsFetcher(
    Fetcher[
        UsBioenergyStatisticsQueryParams,
        list[UsBioenergyStatisticsData],
    ]
):
    """Fetch USDA ERS U.S. Bioenergy Statistics."""

    require_credentials = False

    @staticmethod
    def transform_query(params: dict[str, Any]) -> UsBioenergyStatisticsQueryParams:
        """Transform the query params."""
        return UsBioenergyStatisticsQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: UsBioenergyStatisticsQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Extract the selected table's long-format rows."""
        from openbb_government_us.usda.utils import ers_us_bioenergy_statistics

        return await ers_us_bioenergy_statistics.afetch_table(query.table)

    @staticmethod
    def _is_annual_token(period: str | None) -> bool:
        """Return whether a period token describes a whole year."""
        if not period:
            return True
        lowered = period.casefold()
        return period.startswith("Yr") or lowered == "annual" or "year" in lowered

    @staticmethod
    def _time_label(cadence: str, year: int, period: str | None) -> str:
        """Fold the year and any within-year period into one time label."""
        if period is None:
            return str(year)
        if cadence not in SUBANNUAL_CADENCES or (
            UsBioenergyStatisticsFetcher._is_annual_token(period)
        ):
            return str(year)
        if " to " in period:
            return period
        return f"{year} {period}"

    @staticmethod
    def transform_data(
        query: UsBioenergyStatisticsQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[UsBioenergyStatisticsData]:
        """Fold time and location into one period label and pivot series to columns."""
        cadence = BIOENERGY_TABLES[query.table]["cadence"]
        rows = [
            record
            for record in data
            if (query.start_year is None or record["year"] >= query.start_year)
            and (query.end_year is None or record["year"] <= query.end_year)
        ]
        fold_location = (
            len({record["location"] for record in rows if record["location"]}) > 1
        )
        pivoted: dict[str, dict] = {}
        combo_order: dict[tuple, int] = {}
        col_order: list[str] = []
        for order, record in enumerate(rows):
            year = record["year"]
            location = record["location"] if fold_location else None
            time_label = UsBioenergyStatisticsFetcher._time_label(
                cadence, year, record["period"]
            )
            label = " — ".join(part for part in (location, time_label) if part)
            row = pivoted.get(label)
            if row is None:
                combo = (location,)
                combo_order.setdefault(combo, len(combo_order))
                row = {
                    "_combo": combo_order[combo],
                    "_year": year,
                    "_period_ord": record["period_ord"],
                    "_order": order,
                    "period": label,
                }
                pivoted[label] = row
            column = record["series"]
            if column not in col_order:
                col_order.append(column)
            row[column] = record["value"]
        results = sorted(
            pivoted.values(),
            key=lambda row: (
                row["_combo"],
                row["_year"],
                row["_period_ord"],
                row["_order"],
            ),
        )
        validated: list[UsBioenergyStatisticsData] = []
        for row in results:
            payload = {"period": row["period"]}
            for column in col_order:
                payload[column] = row.get(column)
            validated.append(UsBioenergyStatisticsData.model_validate(payload))
        return validated
