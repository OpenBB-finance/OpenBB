"""Tests for the USDA ERS commuting zones and labor market areas utils and model."""

import asyncio
import io
import zipfile

import numpy as np
import pandas as pd
import pytest
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic.alias_generators import to_snake

from openbb_government_us.usda.models.commuting_zones_and_labor_market_areas import (
    CommutingZonesAndLaborMarketAreasData,
    CommutingZonesAndLaborMarketAreasFetcher,
    CommutingZonesAndLaborMarketAreasQueryParams,
)
from openbb_government_us.usda.utils import ers_commuting_zones_and_labor_market_areas
from openbb_government_us.usda.utils.ers_commuting_zones_and_labor_market_areas import (
    RECORD_KEYS,
    STATE_FIPS,
    STATE_NAMES,
    VINTAGE_FILES,
    _beale,
    _blank_record,
    _code,
    _int,
    _is_missing,
    _msa_code,
    _num,
    _padded,
    _text,
    extract_inner_csv,
    parse_1980_1990,
    parse_2000,
    parse_2020,
    parse_preliminary_2020,
    state_name,
)

SAMPLE_2020_CSV = (
    "FIPStxt,CountyName,StateName,CZ2020,CZName,CZContainment,CZAvgContainment\n"
    '01001,Autauga County,Alabama,1,"Montgomery, AL",91.34,89.95\n'
    '01003,Baldwin County,Alabama,2,"Mobile, AL",92.97,84.86\n'
    '99999,Testville County,Testland,7,"Test, TL",50.0,60.0\n'
    ",,,,,,\n"
)

SAMPLE_PRELIM_CSV = (
    "FIPStxt,State,CountyName,PreliminaryCZ2020\n"
    "01001,AL,Autauga County,1\n"
    "01003,AL,Baldwin County,2\n"
    ",,,\n"
)


def frame_2000() -> pd.DataFrame:
    """Build a synthetic 2000 workbook frame with legacy xlrd-style dtypes."""
    return pd.DataFrame(
        {
            "FIPS": [1001, 1005, 48001, None],
            "Commuting Zone ID, 2000": [60, 20, 500, 0],
            "Commuting Zone ID, 1990": [11101.0, 10301.0, float("nan"), 0.0],
            "Commuting Zone ID, 1980": [28101.0, 28801.0, 30101.0, 0.0],
            "County name": ["Autauga County", "Barbour County", "Anderson County", ""],
            "Metropolitan area, 2003": [
                "Montgomery, AL Metropolitan Statistical Area",
                float("nan"),
                "Palestine, TX Micropolitan Statistical Area",
                float("nan"),
            ],
            "County population 2000": [43671, 29038, 55109, 0],
            "Commuting zone population 2000": [448828.0, 43350.0, 120000.0, 0.0],
        }
    )


def frame_1980_1990() -> pd.DataFrame:
    """Build a synthetic 1980/1990 workbook frame with legacy xlrd-style dtypes."""
    return pd.DataFrame(
        {
            "County FIPS Code": [1001, 1005, 48001, None],
            "CZ90": [11101, 10301, 30101, 0],
            "County name": ["Autauga County", "Barbour County", "Anderson County", ""],
            "Distance": [0.963, 0.976, 0.9, 0.0],
            "Population 1990": [34222, 25417, 48024, 0],
            "CZ80": [28101.0, 28801.0, 30101.0, 0.0],
            "Rural-urban Continuum Code 1993 (Beale Code)": ["2", ".", "6", "."],
            "MSA 1993": [5240, 0, 6200, 0],
            "MSA name": [
                "Montgomery, AL MSA",
                float("nan"),
                "Palestine, TX",
                float("nan"),
            ],
            "State place code": [151000, 124568, 4855356, 0],
            "Name of largest place in commuting zone": [
                "Montgomery city, AL",
                "Eufaula city, AL",
                "Palestine city, TX",
                "",
            ],
        }
    )


class TestErsCommutingZonesUtils:
    """Tests for the ers_commuting_zones_and_labor_market_areas utils module."""

    def test_vintage_catalog(self):
        """The catalog holds the four vintages with unique media paths."""
        assert list(VINTAGE_FILES) == [
            "2020",
            "preliminary_2020",
            "2000",
            "1980_1990",
        ]
        paths = [config["media_path"] for config in VINTAGE_FILES.values()]
        assert len(set(paths)) == 4
        assert VINTAGE_FILES["2020"]["format"] == "csv"
        assert VINTAGE_FILES["preliminary_2020"]["format"] == "zip_csv"
        assert VINTAGE_FILES["2000"]["format"] == "xls"
        assert VINTAGE_FILES["1980_1990"]["sheet"] == "CZLMA903"

    def test_state_fips_and_names(self):
        """State names are unique, sorted, and include DC and Puerto Rico."""
        assert STATE_FIPS["01"] == "Alabama"
        assert STATE_FIPS["48"] == "Texas"
        assert STATE_FIPS["72"] == "Puerto Rico"
        assert STATE_FIPS["11"] == "District of Columbia"
        assert list(STATE_NAMES) == sorted(STATE_NAMES)
        assert len(set(STATE_NAMES)) == len(STATE_NAMES)
        assert "Puerto Rico" in STATE_NAMES

    def test_state_name(self):
        """state_name maps a FIPS prefix to a full name, unknown prefix None."""
        assert state_name("01001") == "Alabama"
        assert state_name("48001") == "Texas"
        assert state_name("99999") is None

    def test_is_missing(self):
        """Blank, None, and NaN cells are missing; other values are not."""
        assert _is_missing(None) is True
        assert _is_missing(float("nan")) is True
        assert _is_missing("   ") is True
        assert _is_missing("") is True
        assert _is_missing("x") is False
        assert _is_missing(0) is False
        assert _is_missing(1.5) is False

    def test_blank_record(self):
        """A blank record holds every union key set to None."""
        record = _blank_record()
        assert set(record) == set(RECORD_KEYS)
        assert all(value is None for value in record.values())

    def test_text(self):
        """_text strips strings and maps blanks and NaN to None."""
        assert _text("  Autauga County ") == "Autauga County"
        assert _text("") is None
        assert _text(float("nan")) is None
        assert _text(None) is None

    def test_code(self):
        """_code renders int, float, and string codes without a decimal."""
        assert _code(60) == "60"
        assert _code(11101.0) == "11101"
        assert _code("28101") == "28101"
        assert _code("60.0") == "60"
        assert _code(float("nan")) is None
        assert _code("") is None
        assert _code(None) is None

    def test_padded(self):
        """_padded left-pads integer-like codes and passes None through."""
        assert _padded(1001, 5) == "01001"
        assert _padded(151000, 7) == "0151000"
        assert _padded(float("nan"), 5) is None

    def test_msa_code(self):
        """_msa_code pads to four digits and treats all-zero as no MSA."""
        assert _msa_code(5240) == "5240"
        assert _msa_code(0) is None
        assert _msa_code(float("nan")) is None

    def test_beale(self):
        """_beale keeps digit codes and coerces '.' and blanks to None."""
        assert _beale("2") == "2"
        assert _beale("6.0") == "6"
        assert _beale(".") is None
        assert _beale(float("nan")) is None
        assert _beale("") is None

    def test_num_and_int(self):
        """_num parses floats; _int truncates counts; both handle missing."""
        assert _num("0.963") == 0.963
        assert _num(448828.0) == 448828.0
        assert _num("abc") is None
        assert _num(float("nan")) is None
        assert _int(448828.0) == 448828
        assert _int("43671") == 43671
        assert _int(None) is None
        assert _num(np.int64(5)) == 5.0
        assert _int(np.float64(43671.0)) == 43671

    def test_parse_2020(self):
        """The 2020 CSV parses to county records, blanks skipped."""
        records = parse_2020(SAMPLE_2020_CSV)
        assert len(records) == 3
        assert records[0] == {
            **_blank_record(),
            "fips": "01001",
            "state": "Alabama",
            "county_name": "Autauga County",
            "commuting_zone": "1",
            "commuting_zone_name": "Montgomery, AL",
            "cz_containment": 91.34,
            "cz_avg_containment": 89.95,
        }
        assert records[2]["state"] == "Testland"

    def test_parse_preliminary_2020(self):
        """The preliminary 2020 CSV parses with state derived from FIPS."""
        records = parse_preliminary_2020(SAMPLE_PRELIM_CSV)
        assert len(records) == 2
        assert records[0]["fips"] == "01001"
        assert records[0]["state"] == "Alabama"
        assert records[0]["commuting_zone"] == "1"
        assert records[0]["commuting_zone_name"] is None

    def test_parse_2000(self, monkeypatch):
        """The 2000 workbook parses with crosswalk codes and populations."""
        monkeypatch.setattr(pd, "read_excel", lambda *a, **k: frame_2000())
        records = parse_2000(b"ignored")
        assert len(records) == 3
        assert records[0] == {
            **_blank_record(),
            "fips": "01001",
            "state": "Alabama",
            "county_name": "Autauga County",
            "commuting_zone": "60",
            "cz_1990": "11101",
            "cz_1980": "28101",
            "metro_area": "Montgomery, AL Metropolitan Statistical Area",
            "county_population": 43671,
            "commuting_zone_population": 448828,
        }
        assert records[1]["metro_area"] is None
        assert records[2]["fips"] == "48001"
        assert records[2]["cz_1990"] is None

    def test_parse_1980_1990(self, monkeypatch):
        """The 1980/1990 workbook parses codes, Beale, MSA, and place codes."""
        monkeypatch.setattr(pd, "read_excel", lambda *a, **k: frame_1980_1990())
        records = parse_1980_1990(b"ignored")
        assert len(records) == 3
        assert records[0] == {
            **_blank_record(),
            "fips": "01001",
            "state": "Alabama",
            "county_name": "Autauga County",
            "commuting_zone": "11101",
            "cz_1980": "28101",
            "commuting_zone_name": "Montgomery city, AL",
            "county_population": 34222,
            "distance": 0.963,
            "beale_code": "2",
            "msa_code": "5240",
            "msa_name": "Montgomery, AL MSA",
            "place_code": "0151000",
        }
        assert records[1]["beale_code"] is None
        assert records[1]["msa_code"] is None
        assert records[1]["msa_name"] is None
        assert records[2]["place_code"] == "4855356"

    def test_extract_inner_csv(self):
        """extract_inner_csv reads the matching CSV member from a zip."""
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w") as archive:
            archive.writestr("README-preliminary-2020-commuting-zones.md", "notes")
            archive.writestr(
                "preliminary-2020-commuting-zones.csv",
                SAMPLE_PRELIM_CSV.encode("utf-8-sig"),
            )
        text = extract_inner_csv(buffer.getvalue(), "preliminary-2020-commuting-zones")
        assert text.startswith("FIPStxt,State,CountyName,PreliminaryCZ2020")

    def test_afetch_vintage_csv(self, monkeypatch):
        """afetch_vintage fetches and parses the 2020 CSV through the cache."""
        calls = []

        async def fake_afetch_ers_file(media_path, product=None, ttl=None):
            calls.append((media_path, product))
            return SAMPLE_2020_CSV.encode("utf-8-sig")

        monkeypatch.setattr(
            "openbb_government_us.usda.utils.ers_client.afetch_ers_file",
            fake_afetch_ers_file,
        )
        records = asyncio.run(
            ers_commuting_zones_and_labor_market_areas.afetch_vintage("2020")
        )
        assert calls == [
            (
                "/media/6968/2020-commuting-zones.csv",
                ers_commuting_zones_and_labor_market_areas.PRODUCT_PAGE,
            )
        ]
        assert records[0]["commuting_zone"] == "1"

    def test_afetch_vintage_zip(self, monkeypatch):
        """afetch_vintage extracts and parses the preliminary 2020 zip."""
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w") as archive:
            archive.writestr(
                "preliminary-2020-commuting-zones.csv",
                SAMPLE_PRELIM_CSV.encode("utf-8-sig"),
            )

        async def fake_afetch_ers_file(media_path, product=None, ttl=None):
            return buffer.getvalue()

        monkeypatch.setattr(
            "openbb_government_us.usda.utils.ers_client.afetch_ers_file",
            fake_afetch_ers_file,
        )
        records = asyncio.run(
            ers_commuting_zones_and_labor_market_areas.afetch_vintage(
                "preliminary_2020"
            )
        )
        assert [record["fips"] for record in records] == ["01001", "01003"]

    def test_afetch_vintage_xls_2000(self, monkeypatch):
        """afetch_vintage dispatches the 2000 vintage to the workbook parser."""

        async def fake_afetch_ers_file(media_path, product=None, ttl=None):
            return b"xls-bytes"

        monkeypatch.setattr(
            "openbb_government_us.usda.utils.ers_client.afetch_ers_file",
            fake_afetch_ers_file,
        )
        monkeypatch.setattr(pd, "read_excel", lambda *a, **k: frame_2000())
        records = asyncio.run(
            ers_commuting_zones_and_labor_market_areas.afetch_vintage("2000")
        )
        assert records[0]["commuting_zone"] == "60"

    def test_afetch_vintage_xls_1980_1990(self, monkeypatch):
        """afetch_vintage dispatches the 1980/1990 vintage to its parser."""

        async def fake_afetch_ers_file(media_path, product=None, ttl=None):
            return b"xls-bytes"

        monkeypatch.setattr(
            "openbb_government_us.usda.utils.ers_client.afetch_ers_file",
            fake_afetch_ers_file,
        )
        monkeypatch.setattr(pd, "read_excel", lambda *a, **k: frame_1980_1990())
        records = asyncio.run(
            ers_commuting_zones_and_labor_market_areas.afetch_vintage("1980_1990")
        )
        assert records[0]["beale_code"] == "2"


def make_record(**overrides) -> dict:
    """Build a parsed county record with optional field overrides."""
    record = _blank_record()
    record.update(
        fips="01001",
        state="Alabama",
        county_name="Autauga County",
        commuting_zone="1",
    )
    record.update(overrides)
    return record


class TestCommutingZonesAndLaborMarketAreas:
    """Tests for the CommutingZonesAndLaborMarketAreas model."""

    def test_transform_query(self):
        """transform_query builds the query params model."""
        query = CommutingZonesAndLaborMarketAreasFetcher.transform_query(
            {"vintage": "2000", "state": "Texas"}
        )
        assert isinstance(query, CommutingZonesAndLaborMarketAreasQueryParams)
        assert query.vintage == "2000"
        assert query.state == "Texas"

    def test_vintage_defaults_to_2020(self):
        """The vintage defaults to 2020 and state defaults to None."""
        query = CommutingZonesAndLaborMarketAreasQueryParams()
        assert query.vintage == "2020"
        assert query.state is None

    def test_vintage_accepts_list_and_blank(self):
        """A list vintage takes the first element, blanks fall back to 2020."""
        assert (
            CommutingZonesAndLaborMarketAreasQueryParams(vintage=["2000"]).vintage
            == "2000"
        )
        assert (
            CommutingZonesAndLaborMarketAreasQueryParams(vintage="").vintage == "2020"
        )

    def test_unknown_vintage_raises(self):
        """Unknown vintages raise OpenBBError listing valid choices."""
        with pytest.raises(OpenBBError, match="Invalid vintage: 1975.*2020"):
            CommutingZonesAndLaborMarketAreasQueryParams(vintage="1975")

    def test_state_blank_list_and_canonical(self):
        """State normalizes blanks to None and matches names case-insensitively."""
        assert CommutingZonesAndLaborMarketAreasQueryParams(state="").state is None
        assert CommutingZonesAndLaborMarketAreasQueryParams(state=None).state is None
        assert (
            CommutingZonesAndLaborMarketAreasQueryParams(state="texas").state == "Texas"
        )
        assert (
            CommutingZonesAndLaborMarketAreasQueryParams(state=["new york"]).state
            == "New York"
        )

    def test_unknown_state_raises(self):
        """Unknown states raise OpenBBError listing valid choices."""
        with pytest.raises(OpenBBError, match="Invalid state: Neverland.*Alabama"):
            CommutingZonesAndLaborMarketAreasQueryParams(state="Neverland")

    def test_aextract_fetches_selected_vintage(self, monkeypatch):
        """aextract_data fetches the selected vintage's records."""
        captured = {}

        async def fake_afetch_vintage(vintage):
            captured["vintage"] = vintage
            return [make_record()]

        monkeypatch.setattr(
            ers_commuting_zones_and_labor_market_areas,
            "afetch_vintage",
            fake_afetch_vintage,
        )
        query = CommutingZonesAndLaborMarketAreasFetcher.transform_query(
            {"vintage": "2000"}
        )
        records = asyncio.run(
            CommutingZonesAndLaborMarketAreasFetcher.aextract_data(query, None)
        )
        assert captured["vintage"] == "2000"
        assert records[0]["fips"] == "01001"

    def test_transform_data_lookup_rows(self):
        """Each county is one row carrying its classification codes."""
        records = [
            make_record(
                commuting_zone_name="Montgomery, AL",
                cz_containment=91.34,
                cz_avg_containment=89.95,
            )
        ]
        query = CommutingZonesAndLaborMarketAreasFetcher.transform_query({})
        data = CommutingZonesAndLaborMarketAreasFetcher.transform_data(query, records)
        assert len(data) == 1
        dumped = data[0].model_dump(by_alias=True)
        assert dumped["fips"] == "01001"
        assert dumped["state"] == "Alabama"
        assert dumped["commuting_zone"] == "1"
        assert dumped["cz_containment"] == 91.34

    def test_transform_data_filters_state(self):
        """The state filter keeps only the selected state's counties."""
        records = [
            make_record(fips="01001", state="Alabama"),
            make_record(fips="48001", state="Texas", county_name="Anderson County"),
        ]
        query = CommutingZonesAndLaborMarketAreasFetcher.transform_query(
            {"state": "Texas"}
        )
        data = CommutingZonesAndLaborMarketAreasFetcher.transform_data(query, records)
        assert [row.fips for row in data] == ["48001"]
        assert data[0].state == "Texas"

    def test_transform_data_orders_by_fips(self):
        """Rows are ordered by ascending FIPS code."""
        records = [
            make_record(fips="48001", state="Texas"),
            make_record(fips="01001", state="Alabama"),
            make_record(fips="06037", state="California"),
        ]
        query = CommutingZonesAndLaborMarketAreasFetcher.transform_query({})
        data = CommutingZonesAndLaborMarketAreasFetcher.transform_data(query, records)
        assert [row.fips for row in data] == ["01001", "06037", "48001"]

    def test_transform_data_empty_raises(self):
        """No counties surviving the state filter raises EmptyDataError."""
        query = CommutingZonesAndLaborMarketAreasFetcher.transform_query(
            {"state": "Wyoming"}
        )
        with pytest.raises(EmptyDataError, match="No records match"):
            CommutingZonesAndLaborMarketAreasFetcher.transform_data(
                query, [make_record(state="Alabama")]
            )

    def test_columns_defs_bind_to_served_keys(self):
        """Every declared column definition binds to a served row key."""
        records = [
            make_record(
                commuting_zone_name="Montgomery, AL",
                cz_containment=91.34,
                cz_avg_containment=89.95,
                cz_1990="11101",
                cz_1980="28101",
                metro_area="Montgomery, AL",
                county_population=43671,
                commuting_zone_population=448828,
                distance=0.963,
                beale_code="2",
                msa_code="5240",
                msa_name="Montgomery, AL MSA",
                place_code="0151000",
            )
        ]
        query = CommutingZonesAndLaborMarketAreasFetcher.transform_query({})
        data = CommutingZonesAndLaborMarketAreasFetcher.transform_data(query, records)
        served = set(data[0].model_dump(by_alias=True))
        schema = CommutingZonesAndLaborMarketAreasData.model_json_schema(
            by_alias=True, mode="serialization"
        )
        column_fields = [to_snake(key) for key in schema["properties"]]
        assert column_fields, "no column definitions generated"
        for field in column_fields:
            assert field in served, field
        assert served == set(column_fields)

    def test_visible_columns_are_populated_every_vintage(self):
        """The four visible columns carry a value in each vintage sample."""
        visible = ["fips", "state", "county_name", "commuting_zone"]
        samples = [
            make_record(),
            make_record(commuting_zone="60", cz_1990="11101"),
            make_record(commuting_zone="11101", beale_code="2"),
        ]
        query = CommutingZonesAndLaborMarketAreasFetcher.transform_query({})
        for record in samples:
            data = CommutingZonesAndLaborMarketAreasFetcher.transform_data(
                query, [record]
            )
            dumped = data[0].model_dump(by_alias=True)
            for field in visible:
                assert dumped[field] is not None, field

    def test_widget_config_metadata(self):
        """The whole-widget config carries the ERS category and source."""
        config = CommutingZonesAndLaborMarketAreasData.model_config[
            "json_schema_extra"
        ]["x-widget_config"]
        assert config["$.category"] == "Economy"
        assert config["$.subCategory"] == "Agriculture"
        assert config["$.source"] == ["USDA", "ERS"]

    def test_hidden_optional_columns_toggleable(self):
        """Columns absent from the default vintage are hidden, the rest shown."""
        fields = CommutingZonesAndLaborMarketAreasData.model_fields
        for name in ("cz_1990", "cz_1980", "beale_code", "place_code"):
            config = fields[name].json_schema_extra["x-widget_config"]
            assert config["hide"] is True
        for name in (
            "fips",
            "state",
            "county_name",
            "commuting_zone",
            "commuting_zone_name",
            "cz_containment",
            "cz_avg_containment",
        ):
            config = fields[name].json_schema_extra["x-widget_config"]
            assert "hide" not in config
