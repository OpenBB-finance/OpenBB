"""Tests for the USDA ERS area and road ruggedness scales utils and model."""

import asyncio
import csv
import io

import pytest
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic.alias_generators import to_snake

from openbb_government_us.usda.models.area_and_road_ruggedness_scales import (
    AreaAndRoadRuggednessScalesData as ArsData,
    AreaAndRoadRuggednessScalesFetcher as ArsFetcher,
    AreaAndRoadRuggednessScalesQueryParams as ArsQuery,
)
from openbb_government_us.usda.utils import (
    ers_area_and_road_ruggedness_scales as ers,
)
from openbb_government_us.usda.utils.ers_area_and_road_ruggedness_scales import (
    ALL_STATES,
    CANONICAL_COLUMNS,
    DEFAULT_STATE,
    DEFAULT_VINTAGE,
    PRODUCT_PAGE,
    STATES,
    VINTAGE_CATALOG,
    VINTAGES,
    capitalize_text,
    clean_text,
    parse_csv_records,
    parse_float,
    parse_population,
    state_options,
    vintage_options,
)

HEADER_2020: list[str] = [
    "TractFIPS23", "CountyFIPS23", "CountyCode23", "CountyName23", "TractFIPS20",
    "TractCode20", "TractName20", "CountyFIPS20", "CountyCode20", "CountyName20",
    "StateFIPS20", "StateName20", "RSRegion", "RSRegionName", "PrimaryRUCA",
    "RuralityCode", "RuralityName", "Population", "LandArea", "PopDensity",
    "AreaTRI_Count", "AreaTRI_Mean", "AreaTRI_StdDev", "AreaTRI_Median",
    "AreaTRI_Min", "AreaTRI_Max", "AreaTRI_Range", "ARS", "ARSDescription",
    "RoadTRI_Count", "RoadTRI_Mean", "RoadTRI_StdDev", "RoadTRI_Median",
    "RoadTRI_Min", "RoadTRI_Max", "RoadTRI_Range", "RRS", "RRSDescription",
]  # fmt: skip

ROWS_2020: list[list] = [
    [
        "01001020100",
        "01001",
        "001",
        "Autauga County",
        "01001020100",
        "020100",
        "Census Tract 201",
        "01001",
        "001",
        "Autauga County",
        "01",
        "Alabama",
        "6",
        "Southern Coastal Plains",
        "1",
        "1",
        "Urbanized area",
        "1775",
        "3.8",
        "467.9",
        "217",
        "26.751",
        "14.542",
        "25.04",
        "4.123",
        "97.519",
        "93.396",
        "2",
        "Nearly level",
        "126",
        "21.712",
        "13.916",
        "20.445",
        "2.236",
        "96.628",
        "94.392",
        "2",
        "Nearly level",
    ],
    [
        "54001965500",
        "54001",
        "001",
        "Barbour County",
        "54001965500",
        "965500",
        "Census Tract 9655",
        "54001",
        "001",
        "Barbour County",
        "54",
        "West Virginia",
        "1",
        "Appalachian Mountains",
        "10",
        "3",
        "Rural",
        "3663",
        "131.7",
        "27.8",
        "8204",
        "77.334",
        "34.774",
        "73.665",
        "5.916",
        "222.324",
        "216.408",
        "4",
        "Moderately rugged",
        "2645",
        "36.417",
        "24.009",
        "31.78",
        "1",
        "169.505",
        "168.505",
        "3",
        "Slightly rugged",
    ],
    [
        "54045956500",
        "54045",
        "045",
        "Logan County",
        "54045956500",
        "956500",
        "Census Tract 9565",
        "54045",
        "045",
        "Logan County",
        "54",
        "West Virginia",
        "1",
        "Appalachian Mountains",
        "10",
        "3",
        "Rural",
        "2052",
        "42.6",
        "48.2",
        "2614",
        "186.368",
        "46.412",
        "191.625",
        "20.445",
        "311.182",
        "290.737",
        "6",
        "Extremely rugged",
        "486",
        "69.795",
        "39.731",
        "63.119",
        "1",
        "215.014",
        "214.014",
        "5",
        "Highly rugged",
    ],
    [
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "Nowhere",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
    ],
    [
        "02000000000",
        "02000",
        "000",
        "No State County",
        "02000000000",
        "000000",
        "Census Tract 0",
        "02000",
        "000",
        "No State County",
        "00",
        "",
        "11",
        "Alaska",
        "99",
        "99",
        "no rurality code",
        "0",
        "1.0",
        "",
        "1",
        "1.0",
        "0.0",
        "1.0",
        "1.0",
        "1.0",
        "0.0",
        "1",
        "level",
        "1",
        "1.0",
        "0.0",
        "1.0",
        "1.0",
        "1.0",
        "0.0",
        "1",
        "level",
    ],
]

HEADER_2010: list[str] = [
    "TractFIPS", "TractCode", "TractName", "CountyFIPS", "CountyCode",
    "CountyName", "StateFIPS", "State", "RSRegion", "RSRegionName", "PrimaryRUCA",
    "RuralityCode", "RuralityName", "Population", "LandArea", "PopDensity",
    "AreaTRI_Count", "AreaTRI_Mean", "AreaTRI_StdDev", "AreaTRI_Median",
    "AreaTRI_Min", "AreaTRI_Max", "AreaTRI_Range", "ARS", "ARSDescription",
    "RoadTRI_Count", "RoadTRI_Mean", "RoadTRI_StdDev", "RoadTRI_Median",
    "RoadTRI_Min", "RoadTRI_Max", "RoadTRI_Range", "RRS", "RRSDescription",
]  # fmt: skip

ROWS_2010: list[list] = [
    [
        "01001020100",
        "020100",
        "Census Tract 201",
        "01001",
        "001",
        "Autauga County",
        "01",
        "AL",
        "6",
        "Southern Coastal Plains",
        "1",
        "1",
        "urbanized area",
        "1912",
        "3.8",
        "504.8",
        "216",
        "26.834",
        "14.438",
        "25.080",
        "4.123",
        "97.519",
        "93.396",
        "2",
        "nearly level",
        "125",
        "19.866",
        "10.744",
        "19.774",
        "2.236",
        "60.481",
        "58.245",
        "2",
        "nearly level",
    ],
    [
        "54001965500",
        "965500",
        "Census Tract 9655",
        "54001",
        "001",
        "Barbour County",
        "54",
        "WV",
        "1",
        "Appalachian Mountains",
        "3",
        "2",
        "urban commuting",
        "3979",
        "131.8",
        "30.2",
        "8203",
        "77.343",
        "34.771",
        "73.655",
        "5.916",
        "222.324",
        "216.408",
        "4",
        "moderately rugged",
        "2010",
        "30.476",
        "19.792",
        "26.963",
        "1.000",
        "127.836",
        "126.836",
        "3",
        "slightly rugged",
    ],
    [
        "54045956500",
        "956500",
        "Census Tract 9565",
        "54045",
        "045",
        "Logan County",
        "54",
        "WV",
        "1",
        "Appalachian Mountains",
        "10",
        "3",
        "rural",
        "2180",
        "42.6",
        "",
        "2618",
        "186.261",
        "46.464",
        "191.587",
        "20.445",
        "311.182",
        "290.737",
        "6",
        "extremely rugged",
        "812",
        "101.791",
        "51.984",
        "95.737",
        "2.236",
        "259.609",
        "257.373",
        "5",
        "highly rugged",
    ],
    [
        "00000000000",
        "000000",
        "Census Tract X",
        "00000",
        "000",
        "Blank County",
        "00",
        "",
        "1",
        "Appalachian Mountains",
        "1",
        "1",
        "urbanized area",
        "1",
        "1.0",
        "1.0",
        "1",
        "1.0",
        "0.0",
        "1.0",
        "1.0",
        "1.0",
        "0.0",
        "1",
        "level",
        "1",
        "1.0",
        "0.0",
        "1.0",
        "1.0",
        "1.0",
        "0.0",
        "1",
        "level",
    ],
]


def _to_csv(header: list[str], rows: list[list]) -> str:
    """Serialize a header and rows to CSV text."""
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(header)
    writer.writerows(rows)
    return buffer.getvalue()


CSV_2020 = _to_csv(HEADER_2020, ROWS_2020)
CSV_2010 = _to_csv(HEADER_2010, ROWS_2010)


class TestErsAreaAndRoadRuggednessScalesUtils:
    """Tests for the ers area and road ruggedness scales utils module."""

    def test_catalog(self):
        """The catalog points at the two CSV vintages with their media paths."""
        assert list(VINTAGE_CATALOG) == ["2020", "2010"]
        assert VINTAGES == ("2020", "2010")
        assert DEFAULT_VINTAGE == "2020"
        assert DEFAULT_STATE == "WV"
        assert (
            VINTAGE_CATALOG["2020"]["media"]
            == "/media/5414/2020-area-and-road-ruggedness-scales.csv"
        )
        assert (
            VINTAGE_CATALOG["2010"]["media"]
            == "/media/5412/area-and-road-ruggedness-scales.csv"
        )
        assert VINTAGE_CATALOG["2020"]["state_kind"] == "name"
        assert VINTAGE_CATALOG["2010"]["state_kind"] == "postal"
        assert VINTAGE_CATALOG["2020"]["identifiers"]["tract_fips"] == "TractFIPS20"
        assert VINTAGE_CATALOG["2010"]["identifiers"]["tract_fips"] == "TractFIPS"
        assert PRODUCT_PAGE.endswith("area-and-road-ruggedness-scales")

    def test_canonical_columns(self):
        """The canonical schema is thirty-three keys and carries no vintage."""
        assert len(CANONICAL_COLUMNS) == 33
        assert CANONICAL_COLUMNS[0] == "tract_fips"
        assert CANONICAL_COLUMNS[-1] == "rrs_description"
        assert "vintage" not in CANONICAL_COLUMNS
        assert "state" in CANONICAL_COLUMNS
        assert "state_name" in CANONICAL_COLUMNS
        assert len(set(CANONICAL_COLUMNS)) == len(CANONICAL_COLUMNS)

    def test_states(self):
        """The state set is the fifty states and the District of Columbia."""
        assert len(STATES) == 51
        assert "DC" in STATES
        assert "PR" not in STATES
        assert frozenset(STATES) == ALL_STATES

    def test_vintage_options(self):
        """The vintage options are labeled newest-first."""
        options = vintage_options()
        assert [opt["value"] for opt in options] == ["2020", "2010"]
        assert all(opt["label"] == opt["value"] for opt in options)

    def test_state_options(self):
        """State options cover the same 51 states on both vintages, full labels."""
        opts_2020 = state_options("2020")
        opts_2010 = state_options("2010")
        assert [opt["value"] for opt in opts_2020] == list(STATES)
        assert [opt["value"] for opt in opts_2010] == list(STATES)
        assert state_options("bogus") == state_options(DEFAULT_VINTAGE)
        wv = next(opt for opt in opts_2020 if opt["value"] == "WV")
        assert wv["label"] == "West Virginia"
        dc = next(opt for opt in opts_2020 if opt["value"] == "DC")
        assert dc["label"] == "District of Columbia"

    def test_clean_text(self):
        """Text cleaning strips whitespace and maps blanks and nan to None."""
        assert clean_text("West Virginia") == "West Virginia"
        assert clean_text("  54  ") == "54"
        assert clean_text(6) == "6"
        assert clean_text(None) is None
        assert clean_text("") is None
        assert clean_text("   ") is None
        assert clean_text("nan") is None

    def test_capitalize_text(self):
        """Sentence-casing unifies lowercase and title-case labels, blanks None."""
        assert capitalize_text("nearly level") == "Nearly level"
        assert capitalize_text("Nearly level") == "Nearly level"
        assert capitalize_text("urban commuting") == "Urban commuting"
        assert capitalize_text("no rurality code") == "No rurality code"
        assert capitalize_text("") is None
        assert capitalize_text(None) is None

    def test_parse_population(self):
        """Integer parsing handles digits, thousands, and float fallbacks."""
        assert parse_population("1775") == 1775
        assert parse_population("1,775") == 1775
        assert parse_population("1775.0") == 1775
        assert parse_population(3663) == 3663
        assert parse_population(None) is None
        assert parse_population("") is None
        assert parse_population("na") is None
        assert parse_population("abc") is None

    def test_parse_float(self):
        """Float parsing preserves full precision and maps blanks to None."""
        assert parse_float("186.368") == 186.368
        assert parse_float("290.737") == 290.737
        assert parse_float("1,234.5") == 1234.5
        assert parse_float(48.2) == 48.2
        assert parse_float(None) is None
        assert parse_float("") is None
        assert parse_float("n/a") is None
        assert parse_float("abc") is None

    def test_parse_csv_records_2020_name_vintage(self):
        """The 2020 vintage derives postal codes from the full state name."""
        records = parse_csv_records(CSV_2020, "2020")
        assert [record["tract_fips"] for record in records] == [
            "01001020100",
            "54001965500",
            "54045956500",
            "02000000000",
        ]
        al = records[0]
        assert set(al) == set(CANONICAL_COLUMNS)
        assert al["state"] == "AL"
        assert al["state_name"] == "Alabama"
        assert al["county_name"] == "Autauga County"
        assert al["rurality_name"] == "Urbanized area"
        assert al["ars"] == "2"
        assert al["ars_description"] == "Nearly level"
        assert al["population"] == 1775
        assert isinstance(al["population"], int)
        assert al["land_area"] == 3.8
        assert al["area_tri_mean"] == 26.751
        assert al["area_tri_count"] == 217
        wv = records[2]
        assert wv["state"] == "WV"
        assert wv["ars"] == "6"
        assert wv["ars_description"] == "Extremely rugged"
        assert wv["rrs"] == "5"
        assert wv["rrs_description"] == "Highly rugged"
        assert wv["area_tri_max"] == 311.182
        blank_state = records[3]
        assert blank_state["state"] is None
        assert blank_state["state_name"] is None
        assert blank_state["rurality_name"] == "No rurality code"

    def test_parse_csv_records_2010_postal_vintage(self):
        """The 2010 vintage derives the full name from the postal code."""
        records = parse_csv_records(CSV_2010, "2010")
        assert [record["tract_fips"] for record in records] == [
            "01001020100",
            "54001965500",
            "54045956500",
            "00000000000",
        ]
        al = records[0]
        assert set(al) == set(CANONICAL_COLUMNS)
        assert al["state"] == "AL"
        assert al["state_name"] == "Alabama"
        assert al["rurality_name"] == "Urbanized area"
        assert al["ars_description"] == "Nearly level"
        assert al["rrs_description"] == "Nearly level"
        logan = records[2]
        assert logan["state"] == "WV"
        assert logan["state_name"] == "West Virginia"
        assert logan["rurality_name"] == "Rural"
        assert logan["pop_density"] is None
        assert logan["ars_description"] == "Extremely rugged"
        assert logan["rrs_description"] == "Highly rugged"
        blank_state = records[3]
        assert blank_state["state"] is None
        assert blank_state["state_name"] is None

    def test_parse_csv_records_identical_schema_across_vintages(self):
        """Both vintages normalize the shared tract to one identical schema."""
        r2020 = parse_csv_records(CSV_2020, "2020")
        r2010 = parse_csv_records(CSV_2010, "2010")
        tract_2020 = next(r for r in r2020 if r["tract_fips"] == "54045956500")
        tract_2010 = next(r for r in r2010 if r["tract_fips"] == "54045956500")
        assert set(tract_2020) == set(tract_2010) == set(CANONICAL_COLUMNS)
        assert tract_2020["state"] == tract_2010["state"] == "WV"
        assert tract_2020["state_name"] == tract_2010["state_name"] == "West Virginia"
        assert tract_2020["ars"] == tract_2010["ars"] == "6"

    def test_parse_csv_records_skips_blank_tract(self):
        """Rows with a blank tract FIPS emit no record."""
        text = _to_csv(HEADER_2020, [ROWS_2020[3], ROWS_2020[0]])
        records = parse_csv_records(text, "2020")
        assert [record["tract_fips"] for record in records] == ["01001020100"]

    def test_afetch_vintage(self, monkeypatch):
        """A vintage fetches through the cache and decodes the utf-8-sig CSV."""
        calls = []

        async def fake_afetch_ers_file(media, product=None, ttl=None):
            calls.append((media, product))
            return ("﻿" + CSV_2020).encode("utf-8")

        monkeypatch.setattr(
            "openbb_government_us.usda.utils.ers_client.afetch_ers_file",
            fake_afetch_ers_file,
        )
        records = asyncio.run(ers.afetch_vintage("2020"))
        assert calls == [(VINTAGE_CATALOG["2020"]["media"], PRODUCT_PAGE)]
        assert {record["state"] for record in records if record["state"]} == {
            "AL",
            "WV",
        }


class TestAreaAndRoadRuggednessScales:
    """Tests for the AreaAndRoadRuggednessScales model."""

    def _rows_2020(self):
        """Parse the 2020 fixture into canonical records."""
        return parse_csv_records(CSV_2020, "2020")

    def _rows_2010(self):
        """Parse the 2010 fixture into canonical records."""
        return parse_csv_records(CSV_2010, "2010")

    def test_transform_query_defaults(self):
        """transform_query applies the vintage and state defaults."""
        query = ArsFetcher.transform_query({})
        assert isinstance(query, ArsQuery)
        assert query.vintage == "2020"
        assert query.state == "WV"

    def test_blank_values_fall_back_to_defaults(self):
        """Blank vintage and state normalize to their defaults."""
        query = ArsQuery(vintage="", state="")
        assert query.vintage == "2020"
        assert query.state == "WV"

    def test_list_valued_params_take_first(self):
        """List-valued vintage and state inputs take the first element."""
        query = ArsQuery(vintage=["2010"], state=["co"])
        assert query.vintage == "2010"
        assert query.state == "CO"

    def test_invalid_vintage_raises(self):
        """An unknown vintage raises OpenBBError."""
        with pytest.raises(OpenBBError, match="Invalid vintage: 1999"):
            ArsQuery(vintage="1999")

    def test_invalid_state_raises(self):
        """An unknown state raises OpenBBError."""
        with pytest.raises(OpenBBError, match="Invalid state: ZZ"):
            ArsQuery(state="ZZ")

    def test_state_uppercases(self):
        """State input is upper-cased and trimmed."""
        assert ArsQuery(state="wv").state == "WV"
        assert ArsQuery(state=" co ").state == "CO"

    def test_aextract_data_returns_records(self, monkeypatch):
        """aextract_data returns the selected vintage's parsed records."""

        async def fake_afetch_vintage(vintage):
            return parse_csv_records(
                CSV_2010 if vintage == "2010" else CSV_2020, vintage
            )

        monkeypatch.setattr(ers, "afetch_vintage", fake_afetch_vintage)
        query = ArsFetcher.transform_query({"vintage": "2010", "state": "WV"})
        records = asyncio.run(ArsFetcher.aextract_data(query, None))
        assert {record["state"] for record in records if record["state"]} == {
            "AL",
            "WV",
        }

    def test_transform_data_scopes_to_state_and_sorts(self):
        """The default view keeps one state and sorts by tract FIPS ascending."""
        query = ArsFetcher.transform_query({"vintage": "2020", "state": "WV"})
        data = ArsFetcher.transform_data(query, self._rows_2020())
        assert {row.state for row in data} == {"WV"}
        assert [row.tract_fips for row in data] == ["54001965500", "54045956500"]

    def test_transform_data_empty_state_raises(self):
        """A vintage lacking the requested state raises EmptyDataError."""
        query = ArsQuery(vintage="2020", state="CO")
        with pytest.raises(EmptyDataError):
            ArsFetcher.transform_data(query, self._rows_2020())

    def test_lookup_is_one_row_per_tract_with_no_vintage_column(self):
        """Every row is a tract lookup with the canonical keys, no vintage key."""
        query = ArsFetcher.transform_query({"vintage": "2020", "state": "WV"})
        data = ArsFetcher.transform_data(query, self._rows_2020())
        assert len(data) == 2
        served = set(data[0].model_dump(by_alias=True))
        assert served == set(CANONICAL_COLUMNS)
        assert "vintage" not in served

    def test_both_vintages_serve_identical_schema(self):
        """The 2010 vintage serves the byte-identical schema to the 2020 vintage."""
        q2020 = ArsQuery(vintage="2020", state="WV")
        q2010 = ArsQuery(vintage="2010", state="WV")
        s2020 = set(
            ArsFetcher.transform_data(q2020, self._rows_2020())[0].model_dump(
                by_alias=True
            )
        )
        s2010 = set(
            ArsFetcher.transform_data(q2010, self._rows_2010())[0].model_dump(
                by_alias=True
            )
        )
        assert s2020 == s2010 == set(CANONICAL_COLUMNS)

    def test_columns_defs_bind_to_served_keys(self):
        """Every declared column definition binds to a served record key."""
        declared = set()
        for name, field in ArsData.model_fields.items():
            alias = field.serialization_alias or name
            extra = field.json_schema_extra
            config = extra.get("x-widget_config", {}) if isinstance(extra, dict) else {}
            if config.get("exclude"):
                continue
            declared.add(to_snake(alias))
        assert declared == set(CANONICAL_COLUMNS)
        query = ArsFetcher.transform_query({"vintage": "2020", "state": "WV"})
        data = ArsFetcher.transform_data(query, self._rows_2020())
        served = set()
        for row in data:
            served.update(row.model_dump(by_alias=True))
        assert declared == served

    def test_no_dead_constant_column(self):
        """Every served key carries a declared column definition."""
        declared = set(CANONICAL_COLUMNS)
        query = ArsFetcher.transform_query({"vintage": "2020", "state": "WV"})
        data = ArsFetcher.transform_data(query, self._rows_2020())
        for row in data:
            for key in row.model_dump(by_alias=True):
                assert to_snake(key) in declared

    def test_param_scoping_options(self):
        """Choice params are single-select with real labels and dependent states."""
        extra = ArsQuery.__json_schema_extra__
        vintage = extra["vintage"]["x-widget_config"]
        assert vintage["label"] == "Vintage"
        assert vintage["multiSelect"] is False and vintage["multiple"] is False
        assert vintage["value"] == "2020"
        assert [opt["value"] for opt in vintage["options"]] == ["2020", "2010"]
        state = extra["state"]["x-widget_config"]
        assert state["label"] == "State"
        assert state["multiSelect"] is False and state["multiple"] is False
        assert state["type"] == "endpoint"
        assert state["value"] == "WV"
        assert state["optionsEndpoint"].endswith("/usda/area_road_ruggedness_states")
        assert state["optionsParams"] == {"vintage": "$vintage"}

    def test_widget_config_and_column_headers(self):
        """The whole-widget config and per-field headers are populated."""
        widget = ArsData.model_config["json_schema_extra"]["x-widget_config"]
        assert widget["$.name"] == "USDA ERS Area and Road Ruggedness Scales"
        assert widget["$.category"] == "Economy"
        assert widget["$.subCategory"] == "Agriculture"
        assert widget["$.source"] == ["USDA", "ERS"]
        fields = ArsData.model_fields
        for name in ("tract_fips", "county_name", "state", "state_name"):
            assert fields[name].json_schema_extra["x-widget_config"]["pinned"] == "left"
        for name in (
            "tract_fips",
            "county_fips",
            "state_fips",
            "state",
            "ars",
            "rrs",
            "rs_region",
            "primary_ruca",
            "rurality_code",
        ):
            config = fields[name].json_schema_extra["x-widget_config"]
            assert config["cellDataType"] == "text"
        for name in (
            "population",
            "land_area",
            "pop_density",
            "area_tri_mean",
            "road_tri_median",
        ):
            config = fields[name].json_schema_extra["x-widget_config"]
            assert config["cellDataType"] == "number"

    def test_optional_dims_are_hidden(self):
        """The plumbing and granular statistic fields are hidden, not visible."""
        fields = ArsData.model_fields
        hidden = {
            "tract_name",
            "county_fips",
            "state_fips",
            "rs_region",
            "primary_ruca",
            "rurality_code",
            "area_tri_count",
            "area_tri_std_dev",
            "area_tri_min",
            "area_tri_max",
            "area_tri_range",
            "road_tri_count",
            "road_tri_std_dev",
            "road_tri_min",
            "road_tri_max",
            "road_tri_range",
        }
        for name in hidden:
            config = fields[name].json_schema_extra["x-widget_config"]
            assert config.get("hide") is True
        visible = {
            "tract_fips",
            "county_name",
            "state",
            "state_name",
            "rs_region_name",
            "rurality_name",
            "population",
            "land_area",
            "pop_density",
            "area_tri_mean",
            "area_tri_median",
            "ars",
            "ars_description",
            "road_tri_mean",
            "road_tri_median",
            "rrs",
            "rrs_description",
        }
        for name in visible:
            config = fields[name].json_schema_extra["x-widget_config"]
            assert config.get("hide") is not True

    def test_null_token_mixin_coerces_placeholder(self):
        """The Data model coerces placeholder tokens to None but keeps columns."""
        row = ArsData.model_validate(
            {"tract_fips": "54045956500", "state": "WV", "pop_density": ""}
        )
        dumped = row.model_dump(by_alias=True)
        assert dumped["tract_fips"] == "54045956500"
        assert dumped["pop_density"] is None
        assert "pop_density" in dumped

    def test_numeric_values_are_full_precision(self):
        """Terrain statistics carry their full unrounded precision."""
        query = ArsFetcher.transform_query({"vintage": "2020", "state": "WV"})
        data = ArsFetcher.transform_data(query, self._rows_2020())
        logan = next(row for row in data if row.tract_fips == "54045956500")
        assert logan.area_tri_mean == 186.368
        assert logan.area_tri_range == 290.737
        assert logan.road_tri_mean == 69.795
        assert logan.population == 2052
