"""Tests for the USDA ERS meat price spreads utils and model."""

import asyncio

import pytest
from openbb_core.app.model.abstract.error import OpenBBError

from openbb_government_us.usda.models.meat_price_spreads import (
    MeatPriceSpreadsData,
    MeatPriceSpreadsFetcher,
    MeatPriceSpreadsQueryParams,
)
from openbb_government_us.usda.utils import ers_meat_price_spreads
from openbb_government_us.usda.utils.ers_meat_price_spreads import (
    MEAT_PRICE_SPREADS_FILES,
    build_url,
    frequency_for,
    media_path,
    parse_rows,
    parse_value,
)

CHOICE_BEEF_CSV = (
    "Year,Period,Period_Number,Data_Item,Value,Units\n"
    "2020,Annual,17,Choice beef retail value,653.6,"
    "Cents per pound of retail equivalent\n"
    '2025,"Quarter 4, October-December",16,Choice beef retail value,'
    '"1,009.30",Cents per pound of retail equivalent\n'
    "2024,June,6,Choice beef retail value,,"
    "Cents per pound of retail equivalent\n"
)

SUMMARY_CSV = (
    "Year,Month,Month_Number,Data_Item,Value,Units\n"
    "2024,July,7,Consumer price index all items,314.54,1982-84=100\n"
)

HISTORICAL_CSV = (
    "Year,Month,Month-number,Data_Item,Value,Units\n"
    "1970,January,1,Pork byproduct value,4.3,Cents per pound of retail equivalent\n"
)

RETAIL_PRICES_CSV = (
    "Year,Month,Month_Number,Data_Item,Value,Units,Source\n"
    "2024,June,6,Ground chuck retail price,5.364,Dollars per pound,BLS\n"
    "2024,July,7,Ground chuck retail price,NA,Dollars per pound,BLS\n"
)


class TestErsMeatPriceSpreadsUtils:
    """Tests for the ers_meat_price_spreads utils module."""

    def test_catalog_contents(self):
        """The catalog holds the five tables with unique ids and slugs."""
        assert set(MEAT_PRICE_SPREADS_FILES) == {
            "summary",
            "choice_beef",
            "pork",
            "retail_prices",
            "historical_monthly",
        }
        media_ids = [entry["media_id"] for entry in MEAT_PRICE_SPREADS_FILES.values()]
        assert media_ids == [5025, 5020, 5026, 5024, 5028]
        assert len(set(media_ids)) == 5
        slugs = [entry["slug"] for entry in MEAT_PRICE_SPREADS_FILES.values()]
        assert len(set(slugs)) == 5
        assert MEAT_PRICE_SPREADS_FILES["choice_beef"]["period_column"] == "Period"
        assert MEAT_PRICE_SPREADS_FILES["summary"]["period_column"] == "Month"
        assert (
            MEAT_PRICE_SPREADS_FILES["historical_monthly"]["period_number_column"]
            == "Month-number"
        )

    def test_media_path(self):
        """media_path builds the table's media path."""
        assert media_path("pork") == "/media/5026/pork-values-and-spreads.csv"

    def test_build_url(self):
        """URLs follow the /media/{media_id}/{slug}.csv pattern."""
        assert build_url("summary") == (
            "https://www.ers.usda.gov/media/5025/"
            "summary-of-retail-prices-and-price-spreads.csv"
        )

    def test_parse_value_handles_commas_and_null_tokens(self):
        """Values parse to floats, stripping commas and null tokens to None."""
        assert parse_value("653.6") == 653.6
        assert parse_value("1,009.30") == 1009.3
        assert parse_value("") is None
        assert parse_value(None) is None
        assert parse_value("NA") is None

    def test_frequency_for_classifies_period_numbers(self):
        """Period numbers map to annual, quarterly, and monthly frequencies."""
        assert frequency_for(17) == "annual"
        assert frequency_for(13) == "quarterly"
        assert frequency_for(16) == "quarterly"
        assert frequency_for(1) == "monthly"
        assert frequency_for(12) == "monthly"

    def test_parse_rows_period_columns_and_comma_and_skip(self):
        """choice_beef reads Period columns, parses commas, and skips blanks."""
        rows = parse_rows(CHOICE_BEEF_CSV, "choice_beef")
        assert rows == [
            {
                "year": 2020,
                "period": "Annual",
                "period_number": 17,
                "frequency": "annual",
                "data_item": "Choice beef retail value",
                "value": 653.6,
            },
            {
                "year": 2025,
                "period": "Quarter 4, October-December",
                "period_number": 16,
                "frequency": "quarterly",
                "data_item": "Choice beef retail value",
                "value": 1009.3,
            },
        ]

    def test_parse_rows_month_columns(self):
        """summary reads the Month and Month_Number columns."""
        rows = parse_rows(SUMMARY_CSV, "summary")
        assert rows == [
            {
                "year": 2024,
                "period": "July",
                "period_number": 7,
                "frequency": "monthly",
                "data_item": "Consumer price index all items",
                "value": 314.54,
            }
        ]

    def test_parse_rows_hyphenated_number_column(self):
        """historical_monthly reads the hyphenated Month-number column."""
        rows = parse_rows(HISTORICAL_CSV, "historical_monthly")
        assert rows == [
            {
                "year": 1970,
                "period": "January",
                "period_number": 1,
                "frequency": "monthly",
                "data_item": "Pork byproduct value",
                "value": 4.3,
            }
        ]

    def test_parse_rows_skips_na_token(self):
        """retail_prices drops the 'NA' null-token row."""
        rows = parse_rows(RETAIL_PRICES_CSV, "retail_prices")
        assert len(rows) == 1
        assert rows[0]["value"] == 5.364
        assert rows[0]["data_item"] == "Ground chuck retail price"

    def test_afetch_table(self, monkeypatch):
        """afetch_table fetches through the ERS cache client and parses the CSV."""
        calls = []

        async def fake_afetch_ers_file(path, product=None, ttl=None):
            calls.append((path, product))
            return CHOICE_BEEF_CSV.encode("utf-8-sig")

        monkeypatch.setattr(
            "openbb_government_us.usda.utils.ers_client.afetch_ers_file",
            fake_afetch_ers_file,
        )
        rows = asyncio.run(ers_meat_price_spreads.afetch_table("choice_beef"))
        assert calls == [
            (
                "/media/5020/choice-beef-values-and-spreads-and-the-all-fresh-"
                "retail-value.csv",
                ers_meat_price_spreads.PRODUCT_PAGE,
            )
        ]
        assert len(rows) == 2
        assert rows[0]["data_item"] == "Choice beef retail value"


class TestMeatPriceSpreads:
    """Tests for the MeatPriceSpreads model."""

    def test_transform_query(self):
        """transform_query builds the query params model."""
        query = MeatPriceSpreadsFetcher.transform_query(
            {"table": "pork", "start_year": 2021}
        )
        assert isinstance(query, MeatPriceSpreadsQueryParams)
        assert query.table == "pork"
        assert query.start_year == 2021

    def test_table_defaults_when_blank(self):
        """Empty, None, or empty-list table values normalize to the default."""
        assert MeatPriceSpreadsQueryParams().table == "choice_beef"
        assert MeatPriceSpreadsQueryParams(table=None).table == "choice_beef"
        assert MeatPriceSpreadsQueryParams(table="").table == "choice_beef"
        assert MeatPriceSpreadsQueryParams(table=[]).table == "choice_beef"

    def test_table_accepts_list_and_whitespace(self):
        """A single-item list or padded string resolves to one table key."""
        assert MeatPriceSpreadsQueryParams(table=["pork"]).table == "pork"
        assert MeatPriceSpreadsQueryParams(table=" summary ").table == "summary"
        assert MeatPriceSpreadsQueryParams(table=["", "retail_prices"]).table == (
            "retail_prices"
        )

    def test_unknown_table_raises(self):
        """Unknown table keys raise OpenBBError listing valid choices."""
        with pytest.raises(OpenBBError, match="Invalid table: bogus"):
            MeatPriceSpreadsQueryParams(table="bogus")

    def test_frequency_literal(self):
        """The frequency field accepts the three supported values."""
        assert MeatPriceSpreadsQueryParams(frequency="quarterly").frequency == (
            "quarterly"
        )

    def test_data_exposes_single_period_column(self):
        """The Data model serves exactly one static, pinned period column."""
        assert set(MeatPriceSpreadsData.model_fields) == {"period"}

    def test_period_label_folds_year_and_period(self):
        """The label folds the year with any sub-annual period token."""
        label = MeatPriceSpreadsFetcher._period_label
        assert label(2020, None) == "2020"
        assert label(2020, "Annual") == "2020"
        assert label(2020, "Calendar year") == "2020"
        assert label(2020, "Yr 2020") == "2020"
        assert label(2020, "January") == "2020 January"
        assert label(2020, "Quarter 1, January-March") == (
            "2020 Quarter 1, January-March"
        )
        assert label(2025, "Feb-25 to Jun-25") == "Feb-25 to Jun-25"

    def test_aextract_selects_table(self, monkeypatch):
        """aextract_data fetches only the queried table."""
        fetched = []

        async def fake_afetch_table(table, **kwargs):
            fetched.append(table)
            return [{"table": table}]

        monkeypatch.setattr(ers_meat_price_spreads, "afetch_table", fake_afetch_table)
        query = MeatPriceSpreadsFetcher.transform_query({"table": "pork"})
        records = asyncio.run(MeatPriceSpreadsFetcher.aextract_data(query, None))
        assert fetched == ["pork"]
        assert records == [{"table": "pork"}]

    def test_transform_data_pivots_items_into_columns(self):
        """Each data item becomes a column and the period folds into one label."""
        records = [
            {
                "year": 2020,
                "period": "Annual",
                "period_number": 17,
                "frequency": "annual",
                "data_item": "Choice beef retail value",
                "value": 653.6,
            },
            {
                "year": 2020,
                "period": "Annual",
                "period_number": 17,
                "frequency": "annual",
                "data_item": "Choice beef wholesale value",
                "value": 363.2,
            },
            {
                "year": 2020,
                "period": "January",
                "period_number": 1,
                "frequency": "monthly",
                "data_item": "Choice beef retail value",
                "value": 600.0,
            },
        ]
        query = MeatPriceSpreadsFetcher.transform_query({})
        data = MeatPriceSpreadsFetcher.transform_data(query, records)
        assert [row.period for row in data] == ["2020 January", "2020"]
        assert isinstance(data[0], MeatPriceSpreadsData)
        january = data[0].model_dump()
        annual = data[1].model_dump()
        assert "year" not in january
        assert "frequency" not in january
        assert list(january) == [
            "period",
            "Choice beef retail value",
            "Choice beef wholesale value",
        ]
        assert january["Choice beef retail value"] == 600.0
        assert january["Choice beef wholesale value"] is None
        assert annual["Choice beef retail value"] == 653.6
        assert annual["Choice beef wholesale value"] == 363.2

    def test_transform_data_emits_identical_column_union(self):
        """Every row carries the same value columns in first-seen order."""
        records = [
            {
                "year": 2020,
                "period": "January",
                "period_number": 1,
                "frequency": "monthly",
                "data_item": "Retail value",
                "value": 1.0,
            },
            {
                "year": 2020,
                "period": "February",
                "period_number": 2,
                "frequency": "monthly",
                "data_item": "Wholesale value",
                "value": 2.0,
            },
        ]
        query = MeatPriceSpreadsFetcher.transform_query({})
        data = MeatPriceSpreadsFetcher.transform_data(query, records)
        dumps = [row.model_dump() for row in data]
        assert list(dumps[0]) == ["period", "Retail value", "Wholesale value"]
        assert list(dumps[1]) == ["period", "Retail value", "Wholesale value"]
        assert dumps[0]["Retail value"] == 1.0
        assert dumps[0]["Wholesale value"] is None
        assert dumps[1]["Retail value"] is None
        assert dumps[1]["Wholesale value"] == 2.0

    def test_transform_data_sorts_by_year_then_period_number(self):
        """Rows sort by year, then by month, quarter, and annual period order."""
        records = [
            {
                "year": 2021,
                "period": "Annual",
                "period_number": 17,
                "frequency": "annual",
                "data_item": "Pork retail value",
                "value": 1.0,
            },
            {
                "year": 2020,
                "period": "Quarter 1, January-March",
                "period_number": 13,
                "frequency": "quarterly",
                "data_item": "Pork retail value",
                "value": 2.0,
            },
            {
                "year": 2020,
                "period": "February",
                "period_number": 2,
                "frequency": "monthly",
                "data_item": "Pork retail value",
                "value": 3.0,
            },
        ]
        query = MeatPriceSpreadsFetcher.transform_query({"table": "pork"})
        data = MeatPriceSpreadsFetcher.transform_data(query, records)
        assert [row.period for row in data] == [
            "2020 February",
            "2020 Quarter 1, January-March",
            "2021",
        ]

    def test_transform_data_filters_years(self):
        """start_year and end_year filter on the integer year."""
        records = [
            {
                "year": year,
                "period": "Annual",
                "period_number": 17,
                "frequency": "annual",
                "data_item": "Pork retail value",
                "value": float(year),
            }
            for year in (2019, 2020, 2021, 2022)
        ]
        query = MeatPriceSpreadsFetcher.transform_query(
            {"start_year": 2020, "end_year": 2021}
        )
        data = MeatPriceSpreadsFetcher.transform_data(query, records)
        assert [row.period for row in data] == ["2020", "2021"]

    def test_transform_data_filters_frequency(self):
        """The frequency filter keeps only rows of the requested frequency."""
        records = [
            {
                "year": 2020,
                "period": "Annual",
                "period_number": 17,
                "frequency": "annual",
                "data_item": "Pork retail value",
                "value": 1.0,
            },
            {
                "year": 2020,
                "period": "January",
                "period_number": 1,
                "frequency": "monthly",
                "data_item": "Pork retail value",
                "value": 2.0,
            },
        ]
        query = MeatPriceSpreadsFetcher.transform_query(
            {"table": "pork", "frequency": "annual"}
        )
        data = MeatPriceSpreadsFetcher.transform_data(query, records)
        assert [row.period for row in data] == ["2020"]
