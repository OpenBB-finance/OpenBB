"""Tests for the USDA ERS urban influence codes utils and model."""

import asyncio
import csv
from io import BytesIO, StringIO

import pandas as pd
import pytest
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic.alias_generators import to_snake

from openbb_government_us.usda.models.urban_influence_codes import (
    UrbanInfluenceCodesData,
    UrbanInfluenceCodesFetcher,
    UrbanInfluenceCodesQueryParams,
)
from openbb_government_us.usda.utils import ers_urban_influence_codes as uic
from openbb_government_us.usda.utils.ers_urban_influence_codes import (
    ALL_TERRITORIES,
    MEDIA_2003_1993_XLS,
    MEDIA_2003_PR_XLS,
    MEDIA_2013_XLS,
    MEDIA_2024_CSV,
    SHEET_2003_1993,
    SHEET_2003_PR,
    SHEET_2013,
    STATE_LABELS,
    VINTAGE_LABELS,
    VINTAGES,
    allowed_states,
    parse_1993_combined,
    parse_2003_combined,
    parse_2003_pr,
    parse_2013_xls,
    parse_2024_csv,
    state_options,
)

CSV_2024_HEADER = ["FIPS-UIC", "State", "County_Name", "Attribute", "Value"]

CSV_2024_ROWS = [
    ["01001", "AL", "Autauga County", "Population_2020", "58805"],
    ["01001", "AL", "Autauga County", "UIC_2024", "4"],
    [
        "01001",
        "AL",
        "Autauga County",
        "Description",
        "Small metro (in a metro area with fewer than 1 million residents)",
    ],
    ["01005", "AL", "Barbour County", "Population_2020", "25223"],
    ["01005", "AL", "Barbour County", "UIC_2024", "5"],
    [
        "01005",
        "AL",
        "Barbour County",
        "Description",
        "Micropolitan, adjacent to a small metro area",
    ],
    ["02013", "AK", "Aleutians East Borough", "Population_2020", "3420"],
    ["02013", "AK", "Aleutians East Borough", "UIC_2024", "8"],
    [
        "02013",
        "AK",
        "Aleutians East Borough",
        "Description",
        "Noncore, not adjacent to a metro area, with a town of at least 5,000",
    ],
    ["60030", "AS", "Rose Island", "Population_2020", "0"],
    ["60030", "AS", "Rose Island", "Description", "Not Applicable"],
]


def build_2024_csv(rows: list[list[str]]) -> str:
    """Build long-format 2024 CSV text from the header and rows."""
    buffer = StringIO()
    writer = csv.writer(buffer)
    writer.writerow(CSV_2024_HEADER)
    writer.writerows(rows)
    return buffer.getvalue()


def build_xlsx(frame: pd.DataFrame, sheet_name: str) -> bytes:
    """Write a frame to a single-sheet workbook and return the raw bytes."""
    buffer = BytesIO()
    frame.to_excel(buffer, sheet_name=sheet_name, index=False)
    return buffer.getvalue()


DF_2013 = pd.DataFrame(
    {
        "FIPS": [1001, 1005],
        "State": ["AL", "AL"],
        "County_Name": ["Autauga County", "Barbour County"],
        "Population_2010": [54571, 27457],
        "UIC_2013": [2, 5],
        "Description": [
            "Small-in a metro area with fewer than 1 million residents        ",
            "Micropolitan area adjacent to a small metro area",
        ],
    }
)

DF_2003_1993 = pd.DataFrame(
    {
        "FIPS Code": [1001, 8014, 56035],
        "State": ["AL", "CO", "WY"],
        "County name": ["Autauga County", "Broomfield County", "Sublette County"],
        "2003 Urban Influence Code": [2, 1, 10],
        "2003 Urban Influence Code description": [
            "Small-in a metro area with fewer than 1 million residents",
            "Large-in a metro area with at least 1 million residents or more",
            "Noncore adjacent to micro area and does not contain a town",
        ],
        "2000 Population": [43671.0, float("nan"), 5920.0],
        "2000 Persons per square mile": [
            73.27742041665574,
            float("nan"),
            1.212475413729223,
        ],
        "1993 Urban Influence Code": [2, 1, 9],
        "1993 Urban Influence Code description": [
            "Small-in a metro area with fewer than 1 million residents",
            "Large-in a metro area with at least 1 million residents or more",
            "Not adjacent to a metro area and does not contain a town",
        ],
    }
)

DF_2003_PR = pd.DataFrame(
    {
        "FIPS Code": [72001, 72003],
        "State": ["PR", "PR"],
        "Municipio Name": ["Adjuntas Municipio", "Aguada Municipio"],
        "Population 2003 ": [19143, 42042],
        "Urban Influence  Code, 2003": [5, 3],
        "Description of the 2003 Code": [
            "Micropolitan adjacent to a small metro area",
            "Micropolitan adjacent to a large metro area",
        ],
    }
)

XLSX_2013 = build_xlsx(DF_2013, SHEET_2013)
XLSX_2003_1993 = build_xlsx(DF_2003_1993, SHEET_2003_1993)
XLSX_2003_PR = build_xlsx(DF_2003_PR, SHEET_2003_PR)
CSV_2024 = build_2024_csv(CSV_2024_ROWS)


class TestErsUrbanInfluenceCodesUtils:
    """Tests for the ers_urban_influence_codes utils module."""

    def test_vintage_catalog(self):
        """The vintage catalog holds four labeled vintages."""
        assert VINTAGES == ("2024", "2013", "2003", "1993")
        assert set(VINTAGE_LABELS) == set(VINTAGES)
        assert MEDIA_2024_CSV.endswith("2024-urban-influence-codes.csv")
        assert MEDIA_2013_XLS.endswith(".xls")
        assert "us-counties" in MEDIA_2003_1993_XLS
        assert "puerto-rico" in MEDIA_2003_PR_XLS

    def test_state_catalog(self):
        """The state map covers 50 states, DC, and five territories."""
        assert len(STATE_LABELS) == 56
        assert STATE_LABELS["AL"] == "Alabama"
        assert STATE_LABELS["DC"] == "District of Columbia"
        assert STATE_LABELS["PR"] == "Puerto Rico"
        assert frozenset({"AS", "GU", "MP", "PR", "VI"}) == ALL_TERRITORIES

    def test_allowed_states_per_vintage(self):
        """Each vintage exposes its published state and territory set."""
        assert len(allowed_states("2024")) == 56
        assert len(allowed_states("2013")) == 52
        assert len(allowed_states("2003")) == 52
        assert len(allowed_states("1993")) == 51
        assert "PR" in allowed_states("2013")
        assert "GU" in allowed_states("2024")
        assert "GU" not in allowed_states("2013")
        assert "PR" not in allowed_states("1993")

    def test_state_options(self):
        """State options are label/value pairs scoped to the vintage."""
        options = state_options("1993")
        assert len(options) == 51
        assert {"label": "Alaska", "value": "AK"} in options
        assert all(opt["value"] not in ALL_TERRITORIES for opt in options)
        assert {"label": "Puerto Rico", "value": "PR"} in state_options("2003")

    def test_fips5(self):
        """FIPS codes are zero-padded to five characters."""
        assert uic._fips5(1001) == "01001"
        assert uic._fips5("01001") == "01001"
        assert uic._fips5(72001) == "72001"
        assert uic._fips5(1001.0) == "01001"

    def test_clean_text(self):
        """Text collapses runs of whitespace; NaN and blanks become None."""
        assert uic._clean_text("Small-in a metro area   ") == "Small-in a metro area"
        assert uic._clean_text("a  b   c") == "a b c"
        assert uic._clean_text(float("nan")) is None
        assert uic._clean_text("") is None
        assert uic._clean_text(None) is None

    def test_text_int(self):
        """CSV integer strings parse to ints; blanks and junk become None."""
        assert uic._text_int("58805") == 58805
        assert uic._text_int("0") == 0
        assert uic._text_int("") is None
        assert uic._text_int(None) is None
        assert uic._text_int("n/a") is None

    def test_cell_number(self):
        """Spreadsheet cells return native numbers; NaN and None become None."""
        assert uic._cell_number(54571) == 54571
        assert uic._cell_number(1.212475413729223) == 1.212475413729223
        assert uic._cell_number(float("nan")) is None
        assert uic._cell_number(None) is None
        assert uic._cell_number(pd.array([73.5])[0]) == 73.5

    def test_code(self):
        """Codes render as bare ordinal strings; NaN and blanks become None."""
        assert uic._code(4) == "4"
        assert uic._code(12.0) == "12"
        assert uic._code("5") == "5"
        assert uic._code(float("nan")) is None
        assert uic._code("") is None
        assert uic._code(None) is None

    def test_parse_2024_csv_pivots_long_to_wide(self):
        """The long 2024 CSV pivots to one record per county FIPS."""
        records = parse_2024_csv(CSV_2024)
        assert {r["fips"] for r in records} == {"01001", "01005", "02013", "60030"}
        autauga = next(r for r in records if r["fips"] == "01001")
        assert autauga["state"] == "AL"
        assert autauga["county_name"] == "Autauga County"
        assert autauga["urban_influence_code"] == "4"
        assert autauga["population"] == 58805
        assert autauga["population_density"] is None
        assert "fewer than 1 million" in autauga["description"]

    def test_parse_2024_csv_missing_code(self):
        """A county lacking a UIC row surfaces a null code with its text."""
        records = parse_2024_csv(CSV_2024)
        samoa = next(r for r in records if r["fips"] == "60030")
        assert samoa["urban_influence_code"] is None
        assert samoa["population"] == 0
        assert samoa["description"] == "Not Applicable"

    def test_parse_2013_xls(self):
        """The wide 2013 workbook parses to unified records without density."""
        records = parse_2013_xls(XLSX_2013)
        assert len(records) == 2
        first = records[0]
        assert first["fips"] == "01001"
        assert first["urban_influence_code"] == "2"
        assert first["population"] == 54571
        assert first["population_density"] is None
        assert first["description"].endswith("1 million residents")

    def test_parse_2003_combined(self):
        """The combined workbook's 2003 columns parse with 2000-census density."""
        records = parse_2003_combined(XLSX_2003_1993)
        sublette = next(r for r in records if r["fips"] == "56035")
        assert sublette["urban_influence_code"] == "10"
        assert sublette["population"] == 5920.0
        assert sublette["population_density"] == 1.212475413729223
        broomfield = next(r for r in records if r["fips"] == "08014")
        assert broomfield["population"] is None
        assert broomfield["population_density"] is None

    def test_parse_1993_combined(self):
        """The combined workbook's 1993 columns use the 2000-census population."""
        records = parse_1993_combined(XLSX_2003_1993)
        sublette = next(r for r in records if r["fips"] == "56035")
        assert sublette["urban_influence_code"] == "9"
        assert sublette["population"] == 5920.0
        assert sublette["population_density"] == 1.212475413729223

    def test_parse_2003_pr(self):
        """The Puerto Rico workbook parses its quirky headers without density."""
        records = parse_2003_pr(XLSX_2003_PR)
        assert len(records) == 2
        adjuntas = records[0]
        assert adjuntas["fips"] == "72001"
        assert adjuntas["state"] == "PR"
        assert adjuntas["county_name"] == "Adjuntas Municipio"
        assert adjuntas["urban_influence_code"] == "5"
        assert adjuntas["population"] == 19143
        assert adjuntas["population_density"] is None

    def test_afetch_vintage_2024(self, monkeypatch):
        """The 2024 vintage fetches and pivots the CSV file."""

        async def fake_fetch(media_path, product=None, ttl=None):
            assert media_path == MEDIA_2024_CSV
            return CSV_2024.encode("utf-8-sig")

        monkeypatch.setattr(
            "openbb_government_us.usda.utils.ers_client.afetch_ers_file", fake_fetch
        )
        records = asyncio.run(uic.afetch_vintage("2024"))
        assert {r["fips"] for r in records} == {"01001", "01005", "02013", "60030"}

    def test_afetch_vintage_2013(self, monkeypatch):
        """The 2013 vintage fetches and parses the wide workbook."""

        async def fake_fetch(media_path, product=None, ttl=None):
            assert media_path == MEDIA_2013_XLS
            return XLSX_2013

        monkeypatch.setattr(
            "openbb_government_us.usda.utils.ers_client.afetch_ers_file", fake_fetch
        )
        records = asyncio.run(uic.afetch_vintage("2013"))
        assert {r["fips"] for r in records} == {"01001", "01005"}

    def test_afetch_vintage_2003_appends_puerto_rico(self, monkeypatch):
        """The 2003 vintage appends the Puerto Rico municipios to U.S. counties."""

        async def fake_fetch(media_path, product=None, ttl=None):
            if media_path == MEDIA_2003_1993_XLS:
                return XLSX_2003_1993
            assert media_path == MEDIA_2003_PR_XLS
            return XLSX_2003_PR

        monkeypatch.setattr(
            "openbb_government_us.usda.utils.ers_client.afetch_ers_file", fake_fetch
        )
        records = asyncio.run(uic.afetch_vintage("2003"))
        states = {r["state"] for r in records}
        assert "PR" in states
        assert "72001" in {r["fips"] for r in records}

    def test_afetch_vintage_1993(self, monkeypatch):
        """The 1993 vintage reads the combined workbook without Puerto Rico."""

        async def fake_fetch(media_path, product=None, ttl=None):
            assert media_path == MEDIA_2003_1993_XLS
            return XLSX_2003_1993

        monkeypatch.setattr(
            "openbb_government_us.usda.utils.ers_client.afetch_ers_file", fake_fetch
        )
        records = asyncio.run(uic.afetch_vintage("1993"))
        assert "PR" not in {r["state"] for r in records}

    def test_afetch_vintage_invalid_raises(self):
        """An unknown vintage raises OpenBBError listing valid choices."""
        with pytest.raises(OpenBBError, match="Invalid vintage: 1900"):
            asyncio.run(uic.afetch_vintage("1900"))


class TestUrbanInfluenceCodes:
    """Tests for the UrbanInfluenceCodes model."""

    def test_transform_query(self):
        """transform_query builds the query params model."""
        query = UrbanInfluenceCodesFetcher.transform_query(
            {"vintage": "2003", "state": "WY"}
        )
        assert isinstance(query, UrbanInfluenceCodesQueryParams)
        assert query.vintage == "2003"
        assert query.state == "WY"

    def test_vintage_defaults_and_blank(self):
        """The vintage defaults to 2024 and blanks fall back."""
        assert UrbanInfluenceCodesQueryParams().vintage == "2024"
        assert UrbanInfluenceCodesQueryParams(vintage="").vintage == "2024"
        assert UrbanInfluenceCodesQueryParams(vintage=["2013"]).vintage == "2013"

    def test_unknown_vintage_raises(self):
        """Unknown vintages raise OpenBBError listing valid choices."""
        with pytest.raises(OpenBBError, match="Invalid vintage: 1900"):
            UrbanInfluenceCodesQueryParams(vintage="1900")

    def test_state_defaults_and_normalizes(self):
        """State defaults to None, uppercases, and takes the first of a list."""
        assert UrbanInfluenceCodesQueryParams().state is None
        assert UrbanInfluenceCodesQueryParams(state="").state is None
        assert UrbanInfluenceCodesQueryParams(state="   ").state is None
        assert UrbanInfluenceCodesQueryParams(state="al").state == "AL"
        assert UrbanInfluenceCodesQueryParams(state=["wy"]).state == "WY"

    def test_unknown_state_raises(self):
        """An unknown state code raises OpenBBError."""
        with pytest.raises(OpenBBError, match="Invalid state: ZZ"):
            UrbanInfluenceCodesQueryParams(state="ZZ")

    def test_state_scoped_to_vintage(self):
        """A state outside a vintage's published set raises OpenBBError."""
        with pytest.raises(OpenBBError, match="Invalid state 'GU' for vintage '2013'"):
            UrbanInfluenceCodesQueryParams(vintage="2013", state="GU")
        assert UrbanInfluenceCodesQueryParams(vintage="2024", state="GU").state == "GU"

    def test_aextract_data_passes_vintage(self, monkeypatch):
        """aextract_data forwards the vintage to afetch_vintage."""
        calls = []

        async def fake_afetch_vintage(vintage):
            calls.append(vintage)
            return parse_2024_csv(CSV_2024)

        monkeypatch.setattr(uic, "afetch_vintage", fake_afetch_vintage)
        query = UrbanInfluenceCodesFetcher.transform_query({"vintage": "2024"})
        records = asyncio.run(UrbanInfluenceCodesFetcher.aextract_data(query, None))
        assert calls == ["2024"]
        assert records

    def test_transform_data_filters_by_state(self):
        """transform_data keeps only the selected state's counties."""
        records = parse_2024_csv(CSV_2024)
        query = UrbanInfluenceCodesFetcher.transform_query(
            {"vintage": "2024", "state": "AL"}
        )
        data = UrbanInfluenceCodesFetcher.transform_data(query, records)
        assert {row.state for row in data} == {"AL"}
        assert {row.fips for row in data} == {"01001", "01005"}

    def test_transform_data_all_states_sorted_by_fips(self):
        """With no state filter every county returns, sorted by FIPS."""
        records = parse_2024_csv(CSV_2024)
        query = UrbanInfluenceCodesFetcher.transform_query({"vintage": "2024"})
        data = UrbanInfluenceCodesFetcher.transform_data(query, records)
        assert [row.fips for row in data] == ["01001", "01005", "02013", "60030"]

    def test_transform_data_density_populated_for_2003(self):
        """The 2003 vintage carries a high-precision population density."""
        records = parse_2003_combined(XLSX_2003_1993)
        query = UrbanInfluenceCodesFetcher.transform_query(
            {"vintage": "2003", "state": "WY"}
        )
        data = UrbanInfluenceCodesFetcher.transform_data(query, records)
        assert data[0].population_density == 1.212475413729223

    def test_transform_data_empty_raises(self):
        """A state slice with no rows raises EmptyDataError."""
        records = parse_2024_csv(CSV_2024)
        query = UrbanInfluenceCodesFetcher.transform_query(
            {"vintage": "2024", "state": "WY"}
        )
        with pytest.raises(EmptyDataError, match="No records match"):
            UrbanInfluenceCodesFetcher.transform_data(query, records)

    def test_columns_defs_bind_to_served_keys(self):
        """Every declared column definition binds to a served row key."""
        records = parse_2024_csv(CSV_2024)
        query = UrbanInfluenceCodesFetcher.transform_query({"vintage": "2024"})
        data = UrbanInfluenceCodesFetcher.transform_data(query, records)
        served = set(data[0].model_dump(by_alias=True))
        schema = UrbanInfluenceCodesData.model_json_schema(
            by_alias=True, mode="serialization"
        )
        column_fields = [to_snake(key) for key in schema["properties"]]
        assert column_fields, "no column definitions generated"
        for field in column_fields:
            assert field in served, field
        assert served == set(column_fields)

    def test_code_and_fips_columns_are_text(self):
        """FIPS, state, and code columns declare a text cell data type."""
        fields = UrbanInfluenceCodesData.model_fields
        for name in ("fips", "state", "urban_influence_code"):
            config = fields[name].json_schema_extra["x-widget_config"]
            assert config["cellDataType"] == "text"

    def test_population_density_hidden(self):
        """The population density column is hidden so no empty column renders."""
        config = UrbanInfluenceCodesData.model_fields[
            "population_density"
        ].json_schema_extra["x-widget_config"]
        assert config["hide"] is True
        assert config["cellDataType"] == "number"

    def test_widget_config_metadata(self):
        """The whole-widget config carries the ERS category and source."""
        config = UrbanInfluenceCodesData.model_config["json_schema_extra"][
            "x-widget_config"
        ]
        assert config["$.category"] == "Economy"
        assert config["$.subCategory"] == "Agriculture"
        assert config["$.source"] == ["USDA", "ERS"]
