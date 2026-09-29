"""Tests for the USDA ERS rural-urban continuum codes utils and model."""

import asyncio
import csv
from io import StringIO

import pandas as pd
import pytest
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic.alias_generators import to_snake

from openbb_government_us.usda.models.rural_urban_continuum_codes import (
    RuralUrbanContinuumCodesData,
    RuralUrbanContinuumCodesFetcher,
    RuralUrbanContinuumCodesQueryParams,
)
from openbb_government_us.usda.utils import ers_rural_urban_continuum_codes as rucc
from openbb_government_us.usda.utils.ers_rural_urban_continuum_codes import (
    STATE_NAMES,
    VINTAGE_CATALOG,
    VINTAGE_OPTIONS,
    VINTAGES,
    afetch_states,
    afetch_vintage,
    clean_text,
    parse_csv_records,
    parse_population,
    parse_xls_records,
)

CSV_HEADER = ["FIPS", "State", "County_Name", "Attribute", "Value"]

CSV_ROWS = [
    ["01001", "AL", "Autauga County", "Population_2020", "58805"],
    ["01001", "AL", "Autauga County", "RUCC_2023", "2"],
    [
        "01001",
        "AL",
        "Autauga County",
        "Description",
        "Metro - Counties in metro areas of 250,000 to 1 million population",
    ],
    ["56039", "WY", "Teton County", "Population_2020", "23331"],
    ["56039", "WY", "Teton County", "RUCC_2023", "7"],
    [
        "56039",
        "WY",
        "Teton County",
        "Description",
        "Nonmetro - Urban population of 5,000 to 20,000, not adjacent to a metro area",
    ],
    ["60030", "AS", "Rose Island", "Population_2020", "0"],
    ["60030", "AS", "Rose Island", "Description", "Not Applicable"],
]


def build_csv(rows: list[list[str]]) -> str:
    """Build melted CSV text from the header and observation rows."""
    buffer = StringIO()
    writer = csv.writer(buffer)
    writer.writerow(CSV_HEADER)
    writer.writerows(rows)
    return buffer.getvalue()


SAMPLE_CSV = build_csv(CSV_ROWS)

MAINLAND_FRAME = pd.DataFrame(
    {
        "FIPS Code": ["01001", "56039"],
        "State": ["AL", " WY"],
        "County Name": ["Autauga County", "  Teton County  "],
        "1993 Rural-urban Continuum Code": ["2", "9"],
        "2003 Rural-urban Continuum Code": ["2", "7"],
        "2000 Population ": ["43671", "18251"],
        "Percent of workers in nonmetro counties commuting to central counties"
        " of adjacent metro areas": ["0", "0"],
        "Description for 2003 codes": [
            "County in metro area of 250,000 to 1 million population",
            "Nonmetro county with urban population of 2,500-19,999",
        ],
    }
)

PR_FRAME = pd.DataFrame(
    {
        "FIPS Code": ["72001"],
        "State": ["PR"],
        "Municipio Name": ["Adjuntas Municipio"],
        "Population 2003 ": ["19143"],
        "Rural-urban Continuum Code, 2003": ["6"],
        "Description of the 2003 Code": [
            "Nonmetro county with urban population of 2,500-19,999,"
            " adjacent to a metro area"
        ],
    }
)

CODE_ONLY_FRAME = pd.DataFrame(
    {
        "FIPS Code": ["01001", "01005"],
        "State": [" AL", "AL"],
        "County Name": ["    AUTAUGA COUNTY   ", "BARBOUR COUNTY"],
        "1974 Rural-urban Continuum Code": ["3", "6"],
    }
)

MAINLAND_PART = VINTAGE_CATALOG["2003"]["parts"][0]
CODE_ONLY_PART = {
    "media": "/media/5774/1974-rural-urban-continuum-codes.xls",
    "sheet": "RuralUrbanCont1974",
    "fips": "FIPS Code",
    "state": "State",
    "name": "County Name",
    "code": "1974 Rural-urban Continuum Code",
    "description": None,
    "population": None,
}


def make_record(**overrides) -> dict:
    """Build a parsed county-lookup record with optional field overrides."""
    record = {
        "vintage": "2023",
        "fips": "56039",
        "state": "WY",
        "county_name": "Teton County",
        "rucc_code": "7",
        "description": "Nonmetro - Urban population of 5,000 to 20,000",
        "population": 23331,
    }
    record.update(overrides)
    return record


class TestErsRuralUrbanContinuumCodesUtils:
    """Tests for the ers_rural_urban_continuum_codes utils module."""

    def test_catalog_contents(self):
        """The catalog holds the three complete vintages, newest first."""
        assert VINTAGES == ("2023", "2013", "2003")
        assert VINTAGE_CATALOG["2023"]["format"] == "csv"
        assert VINTAGE_CATALOG["2023"]["media"].startswith("/media/5768/")
        assert VINTAGE_CATALOG["2013"]["format"] == "xls"
        assert len(VINTAGE_CATALOG["2003"]["parts"]) == 2
        assert VINTAGE_CATALOG["2003"]["parts"][1]["media"].startswith("/media/5771/")
        assert VINTAGE_CATALOG["2003"]["parts"][1]["name"] == "Municipio Name"

    def test_vintage_options(self):
        """The vintage options are label/value pairs for every vintage."""
        assert [
            {"label": vintage, "value": vintage} for vintage in VINTAGES
        ] == VINTAGE_OPTIONS

    def test_state_names(self):
        """The state map covers the fifty states, DC, and five territories."""
        assert len(STATE_NAMES) == 56
        assert STATE_NAMES["WY"] == "Wyoming"
        assert STATE_NAMES["PR"] == "Puerto Rico"
        assert STATE_NAMES["AS"] == "American Samoa"

    def test_clean_text(self):
        """clean_text strips cells and coerces blanks and 'nan' to None."""
        assert clean_text("  Autauga County  ") == "Autauga County"
        assert clean_text(" AL") == "AL"
        assert clean_text("") is None
        assert clean_text("   ") is None
        assert clean_text(None) is None
        assert clean_text("nan") is None
        assert clean_text(float("nan")) is None

    def test_parse_population(self):
        """parse_population keeps full integer counts and coerces blanks to None."""
        assert parse_population("58805") == 58805
        assert parse_population("43,671") == 43671
        assert parse_population("0") == 0
        assert parse_population("19143.0") == 19143
        assert parse_population("") is None
        assert parse_population(None) is None
        assert parse_population("nan") is None
        assert parse_population("n/a") is None
        assert parse_population("not a number") is None

    def test_parse_csv_records_pivots_per_county(self):
        """The melted CSV pivots to one record per FIPS with the attributes."""
        records = parse_csv_records(SAMPLE_CSV, VINTAGE_CATALOG["2023"], "2023")
        assert [record["fips"] for record in records] == ["01001", "56039", "60030"]
        autauga = records[0]
        assert autauga["state"] == "AL"
        assert autauga["county_name"] == "Autauga County"
        assert autauga["rucc_code"] == "2"
        assert autauga["population"] == 58805
        assert autauga["vintage"] == "2023"
        assert autauga["description"].startswith("Metro - Counties in metro areas")

    def test_parse_csv_records_skips_blank_fips(self):
        """A melted row without a FIPS code is dropped."""
        text = build_csv(
            [["", "AL", "Footnote", "Description", "Sources: ERS"], *CSV_ROWS]
        )
        records = parse_csv_records(text, VINTAGE_CATALOG["2023"], "2023")
        assert [record["fips"] for record in records] == ["01001", "56039", "60030"]

    def test_parse_csv_records_missing_code_is_none(self):
        """A county with no RUCC attribute keeps rucc_code None but its rest."""
        records = parse_csv_records(SAMPLE_CSV, VINTAGE_CATALOG["2023"], "2023")
        rose = records[2]
        assert rose["fips"] == "60030"
        assert rose["rucc_code"] is None
        assert rose["population"] == 0
        assert rose["description"] == "Not Applicable"

    def test_parse_xls_records_full_columns(self, monkeypatch):
        """Rows map to records, stripping padding and reading full columns."""
        monkeypatch.setattr(pd, "read_excel", lambda *a, **k: MAINLAND_FRAME.copy())
        records = parse_xls_records(b"mainland", MAINLAND_PART, "2003")
        teton = records[1]
        assert teton["fips"] == "56039"
        assert teton["state"] == "WY"
        assert teton["county_name"] == "Teton County"
        assert teton["rucc_code"] == "7"
        assert teton["population"] == 18251
        assert teton["description"].startswith("Nonmetro county")

    def test_parse_xls_records_code_only(self, monkeypatch):
        """A code-only workbook yields None description and population."""
        monkeypatch.setattr(pd, "read_excel", lambda *a, **k: CODE_ONLY_FRAME.copy())
        records = parse_xls_records(b"1974", CODE_ONLY_PART, "1974")
        assert records[0] == {
            "vintage": "1974",
            "fips": "01001",
            "state": "AL",
            "county_name": "AUTAUGA COUNTY",
            "rucc_code": "3",
            "description": None,
            "population": None,
        }

    def test_parse_xls_records_skips_blank_fips(self, monkeypatch):
        """Rows without a FIPS code are dropped."""
        frame = pd.DataFrame(
            {
                "FIPS Code": ["01001", None],
                "State": ["AL", "AL"],
                "County Name": ["Autauga County", "Footnote row"],
                "1974 Rural-urban Continuum Code": ["3", ""],
            }
        )
        monkeypatch.setattr(pd, "read_excel", lambda *a, **k: frame.copy())
        records = parse_xls_records(b"1974", CODE_ONLY_PART, "1974")
        assert len(records) == 1
        assert records[0]["fips"] == "01001"

    def test_afetch_vintage_csv(self, monkeypatch):
        """The CSV vintage fetches and pivots the melted file."""

        async def fake_afetch_ers_file(media_path, product=None, ttl=None):
            assert media_path == VINTAGE_CATALOG["2023"]["media"]
            return SAMPLE_CSV.encode("utf-8-sig")

        monkeypatch.setattr(
            "openbb_government_us.usda.utils.ers_client.afetch_ers_file",
            fake_afetch_ers_file,
        )
        records = asyncio.run(afetch_vintage("2023"))
        assert {record["fips"] for record in records} == {
            "01001",
            "56039",
            "60030",
        }

    def test_afetch_vintage_merges_2003(self, monkeypatch):
        """The 2003 vintage fetches both parts and merges mainland with PR."""
        seen: list[str] = []

        async def fake_afetch_ers_file(media_path, product=None, ttl=None):
            seen.append(media_path)
            return media_path.encode("utf-8")

        def fake_read_excel(io, sheet_name=None, engine=None, dtype=None):
            return {"beale03": MAINLAND_FRAME, "pr2003": PR_FRAME}[sheet_name].copy()

        monkeypatch.setattr(
            "openbb_government_us.usda.utils.ers_client.afetch_ers_file",
            fake_afetch_ers_file,
        )
        monkeypatch.setattr(pd, "read_excel", fake_read_excel)
        records = asyncio.run(afetch_vintage("2003"))
        assert len(seen) == 2
        assert [record["fips"] for record in records] == ["01001", "56039", "72001"]
        assert records[2]["state"] == "PR"
        assert records[2]["population"] == 19143

    def test_afetch_states(self, monkeypatch):
        """States are the vintage's distinct codes, labeled and sorted."""

        async def fake_afetch_vintage(vintage):
            return [
                make_record(state="WY"),
                make_record(state="AL"),
                make_record(state="WY"),
                make_record(state=None),
            ]

        monkeypatch.setattr(rucc, "afetch_vintage", fake_afetch_vintage)
        options = asyncio.run(afetch_states("2023"))
        assert options == [
            {"label": "Alabama", "value": "AL"},
            {"label": "Wyoming", "value": "WY"},
        ]


class TestRuralUrbanContinuumCodes:
    """Tests for the RuralUrbanContinuumCodes model."""

    def test_transform_query(self):
        """transform_query builds the query params model."""
        query = RuralUrbanContinuumCodesFetcher.transform_query(
            {"vintage": "2013", "state": "IA"}
        )
        assert isinstance(query, RuralUrbanContinuumCodesQueryParams)
        assert query.vintage == "2013"
        assert query.state == "IA"

    def test_vintage_defaults_and_blank(self):
        """The vintage defaults to 2023 and blanks fall back."""
        assert RuralUrbanContinuumCodesQueryParams().vintage == "2023"
        assert RuralUrbanContinuumCodesQueryParams(vintage="").vintage == "2023"
        assert RuralUrbanContinuumCodesQueryParams(vintage=["2003"]).vintage == "2003"

    def test_unknown_vintage_raises(self):
        """An unknown vintage raises OpenBBError listing valid choices."""
        with pytest.raises(OpenBBError, match="Invalid vintage: 2020.*2023"):
            RuralUrbanContinuumCodesQueryParams(vintage="2020")

    def test_state_defaults_none_and_normalizes(self):
        """State defaults to None, uppercases, and takes the first of a list."""
        assert RuralUrbanContinuumCodesQueryParams().state is None
        assert RuralUrbanContinuumCodesQueryParams(state="").state is None
        assert RuralUrbanContinuumCodesQueryParams(state="wy").state == "WY"
        assert RuralUrbanContinuumCodesQueryParams(state=["ny"]).state == "NY"

    def test_unknown_state_raises(self):
        """An unknown state code raises OpenBBError."""
        with pytest.raises(OpenBBError, match="Invalid state: ZZ"):
            RuralUrbanContinuumCodesQueryParams(state="ZZ")

    def test_aextract_data_forwards_vintage(self, monkeypatch):
        """aextract_data forwards the vintage to afetch_vintage."""
        calls: list[str] = []

        async def fake_afetch_vintage(vintage):
            calls.append(vintage)
            return [make_record()]

        monkeypatch.setattr(rucc, "afetch_vintage", fake_afetch_vintage)
        query = RuralUrbanContinuumCodesFetcher.transform_query({"vintage": "2013"})
        records = asyncio.run(
            RuralUrbanContinuumCodesFetcher.aextract_data(query, None)
        )
        assert calls == ["2013"]
        assert records[0]["fips"] == "56039"

    def test_transform_data_filters_by_state(self):
        """A state filter keeps only that state's counties."""
        records = [
            make_record(fips="01001", state="AL", county_name="Autauga County"),
            make_record(fips="56039", state="WY", county_name="Teton County"),
        ]
        query = RuralUrbanContinuumCodesFetcher.transform_query({"state": "WY"})
        data = RuralUrbanContinuumCodesFetcher.transform_data(query, records)
        assert [row.fips for row in data] == ["56039"]
        assert data[0].state == "WY"

    def test_transform_data_all_states_when_none(self):
        """No state filter returns every county of the vintage."""
        records = [
            make_record(fips="01001", state="AL"),
            make_record(fips="56039", state="WY"),
        ]
        query = RuralUrbanContinuumCodesFetcher.transform_query({})
        data = RuralUrbanContinuumCodesFetcher.transform_data(query, records)
        assert {row.state for row in data} == {"AL", "WY"}

    def test_transform_data_sorted_by_fips(self):
        """Rows are emitted in ascending FIPS order regardless of input order."""
        records = [
            make_record(fips="56039", state="WY"),
            make_record(fips="01001", state="AL"),
            make_record(fips="06037", state="CA"),
        ]
        query = RuralUrbanContinuumCodesFetcher.transform_query({})
        data = RuralUrbanContinuumCodesFetcher.transform_data(query, records)
        assert [row.fips for row in data] == ["01001", "06037", "56039"]

    def test_transform_data_passes_through_nulls(self):
        """A row with a blank description or population keeps them null."""
        records = [
            make_record(
                fips="01001",
                state="AL",
                rucc_code="3",
                description=None,
                population=None,
            )
        ]
        query = RuralUrbanContinuumCodesFetcher.transform_query({"vintage": "2003"})
        data = RuralUrbanContinuumCodesFetcher.transform_data(query, records)
        assert data[0].rucc_code == "3"
        assert data[0].description is None
        assert data[0].population is None

    def test_transform_data_empty_raises(self):
        """A state with no rows raises EmptyDataError."""
        query = RuralUrbanContinuumCodesFetcher.transform_query({"state": "PR"})
        with pytest.raises(EmptyDataError, match="No records match"):
            RuralUrbanContinuumCodesFetcher.transform_data(
                query, [make_record(state="WY")]
            )

    def test_columns_defs_bind_to_served_keys(self):
        """Every declared column definition binds to a served row key."""
        records = [make_record()]
        query = RuralUrbanContinuumCodesFetcher.transform_query({})
        data = RuralUrbanContinuumCodesFetcher.transform_data(query, records)
        served = set(data[0].model_dump(by_alias=True))
        schema = RuralUrbanContinuumCodesData.model_json_schema(
            by_alias=True, mode="serialization"
        )
        column_fields = [to_snake(key) for key in schema["properties"]]
        assert column_fields, "no column definitions generated"
        for field in column_fields:
            assert field in served, field
        assert served == set(column_fields)

    def test_no_always_empty_column_on_default(self):
        """Every served column is populated for the default 2023 vintage rows."""
        records = [
            make_record(fips="01001", state="AL"),
            make_record(fips="56039", state="WY"),
        ]
        query = RuralUrbanContinuumCodesFetcher.transform_query({})
        data = RuralUrbanContinuumCodesFetcher.transform_data(query, records)
        served_keys = data[0].model_dump(by_alias=True).keys()
        for key in served_keys:
            assert any(
                row.model_dump(by_alias=True)[key] is not None for row in data
            ), key

    def test_widget_config_metadata(self):
        """The whole-widget config carries the ERS category and source."""
        config = RuralUrbanContinuumCodesData.model_config["json_schema_extra"][
            "x-widget_config"
        ]
        assert config["$.name"] == "USDA ERS Rural-Urban Continuum Codes"
        assert config["$.category"] == "Economy"
        assert config["$.subCategory"] == "Agriculture"
        assert config["$.source"] == ["USDA", "ERS"]

    def test_fips_and_code_columns_are_text(self):
        """FIPS and RUCC code render as text so leading zeros survive."""
        schema = RuralUrbanContinuumCodesData.model_json_schema(
            by_alias=True, mode="serialization"
        )
        for field in ("fips", "rucc_code"):
            config = schema["properties"][field]["x-widget_config"]
            assert config["cellDataType"] == "text"
