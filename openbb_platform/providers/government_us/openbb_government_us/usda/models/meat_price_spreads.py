"""USDA ERS Meat Price Spreads Model."""

from typing import Any, Literal

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from pydantic import ConfigDict, Field, field_validator

from openbb_government_us.usda.utils.ers_meat_price_spreads import (
    MEAT_PRICE_SPREADS_FILES,
)
from openbb_government_us.utils.serializers import NullTokenMixin

DEFAULT_TABLE = "choice_beef"

ANNUAL_DESCRIPTORS = frozenset({"Annual", "Calendar year"})

Frequency = Literal["annual", "quarterly", "monthly"]


class MeatPriceSpreadsQueryParams(QueryParams):
    """USDA ERS Meat Price Spreads Query Parameters.

    Source: https://www.ers.usda.gov/data-products/meat-price-spreads
    """

    __json_schema_extra__ = {
        "table": {
            "x-widget_config": {
                "label": "Table",
                "multiSelect": False,
                "multiple": False,
                "value": DEFAULT_TABLE,
                "options": [
                    {"label": entry["title"], "value": key}
                    for key, entry in MEAT_PRICE_SPREADS_FILES.items()
                ],
                "style": {"popupWidth": 480},
            },
        },
        "frequency": {
            "x-widget_config": {
                "label": "Frequency",
                "multiSelect": False,
                "multiple": False,
                "options": [
                    {"label": "Annual", "value": "annual"},
                    {"label": "Quarterly", "value": "quarterly"},
                    {"label": "Monthly", "value": "monthly"},
                ],
            },
        },
        "start_year": {"x-widget_config": {"label": "Start year"}},
        "end_year": {"x-widget_config": {"label": "End year"}},
    }

    table: str = Field(
        default=DEFAULT_TABLE,
        description="Table to retrieve. Each table is a self-contained set of"
        + " data items pivoted into columns; the column set differs by table."
        + " Valid tables are:\n    "
        + ", ".join(MEAT_PRICE_SPREADS_FILES)
        + "\n",
    )
    frequency: Frequency | None = Field(
        default=None,
        description="Filter rows by observation frequency. Only the choice_beef"
        + " and pork tables mix annual, quarterly, and monthly rows; the other"
        + " tables carry only monthly rows. If None, all frequencies are"
        + " included.",
    )
    start_year: int | None = Field(
        default=None,
        description="Start year for filtering the data."
        + " None returns from the beginning of the series"
        + " (historical_monthly reaches 1970).",
    )
    end_year: int | None = Field(
        default=None,
        description="End year for filtering the data."
        + " If None, returns up to the most recent year.",
    )

    @field_validator("table", mode="before", check_fields=False)
    @classmethod
    def _validate_table(cls, v):
        """Validate the selected table key."""
        if isinstance(v, (list, tuple)):
            v = next((item for item in v if item), None)
        if not v:
            return DEFAULT_TABLE
        table = str(v).strip()
        if table not in MEAT_PRICE_SPREADS_FILES:
            raise OpenBBError(
                f"Invalid table: {table}. Valid tables are: "
                + ", ".join(MEAT_PRICE_SPREADS_FILES)
            )
        return table


class MeatPriceSpreadsData(NullTokenMixin, Data):
    """USDA ERS Meat Price Spreads Data."""

    model_config = ConfigDict(
        json_schema_extra={
            "x-widget_config": {
                "$.name": "USDA ERS Meat Price Spreads",
                "$.description": "Retail values, wholesale values, farm values,"
                " price spreads, and farmers' shares for beef, pork, poultry,"
                " and eggs, published by the USDA Economic Research Service.",
                "$.category": "Economy",
                "$.subCategory": "Agriculture",
                "$.source": ["USDA", "ERS"],
            },
        }
    )

    period: str = Field(
        description="Row label of the observation: the year for annual rows"
        + " ('2020'), the year and the within-year period for sub-annual rows"
        + " ('2020 January', '2020 Quarter 1, January-March'). The table's"
        + " published data items spread into the wide value columns.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Period",
                "pinned": "left",
                "maxWidth": 240,
            }
        },
    )


class MeatPriceSpreadsFetcher(
    Fetcher[
        MeatPriceSpreadsQueryParams,
        list[MeatPriceSpreadsData],
    ]
):
    """Fetch USDA ERS Meat Price Spreads."""

    require_credentials = False

    @staticmethod
    def transform_query(params: dict[str, Any]) -> MeatPriceSpreadsQueryParams:
        """Transform the query params."""
        return MeatPriceSpreadsQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: MeatPriceSpreadsQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Extract the selected table's long CSV rows."""
        from openbb_government_us.usda.utils import ers_meat_price_spreads

        return await ers_meat_price_spreads.afetch_table(query.table)

    @staticmethod
    def _period_label(year: int, period: str | None) -> str:
        """Fold the year and within-year period into one readable time label."""
        if not period or period.startswith("Yr") or period in ANNUAL_DESCRIPTORS:
            return str(year)
        if " to " in period:
            return period
        return f"{year} {period}"

    @staticmethod
    def transform_data(
        query: MeatPriceSpreadsQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[MeatPriceSpreadsData]:
        """Pivot the long rows into one wide row per period label."""
        pivoted: dict[tuple, dict] = {}
        col_order: list[str] = []
        for record in data:
            year = record["year"]
            if query.start_year is not None and year < query.start_year:
                continue
            if query.end_year is not None and year > query.end_year:
                continue
            if query.frequency is not None and record["frequency"] != query.frequency:
                continue
            key = (year, record["period"])
            row = pivoted.get(key)
            if row is None:
                row = {
                    "_year": year,
                    "_period_sort": record["period_number"],
                    "period": MeatPriceSpreadsFetcher._period_label(
                        year, record["period"]
                    ),
                }
                pivoted[key] = row
            column = record["data_item"]
            if column not in col_order:
                col_order.append(column)
            row[column] = record["value"]
        results = sorted(
            pivoted.values(),
            key=lambda row: (row["_year"], row["_period_sort"]),
        )
        validated: list[MeatPriceSpreadsData] = []
        for row in results:
            payload = {"period": row["period"]}
            for column in col_order:
                payload[column] = row.get(column)
            validated.append(MeatPriceSpreadsData.model_validate(payload))
        return validated
