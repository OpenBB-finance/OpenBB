"""Tests for the USDA ERS rice yearbook utils and model."""

import asyncio

import pytest
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.utils.errors import EmptyDataError

from openbb_government_us.usda.models.rice_yearbook import (
    DEFAULT_TABLE,
    MAX_WIDE_COLUMNS,
    RiceYearbookData,
    RiceYearbookFetcher,
    RiceYearbookQueryParams,
)
from openbb_government_us.usda.utils import ers_rice_yearbook
from openbb_government_us.usda.utils.ers_rice_yearbook import (
    RICE_TABLES,
    _period_sort_key,
    classify_frequency,
    clean_token,
    display_period,
    parse_table,
    table_frequencies,
)


def make_record(
    year=1970,
    period="MARKETING YEAR (AUGUST-JULY)",
    rice_class="ALL CLASSES",
    location="U.S. TOTAL",
    rank=None,
    aggregate_level=None,
    series="BEGINNING STOCKS",
    unit="MILLION HUNDREDWEIGHT",
    value=16.4,
):
    """Build a long-format record in the parse_table shape."""
    return {
        "table": "t",
        "year": year,
        "period": period,
        "rice_class": rice_class,
        "location": location,
        "rank": rank,
        "aggregate_level": aggregate_level,
        "series": series,
        "unit": unit,
        "value": value,
    }


SUPPLY_CSV = (
    "TABLE_NAME,TABLE_NUMBER,COMMODITY_DESCRIPTION,CLASS_DESCRIPTION,YEAR,"
    "REFERENCE_PERIOD_DESCRIPTION,LOCATION_DESCRIPTION,STATISTIC_DESCRIPTION,"
    "VALUE,UNIT_DESCRIPTION\n"
    "Supply,8,RICE,ALL CLASSES,1970,MARKETING YEAR (AUGUST-JULY),U.S. TOTAL,"
    "BEGINNING STOCKS,16.4,MILLION HUNDREDWEIGHT\n"
    "Supply,8,RICE,ALL CLASSES,1970,MARKETING YEAR (AUGUST-JULY),U.S. TOTAL,"
    "STOCKS-TO-USE RATIO,22.41,PERCENT\n"
    "Supply,8,RICE,ALL CLASSES,1971,MARKETING YEAR (AUGUST-JULY),U.S. TOTAL,"
    "BEGINNING STOCKS,18.6,MILLION HUNDREDWEIGHT\n"
    "Supply,8,RICE,ALL CLASSES,1971,MARKETING YEAR (AUGUST-JULY),U.S. TOTAL,"
    "STOCKS-TO-USE RATIO,NA,PERCENT\n"
    "Supply,8,RICE,ALL CLASSES,abcd,MARKETING YEAR (AUGUST-JULY),U.S. TOTAL,"
    "BEGINNING STOCKS,99.0,MILLION HUNDREDWEIGHT\n"
    "Supply,7,RICE,LONG GRAIN,2016,MARKETING YEAR (AUGUST-JULY),CALIFORNIA,"
    "PRODUCTION,12.0,MILLION HUNDREDWEIGHT\n"
)


class TestClassifyAndDisplay:
    """Tests for frequency classification and period display."""

    def test_classify_annual_variants(self):
        """None and the annual descriptors classify as Annual."""
        assert classify_frequency(None) == "Annual"
        assert classify_frequency("CROP YEAR (AUGUST-JULY)") == "Annual"
        assert classify_frequency("MARKETING YEAR (OCTOBER-SEPTEMBER)") == "Annual"
        assert classify_frequency("CALENDAR YEAR") == "Annual"
        assert classify_frequency("MARKETING") == "Annual"

    def test_classify_monthly(self):
        """A bare month name, in any case, classifies as Monthly."""
        assert classify_frequency("AUGUST") == "Monthly"
        assert classify_frequency("January") == "Monthly"

    def test_classify_point_in_time(self):
        """A 'Month day' token classifies as Point-in-time."""
        assert classify_frequency("March 1") == "Point-in-time"
        assert classify_frequency("August 1") == "Point-in-time"

    def test_classify_weekly(self):
        """A weekly range or 'DD-Mon' token classifies as Weekly."""
        assert classify_frequency("January 6 - January 13") == "Weekly"
        assert classify_frequency("28-Apr") == "Weekly"

    def test_display_period(self):
        """Bare months title-case; None and other tokens pass through."""
        assert display_period(None) is None
        assert display_period("AUGUST") == "August"
        assert display_period("MARKETING YEAR (AUGUST-JULY)") == (
            "MARKETING YEAR (AUGUST-JULY)"
        )
        assert display_period("March 1") == "March 1"

    def test_period_sort_key(self):
        """Sub-annual periods sort within the marketing year, else zero."""
        assert _period_sort_key("August", "Monthly") == 1
        assert _period_sort_key("July", "Monthly") == 12
        assert _period_sort_key("March 1", "Point-in-time") == 8
        assert _period_sort_key("MARKETING YEAR (AUGUST-JULY)", "Annual") == 0
        assert _period_sort_key(None, "Weekly") == 0

    def test_period_sort_key_weekly_is_calendar_dated(self):
        """Weekly tokens rank by calendar month and day, in either format."""
        assert _period_sort_key("7-Jan", "Weekly") == 107
        assert _period_sort_key("31-Dec", "Weekly") == 1231
        assert _period_sort_key("January 6 - January 13", "Weekly") == 106
        assert _period_sort_key("December 15 - December 29", "Weekly") == 1215
        assert _period_sort_key("no date here", "Weekly") == 0


class TestParseTable:
    """Tests for parse_table and clean_token."""

    def test_clean_token(self):
        """Blank and placeholder tokens coerce to None; text is stripped."""
        assert clean_token("NA") is None
        assert clean_token("  --  ") is None
        assert clean_token("") is None
        assert clean_token(None) is None
        assert clean_token("  LONG GRAIN  ") == "LONG GRAIN"

    def test_parse_table_filters_and_shape(self):
        """Only the table's rows parse, with the full record shape."""
        records = parse_table(SUPPLY_CSV, "us_supply_disappearance_price")
        assert {r["table"] for r in records} == {"us_supply_disappearance_price"}
        assert records[0] == {
            "table": "us_supply_disappearance_price",
            "year": 1970,
            "period": "MARKETING YEAR (AUGUST-JULY)",
            "rice_class": "ALL CLASSES",
            "location": "U.S. TOTAL",
            "rank": None,
            "aggregate_level": None,
            "series": "BEGINNING STOCKS",
            "unit": "MILLION HUNDREDWEIGHT",
            "value": 16.4,
        }

    def test_parse_table_skips_bad_rows(self):
        """Rows with NA value or a non-numeric year are dropped."""
        records = parse_table(SUPPLY_CSV, "us_supply_disappearance_price")
        assert {r["year"] for r in records} == {1970, 1971}
        ratios = [r for r in records if r["series"] == "STOCKS-TO-USE RATIO"]
        assert [r["year"] for r in ratios] == [1970]

    def test_table_frequencies(self, monkeypatch):
        """table_frequencies lists distinct frequencies, annual last-to-first."""

        async def fake_afetch_table(table, **kwargs):
            return [
                {"period": "AUGUST"},
                {"period": "MARKETING YEAR (AUGUST-JULY)"},
                {"period": "SEPTEMBER"},
            ]

        monkeypatch.setattr(ers_rice_yearbook, "afetch_table", fake_afetch_table)
        assert asyncio.run(table_frequencies("us_rough_price_by_month")) == [
            "Annual",
            "Monthly",
        ]

    def test_afetch_table(self, monkeypatch):
        """afetch_table fetches the media file through the ERS cache."""
        calls = []

        async def fake_afetch_ers_file(media_path, product=None, ttl=None):
            calls.append((media_path, product))
            return SUPPLY_CSV.encode("utf-8")

        monkeypatch.setattr(
            "openbb_government_us.usda.utils.ers_client.afetch_ers_file",
            fake_afetch_ers_file,
        )
        records = asyncio.run(
            ers_rice_yearbook.afetch_table("us_supply_disappearance_price")
        )
        assert calls == [
            (
                RICE_TABLES["us_supply_disappearance_price"]["media"],
                "data-products/rice-yearbook",
            )
        ]
        assert {r["year"] for r in records} == {1970, 1971}


class TestRiceYearbookQueryParams:
    """Tests for the rice-yearbook query params."""

    def test_table_default_blank_and_strip(self):
        """A blank table defaults; a padded one is stripped."""
        assert RiceYearbookQueryParams(table=None).table == DEFAULT_TABLE
        assert RiceYearbookQueryParams(table="").table == DEFAULT_TABLE
        assert RiceYearbookQueryParams(table="  us_state_yields  ").table == (
            "us_state_yields"
        )

    def test_invalid_table_raises(self):
        """An unknown table raises OpenBBError listing valid choices."""
        with pytest.raises(OpenBBError, match="Invalid table: bogus"):
            RiceYearbookQueryParams(table="bogus")

    def test_frequency_validator(self):
        """A blank frequency is None; a padded one is stripped."""
        assert RiceYearbookQueryParams(frequency=None).frequency is None
        assert RiceYearbookQueryParams(frequency="").frequency is None
        assert RiceYearbookQueryParams(frequency=["Monthly"]).frequency == "Monthly"


class TestRiceYearbook:
    """Tests for the RiceYearbook model and pivot."""

    def test_transform_query_default(self):
        """transform_query defaults the table and keeps the year filter."""
        query = RiceYearbookFetcher.transform_query({"start_year": 2000})
        assert query.table == DEFAULT_TABLE
        assert query.start_year == 2000

    def test_aextract_data(self, monkeypatch):
        """aextract_data fetches only the selected table's rows."""
        fetched = []

        async def fake_afetch_table(table, **kwargs):
            fetched.append(table)
            return [{"table": table}]

        monkeypatch.setattr(ers_rice_yearbook, "afetch_table", fake_afetch_table)
        query = RiceYearbookFetcher.transform_query({"table": "us_state_yields"})
        records = asyncio.run(RiceYearbookFetcher.aextract_data(query, None))
        assert fetched == ["us_state_yields"]
        assert records == [{"table": "us_state_yields"}]

    def test_transform_data_empty(self):
        """Empty extracted data returns an empty result."""
        query = RiceYearbookFetcher.transform_query({})
        assert RiceYearbookFetcher.transform_data(query, []) == []

    def test_classify_dims_never_spreads_an_unpopulated_dim(self):
        """A dim no record populates cannot partition the series into columns."""
        rows = [
            make_record(location="CALIFORNIA", series="PRODUCTION"),
            make_record(location="ARKANSAS", series="ACREAGE"),
        ]
        assert all(record["rank"] is None for record in rows)
        assert RiceYearbookFetcher._classify_dims(rows, ["rank", "location"]) == (
            ["location"],
            [],
        )

    def test_a_single_annual_basis_does_not_partition_the_series(self):
        """One published basis cannot split the series, so it stays out of columns."""
        rows = [
            make_record(series="BEGINNING STOCKS"),
            make_record(series="PRODUCTION"),
        ]
        assert len({record["period"] for record in rows}) == 1
        assert RiceYearbookFetcher._basis_partitions_series(rows) is False

    def test_transform_data_annual_multi_unit(self):
        """An annual table labels rows by year with unit-tagged columns."""
        records = parse_table(SUPPLY_CSV, "us_supply_disappearance_price")
        query = RiceYearbookFetcher.transform_query(
            {"table": "us_supply_disappearance_price"}
        )
        data = RiceYearbookFetcher.transform_data(query, records)
        assert [row.period for row in data] == ["1971", "1970"]
        dumped = data[1].model_dump()
        assert dumped["BEGINNING STOCKS (MILLION HUNDREDWEIGHT)"] == 16.4
        assert dumped["STOCKS-TO-USE RATIO (PERCENT)"] == 22.41
        assert data[0].model_dump()["STOCKS-TO-USE RATIO (PERCENT)"] is None

    def test_transform_data_folds_compact_class_and_location_into_columns(self):
        """Compact class and location dims spread across the columns."""
        records = [
            make_record(
                year=2016,
                rice_class=rice_class,
                location=location,
                series="PRODUCTION",
                value=value,
            )
            for rice_class, location, value in (
                ("LONG GRAIN", "CALIFORNIA", 12.0),
                ("MEDIUM GRAIN", "ARKANSAS", 8.0),
                ("LONG GRAIN", "ARKANSAS", 5.0),
            )
        ]
        query = RiceYearbookFetcher.transform_query({"table": "us_production_by_class"})
        data = RiceYearbookFetcher.transform_data(query, records)
        assert [row.period for row in data] == ["2016"]
        dumped = data[0].model_dump()
        assert dumped["LONG GRAIN — CALIFORNIA — PRODUCTION"] == 12.0
        assert dumped["MEDIUM GRAIN — ARKANSAS — PRODUCTION"] == 8.0
        assert dumped["LONG GRAIN — ARKANSAS — PRODUCTION"] == 5.0

    def test_transform_data_keeps_wide_location_in_the_row_label(self):
        """A location dim too wide to spread stays folded into the row label."""
        records = [
            make_record(
                year=year,
                location=f"COUNTRY {index:02d}",
                series=series,
                value=float(index),
            )
            for year in (2016, 2017)
            for index in range(MAX_WIDE_COLUMNS)
            for series in ("EXPORTS", "IMPORTS")
        ]
        query = RiceYearbookFetcher.transform_query(
            {"table": "world_trade_milled_basis"}
        )
        data = RiceYearbookFetcher.transform_data(query, records)
        assert len(data) == 2 * MAX_WIDE_COLUMNS
        assert data[0].period == "COUNTRY 00 — 2017"
        assert data[0].model_dump()["EXPORTS"] == 0.0

    def test_transform_data_drops_a_dim_the_period_already_fixes(self):
        """A dim determined by the period and the other dims leaves the labels."""
        records = [
            make_record(
                year=2020,
                location=location,
                rank=rank,
                series="U.S. EXPORTS",
                value=value,
            )
            for location, rank, value in (
                ("Mexico", "1", 794.8),
                ("Haiti", "2", 391.6),
                ("Subtotal", None, 1186.4),
                ("Total exports", None, 1500.0),
            )
        ]
        query = RiceYearbookFetcher.transform_query({"table": "us_top_export_markets"})
        data = RiceYearbookFetcher.transform_data(query, records)
        assert [row.period for row in data] == ["2020"]
        dumped = data[0].model_dump()
        assert dumped["Mexico — U.S. EXPORTS"] == 794.8
        assert dumped["Haiti — U.S. EXPORTS"] == 391.6

    def test_transform_data_folds_partitioning_class_into_columns(self):
        """A class that partitions the series folds into the column headers."""
        records = [
            make_record(
                year=year,
                period="CALENDAR YEAR",
                rice_class=rice_class,
                series=series,
                unit="DOLLARS PER HUNDREDWEIGHT",
                value=value,
            )
            for year, rice_class, series, value in (
                (2023, "ALL CLASSES", "LOAN RATE", 7.0),
                (2023, "LONG GRAIN", "REFERENCE PRICE", 14.0),
                (2024, "ALL CLASSES", "LOAN RATE", 7.5),
                (2024, "LONG GRAIN", "REFERENCE PRICE", 14.5),
            )
        ]
        query = RiceYearbookFetcher.transform_query(
            {"table": "us_prices_and_payment_rates"}
        )
        data = RiceYearbookFetcher.transform_data(query, records)
        assert [row.period for row in data] == ["2024", "2023"]
        dumped = data[1].model_dump()
        assert dumped["ALL CLASSES — LOAN RATE"] == 7.0
        assert dumped["LONG GRAIN — REFERENCE PRICE"] == 14.0

    def test_resolve_frequency_honors_explicit_choice(self):
        """An explicitly requested, available frequency is kept."""
        records = [make_record(year=2020, period="MARKETING YEAR (AUGUST-JULY)")]
        query = RiceYearbookFetcher.transform_query(
            {"table": DEFAULT_TABLE, "frequency": "Annual"}
        )
        frequency, available = RiceYearbookFetcher._resolve_frequency(query, records)
        assert frequency == "Annual"
        assert available == ["Annual"]

    def test_transform_data_monthly_default_and_labels(self):
        """An annual+monthly table defaults to Monthly and labels year-month."""
        records = [
            make_record(
                year=2006,
                period="AUGUST",
                series="ROUGH PRICE",
                unit="DOLLARS",
                value=9.0,
            ),
            make_record(
                year=2006,
                period="SEPTEMBER",
                series="ROUGH PRICE",
                unit="DOLLARS",
                value=9.5,
            ),
            make_record(
                year=2006,
                period="MARKETING YEAR (AUGUST-JULY)",
                series="ROUGH PRICE",
                unit="DOLLARS",
                value=9.2,
            ),
        ]
        query = RiceYearbookFetcher.transform_query(
            {"table": "us_rough_price_by_month"}
        )
        freq, available = RiceYearbookFetcher._resolve_frequency(query, records)
        assert freq == "Monthly"
        assert available == ["Monthly", "Annual"]
        data = RiceYearbookFetcher.transform_data(query, records)
        assert [row.period for row in data] == ["2006 September", "2006 August"]

    def test_transform_data_point_in_time_labels(self):
        """A point-in-time table labels rows with the stocks date."""
        records = [
            make_record(
                year=2020,
                period="March 1",
                series="ROUGH",
                unit="MILLION CWT",
                value=5.0,
            ),
            make_record(
                year=2020,
                period="August 1",
                series="ROUGH",
                unit="MILLION CWT",
                value=3.0,
            ),
        ]
        query = RiceYearbookFetcher.transform_query(
            {"table": "us_stocks_rough_and_milled"}
        )
        data = RiceYearbookFetcher.transform_data(query, records)
        assert [row.period for row in data] == ["2020 March 1", "2020 August 1"]

    def test_transform_data_weekly_rows_are_newest_first(self):
        """A weekly table orders rows newest-first inside the calendar year."""
        records = [
            make_record(
                year=2025,
                period=period,
                series="WORLD MARKET PRICE",
                unit="DOLLARS/CWT",
                value=value,
            )
            for period, value in (
                ("2-Jan", 1.0),
                ("5-Feb", 2.0),
                ("31-Dec", 3.0),
                ("November 3 - November 10", 4.0),
            )
        ]
        query = RiceYearbookFetcher.transform_query(
            {"table": "world_market_prices_loan_basis"}
        )
        data = RiceYearbookFetcher.transform_data(query, records)
        assert [row.period for row in data] == [
            "2025 31-Dec",
            "2025 November 3 - November 10",
            "2025 5-Feb",
            "2025 2-Jan",
        ]

    def test_transform_data_folds_a_partitioning_annual_basis_into_columns(self):
        """Annual bases publishing disjoint series move into the column headers."""
        records = [
            make_record(
                year=year,
                period=period,
                series=series,
                unit="THOUSAND METRIC TONS",
                value=value,
            )
            for year, period, series, value in (
                (2024, "MARKETING YEAR (AUGUST-JULY)", "PRODUCTION", 1.0),
                (2024, "CALENDAR YEAR", "EXPORTS", 2.0),
                (2025, "MARKETING YEAR (AUGUST-JULY)", "PRODUCTION", 3.0),
                (2025, "CALENDAR YEAR", "EXPORTS", 4.0),
            )
        ]
        query = RiceYearbookFetcher.transform_query(
            {"table": "world_supply_and_utilization"}
        )
        data = RiceYearbookFetcher.transform_data(query, records)
        assert [row.period for row in data] == ["2025", "2024"]
        assert data[0].model_dump() == {
            "period": "2025",
            "PRODUCTION — MARKETING YEAR (AUGUST-JULY)": 3.0,
            "EXPORTS — CALENDAR YEAR": 4.0,
        }

    def test_transform_data_disambiguates_annual_bases(self):
        """Two annual bases in one year get distinct labels."""
        records = [
            make_record(year=1960, period="MARKETING YEAR (AUGUST-JULY)", value=1.0),
            make_record(year=1960, period="CALENDAR YEAR", value=2.0),
        ]
        query = RiceYearbookFetcher.transform_query(
            {"table": "world_supply_and_utilization"}
        )
        data = RiceYearbookFetcher.transform_data(query, records)
        assert {row.period for row in data} == {
            "1960 — MARKETING YEAR (AUGUST-JULY)",
            "1960 — CALENDAR YEAR",
        }

    def test_transform_data_year_filters(self):
        """start_year and end_year filter rows on the integer year."""
        records = parse_table(SUPPLY_CSV, "us_supply_disappearance_price")
        query = RiceYearbookFetcher.transform_query(
            {"table": "us_supply_disappearance_price", "start_year": 1971}
        )
        data = RiceYearbookFetcher.transform_data(query, records)
        assert {row.period for row in data} == {"1971"}

    def test_transform_data_empty_raises(self):
        """A filter that excludes every row raises EmptyDataError."""
        records = parse_table(SUPPLY_CSV, "us_supply_disappearance_price")
        query = RiceYearbookFetcher.transform_query(
            {"table": "us_supply_disappearance_price", "start_year": 2100}
        )
        with pytest.raises(EmptyDataError):
            RiceYearbookFetcher.transform_data(query, records)

    def test_data_model_only_period_is_static(self):
        """The only static served field is the pinned period label."""
        assert set(RiceYearbookData.model_fields) == {"period"}

    def test_data_model_keeps_dynamic_columns_and_precision(self):
        """The Data model preserves dynamic columns at full precision."""
        row = RiceYearbookData.model_validate(
            {"period": "1970", "BEGINNING STOCKS (MILLION HUNDREDWEIGHT)": 16.412345}
        )
        assert row.model_dump()["BEGINNING STOCKS (MILLION HUNDREDWEIGHT)"] == 16.412345
