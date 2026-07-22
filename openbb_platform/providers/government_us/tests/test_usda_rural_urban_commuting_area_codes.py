"""Tests for the USDA ERS rural-urban commuting area codes utils and model."""

import asyncio
import io

import openpyxl
import pytest
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic.alias_generators import to_snake

from openbb_government_us.usda.models.rural_urban_commuting_area_codes import (
    SERVED_FIELDS,
    RuralUrbanCommutingAreaCodesData,
    RuralUrbanCommutingAreaCodesFetcher,
    RuralUrbanCommutingAreaCodesQueryParams,
)
from openbb_government_us.usda.utils import (
    ers_rural_urban_commuting_area_codes as ruca,
)
from openbb_government_us.usda.utils.ers_rural_urban_commuting_area_codes import (
    TABLE_CATALOG,
    TABLE_LABELS,
    _fips_str,
    _to_float,
    _to_int,
    _xlsx_data_rows,
    afetch_table,
    allowed_states,
    normalize_code,
    parse_tract_1990,
    parse_tract_2000,
    parse_tract_2010,
    parse_tract_2020,
    parse_zip_2010,
    parse_zip_2020,
    primary_description,
    secondary_description,
    state_options,
)

TRACT_2020_CSV = (
    "StateFIPS20,TractFIPS20,CountyName20,TractName20,PrimaryRUCA,"
    "PrimaryRUCADescription,SecondaryRUCA,SecondaryRUCADescription,"
    "Population,LandArea,PopDensity\n"
    "10,10001040100,Kent County,Census Tract 401,2,Metropolitan high commuting,"
    "2,Metropolitan high commuting no additional code,7315,48.2,151.9\n"
    "10,10001040201,Kent County,Census Tract 402.01,1,Metropolitan core,"
    "1.1,Metropolitan core secondary flow,5446,3.8,1449.2\n"
    "01,01001020100,Autauga County,Census Tract 201,1,Metropolitan core,"
    "1,Metropolitan core no additional code,1775,3.8,467.9\n"
)

ZIP_2020_CSV = (
    "ZIPCode,State,ZIPCodeType,POName,PrimaryRUCA,SecondaryRUCA\n"
    "19701,DE,ZIP Code Area,Bear,1,1\n"
    "00001,AK,Post Office or large volume customer,N Dillingham,10,10.1\n"
)

ZIP_2010_CSV = (
    "''ZIP_CODE'',STATE,ZIP_TYPE,RUCA1,RUCA2\n"
    "''19701'',DE,Zip Code Area,1,1\n"
    "''00001'',AK,Post Office or large volume customer,99,99\n"
)

TRACT_2010_ROWS = [
    ("Errata note", None, None, None, None, None, None, None, None),
    (
        "State-County FIPS Code",
        "Select State",
        "Select County",
        "State-County-Tract FIPS Code",
        "Primary RUCA Code 2010",
        "Secondary RUCA Code 2010",
        "Tract Population 2010",
        "Land Area 2010",
        "Population Density 2010",
    ),
    ("10001", "DE", "Kent County", "10001040100", 2, 2.1, 6541, 48.164644778277, 135.8),
    (
        "01001",
        "AL",
        "Autauga County",
        "01001020100",
        1,
        1,
        1912,
        3.78764071493768,
        504.7,
    ),
]

TRACT_2000_ROWS = [
    (
        "State-County FIPS Code",
        "Select State",
        "Select County ",
        "State County Tract Code",
        "RUCA Primary Code 2000",
        "RUCA Secondary Code 2000",
        "Tract Population 2000",
        "Select Your State Code",
        "County Code",
        "Census Tract Code",
    ),
    ("10001", "DE", "Kent County", "10001040100", 2.0, 2.1, 5337.0, 10.0, 1.0, 40100.0),
    (
        "05001",
        "AR",
        "Arkansas County",
        "05001480100",
        5.0,
        5.2,
        3200.0,
        5.0,
        1.0,
        480100.0,
    ),
]

TRACT_1990_ROWS = [
    ("Errata note", "", "", "", ""),
    (
        "FIPS state-county-tract code",
        "Rural-urban commuting area code",
        "Census tract population, 1990",
        "Census tract land area, square miles, 1990",
        "County metropolitan status, 1993",
    ),
    ("100010401.00", "2.0", "4429", 48.127, "1"),
    ("050014801.00", "99.0", "12", 900.5, "0"),
]


def make_record(**overrides) -> dict:
    """Build a unified lookup record with optional field overrides."""
    record = {
        "area_fips": "10001040100",
        "state": "DE",
        "area_name": None,
        "county": "Kent County",
        "area_type": None,
        "primary_ruca": "2",
        "primary_ruca_description": "Metropolitan high commuting",
        "secondary_ruca": "2",
        "secondary_ruca_description": "Metropolitan high commuting, no additional code",
        "population": 7315,
        "land_area": 48.2,
        "population_density": 151.9,
    }
    record.update(overrides)
    return record


class TestErsRuralUrbanCommutingAreaCodesUtils:
    """Tests for the ers_rural_urban_commuting_area_codes utils module."""

    def test_table_catalog_matches_labels(self):
        """Every catalog table has a label and a known file format."""
        assert set(TABLE_CATALOG) == set(TABLE_LABELS)
        assert {kind for _, kind in TABLE_CATALOG.values()} == {"csv", "xls", "xlsx"}

    def test_normalize_code_variants(self):
        """Codes normalize to canonical strings with trailing '.0' dropped."""
        assert normalize_code(None) is None
        assert normalize_code("") is None
        assert normalize_code("  ") is None
        assert normalize_code("1") == "1"
        assert normalize_code("2.0") == "2"
        assert normalize_code("1.1") == "1.1"
        assert normalize_code("99.0") == "99"
        assert normalize_code("10.3") == "10.3"
        assert normalize_code(2.0) == "2"
        assert normalize_code(5) == "5"
        assert normalize_code("abc") == "abc"
        assert normalize_code([]) is None

    def test_primary_description(self):
        """Primary descriptions map codes to canonical labels."""
        assert primary_description(None) is None
        assert primary_description("2") == "Metropolitan high commuting"
        assert primary_description("13") is None

    def test_secondary_description_exact_and_fallback(self):
        """Secondary descriptions use the exact label or fall back to primary."""
        assert secondary_description(None) is None
        assert (
            secondary_description("2.1")
            == "Metropolitan high commuting, seconary flow to larger UA"
        )
        assert secondary_description("5.2") == "Micropolitan high commuting"
        assert secondary_description("99") == "Not coded"
        assert secondary_description("13") is None

    def test_allowed_states(self):
        """State availability differs by table, with a full-set fallback."""
        assert len(allowed_states("tract_2020")) == 56
        assert len(allowed_states("tract_2010")) == 52
        assert len(allowed_states("tract_2000")) == 51
        assert "PR" in allowed_states("zip_2010")
        assert "PR" not in allowed_states("tract_1990")
        assert len(allowed_states("unknown_table")) == 56

    def test_state_options(self):
        """State options are labeled and led alphabetically by code."""
        options = state_options("tract_2000")
        assert {"label": "Delaware", "value": "DE"} in options
        assert all(set(option) == {"label", "value"} for option in options)
        assert [option["value"] for option in options] == sorted(
            option["value"] for option in options
        )

    def test_to_int(self):
        """Populations parse to exact ints, blanks and junk to None."""
        assert _to_int(None) is None
        assert _to_int("") is None
        assert _to_int("5") == 5
        assert _to_int("1921.0") == 1921
        assert _to_int("abc") is None
        assert _to_int(7) == 7
        assert _to_int([]) is None

    def test_to_float(self):
        """Measures parse to full-precision floats, blanks and junk to None."""
        assert _to_float(None) is None
        assert _to_float("") is None
        assert _to_float("3.78764071493768") == 3.78764071493768
        assert _to_float("abc") is None
        assert _to_float(3) == 3.0
        assert _to_float([]) is None

    def test_fips_str(self):
        """FIPS and ZIP identifiers keep leading zeros at a fixed width."""
        assert _fips_str(None, 11) is None
        assert _fips_str("  ", 5) is None
        assert _fips_str("01001020100", 11) == "01001020100"
        assert _fips_str("1001020100", 11) == "01001020100"
        assert _fips_str(1001020100, 11) == "01001020100"
        assert _fips_str("ABC", 5) == "ABC"

    def test_parse_tract_2020_filters_state(self):
        """The 2020 tract CSV parses inline descriptions and filters by state."""
        records = parse_tract_2020(TRACT_2020_CSV, "DE")
        assert {record["area_fips"] for record in records} == {
            "10001040100",
            "10001040201",
        }
        first = records[0]
        assert first["state"] == "DE"
        assert first["county"] == "Kent County"
        assert first["area_name"] == "Census Tract 401"
        assert first["primary_ruca_description"] == "Metropolitan high commuting"
        assert first["population"] == 7315
        assert first["land_area"] == 48.2
        assert first["population_density"] == 151.9

    def test_parse_tract_2020_all_states(self):
        """A None state keeps every row of the 2020 tract CSV."""
        records = parse_tract_2020(TRACT_2020_CSV, None)
        assert {record["state"] for record in records} == {"DE", "AL"}

    def test_parse_zip_2020(self):
        """The 2020 ZIP CSV maps codes to descriptions and carries the type."""
        records = parse_zip_2020(ZIP_2020_CSV, None)
        assert {record["area_fips"] for record in records} == {"19701", "00001"}
        bear = next(r for r in records if r["area_fips"] == "19701")
        assert bear["area_name"] == "Bear"
        assert bear["area_type"] == "ZIP Code Area"
        assert bear["primary_ruca_description"] == "Metropolitan core"
        assert bear["population"] is None
        assert {r["area_fips"] for r in parse_zip_2020(ZIP_2020_CSV, "DE")} == {"19701"}

    def test_parse_zip_2010_strips_quotes(self):
        """The 2010 ZIP CSV strips the doubled single quotes around the code."""
        records = parse_zip_2010(ZIP_2010_CSV, "DE")
        assert len(records) == 1
        assert records[0]["area_fips"] == "19701"
        assert records[0]["area_type"] == "Zip Code Area"
        assert records[0]["primary_ruca"] == "1"

    def test_parse_tract_2010(self, monkeypatch):
        """The 2010 tract XLSX parser reads from the data rows past the header."""
        monkeypatch.setattr(ruca, "_xlsx_data_rows", lambda content: TRACT_2010_ROWS)
        records = parse_tract_2010(b"", "DE")
        assert len(records) == 1
        row = records[0]
        assert row["area_fips"] == "10001040100"
        assert row["county"] == "Kent County"
        assert row["primary_ruca"] == "2"
        assert row["secondary_ruca"] == "2.1"
        assert row["population"] == 6541
        assert row["land_area"] == 48.164644778277
        assert row["population_density"] == 135.8

    def test_parse_tract_2000_no_land_area(self, monkeypatch):
        """The 2000 tract XLS parser has no land area or density columns."""
        monkeypatch.setattr(ruca, "_xls_data_rows", lambda content: TRACT_2000_ROWS)
        records = parse_tract_2000(b"", None)
        de_row = next(r for r in records if r["state"] == "DE")
        assert de_row["primary_ruca"] == "2"
        assert de_row["secondary_ruca"] == "2.1"
        assert de_row["population"] == 5337
        assert de_row["land_area"] is None
        assert de_row["population_density"] is None
        ar_row = next(r for r in records if r["state"] == "AR")
        assert ar_row["secondary_ruca"] == "5.2"
        assert ar_row["secondary_ruca_description"] == "Micropolitan high commuting"
        assert {r["state"] for r in parse_tract_2000(b"", "DE")} == {"DE"}

    def test_parse_tract_1990_combined_code(self, monkeypatch):
        """The 1990 combined code splits into primary and secondary codes."""
        monkeypatch.setattr(ruca, "_xls_data_rows", lambda content: TRACT_1990_ROWS)
        records = parse_tract_1990(b"", "DE")
        assert len(records) == 1
        row = records[0]
        assert row["area_fips"] == "10001040100"
        assert row["state"] == "DE"
        assert row["primary_ruca"] == "2"
        assert row["secondary_ruca"] == "2"
        assert row["county"] is None
        assert row["population"] == 4429
        assert row["land_area"] == 48.127
        assert row["population_density"] is None

    def test_parse_tract_1990_not_coded(self, monkeypatch):
        """A 99.0 combined code becomes primary 99 and secondary 99."""
        monkeypatch.setattr(ruca, "_xls_data_rows", lambda content: TRACT_1990_ROWS)
        records = parse_tract_1990(b"", None)
        ar_row = next(r for r in records if r["state"] == "AR")
        assert ar_row["primary_ruca"] == "99"
        assert ar_row["secondary_ruca"] == "99"
        assert ar_row["primary_ruca_description"] == "Not coded"

    def test_xlsx_data_rows_reads_data_sheet(self):
        """The XLSX reader returns the 'Data' worksheet value rows."""
        workbook = openpyxl.Workbook()
        sheet = workbook.active
        sheet.title = "Data"
        sheet.append(("Errata", None))
        sheet.append(("header", "row"))
        sheet.append(("10001", "DE"))
        buffer = io.BytesIO()
        workbook.save(buffer)
        rows = _xlsx_data_rows(buffer.getvalue())
        assert rows[2][0] == "10001"
        assert rows[2][1] == "DE"

    def test_xls_data_rows_reads_data_sheet(self, monkeypatch):
        """The XLS reader returns the 'Data' worksheet cell values."""

        class FakeSheet:
            nrows = 2
            ncols = 2

            @staticmethod
            def cell_value(row, col):
                return [["a", "b"], ["10001", "DE"]][row][col]

        class FakeBook:
            @staticmethod
            def sheet_by_name(name):
                assert name == "Data"
                return FakeSheet()

        monkeypatch.setattr("xlrd.open_workbook", lambda file_contents: FakeBook())
        rows = ruca._xls_data_rows(b"binary")
        assert rows == [["a", "b"], ["10001", "DE"]]

    def test_afetch_table_csv(self, monkeypatch):
        """afetch_table decodes and parses the CSV tables."""

        async def fake_afetch_ers_file(media_path, product=None, ttl=None):
            assert media_path == TABLE_CATALOG["tract_2020"][0]
            return TRACT_2020_CSV.encode("utf-8-sig")

        monkeypatch.setattr(
            "openbb_government_us.usda.utils.ers_client.afetch_ers_file",
            fake_afetch_ers_file,
        )
        records = asyncio.run(afetch_table("tract_2020", "DE"))
        assert all(record["state"] == "DE" for record in records)
        assert len(records) == 2

    def test_afetch_table_binary(self, monkeypatch):
        """afetch_table routes the workbook tables through the binary parser."""

        async def fake_afetch_ers_file(media_path, product=None, ttl=None):
            return b"workbook-bytes"

        monkeypatch.setattr(
            "openbb_government_us.usda.utils.ers_client.afetch_ers_file",
            fake_afetch_ers_file,
        )
        monkeypatch.setattr(ruca, "_xlsx_data_rows", lambda content: TRACT_2010_ROWS)
        records = asyncio.run(afetch_table("tract_2010", "DE"))
        assert len(records) == 1
        assert records[0]["area_fips"] == "10001040100"


class TestRuralUrbanCommutingAreaCodes:
    """Tests for the RuralUrbanCommutingAreaCodes model."""

    def test_transform_query(self):
        """transform_query builds the query params model."""
        query = RuralUrbanCommutingAreaCodesFetcher.transform_query(
            {"table": "zip_2020", "state": "de"}
        )
        assert isinstance(query, RuralUrbanCommutingAreaCodesQueryParams)
        assert query.table == "zip_2020"
        assert query.state == "DE"

    def test_table_defaults_and_blank(self):
        """The table defaults to the 2020 tracts and blanks fall back."""
        assert RuralUrbanCommutingAreaCodesQueryParams().table == "tract_2020"
        assert RuralUrbanCommutingAreaCodesQueryParams(table="").table == "tract_2020"
        assert (
            RuralUrbanCommutingAreaCodesQueryParams(table=["zip_2010"]).table
            == "zip_2010"
        )

    def test_unknown_table_raises(self):
        """Unknown tables raise OpenBBError listing valid choices."""
        with pytest.raises(OpenBBError, match="Invalid table: bogus.*tract_2020"):
            RuralUrbanCommutingAreaCodesQueryParams(table="bogus")

    def test_state_defaults_and_normalizes(self):
        """State defaults to DE, uppercases, and blanks become None."""
        assert RuralUrbanCommutingAreaCodesQueryParams().state == "DE"
        assert RuralUrbanCommutingAreaCodesQueryParams(state="").state is None
        assert RuralUrbanCommutingAreaCodesQueryParams(state="ny").state == "NY"
        assert RuralUrbanCommutingAreaCodesQueryParams(state=["ia"]).state == "IA"

    def test_state_none_allowed(self):
        """A None state passes the per-table validator for every area."""
        query = RuralUrbanCommutingAreaCodesQueryParams(table="tract_2000", state="")
        assert query.state is None

    def test_state_scoped_to_table(self):
        """A state outside a table's published set raises OpenBBError."""
        with pytest.raises(
            OpenBBError, match="Invalid state 'PR' for table 'tract_2000'"
        ):
            RuralUrbanCommutingAreaCodesQueryParams(table="tract_2000", state="PR")
        query = RuralUrbanCommutingAreaCodesQueryParams(table="tract_2020", state="PR")
        assert query.state == "PR"

    def test_aextract_data_passes_table_and_state(self, monkeypatch):
        """aextract_data forwards the table and state to afetch_table."""
        calls = []

        async def fake_afetch_table(table, state):
            calls.append((table, state))
            return [make_record()]

        monkeypatch.setattr(ruca, "afetch_table", fake_afetch_table)
        query = RuralUrbanCommutingAreaCodesFetcher.transform_query(
            {"table": "zip_2020", "state": "DE"}
        )
        records = asyncio.run(
            RuralUrbanCommutingAreaCodesFetcher.aextract_data(query, None)
        )
        assert calls == [("zip_2020", "DE")]
        assert records[0]["state"] == "DE"

    def test_transform_data_orders_by_identifier(self):
        """Rows are ordered ascending by the FIPS or ZIP identifier."""
        records = [
            make_record(area_fips="10001040300"),
            make_record(area_fips="10001040100"),
            make_record(area_fips="10001040200"),
        ]
        query = RuralUrbanCommutingAreaCodesFetcher.transform_query({})
        data = RuralUrbanCommutingAreaCodesFetcher.transform_data(query, records)
        assert [row.area_fips for row in data] == [
            "10001040100",
            "10001040200",
            "10001040300",
        ]

    def test_transform_data_selects_served_fields(self):
        """Only the served fields are validated, dropping any extra keys."""
        record = make_record()
        record["_vintage"] = "2020"
        query = RuralUrbanCommutingAreaCodesFetcher.transform_query({})
        data = RuralUrbanCommutingAreaCodesFetcher.transform_data(query, [record])
        dumped = data[0].model_dump(by_alias=True)
        assert set(dumped) == set(SERVED_FIELDS)
        assert "_vintage" not in dumped

    def test_transform_data_empty_raises(self):
        """No records raises EmptyDataError."""
        query = RuralUrbanCommutingAreaCodesFetcher.transform_query({})
        with pytest.raises(EmptyDataError, match="No records match"):
            RuralUrbanCommutingAreaCodesFetcher.transform_data(query, [])

    def test_columns_defs_bind_to_served_keys(self):
        """Every declared column definition binds to a served row key."""
        query = RuralUrbanCommutingAreaCodesFetcher.transform_query({})
        data = RuralUrbanCommutingAreaCodesFetcher.transform_data(
            query, [make_record()]
        )
        served = set(data[0].model_dump(by_alias=True))
        schema = RuralUrbanCommutingAreaCodesData.model_json_schema(
            by_alias=True, mode="serialization"
        )
        column_fields = [to_snake(key) for key in schema["properties"]]
        assert column_fields, "no column definitions generated"
        assert set(column_fields) == served

    def test_code_and_fips_columns_are_text(self):
        """FIPS, state, and code columns render as text, measures as numbers."""
        fields = RuralUrbanCommutingAreaCodesData.model_fields
        for name in (
            "area_fips",
            "state",
            "primary_ruca",
            "secondary_ruca",
        ):
            config = fields[name].json_schema_extra["x-widget_config"]
            assert config["cellDataType"] == "text"
        for name in ("population", "land_area", "population_density"):
            config = fields[name].json_schema_extra["x-widget_config"]
            assert config["cellDataType"] == "number"
            assert "hide" not in config

    def test_default_table_columns_are_visible(self):
        """Only the ZIP-only column is hidden, so the tract view stays readable."""
        fields = RuralUrbanCommutingAreaCodesData.model_fields
        hidden = {
            name
            for name, field in fields.items()
            if field.json_schema_extra["x-widget_config"].get("hide")
        }
        assert hidden == {"area_type"}
        assert [
            name
            for name, field in fields.items()
            if field.json_schema_extra["x-widget_config"].get("pinned") == "left"
        ] == ["area_fips", "state", "county"]

    def test_widget_config_metadata(self):
        """The whole-widget config carries the ERS category and source."""
        config = RuralUrbanCommutingAreaCodesData.model_config["json_schema_extra"][
            "x-widget_config"
        ]
        assert config["$.name"] == "USDA ERS Rural-Urban Commuting Area (RUCA) Codes"
        assert config["$.category"] == "Economy"
        assert config["$.subCategory"] == "Agriculture"
        assert config["$.source"] == ["USDA", "ERS"]
