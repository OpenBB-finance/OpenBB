"""Unit tests for ``openbb_sec.utils.helpers``."""

import asyncio
from unittest.mock import patch

import pytest
from openbb_core.app.model.abstract.error import OpenBBError

from openbb_sec.utils import helpers


def test_sec_callback_text_fallback():
    """sec_callback returns plain text when Content-Type is neither json/html."""

    class _Resp:
        headers = {"Content-Type": "application/octet-stream"}

        async def json(self):
            return {"unused": True}

        async def text(self, encoding=None):
            return f"plain:{encoding}"

    out = asyncio.run(helpers.sec_callback(_Resp(), None))
    assert out == "plain:None"


def test_sec_callback_json_and_html():
    """sec_callback dispatches on the json and html content types."""

    class _Json:
        headers = {"Content-Type": "application/json; charset=utf-8"}

        async def json(self):
            return {"ok": 1}

        async def text(self, encoding=None):
            return "x"

    class _Html:
        headers = {"Content-Type": "text/html"}

        async def json(self):
            return {}

        async def text(self, encoding=None):
            return f"html:{encoding}"

    assert asyncio.run(helpers.sec_callback(_Json(), None)) == {"ok": 1}
    assert asyncio.run(helpers.sec_callback(_Html(), None)) == "html:latin-1"


def test_get_all_companies_invalid_response():
    """An empty/invalid response raises OpenBBError."""

    async def _fake(url, **kwargs):
        return None

    with patch.object(helpers, "cached_request", _fake):
        with pytest.raises(OpenBBError, match="Empty or invalid"):
            asyncio.run(helpers.get_all_companies())


def test_get_all_companies_unexpected_columns():
    """A response whose row width != 3 raises a format error."""

    async def _fake(url, **kwargs):
        return {"0": {"cik_str": 320193, "ticker": "AAPL"}}

    with patch.object(helpers, "cached_request", _fake):
        with pytest.raises(OpenBBError, match="Unexpected SEC response format"):
            asyncio.run(helpers.get_all_companies())


def test_get_all_companies_ok():
    """A well-formed response yields a 3-column string DataFrame."""

    async def _fake(url, **kwargs):
        return {
            "0": {"cik_str": 320193, "ticker": "AAPL", "title": "Apple Inc."},
            "1": {"cik_str": 789019, "ticker": "MSFT", "title": "Microsoft"},
        }

    with patch.object(helpers, "cached_request", _fake):
        df = asyncio.run(helpers.get_all_companies())
    assert list(df.columns) == ["cik", "symbol", "name"]
    assert df.loc["0", "symbol"] == "AAPL"
    assert df.loc["0", "cik"] == "320193"


def _ciks_frame():
    """Patch get_all_ciks to a small institutions frame."""

    async def _fake(use_cache=True):
        from pandas import DataFrame

        return DataFrame(
            {
                "Institution": ["VANGUARD GROUP INC", "BLACKROCK INC", "ACME LLC"],
                "CIK Number": ["0000102909", "0001364742", "0000999999"],
            }
        )

    return _fake


def test_search_institutions_case_insensitive():
    """search_institutions filters by case-insensitive substring."""
    with patch.object(helpers, "get_all_ciks", _ciks_frame()):
        out = asyncio.run(helpers.search_institutions("blackrock"))
    assert len(out) == 1
    assert out.iloc[0]["CIK Number"] == "0001364742"


def _companies_frame():
    from pandas import DataFrame

    return DataFrame(
        {
            "cik": ["320193", "789019"],
            "symbol": ["AAPL", "MSFT"],
            "name": ["Apple Inc.", "Microsoft"],
        }
    )


def _mf_frame():
    from pandas import DataFrame

    return DataFrame(
        {
            "cik": ["36405"],
            "seriesId": ["S000002277"],
            "classId": ["C000005942"],
            "symbol": ["VFINX"],
        }
    )


def test_symbol_map_company_hit():
    """A ticker present in the company list zero-pads to a 10-digit CIK."""

    async def _companies(use_cache=True):
        return _companies_frame()

    with patch.object(helpers, "get_all_companies", _companies):
        cik = asyncio.run(helpers.symbol_map("aapl"))
    assert cik == "0000320193"


def test_symbol_map_fund_fallback():
    """A ticker absent from companies falls back to the MF/ETF map."""

    async def _companies(use_cache=True):
        return _companies_frame()

    async def _mf(use_cache=True):
        return _mf_frame()

    with (
        patch.object(helpers, "get_all_companies", _companies),
        patch.object(helpers, "get_mf_and_etf_map", _mf),
    ):
        cik = asyncio.run(helpers.symbol_map("VFINX"))
    assert cik == "0000036405"


def test_symbol_map_not_found_returns_empty():
    """A ticker in neither list returns an empty string."""

    async def _companies(use_cache=True):
        return _companies_frame()

    async def _mf(use_cache=True):
        return _mf_frame()

    with (
        patch.object(helpers, "get_all_companies", _companies),
        patch.object(helpers, "get_mf_and_etf_map", _mf),
    ):
        assert asyncio.run(helpers.symbol_map("NOPE")) == ""


def test_cik_map_hit_and_miss():
    """cik_map resolves an integer CIK to a ticker, else returns an error string."""

    async def _companies(use_cache=True):
        return _companies_frame()

    with patch.object(helpers, "get_all_companies", _companies):
        assert asyncio.run(helpers.cik_map(320193)) == "AAPL"
        msg = asyncio.run(helpers.cik_map("0000000001"))
    assert "does not have a unique ticker" in msg


def test_get_schema_filelist():
    """get_schema_filelist parses the 'Name' column of an HTML table."""
    html = (
        "<table><tr><th>Name</th></tr>"
        "<tr><td>Parent Directory</td></tr>"
        "<tr><td>elts/</td></tr>"
        "<tr><td>us-gaap-2024.xsd</td></tr></table>"
    )
    with patch.object(helpers, "cached_text", return_value=html):
        out = helpers.get_schema_filelist(query="elts")
    assert out[0] == "https://xbrl.fasb.org/us-gaap/elts/"
    assert "us-gaap-2024.xsd" in out


def test_get_schema_filelist_explicit_url_no_query():
    """With an explicit url and no query the first cell becomes that url."""
    html = "<table><tr><th>Name</th></tr><tr><td>Parent Directory</td></tr><tr><td>a.xsd</td></tr></table>"
    with patch.object(helpers, "cached_text", return_value=html):
        out = helpers.get_schema_filelist(url="https://example.com/dir")
    assert out[0] == "https://example.com/dir"
    assert out[1] == "a.xsd"


def _ftd_zip_bytes(rows: str) -> bytes:
    """Build an in-memory pipe-delimited zip the way the SEC serves FTD data."""
    import io
    import zipfile

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("ftd.txt", rows)
    return buf.getvalue()


def test_download_zip_file_zip_branch_and_settlement():
    """The ZipFile fallback branch renames SETTLEMENT DATE columns."""
    rows = (
        "SETTLEMENT DATE|CUSIP|SYMBOL|QUANTITY (FAILS)|DESCRIPTION|PRICE\n"
        "20230103|000000000|AAPL|100|APPLE INC|130.5\n"
        "20230103|000000001|MSFT|200|MICROSOFT|UNAVAILABLE\n"
        "summary line one\n"
        "summary line two\n"
    )
    zip_bytes = _ftd_zip_bytes(rows)

    async def _fake(url, **kwargs):
        return zip_bytes

    real_read_csv = __import__("pandas").read_csv
    calls = {"n": 0}

    def _read_csv(*args, **kwargs):
        calls["n"] += 1
        if calls["n"] == 1 and kwargs.get("compression") == "zip":
            raise ValueError("forced fallback")
        return real_read_csv(*args, **kwargs)

    with (
        patch.object(helpers, "cached_request", _fake),
        patch("pandas.read_csv", _read_csv),
    ):
        out = asyncio.run(helpers.download_zip_file("http://x/ftd.zip", symbol="AAPL"))

    assert isinstance(out, list)
    assert len(out) == 1
    rec = out[0]
    assert rec["symbol"] == "AAPL"
    assert "cusip" in rec
    assert str(rec["date"]) == "2023-01-03"
    assert rec["price"] == 130.5


def test_download_zip_file_direct_read_branch():
    """A single-member zip is parsed directly by read_csv."""
    rows = (
        "SETTLEMENT DATE|CUSIP|SYMBOL|QUANTITY (FAILS)|DESCRIPTION|PRICE\n"
        "20230103|000000000|AAPL|100|APPLE INC|130.5\n"
        "20230104|000000001|MSFT|150|MICROSOFT|UNAVAILABLE\n"
        "summary one\n"
        "summary two\n"
    )
    zip_bytes = _ftd_zip_bytes(rows)

    async def _fake(url, **kwargs):
        return zip_bytes

    with patch.object(helpers, "cached_request", _fake):
        out = asyncio.run(helpers.download_zip_file("http://x/ftd.zip", symbol="AAPL"))

    assert len(out) == 1
    rec = out[0]
    assert rec["symbol"] == "AAPL"
    assert "cusip" in rec
    assert str(rec["date"]) == "2023-01-03"
    assert rec["price"] == 130.5


def test_get_series_id_requires_input():
    """get_series_id raises when neither symbol nor cik is supplied."""
    with pytest.raises(OpenBBError, match="Either symbol or cik"):
        asyncio.run(helpers.get_series_id())


def test_get_nport_candidates_empty_frame_falls_back_to_symbol_map():
    """An empty series-id frame falls back to symbol_map and raises not-found."""
    from pandas import DataFrame

    async def _series(symbol, use_cache=True):
        return DataFrame({"seriesId": []})

    async def _symbol_map(symbol, use_cache=True):
        return ""

    with (
        patch.object(helpers, "get_series_id", _series),
        patch.object(helpers, "symbol_map", _symbol_map),
    ):
        with pytest.raises(OpenBBError, match="Fund not found"):
            asyncio.run(helpers.get_nport_candidates("BADFUND"))


def test_get_nport_candidates_empty_series_raises():
    """A blank series id raises the fund-not-found error before any request."""

    async def _series(symbol, use_cache=True):
        return None

    async def _symbol_map(symbol, use_cache=True):
        return ""

    with (
        patch.object(helpers, "get_series_id", _series),
        patch.object(helpers, "symbol_map", _symbol_map),
    ):
        with pytest.raises(OpenBBError, match="Fund not found"):
            asyncio.run(helpers.get_nport_candidates("BADFUND"))


def test_get_all_ciks():
    """get_all_ciks parses the colon-delimited CIK lookup file."""

    class _Resp:
        async def text(self, encoding=None):
            return "APPLE INC:0000320193:\nMICROSOFT CORP:0000789019:\n"

    async def _fake(url, response_callback=None, **kwargs):
        return await response_callback(_Resp(), None)

    with patch.object(helpers, "cached_request", _fake):
        df = asyncio.run(helpers.get_all_ciks())
    assert list(df.columns) == ["Institution", "CIK Number"]
    assert (df["Institution"] == "APPLE INC").any()


def test_get_mf_and_etf_map():
    """get_mf_and_etf_map builds a frame from the fields/data payload."""

    async def _fake(url, **kwargs):
        return {
            "fields": ["cik", "seriesId", "classId", "symbol"],
            "data": [["36405", "S000002277", "C000005942", "VFINX"]],
        }

    with patch.object(helpers, "cached_request", _fake):
        df = asyncio.run(helpers.get_mf_and_etf_map())
    assert list(df.columns) == ["cik", "seriesId", "classId", "symbol"]
    assert df.iloc[0]["symbol"] == "VFINX"


def test_get_ftd_urls_found():
    """get_ftd_urls extracts download URLs from the SEC data.json catalog."""

    async def _fake(url, **kwargs):
        return {
            "dataset": [
                {"title": "Other"},
                {
                    "title": "Fails-to-Deliver Data",
                    "distribution": [
                        {"downloadURL": "https://x/cnsfails202301a.zip"},
                        {"noUrl": True},
                    ],
                },
            ]
        }

    with patch.object(helpers, "amake_request", _fake):
        out = asyncio.run(helpers.get_ftd_urls())
    assert list(out.values()) == ["https://x/cnsfails202301a.zip"]


def test_get_ftd_urls_not_found():
    """A catalog without the FTD entry yields an empty mapping."""

    async def _fake(url, **kwargs):
        return {"dataset": [{"title": "Other"}]}

    with patch.object(helpers, "amake_request", _fake):
        assert asyncio.run(helpers.get_ftd_urls()) == {}


def test_get_series_id_symbol_match():
    """get_series_id returns the row matching an exact symbol."""

    async def _mf(use_cache=True):
        return _mf_frame()

    with patch.object(helpers, "get_mf_and_etf_map", _mf):
        out = asyncio.run(helpers.get_series_id(symbol="VFINX"))
    assert out.iloc[0]["seriesId"] == "S000002277"


def test_get_series_id_cik_match():
    """get_series_id resolves by CIK when no symbol is given."""

    async def _mf(use_cache=True):
        return _mf_frame()

    with patch.object(helpers, "get_mf_and_etf_map", _mf):
        out = asyncio.run(helpers.get_series_id(cik="36405"))
    assert out.iloc[0]["symbol"] == "VFINX"


def test_download_zip_file_invokes_callback():
    """download_zip_file reads the response body through its callback."""
    zip_bytes = _ftd_zip_bytes("SYMBOL|PRICE\nAAPL|1\nx\ny\n")

    class _Resp:
        async def read(self):
            return zip_bytes

    async def _fake(url, response_callback=None, **kwargs):
        return await response_callback(_Resp(), None)

    with patch.object(helpers, "cached_request", _fake):
        out = asyncio.run(helpers.download_zip_file("http://x/ftd.zip"))
    assert isinstance(out, list)


@pytest.mark.parametrize(
    "value, expected",
    [
        (5.7e12, "$5.7T AUM"),
        (4e9, "$4.0B AUM"),
        (3e6, "$3.0M AUM"),
        (1000, "$1,000 AUM"),
        (0, ""),
        (None, ""),
    ],
)
def test_format_aum(value, expected):
    """_format_aum renders compact T/B/M/raw strings."""
    assert helpers._format_aum(value) == expected


def test_sec_range_read(monkeypatch):
    """_sec_range_read returns the body, with and without a Range header."""

    class _R:
        def read(self):
            return b"BYTES"

    import urllib.request as _u

    monkeypatch.setattr(_u, "urlopen", lambda req, timeout=120: _R())
    assert helpers._sec_range_read("http://x", "UA") == b"BYTES"
    assert helpers._sec_range_read("http://x", "UA", "bytes=0-3") == b"BYTES"


def _zip_blob(name, content):
    """Build a single-member deflated zip."""
    import io
    import zipfile

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(name, content)
    return buf.getvalue()


def _range_server(blob):
    """Return a fake _sec_range_read that serves byte ranges of ``blob``."""

    def _read(url, ua, byte_range=None):
        if byte_range is None:
            return blob
        spec = byte_range.split("=")[1]
        if spec.startswith("-"):
            return blob[-int(spec[1:]) :]
        start, end = spec.split("-")
        return blob[int(start) : int(end) + 1]

    return _read


def test_zip_member_text_found(monkeypatch):
    """_zip_member_text extracts and decompresses a named member."""
    blob = _zip_blob("T.tsv", "a\tb\nx\ty\n")
    monkeypatch.setattr(helpers, "_sec_range_read", _range_server(blob))
    assert helpers._zip_member_text("http://x.zip", "T.tsv", "UA") == "a\tb\nx\ty\n"


def test_zip_member_text_missing_member(monkeypatch):
    """A member not in the archive returns None."""
    blob = _zip_blob("T.tsv", "x")
    monkeypatch.setattr(helpers, "_sec_range_read", _range_server(blob))
    assert helpers._zip_member_text("http://x.zip", "NOPE.tsv", "UA") is None


def test_zip_member_text_no_eocd(monkeypatch):
    """Bytes without an end-of-central-directory record return None."""
    monkeypatch.setattr(
        helpers, "_sec_range_read", lambda u, ua, byte_range=None: b"not-a-zip"
    )
    assert helpers._zip_member_text("http://x.zip", "T.tsv", "UA") is None


def test_series_names_from_dataset_ok(monkeypatch):
    """A dataset member yields a series_id -> name map, skipping N/A rows."""
    monkeypatch.setattr(
        helpers, "_sec_range_read", lambda u, ua: b'href="/x/2026q1_nport.zip"'
    )
    monkeypatch.setattr(
        helpers,
        "_zip_member_text",
        lambda url, member, ua: "SERIES_ID\tSERIES_NAME\nS1\tFund One\nN/A\tNope\n",
    )
    out = helpers._series_names_from_dataset(
        "http://l", "nport", "M.tsv", "SERIES_ID", "SERIES_NAME", "UA"
    )
    assert out == {"S1": "Fund One"}


def test_series_names_from_dataset_no_zips(monkeypatch):
    """No matching zip link yields an empty map."""
    monkeypatch.setattr(helpers, "_sec_range_read", lambda u, ua: b"<html></html>")
    assert (
        helpers._series_names_from_dataset("http://l", "nport", "M.tsv", "A", "B", "UA")
        == {}
    )


def test_series_names_from_dataset_member_missing(monkeypatch):
    """A missing member yields an empty map."""
    monkeypatch.setattr(
        helpers, "_sec_range_read", lambda u, ua: b'href="/x/2026q1_nport.zip"'
    )
    monkeypatch.setattr(helpers, "_zip_member_text", lambda url, member, ua: None)
    assert (
        helpers._series_names_from_dataset("http://l", "nport", "M.tsv", "A", "B", "UA")
        == {}
    )


def test_series_names_from_dataset_missing_columns(monkeypatch):
    """Headers lacking the id or name column yield an empty map."""
    monkeypatch.setattr(
        helpers, "_sec_range_read", lambda u, ua: b'href="/x/2026q1_nport.zip"'
    )
    monkeypatch.setattr(
        helpers, "_zip_member_text", lambda url, member, ua: "SERIES_ID\tZ\nS1\tx\n"
    )
    assert (
        helpers._series_names_from_dataset(
            "http://l", "nport", "M.tsv", "SERIES_ID", "SERIES_NAME", "UA"
        )
        == {}
    )


def test_fetch_series_name_map_merges_sources(monkeypatch):
    """N-MFP and N-PORT maps merge into one."""

    def _fake(listing_url, pattern, member, sid, name, ua):
        return {"S_MMF": "MMF"} if pattern == "nmfp" else {"S_ETF": "ETF"}

    monkeypatch.setattr(helpers, "_series_names_from_dataset", _fake)
    assert helpers._fetch_series_name_map() == {"S_MMF": "MMF", "S_ETF": "ETF"}


def test_fetch_series_name_map_suppresses_errors(monkeypatch):
    """An error in one source is suppressed; the other still contributes."""

    def _fake(listing_url, pattern, *args):
        if pattern == "nmfp":
            raise RuntimeError("boom")
        return {"S_ETF": "ETF"}

    monkeypatch.setattr(helpers, "_series_names_from_dataset", _fake)
    assert helpers._fetch_series_name_map() == {"S_ETF": "ETF"}


def test_get_series_name_map_cache_miss_then_hit(monkeypatch):
    """The series map is fetched once then served from cache."""
    store: dict = {}

    async def _aget(key):
        return store.get(key)

    async def _aset(key, value, expire=None):
        store[key] = value

    monkeypatch.setattr("openbb_sec.utils.cache.aget_cached", _aget)
    monkeypatch.setattr("openbb_sec.utils.cache.aset_cached", _aset)
    monkeypatch.setattr(helpers, "_fetch_series_name_map", lambda: {"S": "F"})
    assert asyncio.run(helpers.get_series_name_map()) == {"S": "F"}
    monkeypatch.setattr(helpers, "_fetch_series_name_map", lambda: {"OTHER": "X"})
    assert asyncio.run(helpers.get_series_name_map()) == {"S": "F"}


def test_get_series_name_map_no_cache(monkeypatch):
    """use_cache=False always rebuilds the map."""
    monkeypatch.setattr(helpers, "_fetch_series_name_map", lambda: {"S": "F"})
    assert asyncio.run(helpers.get_series_name_map(use_cache=False)) == {"S": "F"}


def _nport_funds_frame():
    from pandas import DataFrame

    return DataFrame(
        {
            "cik": ["1", "2", "3", "4", "4"],
            "seriesId": ["S1", "S2", "S3", "S4", "S4"],
            "classId": ["C1", "C2", "C3", "C4", "C4"],
            "symbol": ["AAA", "BBB", "CCC", "", "DDD"],
        }
    )


def test_get_nport_fund_choices_filters_and_labels(monkeypatch):
    """Only funds with a series name are kept, labelled 'TICKER - Name'."""

    async def _mf(use_cache=True):
        return _nport_funds_frame()

    async def _names(use_cache=True):
        return {"S1": "Fund One", "S2": "Fund Two", "S4": "Fund Four"}

    monkeypatch.setattr(helpers, "get_mf_and_etf_map", _mf)
    monkeypatch.setattr(helpers, "get_series_name_map", _names)
    out = asyncio.run(helpers.get_nport_fund_choices(use_cache=False))
    values = [c["value"] for c in out]
    assert "AAA" in values and "CCC" not in values
    aaa = next(c for c in out if c["value"] == "AAA")
    assert aaa["label"] == "AAA - Fund One"


def test_get_nport_fund_choices_no_map_keeps_all(monkeypatch):
    """With no series map the funds are kept and labelled by ticker only."""

    async def _mf(use_cache=True):
        from pandas import DataFrame

        return DataFrame(
            {"cik": ["1"], "seriesId": ["S1"], "classId": ["C1"], "symbol": ["AAA"]}
        )

    async def _names(use_cache=True):
        return {}

    monkeypatch.setattr(helpers, "get_mf_and_etf_map", _mf)
    monkeypatch.setattr(helpers, "get_series_name_map", _names)
    out = asyncio.run(helpers.get_nport_fund_choices(use_cache=False))
    assert out[0]["label"] == "AAA"


def test_get_nport_fund_choices_cache_hit(monkeypatch):
    """A cached choices list is returned without rebuilding."""

    async def _aget(key):
        return [{"label": "cached", "value": "X"}]

    monkeypatch.setattr("openbb_sec.utils.cache.aget_cached", _aget)
    assert asyncio.run(helpers.get_nport_fund_choices()) == [
        {"label": "cached", "value": "X"}
    ]


def test_fetch_13f_filers(monkeypatch):
    """13F filers join submission/coverpage/summary keeping the largest value."""
    members = {
        "SUBMISSION.tsv": (
            "ACCESSION_NUMBER\tCIK\nA1\t0000001067983\nA2\t0000001067983\nA3\t0000000999\n"
        ),
        "COVERPAGE.tsv": (
            "ACCESSION_NUMBER\tFILINGMANAGER_NAME\n"
            "A1\tBerkshire Hathaway Inc\nA2\tBerkshire Hathaway Inc\nA3\t  \n"
        ),
        "SUMMARYPAGE.tsv": (
            "ACCESSION_NUMBER\tTABLEVALUETOTAL\nA1\t100\nA2\t5000\nA3\tnan\n"
        ),
    }
    monkeypatch.setattr(
        helpers,
        "_sec_range_read",
        lambda u, ua: b'href="/x/01mar2026-31may2026_form13f.zip"',
    )
    monkeypatch.setattr(
        helpers, "_zip_member_text", lambda url, member, ua: members[member]
    )
    out = helpers._fetch_13f_filers()
    assert out["1067983"]["name"] == "Berkshire Hathaway Inc"
    assert out["1067983"]["aum"] == 5000.0
    assert "999" not in out


def test_fetch_13f_filers_no_zips(monkeypatch):
    """No 13F zip link yields an empty map."""
    monkeypatch.setattr(helpers, "_sec_range_read", lambda u, ua: b"<html></html>")
    assert helpers._fetch_13f_filers() == {}


def test_get_13f_filer_choices_sorted_with_tickers(monkeypatch):
    """Choices are AUM-sorted; company filers get a ticker tag; no-AUM dropped."""

    def _filers():
        return {
            "1067983": {"name": "Berkshire", "aum": 5e12},
            "999": {"name": "Small LLC", "aum": 1e6},
            "777": {"name": "No AUM Notice", "aum": None},
            "555": {"name": "Zero AUM", "aum": 0.0},
        }

    async def _companies(use_cache=True):
        from pandas import DataFrame

        return DataFrame(
            {"cik": ["1067983"], "symbol": ["BRK-B"], "name": ["Berkshire"]}
        )

    monkeypatch.setattr(helpers, "_fetch_13f_filers", _filers)
    monkeypatch.setattr(helpers, "get_all_companies", _companies)
    out = asyncio.run(helpers.get_13f_filer_choices(use_cache=False))
    assert [c["value"] for c in out] == ["1067983", "999"]
    assert out[0]["label"] == "Berkshire (BRK-B)"
    assert out[1]["label"] == "Small LLC"


def test_get_13f_filer_choices_company_lookup_error(monkeypatch):
    """A failed company lookup degrades to name-only labels."""
    monkeypatch.setattr(
        helpers, "_fetch_13f_filers", lambda: {"1": {"name": "X", "aum": 1.0}}
    )

    async def _boom(use_cache=True):
        raise RuntimeError("down")

    monkeypatch.setattr(helpers, "get_all_companies", _boom)
    out = asyncio.run(helpers.get_13f_filer_choices(use_cache=False))
    assert out[0]["label"] == "X"


def test_get_13f_filer_choices_cache_hit(monkeypatch):
    """A cached filer list is returned without rebuilding."""

    async def _aget(key):
        return [{"label": "cached", "value": "1"}]

    monkeypatch.setattr("openbb_sec.utils.cache.aget_cached", _aget)
    assert asyncio.run(helpers.get_13f_filer_choices()) == [
        {"label": "cached", "value": "1"}
    ]


def test_get_nport_candidates_paginates(monkeypatch):
    """Candidates are paged from EFTS and sorted newest-first."""
    from pandas import DataFrame

    async def _series(symbol, use_cache=True):
        return DataFrame({"seriesId": ["S000001"]})

    pages = [
        {
            "hits": {
                "hits": [
                    {
                        "_id": "acc1:f.htm",
                        "_source": {
                            "display_names": ["Fund"],
                            "ciks": ["1"],
                            "file_date": "2026-05-31",
                            "period_ending": "2026-05-31",
                            "form": "N-MFP3",
                        },
                    }
                ],
                "total": {"value": 2},
            }
        },
        {
            "hits": {
                "hits": [
                    {
                        "_id": "acc2:g.htm",
                        "_source": {
                            "display_names": ["Fund"],
                            "ciks": ["1"],
                            "file_date": "2026-04-30",
                            "form": "N-MFP3",
                        },
                    }
                ],
                "total": {"value": 2},
            }
        },
    ]
    state = {"n": 0}

    async def _cached(url, **kwargs):
        page = pages[state["n"]]
        state["n"] += 1
        return page

    monkeypatch.setattr(helpers, "get_series_id", _series)
    monkeypatch.setattr(helpers, "cached_request", _cached)
    out = asyncio.run(helpers.get_nport_candidates("VMFXX"))
    assert len(out) == 2
    assert out[0]["file_date"] == "2026-05-31"
    assert out[1]["period_ending"] == "2026-04-30"


def test_get_nport_candidates_non_dict_breaks(monkeypatch):
    """A non-dict EFTS response ends pagination with no candidates."""
    from pandas import DataFrame

    async def _series(symbol, use_cache=True):
        return DataFrame({"seriesId": ["S000001"]})

    async def _cached(url, **kwargs):
        return "throttled"

    monkeypatch.setattr(helpers, "get_series_id", _series)
    monkeypatch.setattr(helpers, "cached_request", _cached)
    assert asyncio.run(helpers.get_nport_candidates("VMFXX")) == []


def test_series_names_from_dataset_missing_id_column(monkeypatch):
    """A header lacking the id column yields an empty map."""
    monkeypatch.setattr(
        helpers, "_sec_range_read", lambda u, ua: b'href="/x/2026q1_nport.zip"'
    )
    monkeypatch.setattr(
        helpers, "_zip_member_text", lambda url, member, ua: "X\tY\n1\t2\n"
    )
    assert (
        helpers._series_names_from_dataset(
            "http://l", "nport", "M.tsv", "SERIES_ID", "SERIES_NAME", "UA"
        )
        == {}
    )


def test_get_nport_fund_choices_writes_cache(monkeypatch):
    """A cache miss builds and stores the fund choices."""
    store: dict = {}

    async def _aget(key):
        return store.get(key)

    async def _aset(key, value, expire=None):
        store[key] = value

    async def _mf(use_cache=True):
        from pandas import DataFrame

        return DataFrame(
            {"cik": ["1"], "seriesId": ["S1"], "classId": ["C1"], "symbol": ["AAA"]}
        )

    async def _names(use_cache=True):
        return {"S1": "Fund One"}

    monkeypatch.setattr("openbb_sec.utils.cache.aget_cached", _aget)
    monkeypatch.setattr("openbb_sec.utils.cache.aset_cached", _aset)
    monkeypatch.setattr(helpers, "get_mf_and_etf_map", _mf)
    monkeypatch.setattr(helpers, "get_series_name_map", _names)
    out = asyncio.run(helpers.get_nport_fund_choices())
    assert out[0]["value"] == "AAA"
    assert "sec_nport_fund_choices" in store


def _thirteen_f_members(summary):
    """Build 13F dataset members with a given SUMMARYPAGE body."""
    return {
        "SUBMISSION.tsv": "ACCESSION_NUMBER\tCIK\nA1\t0000000001\n",
        "COVERPAGE.tsv": "ACCESSION_NUMBER\tFILINGMANAGER_NAME\nA1\tManager LLC\n",
        "SUMMARYPAGE.tsv": summary,
    }


def test_fetch_13f_filers_empty_summary(monkeypatch):
    """An empty summary member leaves the filer's AUM unset."""
    members = _thirteen_f_members("")
    monkeypatch.setattr(
        helpers,
        "_sec_range_read",
        lambda u, ua: b'href="/x/01mar2026-31may2026_form13f.zip"',
    )
    monkeypatch.setattr(
        helpers, "_zip_member_text", lambda url, member, ua: members[member]
    )
    assert helpers._fetch_13f_filers()["1"]["aum"] is None


def test_fetch_13f_filers_summary_missing_column(monkeypatch):
    """A summary member without the value column leaves AUM unset."""
    members = _thirteen_f_members("ACCESSION_NUMBER\tWRONG\nA1\t5\n")
    monkeypatch.setattr(
        helpers,
        "_sec_range_read",
        lambda u, ua: b'href="/x/01mar2026-31may2026_form13f.zip"',
    )
    monkeypatch.setattr(
        helpers, "_zip_member_text", lambda url, member, ua: members[member]
    )
    assert helpers._fetch_13f_filers()["1"]["aum"] is None


def test_fetch_13f_filers_bad_aum(monkeypatch):
    """A non-numeric portfolio value is coerced to None."""
    members = _thirteen_f_members("ACCESSION_NUMBER\tTABLEVALUETOTAL\nA1\tabc\n")
    monkeypatch.setattr(
        helpers,
        "_sec_range_read",
        lambda u, ua: b'href="/x/01mar2026-31may2026_form13f.zip"',
    )
    monkeypatch.setattr(
        helpers, "_zip_member_text", lambda url, member, ua: members[member]
    )
    assert helpers._fetch_13f_filers()["1"]["aum"] is None


def test_get_13f_filer_choices_writes_cache(monkeypatch):
    """A cache miss builds and stores the filer list."""
    store: dict = {}

    async def _aget(key):
        return store.get(key)

    async def _aset(key, value, expire=None):
        store[key] = value

    async def _companies(use_cache=True):
        from pandas import DataFrame

        return DataFrame({"cik": [], "symbol": [], "name": []})

    monkeypatch.setattr("openbb_sec.utils.cache.aget_cached", _aget)
    monkeypatch.setattr("openbb_sec.utils.cache.aset_cached", _aset)
    monkeypatch.setattr(
        helpers, "_fetch_13f_filers", lambda: {"1": {"name": "X", "aum": 1.0}}
    )
    monkeypatch.setattr(helpers, "get_all_companies", _companies)
    out = asyncio.run(helpers.get_13f_filer_choices())
    assert out[0]["label"] == "X"
    assert "sec_13f_filer_choices" in store
