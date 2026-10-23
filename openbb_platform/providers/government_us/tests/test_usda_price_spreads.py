"""Tests for the USDA ERS price spreads utils and model."""

import asyncio

import pytest
from openbb_core.app.model.abstract.error import OpenBBError

from openbb_government_us.usda.models.price_spreads import (
    FarmToConsumerPriceSpreadsFetcher,
    FarmToConsumerPriceSpreadsQueryParams,
)
from openbb_government_us.usda.utils import ers_price_spreads
from openbb_government_us.usda.utils.ers_price_spreads import (
    PRICE_SPREADS_FILES,
    build_url,
    parse_attribute,
    parse_rows,
)

SAMPLE_CSV = (
    "Commodity,Year,Attribute,Value\n"
    "Fresh apples,2015,Retail price (cents/pound),155.11\n"
    "Fresh apples,2016,Farm price (cents/pound),\n"
    "Fresh apples,2016,Farm share (percent),21.37\n"
)


class TestErsPriceSpreadsUtils:
    """Tests for the ers_price_spreads utils module."""

    def test_catalog_contents(self):
        """The catalog holds the 24 current items with unique ids and slugs."""
        assert len(PRICE_SPREADS_FILES) == 24
        categories = {entry["category"] for entry in PRICE_SPREADS_FILES.values()}
        assert categories == {
            "dairy",
            "fresh_fruit",
            "fresh_vegetables",
            "processed",
            "field_crops",
        }
        media_ids = [entry["media_id"] for entry in PRICE_SPREADS_FILES.values()]
        assert len(set(media_ids)) == 24
        slugs = [entry["slug"] for entry in PRICE_SPREADS_FILES.values()]
        assert len(set(slugs)) == 24

    def test_build_url(self):
        """URLs follow the /media/{media_id}/{slug}.csv pattern."""
        assert (
            build_url("milk_and_dairy_basket")
            == "https://www.ers.usda.gov/media/5716/milk-and-dairy-basket.csv"
        )
        assert build_url("orange_juice_nfc") == (
            "https://www.ers.usda.gov/media/5762/"
            "orange-juice-not-from-concentrate-one-gallon.csv"
        )

    def test_parse_attribute_price_measures(self):
        """Price, value, and share attributes map to snake_case measures."""
        assert parse_attribute("Retail price (dollars/pound)") == (
            "retail_price",
            "dollars/pound",
        )
        assert parse_attribute("Farm price (cents/pound)") == (
            "farm_price",
            "cents/pound",
        )
        assert parse_attribute("Farm value (dollars/gallon)") == (
            "farm_value",
            "dollars/gallon",
        )
        assert parse_attribute("Farm share (percent)") == ("farm_share", "percent")

    def test_parse_attribute_normalizes_plural_pounds(self):
        """The fresh-grapes 'cents/pounds' unit is normalized to 'cents/pound'."""
        assert parse_attribute("Retail price (cents/pounds)") == (
            "retail_price",
            "cents/pound",
        )
        assert parse_attribute("Farm price (cents/pounds)") == (
            "farm_price",
            "cents/pound",
        )

    def test_parse_attribute_basket_index_units(self):
        """Basket attributes keep the index base as the unit."""
        assert parse_attribute("Retail cost (2022 = 100)") == (
            "retail_cost_index",
            "2022 = 100",
        )
        assert parse_attribute("Farm value (2018 = 100)") == (
            "farm_value_index",
            "2018 = 100",
        )
        assert parse_attribute("Farm-to-retail spread (2022 = 100)") == (
            "farm_to_retail_spread_index",
            "2022 = 100",
        )
        assert parse_attribute("Farm-value share (percent)") == (
            "farm_share",
            "percent",
        )

    def test_parse_attribute_rejects_unparenthesized(self):
        """Attributes without a parenthesized unit raise OpenBBError."""
        with pytest.raises(OpenBBError, match="Unrecognized attribute format"):
            parse_attribute("Farm share-Percent")

    def test_parse_attribute_rejects_unknown_measure(self):
        """Unknown measure text raises OpenBBError."""
        with pytest.raises(OpenBBError, match="Unrecognized measure"):
            parse_attribute("Wholesale price (dollars/pound)")

    def test_parse_rows_skips_empty_values(self):
        """Rows with an empty Value are dropped and values parse as floats."""
        rows = parse_rows(SAMPLE_CSV)
        assert rows == [
            {
                "commodity": "Fresh apples",
                "year": "2015",
                "attribute": "Retail price (cents/pound)",
                "value": 155.11,
            },
            {
                "commodity": "Fresh apples",
                "year": "2016",
                "attribute": "Farm share (percent)",
                "value": 21.37,
            },
        ]

    def test_parse_rows_keeps_marketing_year_strings(self):
        """Marketing-year Year strings pass through unchanged."""
        text = (
            "Commodity,Year,Attribute,Value\n"
            "Fresh oranges,2024/25,Farm share (percent),17.64\n"
        )
        assert parse_rows(text) == [
            {
                "commodity": "Fresh oranges",
                "year": "2024/25",
                "attribute": "Farm share (percent)",
                "value": 17.64,
            }
        ]

    def test_media_path(self):
        """media_path builds the item's media path."""
        assert (
            ers_price_spreads.media_path("fresh_apples")
            == "/media/5736/fresh-apples.csv"
        )

    def test_afetch_item(self, monkeypatch):
        """afetch_item fetches through the ERS cache client and parses the CSV."""
        calls = []

        async def fake_afetch_ers_file(media_path, product=None, ttl=None):
            calls.append((media_path, product))
            return SAMPLE_CSV.encode("utf-8-sig")

        monkeypatch.setattr(
            "openbb_government_us.usda.utils.ers_client.afetch_ers_file",
            fake_afetch_ers_file,
        )
        rows = asyncio.run(ers_price_spreads.afetch_item("fresh_apples"))
        assert calls == [
            ("/media/5736/fresh-apples.csv", ers_price_spreads.PRODUCT_PAGE)
        ]
        assert len(rows) == 2
        assert rows[0]["commodity"] == "Fresh apples"


class TestFarmToConsumerPriceSpreads:
    """Tests for the FarmToConsumerPriceSpreads model."""

    def test_transform_query(self):
        """transform_query builds the query params model."""
        query = FarmToConsumerPriceSpreadsFetcher.transform_query(
            {"item": "sugar", "start_year": 2010}
        )
        assert isinstance(query, FarmToConsumerPriceSpreadsQueryParams)
        assert query.item == "sugar"
        assert query.start_year == 2010

    def test_item_accepts_list_and_comma_string(self):
        """Item accepts a list or a comma-separated string of slugs."""
        query = FarmToConsumerPriceSpreadsQueryParams(item=["fresh_apples", "sugar"])
        assert query.item == "fresh_apples,sugar"
        query = FarmToConsumerPriceSpreadsQueryParams(item=" fresh_apples , sugar ")
        assert query.item == "fresh_apples,sugar"

    def test_item_blank_returns_none(self):
        """Empty or whitespace-only item values normalize to None."""
        assert FarmToConsumerPriceSpreadsQueryParams(item=None).item is None
        assert FarmToConsumerPriceSpreadsQueryParams(item="").item is None
        assert FarmToConsumerPriceSpreadsQueryParams(item=" , ").item is None

    def test_unknown_item_raises(self):
        """Unknown item slugs raise OpenBBError listing valid choices."""
        with pytest.raises(OpenBBError, match="Invalid item.*bogus.*fresh_apples"):
            FarmToConsumerPriceSpreadsQueryParams(item="fresh_apples,bogus")

    def test_aextract_selects_by_item(self, monkeypatch):
        """aextract_data fetches only the requested items, tagged with category."""
        fetched = []

        async def fake_afetch(item, **kwargs):
            fetched.append(item)
            return [
                {
                    "commodity": item,
                    "year": "2020",
                    "attribute": "Farm share (percent)",
                    "value": 25.0,
                }
            ]

        monkeypatch.setattr(ers_price_spreads, "afetch_item", fake_afetch)
        query = FarmToConsumerPriceSpreadsFetcher.transform_query(
            {"item": "sugar,whole_milk"}
        )
        records = asyncio.run(
            FarmToConsumerPriceSpreadsFetcher.aextract_data(query, None)
        )
        assert fetched == ["sugar", "whole_milk"]
        assert [record["item"] for record in records] == ["sugar", "whole_milk"]
        assert [record["category"] for record in records] == ["field_crops", "dairy"]

    def test_aextract_selects_by_category(self, monkeypatch):
        """aextract_data with only a category fetches every item in it."""

        async def fake_afetch(item, **kwargs):
            return []

        monkeypatch.setattr(ers_price_spreads, "afetch_item", fake_afetch)
        query = FarmToConsumerPriceSpreadsFetcher.transform_query(
            {"category": "field_crops"}
        )
        records = asyncio.run(
            FarmToConsumerPriceSpreadsFetcher.aextract_data(query, None)
        )
        assert records == []

    def test_aextract_category_filters_items(self, monkeypatch):
        """aextract_data intersects the item list with the category filter."""
        fetched = []

        async def fake_afetch(item, **kwargs):
            fetched.append(item)
            return []

        monkeypatch.setattr(ers_price_spreads, "afetch_item", fake_afetch)
        query = FarmToConsumerPriceSpreadsFetcher.transform_query(
            {"item": "sugar,whole_milk", "category": "dairy"}
        )
        asyncio.run(FarmToConsumerPriceSpreadsFetcher.aextract_data(query, None))
        assert fetched == ["whole_milk"]

    def test_aextract_conflicting_filters_raise(self):
        """An item/category combination matching nothing raises OpenBBError."""
        query = FarmToConsumerPriceSpreadsFetcher.transform_query(
            {"item": "sugar", "category": "dairy"}
        )
        with pytest.raises(OpenBBError, match="No items match"):
            asyncio.run(FarmToConsumerPriceSpreadsFetcher.aextract_data(query, None))

    def test_transform_data_splits_marketing_year(self):
        """Marketing-year strings split into a start year and the raw string."""
        query = FarmToConsumerPriceSpreadsFetcher.transform_query({})
        data = FarmToConsumerPriceSpreadsFetcher.transform_data(
            query,
            [
                {
                    "item": "fresh_oranges",
                    "category": "fresh_fruit",
                    "commodity": "Fresh oranges",
                    "year": "2024/25",
                    "attribute": "Retail price (cents/pound)",
                    "value": 144.75,
                },
                {
                    "item": "fresh_apples",
                    "category": "fresh_fruit",
                    "commodity": "Fresh apples",
                    "year": "2024",
                    "attribute": "Retail price (cents/pound)",
                    "value": 155.11,
                },
            ],
        )
        assert data[0].commodity == "Fresh apples"
        assert data[0].year == 2024
        assert data[0].marketing_year is None
        assert data[1].commodity == "Fresh oranges"
        assert data[1].year == 2024
        assert data[1].marketing_year == "2024/25"

    def test_transform_data_filters_years(self):
        """start_year and end_year filter on the integer year."""
        records = [
            {
                "item": "sugar",
                "category": "field_crops",
                "commodity": "Sugar, white, per pound",
                "year": str(year),
                "attribute": "Farm share (percent)",
                "value": float(year),
            }
            for year in (2018, 2019, 2020, 2021)
        ]
        query = FarmToConsumerPriceSpreadsFetcher.transform_query(
            {"start_year": 2019, "end_year": 2020}
        )
        data = FarmToConsumerPriceSpreadsFetcher.transform_data(query, records)
        assert [row.year for row in data] == [2019, 2020]

    def test_transform_data_pivots_measures_into_columns(self):
        """Each measure becomes its own column, one row per item and year."""
        records = [
            {
                "item": "milk_and_dairy_basket",
                "category": "dairy",
                "commodity": "Milk and dairy basket",
                "year": "2023",
                "attribute": "Farm value (2022 = 100)",
                "value": 91.5,
            },
            {
                "item": "fresh_grapes",
                "category": "fresh_fruit",
                "commodity": "Fresh grapes",
                "year": "2024",
                "attribute": "Farm price (cents/pounds)",
                "value": 75.0,
            },
            {
                "item": "fresh_grapes",
                "category": "fresh_fruit",
                "commodity": "Fresh grapes",
                "year": "2023",
                "attribute": "Retail price (cents/pounds)",
                "value": 190.68,
            },
        ]
        query = FarmToConsumerPriceSpreadsFetcher.transform_query({})
        data = FarmToConsumerPriceSpreadsFetcher.transform_data(query, records)
        assert [(row.commodity, row.year) for row in data] == [
            ("Fresh grapes", 2023),
            ("Fresh grapes", 2024),
            ("Milk and dairy basket", 2023),
        ]
        assert data[0].retail_price == 190.68
        assert data[1].farm_price == 75.0
        assert data[2].farm_value_index == 91.5
