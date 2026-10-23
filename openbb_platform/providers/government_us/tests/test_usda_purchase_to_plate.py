"""Tests for the USDA ERS purchase to plate utils and model."""

import asyncio
import io
import zipfile

import pytest
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic.alias_generators import to_snake

from openbb_government_us.usda.models.purchase_to_plate import (
    PurchaseToPlateData,
    PurchaseToPlateFetcher,
    PurchaseToPlateQueryParams,
)
from openbb_government_us.usda.utils import ers_purchase_to_plate as ptp
from openbb_government_us.usda.utils.ers_purchase_to_plate import (
    CATALOG,
    CYCLE_BY_YEAR,
    CYCLE_HEADERS,
    CYCLE_ORDER,
    DIGIT_TO_GROUP,
    FOOD_GROUPS,
    build_url,
    clean_token,
    extract_csv_text,
    food_group_slug,
    group_options,
    media_path,
    normalize_mod,
    parse_price,
    parse_rows,
)

SAMPLE_CSV = (
    "year,food_code,mod_code,food_description,method,method_description,"
    "nhanes,price_100gm\n"
    '2011/2012,11100000,0,"Milk, NFS",4,FNDDS recipe,NA,0.091897\n'
    '2013/2014,11100000,NA,"Milk, NFS updated",1,Links to FNDDS,Base,0.103359\n'
    '2017/2018,11100000,NA,"Milk, NFS newest",2,Links to altEC,Base,0.100484\n'
    '2011/2012,11526000,201914,"Soup W/ WHOLE MILK",3,Recipe,NA,0.05\n'
    '2011/2012,11526000,0,"Soup base",3,Recipe,NA,0.04\n'
    '2015/2016,11900000,NA,"All-NA milk",1,Links to FNDDS,Base,NA\n'
    '2017/2018,21000000,NA,"Beef, ground",1,Links to FNDDS,Top 90,0.55\n'
    '2020/2021,11700000,NA,"Future cycle",1,Links to FNDDS,Base,0.20\n'
)


def build_zip(
    csv_text: str,
    member: str = "pp_national_average_prices_csv.csv",
) -> bytes:
    """Zip one CSV member into raw archive bytes."""
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(member, csv_text.encode("utf-8-sig"))
    return buffer.getvalue()


SAMPLE_ZIP = build_zip(SAMPLE_CSV)


def make_record(**overrides) -> dict:
    """Build a long parsed row record with optional field overrides."""
    record = {
        "food_code": "11100000",
        "mod_code": "0",
        "food_group": "milk",
        "cycle": "cycle_2011_2012",
        "cycle_index": 0,
        "food_description": "Milk, NFS",
        "method_description": "Links to FNDDS",
        "nhanes": "Base",
        "price": 0.091897,
    }
    record.update(overrides)
    return record


class TestErsPurchaseToPlateUtils:
    """Tests for the ers_purchase_to_plate utils module."""

    def test_catalog_contents(self):
        """The catalog holds the single national-average-prices zip table."""
        assert list(CATALOG) == ["national_average_prices"]
        entry = CATALOG["national_average_prices"]
        assert entry["media_path"].endswith("csv-format.zip")
        assert entry["member"] == "pp_national_average_prices_csv.csv"

    def test_cycle_maps(self):
        """The cycle maps cover the four biennial cycles in order."""
        assert list(CYCLE_BY_YEAR) == [
            "2011/2012",
            "2013/2014",
            "2015/2016",
            "2017/2018",
        ]
        assert CYCLE_ORDER == (
            "cycle_2011_2012",
            "cycle_2013_2014",
            "cycle_2015_2016",
            "cycle_2017_2018",
        )
        assert CYCLE_HEADERS["cycle_2011_2012"] == "2011/2012"
        assert CYCLE_HEADERS["cycle_2017_2018"] == "2017/2018"

    def test_food_groups(self):
        """The nine food groups map their leading digit to a slug and label."""
        assert len(FOOD_GROUPS) == 9
        assert FOOD_GROUPS["milk"] == {
            "digit": "1",
            "label": "Milk and milk products",
        }
        assert DIGIT_TO_GROUP["1"] == "milk"
        assert DIGIT_TO_GROUP["9"] == "sugars"
        assert len(set(DIGIT_TO_GROUP)) == 9

    def test_group_options(self):
        """Food-group options are label/value pairs in published order."""
        options = group_options()
        assert len(options) == 9
        assert options[0] == {"label": "Milk and milk products", "value": "milk"}
        assert {"label": "Vegetables", "value": "vegetables"} in options

    def test_food_group_slug(self):
        """The leading digit resolves the food-group slug, else None."""
        assert food_group_slug("11100000") == "milk"
        assert food_group_slug("21000000") == "meat"
        assert food_group_slug("91000000") == "sugars"
        assert food_group_slug("01000000") is None

    def test_media_path_and_url(self):
        """media_path and build_url resolve the table's archive location."""
        assert media_path("national_average_prices") == (
            "/media/6557/purchase-to-plate-national-average-prices"
            "-for-nhanes-csv-format.zip"
        )
        assert build_url("national_average_prices") == (
            "https://www.ers.usda.gov/media/6557/purchase-to-plate"
            "-national-average-prices-for-nhanes-csv-format.zip"
        )

    def test_normalize_mod(self):
        """Absent modification codes normalize to '0'; real codes are kept."""
        assert normalize_mod("0") == "0"
        assert normalize_mod("NA") == "0"
        assert normalize_mod("n/a") == "0"
        assert normalize_mod("") == "0"
        assert normalize_mod(None) == "0"
        assert normalize_mod(" NA ") == "0"
        assert normalize_mod("201914") == "201914"

    def test_clean_token(self):
        """Placeholder tokens map to None; real values are stripped."""
        assert clean_token("NA") is None
        assert clean_token("n/a") is None
        assert clean_token("") is None
        assert clean_token(None) is None
        assert clean_token("Base") == "Base"
        assert clean_token(" Top 90 ") == "Top 90"

    def test_parse_price(self):
        """Prices parse to floats at full precision; 'NA' cells become None."""
        assert parse_price("0.091897") == 0.091897
        assert parse_price("0.302781") == 0.302781
        assert parse_price("NA") is None
        assert parse_price("") is None
        assert parse_price(None) is None

    def test_extract_csv_text(self):
        """The CSV member is extracted and decoded from the zip archive."""
        text = extract_csv_text(SAMPLE_ZIP, "pp_national_average_prices_csv.csv")
        assert text.splitlines()[0].startswith("year,food_code,mod_code")
        assert "Milk, NFS" in text

    def test_parse_rows_normalizes_and_keys(self):
        """Rows normalize the mod code, tag the food group, and coerce prices."""
        records = parse_rows(SAMPLE_CSV)
        base = next(
            r
            for r in records
            if r["food_code"] == "11100000" and r["cycle"] == "cycle_2011_2012"
        )
        assert base["mod_code"] == "0"
        assert base["food_group"] == "milk"
        assert base["cycle_index"] == 0
        assert base["nhanes"] is None
        assert base["price"] == 0.091897
        modified = next(r for r in records if r["mod_code"] == "201914")
        assert modified["food_code"] == "11526000"
        assert modified["cycle_index"] == 0
        na_price = next(r for r in records if r["food_code"] == "11900000")
        assert na_price["price"] is None
        assert na_price["cycle"] == "cycle_2015_2016"
        assert na_price["cycle_index"] == 2

    def test_parse_rows_skips_unknown_cycle(self):
        """A row of an unrecognized survey cycle is skipped."""
        records = parse_rows(SAMPLE_CSV)
        assert all(r["food_code"] != "11700000" for r in records)
        assert {r["cycle"] for r in records} <= set(CYCLE_ORDER)

    def test_afetch_table(self, monkeypatch):
        """afetch_table fetches the zip through the cache and parses it."""
        calls = []

        async def fake_afetch_ers_file(path, product=None, ttl=None):
            calls.append((path, product))
            return SAMPLE_ZIP

        monkeypatch.setattr(
            "openbb_government_us.usda.utils.ers_client.afetch_ers_file",
            fake_afetch_ers_file,
        )
        records = asyncio.run(ptp.afetch_table())
        assert calls == [
            (
                CATALOG["national_average_prices"]["media_path"],
                ptp.PRODUCT_PAGE,
            )
        ]
        assert any(r["food_code"] == "11100000" for r in records)


class TestPurchaseToPlate:
    """Tests for the PurchaseToPlate model."""

    def test_transform_query(self):
        """transform_query builds the query params model."""
        query = PurchaseToPlateFetcher.transform_query({"food_group": "meat"})
        assert isinstance(query, PurchaseToPlateQueryParams)
        assert query.food_group == "meat"

    def test_food_group_defaults_and_normalizes(self):
        """Food group defaults to milk, casefolds, and takes the first of a list."""
        assert PurchaseToPlateQueryParams().food_group == "milk"
        assert PurchaseToPlateQueryParams(food_group="").food_group == "milk"
        assert PurchaseToPlateQueryParams(food_group="MILK").food_group == "milk"
        assert PurchaseToPlateQueryParams(food_group=["grains"]).food_group == "grains"

    def test_unknown_food_group_raises(self):
        """An unknown food group raises OpenBBError listing valid choices."""
        with pytest.raises(OpenBBError, match="Invalid food_group: bogus.*milk"):
            PurchaseToPlateQueryParams(food_group="bogus")

    def test_aextract_data_returns_long_records(self, monkeypatch):
        """aextract_data returns the parsed long records from the util."""

        async def fake_afetch_table(table="national_average_prices"):
            return parse_rows(SAMPLE_CSV)

        monkeypatch.setattr(ptp, "afetch_table", fake_afetch_table)
        query = PurchaseToPlateFetcher.transform_query({})
        records = asyncio.run(PurchaseToPlateFetcher.aextract_data(query, None))
        assert any(r["food_code"] == "11100000" for r in records)

    def test_transform_data_pivots_cycles_into_columns(self):
        """Each food item is one row with a price column per survey cycle."""
        query = PurchaseToPlateFetcher.transform_query({})
        data = PurchaseToPlateFetcher.transform_data(query, parse_rows(SAMPLE_CSV))
        milk = next(row for row in data if row.food_code == "11100000")
        dumped = milk.model_dump(by_alias=True)
        assert dumped["cycle_2011_2012"] == 0.091897
        assert dumped["cycle_2013_2014"] == 0.103359
        assert dumped["cycle_2015_2016"] is None
        assert dumped["cycle_2017_2018"] == 0.100484

    def test_transform_data_carries_most_recent_cycle_dims(self):
        """Descriptive dims come from the most recent cycle the item appears in."""
        query = PurchaseToPlateFetcher.transform_query({})
        data = PurchaseToPlateFetcher.transform_data(query, parse_rows(SAMPLE_CSV))
        milk = next(row for row in data if row.food_code == "11100000")
        assert milk.food_description == "Milk, NFS newest"
        assert milk.method_description == "Links to altEC"
        assert milk.nhanes == "Base"

    def test_transform_data_nhanes_na_becomes_none(self):
        """A 2011/2012-only item's 'NA' NHANES flag coerces to None."""
        query = PurchaseToPlateFetcher.transform_query({})
        data = PurchaseToPlateFetcher.transform_data(query, parse_rows(SAMPLE_CSV))
        base = next(
            row for row in data if row.food_code == "11526000" and row.mod_code == "0"
        )
        assert base.nhanes is None
        assert base.cycle_2011_2012 == 0.04

    def test_transform_data_drops_all_none_rows(self):
        """A food item with no priced cycle is dropped."""
        query = PurchaseToPlateFetcher.transform_query({})
        data = PurchaseToPlateFetcher.transform_data(query, parse_rows(SAMPLE_CSV))
        assert all(row.food_code != "11900000" for row in data)

    def test_transform_data_filters_food_group(self):
        """Only the selected food group's items survive the filter."""
        query = PurchaseToPlateFetcher.transform_query({})
        data = PurchaseToPlateFetcher.transform_data(query, parse_rows(SAMPLE_CSV))
        assert all(row.food_code[0] == "1" for row in data)
        assert all(row.food_code != "21000000" for row in data)
        meat_query = PurchaseToPlateFetcher.transform_query({"food_group": "meat"})
        meat = PurchaseToPlateFetcher.transform_data(meat_query, parse_rows(SAMPLE_CSV))
        assert [row.food_code for row in meat] == ["21000000"]
        assert meat[0].cycle_2017_2018 == 0.55

    def test_transform_data_sort_order(self):
        """Rows sort by food code, then modification code with base first."""
        query = PurchaseToPlateFetcher.transform_query({})
        data = PurchaseToPlateFetcher.transform_data(query, parse_rows(SAMPLE_CSV))
        assert [(row.food_code, row.mod_code) for row in data] == [
            ("11100000", "0"),
            ("11526000", "0"),
            ("11526000", "201914"),
        ]

    def test_transform_data_cycle_columns_chronological(self):
        """The cycle price columns serialize oldest-first."""
        query = PurchaseToPlateFetcher.transform_query({})
        data = PurchaseToPlateFetcher.transform_data(query, parse_rows(SAMPLE_CSV))
        dumped = data[0].model_dump(by_alias=True)
        cycle_keys = [key for key in dumped if key.startswith("cycle_")]
        assert cycle_keys == [
            "cycle_2011_2012",
            "cycle_2013_2014",
            "cycle_2015_2016",
            "cycle_2017_2018",
        ]

    def test_transform_data_empty_raises(self):
        """No records surviving the filters raises EmptyDataError."""
        query = PurchaseToPlateFetcher.transform_query({"food_group": "eggs"})
        with pytest.raises(EmptyDataError, match="No records match"):
            PurchaseToPlateFetcher.transform_data(query, parse_rows(SAMPLE_CSV))

    def test_columns_defs_bind_to_served_keys(self):
        """Every declared column definition binds to a served row key."""
        query = PurchaseToPlateFetcher.transform_query({})
        data = PurchaseToPlateFetcher.transform_data(query, parse_rows(SAMPLE_CSV))
        served = set(data[0].model_dump(by_alias=True))
        schema = PurchaseToPlateData.model_json_schema(
            by_alias=True, mode="serialization"
        )
        column_fields = {to_snake(key) for key in schema["properties"]}
        assert column_fields, "no column definitions generated"
        assert served == column_fields

    def test_widget_config_metadata(self):
        """The whole-widget config carries the ERS category and source."""
        config = PurchaseToPlateData.model_config["json_schema_extra"][
            "x-widget_config"
        ]
        assert config["$.category"] == "Economy"
        assert config["$.subCategory"] == "Agriculture"
        assert config["$.source"] == ["USDA", "ERS"]
