"""Tests for the USDA ERS Food Price Outlook utils and model."""

import asyncio
from datetime import date

import pytest
from openbb_core.app.model.abstract.error import OpenBBError

from openbb_government_us.usda.models.food_price_outlook import (
    DEFAULT_TABLE,
    TABLE_LABELS,
    FoodPriceOutlookData,
    FoodPriceOutlookFetcher,
    FoodPriceOutlookQueryParams,
)
from openbb_government_us.usda.utils import ers_food_price_outlook
from openbb_government_us.usda.utils.ers_food_price_outlook import (
    CPI_ITEMS,
    FOOD_PRICE_OUTLOOK_FILES,
    PPI_ITEMS,
    PRODUCT_PAGE,
    _item_value,
    attribute_year,
    build_url,
    clean_label,
    media_path,
    normalize_item,
    parse_annual_rows,
    parse_history_rows,
    parse_snapshot_rows,
    parse_table,
    table_items,
)

SNAPSHOT_CPI_CSV = (
    "Top-level,Aggregate,Mid-level,Low-level,Disaggregate,Attribute,Unit,Value\n"
    "All food,,,,,Relative importance,Percent,100.0\n"
    "All food,,,,,Month-to-month April 2026 to May 2026,Percent change,0.2\n"
    "All food,,,,,Annual 2023,Percent change,5.8\n"
    "All food,,,,,Lower bound of prediction interval 2026,Percent change,2.2\n"
    "All food,Food at home,Meats poultry and fish,Meats,Beef and veal,"
    "Annual 2024,Percent change,5.4\n"
    "All food,Food at home,Meats poultry and fish,Meats,Beef and veal¹,"
    "Annual 2023*,Percent change,3.6\n"
    "All food,Food at home,,,,Annual 2025,Percent change,2.3\n"
    "All food,,,,,Annual 2025,Percent change,\n"
)

SNAPSHOT_PPI_CSV = (
    "Producer Price Index item,Attribute,Unit,Value\n"
    "Unprocessed foodstuffs and feedstuffs,Annual 2023,Percent change,-10.3\n"
    "Unprocessed foodstuffs and feedstuffs,"
    "Month-to-month April 2026 to May 2026,Percent change,5.5\n"
    "Farm-level fruit,Annual 2024,Percent change,3.0\n"
    "Processed foods and feeds,Annual 2025,Percent change,\n"
)

ANNUAL_CSV = (
    "Consumer Price Index item,Year,Percent change\n"
    "All food,1974,14.3\n"
    "Food away from home,1974,12.7\n"
    "All food,1975,8.5\n"
    "Food away from home,1975,5.8\n"
    "All food,1976,\n"
)

HISTORY_CSV = (
    "Consumer Price Index item,Month of forecast,Year of forecast,"
    "Year being forecast,Attribute,Forecast percent change\n"
    "All food,7,2002,2003,Lower bound of prediction interval,-0.2\n"
    "All food,7,2002,2003,Mid point of prediction interval,1.9\n"
    "All food,7,2002,2003,Upper bound of prediction interval,4.1\n"
    "All food,8,2002,2003,Lower bound of prediction interval,-0.2\n"
    "All food,8,2002,2003,Mid point of prediction interval,1.8\n"
    "Eggs,7,2002,2003,Mid point of prediction interval,\n"
)


class TestErsFoodPriceOutlookUtils:
    """Tests for the ers_food_price_outlook utils module."""

    def test_catalog_contents(self):
        """The catalog holds the six tidy tables with kind and index metadata."""
        assert len(FOOD_PRICE_OUTLOOK_FILES) == 6
        assert {entry["kind"] for entry in FOOD_PRICE_OUTLOOK_FILES.values()} == {
            "snapshot",
            "annual",
            "history",
        }
        assert {entry["index"] for entry in FOOD_PRICE_OUTLOOK_FILES.values()} == {
            "cpi",
            "ppi",
        }
        for entry in FOOD_PRICE_OUTLOOK_FILES.values():
            assert isinstance(entry["media_id"], int)
            assert entry["slug"]
        assert FOOD_PRICE_OUTLOOK_FILES["cpi_forecast"]["media_id"] == 6460

    def test_table_items(self):
        """table_items returns the CPI or PPI item map for the table's index."""
        assert table_items("cpi_forecast") is CPI_ITEMS
        assert table_items("ppi_annual") is PPI_ITEMS

    def test_media_path_and_url(self):
        """media_path and build_url follow the /media/{id}/{slug}.csv pattern."""
        assert media_path("cpi_forecast") == (
            "/media/6460/changes-in-consumer-price-indexes-2023-through-2026.csv"
        )
        assert build_url("cpi_forecast") == (
            "https://www.ers.usda.gov/media/6460/"
            "changes-in-consumer-price-indexes-2023-through-2026.csv"
        )

    def test_clean_label(self):
        """clean_label strips footnote superscripts, asterisks, and whitespace."""
        assert clean_label("  All food  ") == "All food"
        assert clean_label("Beef and veal¹") == "Beef and veal"
        assert clean_label("Annual 2023*") == "Annual 2023"
        assert clean_label(None) == ""

    def test_normalize_item_renames(self):
        """normalize_item applies the known cross-file spelling variant."""
        assert normalize_item("Farm-level fruit") == "Farm-level fruits"
        assert normalize_item("  All food ") == "All food"

    def test_attribute_year(self):
        """attribute_year parses the trailing year, else returns None."""
        assert attribute_year("Annual 2023") == 2023
        assert attribute_year("Lower bound of prediction interval 2026") == 2026
        assert attribute_year("Mid point of prediction interval 2026") == 2026
        assert attribute_year("Month-to-month April 2026 to May 2026") is None
        assert attribute_year("Relative importance") is None

    def test_item_value_missing_column_raises(self):
        """_item_value raises when no price-index item column is present."""
        with pytest.raises(OpenBBError, match="No 'Price Index item' column"):
            _item_value({"Attribute": "Annual 2023"})

    def test_parse_snapshot_rows_cpi_hierarchy(self):
        """The CPI snapshot parser reads the hierarchy and attribute year."""
        rows = parse_snapshot_rows(SNAPSHOT_CPI_CSV)
        assert len(rows) == 7
        all_food = rows[0]
        assert all_food["item"] == "All food"
        assert all_food["top_level"] == "All food"
        assert all_food["aggregate"] is None
        assert all_food["attribute"] == "Relative importance"
        assert all_food["year"] is None
        assert all_food["value"] == 100.0
        beef = rows[4]
        assert beef["item"] == "Beef and veal"
        assert beef["low_level"] == "Meats"
        assert beef["disaggregate"] == "Beef and veal"
        assert beef["attribute"] == "Annual 2024"
        assert beef["year"] == 2024
        superscript = rows[5]
        assert superscript["item"] == "Beef and veal"
        assert superscript["attribute"] == "Annual 2023"
        assert superscript["year"] == 2023

    def test_parse_snapshot_rows_ppi_and_rename(self):
        """The PPI snapshot parser uses the item column and renames variants."""
        rows = parse_snapshot_rows(SNAPSHOT_PPI_CSV)
        assert len(rows) == 3
        assert rows[0]["item"] == "Unprocessed foodstuffs and feedstuffs"
        assert "top_level" not in rows[0]
        assert rows[2]["item"] == "Farm-level fruits"

    def test_parse_annual_rows(self):
        """The annual parser types the year and skips blank percent changes."""
        rows = parse_annual_rows(ANNUAL_CSV)
        assert len(rows) == 4
        assert rows[0] == {
            "item": "All food",
            "attribute": "Annual percent change",
            "unit": "Percent change",
            "year": 1974,
            "value": 14.3,
        }
        assert all(isinstance(row["year"], int) for row in rows)

    def test_parse_history_rows(self):
        """The history parser builds the forecast date and skips blanks."""
        rows = parse_history_rows(HISTORY_CSV)
        assert len(rows) == 5
        assert rows[0] == {
            "item": "All food",
            "attribute": "Lower bound of prediction interval",
            "unit": "Percent change",
            "year": 2003,
            "forecast_date": date(2002, 7, 1),
            "value": -0.2,
        }
        assert rows[3]["forecast_date"] == date(2002, 8, 1)

    def test_parse_table_dispatch(self):
        """parse_table dispatches to the parser matching the table's kind."""
        assert len(parse_table(SNAPSHOT_CPI_CSV, "cpi_forecast")) == 7
        assert len(parse_table(ANNUAL_CSV, "cpi_annual")) == 4
        assert len(parse_table(HISTORY_CSV, "cpi_forecast_history")) == 5

    def test_afetch_table(self, monkeypatch):
        """afetch_table downloads through the ERS cache and parses the CSV."""
        calls = []

        async def fake_afetch_ers_file(path, product=None, ttl=None):
            calls.append((path, product))
            return SNAPSHOT_CPI_CSV.encode("utf-8-sig")

        monkeypatch.setattr(
            "openbb_government_us.usda.utils.ers_client.afetch_ers_file",
            fake_afetch_ers_file,
        )
        rows = asyncio.run(ers_food_price_outlook.afetch_table("cpi_forecast"))
        assert calls == [(media_path("cpi_forecast"), PRODUCT_PAGE)]
        assert len(rows) == 7
        assert rows[0]["item"] == "All food"


class TestFoodPriceOutlookQueryParams:
    """Tests for the FoodPriceOutlook query parameters."""

    def test_table_labels_cover_catalog(self):
        """Every catalog table has a display label."""
        assert set(TABLE_LABELS) == set(FOOD_PRICE_OUTLOOK_FILES)

    def test_table_default_blank_and_whitespace(self):
        """A blank table falls back to the default and padding is stripped."""
        assert FoodPriceOutlookQueryParams().table == DEFAULT_TABLE
        assert FoodPriceOutlookQueryParams(table="").table == DEFAULT_TABLE
        assert FoodPriceOutlookQueryParams(table=None).table == DEFAULT_TABLE
        assert FoodPriceOutlookQueryParams(table="  ppi_annual  ").table == "ppi_annual"

    def test_unknown_table_raises(self):
        """An unknown table raises OpenBBError listing valid choices."""
        with pytest.raises(OpenBBError, match="Invalid table: bogus"):
            FoodPriceOutlookQueryParams(table="bogus")

    def test_non_string_table_raises(self):
        """A non-string, non-empty table value raises OpenBBError."""
        with pytest.raises(OpenBBError, match="Invalid table"):
            FoodPriceOutlookQueryParams(table=123)

    def test_item_normalization(self):
        """The item filter normalizes to a single stripped name, commas kept."""
        assert (
            FoodPriceOutlookQueryParams(item="  Meats, poultry, and fish  ").item
            == "Meats, poultry, and fish"
        )
        assert (
            FoodPriceOutlookQueryParams(item=["Beef and veal"]).item == "Beef and veal"
        )
        assert FoodPriceOutlookQueryParams(item="").item is None
        assert FoodPriceOutlookQueryParams(item="   ").item is None


class TestFoodPriceOutlook:
    """Tests for the FoodPriceOutlook fetcher and pivot."""

    def test_transform_query(self):
        """transform_query builds the query params model."""
        query = FoodPriceOutlookFetcher.transform_query(
            {"table": "cpi_annual", "start_year": 2000}
        )
        assert isinstance(query, FoodPriceOutlookQueryParams)
        assert query.table == "cpi_annual"
        assert query.start_year == 2000

    def test_aextract_data_fetches_selected_table(self, monkeypatch):
        """aextract_data fetches only the selected table's rows."""
        fetched = []

        async def fake_afetch_table(table, **kwargs):
            fetched.append(table)
            return [{"table": table}]

        monkeypatch.setattr(ers_food_price_outlook, "afetch_table", fake_afetch_table)
        query = FoodPriceOutlookFetcher.transform_query({"table": "ppi_forecast"})
        records = asyncio.run(FoodPriceOutlookFetcher.aextract_data(query, None))
        assert fetched == ["ppi_forecast"]
        assert records == [{"table": "ppi_forecast"}]

    def test_transform_data_snapshot_cpi_pivots_attributes(self):
        """The CPI snapshot spreads attributes into columns, one row per item."""
        records = parse_table(SNAPSHOT_CPI_CSV, "cpi_forecast")
        query = FoodPriceOutlookFetcher.transform_query({"table": "cpi_forecast"})
        data = FoodPriceOutlookFetcher.transform_data(query, records)
        assert [row.item for row in data] == [
            "All food",
            "Beef and veal",
            "Food at home",
        ]
        all_food = data[0].model_dump()
        assert all_food["Relative importance"] == 100.0
        assert all_food["Annual 2023"] == 5.8
        assert all_food["Lower bound of prediction interval 2026"] == 2.2
        assert all_food["year"] is None
        beef = data[1].model_dump()
        assert beef["disaggregate"] == "Beef and veal"
        assert beef["Annual 2024"] == 5.4
        assert beef["Annual 2023"] == 3.6

    def test_transform_data_snapshot_item_filters_rows(self):
        """The item filter keeps only the exactly named row for the snapshot table."""
        records = parse_table(SNAPSHOT_CPI_CSV, "cpi_forecast")
        query = FoodPriceOutlookFetcher.transform_query(
            {"table": "cpi_forecast", "item": "Beef and veal"}
        )
        data = FoodPriceOutlookFetcher.transform_data(query, records)
        assert [row.item for row in data] == ["Beef and veal"]
        partial = FoodPriceOutlookFetcher.transform_query(
            {"table": "cpi_forecast", "item": "beef"}
        )
        assert FoodPriceOutlookFetcher.transform_data(partial, records) == []

    def test_transform_data_snapshot_year_filters_columns(self):
        """The year filter drops year-bearing measures but keeps year-less ones."""
        records = parse_table(SNAPSHOT_CPI_CSV, "cpi_forecast")
        query = FoodPriceOutlookFetcher.transform_query(
            {"table": "cpi_forecast", "start_year": 2024}
        )
        data = FoodPriceOutlookFetcher.transform_data(query, records)
        all_food = data[0].model_dump()
        assert "Annual 2023" not in all_food
        assert all_food["Relative importance"] == 100.0
        assert all_food["Lower bound of prediction interval 2026"] == 2.2
        assert [row.item for row in data] == [
            "All food",
            "Beef and veal",
            "Food at home",
        ]

    def test_transform_data_snapshot_ppi(self):
        """The PPI snapshot pivots without hierarchy and renames items."""
        records = parse_table(SNAPSHOT_PPI_CSV, "ppi_forecast")
        query = FoodPriceOutlookFetcher.transform_query({"table": "ppi_forecast"})
        data = FoodPriceOutlookFetcher.transform_data(query, records)
        items = {row.item for row in data}
        assert items == {"Unprocessed foodstuffs and feedstuffs", "Farm-level fruits"}
        unprocessed = next(
            row for row in data if row.item == "Unprocessed foodstuffs and feedstuffs"
        ).model_dump()
        assert unprocessed["Annual 2023"] == -10.3
        assert unprocessed["Month-to-month April 2026 to May 2026"] == 5.5
        assert unprocessed["top_level"] is None

    def test_transform_data_annual_pivots_items_into_columns(self):
        """The annual table spreads items into columns with the year as the row label."""
        records = parse_table(ANNUAL_CSV, "cpi_annual")
        query = FoodPriceOutlookFetcher.transform_query({"table": "cpi_annual"})
        data = FoodPriceOutlookFetcher.transform_data(query, records)
        assert [row.item for row in data] == ["1974", "1975"]
        first = data[0].model_dump()
        assert first["All food"] == 14.3
        assert first["Food away from home"] == 12.7
        assert first["unit"] == "Percent change"
        assert first["year"] is None

    def test_transform_data_annual_item_filters_columns(self):
        """The item filter keeps only matching value columns for the annual table."""
        records = parse_table(ANNUAL_CSV, "cpi_annual")
        query = FoodPriceOutlookFetcher.transform_query(
            {"table": "cpi_annual", "item": "all food"}
        )
        data = FoodPriceOutlookFetcher.transform_data(query, records)
        first = data[0].model_dump()
        assert first["All food"] == 14.3
        assert "Food away from home" not in first

    def test_transform_data_annual_year_filters_rows(self):
        """start_year and end_year select which year rows appear on annual tables."""
        records = parse_table(ANNUAL_CSV, "cpi_annual")
        query = FoodPriceOutlookFetcher.transform_query(
            {"table": "cpi_annual", "start_year": 1975, "end_year": 1975}
        )
        data = FoodPriceOutlookFetcher.transform_data(query, records)
        assert [row.item for row in data] == ["1975"]

    def test_transform_data_history_pivots_bounds_and_vintages(self):
        """The history table pivots bounds into columns, one row per vintage."""
        records = parse_table(HISTORY_CSV, "cpi_forecast_history")
        query = FoodPriceOutlookFetcher.transform_query(
            {"table": "cpi_forecast_history"}
        )
        data = FoodPriceOutlookFetcher.transform_data(query, records)
        assert [row.forecast_date for row in data] == [
            date(2002, 7, 1),
            date(2002, 8, 1),
        ]
        july = data[0].model_dump()
        assert july["item"] == "All food"
        assert july["year"] == 2003
        assert july["Lower bound of prediction interval"] == -0.2
        assert july["Mid point of prediction interval"] == 1.9
        assert july["Upper bound of prediction interval"] == 4.1
        august = data[1].model_dump()
        assert august["Mid point of prediction interval"] == 1.8
        assert "Upper bound of prediction interval" not in august

    def test_transform_data_history_filters(self):
        """The item and year filters drop non-matching history rows."""
        records = parse_table(HISTORY_CSV, "cpi_forecast_history")
        empty = FoodPriceOutlookFetcher.transform_data(
            FoodPriceOutlookFetcher.transform_query(
                {"table": "cpi_forecast_history", "start_year": 2004}
            ),
            records,
        )
        assert empty == []
        eggs = FoodPriceOutlookFetcher.transform_data(
            FoodPriceOutlookFetcher.transform_query(
                {"table": "cpi_forecast_history", "item": "eggs"}
            ),
            records,
        )
        assert eggs == []

    def test_data_model_dynamic_columns_and_null_tokens(self):
        """The Data model keeps dynamic columns and coerces placeholder tokens."""
        row = FoodPriceOutlookData.model_validate(
            {
                "table": "cpi_annual",
                "year": 2025,
                "unit": "Percent change",
                "All food": 2.899999999,
                "Eggs": "--",
            }
        )
        dumped = row.model_dump()
        assert dumped["All food"] == 2.899999999
        assert dumped["Eggs"] is None
