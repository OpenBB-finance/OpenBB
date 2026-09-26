"""USDA ERS Agricultural Productivity Model."""

from typing import Any

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.app.service.system_service import SystemService
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import ConfigDict, Field, field_validator, model_validator

from openbb_government_us.usda.utils.ers_agricultural_productivity import (
    AGRICULTURAL_PRODUCTIVITY_FILES,
    NATIONAL_STATE,
    allowed_states,
)
from openbb_government_us.utils.serializers import NullTokenMixin

api_prefix = SystemService().system_settings.api_settings.prefix

DEFAULT_TABLE = "national_indices"
DEFAULT_STATE = NATIONAL_STATE


class AgriculturalProductivityQueryParams(QueryParams):
    """USDA ERS Agricultural Productivity Query Parameters.

    Source: https://www.ers.usda.gov/data-products/agricultural-productivity-in-the-united-states
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
                    for key, config in AGRICULTURAL_PRODUCTIVITY_FILES.items()
                ],
                "style": {"popupWidth": 520},
            },
        },
        "state": {
            "x-widget_config": {
                "label": "State",
                "type": "endpoint",
                "value": DEFAULT_STATE,
                "multiSelect": False,
                "multiple": False,
                "optionsEndpoint": f"{api_prefix}/usda/agricultural_productivity_states",
                "optionsParams": {"table": "$table"},
                "style": {"popupWidth": 280},
            },
        },
        "start_year": {"x-widget_config": {"label": "Start year"}},
        "end_year": {"x-widget_config": {"label": "End year"}},
    }

    table: str = Field(
        default=DEFAULT_TABLE,
        description="Productivity table to retrieve. Each table is a set of"
        + " named index series indexed by year; the series become the wide"
        + " value columns while year, and the State for the relative-levels"
        + " table, stay as pinned row columns. The national tables cover the"
        + " United States; the relative-levels table covers the 48 contiguous"
        + " States. Valid tables are:\n    "
        + ", ".join(AGRICULTURAL_PRODUCTIVITY_FILES)
        + "\n",
    )
    state: str = Field(
        default=DEFAULT_STATE,
        description="State to retrieve for the relative-levels table, as a"
        + " two-letter code, or 'US' for the national tables. The national"
        + " tables are published for the United States only; a State value is"
        + " ignored for them.",
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
        table = v[0] if isinstance(v, (list, tuple)) else v
        table = str(table).strip()
        if table not in AGRICULTURAL_PRODUCTIVITY_FILES:
            raise OpenBBError(
                f"Invalid table: {table}. Valid tables are: "
                + ", ".join(AGRICULTURAL_PRODUCTIVITY_FILES)
            )
        return table

    @field_validator("state", mode="before", check_fields=False)
    @classmethod
    def _validate_state(cls, v):
        """Normalize the state to a two-letter code, defaulting to 'US'."""
        if not v:
            return DEFAULT_STATE
        value = v[0] if isinstance(v, (list, tuple)) else v
        return str(value).strip().upper() or DEFAULT_STATE

    @model_validator(mode="after")
    def _reconcile_state(self):
        """Coerce the state to one published for the selected table."""
        codes = allowed_states(self.table)
        if self.state not in codes:
            self.state = codes[0]
        return self


class AgriculturalProductivityData(NullTokenMixin, Data):
    """USDA ERS Agricultural Productivity.

    One selected productivity table pivoted to a wide layout: year stays in
    the rows while the table's series dimension spreads into value columns,
    whose set varies by table.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "x-widget_config": {
                "$.name": "USDA ERS Agricultural Productivity",
                "$.description": "Farm output, input, and total factor"
                " productivity indices for the United States, and the relative"
                " productivity levels of the 48 contiguous States, published by"
                " the USDA Economic Research Service.",
                "$.category": "Economy",
                "$.subCategory": "Agriculture",
                "$.source": ["USDA", "ERS"],
            },
        }
    )

    year: int = Field(
        description="Year of the observation.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Year",
                "cellDataType": "text",
                "pinned": "left",
                "maxWidth": 90,
            }
        },
    )
    state: str | None = Field(
        default=None,
        description="State of the observation, or 'United States' for the"
        + " national tables.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "State",
                "pinned": "left",
                "hide": True,
            }
        },
    )


class AgriculturalProductivityFetcher(
    Fetcher[
        AgriculturalProductivityQueryParams,
        list[AgriculturalProductivityData],
    ]
):
    """Fetch USDA ERS Agricultural Productivity."""

    require_credentials = False

    @staticmethod
    def transform_query(params: dict[str, Any]) -> AgriculturalProductivityQueryParams:
        """Transform the query params."""
        return AgriculturalProductivityQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: AgriculturalProductivityQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Extract the selected table's long-format rows."""
        from openbb_government_us.usda.utils import ers_agricultural_productivity

        return await ers_agricultural_productivity.afetch_table(query.table)

    @staticmethod
    def transform_data(
        query: AgriculturalProductivityQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[AgriculturalProductivityData]:
        """Pivot the series into columns, one row per year, oldest year first."""
        from openbb_government_us.usda.utils.ers_agricultural_productivity import (
            STATE_LABELS,
        )

        state_label = STATE_LABELS.get(query.state, query.state)
        series_order: list[str] = []
        seen_series: set[str] = set()
        pivoted: dict[int, dict] = {}
        for record in data:
            if record["state"] is not None and record["state"] != query.state:
                continue
            year = record["year"]
            if query.start_year is not None and year < query.start_year:
                continue
            if query.end_year is not None and year > query.end_year:
                continue
            row = pivoted.get(year)
            if row is None:
                row = {"year": year, "state": state_label}
                pivoted[year] = row
            series = record["series"]
            if series not in seen_series:
                seen_series.add(series)
                series_order.append(series)
            row[series] = record["value"]
        if not pivoted:
            raise EmptyDataError("No records match the given filters.")
        results: list[AgriculturalProductivityData] = []
        for year in sorted(pivoted):
            row = pivoted[year]
            ordered = {"year": row["year"], "state": row["state"]}
            for series in series_order:
                if series in row:
                    ordered[series] = row[series]
            results.append(AgriculturalProductivityData.model_validate(ordered))
        return results
