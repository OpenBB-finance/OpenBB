"""Tests for the USDA ERS Normalized Prices utils and model."""

import asyncio
import csv
import io
import zipfile
from io import StringIO

import pytest
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.utils.errors import EmptyDataError

from openbb_government_us.usda.models.normalized_prices import (
    TABLE_OPTIONS,
    NormalizedPricesData,
    NormalizedPricesFetcher,
    NormalizedPricesQueryParams,
)
from openbb_government_us.usda.utils import ers_normalized_prices
from openbb_government_us.usda.utils.ers_normalized_prices import (
    DEFAULT_TABLE,
    INDEX_UNITS,
    MEDIA_PATH,
    NORMALIZED_PRICES_TABLES,
    PRODUCT_PAGE,
    extract_inner_csv,
    parse_column,
    parse_table,
    parse_value,
)


def _csv(header, rows):
    """Serialize a header and rows to CSV text."""
    buffer = StringIO()
    writer = csv.writer(buffer)
    writer.writerow(header)
    for row in rows:
        writer.writerow(row)
    return buffer.getvalue()


TABLE1_CSV = _csv(
    ["Commodity", "Description", "Report Year", "Price", "Units"],
    [
        ["Wheat", "all types", "2021", "4.65", "$ / bu"],
        ["Wheat", "all types", "2020", "4.93", "$ / bu"],
        ["Wheat", "all types", "2022", "4.68", "$ / bu"],
        ["Rye", "", "2020", "6.07", "$ / bu"],
        ["Rye", "", "2021", "5.72", "$ / bu"],
        ["Rye", "", "2022", "5.49", "$ / bu"],
        ["Milk", "", "2020", "18.32", "$ / cwt"],
        ["Milk", "", "2021", "17.23", "$ / cwt"],
        ["Milk", "", "2022", "17.42", "$ / cwt"],
        ["", "orphan", "2022", "1.0", "$ / bu"],
        ["Oats", "", "bad", "2.53", "$ / bu"],
    ],
)

TABLE2_CSV = _csv(
    ["Commodity", "Price index year", "Price"],
    [
        ["Index for prices received by farmers: All farm products", "2023", "118.6"],
        ["Index for prices received by farmers: All farm products", "2022", "130"],
        ["Index for prices received by farmers: All farm products", "2024", "119.5"],
        ["Index for prices paid by farmers: Fertilizer", "2022", "148.1"],
        ["Index for prices paid by farmers: Fertilizer", "2023", "110.5"],
        ["Index for prices paid by farmers: Fertilizer", "2024", "101.2"],
    ],
)

TABLE3_CSV = _csv(
    ["State", "Commodity", "Description", "Units", "Price"],
    [
        ["Alabama", "Wheat", "all types", "$/bu", "6.31"],
        ["Alaska", "Wheat", "all types", "$/bu", ""],
        ["Arizona", "Wheat", "all types", "$/bu", "8.38"],
        ["Wyoming", "Wheat", "all types", "$/bu", ""],
        ["Alabama", "Milk", "", "$/cwt", "22.04"],
        ["Alaska", "Milk", "", "$/cwt", "5.55"],
        ["Arizona", "Milk", "", "$/cwt", "19.78"],
        ["Wyoming", "Milk", "", "$/cwt", ""],
        ["", "Ghost", "", "$/bu", "9.9"],
    ],
)


def _zip_bytes():
    """Build all-tables zip bytes with the three CSVs and note members."""
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        archive.writestr("table1-national-prices-2025.csv", TABLE1_CSV)
        archive.writestr("table1-national-prices-2025-notes.txt", "notes")
        archive.writestr("table2-national-indices-2025.csv", TABLE2_CSV)
        archive.writestr("table2-national-indices-2025-notes.txt", "notes")
        archive.writestr("table3-state-prices-2025.csv", TABLE3_CSV)
        archive.writestr("table3-state-prices-2025-notes.txt", "notes")
    return buffer.getvalue()


class TestErsNormalizedPricesUtils:
    """Tests for the ers_normalized_prices utils module."""

    def test_catalog_contents(self):
        """The catalog holds the three tables with their pivot configuration."""
        assert set(NORMALIZED_PRICES_TABLES) == {
            "table1_national_prices",
            "table2_national_indices",
            "table3_state_prices",
        }
        assert DEFAULT_TABLE == "table1_national_prices"
        assert DEFAULT_TABLE in NORMALIZED_PRICES_TABLES
        prefixes = {c["csv_prefix"] for c in NORMALIZED_PRICES_TABLES.values()}
        assert prefixes == {"table1", "table2", "table3"}
        dimensions = {c["dimension"] for c in NORMALIZED_PRICES_TABLES.values()}
        assert dimensions == {"year", "state"}
        for config in NORMALIZED_PRICES_TABLES.values():
            assert config["label"]
            assert config["commodity_field"]
            assert config["column_field"]
            assert config["value_field"]

    def test_parse_value_numeric(self):
        """A numeric cell parses to a float keeping full precision."""
        assert parse_value("149.630228133494") == 149.630228133494

    def test_parse_value_blank(self):
        """A blank cell parses to None."""
        assert parse_value("") is None
        assert parse_value("   ") is None
        assert parse_value(None) is None

    def test_parse_value_non_numeric(self):
        """A non-numeric cell parses to None."""
        assert parse_value("n/a") is None

    def test_parse_column_year(self):
        """A four-digit year token parses to an integer."""
        assert parse_column("2020", "year") == 2020

    def test_parse_column_bad_year(self):
        """A non-four-digit year token parses to None."""
        assert parse_column("bad", "year") is None
        assert parse_column("202", "year") is None
        assert parse_column("", "year") is None

    def test_parse_column_state(self):
        """A State token is kept, an empty State token is None."""
        assert parse_column("Alabama", "state") == "Alabama"
        assert parse_column("  ", "state") is None

    def test_parse_table1_builds_records(self):
        """Table 1 records carry commodity, description, units, year, value."""
        records = parse_table(TABLE1_CSV, "table1_national_prices")
        wheat = [r for r in records if r["commodity"] == "Wheat"]
        assert wheat[0] == {
            "table": "table1_national_prices",
            "commodity": "Wheat",
            "description": "all types",
            "units": "$ / bu",
            "dimension": "year",
            "column": 2021,
            "value": 4.65,
            "order": 0,
        }

    def test_parse_table1_blank_description_is_none(self):
        """A blank description becomes None."""
        records = parse_table(TABLE1_CSV, "table1_national_prices")
        rye = next(r for r in records if r["commodity"] == "Rye")
        assert rye["description"] is None

    def test_parse_table1_skips_blank_commodity_and_bad_year(self):
        """Rows with no commodity or a non-year token are skipped."""
        records = parse_table(TABLE1_CSV, "table1_national_prices")
        assert all(r["commodity"] for r in records)
        assert "orphan" not in {r["description"] for r in records}
        assert all(r["column"] != "bad" for r in records)
        assert len(records) == 9

    def test_parse_table1_order_is_stable_per_group(self):
        """The first-seen order indexes each commodity group, not each row."""
        records = parse_table(TABLE1_CSV, "table1_national_prices")
        orders = {r["commodity"]: r["order"] for r in records}
        assert orders == {"Wheat": 0, "Rye": 1, "Milk": 2}

    def test_parse_table2_units_constant_and_no_description(self):
        """Table 2 stamps the index unit and carries no description."""
        records = parse_table(TABLE2_CSV, "table2_national_indices")
        assert all(r["units"] == INDEX_UNITS for r in records)
        assert all(r["description"] is None for r in records)
        assert {r["column"] for r in records} == {2022, 2023, 2024}

    def test_parse_table3_state_and_blank_value(self):
        """Table 3 keeps the State as the pivot column and blanks become None."""
        records = parse_table(TABLE3_CSV, "table3_state_prices")
        assert {r["dimension"] for r in records} == {"state"}
        alaska_wheat = next(
            r for r in records if r["commodity"] == "Wheat" and r["column"] == "Alaska"
        )
        assert alaska_wheat["value"] is None
        assert alaska_wheat["units"] == "$/bu"
        assert "Ghost" not in {r["commodity"] for r in records}

    def test_extract_inner_csv_matches_prefix(self):
        """The inner CSV is matched by prefix and endswith .csv, not the notes."""
        text = extract_inner_csv(_zip_bytes(), "table2")
        assert text.splitlines()[0] == "Commodity,Price index year,Price"

    def test_afetch_table(self, monkeypatch):
        """afetch_table fetches the zip through the ERS cache and parses one table."""
        calls = []

        async def fake_afetch_ers_file(media_path, product=None, ttl=None):
            calls.append((media_path, product))
            return _zip_bytes()

        monkeypatch.setattr(
            "openbb_government_us.usda.utils.ers_client.afetch_ers_file",
            fake_afetch_ers_file,
        )
        records = asyncio.run(
            ers_normalized_prices.afetch_table("table1_national_prices")
        )
        assert calls == [(MEDIA_PATH, PRODUCT_PAGE)]
        assert {r["commodity"] for r in records} == {"Wheat", "Rye", "Milk"}


class TestNormalizedPrices:
    """Tests for the NormalizedPrices model."""

    def test_transform_query_default_table(self):
        """transform_query defaults the table."""
        query = NormalizedPricesFetcher.transform_query({})
        assert isinstance(query, NormalizedPricesQueryParams)
        assert query.table == DEFAULT_TABLE

    def test_table_blank_returns_default(self):
        """A blank or None table normalizes to the default table."""
        assert NormalizedPricesQueryParams(table=None).table == DEFAULT_TABLE
        assert NormalizedPricesQueryParams(table="").table == DEFAULT_TABLE

    def test_table_strips_whitespace(self):
        """A padded table value is stripped before validation."""
        query = NormalizedPricesQueryParams(table="  table3_state_prices  ")
        assert query.table == "table3_state_prices"

    def test_table_list_coerced_to_first(self):
        """A single-element list table value is coerced to its first element."""
        query = NormalizedPricesQueryParams(table=["table2_national_indices"])
        assert query.table == "table2_national_indices"

    def test_unknown_table_raises(self):
        """An unknown table raises OpenBBError listing valid choices."""
        with pytest.raises(OpenBBError, match="Invalid table: bogus"):
            NormalizedPricesQueryParams(table="bogus")

    def test_non_string_table_raises(self):
        """A non-string, non-empty table value raises OpenBBError."""
        with pytest.raises(OpenBBError, match="Invalid table"):
            NormalizedPricesQueryParams(table=123)

    def test_aextract_data_fetches_selected_table(self, monkeypatch):
        """aextract_data fetches only the selected table's rows."""
        fetched = []

        async def fake_afetch_table(table, **kwargs):
            fetched.append(table)
            return [{"table": table}]

        monkeypatch.setattr(ers_normalized_prices, "afetch_table", fake_afetch_table)
        query = NormalizedPricesFetcher.transform_query(
            {"table": "table3_state_prices"}
        )
        records = asyncio.run(NormalizedPricesFetcher.aextract_data(query, None))
        assert fetched == ["table3_state_prices"]
        assert records == [{"table": "table3_state_prices"}]

    def test_transform_data_table1_pivots_years_chronological(self):
        """Table 1 spreads report years into ascending columns, published order."""
        records = parse_table(TABLE1_CSV, "table1_national_prices")
        query = NormalizedPricesFetcher.transform_query({})
        data = NormalizedPricesFetcher.transform_data(query, records)
        assert [row.commodity for row in data] == ["Wheat", "Rye", "Milk"]
        served = data[0].model_dump(by_alias=True)
        year_keys = [k for k in served if k.isdigit()]
        assert year_keys == ["2020", "2021", "2022"]
        assert served["2020"] == 4.93
        assert served["2021"] == 4.65
        assert served["2022"] == 4.68
        assert served["units"] == "$ / bu"

    def test_transform_data_table2_index_series(self):
        """Table 2 rows are index series with the constant index unit."""
        records = parse_table(TABLE2_CSV, "table2_national_indices")
        query = NormalizedPricesFetcher.transform_query(
            {"table": "table2_national_indices"}
        )
        data = NormalizedPricesFetcher.transform_data(query, records)
        first = data[0].model_dump(by_alias=True)
        assert first["commodity"] == (
            "Index for prices received by farmers: All farm products"
        )
        assert first["units"] == INDEX_UNITS
        assert first["description"] is None
        assert [k for k in first if k.isdigit()] == ["2022", "2023", "2024"]
        assert first["2022"] == 130.0

    def test_transform_data_table3_states_alphabetical_blanks_none(self):
        """Table 3 spreads States into alphabetical columns, blanks as None."""
        records = parse_table(TABLE3_CSV, "table3_state_prices")
        query = NormalizedPricesFetcher.transform_query(
            {"table": "table3_state_prices"}
        )
        data = NormalizedPricesFetcher.transform_data(query, records)
        wheat = next(row for row in data if row.commodity == "Wheat")
        served = wheat.model_dump(by_alias=True)
        state_keys = [
            k for k in served if k not in ("commodity", "units", "description")
        ]
        assert state_keys == ["Alabama", "Alaska", "Arizona"]
        assert served["Alabama"] == 6.31
        assert served["Alaska"] is None
        assert served["Arizona"] == 8.38
        assert "Wyoming" not in served

    def test_transform_data_drops_all_blank_column(self):
        """A State suppressed for every commodity is dropped, not left empty."""
        records = parse_table(TABLE3_CSV, "table3_state_prices")
        query = NormalizedPricesFetcher.transform_query(
            {"table": "table3_state_prices"}
        )
        data = NormalizedPricesFetcher.transform_data(query, records)
        for row in data:
            assert "Wyoming" not in row.model_dump(by_alias=True)

    def test_transform_data_empty_raises(self):
        """Empty input raises EmptyDataError."""
        query = NormalizedPricesFetcher.transform_query({})
        with pytest.raises(EmptyDataError):
            NormalizedPricesFetcher.transform_data(query, [])

    def test_transform_data_preserves_precision(self):
        """Dynamic value columns keep full source precision."""
        records = parse_table(
            _csv(
                ["Commodity", "Description", "Report Year", "Price", "Units"],
                [["Corn", "for grain", "2025", "5.043918273645", "$ / bu"]],
            ),
            "table1_national_prices",
        )
        query = NormalizedPricesFetcher.transform_query({})
        data = NormalizedPricesFetcher.transform_data(query, records)
        assert data[0].model_dump(by_alias=True)["2025"] == 5.043918273645

    def test_query_params_widget_options(self):
        """The table param exposes the three tables as a single-select filter."""
        config = NormalizedPricesQueryParams.__json_schema_extra__["table"][
            "x-widget_config"
        ]
        assert config["multiSelect"] is False
        assert config["multiple"] is False
        assert config["value"] == DEFAULT_TABLE
        assert len(config["options"]) == 3
        assert config["options"] == TABLE_OPTIONS

    def test_widget_model_config(self):
        """The whole-widget config carries the name, category, and source."""
        config = NormalizedPricesData.model_config["json_schema_extra"][
            "x-widget_config"
        ]
        assert config["$.name"] == "USDA ERS Normalized Prices"
        assert config["$.category"] == "Economy"
        assert config["$.subCategory"] == "Agriculture"
        assert config["$.source"] == ["USDA", "ERS"]

    def test_columns_defs_bind_to_served_keys(self):
        """Every non-excluded field binds to a served key, dynamics included."""
        records = parse_table(TABLE1_CSV, "table1_national_prices")
        query = NormalizedPricesFetcher.transform_query({})
        data = NormalizedPricesFetcher.transform_data(query, records)
        served = set(data[0].model_dump(by_alias=True))
        fields = NormalizedPricesData.model_fields
        for name, field in fields.items():
            extra = (field.json_schema_extra or {}).get("x-widget_config", {})
            if extra.get("exclude"):
                continue
            assert name in served
        assert "table" not in served
        assert "_order" not in served
        dynamic = served - set(fields)
        assert dynamic == {"2020", "2021", "2022"}

    def test_no_dead_constant_columns(self):
        """Every served key lacking a columnDef varies across the rows."""
        records = parse_table(TABLE3_CSV, "table3_state_prices")
        query = NormalizedPricesFetcher.transform_query(
            {"table": "table3_state_prices"}
        )
        data = NormalizedPricesFetcher.transform_data(query, records)
        rows = [row.model_dump(by_alias=True) for row in data]
        fields = set(NormalizedPricesData.model_fields)
        served = set(rows[0])
        for key in served - fields:
            values = [row.get(key) for row in rows]
            assert len(set(values)) > 1, key
