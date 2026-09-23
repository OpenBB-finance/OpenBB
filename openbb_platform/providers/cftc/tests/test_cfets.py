import asyncio
import copy
import json
from datetime import date

import pytest
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.utils.errors import EmptyDataError

from openbb_cftc.utils import cfets, store

BULLETIN = {
    "head": {"rep_code": "200"},
    "data": {
        "endDate": "2026-07-29",
        "startDate": "2026-07-16",
        "lastDate": "2026-07-29",
        "lastDateEn": "29 Jul 2026",
    },
    "records": [
        {
            "refIntrstRateNm": "CDB10",
            "refIntrstRateNmEn": "CDB10",
            "rateList": [
                {
                    "prd": "6M",
                    "wghtdAvgFxngRate": "1.7900",
                    "trdVol": "900.00",
                    "sortNo": 180,
                }
            ],
        },
        {
            "refIntrstRateNm": "FR007",
            "refIntrstRateNmEn": "FR007",
            "rateList": [
                {
                    "prd": "1Y",
                    "wghtdAvgFxngRate": "1.4262",
                    "trdVol": "59400.00",
                    "sortNo": 365,
                },
                {
                    "prd": "1M",
                    "wghtdAvgFxngRate": "1.4445",
                    "trdVol": "24100.00",
                    "sortNo": 30,
                },
                {
                    "prd": "3M",
                    "wghtdAvgFxngRate": "1.4421",
                    "trdVol": "29010.00",
                    "sortNo": 90,
                },
                {
                    "prd": "6M",
                    "wghtdAvgFxngRate": "1.4383",
                    "trdVol": "22250.00",
                    "sortNo": 180,
                },
                {
                    "prd": "9M",
                    "wghtdAvgFxngRate": "1.4300",
                    "trdVol": "30600.00",
                    "sortNo": 270,
                },
                {
                    "prd": "2Y",
                    "wghtdAvgFxngRate": "1.4321",
                    "trdVol": "3450.00",
                    "sortNo": 730,
                },
                {
                    "prd": "3Y",
                    "wghtdAvgFxngRate": "1.4526",
                    "trdVol": "1700.00",
                    "sortNo": 1095,
                },
                {
                    "prd": "5Y",
                    "wghtdAvgFxngRate": "1.5125",
                    "trdVol": "20600.00",
                    "sortNo": 1825,
                },
                {
                    "prd": "??",
                    "wghtdAvgFxngRate": "bad",
                    "trdVol": "1.00",
                    "sortNo": 9999,
                },
                {
                    "prd": "4Y",
                    "wghtdAvgFxngRate": "1.48",
                    "trdVol": "n/a",
                    "sortNo": 1461,
                },
            ],
        },
        {
            "refIntrstRateNm": "Shibor3M",
            "refIntrstRateNmEn": "Shibor3M",
            "rateList": [
                {
                    "prd": "1Y",
                    "wghtdAvgFxngRate": "1.4650",
                    "trdVol": "50.00",
                    "sortNo": 365,
                }
            ],
        },
    ],
}


class _Response:
    def __init__(self, body, status=200):
        self._body = body
        self.status = status

    def raise_for_status(self):
        if self.status >= 400:
            raise OpenBBError(f"status {self.status}")

    async def text(self):
        return self._body

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        return False


class _Session:
    def __init__(self, body, seen):
        self._body = body
        self._seen = seen

    def post(self, url, **kwargs):
        self._seen.append(kwargs.get("data"))

        return _Response(self._body)

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        return False


def _patch(monkeypatch, payload):
    import aiohttp

    seen: list = []
    body = json.dumps(payload) if isinstance(payload, dict) else payload
    monkeypatch.setattr(aiohttp, "ClientSession", lambda *a, **k: _Session(body, seen))
    monkeypatch.setattr(aiohttp, "TCPConnector", lambda *a, **k: None)

    return seen


def test_normalize_reference():
    assert cfets.normalize_reference("Shibor 3M") == "SHIBOR3M"
    assert cfets.normalize_reference("fr007") == "FR007"
    assert cfets.normalize_reference(None) == ""


def test_today_cct_is_a_date():
    assert isinstance(cfets._today_cct(), date)


def test_download_bulletin_posts_the_search_date(monkeypatch):
    seen = _patch(monkeypatch, BULLETIN)
    payload = asyncio.run(cfets._download_bulletin("2026-07-29"))

    assert payload["data"]["lastDate"] == "2026-07-29"
    assert seen == ["lang=en&searchDate=2026-07-29"]


@pytest.mark.parametrize(
    "payload",
    [
        {"head": {"rep_code": "500"}, "records": [{"x": 1}]},
        {"head": {"rep_code": "200"}, "records": []},
    ],
)
def test_download_bulletin_rejects_bad_responses(monkeypatch, payload):
    _patch(monkeypatch, payload)

    with pytest.raises(OpenBBError, match="Unexpected IRS bulletin response"):
        asyncio.run(cfets._download_bulletin("2026-07-29"))


def test_fetch_irs_bulletin_caches_a_closed_date(monkeypatch):
    _patch(monkeypatch, BULLETIN)
    monkeypatch.setattr(cfets, "_today_cct", lambda: date(2026, 7, 30))

    first = asyncio.run(cfets.fetch_irs_bulletin(date(2026, 7, 29)))

    def _forbidden(*args, **kwargs):
        raise AssertionError("the bulletin must be served from the document store")

    monkeypatch.setattr(cfets, "_download_bulletin", _forbidden)
    second = asyncio.run(cfets.fetch_irs_bulletin(date(2026, 7, 29)))

    assert first == second
    assert store.get_document("cfets-irs-bulletin:2026-07-29") == first


def test_fetch_irs_bulletin_caches_a_walked_back_date_under_both_keys(monkeypatch):
    _patch(monkeypatch, BULLETIN)
    monkeypatch.setattr(cfets, "_today_cct", lambda: date(2026, 8, 3))

    asyncio.run(cfets.fetch_irs_bulletin(date(2026, 8, 1)))

    assert store.get_document("cfets-irs-bulletin:2026-07-29") is not None
    assert store.get_document("cfets-irs-bulletin:2026-08-01") is not None


def test_fetch_irs_bulletin_does_not_cache_todays_bulletin(monkeypatch):
    _patch(monkeypatch, BULLETIN)
    monkeypatch.setattr(cfets, "_today_cct", lambda: date(2026, 7, 29))

    asyncio.run(cfets.fetch_irs_bulletin(None))

    assert store.get_document("cfets-irs-bulletin:2026-07-29") is None


def test_fetch_irs_bulletin_without_cache_skips_the_store(monkeypatch):
    seen = _patch(monkeypatch, BULLETIN)
    monkeypatch.setattr(cfets, "_today_cct", lambda: date(2026, 7, 30))
    store.put_document("cfets-irs-bulletin:2026-07-29", {"stale": True})

    payload = asyncio.run(cfets.fetch_irs_bulletin(date(2026, 7, 29), use_cache=False))

    assert payload["data"]["lastDate"] == "2026-07-29"
    assert seen
    assert store.get_document("cfets-irs-bulletin:2026-07-29") == {"stale": True}


def test_bulletin_nodes_sorts_and_scales_fr007():
    nodes = cfets.bulletin_nodes(BULLETIN, "fr007")
    days = [node["tenor_days"] for node in nodes]

    assert len(nodes) == 9
    assert days == sorted(days)
    assert [node["tenor"] for node in nodes] == [
        "1M",
        "3M",
        "6M",
        "9M",
        "1Y",
        "2Y",
        "3Y",
        "4Y",
        "5Y",
    ]

    one_month = nodes[0]
    assert one_month["tenor"] == "1M"
    assert one_month["par_rate"] == pytest.approx(0.014445)
    assert one_month["volume"] == pytest.approx(24100.0)
    assert one_month["day_count"] == "ACT/365F"
    assert one_month["day_count_basis"] == 365.0
    assert one_month["payment_period_days"] == 91

    four_year = next(node for node in nodes if node["tenor"] == "4Y")
    assert four_year["volume"] is None


def test_bulletin_nodes_leaves_bond_reference_conventions_unset():
    nodes = cfets.bulletin_nodes(BULLETIN, "CDB10")

    assert len(nodes) == 1
    assert nodes[0]["day_count"] is None
    assert nodes[0]["day_count_basis"] is None


def test_bulletin_nodes_rejects_an_unpublished_reference():
    with pytest.raises(EmptyDataError, match="LPR1Y.*Published reference rates"):
        cfets.bulletin_nodes(BULLETIN, "LPR1Y")


def test_bulletin_reference_names_reads_the_published_order():
    assert cfets.bulletin_reference_names(BULLETIN) == ["CDB10", "FR007", "Shibor3M"]


def test_bulletin_nodes_falls_back_to_the_local_name():
    payload = copy.deepcopy(BULLETIN)
    del payload["records"][1]["refIntrstRateNmEn"]

    assert len(cfets.bulletin_nodes(payload, "FR007")) == 9


def test_fetch_irs_bulletin_walks_back_to_a_published_day(monkeypatch):
    monkeypatch.setattr(cfets, "_today_cct", lambda: date(2026, 7, 30))
    seen: list = []

    async def _bulletin(search_date):
        seen.append(search_date)

        if search_date != "2026-07-29":
            raise OpenBBError(f"Unexpected IRS bulletin response for {search_date}.")

        return BULLETIN

    monkeypatch.setattr(cfets, "_download_bulletin", _bulletin)
    payload = asyncio.run(cfets.fetch_irs_bulletin(None))

    assert payload["data"]["lastDate"] == "2026-07-29"
    assert seen == ["2026-07-30", "2026-07-29"]


def test_fetch_irs_bulletin_raises_after_exhausting_the_lookback(monkeypatch):
    monkeypatch.setattr(cfets, "_today_cct", lambda: date(2026, 7, 30))

    async def _empty(search_date):
        raise OpenBBError(f"Unexpected IRS bulletin response for {search_date}.")

    monkeypatch.setattr(cfets, "_download_bulletin", _empty)

    with pytest.raises(OpenBBError, match="Unexpected IRS bulletin response"):
        asyncio.run(cfets.fetch_irs_bulletin(None))


def test_cny_curve_records_shapes_the_fr007_strip(monkeypatch):
    async def _bulletin(search_date, use_cache=True):
        return BULLETIN

    monkeypatch.setattr(cfets, "fetch_irs_bulletin", _bulletin)
    records = asyncio.run(cfets.cny_curve_records(date(2026, 7, 29)))

    assert len(records) == 9

    first = records[0]
    assert first["UPI FISN"] == "NA/Swap Fxd Flt CNY"
    assert first["Notional currency-Leg 1"] == "CNY"
    assert first["Effective Date"] == "2026-07-29"
    assert first["Expiration Date"] == "2026-08-28"
    assert float(first["Fixed rate-Leg 1"]) == pytest.approx(0.014445)
    assert first["Notional amount-Leg 1"] == "24,100,000,000"
    assert first["Fixed rate day count convention-leg 1"] == "A005"
    assert first["Dissemination Timestamp"] == "2026-07-29T00:00:00Z"

    four_year = next(r for r in records if r["Expiration Date"] == "2030-07-29")
    assert four_year["Notional amount-Leg 1"] == "1,000,000"


def test_cny_curve_records_returns_empty_on_an_outage(monkeypatch):
    async def _broken(search_date, use_cache=True):
        raise OpenBBError("service down")

    monkeypatch.setattr(cfets, "fetch_irs_bulletin", _broken)

    assert asyncio.run(cfets.cny_curve_records(date(2026, 7, 29))) == []


def test_cny_curve_records_returns_empty_without_fr007(monkeypatch):
    payload = {
        "head": {"rep_code": "200"},
        "data": {"lastDate": "2026-07-29"},
        "records": [BULLETIN["records"][0]],
    }

    async def _bulletin(search_date, use_cache=True):
        return payload

    monkeypatch.setattr(cfets, "fetch_irs_bulletin", _bulletin)

    assert asyncio.run(cfets.cny_curve_records(date(2026, 7, 29))) == []


def test_mentions_cny_reads_both_fields():
    assert cfets.mentions_cny({"UPI Underlier Name": "CNY USD"}) is True
    assert cfets.mentions_cny({"UPI FISN": "NA/Fwd NDF CNY USD"}) is True
    assert cfets.mentions_cny({"UPI Underlier Name": "EUR USD"}) is False
    assert cfets.mentions_cny({}) is False


def test_download_bulletin_wraps_transport_errors(monkeypatch):
    import aiohttp

    class _Broken:
        def post(self, url, **kwargs):
            raise RuntimeError("dns down")

        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            return False

    monkeypatch.setattr(aiohttp, "ClientSession", lambda *a, **k: _Broken())
    monkeypatch.setattr(aiohttp, "TCPConnector", lambda *a, **k: None)

    with pytest.raises(OpenBBError, match="Failed to fetch the IRS bulletin"):
        asyncio.run(cfets._download_bulletin("2026-07-29"))


def test_download_bulletin_passes_through_http_failures(monkeypatch):
    import aiohttp

    class _Http500:
        def post(self, url, **kwargs):
            return _Response("", status=500)

        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            return False

    monkeypatch.setattr(aiohttp, "ClientSession", lambda *a, **k: _Http500())
    monkeypatch.setattr(aiohttp, "TCPConnector", lambda *a, **k: None)

    with pytest.raises(OpenBBError, match="status 500"):
        asyncio.run(cfets._download_bulletin("2026-07-29"))
