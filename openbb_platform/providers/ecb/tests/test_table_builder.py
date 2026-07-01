import asyncio

from openbb_ecb.utils import query_builder
from openbb_ecb.utils.table_builder import (
    _dim_labels,
    _first,
    _or_key,
    _resolve_labels,
    _scale,
    build_presentation_table,
)


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


def test_first():
    assert _first({"UNIT__label": "Euro", "UNIT": "EUR"}, "UNIT") == "Euro"
    assert _first({"UNIT": "EUR"}, "UNIT") == "EUR"
    assert _first({}, "UNIT") == ""


def test_dim_labels():
    record = {
        "_dim_ids": ["FREQ", "REF_AREA", "X"],
        "FREQ__label": "Monthly",
        "REF_AREA__label": "Euro area",
        "X__label": "",
    }
    assert _dim_labels(record) == [("FREQ", "Monthly"), ("REF_AREA", "Euro area")]
    assert _dim_labels({}) == []


def test_resolve_labels_json_distinguishing():
    row = {
        "dims": [("FREQ", "Monthly"), ("REF_AREA", "Austria"), ("ITEM", "HICP")],
        "title": "",
        "compl": "",
    }
    title, description = _resolve_labels(row, {"FREQ", "REF_AREA", "ITEM"})
    assert title == "Austria · HICP"
    assert description == "Monthly, Austria, HICP"


def test_resolve_labels_json_context_only():
    only_freq = {"dims": [("FREQ", "Monthly")], "title": "", "compl": ""}
    assert _resolve_labels(only_freq, {"FREQ"}) == ("Monthly", "Monthly")
    nothing_varies = {"dims": [("FREQ", "Monthly")], "title": "", "compl": ""}
    assert _resolve_labels(nothing_varies, set()) == ("Monthly", "Monthly")


def test_resolve_labels_csv():
    both = {"dims": [], "title": "Short", "compl": "Full definition"}
    assert _resolve_labels(both, set()) == ("Short", "Full definition")
    compl_only = {"dims": [], "title": "", "compl": "Only compl"}
    assert _resolve_labels(compl_only, set()) == ("Only compl", "Only compl")


class _FakeMeta:
    def __init__(self, rows):
        self._rows = rows

    def get_table_rows(self, table_id):
        return self._rows


_DB = {
    "AAA": [
        {
            "series_key": "a.1",
            "_dim_ids": ["D0", "D1"],
            "D0__label": "Monthly",
            "D1__label": "Item one",
            "UNIT__label": "Euro",
            "UNIT_MULT": "6",
            "OBS_VALUE": 9.0,
            "date": "2024-01-01",
        },
        {
            "series_key": "a.1",
            "_dim_ids": ["D0", "D1"],
            "D0__label": "Monthly",
            "D1__label": "Item one",
            "OBS_VALUE": 8.0,
            "date": "2023-10-01",
        },
        {
            "series_key": "a.2",
            "_dim_ids": ["D0", "D1"],
            "D0__label": "Monthly",
            "D1__label": "Item two",
            "UNIT_MEASURE__label": "Index",
            "UNIT_MULT": "0",
            "OBS_VALUE": 5.0,
            "date": "2024-01-01",
        },
        {
            "series_key": "a.2",
            "_dim_ids": ["D0", "D1"],
            "OBS_VALUE": None,
            "date": None,
        },
        {
            "series_key": "a.9",
            "_dim_ids": ["D0", "D1"],
            "D0__label": "Monthly",
            "D1__label": "Not wanted",
            "OBS_VALUE": 1.0,
            "date": "2024-01-01",
        },
    ],
    "BBB": [
        {
            "series_key": "b.1",
            "TITLE": "CSV title",
            "TITLE_COMPL": "CSV full definition",
            "UNIT": "PCPA",
            "UNIT_MULT": "0",
            "OBS_VALUE": 3.0,
            "date": "2024-01-01",
        }
    ],
    "DDD": [
        {
            "series_key": "d.1",
            "OBS_VALUE": 7.0,
            "date": "2024-01-01",
        }
    ],
}


def _make_fetch(calls):
    async def _fetch(flow_ref, key, **kwargs):
        calls.append((flow_ref, key, kwargs.get("last_n")))
        return list(_DB.get(flow_ref, []))

    return _fetch


def test_build_presentation_table(monkeypatch):
    calls: list = []
    monkeypatch.setattr(query_builder, "fetch_sdmx_data", _make_fetch(calls))
    rows = [
        {"flow": "AAA", "key": "a.1"},
        {"flow": "AAA", "key": "a.1"},
        {"flow": "AAA", "key": "a.2"},
        {"flow": "AAA", "key": "a.3"},
        {"flow": "BBB", "key": "b.1"},
        {"flow": "DDD", "key": "d.1"},
    ]
    result = asyncio.run(
        build_presentation_table(_FakeMeta(rows), "T", use_cache=False, limit=4)
    )
    by_title = {r["title"]: r for r in result}

    assert all(last_n == 4 for _, _, last_n in calls)
    assert by_title["Item one"]["2024-01-01"] == 9_000_000.0
    assert by_title["Item one"]["2023-10-01"] == 8.0
    assert by_title["Item one"]["unit"] == "Euro"
    assert by_title["Item one"]["description"] == "Monthly, Item one"
    assert by_title["Item two"]["unit"] == "Index"
    assert by_title["Item two"]["2024-01-01"] == 5.0
    assert by_title["CSV title"]["description"] == "CSV full definition"
    assert by_title["CSV title"]["unit"] == "PCPA"
    assert by_title["d.1"]["2024-01-01"] == 7.0
    assert "Not wanted" not in by_title
    assert len(result) == 4


def test_build_presentation_table_batches(monkeypatch):
    calls: list = []
    monkeypatch.setattr(query_builder, "fetch_sdmx_data", _make_fetch(calls))
    rows = [{"flow": "AAA", "key": f"a.{i}"} for i in range(30)]
    asyncio.run(build_presentation_table(_FakeMeta(rows), "T", use_cache=False))
    assert len(calls) == 2


def test_build_presentation_table_empty():
    assert asyncio.run(build_presentation_table(_FakeMeta([]), "T")) == []
