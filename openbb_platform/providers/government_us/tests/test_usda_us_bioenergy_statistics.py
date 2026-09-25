"""Tests for the USDA ERS U.S. Bioenergy Statistics utils and model."""

import asyncio
import csv
from io import StringIO
from typing import Any, cast

import pytest
from openbb_core.app.model.abstract.error import OpenBBError

from openbb_government_us.usda.models.us_bioenergy_statistics import (
    DEFAULT_TABLE,
    UsBioenergyStatisticsData,
    UsBioenergyStatisticsFetcher,
    UsBioenergyStatisticsQueryParams,
)
from openbb_government_us.usda.utils import ers_us_bioenergy_statistics
from openbb_government_us.usda.utils.ers_us_bioenergy_statistics import (
    BIOENERGY_TABLES,
    MEDIA_PATH,
    PRODUCT_PAGE,
    parse_table,
    series_label,
)

HEADER = [
    "table",
    "table_name",
    "year",
    "year_cat",
    "year_desc",
    "period",
    "period_cat",
    "period_desc",
    "geographic_level",
    "location",
    "commodity",
    "data_item",
    "data_item_desc",
    "units",
    "value",
]


def _row(
    table,
    year,
    period,
    period_desc,
    commodity,
    data_item,
    units,
    value,
    location="United States",
    data_item_desc="",
    geographic_level="Country",
):
    """Build one CSV row in HEADER order."""
    return [
        table,
        "name",
        year,
        "Calendar",
        "year desc",
        period,
        "period cat",
        period_desc,
        geographic_level,
        location,
        commodity,
        data_item,
        data_item_desc,
        units,
        value,
    ]


def _make_csv(rows):
    """Serialize header and rows to CSV text."""
    buffer = StringIO()
    writer = csv.writer(buffer)
    writer.writerow(HEADER)
    for row in rows:
        writer.writerow(row)
    return buffer.getvalue()


ETHANOL_CSV = _make_csv(
    [
        _row(
            "1",
            2024,
            "4",
            "Q4 Jun-Aug",
            "Fuel ethanol",
            "Production",
            "1,000 gallons",
            "100.0",
        ),
        _row(
            "1",
            2024,
            "4",
            "Q4 Jun-Aug",
            "Fuel ethanol",
            "Exports",
            "1,000 gallons",
            "20.0",
        ),
        _row(
            "1",
            2024,
            "4",
            "Q4 Jun-Aug",
            "Corn",
            "Fuel alcohol use",
            "1,000 bushels",
            "35.0",
        ),
        _row(
            "1",
            2024,
            "2024",
            "Corn marketing year (Sep-Aug)",
            "Fuel ethanol",
            "Production",
            "1,000 gallons",
            "400.0",
        ),
        _row(
            "1",
            2025,
            "1",
            "Q1 Sep-Nov",
            "Fuel ethanol",
            "Production",
            "1,000 gallons",
            "149.630228133494",
        ),
        _row(
            "1", 2024, "4", "Q4 Jun-Aug", "Fuel ethanol", "Imports", "1,000 gallons", ""
        ),
        _row(
            "1",
            "NA",
            "4",
            "Q4 Jun-Aug",
            "Fuel ethanol",
            "Production",
            "1,000 gallons",
            "9.0",
        ),
        _row(
            "2",
            2024,
            "2024",
            "Calendar year (Jan-Dec)",
            "Fuel ethanol",
            "Production",
            "1,000 gallons",
            "999.0",
        ),
    ]
)

PERIOD_EDGE_CSV = _make_csv(
    [
        _row(
            "1",
            2024,
            "",
            "",
            "Fuel ethanol",
            "Production",
            "1,000 gallons",
            "400.0",
        ),
        _row(
            "1",
            2025,
            "1",
            "Sep 2025 to Aug 2026",
            "Fuel ethanol",
            "Production",
            "1,000 gallons",
            "410.0",
        ),
    ]
)

OILS_CSV = _make_csv(
    [
        _row(
            "7",
            2025,
            "2025",
            "Calendar year (Jan-Dec)",
            "Lard",
            "Price",
            "Cents per pound",
            "60.0",
            data_item_desc="Average wholesale price for loose lard",
        ),
        _row(
            "7",
            2025,
            "2025",
            "Calendar year (Jan-Dec)",
            "Lard",
            "Total supply",
            "Million pounds",
            "1000.0",
            data_item_desc="NA",
        ),
    ]
)

STATE_CSV = _make_csv(
    [
        _row(
            "11",
            2025,
            "1",
            "Jan",
            "Fuel ethanol",
            "Number of plants",
            "Number of plants",
            "5.0",
            location="Texas",
            geographic_level="State",
        ),
        _row(
            "11",
            2025,
            "1",
            "Jan",
            "Fuel ethanol",
            "Production capacity",
            "Million gallons per year",
            "430.0",
            location="Texas",
            geographic_level="State",
        ),
        _row(
            "11",
            2025,
            "1",
            "Jan",
            "Fuel ethanol",
            "Number of plants",
            "Number of plants",
            "3.0",
            location="Iowa",
            geographic_level="State",
        ),
        _row(
            "11",
            2025,
            "1",
            "Jan",
            "Fuel ethanol",
            "Production capacity",
            "Million gallons per year",
            "200.0",
            location="Iowa",
            geographic_level="State",
        ),
    ]
)

EDGE_CSV = _make_csv(
    [
        _row(
            "1",
            2024,
            "",
            "Q4 Jun-Aug",
            "Fuel ethanol",
            "Production",
            "1,000 gallons",
            "1.0",
        ),
    ]
)


class TestErsUsBioenergyStatisticsUtils:
    """Tests for the ers_us_bioenergy_statistics utils module."""

    def test_catalog_contents(self):
        """The catalog holds the 22 tables with their pivot configuration."""
        assert len(BIOENERGY_TABLES) == 22
        keys = {config["csv_table_key"] for config in BIOENERGY_TABLES.values()}
        assert keys == {
            "1",
            "2",
            "3",
            "4.1",
            "4.2",
            "4.3",
            "4.4",
            "5",
            "6",
            "7",
            "8.1",
            "8.2",
            "8.3",
            "9",
            "10",
            "11",
            "12",
            "13",
            "14",
            "15",
            "16",
            "17",
        }
        assert DEFAULT_TABLE in BIOENERGY_TABLES
        located = {
            slug for slug, config in BIOENERGY_TABLES.items() if config["row_location"]
        }
        assert located == {
            "distillers_dried_grains_price",
            "ethanol_capacity_by_state",
            "biodiesel_renewable_diesel_plants_by_state",
        }
        for config in BIOENERGY_TABLES.values():
            assert config["label"]
            assert config["cadence"]
            assert isinstance(config["series_fields"], tuple)
            assert config["series_fields"]

    def test_series_label_appends_unit(self):
        """A multi-part series joins with ' - ' and appends the unit."""
        assert (
            series_label(["Fuel ethanol", "Production"], "1,000 gallons")
            == "Fuel ethanol - Production (1,000 gallons)"
        )

    def test_series_label_suppresses_unit_matching_component(self):
        """A unit already present as a component is not appended."""
        assert series_label(["Number of plants"], "Number of plants") == (
            "Number of plants"
        )

    def test_series_label_suppresses_unit_matching_label(self):
        """A unit equal to the joined label is not appended."""
        assert series_label(["Cents", "per"], "Cents - per") == "Cents - per"

    def test_series_label_drops_placeholder_component(self):
        """A placeholder component such as 'NA' is dropped from the label."""
        assert (
            series_label(["Lard", "Total supply", "NA"], "Million pounds")
            == "Lard - Total supply (Million pounds)"
        )

    def test_series_label_collapses_repeated_component(self):
        """An immediately repeated component is collapsed."""
        assert series_label(["Price", "Price"], "Dollars per ton") == (
            "Price (Dollars per ton)"
        )

    def test_series_label_unit_only_when_label_empty(self):
        """When every component drops out, the unit becomes the label."""
        assert series_label(["", "na"], "Percent") == "Percent"

    def test_series_label_no_unit_when_placeholder(self):
        """A placeholder unit is not appended."""
        assert series_label(["Total use"], "NA") == "Total use"

    def test_parse_table_filters_to_selected_table(self):
        """Only rows of the selected table survive; other tables are dropped."""
        records = parse_table(ETHANOL_CSV, "ethanol_supply_marketing_year")
        assert len(records) == 5
        assert all(
            record["table"] == "ethanol_supply_marketing_year" for record in records
        )

    def test_parse_table_builds_series_and_row_fields(self):
        """A commodity-and-data-item table emits composite series headers."""
        records = parse_table(ETHANOL_CSV, "ethanol_supply_marketing_year")
        assert records[0] == {
            "table": "ethanol_supply_marketing_year",
            "year": 2024,
            "period": "Q4 Jun-Aug",
            "period_ord": 4,
            "location": None,
            "series": "Fuel ethanol - Production (1,000 gallons)",
            "value": 100.0,
        }
        assert records[2]["series"] == "Corn - Fuel alcohol use (1,000 bushels)"

    def test_parse_table_annual_period_ordinal(self):
        """An annual-total row's period ordinal is its year, sorting it last."""
        records = parse_table(ETHANOL_CSV, "ethanol_supply_marketing_year")
        annual = next(
            record
            for record in records
            if record["period"] == "Corn marketing year (Sep-Aug)"
        )
        assert annual["period_ord"] == 2024

    def test_parse_table_skips_blank_value_and_bad_year(self):
        """A blank value and a non-four-digit year are both skipped."""
        records = parse_table(ETHANOL_CSV, "ethanol_supply_marketing_year")
        assert 9.0 not in [record["value"] for record in records]
        assert all(record["value"] != "" for record in records)

    def test_parse_table_period_ordinal_fallback(self):
        """A non-numeric period yields a zero ordinal."""
        records = parse_table(EDGE_CSV, "ethanol_supply_marketing_year")
        assert len(records) == 1
        assert records[0]["period_ord"] == 0

    def test_parse_table_keeps_location_for_state_table(self):
        """A by-State table keeps the State as the location, unit suppressed."""
        records = parse_table(STATE_CSV, "ethanol_capacity_by_state")
        assert {record["location"] for record in records} == {"Texas", "Iowa"}
        assert "Number of plants" in {record["series"] for record in records}

    def test_parse_table_drops_location_for_national_table(self):
        """A national table sets location to None even though the CSV has one."""
        records = parse_table(ETHANOL_CSV, "ethanol_supply_marketing_year")
        assert all(record["location"] is None for record in records)

    def test_afetch_table(self, monkeypatch):
        """afetch_table fetches the CSV through the ERS cache and parses it."""
        calls = []

        async def fake_afetch_ers_file(media_path, product=None, ttl=None):
            calls.append((media_path, product))
            return ETHANOL_CSV.encode("utf-8-sig")

        monkeypatch.setattr(
            "openbb_government_us.usda.utils.ers_client.afetch_ers_file",
            fake_afetch_ers_file,
        )
        records = asyncio.run(
            ers_us_bioenergy_statistics.afetch_table("ethanol_supply_marketing_year")
        )
        assert calls == [(MEDIA_PATH, PRODUCT_PAGE)]
        assert len(records) == 5


class TestUsBioenergyStatistics:
    """Tests for the UsBioenergyStatistics model."""

    def test_transform_query_default_table(self):
        """transform_query defaults the table and keeps year filters."""
        query = UsBioenergyStatisticsFetcher.transform_query({"start_year": 2000})
        assert isinstance(query, UsBioenergyStatisticsQueryParams)
        assert query.table == DEFAULT_TABLE
        assert query.start_year == 2000

    def test_table_blank_returns_default(self):
        """A blank or None table normalizes to the default table."""
        assert UsBioenergyStatisticsQueryParams(table=None).table == DEFAULT_TABLE
        assert UsBioenergyStatisticsQueryParams(table="").table == DEFAULT_TABLE

    def test_table_strips_whitespace(self):
        """A padded table value is stripped before validation."""
        query = UsBioenergyStatisticsQueryParams(table="  ethanol_capacity_by_state  ")
        assert query.table == "ethanol_capacity_by_state"

    def test_unknown_table_raises(self):
        """An unknown table raises OpenBBError listing valid choices."""
        with pytest.raises(OpenBBError, match="Invalid table: bogus"):
            UsBioenergyStatisticsQueryParams(table="bogus")

    def test_non_string_table_raises(self):
        """A non-string, non-empty table value raises OpenBBError."""
        with pytest.raises(OpenBBError, match="Invalid table"):
            UsBioenergyStatisticsQueryParams(table=123)

    def test_aextract_data_fetches_selected_table(self, monkeypatch):
        """aextract_data fetches only the selected table's rows."""
        fetched = []

        async def fake_afetch_table(table, **kwargs):
            fetched.append(table)
            return [{"table": table}]

        monkeypatch.setattr(
            ers_us_bioenergy_statistics, "afetch_table", fake_afetch_table
        )
        query = UsBioenergyStatisticsFetcher.transform_query(
            {"table": "biodiesel_and_diesel_prices"}
        )
        records = asyncio.run(UsBioenergyStatisticsFetcher.aextract_data(query, None))
        assert fetched == ["biodiesel_and_diesel_prices"]
        assert records == [{"table": "biodiesel_and_diesel_prices"}]

    def test_only_period_field_is_static(self):
        """The model serves exactly one static, pinned period column."""
        assert set(UsBioenergyStatisticsData.model_fields) == {"period"}
        config = UsBioenergyStatisticsData.model_fields["period"].json_schema_extra[
            "x-widget_config"
        ]
        assert config["headerName"] == "Period"
        assert config["pinned"] == "left"

    def test_transform_data_folds_period_and_pivots_series(self):
        """A sub-annual row folds year and quarter, each series a column."""
        records = parse_table(ETHANOL_CSV, DEFAULT_TABLE)
        query = UsBioenergyStatisticsFetcher.transform_query({})
        data = UsBioenergyStatisticsFetcher.transform_data(query, records)
        first = data[0].model_dump(by_alias=True)
        assert first["period"] == "2024 Q4 Jun-Aug"
        assert first["Fuel ethanol - Production (1,000 gallons)"] == 100.0
        assert first["Fuel ethanol - Exports (1,000 gallons)"] == 20.0
        assert first["Corn - Fuel alcohol use (1,000 bushels)"] == 35.0
        assert "year" not in first
        assert "location" not in first

    def test_transform_data_collapses_annual_row_to_year(self):
        """An annual marketing-year row collapses its label to the bare year."""
        records = parse_table(ETHANOL_CSV, DEFAULT_TABLE)
        query = UsBioenergyStatisticsFetcher.transform_query({})
        data = UsBioenergyStatisticsFetcher.transform_data(query, records)
        annual = next(row for row in data if row.period == "2024")
        dumped = annual.model_dump()
        assert dumped["Fuel ethanol - Production (1,000 gallons)"] == 400.0
        assert dumped["Fuel ethanol - Exports (1,000 gallons)"] is None

    def test_annual_token_detection(self):
        """An absent period token describes a whole year."""
        is_annual = UsBioenergyStatisticsFetcher._is_annual_token
        assert is_annual(None) is True
        assert is_annual("") is True
        assert is_annual("Yr Sep-Aug") is True
        assert is_annual("Calendar year (Jan-Dec)") is True
        assert is_annual("Q1 Sep-Nov") is False

    def test_transform_data_labels_rows_without_a_period(self):
        """A row with no period token is labeled with the bare year."""
        records = parse_table(PERIOD_EDGE_CSV, DEFAULT_TABLE)
        data = UsBioenergyStatisticsFetcher.transform_data(
            UsBioenergyStatisticsFetcher.transform_query({}), records
        )
        assert data[0].model_dump() == {
            "period": "2024",
            "Fuel ethanol - Production (1,000 gallons)": 400.0,
        }

    def test_transform_data_keeps_a_spanning_period_as_the_label(self):
        """A period spanning two years already names them, so the year is dropped."""
        records = parse_table(PERIOD_EDGE_CSV, DEFAULT_TABLE)
        data = UsBioenergyStatisticsFetcher.transform_data(
            UsBioenergyStatisticsFetcher.transform_query({}), records
        )
        assert data[1].model_dump() == {
            "period": "Sep 2025 to Aug 2026",
            "Fuel ethanol - Production (1,000 gallons)": 410.0,
        }

    def test_transform_data_orders_chronologically(self):
        """Rows sort by year then period ordinal, annual totals last in a year."""
        records = parse_table(ETHANOL_CSV, DEFAULT_TABLE)
        query = UsBioenergyStatisticsFetcher.transform_query({})
        data = UsBioenergyStatisticsFetcher.transform_data(query, records)
        order = [row.period for row in data]
        assert order == ["2024 Q4 Jun-Aug", "2024", "2025 Q1 Sep-Nov"]

    def test_transform_data_filters_years(self):
        """start_year and end_year filter rows on the integer year."""
        records = parse_table(ETHANOL_CSV, DEFAULT_TABLE)
        start = UsBioenergyStatisticsFetcher.transform_data(
            UsBioenergyStatisticsFetcher.transform_query({"start_year": 2025}),
            records,
        )
        assert [row.period for row in start] == ["2025 Q1 Sep-Nov"]
        end = UsBioenergyStatisticsFetcher.transform_data(
            UsBioenergyStatisticsFetcher.transform_query({"end_year": 2024}),
            records,
        )
        assert {row.period for row in end} == {"2024 Q4 Jun-Aug", "2024"}

    def test_transform_data_state_table_folds_location(self):
        """A by-State table folds the State into the period label."""
        records = parse_table(STATE_CSV, "ethanol_capacity_by_state")
        query = UsBioenergyStatisticsFetcher.transform_query(
            {"table": "ethanol_capacity_by_state"}
        )
        data = UsBioenergyStatisticsFetcher.transform_data(query, records)
        assert [row.period for row in data] == ["Texas — 2025", "Iowa — 2025"]
        texas = next(row for row in data if row.period == "Texas — 2025")
        dumped = texas.model_dump()
        assert "location" not in dumped
        assert dumped["Number of plants"] == 5.0
        assert dumped["Production capacity (Million gallons per year)"] == 430.0

    def test_transform_data_national_table_bare_period(self):
        """A national table leaves no folded location in the period label."""
        records = parse_table(ETHANOL_CSV, DEFAULT_TABLE)
        query = UsBioenergyStatisticsFetcher.transform_query({})
        data = UsBioenergyStatisticsFetcher.transform_data(query, records)
        assert all(" — " not in row.period for row in data)
        assert all("location" not in row.model_dump() for row in data)

    def test_transform_data_uniform_column_set(self):
        """Every row carries the identical union of value columns."""
        records = parse_table(ETHANOL_CSV, DEFAULT_TABLE)
        query = UsBioenergyStatisticsFetcher.transform_query({})
        data = UsBioenergyStatisticsFetcher.transform_data(query, records)
        keysets = [set(row.model_dump(by_alias=True)) for row in data]
        assert all(keyset == keysets[0] for keyset in keysets)

    def test_transform_data_excludes_sort_keys(self):
        """Internal sort keys never leak into the validated records."""
        records = parse_table(ETHANOL_CSV, DEFAULT_TABLE)
        query = UsBioenergyStatisticsFetcher.transform_query({})
        data = UsBioenergyStatisticsFetcher.transform_data(query, records)
        dumped = data[0].model_dump()
        for key in ("_order", "_combo", "_year", "_period_ord", "table", "location"):
            assert key not in dumped

    def test_transform_data_preserves_precision(self):
        """Dynamic value columns keep full source precision."""
        records = parse_table(ETHANOL_CSV, DEFAULT_TABLE)
        query = UsBioenergyStatisticsFetcher.transform_query({})
        data = UsBioenergyStatisticsFetcher.transform_data(query, records)
        row_2025 = next(row for row in data if row.period == "2025 Q1 Sep-Nov")
        dumped = row_2025.model_dump()
        assert dumped["Fuel ethanol - Production (1,000 gallons)"] == 149.630228133494

    def test_oils_table_folds_annual_descriptors_to_year(self):
        """The oils table folds each marketing-year descriptor to the bare year."""
        records = parse_table(OILS_CSV, "oils_and_fats_supply_and_prices")
        query = UsBioenergyStatisticsFetcher.transform_query(
            {"table": "oils_and_fats_supply_and_prices"}
        )
        data = UsBioenergyStatisticsFetcher.transform_data(query, records)
        assert len(data) == 1
        assert data[0].period == "2025"
        dumped = data[0].model_dump()
        assert (
            dumped[
                "Lard - Price - Average wholesale price for loose lard"
                " (Cents per pound)"
            ]
            == 60.0
        )
        assert dumped["Lard - Total supply (Million pounds)"] == 1000.0

    def test_query_params_widget_options(self):
        """The table param exposes all 22 tables as a single-select filter."""
        config = UsBioenergyStatisticsQueryParams.__json_schema_extra__["table"][
            "x-widget_config"
        ]
        assert config["multiSelect"] is False
        assert config["multiple"] is False
        assert config["value"] == DEFAULT_TABLE
        options = config["options"]
        assert isinstance(options, list)
        assert len(options) == 22

    def test_widget_model_config(self):
        """The whole-widget config carries the name, category, and source."""
        extra = cast(
            dict[str, Any],
            UsBioenergyStatisticsData.model_config["json_schema_extra"],
        )
        config = extra["x-widget_config"]
        assert config["$.name"] == "USDA ERS U.S. Bioenergy Statistics"
        assert config["$.category"] == "Economy"
        assert config["$.subCategory"] == "Agriculture"
        assert config["$.source"] == ["USDA", "ERS"]

    def test_columns_defs_bind_to_served_keys(self):
        """The lone static field binds to a served key alongside the dynamics."""
        records = parse_table(ETHANOL_CSV, DEFAULT_TABLE)
        query = UsBioenergyStatisticsFetcher.transform_query({})
        data = UsBioenergyStatisticsFetcher.transform_data(query, records)
        served = set(data[0].model_dump(by_alias=True))
        assert set(UsBioenergyStatisticsData.model_fields) == {"period"}
        assert "period" in served
        assert "year" not in served
        assert "location" not in served
        assert "table" not in served
        dynamic = served - {"period"}
        assert "Fuel ethanol - Production (1,000 gallons)" in dynamic
