import asyncio
import io
import json
import zipfile

import pytest
from openbb_core.app.model.abstract.error import OpenBBError

from openbb_cftc.utils import fixings


class _Response:
    def __init__(self, body, status=200):
        self._body = body
        self.status = status

    def raise_for_status(self):
        if self.status >= 400:
            raise OpenBBError(f"status {self.status}")

    async def text(self):
        return self._body if isinstance(self._body, str) else self._body.decode()

    async def read(self):
        return self._body if isinstance(self._body, bytes) else self._body.encode()

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        return False


class _Session:
    def __init__(self, replies, seen):
        self._replies = replies
        self._seen = seen

    def _reply(self, url):
        self._seen.append(url)

        for fragment, body in self._replies:
            if fragment in url:
                return body if isinstance(body, _Response) else _Response(body)

        return _Response("", status=404)

    def get(self, url, **kwargs):
        return self._reply(url)

    def post(self, url, **kwargs):
        self._seen.append(kwargs.get("json") or kwargs.get("data"))

        return self._reply(url)

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        return False


def _patch(monkeypatch, replies):
    import aiohttp

    seen: list = []
    monkeypatch.setattr(
        aiohttp, "ClientSession", lambda *a, **k: _Session(replies, seen)
    )
    monkeypatch.setattr(aiohttp, "TCPConnector", lambda *a, **k: None)

    return seen


TAIBOR_SHEET = (
    "中華民國銀行公會金融業拆款中心,,,,,,,,\n"
    "台北金融業拆款定盤利率,,,,,,,,\n"
    "日期,一星期,二星期,一個月,二個月,三個月,六個月,九個月,一年期\n"
    "27JUL26,1.38078,1.47022,1.60033,1.62644,1.67944,1.71100,1.78133,1.89067\n"
    "24JUL26,1.38078,1.47022,1.60033,1.62600,1.67944,1.71100,1.78133,1.89067\n"
    "======,,,,,,,,\n"
)


def _taibor_zip() -> bytes:
    buffer = io.BytesIO()

    with zipfile.ZipFile(buffer, "w") as bundle:
        bundle.writestr("JUL2026.csv", TAIBOR_SHEET.encode("big5"))
        bundle.writestr("notes.txt", b"ignored")

    return buffer.getvalue()


TAIBOR_INDEX = (
    "<table><tr><td>2026/07/27</td><td>"
    "<a href='/taiborDaily/DownloadAll?id=3235'>x</a></td></tr>"
    "<tr><td>2020/01/01</td><td>"
    "<a href='/taiborDaily/DownloadAll?id=1'>old</a></td></tr>"
    "<tr><td>no date here</td></tr></table>"
)


def test_taibor_rows_parses_dated_lines():
    rows = fixings._taibor_rows(TAIBOR_SHEET, 5, "2026-01-01", "2026-12-31")

    assert rows == {"2026-07-27": 0.0167944, "2026-07-24": 0.0167944}


def test_taibor_rows_skips_rows_outside_the_window():
    assert fixings._taibor_rows(TAIBOR_SHEET, 5, "2027-01-01", "2027-12-31") == {}


def test_taibor_rows_skips_short_and_unparseable_rows():
    text = "27JUL26,1.0\n27JUL26,1,2,3,4,bad\nnotadate,1,2,3,4,5.0\n"

    assert fixings._taibor_rows(text, 5, "2000-01-01", "2030-01-01") == {}


def test_fetch_taibor_merges_archives(monkeypatch):
    seen = _patch(
        monkeypatch,
        [("taiborDaily/index", TAIBOR_INDEX), ("DownloadAll", _taibor_zip())],
    )
    rates = asyncio.run(fixings._fetch_taibor("5", "2026-01-01", "2026-12-31"))

    assert rates["2026-07-27"] == pytest.approx(0.0167944)
    assert any("id=3235" in str(x) for x in seen)
    assert not any("id=1" in str(x) for x in seen)


def test_fetch_taibor_skips_a_bad_archive(monkeypatch):
    _patch(
        monkeypatch,
        [("taiborDaily/index", TAIBOR_INDEX), ("DownloadAll", b"not-a-zip")],
    )

    with pytest.raises(OpenBBError, match="Unexpected fixings response"):
        asyncio.run(fixings._fetch_taibor("5", "2026-01-01", "2026-12-31"))


def test_fetch_taibor_skips_a_failed_download(monkeypatch):
    _patch(
        monkeypatch,
        [
            ("taiborDaily/index", TAIBOR_INDEX),
            ("DownloadAll", _Response("", status=500)),
        ],
    )

    with pytest.raises(OpenBBError):
        asyncio.run(fixings._fetch_taibor("5", "2026-01-01", "2026-12-31"))


CFETS_CSV = (
    "2026-07-27,,,,,,1.44,1.44,1.43\n"
    "2026-07-24,,,,,,1.4,1.41,1.43\n"
    "2020-01-02,,,,,,2.0,2.1,2.2\n"
    "header,row,not,a,date,x,y,z,w\n"
    "2026-07-23,,,,,,1.39,bad,1.45\n"
)


def test_fetch_cfets_reads_the_named_column(monkeypatch):
    _patch(monkeypatch, [("frr-chrt.csv", CFETS_CSV)])
    rates = asyncio.run(fixings._fetch_cfets("7", "2026-01-01", "2026-12-31"))

    assert rates == {
        "2026-07-27": pytest.approx(0.0144),
        "2026-07-24": pytest.approx(0.0141),
    }


def test_fetch_cfets_raises_when_nothing_is_in_range(monkeypatch):
    _patch(monkeypatch, [("frr-chrt.csv", CFETS_CSV)])

    with pytest.raises(OpenBBError, match="Unexpected fixings response"):
        asyncio.run(fixings._fetch_cfets("7", "2030-01-01", "2030-12-31"))


FINWIRE_BODY = json.dumps(
    {
        "data": {
            "indicator": "wibor-3m",
            "points": [
                {"date": "2026-07-24", "value": 3.79},
                {"date": "2026-07-23", "value": 3.82},
                {"date": "2020-01-02", "value": 1.71},
                {"date": "bad", "value": 1.0},
                {"date": "2026-07-22", "value": None},
            ],
        }
    }
)


def test_fetch_finwire_reads_points(monkeypatch):
    seen = _patch(monkeypatch, [("interest-rate", FINWIRE_BODY)])
    rates = asyncio.run(fixings._fetch_finwire("wibor-3m", "2026-07-01", "2026-07-24"))

    assert rates == {
        "2026-07-24": pytest.approx(0.0379),
        "2026-07-23": pytest.approx(0.0382),
    }
    assert any("days=" in str(u) for u in seen)


def test_fetch_finwire_raises_on_an_empty_series(monkeypatch):
    _patch(monkeypatch, [("interest-rate", json.dumps({"data": {"points": []}}))])

    with pytest.raises(OpenBBError, match="Unexpected fixings response"):
        asyncio.run(fixings._fetch_finwire("wibor-3m", "2026-07-01", "2026-07-24"))


GPW_TABLE = (
    "<table><tr><td>Index Date</td><td>1M</td></tr>"
    "<tr><td>2026-07-17</td><td>3.599</td><td>3.59886</td></tr>"
    "<tr><td>2026-07-16</td><td>3.641</td><td>3.59812</td></tr>"
    "<tr><td>2026-07-20</td><td>-</td><td>3.59868</td></tr>"
    "<tr><td>2020-01-02</td><td>1.500</td><td>1.5</td></tr></table>"
)


def test_fetch_gpw_reads_the_column(monkeypatch):
    _patch(monkeypatch, [("delayed_data", GPW_TABLE)])
    rates = asyncio.run(fixings._fetch_gpw("1", "2026-07-01", "2026-07-31"))

    assert rates == {
        "2026-07-17": pytest.approx(0.03599),
        "2026-07-16": pytest.approx(0.03641),
    }


def test_fetch_gpw_retries_then_succeeds(monkeypatch):
    import aiohttp

    monkeypatch.setattr(fixings, "GPW_RETRY_SECONDS", 0.0)
    attempts = {"n": 0}
    real = _Session([("delayed_data", GPW_TABLE)], [])

    class _Flaky:
        def get(self, url, **kwargs):
            attempts["n"] += 1

            if attempts["n"] < 3:
                raise aiohttp.ClientError("reset")

            return real.get(url)

        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            return False

    monkeypatch.setattr(aiohttp, "ClientSession", lambda *a, **k: _Flaky())
    monkeypatch.setattr(aiohttp, "TCPConnector", lambda *a, **k: None)
    rates = asyncio.run(fixings._fetch_gpw("1", "2026-07-01", "2026-07-31"))

    assert attempts["n"] == 3
    assert rates["2026-07-17"] == pytest.approx(0.03599)


def test_fetch_gpw_gives_up_after_the_last_attempt(monkeypatch):
    import aiohttp

    monkeypatch.setattr(fixings, "GPW_RETRY_SECONDS", 0.0)
    monkeypatch.setattr(fixings, "GPW_MAX_ATTEMPTS", 2)

    class _Dead:
        def get(self, url, **kwargs):
            raise aiohttp.ClientError("reset")

        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            return False

    monkeypatch.setattr(aiohttp, "ClientSession", lambda *a, **k: _Dead())
    monkeypatch.setattr(aiohttp, "TCPConnector", lambda *a, **k: None)

    with pytest.raises(aiohttp.ClientError):
        asyncio.run(fixings._fetch_gpw("1", "2026-07-01", "2026-07-31"))


def test_fetch_gpw_raises_when_no_rows_match(monkeypatch):
    _patch(monkeypatch, [("delayed_data", GPW_TABLE)])

    with pytest.raises(OpenBBError, match="Unexpected fixings response"):
        asyncio.run(fixings._fetch_gpw("1", "2030-01-01", "2030-12-31"))


BOK_CONTENT = json.dumps(
    [
        {
            "Selection of Items": "CD (91-day)",
            "20260727": 2.92,
            "20260724": 2.91,
            "20200102": 1.3,
            "Unit": "Percent Per Annum",
            "20260723": "",
        }
    ]
)


def test_fetch_bok_reads_date_keyed_columns(monkeypatch):
    seen = _patch(
        monkeypatch,
        [("httpService", json.dumps({"data": {"jsonCtnt": BOK_CONTENT}}))],
    )
    rates = asyncio.run(
        fixings._fetch_bok("817Y002/010502000", "2026-07-01", "2026-07-27")
    )

    assert rates["2026-07-27"] == pytest.approx(0.0292)
    assert rates["2026-07-24"] == pytest.approx(0.0291)
    assert rates["2020-01-02"] == pytest.approx(0.013)
    body = next(x for x in seen if isinstance(x, dict))
    assert body["data"]["statSrchDsList"][0]["dsItmVal1"] == "010502000"
    assert body["header"]["trxCd"] == fixings.BOK_ECOS_TRX


def test_fetch_bok_raises_without_content(monkeypatch):
    _patch(monkeypatch, [("httpService", json.dumps({"data": {}}))])

    with pytest.raises(OpenBBError, match="ECOS"):
        asyncio.run(fixings._fetch_bok("817Y002/010502000", "2026-07-01", "2026-07-27"))


def test_fetch_bok_raises_when_no_dates_parse(monkeypatch):
    body = json.dumps({"data": {"jsonCtnt": json.dumps([{"Unit": "x"}])}})
    _patch(monkeypatch, [("httpService", body)])

    with pytest.raises(OpenBBError, match="ECOS"):
        asyncio.run(fixings._fetch_bok("817Y002/010502000", "2026-07-01", "2026-07-27"))


SARB_ROWS = json.dumps(
    [
        {"Period": "2026-07-24T00:00:00", "Value": 7.0},
        {"Period": "2026-07-23T00:00:00", "Value": 7.0},
        {"Period": "2020-01-02T00:00:00", "Value": 6.5},
        {"Period": "", "Value": 1.0},
        {"Period": "2026-07-22T00:00:00", "Value": None},
    ]
)


def test_fetch_sarb_series_reads_observations(monkeypatch):
    _patch(monkeypatch, [("GetTimeseriesObservations", SARB_ROWS)])
    rates = asyncio.run(
        fixings._fetch_sarb_series("MMRD403A", "2026-07-01", "2026-07-31")
    )

    assert rates == {
        "2026-07-24": pytest.approx(0.07),
        "2026-07-23": pytest.approx(0.07),
    }


def test_fetch_sarb_series_rejects_a_non_list(monkeypatch):
    _patch(monkeypatch, [("GetTimeseriesObservations", json.dumps({"x": 1}))])

    with pytest.raises(OpenBBError, match="Unexpected fixings response"):
        asyncio.run(fixings._fetch_sarb_series("MMRD403A", "2026-07-01", "2026-07-31"))


def test_fetch_sarb_series_rejects_an_empty_window(monkeypatch):
    _patch(monkeypatch, [("GetTimeseriesObservations", SARB_ROWS)])

    with pytest.raises(OpenBBError, match="Unexpected fixings response"):
        asyncio.run(fixings._fetch_sarb_series("MMRD403A", "2030-01-01", "2030-12-31"))


def _hkma_page(records):
    return json.dumps({"result": {"records": records}})


def test_fetch_hkma_pages_until_exhausted(monkeypatch):
    monkeypatch.setattr(fixings, "HKMA_PAGE_SIZE", 2)
    pages = [
        _hkma_page(
            [
                {"end_of_date": "2026-07-24", "hibor_fixing_1m": 2.72},
                {"end_of_date": "2026-07-23", "hibor_fixing_1m": 2.71},
            ]
        ),
        _hkma_page([{"end_of_date": "2026-07-22", "hibor_fixing_1m": 2.70}]),
    ]
    calls = {"n": 0}

    class _Paged(_Session):
        def get(self, url, **kwargs):
            body = pages[min(calls["n"], len(pages) - 1)]
            calls["n"] += 1

            return _Response(body)

    import aiohttp

    monkeypatch.setattr(aiohttp, "ClientSession", lambda *a, **k: _Paged([], []))
    monkeypatch.setattr(aiohttp, "TCPConnector", lambda *a, **k: None)
    rates = asyncio.run(
        fixings._fetch_hkma("hibor_fixing_1m", "2026-07-01", "2026-07-31")
    )

    assert len(rates) == 3
    assert rates["2026-07-22"] == pytest.approx(0.027)


def test_fetch_hkma_raises_when_empty(monkeypatch):
    _patch(monkeypatch, [("hkma", _hkma_page([]))])

    with pytest.raises(OpenBBError, match="Unexpected fixings response"):
        asyncio.run(fixings._fetch_hkma("hibor_fixing_1m", "2026-07-01", "2026-07-31"))


BNM_TABLE = (
    "<table><tr><td>Ref</td><td>Pub</td><td>Rate</td></tr>"
    "<tr><td>24/07/2026</td><td>27/07/2026</td><td>2.75</td></tr>"
    "<tr><td>23/07/2026</td><td>24/07/2026</td><td>2.74</td></tr>"
    "<tr><td>02/01/2020</td><td>03/01/2020</td><td>3.00</td></tr>"
    "<tr><td>notadate</td><td>x</td><td>1.0</td></tr>"
    "<tr><td>22/07/2026</td><td>x</td><td>bad</td></tr></table>"
)


def test_fetch_bnm_reads_the_column(monkeypatch):
    seen = _patch(monkeypatch, [("data-download", BNM_TABLE)])
    rates = asyncio.run(
        fixings._fetch_bnm("data-download-myor?x=1|2", "2026-01-01", "2026-12-31")
    )

    assert rates["2026-07-24"] == pytest.approx(0.0275)
    assert rates["2026-07-23"] == pytest.approx(0.0274)
    assert any("data-download-myor" in str(u) for u in seen)


def test_fetch_bnm_raises_when_nothing_parses(monkeypatch):
    _patch(monkeypatch, [("data-download", BNM_TABLE)])

    with pytest.raises(OpenBBError, match="Unexpected fixings response"):
        asyncio.run(
            fixings._fetch_bnm("data-download-myor|2", "2030-01-01", "2030-12-31")
        )


CNB_YEAR = (
    "|1 day||1 week||2 weeks||1 month||2 months||3 months|\n"
    "Date|PRIBID|PRIBOR|PRIBID|PRIBOR|PRIBID|PRIBOR|PRIBID|PRIBOR|PRIBID|PRIBOR|PRIBID|PRIBOR\n"
    "23 Jul 2026||3.75||3.77||3.79||3.80||||3.85\n"
    "22 Jul 2026||3.75||3.77||3.78||3.80||||3.85\n"
    "bad row||1||2||3||4||||5\n"
)


def test_fetch_cnb_reads_the_tenor_column(monkeypatch):
    seen = _patch(monkeypatch, [("year.txt", CNB_YEAR)])
    rates = asyncio.run(fixings._fetch_cnb("12", "2026-01-01", "2026-12-31"))

    assert rates == {
        "2026-07-23": pytest.approx(0.0385),
        "2026-07-22": pytest.approx(0.0385),
    }
    assert any("year=2026" in str(u) for u in seen)


def test_fetch_cnb_clamps_the_year_span(monkeypatch):
    seen = _patch(monkeypatch, [("year.txt", CNB_YEAR)])
    asyncio.run(fixings._fetch_cnb("12", "1990-01-01", "2026-12-31"))
    years = {str(u).split("year=")[-1] for u in seen if "year=" in str(u)}

    assert len(years) == fixings.CNB_MAX_YEARS + 1


def test_fetch_cnb_skips_a_failed_year(monkeypatch):
    _patch(monkeypatch, [("year.txt", _Response("", status=500))])

    with pytest.raises(OpenBBError, match="Unexpected fixings response"):
        asyncio.run(fixings._fetch_cnb("12", "2026-01-01", "2026-12-31"))


BBK_CSV = (
    '"",BBIG1.D.SERIES,FLAGS\n'
    '"",Money market rates,\n'
    "Decimals,3,\n"
    "2026-07-24,2.488,\n"
    "2026-07-23,2.472,\n"
    "2020-01-02,-0.400,\n"
    "2026-07-22,,\n"
    "notadate,1.0,\n"
)


def test_fetch_bbk_reads_daily_rows(monkeypatch):
    _patch(monkeypatch, [("rest/download", BBK_CSV)])
    rates = asyncio.run(
        fixings._fetch_bbk("BBIG1/D.SERIES", "2026-07-01", "2026-07-31")
    )

    assert rates == {
        "2026-07-24": pytest.approx(0.02488),
        "2026-07-23": pytest.approx(0.02472),
    }


def test_fetch_bbk_rejects_a_non_csv_body(monkeypatch):
    _patch(monkeypatch, [("rest/download", "no separators here")])

    with pytest.raises(OpenBBError, match="Unexpected fixings response"):
        asyncio.run(fixings._fetch_bbk("BBIG1/D.SERIES", "2026-07-01", "2026-07-31"))


def test_fetch_bbk_rejects_an_empty_window(monkeypatch):
    _patch(monkeypatch, [("rest/download", BBK_CSV)])

    with pytest.raises(OpenBBError, match="Unexpected fixings response"):
        asyncio.run(fixings._fetch_bbk("BBIG1/D.SERIES", "2030-01-01", "2030-12-31"))


class _Sheet:
    def __init__(self, rows, ncols):
        self._rows = rows
        self.nrows = len(rows)
        self.ncols = ncols

    def cell_value(self, row, col):
        cells = self._rows[row]

        return cells[col] if col < len(cells) else ""


class _Book:
    def __init__(self, sheets):
        self._sheets = sheets
        self.datemode = 0

    def sheet_names(self):
        return list(self._sheets)

    def sheet_by_name(self, name):
        return self._sheets[name]


def _patch_mnb(monkeypatch, book):
    import xlrd

    _patch(monkeypatch, [("bubor", b"payload")])
    monkeypatch.setattr(xlrd, "open_workbook", lambda **kwargs: book)
    monkeypatch.setattr(
        xlrd, "xldate_as_tuple", lambda value, mode: (2026, 7, int(value), 0, 0, 0)
    )


def test_fetch_mnb_reads_year_sheets(monkeypatch):
    rows = [
        ["h"] * 8,
        ["h"] * 8,
        [24.0, 5.75, 5.75, 5.75, 5.75, 5.65, 5.60, 5.56],
        [23.0, 5.75, 5.75, 5.75, 5.75, 5.66, 5.61, 5.57],
        ["", "", "", "", "", "", "", ""],
    ]
    _patch_mnb(monkeypatch, _Book({"2026": _Sheet(rows, 8), "comment": _Sheet([], 0)}))
    rates = asyncio.run(fixings._fetch_mnb("6", "2026-01-01", "2026-12-31"))

    assert rates == {
        "2026-07-24": pytest.approx(0.0560),
        "2026-07-23": pytest.approx(0.0561),
    }


def test_fetch_mnb_skips_short_rows_and_bad_values(monkeypatch):
    rows = [["h"], ["h"], [24.0], ["notafloat", 1, 2, 3, 4, 5, 6, 7]]
    _patch_mnb(monkeypatch, _Book({"2026": _Sheet(rows, 8)}))

    with pytest.raises(OpenBBError, match="Unexpected fixings response"):
        asyncio.run(fixings._fetch_mnb("6", "2026-01-01", "2026-12-31"))


def test_fetch_mnb_ignores_years_outside_the_window(monkeypatch):
    rows = [["h"] * 8, ["h"] * 8, [24.0, 1, 2, 3, 4, 5, 5.60, 7]]
    _patch_mnb(monkeypatch, _Book({"2019": _Sheet(rows, 8)}))

    with pytest.raises(OpenBBError, match="Unexpected fixings response"):
        asyncio.run(fixings._fetch_mnb("6", "2026-01-01", "2026-12-31"))


@pytest.mark.parametrize(
    ("index", "source"),
    [
        ("TAIBOR", "_fetch_taibor"),
        ("FR007", "_fetch_cfets"),
        ("WIBOR", "_fetch_finwire"),
        ("POLSTR", "_fetch_gpw"),
        ("BUBOR", "_fetch_mnb"),
        ("KRWCD", "_fetch_bok"),
        ("JIBAR", "_fetch_sarb_series"),
        ("HIBOR", "_fetch_hkma"),
        ("MYOR", "_fetch_bnm"),
        ("PRIBOR", "_fetch_cnb"),
        ("EURIBOR", "_fetch_bbk"),
    ],
)
def test_get_fixings_dispatches_to_each_source(monkeypatch, index, source):
    from datetime import date

    called: list = []

    async def _fetch(path, start, end):
        called.append(path)

        return {"2026-07-24": 0.05}

    monkeypatch.setattr(fixings, source, _fetch)
    rates = asyncio.run(
        fixings.get_fixings(
            index, date(2026, 7, 24), date(2026, 7, 24), use_cache=False
        )
    )

    assert called
    assert rates[date(2026, 7, 24)] == pytest.approx(0.05)
