"""USDA ERS State Agricultural Trade Model."""

from typing import Any

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.app.service.system_service import SystemService
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import ConfigDict, Field, field_validator, model_validator

from openbb_government_us.usda.utils.ers_state_agricultural_trade import (
    COMMODITIES,
    DATASET_A_STATE_NAMES,
    DEFAULT_COMMODITY,
    DEFAULT_STATE,
    DEFAULT_TABLE,
    STATE_CODE_TO_NAME,
    STATE_NAME_TO_CODE,
    STATE_SCOPED_TABLES,
    TABLE_LABELS,
    TABLE_UNITS,
    allowed_state_names,
    commodity_options,
)
from openbb_government_us.utils.serializers import NullTokenMixin

api_prefix = SystemService().system_settings.api_settings.prefix


class StateAgriculturalTradeQueryParams(QueryParams):
    """USDA ERS State Agricultural Trade Query Parameters.

    Source: https://www.ers.usda.gov/data-products/state-agricultural-trade-data
    """

    __json_schema_extra__ = {
        "table": {
            "x-widget_config": {
                "label": "Table",
                "value": DEFAULT_TABLE,
                "multiSelect": False,
                "multiple": False,
                "options": [
                    {"label": label, "value": key}
                    for key, label in TABLE_LABELS.items()
                ],
                "style": {"popupWidth": 420},
            },
        },
        "state": {
            "x-widget_config": {
                "label": "State",
                "type": "endpoint",
                "value": DEFAULT_STATE,
                "multiSelect": False,
                "multiple": False,
                "optionsEndpoint": f"{api_prefix}/usda/state_ag_trade_states",
                "optionsParams": {"table": "$table"},
                "style": {"popupWidth": 280},
            },
        },
        "commodity": {
            "x-widget_config": {
                "label": "Commodity (exports by state)",
                "value": DEFAULT_COMMODITY,
                "multiSelect": False,
                "multiple": False,
                "options": commodity_options(),
                "style": {"popupWidth": 320},
            },
        },
        "start_year": {"x-widget_config": {"label": "Start year"}},
        "end_year": {"x-widget_config": {"label": "End year"}},
    }

    table: str = Field(
        default=DEFAULT_TABLE,
        description="Table to retrieve. 'exports_by_commodity' spreads a state's"
        + " export commodities across the calendar years; 'exports_by_state'"
        + " spreads the states across the calendar years for one commodity;"
        + " 'top_exports' and 'top_imports' spread a state's top fiscal-year"
        + " commodities across the fiscal years. Valid tables are:\n    "
        + ", ".join(TABLE_LABELS)
        + "\n",
    )
    state: str = Field(
        default=DEFAULT_STATE,
        description="State whose commodities are spread into columns for the"
        + " 'exports_by_commodity', 'top_exports', and 'top_imports' tables, as"
        + " a full state name or two-letter code, or 'United States' for the"
        + " national total. Ignored by the 'exports_by_state' table. The"
        + " calendar-year tables cover the 50 states and the United States; the"
        + " fiscal-year tables also cover the District of Columbia, Puerto Rico,"
        + " and the Virgin Islands.",
    )
    commodity: str = Field(
        default=DEFAULT_COMMODITY,
        description="Commodity whose states are spread into columns for the"
        + " 'exports_by_state' table. Ignored by the other tables. Valid"
        + " commodities are:\n    "
        + ", ".join(COMMODITIES)
        + "\n",
    )
    start_year: int | None = Field(
        default=None,
        description="Start year for filtering the data, compared against the"
        + " calendar or fiscal year. If None, returns from the first published"
        + " year.",
    )
    end_year: int | None = Field(
        default=None,
        description="End year for filtering the data, compared against the"
        + " calendar or fiscal year. If None, returns up to the most recent"
        + " year.",
    )

    @field_validator("table", mode="before", check_fields=False)
    @classmethod
    def _validate_table(cls, v):
        """Validate table."""
        if not v:
            return DEFAULT_TABLE
        value = v[0] if isinstance(v, (list, tuple)) else v
        value = str(value).strip()
        if value not in TABLE_LABELS:
            raise OpenBBError(
                f"Invalid table: {value}. Valid tables are: " + ", ".join(TABLE_LABELS)
            )
        return value

    @field_validator("state", mode="before", check_fields=False)
    @classmethod
    def _validate_state(cls, v):
        """Validate state, accepting a full name or a two-letter code."""
        if not v:
            return DEFAULT_STATE
        value = v[0] if isinstance(v, (list, tuple)) else v
        value = str(value).strip()
        if value.upper() in STATE_CODE_TO_NAME:
            return STATE_CODE_TO_NAME[value.upper()]
        if value in STATE_NAME_TO_CODE:
            return value
        raise OpenBBError(
            f"Invalid state: {value}. Valid states are: "
            + ", ".join(STATE_NAME_TO_CODE)
        )

    @field_validator("commodity", mode="before", check_fields=False)
    @classmethod
    def _validate_commodity(cls, v):
        """Validate commodity."""
        if not v:
            return DEFAULT_COMMODITY
        value = v[0] if isinstance(v, (list, tuple)) else v
        value = str(value).strip()
        if value not in COMMODITIES:
            raise OpenBBError(
                f"Invalid commodity: {value}. Valid commodities are: "
                + ", ".join(COMMODITIES)
            )
        return value

    @model_validator(mode="after")
    def _validate_state_for_table(self):
        """Validate that the state is published for a state-scoped table."""
        if self.table in STATE_SCOPED_TABLES:
            names = allowed_state_names(self.table)
            if self.state not in names:
                raise OpenBBError(
                    f"Invalid state '{self.state}' for table '{self.table}'."
                    " This table is published for: " + ", ".join(names)
                )
        return self


class StateAgriculturalTradeData(NullTokenMixin, Data):
    """USDA ERS State Agricultural Trade Data.

    One selected table pivoted to a wide layout: the years stay in the rows
    while the commodity or state dimension spreads into value columns, whose
    set is fixed for the all-data tables and varies by state for the
    top-commodity tables.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "x-widget_config": {
                "$.name": "USDA ERS State Agricultural Trade",
                "$.description": "State-level U.S. agricultural exports by"
                " commodity and by state on a calendar-year basis, and the top"
                " export and import commodities by state on a fiscal-year basis,"
                " published by the USDA Economic Research Service.",
                "$.category": "Economy",
                "$.subCategory": "Agriculture",
                "$.source": ["USDA", "ERS"],
            },
        }
    )

    year: int = Field(
        description="Calendar year for the all-data tables, or fiscal year for"
        + " the top-commodity tables.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Year",
                "cellDataType": "number",
                "pinned": "left",
                "maxWidth": 90,
            }
        },
    )
    state: str | None = Field(
        default=None,
        description="State whose commodities the columns spread, for the"
        + " commodity and top-commodity tables. None for the exports-by-state"
        + " table.",
        json_schema_extra={"x-widget_config": {"headerName": "State", "hide": True}},
    )
    commodity: str | None = Field(
        default=None,
        description="Commodity whose states the columns spread, for the"
        + " exports-by-state table. None for the other tables.",
        json_schema_extra={
            "x-widget_config": {"headerName": "Commodity", "hide": True}
        },
    )
    unit: str | None = Field(
        default=None,
        description="Unit shared by every value column: 'Million dollars' for"
        + " the calendar-year tables, 'Dollars' for the fiscal-year tables.",
        json_schema_extra={"x-widget_config": {"headerName": "Unit", "hide": True}},
    )


class StateAgriculturalTradeFetcher(
    Fetcher[
        StateAgriculturalTradeQueryParams,
        list[StateAgriculturalTradeData],
    ]
):
    """Fetch USDA ERS State Agricultural Trade."""

    require_credentials = False

    @staticmethod
    def transform_query(params: dict[str, Any]) -> StateAgriculturalTradeQueryParams:
        """Transform the query params."""
        return StateAgriculturalTradeQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: StateAgriculturalTradeQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Extract the selected table's long-format rows."""
        from openbb_government_us.usda.utils import ers_state_agricultural_trade

        return await ers_state_agricultural_trade.afetch_table(query.table)

    @staticmethod
    def transform_data(
        query: StateAgriculturalTradeQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[StateAgriculturalTradeData]:
        """Pivot the long-format rows into the selected wide table."""
        table = query.table
        unit = TABLE_UNITS[table]
        if table == "exports_by_commodity":
            records = [row for row in data if row["state"] == query.state]
            column_of = "commodity"
            order_ref: tuple[str, ...] | None = COMMODITIES
            dims = {"state": query.state, "commodity": None, "unit": unit}
        elif table == "exports_by_state":
            records = [row for row in data if row["commodity"] == query.commodity]
            column_of = "state"
            order_ref = DATASET_A_STATE_NAMES
            dims = {"state": None, "commodity": query.commodity, "unit": unit}
        else:
            code = STATE_NAME_TO_CODE.get(query.state, query.state)
            records = [row for row in data if row["state"] == code]
            column_of = "commodity"
            order_ref = None
            dims = {"state": query.state, "commodity": None, "unit": unit}

        by_year: dict[int, dict] = {}
        present: set[str] = set()
        for record in records:
            year = record["year"]
            if query.start_year is not None and year < query.start_year:
                continue
            if query.end_year is not None and year > query.end_year:
                continue
            column = record[column_of]
            present.add(column)
            row = by_year.get(year)
            if row is None:
                row = {"year": year, **dims}
                by_year[year] = row
            row[column] = record["value"]
        if not by_year:
            raise EmptyDataError("No records match the given filters.")
        if order_ref is None:
            column_order = sorted(present)
        else:
            column_order = [column for column in order_ref if column in present]
            column_order += sorted(present.difference(order_ref))
        results: list[StateAgriculturalTradeData] = []
        for year in sorted(by_year):
            source = by_year[year]
            row = {"year": year, **dims}
            for column in column_order:
                row[column] = source.get(column)
            results.append(StateAgriculturalTradeData.model_validate(row))
        return results
