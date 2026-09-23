"""Tests for the USDA ERS food security in the United States utils and model."""

import asyncio
import zipfile
from io import BytesIO

import pytest
from openbb_core.app.model.abstract.error import OpenBBError

from openbb_government_us.usda.models.food_security_in_the_united_states import (
    DEFAULT_TABLE,
    FoodSecurityInTheUnitedStatesData,
    FoodSecurityInTheUnitedStatesFetcher,
    FoodSecurityInTheUnitedStatesQueryParams,
)
from openbb_government_us.usda.utils import ers_food_security_in_the_united_states
from openbb_government_us.usda.utils.ers_food_security_in_the_united_states import (
    FOOD_SECURITY_TABLES,
    MEDIA_PATH,
    MEMBER_PREFIX,
    PRODUCT_PAGE,
    afetch_categories,
    afetch_table,
    clean_number,
    normalize_header,
    parse_table,
)

ALL_HOUSEHOLDS_CSV = (
    'Year,Category,Subcategory,Sub-subcategory,Total,"Food secure-1,000",'
    'Food secure-percent,"Food insecure-1,000",Food insecure-percent,'
    '"Low food security-1,000",Low food security-percent,'
    '"Very low food security-1,000",Very low food security-percent\n'
    "2023,All households,,,132532,114576,86.5,17956,13.5,11157,8.4,6799,5.1\n"
    "2024,All households,,,134062,115722,86.3,18340,13.7,11138,8.3,7202,5.4\n"
    "2024,Race/ethnicity of households,White non-Hispanic,,84552,76015,89.9,"
    "8537,10.1,5071,6.0,3466,4.1\n"
    "2024,Race/ethnicity of households,Black non-Hispanic,,17582,13300,75.6,"
    "4282,24.4,2433,13.8,1849,10.5\n"
    "2024,Household composition,With children < 18 years,With children < 6 years,"
    "16000, N/A ,82.6,2938,17.4,2304,13.7,634,3.8\n"
    ",All households,,,999,1,1,1,1,1,1,1,1\n"
    "abcd,All households,,,999,1,1,1,1,1,1,1,1\n"
)

CHILDREN_CSV = (
    'Year,Category,Subcategory,Total,"Food-secure households-1,000",'
    'Food-secure households-percent,"Food-insecure households-1,000",'
    'Food-insecure households-percent," Households with food-insecure children-1,000 ",'
    "Households with food-insecure children-percent,"
    '"Households with very low food security among children-1,000",'
    "Households with very low food security among children-percent\n"
    "2008,All households with children,,39699,31364,79,8335,21,4361,11,506,1.3\n"
    "2024,Household composition,Married-couple families,26705,22886,85.7,3819,"
    "14.3,1912,7.2,196,0.7\n"
)

CHILD_TRENDS_CSV = (
    'Year,Category,Total,"Food-secure households-1,000",Food-secure households-percent,'
    '"Food-insecure households-1,000",Food-insecure households-percent,'
    '" Households with food-insecure children-1,000 ",'
    "Households with food-insecure children-percent,"
    '" Households with very low food security among children-1,000 ",'
    "Households with very low food security among children-percent,\n"
    "1998,Children - by food security status of household,71282,57255,80.3,14027,"
    "19.7,7840,11,716,1,\n"
    "1999,Households with Children,�72179,59344,83.1,12074,16.9,6996,9.8,"
    "511,0.7,\n"
)

EDUCATION_CSV = (
    'Year,Category,Subcategory,Sub-subcategory,Total,"Food insecure-1,000",'
    'Food insecure-percent,Food insecure-share,"Very low food security-1,000",'
    "Very low food security-percent,Very low food security-share\n"
    "2017,All households,,,127272,15018,11.8,100,5757,4.5,100\n"
    "2017,All households,Employment,Full-time,83681,7871,9.4,52.4,2448,2.9,42.5\n"
)

STATE_CSV = (
    "Year,State,Food insecurity prevalence,Food insecurity�margin of error,"
    "Very low food security prevalence,Very low food security�margin of error \n"
    "2006�2008,U.S. total,12.2,0.25,4.6,0.18\n"
    "2022�2024,U.S.,13.3,0.40,5.2,0.21\n"
    "2022�2024,CA,12.5,0.82,4.4,0.49\n"
)


class TestErsFoodSecurityUtils:
    """Tests for the ers_food_security_in_the_united_states utils module."""

    def test_catalog_contents(self):
        """The catalog holds the six tables mapped to their zip members."""
        assert list(FOOD_SECURITY_TABLES) == [
            "national_trend",
            "by_characteristic",
            "households_with_children",
            "child_trends",
            "education_employment_disability",
            "by_state",
        ]
        assert MEDIA_PATH == "/media/799/food-security-csv-data-files.zip"
        assert FOOD_SECURITY_TABLES["national_trend"]["category_mode"] == "only_all"
        assert (
            FOOD_SECURITY_TABLES["by_characteristic"]["category_mode"] == "exclude_all"
        )
        assert FOOD_SECURITY_TABLES["by_state"]["year_is_period"] is True
        for config in FOOD_SECURITY_TABLES.values():
            assert config["label"]
            assert config["member"].endswith(".csv")
            assert config["measures"]

    def test_normalize_header_replaces_fffd_and_spaces(self):
        """The replacement character and stray spaces are normalized."""
        assert (
            normalize_header("Food insecurity�margin of error")
            == "Food insecurity margin of error"
        )
        assert (
            normalize_header(" Households with food-insecure children-1,000 ")
            == "Households with food-insecure children-1,000"
        )

    def test_clean_number_strips_fffd_and_commas(self):
        """Numeric cells strip the replacement character and thousands commas."""
        assert clean_number("�72179") == 72179.0
        assert clean_number("1,234") == 1234.0
        assert clean_number("86.5") == 86.5

    def test_clean_number_handles_blank_and_na(self):
        """Blank and N/A cells parse to None."""
        assert clean_number("") is None
        assert clean_number("   ") is None
        assert clean_number(" N/A ") is None

    def test_parse_national_keeps_only_all_households(self):
        """The national table keeps only the All households category."""
        records = parse_table(ALL_HOUSEHOLDS_CSV, "national_trend")
        assert {record["category"] for record in records} == {"All households"}
        assert {record["year"] for record in records} == {"2023", "2024"}
        first = next(
            record
            for record in records
            if record["year"] == "2024" and record["series"] == "Food secure (percent)"
        )
        assert first["value"] == 86.3
        assert first["sort_year"] == 2024
        assert first["subcategory"] is None

    def test_parse_by_characteristic_excludes_all_households(self):
        """The by-characteristic table drops the All households aggregate."""
        records = parse_table(ALL_HOUSEHOLDS_CSV, "by_characteristic")
        assert "All households" not in {record["category"] for record in records}
        race = [
            record
            for record in records
            if record["subcategory"] == "White non-Hispanic"
            and record["series"] == "Food insecure (percent)"
        ]
        assert len(race) == 1
        assert race[0]["value"] == 10.1
        sub_sub = next(
            record
            for record in records
            if record["sub_subcategory"] == "With children < 6 years"
            and record["series"] == "Food secure (1,000)"
        )
        assert sub_sub["value"] is None

    def test_parse_skips_blank_and_nonnumeric_years(self):
        """Rows with a blank or non-numeric year label are dropped."""
        records = parse_table(ALL_HOUSEHOLDS_CSV, "national_trend")
        assert all(record["sort_year"] in (2023, 2024) for record in records)

    def test_parse_children_uses_padded_header(self):
        """The children table reads the space-padded food-insecure-children column."""
        records = parse_table(CHILDREN_CSV, "households_with_children")
        record = next(
            record
            for record in records
            if record["year"] == "2008"
            and record["series"] == "Households with food-insecure children (1,000)"
        )
        assert record["value"] == 4361.0
        assert record["category"] == "All households with children"

    def test_parse_child_trends_strips_fffd_number(self):
        """The child-trends table strips a replacement-character number prefix."""
        records = parse_table(CHILD_TRENDS_CSV, "child_trends")
        total = next(
            record
            for record in records
            if record["year"] == "1999"
            and record["series"] == "Total households (1,000)"
        )
        assert total["value"] == 72179.0
        assert {record["category"] for record in records} == {
            "Children - by food security status of household",
            "Households with Children",
        }

    def test_parse_education_adds_share_measures(self):
        """The education table adds the share measures to the vocabulary."""
        records = parse_table(EDUCATION_CSV, "education_employment_disability")
        share = next(
            record
            for record in records
            if record["subcategory"] == "Employment"
            and record["series"] == "Food insecure (share of food insecure)"
        )
        assert share["value"] == 52.4

    def test_parse_state_normalizes_period_and_labels(self):
        """The state table normalizes the period dash and national labels."""
        records = parse_table(STATE_CSV, "by_state")
        assert {record["year"] for record in records} == {"2006-2008", "2022-2024"}
        assert {record["state"] for record in records} == {"United States", "CA"}
        moe = next(
            record
            for record in records
            if record["state"] == "CA"
            and record["series"] == "Food insecurity margin of error"
        )
        assert moe["value"] == 0.82

    def test_parse_empty_text_returns_empty(self):
        """Empty CSV text yields no records."""
        assert parse_table("", "national_trend") == []

    def test_parse_missing_year_column_returns_empty(self):
        """A table without a Year header yields no records."""
        assert parse_table("Foo,Bar\n1,2\n", "national_trend") == []

    def test_parse_skips_blank_line_and_short_row(self):
        """A blank line is skipped and a truncated row emits only its cells."""
        text = (
            'Year,Category,Subcategory,Sub-subcategory,Total,"Food secure-1,000"\n'
            "\n"
            "2024,All households,,,134062\n"
        )
        records = parse_table(text, "national_trend")
        assert {record["year"] for record in records} == {"2024"}
        emitted = {record["series"] for record in records}
        assert "Total households (1,000)" in emitted
        assert "Food secure (1,000)" not in emitted

    def test_afetch_table(self, monkeypatch):
        """afetch_table fetches the zip through the cache and reads the member."""
        calls = []
        buffer = BytesIO()
        member = FOOD_SECURITY_TABLES["national_trend"]["member"]
        with zipfile.ZipFile(buffer, "w") as archive:
            archive.writestr(MEMBER_PREFIX + member, ALL_HOUSEHOLDS_CSV)
        content = buffer.getvalue()

        async def fake_afetch_ers_file(media_path, product=None, ttl=None):
            calls.append((media_path, product))
            return content

        monkeypatch.setattr(
            "openbb_government_us.usda.utils.ers_client.afetch_ers_file",
            fake_afetch_ers_file,
        )
        records = asyncio.run(afetch_table("national_trend"))
        assert calls == [(MEDIA_PATH, PRODUCT_PAGE)]
        assert {record["category"] for record in records} == {"All households"}

    def test_afetch_categories(self, monkeypatch):
        """afetch_categories lists the distinct categories in first-seen order."""
        buffer = BytesIO()
        member = FOOD_SECURITY_TABLES["by_characteristic"]["member"]
        with zipfile.ZipFile(buffer, "w") as archive:
            archive.writestr(MEMBER_PREFIX + member, ALL_HOUSEHOLDS_CSV)
        content = buffer.getvalue()

        async def fake_afetch_ers_file(media_path, product=None, ttl=None):
            return content

        monkeypatch.setattr(
            "openbb_government_us.usda.utils.ers_client.afetch_ers_file",
            fake_afetch_ers_file,
        )
        categories = asyncio.run(afetch_categories("by_characteristic"))
        assert categories == ["Race/ethnicity of households", "Household composition"]


def _long_record(year, sort_year, series, value, **dims):
    """Build one long-format food-security record for the transform tests."""
    fields = {
        "category": None,
        "subcategory": None,
        "sub_subcategory": None,
        "state": None,
    }
    fields.update(dims)
    return {
        "table": "test",
        "year": year,
        "sort_year": sort_year,
        "series": series,
        "value": value,
        **fields,
    }


class TestFoodSecurityInTheUnitedStates:
    """Tests for the FoodSecurityInTheUnitedStates model."""

    def test_transform_query_default_table(self):
        """transform_query defaults the table and keeps the filters."""
        query = FoodSecurityInTheUnitedStatesFetcher.transform_query(
            {"start_year": 2010}
        )
        assert isinstance(query, FoodSecurityInTheUnitedStatesQueryParams)
        assert query.table == DEFAULT_TABLE
        assert query.start_year == 2010
        assert query.category is None

    def test_table_blank_returns_default(self):
        """A blank or None table normalizes to the default table."""
        assert (
            FoodSecurityInTheUnitedStatesQueryParams(table=None).table  # ty: ignore[invalid-argument-type]
            == DEFAULT_TABLE
        )
        assert FoodSecurityInTheUnitedStatesQueryParams(table="").table == DEFAULT_TABLE

    def test_table_strips_whitespace(self):
        """A padded table value is stripped before validation."""
        query = FoodSecurityInTheUnitedStatesQueryParams(table="  by_state  ")
        assert query.table == "by_state"

    def test_unknown_table_raises(self):
        """An unknown table raises OpenBBError listing valid choices."""
        with pytest.raises(OpenBBError, match="Invalid table: bogus"):
            FoodSecurityInTheUnitedStatesQueryParams(table="bogus")

    def test_non_string_table_raises(self):
        """A non-string, non-empty table value raises OpenBBError."""
        with pytest.raises(OpenBBError, match="Invalid table"):
            FoodSecurityInTheUnitedStatesQueryParams(table=123)  # ty: ignore[invalid-argument-type]

    def test_category_normalizes_to_string_or_none(self):
        """The category filter normalizes to a stripped string or None."""
        assert FoodSecurityInTheUnitedStatesQueryParams(category="").category is None
        assert (
            FoodSecurityInTheUnitedStatesQueryParams(category="  Hispanic  ").category
            == "Hispanic"
        )
        assert (
            FoodSecurityInTheUnitedStatesQueryParams(category=["Hispanic"]).category  # ty: ignore[invalid-argument-type]
            == "Hispanic"
        )

    def test_aextract_data_fetches_selected_table(self, monkeypatch):
        """aextract_data fetches only the selected table's rows."""
        fetched = []

        async def fake_afetch_table(table, **kwargs):
            fetched.append(table)
            return [{"table": table}]

        monkeypatch.setattr(
            ers_food_security_in_the_united_states, "afetch_table", fake_afetch_table
        )
        query = FoodSecurityInTheUnitedStatesFetcher.transform_query(
            {"table": "by_state"}
        )
        records = asyncio.run(
            FoodSecurityInTheUnitedStatesFetcher.aextract_data(query, None)
        )
        assert fetched == ["by_state"]
        assert records == [{"table": "by_state"}]

    def test_data_model_serves_only_period(self):
        """The Data model exposes a single pinned period field."""
        assert set(FoodSecurityInTheUnitedStatesData.model_fields) == {"period"}
        widget = FoodSecurityInTheUnitedStatesData.model_fields[
            "period"
        ].json_schema_extra["x-widget_config"]
        assert widget["pinned"] == "left"
        assert widget["headerName"] == "Period"

    def test_transform_data_national_folds_year_only(self):
        """The national table folds the constant category away, leaving the year."""
        records = parse_table(ALL_HOUSEHOLDS_CSV, "national_trend")
        query = FoodSecurityInTheUnitedStatesFetcher.transform_query({})
        data = FoodSecurityInTheUnitedStatesFetcher.transform_data(query, records)
        assert [row.period for row in data] == ["2023", "2024"]
        row_2024 = data[1].model_dump(by_alias=True)
        assert row_2024["Total households (1,000)"] == 134062.0
        assert row_2024["Food secure (percent)"] == 86.3
        assert row_2024["Very low food security (1,000)"] == 7202.0

    def test_transform_data_folds_varying_dimensions(self):
        """Varying characteristic dimensions fold into a unique period label."""
        records = [
            _long_record("2020", 2020, "S1", 1.0, category="A", subcategory="X"),
            _long_record("2020", 2020, "S2", 2.0, category="A", subcategory="X"),
            _long_record("2020", 2020, "S1", 3.0, category="A", subcategory="Y"),
            _long_record("2020", 2020, "S1", 5.0, category="B", subcategory="Z"),
        ]
        query = FoodSecurityInTheUnitedStatesFetcher.transform_query({})
        data = FoodSecurityInTheUnitedStatesFetcher.transform_data(query, records)
        periods = [row.period for row in data]
        assert periods == [
            "A — X — 2020",
            "A — Y — 2020",
            "B — Z — 2020",
        ]
        assert len(set(periods)) == len(periods)

    def test_transform_data_omits_constant_dimension(self):
        """A dimension that never varies is left out of the period label."""
        records = [
            _long_record("2019", 2019, "S1", 1.0, category="A", subcategory="X"),
            _long_record("2019", 2019, "S1", 2.0, category="A", subcategory="Y"),
        ]
        query = FoodSecurityInTheUnitedStatesFetcher.transform_query({})
        data = FoodSecurityInTheUnitedStatesFetcher.transform_data(query, records)
        assert [row.period for row in data] == ["X — 2019", "Y — 2019"]

    def test_transform_data_null_token_dim_treated_as_absent(self):
        """A null-token dimension value drops out of the folded label."""
        records = [
            _long_record("2018", 2018, "S1", 1.0, category="A", subcategory="X"),
            _long_record("2018", 2018, "S1", 2.0, category="A", subcategory="Y"),
            _long_record("2018", 2018, "S1", 3.0, category="A", subcategory="NA"),
        ]
        query = FoodSecurityInTheUnitedStatesFetcher.transform_query({})
        data = FoodSecurityInTheUnitedStatesFetcher.transform_data(query, records)
        assert [row.period for row in data] == ["X — 2018", "Y — 2018", "2018"]

    def test_transform_data_emits_identical_value_columns(self):
        """Every row carries the full union of value columns, missing ones None."""
        records = [
            _long_record("2021", 2021, "S1", 1.0, category="A"),
            _long_record("2021", 2021, "S2", 2.0, category="B"),
        ]
        query = FoodSecurityInTheUnitedStatesFetcher.transform_query({})
        data = FoodSecurityInTheUnitedStatesFetcher.transform_data(query, records)
        dumped = [row.model_dump(by_alias=True) for row in data]
        assert dumped[0] == {"period": "A — 2021", "S1": 1.0, "S2": None}
        assert dumped[1] == {"period": "B — 2021", "S1": None, "S2": 2.0}

    def test_transform_data_by_characteristic_category_filter(self):
        """A category filter narrows rows and drops the now-constant category."""
        records = parse_table(ALL_HOUSEHOLDS_CSV, "by_characteristic")
        query = FoodSecurityInTheUnitedStatesFetcher.transform_query(
            {"table": "by_characteristic", "category": "Race/ethnicity of households"}
        )
        data = FoodSecurityInTheUnitedStatesFetcher.transform_data(query, records)
        assert [row.period for row in data] == [
            "White non-Hispanic — 2024",
            "Black non-Hispanic — 2024",
        ]

    def test_transform_data_by_state_folds_state_into_period(self):
        """The state table folds the State and keeps the 3-year period verbatim."""
        records = parse_table(STATE_CSV, "by_state")
        query = FoodSecurityInTheUnitedStatesFetcher.transform_query(
            {"table": "by_state"}
        )
        data = FoodSecurityInTheUnitedStatesFetcher.transform_data(query, records)
        assert [row.period for row in data] == [
            "United States — 2006-2008",
            "United States — 2022-2024",
            "CA — 2022-2024",
        ]
        national = data[0].model_dump(by_alias=True)
        assert national["Food insecurity prevalence (percent)"] == 12.2
        assert national["Very low food security margin of error"] == 0.18

    def test_transform_data_category_ignored_for_by_state(self):
        """A category filter does not drop the by-state rows without a category."""
        records = parse_table(STATE_CSV, "by_state")
        query = FoodSecurityInTheUnitedStatesFetcher.transform_query(
            {"table": "by_state", "category": "Race/ethnicity of households"}
        )
        data = FoodSecurityInTheUnitedStatesFetcher.transform_data(query, records)
        assert {row.period for row in data} == {
            "United States — 2006-2008",
            "United States — 2022-2024",
            "CA — 2022-2024",
        }

    def test_transform_data_filters_years(self):
        """start_year and end_year filter rows on the integer sort year."""
        records = parse_table(ALL_HOUSEHOLDS_CSV, "national_trend")
        start = FoodSecurityInTheUnitedStatesFetcher.transform_data(
            FoodSecurityInTheUnitedStatesFetcher.transform_query({"start_year": 2024}),
            records,
        )
        assert [row.period for row in start] == ["2024"]
        end = FoodSecurityInTheUnitedStatesFetcher.transform_data(
            FoodSecurityInTheUnitedStatesFetcher.transform_query({"end_year": 2023}),
            records,
        )
        assert [row.period for row in end] == ["2023"]

    def test_transform_data_sorts_years_chronologically(self):
        """Pivoted rows emit in ascending year order."""
        reversed_csv = (
            'Year,Category,Subcategory,Sub-subcategory,Total,"Food secure-1,000",'
            'Food secure-percent,"Food insecure-1,000",Food insecure-percent,'
            '"Low food security-1,000",Low food security-percent,'
            '"Very low food security-1,000",Very low food security-percent\n'
            "2024,All households,,,134062,115722,86.3,18340,13.7,11138,8.3,7202,5.4\n"
            "2001,All households,,,107824,96303,89.3,11521,10.7,8010,7.4,3511,3.3\n"
        )
        records = parse_table(reversed_csv, "national_trend")
        query = FoodSecurityInTheUnitedStatesFetcher.transform_query({})
        data = FoodSecurityInTheUnitedStatesFetcher.transform_data(query, records)
        assert [row.period for row in data] == ["2001", "2024"]

    def test_transform_data_no_duplicate_rows(self):
        """No two by-characteristic rows share a period or a serialized row."""
        records = parse_table(ALL_HOUSEHOLDS_CSV, "by_characteristic")
        query = FoodSecurityInTheUnitedStatesFetcher.transform_query(
            {"table": "by_characteristic"}
        )
        data = FoodSecurityInTheUnitedStatesFetcher.transform_data(query, records)
        periods = [row.period for row in data]
        dumped = [tuple(sorted(row.model_dump(by_alias=True).items())) for row in data]
        assert len(set(periods)) == len(periods)
        assert len(set(dumped)) == len(dumped)

    def test_param_scoping_options(self):
        """Choice params are single-select with real labels and options."""
        extra = FoodSecurityInTheUnitedStatesQueryParams.__json_schema_extra__
        table = extra["table"]["x-widget_config"]
        assert table["label"] == "Table"
        assert table["multiSelect"] is False
        assert table["multiple"] is False
        assert table["value"] == DEFAULT_TABLE
        assert {opt["value"] for opt in table["options"]} == set(  # ty: ignore[invalid-argument-type, not-subscriptable, not-iterable]
            FOOD_SECURITY_TABLES
        )
        category = extra["category"]["x-widget_config"]
        assert category["type"] == "endpoint"
        assert category["optionsParams"] == {"table": "$table"}
        assert category["multiSelect"] is False

    def test_widget_config_and_period_header(self):
        """The whole-widget config and the pinned period header are populated."""
        widget = FoodSecurityInTheUnitedStatesData.model_config["json_schema_extra"][  # ty: ignore[not-subscriptable]
            "x-widget_config"
        ]
        assert widget["$.name"] == "USDA ERS Food Security in the United States"
        assert widget["$.category"] == "Economy"
        assert widget["$.subCategory"] == "Agriculture"
        assert widget["$.source"] == ["USDA", "ERS"]
        period = FoodSecurityInTheUnitedStatesData.model_fields["period"]
        assert period.json_schema_extra["x-widget_config"]["pinned"] == "left"

    def test_null_token_mixin_coerces_value_column(self):
        """The Data model coerces placeholder tokens in value columns to None."""
        row = FoodSecurityInTheUnitedStatesData.model_validate(
            {"period": "CA — 2006-2008", "Food secure (percent)": "--"}
        )
        dumped = row.model_dump(by_alias=True)
        assert dumped["period"] == "CA — 2006-2008"
        assert dumped["Food secure (percent)"] is None
