"""Tests for the USDA ERS Food-at-Home Monthly Area Prices utils and model."""

import asyncio
import csv
import io
import zipfile
from datetime import date
from io import StringIO

import pytest
from openbb_core.app.model.abstract.error import OpenBBError

from openbb_government_us.usda.models.food_at_home_monthly_area_prices import (
    FoodAtHomeMonthlyAreaPricesData,
    FoodAtHomeMonthlyAreaPricesFetcher,
    FoodAtHomeMonthlyAreaPricesQueryParams,
)
from openbb_government_us.usda.utils import ers_food_at_home_monthly_area_prices as fmap
from openbb_government_us.usda.utils.ers_food_at_home_monthly_area_prices import (
    AREA_FIELDS,
    AREAS,
    DEFAULT_GROUP,
    DEFAULT_ITEM,
    DEFAULT_MEASURE,
    DEFAULT_TABLE,
    EFPG,
    FMAP_TABLES,
    GROUPS,
    MEASURES,
    PRODUCT_PAGE,
    build_url,
    extract_csv_text,
    group_options,
    item_options,
    measure_options,
    media_path,
    parse_series,
    resolve_measure,
    table_measures,
)

HEADER = ["Year", "Month", "EFPG_code", "Metroregion_code", "Attribute", "Value"]


def _make_csv(rows):
    """Serialize the FMAP header and rows to CSV text."""
    buffer = StringIO()
    writer = csv.writer(buffer)
    writer.writerow(HEADER)
    for row in rows:
        writer.writerow(row)
    return buffer.getvalue()


MAIN_CSV = _make_csv(
    [
        [2012, 1, 40000, 0, "Unit_value_mean_wtd", "0.10"],
        [2012, 1, 40000, 1, "Unit_value_mean_wtd", "0.11"],
        [2012, 1, 40000, 99999, "Unit_value_mean_wtd", "9.99"],
        [2012, 1, 40000, 0, "Price_index_GEKS", "1.00"],
        [2012, 2, 40000, 0, "Unit_value_mean_wtd", "0.20"],
        [2012, 2, 40000, 1, "Unit_value_mean_wtd", "0.21"],
        [2013, 1, 40000, 0, "Unit_value_mean_wtd", "0.305050505"],
        [2012, 1, 40030, 0, "Unit_value_mean_wtd", "5.55"],
    ]
)

SUPP_CSV = _make_csv(
    [
        [2016, 1, 40000, 0, "Price_index_GEKS", "1.01"],
        [2016, 1, 40000, 1, "Price_index_GEKS", "1.02"],
    ]
)


def _zip_bytes(member, text):
    """Build zip bytes carrying one CSV member."""
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        archive.writestr(member, text)
    return buffer.getvalue()


class TestErsFoodAtHomeMonthlyAreaPricesUtils:
    """Tests for the ers_food_at_home_monthly_area_prices utility module."""

    def test_catalog_shapes(self):
        """The catalog constants have the published cardinalities."""
        assert set(FMAP_TABLES) == {
            "monthly_area_prices",
            "supplemental_price_indexes",
        }
        assert len(AREAS) == 15
        assert len(AREA_FIELDS) == 15
        assert len(EFPG) == 90
        assert len(GROUPS) == 7
        assert len(MEASURES) == 14
        assert DEFAULT_TABLE in FMAP_TABLES
        assert DEFAULT_ITEM in EFPG
        assert DEFAULT_GROUP in GROUPS
        assert DEFAULT_MEASURE in MEASURES

    def test_area_fields_digit_free(self):
        """Area field names carry no digits, so aliases never split."""
        for field in AREA_FIELDS:
            assert not any(character.isdigit() for character in field)

    def test_every_efpg_group_is_known(self):
        """Every EFPG entry belongs to a declared Tier-1 group."""
        for meta in EFPG.values():
            assert meta["group"] in GROUPS
        assert EFPG[DEFAULT_ITEM]["name"] == "Whole milk"

    def test_group_item_counts(self):
        """The item counts per group match the published totals."""
        counts = {group: 0 for group in GROUPS}
        for meta in EFPG.values():
            counts[meta["group"]] += 1
        assert counts == {
            "Grains": 8,
            "Vegetables": 23,
            "Fruit": 8,
            "Dairy": 8,
            "Meat and Protein Foods": 14,
            "Prepared meals, sides, and salads": 4,
            "Other foods": 25,
        }

    def test_media_path_and_url(self):
        """media_path and build_url resolve a table's archive location."""
        path = media_path("monthly_area_prices")
        assert path.startswith("/media/5400/")
        assert build_url("monthly_area_prices") == fmap.BASE_URL + path

    def test_table_measures_counts(self):
        """The main table publishes 9 measures, the supplemental 11."""
        assert len(table_measures("monthly_area_prices")) == 9
        assert len(table_measures("supplemental_price_indexes")) == 11

    def test_measure_options_labels(self):
        """measure_options returns labeled option dicts for a table."""
        options = measure_options("monthly_area_prices")
        assert len(options) == 9
        assert {"label": "GEKS price index", "value": "price_index_geks"} in options

    def test_group_options(self):
        """group_options returns one labeled option per Tier-1 group."""
        options = group_options()
        assert len(options) == 7
        assert {"label": "Dairy", "value": "Dairy"} in options

    def test_item_options_scoped_to_group(self):
        """item_options lists only a group's items, labeled by name."""
        options = item_options("Dairy")
        assert options[0] == {"label": "Whole milk", "value": "40000"}
        assert {opt["value"] for opt in options} == {
            code for code, meta in EFPG.items() if meta["group"] == "Dairy"
        }

    def test_resolve_measure_keeps_valid(self):
        """A measure the table publishes is returned unchanged."""
        assert (
            resolve_measure("monthly_area_prices", "unit_value_mean_wtd")
            == "unit_value_mean_wtd"
        )

    def test_resolve_measure_falls_back_when_unavailable(self):
        """A measure absent from the table falls back to the table default."""
        assert (
            resolve_measure("supplemental_price_indexes", "unit_value_mean_wtd")
            == "price_index_geks"
        )

    def test_resolve_measure_falls_back_when_unknown(self):
        """An unknown measure falls back to the table default."""
        assert resolve_measure("monthly_area_prices", "bogus") == "unit_value_mean_wtd"

    def test_parse_series_filters_item_and_measure(self):
        """parse_series keeps only the requested item and measure rows."""
        records = parse_series(MAIN_CSV, "40000", "Unit_value_mean_wtd")
        assert len(records) == 6
        assert all(record["value"] != 5.55 for record in records)
        assert all(record["value"] != 1.00 for record in records)
        first = records[0]
        assert first == {
            "year": 2012,
            "month": 1,
            "area_code": "0",
            "value": 0.10,
        }

    def test_parse_series_preserves_precision(self):
        """parse_series keeps the full source float precision."""
        records = parse_series(MAIN_CSV, "40000", "Unit_value_mean_wtd")
        year_2013 = next(record for record in records if record["year"] == 2013)
        assert year_2013["value"] == 0.305050505

    def test_extract_csv_text(self):
        """extract_csv_text decodes a named CSV member from zip bytes."""
        payload = _zip_bytes("FMAP-Data.csv", MAIN_CSV)
        text = extract_csv_text(payload, "FMAP-Data.csv")
        assert text.splitlines()[0] == ",".join(HEADER)

    def test_afetch_series(self, monkeypatch):
        """afetch_series fetches through the ERS cache and parses the member."""
        calls = []

        async def fake_afetch_ers_file(media_path, product=None, ttl=None):
            calls.append((media_path, product))
            return _zip_bytes("FMAP-Data.csv", MAIN_CSV)

        monkeypatch.setattr(
            "openbb_government_us.usda.utils.ers_client.afetch_ers_file",
            fake_afetch_ers_file,
        )
        records = asyncio.run(
            fmap.afetch_series("monthly_area_prices", "40000", "Unit_value_mean_wtd")
        )
        assert calls == [
            (FMAP_TABLES["monthly_area_prices"]["media_path"], PRODUCT_PAGE)
        ]
        assert len(records) == 6

    def test_afetch_series_supplemental_member(self, monkeypatch):
        """afetch_series reads the supplemental table's own zip member."""
        calls = []

        async def fake_afetch_ers_file(media_path, product=None, ttl=None):
            calls.append(media_path)
            return _zip_bytes("FMAP-SupIndex-Data.csv", SUPP_CSV)

        monkeypatch.setattr(
            "openbb_government_us.usda.utils.ers_client.afetch_ers_file",
            fake_afetch_ers_file,
        )
        records = asyncio.run(
            fmap.afetch_series(
                "supplemental_price_indexes", "40000", "Price_index_GEKS"
            )
        )
        assert calls == [FMAP_TABLES["supplemental_price_indexes"]["media_path"]]
        assert len(records) == 2


class TestFoodAtHomeMonthlyAreaPricesQueryParams:
    """Tests for the query-param validation and widget scoping."""

    def test_transform_query_defaults(self):
        """transform_query applies every default and keeps year filters."""
        query = FoodAtHomeMonthlyAreaPricesFetcher.transform_query({"start_year": 2015})
        assert isinstance(query, FoodAtHomeMonthlyAreaPricesQueryParams)
        assert query.table == DEFAULT_TABLE
        assert query.group == DEFAULT_GROUP
        assert query.item == DEFAULT_ITEM
        assert query.measure == DEFAULT_MEASURE
        assert query.start_year == 2015

    def test_table_blank_and_strip(self):
        """A blank table defaults and a padded table is stripped."""
        assert FoodAtHomeMonthlyAreaPricesQueryParams(table=None).table == DEFAULT_TABLE
        assert (
            FoodAtHomeMonthlyAreaPricesQueryParams(
                table="  supplemental_price_indexes  "
            ).table
            == "supplemental_price_indexes"
        )

    def test_unknown_table_raises(self):
        """An unknown table raises OpenBBError."""
        with pytest.raises(OpenBBError, match="Invalid table: bogus"):
            FoodAtHomeMonthlyAreaPricesQueryParams(table="bogus")

    def test_group_blank_strip_and_invalid(self):
        """The group defaults on blank, strips padding, and rejects unknowns."""
        assert FoodAtHomeMonthlyAreaPricesQueryParams(group="").group == DEFAULT_GROUP
        assert (
            FoodAtHomeMonthlyAreaPricesQueryParams(group="  Fruit  ").group == "Fruit"
        )
        with pytest.raises(OpenBBError, match="Invalid group: bogus"):
            FoodAtHomeMonthlyAreaPricesQueryParams(group="bogus")

    def test_item_blank_list_and_invalid(self):
        """The item defaults on blank, unwraps a list, and rejects unknowns."""
        assert FoodAtHomeMonthlyAreaPricesQueryParams(item=None).item == DEFAULT_ITEM
        assert FoodAtHomeMonthlyAreaPricesQueryParams(item=["30000"]).item == "30000"
        assert FoodAtHomeMonthlyAreaPricesQueryParams(item=" 46000 ").item == "46000"
        with pytest.raises(OpenBBError, match="Invalid item: 11111"):
            FoodAtHomeMonthlyAreaPricesQueryParams(item="11111")

    def test_measure_blank_strip_and_invalid(self):
        """The measure defaults on blank, strips padding, and rejects unknowns."""
        assert (
            FoodAtHomeMonthlyAreaPricesQueryParams(measure="").measure
            == DEFAULT_MEASURE
        )
        assert (
            FoodAtHomeMonthlyAreaPricesQueryParams(
                measure="  price_index_geks "
            ).measure
            == "price_index_geks"
        )
        with pytest.raises(OpenBBError, match="Invalid measure"):
            FoodAtHomeMonthlyAreaPricesQueryParams(measure=123)

    def test_item_param_is_scoped_endpoint(self):
        """The item param is a single-select endpoint keyed on the group."""
        config = FoodAtHomeMonthlyAreaPricesQueryParams.__json_schema_extra__["item"][
            "x-widget_config"
        ]
        assert config["multiSelect"] is False
        assert config["multiple"] is False
        assert config["type"] == "endpoint"
        assert config["value"] == DEFAULT_ITEM
        assert config["optionsParams"] == {"group": "$group"}
        assert config["optionsEndpoint"].endswith("/usda/fmap_food_items")

    def test_measure_param_is_scoped_endpoint(self):
        """The measure param is a single-select endpoint keyed on the table."""
        config = FoodAtHomeMonthlyAreaPricesQueryParams.__json_schema_extra__[
            "measure"
        ]["x-widget_config"]
        assert config["multiSelect"] is False
        assert config["optionsParams"] == {"table": "$table"}
        assert config["optionsEndpoint"].endswith("/usda/fmap_measures")

    def test_table_and_group_static_options(self):
        """The table and group params expose static single-select options."""
        table = FoodAtHomeMonthlyAreaPricesQueryParams.__json_schema_extra__["table"][
            "x-widget_config"
        ]
        group = FoodAtHomeMonthlyAreaPricesQueryParams.__json_schema_extra__["group"][
            "x-widget_config"
        ]
        assert len(table["options"]) == 2
        assert len(group["options"]) == 7
        assert table["multiSelect"] is False
        assert group["multiSelect"] is False


class TestFoodAtHomeMonthlyAreaPricesModel:
    """Tests for the fetcher extraction and pivot."""

    def test_aextract_data_resolves_measure_source(self, monkeypatch):
        """aextract_data passes the resolved measure's source attribute."""
        captured = {}

        async def fake_afetch_series(table, item, source):
            captured["args"] = (table, item, source)
            return []

        monkeypatch.setattr(fmap, "afetch_series", fake_afetch_series)
        query = FoodAtHomeMonthlyAreaPricesFetcher.transform_query(
            {"table": "supplemental_price_indexes", "item": "40000"}
        )
        asyncio.run(FoodAtHomeMonthlyAreaPricesFetcher.aextract_data(query, None))
        assert captured["args"] == (
            "supplemental_price_indexes",
            "40000",
            "Price_index_GEKS",
        )

    def _records(self):
        """Return the parsed synthetic long records for the main table."""
        return parse_series(MAIN_CSV, "40000", "Unit_value_mean_wtd")

    def test_transform_data_pivots_areas_into_columns(self):
        """Each area becomes a column, one row per month, dated first-of-month."""
        query = FoodAtHomeMonthlyAreaPricesFetcher.transform_query({})
        data = FoodAtHomeMonthlyAreaPricesFetcher.transform_data(query, self._records())
        first = data[0].model_dump(by_alias=True)
        assert first["date"] == date(2012, 1, 1)
        assert first["national"] == 0.10
        assert first["northeast"] == 0.11

    def test_transform_data_skips_unknown_area(self):
        """A metroregion code outside the 15-area map never becomes a value."""
        query = FoodAtHomeMonthlyAreaPricesFetcher.transform_query({})
        data = FoodAtHomeMonthlyAreaPricesFetcher.transform_data(query, self._records())
        first = data[0].model_dump(by_alias=True)
        assert 9.99 not in first.values()
        assert first["midwest"] is None

    def test_transform_data_orders_chronologically(self):
        """Rows sort ascending by year then month."""
        query = FoodAtHomeMonthlyAreaPricesFetcher.transform_query({})
        data = FoodAtHomeMonthlyAreaPricesFetcher.transform_data(query, self._records())
        assert [row.date for row in data] == [
            date(2012, 1, 1),
            date(2012, 2, 1),
            date(2013, 1, 1),
        ]

    def test_transform_data_filters_years(self):
        """start_year and end_year filter rows on the integer year."""
        records = self._records()
        start = FoodAtHomeMonthlyAreaPricesFetcher.transform_data(
            FoodAtHomeMonthlyAreaPricesFetcher.transform_query({"start_year": 2013}),
            records,
        )
        assert {row.date.year for row in start} == {2013}
        end = FoodAtHomeMonthlyAreaPricesFetcher.transform_data(
            FoodAtHomeMonthlyAreaPricesFetcher.transform_query({"end_year": 2012}),
            records,
        )
        assert {row.date.year for row in end} == {2012}

    def test_transform_data_preserves_precision(self):
        """Area values keep full source precision, no rounding."""
        query = FoodAtHomeMonthlyAreaPricesFetcher.transform_query({})
        data = FoodAtHomeMonthlyAreaPricesFetcher.transform_data(query, self._records())
        year_2013 = next(row for row in data if row.date.year == 2013)
        assert year_2013.national == 0.305050505

    def test_fetch_data_end_to_end(self, monkeypatch):
        """fetch_data extracts and pivots into wide rows with 15 area columns."""

        async def fake_afetch_series(table, item, source):
            return parse_series(MAIN_CSV, item, source)

        monkeypatch.setattr(fmap, "afetch_series", fake_afetch_series)
        result = asyncio.run(FoodAtHomeMonthlyAreaPricesFetcher.fetch_data({}, {}))
        assert len(result) == 3
        served = result[0].model_dump(by_alias=True)
        assert set(served) == {"date"} | set(AREA_FIELDS)

    def test_widget_model_config(self):
        """The whole-widget config carries the name, category, and source."""
        config = FoodAtHomeMonthlyAreaPricesData.model_config["json_schema_extra"][
            "x-widget_config"
        ]
        assert config["$.name"] == "USDA ERS Food-at-Home Monthly Area Prices"
        assert config["$.category"] == "Economy"
        assert config["$.subCategory"] == "Agriculture"
        assert config["$.source"] == ["USDA", "ERS"]

    def test_date_column_pinned_left(self):
        """The date column is pinned left as a date cell."""
        config = FoodAtHomeMonthlyAreaPricesData.model_fields["date"].json_schema_extra[
            "x-widget_config"
        ]
        assert config["pinned"] == "left"
        assert config["cellDataType"] == "date"

    def test_columns_defs_bind_to_served_keys(self):
        """Every field binds to a served key and no served key is a constant."""
        query = FoodAtHomeMonthlyAreaPricesFetcher.transform_query({})
        data = FoodAtHomeMonthlyAreaPricesFetcher.transform_data(query, self._records())
        served = set(data[0].model_dump(by_alias=True))
        fields = FoodAtHomeMonthlyAreaPricesData.model_fields
        for name, field in fields.items():
            extra = (field.json_schema_extra or {}).get("x-widget_config", {})
            if extra.get("exclude"):
                continue
            assert name in served
        assert served == set(fields)
        for area_field in AREA_FIELDS:
            config = fields[area_field].json_schema_extra["x-widget_config"]
            assert config["cellDataType"] == "number"
