"""Unit tests for ``openbb_sec.utils.asset_data``."""

from io import BytesIO
from types import SimpleNamespace

from openbb_sec.utils import asset_data


def _cond(**kwargs):
    """Build an AgGrid filter condition stand-in."""
    return SimpleNamespace(**kwargs)


def _sort(col_id, direction):
    """Build an AgGrid sort-model entry stand-in."""
    return SimpleNamespace(colId=col_id, sort=direction)


def _request(*, filter_model=None, sort_model=None, start=0, end=0):
    """Build an SSRM query request stand-in."""
    return SimpleNamespace(
        filterModel=filter_model or {},
        sortModel=sort_model or [],
        startRow=start,
        endRow=end,
    )


class TestFetchStream:
    """The streaming, identity-encoded SEC fetch."""

    def test_fetch_stream_sets_decode_and_headers(self, monkeypatch):
        captured: dict = {}
        raw = SimpleNamespace(decode_content=False)
        resp = SimpleNamespace(raw=raw)

        def _fake_request(url, headers=None, stream=None, timeout=None):
            captured.update(url=url, headers=headers, stream=stream, timeout=timeout)
            return resp

        monkeypatch.setattr(
            "openbb_sec.utils.ratelimit.sec_make_request", _fake_request
        )
        out = asset_data._fetch_stream("https://www.sec.gov/x.xml")
        assert out is resp
        assert raw.decode_content is True
        assert captured["stream"] is True
        assert captured["headers"]["Accept-Encoding"] == "identity"


class TestParseRecordsStream:
    """Streaming XML record parsing into columns and aligned rows."""

    def test_parses_heterogeneous_records(self):
        xml = (
            b"<assetData>"
            b"<asset><assetNumber>1</assetNumber><balance>100</balance></asset>"
            b"<asset><assetNumber>2</assetNumber><!--c--><status>ok</status></asset>"
            b"</assetData>"
        )
        columns, rows = asset_data.parse_records_stream(BytesIO(xml))
        # Each asset's fields align into shared columns; comment children skip.
        assert columns[:3] == ["assetNumber", "balance", "status"]
        assert rows[:2] == [("1", "100", "", ""), ("2", "", "ok", "")]
        # Artifact of the streaming clear/prune: once its asset children are
        # emptied, the root collapses into one spurious, all-blank record under
        # an ``asset`` column.
        assert columns[3] == "asset"
        assert rows[2] == ("", "", "", "")

    def test_tail_text_definitions_disable_tabular_parsing(self):
        xml = (
            b"<assetData><assets>"
            b"<assetTypeNumber>HCA</assetTypeNumber>"
            b"<!--  comments  -->"
            b"<newEx103tag1>assetTypeNumber</newEx103tag1>"
            b"<![CDATA[ Asset Number Type - HCA indicates Hyundai Capital America. ]]>"
            b"<newEx103tag2>originatorName</newEx103tag2>"
            b"<![CDATA[ Originator - HCA indicates Hyundai Capital America. ]]>"
            b"</assets></assetData>"
        )
        columns, rows = asset_data.parse_records_stream(BytesIO(xml))
        assert columns == []
        assert rows == []

    def test_non_asset_data_root_yields_nothing(self):
        columns, rows = asset_data.parse_records_stream(
            BytesIO(b"<xbrl><x>1</x></xbrl>")
        )
        assert columns == []
        assert rows == []


class TestLoadAssetData:
    """Cached load of asset-data rows."""

    def test_cache_hit_skips_fetch(self, monkeypatch):
        called: dict = {}
        monkeypatch.setattr(
            "openbb_sec.utils.cache._make_key", lambda url, suffix="": "k"
        )
        monkeypatch.setattr(
            "openbb_sec.utils.cache._cache_get", lambda key: (["a"], [("1",)])
        )
        monkeypatch.setattr(
            asset_data, "_fetch_stream", lambda url: called.setdefault("fetched", True)
        )
        columns, rows = asset_data.load_asset_data("https://www.sec.gov/x.xml")
        assert columns == ["a"]
        assert rows == [("1",)]
        assert "fetched" not in called

    def test_cache_miss_fetches_parses_and_stores(self, monkeypatch):
        stored: dict = {}
        closed: dict = {}
        monkeypatch.setattr(
            "openbb_sec.utils.cache._make_key", lambda url, suffix="": "k"
        )
        monkeypatch.setattr("openbb_sec.utils.cache._cache_get", lambda key: None)
        monkeypatch.setattr(
            "openbb_sec.utils.cache._cache_set",
            lambda key, value, expire: stored.update(value=value, expire=expire),
        )
        resp = SimpleNamespace(
            raw=BytesIO(b"<assetData><asset><n>1</n></asset></assetData>"),
            close=lambda: closed.setdefault("closed", True),
        )
        monkeypatch.setattr(asset_data, "_fetch_stream", lambda url: resp)
        columns, rows = asset_data.load_asset_data("https://www.sec.gov/x.xml")
        # ``n`` is the real field; the trailing ``asset`` column/blank row is the
        # collapsed-root artifact (see TestParseRecordsStream). The whole parsed
        # tuple is what gets cached.
        assert columns == ["n", "asset"]
        assert rows == [("1", ""), ("", "")]
        assert closed["closed"] is True
        assert stored["value"] == (["n", "asset"], [("1", ""), ("", "")])
        assert stored["expire"] is None


class TestAsNumber:
    """Best-effort float conversion."""

    def test_as_number(self):
        assert asset_data._as_number("1.5") == 1.5
        assert asset_data._as_number("x") is None
        assert asset_data._as_number(None) is None


class TestBuildPredicate:
    """AgGrid filter-condition to row-predicate compilation."""

    def test_set_filter(self):
        pred = asset_data._build_predicate(
            0, _cond(filterType="set", values=["a", "b"])
        )
        assert pred(("a",)) is True
        assert pred(("c",)) is False

    def test_values_present_forces_set_semantics(self):
        pred = asset_data._build_predicate(0, _cond(filterType="text", values=["x"]))
        assert pred(("x",)) is True
        assert pred(("y",)) is False

    def test_number_operators(self):
        cases = [
            ("equals", "10", True),
            ("equals", "5", False),
            ("notequal", "5", True),
            ("greaterthan", "11", True),
            ("greaterthanorequal", "10", True),
            ("lessthan", "9", True),
            ("lessthanorequal", "10", True),
        ]
        for op, value, expected in cases:
            pred = asset_data._build_predicate(
                0, _cond(filterType="number", type=op, filter="10")
            )
            assert pred((value,)) is expected, op

    def test_number_inrange(self):
        pred = asset_data._build_predicate(
            0, _cond(filterType="number", type="inrange", filter="10", filterTo="20")
        )
        assert pred(("15",)) is True
        assert pred(("25",)) is False
        assert pred(("x",)) is False

    def test_number_unknown_operator_is_none(self):
        assert (
            asset_data._build_predicate(
                0, _cond(filterType="number", type="bogus", filter="1")
            )
            is None
        )

    def test_text_operators(self):
        cases = [
            ("contains", "xABz", True),
            ("notcontains", "xyz", True),
            ("equals", "ab", True),
            ("notequal", "cd", True),
            ("startswith", "ABc", True),
            ("endswith", "xAB", True),
        ]
        for op, value, expected in cases:
            pred = asset_data._build_predicate(
                0, _cond(filterType="text", type=op, filter="ab")
            )
            assert pred((value,)) is expected, op

    def test_text_blank_operators(self):
        blank = asset_data._build_predicate(0, _cond(filterType="text", type="blank"))
        assert blank(("",)) is True
        assert blank(("x",)) is False
        notblank = asset_data._build_predicate(
            0, _cond(filterType="text", type="notblank")
        )
        assert notblank(("x",)) is True

    def test_text_default_contains_when_unknown_op(self):
        pred = asset_data._build_predicate(0, _cond(type="", filter="foo"))
        assert pred(("FooBar",)) is True

    def test_text_default_empty_needle_is_none(self):
        assert asset_data._build_predicate(0, _cond(type="", filter=None)) is None


class TestApplyFilters:
    """Row filtering by an AgGrid filterModel."""

    columns = {"name": 0, "amt": 1}
    rows = [("apple", "10"), ("banana", "20")]

    def test_skips_unknown_columns_and_applies_predicate(self):
        filter_model = {
            "missing": _cond(filterType="text", type="contains", filter="x"),
            "name": _cond(filterType="text", type="contains", filter="app"),
        }
        out = asset_data._apply_filters(self.columns, self.rows, filter_model)
        assert out == [("apple", "10")]

    def test_none_predicate_leaves_rows_unfiltered(self):
        filter_model = {"name": _cond(type="", filter=None)}
        out = asset_data._apply_filters(self.columns, self.rows, filter_model)
        assert out is self.rows

    def test_empty_filter_model_returns_rows(self):
        assert asset_data._apply_filters(self.columns, self.rows, {}) is self.rows


class TestApplySort:
    """Numeric-aware, multi-key, blanks-last sorting."""

    columns = {"name": 0, "amt": 1}

    def test_numeric_ascending_keeps_blanks_last(self):
        rows = [("c", "30"), ("a", "10"), ("b", ""), ("d", "20")]
        out = asset_data._apply_sort(self.columns, rows, [_sort("amt", "asc")])
        assert [r[1] for r in out] == ["10", "20", "30", ""]

    def test_numeric_descending_keeps_blanks_last(self):
        rows = [("c", "30"), ("a", "10"), ("b", ""), ("d", "20")]
        out = asset_data._apply_sort(self.columns, rows, [_sort("amt", "desc")])
        assert [r[1] for r in out] == ["30", "20", "10", ""]

    def test_text_sort(self):
        rows = [("banana", "1"), ("apple", "2"), ("", "3")]
        out = asset_data._apply_sort(self.columns, rows, [_sort("name", "asc")])
        assert [r[0] for r in out] == ["apple", "banana", ""]

    def test_multi_key_sort(self):
        rows = [("x", "b", "2"), ("x", "a", "1"), ("y", "a", "3")]
        out = asset_data._apply_sort(
            {"c0": 0, "c1": 1}, rows, [_sort("c0", "asc"), _sort("c1", "asc")]
        )
        assert out == [("x", "a", "1"), ("x", "b", "2"), ("y", "a", "3")]

    def test_unknown_column_is_skipped(self):
        rows = [("a", "1"), ("b", "2")]
        out = asset_data._apply_sort(self.columns, rows, [_sort("ghost", "asc")])
        assert out == rows

    def test_empty_sort_model_returns_rows(self):
        rows = [("a", "1")]
        assert asset_data._apply_sort(self.columns, rows, []) is rows


class TestQuery:
    """Combined filter / sort / page for an SSRM request."""

    columns = ["name", "amt"]
    rows = [("c", "30"), ("a", "10"), ("b", "20")]

    def test_sorts_and_pages(self):
        request = _request(sort_model=[_sort("amt", "asc")], start=0, end=2)
        page, total = asset_data.query(self.columns, self.rows, request)
        assert total == 3
        assert page == [{"name": "a", "amt": "10"}, {"name": "b", "amt": "20"}]

    def test_non_positive_end_row_returns_all(self):
        request = _request(start=0, end=0)
        page, total = asset_data.query(self.columns, self.rows, request)
        assert total == 3
        assert len(page) == 3

    def test_negative_start_row_clamped(self):
        request = _request(start=-5, end=1)
        page, _ = asset_data.query(self.columns, self.rows, request)
        assert len(page) == 1

    def test_filter_reduces_total(self):
        request = _request(
            filter_model={"name": _cond(filterType="text", type="equals", filter="a")}
        )
        page, total = asset_data.query(self.columns, self.rows, request)
        assert total == 1
        assert page == [{"name": "a", "amt": "10"}]
