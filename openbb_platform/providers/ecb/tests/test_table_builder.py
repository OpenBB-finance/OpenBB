import asyncio

from openbb_core.app.model.abstract.error import OpenBBError

from openbb_ecb.utils import query_builder
from openbb_ecb.utils.table_builder import (
    _area_index,
    _batch_keys,
    _blank,
    _jdf_units,
    _or_key,
    _row_unit,
    _scale,
    _segments,
    _short_unit,
    build_presentation_table,
    publication_frequencies,
)

_NB = chr(0xA0)


def test_scale():
    assert _scale(9.0, "6") == 9_000_000.0
    assert _scale(5.0, "0") == 5.0
    assert _scale(5.0, None) == 5.0
    assert _scale(5.0, "") == 5.0
    assert _scale(6.0, "bad") == 6.0
    assert _scale(None, "6") is None


def test_or_key():
    assert _or_key(["M.A.1", "M.B.1", "Q.A.1"]) == "M+Q.A+B.1"
    assert _or_key(["X.Y"]) == "X.Y"
    assert _or_key(["Q.W1.X"], 1) == "Q..X"


def test_blank():
    assert _blank("A.B.C", 1) == "A..C"
    assert _blank("A.B", 5) == "A.B"


def test_batch_keys():
    homogeneous = [f"M.U2.A{i}.EUR" for i in range(10)]
    assert _batch_keys(homogeneous) == [homogeneous]
    many = [f"M.U2.A{i}.EUR" for i in range(30)]
    assert [len(b) for b in _batch_keys(many)] == [25, 5]
    diverse = [f"F{i}.R{i}.I{i}.U{i}" for i in range(4)]
    assert [len(b) for b in _batch_keys(diverse, cap=8)] == [1, 1, 1, 1]
    assert _batch_keys([]) == []


def test_segments():
    assert _segments("Monetary aggregate M3, Stocks") == [
        "Monetary aggregate M3",
        "Stocks",
    ]
    assert _segments("HICP - Total - Annual rate") == ["HICP", "Total", "Annual rate"]
    assert _segments("") == []


def test_short_unit():
    assert _short_unit("EUR", "Euro") == "Euro"
    assert _short_unit("XG", "Domestic currency; ratio to gross domestic product") == (
        "% of GDP"
    )
    assert _short_unit("XDC", "Domestic currency (incl. conversion)") == (
        "Domestic currency"
    )
    assert _short_unit("LONG", "A very long unit label that exceeds the width cap") == (
        "LONG"
    )
    assert _short_unit("", "") == ""


class _FakeMeta:
    def __init__(self, table, dsd=None, dsd_error=False, codelists=None):
        self._table = table
        self._dsd = dsd
        self._dsd_error = dsd_error
        self._codelists = codelists or {}

    def get_table(self, table_id):
        return self._table

    def get_codelist(self, codelist_id):
        return self._codelists.get(codelist_id, {"EUR": "Euro"})

    def get_dsd_for_dataflow(self, flow):
        if self._dsd_error:
            raise OpenBBError("no dsd")
        return self._dsd or {"dimensions": []}


def test_area_index():
    dsd = {"dimensions": [{"id": "FREQ"}, {"id": "COUNTERPART_AREA"}]}
    assert _area_index(_FakeMeta({}, dsd=dsd), "X") == 1
    assert _area_index(_FakeMeta({}, dsd={"dimensions": [{"id": "FREQ"}]}), "X") is None
    assert _area_index(_FakeMeta({}, dsd_error=True), "X") is None


_DB = {
    "AAA": [
        {
            "series_key": "a.1",
            "TITLE": "Monetary aggregate M1, Stocks",
            "TITLE_COMPL": "M1 stocks full definition",
            "UNIT": "EUR",
            "UNIT_MULT": "6",
            "OBS_VALUE": 9.0,
            "date": "2024-03-01",
        },
        {
            "series_key": "a.1",
            "UNIT": "EUR",
            "UNIT_MULT": "6",
            "OBS_VALUE": 8.0,
            "date": "2024-02-01",
        },
        {
            "series_key": "a.1",
            "OBS_VALUE": None,
            "date": None,
        },
        {
            "series_key": "a.2",
            "TITLE": "Monetary aggregate M1, Transactions",
            "UNIT": "EUR",
            "UNIT_MULT": "6",
            "OBS_VALUE": 2.0,
            "date": "2024-03-01",
        },
        {
            "series_key": "a.3",
            "TITLE": "Monetary aggregate M2, Stocks",
            "UNIT": "EUR",
            "OBS_VALUE": 5.0,
            "date": "2024-03-01",
        },
        {
            "series_key": "a.5",
            "TITLE": "Reserve assets",
            "UNIT": "EUR",
            "UNIT_MULT": "0",
            "OBS_VALUE": 3.0,
            "date": "2024-03-01",
        },
        {
            "series_key": "a.5",
            "OBS_VALUE": 2.5,
            "date": "2024-01-01",
        },
        {
            "series_key": "a.6",
            "TITLE": "",
            "UNIT": "EUR",
            "OBS_VALUE": 7.0,
            "date": "2024-03-01",
        },
        {
            "series_key": "a.9",
            "TITLE": "Not wanted",
            "OBS_VALUE": 1.0,
            "date": "2024-03-01",
        },
        {
            "OBS_VALUE": 1.0,
            "date": "2024-03-01",
        },
    ],
    "GEO": [
        {
            "series_key": "Q.US.X",
            "TITLE": "Direct investment with the United States, assets, stocks",
            "UNIT": "EUR",
            "UNIT_MULT": "0",
            "OBS_VALUE": 11.0,
            "date": "2024-03-01",
        },
        {
            "series_key": "Q.GB.X",
            "TITLE": "Direct investment with the United Kingdom, assets, stocks",
            "UNIT": "EUR",
            "UNIT_MULT": "0",
            "OBS_VALUE": 12.0,
            "date": "2024-03-01",
        },
        {
            "series_key": "Q.W1.X",
            "TITLE": "Direct investment, assets, stocks",
            "UNIT": "EUR",
            "UNIT_MULT": "0",
            "OBS_VALUE": 13.0,
            "date": "2024-03-01",
        },
        {
            "series_key": "Q.US.Y",
            "TITLE": "Other, series",
            "OBS_VALUE": 99.0,
            "date": "2024-03-01",
        },
    ],
    "GEO2": [
        {
            "series_key": "Q.US.X",
            "TITLE": "Total, stocks",
            "UNIT": "EUR",
            "OBS_VALUE": 21.0,
            "date": "2024-03-01",
        },
        {
            "series_key": "Q.GB.X",
            "TITLE": "Total with Britain, stocks",
            "UNIT": "EUR",
            "OBS_VALUE": 22.0,
            "date": "2024-03-01",
        },
    ],
    "FRQ": [
        {
            "series_key": "M.R1",
            "TITLE": "Euribor 3-month, Historical close, Monthly",
            "UNIT": "PCPA",
            "OBS_VALUE": 2.34,
            "date": "2024-03-01",
        },
        {
            "series_key": "M.R2",
            "TITLE": "Euribor 6-month, Historical close, Monthly",
            "UNIT": "PCPA",
            "OBS_VALUE": 2.6,
            "date": "2024-03-01",
        },
        {
            "series_key": "A.R1",
            "TITLE": "Euribor 3-month, Historical close, Annual",
            "UNIT": "PCPA",
            "OBS_VALUE": 2.2,
            "date": "2024-01-01",
        },
        {
            "series_key": "A.R2",
            "TITLE": "Euribor 6-month, Historical close, Annual",
            "UNIT": "PCPA",
            "OBS_VALUE": 2.21,
            "date": "2024-01-01",
        },
    ],
    "LMX": [
        {
            "series_key": "Q.AT.U",
            "TITLE": "",
            "FREQ": "Q",
            "REF_AREA": "AT",
            "MEASURE": "U",
            "UNIT": "PS",
            "OBS_VALUE": 10.0,
            "date": "2024-03-01",
        },
        {
            "series_key": "Q.BE.U",
            "TITLE": "",
            "FREQ": "Q",
            "REF_AREA": "BE",
            "MEASURE": "U",
            "UNIT": "PS",
            "OBS_VALUE": 20.0,
            "date": "2024-03-01",
        },
        {
            "series_key": "Q.AT.R",
            "TITLE": "",
            "FREQ": "Q",
            "REF_AREA": "AT",
            "MEASURE": "R",
            "UNIT": "PC",
            "OBS_VALUE": 3.1,
            "date": "2024-03-01",
        },
        {
            "series_key": "Q.BE.R",
            "TITLE": "",
            "FREQ": "Q",
            "REF_AREA": "BE",
            "MEASURE": "R",
            "UNIT": "PC",
            "OBS_VALUE": 4.2,
            "date": "2024-03-01",
        },
    ],
    "MIX": [
        {
            "series_key": "Q.AT.U",
            "TITLE": "Employment, Known",
            "FREQ": "Q",
            "REF_AREA": "AT",
            "MEASURE": "U",
            "UNIT": "PS",
            "OBS_VALUE": 5.0,
            "date": "2024-03-01",
        },
        {
            "series_key": "Q.BE.R",
            "TITLE": "",
            "FREQ": "Q",
            "REF_AREA": "BE",
            "MEASURE": "R",
            "UNIT": "PC",
            "OBS_VALUE": 4.2,
            "date": "2024-03-01",
        },
    ],
    "SC": [
        {
            "series_key": "s.1",
            "TITLE": "Alpha, Shared",
            "UNIT": "EUR",
            "OBS_VALUE": 1.0,
            "date": "2024-03-01",
        },
        {
            "series_key": "s.2",
            "TITLE": "Shared",
            "UNIT": "EUR",
            "OBS_VALUE": 2.0,
            "date": "2024-03-01",
        },
    ],
    "ENT": [
        {
            "series_key": "M.AT.D",
            "TITLE": "Government debt, percent of GDP",
            "FREQ": "M",
            "REF_AREA": "AT",
            "ITEM": "D",
            "UNIT": "XG",
            "OBS_VALUE": 0.4,
            "date": "2024-03-01",
        },
        {
            "series_key": "M.BE.D",
            "TITLE": "Government debt, percent of GDP",
            "FREQ": "M",
            "REF_AREA": "BE",
            "ITEM": "D",
            "UNIT": "XG",
            "OBS_VALUE": 0.5,
            "date": "2024-03-01",
        },
    ],
}


def _make_fetch(calls):
    async def _fetch(flow_ref, key, **kwargs):
        calls.append((flow_ref, key, kwargs.get("last_n")))
        return list(_DB.get(flow_ref, []))

    return _fetch


def _table(rows, title="Monetary aggregates"):
    return {"title": title, "subcategory": "", "rows": rows}


def test_build_presentation_table(monkeypatch):
    calls: list = []
    monkeypatch.setattr(query_builder, "fetch_sdmx_data_csv", _make_fetch(calls))
    rows = [
        {"flow": "AAA", "key": "a.1"},
        {"flow": "AAA", "key": "a.1"},
        {"flow": "AAA", "key": "a.2"},
        {"flow": "AAA", "key": "a.3"},
        {"flow": "AAA", "key": "a.4"},
        {"flow": "AAA", "key": "a.5"},
        {"flow": "AAA", "key": "a.6"},
    ]
    result = asyncio.run(
        build_presentation_table(_FakeMeta(_table(rows)), "T", use_cache=False, limit=2)
    )
    assert all(last_n == 2 for _, _, last_n in calls)

    date_cols = [k for k in result[0] if k not in ("title", "description", "unit")]
    assert date_cols == ["2024-03-01", "2024-02-01"]

    titles = [r["title"] for r in result]
    assert "Monetary aggregate M1" in titles
    assert "Monetary aggregate M2, Stocks" in titles
    assert _NB * 4 + "Stocks" in titles
    assert _NB * 4 + "Transactions" in titles
    assert "Reserve assets" in titles

    by_title = {r["title"]: r for r in result}
    assert by_title["Monetary aggregate M1"]["2024-03-01"] is None
    assert by_title[_NB * 4 + "Stocks"]["2024-03-01"] == 9_000_000.0
    assert by_title["Monetary aggregate M2, Stocks"]["2024-03-01"] == 5.0
    assert by_title[_NB * 4 + "Stocks"]["unit"] == "Euro"
    assert by_title[_NB * 4 + "Transactions"]["description"] == (
        "Monetary aggregate M1, Transactions"
    )
    assert "M1 stocks full definition" in {r["description"] for r in result}
    assert "a.6" in titles
    assert by_title["a.6"]["description"] == "a.6"
    assert "Not wanted" not in titles
    assert by_title["Reserve assets"]["2024-03-01"] == 3.0
    assert by_title["Reserve assets"]["2024-02-01"] == 2.5
    assert by_title["a.6"]["2024-02-01"] is None


def test_build_presentation_table_order(monkeypatch):
    monkeypatch.setattr(query_builder, "fetch_sdmx_data_csv", _make_fetch([]))
    rows = [{"flow": "AAA", "key": "a.3"}, {"flow": "AAA", "key": "a.1"}]
    result = asyncio.run(
        build_presentation_table(_FakeMeta(_table(rows)), "T", use_cache=False, limit=2)
    )
    assert [r["title"] for r in result] == [
        "Monetary aggregate M2",
        "Monetary aggregate M1",
    ]


def test_build_presentation_table_geographical(monkeypatch):
    calls: list = []
    monkeypatch.setattr(query_builder, "fetch_sdmx_data_csv", _make_fetch(calls))
    dsd = {
        "dimensions": [
            {"id": "FREQ"},
            {"id": "COUNTERPART_AREA", "codelist_id": "CL_AREA"},
            {"id": "REF_SECTOR"},
        ]
    }
    codelists = {"CL_AREA": {"US": "United States", "GB": "United Kingdom"}}
    table = _table(
        [{"flow": "GEO", "key": "Q.W1.X"}],
        title="Financial account (Geographical breakdown)",
    )
    result = asyncio.run(
        build_presentation_table(
            _FakeMeta(table, dsd=dsd, codelists=codelists), "G", use_cache=False
        )
    )
    assert calls[0][1] == "Q..X"
    assert [r["title"] for r in result] == [
        "Direct investment",
        _NB * 4 + "assets",
        _NB * 8 + "stocks",
        _NB * 12 + "United Kingdom",
        _NB * 12 + "United States",
    ]
    assert result[2]["2024-03-01"] == 13.0
    assert result[3]["2024-03-01"] == 12.0
    assert result[4]["2024-03-01"] == 11.0


def test_build_presentation_table_geographical_no_aggregate(monkeypatch):
    monkeypatch.setattr(query_builder, "fetch_sdmx_data_csv", _make_fetch([]))
    dsd = {
        "dimensions": [
            {"id": "FREQ"},
            {"id": "COUNTERPART_AREA"},
            {"id": "REF_SECTOR"},
        ]
    }
    table = _table(
        [{"flow": "GEO2", "key": "Q.W1.X"}],
        title="Geographical breakdown",
    )
    result = asyncio.run(
        build_presentation_table(_FakeMeta(table, dsd=dsd), "G2", use_cache=False)
    )
    assert [r["title"] for r in result] == [
        "Total",
        _NB * 4 + "stocks",
        _NB * 8 + "GB",
    ]
    assert result[1]["2024-03-01"] == 21.0
    assert result[2]["2024-03-01"] == 22.0


def test_build_presentation_table_entities(monkeypatch):
    monkeypatch.setattr(query_builder, "fetch_sdmx_data_csv", _make_fetch([]))
    dsd = {
        "dimensions": [
            {"id": "FREQ"},
            {"id": "REF_AREA", "codelist_id": "CL_AREA"},
            {"id": "ITEM"},
            {},
        ]
    }
    codelists = {
        "CL_AREA": {"AT": "Austria", "BE": "Belgium"},
        "CL_UNIT": {"XG": "Domestic currency; ratio to gross domestic product"},
    }
    rows = [{"flow": "ENT", "key": "M.AT.D"}, {"flow": "ENT", "key": "M.BE.D"}]
    result = asyncio.run(
        build_presentation_table(
            _FakeMeta(_table(rows), dsd=dsd, codelists=codelists),
            "E",
            use_cache=False,
        )
    )
    assert [r["title"] for r in result] == [
        "Government debt",
        _NB * 4 + "percent of GDP",
        _NB * 8 + "Austria",
        _NB * 8 + "Belgium",
    ]
    assert result[2]["2024-03-01"] == 0.4
    assert result[3]["2024-03-01"] == 0.5
    assert result[2]["unit"] == "% of GDP"


def test_build_presentation_table_entities_key_fallback(monkeypatch):
    monkeypatch.setattr(query_builder, "fetch_sdmx_data_csv", _make_fetch([]))
    rows = [{"flow": "ENT", "key": "M.AT.D"}, {"flow": "ENT", "key": "M.BE.D"}]
    result = asyncio.run(
        build_presentation_table(
            _FakeMeta(_table(rows), dsd_error=True), "E", use_cache=False
        )
    )
    assert [r["title"].strip() for r in result] == [
        "Government debt",
        "percent of GDP",
        "AT",
        "BE",
    ]


_FRQ_DSD = {"dimensions": [{"id": "FREQ"}, {"id": "ITEM"}]}
_FRQ_ROWS = [
    {"flow": "FRQ", "key": "M.R1"},
    {"flow": "FRQ", "key": "M.R2"},
    {"flow": "FRQ", "key": "A.R1"},
    {"flow": "FRQ", "key": "A.R2"},
]


def test_build_presentation_table_frequency(monkeypatch):
    monkeypatch.setattr(query_builder, "fetch_sdmx_data_csv", _make_fetch([]))
    meta = _FakeMeta(_table(_FRQ_ROWS), dsd=_FRQ_DSD)
    result = asyncio.run(build_presentation_table(meta, "T", use_cache=False))
    assert [r["title"] for r in result] == ["Euribor 3-month", "Euribor 6-month"]
    assert result[0]["2024-03-01"] == 2.34
    assert result[1]["2024-03-01"] == 2.60

    annual = asyncio.run(
        build_presentation_table(meta, "T", use_cache=False, context={"FREQ": "A"})
    )
    assert [r["title"] for r in annual] == ["Euribor 3-month", "Euribor 6-month"]
    assert annual[0]["2024-01-01"] == 2.2
    assert annual[1]["2024-01-01"] == 2.21

    unknown = asyncio.run(
        build_presentation_table(meta, "T", use_cache=False, context={"FREQ": "X"})
    )
    assert unknown[0]["2024-03-01"] == 2.34


def test_publication_frequencies():
    meta = _FakeMeta(_table(_FRQ_ROWS), dsd=_FRQ_DSD)
    assert publication_frequencies(meta, "T") == ["M", "A"]
    assert publication_frequencies(_FakeMeta(_table(_FRQ_ROWS)), "T") == []
    late = {"dimensions": [{"id": "ITEM"}, {"id": "FREQ"}]}
    rows = [{"flow": "FRQ", "key": "R1.M"}]
    assert publication_frequencies(_FakeMeta(_table(rows), dsd=late), "T") == ["M"]


def test_build_presentation_table_entity_hierarchy(monkeypatch):
    monkeypatch.setattr(query_builder, "fetch_sdmx_data_csv", _make_fetch([]))
    dsd = {
        "dimensions": [
            {"id": "FREQ"},
            {"id": "REF_AREA", "codelist_id": "CL_AREA"},
            {"id": "MEASURE", "codelist_id": "CL_MEAS"},
        ]
    }
    codelists = {
        "CL_AREA": {"AT": "Austria", "BE": "Belgium"},
        "CL_MEAS": {"U": "Unemployment", "R": "Unemployment rate"},
    }
    rows = [
        {"flow": "LMX", "key": "Q.AT.U"},
        {"flow": "LMX", "key": "Q.BE.U"},
        {"flow": "LMX", "key": "Q.AT.R"},
        {"flow": "LMX", "key": "Q.BE.R"},
    ]
    result = asyncio.run(
        build_presentation_table(
            _FakeMeta(_table(rows), dsd=dsd, codelists=codelists),
            "L",
            use_cache=False,
        )
    )
    assert [r["title"] for r in result] == [
        "Unemployment",
        _NB * 4 + "Austria",
        _NB * 4 + "Belgium",
        "Unemployment rate",
        _NB * 4 + "Austria",
        _NB * 4 + "Belgium",
    ]
    assert result[1]["2024-03-01"] == 10.0
    assert result[2]["2024-03-01"] == 20.0
    assert result[4]["2024-03-01"] == 3.1
    assert result[5]["2024-03-01"] == 4.2
    assert result[1]["description"] == "Unemployment, Austria"


def test_build_presentation_table_untitled_single(monkeypatch):
    monkeypatch.setattr(query_builder, "fetch_sdmx_data_csv", _make_fetch([]))
    dsd = {
        "dimensions": [
            {"id": "FREQ"},
            {"id": "REF_AREA", "codelist_id": "CL_AREA"},
            {"id": "MEASURE", "codelist_id": "CL_MEAS"},
        ]
    }
    codelists = {
        "CL_AREA": {"AT": "Austria", "BE": "Belgium"},
        "CL_MEAS": {"U": "Employment", "R": "Unemployment rate"},
    }
    rows = [{"flow": "MIX", "key": "Q.AT.U"}, {"flow": "MIX", "key": "Q.BE.R"}]
    result = asyncio.run(
        build_presentation_table(
            _FakeMeta(_table(rows), dsd=dsd, codelists=codelists),
            "M",
            use_cache=False,
        )
    )
    titles = [r["title"] for r in result]
    assert "Employment, Known" in titles
    assert "Unemployment rate, Belgium" in titles
    assert not any("Q.BE.R" in t for t in titles)

    solo = asyncio.run(
        build_presentation_table(
            _FakeMeta(_table([{"flow": "MIX", "key": "Q.BE.R"}]), dsd=dsd),
            "M",
            use_cache=False,
        )
    )
    assert [r["title"] for r in solo] == ["Q.BE.R"]


def test_build_presentation_table_strip_fallback(monkeypatch):
    monkeypatch.setattr(query_builder, "fetch_sdmx_data_csv", _make_fetch([]))
    rows = [{"flow": "SC", "key": "s.1"}, {"flow": "SC", "key": "s.2"}]
    result = asyncio.run(
        build_presentation_table(_FakeMeta(_table(rows)), "T", use_cache=False)
    )
    assert [r["title"] for r in result] == ["Alpha", "Shared"]


def test_build_presentation_table_batches(monkeypatch):
    calls: list = []
    monkeypatch.setattr(query_builder, "fetch_sdmx_data_csv", _make_fetch(calls))
    rows = [{"flow": "AAA", "key": f"a.{i}"} for i in range(30)]
    asyncio.run(build_presentation_table(_FakeMeta(_table(rows)), "T", use_cache=False))
    assert len(calls) == 2


def test_build_presentation_table_empty():
    assert asyncio.run(build_presentation_table(_FakeMeta(_table([])), "T")) == []


class _UnitMeta:
    def __init__(self, dsd, error=False):
        self._dsd = dsd
        self._error = error

    def get_dsd_for_dataflow(self, dataflow_id):
        if self._error:
            raise OpenBBError("no dsd")
        return self._dsd

    def get_codelist(self, codelist_id):
        return {"EUR": "Euro", "G1": "Growth rate, period on period"}


def test_jdf_units():
    assert _jdf_units(_UnitMeta(None, error=True), "J", ["FREQ"]) == {}
    dsd = {
        "dimensions": [
            {"id": "FREQ"},
            {"id": "UNIT_MEASURE", "codelist_id": "CL_UNIT"},
            {"id": "TRANSFORMATION"},
        ]
    }
    units = _jdf_units(_UnitMeta(dsd), "J", ["FREQ", "UNIT_MEASURE", "TRANSFORMATION"])
    assert units["UNIT_MEASURE"][0] == 1
    assert units["TRANSFORMATION"][0] == 2
    assert _jdf_units(_UnitMeta(dsd), "J", ["FREQ"]) == {}


def test_row_unit():
    units = {
        "TRANSFORMATION": (2, {"G1": "Growth rate, period on period"}),
        "UNIT_MEASURE": (1, {"EUR": "Euro"}),
    }
    assert _row_unit(None, units) == ""
    assert _row_unit("M.EUR.G1", units) == "Growth rate, period on period"
    assert _row_unit("M.EUR.N", units) == "Euro"
    assert _row_unit("M.EUR._Z", units) == "Euro"
    assert _row_unit("M.XX.N", {"UNIT": (1, {"XX": "Index"})}) == "Index"
    assert _row_unit("M..N", {"UNIT_MEASURE": (1, {})}) == ""
    assert _row_unit("M", units) == ""


class _FakeJdfMeta:
    def __init__(self, structure, table, dims, unit_dsd=None):
        self._structure = structure
        self._table = table
        self._dims = dims
        self._unit_dsd = unit_dsd

    def get_table(self, table_id):
        return self._table

    def get_table_structure(self, table_id):
        return self._structure

    def get_table_default_context(self, table_id):
        return dict(self._table.get("default_context") or {})

    def get_dataflow_dimensions(self, dataflow_id):
        return self._dims

    def get_codelist(self, codelist_id):
        return {"EUR": "Euro", "G1": "Growth rate, period on period"}

    def get_dsd_for_dataflow(self, dataflow_id):
        if self._unit_dsd is None:
            raise OpenBBError("no dsd")
        return self._unit_dsd


def _make_sdmx(records, calls=None):
    async def _fetch(flow, key, **kwargs):
        if calls is not None:
            calls.append(key)
        return list(records)

    return _fetch


_JDF_STRUCTURE = [
    {
        "label": "New business",
        "code": "1",
        "codelist_id": "JDF_ROW_LABELS",
        "dimension_id": None,
        "children": [
            {
                "label": "Loans",
                "code": "A20",
                "codelist_id": "CL_BS_ITEM",
                "dimension_id": "BS_ITEM",
                "children": [],
            },
            {
                "label": "Deposits",
                "code": "A21",
                "codelist_id": "CL_BS_ITEM",
                "dimension_id": "BS_ITEM",
                "children": [],
            },
        ],
    }
]
_JDF_DIMS = [
    {"id": "FREQ"},
    {"id": "BS_ITEM"},
    {"id": "REF_AREA"},
    {"id": "UNIT_MEASURE"},
    {"id": "TRANSFORMATION"},
]


def test_build_jdf_table(monkeypatch):
    records = [
        {
            "FREQ": "M",
            "BS_ITEM": "A20",
            "REF_AREA": "DE",
            "UNIT_MEASURE": "EUR",
            "TRANSFORMATION": "N",
            "TITLE_COMPL": "Loans to euro area residents reported by MFIs",
            "OBS_VALUE": 5.0,
            "date": "2024-02-01",
        },
        {
            "FREQ": "M",
            "BS_ITEM": "A20",
            "REF_AREA": "DE",
            "UNIT_MEASURE": "EUR",
            "TRANSFORMATION": "N",
            "OBS_VALUE": 6.0,
            "date": "2024-01-01",
        },
        {
            "FREQ": "M",
            "BS_ITEM": "A20",
            "REF_AREA": "DE",
            "UNIT_MEASURE": "EUR",
            "TRANSFORMATION": "N",
            "OBS_VALUE": None,
            "date": "2024-03-01",
        },
        {
            "FREQ": "M",
            "BS_ITEM": "A21",
            "REF_AREA": "DE",
            "UNIT_MEASURE": "EUR",
            "TRANSFORMATION": "G1",
            "TITLE": "Deposit growth",
            "UNIT_MULT": "3",
            "OBS_VALUE": 1.5,
            "date": "2024-02-01",
        },
        {
            "FREQ": "M",
            "BS_ITEM": "ZZZ",
            "REF_AREA": "DE",
            "UNIT_MEASURE": "EUR",
            "TRANSFORMATION": "N",
            "OBS_VALUE": 9.0,
            "date": "2024-02-01",
        },
    ]
    calls: list = []
    monkeypatch.setattr(
        query_builder, "fetch_sdmx_data_csv", _make_sdmx(records, calls)
    )
    table = {
        "source": "jdf",
        "dataflow_id": "J",
        "default_context": {"FREQ": "M", "REF_AREA": "U2"},
        "leaf_keys": [None, "M.A20.U2.EUR.N", "M.A21.U2.EUR.G1"],
    }
    unit_dsd = {
        "dimensions": [
            {"id": "UNIT_MEASURE", "codelist_id": "CL_UNIT"},
            {"id": "TRANSFORMATION", "codelist_id": "CL_TRANS"},
        ]
    }
    meta = _FakeJdfMeta(_JDF_STRUCTURE, table, _JDF_DIMS, unit_dsd)
    rows = asyncio.run(
        build_presentation_table(
            meta, "J", use_cache=False, limit=4, context={"FREQ": "M", "REF_AREA": "DE"}
        )
    )
    assert calls == ["M.A20+A21.DE.EUR.G1+N"]
    by = {r["title"].strip(): r for r in rows}
    assert by["New business"]["2024-02-01"] is None
    assert by["New business"]["unit"] == ""
    assert by["New business"]["description"] == "New business"
    assert by["Loans"]["2024-02-01"] == 5.0
    assert by["Loans"]["2024-01-01"] == 6.0
    assert by["Loans"]["unit"] == "Euro"
    assert by["Loans"]["title"].startswith(_NB * 4)
    assert by["Loans"]["description"] == "Loans to euro area residents reported by MFIs"
    assert by["Deposits"]["2024-02-01"] == 1500.0
    assert by["Deposits"]["2024-01-01"] is None
    assert by["Deposits"]["unit"] == "Growth rate, period on period"
    assert by["Deposits"]["description"] == "Deposit growth"


def test_build_jdf_table_unit_attribute(monkeypatch):
    records = [
        {
            "FREQ": "M",
            "BS_ITEM": "A20",
            "UNIT": "EUR",
            "OBS_VALUE": 7.0,
            "date": "2024-02-01",
        }
    ]
    monkeypatch.setattr(query_builder, "fetch_sdmx_data_csv", _make_sdmx(records))
    structure = [
        {
            "label": "Loans",
            "code": "A20",
            "codelist_id": "CL_BS_ITEM",
            "dimension_id": "BS_ITEM",
            "children": [],
        }
    ]
    table = {
        "source": "jdf",
        "dataflow_id": "J",
        "default_context": {"FREQ": "M"},
        "leaf_keys": ["M.A20"],
    }
    dims = [{"id": "FREQ"}, {"id": "BS_ITEM"}]
    meta = _FakeJdfMeta(structure, table, dims, unit_dsd={"dimensions": []})
    rows = asyncio.run(build_presentation_table(meta, "J", use_cache=False))
    assert rows[0]["unit"] == "Euro"
    assert rows[0]["2024-02-01"] == 7.0


def test_build_jdf_table_unresolved(monkeypatch):
    monkeypatch.setattr(query_builder, "fetch_sdmx_data_csv", _make_sdmx([]))
    table = {"source": "jdf", "dataflow_id": "J", "default_context": {"FREQ": "M"}}
    meta = _FakeJdfMeta(_JDF_STRUCTURE, table, _JDF_DIMS)
    rows = asyncio.run(build_presentation_table(meta, "J", use_cache=False))
    assert len(rows) == 3
    assert all(
        r.get(key) is None
        for r in rows
        for key in r
        if key not in ("title", "description", "unit")
    )
