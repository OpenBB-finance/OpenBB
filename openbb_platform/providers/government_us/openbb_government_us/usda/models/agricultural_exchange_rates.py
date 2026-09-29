"""Agricultural Exchange Rates Model."""

from typing import Any

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import ConfigDict, Field, field_validator, model_validator

from openbb_government_us.usda.utils.ers_agricultural_exchange_rates import (
    BILATERAL_REGIONS,
    EXCHANGE_RATE_FILES,
    INDEX_WEIGHTS,
)
from openbb_government_us.utils.serializers import NullTokenMixin

DEFAULT_TABLE = "real_index_annual"
DEFAULT_WEIGHTS = "U.S. markets (U.S. export weights)"


class AgriculturalExchangeRatesQueryParams(QueryParams):
    """Agricultural Exchange Rates Query Parameters.

    Source: https://www.ers.usda.gov/data-products/agricultural-exchange-rate-data-set
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
                    for key, config in EXCHANGE_RATE_FILES.items()
                ],
                "style": {"popupWidth": 420},
            },
        },
        "weights": {
            "x-widget_config": {
                "label": "Weight scheme",
                "value": DEFAULT_WEIGHTS,
                "multiSelect": False,
                "multiple": False,
                "options": [
                    {"label": scheme, "value": scheme} for scheme in INDEX_WEIGHTS
                ],
                "style": {"popupWidth": 360},
            },
        },
        "region": {
            "x-widget_config": {
                "label": "Region",
                "multiSelect": False,
                "multiple": False,
                "options": [
                    {"label": region, "value": region} for region in BILATERAL_REGIONS
                ],
                "style": {"popupWidth": 260},
            },
        },
        "start_year": {"x-widget_config": {"label": "Start year"}},
        "end_year": {"x-widget_config": {"label": "End year"}},
    }

    table: str = Field(
        default=DEFAULT_TABLE,
        description="Exchange-rate table to retrieve. Each table pivots to a wide"
        + " layout with time in the rows and the commodity (index tables) or"
        + " partner country (bilateral tables) in the value columns."
        + " Valid tables are:\n    "
        + ", ".join(EXCHANGE_RATE_FILES)
        + "\n",
    )
    weights: str | None = Field(
        default=DEFAULT_WEIGHTS,
        description="Trade-weight scheme to keep for the index tables. Defaults to"
        + " the U.S. export-weighted index. Set to None to stack all three schemes"
        + " as a pinned row dimension. Ignored for the bilateral tables."
        + " Valid schemes are:\n    "
        + ", ".join(INDEX_WEIGHTS)
        + "\n",
    )
    region: str | None = Field(
        default=None,
        description="Region to keep for the bilateral tables, filtering which"
        + " partner-country columns appear. If None, all partner countries are"
        + " returned. Ignored for the index tables. Valid regions are:\n    "
        + ", ".join(BILATERAL_REGIONS)
        + "\n",
    )
    start_year: int | None = Field(
        default=None,
        description="Start year for filtering the data."
        + " If None, returns from the beginning of the series.",
    )
    end_year: int | None = Field(
        default=None,
        description="End year for filtering the data."
        + " If None, returns up to the most recent year.",
    )

    @field_validator("table", mode="before", check_fields=False)
    @classmethod
    def _validate_table(cls, v):
        """Validate table."""
        if not v:
            return DEFAULT_TABLE
        table = v[0] if isinstance(v, (list, tuple)) else v
        table = str(table).strip()
        if table not in EXCHANGE_RATE_FILES:
            raise OpenBBError(
                f"Invalid table: {table}. Valid tables are: "
                + ", ".join(EXCHANGE_RATE_FILES)
            )
        return table

    @field_validator("weights", "region", mode="before", check_fields=False)
    @classmethod
    def _validate_optional_filters(cls, v):
        """Normalize an optional filter to a stripped string or None."""
        if not v:
            return None
        value = v[0] if isinstance(v, (list, tuple)) else v
        return str(value).strip() or None

    @model_validator(mode="after")
    def _validate_filter_scope(self):
        """Validate an applied filter's value against the table's dimension set."""
        kind = EXCHANGE_RATE_FILES[self.table]["kind"]
        if (
            kind == "index"
            and self.weights is not None
            and (self.weights not in INDEX_WEIGHTS)
        ):
            raise OpenBBError(
                f"Invalid weight scheme: {self.weights}. Valid schemes are: "
                + ", ".join(INDEX_WEIGHTS)
            )
        if (
            kind == "bilateral"
            and self.region is not None
            and (self.region not in BILATERAL_REGIONS)
        ):
            raise OpenBBError(
                f"Invalid region: {self.region}. Valid regions are: "
                + ", ".join(BILATERAL_REGIONS)
            )
        return self


class AgriculturalExchangeRatesData(NullTokenMixin, Data):
    """Agricultural Exchange Rates Data.

    One selected exchange-rate table pivoted to a wide layout: time stays in
    the rows while the commodity (index tables) or partner country (bilateral
    tables) spreads into value columns, whose set varies by table.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "x-widget_config": {
                "$.name": "USDA ERS Agricultural Exchange Rates",
                "$.description": "Real and nominal agricultural exchange rates,"
                " as commodity trade-weighted indexes and bilateral local-currency"
                " rates per U.S. dollar, published by the USDA Economic Research"
                " Service.",
                "$.category": "Economy",
                "$.subCategory": "Agriculture",
                "$.source": ["USDA", "ERS"],
            },
        }
    )

    period: str = Field(
        description="Row label of the observation: the year for annual tables"
        + " ('1970'), the year and month for monthly tables ('1970 January'),"
        + " with the trade-weight scheme prefixed when more than one scheme is"
        + " shown at once.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Period",
                "pinned": "left",
                "maxWidth": 320,
            }
        },
    )


class AgriculturalExchangeRatesFetcher(
    Fetcher[
        AgriculturalExchangeRatesQueryParams,
        list[AgriculturalExchangeRatesData],
    ]
):
    """Fetch USDA ERS Agricultural Exchange Rate Data Set."""

    require_credentials = False

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> AgriculturalExchangeRatesQueryParams:
        """Transform the query params."""
        return AgriculturalExchangeRatesQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: AgriculturalExchangeRatesQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Extract the selected table's long-format rows."""
        from openbb_government_us.usda.utils import ers_agricultural_exchange_rates

        return await ers_agricultural_exchange_rates.afetch_table(query.table)

    @staticmethod
    def _period_label(
        weights: str | None, year: int, month: str | None, weights_vary: bool
    ) -> str:
        """Fold the weight scheme, year, and month into one readable label."""
        time_label = f"{year} {month}" if month else str(year)
        if weights_vary and weights:
            return f"{weights} — {time_label}"
        return time_label

    @staticmethod
    def transform_data(
        query: AgriculturalExchangeRatesQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[AgriculturalExchangeRatesData]:
        """Filter, then pivot into period rows with the series as columns."""
        kind = EXCHANGE_RATE_FILES[query.table]["kind"]
        filtered: list[dict] = []
        for record in data:
            year = record["year"]
            if query.start_year is not None and year < query.start_year:
                continue
            if query.end_year is not None and year > query.end_year:
                continue
            if (
                kind == "index"
                and query.weights is not None
                and record["weights"] != query.weights
            ):
                continue
            if (
                kind == "bilateral"
                and query.region is not None
                and record["region"] != query.region
            ):
                continue
            filtered.append(record)
        if not filtered:
            raise EmptyDataError("No records match the given filters.")
        weights_vary = len({r["weights"] for r in filtered if r["weights"]}) > 1
        pivoted: dict[tuple, dict] = {}
        column_order: list[str] = []
        seen_columns: set[str] = set()
        for record in filtered:
            weights = record["weights"]
            key = (weights, record["year"], record["month"])
            row = pivoted.get(key)
            if row is None:
                row = {
                    "_weights_order": (
                        INDEX_WEIGHTS.index(weights)
                        if weights in INDEX_WEIGHTS
                        else len(INDEX_WEIGHTS)
                    ),
                    "_year": record["year"],
                    "_month_order": record["month_order"] or 0,
                    "period": AgriculturalExchangeRatesFetcher._period_label(
                        weights, record["year"], record["month"], weights_vary
                    ),
                }
                pivoted[key] = row
            if record["series"] not in seen_columns:
                seen_columns.add(record["series"])
                column_order.append(record["series"])
            row[record["series"]] = record["value"]
        results = sorted(
            pivoted.values(),
            key=lambda row: (
                row["_weights_order"],
                -row["_year"],
                -row["_month_order"],
            ),
        )
        validated: list[AgriculturalExchangeRatesData] = []
        for row in results:
            payload: dict[str, Any] = {"period": row["period"]}
            for column in column_order:
                payload[column] = row.get(column)
            validated.append(AgriculturalExchangeRatesData.model_validate(payload))
        return validated
