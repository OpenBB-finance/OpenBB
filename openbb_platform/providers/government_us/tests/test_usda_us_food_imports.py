"""Tests for the USDA ERS U.S. food imports utils and model."""

import asyncio

import pytest
from openbb_core.app.model.abstract.error import OpenBBError
from pydantic.alias_generators import to_snake

from openbb_government_us.usda.models.us_food_imports import (
    UsFoodImportsData,
    UsFoodImportsFetcher,
    UsFoodImportsQueryParams,
)
from openbb_government_us.usda.utils import ers_us_food_imports
from openbb_government_us.usda.utils.ers_us_food_imports import (
    DEFAULT_COMMODITY,
    DEFAULT_FOOD_GROUP,
    FOOD_GROUPS,
    FOOD_IMPORTS_FILES,
    MEASURES,
    MEDIA_PATH,
    PRODUCT_PAGE,
    build_url,
    clean_country,
    food_group_column_label,
    parse_rows,
    product_lines,
    unit_label,
)

FIXTURE_CSV = (
    "Commodity,Country,UOM,Category,SubCategory,RowNumber,YearNum,FoodValue\n"
    "U.S. imports,WORLD,Million $,Food dollars,Total foods,1,2023,100.0\n"
    "U.S. imports,WORLD,Million $,Food dollars,Total foods,1,2024,110.0\n"
    "Fruits,WORLD,Million $,Food dollars,Foods,7,2023,40.0\n"
    "Fruits,WORLD,Million $,Food dollars,Foods,7,2024,44.0\n"
    "Beverages,WORLD,Million $,Food dollars,Foods,15,2023,20.0\n"
    "Beverages,WORLD,Million $,Food dollars,Foods,15,2024,22.0\n"
    "Animals,WORLD,Million $,Food dollars,Subtotal foods,16,2023,5.0\n"
    "Fruits,WORLD,percent,Food dollars,Foods,7,2024,10.0\n"
    "Fruits,WORLD,percent,Food dollars,Foods,7,means10years,3.3\n"
    'Live meat animals,WORLD (Quantity),"1,000",Food volume,Foods,2,2024,900.0\n'
    'Beverages,WORLD (Quantity),"1,000 litpf",Food volume,Foods,3,2024,500.0\n'
    'Fruits,WORLD (Quantity),"1,000 mt",Food volume,Foods,7,2024,700.0\n'
    "Fruits,WORLD,Dollars per mt,Prices,Imported food prices,7,2024,1234.5\n"
    "Live meat animals,WORLD,Dollars,Prices,Imported food prices,2,2024,88.0\n"
    "Total fruit and preparations,MEXICO,Million $,Fruits,Foods,1,2023,30.0\n"
    "Total fruit and preparations,MEXICO,Million $,Fruits,Foods,1,2024,33.0\n"
    "Total fruit and preparations,CANADA,Million $,Fruits,Foods,2,2023,10.0\n"
    "Total fruit and preparations,CANADA,Million $,Fruits,Foods,2,2024,11.0\n"
    'Total fruit and preparations,"GERMANY, FED. REPUBLIC",Million $,Fruits,Foods,3,2024,2.0\n'
    "Total fruit and preparations,REST OF WORLD,Million $,Fruits,Foods,4,2024,5.0\n"
    "Total fruit and preparations,WORLD,Million $,Fruits,Foods,5,2024,51.0\n"
    'Total fruit and preparations,WORLD (Quantity),"1,000 mt",Fruits,Foods,6,2024,800.0\n'
    "Fresh or chilled fruit,MEXICO,Million $,Fruits,Foods,7,2024,8.0\n"
    "Total fruit and preparations,MEXICO,Million $,Fruits,Foods,1,notayear,99.0\n"
    "Total fruit and preparations,MEXICO,Million $,Fruits,Foods,1,2022,n/a\n"
    "Total fruit and preparations,MEXICO,Million $,Fruits,Foods,bad,2021,5.0\n"
)


class TestErsUsFoodImportsUtils:
    """Tests for the ers_us_food_imports utils module."""

    def test_catalog_and_url(self):
        """The catalog is a single summary file and build_url points at it."""
        assert FOOD_IMPORTS_FILES == {"summary": (MEDIA_PATH, PRODUCT_PAGE)}
        assert MEDIA_PATH.startswith("/media/6495/")
        assert build_url().endswith(MEDIA_PATH)
        assert len(FOOD_GROUPS) == 14

    def test_clean_country_title_cases_and_fixes(self):
        """Country labels title-case, with the special sources mapped."""
        assert clean_country("MEXICO") == "Mexico"
        assert clean_country("COSTA RICA") == "Costa Rica"
        assert clean_country("China ") == "China"
        assert clean_country("REPUBLIC OF SOUTH AFRICA") == "Republic of South Africa"
        assert clean_country("GERMANY, FED. REPUBLIC") == "Germany"
        assert clean_country("REST OF WORLD") == "Rest of world"
        assert clean_country("WORLD") == "World"
        assert clean_country("WORLD (Quantity)") == "World"
        assert clean_country("COTE D�IVOIRE") == "Cote d'Ivoire"

    def test_unit_label_disambiguates_head(self):
        """The bare thousand unit is labeled as head; others pass through."""
        assert unit_label("1,000") == "1,000 head"
        assert unit_label(" 1,000 mt ") == "1,000 mt"
        assert unit_label("Dollars per KL") == "Dollars per KL"

    def test_food_group_column_label(self):
        """Aggregate commodity names map to their short column labels."""
        assert food_group_column_label("U.S. imports") == "Total foods"
        assert food_group_column_label("Live meat animals") == "Live animals"
        assert food_group_column_label("Fish and shellfish") == "Fish"
        assert food_group_column_label("Grains") == "Grains"

    def test_parse_rows_skips_means_nonnumeric_and_bad_rownumber(self):
        """Period averages, non-numeric values, and bad row numbers are dropped."""
        records = parse_rows(FIXTURE_CSV)
        assert all(isinstance(record["year"], int) for record in records)
        assert all(record["year"] not in (2021, 2022) for record in records)
        mexico_years = {
            record["year"]
            for record in records
            if record["category"] == "Fruits"
            and record["commodity"] == "Total fruit and preparations"
            and record["country"] == "MEXICO"
        }
        assert mexico_years == {2023, 2024}

    def test_parse_rows_types_and_values(self):
        """Parsed records carry stripped strings, int row numbers, and floats."""
        records = parse_rows(FIXTURE_CSV)
        total = next(
            record
            for record in records
            if record["commodity"] == "U.S. imports" and record["year"] == 2024
        )
        assert total == {
            "commodity": "U.S. imports",
            "country": "WORLD",
            "uom": "Million $",
            "category": "Food dollars",
            "subcategory": "Total foods",
            "row_number": 1,
            "year": 2024,
            "value": 110.0,
        }

    def test_product_lines_ordered_by_row_number(self):
        """Product lines list by first row number, the total line first."""
        records = parse_rows(FIXTURE_CSV)
        assert product_lines(records, "Fruits") == [
            "Total fruit and preparations",
            "Fresh or chilled fruit",
        ]

    def test_product_lines_empty_group(self):
        """A group absent from the file yields no product lines."""
        records = parse_rows(FIXTURE_CSV)
        assert product_lines(records, "Grains") == []

    def test_afetch_records(self, monkeypatch):
        """afetch_records fetches the CSV through the ERS cache and parses it."""
        calls = []

        async def fake_afetch_ers_file(media_path, product=None, ttl=None):
            calls.append((media_path, product))
            return FIXTURE_CSV.encode("utf-8")

        monkeypatch.setattr(
            "openbb_government_us.usda.utils.ers_client.afetch_ers_file",
            fake_afetch_ers_file,
        )
        records = asyncio.run(ers_us_food_imports.afetch_records())
        assert calls == [(MEDIA_PATH, PRODUCT_PAGE)]
        assert any(record["commodity"] == "U.S. imports" for record in records)


class TestUsFoodImports:
    """Tests for the UsFoodImports model."""

    def _records(self):
        """Parse the fixture into long records."""
        return parse_rows(FIXTURE_CSV)

    def test_transform_query_defaults(self):
        """transform_query applies the table, measure, and food-group defaults."""
        query = UsFoodImportsFetcher.transform_query({})
        assert isinstance(query, UsFoodImportsQueryParams)
        assert query.table == "by_food_group"
        assert query.measure == "value"
        assert query.food_group == DEFAULT_FOOD_GROUP
        assert query.commodity is None

    def test_blank_values_fall_back_to_defaults(self):
        """Blank table, measure, and food group normalize to their defaults."""
        query = UsFoodImportsQueryParams(table="", measure="", food_group="")
        assert query.table == "by_food_group"
        assert query.measure == "value"
        assert query.food_group == DEFAULT_FOOD_GROUP

    def test_invalid_table_measure_food_group_raise(self):
        """Unknown table, measure, or food group raise OpenBBError."""
        with pytest.raises(OpenBBError, match="Invalid table: bogus"):
            UsFoodImportsQueryParams(table="bogus")
        with pytest.raises(OpenBBError, match="Invalid measure: bogus"):
            UsFoodImportsQueryParams(measure="bogus")
        with pytest.raises(OpenBBError, match="Invalid food group: bogus"):
            UsFoodImportsQueryParams(food_group="bogus")

    def test_food_group_accepts_valid_value(self):
        """A valid non-default food group passes validation unchanged."""
        assert (
            UsFoodImportsQueryParams(food_group="Beverages").food_group == "Beverages"
        )

    def test_commodity_normalizes_to_string_or_none(self):
        """The commodity filter strips and accepts a single-element list."""
        assert UsFoodImportsQueryParams(commodity="  Bananas ").commodity == "Bananas"
        assert UsFoodImportsQueryParams(commodity=["Wine"]).commodity == "Wine"
        assert UsFoodImportsQueryParams(commodity="").commodity is None

    def test_aextract_data_returns_records(self, monkeypatch):
        """aextract_data returns the parsed summary records."""

        async def fake_afetch_records():
            return parse_rows(FIXTURE_CSV)

        monkeypatch.setattr(ers_us_food_imports, "afetch_records", fake_afetch_records)
        query = UsFoodImportsFetcher.transform_query({})
        records = asyncio.run(UsFoodImportsFetcher.aextract_data(query, None))
        assert any(record["commodity"] == "Fruits" for record in records)

    def test_by_food_group_value_pivot(self):
        """The food-group value table spreads food groups into columns by year."""
        query = UsFoodImportsFetcher.transform_query({})
        data = UsFoodImportsFetcher.transform_data(query, self._records())
        assert [row.year for row in data] == [2023, 2024]
        first = data[0].model_dump(by_alias=True)
        assert first["Total foods"] == 100.0
        assert first["Fruits"] == 40.0
        assert first["Beverages"] == 20.0
        assert first["unit"] == "Million $"
        assert first["food_group"] is None
        assert "Animals" not in first

    def test_by_food_group_value_column_order(self):
        """Food-group value columns follow the source row-number order."""
        query = UsFoodImportsFetcher.transform_query({})
        data = UsFoodImportsFetcher.transform_data(query, self._records())
        keys = list(data[0].model_dump(by_alias=True))
        assert keys[:4] == ["year", "food_group", "commodity", "unit"]
        assert keys[4:] == ["Total foods", "Fruits", "Beverages"]

    def test_by_food_group_value_change_excludes_period_average(self):
        """The value-change measure reads percent rows and drops period averages."""
        query = UsFoodImportsFetcher.transform_query({"measure": "value_change"})
        data = UsFoodImportsFetcher.transform_data(query, self._records())
        assert [row.year for row in data] == [2024]
        row = data[0].model_dump(by_alias=True)
        assert row["Fruits"] == 10.0
        assert row["unit"] == "percent"

    def test_by_food_group_volume_carries_unit_in_header(self):
        """Volume columns embed each food group's own unit in the column key."""
        query = UsFoodImportsFetcher.transform_query({"measure": "volume"})
        data = UsFoodImportsFetcher.transform_data(query, self._records())
        row = data[0].model_dump(by_alias=True)
        assert row["Live animals (1,000 head)"] == 900.0
        assert row["Beverages (1,000 litpf)"] == 500.0
        assert row["Fruits (1,000 mt)"] == 700.0
        assert row["unit"] is None

    def test_by_food_group_unit_price(self):
        """Unit-price columns carry the price unit in the column key."""
        query = UsFoodImportsFetcher.transform_query({"measure": "unit_price"})
        data = UsFoodImportsFetcher.transform_data(query, self._records())
        row = data[0].model_dump(by_alias=True)
        assert row["Fruits (Dollars per mt)"] == 1234.5
        assert row["Live animals (Dollars)"] == 88.0

    def test_by_source_value_pivot_and_country_cleanup(self):
        """The source table spreads cleaned source countries into columns."""
        query = UsFoodImportsFetcher.transform_query({"table": "by_source"})
        data = UsFoodImportsFetcher.transform_data(query, self._records())
        assert [row.year for row in data] == [2023, 2024]
        row_2024 = data[1].model_dump(by_alias=True)
        assert list(row_2024)[4:] == [
            "Mexico",
            "Canada",
            "Germany",
            "Rest of world",
            "World",
        ]
        assert row_2024["Mexico"] == 33.0
        assert row_2024["Germany"] == 2.0
        assert row_2024["World"] == 51.0
        assert row_2024["food_group"] == "Fruits"
        assert row_2024["commodity"] == "Total fruit and preparations"
        assert row_2024["unit"] == "Million $"

    def test_by_source_defaults_to_total_product_line(self):
        """With no commodity, the source table uses the group's total line."""
        query = UsFoodImportsFetcher.transform_query({"table": "by_source"})
        data = UsFoodImportsFetcher.transform_data(query, self._records())
        assert all(row.commodity == "Total fruit and preparations" for row in data)
        assert all("Mexico" in row.model_dump(by_alias=True) for row in data)

    def test_by_source_selects_named_commodity(self):
        """A named product line restricts the source table to that commodity."""
        query = UsFoodImportsFetcher.transform_query(
            {"table": "by_source", "commodity": "Fresh or chilled fruit"}
        )
        data = UsFoodImportsFetcher.transform_data(query, self._records())
        assert [row.year for row in data] == [2024]
        assert data[0].model_dump(by_alias=True)["Mexico"] == 8.0

    def test_by_source_volume_single_world_column(self):
        """Source volume yields the world-quantity column with its unit."""
        query = UsFoodImportsFetcher.transform_query(
            {"table": "by_source", "measure": "volume"}
        )
        data = UsFoodImportsFetcher.transform_data(query, self._records())
        row = data[0].model_dump(by_alias=True)
        assert row["World (1,000 mt)"] == 800.0
        assert row["unit"] is None

    def test_by_source_rejects_unsupported_measure(self):
        """Measures other than value and volume return no source rows."""
        query = UsFoodImportsFetcher.transform_query(
            {"table": "by_source", "measure": "inflation"}
        )
        assert UsFoodImportsFetcher.transform_data(query, self._records()) == []

    def test_year_filters(self):
        """start_year and end_year filter the emitted year rows."""
        start = UsFoodImportsFetcher.transform_data(
            UsFoodImportsFetcher.transform_query({"start_year": 2024}), self._records()
        )
        assert [row.year for row in start] == [2024]
        end = UsFoodImportsFetcher.transform_data(
            UsFoodImportsFetcher.transform_query({"end_year": 2023}), self._records()
        )
        assert [row.year for row in end] == [2023]

    def test_by_source_year_filters(self):
        """Year filters apply on the source table as well."""
        start = UsFoodImportsFetcher.transform_data(
            UsFoodImportsFetcher.transform_query(
                {"table": "by_source", "start_year": 2024}
            ),
            self._records(),
        )
        assert [row.year for row in start] == [2024]
        end = UsFoodImportsFetcher.transform_data(
            UsFoodImportsFetcher.transform_query(
                {"table": "by_source", "end_year": 2023}
            ),
            self._records(),
        )
        assert [row.year for row in end] == [2023]

    def test_columns_defs_bind_to_served_keys(self):
        """Every declared column definition binds to a served record key."""
        declared = set()
        for name, field in UsFoodImportsData.model_fields.items():
            alias = field.serialization_alias or name
            extra = field.json_schema_extra
            config = extra.get("x-widget_config", {}) if isinstance(extra, dict) else {}
            if config.get("exclude"):
                continue
            declared.add(to_snake(alias))
        query = UsFoodImportsFetcher.transform_query({})
        data = UsFoodImportsFetcher.transform_data(query, self._records())
        served = set()
        for row in data:
            served.update(row.model_dump(by_alias=True))
        assert declared <= served

    def test_param_scoping_options(self):
        """Choice params are single-select with real labels and options."""
        extra = UsFoodImportsQueryParams.__json_schema_extra__
        table = extra["table"]["x-widget_config"]
        assert table["label"] == "Table" and table["multiSelect"] is False
        assert {opt["value"] for opt in table["options"]} == {
            "by_food_group",
            "by_source",
        }
        measure = extra["measure"]["x-widget_config"]
        assert {opt["value"] for opt in measure["options"]} == set(MEASURES)
        commodity = extra["commodity"]["x-widget_config"]
        assert commodity["type"] == "endpoint"
        assert commodity["optionsParams"] == {"food_group": "$food_group"}
        assert commodity["value"] == DEFAULT_COMMODITY

    def test_widget_config_and_column_headers(self):
        """The whole-widget config and per-field headers are populated."""
        widget = UsFoodImportsData.model_config["json_schema_extra"]["x-widget_config"]
        assert widget["$.name"] == "USDA ERS U.S. Food Imports"
        assert widget["$.category"] == "Economy"
        assert widget["$.subCategory"] == "Agriculture"
        assert widget["$.source"] == ["USDA", "ERS"]
        fields = UsFoodImportsData.model_fields
        assert fields["year"].json_schema_extra["x-widget_config"]["pinned"] == "left"
        assert fields["food_group"].json_schema_extra["x-widget_config"]["hide"] is True

    def test_null_token_mixin_coerces_placeholder(self):
        """The Data model coerces placeholder tokens to None but keeps columns."""
        row = UsFoodImportsData.model_validate(
            {"year": 2024, "food_group": "--", "Fruits": 44.0}
        )
        dumped = row.model_dump(by_alias=True)
        assert dumped["food_group"] is None
        assert dumped["Fruits"] == 44.0
