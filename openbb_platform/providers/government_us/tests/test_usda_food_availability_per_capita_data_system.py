"""Tests for the USDA ERS Food Availability (Per Capita) Data System utils and model."""

import asyncio

import pytest
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic.alias_generators import to_snake

from openbb_government_us.usda.models.food_availability_per_capita_data_system import (
    DATA_SYSTEM_OPTIONS,
    SYSTEM_DEFAULT_GROUP,
    FoodAvailabilityPerCapitaDataSystemData,
    FoodAvailabilityPerCapitaDataSystemFetcher,
    FoodAvailabilityPerCapitaDataSystemQueryParams,
)
from openbb_government_us.usda.utils import (
    ers_food_availability_per_capita_data_system as ers,
)
from openbb_government_us.usda.utils.ers_food_availability_per_capita_data_system import (
    CATALOG,
    DATA_SYSTEMS,
    PRODUCT_PAGE,
    afetch_blocks,
    afetch_records,
    clean_block_label,
    distinct_blocks,
    foodgroup_columns,
    group_options,
    is_year_token,
    parse_long,
    parse_records,
    parse_value,
    parse_wide_columnar,
    parse_wide_fixed,
)

LONG_CSV = (
    "Commodity,Year,Attribute,Value,Notes\n"
    'Eggs: Per capita availability,1909,"U.S. population, July 1-Millions",90.49,Resident only.\n'
    "Eggs: Per capita availability,1909,Shell-Total-Millions,NA,\n"
    "Eggs: Per capita availability,1909,Empty-Col-Millions,NA,\n"
    'Eggs: Per capita availability,2020,"U.S. population, July 1-Millions",330.0,\n'
    "Eggs: Per capita availability,2020,Shell-Total-Millions,66000.0,\n"
    "Eggs: Per capita availability,2020,Empty-Col-Millions,--,\n"
    "Eggs: Per capita availability,20201,Shell-Total-Millions,1.0,\n"
    "Eggs and egg products: Supply and use,1909,Supply-Total-Millions,100.0,\n"
    "Eggs and egg products: Supply and use,2020,Supply-Total-Millions,200.0,\n"
)

COLUMNAR_CSV = (
    "Year,Variable,Unit,Commodity,Population,Production,Imports,Beginning stocks\n"
    "1970,Coffee Tea Cocoa,Pounds,Coffee,205.0,6,2667,\n"
    "1971,Coffee Tea Cocoa,Pounds,Coffee,207.0,4,2942,\n"
    "1970,Coffee Tea Cocoa,Pounds,Tea,205.0,,137,\n"
    "1971,Coffee Tea Cocoa,Pounds,Tea,207.0,,175,\n"
)

COLUMNAR_CONFIG = {
    "format": "wide_columnar",
    "year_col": 0,
    "block_col": 3,
    "id_cols": (0, 1, 2, 3),
    "header_row": 0,
    "data_start": 1,
}

FIXED_CSV = (
    "Some Title,,\n"
    "Year,Col A,Col B\n"
    ",,\n"
    ",,\n"
    ",--- Millions ---,\n"
    '1970,"2,054",1.5\n'
    '1971,"2,100",1.6\n'
    ",,\n"
    "Source: foo,,\n"
)

FIXED_CONFIG = {
    "format": "wide_fixed",
    "block": "My Block",
    "year_col": 0,
    "data_start": 5,
    "columns": ((1, "Col A - Number"), (2, "Col B - Number")),
}


class FakeSheet:
    """A minimal xlrd sheet stand-in backed by a row grid."""

    def __init__(self, grid: list[list]) -> None:
        self._grid = grid
        self.nrows = len(grid)
        self.ncols = max(len(row) for row in grid)

    def cell_value(self, row: int, col: int):
        """Return the cell value, or an empty string past the row's end."""
        cells = self._grid[row]
        return cells[col] if col < len(cells) else ""


class FakeBook:
    """A minimal xlrd workbook stand-in mapping sheet names to FakeSheet."""

    def __init__(self, sheets: dict) -> None:
        self._sheets = sheets

    def sheet_by_name(self, name: str) -> FakeSheet:
        """Return the fake sheet registered under name."""
        return self._sheets[name]


def _totals_grid() -> list[list]:
    """Build a fake nutrient Totals sheet with two year rows."""
    blank = [[""] * 30 for _ in range(6)]
    row_1909 = [1909.0] + [float(index * 10) for index in range(1, 30)]
    row_2010 = [2010.0] + [float(index * 11) for index in range(1, 30)]
    footer = ["Source: foo"]
    return [*blank, row_1909, row_2010, footer]


def _foodgroups_grid() -> list[list]:
    """Build a fake nutrient Foodgroups sheet with two food-group blocks."""
    header = [[""] * 57 for _ in range(4)]
    meat_1970 = [1970.0] + [float(index) for index in range(1, 57)]
    meat_2010 = [2010.0] + [float(index * 2) for index in range(1, 57)]
    dairy_1970 = [1970.0] + [float(index * 3) for index in range(1, 57)]
    dairy_2010 = [2010.0] + [float(index * 4) for index in range(1, 57)]
    return [
        *header,
        ["Meat, poultry, and fish"],
        meat_1970,
        meat_2010,
        ["Dairy products2"],
        dairy_1970,
        dairy_2010,
        ["1Percentages are based on aggregate nutrient data."],
    ]


def _fake_workbook(**_kwargs) -> FakeBook:
    """Return a fake nutrient workbook for the Totals and Foodgroups sheets."""
    return FakeBook(
        {
            "Totals": FakeSheet(_totals_grid()),
            "Foodgroups": FakeSheet(_foodgroups_grid()),
        }
    )


class TestErsFoodAvailabilityUtils:
    """Tests for the ers_food_availability_per_capita_data_system utils module."""

    def test_catalog_shape_and_media_paths(self):
        """The catalog covers all three systems with well-formed media paths."""
        assert set(CATALOG) == set(DATA_SYSTEMS)
        assert len(CATALOG["food_availability"]) == 27
        assert len(CATALOG["loss_adjusted"]) == 9
        assert len(CATALOG["nutrient"]) == 2
        for system in DATA_SYSTEMS:
            for config in CATALOG[system].values():
                assert config["media"].startswith("/media/")
                assert config["format"] in (
                    "long",
                    "wide_columnar",
                    "wide_fixed",
                    "nutrient_totals",
                    "nutrient_foodgroups",
                )
                assert config.get("label")

    def test_grains_repeats_across_systems(self):
        """The grains slug points at different files in each system."""
        fa = CATALOG["food_availability"]["grains"]["media"]
        la = CATALOG["loss_adjusted"]["grains"]["media"]
        assert fa == "/media/5353/grains.csv"
        assert la == "/media/5391/grains.csv"
        assert fa != la

    def test_group_options_labels_and_values(self):
        """group_options lists a label/value per file in catalog order."""
        options = group_options("food_availability")
        assert options[0] == {
            "label": "Coffee, tea, cocoa, and spices",
            "value": "coffee_tea_cocoa",
        }
        assert {opt["value"] for opt in options} == set(CATALOG["food_availability"])

    def test_parse_value_keeps_precision_and_nulls(self):
        """parse_value strips separators, keeps floats, and nulls placeholders."""
        assert parse_value("7.734131637") == 7.734131637
        assert parse_value("2,054") == 2054.0
        assert parse_value(90.49) == 90.49
        assert parse_value("NA") is None
        assert parse_value("--") is None
        assert parse_value("") is None
        assert parse_value("*") is None

    def test_is_year_token(self):
        """Only four-digit tokens are treated as calendar years."""
        assert is_year_token("1970") is True
        assert is_year_token(" 2020 ") is True
        assert is_year_token("20201") is False
        assert is_year_token("197") is False
        assert is_year_token("abcd") is False

    def test_clean_block_label(self):
        """Footnote digits and surrounding whitespace are stripped."""
        assert clean_block_label("Dairy products2") == "Dairy products"
        assert clean_block_label("    Citrus") == "Citrus"
        assert clean_block_label("Meat, poultry, and fish") == "Meat, poultry, and fish"

    def test_parse_long_records_and_year_guard(self):
        """parse_long yields tidy records and drops non-four-digit years."""
        records = parse_long(LONG_CSV)
        assert all(len(str(record["year"])) == 4 for record in records)
        assert not any(record["year"] == 20201 for record in records)
        first = records[0]
        assert first == {
            "block": "Eggs: Per capita availability",
            "year": 1909,
            "attribute": "U.S. population, July 1-Millions",
            "value": 90.49,
        }
        na_row = next(
            r
            for r in records
            if r["attribute"] == "Shell-Total-Millions" and r["year"] == 1909
        )
        assert na_row["value"] is None

    def test_parse_wide_columnar_blocks_and_measures(self):
        """parse_wide_columnar keys blocks off the commodity column."""
        records = parse_wide_columnar(COLUMNAR_CSV, COLUMNAR_CONFIG)
        assert distinct_blocks(records) == ["Coffee", "Tea"]
        coffee_1970 = {
            r["attribute"]: r["value"]
            for r in records
            if r["block"] == "Coffee" and r["year"] == 1970
        }
        assert coffee_1970["Population"] == 205.0
        assert coffee_1970["Production"] == 6.0
        assert coffee_1970["Beginning stocks"] is None
        tea_1970 = {
            r["attribute"]: r["value"]
            for r in records
            if r["block"] == "Tea" and r["year"] == 1970
        }
        assert tea_1970["Production"] is None

    def test_parse_wide_fixed_columns_and_commas(self):
        """parse_wide_fixed maps hardcoded columns and strips thousands commas."""
        records = parse_wide_fixed(FIXED_CSV, FIXED_CONFIG)
        assert distinct_blocks(records) == ["My Block"]
        by_key = {(r["year"], r["attribute"]): r["value"] for r in records}
        assert by_key[(1970, "Col A - Number")] == 2054.0
        assert by_key[(1970, "Col B - Number")] == 1.5
        assert by_key[(1971, "Col A - Number")] == 2100.0

    def test_parse_long_skips_short_rows(self):
        """A row with fewer than four fields is skipped."""
        text = "Commodity,Year,Attribute,Value\nOnly,three\nBlock,1970,Attr,1.0\n"
        assert parse_long(text) == [
            {"block": "Block", "year": 1970, "attribute": "Attr", "value": 1.0}
        ]

    def test_parse_wide_columnar_skips_trailing_nonyear(self):
        """A trailing footnote row past the data is skipped."""
        text = COLUMNAR_CSV + "Source: foo,,,,,,,\n"
        records = parse_wide_columnar(text, COLUMNAR_CONFIG)
        assert all(record["year"] in (1970, 1971) for record in records)

    def test_parse_records_dispatches_by_format(self):
        """parse_records dispatches the raw bytes to the format's parser."""
        columnar = parse_records(COLUMNAR_CSV.encode("utf-8"), COLUMNAR_CONFIG)
        assert distinct_blocks(columnar) == ["Coffee", "Tea"]
        fixed = parse_records(FIXED_CSV.encode("utf-8"), FIXED_CONFIG)
        assert distinct_blocks(fixed) == ["My Block"]

    def test_parse_nutrient_foodgroups_skips_year_before_block(self, monkeypatch):
        """A year row before any food-group label is skipped."""
        grid = [[""] * 57 for _ in range(4)]
        grid.append([1970.0] + [float(index) for index in range(1, 57)])
        grid.append(["Meat, poultry, and fish"])
        grid.append([1970.0] + [float(index) for index in range(1, 57)])

        def fake(**_kwargs):
            return FakeBook({"Foodgroups": FakeSheet(grid)})

        monkeypatch.setattr("xlrd.open_workbook", fake)
        records = parse_records(b"", CATALOG["nutrient"]["food_group"])
        assert distinct_blocks(records) == ["Meat, poultry, and fish"]

    def test_foodgroup_columns_pairs(self):
        """foodgroup_columns pairs a value and percent column per nutrient."""
        columns = foodgroup_columns()
        assert len(columns) == 56
        assert columns[0] == (1, "Food energy - Kilocalories")
        assert columns[1] == (2, "Food energy - Percent of total")
        assert columns[-1] == (56, "Sodium - Percent of total")

    def test_parse_nutrient_totals(self, monkeypatch):
        """parse_nutrient_totals reads the Totals sheet into tidy records."""
        monkeypatch.setattr("xlrd.open_workbook", _fake_workbook)
        config = CATALOG["nutrient"]["totals"]
        records = parse_records(b"", config)
        assert distinct_blocks(records) == ["Totals"]
        years = sorted({record["year"] for record in records})
        assert years == [1909, 2010]
        energy = next(
            r
            for r in records
            if r["attribute"] == "Food energy - Kilocalories" and r["year"] == 1909
        )
        assert energy["value"] == 10.0

    def test_parse_nutrient_foodgroups(self, monkeypatch):
        """parse_nutrient_foodgroups blocks by food group with paired columns."""
        monkeypatch.setattr("xlrd.open_workbook", _fake_workbook)
        config = CATALOG["nutrient"]["food_group"]
        records = parse_records(b"", config)
        assert distinct_blocks(records) == ["Meat, poultry, and fish", "Dairy products"]
        meat_1970 = {
            r["attribute"]: r["value"]
            for r in records
            if r["block"] == "Meat, poultry, and fish" and r["year"] == 1970
        }
        assert meat_1970["Food energy - Kilocalories"] == 1.0
        assert meat_1970["Food energy - Percent of total"] == 2.0

    def test_afetch_records_downloads_and_parses(self, monkeypatch):
        """afetch_records downloads the file through the cache and parses it."""
        calls = []

        async def fake_afetch_ers_file(media_path, product=None, ttl=None):
            calls.append((media_path, product))
            return LONG_CSV.encode("utf-8")

        monkeypatch.setattr(
            "openbb_government_us.usda.utils.ers_client.afetch_ers_file",
            fake_afetch_ers_file,
        )
        records = asyncio.run(afetch_records("food_availability", "eggs"))
        assert calls == [("/media/5333/eggs.csv", PRODUCT_PAGE)]
        assert any(
            record["block"] == "Eggs: Per capita availability" for record in records
        )

    def test_afetch_blocks_short_circuits_wide_files(self, monkeypatch):
        """afetch_blocks returns the single block without a download for wide files."""
        calls = []

        async def fake_afetch_ers_file(media_path, product=None, ttl=None):
            calls.append(media_path)
            return b""

        monkeypatch.setattr(
            "openbb_government_us.usda.utils.ers_client.afetch_ers_file",
            fake_afetch_ers_file,
        )
        blocks = asyncio.run(afetch_blocks("food_availability", "population"))
        assert blocks == [
            "Population: Resident and resident plus Armed Forces overseas"
        ]
        assert calls == []

    def test_afetch_blocks_parses_long_files(self, monkeypatch):
        """afetch_blocks parses the file for its distinct blocks otherwise."""

        async def fake_afetch_ers_file(media_path, product=None, ttl=None):
            return LONG_CSV.encode("utf-8")

        monkeypatch.setattr(
            "openbb_government_us.usda.utils.ers_client.afetch_ers_file",
            fake_afetch_ers_file,
        )
        blocks = asyncio.run(afetch_blocks("food_availability", "eggs"))
        assert blocks == [
            "Eggs: Per capita availability",
            "Eggs and egg products: Supply and use",
        ]


class TestFoodAvailabilityPerCapitaDataSystem:
    """Tests for the FoodAvailabilityPerCapitaDataSystem model."""

    def _records(self):
        """Parse the long fixture into records."""
        return parse_long(LONG_CSV)

    def test_transform_query_defaults(self):
        """transform_query applies the system default and resolves the food group."""
        query = FoodAvailabilityPerCapitaDataSystemFetcher.transform_query({})
        assert isinstance(query, FoodAvailabilityPerCapitaDataSystemQueryParams)
        assert query.data_system == "food_availability"
        assert query.food_group == "eggs"
        assert query.commodity is None

    def test_blank_data_system_falls_back(self):
        """A blank data system normalizes to the default."""
        query = FoodAvailabilityPerCapitaDataSystemQueryParams(data_system="")
        assert query.data_system == "food_availability"

    def test_invalid_data_system_raises(self):
        """An unknown data system raises OpenBBError."""
        with pytest.raises(OpenBBError, match="Invalid data system: bogus"):
            FoodAvailabilityPerCapitaDataSystemQueryParams(data_system="bogus")

    def test_food_group_resolves_per_system(self):
        """A None food group resolves to each system's default file."""
        for system, expected in SYSTEM_DEFAULT_GROUP.items():
            query = FoodAvailabilityPerCapitaDataSystemQueryParams(data_system=system)
            assert query.food_group == expected

    def test_food_group_invalid_for_system_raises(self):
        """A food group absent from the selected system raises OpenBBError."""
        with pytest.raises(OpenBBError, match="Invalid food group 'eggs'"):
            FoodAvailabilityPerCapitaDataSystemQueryParams(
                data_system="loss_adjusted", food_group="eggs"
            )

    def test_commodity_normalizes_to_string_or_none(self):
        """The commodity filter strips and accepts a single-element list."""
        assert (
            FoodAvailabilityPerCapitaDataSystemQueryParams(
                commodity="  Coffee "
            ).commodity
            == "Coffee"
        )
        assert (
            FoodAvailabilityPerCapitaDataSystemQueryParams(commodity=["Tea"]).commodity
            == "Tea"
        )
        assert (
            FoodAvailabilityPerCapitaDataSystemQueryParams(commodity="").commodity
            is None
        )

    def test_aextract_data_returns_records(self, monkeypatch):
        """aextract_data returns the parsed file records."""

        async def fake_afetch_records(data_system, food_group):
            return parse_long(LONG_CSV)

        monkeypatch.setattr(ers, "afetch_records", fake_afetch_records)
        query = FoodAvailabilityPerCapitaDataSystemFetcher.transform_query({})
        records = asyncio.run(
            FoodAvailabilityPerCapitaDataSystemFetcher.aextract_data(query, None)
        )
        assert any(
            record["block"] == "Eggs: Per capita availability" for record in records
        )

    def test_pivot_attributes_to_columns_years_to_rows(self):
        """The pivot spreads attributes into columns with chronological year rows."""
        query = FoodAvailabilityPerCapitaDataSystemFetcher.transform_query({})
        data = FoodAvailabilityPerCapitaDataSystemFetcher.transform_data(
            query, self._records()
        )
        assert [row.year for row in data] == [1909, 2020]
        first = data[0].model_dump(by_alias=True)
        assert first["year"] == 1909
        assert first["U.S. population, July 1-Millions"] == 90.49
        assert first["Shell-Total-Millions"] is None
        last = data[1].model_dump(by_alias=True)
        assert last["U.S. population, July 1-Millions"] == 330.0
        assert last["Shell-Total-Millions"] == 66000.0

    def test_pivot_drops_all_empty_columns(self):
        """A measure with no value in any row is dropped from the wide table."""
        query = FoodAvailabilityPerCapitaDataSystemFetcher.transform_query({})
        data = FoodAvailabilityPerCapitaDataSystemFetcher.transform_data(
            query, self._records()
        )
        for row in data:
            assert "Empty-Col-Millions" not in row.model_dump(by_alias=True)

    def test_pivot_defaults_to_first_block(self):
        """With no commodity, the pivot uses the file's first block."""
        query = FoodAvailabilityPerCapitaDataSystemFetcher.transform_query({})
        data = FoodAvailabilityPerCapitaDataSystemFetcher.transform_data(
            query, self._records()
        )
        served = data[0].model_dump(by_alias=True)
        assert "U.S. population, July 1-Millions" in served
        assert "Supply-Total-Millions" not in served

    def test_pivot_selects_named_commodity(self):
        """A named commodity restricts the pivot to that block."""
        query = FoodAvailabilityPerCapitaDataSystemFetcher.transform_query(
            {"commodity": "Eggs and egg products: Supply and use"}
        )
        data = FoodAvailabilityPerCapitaDataSystemFetcher.transform_data(
            query, self._records()
        )
        served = data[0].model_dump(by_alias=True)
        assert served["Supply-Total-Millions"] == 100.0
        assert "U.S. population, July 1-Millions" not in served

    def test_year_filters(self):
        """start_year and end_year filter the emitted year rows."""
        start = FoodAvailabilityPerCapitaDataSystemFetcher.transform_data(
            FoodAvailabilityPerCapitaDataSystemFetcher.transform_query(
                {"start_year": 2000}
            ),
            self._records(),
        )
        assert [row.year for row in start] == [2020]
        end = FoodAvailabilityPerCapitaDataSystemFetcher.transform_data(
            FoodAvailabilityPerCapitaDataSystemFetcher.transform_query(
                {"end_year": 1950}
            ),
            self._records(),
        )
        assert [row.year for row in end] == [1909]

    def test_empty_block_raises(self):
        """A commodity that matches no rows raises EmptyDataError."""
        query = FoodAvailabilityPerCapitaDataSystemFetcher.transform_query(
            {"commodity": "Does not exist"}
        )
        with pytest.raises(EmptyDataError):
            FoodAvailabilityPerCapitaDataSystemFetcher.transform_data(
                query, self._records()
            )

    def test_columns_defs_bind_and_no_constant_leak(self):
        """The only column definition is year, and no internal constant is served."""
        declared = set()
        for name, field in FoodAvailabilityPerCapitaDataSystemData.model_fields.items():
            alias = field.serialization_alias or name
            extra = field.json_schema_extra
            config = extra.get("x-widget_config", {}) if isinstance(extra, dict) else {}
            if config.get("exclude"):
                continue
            declared.add(to_snake(alias))
        assert declared == {"year"}
        query = FoodAvailabilityPerCapitaDataSystemFetcher.transform_query({})
        data = FoodAvailabilityPerCapitaDataSystemFetcher.transform_data(
            query, self._records()
        )
        served = set()
        for row in data:
            served.update(row.model_dump(by_alias=True))
        assert declared <= served
        for leaked in ("data_system", "food_group", "commodity", "block"):
            assert leaked not in served

    def test_param_scoping_options(self):
        """Choice and endpoint params are single-select with real labels."""
        extra = FoodAvailabilityPerCapitaDataSystemQueryParams.__json_schema_extra__
        system = extra["data_system"]["x-widget_config"]
        assert system["label"] == "Data system"
        assert system["multiSelect"] is False and system["multiple"] is False
        assert {opt["value"] for opt in system["options"]} == set(DATA_SYSTEMS)
        assert DATA_SYSTEM_OPTIONS[0]["value"] == "food_availability"
        food_group = extra["food_group"]["x-widget_config"]
        assert food_group["type"] == "endpoint"
        assert food_group["optionsParams"] == {"data_system": "$data_system"}
        commodity = extra["commodity"]["x-widget_config"]
        assert commodity["type"] == "endpoint"
        assert commodity["optionsParams"] == {
            "data_system": "$data_system",
            "food_group": "$food_group",
        }

    def test_widget_config_and_year_header(self):
        """The whole-widget config and the year column header are populated."""
        widget = FoodAvailabilityPerCapitaDataSystemData.model_config[
            "json_schema_extra"
        ]["x-widget_config"]
        assert widget["$.name"] == "USDA ERS Food Availability (Per Capita)"
        assert widget["$.category"] == "Economy"
        assert widget["$.subCategory"] == "Agriculture"
        assert widget["$.source"] == ["USDA", "ERS"]
        year = FoodAvailabilityPerCapitaDataSystemData.model_fields["year"]
        assert year.json_schema_extra["x-widget_config"]["pinned"] == "left"

    def test_null_token_mixin_coerces_placeholder(self):
        """The Data model coerces placeholder tokens to None but keeps the schema."""
        row = FoodAvailabilityPerCapitaDataSystemData.model_validate(
            {"year": 2020, "Shell-Total-Millions": "--"}
        )
        dumped = row.model_dump(by_alias=True)
        assert dumped["year"] == 2020
        assert dumped["Shell-Total-Millions"] is None
