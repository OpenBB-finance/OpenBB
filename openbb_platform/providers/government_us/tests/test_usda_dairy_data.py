"""Tests for the USDA ERS dairy data utils and model."""

import asyncio
from datetime import date

import pytest
from openbb_core.app.model.abstract.error import OpenBBError

from openbb_government_us.usda.models.dairy_data import (
    DairyDataFetcher,
    DairyDataQueryParams,
)
from openbb_government_us.usda.utils import ers_dairy_data
from openbb_government_us.usda.utils.ers_dairy_data import (
    DAIRY_DATA_FILES,
    build_url,
    clean_label,
    frequency_of,
    media_path,
    parse_rows,
    period_end,
)

GLANCE_CSV = (
    "Year,Period,Timeperiod_id,Frequency,Category,Data_item,Value,Unit\n"
    "2024,Annual,17,Annual,Consumer Price Indexes,All food,2.26,"
    "Year-over-year percent change\n"
    "2026,May,5,Monthly,Wholesale dairy product prices,Dry whey,0.6396,"
    "Dollars per pound\n"
    "2026,June,6,Monthly,Milk production,Milk cows,NA,Thousands\n"
)

QUARTERLY_CSV = (
    "Year,Period,Timeperiod_id,Timeperiod_name,Aggregation,Data_item,Value,Units\n"
    "1998,JAN-MAR,13,Quarter 1,Not applicable,16-percent protein feed value,"
    "5.31,Dollars per hundredweight\n"
    "1998,OCT-DEC,16,Quarter 4,Not applicable,Milk per cow,4300,Pounds\n"
    "1998,ANNUAL,17,Annual aggregation,Quarterly sum,Milk production,"
    "157441,Million pounds\n"
)

PRODUCTS_CSV = (
    "Table,Year,Period,Timeperiod_id,Frequency,Product,Category,Data_item,"
    "Quantity,Units\n"
    '"Amer cheese, monthly",2011,January,1,Monthly,American Style Cheese,'
    "Supply,Beginning cold-storage stocks,630.789,Million pounds\n"
    '"Evap cond whole, annual",2025,Annual,17,Annual,'
    "Evaporated and condensed whole milk,Annual adjustments,"
    "Apparent domestic human use,791.816,Million pounds\n"
)

ALLOCATION_CSV = (
    "Table,Table_id,Category,Data_item_id,Data_item,Year,Value,Units,"
    "Data_item_description\n"
    "Product volume,1,Supply,1-1.00,Supply,2000,NA,Million pounds,"
    '"Product volume, Supply"\n'
    "Product volume,1,Supply,1-1.01.00,Milk production (farm level),2000,"
    '167393,Million pounds,"Product volume, Supply , Milk production (farm level)"\n'
)

STATE_CSV = (
    "Table,Year,Data_item,Region,State,Value,Units\n"
    'Milk cows,1970,"Milk cows, average inventory",Northeast,Connecticut,'
    "59,Thousand head\n"
    "Milk production,2025,Percent of U.S. milk production,United States,"
    "Total region,100,Percent\n"
    "Milk production,2025,Milk production,Northeast,Vermont,,Million pounds\n"
)

PLANTS_CSV = (
    "Year,Data_item,Quantity,Units\n"
    '2008,"Total beverage milk consumed \r\n",55169.5,Million pounds\n'
    "2024,Number of plants,441,Plants\n"
)


class TestErsDairyDataUtils:
    """Tests for the ers_dairy_data utils module."""

    def test_catalog_contents(self):
        """The catalog holds the 12 current tables with unique ids and slugs."""
        assert len(DAIRY_DATA_FILES) == 12
        media_ids = [entry["media_id"] for entry in DAIRY_DATA_FILES.values()]
        assert len(set(media_ids)) == 12
        slugs = [entry["slug"] for entry in DAIRY_DATA_FILES.values()]
        assert len(set(slugs)) == 12
        assert all(entry["title"] for entry in DAIRY_DATA_FILES.values())

    def test_build_url(self):
        """URLs follow the /media/{media_id}/{slug}.csv pattern."""
        assert build_url("situation_at_a_glance") == (
            "https://www.ers.usda.gov/media/5501/"
            "us-dairy-situation-at-a-glance-monthly-and-annual.csv"
        )
        assert build_url("milk_fat_skim_solids_allocation") == (
            "https://www.ers.usda.gov/media/7134/"
            "supply-and-allocation-of-milk-fat-and-skim-solids-by-product-annual.csv"
        )

    def test_media_path(self):
        """media_path builds the table's media path."""
        assert media_path("fluid_milk_plants") == (
            "/media/5520/number-and-average-size-of-u-s-fluid-milk-product-plants.csv"
        )

    def test_period_end(self):
        """Timeperiod ids resolve to month, quarter, and year end dates."""
        assert period_end(2024, 2) == date(2024, 2, 29)
        assert period_end(2023, 2) == date(2023, 2, 28)
        assert period_end(2026, 5) == date(2026, 5, 31)
        assert period_end(1998, 13) == date(1998, 3, 31)
        assert period_end(1998, 16) == date(1998, 12, 31)
        assert period_end(2020, 17) == date(2020, 12, 31)

    def test_frequency_of(self):
        """Timeperiod ids map to monthly, quarterly, and annual frequencies."""
        assert frequency_of(1) == "monthly"
        assert frequency_of(12) == "monthly"
        assert frequency_of(13) == "quarterly"
        assert frequency_of(16) == "quarterly"
        assert frequency_of(17) == "annual"

    def test_clean_label(self):
        """Labels lose stray whitespace and blank labels become None."""
        assert clean_label("Total beverage milk consumed \r\n") == (
            "Total beverage milk consumed"
        )
        assert clean_label(" Milk cows ") == "Milk cows"
        assert clean_label("") is None
        assert clean_label("  ") is None
        assert clean_label(None) is None

    def test_parse_rows_glance_schema(self):
        """The glance file parses with its singular Unit column and NA rows drop."""
        rows = parse_rows(GLANCE_CSV)
        assert len(rows) == 2
        assert rows[0] == {
            "date": date(2024, 12, 31),
            "year": 2024,
            "period": "Annual",
            "frequency": "annual",
            "sub_table": None,
            "product": None,
            "category": "Consumer Price Indexes",
            "data_item": "All food",
            "data_item_id": None,
            "data_item_description": None,
            "region": None,
            "state": None,
            "value": 2.26,
            "unit": "Year-over-year percent change",
        }
        assert rows[1]["date"] == date(2026, 5, 31)
        assert rows[1]["frequency"] == "monthly"
        assert rows[1]["value"] == 0.6396

    def test_parse_rows_quarterly_schema(self):
        """Quarterly timeperiod ids resolve to quarter end dates."""
        rows = parse_rows(QUARTERLY_CSV)
        assert [row["date"] for row in rows] == [
            date(1998, 3, 31),
            date(1998, 12, 31),
            date(1998, 12, 31),
        ]
        assert [row["frequency"] for row in rows] == [
            "quarterly",
            "quarterly",
            "annual",
        ]
        assert rows[0]["period"] == "JAN-MAR"
        assert rows[2]["value"] == 157441.0
        assert rows[2]["unit"] == "Million pounds"

    def test_parse_rows_products_schema(self):
        """The products file exposes sub_table and product columns."""
        rows = parse_rows(PRODUCTS_CSV)
        assert rows[0]["sub_table"] == "Amer cheese, monthly"
        assert rows[0]["product"] == "American Style Cheese"
        assert rows[0]["category"] == "Supply"
        assert rows[0]["date"] == date(2011, 1, 31)
        assert rows[1]["sub_table"] == "Evap cond whole, annual"
        assert rows[1]["frequency"] == "annual"

    def test_parse_rows_allocation_schema(self):
        """The allocation file exposes item ids and drops NA header rows."""
        rows = parse_rows(ALLOCATION_CSV)
        assert len(rows) == 1
        assert rows[0]["data_item_id"] == "1-1.01.00"
        assert rows[0]["data_item"] == "Milk production (farm level)"
        assert rows[0]["data_item_description"] == (
            "Product volume, Supply , Milk production (farm level)"
        )
        assert rows[0]["date"] == date(2000, 12, 31)

    def test_parse_rows_state_schema(self):
        """The state file exposes region and state and drops empty values."""
        rows = parse_rows(STATE_CSV)
        assert len(rows) == 2
        assert rows[0]["region"] == "Northeast"
        assert rows[0]["state"] == "Connecticut"
        assert rows[0]["sub_table"] == "Milk cows"
        assert rows[1]["state"] == "Total region"
        assert rows[1]["value"] == 100.0

    def test_parse_rows_strips_embedded_newlines(self):
        """The plants file's literal trailing CRLF in Data_item is stripped."""
        rows = parse_rows(PLANTS_CSV)
        assert [row["data_item"] for row in rows] == [
            "Total beverage milk consumed",
            "Number of plants",
        ]
        assert rows[0]["period"] is None
        assert rows[0]["date"] == date(2008, 12, 31)
        assert rows[0]["frequency"] == "annual"

    def test_afetch_table(self, monkeypatch):
        """afetch_table fetches through the ERS cache client and parses the CSV."""
        calls = []

        async def fake_afetch_ers_file(media_path, product=None, ttl=None):
            calls.append((media_path, product))
            return GLANCE_CSV.encode("utf-8-sig")

        monkeypatch.setattr(
            "openbb_government_us.usda.utils.ers_client.afetch_ers_file",
            fake_afetch_ers_file,
        )
        rows = asyncio.run(ers_dairy_data.afetch_table("situation_at_a_glance"))
        assert calls == [
            (
                "/media/5501/us-dairy-situation-at-a-glance-monthly-and-annual.csv",
                ers_dairy_data.PRODUCT_PAGE,
            )
        ]
        assert len(rows) == 2
        assert rows[0]["category"] == "Consumer Price Indexes"


class TestDairyData:
    """Tests for the DairyData model."""

    def test_transform_query(self):
        """transform_query builds the query params model."""
        query = DairyDataFetcher.transform_query(
            {"table": "milk_cows_by_state", "start_year": 2010}
        )
        assert isinstance(query, DairyDataQueryParams)
        assert query.table == "milk_cows_by_state"
        assert query.start_year == 2010

    def test_table_accepts_list_and_comma_string(self):
        """Table accepts a list or a comma-separated string of keys."""
        query = DairyDataQueryParams(table=["fluid_milk_sales", "cheese_per_capita"])
        assert query.table == "fluid_milk_sales,cheese_per_capita"
        query = DairyDataQueryParams(table=" fluid_milk_sales , cheese_per_capita ")
        assert query.table == "fluid_milk_sales,cheese_per_capita"

    def test_table_blank_returns_default(self):
        """Empty or whitespace-only table values normalize to the default."""
        assert DairyDataQueryParams().table == "situation_at_a_glance"
        assert DairyDataQueryParams(table=None).table == "situation_at_a_glance"
        assert DairyDataQueryParams(table="").table == "situation_at_a_glance"
        assert DairyDataQueryParams(table=" , ").table == "situation_at_a_glance"

    def test_unknown_table_raises(self):
        """Unknown table keys raise OpenBBError listing valid choices."""
        with pytest.raises(
            OpenBBError, match="Invalid table.*bogus.*cheese_per_capita"
        ):
            DairyDataQueryParams(table="fluid_milk_sales,bogus")

    def test_aextract_selects_tables(self, monkeypatch):
        """aextract_data fetches only the requested tables, tagged with the key."""
        fetched = []

        async def fake_afetch(table, **kwargs):
            fetched.append(table)
            return [
                {
                    "date": date(2020, 12, 31),
                    "year": 2020,
                    "period": "Annual",
                    "frequency": "annual",
                    "sub_table": None,
                    "product": None,
                    "category": None,
                    "data_item": table,
                    "data_item_id": None,
                    "data_item_description": None,
                    "region": None,
                    "state": None,
                    "value": 1.0,
                    "unit": "Pounds",
                }
            ]

        monkeypatch.setattr(ers_dairy_data, "afetch_table", fake_afetch)
        query = DairyDataFetcher.transform_query(
            {"table": "fluid_milk_sales,cheese_per_capita"}
        )
        records = asyncio.run(DairyDataFetcher.aextract_data(query, None))
        assert fetched == ["fluid_milk_sales", "cheese_per_capita"]
        assert [record["table"] for record in records] == [
            "fluid_milk_sales",
            "cheese_per_capita",
        ]

    def test_transform_data_filters_frequency(self):
        """The frequency filter keeps only matching rows before the pivot."""
        records = [
            _record(table="situation_at_a_glance", year=2026, frequency="monthly"),
            _record(table="situation_at_a_glance", year=2025, frequency="annual"),
        ]
        query = DairyDataFetcher.transform_query({"frequency": "annual"})
        data = DairyDataFetcher.transform_data(query, records)
        assert len(data) == 1
        dumped = data[0].model_dump()
        assert "2025-12-31" in dumped
        assert "2026-12-31" not in dumped

    def test_transform_data_filters_years(self):
        """start_year and end_year select which date columns appear."""
        records = [
            _record(table="production_factors", year=year, frequency="annual")
            for year in (2018, 2019, 2020, 2021)
        ]
        query = DairyDataFetcher.transform_query({"start_year": 2019, "end_year": 2020})
        data = DairyDataFetcher.transform_data(query, records)
        assert len(data) == 1
        date_cols = sorted(k for k in data[0].model_dump() if k.startswith("20"))
        assert date_cols == ["2019-12-31", "2020-12-31"]

    def test_transform_data_pivots_dates_into_columns(self):
        """Each data item is one row with a value column per observation date."""
        records = [
            _record(table="fluid_milk_sales", year=2024, frequency="annual"),
            _record(table="cheese_per_capita", year=2024, frequency="annual"),
            _record(table="cheese_per_capita", year=2023, frequency="annual"),
        ]
        query = DairyDataFetcher.transform_query({})
        data = DairyDataFetcher.transform_data(query, records)
        assert len(data) == 2
        assert data[0].unit == "pounds"
        cheese = data[1].model_dump()
        assert cheese["2023-12-31"] == 1.5
        assert cheese["2024-12-31"] == 1.5

    def test_transform_data_date_columns_are_chronological(self):
        """Date columns are chronological and identical on every row."""
        records = [
            _record(table="fluid_milk_sales", year=year, frequency="annual")
            for year in (2024, 2021, 2023, 2022)
        ] + [_record(table="cheese_per_capita", year=2020, frequency="annual")]
        query = DairyDataFetcher.transform_query({})
        data = DairyDataFetcher.transform_data(query, records)
        dumped = [row.model_dump() for row in data]
        date_cols = [key for key in dumped[0] if key.startswith("20")]
        assert date_cols == [
            "2020-12-31",
            "2021-12-31",
            "2022-12-31",
            "2023-12-31",
            "2024-12-31",
        ]
        assert all(list(row) == list(dumped[0]) for row in dumped)
        assert dumped[0]["2020-12-31"] is None
        assert dumped[1]["2024-12-31"] is None


def _record(table: str, year: int, frequency: str) -> dict:
    """Build a normalized record for transform_data tests.

    Parameters
    ----------
    table : str
        Table key to tag the record with.
    year : int
        Calendar year of the record.
    frequency : str
        Observation frequency of the record.

    Returns
    -------
    dict
        A record shaped like the aextract_data output.
    """
    return {
        "table": table,
        "date": date(year, 12, 31),
        "year": year,
        "period": "Annual",
        "frequency": frequency,
        "sub_table": None,
        "product": None,
        "category": "Category",
        "data_item": "Data item",
        "data_item_id": None,
        "data_item_description": None,
        "region": None,
        "state": None,
        "value": 1.5,
        "unit": "pounds",
    }
