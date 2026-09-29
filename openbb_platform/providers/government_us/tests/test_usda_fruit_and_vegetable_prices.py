"""Tests for the USDA ERS fruit and vegetable prices utils and model."""

import asyncio

import pytest
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.utils.errors import EmptyDataError

from openbb_government_us.usda.models.fruit_and_vegetable_prices import (
    DEFAULT_TABLE,
    FruitAndVegetablePricesData,
    FruitAndVegetablePricesFetcher,
    FruitAndVegetablePricesQueryParams,
)
from openbb_government_us.usda.utils import ers_fruit_and_vegetable_prices
from openbb_government_us.usda.utils.ers_fruit_and_vegetable_prices import (
    DATA_YEAR,
    FVP_TABLES,
    build_url,
    media_path,
    parse_rows,
    parse_value,
)

FRUIT_CSV = (
    "Fruit,Form,AverageRetailPrice,AverageRetailPriceUnitOfMeasure,"
    "PreparationYieldFactor,SizeOfACupEquivalent ,CupEquivalentUnitOfMeasure,"
    "AveragePricePerCupEquivalent\n"
    "Apples,Fresh,1.86093095,per pound,0.9,0.2425,pounds,0.501435057\n"
    '"Apples, applesauce",Canned,1.208099427,per pound,1,0.5401,pounds,0.652533815\n'
    "Apricots,Fresh,3.803731821,per pound,0.93,0.3638,pounds,1.487802023\n"
    "Apricots,Dried,8.634283691,per pound,1,0.1433,pounds,1.237296915\n"
    ",Fresh,1.0,per pound,1,0.5,pounds,1.0\n"
    "Bananas,Fresh,NA,per pound,0.64,0.3307,pounds,0.31498274\n"
)

VEGETABLE_CSV = (
    "Vegetable,Form,AverageRetailPrice,AverageRetailPriceUnitOfMeasure,"
    "PreparationYieldFactor,SizeOfACupEquivalent ,CupEquivalentUnitOfMeasure,"
    "AveragePricePerCupEquivalent\n"
    "Asparagus,Frozen,6.780904794,per pound,1.0335,0.3968,pounds,2.603589725\n"
    "Asparagus,Fresh,3.212453364,per pound,0.4938,0.3968,pounds,2.581435739\n"
    "Asparagus,Canned,3.676296303,per pound,0.65,0.3968,pounds,2.244418891\n"
)


class TestErsFruitAndVegetablePricesUtils:
    """Tests for the ers_fruit_and_vegetable_prices utils module."""

    def test_catalog_contents(self):
        """The catalog holds the fruit and vegetable tables with unique ids."""
        assert set(FVP_TABLES) == {"fruit", "vegetable"}
        assert FVP_TABLES["fruit"]["media_id"] == 6210
        assert FVP_TABLES["vegetable"]["media_id"] == 6240
        assert FVP_TABLES["fruit"]["item_column"] == "Fruit"
        assert FVP_TABLES["vegetable"]["item_column"] == "Vegetable"
        media_ids = [entry["media_id"] for entry in FVP_TABLES.values()]
        assert len(set(media_ids)) == 2
        assert DATA_YEAR == 2023

    def test_media_path(self):
        """media_path builds the table's media path."""
        assert media_path("fruit") == (
            "/media/6210/all-fruits-average-prices-csv-format.csv"
        )
        assert media_path("vegetable") == (
            "/media/6240/all-vegetables-average-prices-csv-format.csv"
        )

    def test_build_url(self):
        """URLs follow the /media/{media_id}/{slug}.csv pattern."""
        assert build_url("fruit") == (
            "https://www.ers.usda.gov/media/6210/"
            "all-fruits-average-prices-csv-format.csv"
        )

    def test_parse_value_handles_commas_and_null_tokens(self):
        """Values parse to floats, stripping commas and null tokens to None."""
        assert parse_value("1.86093095") == 1.86093095
        assert parse_value("1,009.30") == 1009.3
        assert parse_value("") is None
        assert parse_value(None) is None
        assert parse_value("NA") is None

    def test_parse_rows_strips_trailing_space_header_and_renames(self):
        """The trailing-space header is stripped and columns become snake_case."""
        rows = parse_rows(FRUIT_CSV, "fruit")
        assert rows[0] == {
            "item": "Apples",
            "form": "Fresh",
            "average_retail_price": 1.86093095,
            "average_retail_price_unit": "per pound",
            "preparation_yield_factor": 0.9,
            "cup_equivalent_size": 0.2425,
            "cup_equivalent_unit": "pounds",
            "average_price_per_cup_equivalent": 0.501435057,
        }

    def test_parse_rows_keeps_full_precision(self):
        """Numeric measures are kept at full source precision."""
        rows = parse_rows(FRUIT_CSV, "fruit")
        applesauce = next(r for r in rows if r["item"] == "Apples, applesauce")
        assert applesauce["average_price_per_cup_equivalent"] == 0.652533815
        assert applesauce["form"] == "Canned"

    def test_parse_rows_skips_blank_item(self):
        """A row with a blank item cell is skipped."""
        rows = parse_rows(FRUIT_CSV, "fruit")
        assert all(row["item"] for row in rows)
        assert len(rows) == 5

    def test_parse_rows_null_token_measure_becomes_none(self):
        """A null-token numeric measure is coerced to None, keeping the row."""
        rows = parse_rows(FRUIT_CSV, "fruit")
        bananas = next(r for r in rows if r["item"] == "Bananas")
        assert bananas["average_retail_price"] is None
        assert bananas["average_price_per_cup_equivalent"] == 0.31498274

    def test_parse_rows_uses_vegetable_item_column(self):
        """The vegetable table reads its Vegetable item column."""
        rows = parse_rows(VEGETABLE_CSV, "vegetable")
        assert {row["item"] for row in rows} == {"Asparagus"}
        assert {row["form"] for row in rows} == {"Fresh", "Canned", "Frozen"}

    def test_afetch_table(self, monkeypatch):
        """afetch_table fetches through the ERS cache client and parses the CSV."""
        calls = []

        async def fake_afetch_ers_file(path, product=None, ttl=None):
            calls.append((path, product))
            return FRUIT_CSV.encode("utf-8-sig")

        monkeypatch.setattr(
            "openbb_government_us.usda.utils.ers_client.afetch_ers_file",
            fake_afetch_ers_file,
        )
        rows = asyncio.run(ers_fruit_and_vegetable_prices.afetch_table("fruit"))
        assert calls == [
            (
                "/media/6210/all-fruits-average-prices-csv-format.csv",
                ers_fruit_and_vegetable_prices.PRODUCT_PAGE,
            )
        ]
        assert rows[0]["item"] == "Apples"


class TestFruitAndVegetablePrices:
    """Tests for the FruitAndVegetablePrices model."""

    def test_transform_query_default_table(self):
        """transform_query defaults the table to fruit."""
        query = FruitAndVegetablePricesFetcher.transform_query({})
        assert isinstance(query, FruitAndVegetablePricesQueryParams)
        assert query.table == DEFAULT_TABLE

    def test_table_defaults_when_blank(self):
        """Empty, None, or empty-list table values normalize to the default."""
        assert FruitAndVegetablePricesQueryParams().table == "fruit"
        assert FruitAndVegetablePricesQueryParams(table=None).table == "fruit"
        assert FruitAndVegetablePricesQueryParams(table="").table == "fruit"
        assert FruitAndVegetablePricesQueryParams(table=[]).table == "fruit"

    def test_table_accepts_list_and_whitespace(self):
        """A single-item list or padded string resolves to one table key."""
        assert FruitAndVegetablePricesQueryParams(table=["vegetable"]).table == (
            "vegetable"
        )
        assert FruitAndVegetablePricesQueryParams(table=" Vegetable ").table == (
            "vegetable"
        )
        assert FruitAndVegetablePricesQueryParams(table=["", "fruit"]).table == "fruit"

    def test_unknown_table_raises(self):
        """Unknown table keys raise OpenBBError listing valid choices."""
        with pytest.raises(OpenBBError, match="Invalid table: bogus"):
            FruitAndVegetablePricesQueryParams(table="bogus")

    def test_aextract_selects_table(self, monkeypatch):
        """aextract_data fetches only the queried table."""
        fetched = []

        async def fake_afetch_table(table, **kwargs):
            fetched.append(table)
            return [{"item": table, "form": "Fresh"}]

        monkeypatch.setattr(
            ers_fruit_and_vegetable_prices, "afetch_table", fake_afetch_table
        )
        query = FruitAndVegetablePricesFetcher.transform_query({"table": "vegetable"})
        records = asyncio.run(FruitAndVegetablePricesFetcher.aextract_data(query, None))
        assert fetched == ["vegetable"]
        assert records == [{"item": "vegetable", "form": "Fresh"}]

    def test_transform_data_orders_by_item_then_form(self):
        """Rows sort by item ascending, then by form."""
        records = parse_rows(FRUIT_CSV, "fruit")
        query = FruitAndVegetablePricesFetcher.transform_query({})
        data = FruitAndVegetablePricesFetcher.transform_data(query, records)
        assert [(row.item, row.form) for row in data] == [
            ("Apples", "Fresh"),
            ("Apples, applesauce", "Canned"),
            ("Apricots", "Dried"),
            ("Apricots", "Fresh"),
            ("Bananas", "Fresh"),
        ]
        assert isinstance(data[0], FruitAndVegetablePricesData)

    def test_transform_data_full_precision(self):
        """The pivoted rows carry every measure at full precision."""
        records = parse_rows(VEGETABLE_CSV, "vegetable")
        query = FruitAndVegetablePricesFetcher.transform_query({"table": "vegetable"})
        data = FruitAndVegetablePricesFetcher.transform_data(query, records)
        canned = next(row for row in data if row.form == "Canned")
        dumped = canned.model_dump()
        assert dumped["average_retail_price"] == 3.676296303
        assert dumped["average_price_per_cup_equivalent"] == 2.244418891
        assert dumped["cup_equivalent_size"] == 0.3968
        assert dumped["cup_equivalent_unit"] == "pounds"

    def test_transform_data_empty_raises(self):
        """An empty dataset raises EmptyDataError."""
        query = FruitAndVegetablePricesFetcher.transform_query({})
        with pytest.raises(EmptyDataError):
            FruitAndVegetablePricesFetcher.transform_data(query, [])

    def test_data_model_widget_config(self):
        """The model carries the whole-widget and per-field widget configs."""
        widget = FruitAndVegetablePricesData.model_config["json_schema_extra"][
            "x-widget_config"
        ]
        assert widget["$.name"] == "USDA ERS Fruit & Vegetable Prices"
        assert widget["$.category"] == "Economy"
        assert widget["$.subCategory"] == "Agriculture"
        assert widget["$.source"] == ["USDA", "ERS"]
        fields = FruitAndVegetablePricesData.model_fields
        assert fields["item"].json_schema_extra["x-widget_config"]["pinned"] == "left"
        assert fields["form"].json_schema_extra["x-widget_config"]["pinned"] == "left"
        assert (
            fields["average_retail_price"].json_schema_extra["x-widget_config"][
                "cellDataType"
            ]
            == "number"
        )

    def test_query_param_options(self):
        """The table param exposes labeled single-select options."""
        config = FruitAndVegetablePricesQueryParams.__json_schema_extra__["table"][
            "x-widget_config"
        ]
        assert config["multiSelect"] is False
        assert config["multiple"] is False
        assert config["value"] == "fruit"
        assert config["options"] == [
            {"label": "Fruit", "value": "fruit"},
            {"label": "Vegetable", "value": "vegetable"},
        ]
