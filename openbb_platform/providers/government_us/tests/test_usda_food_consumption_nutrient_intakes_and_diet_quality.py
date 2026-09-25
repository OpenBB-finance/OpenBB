"""Tests for the USDA ERS food consumption, nutrient intakes, and diet quality utils and model."""

import asyncio

import pytest
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.utils.errors import EmptyDataError

from openbb_government_us.usda.models.food_consumption_nutrient_intakes_and_diet_quality import (
    FoodConsumptionNutrientIntakesAndDietQualityData,
    FoodConsumptionNutrientIntakesAndDietQualityFetcher,
    FoodConsumptionNutrientIntakesAndDietQualityQueryParams,
    _cycle_year,
    _source_index,
)
from openbb_government_us.usda.utils import (
    ers_food_consumption_nutrient_intakes_and_diet_quality as util,
)
from openbb_government_us.usda.utils.ers_food_consumption_nutrient_intakes_and_diet_quality import (
    DEFAULT_DEMOGRAPHIC,
    DEFAULT_STATISTIC,
    DEFAULT_TABLE,
    DEMOGRAPHICS,
    RECOMMENDED_COLUMN_ORDER,
    STATISTIC_CHOICES,
    TABLE_FILES,
    TABLE_LABELS,
    item_column,
    normalize_unit,
    parse_intake,
    parse_recommended,
    parse_sample_sizes,
    parse_table,
    split_cycle_variable,
    to_number,
    to_number_or_text,
)

TABLE1_CSV = (
    "Demographics,Survey years,Sample size,Table\n"
    "U.S. aged 2 and above,1977-1978,41471,Table 1-Sample sizes\n"
    "U.S. aged 2 and above,2017-2018,7121,Table 1-Sample sizes\n"
    "Male,1977-1978,18303,Table 1-Sample sizes\n"
    "Male,2017-2018,3481,Table 1-Sample sizes\n"
    "Adult education: less than high school,1977-1978,,Table 1-Sample sizes\n"
    "Adult education: less than high school,2017-2018,1200,Table 1-Sample sizes\n"
)

TABLE2_CSV = (
    "Nutrient,Food source,Measurement,Nutrient:Food source,"
    "Survey years:Variable,Value,Table,Demographics\n"
    "Energy ,Total,Calories,Energy :Total,1977-1978-Mean,1806.88,Table 2,"
    "US consumers aged 2 and above\n"
    "Energy ,FAH,Calories ,Energy :FAH,1977-1978-Mean,1462.27,Table 2,"
    "US consumers aged 2 and above\n"
    "Energy ,Total,Calories,Energy :Total,2017-2018-Mean,2093.14,Table 2,"
    "US consumers aged 2 and above\n"
    "Energy ,FAH,Calories,Energy :FAH,2017-2018-Mean,1402.55,Table 2,"
    "US consumers aged 2 and above\n"
    "Protein,Total,Grams,Protein:Total,1977-1978-Mean,78.25,Table 2,"
    "US consumers aged 2 and above\n"
    "Protein,Total,Grams,Protein:Total,2017-2018-Mean,78.28,Table 2,"
    "US consumers aged 2 and above\n"
    "Total Fat ,Total,,Total Fat :Total,1977-1978-Mean,63.4,Table 2,"
    "US consumers aged 2 and above\n"
    "Total Fat ,Total,Grams,Total Fat :Total,2017-2018-Mean,70.0,Table 2,"
    "US consumers aged 2 and above\n"
    "Energy ,Total,Calories,Energy :Total,1977-1978-SE of mean,12.39,Table 2,"
    "US consumers aged 2 and above\n"
    "Energy ,Total,Calories,Energy :Total,2017-2018-Mean,9999,Table 2,Sex - Males\n"
    "Iron ,Total,Milligrams,Iron :Total,1977-1978-Mean,,Table 2,"
    "US consumers aged 2 and above\n"
)

TABLE5_CSV = (
    "Food group,Food source,Measurement,Food group:Food source,"
    "Survey years:Variable,Value,Table,Demographics\n"
    "Added sugars ,Total,Teaspoons,Added sugars:Total,1977-1998-Mean,15.0,Table 5,"
    "US consumers aged 2 and above\n"
)

TABLE4_CSV = (
    "Nutrient,Food source,Measurement,Nutrient:Food source,"
    "Survey years:Variable,Value,Table,Demographics\n"
    'Sodium,FAH,"Grams per 1,000",Sodium:FAH,1977-1978-Mean,"42,91",Table 4,'
    "US consumers aged 2 and above\n"
)

TABLE8_CSV = (
    "Nutrient or Food group,Variable,Value,Table\n"
    'Fiber (g),"Recommended density*:Nutrient or food group amount per 1,000'
    ' calories",14,Table 8\n'
    'Fiber (g),"2017-2018 Actual density-Total-Nutrient or food group amount per'
    ' 1,000 calories ",8.05,Table 8\n'
    'Fiber (g),"2017-2018 density as a ratio of the recommended density-Total-Ratio'
    ' of actual density to the recommended density",0.575,Table 8\n'
    'Total fats (percent of calories)**,"Recommended density*:Nutrient or food group'
    ' amount per 1,000 calories",20-35,Table 8\n'
    "Fiber (g),Some unmapped variable,999,Table 8\n"
)


def intake_record(**overrides) -> dict:
    """Build a parsed intake record with optional field overrides."""
    record = {
        "item": "Energy",
        "food_source": "Total",
        "units": "Calories",
        "demographics": "US consumers aged 2 and above",
        "statistic": "Mean",
        "cycle": "1977-1978",
        "value": 1806.88,
        "order": 0,
    }
    record.update(overrides)
    return record


class TestErsFoodConsumptionUtils:
    """Tests for the ers_food_consumption_nutrient_intakes_and_diet_quality utils."""

    def test_catalog_contents(self):
        """The catalog holds eight tables with unique media paths and labels."""
        assert len(TABLE_FILES) == 8
        assert set(TABLE_FILES) == set(TABLE_LABELS)
        assert len(set(TABLE_FILES.values())) == 8
        assert TABLE_FILES["2_nutrient_intake"].startswith("/media/5465/")
        assert TABLE_FILES["8_recommended_vs_actual_density"].startswith("/media/5477/")

    def test_catalog_dimensions(self):
        """The dimension constants match the published survey design."""
        assert util.DEFAULT_TABLE == "2_nutrient_intake"
        assert len(util.SURVEY_CYCLES) == 11
        assert util.SURVEY_CYCLES[0] == "1977-1978"
        assert util.SURVEY_CYCLES[-1] == "2017-2018"
        assert len(util.FOOD_SOURCES) == 7
        assert len(DEMOGRAPHICS) == 20
        assert DEFAULT_DEMOGRAPHIC in DEMOGRAPHICS
        assert set(STATISTIC_CHOICES) == {"mean", "se_of_mean"}
        assert len(RECOMMENDED_COLUMN_ORDER) == 13
        assert RECOMMENDED_COLUMN_ORDER[0] == "Recommended"

    def test_item_column(self):
        """Nutrient tables key on 'Nutrient', food-group tables on 'Food group'."""
        assert item_column("2_nutrient_intake") == "Nutrient"
        assert item_column("4_nutrient_density") == "Nutrient"
        assert item_column("5_food_group_intake") == "Food group"
        assert item_column("7_food_group_density") == "Food group"

    def test_normalize_unit(self):
        """Units strip whitespace, map the truncated variant, and blank to None."""
        assert normalize_unit("Calories ") == "Calories"
        assert normalize_unit("Grams per 1,000") == "Grams per 1,000 calories"
        assert normalize_unit("Percent of total") == "Percent of total"
        assert normalize_unit("") is None
        assert normalize_unit(None) is None

    def test_split_cycle_variable(self):
        """The cycle splits from the statistic on the last hyphen."""
        assert split_cycle_variable("1977-1978-Mean") == ("1977-1978", "Mean")
        assert split_cycle_variable("2017-2018-SE of mean") == (
            "2017-2018",
            "SE of mean",
        )
        assert split_cycle_variable("") == ("", "")

    def test_to_number(self):
        """Numeric cells parse to float; blank and corrupted cells return None."""
        assert to_number("1806.88") == 1806.88
        assert to_number("") is None
        assert to_number(None) is None
        assert to_number("42,91") is None
        assert to_number("3+L:T.36") is None

    def test_to_number_or_text(self):
        """Numeric cells parse to float; a range stays text; blank returns None."""
        assert to_number_or_text("14") == 14.0
        assert to_number_or_text("20-35") == "20-35"
        assert to_number_or_text("") is None
        assert to_number_or_text(None) is None

    def test_parse_sample_sizes(self):
        """Table 1 rows parse to subgroup/cycle records, blanks to None."""
        records = parse_sample_sizes(TABLE1_CSV)
        assert len(records) == 6
        assert records[0] == {
            "demographic": "U.S. aged 2 and above",
            "cycle": "1977-1978",
            "value": 41471,
            "order": 0,
        }
        blank = next(r for r in records if r["value"] is None)
        assert blank["demographic"] == "Adult education: less than high school"

    def test_parse_intake_nutrient(self):
        """Table 2 rows parse with stripped item, unit, split cycle and statistic."""
        records = parse_intake(TABLE2_CSV, "2_nutrient_intake")
        assert len(records) == 11
        first = records[0]
        assert first["item"] == "Energy"
        assert first["food_source"] == "Total"
        assert first["units"] == "Calories"
        assert first["statistic"] == "Mean"
        assert first["cycle"] == "1977-1978"
        assert first["value"] == 1806.88
        assert records[1]["units"] == "Calories"
        se = next(r for r in records if r["statistic"] == "SE of mean")
        assert se["value"] == 12.39
        blank = next(r for r in records if r["value"] is None)
        assert blank["item"] == "Iron"
        empty_unit = next(
            r for r in records if r["item"] == "Total Fat" and r["units"] is None
        )
        assert empty_unit["cycle"] == "1977-1978"

    def test_parse_intake_food_group(self):
        """Table 5 rows parse on the 'Food group' column."""
        records = parse_intake(TABLE5_CSV, "5_food_group_intake")
        assert len(records) == 1
        assert records[0]["item"] == "Added sugars"
        assert records[0]["units"] == "Teaspoons"

    def test_parse_intake_corrupted_value(self):
        """A comma-decimal source cell coerces to None and the unit normalizes."""
        records = parse_intake(TABLE4_CSV, "4_nutrient_density")
        assert len(records) == 1
        assert records[0]["value"] is None
        assert records[0]["units"] == "Grams per 1,000 calories"

    def test_parse_recommended(self):
        """Table 8 rows map to wide columns, skip unmapped, keep the text range."""
        records = parse_recommended(TABLE8_CSV)
        columns = [r["column"] for r in records]
        assert "Recommended" in columns
        assert "Actual: Total" in columns
        assert "Ratio: Total" in columns
        assert len(records) == 4
        text_row = next(r for r in records if r["value"] == "20-35")
        assert text_row["item"] == "Total fats (percent of calories)**"

    def test_parse_table_dispatch(self):
        """parse_table routes each table key to its parser."""
        assert parse_table(TABLE1_CSV, "1_sample_sizes")[0]["demographic"] == (
            "U.S. aged 2 and above"
        )
        assert parse_table(TABLE2_CSV, "2_nutrient_intake")[0]["item"] == "Energy"
        assert (
            parse_table(TABLE8_CSV, "8_recommended_vs_actual_density")[0]["column"]
            == "Recommended"
        )

    def test_afetch_table(self, monkeypatch):
        """afetch_table fetches the table's media path through the ERS cache."""
        calls = []

        async def fake_afetch_ers_file(media_path, product=None, ttl=None):
            calls.append((media_path, product))
            return TABLE2_CSV.encode("utf-8-sig")

        monkeypatch.setattr(
            "openbb_government_us.usda.utils.ers_client.afetch_ers_file",
            fake_afetch_ers_file,
        )
        records = asyncio.run(util.afetch_table("2_nutrient_intake"))
        assert calls == [(TABLE_FILES["2_nutrient_intake"], util.PRODUCT_PAGE)]
        assert records[0]["item"] == "Energy"


class TestFoodConsumptionNutrientIntakesAndDietQuality:
    """Tests for the FoodConsumptionNutrientIntakesAndDietQuality model."""

    def test_transform_query(self):
        """transform_query builds the query params model."""
        query = FoodConsumptionNutrientIntakesAndDietQualityFetcher.transform_query(
            {"table": "3_nutrient_intake_share", "statistic": "se_of_mean"}
        )
        assert isinstance(
            query, FoodConsumptionNutrientIntakesAndDietQualityQueryParams
        )
        assert query.table == "3_nutrient_intake_share"
        assert query.statistic == "se_of_mean"

    def test_defaults(self):
        """The query defaults to the nutrient-intake table, US 2+, and the mean."""
        query = FoodConsumptionNutrientIntakesAndDietQualityQueryParams()
        assert query.table == DEFAULT_TABLE
        assert query.demographics == DEFAULT_DEMOGRAPHIC
        assert query.statistic == DEFAULT_STATISTIC

    def test_table_validation(self):
        """Table normalizes lists and blanks, and rejects unknown keys."""
        assert (
            FoodConsumptionNutrientIntakesAndDietQualityQueryParams(
                table=["1_sample_sizes"]
            ).table
            == "1_sample_sizes"
        )
        assert (
            FoodConsumptionNutrientIntakesAndDietQualityQueryParams(table="").table
            == DEFAULT_TABLE
        )
        with pytest.raises(OpenBBError, match="Invalid table: bogus"):
            FoodConsumptionNutrientIntakesAndDietQualityQueryParams(table="bogus")

    def test_demographics_validation(self):
        """Demographics normalizes lists and blanks, and rejects unknown labels."""
        assert (
            FoodConsumptionNutrientIntakesAndDietQualityQueryParams(
                demographics=["Sex - Males"]
            ).demographics
            == "Sex - Males"
        )
        assert (
            FoodConsumptionNutrientIntakesAndDietQualityQueryParams(
                demographics=""
            ).demographics
            == DEFAULT_DEMOGRAPHIC
        )
        with pytest.raises(OpenBBError, match="Invalid demographics: Martians"):
            FoodConsumptionNutrientIntakesAndDietQualityQueryParams(
                demographics="Martians"
            )

    def test_statistic_validation(self):
        """Statistic normalizes lists and blanks, and rejects unknown slugs."""
        assert (
            FoodConsumptionNutrientIntakesAndDietQualityQueryParams(
                statistic=["se_of_mean"]
            ).statistic
            == "se_of_mean"
        )
        assert (
            FoodConsumptionNutrientIntakesAndDietQualityQueryParams(
                statistic=""
            ).statistic
            == DEFAULT_STATISTIC
        )
        with pytest.raises(OpenBBError, match="Invalid statistic: median"):
            FoodConsumptionNutrientIntakesAndDietQualityQueryParams(statistic="median")

    def test_aextract_data(self, monkeypatch):
        """aextract_data fetches the selected table's media path."""
        calls = []

        async def fake_afetch_ers_file(media_path, product=None, ttl=None):
            calls.append((media_path, product))
            return TABLE1_CSV.encode("utf-8-sig")

        monkeypatch.setattr(
            "openbb_government_us.usda.utils.ers_client.afetch_ers_file",
            fake_afetch_ers_file,
        )
        query = FoodConsumptionNutrientIntakesAndDietQualityFetcher.transform_query(
            {"table": "1_sample_sizes"}
        )
        records = asyncio.run(
            FoodConsumptionNutrientIntakesAndDietQualityFetcher.aextract_data(
                query, None
            )
        )
        assert calls == [(TABLE_FILES["1_sample_sizes"], util.PRODUCT_PAGE)]
        assert records[0]["demographic"] == "U.S. aged 2 and above"

    def test_helpers(self):
        """The cycle-year and food-source helpers cover their branches."""
        assert _cycle_year("1977-1978") == 1977
        assert _cycle_year("bad") is None
        assert _source_index("FAH") == 1
        assert _source_index(None) == 0

    def test_transform_intake_pivots_cycles(self):
        """Table 2 pivots the mean into chronological survey-cycle columns."""
        records = parse_intake(TABLE2_CSV, "2_nutrient_intake")
        query = FoodConsumptionNutrientIntakesAndDietQualityFetcher.transform_query({})
        data = FoodConsumptionNutrientIntakesAndDietQualityFetcher.transform_data(
            query, records
        )
        served = list(data[0].model_dump(by_alias=True))
        assert served[:3] == ["item", "food_source", "units"]
        assert served[3:] == ["1977-1978", "2017-2018"]
        energy_total = data[0].model_dump(by_alias=True)
        assert energy_total["item"] == "Energy — Total"
        assert energy_total["food_source"] == "Total"
        assert energy_total["1977-1978"] == 1806.88
        assert energy_total["2017-2018"] == 2093.14

    def test_transform_intake_orders_item_then_source(self):
        """Rows sort by item, then by published food-source order."""
        records = parse_intake(TABLE2_CSV, "2_nutrient_intake")
        query = FoodConsumptionNutrientIntakesAndDietQualityFetcher.transform_query({})
        data = FoodConsumptionNutrientIntakesAndDietQualityFetcher.transform_data(
            query, records
        )
        order = [(row.item, row.food_source) for row in data]
        assert order == [
            ("Energy — Total", "Total"),
            ("Energy — FAH", "FAH"),
            ("Protein — Total", "Total"),
            ("Total Fat — Total", "Total"),
            ("Iron — Total", "Total"),
        ]

    def test_transform_intake_filters_statistic_and_demographic(self):
        """Only the selected statistic and demographic survive the pivot."""
        records = parse_intake(TABLE2_CSV, "2_nutrient_intake")
        query = FoodConsumptionNutrientIntakesAndDietQualityFetcher.transform_query({})
        data = FoodConsumptionNutrientIntakesAndDietQualityFetcher.transform_data(
            query, records
        )
        for row in data:
            dumped = row.model_dump(by_alias=True)
            assert dumped.get("1977-1978") != 12.39
            assert dumped.get("1977-1978") != 9999

    def test_transform_intake_end_year_and_bad_cycle(self):
        """end_year drops later cycles and a malformed cycle is skipped."""
        records = [
            intake_record(cycle="1977-1978", value=1.0, order=0),
            intake_record(cycle="2017-2018", value=2.0, order=1),
            intake_record(cycle="Unknown", value=3.0, order=2),
        ]
        query = FoodConsumptionNutrientIntakesAndDietQualityFetcher.transform_query(
            {"end_year": 1990}
        )
        data = FoodConsumptionNutrientIntakesAndDietQualityFetcher.transform_data(
            query, records
        )
        served = list(data[0].model_dump(by_alias=True))
        assert "1977-1978" in served
        assert "2017-2018" not in served
        assert "Unknown" not in served

    def test_transform_sample_end_year_and_bad_cycle(self):
        """Table 1 end_year drops later cycles and a malformed cycle is skipped."""
        records = [
            {"demographic": "Male", "cycle": "1977-1978", "value": 100, "order": 0},
            {"demographic": "Male", "cycle": "2017-2018", "value": 200, "order": 1},
            {"demographic": "Male", "cycle": "Unknown", "value": 300, "order": 2},
        ]
        query = FoodConsumptionNutrientIntakesAndDietQualityFetcher.transform_query(
            {"table": "1_sample_sizes", "end_year": 1990}
        )
        data = FoodConsumptionNutrientIntakesAndDietQualityFetcher.transform_data(
            query, records
        )
        served = list(data[0].model_dump(by_alias=True))
        assert "1977-1978" in served
        assert "2017-2018" not in served
        assert "Unknown" not in served

    def test_transform_intake_resolves_unit(self):
        """A row whose first cycle has a blank unit takes a later cycle's unit."""
        records = parse_intake(TABLE2_CSV, "2_nutrient_intake")
        query = FoodConsumptionNutrientIntakesAndDietQualityFetcher.transform_query({})
        data = FoodConsumptionNutrientIntakesAndDietQualityFetcher.transform_data(
            query, records
        )
        total_fat = next(row for row in data if row.item == "Total Fat — Total")
        assert total_fat.units == "Grams"

    def test_transform_intake_year_filter(self):
        """start_year and end_year select which survey cycles appear."""
        records = parse_intake(TABLE2_CSV, "2_nutrient_intake")
        query = FoodConsumptionNutrientIntakesAndDietQualityFetcher.transform_query(
            {"start_year": 2000}
        )
        data = FoodConsumptionNutrientIntakesAndDietQualityFetcher.transform_data(
            query, records
        )
        served = list(data[0].model_dump(by_alias=True))
        assert "1977-1978" not in served
        assert "2017-2018" in served

    def test_transform_intake_empty_raises(self):
        """A demographic with no rows raises EmptyDataError."""
        records = parse_intake(TABLE2_CSV, "2_nutrient_intake")
        query = FoodConsumptionNutrientIntakesAndDietQualityFetcher.transform_query(
            {"demographics": "Ages 65 and above"}
        )
        with pytest.raises(EmptyDataError, match="No records match"):
            FoodConsumptionNutrientIntakesAndDietQualityFetcher.transform_data(
                query, records
            )

    def test_transform_sample(self):
        """Table 1 pivots one row per subgroup with cycle columns."""
        records = parse_sample_sizes(TABLE1_CSV)
        query = FoodConsumptionNutrientIntakesAndDietQualityFetcher.transform_query(
            {"table": "1_sample_sizes"}
        )
        data = FoodConsumptionNutrientIntakesAndDietQualityFetcher.transform_data(
            query, records
        )
        assert [row.item for row in data] == [
            "U.S. aged 2 and above",
            "Male",
            "Adult education: less than high school",
        ]
        first = data[0].model_dump(by_alias=True)
        assert first["1977-1978"] == 41471
        assert first["food_source"] is None
        assert first["units"] is None

    def test_transform_sample_year_filter_empty_raises(self):
        """Filtering Table 1 past its range raises EmptyDataError."""
        records = parse_sample_sizes(TABLE1_CSV)
        query = FoodConsumptionNutrientIntakesAndDietQualityFetcher.transform_query(
            {"table": "1_sample_sizes", "start_year": 2100}
        )
        with pytest.raises(EmptyDataError, match="No records match"):
            FoodConsumptionNutrientIntakesAndDietQualityFetcher.transform_data(
                query, records
            )

    def test_transform_recommended(self):
        """Table 8 pivots the 13 fixed columns and keeps the text range."""
        records = parse_recommended(TABLE8_CSV)
        query = FoodConsumptionNutrientIntakesAndDietQualityFetcher.transform_query(
            {"table": "8_recommended_vs_actual_density"}
        )
        data = FoodConsumptionNutrientIntakesAndDietQualityFetcher.transform_data(
            query, records
        )
        served = list(data[0].model_dump(by_alias=True))
        assert served[:3] == ["item", "food_source", "units"]
        assert served[3:] == list(RECOMMENDED_COLUMN_ORDER)
        fiber = data[0].model_dump(by_alias=True)
        assert fiber["item"] == "Fiber (g)"
        assert fiber["Recommended"] == 14.0
        assert fiber["Actual: Total"] == 8.05
        total_fats = next(row for row in data if row.item.startswith("Total fats"))
        assert total_fats.model_dump(by_alias=True)["Recommended"] == "20-35"

    def test_transform_recommended_empty_raises(self):
        """Table 8 with no mapped rows raises EmptyDataError."""
        query = FoodConsumptionNutrientIntakesAndDietQualityFetcher.transform_query(
            {"table": "8_recommended_vs_actual_density"}
        )
        with pytest.raises(EmptyDataError, match="No records match"):
            FoodConsumptionNutrientIntakesAndDietQualityFetcher.transform_data(
                query, []
            )

    def test_columns_defs_bind_to_served_keys(self):
        """Every non-excluded field binds to a served key; dynamics are non-constant."""
        records = parse_intake(TABLE2_CSV, "2_nutrient_intake")
        query = FoodConsumptionNutrientIntakesAndDietQualityFetcher.transform_query({})
        data = FoodConsumptionNutrientIntakesAndDietQualityFetcher.transform_data(
            query, records
        )
        served = set(data[0].model_dump(by_alias=True))
        fields = FoodConsumptionNutrientIntakesAndDietQualityData.model_fields
        for name, field in fields.items():
            extra = (field.json_schema_extra or {}).get("x-widget_config", {})
            if extra.get("exclude"):
                continue
            assert name in served
        dynamic = served - set(fields)
        assert dynamic == {"1977-1978", "2017-2018"}
        for key in dynamic:
            values = {row.model_dump(by_alias=True).get(key) for row in data}
            assert len(values) > 1

    def test_widget_options(self):
        """The choice params expose single-select options with defaults."""
        extra = FoodConsumptionNutrientIntakesAndDietQualityQueryParams.__json_schema_extra__
        table = extra["table"]["x-widget_config"]
        assert table["multiSelect"] is False
        assert table["multiple"] is False
        assert table["value"] == DEFAULT_TABLE
        assert len(table["options"]) == 8
        assert len(extra["demographics"]["x-widget_config"]["options"]) == 20
        assert len(extra["statistic"]["x-widget_config"]["options"]) == 2

    def test_widget_model_config(self):
        """The whole-widget config carries the name, category, and source."""
        config = FoodConsumptionNutrientIntakesAndDietQualityData.model_config[
            "json_schema_extra"
        ]["x-widget_config"]
        assert config["$.name"].startswith("USDA ERS Food Consumption")
        assert config["$.category"] == "Economy"
        assert config["$.subCategory"] == "Agriculture"
        assert config["$.source"] == ["USDA", "ERS"]
