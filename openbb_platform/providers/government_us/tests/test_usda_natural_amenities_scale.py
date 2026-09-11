"""Tests for the USDA ERS natural amenities scale utils and model."""

import asyncio

import pytest
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic.alias_generators import to_snake

from openbb_government_us.usda.models.natural_amenities_scale import (
    NaturalAmenitiesScaleData as NasData,
    NaturalAmenitiesScaleFetcher as NasFetcher,
    NaturalAmenitiesScaleQueryParams as NasQuery,
)
from openbb_government_us.usda.utils import ers_natural_amenities_scale as ers
from openbb_government_us.usda.utils.ers_natural_amenities_scale import (
    ALL_STATES,
    CANONICAL_COLUMNS,
    COLUMN_SPECS,
    DATA_START,
    MEDIA_PATH,
    PRODUCT_PAGE,
    SHEET,
    STATE_NAMES,
    STATES,
    _to_code,
    _to_num,
    _to_text,
    afetch_records,
    parse_rows,
    state_options,
)

HEADER_ROW: list = [
    "FIPS Code", "Combined", "STATE", "County name", "Division", "code",
    "Code", "Temp Jan", "Sun Jan", "Temp Jul", "Hum Jul", "topography",
    "Percent", "Log", "JAN TEMP - Z", "JAN SUN - Z", "JUL TEMP - Z",
    "JUL HUM - Z", "TOPOG - Z", "LN WATER AREA - Z", "Scale", "rank",
]  # fmt: skip

DATA_ROWS: list[list] = [
    [
        "44001",
        "44001",
        "RI",
        "BRISTOL",
        1.0,
        2.0,
        2.0,
        28.4,
        168.0,
        72.1,
        67.0,
        4.0,
        44.8,
        8.407,
        -0.36902,
        0.49656,
        0.62448,
        -0.75347,
        -0.73966,
        2.09933,
        1.36,
        4.0,
    ],  # fmt: skip
    [
        "01003",
        "01003",
        "AL",
        "BALDWIN",
        6.0,
        2.0,
        2.0,
        51.9,
        152.0,
        80.6,
        72.0,
        4.0,
        21.24,
        7.661,
        1.57504,
        0.01482,
        0.36308,
        -1.09576,
        -0.73966,
        1.70428,
        1.82,
        4.0,
    ],  # fmt: skip
    [
        "44005",
        "44005",
        "RI",
        "NEWPORT",
        1.0,
        4.0,
        5.0,
        28.3,
        168.0,
        69.9,
        67.0,
        4.0,
        66.82,
        8.807,
        -0.37729,
        0.49656,
        1.20740,
        -0.75347,
        -0.73966,
        2.31099,
        2.14,
        4.0,
    ],  # fmt: skip
    [
        "01001",
        "01001",
        "AL",
        "AUTAUGA",
        6.0,
        2.0,
        2.0,
        47.4,
        130.0,
        81.0,
        66.0,
        14.0,
        1.4,
        4.944,
        1.20277,
        -0.64758,
        -0.13206,
        -0.68502,
        0.77701,
        0.26585,
        0.78,
        4.0,
    ],  # fmt: skip
    [
        "51515",
        "51019",
        "VA",
        "BEDFORD CITY",
        5.0,
        4.0,
        5.0,
        36.0,
        150.0,
        75.0,
        55.0,
        10.0,
        0.1,
        2.0,
        0.1,
        0.2,
        0.3,
        0.4,
        0.5,
        0.6,
        2.1,
        5.0,
    ],  # fmt: skip
]

COMPACT_ROWS: list[list] = [["title"], HEADER_ROW, *DATA_ROWS]


def _padded(data_rows: list[list]) -> list[list]:
    """Prefix data rows with DATA_START blank rows to exercise the offset."""
    return [["" for _ in range(22)] for _ in range(DATA_START)] + data_rows


class _FakeXlsSheet:
    """Minimal xlrd sheet standing in for the NATAMENF worksheet."""

    def __init__(self, rows: list[list]) -> None:
        self._rows = rows
        self.nrows = len(rows)
        self.ncols = max((len(row) for row in rows), default=0)

    def cell_value(self, r: int, c: int):
        """Return the cell value, blank past a short row's end."""
        row = self._rows[r]
        return row[c] if c < len(row) else ""


class _FakeXlsBook:
    """Minimal xlrd workbook returning one fake sheet by name."""

    def __init__(self, rows: list[list]) -> None:
        self._rows = rows

    def sheet_by_name(self, name: str) -> _FakeXlsSheet:
        """Return the fake sheet regardless of requested name."""
        return _FakeXlsSheet(self._rows)


class TestErsNaturalAmenitiesScaleUtils:
    """Tests for the ers natural amenities scale utils module."""

    def test_catalog(self):
        """The catalog points at the single NATAMENF workbook and offset."""
        assert MEDIA_PATH == (
            "/media/6172/natural-amenities-scale-including-the-6-components"
            "-for-us-counties.xls"
        )
        assert SHEET == "NATAMENF"
        assert DATA_START == 105
        assert PRODUCT_PAGE.endswith("natural-amenities-scale")

    def test_canonical_columns(self):
        """There are 22 canonical columns in source order."""
        assert len(CANONICAL_COLUMNS) == 22
        assert len(COLUMN_SPECS) == 22
        assert CANONICAL_COLUMNS[0] == "fips"
        assert CANONICAL_COLUMNS[1] == "fips_used_for_measures"
        assert CANONICAL_COLUMNS[-2] == "natural_amenity_scale"
        assert CANONICAL_COLUMNS[-1] == "natural_amenity_rank"
        kinds = {name: kind for name, kind in COLUMN_SPECS}
        assert kinds["fips"] == "text"
        assert kinds["census_division"] == "code"
        assert kinds["natural_amenity_rank"] == "code"
        assert kinds["natural_amenity_scale"] == "num"

    def test_state_options(self):
        """State options cover the 48 contiguous states plus DC."""
        options = state_options()
        values = [opt["value"] for opt in options]
        assert len(values) == 49
        assert values == sorted(values)
        assert "DC" in values
        assert "AK" not in values
        assert "HI" not in values
        assert "PR" not in values
        labels = {opt["label"] for opt in options}
        assert "District of Columbia" in labels
        assert set(values) == set(STATES) == set(ALL_STATES)
        assert STATE_NAMES["RI"] == "Rhode Island"

    def test_to_text(self):
        """Text coercion strips and maps blanks to None."""
        assert _to_text("AL") == "AL"
        assert _to_text("  AUTAUGA ") == "AUTAUGA"
        assert _to_text(5) == "5"
        assert _to_text(None) is None
        assert _to_text("") is None
        assert _to_text("   ") is None

    def test_to_code(self):
        """Code coercion renders integer-valued cells as plain code strings."""
        assert _to_code(6.0) == "6"
        assert _to_code(14.0) == "14"
        assert _to_code(2) == "2"
        assert _to_code("7") == "7"
        assert _to_code(None) is None
        assert _to_code("") is None
        assert _to_code("   ") is None
        assert _to_code("NA") == "NA"

    def test_to_num(self):
        """Number coercion preserves full precision and maps blanks to None."""
        assert _to_num(28.4) == 28.4
        assert _to_num("2.09933") == 2.09933
        assert _to_num(-0.75347) == -0.75347
        assert _to_num(0) == 0.0
        assert _to_num(None) is None
        assert _to_num("") is None
        assert _to_num("  ") is None
        assert _to_num("x") is None

    def test_parse_rows_compact(self):
        """Parsing the compact fixture skips the title and header rows."""
        records = parse_rows(COMPACT_ROWS, data_start=2)
        assert [record["fips"] for record in records] == [
            "44001",
            "01003",
            "44005",
            "01001",
            "51515",
        ]
        autauga = next(r for r in records if r["fips"] == "01001")
        assert autauga["state"] == "AL"
        assert autauga["county_name"] == "AUTAUGA"
        assert autauga["census_division"] == "6"
        assert autauga["rural_urban_continuum_code"] == "2"
        assert autauga["urban_influence_code"] == "2"
        assert autauga["topography_code"] == "14"
        assert autauga["natural_amenity_rank"] == "4"
        assert autauga["mean_january_temperature"] == 47.4
        assert autauga["natural_amenity_scale"] == 0.78
        assert autauga["log_water_area_z"] == 0.26585

    def test_parse_rows_uses_default_offset(self):
        """Parsing with the default offset starts at DATA_START."""
        records = parse_rows(_padded(DATA_ROWS))
        assert len(records) == 5
        assert {record["state"] for record in records} == {"RI", "AL", "VA"}

    def test_parse_rows_combined_county_fips(self):
        """A combined county carries a measures FIPS distinct from its own."""
        records = parse_rows(COMPACT_ROWS, data_start=2)
        combined = next(r for r in records if r["fips"] == "51515")
        assert combined["fips_used_for_measures"] == "51019"
        assert combined["fips"] != combined["fips_used_for_measures"]

    def test_parse_rows_skips_blank_first_cell(self):
        """Rows with a blank first cell or no cells emit no record."""
        rows = [
            ["title"],
            HEADER_ROW,
            ["", "", "AL", "GHOST", 6.0],
            [],
            DATA_ROWS[3],
        ]
        records = parse_rows(rows, data_start=2)
        assert [record["fips"] for record in records] == ["01001"]

    def test_afetch_records(self, monkeypatch):
        """afetch_records fetches through the cache and parses the sheet."""
        calls = []

        async def fake_afetch_ers_file(media, product=None, ttl=None):
            calls.append((media, product))
            return b"legacy-xls-bytes"

        monkeypatch.setattr(
            "openbb_government_us.usda.utils.ers_client.afetch_ers_file",
            fake_afetch_ers_file,
        )
        monkeypatch.setattr(
            "xlrd.open_workbook",
            lambda file_contents=None: _FakeXlsBook(_padded(DATA_ROWS)),
        )
        records = asyncio.run(afetch_records())
        assert calls == [(MEDIA_PATH, PRODUCT_PAGE)]
        assert {record["state"] for record in records} == {"RI", "AL", "VA"}
        assert any(record["county_name"] == "NEWPORT" for record in records)


class TestNaturalAmenitiesScale:
    """Tests for the NaturalAmenitiesScale model."""

    def _rows(self):
        """Parse the compact fixture into canonical records."""
        return parse_rows(COMPACT_ROWS, data_start=2)

    def test_transform_query_defaults(self):
        """transform_query leaves the optional state unset."""
        query = NasFetcher.transform_query({})
        assert isinstance(query, NasQuery)
        assert query.state is None

    def test_blank_state_falls_back_to_none(self):
        """A blank state normalizes to None."""
        assert NasQuery(state="").state is None
        assert NasQuery(state="   ").state is None

    def test_invalid_state_raises(self):
        """An unknown state raises OpenBBError."""
        with pytest.raises(OpenBBError, match="Invalid state: ZZ"):
            NasQuery(state="ZZ")

    def test_alaska_is_rejected(self):
        """Alaska is not scored and is rejected as a state filter."""
        with pytest.raises(OpenBBError, match="Invalid state: AK"):
            NasQuery(state="AK")

    def test_state_uppercases(self):
        """State input is upper-cased and trimmed."""
        assert NasQuery(state="ri").state == "RI"
        assert NasQuery(state=" al ").state == "AL"

    def test_aextract_data_returns_records(self, monkeypatch):
        """aextract_data returns the parsed county records."""

        async def fake_afetch_records():
            return self._rows()

        monkeypatch.setattr(ers, "afetch_records", fake_afetch_records)
        query = NasFetcher.transform_query({})
        records = asyncio.run(NasFetcher.aextract_data(query, None))
        assert {record["state"] for record in records} == {"RI", "AL", "VA"}

    def test_transform_data_all_states_sorts_by_fips(self):
        """The default view keeps every county and sorts by FIPS ascending."""
        query = NasFetcher.transform_query({})
        data = NasFetcher.transform_data(query, self._rows())
        assert [row.fips for row in data] == [
            "01001",
            "01003",
            "44001",
            "44005",
            "51515",
        ]

    def test_transform_data_scopes_to_state(self):
        """A state filter keeps only that state's counties."""
        query = NasFetcher.transform_query({"state": "RI"})
        data = NasFetcher.transform_data(query, self._rows())
        assert {row.state for row in data} == {"RI"}
        assert [row.fips for row in data] == ["44001", "44005"]

    def test_transform_data_empty_state_raises(self):
        """A state absent from the data raises EmptyDataError."""
        query = NasFetcher.transform_query({"state": "WY"})
        with pytest.raises(EmptyDataError):
            NasFetcher.transform_data(query, self._rows())

    def test_lookup_is_one_row_per_fips_no_year_column(self):
        """Every row is a county lookup carrying the 22 fields, no year column."""
        query = NasFetcher.transform_query({"state": "AL"})
        data = NasFetcher.transform_data(query, self._rows())
        assert len(data) == 2
        served = set(data[0].model_dump(by_alias=True))
        assert served == set(CANONICAL_COLUMNS)
        assert "year" not in served

    def test_codes_serialize_as_text(self):
        """Classification codes serialize as plain code strings, not numbers."""
        query = NasFetcher.transform_query({"state": "AL"})
        row = NasFetcher.transform_data(query, self._rows())[0].model_dump(
            by_alias=True
        )
        assert row["census_division"] == "6"
        assert row["rural_urban_continuum_code"] == "2"
        assert row["topography_code"] == "14"
        assert row["natural_amenity_rank"] == "4"
        assert row["natural_amenity_scale"] == 0.78
        assert row["mean_january_temperature"] == 47.4

    def test_columns_defs_bind_to_served_keys(self):
        """Every declared column definition binds to a served record key."""
        declared = set()
        for name, field in NasData.model_fields.items():
            alias = field.serialization_alias or name
            extra = field.json_schema_extra
            config = extra.get("x-widget_config", {}) if isinstance(extra, dict) else {}
            if config.get("exclude"):
                continue
            declared.add(to_snake(alias))
        assert declared == set(CANONICAL_COLUMNS)
        query = NasFetcher.transform_query({})
        data = NasFetcher.transform_data(query, self._rows())
        served = set()
        for row in data:
            served.update(row.model_dump(by_alias=True))
        assert declared == served

    def test_no_dead_constant_column(self):
        """Every served key carries a declared column definition."""
        declared = set(CANONICAL_COLUMNS)
        query = NasFetcher.transform_query({})
        data = NasFetcher.transform_data(query, self._rows())
        for row in data:
            for key in row.model_dump(by_alias=True):
                assert to_snake(key) in declared

    def test_fips_used_for_measures_hidden_but_served(self):
        """The measures-FIPS column is served but hidden by default."""
        config = NasData.model_fields["fips_used_for_measures"].json_schema_extra[
            "x-widget_config"
        ]
        assert config["hide"] is True
        assert config["cellDataType"] == "text"
        query = NasFetcher.transform_query({"state": "VA"})
        dumped = NasFetcher.transform_data(query, self._rows())[0].model_dump(
            by_alias=True
        )
        assert "fips_used_for_measures" in dumped
        assert dumped["fips_used_for_measures"] == "51019"

    def test_param_scoping_options(self):
        """The state param is single-select with a real label and static options."""
        extra = NasQuery.__json_schema_extra__
        state = extra["state"]["x-widget_config"]
        assert state["label"] == "State"
        assert state["multiSelect"] is False
        assert state["multiple"] is False
        assert "value" not in state
        values = [opt["value"] for opt in state["options"]]
        assert len(values) == 49
        assert "DC" in values
        assert "AK" not in values

    def test_widget_config_and_column_headers(self):
        """The whole-widget config and per-field headers are populated."""
        widget = NasData.model_config["json_schema_extra"]["x-widget_config"]
        assert widget["$.name"] == "USDA ERS Natural Amenities Scale"
        assert widget["$.category"] == "Economy"
        assert widget["$.subCategory"] == "Agriculture"
        assert widget["$.source"] == ["USDA", "ERS"]
        fields = NasData.model_fields
        for name in ("fips", "state", "county_name"):
            assert fields[name].json_schema_extra["x-widget_config"]["pinned"] == "left"
        for name in (
            "fips",
            "state",
            "census_division",
            "topography_code",
            "natural_amenity_rank",
        ):
            config = fields[name].json_schema_extra["x-widget_config"]
            assert config["cellDataType"] == "text"
        for name in (
            "mean_january_temperature",
            "natural_amenity_scale",
            "log_water_area_z",
        ):
            config = fields[name].json_schema_extra["x-widget_config"]
            assert config["cellDataType"] == "number"

    def test_null_token_mixin_coerces_placeholder(self):
        """The Data model coerces placeholder tokens to None but keeps columns."""
        row = NasData.model_validate(
            {"fips": "44001", "state": "RI", "natural_amenity_scale": "--"}
        )
        dumped = row.model_dump(by_alias=True)
        assert dumped["fips"] == "44001"
        assert dumped["natural_amenity_scale"] is None
        assert "natural_amenity_scale" in dumped
