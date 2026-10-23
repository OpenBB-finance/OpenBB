"""Tests for the USDA ERS international agricultural productivity utils and model."""

import asyncio
import csv
from io import StringIO

import pytest
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic.alias_generators import to_snake

from openbb_government_us.usda.models.international_agricultural_productivity import (
    InternationalAgriculturalProductivityData,
    InternationalAgriculturalProductivityFetcher,
    InternationalAgriculturalProductivityQueryParams,
)
from openbb_government_us.usda.utils import (
    ers_international_agricultural_productivity as ers,
)
from openbb_government_us.usda.utils.ers_international_agricultural_productivity import (
    DEFAULT_COUNTRY,
    DEFAULT_GROUPING,
    DEFAULT_MEASURE,
    ENTITIES,
    ENTITY_GROUPING,
    ENTITY_LABEL,
    GROUPINGS,
    MEASURES,
    VARIABLE_HEADERS,
    afetch_dataset,
    afetch_entity,
    entity_options,
    grouping_options,
    measure_options,
    parse_entity,
)

CSV_HEADER = [
    "Order",
    "FAO",
    "ISO3",
    "Country/territory",
    "Region",
    "Sub-Region",
    "Inc I",
    "Year",
    "Variable",
    "Value",
]

SAMPLE_ROWS = [
    [
        "179",
        "231",
        "USA",
        "United States",
        "NORTH AMERICA",
        "",
        "HI",
        "2014",
        "TFP_Index",
        "90",
    ],
    [
        "179",
        "231",
        "USA",
        "United States",
        "NORTH AMERICA",
        "",
        "HI",
        "2015",
        "TFP_Index",
        "100",
    ],
    [
        "179",
        "231",
        "USA",
        "United States",
        "NORTH AMERICA",
        "",
        "HI",
        "2023",
        "TFP_Index",
        "104.4948",
    ],
    [
        "179",
        "231",
        "USA",
        "United States",
        "NORTH AMERICA",
        "",
        "HI",
        "2014",
        "Outall_Index",
        "91",
    ],
    [
        "179",
        "231",
        "USA",
        "United States",
        "NORTH AMERICA",
        "",
        "HI",
        "2015",
        "Outall_Index",
        "100",
    ],
    [
        "179",
        "231",
        "USA",
        "United States",
        "NORTH AMERICA",
        "",
        "HI",
        "2023",
        "Outall_Index",
        "107",
    ],
    [
        "179",
        "231",
        "USA",
        "United States",
        "NORTH AMERICA",
        "",
        "HI",
        "2014",
        "Outall_Q",
        "1000",
    ],
    [
        "179",
        "231",
        "USA",
        "United States",
        "NORTH AMERICA",
        "",
        "HI",
        "2015",
        "Outall_Q",
        "1100",
    ],
    [
        "179",
        "231",
        "USA",
        "United States",
        "NORTH AMERICA",
        "",
        "HI",
        "2023",
        "Outall_Q",
        "1200",
    ],
    [
        "179",
        "231",
        "USA",
        "United States",
        "NORTH AMERICA",
        "",
        "HI",
        "2014",
        "Land_Q",
        "50",
    ],
    [
        "179",
        "231",
        "USA",
        "United States",
        "NORTH AMERICA",
        "",
        "HI",
        "2015",
        "Land_Q",
        "55",
    ],
    [
        "179",
        "231",
        "USA",
        "United States",
        "NORTH AMERICA",
        "",
        "HI",
        "2023",
        "Land_Q",
        "60",
    ],
    [
        "179",
        "231",
        "USA",
        "United States",
        "NORTH AMERICA",
        "",
        "HI",
        "2014",
        "Outfish_Q",
        "5",
    ],
    [
        "179",
        "231",
        "USA",
        "United States",
        "NORTH AMERICA",
        "",
        "HI",
        "2015",
        "Outfish_Q",
        "6",
    ],
    [
        "179",
        "231",
        "USA",
        "United States",
        "NORTH AMERICA",
        "",
        "HI",
        "2023",
        "Outfish_Q",
        "7",
    ],
    [
        "12",
        "250",
        "COD",
        "Congo DR",
        "SSA",
        "SSA, Central",
        "LI",
        "2015",
        "TFP_Index",
        "80",
    ],
    [
        "12",
        "250",
        "COD",
        "Congo DR",
        "SSA",
        "SSA, Central",
        "LI",
        "2023",
        "TFP_Index",
        "85",
    ],
    [
        "12",
        "250",
        "COD",
        "Congo DR",
        "SSA",
        "SSA, Central",
        "LI",
        "2015",
        "Outall_Q",
        "200",
    ],
    [
        "12",
        "250",
        "COD",
        "Congo DR",
        "SSA",
        "SSA, Central",
        "LI",
        "2023",
        "Outall_Q",
        "210",
    ],
    [
        "12",
        "250",
        "COD",
        "Congo DR",
        "SSA",
        "SSA, Central",
        "LI",
        "2015",
        "Land_Q",
        "10",
    ],
    [
        "12",
        "250",
        "COD",
        "Congo DR",
        "SSA",
        "SSA, Central",
        "LI",
        "2023",
        "Land_Q",
        "11",
    ],
    [
        "179",
        "231",
        "USA",
        "United States",
        "NORTH AMERICA",
        "",
        "HI",
        "",
        "TFP_Index",
        "1",
    ],
    [
        "179",
        "231",
        "USA",
        "United States",
        "NORTH AMERICA",
        "",
        "HI",
        "2016",
        "TFP_Index",
        "n/a",
    ],
    [
        "179",
        "231",
        "USA",
        "United States",
        "NORTH AMERICA",
        "",
        "HI",
        "2016",
        "GDP_Growth",
        "5",
    ],
    ["999", "0", "ZZZ", "Nowhere", "SSA", "", "LI", "2015", "TFP_Index", "12"],
]


def build_csv(rows: list[list[str]]) -> str:
    """Build CSV text from the header and full-width rows."""
    buffer = StringIO()
    writer = csv.writer(buffer)
    writer.writerow(CSV_HEADER)
    writer.writerows(rows)
    return buffer.getvalue()


SAMPLE_CSV = build_csv(SAMPLE_ROWS)


def make_record(**overrides) -> dict:
    """Build a parsed observation record with optional field overrides."""
    record = {"year": 2015, "variable": "TFP_Index", "value": 100.0}
    record.update(overrides)
    return record


class TestErsInternationalAgriculturalProductivityUtils:
    """Tests for the ers_international_agricultural_productivity utils module."""

    def test_grouping_catalog(self):
        """The grouping catalog holds the nine documented buckets."""
        assert len(GROUPINGS) == 9
        assert GROUPINGS["north_america"] == "North America"
        assert GROUPINGS["country_grouping"] == "Country grouping"

    def test_entity_catalog_covers_every_grouping(self):
        """Every entity maps to a known grouping and unique labeled order."""
        assert len(ENTITIES) == 234
        assert len(ENTITY_LABEL) == 234
        assert {bucket for _, _, bucket in ENTITIES} == set(GROUPINGS)
        assert ENTITY_LABEL[179] == "United States"
        assert ENTITY_LABEL[220] == "World"
        assert ENTITY_GROUPING[220] == "country_grouping"

    def test_default_country_is_world(self):
        """The default country is the world aggregate at order 220."""
        assert DEFAULT_COUNTRY == 220
        assert ENTITY_LABEL[DEFAULT_COUNTRY] == "World"

    def test_measure_families(self):
        """The measure families hold seven index and twelve quantity columns."""
        assert set(MEASURES) == {"productivity_indices", "physical_quantities"}
        assert len(MEASURES["productivity_indices"]["columns"]) == 7
        assert len(MEASURES["physical_quantities"]["columns"]) == 12
        assert len(VARIABLE_HEADERS) == 19
        assert VARIABLE_HEADERS["TFP_Index"] == "TFP index (2015=100)"

    def test_grouping_options(self):
        """Grouping options are label/value pairs over the nine buckets."""
        options = grouping_options()
        assert len(options) == 9
        assert {"label": "North America", "value": "north_america"} in options

    def test_measure_options(self):
        """Measure options are label/value pairs over the two families."""
        options = measure_options()
        assert options == [
            {
                "label": "Productivity indices (2015=100)",
                "value": "productivity_indices",
            },
            {"label": "Physical quantities", "value": "physical_quantities"},
        ]

    def test_entity_options_scoped_to_grouping(self):
        """Entity options list only the selected grouping's entities."""
        options = entity_options("north_america")
        assert options == [
            {"label": "Canada", "value": 178},
            {"label": "United States", "value": 179},
            {"label": "NORTH AMERICA", "value": 215},
        ]
        assert all(
            ENTITY_GROUPING[option["value"]] == "income_group"
            for option in entity_options("income_group")
        )

    def test_entity_options_disambiguate_duplicate_name(self):
        """The duplicate name 'China' resolves to two distinct orders."""
        asia = {
            option["value"]: option["label"]
            for option in entity_options("asia_pacific")
        }
        income = {
            option["value"]: option["label"]
            for option in entity_options("income_group")
        }
        assert asia[81] == "China"
        assert income[227] == "China"

    def test_parse_entity_filters_order_variable_year_value(self):
        """parse_entity keeps one entity's known, dated, numeric records."""
        records = parse_entity(SAMPLE_CSV, 179)
        assert {record["variable"] for record in records} == {
            "TFP_Index",
            "Outall_Index",
            "Outall_Q",
            "Land_Q",
            "Outfish_Q",
        }
        assert {record["year"] for record in records} == {2014, 2015, 2023}
        assert all(isinstance(record["value"], float) for record in records)
        assert all(isinstance(record["year"], int) for record in records)

    def test_parse_entity_other_entities_excluded(self):
        """parse_entity returns nothing for an order absent from the file."""
        assert parse_entity(SAMPLE_CSV, 999999) == []
        congo = parse_entity(SAMPLE_CSV, 12)
        assert {record["variable"] for record in congo} == {
            "TFP_Index",
            "Outall_Q",
            "Land_Q",
        }

    def test_afetch_dataset_downloads_and_caches(self, monkeypatch, tmp_path):
        """afetch_dataset downloads once, decodes, and serves from cache after."""
        monkeypatch.setenv("OPENBB_USDA_CACHE_DIR", str(tmp_path))
        calls = []

        async def fake_download():
            calls.append(1)
            return SAMPLE_CSV.encode("utf-8-sig")

        monkeypatch.setattr(ers, "_adownload", fake_download)
        first = asyncio.run(afetch_dataset())
        second = asyncio.run(afetch_dataset())
        assert "United States" in first
        assert first == second
        assert len(calls) == 1

    def test_afetch_entity(self, monkeypatch):
        """afetch_entity fetches the dataset and parses the requested entity."""

        async def fake_dataset():
            return SAMPLE_CSV

        monkeypatch.setattr(ers, "afetch_dataset", fake_dataset)
        records = asyncio.run(afetch_entity(179))
        assert {record["year"] for record in records} == {2014, 2015, 2023}

    def test_adownload_reads_response_bytes(self, monkeypatch):
        """_adownload returns the response body on a 200 status."""

        class FakeResponse:
            status = 200

            async def read(self):
                return SAMPLE_CSV.encode("utf-8-sig")

        async def fake_amake_request(url, timeout=None, response_callback=None):
            assert timeout == ers.DOWNLOAD_TIMEOUT
            return await response_callback(FakeResponse(), None)

        monkeypatch.setattr(
            "openbb_core.provider.utils.helpers.amake_request", fake_amake_request
        )
        content = asyncio.run(ers._adownload())
        assert content.decode("utf-8-sig").splitlines()[0].startswith("Order,")

    def test_adownload_raises_on_bad_status(self, monkeypatch):
        """_adownload raises OpenBBError when the response status is not 200."""

        class FakeResponse:
            status = 500

            async def read(self):
                return b""

        async def fake_amake_request(url, timeout=None, response_callback=None):
            return await response_callback(FakeResponse(), None)

        monkeypatch.setattr(
            "openbb_core.provider.utils.helpers.amake_request", fake_amake_request
        )
        with pytest.raises(OpenBBError, match="status 500"):
            asyncio.run(ers._adownload())


class TestInternationalAgriculturalProductivity:
    """Tests for the InternationalAgriculturalProductivity model."""

    def test_transform_query(self):
        """transform_query builds the query params model."""
        query = InternationalAgriculturalProductivityFetcher.transform_query(
            {
                "grouping": "asia_pacific",
                "country": 103,
                "measure": "physical_quantities",
            }
        )
        assert isinstance(query, InternationalAgriculturalProductivityQueryParams)
        assert query.grouping == "asia_pacific"
        assert query.country == 103
        assert query.measure == "physical_quantities"

    def test_defaults(self):
        """The params default to the world, the country grouping, and indices."""
        query = InternationalAgriculturalProductivityQueryParams()
        assert query.grouping == DEFAULT_GROUPING
        assert query.country == DEFAULT_COUNTRY
        assert query.measure == DEFAULT_MEASURE

    def test_country_normalizes_and_defaults(self):
        """Country coerces strings and lists to an int and blanks fall back."""
        assert (
            InternationalAgriculturalProductivityQueryParams(country="179").country
            == 179
        )
        assert (
            InternationalAgriculturalProductivityQueryParams(country=[103]).country
            == 103
        )
        assert (
            InternationalAgriculturalProductivityQueryParams(country="").country
            == DEFAULT_COUNTRY
        )

    def test_invalid_country_raises(self):
        """An unknown or non-integer country raises OpenBBError."""
        with pytest.raises(OpenBBError, match="Invalid country order: 500"):
            InternationalAgriculturalProductivityQueryParams(country=500)
        with pytest.raises(OpenBBError, match="Invalid country: abc"):
            InternationalAgriculturalProductivityQueryParams(country="abc")

    def test_grouping_defaults_and_validates(self):
        """Grouping falls back on blanks and rejects unknown buckets."""
        assert (
            InternationalAgriculturalProductivityQueryParams(grouping="").grouping
            == DEFAULT_GROUPING
        )
        assert (
            InternationalAgriculturalProductivityQueryParams(
                grouping=["europe"]
            ).grouping
            == "europe"
        )
        with pytest.raises(OpenBBError, match="Invalid grouping: bogus"):
            InternationalAgriculturalProductivityQueryParams(grouping="bogus")

    def test_measure_defaults_and_validates(self):
        """Measure falls back on blanks and rejects unknown families."""
        assert (
            InternationalAgriculturalProductivityQueryParams(measure="").measure
            == DEFAULT_MEASURE
        )
        assert (
            InternationalAgriculturalProductivityQueryParams(
                measure=["physical_quantities"]
            ).measure
            == "physical_quantities"
        )
        with pytest.raises(OpenBBError, match="Invalid measure: bogus"):
            InternationalAgriculturalProductivityQueryParams(measure="bogus")

    def test_aextract_data_forwards_country(self, monkeypatch):
        """aextract_data forwards the selected country order to afetch_entity."""
        calls = []

        async def fake_afetch_entity(order):
            calls.append(order)
            return parse_entity(SAMPLE_CSV, order)

        monkeypatch.setattr(ers, "afetch_entity", fake_afetch_entity)
        query = InternationalAgriculturalProductivityFetcher.transform_query(
            {"country": 179}
        )
        records = asyncio.run(
            InternationalAgriculturalProductivityFetcher.aextract_data(query, None)
        )
        assert calls == [179]
        assert {record["year"] for record in records} == {2014, 2015, 2023}

    def test_transform_data_pivots_indices(self):
        """The index family spreads into one value column per present index."""
        records = parse_entity(SAMPLE_CSV, 179)
        query = InternationalAgriculturalProductivityFetcher.transform_query(
            {"country": 179, "measure": "productivity_indices"}
        )
        data = InternationalAgriculturalProductivityFetcher.transform_data(
            query, records
        )
        assert [row.year for row in data] == [2014, 2015, 2023]
        dumped = data[-1].model_dump(by_alias=True)
        assert dumped["year"] == 2023
        assert dumped["TFP index (2015=100)"] == 104.4948
        assert dumped["Output index (2015=100)"] == 107.0
        assert "Total output ($1,000, 2015 prices)" not in dumped

    def test_transform_data_pivots_quantities_in_canonical_order(self):
        """The quantity family spreads into canonically ordered value columns."""
        records = parse_entity(SAMPLE_CSV, 179)
        query = InternationalAgriculturalProductivityFetcher.transform_query(
            {"country": 179, "measure": "physical_quantities"}
        )
        data = InternationalAgriculturalProductivityFetcher.transform_data(
            query, records
        )
        columns = [key for key in data[0].model_dump(by_alias=True) if key != "year"]
        assert columns == [
            "Total output ($1,000, 2015 prices)",
            "Aquaculture output ($1,000, 2015 prices)",
            "Agricultural land (1,000 ha, rainfed-cropland-equiv.)",
        ]

    def test_transform_data_omits_absent_measure_column(self):
        """A measure with no observations for the entity yields no column."""
        records = parse_entity(SAMPLE_CSV, 12)
        query = InternationalAgriculturalProductivityFetcher.transform_query(
            {"country": 12, "measure": "physical_quantities"}
        )
        data = InternationalAgriculturalProductivityFetcher.transform_data(
            query, records
        )
        columns = {key for row in data for key in row.model_dump(by_alias=True)}
        assert "Aquaculture output ($1,000, 2015 prices)" not in columns
        assert "Total output ($1,000, 2015 prices)" in columns

    def test_transform_data_years_chronological(self):
        """Year rows are emitted oldest-first regardless of input order."""
        records = [
            make_record(year=2023, value=3.0),
            make_record(year=2014, value=1.0),
            make_record(year=2015, value=2.0),
        ]
        query = InternationalAgriculturalProductivityFetcher.transform_query(
            {"country": 179}
        )
        data = InternationalAgriculturalProductivityFetcher.transform_data(
            query, records
        )
        assert [row.year for row in data] == [2014, 2015, 2023]

    def test_transform_data_filters_years(self):
        """start_year and end_year select which year rows appear."""
        records = parse_entity(SAMPLE_CSV, 179)
        query = InternationalAgriculturalProductivityFetcher.transform_query(
            {"country": 179, "start_year": 2015, "end_year": 2015}
        )
        data = InternationalAgriculturalProductivityFetcher.transform_data(
            query, records
        )
        assert [row.year for row in data] == [2015]

    def test_transform_data_empty_raises(self):
        """No records surviving the filters raises EmptyDataError."""
        records = parse_entity(SAMPLE_CSV, 179)
        query = InternationalAgriculturalProductivityFetcher.transform_query(
            {"country": 179, "start_year": 2100}
        )
        with pytest.raises(EmptyDataError, match="No records match"):
            InternationalAgriculturalProductivityFetcher.transform_data(query, records)

    def test_columns_defs_bind_to_served_keys(self):
        """The declared column binds to a served key; measure columns are dynamic."""
        records = parse_entity(SAMPLE_CSV, 179)
        query = InternationalAgriculturalProductivityFetcher.transform_query(
            {"country": 179, "measure": "productivity_indices"}
        )
        data = InternationalAgriculturalProductivityFetcher.transform_data(
            query, records
        )
        dumped = [row.model_dump(by_alias=True) for row in data]
        served = set(dumped[0])
        schema = InternationalAgriculturalProductivityData.model_json_schema(
            by_alias=True, mode="serialization"
        )
        column_fields = [to_snake(key) for key in schema["properties"]]
        assert column_fields == ["year"]
        for field in column_fields:
            assert field in served, field
        dynamic = served - set(column_fields)
        assert dynamic
        for key in dynamic:
            assert len({row[key] for row in dumped}) > 1, key

    def test_widget_config_metadata(self):
        """The whole-widget config carries the ERS category and source."""
        config = InternationalAgriculturalProductivityData.model_config[
            "json_schema_extra"
        ]["x-widget_config"]
        assert config["$.name"] == "USDA ERS International Agricultural Productivity"
        assert config["$.category"] == "Economy"
        assert config["$.subCategory"] == "Agriculture"
        assert config["$.source"] == ["USDA", "ERS"]
