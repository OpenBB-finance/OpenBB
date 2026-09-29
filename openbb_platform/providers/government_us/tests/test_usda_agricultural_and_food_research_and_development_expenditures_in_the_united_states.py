"""Tests for the USDA ERS Agricultural and Food R&D Expenditures utils and model."""

import asyncio
import csv
from io import StringIO

import pytest
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.utils.errors import EmptyDataError

from openbb_government_us.usda.models.agricultural_and_food_research_and_development_expenditures_in_the_united_states import (
    DEFAULT_MEASURE,
    AgriculturalAndFoodRdExpendituresData,
    AgriculturalAndFoodRdExpendituresFetcher,
    AgriculturalAndFoodRdExpendituresQueryParams,
)
from openbb_government_us.usda.utils import (
    ers_agricultural_and_food_research_and_development_expenditures_in_the_united_states as util,
)
from openbb_government_us.usda.utils.ers_agricultural_and_food_research_and_development_expenditures_in_the_united_states import (
    MEASURES,
    MEDIA_PATH,
    PRODUCT_PAGE,
    SERIES,
    SERIES_ORDER,
    parse_attribute,
    parse_csv,
)

HEADER = ["Year", "Attribute", "Value"]

_ROWS = [
    [
        1970,
        "Public agricultural and food R&D (current U.S. dollars- millions)",
        "548.729",
    ],
    [
        1970,
        "Public agricultural and food R&D performed by USDA intramural agencies (current U.S. dollars- millions)",
        "229.134",
    ],
    [
        1970,
        "Public agricultural & food R&D performed by State universities and cooperating institutions (current U.S. dollars- millions)",
        "319.595",
    ],
    [
        1970,
        "Private agriculture input industries R&D (current U.S. dollars- millions)",
        "306.378",
    ],
    [1970, "Private food industry R&D (current U.S. dollars- millions)", "222.0"],
    [1970, "R&D Price Index (2022 =100)", "10.036"],
    [
        1970,
        "Public agricultural and food R&D (constant 2022 U.S. dollars- millions)",
        "5467.612",
    ],
    [
        1970,
        "Public agricultural and food R&D performed by USDA intramural agencies (constant 2022 U.S. dollars- millions)",
        "2283.121",
    ],
    [
        1970,
        "Public agricultural & food R&D performed by State universities and cooperating institutions (constant 2022 U.S. dollars- millions)",
        "3184.49",
    ],
    [
        1970,
        "Private agriculture input industries R&D (constant 2022 U.S. dollars- millions)",
        "3052.791",
    ],
    [
        1970,
        "Private food industry R&D (constant 2022 U.S. dollars- millions)",
        "2212.037",
    ],
    [
        1971,
        "Public agricultural and food R&D (current U.S. dollars- millions)",
        "586.163",
    ],
    [1971, "R&D Price Index (2022 =100)", "10.618"],
    [2022, "Public agricultural and food R&D (current U.S. dollars- millions)", "NA"],
    [2022, "Private food industry R&D (current U.S. dollars- millions)", "7910.0"],
    [2022, "R&D Price Index (2022 =100)", "100.0"],
    [99, "Public agricultural and food R&D (current U.S. dollars- millions)", "5.0"],
    [1970, "Some other unmapped R&D (current U.S. dollars- millions)", "1.0"],
]


def _make_csv(rows):
    """Serialize a header and rows to CSV text."""
    buffer = StringIO()
    writer = csv.writer(buffer)
    writer.writerow(HEADER)
    for row in rows:
        writer.writerow(row)
    return buffer.getvalue()


SAMPLE_CSV = _make_csv(_ROWS)


class TestErsAgriculturalAndFoodRdExpendituresUtils:
    """Tests for the R&D expenditures utils module."""

    def test_catalog_constants(self):
        """The catalog exposes the media path, product page, and measures."""
        assert MEDIA_PATH.startswith("/media/")
        assert MEDIA_PATH.endswith(".csv")
        assert PRODUCT_PAGE.startswith("data-products/")
        assert MEASURES == ("nominal", "real")

    def test_series_map_and_order(self):
        """The series map and order cover the six fixed columns."""
        assert set(SERIES.values()) == set(SERIES_ORDER)
        assert len(SERIES_ORDER) == 6
        assert SERIES_ORDER[0] == "public_total"
        assert SERIES_ORDER[-1] == "rd_price_index"

    def test_parse_attribute_nominal(self):
        """A current-dollar attribute maps to its field with the nominal measure."""
        field, measure = parse_attribute(
            "Private food industry R&D (current U.S. dollars- millions)"
        )
        assert field == "private_food_industry"
        assert measure == "nominal"

    def test_parse_attribute_real(self):
        """A constant-dollar attribute maps to its field with the real measure."""
        field, measure = parse_attribute(
            "Public agricultural and food R&D (constant 2022 U.S. dollars- millions)"
        )
        assert field == "public_total"
        assert measure == "real"

    def test_parse_attribute_index_is_measure_agnostic(self):
        """The price index maps to its field with no measure."""
        field, measure = parse_attribute("R&D Price Index (2022 =100)")
        assert field == "rd_price_index"
        assert measure is None

    def test_parse_attribute_distinguishes_prefix_series(self):
        """The base total is not confused with its longer intramural variant."""
        total, _ = parse_attribute(
            "Public agricultural and food R&D (current U.S. dollars- millions)"
        )
        intramural, _ = parse_attribute(
            "Public agricultural and food R&D performed by USDA intramural agencies (current U.S. dollars- millions)"
        )
        assert total == "public_total"
        assert intramural == "public_usda_intramural"

    def test_parse_attribute_unmapped(self):
        """An unrecognized attribute yields no field and no measure."""
        assert parse_attribute(
            "Some other unmapped R&D (current U.S. dollars- millions)"
        ) == (
            None,
            None,
        )

    def test_parse_csv_record_shape(self):
        """A parsed record carries year, series, measure, and numeric value."""
        records = parse_csv(SAMPLE_CSV)
        first = records[0]
        assert first == {
            "year": 1970,
            "series": "public_total",
            "measure": "nominal",
            "value": 548.729,
        }

    def test_parse_csv_coerces_na_to_none(self):
        """The 'NA' token becomes a None value, keeping the record."""
        records = parse_csv(SAMPLE_CSV)
        na_rows = [
            r for r in records if r["year"] == 2022 and r["series"] == "public_total"
        ]
        assert len(na_rows) == 1
        assert na_rows[0]["value"] is None

    def test_parse_csv_skips_bad_year(self):
        """A non-four-digit year is skipped."""
        records = parse_csv(SAMPLE_CSV)
        assert all(record["year"] in {1970, 1971, 2022} for record in records)

    def test_parse_csv_skips_unmapped_attribute(self):
        """An unrecognized attribute is skipped, mapping nothing to None."""
        records = parse_csv(SAMPLE_CSV)
        assert all(record["series"] in SERIES_ORDER for record in records)
        assert 1.0 not in [record["value"] for record in records]

    def test_parse_csv_preserves_precision(self):
        """Numeric values keep full source precision."""
        records = parse_csv(SAMPLE_CSV)
        real_state = [
            r
            for r in records
            if r["year"] == 1970
            and r["series"] == "public_state_universities"
            and r["measure"] == "real"
        ]
        assert real_state[0]["value"] == 3184.49

    def test_afetch_records(self, monkeypatch):
        """afetch_records fetches the CSV through the ERS cache and parses it."""
        calls = []

        async def fake_afetch_ers_file(media_path, product=None, ttl=None):
            calls.append((media_path, product))
            return SAMPLE_CSV.encode("utf-8-sig")

        monkeypatch.setattr(
            "openbb_government_us.usda.utils.ers_client.afetch_ers_file",
            fake_afetch_ers_file,
        )
        records = asyncio.run(util.afetch_records())
        assert calls == [(MEDIA_PATH, PRODUCT_PAGE)]
        assert any(record["series"] == "rd_price_index" for record in records)


class TestAgriculturalAndFoodRdExpenditures:
    """Tests for the AgriculturalAndFoodRdExpenditures model."""

    def test_transform_query_default_measure(self):
        """transform_query defaults the measure and keeps year filters."""
        query = AgriculturalAndFoodRdExpendituresFetcher.transform_query(
            {"start_year": 2000}
        )
        assert isinstance(query, AgriculturalAndFoodRdExpendituresQueryParams)
        assert query.measure == DEFAULT_MEASURE
        assert query.start_year == 2000

    def test_measure_blank_returns_default(self):
        """A blank or None measure normalizes to the default measure."""
        assert (
            AgriculturalAndFoodRdExpendituresQueryParams(measure=None).measure
            == DEFAULT_MEASURE
        )
        assert (
            AgriculturalAndFoodRdExpendituresQueryParams(measure="").measure
            == DEFAULT_MEASURE
        )

    def test_measure_accepts_list(self):
        """A single-item list measure value is unwrapped and lower-cased."""
        query = AgriculturalAndFoodRdExpendituresQueryParams(measure=["Nominal"])
        assert query.measure == "nominal"

    def test_unknown_measure_raises(self):
        """An unknown measure raises OpenBBError listing valid choices."""
        with pytest.raises(OpenBBError, match="Invalid measure: gross"):
            AgriculturalAndFoodRdExpendituresQueryParams(measure="gross")

    def test_aextract_data_fetches_records(self, monkeypatch):
        """aextract_data returns the util's long-format records."""

        async def fake_afetch_records():
            return [
                {
                    "year": 1970,
                    "series": "public_total",
                    "measure": "nominal",
                    "value": 1.0,
                }
            ]

        monkeypatch.setattr(util, "afetch_records", fake_afetch_records)
        query = AgriculturalAndFoodRdExpendituresFetcher.transform_query({})
        records = asyncio.run(
            AgriculturalAndFoodRdExpendituresFetcher.aextract_data(query, None)
        )
        assert records == [
            {"year": 1970, "series": "public_total", "measure": "nominal", "value": 1.0}
        ]

    def test_transform_data_pivots_nominal(self):
        """The nominal measure fills the fixed columns, one row per year."""
        records = parse_csv(SAMPLE_CSV)
        query = AgriculturalAndFoodRdExpendituresFetcher.transform_query(
            {"measure": "nominal"}
        )
        data = AgriculturalAndFoodRdExpendituresFetcher.transform_data(query, records)
        first = data[0].model_dump()
        assert first["year"] == 1970
        assert first["public_total"] == 548.729
        assert first["public_usda_intramural"] == 229.134
        assert first["public_state_universities"] == 319.595
        assert first["private_input_industries"] == 306.378
        assert first["private_food_industry"] == 222.0
        assert first["rd_price_index"] == 10.036

    def test_transform_data_pivots_real(self):
        """The real measure fills the same columns with constant-dollar values."""
        records = parse_csv(SAMPLE_CSV)
        query = AgriculturalAndFoodRdExpendituresFetcher.transform_query(
            {"measure": "real"}
        )
        data = AgriculturalAndFoodRdExpendituresFetcher.transform_data(query, records)
        first = data[0].model_dump()
        assert first["year"] == 1970
        assert first["public_total"] == 5467.612
        assert first["public_state_universities"] == 3184.49
        assert first["rd_price_index"] == 10.036

    def test_transform_data_orders_chronologically(self):
        """Rows sort by year, oldest first."""
        records = parse_csv(SAMPLE_CSV)
        query = AgriculturalAndFoodRdExpendituresFetcher.transform_query(
            {"measure": "nominal"}
        )
        data = AgriculturalAndFoodRdExpendituresFetcher.transform_data(query, records)
        assert [row.year for row in data] == [1970, 1971, 2022]

    def test_transform_data_na_is_none(self):
        """A source 'NA' surfaces as a None cell, not a dropped row."""
        records = parse_csv(SAMPLE_CSV)
        query = AgriculturalAndFoodRdExpendituresFetcher.transform_query(
            {"measure": "nominal"}
        )
        data = AgriculturalAndFoodRdExpendituresFetcher.transform_data(query, records)
        row_2022 = next(row for row in data if row.year == 2022)
        dumped = row_2022.model_dump()
        assert dumped["public_total"] is None
        assert dumped["private_food_industry"] == 7910.0
        assert dumped["rd_price_index"] == 100.0

    def test_transform_data_index_shared_across_measures(self):
        """The measure-agnostic index appears under the real measure too."""
        records = parse_csv(SAMPLE_CSV)
        query = AgriculturalAndFoodRdExpendituresFetcher.transform_query(
            {"measure": "real"}
        )
        data = AgriculturalAndFoodRdExpendituresFetcher.transform_data(query, records)
        row_1971 = next(row for row in data if row.year == 1971)
        assert row_1971.model_dump()["rd_price_index"] == 10.618

    def test_transform_data_filters_years(self):
        """start_year and end_year filter rows on the integer year."""
        records = parse_csv(SAMPLE_CSV)
        start = AgriculturalAndFoodRdExpendituresFetcher.transform_data(
            AgriculturalAndFoodRdExpendituresFetcher.transform_query(
                {"measure": "nominal", "start_year": 1971}
            ),
            records,
        )
        assert {row.year for row in start} == {1971, 2022}
        end = AgriculturalAndFoodRdExpendituresFetcher.transform_data(
            AgriculturalAndFoodRdExpendituresFetcher.transform_query(
                {"measure": "nominal", "end_year": 1970}
            ),
            records,
        )
        assert {row.year for row in end} == {1970}

    def test_transform_data_empty_raises(self):
        """A filter that matches nothing raises EmptyDataError."""
        records = parse_csv(SAMPLE_CSV)
        query = AgriculturalAndFoodRdExpendituresFetcher.transform_query(
            {"measure": "nominal", "start_year": 3000}
        )
        with pytest.raises(EmptyDataError):
            AgriculturalAndFoodRdExpendituresFetcher.transform_data(query, records)

    def test_measure_param_scoping(self):
        """The measure param is a labeled single-select with a default value."""
        config = AgriculturalAndFoodRdExpendituresQueryParams.__json_schema_extra__[
            "measure"
        ]["x-widget_config"]
        assert config["label"] == "Measure"
        assert config["multiSelect"] is False
        assert config["multiple"] is False
        assert config["value"] == DEFAULT_MEASURE
        assert {option["value"] for option in config["options"]} == {"nominal", "real"}

    def test_year_params_labeled(self):
        """The year-range params carry human labels."""
        extra = AgriculturalAndFoodRdExpendituresQueryParams.__json_schema_extra__
        assert extra["start_year"]["x-widget_config"]["label"] == "Start year"
        assert extra["end_year"]["x-widget_config"]["label"] == "End year"

    def test_widget_model_config(self):
        """The whole-widget config carries the name, category, and source."""
        config = AgriculturalAndFoodRdExpendituresData.model_config[
            "json_schema_extra"
        ]["x-widget_config"]
        assert config["$.name"] == "USDA ERS Agricultural and Food R&D Expenditures"
        assert config["$.category"] == "Economy"
        assert config["$.subCategory"] == "Agriculture"
        assert config["$.source"] == ["USDA", "ERS"]

    def test_value_columns_are_numeric(self):
        """Every value column declares a numeric cell type and a header name."""
        fields = AgriculturalAndFoodRdExpendituresData.model_fields
        for name in SERIES_ORDER:
            config = fields[name].json_schema_extra["x-widget_config"]
            assert config["cellDataType"] == "number"
            assert config["headerName"]

    def test_year_column_pinned(self):
        """The year column is pinned to the left."""
        config = AgriculturalAndFoodRdExpendituresData.model_fields[
            "year"
        ].json_schema_extra["x-widget_config"]
        assert config["pinned"] == "left"

    def test_measure_not_a_served_field(self):
        """The measure is implied by the param, never a served data column."""
        assert "measure" not in AgriculturalAndFoodRdExpendituresData.model_fields

    def test_columns_defs_bind_to_served_keys(self):
        """Every column definition binds to a served key, and none is orphaned."""
        records = parse_csv(SAMPLE_CSV)
        query = AgriculturalAndFoodRdExpendituresFetcher.transform_query(
            {"measure": "nominal"}
        )
        data = AgriculturalAndFoodRdExpendituresFetcher.transform_data(query, records)
        served = set(data[0].model_dump(by_alias=True))
        column_fields = set(AgriculturalAndFoodRdExpendituresData.model_fields)
        assert served == column_fields

    def test_no_dynamic_or_dead_columns(self):
        """The served keys are the fixed column set, with no extra keys."""
        records = parse_csv(SAMPLE_CSV)
        query = AgriculturalAndFoodRdExpendituresFetcher.transform_query(
            {"measure": "real"}
        )
        data = AgriculturalAndFoodRdExpendituresFetcher.transform_data(query, records)
        expected = {"year", *SERIES_ORDER}
        for row in data:
            assert set(row.model_dump(by_alias=True)) == expected
