"""Tests for the USDA ERS Oil Crops Yearbook utils and model."""

import asyncio
import csv
from io import StringIO

import pytest
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.utils.errors import EmptyDataError

from openbb_government_us.usda.models.oil_crops_yearbook import (
    OilCropsYearbookData,
    OilCropsYearbookFetcher,
    OilCropsYearbookQueryParams,
)
from openbb_government_us.usda.utils import ers_oil_crops_yearbook
from openbb_government_us.usda.utils.ers_oil_crops_yearbook import (
    DEFAULT_FREQUENCY,
    DEFAULT_TABLE,
    FREQUENCIES_BY_TABLE,
    OIL_CROPS_TABLES,
    OILCROPS_CSV,
    PRODUCT_PAGE,
    annual_descriptor,
    coerce_period,
    format_period,
    frequency_of,
    parse_amount,
    parse_rows,
    period_ordinal,
    start_month,
)

COLUMNS = [
    "Timeperiod_Desc",
    "Marketing_Year",
    "MY_Definition",
    "Commodity_Group",
    "Commodity_Desc",
    "Commodity_Desc2",
    "Attribute_Desc",
    "Attribute_Desc2",
    "Geography_Desc",
    "Geography_Desc2",
    "Amount",
    "Unit_Desc",
    "Table_number",
    "Table_name",
]


def build_csv(rows: list[dict]) -> str:
    """Build all-tables CSV text from partial row dicts."""
    buffer = StringIO()
    writer = csv.DictWriter(buffer, fieldnames=COLUMNS)
    writer.writeheader()
    for row in rows:
        writer.writerow({column: row.get(column, "") for column in COLUMNS})
    return buffer.getvalue()


def soybean_row(year, attribute, amount, unit, timeperiod="MY Total"):
    """Build a Table 3 soybean supply row."""
    return {
        "Timeperiod_Desc": timeperiod,
        "Marketing_Year": year,
        "MY_Definition": "September–August",
        "Commodity_Desc": "Soybeans",
        "Commodity_Desc2": "Soybeans",
        "Attribute_Desc": attribute,
        "Attribute_Desc2": attribute,
        "Geography_Desc": "United States",
        "Geography_Desc2": "United States",
        "Amount": amount,
        "Unit_Desc": unit,
        "Table_number": "3",
        "Table_name": "Table 3—Soybeans: U.S. supply, disappearance, and price",
    }


SOYBEAN_CSV = build_csv(
    [
        soybean_row("2023/24", "Beginning stocks", "264.184", "Million bushels"),
        soybean_row("2023/24", "Production", "4162.057", "Million bushels"),
        soybean_row(
            "2023/24",
            "Season-average price received by farmers",
            "12.4",
            "Dollars/bushel",
        ),
        soybean_row("2022/23", "Beginning stocks", "274.394", "Million bushels"),
        soybean_row("2022/23", "Production", "4270.381", "Million bushels"),
        soybean_row("2024/25", "Beginning stocks", "342.433", "Million bushels"),
        soybean_row("2024/25", "Production", "4374.228", "Million bushels"),
        soybean_row("2024/25", "Ending stocks", "NA", "Million bushels"),
        soybean_row("", "Production", "99.0", "Million bushels"),
        {
            "Timeperiod_Desc": "MY Total",
            "Marketing_Year": "2024/25",
            "Attribute_Desc": "Production",
            "Attribute_Desc2": "Production",
            "Geography_Desc2": "United States",
            "Amount": "1.0",
            "Unit_Desc": "Million pounds",
            "Table_number": "5",
            "Table_name": "Table 5—Soybean oil",
        },
    ]
)

EXPORTS_CSV = build_csv(
    [
        {
            "Timeperiod_Desc": "MY Total",
            "Marketing_Year": "2023/24",
            "MY_Definition": "September–August",
            "Attribute_Desc": "U.S. Exports",
            "Attribute_Desc2": "U.S. Exports",
            "Geography_Desc": " China",
            "Geography_Desc2": " China",
            "Amount": "100.0",
            "Unit_Desc": "Thousand metric tons",
            "Table_number": "38",
            "Table_name": "Table 38—U.S. soybean exports by selected destinations",
        },
        {
            "Timeperiod_Desc": "MY Total",
            "Marketing_Year": "2023/24",
            "MY_Definition": "September–August",
            "Attribute_Desc": "U.S. Exports",
            "Attribute_Desc2": "U.S. Exports",
            "Geography_Desc": " World",
            "Geography_Desc2": " World",
            "Amount": "200.0",
            "Unit_Desc": "Thousand metric tons",
            "Table_number": "38",
            "Table_name": "Table 38—U.S. soybean exports by selected destinations",
        },
        {
            "Timeperiod_Desc": "MY Total",
            "Marketing_Year": "2022/23",
            "MY_Definition": "September–August",
            "Attribute_Desc": "U.S. Exports",
            "Attribute_Desc2": "U.S. Exports",
            "Geography_Desc": " China",
            "Geography_Desc2": " China",
            "Amount": "90.0",
            "Unit_Desc": "Thousand metric tons",
            "Table_number": "38",
            "Table_name": "Table 38—U.S. soybean exports by selected destinations",
        },
    ]
)


def wholesale_row(month, series, amount, unit):
    """Build a Table 34 wholesale-price monthly row."""
    return {
        "Timeperiod_Desc": month,
        "Marketing_Year": "2024",
        "MY_Definition": "January–December",
        "Attribute_Desc": "Wholesale prices",
        "Attribute_Desc2": series,
        "Geography_Desc2": "United States",
        "Amount": amount,
        "Unit_Desc": unit,
        "Table_number": "34",
        "Table_name": "Table 34—Prices",
    }


WHOLESALE_CSV = build_csv(
    [
        wholesale_row(
            "February",
            "Soybean oil, crude, tank cars, FOB Decatur, IL",
            "50.0",
            "Cents/pound",
        ),
        wholesale_row(
            "January",
            "Soybean oil, crude, tank cars, FOB Decatur, IL",
            "49.0975",
            "Cents/pound",
        ),
        wholesale_row(
            "January",
            "Biodiesel: FOB Iowa, B100 (Soy methyl ester)",
            "5.25",
            "Dollars/gallon",
        ),
        {
            "Timeperiod_Desc": "January",
            "Marketing_Year": "2024",
            "Attribute_Desc": "Meal prices",
            "Attribute_Desc2": "Soybean meal, High protein, Decatur, IL",
            "Geography_Desc2": "United States",
            "Amount": "300.0",
            "Unit_Desc": "Dollars/short ton",
            "Table_number": "34",
            "Table_name": "Table 34—Prices",
        },
    ]
)


def world_oilseed_row(year, commodity, attribute, amount):
    """Build a Table 41 world oilseed row."""
    return {
        "Timeperiod_Desc": "MY Total",
        "Marketing_Year": year,
        "MY_Definition": "Varies by country and commodity",
        "Commodity_Desc": commodity,
        "Commodity_Desc2": commodity,
        "Attribute_Desc": attribute,
        "Attribute_Desc2": attribute,
        "Geography_Desc": "World",
        "Geography_Desc2": "World",
        "Amount": amount,
        "Unit_Desc": "Million metric tons",
        "Table_number": "41",
        "Table_name": "Table 41—World oilseed supply and distribution",
    }


WORLD_OILSEED_CSV = build_csv(
    [
        world_oilseed_row("2024/25", "Copra", "Production", "5.785"),
        world_oilseed_row("2024/25", "Copra", "Exports", "0.07"),
        world_oilseed_row("2023/24", "Copra", "Production", "5.5"),
        world_oilseed_row("2024/25", "Soybeans", "Production", "420.0"),
        world_oilseed_row("2023/24", "Soybeans", "Production", "396.0"),
    ]
)


def world_complex_row(year, commodity, geography, attribute, amount):
    """Build a Table 37 world soybean complex row."""
    return {
        "Timeperiod_Desc": "MY Total",
        "Marketing_Year": year,
        "MY_Definition": "Varies by country and commodity",
        "Commodity_Desc": commodity,
        "Commodity_Desc2": commodity,
        "Attribute_Desc": attribute,
        "Attribute_Desc2": attribute,
        "Geography_Desc": geography,
        "Geography_Desc2": geography,
        "Amount": amount,
        "Unit_Desc": "Million metric tons",
        "Table_number": "37",
        "Table_name": "Table 37—World soybean complex",
    }


WORLD_COMPLEX_CSV = build_csv(
    [
        world_complex_row("2024/25", "Soybeans", "World", "Production", "427.0"),
        world_complex_row("2023/24", "Soybeans", "World", "Production", "396.0"),
        world_complex_row(
            "2024/25", "Soybeans", "Major exporters", "Production", "220.0"
        ),
        world_complex_row("2024/25", "Soybean oil", "World", "Production", "60.0"),
    ]
)

WORLD_COMPLEX_NO_WORLD_CSV = build_csv(
    [
        world_complex_row(
            "2024/25", "Soybeans", "Major exporters", "Production", "220.0"
        ),
        world_complex_row(
            "2023/24", "Soybeans", "Major exporters", "Production", "210.0"
        ),
    ]
)


def stocks_row(year, attribute, amount, timeperiod):
    """Build a Table 1 soybean stocks row."""
    return {
        "Timeperiod_Desc": timeperiod,
        "Marketing_Year": year,
        "MY_Definition": "September–August",
        "Commodity_Desc": "Soybeans",
        "Commodity_Desc2": "Soybeans",
        "Attribute_Desc": attribute,
        "Attribute_Desc2": attribute,
        "Geography_Desc": "United States",
        "Geography_Desc2": "United States",
        "Amount": amount,
        "Unit_Desc": "Thousand bushels",
        "Table_number": "1",
        "Table_name": "Table 1—Soybean stocks",
    }


STOCKS_CSV = build_csv(
    [
        stocks_row("2023/24", "Total stocks", "970050.0", "June 1"),
        stocks_row("2023/24", "Off-farm stocks", "504050.0", "June 1"),
        stocks_row("2023/24", "Total stocks", "342433.0", "September 1"),
        stocks_row("2023/24", "Total stocks", "3000719.0", "December 1"),
        stocks_row("2023/24", "Total stocks", "1844824.0", "March 1"),
    ]
)


def quarter_row(year, attribute, amount, timeperiod):
    """Build a Table 6 soybean by-quarter row."""
    return {
        "Timeperiod_Desc": timeperiod,
        "Marketing_Year": year,
        "MY_Definition": "September–August",
        "Commodity_Desc": "Soybeans",
        "Commodity_Desc2": "Soybeans",
        "Attribute_Desc": attribute,
        "Attribute_Desc2": attribute,
        "Geography_Desc": "United States",
        "Geography_Desc2": "United States",
        "Amount": amount,
        "Unit_Desc": "Thousand bushels",
        "Table_number": "6",
        "Table_name": "Table 6—Soybeans by quarter",
    }


QUARTER_CSV = build_csv(
    [
        quarter_row("2023/24", "Crush", "600.0", "June–Aug."),
        quarter_row("2023/24", "Crush", "610.0", "Sep.–Nov."),
        quarter_row("2023/24", "Exports", "200.0", "Sep.–Nov."),
        quarter_row("2023/24", "Crush", "620.0", "Dec.–Feb."),
        quarter_row("2023/24", "Crush", "630.0", "Mar.–May"),
        quarter_row("2023/24", "Crush", "2460.0", "MY Total"),
        quarter_row("2023/24", "Crush", "200.0", "September"),
    ]
)


def meal_month_row(year, attribute, amount, timeperiod):
    """Build a Table 7 soybean meal by-month row."""
    return {
        "Timeperiod_Desc": timeperiod,
        "Marketing_Year": year,
        "MY_Definition": "October–September",
        "Commodity_Desc": "Soybean meal",
        "Commodity_Desc2": "Soybean meal",
        "Attribute_Desc": attribute,
        "Attribute_Desc2": attribute,
        "Geography_Desc": "United States",
        "Geography_Desc2": "United States",
        "Amount": amount,
        "Unit_Desc": "Thousand short tons",
        "Table_number": "7",
        "Table_name": "Table 7—Soybean meal by month",
    }


MEAL_MONTH_CSV = build_csv(
    [
        meal_month_row("2023/24", "Production", "4738.0", "January"),
        meal_month_row("2023/24", "Production", "4706.0", "October"),
        meal_month_row("2023/24", "Ending stocks", "334.0", "October"),
        meal_month_row("2023/24", "Production", "4818.0", "December"),
        meal_month_row("2023/24", "Production", "56000.0", "MY Total"),
        meal_month_row("2022/23", "Production", "55000.0", "MY Total"),
    ]
)


class TestErsOilCropsYearbookUtils:
    """Tests for the ers_oil_crops_yearbook utils module."""

    def test_catalog_contents(self):
        """The catalog holds 47 tables covering Table_number 1-43 with 34a-e."""
        assert len(OIL_CROPS_TABLES) == 47
        assert DEFAULT_TABLE in OIL_CROPS_TABLES
        split = [
            key
            for key, config in OIL_CROPS_TABLES.items()
            if config["table_number"] == "34"
        ]
        assert len(split) == 5
        for config in OIL_CROPS_TABLES.values():
            assert config["label"]
            assert config["series_col"] in (
                "Attribute_Desc",
                "Attribute_Desc2",
                "Geography_Desc2",
            )
            if config["table_number"] == "34":
                assert config["attribute_filter"]
            else:
                assert config["attribute_filter"] is None

    def test_frequencies_by_table(self):
        """Each table exposes only its published frequency set, default first."""
        assert FREQUENCIES_BY_TABLE["soybean_stocks_quarterly"] == ["point_in_time"]
        assert FREQUENCIES_BY_TABLE["soybeans_supply_disappearance_by_quarter"] == [
            "annual",
            "quarterly",
            "monthly",
        ]
        assert FREQUENCIES_BY_TABLE["soybean_meal_supply_disappearance_by_month"] == [
            "annual",
            "monthly",
        ]
        assert FREQUENCIES_BY_TABLE["prices_received_by_farmers"] == ["monthly"]
        assert FREQUENCIES_BY_TABLE["soybeans_supply_disappearance_price"] == ["annual"]
        assert DEFAULT_FREQUENCY["soybean_stocks_quarterly"] == "point_in_time"
        assert (
            DEFAULT_FREQUENCY["soybeans_supply_disappearance_by_quarter"] == "quarterly"
        )
        assert (
            DEFAULT_FREQUENCY["soybean_meal_supply_disappearance_by_month"] == "monthly"
        )
        assert DEFAULT_FREQUENCY["prices_received_by_farmers"] == "monthly"
        assert DEFAULT_FREQUENCY["soybeans_supply_disappearance_price"] == "annual"

    def test_parse_amount(self):
        """parse_amount handles blanks, null tokens, commas, and bad values."""
        assert parse_amount("274.394") == 274.394
        assert parse_amount("1,000.5") == 1000.5
        assert parse_amount("") is None
        assert parse_amount(None) is None
        assert parse_amount("NA") is None
        assert parse_amount("n/a") is None
        assert parse_amount("abc") is None

    def test_coerce_period(self):
        """coerce_period nulls whole-year totals and strips real periods."""
        assert coerce_period("MY Total") is None
        assert coerce_period("") is None
        assert coerce_period(None) is None
        assert coerce_period("January") == "January"
        assert coerce_period(" June 1 ") == "June 1"

    def test_frequency_of(self):
        """frequency_of classifies each period token into a bucket."""
        assert frequency_of("MY Total") == "annual"
        assert frequency_of("") == "annual"
        assert frequency_of(None) == "annual"
        assert frequency_of("January") == "monthly"
        assert frequency_of("June 1") == "point_in_time"
        assert frequency_of("Sep.–Nov.") == "quarterly"
        assert frequency_of("Sep.-Nov.") == "quarterly"
        assert frequency_of("Marketing year") == "annual"

    def test_start_month(self):
        """start_month reads the opening month of a marketing-year span."""
        assert start_month("October–September") == 10
        assert start_month("September-August") == 9
        assert start_month("January–December") == 1
        assert start_month("September") == 9
        assert start_month("Varies by country and commodity") == 1
        assert start_month("") == 1
        assert start_month(None) == 1

    def test_annual_descriptor(self):
        """annual_descriptor abbreviates a marketing-year span."""
        assert annual_descriptor("September–August") == "Marketing year (Sep-Aug)"
        assert annual_descriptor("October-September") == "Marketing year (Oct-Sep)"
        assert annual_descriptor("Foo–Bar") == "Marketing year"
        assert annual_descriptor("") == "Marketing year"
        assert annual_descriptor(None) == "Marketing year"

    def test_format_period(self):
        """format_period labels annual, quarterly, and verbatim periods."""
        assert (
            format_period(None, "annual", "September–August")
            == "Marketing year (Sep-Aug)"
        )
        assert format_period(None, "monthly", "October–September") is None
        assert format_period("Sep.–Nov.", "quarterly", None) == "Sep-Nov (Q1)"
        assert format_period("June–Aug.", "quarterly", None) == "June-Aug (Q4)"
        assert format_period("Other", "quarterly", None) == "Other (Q1)"
        assert format_period("January", "monthly", None) == "January"
        assert format_period("September 1", "point_in_time", None) == "September 1"

    def test_period_ordinal(self):
        """period_ordinal ranks periods within their marketing year."""
        assert period_ordinal(None, "annual", None) == 0
        assert period_ordinal("June 1", "point_in_time", None) == 3
        assert period_ordinal("Other", "point_in_time", None) == 0
        assert period_ordinal("Mar.–May", "quarterly", None) == 2
        assert period_ordinal("Other", "quarterly", None) == 0
        assert period_ordinal("January", "monthly", "October–September") == 3
        assert period_ordinal("Bogus", "monthly", None) == 0
        assert period_ordinal("January", "annual", None) == 0

    def test_parse_rows_series_and_skips(self):
        """A series table emits one record per attribute, skipping bad rows."""
        records = parse_rows(SOYBEAN_CSV, "soybeans_supply_disappearance_price")
        assert len(records) == 7
        assert all(
            record["table"] == "soybeans_supply_disappearance_price"
            for record in records
        )
        first = records[0]
        assert first == {
            "table": "soybeans_supply_disappearance_price",
            "marketing_year": "2023/24",
            "year": 2023,
            "period": None,
            "frequency": "annual",
            "my_definition": "September–August",
            "commodity": None,
            "geography": None,
            "unit_desc": "Million bushels",
            "series": "Beginning stocks",
            "amount": 264.184,
        }
        assert "NA" not in [record["series"] for record in records]
        assert all(record["year"] in (2022, 2023, 2024) for record in records)

    def test_parse_rows_skips_other_tables(self):
        """Rows belonging to a different Table_number are ignored."""
        records = parse_rows(SOYBEAN_CSV, "soybeans_supply_disappearance_price")
        assert all(record["unit_desc"] != "Million pounds" for record in records)

    def test_parse_rows_geography_series_strips_leading_space(self):
        """A geography-pivot table strips the leading space on destinations."""
        records = parse_rows(EXPORTS_CSV, "soybean_exports_by_destination")
        assert {record["series"] for record in records} == {"China", "World"}
        assert all(record["unit_desc"] == "Thousand metric tons" for record in records)

    def test_parse_rows_attribute_filter_and_frequency(self):
        """The 34d split keeps its category and classifies monthly frequency."""
        records = parse_rows(WHOLESALE_CSV, "prices_fats_and_oils_wholesale")
        assert len(records) == 3
        assert {record["series"] for record in records} == {
            "Soybean oil, crude, tank cars, FOB Decatur, IL",
            "Biodiesel: FOB Iowa, B100 (Soy methyl ester)",
        }
        assert all(record["frequency"] == "monthly" for record in records)

    def test_parse_rows_commodity_row_dimension(self):
        """A world table captures commodity as a row dimension."""
        records = parse_rows(WORLD_OILSEED_CSV, "world_oilseed_supply_and_distribution")
        assert {record["commodity"] for record in records} == {"Copra", "Soybeans"}
        assert all(record["geography"] is None for record in records)

    def test_afetch_table(self, monkeypatch):
        """afetch_table fetches the CSV through the ERS cache and parses it."""
        calls = []

        async def fake_afetch_ers_file(media_path, product=None, ttl=None):
            calls.append((media_path, product))
            return SOYBEAN_CSV.encode("utf-8")

        monkeypatch.setattr(
            "openbb_government_us.usda.utils.ers_client.afetch_ers_file",
            fake_afetch_ers_file,
        )
        records = asyncio.run(
            ers_oil_crops_yearbook.afetch_table("soybeans_supply_disappearance_price")
        )
        assert calls == [(OILCROPS_CSV, PRODUCT_PAGE)]
        assert len(records) == 7


class TestOilCropsYearbookQueryParams:
    """Tests for the OilCropsYearbook query parameters."""

    def test_table_blank_returns_default(self):
        """A blank or None table normalizes to the default table."""
        assert OilCropsYearbookQueryParams(table=None).table == DEFAULT_TABLE
        assert OilCropsYearbookQueryParams(table="").table == DEFAULT_TABLE

    def test_table_strips_whitespace(self):
        """A padded table value is stripped before validation."""
        query = OilCropsYearbookQueryParams(table="  soybean_exports_by_destination  ")
        assert query.table == "soybean_exports_by_destination"

    def test_unknown_table_raises(self):
        """An unknown table raises OpenBBError listing valid choices."""
        with pytest.raises(OpenBBError, match="Invalid table: bogus"):
            OilCropsYearbookQueryParams(table="bogus")

    def test_non_string_table_raises(self):
        """A non-string, non-empty table value raises OpenBBError."""
        with pytest.raises(OpenBBError, match="Invalid table"):
            OilCropsYearbookQueryParams(table=123)

    def test_frequency_validator(self):
        """frequency lowercases known tokens, nulls blanks, rejects unknowns."""
        assert OilCropsYearbookQueryParams(frequency="Monthly").frequency == "monthly"
        assert OilCropsYearbookQueryParams(frequency=None).frequency is None
        assert OilCropsYearbookQueryParams(frequency="").frequency is None
        with pytest.raises(OpenBBError, match="Invalid frequency"):
            OilCropsYearbookQueryParams(frequency="weekly")
        with pytest.raises(OpenBBError, match="Invalid frequency"):
            OilCropsYearbookQueryParams(frequency=123)


class TestOilCropsYearbook:
    """Tests for the OilCropsYearbook model transform."""

    def test_transform_query_default_table(self):
        """transform_query defaults the table and keeps year filters."""
        query = OilCropsYearbookFetcher.transform_query({"start_year": 2000})
        assert isinstance(query, OilCropsYearbookQueryParams)
        assert query.table == DEFAULT_TABLE
        assert query.start_year == 2000

    def test_aextract_data_fetches_selected_table(self, monkeypatch):
        """aextract_data fetches only the selected table's rows."""
        fetched = []

        async def fake_afetch_table(table, **kwargs):
            fetched.append(table)
            return [{"table": table}]

        monkeypatch.setattr(ers_oil_crops_yearbook, "afetch_table", fake_afetch_table)
        query = OilCropsYearbookFetcher.transform_query(
            {"table": "soybean_exports_by_destination"}
        )
        records = asyncio.run(OilCropsYearbookFetcher.aextract_data(query, None))
        assert fetched == ["soybean_exports_by_destination"]
        assert records == [{"table": "soybean_exports_by_destination"}]

    def _dump(self, table, records, **params):
        """Run transform_data and return the by-alias dumps."""
        query = OilCropsYearbookFetcher.transform_query({"table": table, **params})
        data = OilCropsYearbookFetcher.transform_data(query, records)
        return [row.model_dump(by_alias=True) for row in data]

    def test_transform_empty_input(self):
        """Empty extracted data returns an empty result."""
        query = OilCropsYearbookFetcher.transform_query({})
        assert OilCropsYearbookFetcher.transform_data(query, []) == []

    def test_transform_annual_series_columns(self):
        """An annual balance-sheet table labels rows by year, series as columns."""
        records = parse_rows(SOYBEAN_CSV, "soybeans_supply_disappearance_price")
        dumped = self._dump("soybeans_supply_disappearance_price", records)
        assert [row["period"] for row in dumped] == ["2024/25", "2023/24", "2022/23"]
        assert dumped[1]["Beginning stocks (Million bushels)"] == 264.184
        assert (
            dumped[1]["Season-average price received by farmers (Dollars/bushel)"]
            == 12.4
        )
        assert (
            dumped[2]["Season-average price received by farmers (Dollars/bushel)"]
            is None
        )

    def test_transform_year_filter(self):
        """start_year and end_year restrict the period rows."""
        records = parse_rows(SOYBEAN_CSV, "soybeans_supply_disappearance_price")
        start = self._dump(
            "soybeans_supply_disappearance_price", records, start_year=2024
        )
        assert [row["period"] for row in start] == ["2024/25"]
        end = self._dump("soybeans_supply_disappearance_price", records, end_year=2022)
        assert [row["period"] for row in end] == ["2022/23"]

    def test_transform_empty_raises(self):
        """A filter that excludes every row raises EmptyDataError."""
        records = parse_rows(SOYBEAN_CSV, "soybeans_supply_disappearance_price")
        query = OilCropsYearbookFetcher.transform_query(
            {"table": "soybeans_supply_disappearance_price", "start_year": 3000}
        )
        with pytest.raises(EmptyDataError):
            OilCropsYearbookFetcher.transform_data(query, records)

    def test_transform_trade_destinations_as_columns(self):
        """A trade table spreads destinations into columns keyed by year."""
        records = parse_rows(EXPORTS_CSV, "soybean_exports_by_destination")
        dumped = self._dump("soybean_exports_by_destination", records)
        assert [row["period"] for row in dumped] == ["2023/24", "2022/23"]
        assert dumped[0]["China"] == 100.0
        assert dumped[0]["World"] == 200.0

    def test_transform_point_in_time_labels(self):
        """A stocks table folds the stock date into the period, ordered."""
        records = parse_rows(STOCKS_CSV, "soybean_stocks_quarterly")
        dumped = self._dump("soybean_stocks_quarterly", records)
        assert [row["period"] for row in dumped] == [
            "2023/24 June 1",
            "2023/24 March 1",
            "2023/24 December 1",
            "2023/24 September 1",
        ]
        assert dumped[3]["Total stocks"] == 342433.0
        assert dumped[0]["Off-farm stocks"] == 504050.0

    def test_transform_monthly_folds_units(self):
        """A monthly price table folds each series' unit into its header."""
        records = parse_rows(WHOLESALE_CSV, "prices_fats_and_oils_wholesale")
        dumped = self._dump("prices_fats_and_oils_wholesale", records)
        assert [row["period"] for row in dumped] == ["2024 February", "2024 January"]
        assert (
            dumped[1]["Soybean oil, crude, tank cars, FOB Decatur, IL (Cents/pound)"]
            == 49.0975
        )
        assert (
            dumped[1]["Biodiesel: FOB Iowa, B100 (Soy methyl ester) (Dollars/gallon)"]
            == 5.25
        )

    def test_transform_folds_commodity_into_period(self):
        """A multi-commodity world table folds the commodity into the period."""
        records = parse_rows(WORLD_OILSEED_CSV, "world_oilseed_supply_and_distribution")
        dumped = self._dump("world_oilseed_supply_and_distribution", records)
        assert [row["period"] for row in dumped] == [
            "Copra — 2024/25",
            "Copra — 2023/24",
            "Soybeans — 2024/25",
            "Soybeans — 2023/24",
        ]
        assert dumped[2]["Production"] == 420.0

    def test_transform_folds_partitioning_commodity_into_columns(self):
        """A commodity that partitions the series folds into the column headers."""
        records = parse_rows(
            build_csv(
                [
                    world_oilseed_row("2023/24", "Copra", "Production", "5.0"),
                    world_oilseed_row("2023/24", "Soybeans", "Crush", "300.0"),
                    world_oilseed_row("2024/25", "Copra", "Production", "5.5"),
                    world_oilseed_row("2024/25", "Soybeans", "Crush", "320.0"),
                ]
            ),
            "world_oilseed_supply_and_distribution",
        )
        dumped = self._dump("world_oilseed_supply_and_distribution", records)
        assert [row["period"] for row in dumped] == ["2024/25", "2023/24"]
        assert dumped[1]["Copra — Production"] == 5.0
        assert dumped[1]["Soybeans — Crush"] == 300.0

    def test_transform_frequency_selection_and_fallback(self):
        """Annual frequency selects annual rows; an absent one falls back."""
        records = parse_rows(
            MEAL_MONTH_CSV, "soybean_meal_supply_disappearance_by_month"
        )
        annual = self._dump(
            "soybean_meal_supply_disappearance_by_month", records, frequency="annual"
        )
        assert [row["period"] for row in annual] == ["2023/24", "2022/23"]
        assert annual[0]["Production"] == 56000.0
        fallback = self._dump(
            "soybean_meal_supply_disappearance_by_month",
            records,
            frequency="quarterly",
        )
        assert [row["period"] for row in fallback] == [
            "2023/24 January",
            "2023/24 December",
            "2023/24 October",
        ]

    def test_data_model_only_period_is_static(self):
        """The only static served field is the pinned period label."""
        assert set(OilCropsYearbookData.model_fields) == {"period"}

    def test_data_model_keeps_dynamic_columns_and_precision(self):
        """The Data model preserves dynamic columns at full precision."""
        row = OilCropsYearbookData.model_validate(
            {"period": "2024/25 January", "Imports": 149.630228133494}
        )
        assert row.model_dump(by_alias=True)["Imports"] == 149.630228133494
