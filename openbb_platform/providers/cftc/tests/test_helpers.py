import asyncio

import pytest
from openbb_core.app.model.abstract.error import OpenBBError

from openbb_cftc.models.cot_search import CftcCotSearchData
from openbb_cftc.utils import helpers


class _FakeResponse:
    def __init__(self, status, content_type, payload=None):
        self.status = status
        self.headers = {"Content-Type": content_type}
        self._payload = payload

    async def json(self):
        return self._payload


def test_socrata_json_raises_on_a_maintenance_page():
    with pytest.raises(OpenBBError, match="maintenance"):
        asyncio.run(helpers.socrata_json(_FakeResponse(503, "text/html"), None))


def test_socrata_json_returns_the_payload_on_success():
    response = _FakeResponse(200, "application/json", [{"code": "1"}])

    assert asyncio.run(helpers.socrata_json(response, None)) == [{"code": "1"}]


def test_get_cot_choices_shapes_and_caches(monkeypatch):
    calls: list = []

    async def _fetch(params, credentials):
        calls.append(params)
        return [
            CftcCotSearchData(
                code="CFTC_088691",
                name=" GOLD ",
                subcategory=" PRECIOUS METALS ",
            ),
            CftcCotSearchData(code="", name="NO CODE"),
        ]

    monkeypatch.setattr(
        "openbb_cftc.models.cot_search.CftcCotSearchFetcher.fetch_data", _fetch
    )
    first = asyncio.run(helpers.get_cot_choices())
    second = asyncio.run(helpers.get_cot_choices())

    assert len(calls) == 1
    assert first is second
    assert first == [
        {
            "label": "GOLD",
            "value": "CFTC_088691",
            "extraInfo": {
                "description": "PRECIOUS METALS  | CFTC_088691",
                "rightOfDescription": "",
            },
        }
    ]


def test_get_cot_choices_ignores_foreign_rows(monkeypatch):

    async def _fetch(params, credentials):
        return [("not", "a record"), CftcCotSearchData(code="1", name="GOLD")]

    monkeypatch.setattr(
        "openbb_cftc.models.cot_search.CftcCotSearchFetcher.fetch_data", _fetch
    )
    choices = asyncio.run(helpers.get_cot_choices())

    assert [c["value"] for c in choices] == ["1"]


def test_reset_cot_choices(monkeypatch):
    calls: list = []

    async def _fetch(params, credentials):
        calls.append(params)
        return [CftcCotSearchData(code="1", name="GOLD")]

    monkeypatch.setattr(
        "openbb_cftc.models.cot_search.CftcCotSearchFetcher.fetch_data", _fetch
    )
    asyncio.run(helpers.get_cot_choices())
    helpers.reset_cot_choices()
    asyncio.run(helpers.get_cot_choices())

    assert len(calls) == 2


def test_get_ppd_date_choices_is_newest_first(monkeypatch):

    async def _dates(asset_class):
        return ["2026-07-14", "2026-07-15"]

    monkeypatch.setattr("openbb_cftc.utils.dtcc.get_available_dates", _dates)
    choices = asyncio.run(helpers.get_ppd_date_choices(asset_class="rates"))

    assert [c["value"] for c in choices] == ["2026-07-15", "2026-07-14"]
