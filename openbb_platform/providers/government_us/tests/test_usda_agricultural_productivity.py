"""Tests for the USDA ERS Agricultural Productivity utils and model."""

import asyncio
import csv
from io import StringIO

import pytest
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.utils.errors import EmptyDataError

from openbb_government_us.usda.models.agricultural_productivity import (
    DEFAULT_STATE,
    DEFAULT_TABLE,
    AgriculturalProductivityData,
    AgriculturalProductivityFetcher,
    AgriculturalProductivityQueryParams,
)
from openbb_government_us.usda.utils import ers_agricultural_productivity
from openbb_government_us.usda.utils.ers_agricultural_productivity import (
    AGRICULTURAL_PRODUCTIVITY_FILES,
    CONTIGUOUS_STATES,
    PRODUCT_PAGE,
    allowed_states,
    parse_table,
    state_options,
)

NATIONAL_HEADER = ["Year", "Attribute", "Value"]
STATE_HEADER = [
    "ID",
    "Variable Name",
    "Variable Description",
    "State",
    "Units",
    "Year",
    "Value",
]


def _make_csv(header, rows):
    """Serialize a header and rows to CSV text."""
    buffer = StringIO()
    writer = csv.writer(buffer)
    writer.writerow(header)
    for row in rows:
        writer.writerow(row)
    return buffer.getvalue()


NATIONAL_CSV = _make_csv(
    NATIONAL_HEADER,
    [
        [1948, "Total agricultural output", "0.35175"],
        [1948, "Crops output: Total", "0.33548"],
        [1948, "Farm inputs: Total ", "0.95063"],
        [1948, "Total factor productivity (TFP)", "0.37002"],
        [1949, "Total agricultural output", "0.34635"],
        [1949, "Crops output: Total", "0.32470"],
        [1949, "Farm inputs: Total ", "0.96352"],
        [1949, "Total factor productivity (TFP)", "0.35946"],
        [1949, "Energy price", ""],
        [99, "Total agricultural output", "5.0"],
        [1950, "", "9.9"],
    ],
)

STATE_CSV = _make_csv(
    STATE_HEADER,
    [
        [
            "1",
            "Total agricultural output quantity index",
            "desc A",
            "CA",
            "Index",
            1960,
            "3.1712",
        ],
        ["2", "Total input quantity index", "desc B", "CA", "Index", 1960, "3.8544"],
        ["3", "Total factor productivity", "desc C", "CA", "Ratio", 1960, "0.85801"],
        [
            "4",
            "Total agricultural output quantity index",
            "desc A",
            "ca",
            "Index",
            1961,
            "3.1969",
        ],
        ["5", "Total input quantity index", "desc B", "CA", "Index", 1961, "3.9338"],
        ["6", "Total factor productivity", "desc C", "CA", "Ratio", 1961, "0.84751"],
        [
            "7",
            "Total agricultural output quantity index",
            "desc A",
            "AL",
            "Index",
            1960,
            "1.0",
        ],
        ["8", "Total factor productivity", "desc C", "AL", "Ratio", 1960, "1.0"],
    ],
)


class TestErsAgriculturalProductivityUtils:
    """Tests for the ers_agricultural_productivity utils module."""

    def test_catalog_contents(self):
        """The catalog holds the three tables with their pivot configuration."""
        assert set(AGRICULTURAL_PRODUCTIVITY_FILES) == {
            "national_indices",
            "national_price_quantity",
            "state_relative_levels",
        }
        assert DEFAULT_TABLE in AGRICULTURAL_PRODUCTIVITY_FILES
        national = {
            key
            for key, config in AGRICULTURAL_PRODUCTIVITY_FILES.items()
            if config["geography"] == "national"
        }
        assert national == {"national_indices", "national_price_quantity"}
        for key, config in AGRICULTURAL_PRODUCTIVITY_FILES.items():
            assert config["label"]
            assert config["media"].startswith("/media/")
            assert config["media"].endswith(".csv")
            assert config["year_col"] == "Year"
            assert config["value_col"] == "Value"
            if config["geography"] == "state":
                assert config["state_col"] == "State"
                assert config["series_col"] == "Variable Name"
            else:
                assert config["state_col"] is None
                assert config["series_col"] == "Attribute"

    def test_contiguous_states_count(self):
        """The contiguous-state list holds exactly the 48 codes, no US."""
        assert len(CONTIGUOUS_STATES) == 48
        assert "US" not in CONTIGUOUS_STATES
        assert "AK" not in CONTIGUOUS_STATES
        assert "HI" not in CONTIGUOUS_STATES
        assert CONTIGUOUS_STATES[0] == "AL"

    def test_allowed_states_national(self):
        """A national table is published for the United States only."""
        assert allowed_states("national_indices") == ("US",)
        assert allowed_states("national_price_quantity") == ("US",)

    def test_allowed_states_state(self):
        """The relative-levels table is published for the 48 contiguous States."""
        assert allowed_states("state_relative_levels") == CONTIGUOUS_STATES

    def test_allowed_states_unknown(self):
        """An unknown table falls back to the national aggregate."""
        assert allowed_states("bogus") == ("US",)

    def test_state_options_national(self):
        """A national table offers a single United States option."""
        assert state_options("national_indices") == [
            {"label": "United States", "value": "US"}
        ]

    def test_state_options_state(self):
        """The state table offers 48 labeled options, Alabama first."""
        options = state_options("state_relative_levels")
        assert len(options) == 48
        assert options[0] == {"label": "Alabama", "value": "AL"}

    def test_parse_national_table(self):
        """A national table parses to state-less records with verbatim series."""
        records = parse_table(NATIONAL_CSV, "national_indices")
        assert len(records) == 8
        first = records[0]
        assert first == {
            "table": "national_indices",
            "year": 1948,
            "state": None,
            "series": "Total agricultural output",
            "value": 0.35175,
        }
        assert records[2]["series"] == "Farm inputs: Total"

    def test_parse_state_table(self):
        """The state table keeps the State code and Variable Name series."""
        records = parse_table(STATE_CSV, "state_relative_levels")
        assert len(records) == 8
        assert {record["state"] for record in records} == {"CA", "AL"}
        assert records[0] == {
            "table": "state_relative_levels",
            "year": 1960,
            "state": "CA",
            "series": "Total agricultural output quantity index",
            "value": 3.1712,
        }
        assert "desc A" not in records[0].values()
        assert "Index" not in records[0].values()

    def test_parse_state_uppercases_code(self):
        """A lower-case State code is normalized to upper case."""
        records = parse_table(STATE_CSV, "state_relative_levels")
        assert all(record["state"] in {"CA", "AL"} for record in records)

    def test_parse_skips_blank_value_and_bad_year(self):
        """A blank value and a non-four-digit year are both skipped."""
        records = parse_table(NATIONAL_CSV, "national_indices")
        assert 5.0 not in [record["value"] for record in records]
        assert all(record["year"] in {1948, 1949} for record in records)

    def test_parse_skips_blank_series(self):
        """A row with a blank series is skipped and yields no year row."""
        records = parse_table(NATIONAL_CSV, "national_indices")
        assert all(record["series"] for record in records)
        assert 1950 not in {record["year"] for record in records}

    def test_afetch_table(self, monkeypatch):
        """afetch_table fetches the CSV through the ERS cache and parses it."""
        calls = []

        async def fake_afetch_ers_file(media_path, product=None, ttl=None):
            calls.append((media_path, product))
            return NATIONAL_CSV.encode("utf-8-sig")

        monkeypatch.setattr(
            "openbb_government_us.usda.utils.ers_client.afetch_ers_file",
            fake_afetch_ers_file,
        )
        records = asyncio.run(
            ers_agricultural_productivity.afetch_table("national_indices")
        )
        assert calls == [
            (
                AGRICULTURAL_PRODUCTIVITY_FILES["national_indices"]["media"],
                PRODUCT_PAGE,
            )
        ]
        assert len(records) == 8


class TestAgriculturalProductivity:
    """Tests for the AgriculturalProductivity model."""

    def test_transform_query_default_table(self):
        """transform_query defaults the table and keeps year filters."""
        query = AgriculturalProductivityFetcher.transform_query({"start_year": 2000})
        assert isinstance(query, AgriculturalProductivityQueryParams)
        assert query.table == DEFAULT_TABLE
        assert query.state == DEFAULT_STATE
        assert query.start_year == 2000

    def test_table_blank_returns_default(self):
        """A blank or None table normalizes to the default table."""
        assert AgriculturalProductivityQueryParams(table=None).table == DEFAULT_TABLE
        assert AgriculturalProductivityQueryParams(table="").table == DEFAULT_TABLE

    def test_table_accepts_list(self):
        """A single-item list table value is unwrapped."""
        query = AgriculturalProductivityQueryParams(table=["national_price_quantity"])
        assert query.table == "national_price_quantity"

    def test_table_strips_whitespace(self):
        """A padded table value is stripped before validation."""
        query = AgriculturalProductivityQueryParams(table="  state_relative_levels  ")
        assert query.table == "state_relative_levels"

    def test_unknown_table_raises(self):
        """An unknown table raises OpenBBError listing valid choices."""
        with pytest.raises(OpenBBError, match="Invalid table: bogus"):
            AgriculturalProductivityQueryParams(table="bogus")

    def test_non_string_table_raises(self):
        """A non-string, non-empty table value raises OpenBBError."""
        with pytest.raises(OpenBBError, match="Invalid table"):
            AgriculturalProductivityQueryParams(table=123)

    def test_state_blank_returns_default(self):
        """A blank or None state normalizes to the default state."""
        assert AgriculturalProductivityQueryParams(state=None).state == DEFAULT_STATE
        assert AgriculturalProductivityQueryParams(state="").state == DEFAULT_STATE

    def test_state_accepts_list(self):
        """A single-item list state value is unwrapped and upper-cased."""
        query = AgriculturalProductivityQueryParams(
            table="state_relative_levels", state=["ca"]
        )
        assert query.state == "CA"

    def test_national_table_ignores_state(self):
        """A national table coerces any State value back to 'US'."""
        query = AgriculturalProductivityQueryParams(
            table="national_indices", state="CA"
        )
        assert query.state == "US"

    def test_state_table_coerces_stale_us(self):
        """The state table coerces a stale 'US' value to the first State."""
        query = AgriculturalProductivityQueryParams(
            table="state_relative_levels", state="US"
        )
        assert query.state == "AL"

    def test_state_table_coerces_invalid(self):
        """The state table coerces an out-of-range code to the first State."""
        query = AgriculturalProductivityQueryParams(
            table="state_relative_levels", state="ZZ"
        )
        assert query.state == "AL"

    def test_state_table_keeps_valid(self):
        """The state table keeps a valid contiguous-State code."""
        query = AgriculturalProductivityQueryParams(
            table="state_relative_levels", state="ca"
        )
        assert query.state == "CA"

    def test_aextract_data_fetches_selected_table(self, monkeypatch):
        """aextract_data fetches only the selected table's rows."""
        fetched = []

        async def fake_afetch_table(table, **kwargs):
            fetched.append(table)
            return [{"table": table}]

        monkeypatch.setattr(
            ers_agricultural_productivity, "afetch_table", fake_afetch_table
        )
        query = AgriculturalProductivityFetcher.transform_query(
            {"table": "national_price_quantity"}
        )
        records = asyncio.run(
            AgriculturalProductivityFetcher.aextract_data(query, None)
        )
        assert fetched == ["national_price_quantity"]
        assert records == [{"table": "national_price_quantity"}]

    def test_transform_data_pivots_series_into_columns(self):
        """Each series becomes a column, one row per year."""
        records = parse_table(NATIONAL_CSV, "national_indices")
        query = AgriculturalProductivityFetcher.transform_query({})
        data = AgriculturalProductivityFetcher.transform_data(query, records)
        first = data[0].model_dump()
        assert first["year"] == 1948
        assert first["state"] == "United States"
        assert first["Total agricultural output"] == 0.35175
        assert first["Crops output: Total"] == 0.33548
        assert first["Farm inputs: Total"] == 0.95063
        assert first["Total factor productivity (TFP)"] == 0.37002

    def test_transform_data_orders_chronologically(self):
        """Rows sort by year, oldest first."""
        records = parse_table(NATIONAL_CSV, "national_indices")
        query = AgriculturalProductivityFetcher.transform_query({})
        data = AgriculturalProductivityFetcher.transform_data(query, records)
        assert [row.year for row in data] == [1948, 1949]

    def test_transform_data_series_column_order(self):
        """Dynamic columns keep the source series order across all rows."""
        records = parse_table(NATIONAL_CSV, "national_indices")
        query = AgriculturalProductivityFetcher.transform_query({})
        data = AgriculturalProductivityFetcher.transform_data(query, records)
        keys = list(data[0].model_dump(by_alias=True))
        assert keys == [
            "year",
            "state",
            "Total agricultural output",
            "Crops output: Total",
            "Farm inputs: Total",
            "Total factor productivity (TFP)",
        ]

    def test_transform_data_filters_years(self):
        """start_year and end_year filter rows on the integer year."""
        records = parse_table(NATIONAL_CSV, "national_indices")
        start = AgriculturalProductivityFetcher.transform_data(
            AgriculturalProductivityFetcher.transform_query({"start_year": 1949}),
            records,
        )
        assert {row.year for row in start} == {1949}
        end = AgriculturalProductivityFetcher.transform_data(
            AgriculturalProductivityFetcher.transform_query({"end_year": 1948}),
            records,
        )
        assert {row.year for row in end} == {1948}

    def test_transform_data_state_table_filters_to_state(self):
        """The state table keeps only the selected State's rows."""
        records = parse_table(STATE_CSV, "state_relative_levels")
        query = AgriculturalProductivityFetcher.transform_query(
            {"table": "state_relative_levels", "state": "CA"}
        )
        data = AgriculturalProductivityFetcher.transform_data(query, records)
        assert [row.year for row in data] == [1960, 1961]
        first = data[0].model_dump()
        assert first["state"] == "California"
        assert first["Total agricultural output quantity index"] == 3.1712
        assert first["Total input quantity index"] == 3.8544
        assert first["Total factor productivity"] == 0.85801

    def test_transform_data_state_table_missing_series(self):
        """A State row lacking a series omits that column, keeping the rest."""
        records = parse_table(STATE_CSV, "state_relative_levels")
        query = AgriculturalProductivityFetcher.transform_query(
            {"table": "state_relative_levels", "state": "AL"}
        )
        data = AgriculturalProductivityFetcher.transform_data(query, records)
        assert [row.year for row in data] == [1960]
        dumped = data[0].model_dump()
        assert dumped["state"] == "Alabama"
        assert dumped["Total agricultural output quantity index"] == 1.0
        assert dumped["Total factor productivity"] == 1.0
        assert "Total input quantity index" not in dumped

    def test_transform_data_empty_raises(self):
        """A filter that matches nothing raises EmptyDataError."""
        records = parse_table(NATIONAL_CSV, "national_indices")
        query = AgriculturalProductivityFetcher.transform_query({"start_year": 3000})
        with pytest.raises(EmptyDataError):
            AgriculturalProductivityFetcher.transform_data(query, records)

    def test_transform_data_preserves_precision(self):
        """Dynamic value columns keep full source precision."""
        records = parse_table(STATE_CSV, "state_relative_levels")
        query = AgriculturalProductivityFetcher.transform_query(
            {"table": "state_relative_levels", "state": "CA"}
        )
        data = AgriculturalProductivityFetcher.transform_data(query, records)
        assert data[1].model_dump()["Total factor productivity"] == 0.84751

    def test_query_params_widget_options(self):
        """The table param exposes the three tables as a single-select filter."""
        config = AgriculturalProductivityQueryParams.__json_schema_extra__["table"][
            "x-widget_config"
        ]
        assert config["multiSelect"] is False
        assert config["multiple"] is False
        assert config["value"] == DEFAULT_TABLE
        assert len(config["options"]) == 3

    def test_state_param_dependent_endpoint(self):
        """The state param is a single-select endpoint keyed off the table."""
        config = AgriculturalProductivityQueryParams.__json_schema_extra__["state"][
            "x-widget_config"
        ]
        assert config["type"] == "endpoint"
        assert config["multiSelect"] is False
        assert config["multiple"] is False
        assert config["value"] == DEFAULT_STATE
        assert config["optionsEndpoint"].endswith(
            "/usda/agricultural_productivity_states"
        )
        assert config["optionsParams"] == {"table": "$table"}

    def test_widget_model_config(self):
        """The whole-widget config carries the name, category, and source."""
        config = AgriculturalProductivityData.model_config["json_schema_extra"][
            "x-widget_config"
        ]
        assert config["$.name"] == "USDA ERS Agricultural Productivity"
        assert config["$.category"] == "Economy"
        assert config["$.subCategory"] == "Agriculture"
        assert config["$.source"] == ["USDA", "ERS"]

    def test_state_field_hidden(self):
        """The optional State dimension is hidden by default, not excluded."""
        extra = AgriculturalProductivityData.model_fields["state"].json_schema_extra
        config = extra["x-widget_config"]
        assert config["hide"] is True
        assert "exclude" not in config

    def test_columns_defs_bind_to_served_keys(self):
        """Every non-excluded field binds to a served key, dynamics included."""
        records = parse_table(NATIONAL_CSV, "national_indices")
        query = AgriculturalProductivityFetcher.transform_query({})
        data = AgriculturalProductivityFetcher.transform_data(query, records)
        served = set(data[0].model_dump(by_alias=True))
        fields = AgriculturalProductivityData.model_fields
        for name, field in fields.items():
            extra = (field.json_schema_extra or {}).get("x-widget_config", {})
            if extra.get("exclude"):
                continue
            assert name in served
        dynamic = served - set(fields)
        assert "Total agricultural output" in dynamic
        assert "Total factor productivity (TFP)" in dynamic
