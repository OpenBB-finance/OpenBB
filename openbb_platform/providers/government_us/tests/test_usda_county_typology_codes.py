"""Tests for the USDA ERS County Typology Codes utils and model."""

import asyncio
import csv
from io import BytesIO, StringIO

import pandas as pd
import pytest
from openbb_core.app.model.abstract.error import OpenBBError

from openbb_government_us.usda.models.county_typology_codes import (
    CountyTypologyCodesData,
    CountyTypologyCodesFetcher,
    CountyTypologyCodesQueryParams,
)
from openbb_government_us.usda.utils import ers_county_typology_codes
from openbb_government_us.usda.utils.ers_county_typology_codes import (
    CANONICAL_FIELDS,
    DEFAULT_VINTAGE,
    STATE_ABBRS,
    VINTAGES,
    cell_int,
    cell_str,
    normalize_fips,
    parse_1979,
    parse_1989,
    parse_2004,
    parse_2015,
    parse_2025,
    parse_vintage,
    state_of,
    state_options,
    vintage_options,
)

CODES_2025 = [
    "High_Farming_2025",
    "High_Mining_2025",
    "High_Manufacturing_2025",
    "High_Government_2025",
    "High_Recreation_2025",
    "Nonspecialized_2025",
    "Industry_Dependence_2025",
    "Low_PostSecondary_Ed_2025",
    "Low_Employment_2025",
    "Population_Loss_2025",
    "Housing_Stress_2025",
    "Retirement_Destination_2025",
    "Persistent_Poverty_1721",
]


def _make_2025_csv(counties: list[dict]) -> str:
    """Serialize the 2025 long CSV from per-county attribute dictionaries."""
    buffer = StringIO()
    writer = csv.writer(buffer)
    writer.writerow(
        ["FIPStxt", "State", "County_Name", "Metro2023", "Attribute", "Value"]
    )
    for county in counties:
        for attribute in CODES_2025:
            writer.writerow(
                [
                    county["fips"],
                    county["state"],
                    county["county_name"],
                    county["metro"],
                    attribute,
                    county["attrs"][attribute],
                ]
            )
    return buffer.getvalue()


COUNTIES_2025 = [
    {
        "fips": "01001",
        "state": "AL",
        "county_name": "Autauga County",
        "metro": "1",
        "attrs": {
            "High_Farming_2025": "0",
            "High_Mining_2025": "0",
            "High_Manufacturing_2025": "0",
            "High_Government_2025": "0",
            "High_Recreation_2025": "0",
            "Nonspecialized_2025": "1",
            "Industry_Dependence_2025": "0",
            "Low_PostSecondary_Ed_2025": "0",
            "Low_Employment_2025": "0",
            "Population_Loss_2025": "0",
            "Housing_Stress_2025": "0",
            "Retirement_Destination_2025": "0",
            "Persistent_Poverty_1721": "0",
        },
    },
    {
        "fips": "48001",
        "state": "TX",
        "county_name": "Anderson County",
        "metro": "0",
        "attrs": {
            "High_Farming_2025": "0",
            "High_Mining_2025": "0",
            "High_Manufacturing_2025": "1",
            "High_Government_2025": "0",
            "High_Recreation_2025": "0",
            "Nonspecialized_2025": "0",
            "Industry_Dependence_2025": "3",
            "Low_PostSecondary_Ed_2025": "1",
            "Low_Employment_2025": "99",
            "Population_Loss_2025": "0",
            "Housing_Stress_2025": "1",
            "Retirement_Destination_2025": "0",
            "Persistent_Poverty_1721": "-1",
        },
    },
]

CSV_2025 = _make_2025_csv(COUNTIES_2025)

HEADER_2015 = [
    "FIPStxt",
    "State",
    "County_name",
    "Metro-nonmetro status, 2013 0=Nonmetro 1=Metro",
    "Economic Types Type_2015_Update non-overlapping",
    "Economic_Type_Label",
    "Farming_2015_Update",
    "Mining_2015-Update",
    "Manufacturing_2015_Update",
    "Government_2015_Update",
    "Recreation_2015_Update",
    "Nonspecialized_2015_Update",
    "Low_Education_2015_Update",
    "Low_Employment_Cnty_2008_2012_25_64",
    "Pop_Loss_2010",
    "Retirement_Dest_2015_Update",
    "Persistent_Poverty_2013",
    "Persistent_Related_Child_Poverty_2013",
]


def _make_2015_csv() -> str:
    """Serialize the 2015 wide CSV, quoting the comma-bearing metro header."""
    buffer = StringIO()
    writer = csv.writer(buffer)
    writer.writerow(HEADER_2015)
    writer.writerow(
        [
            "1001",
            "AL",
            "Autauga County",
            "1",
            "0",
            "Nonspecialized",
            "0",
            "0",
            "0",
            "0",
            "0",
            "1",
            "0",
            "0",
            "0",
            "1",
            "0",
            "0",
        ]
    )
    writer.writerow(
        [
            "48001",
            "TX",
            "Anderson County",
            "0",
            "3",
            "Maufacturing",
            "0",
            "0",
            "1",
            "0",
            "0",
            "0",
            "1",
            "0",
            "0",
            "0",
            "1",
            "1",
        ]
    )
    return buffer.getvalue()


CSV_2015 = _make_2015_csv()


def _xlsx(sheet: str, rows: list[dict]) -> bytes:
    """Build in-memory workbook bytes with one data sheet plus documentation."""
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        pd.DataFrame(rows).to_excel(writer, sheet_name=sheet, index=False)
        pd.DataFrame({"note": ["Documentation"]}).to_excel(
            writer, sheet_name="Documentation", index=False
        )
    return buffer.getvalue()


ROWS_2004 = [
    {
        "FIPSTXT": "01001",
        "FIPS ": 1001,
        "State": "AL",
        "County": "Autauga County",
        "metro": 1,
        "urbinf2003": 2,
        "rururb2003": 2,
        "econdep": 3,
        "farm": 0,
        "mine": 0,
        "manf": 1,
        "fsgov": 0,
        "serv": 0,
        "nonsp": 0,
        "house": 0,
        "loweduc": 0,
        "lowemp": 0,
        "perpov": 0,
        "poploss": 0,
        "rec": 0,
        "retire": 0,
        "perchldpov": 0,
    },
    {
        "FIPSTXT": "48001",
        "FIPS ": 48001,
        "State": "TX",
        "County": "Anderson County",
        "metro": 0,
        "urbinf2003": 5,
        "rururb2003": 4,
        "econdep": 4,
        "farm": 0,
        "mine": 0,
        "manf": 0,
        "fsgov": 1,
        "serv": 0,
        "nonsp": 0,
        "house": 0,
        "loweduc": 1,
        "lowemp": 0,
        "perpov": 0,
        "poploss": 0,
        "rec": 1,
        "retire": 1,
        "perchldpov": 0,
    },
]

ROWS_1989 = [
    {
        "FIPS": "01001",
        "State": "AL",
        "County name": "AUTAUGA COUNTY",
        "RuralUrb93": 2,
        "FM": 8,
        "MI": 8,
        "MF": 8,
        "GV": 8,
        "TS": 8,
        "NS": 8,
        "RT": 8,
        "FL": 8,
        "CM": 8,
        "PV": 8,
        "TP": 8,
    },
    {
        "FIPS": "48001",
        "State": "TX",
        "County name": "ANDERSON COUNTY",
        "RuralUrb93": 6,
        "FM": 0,
        "MI": 0,
        "MF": 1,
        "GV": 0,
        "TS": 0,
        "NS": 0,
        "RT": 0,
        "FL": 0,
        "CM": 0,
        "PV": 1,
        "TP": 0,
    },
]

ROWS_1979 = [
    {
        "FIPS": 1001,
        "State": "ALABAMA           ",
        "County": "AUTAUGA                        ",
        "RURALURB83": 2,
        "NMET": 1,
        "AGTP79R": 9,
        "MFGTP79R": 9,
        "MINTP79R": 9,
        "GVTTP79R": 9,
        "FEDTP79": 9,
        "RETTP79": 9,
        "POVTP79": 9,
        "UNCL79": 9,
        "AGTP86": 9,
        "MFGTP86": 9,
        "MINTP86": 9,
        "GVTTP86": 9,
        "UNCL86": 9,
    },
    {
        "FIPS": 48001,
        "State": "TEXAS             ",
        "County": "ANDERSON                       ",
        "RURALURB83": 6,
        "NMET": 0,
        "AGTP79R": 1,
        "MFGTP79R": 1,
        "MINTP79R": 0,
        "GVTTP79R": 0,
        "FEDTP79": 0,
        "RETTP79": 0,
        "POVTP79": 1,
        "UNCL79": 0,
        "AGTP86": 0,
        "MFGTP86": 1,
        "MINTP86": 0,
        "GVTTP86": 0,
        "UNCL86": 0,
    },
]


class TestErsCountyTypologyCodesUtils:
    """Tests for the ers_county_typology_codes utils module."""

    def test_catalog_contents(self):
        """The catalog holds the six vintages with their reader configuration."""
        assert list(VINTAGES) == [
            "2025",
            "2015",
            "2004",
            "1989",
            "1979_1986_1983def",
            "1979_1986_1974def",
        ]
        assert DEFAULT_VINTAGE == "2025"
        for config in VINTAGES.values():
            assert config["label"]
            assert config["media_path"].startswith("/media/")
            assert config["format"]
        assert VINTAGES["1979_1986_1983def"]["rucc_col"] == "RURALURB83"
        assert VINTAGES["1979_1986_1974def"]["rucc_col"] == "RURALURB74"

    def test_state_options_cover_fifty_one_states(self):
        """State options list the 50 states plus DC as postal-code values."""
        options = state_options()
        assert len(options) == 51
        values = {option["value"] for option in options}
        assert "DC" in values
        assert "TX" in values
        assert values == set(STATE_ABBRS)

    def test_vintage_options_match_catalog(self):
        """Vintage options mirror the catalog order and labels."""
        options = vintage_options()
        assert [option["value"] for option in options] == list(VINTAGES)
        assert options[0]["label"] == "2025 Edition"

    def test_cell_int_preserves_sentinels(self):
        """Sentinels 99, 8, 9, and -1 are kept; blanks and tokens become None."""
        assert cell_int("99") == 99
        assert cell_int(8) == 8
        assert cell_int("-1") == -1
        assert cell_int(3.0) == 3
        assert cell_int("") is None
        assert cell_int("NA") is None
        assert cell_int(None) is None
        assert cell_int(float("nan")) is None
        assert cell_int("abc") is None

    def test_cell_str_strips_and_nulls(self):
        """cell_str strips whitespace and maps blanks and NaN to None."""
        assert cell_str("  AUTAUGA  ") == "AUTAUGA"
        assert cell_str("") is None
        assert cell_str(None) is None
        assert cell_str(float("nan")) is None

    def test_normalize_fips_zero_pads(self):
        """FIPS values normalize to five-digit zero-padded strings."""
        assert normalize_fips("1001") == "01001"
        assert normalize_fips(1001) == "01001"
        assert normalize_fips("02063") == "02063"
        assert normalize_fips(48001) == "48001"
        assert normalize_fips(None) is None
        assert normalize_fips(float("nan")) is None
        assert normalize_fips("") is None
        assert normalize_fips("ab") == "000ab"

    def test_state_of_maps_prefix(self):
        """The FIPS state prefix maps to a postal abbreviation."""
        assert state_of("01001") == "AL"
        assert state_of("48001") == "TX"
        assert state_of("11001") == "DC"
        assert state_of("99999") is None

    def test_parse_2025_pivots_long_to_one_row_per_county(self):
        """The 2025 long CSV pivots to one canonical row per county FIPS."""
        records = parse_2025(CSV_2025)
        assert len(records) == 2
        assert {record["fips"] for record in records} == {"01001", "48001"}
        for record in records:
            assert set(record) == set(CANONICAL_FIELDS)

    def test_parse_2025_derives_economic_type_and_geography(self):
        """Economic type comes from the industry-dependence code, geography from FIPS."""
        records = {record["fips"]: record for record in parse_2025(CSV_2025)}
        autauga = records["01001"]
        assert autauga["state"] == "AL"
        assert autauga["county_name"] == "Autauga County"
        assert autauga["metro"] == 1
        assert autauga["economic_type"] == "Nonspecialized"
        assert autauga["economic_type_code"] == 0
        assert autauga["nonspecialized"] == 1
        anderson = records["48001"]
        assert anderson["state"] == "TX"
        assert anderson["economic_type"] == "Manufacturing"
        assert anderson["manufacturing"] == 1

    def test_parse_2025_keeps_raw_sentinels(self):
        """Documented sentinels 99 and -1 survive the pivot unchanged."""
        anderson = {r["fips"]: r for r in parse_2025(CSV_2025)}["48001"]
        assert anderson["low_employment"] == 99
        assert anderson["persistent_poverty"] == -1

    def test_parse_2015_uses_code_and_keeps_published_label(self):
        """2015 derives a clean economic type from the code and keeps the raw label."""
        records = {record["fips"]: record for record in parse_2015(CSV_2015)}
        anderson = records["48001"]
        assert anderson["fips"] == "48001"
        assert anderson["economic_type"] == "Manufacturing"
        assert anderson["economic_type_label"] == "Maufacturing"
        assert anderson["persistent_child_poverty"] == 1
        autauga = records["01001"]
        assert autauga["fips"] == "01001"
        assert autauga["economic_type"] == "Nonspecialized"

    def test_parsers_skip_blank_fips_rows(self):
        """Every parser drops a row that carries no county FIPS."""
        blank_2025 = (
            "FIPStxt,State,County_Name,Metro2023,Attribute,Value\r\n"
            ",AL,,1,High_Farming_2025,0\r\n"
        )
        assert parse_2025(blank_2025) == []
        blank_2015 = _make_2015_csv().splitlines()[0] + "\r\n" + ",,,,,,,,,,,,,,,,,\r\n"
        assert parse_2015(blank_2015) == []
        assert parse_2004([{**ROWS_2004[0], "FIPSTXT": None}]) == []
        assert parse_1989([{**ROWS_1989[0], "FIPS": ""}]) == []
        assert parse_1979([{**ROWS_1979[0], "FIPS": None}], "RURALURB83") == []

    def test_parse_2004_maps_services_and_codes(self):
        """2004 maps the services economic type and the urban/Beale codes."""
        records = {record["fips"]: record for record in parse_2004(ROWS_2004)}
        anderson = records["48001"]
        assert anderson["economic_type"] == "Federal/State Government"
        assert anderson["economic_type_code"] == 4
        assert anderson["government"] == 1
        assert anderson["recreation"] == 1
        assert anderson["rural_urban_continuum_code"] == 4
        assert anderson["urban_influence_code"] == 5
        autauga = records["01001"]
        assert autauga["economic_type"] == "Manufacturing"
        assert autauga["manufacturing"] == 1

    def test_parse_1989_metro_and_flag_economic_type(self):
        """1989 derives metro from the Beale code and economic type from set flags."""
        records = {record["fips"]: record for record in parse_1989(ROWS_1989)}
        autauga = records["01001"]
        assert autauga["metro"] == 1
        assert autauga["economic_type"] is None
        assert autauga["farming"] == 8
        anderson = records["48001"]
        assert anderson["metro"] == 0
        assert anderson["economic_type"] == "Manufacturing"
        assert anderson["manufacturing"] == 1
        assert anderson["persistent_poverty"] == 1
        assert anderson["rural_urban_continuum_code"] == 6

    def test_parse_1979_metro_and_1986_columns(self):
        """1979/1986 uses NMET for metro and carries the 1986 update columns."""
        records = {
            record["fips"]: record for record in parse_1979(ROWS_1979, "RURALURB83")
        }
        autauga = records["01001"]
        assert autauga["fips"] == "01001"
        assert autauga["metro"] == 1
        assert autauga["economic_type"] is None
        assert autauga["farming"] == 9
        anderson = records["48001"]
        assert anderson["county_name"] == "ANDERSON"
        assert anderson["metro"] == 0
        assert anderson["economic_type"] == "Farming / Manufacturing"
        assert anderson["manufacturing"] == 1
        assert anderson["manufacturing_1986"] == 1
        assert anderson["farming_1986"] == 0
        assert anderson["rural_urban_continuum_code"] == 6

    def test_parse_vintage_dispatches_all_formats(self):
        """parse_vintage routes each vintage to its reader by media content."""
        assert len(parse_vintage("2025", CSV_2025.encode("utf-8-sig"))) == 2
        assert len(parse_vintage("2015", CSV_2015.encode("utf-8-sig"))) == 2
        assert len(parse_vintage("2004", _xlsx("all_final_codes", ROWS_2004))) == 2
        assert len(parse_vintage("1989", _xlsx("Data", ROWS_1989))) == 2
        records = parse_vintage("1979_1986_1974def", _xlsx("Data", ROWS_1979))
        assert len(records) == 2

    def test_afetch_vintage_downloads_and_parses(self, monkeypatch):
        """afetch_vintage fetches the vintage's file through the ERS cache."""
        calls = []

        async def fake_afetch_ers_file(media_path, product=None, ttl=None):
            calls.append((media_path, product))
            return _xlsx("all_final_codes", ROWS_2004)

        monkeypatch.setattr(
            "openbb_government_us.usda.utils.ers_client.afetch_ers_file",
            fake_afetch_ers_file,
        )
        records = asyncio.run(ers_county_typology_codes.afetch_vintage("2004"))
        assert calls == [
            (VINTAGES["2004"]["media_path"], "data-products/county-typology-codes")
        ]
        assert len(records) == 2


class TestCountyTypologyCodes:
    """Tests for the CountyTypologyCodes model."""

    def test_transform_query_defaults_vintage(self):
        """transform_query defaults the vintage and leaves the state optional."""
        query = CountyTypologyCodesFetcher.transform_query({})
        assert isinstance(query, CountyTypologyCodesQueryParams)
        assert query.vintage == DEFAULT_VINTAGE
        assert query.state is None

    def test_vintage_blank_returns_default(self):
        """A blank or None vintage normalizes to the default vintage."""
        assert CountyTypologyCodesQueryParams(vintage=None).vintage == DEFAULT_VINTAGE
        assert CountyTypologyCodesQueryParams(vintage="").vintage == DEFAULT_VINTAGE

    def test_vintage_strips_whitespace(self):
        """A padded vintage value is stripped before validation."""
        assert CountyTypologyCodesQueryParams(vintage="  2004  ").vintage == "2004"

    def test_unknown_vintage_raises(self):
        """An unknown vintage raises OpenBBError listing valid choices."""
        with pytest.raises(OpenBBError, match="Invalid vintage: 1999"):
            CountyTypologyCodesQueryParams(vintage="1999")

    def test_state_normalizes_and_validates(self):
        """State input is upper-cased and validated against the postal set."""
        assert CountyTypologyCodesQueryParams(state="tx").state == "TX"
        assert CountyTypologyCodesQueryParams(state=["ca"]).state == "CA"
        assert CountyTypologyCodesQueryParams(state="").state is None
        assert CountyTypologyCodesQueryParams(state="   ").state is None
        assert CountyTypologyCodesQueryParams(state=None).state is None

    def test_invalid_state_raises(self):
        """An unknown state abbreviation raises OpenBBError."""
        with pytest.raises(OpenBBError, match="Invalid state: ZZ"):
            CountyTypologyCodesQueryParams(state="ZZ")

    def test_aextract_data_fetches_selected_vintage(self, monkeypatch):
        """aextract_data fetches only the selected vintage's records."""
        fetched = []

        async def fake_afetch_vintage(vintage):
            fetched.append(vintage)
            return [{"fips": "01001", "state": "AL"}]

        monkeypatch.setattr(
            ers_county_typology_codes, "afetch_vintage", fake_afetch_vintage
        )
        query = CountyTypologyCodesFetcher.transform_query({"vintage": "1989"})
        records = asyncio.run(CountyTypologyCodesFetcher.aextract_data(query, None))
        assert fetched == ["1989"]
        assert records == [{"fips": "01001", "state": "AL"}]

    def test_transform_data_scopes_by_state_and_sorts(self):
        """transform_data filters to the selected state and sorts by FIPS."""
        records = parse_2025(CSV_2025)
        query = CountyTypologyCodesFetcher.transform_query({"state": "TX"})
        data = CountyTypologyCodesFetcher.transform_data(query, records)
        assert [row.fips for row in data] == ["48001"]
        assert data[0].state == "TX"

    def test_transform_data_all_states_when_unfiltered(self):
        """With no state filter, every county is returned in FIPS order."""
        records = parse_2025(CSV_2025)
        query = CountyTypologyCodesFetcher.transform_query({})
        data = CountyTypologyCodesFetcher.transform_data(query, records)
        assert [row.fips for row in data] == ["01001", "48001"]

    def test_transform_data_returns_lookup_rows(self):
        """Each row is a validated one-per-county lookup record."""
        records = parse_2025(CSV_2025)
        query = CountyTypologyCodesFetcher.transform_query({})
        data = CountyTypologyCodesFetcher.transform_data(query, records)
        autauga = next(row for row in data if row.fips == "01001")
        assert autauga.economic_type == "Nonspecialized"
        assert autauga.metro == 1

    def test_query_params_widget_options(self):
        """The vintage and state params are single-select filters."""
        vintage = CountyTypologyCodesQueryParams.__json_schema_extra__["vintage"][
            "x-widget_config"
        ]
        assert vintage["multiSelect"] is False
        assert vintage["multiple"] is False
        assert vintage["value"] == DEFAULT_VINTAGE
        assert len(vintage["options"]) == 6
        state = CountyTypologyCodesQueryParams.__json_schema_extra__["state"][
            "x-widget_config"
        ]
        assert state["multiSelect"] is False
        assert "value" not in state
        assert len(state["options"]) == 51

    def test_widget_model_config(self):
        """The whole-widget config carries the name, category, and source."""
        config = CountyTypologyCodesData.model_config["json_schema_extra"][
            "x-widget_config"
        ]
        assert config["$.name"] == "USDA ERS County Typology Codes"
        assert config["$.category"] == "Economy"
        assert config["$.subCategory"] == "Agriculture"
        assert config["$.source"] == ["USDA", "ERS"]

    def test_columns_defs_bind_to_served_keys(self):
        """Every served key has a columnDef and every columnDef binds to a key."""
        records = parse_2025(CSV_2025)
        query = CountyTypologyCodesFetcher.transform_query({})
        data = CountyTypologyCodesFetcher.transform_data(query, records)
        served = set(data[0].model_dump(by_alias=True))
        fields = CountyTypologyCodesData.model_fields
        assert served == set(fields)
        for name in fields:
            assert name in served

    def test_visible_columns_have_config_and_are_populated(self):
        """Every visible column carries a config and is non-empty for 2025."""
        records = parse_2025(CSV_2025)
        query = CountyTypologyCodesFetcher.transform_query({})
        data = CountyTypologyCodesFetcher.transform_data(query, records)
        for name, field in CountyTypologyCodesData.model_fields.items():
            config = (field.json_schema_extra or {}).get("x-widget_config", {})
            assert config, f"{name} lacks a widget config"
            if not config.get("hide"):
                assert any(getattr(row, name) is not None for row in data), name

    def test_populated_columns_are_not_hidden(self):
        """No column the default edition populates is hidden from the table."""
        records = parse_2025(CSV_2025)
        query = CountyTypologyCodesFetcher.transform_query({})
        data = CountyTypologyCodesFetcher.transform_data(query, records)
        for name, field in CountyTypologyCodesData.model_fields.items():
            config = (field.json_schema_extra or {}).get("x-widget_config", {})
            if any(getattr(row, name) is not None for row in data):
                assert not config.get("hide"), name

    def test_fips_and_code_columns_are_text(self):
        """FIPS and classification-code columns render as text, not numbers."""
        fields = CountyTypologyCodesData.model_fields
        for name in ("fips", "state", "metro", "economic_type_code", "farming"):
            config = fields[name].json_schema_extra["x-widget_config"]
            assert config["cellDataType"] == "text"
