"""Tests for the USDA ERS frontier and remote area codes utils and model."""

import asyncio
import io

import pytest
from openbb_core.app.model.abstract.error import OpenBBError
from pydantic.alias_generators import to_snake

from openbb_government_us.usda.models.frontier_and_remote_area_codes import (
    FrontierAndRemoteAreaCodesData as FarData,
    FrontierAndRemoteAreaCodesFetcher as FarFetcher,
    FrontierAndRemoteAreaCodesQueryParams as FarQuery,
)
from openbb_government_us.usda.utils import (
    ers_frontier_and_remote_area_codes as ers,
)
from openbb_government_us.usda.utils.ers_frontier_and_remote_area_codes import (
    ALL_STATES,
    CANONICAL_COLUMNS,
    CANONICAL_COLUMNS_NO_NAME,
    FAR_ZIP_FILES,
    PRODUCT_PAGE,
    STATES_49,
    STATES_51,
    _map_row,
    _to_float,
    _to_int,
    _to_str,
    media_path,
    parse_rows,
    state_options,
    year_options,
)

FAR_2020_HEADER: list = [
    "ZIPCode", "State", "POName", "FAR1", "FAR2", "FAR3", "FAR4", "GridPop",
    "GridArea", "PopDensity", "FAR1Pop", "FAR2Pop", "FAR3Pop", "FAR4Pop",
    "FAR1PopPct", "FAR2PopPct", "FAR3PopPct", "FAR4PopPct",
]  # fmt: skip

FAR_2020_ROWS: list[list] = [
    ["2020 Frontier and Remote area codes: Data for ZIP Codes"],
    FAR_2020_HEADER,
    [
        "59003",
        "MT",
        "Ashland",
        1,
        1,
        1,
        1,
        257,
        35.897,
        7.2,
        257,
        257,
        257,
        257,
        100,
        100,
        100,
        100,
    ],
    [
        "59010",
        "MT",
        "Bighorn",
        1,
        1,
        1,
        1,
        205,
        449.743,
        0.5,
        145,
        145,
        145,
        145,
        70.73,
        70.73,
        70.73,
        70.73,
    ],
    [
        "00063",
        "MT",
        "Benton Lake NWR",
        0,
        0,
        0,
        0,
        19,
        13.07,
        1.5,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
    ],
    [
        "00049",
        "CA",
        "Six Rivers National Forest",
        1,
        1,
        0,
        0,
        6,
        297.784,
        0,
        6,
        6,
        0,
        0,
        100,
        100,
        0,
        0,
    ],
    [
        "00177",
        "NH",
        "Pinkham Grant",
        1,
        1,
        1,
        0,
        43,
        3.737,
        11.5,
        43,
        43,
        43,
        0,
        100,
        100,
        100,
        0,
    ],
    [
        "00001",
        "AK",
        "N Dillingham",
        1,
        1,
        1,
        1,
        212,
        16018.957,
        0,
        212,
        212,
        212,
        212,
        100,
        100,
        100,
        100,
    ],
    [
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
    ],
]

FAR_2000_HEADER: list = [
    "ZIP", "state", "far1", "far2", "far3", "far4", "gridpop", "sqmi",
    "density", "fr1pop", "fr2pop", "fr3pop", "fr4pop", "pctfr1", "pctfr2",
    "pctfr3", "pctfr4",
]  # fmt: skip

FAR_2000_ROWS: list[list] = [
    FAR_2000_HEADER,
    [
        "59003",
        "MT",
        1.0,
        1.0,
        1.0,
        1.0,
        300.0,
        36.0,
        8.3,
        300.0,
        300.0,
        300.0,
        300.0,
        100.0,
        100.0,
        100.0,
        100.0,
    ],
    [
        "01001",
        "MA",
        0.0,
        0.0,
        0.0,
        0.0,
        16813.0,
        12.08,
        1391.8046,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
    ],
]


def _build_workbook(sheet_name: str, rows: list[list]) -> bytes:
    """Build in-memory XLSX bytes with one named sheet holding the given rows."""
    import openpyxl

    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = sheet_name
    for row in rows:
        sheet.append(["" if cell is None else cell for cell in row])
    buffer = io.BytesIO()
    workbook.save(buffer)
    return buffer.getvalue()


class _FakeXlsSheet:
    """Minimal xlrd sheet standing in for a legacy .xls worksheet."""

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


class TestErsFrontierAndRemoteAreaCodesUtils:
    """Tests for the ers frontier and remote area codes utils module."""

    def test_catalog(self):
        """The catalog points at the three ZIP vintages with their sheets."""
        assert list(FAR_ZIP_FILES) == ["2020", "2010", "2000"]
        assert FAR_ZIP_FILES["2020"]["media_id"] == 7072
        assert FAR_ZIP_FILES["2010"]["media_id"] == 5621
        assert FAR_ZIP_FILES["2000"]["media_id"] == 5618
        assert FAR_ZIP_FILES["2020"]["ext"] == "xlsx"
        assert FAR_ZIP_FILES["2000"]["ext"] == "xls"
        assert FAR_ZIP_FILES["2020"]["sheet"] == "FAR2020 ZIP Code Data"
        assert FAR_ZIP_FILES["2010"]["sheet"] == "FAR ZIP Code Data"
        assert FAR_ZIP_FILES["2000"]["sheet"] == "FAR ZIP Code Data"
        assert FAR_ZIP_FILES["2020"]["data_start"] == 2
        assert FAR_ZIP_FILES["2000"]["data_start"] == 1
        assert PRODUCT_PAGE.endswith("frontier-and-remote-area-codes")

    def test_media_path(self):
        """The media path is built from the media id, slug, and extension."""
        assert media_path("2020") == "/media/7072/2020-far-codes-zip-codes.xlsx"
        assert media_path("2010") == "/media/5621/2010-far-codes-zip-codes.xlsx"
        assert media_path("2000") == "/media/5618/2000-far-codes-zip-codes.xls"

    def test_canonical_columns(self):
        """The canonical columns are eighteen; the 2000 vintage drops po_name."""
        assert len(CANONICAL_COLUMNS) == 18
        assert CANONICAL_COLUMNS[0] == "zip_code"
        assert CANONICAL_COLUMNS[2] == "po_name"
        assert len(CANONICAL_COLUMNS_NO_NAME) == 17
        assert "po_name" not in CANONICAL_COLUMNS_NO_NAME
        assert list(CANONICAL_COLUMNS_NO_NAME) == [
            name for name in CANONICAL_COLUMNS if name != "po_name"
        ]

    def test_year_options(self):
        """The vintage options are labeled newest-first."""
        options = year_options()
        assert [opt["value"] for opt in options] == ["2020", "2010", "2000"]
        assert all(opt["label"] == opt["value"] for opt in options)

    def test_state_options(self):
        """State options cover 51 states in 2020 and 2010, and 49 in 2000."""
        assert [opt["value"] for opt in state_options("2020")] == list(STATES_51)
        assert [opt["value"] for opt in state_options("2010")] == list(STATES_51)
        assert [opt["value"] for opt in state_options("2000")] == list(STATES_49)
        assert "AK" in {opt["value"] for opt in state_options("2020")}
        assert "AK" not in {opt["value"] for opt in state_options("2000")}
        assert state_options("bogus") == state_options("2020")

    def test_state_constants(self):
        """STATES_49 is STATES_51 without Alaska and Hawaii; ALL_STATES is the union."""
        assert len(STATES_51) == 51
        assert len(STATES_49) == 49
        assert set(STATES_49) == set(STATES_51) - {"AK", "HI"}
        assert frozenset(STATES_51) == ALL_STATES

    def test_to_str(self):
        """String coercion strips text and maps blanks to None."""
        assert _to_str("MT") == "MT"
        assert _to_str("  Ashland ") == "Ashland"
        assert _to_str(5) == "5"
        assert _to_str(None) is None
        assert _to_str("") is None
        assert _to_str("   ") is None

    def test_to_int(self):
        """Integer coercion maps float flags and numeric strings to ints."""
        assert _to_int(1.0) == 1
        assert _to_int(0.0) == 0
        assert _to_int(1) == 1
        assert _to_int("1") == 1
        assert _to_int(None) is None
        assert _to_int("") is None
        assert _to_int("   ") is None
        assert _to_int("x") is None

    def test_to_float(self):
        """Float coercion preserves full precision and maps blanks to None."""
        assert _to_float(7.2) == 7.2
        assert _to_float("7.2") == 7.2
        assert _to_float(79.3377446906404) == 79.3377446906404
        assert _to_float(0) == 0.0
        assert _to_float(None) is None
        assert _to_float("") is None
        assert _to_float("  ") is None
        assert _to_float("x") is None

    def test_map_row_2020(self):
        """A 2020 row maps to all eighteen keys with the right types."""
        record = _map_row(FAR_2020_ROWS[2], CANONICAL_COLUMNS)
        assert set(record) == set(CANONICAL_COLUMNS)
        assert record["zip_code"] == "59003"
        assert record["state"] == "MT"
        assert record["po_name"] == "Ashland"
        assert record["far_level_1"] == 1
        assert isinstance(record["far_level_1"], int)
        assert record["grid_population"] == 257.0
        assert record["land_area_sq_mi"] == 35.897
        assert record["far_level_1_population_pct"] == 100.0

    def test_map_row_no_name_and_short_row(self):
        """The 2000 column map omits po_name and short rows pad to None."""
        record = _map_row(FAR_2000_ROWS[1], CANONICAL_COLUMNS_NO_NAME)
        assert "po_name" not in record
        assert record["far_level_1"] == 1
        short = _map_row(["94582", "CA"], CANONICAL_COLUMNS)
        assert short["zip_code"] == "94582"
        assert short["po_name"] is None
        assert short["far_level_1"] is None
        assert short["grid_population"] is None

    def test_parse_rows_2020(self):
        """Parsing skips the title, header, and blank rows and coerces flags."""
        records = parse_rows(FAR_2020_ROWS, "2020")
        assert [record["zip_code"] for record in records] == [
            "59003",
            "59010",
            "00063",
            "00049",
            "00177",
            "00001",
        ]
        ca = next(record for record in records if record["zip_code"] == "00049")
        assert (
            ca["far_level_1"],
            ca["far_level_2"],
            ca["far_level_3"],
            ca["far_level_4"],
        ) == (1, 1, 0, 0)
        nh = next(record for record in records if record["zip_code"] == "00177")
        assert (
            nh["far_level_1"],
            nh["far_level_2"],
            nh["far_level_3"],
            nh["far_level_4"],
        ) == (1, 1, 1, 0)

    def test_parse_rows_2000_no_name(self):
        """The 2000 vintage starts at row 1 and carries no area name."""
        records = parse_rows(FAR_2000_ROWS, "2000")
        assert [record["zip_code"] for record in records] == ["59003", "01001"]
        assert all("po_name" not in record for record in records)
        assert records[0]["far_level_1"] == 1
        assert isinstance(records[0]["far_level_1"], int)

    def test_parse_rows_skips_blank_and_empty_rows(self):
        """Blank-ZIP rows and empty rows emit no record."""
        rows = [
            ["2020 title"],
            FAR_2020_HEADER,
            ["", "MT", "Blank", 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0],
            [],
            [
                "59003",
                "MT",
                "Ashland",
                1,
                1,
                1,
                1,
                257,
                35.9,
                7.2,
                257,
                257,
                257,
                257,
                100,
                100,
                100,
                100,
            ],
        ]
        records = parse_rows(rows, "2020")
        assert [record["zip_code"] for record in records] == ["59003"]

    def test_afetch_far_zip_xlsx(self, monkeypatch):
        """The xlsx vintage fetches through the cache and parses the sheet."""
        calls = []

        async def fake_afetch_ers_file(media, product=None, ttl=None):
            calls.append((media, product))
            return _build_workbook("FAR2020 ZIP Code Data", FAR_2020_ROWS)

        monkeypatch.setattr(
            "openbb_government_us.usda.utils.ers_client.afetch_ers_file",
            fake_afetch_ers_file,
        )
        records = asyncio.run(ers.afetch_far_zip("2020"))
        assert calls == [(media_path("2020"), PRODUCT_PAGE)]
        assert {record["state"] for record in records} == {"MT", "CA", "NH", "AK"}
        assert any(record["po_name"] == "Ashland" for record in records)

    def test_afetch_far_zip_xls(self, monkeypatch):
        """The legacy .xls vintage reads via xlrd and parses the sheet."""

        async def fake_afetch_ers_file(media, product=None, ttl=None):
            return b"legacy-xls-bytes"

        monkeypatch.setattr(
            "openbb_government_us.usda.utils.ers_client.afetch_ers_file",
            fake_afetch_ers_file,
        )
        monkeypatch.setattr(
            "xlrd.open_workbook",
            lambda file_contents=None: _FakeXlsBook(FAR_2000_ROWS),
        )
        records = asyncio.run(ers.afetch_far_zip("2000"))
        assert [record["zip_code"] for record in records] == ["59003", "01001"]
        assert all("po_name" not in record for record in records)
        assert records[0]["far_level_1"] == 1


class TestFrontierAndRemoteAreaCodes:
    """Tests for the FrontierAndRemoteAreaCodes model."""

    def _rows_2020(self):
        """Parse the 2020 fixture into canonical records."""
        return parse_rows(FAR_2020_ROWS, "2020")

    def _rows_2000(self):
        """Parse the 2000 fixture into canonical records."""
        return parse_rows(FAR_2000_ROWS, "2000")

    def test_transform_query_defaults(self):
        """transform_query applies the vintage and state defaults."""
        query = FarFetcher.transform_query({})
        assert isinstance(query, FarQuery)
        assert query.year == "2020"
        assert query.state == "MT"

    def test_blank_values_fall_back_to_defaults(self):
        """Blank vintage and state normalize to their defaults."""
        query = FarQuery(year="", state="")
        assert query.year == "2020"
        assert query.state == "MT"

    def test_invalid_year_raises(self):
        """An unknown vintage raises OpenBBError."""
        with pytest.raises(OpenBBError, match="Invalid vintage: 1999"):
            FarQuery(year="1999")

    def test_invalid_state_raises(self):
        """An unknown state raises OpenBBError."""
        with pytest.raises(OpenBBError, match="Invalid state: ZZ"):
            FarQuery(state="ZZ")

    def test_state_uppercases(self):
        """State input is upper-cased and trimmed."""
        assert FarQuery(state="mt").state == "MT"
        assert FarQuery(state=" ca ").state == "CA"

    def test_valid_2000_vintage_state(self):
        """The 2000 vintage accepts a contiguous-State selection."""
        query = FarQuery(year="2000", state="MA")
        assert query.year == "2000"
        assert query.state == "MA"

    def test_aextract_data_returns_records(self, monkeypatch):
        """aextract_data returns the selected vintage's parsed records."""

        async def fake_afetch_far_zip(year):
            return parse_rows(FAR_2020_ROWS, year)

        monkeypatch.setattr(ers, "afetch_far_zip", fake_afetch_far_zip)
        query = FarFetcher.transform_query({})
        records = asyncio.run(FarFetcher.aextract_data(query, None))
        assert {record["state"] for record in records} == {"MT", "CA", "NH", "AK"}

    def test_transform_data_scopes_to_state_and_sorts(self):
        """The default view keeps one state and sorts by ZIP code ascending."""
        query = FarFetcher.transform_query({"year": "2020", "state": "MT"})
        data = FarFetcher.transform_data(query, self._rows_2020())
        assert {row.state for row in data} == {"MT"}
        assert [row.zip_code for row in data] == ["00063", "59003", "59010"]

    def test_transform_data_empty_state_returns_empty(self):
        """A vintage lacking the requested state returns no rows."""
        query = FarQuery(year="2000", state="AK")
        data = FarFetcher.transform_data(query, self._rows_2000())
        assert data == []

    def test_lookup_is_one_row_per_zip_with_no_vintage_column(self):
        """Every row is a ZIP lookup carrying the eighteen fields, no year column."""
        query = FarFetcher.transform_query({"year": "2020", "state": "MT"})
        data = FarFetcher.transform_data(query, self._rows_2020())
        assert len(data) == 3
        served = set(data[0].model_dump(by_alias=True))
        assert served == set(CANONICAL_COLUMNS)
        assert "year" not in served

    def test_nested_flags_are_distinct(self):
        """The four FAR flags carry distinct nested-classification signal."""
        ca = FarFetcher.transform_data(
            FarFetcher.transform_query({"state": "CA"}), self._rows_2020()
        )[0].model_dump(by_alias=True)
        assert (
            ca["far_level_1"],
            ca["far_level_2"],
            ca["far_level_3"],
            ca["far_level_4"],
        ) == (1, 1, 0, 0)
        nh = FarFetcher.transform_data(
            FarFetcher.transform_query({"state": "NH"}), self._rows_2020()
        )[0].model_dump(by_alias=True)
        assert (
            nh["far_level_1"],
            nh["far_level_2"],
            nh["far_level_3"],
            nh["far_level_4"],
        ) == (1, 1, 1, 0)

    def test_2000_vintage_po_name_is_null_but_served(self):
        """The 2000 vintage serves po_name as None while keeping the column."""
        query = FarQuery(year="2000", state="MT")
        data = FarFetcher.transform_data(query, self._rows_2000())
        dumped = data[0].model_dump(by_alias=True)
        assert dumped["po_name"] is None
        assert "po_name" in dumped
        assert dumped["far_level_1"] == 1

    def test_columns_defs_bind_to_served_keys(self):
        """Every declared column definition binds to a served record key."""
        declared = set()
        for name, field in FarData.model_fields.items():
            alias = field.serialization_alias or name
            extra = field.json_schema_extra
            config = extra.get("x-widget_config", {}) if isinstance(extra, dict) else {}
            if config.get("exclude"):
                continue
            declared.add(to_snake(alias))
        assert declared == set(CANONICAL_COLUMNS)
        query = FarFetcher.transform_query({"year": "2020", "state": "MT"})
        data = FarFetcher.transform_data(query, self._rows_2020())
        served = set()
        for row in data:
            served.update(row.model_dump(by_alias=True))
        assert declared == served

    def test_no_dead_constant_column(self):
        """Every served key carries a declared column definition."""
        declared = set(CANONICAL_COLUMNS)
        query = FarFetcher.transform_query({"year": "2020", "state": "MT"})
        data = FarFetcher.transform_data(query, self._rows_2020())
        for row in data:
            for key in row.model_dump(by_alias=True):
                assert to_snake(key) in declared

    def test_param_scoping_options(self):
        """Choice params are single-select with real labels and dependent states."""
        extra = FarQuery.__json_schema_extra__
        year = extra["year"]["x-widget_config"]
        assert year["label"] == "Vintage"
        assert year["multiSelect"] is False and year["multiple"] is False
        assert year["value"] == "2020"
        assert [opt["value"] for opt in year["options"]] == ["2020", "2010", "2000"]
        state = extra["state"]["x-widget_config"]
        assert state["label"] == "State"
        assert state["multiSelect"] is False and state["multiple"] is False
        assert state["type"] == "endpoint"
        assert state["value"] == "MT"
        assert state["optionsEndpoint"].endswith("/usda/far_zip_states")
        assert state["optionsParams"] == {"year": "$year"}

    def test_widget_config_and_column_headers(self):
        """The whole-widget config and per-field headers are populated."""
        widget = FarData.model_config["json_schema_extra"]["x-widget_config"]
        assert widget["$.name"] == "USDA ERS Frontier and Remote Area Codes (ZIP)"
        assert widget["$.category"] == "Economy"
        assert widget["$.subCategory"] == "Agriculture"
        assert widget["$.source"] == ["USDA", "ERS"]
        fields = FarData.model_fields
        for name in ("zip_code", "state", "po_name"):
            assert fields[name].json_schema_extra["x-widget_config"]["pinned"] == "left"
        for name in ("zip_code", "state", "po_name", "far_level_1", "far_level_4"):
            config = fields[name].json_schema_extra["x-widget_config"]
            assert config["cellDataType"] == "text"
        for name in (
            "grid_population",
            "land_area_sq_mi",
            "far_level_1_population_pct",
        ):
            config = fields[name].json_schema_extra["x-widget_config"]
            assert config["cellDataType"] == "number"

    def test_null_token_mixin_coerces_placeholder(self):
        """The Data model coerces placeholder tokens to None but keeps columns."""
        row = FarData.model_validate(
            {"zip_code": "59003", "state": "MT", "far_level_1": "--"}
        )
        dumped = row.model_dump(by_alias=True)
        assert dumped["zip_code"] == "59003"
        assert dumped["far_level_1"] is None
        assert "far_level_1" in dumped
