"""Tests for the USDA ERS international macroeconomic data set utils and model."""

import asyncio

import pytest
from openbb_core.app.model.abstract.error import OpenBBError
from pydantic.alias_generators import to_snake

from openbb_government_us.usda.models.international_macroeconomic_data_set import (
    InternationalMacroeconomicDataSetData,
    InternationalMacroeconomicDataSetFetcher,
    InternationalMacroeconomicDataSetQueryParams,
)
from openbb_government_us.usda.utils import ers_international_macroeconomic_data_set
from openbb_government_us.usda.utils.ers_international_macroeconomic_data_set import (
    DEFAULT_MEASURE,
    DEFAULT_VARIABLE,
    INTERNATIONAL_MACRO_FILES,
    MEASURES,
    PRODUCT_PAGE,
    is_growth_unit,
    parse_rows,
    repair_mojibake,
)

FIXTURE_GDP = (
    "Observation,Year,Unit,Value\n"
    "United States,1970,Real GDP USD,5316.391060\n"
    "United States,1971,Real GDP USD,5400.123456\n"
    "United States,1990,Real GDP USD,10054.715526\n"
    "China,1970,Real GDP USD,226.0042\n"
    "China,1971,Real GDP USD,230.5\n"
    "China,1990,Real GDP USD,1000.5597\n"
    "World,1970,Real GDP USD,NA\n"
    "World,1971,Real GDP USD,NA\n"
    "World,1990,Real GDP USD,37004.552065\n"
    "United States,1970,Real GDP USD Percent Change year to year,NA\n"
    "United States,1971,Real GDP USD Percent Change year to year,1.579\n"
    "China,1971,Real GDP USD Percent Change year to year,1.991\n"
    "World,1971,Real GDP USD Percent Change year to year,-0.5\n"
    ",,,\n"
    "United States,means,Real GDP USD,999.0\n"
    "United States,1972,Real GDP USD,foo\n"
)

FIXTURE_EXCHANGE = (
    "Observation,Year,Unit,Value\n"
    "United States,1970,"
    '"US Ag. Trade Weighted Exchange Rate, 2017=100",100.0\n'
    '"US Ag. Trade Weighted Exchange Rate, 2017=100",1970,'
    '"US Ag. Trade Weighted Exchange Rate, 2017=100",68.258272\n'
)

FIXTURE_POPULATION = (
    "Observation,Year,Unit,Value\n"
    "United States,1970,Population,205052174.0\n"
    "CÃ´te d'Ivoire,1970,Population,5000000\n"
    ",,,\n"
    ",,,\n"
)


class TestErsInternationalMacroeconomicDataSetUtils:
    """Tests for the ers_international_macroeconomic_data_set utils module."""

    def test_catalog(self):
        """The catalog holds the seven variable files with their media paths."""
        assert list(INTERNATIONAL_MACRO_FILES) == [
            "real_gdp",
            "real_gdp_per_capita",
            "gdp_deflator",
            "real_gdp_shares",
            "real_exchange_rate",
            "cpi",
            "population",
        ]
        assert INTERNATIONAL_MACRO_FILES["real_gdp"]["media"].startswith("/media/6157/")
        assert INTERNATIONAL_MACRO_FILES["population"]["media"].startswith(
            "/media/6169/"
        )
        assert INTERNATIONAL_MACRO_FILES["population"]["mojibake"] is True
        assert INTERNATIONAL_MACRO_FILES["real_gdp"]["mojibake"] is False
        assert PRODUCT_PAGE == "data-products/international-macroeconomic-data-set"

    def test_is_growth_unit(self):
        """The growth marker classifies percent-change units."""
        assert is_growth_unit("Real GDP USD Percent Change year to year") is True
        assert is_growth_unit("Real GDP USD") is False
        assert is_growth_unit("Population") is False

    def test_repair_mojibake(self):
        """Double-encoded labels repair; clean and undecodable labels pass."""
        assert repair_mojibake("CÃ´te d'Ivoire") == "Côte d'Ivoire"
        assert repair_mojibake("SÃ£o TomÃ© and Principe") == "São Tomé and Principe"
        assert repair_mojibake("United States") == "United States"
        assert repair_mojibake("Côte d'Ivoire") == "Côte d'Ivoire"

    def test_parse_rows_skips_blank_nonyear_null_and_nonnumeric(self):
        """Blank padding, non-year, null-token, and non-numeric rows are dropped."""
        records = parse_rows(FIXTURE_GDP)
        assert all(isinstance(record["year"], int) for record in records)
        assert all(record["value"] is not None for record in records)
        us_years = {
            record["year"]
            for record in records
            if record["observation"] == "United States"
            and record["unit"] == "Real GDP USD"
        }
        assert us_years == {1970, 1971, 1990}
        world_level_years = {
            record["year"]
            for record in records
            if record["observation"] == "World" and record["unit"] == "Real GDP USD"
        }
        assert world_level_years == {1990}

    def test_parse_rows_types_and_values(self):
        """Parsed records carry stripped strings, int years, and full floats."""
        records = parse_rows(FIXTURE_GDP)
        record = next(
            record
            for record in records
            if record["observation"] == "United States"
            and record["unit"] == "Real GDP USD"
            and record["year"] == 1970
        )
        assert record == {
            "observation": "United States",
            "year": 1970,
            "unit": "Real GDP USD",
            "value": 5316.391060,
        }

    def test_parse_rows_relabels_exchange_observation(self):
        """The self-named exchange-rate observation gets a clean column label."""
        records = parse_rows(FIXTURE_EXCHANGE)
        observations = {record["observation"] for record in records}
        assert observations == {"United States", "US Ag. Trade Weighted"}

    def test_parse_rows_repairs_population_mojibake(self):
        """Population observation labels repair when the mojibake flag is set."""
        records = parse_rows(FIXTURE_POPULATION, mojibake=True)
        observations = {record["observation"] for record in records}
        assert observations == {"United States", "Côte d'Ivoire"}
        assert len(records) == 2

    def test_afetch_records(self, monkeypatch):
        """afetch_records fetches the variable's CSV and parses it, per mojibake."""
        calls = []

        async def fake_afetch_ers_file(media_path, product=None, ttl=None):
            calls.append((media_path, product))
            return FIXTURE_POPULATION.encode("utf-8")

        monkeypatch.setattr(
            "openbb_government_us.usda.utils.ers_client.afetch_ers_file",
            fake_afetch_ers_file,
        )
        records = asyncio.run(
            ers_international_macroeconomic_data_set.afetch_records("population")
        )
        assert calls == [
            (INTERNATIONAL_MACRO_FILES["population"]["media"], PRODUCT_PAGE)
        ]
        assert {record["observation"] for record in records} == {
            "United States",
            "Côte d'Ivoire",
        }


class TestInternationalMacroeconomicDataSet:
    """Tests for the InternationalMacroeconomicDataSet model."""

    def _records(self):
        """Parse the GDP fixture into long records."""
        return parse_rows(FIXTURE_GDP)

    def test_transform_query_defaults(self):
        """transform_query applies the variable and measure defaults."""
        query = InternationalMacroeconomicDataSetFetcher.transform_query({})
        assert isinstance(query, InternationalMacroeconomicDataSetQueryParams)
        assert query.variable == DEFAULT_VARIABLE
        assert query.measure == DEFAULT_MEASURE
        assert query.start_year is None
        assert query.end_year is None

    def test_blank_values_fall_back_to_defaults(self):
        """Blank variable and measure normalize to their defaults."""
        query = InternationalMacroeconomicDataSetQueryParams(variable="", measure="")
        assert query.variable == DEFAULT_VARIABLE
        assert query.measure == DEFAULT_MEASURE

    def test_invalid_variable_and_measure_raise(self):
        """Unknown variable or measure raise OpenBBError."""
        with pytest.raises(OpenBBError, match="Invalid variable: bogus"):
            InternationalMacroeconomicDataSetQueryParams(variable="bogus")
        with pytest.raises(OpenBBError, match="Invalid measure: bogus"):
            InternationalMacroeconomicDataSetQueryParams(measure="bogus")

    def test_variable_accepts_valid_value(self):
        """A valid non-default variable passes validation unchanged."""
        query = InternationalMacroeconomicDataSetQueryParams(variable="population")
        assert query.variable == "population"

    def test_aextract_data_returns_records(self, monkeypatch):
        """aextract_data returns the parsed variable records."""

        async def fake_afetch_records(variable):
            assert variable == DEFAULT_VARIABLE
            return parse_rows(FIXTURE_GDP)

        monkeypatch.setattr(
            ers_international_macroeconomic_data_set,
            "afetch_records",
            fake_afetch_records,
        )
        query = InternationalMacroeconomicDataSetFetcher.transform_query({})
        records = asyncio.run(
            InternationalMacroeconomicDataSetFetcher.aextract_data(query, None)
        )
        assert any(record["observation"] == "China" for record in records)

    def test_level_pivot(self):
        """The level table spreads countries into columns by ascending year."""
        query = InternationalMacroeconomicDataSetFetcher.transform_query({})
        data = InternationalMacroeconomicDataSetFetcher.transform_data(
            query, self._records()
        )
        assert [row.year for row in data] == [1970, 1971, 1990]
        first = data[0].model_dump(by_alias=True)
        assert first["United States"] == 5316.391060
        assert first["China"] == 226.0042
        assert first["World"] is None
        assert first["unit"] == "Real GDP USD"
        last = data[2].model_dump(by_alias=True)
        assert last["World"] == 37004.552065

    def test_level_column_order(self):
        """Level columns follow year, unit, then first-seen observation order."""
        query = InternationalMacroeconomicDataSetFetcher.transform_query({})
        data = InternationalMacroeconomicDataSetFetcher.transform_data(
            query, self._records()
        )
        keys = list(data[0].model_dump(by_alias=True))
        assert keys[:2] == ["year", "unit"]
        assert keys[2:] == ["United States", "China", "World"]

    def test_growth_pivot_starts_after_base_year(self):
        """The growth table drops the all-null base year and allows negatives."""
        query = InternationalMacroeconomicDataSetFetcher.transform_query(
            {"measure": "growth"}
        )
        data = InternationalMacroeconomicDataSetFetcher.transform_data(
            query, self._records()
        )
        assert [row.year for row in data] == [1971]
        row = data[0].model_dump(by_alias=True)
        assert row["United States"] == 1.579
        assert row["China"] == 1.991
        assert row["World"] == -0.5
        assert row["unit"] == "Real GDP USD Percent Change year to year"

    def test_year_filters(self):
        """start_year and end_year filter the emitted year rows."""
        start = InternationalMacroeconomicDataSetFetcher.transform_data(
            InternationalMacroeconomicDataSetFetcher.transform_query(
                {"start_year": 1990}
            ),
            self._records(),
        )
        assert [row.year for row in start] == [1990]
        end = InternationalMacroeconomicDataSetFetcher.transform_data(
            InternationalMacroeconomicDataSetFetcher.transform_query(
                {"end_year": 1971}
            ),
            self._records(),
        )
        assert [row.year for row in end] == [1970, 1971]

    def test_exchange_relabel_pivot(self):
        """The exchange table pivots the relabeled self-named observation."""
        query = InternationalMacroeconomicDataSetFetcher.transform_query({})
        data = InternationalMacroeconomicDataSetFetcher.transform_data(
            query, parse_rows(FIXTURE_EXCHANGE)
        )
        row = data[0].model_dump(by_alias=True)
        assert row["United States"] == 100.0
        assert row["US Ag. Trade Weighted"] == 68.258272

    def test_columns_defs_bind_to_served_keys(self):
        """Every declared column definition binds to a served record key."""
        declared = set()
        for name, field in InternationalMacroeconomicDataSetData.model_fields.items():
            alias = field.serialization_alias or name
            extra = field.json_schema_extra
            config = extra.get("x-widget_config", {}) if isinstance(extra, dict) else {}
            if config.get("exclude"):
                continue
            declared.add(to_snake(alias))
        query = InternationalMacroeconomicDataSetFetcher.transform_query({})
        data = InternationalMacroeconomicDataSetFetcher.transform_data(
            query, self._records()
        )
        served = set()
        for row in data:
            served.update(row.model_dump(by_alias=True))
        assert declared <= served

    def test_undeclared_served_keys_vary(self):
        """Served keys without a column definition are dynamic, not constant."""
        declared = set()
        for name, field in InternationalMacroeconomicDataSetData.model_fields.items():
            alias = field.serialization_alias or name
            declared.add(to_snake(alias))
        query = InternationalMacroeconomicDataSetFetcher.transform_query({})
        data = InternationalMacroeconomicDataSetFetcher.transform_data(
            query, self._records()
        )
        dumped = [row.model_dump(by_alias=True) for row in data]
        served = set()
        for row in dumped:
            served.update(row)
        for key in served:
            if to_snake(key) in declared:
                continue
            values = [row.get(key) for row in dumped]
            assert len(set(values)) > 1

    def test_param_scoping_options(self):
        """Choice params are single-select with real labels and full options."""
        extra = InternationalMacroeconomicDataSetQueryParams.__json_schema_extra__
        variable = extra["variable"]["x-widget_config"]
        assert variable["label"] == "Variable"
        assert variable["multiSelect"] is False
        assert variable["multiple"] is False
        assert {opt["value"] for opt in variable["options"]} == set(
            INTERNATIONAL_MACRO_FILES
        )
        assert variable["value"] == DEFAULT_VARIABLE
        measure = extra["measure"]["x-widget_config"]
        assert measure["multiSelect"] is False
        assert {opt["value"] for opt in measure["options"]} == set(MEASURES)
        assert measure["value"] == DEFAULT_MEASURE

    def test_widget_config_and_column_headers(self):
        """The whole-widget config and per-field headers are populated."""
        widget = InternationalMacroeconomicDataSetData.model_config[
            "json_schema_extra"
        ]["x-widget_config"]
        assert widget["$.name"] == "USDA ERS International Macroeconomic Data Set"
        assert widget["$.category"] == "Economy"
        assert widget["$.subCategory"] == "Agriculture"
        assert widget["$.source"] == ["USDA", "ERS"]
        fields = InternationalMacroeconomicDataSetData.model_fields
        year_config = fields["year"].json_schema_extra["x-widget_config"]
        assert year_config["pinned"] == "left"
        assert year_config["cellDataType"] == "number"
        assert fields["unit"].json_schema_extra["x-widget_config"]["hide"] is True

    def test_null_token_mixin_coerces_placeholder(self):
        """The Data model coerces placeholder tokens to None but keeps columns."""
        row = InternationalMacroeconomicDataSetData.model_validate(
            {"year": 1990, "unit": "--", "United States": 10054.715526}
        )
        dumped = row.model_dump(by_alias=True)
        assert dumped["unit"] is None
        assert dumped["United States"] == 10054.715526
