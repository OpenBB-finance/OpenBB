"""Tests for the USDA ERS poverty area measures utils and model."""

import asyncio
import csv
from io import StringIO

import pytest
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic.alias_generators import to_snake

from openbb_government_us.usda.models.poverty_area_measures import (
    PovertyAreaMeasuresData,
    PovertyAreaMeasuresFetcher,
    PovertyAreaMeasuresQueryParams,
)
from openbb_government_us.usda.utils import ers_poverty_area_measures as pam
from openbb_government_us.usda.utils.ers_poverty_area_measures import (
    EDITION_CATALOG,
    EDITION_OPTIONS,
    EDITIONS,
    FLAG_FIELDS,
    LEVEL_OPTIONS,
    LEVELS,
    STATE_NAMES,
    afetch_edition,
    afetch_states,
    cell_int,
    cell_str,
    edition_options,
    flag_column,
    normalize_fips,
    normalize_tract_fips,
    parse_records,
    state_options,
    tract_fips_of,
)

DEFAULT_FLAG = {
    "high_poverty": 1,
    "extreme_poverty": 0,
    "persistent_poverty": 1,
    "enduring_poverty": 2,
}

SPEC_2025 = {
    "high_poverty": {
        "c": ["1970", "1980", "1990", "2000", "2007_11", "2017_21"],
        "t": ["1970", "1980", "1990", "2000", "2007_11", "2017_21"],
    },
    "extreme_poverty": {
        "c": ["1970", "1980", "1990", "2000", "2007_11"],
        "t": ["1970", "1980", "1990", "2000", "2007_11"],
    },
    "persistent_poverty": {"c": ["2000", "2007_11"], "t": ["2000", "2007_11"]},
    "enduring_poverty": {"c": ["2007_11", "2017_21"], "t": ["2007_11", "2017_21"]},
}

SPEC_2023 = {
    "high_poverty": {
        "c": ["1970", "1980", "1990", "2000", "2007_11", "2015_19", "2017_21"],
        "t": ["1970", "1980", "1990", "2000", "2007_11", "2015_19"],
    },
    "extreme_poverty": {
        "c": ["1970", "1980", "1990", "2000", "2007_11", "2015_19", "2017_21"],
        "t": ["1970", "1980", "1990", "2000", "2007_11", "2015_19"],
    },
    "persistent_poverty": {
        "c": ["2000", "2007_11", "2015_19", "2017_21"],
        "t": ["2000", "2007_11", "2015_19"],
    },
    "enduring_poverty": {
        "c": ["2007_11", "2015_19", "2017_21"],
        "t": ["2007_11", "2015_19"],
    },
}

SPEC_2022 = {
    "high_poverty": {
        "c": ["1970", "1980", "1990", "2000", "2007_11", "2015_19"],
        "t": ["1970", "1980", "1990", "2000", "2007_11", "2015_19"],
    },
    "extreme_poverty": {
        "c": ["1970", "1980", "1990", "2000", "2007_11", "2015_19"],
        "t": ["1970", "1980", "1990", "2000", "2007_11", "2015_19"],
    },
    "persistent_poverty": {
        "c": ["2000", "2007_11", "2015_19"],
        "t": ["2000", "2007_11", "2015_19"],
    },
    "enduring_poverty": {
        "c": ["2007_11", "2015_19"],
        "t": ["2007_11", "2015_19"],
    },
}


def build_edition_csv(sep, id_header, id_rows, spec, upper_hi0711c=False):
    """Build an edition CSV from identity columns and generated flag columns."""
    flag_cols = []
    for measure, levels in spec.items():
        for letter in ("c", "t"):
            for period in levels[letter]:
                name = flag_column(measure, period, sep, letter)
                if upper_hi0711c and name == "HiPov0711c":
                    name = "HIPOV0711c"
                flag_cols.append((measure, period, letter, name))
    header = id_header + [name for *_, name in flag_cols]
    buffer = StringIO()
    writer = csv.DictWriter(buffer, fieldnames=header)
    writer.writeheader()
    for id_row in id_rows:
        overrides = id_row.get("_flags", {})
        row = {column: id_row.get(column, "") for column in id_header}
        for measure, period, letter, name in flag_cols:
            row[name] = overrides.get((measure, period, letter), DEFAULT_FLAG[measure])
        writer.writerow(row)
    return buffer.getvalue()


ID_HEADER_2025 = [
    "STUSAB",
    "fips",
    "fipstxt",
    "CountyName",
    "TractFIPS23",
    "Tract",
    "TractName",
    "Region",
    "Subreg3",
    "MetNonmet2023",
    "Beale2023",
    "Ruca2020",
    "BNA01",
]

ID_ROWS_2025 = [
    {
        "STUSAB": "AL",
        "fips": "1001",
        "fipstxt": "01001",
        "CountyName": "Autauga County, Alabama",
        "TractFIPS23": "1001020100",
        "Tract": "20100",
        "TractName": "Census Tract 201; Autauga; Alabama",
        "Region": "3",
        "Subreg3": "6",
        "MetNonmet2023": "1",
        "Beale2023": "2",
        "Ruca2020": "1",
        "BNA01": "0",
        "_flags": {
            ("high_poverty", "1970", "t"): 0,
            ("high_poverty", "2007_11", "t"): 0,
            ("high_poverty", "2017_21", "c"): 0,
            ("high_poverty", "2017_21", "t"): 1,
            ("enduring_poverty", "2017_21", "c"): 3,
        },
    },
    {
        "STUSAB": "AL",
        "fips": "1001",
        "fipstxt": "01001",
        "CountyName": "Autauga County, Alabama",
        "TractFIPS23": "1001020200",
        "Tract": "20200",
        "TractName": "Census Tract 202; Autauga; Alabama",
        "Region": "3",
        "Subreg3": "6",
        "MetNonmet2023": "1",
        "Beale2023": "2",
        "Ruca2020": "1",
        "BNA01": "0",
    },
    {"STUSAB": "", "fips": "", "CountyName": "Footnote row", "Tract": ""},
    {
        "STUSAB": "MS",
        "fips": "28051",
        "fipstxt": "28051",
        "CountyName": "Holmes County, Mississippi",
        "TractFIPS23": "28051950100",
        "Tract": "950100",
        "TractName": "Census Tract 9501; Holmes; Mississippi",
        "Region": "3",
        "Subreg3": "7",
        "MetNonmet2023": "1",
        "Beale2023": "2",
        "Ruca2020": "10",
        "BNA01": "0",
    },
]

CSV_2025 = build_edition_csv(
    "", ID_HEADER_2025, ID_ROWS_2025, SPEC_2025, upper_hi0711c=True
)

ID_HEADER_2023 = [
    "GEO_ID_CT",
    "STUSAB",
    "fips",
    "CountyName",
    "TractName",
    "Tract",
    "Region",
    "subreg3",
    "MetNonmet2023",
    "MetNonmet2013",
    "Beale2013",
    "RUCA_2010",
    "BNA01",
]

ID_ROWS_2023 = [
    {
        "GEO_ID_CT": "0500000US01001",
        "STUSAB": "AL",
        "fips": "1001",
        "CountyName": "Autauga County, Alabama",
        "TractName": "Census Tract 201, Autauga, Alabama",
        "Tract": "020100",
        "Region": "3",
        "subreg3": "6",
        "MetNonmet2023": "1",
        "MetNonmet2013": "0",
        "Beale2013": "2",
        "RUCA_2010": "1",
        "BNA01": "0",
    },
    {
        "GEO_ID_CT": "0500000US28051",
        "STUSAB": "MS",
        "fips": "28051",
        "CountyName": "Holmes County, Mississippi",
        "TractName": "Census Tract 9501, Holmes, Mississippi",
        "Tract": "950100",
        "Region": "3",
        "subreg3": "7",
        "MetNonmet2023": "",
        "MetNonmet2013": "0",
        "Beale2013": "6",
        "RUCA_2010": "10",
        "BNA01": "0",
    },
]

CSV_2023 = build_edition_csv("_", ID_HEADER_2023, ID_ROWS_2023, SPEC_2023)

ID_HEADER_2022 = [
    "GEO_ID_CT",
    "STUSAB",
    "fips",
    "fips_txt",
    "CountyName",
    "TractName",
    "Tract",
    "Region",
    "subreg3",
    "MetNonmet2013",
    "Beale2013",
    "RUCA_2010",
    "BNA01",
]

ID_ROWS_2022 = [
    {
        "GEO_ID_CT": "0500000US01001",
        "STUSAB": "AL",
        "fips": "1001",
        "fips_txt": "01001",
        "CountyName": "Autauga County, Alabama",
        "TractName": "Census Tract 201, Autauga, Alabama",
        "Tract": "020100",
        "Region": "3",
        "subreg3": "6",
        "MetNonmet2013": "1",
        "Beale2013": "2",
        "RUCA_2010": "1",
        "BNA01": "0",
    },
]

CSV_2022 = build_edition_csv("_", ID_HEADER_2022, ID_ROWS_2022, SPEC_2022)


def make_record(**overrides) -> dict:
    """Build a full canonical lookup record with optional field overrides."""
    record: dict = {
        "fips": "01001",
        "state": "AL",
        "county_name": "Autauga County, Alabama",
        "region": 3,
        "subregion": 6,
        "metro_nonmetro": 1,
        "rucc_code": 2,
        "tract_fips": None,
        "tract": None,
        "tract_name": None,
        "ruca_code": None,
        "bna": None,
    }
    for measure, periods in FLAG_FIELDS.items():
        for period in periods:
            record[f"{measure}_{period}"] = 0
    record.update(overrides)
    return record


class TestErsPovertyAreaMeasuresUtils:
    """Tests for the ers_poverty_area_measures utils module."""

    def test_catalog_contents(self):
        """The catalog holds the three editions, newest first, with vintages."""
        assert EDITIONS == ("2025", "2023", "2022")
        assert EDITION_CATALOG["2025"]["flag_sep"] == ""
        assert EDITION_CATALOG["2025"]["media"].startswith("/media/5041/")
        assert EDITION_CATALOG["2025"]["tract_fips_col"] == "TractFIPS23"
        assert EDITION_CATALOG["2025"]["beale_col"] == "Beale2023"
        assert EDITION_CATALOG["2023"]["flag_sep"] == "_"
        assert EDITION_CATALOG["2023"]["media"].startswith("/media/5043/")
        assert EDITION_CATALOG["2023"]["metro_col"] == "MetNonmet2023"
        assert EDITION_CATALOG["2023"]["tract_fips_col"] is None
        assert EDITION_CATALOG["2022"]["media"].startswith("/media/5045/")
        assert EDITION_CATALOG["2022"]["metro_col"] == "MetNonmet2013"

    def test_option_lists(self):
        """The edition, level, and state options carry label/value pairs."""
        assert edition_options() == EDITION_OPTIONS
        assert EDITION_OPTIONS[0] == {"label": "September 2025", "value": "2025"}
        assert LEVELS == ("county", "tract")
        assert LEVEL_OPTIONS[1] == {"label": "Census Tract", "value": "tract"}
        options = state_options()
        assert len(options) == 51
        assert {"label": "Wyoming", "value": "WY"} in options

    def test_state_names(self):
        """The state map covers the fifty states and DC, with no territories."""
        assert len(STATE_NAMES) == 51
        assert STATE_NAMES["DC"] == "District of Columbia"
        assert "PR" not in STATE_NAMES

    def test_cell_int(self):
        """cell_int keeps sentinels and coerces blanks and tokens to None."""
        assert cell_int("1") == 1
        assert cell_int("-1") == -1
        assert cell_int("0") == 0
        assert cell_int("3") == 3
        assert cell_int("2.0") == 2
        assert cell_int("") is None
        assert cell_int("  ") is None
        assert cell_int(None) is None
        assert cell_int("na") is None
        assert cell_int("n/a") is None
        assert cell_int("--") is None
        assert cell_int("-") is None
        assert cell_int("not a number") is None

    def test_cell_str(self):
        """cell_str strips cells and coerces blanks to None."""
        assert cell_str("  Autauga County  ") == "Autauga County"
        assert cell_str("") is None
        assert cell_str("   ") is None
        assert cell_str(None) is None

    def test_normalize_fips(self):
        """normalize_fips zero-pads numeric FIPS and falls back on non-numeric."""
        assert normalize_fips("1001") == "01001"
        assert normalize_fips("01001") == "01001"
        assert normalize_fips("1001.0") == "01001"
        assert normalize_fips("") is None
        assert normalize_fips(None) is None
        assert normalize_fips("X") == "0000X"

    def test_normalize_tract_fips(self):
        """normalize_tract_fips zero-pads to eleven digits or falls back."""
        assert normalize_tract_fips("1001020100") == "01001020100"
        assert normalize_tract_fips("28051950100") == "28051950100"
        assert normalize_tract_fips("") is None
        assert normalize_tract_fips(None) is None
        assert normalize_tract_fips("XY") == "000000000XY"

    def test_flag_column(self):
        """flag_column builds the source column for a measure, period, level."""
        assert flag_column("high_poverty", "2007_11", "", "c") == "HiPov0711c"
        assert flag_column("high_poverty", "2007_11", "_", "t") == "HiPov0711_t"
        assert flag_column("enduring_poverty", "2017_21", "", "c") == "EndurePov1721c"
        assert flag_column("persistent_poverty", "1990", "_", "c") == "PerPov90_c"

    def test_tract_fips_of_from_column(self):
        """tract_fips_of reads and pads the tract-FIPS column when present."""
        config = EDITION_CATALOG["2025"]
        assert (
            tract_fips_of(config, {"tractfips23": "1001020100"}, "01001")
            == "01001020100"
        )

    def test_tract_fips_of_derived(self):
        """tract_fips_of derives from county FIPS and tract when no column."""
        config = EDITION_CATALOG["2023"]
        assert tract_fips_of(config, {"tract": "020100"}, "01001") == "01001020100"
        assert tract_fips_of(config, {"tract": ""}, "01001") is None
        assert tract_fips_of(config, {}, "01001") is None

    def test_parse_records_county_2025(self):
        """The 2025 county level dedupes on FIPS and reads the c-columns."""
        records = parse_records(CSV_2025, "2025", "county")
        assert [record["fips"] for record in records] == ["01001", "28051"]
        autauga = records[0]
        assert autauga["state"] == "AL"
        assert autauga["county_name"] == "Autauga County, Alabama"
        assert autauga["metro_nonmetro"] == 1
        assert autauga["rucc_code"] == 2
        assert autauga["region"] == 3
        assert autauga["subregion"] == 6
        assert autauga["high_poverty_1970"] == 1
        assert autauga["high_poverty_2007_11"] == 1
        assert autauga["high_poverty_2017_21"] == 0
        assert autauga["persistent_poverty_2000"] == 1
        assert autauga["enduring_poverty_2007_11"] == 2
        assert autauga["enduring_poverty_2017_21"] == 3
        assert autauga["tract_fips"] is None
        assert autauga["tract_name"] is None
        assert autauga["ruca_code"] is None
        assert autauga["bna"] is None
        assert autauga["high_poverty_2015_19"] is None

    def test_parse_records_tract_2025(self):
        """The 2025 tract level keeps every tract and reads the t-columns."""
        records = parse_records(CSV_2025, "2025", "tract")
        assert [record["tract_fips"] for record in records] == [
            "01001020100",
            "01001020200",
            "28051950100",
        ]
        first = records[0]
        assert first["fips"] == "01001"
        assert first["tract"] == "20100"
        assert first["tract_name"] == "Census Tract 201; Autauga; Alabama"
        assert first["ruca_code"] == 1
        assert first["bna"] == 0
        assert first["high_poverty_1970"] == 0
        assert first["high_poverty_2007_11"] == 0
        assert first["high_poverty_2017_21"] == 1

    def test_parse_records_level_switches_suffix(self):
        """The same tract reads different values from the c and t columns."""
        county = parse_records(CSV_2025, "2025", "county")[0]
        tract = parse_records(CSV_2025, "2025", "tract")[0]
        assert county["high_poverty_1970"] == 1
        assert tract["high_poverty_1970"] == 0

    def test_parse_records_skips_blank_fips(self):
        """A row without a county FIPS is dropped."""
        records = parse_records(CSV_2025, "2025", "tract")
        assert all(record["fips"] for record in records)
        assert len(records) == 3

    def test_parse_records_2023_underscore_and_metro(self):
        """The 2023 edition reads _c columns and the 2023 metro definition."""
        records = parse_records(CSV_2023, "2023", "county")
        autauga = records[0]
        assert autauga["metro_nonmetro"] == 1
        assert autauga["rucc_code"] == 2
        assert autauga["high_poverty_2015_19"] == 1
        assert autauga["high_poverty_2017_21"] == 1
        assert autauga["high_poverty_2018_22"] is None
        assert autauga["high_poverty_2019_23"] is None
        holmes = records[1]
        assert holmes["metro_nonmetro"] is None

    def test_parse_records_2022_underscore_and_metro(self):
        """The 2022 edition reads the 2013 metro definition and stops at 1519."""
        records = parse_records(CSV_2022, "2022", "county")
        autauga = records[0]
        assert autauga["metro_nonmetro"] == 1
        assert autauga["rucc_code"] == 2
        assert autauga["high_poverty_2015_19"] == 1
        assert autauga["high_poverty_2017_21"] is None

    def test_afetch_edition(self, monkeypatch):
        """afetch_edition downloads the edition file and parses it."""

        async def fake_afetch_ers_file(media_path, product=None, ttl=None):
            assert media_path == EDITION_CATALOG["2025"]["media"]
            assert product == pam.PRODUCT_PAGE
            return CSV_2025.encode("utf-8-sig")

        monkeypatch.setattr(
            "openbb_government_us.usda.utils.ers_client.afetch_ers_file",
            fake_afetch_ers_file,
        )
        records = asyncio.run(afetch_edition("2025", "county"))
        assert [record["fips"] for record in records] == ["01001", "28051"]

    def test_afetch_states(self, monkeypatch):
        """afetch_states lists the edition's distinct states, labeled, sorted."""

        async def fake_afetch_edition(edition, level):
            assert level == "county"
            return [
                make_record(fips="28051", state="MS"),
                make_record(fips="01001", state="AL"),
                make_record(fips="28001", state="MS"),
                make_record(fips="99999", state=None),
            ]

        monkeypatch.setattr(pam, "afetch_edition", fake_afetch_edition)
        options = asyncio.run(afetch_states("2025"))
        assert options == [
            {"label": "Alabama", "value": "AL"},
            {"label": "Mississippi", "value": "MS"},
        ]


class TestPovertyAreaMeasures:
    """Tests for the PovertyAreaMeasures model."""

    def test_transform_query(self):
        """transform_query builds the query params model."""
        query = PovertyAreaMeasuresFetcher.transform_query(
            {"edition": "2023", "level": "tract", "state": "MS"}
        )
        assert isinstance(query, PovertyAreaMeasuresQueryParams)
        assert query.edition == "2023"
        assert query.level == "tract"
        assert query.state == "MS"

    def test_edition_defaults_and_blank(self):
        """The edition defaults to 2025 and blanks fall back."""
        assert PovertyAreaMeasuresQueryParams().edition == "2025"
        assert PovertyAreaMeasuresQueryParams(edition="").edition == "2025"
        assert PovertyAreaMeasuresQueryParams(edition=["2022"]).edition == "2022"

    def test_unknown_edition_raises(self):
        """An unknown edition raises OpenBBError listing valid choices."""
        with pytest.raises(OpenBBError, match="Invalid edition: 2099.*2025"):
            PovertyAreaMeasuresQueryParams(edition="2099")

    def test_level_defaults_and_validates(self):
        """The level defaults to county, lowercases, and takes the first."""
        assert PovertyAreaMeasuresQueryParams().level == "county"
        assert PovertyAreaMeasuresQueryParams(level="").level == "county"
        assert PovertyAreaMeasuresQueryParams(level="TRACT").level == "tract"
        assert PovertyAreaMeasuresQueryParams(level=["tract"]).level == "tract"

    def test_unknown_level_raises(self):
        """An unknown level raises OpenBBError."""
        with pytest.raises(OpenBBError, match="Invalid level: block"):
            PovertyAreaMeasuresQueryParams(level="block")

    def test_state_defaults_none_and_normalizes(self):
        """State defaults to None, uppercases, and takes the first of a list."""
        assert PovertyAreaMeasuresQueryParams().state is None
        assert PovertyAreaMeasuresQueryParams(state="").state is None
        assert PovertyAreaMeasuresQueryParams(state="   ").state is None
        assert PovertyAreaMeasuresQueryParams(state="ms").state == "MS"
        assert PovertyAreaMeasuresQueryParams(state=["ny"]).state == "NY"

    def test_unknown_state_raises(self):
        """An unknown state code raises OpenBBError."""
        with pytest.raises(OpenBBError, match="Invalid state: ZZ"):
            PovertyAreaMeasuresQueryParams(state="ZZ")

    def test_aextract_data_forwards_edition_and_level(self, monkeypatch):
        """aextract_data forwards the edition and level to afetch_edition."""
        calls: list[tuple] = []

        async def fake_afetch_edition(edition, level):
            calls.append((edition, level))
            return [make_record()]

        monkeypatch.setattr(pam, "afetch_edition", fake_afetch_edition)
        query = PovertyAreaMeasuresFetcher.transform_query(
            {"edition": "2023", "level": "tract"}
        )
        records = asyncio.run(PovertyAreaMeasuresFetcher.aextract_data(query, None))
        assert calls == [("2023", "tract")]
        assert records[0]["fips"] == "01001"

    def test_transform_data_filters_by_state(self):
        """A state filter keeps only that state's rows."""
        records = [
            make_record(fips="01001", state="AL"),
            make_record(fips="28051", state="MS"),
        ]
        query = PovertyAreaMeasuresFetcher.transform_query({"state": "MS"})
        data = PovertyAreaMeasuresFetcher.transform_data(query, records)
        assert [row.fips for row in data] == ["28051"]

    def test_transform_data_all_states_when_none(self):
        """No state filter returns every row of the edition."""
        records = [
            make_record(fips="01001", state="AL"),
            make_record(fips="28051", state="MS"),
        ]
        query = PovertyAreaMeasuresFetcher.transform_query({})
        data = PovertyAreaMeasuresFetcher.transform_data(query, records)
        assert {row.state for row in data} == {"AL", "MS"}

    def test_transform_data_sorted_by_fips_then_tract(self):
        """Rows sort by county FIPS then tract FIPS regardless of input order."""
        records = [
            make_record(fips="01001", tract_fips="01001020200"),
            make_record(fips="01001", tract_fips="01001020100"),
            make_record(fips="28051", tract_fips="28051950100"),
        ]
        query = PovertyAreaMeasuresFetcher.transform_query({"level": "tract"})
        data = PovertyAreaMeasuresFetcher.transform_data(query, records)
        assert [row.tract_fips for row in data] == [
            "01001020100",
            "01001020200",
            "28051950100",
        ]

    def test_transform_data_tract_promotes_fips(self):
        """At the tract level the pinned FIPS carries the tract identity."""
        records = [
            make_record(fips="01001", tract_fips="01001020200"),
            make_record(fips="01001", tract_fips="01001020100"),
        ]
        query = PovertyAreaMeasuresFetcher.transform_query({"level": "tract"})
        data = PovertyAreaMeasuresFetcher.transform_data(query, records)
        assert [row.fips for row in data] == ["01001020100", "01001020200"]

    def test_transform_data_county_keeps_county_fips(self):
        """At the county level the pinned FIPS stays the county FIPS."""
        records = [make_record(fips="01001", tract_fips="01001020100")]
        query = PovertyAreaMeasuresFetcher.transform_query({"level": "county"})
        data = PovertyAreaMeasuresFetcher.transform_data(query, records)
        assert data[0].fips == "01001"

    def test_transform_data_passes_through_nulls(self):
        """A row with null flags keeps them null."""
        records = [
            make_record(
                fips="01001",
                state="AL",
                metro_nonmetro=None,
                high_poverty_2015_19=None,
            )
        ]
        query = PovertyAreaMeasuresFetcher.transform_query({})
        data = PovertyAreaMeasuresFetcher.transform_data(query, records)
        assert data[0].metro_nonmetro is None
        assert data[0].high_poverty_2015_19 is None

    def test_transform_data_empty_raises(self):
        """A state with no rows raises EmptyDataError."""
        query = PovertyAreaMeasuresFetcher.transform_query({"state": "WY"})
        with pytest.raises(EmptyDataError, match="No records match"):
            PovertyAreaMeasuresFetcher.transform_data(query, [make_record(state="MS")])

    def test_columns_defs_bind_to_served_keys(self):
        """Every declared column definition binds to a served row key."""
        records = [make_record()]
        query = PovertyAreaMeasuresFetcher.transform_query({})
        data = PovertyAreaMeasuresFetcher.transform_data(query, records)
        served = set(data[0].model_dump(by_alias=True))
        schema = PovertyAreaMeasuresData.model_json_schema(
            by_alias=True, mode="serialization"
        )
        column_fields = [to_snake(key) for key in schema["properties"]]
        assert column_fields, "no column definitions generated"
        for field in column_fields:
            assert field in served, field
        assert served == set(column_fields)

    def test_no_always_empty_visible_column_on_default(self):
        """Every visible column is populated for the default county rows."""
        records = parse_records(CSV_2025, "2025", "county")
        query = PovertyAreaMeasuresFetcher.transform_query({})
        data = PovertyAreaMeasuresFetcher.transform_data(query, records)
        schema = PovertyAreaMeasuresData.model_json_schema(
            by_alias=True, mode="serialization"
        )
        hidden = {
            key
            for key, value in schema["properties"].items()
            if value.get("x-widget_config", {}).get("hide")
        }
        for key in data[0].model_dump(by_alias=True):
            if key in hidden:
                continue
            assert any(
                row.model_dump(by_alias=True)[key] is not None for row in data
            ), key

    def test_tract_only_fields_hidden(self):
        """Tract-only fields and edition-specific periods are hidden."""
        schema = PovertyAreaMeasuresData.model_json_schema(
            by_alias=True, mode="serialization"
        )
        for field in (
            "tract_fips",
            "tract",
            "tract_name",
            "ruca_code",
            "bna",
            "region",
            "subregion",
            "high_poverty_2015_19",
            "high_poverty_2019_23",
            "enduring_poverty_2017_21",
        ):
            assert schema["properties"][field]["x-widget_config"]["hide"] is True
        for field in (
            "fips",
            "high_poverty_2007_11",
            "persistent_poverty_2000",
            "enduring_poverty_2007_11",
        ):
            assert "hide" not in schema["properties"][field]["x-widget_config"]

    def test_widget_config_metadata(self):
        """The whole-widget config carries the ERS category and source."""
        config = PovertyAreaMeasuresData.model_config["json_schema_extra"][
            "x-widget_config"
        ]
        assert config["$.name"] == "USDA ERS Poverty Area Measures"
        assert config["$.category"] == "Economy"
        assert config["$.subCategory"] == "Agriculture"
        assert config["$.source"] == ["USDA", "ERS"]

    def test_fips_and_code_columns_are_text(self):
        """FIPS, tract FIPS, and the flags render as text so codes survive."""
        schema = PovertyAreaMeasuresData.model_json_schema(
            by_alias=True, mode="serialization"
        )
        for field in ("fips", "tract_fips", "high_poverty_2007_11", "rucc_code"):
            config = schema["properties"][field]["x-widget_config"]
            assert config["cellDataType"] == "text"
