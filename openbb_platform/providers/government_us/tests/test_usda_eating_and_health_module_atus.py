"""Tests for the USDA ERS Eating and Health Module (ATUS) utils and model."""

import asyncio
import csv
from io import StringIO

import pytest
from openbb_core.app.model.abstract.error import OpenBBError

from openbb_government_us.usda.models.eating_and_health_module_atus import (
    DEFAULT_TABLE,
    DEFAULT_YEAR,
    EatingAndHealthModuleAtusData,
    EatingAndHealthModuleAtusFetcher,
    EatingAndHealthModuleAtusQueryParams,
)
from openbb_government_us.usda.utils import ers_eating_and_health_module_atus
from openbb_government_us.usda.utils.ers_eating_and_health_module_atus import (
    EATING_HEALTH_TABLES,
    PRODUCT_PAGE,
    RELEASE_YEARS,
    VALUE_SUFFIXES,
    _to_float,
    parse_table,
)


def _make_csv(header, rows):
    """Serialize a header and rows into CSV text."""
    buffer = StringIO()
    writer = csv.writer(buffer)
    writer.writerow(header)
    for row in rows:
        writer.writerow(row)
    return buffer.getvalue()


TABLE_1_HEADER = [
    "Table",
    "Activity",
    "Age",
    "Average minutes per day, civilian population, all, mean",
    "Average minutes per day, civilian population, all, standard error",
    "Average percentage engaged in activity, all, mean",
]

TABLE_1_CSV = _make_csv(
    TABLE_1_HEADER,
    [
        [
            "Table 1: title",
            "Total time in primary eating and drinking",
            "Age 15 and older",
            "66.15129852",
            "0.669463576",
            "95.58497667",
        ],
        [
            "Table 1: title",
            "Total time in associated activities ",
            "Age 15 and older",
            "5.839109421",
            "0.324513393",
            "16.54177755",
        ],
        [
            "Table 1: title",
            "Total time in primary eating and drinking",
            "Age 18 and older",
            "66.51145935",
            "",
            "95.5581665",
        ],
        ["", "", "", "", "", ""],
    ],
)

TABLE_4_HEADER = [
    "Table",
    "Average/times",
    "Age",
    "Number/percent",
    "All, mean",
    "All, standard error",
    "Men, mean",
]

TABLE_4_CSV = _make_csv(
    TABLE_4_HEADER,
    [
        [
            "Table 4: title",
            "Average number",
            "Age 15 and older",
            "number",
            "2.117517471",
            "0.028634607",
            "2.240416527",
        ],
        [
            "Table 4: title",
            "One",
            "Age 15 and older",
            "percent",
            "30.15426397",
            "0.702954497",
            "28.85525823",
        ],
    ],
)

TABLE_8_HEADER = [
    "Table",
    "Category",
    "Gender",
    "Grocery shopping and meal prep, mean",
    "Grocery shopping and meal prep, standard error",
    "Primary eating  and drinking, mean",
]

TABLE_8_CSV = _make_csv(
    TABLE_8_HEADER,
    [
        [
            "Table 8: title",
            "All BMI groups",
            "All",
            "47.19285202",
            "0.78023952",
            "66.80761719",
        ],
        ["Table 8: title", "Underweight", "Men", "", "", ""],
        [
            "Table 8: title",
            "Underweight",
            "Women",
            "41.77579117",
            "7.13983751",
            "79.21186066",
        ],
    ],
)


class TestErsEatingAndHealthModuleAtusUtils:
    """Tests for the ers_eating_and_health_module_atus utils module."""

    def test_catalog_contents(self):
        """The catalog holds the eight tables with both release-year CSVs."""
        assert len(EATING_HEALTH_TABLES) == 8
        assert DEFAULT_TABLE in EATING_HEALTH_TABLES
        assert RELEASE_YEARS == ("2023", "2022")
        for config in EATING_HEALTH_TABLES.values():
            assert config["label"]
            assert set(config["media"]) == {"2023", "2022"}
            for year in RELEASE_YEARS:
                path = config["media"][year]
                assert path.startswith("/media/")
                assert path.endswith(".csv")
                assert year in path

    def test_to_float_parses_numbers(self):
        """A numeric string parses to a float, thousands separators stripped."""
        assert _to_float("66.15129852") == 66.15129852
        assert _to_float(" 1,234.5 ") == 1234.5

    def test_to_float_blank_and_non_numeric_to_none(self):
        """A blank or non-numeric cell coerces to None."""
        assert _to_float("") is None
        assert _to_float("   ") is None
        assert _to_float("--") is None

    def test_parse_table_maps_leading_dimensions(self):
        """The two leading columns map to category and subgroup, title dropped."""
        records = parse_table(TABLE_1_CSV, "eating_and_drinking_time")
        first = records[0]
        assert first["category"] == "Total time in primary eating and drinking"
        assert first["subgroup"] == "Age 15 and older"
        assert first["measure_type"] is None
        assert first["table"] == "eating_and_drinking_time"
        assert "Table 1: title" not in {record["series"] for record in records}

    def test_parse_table_classifies_value_columns(self):
        """Only headers ending in the value suffixes become series columns."""
        records = parse_table(TABLE_1_CSV, "eating_and_drinking_time")
        series = {record["series"] for record in records}
        assert series == {
            "Average minutes per day, civilian population, all, mean",
            "Average minutes per day, civilian population, all, standard error",
            "Average percentage engaged in activity, all, mean",
        }
        assert all(record["series"].endswith(VALUE_SUFFIXES) for record in records)

    def test_parse_table_coerces_values_and_blank_cell(self):
        """Value cells coerce to float and a blank cell yields None."""
        records = parse_table(TABLE_1_CSV, "eating_and_drinking_time")
        by_key = {
            (record["category"], record["subgroup"], record["series"]): record["value"]
            for record in records
        }
        assert (
            by_key[
                (
                    "Total time in primary eating and drinking",
                    "Age 15 and older",
                    "Average minutes per day, civilian population, all, mean",
                )
            ]
            == 66.15129852
        )
        assert (
            by_key[
                (
                    "Total time in primary eating and drinking",
                    "Age 18 and older",
                    "Average minutes per day, civilian population, all, standard error",
                )
            ]
            is None
        )

    def test_parse_table_skips_fully_blank_row(self):
        """A row with no non-blank cell is dropped and does not shift ordinals."""
        records = parse_table(TABLE_1_CSV, "eating_and_drinking_time")
        assert {record["row_ord"] for record in records} == {0, 1, 2}

    def test_parse_table_of_an_empty_file_yields_nothing(self):
        """A file with no header row has no columns to classify, so no records."""
        assert parse_table("", "eating_and_drinking_time") == []

    def test_parse_table_series_ordinal_follows_header(self):
        """The series ordinal follows the value-column order in the header."""
        records = parse_table(TABLE_1_CSV, "eating_and_drinking_time")
        ordinals = {record["series"]: record["series_ord"] for record in records}
        assert ordinals["Average minutes per day, civilian population, all, mean"] == 0
        assert ordinals["Average percentage engaged in activity, all, mean"] == 2

    def test_parse_table_populates_measure_type(self):
        """The fast-food table maps its third dimension to measure_type."""
        records = parse_table(TABLE_4_CSV, "fast_food_purchases")
        by_category = {record["category"]: record["measure_type"] for record in records}
        assert by_category["Average number"] == "number"
        assert by_category["One"] == "percent"

    def test_parse_table_emits_records_for_blank_row(self):
        """A row blank only in its value cells survives with None values."""
        records = parse_table(TABLE_8_CSV, "activities_by_bmi_group")
        blank = [
            record
            for record in records
            if record["category"] == "Underweight" and record["subgroup"] == "Men"
        ]
        assert len(blank) == 3
        assert all(record["value"] is None for record in blank)

    def test_afetch_table(self, monkeypatch):
        """afetch_table resolves the media path and parses the CSV."""
        calls = []

        async def fake_afetch_ers_file(media_path, product=None, ttl=None):
            calls.append((media_path, product))
            return TABLE_1_CSV.encode("utf-8-sig")

        monkeypatch.setattr(
            "openbb_government_us.usda.utils.ers_client.afetch_ers_file",
            fake_afetch_ers_file,
        )
        records = asyncio.run(
            ers_eating_and_health_module_atus.afetch_table(
                "eating_and_drinking_time", "2022"
            )
        )
        expected = EATING_HEALTH_TABLES["eating_and_drinking_time"]["media"]["2022"]
        assert calls == [(expected, PRODUCT_PAGE)]
        assert len(records) == 9


class TestEatingAndHealthModuleAtus:
    """Tests for the EatingAndHealthModuleAtus model."""

    def test_transform_query_defaults(self):
        """transform_query defaults both the table and the release year."""
        query = EatingAndHealthModuleAtusFetcher.transform_query({})
        assert isinstance(query, EatingAndHealthModuleAtusQueryParams)
        assert query.table == DEFAULT_TABLE
        assert query.year == DEFAULT_YEAR

    def test_table_blank_returns_default(self):
        """A blank or None table normalizes to the default table."""
        assert EatingAndHealthModuleAtusQueryParams(table=None).table == DEFAULT_TABLE
        assert EatingAndHealthModuleAtusQueryParams(table="").table == DEFAULT_TABLE

    def test_table_strips_whitespace(self):
        """A padded table value is stripped before validation."""
        query = EatingAndHealthModuleAtusQueryParams(table="  fast_food_purchases  ")
        assert query.table == "fast_food_purchases"

    def test_unknown_table_raises(self):
        """An unknown table raises OpenBBError listing valid choices."""
        with pytest.raises(OpenBBError, match="Invalid table: bogus"):
            EatingAndHealthModuleAtusQueryParams(table="bogus")

    def test_non_string_table_raises(self):
        """A non-string, non-empty table value raises OpenBBError."""
        with pytest.raises(OpenBBError, match="Invalid table"):
            EatingAndHealthModuleAtusQueryParams(table=123)

    def test_year_blank_returns_default(self):
        """A blank or None year normalizes to the default release year."""
        assert EatingAndHealthModuleAtusQueryParams(year=None).year == DEFAULT_YEAR
        assert EatingAndHealthModuleAtusQueryParams(year="").year == DEFAULT_YEAR

    def test_year_accepts_integer(self):
        """An integer year coerces to its string form when valid."""
        assert EatingAndHealthModuleAtusQueryParams(year=2022).year == "2022"

    def test_unknown_year_raises(self):
        """An unknown release year raises OpenBBError listing valid choices."""
        with pytest.raises(OpenBBError, match="Invalid year: 2019"):
            EatingAndHealthModuleAtusQueryParams(year="2019")

    def test_aextract_data_passes_table_and_year(self, monkeypatch):
        """aextract_data forwards the selected table and year to the util."""
        fetched = []

        async def fake_afetch_table(table, year, **kwargs):
            fetched.append((table, year))
            return [{"table": table}]

        monkeypatch.setattr(
            ers_eating_and_health_module_atus, "afetch_table", fake_afetch_table
        )
        query = EatingAndHealthModuleAtusFetcher.transform_query(
            {"table": "activities_by_bmi_group", "year": "2022"}
        )
        records = asyncio.run(
            EatingAndHealthModuleAtusFetcher.aextract_data(query, None)
        )
        assert fetched == [("activities_by_bmi_group", "2022")]
        assert records == [{"table": "activities_by_bmi_group"}]

    def test_transform_data_pivots_series_into_columns(self):
        """Each series becomes a wide column keyed by its published header."""
        records = parse_table(TABLE_1_CSV, "eating_and_drinking_time")
        query = EatingAndHealthModuleAtusFetcher.transform_query({})
        data = EatingAndHealthModuleAtusFetcher.transform_data(query, records)
        first = data[0].model_dump(by_alias=True)
        assert first["category"] == "Total time in primary eating and drinking"
        assert first["subgroup"] == "Age 15 and older"
        assert (
            first["Average minutes per day, civilian population, all, mean"]
            == 66.15129852
        )
        assert first["Average percentage engaged in activity, all, mean"] == 95.58497667

    def test_transform_data_preserves_none_response_category(self):
        """The literal 'None' response category is kept, not coerced to null."""
        records = [
            {
                "table": "grocery_shopper_and_meal_preparer",
                "row_ord": 0,
                "category": "None",
                "subgroup": "Age 15 and older",
                "measure_type": None,
                "series": "Grocery shopping, mean",
                "series_ord": 0,
                "value": 12.3,
            }
        ]
        query = EatingAndHealthModuleAtusFetcher.transform_query(
            {"table": "grocery_shopper_and_meal_preparer"}
        )
        data = EatingAndHealthModuleAtusFetcher.transform_data(query, records)
        assert data[0].category == "None"
        assert data[0].model_dump(by_alias=True)["category"] == "None"

    def test_transform_data_preserves_row_and_column_order(self):
        """Rows keep source order and columns follow the header order."""
        records = parse_table(TABLE_1_CSV, "eating_and_drinking_time")
        query = EatingAndHealthModuleAtusFetcher.transform_query({})
        data = EatingAndHealthModuleAtusFetcher.transform_data(query, records)
        assert [(row.category, row.subgroup) for row in data] == [
            ("Total time in primary eating and drinking", "Age 15 and older"),
            ("Total time in associated activities", "Age 15 and older"),
            ("Total time in primary eating and drinking", "Age 18 and older"),
        ]
        dumped = data[0].model_dump(by_alias=True)
        value_keys = [key for key in dumped if key.endswith(VALUE_SUFFIXES)]
        assert value_keys == [
            "Average minutes per day, civilian population, all, mean",
            "Average minutes per day, civilian population, all, standard error",
            "Average percentage engaged in activity, all, mean",
        ]

    def test_transform_data_keeps_suppressed_cells_as_none(self):
        """A wholly suppressed BMI row survives with null value columns."""
        records = parse_table(TABLE_8_CSV, "activities_by_bmi_group")
        query = EatingAndHealthModuleAtusFetcher.transform_query({})
        data = EatingAndHealthModuleAtusFetcher.transform_data(query, records)
        underweight_men = next(
            row
            for row in data
            if row.category == "Underweight" and row.subgroup == "Men"
        )
        dumped = underweight_men.model_dump(by_alias=True)
        assert dumped["Grocery shopping and meal prep, mean"] is None
        assert dumped["Primary eating  and drinking, mean"] is None

    def test_transform_data_populates_measure_type(self):
        """The fast-food table populates the measure_type dimension."""
        records = parse_table(TABLE_4_CSV, "fast_food_purchases")
        query = EatingAndHealthModuleAtusFetcher.transform_query(
            {"table": "fast_food_purchases"}
        )
        data = EatingAndHealthModuleAtusFetcher.transform_data(query, records)
        assert {row.measure_type for row in data} == {"number", "percent"}

    def test_transform_data_drops_temp_keys(self):
        """Internal sort keys never leak into the validated records."""
        records = parse_table(TABLE_1_CSV, "eating_and_drinking_time")
        query = EatingAndHealthModuleAtusFetcher.transform_query({})
        data = EatingAndHealthModuleAtusFetcher.transform_data(query, records)
        dumped = data[0].model_dump(by_alias=True)
        assert "_row_ord" not in dumped
        assert "table" not in dumped

    def test_query_params_widget_options(self):
        """The table and year params are single-select filters with defaults."""
        extra = EatingAndHealthModuleAtusQueryParams.__json_schema_extra__
        table = extra["table"]["x-widget_config"]
        assert table["multiSelect"] is False
        assert table["multiple"] is False
        assert table["value"] == DEFAULT_TABLE
        assert len(table["options"]) == 8
        year = extra["year"]["x-widget_config"]
        assert year["multiSelect"] is False
        assert year["multiple"] is False
        assert year["value"] == DEFAULT_YEAR
        assert [option["value"] for option in year["options"]] == ["2023", "2022"]

    def test_widget_model_config(self):
        """The whole-widget config carries the name, category, and source."""
        config = EatingAndHealthModuleAtusData.model_config["json_schema_extra"][
            "x-widget_config"
        ]
        assert config["$.name"] == "USDA ERS Eating and Health Module (ATUS)"
        assert config["$.category"] == "Economy"
        assert config["$.subCategory"] == "Agriculture"
        assert config["$.source"] == ["USDA", "ERS"]

    def test_columns_defs_bind_to_served_keys(self):
        """Every model field binds; only dynamic value columns lack a columnDef."""
        records = parse_table(TABLE_1_CSV, "eating_and_drinking_time")
        query = EatingAndHealthModuleAtusFetcher.transform_query({})
        data = EatingAndHealthModuleAtusFetcher.transform_data(query, records)
        served = set(data[0].model_dump(by_alias=True))
        fields = EatingAndHealthModuleAtusData.model_fields
        for name, field in fields.items():
            extra = (field.json_schema_extra or {}).get("x-widget_config", {})
            if extra.get("exclude"):
                continue
            assert name in served
        undefined = served - set(fields)
        assert undefined
        assert all(key.endswith(VALUE_SUFFIXES) for key in undefined)

    def test_no_constant_served_key_lacks_column_def(self):
        """Any served key without a columnDef varies across the served rows."""
        records = parse_table(TABLE_1_CSV, "eating_and_drinking_time")
        query = EatingAndHealthModuleAtusFetcher.transform_query({})
        data = EatingAndHealthModuleAtusFetcher.transform_data(query, records)
        rows = [row.model_dump(by_alias=True) for row in data]
        fields = set(EatingAndHealthModuleAtusData.model_fields)
        served = set(rows[0])
        for key in served - fields:
            values = {row.get(key) for row in rows}
            assert len(values) > 1
