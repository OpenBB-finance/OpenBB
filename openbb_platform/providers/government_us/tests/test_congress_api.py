"""Tests for the Congress.gov API client (pre-108th Congress fallback)."""

import asyncio
from datetime import date

import pytest
from openbb_core.app.model.abstract.error import OpenBBError

from openbb_government_us.congress.utils import congress_api as api


@pytest.fixture(autouse=True)
def _no_ambient_key(monkeypatch):
    """Keep a real key in user settings from leaking into these tests."""
    monkeypatch.setattr(api, "user_credentials", dict)


CREDS = {"congress_gov_api_key": "test-key"}

# Captured before the autouse fixture stubs the module attribute, so the tests
# below can exercise the real settings reader.
_REAL_USER_CREDENTIALS = api.user_credentials


def _responder(routes: dict, calls: list | None = None):
    """Build a fake ``_get`` that serves ``routes`` and records every call."""

    async def _get(path, key, **params):
        if calls is not None:
            calls.append((path, params))
        value = routes.get(path)
        if value is None:
            raise OpenBBError(f"no route for {path}")
        if callable(value):
            return value(params)
        return value

    return _get


def _bill_page(numbers, *, next_url=None, count=None):
    """Build one page of a bill-list response."""
    return {
        "bills": [
            {
                "congress": 95,
                "type": "HR",
                "number": str(n),
                "title": f"Bill {n}",
                "originChamber": "House",
                "originChamberCode": "H",
                "updateDate": "1978-06-22T00:00:00Z",
                "updateDateIncludingText": "1978-06-23T00:00:00Z",
                "latestAction": {"actionDate": f"1978-06-{n:02d}", "text": "Passed."},
            }
            for n in numbers
        ],
        "pagination": {"next": next_url, "count": count},
    }


# --------------------------------------------------------------------------
# credentials
# --------------------------------------------------------------------------


def test_api_key_prefers_explicit_over_settings(monkeypatch):
    """An injected credential wins over whatever user settings hold."""
    monkeypatch.setattr(
        api, "user_credentials", lambda: {"congress_gov_api_key": "settings"}
    )
    assert api.api_key({"congress_gov_api_key": "explicit"}) == "explicit"
    assert api.api_key(None) == "settings"


def test_api_key_missing_names_the_credential():
    """The error tells the user exactly which credential to set and where to get it."""
    with pytest.raises(OpenBBError, match="congress_gov_api_key"):
        api.api_key({})


def _patch_user_service(monkeypatch, credentials):
    """Point the lazily-imported UserService at a stand-in settings object."""
    from openbb_core.app.service import user_service

    settings = type("Settings", (), {"credentials": credentials})()
    service = type("Service", (), {"default_user_settings": settings})

    monkeypatch.setattr(user_service, "UserService", service)


def test_user_credentials_reads_a_secret_str(monkeypatch):
    """A SecretStr credential is unwrapped to its plain value."""

    class _Secret:
        def get_secret_value(self):
            return "unwrapped"

    _patch_user_service(
        monkeypatch, type("Creds", (), {"congress_gov_api_key": _Secret()})()
    )

    assert _REAL_USER_CREDENTIALS() == {"congress_gov_api_key": "unwrapped"}


def test_user_credentials_reads_a_plain_string(monkeypatch):
    """A plain-string credential is passed through unchanged."""
    _patch_user_service(
        monkeypatch, type("Creds", (), {"congress_gov_api_key": "plain"})()
    )

    assert _REAL_USER_CREDENTIALS() == {"congress_gov_api_key": "plain"}


def test_user_credentials_absent_key(monkeypatch):
    """No configured key yields an empty mapping rather than raising."""
    _patch_user_service(
        monkeypatch, type("Creds", (), {"congress_gov_api_key": None})()
    )

    assert _REAL_USER_CREDENTIALS() == {}


def test_user_credentials_survives_a_broken_settings_file(monkeypatch, caplog):
    """An unreadable settings file degrades to no key instead of failing a request."""
    from openbb_core.app.service import user_service

    def _boom():
        raise RuntimeError("settings file is corrupt")

    monkeypatch.setattr(user_service, "UserService", _boom)

    with caplog.at_level("WARNING"):
        assert _REAL_USER_CREDENTIALS() == {}

    assert "could not read user credentials" in caplog.text


# --------------------------------------------------------------------------
# coverage floor
# --------------------------------------------------------------------------


def test_require_coverage_rejects_pre_93rd():
    """Congresses with no structured records explain both source floors."""
    with pytest.raises(OpenBBError, match="predates structured bill data"):
        api._require_coverage(92)

    api._require_coverage(api.API_MIN_CONGRESS)


def test_bill_record_and_list_enforce_the_floor(monkeypatch):
    """Both entry points refuse a Congress the API cannot serve."""
    with pytest.raises(OpenBBError, match="predates structured bill data"):
        asyncio.run(api.bill_record(50, "hr", 1, CREDS))

    with pytest.raises(OpenBBError, match="predates structured bill data"):
        asyncio.run(api.list_bills(50, ["hr"], CREDS))


# --------------------------------------------------------------------------
# request plumbing
# --------------------------------------------------------------------------


def test_get_sends_key_and_format(monkeypatch):
    """Every request carries the key and asks for JSON."""
    seen: dict = {}

    async def _amake_request(url, **kwargs):
        seen["url"] = url
        seen["params"] = kwargs.get("params")
        return {"ok": True}

    import openbb_core.provider.utils.helpers as core_helpers

    monkeypatch.setattr(core_helpers, "amake_request", _amake_request)

    out = asyncio.run(api._get("bill/95/hr", "k", offset=0, limit=250))

    assert out == {"ok": True}
    assert seen["url"] == f"{api.CONGRESS_API_BASE}/bill/95/hr"
    assert seen["params"]["api_key"] == "k"
    assert seen["params"]["format"] == "json"
    assert seen["params"]["limit"] == 250


def test_get_wraps_a_transport_failure(monkeypatch):
    """A network error is reported against the path that failed."""

    async def _amake_request(url, **kwargs):
        raise TimeoutError("connection reset")

    import openbb_core.provider.utils.helpers as core_helpers

    monkeypatch.setattr(core_helpers, "amake_request", _amake_request)

    with pytest.raises(OpenBBError, match="request failed -> bill/95/hr"):
        asyncio.run(api._get("bill/95/hr", "k"))


def test_get_rejects_a_non_dict_body(monkeypatch):
    """An unexpected body shape is surfaced rather than silently treated as empty."""

    async def _amake_request(url, **kwargs):
        return ["not", "a", "dict"]

    import openbb_core.provider.utils.helpers as core_helpers

    monkeypatch.setattr(core_helpers, "amake_request", _amake_request)

    with pytest.raises(OpenBBError, match="Unexpected Congress.gov API response"):
        asyncio.run(api._get("bill/95/hr", "k"))


def test_get_surfaces_an_api_error_body(monkeypatch):
    """An API-level error (bad key, throttling) is raised with its message."""

    async def _amake_request(url, **kwargs):
        return {"error": {"code": "API_KEY_INVALID", "message": "bad key"}}

    import openbb_core.provider.utils.helpers as core_helpers

    monkeypatch.setattr(core_helpers, "amake_request", _amake_request)

    with pytest.raises(OpenBBError, match="API_KEY_INVALID"):
        asyncio.run(api._get("bill/95/hr", "k"))


# --------------------------------------------------------------------------
# pagination
# --------------------------------------------------------------------------


def test_paged_filtered_walks_to_the_reported_count(monkeypatch):
    """Paging continues until the collection's own count is satisfied.

    A fixed page budget silently truncated large Congresses: the 95th House
    returned exactly 10,000 of its 14,414 bills.
    """
    pages = [
        _bill_page(range(1, 251), next_url="more", count=600),
        _bill_page(range(251, 501), next_url="more", count=600),
        _bill_page(range(501, 601), next_url=None, count=600),
    ]
    calls: list = []

    async def _get(path, key, **params):
        calls.append(params["offset"])
        return pages[len(calls) - 1]

    monkeypatch.setattr(api, "_get", _get)

    out = asyncio.run(api._paged_filtered("bill/95/hr", "k", {}))

    assert len(out) == 600
    assert calls == [0, 250, 500]


def test_paged_filtered_stops_when_count_is_reached(monkeypatch):
    """A full final page that completes the count ends the walk."""
    pages = [
        _bill_page(range(1, 251), next_url="more", count=500),
        _bill_page(range(251, 501), next_url="more", count=500),
    ]
    calls: list = []

    async def _get(path, key, **params):
        calls.append(params["offset"])
        return pages[len(calls) - 1]

    monkeypatch.setattr(api, "_get", _get)

    assert len(asyncio.run(api._paged_filtered("bill/95/hr", "k", {}))) == 500
    assert calls == [0, 250]


def test_paged_filtered_warns_when_the_budget_runs_out(monkeypatch, caplog):
    """Exhausting the page budget is logged rather than passing off partial data."""
    monkeypatch.setattr(api, "_MAX_PAGES", 2)

    async def _get(path, key, **params):
        return _bill_page(range(1, 251), next_url="more", count=10_000)

    monkeypatch.setattr(api, "_get", _get)

    with caplog.at_level("WARNING"):
        out = asyncio.run(api._paged_filtered("bill/95/hr", "k", {}))

    assert len(out) == 500
    assert "page budget" in caplog.text


def test_paged_handles_an_empty_first_page(monkeypatch):
    """A collection with no entries returns empty without a second request."""
    calls: list = []

    async def _get(path, key, **params):
        calls.append(params)
        return {"textVersions": [], "pagination": {"count": 0}}

    monkeypatch.setattr(api, "_get", _get)

    assert asyncio.run(api._paged("bill/95/hr/1/text", "k", "textVersions")) == []
    assert len(calls) == 1


def test_paged_returns_a_dict_field_as_one_item(monkeypatch):
    """``subjects`` nests its lists under the field instead of listing them."""

    async def _get(path, key, **params):
        return {
            "subjects": {
                "legislativeSubjects": [{"name": "Labor"}],
                "policyArea": {"name": "Labor and Employment"},
            }
        }

    monkeypatch.setattr(api, "_get", _get)

    out = asyncio.run(api._paged("bill/95/hr/1/subjects", "k", "subjects"))

    assert out[0]["policyArea"] == {"name": "Labor and Employment"}


def test_paged_respects_an_explicit_limit(monkeypatch):
    """A caller-supplied limit caps the page size and stops the walk."""
    calls: list = []

    async def _get(path, key, **params):
        calls.append(params["limit"])
        return {
            "actions": [{"text": "x"}] * params["limit"],
            "pagination": {"next": "more", "count": 999},
        }

    monkeypatch.setattr(api, "_get", _get)

    out = asyncio.run(api._paged("bill/95/hr/1/actions", "k", "actions", limit=10))

    assert len(out) == 10
    assert calls == [10]


# --------------------------------------------------------------------------
# shaping
# --------------------------------------------------------------------------


def test_slim_record_shape():
    """A list entry becomes a BILLSTATUS-shaped record with empty collections."""
    record = api.slim_record(
        {
            "congress": 95,
            "type": "HR",
            "number": "8410",
            "title": "Labor Reform Act",
            "originChamber": "House",
            "originChamberCode": "H",
            "updateDate": "1978-06-22T00:00:00Z",
            "latestAction": {"actionDate": "1978-06-22", "text": "Passed."},
        }
    )

    assert record["bill_id"] == "95-hr-8410"
    assert record["number"] == 8410
    assert record["_detailed"] is False
    for field in ("sponsors", "actions", "summaries", "textVersions", "titles"):
        assert record[field] == []


def test_slim_record_tolerates_a_non_numeric_number():
    """A malformed number does not crash the projection."""
    record = api.slim_record({"congress": 95, "type": "HR", "number": "E1"})
    assert record["number"] == 0
    assert record["bill_id"] == "95-hr-E1"


def test_list_item_normalizes_empty_fields():
    """Blank dates and actions come back as None, matching the store's rows."""
    item = api._list_item({"congress": 95, "type": "HR", "number": "1"})

    assert item["updateDate"] is None
    assert item["updateDateIncludingText"] is None
    assert item["latestAction"] == {"actionDate": None, "text": None}


def test_text_versions_drops_urlless_formats():
    """Formats with no URL are discarded, and a null date becomes empty."""
    out = api._text_versions(
        [
            {
                "type": "Enrolled Bill",
                "date": None,
                "formats": [{"url": None}, {"url": "https://x/BILLS-95hr8410enr.pdf"}],
            }
        ]
    )

    assert out[0]["date"] == ""
    assert out[0]["formats"] == [{"url": "https://x/BILLS-95hr8410enr.pdf"}]


def test_committees_keeps_activities_and_subcommittees():
    """Committee nesting survives the projection."""
    out = api._committees(
        [
            {
                "name": "Judiciary",
                "chamber": "House",
                "activities": [{"name": "Referred to"}],
                "subcommittees": [{"name": "Crime"}],
            }
        ]
    )

    assert out[0]["activities"] == [{"name": "Referred to"}]
    assert out[0]["subcommittees"] == [{"name": "Crime"}]
    assert out[0]["systemCode"] == ""


def test_cosponsors_coerce_the_original_flag():
    """The original-cosponsor flag becomes a real bool for the markdown renderer."""
    out = api._cosponsors(
        [{"fullName": "A", "isOriginalCosponsor": True}, {"fullName": "B"}]
    )

    assert out[0]["isOriginalCosponsor"] is True
    assert out[1]["isOriginalCosponsor"] is False


def test_bill_id_lowercases_the_type():
    """Bill ids are canonical regardless of the casing the API returns."""
    assert api.bill_id(95, "HR", 8410) == "95-hr-8410"


# --------------------------------------------------------------------------
# list_bills
# --------------------------------------------------------------------------


def test_list_bills_sorts_paginates_and_windows(monkeypatch):
    """Merged types are sorted by latest action, then offset and limit applied."""
    calls: list = []

    async def _paged_filtered(path, key, params):
        calls.append((path, dict(params)))
        return _bill_page([1, 2, 3])["bills"]

    monkeypatch.setattr(api, "_paged_filtered", _paged_filtered)

    out = asyncio.run(
        api.list_bills(
            95,
            ["hr"],
            CREDS,
            start_date=date(1978, 1, 1),
            end_date=date(1978, 12, 31),
            limit=2,
            offset=1,
            sort_by="desc",
        )
    )

    assert [b["number"] for b in out] == [2, 1]
    assert calls[0][1] == {
        "fromDateTime": "1978-01-01T00:00:00Z",
        "toDateTime": "1978-12-31T23:59:59Z",
    }


def test_list_bills_ascending_and_unlimited(monkeypatch):
    """``sort_by='asc'`` reverses the order and ``limit=0`` returns everything."""

    async def _paged_filtered(path, key, params):
        return _bill_page([1, 2, 3])["bills"]

    monkeypatch.setattr(api, "_paged_filtered", _paged_filtered)

    out = asyncio.run(api.list_bills(95, ["hr"], CREDS, limit=0, sort_by="asc"))

    assert [b["number"] for b in out] == [1, 2, 3]


def test_list_bills_degrades_when_one_type_fails(monkeypatch, caplog):
    """One failing bill type is logged and skipped, not fatal to the whole list."""

    async def _paged_filtered(path, key, params):
        if path.endswith("/s"):
            raise OpenBBError("upstream 500")
        return _bill_page([1])["bills"]

    monkeypatch.setattr(api, "_paged_filtered", _paged_filtered)

    with caplog.at_level("ERROR"):
        out = asyncio.run(api.list_bills(95, ["hr", "s"], CREDS))

    assert [b["bill_id"] for b in out] == ["95-hr-1"]
    assert "API list failed for 95-s" in caplog.text


# --------------------------------------------------------------------------
# bill_record
# --------------------------------------------------------------------------


def _detail_routes():
    """Routes for a full bill detail fan-out."""
    base = "bill/95/hr/8410"
    return {
        base: {
            "bill": {
                "congress": 95,
                "number": 8410,
                "type": "HR",
                "title": "Labor Reform Act",
                "originChamber": "House",
                "originChamberCode": "H",
                "introducedDate": "1977-07-19",
                "updateDate": "1978-06-22T00:00:00Z",
                "latestAction": {"actionDate": "1978-06-22", "text": "Recommitted."},
                "sponsors": [{"fullName": "Rep. Thompson", "bioguideId": "T000001"}],
            }
        },
        f"{base}/actions": {"actions": [{"actionDate": "1977-07-19", "text": "Intro"}]},
        f"{base}/amendments": {"amendments": []},
        f"{base}/committees": {"committees": [{"name": "Education and Labor"}]},
        f"{base}/cosponsors": {"cosponsors": [{"fullName": "Rep. Perkins"}]},
        f"{base}/relatedbills": {"relatedBills": [{"number": 77}]},
        f"{base}/subjects": {
            "subjects": {
                "legislativeSubjects": [{"name": "Labor"}],
                "policyArea": {"name": "Industrial relations"},
            }
        },
        f"{base}/summaries": {"summaries": [{"text": "<p>Summary.</p>"}]},
        f"{base}/text": {"textVersions": []},
        f"{base}/titles": {"titles": [{"titleType": "Short Title", "title": "LRA"}]},
    }


def test_bill_record_assembles_every_sub_resource(monkeypatch):
    """The detail document and its nine sub-collections fold into one record."""
    monkeypatch.setattr(api, "_get", _responder(_detail_routes()))

    record = asyncio.run(api.bill_record(95, "hr", 8410, CREDS))

    assert record["bill_id"] == "95-hr-8410"
    assert record["_detailed"] is True
    assert record["title"] == "Labor Reform Act"
    assert record["sponsors"][0]["bioguideId"] == "T000001"
    assert record["cosponsors"][0]["isOriginalCosponsor"] is False
    assert record["actions"][0]["text"] == "Intro"
    assert record["committees"][0]["name"] == "Education and Labor"
    assert record["relatedBills"][0]["number"] == 77
    assert record["subjects"] == [{"name": "Labor"}]
    assert record["policyArea"] == {"name": "Industrial relations"}
    assert record["titles"][0]["type"] == "Short Title"
    assert record["latestAction"]["text"] == "Recommitted."


def test_bill_record_policy_area_prefers_the_detail_document(monkeypatch):
    """A policy area on the bill itself wins over the one under subjects."""
    routes = _detail_routes()
    routes["bill/95/hr/8410"]["bill"]["policyArea"] = {"name": "From detail"}
    monkeypatch.setattr(api, "_get", _responder(routes))

    record = asyncio.run(api.bill_record(95, "hr", 8410, CREDS))

    assert record["policyArea"] == {"name": "From detail"}


def test_bill_record_tolerates_a_failing_sub_resource(monkeypatch, caplog):
    """One unavailable sub-collection empties that field instead of failing the bill."""
    routes = _detail_routes()
    del routes["bill/95/hr/8410/summaries"]
    monkeypatch.setattr(api, "_get", _responder(routes))

    with caplog.at_level("WARNING"):
        record = asyncio.run(api.bill_record(95, "hr", 8410, CREDS))

    assert record["summaries"] == []
    assert record["title"] == "Labor Reform Act"
    assert "summaries" in caplog.text


def test_bill_record_missing_bill_raises_bill_not_found(monkeypatch):
    """An absent bill raises the not-found type so callers can answer 404."""
    from openbb_government_us.congress.utils.bulk import BillNotFound

    monkeypatch.setattr(api, "_get", _responder({"bill/95/hr/1": {"bill": None}}))

    with pytest.raises(BillNotFound, match="Bill not found on Congress.gov"):
        asyncio.run(api.bill_record(95, "hr", 1, CREDS))


def test_fetch_bill_list_returns_slim_records(monkeypatch):
    """The cacheable list fetch yields store-ready records."""

    async def _paged_filtered(path, key, params):
        assert path == "bill/95/hr"
        return _bill_page([1, 2])["bills"]

    monkeypatch.setattr(api, "_paged_filtered", _paged_filtered)

    out = asyncio.run(api.fetch_bill_list(95, "HR", CREDS))

    assert [r["bill_id"] for r in out] == ["95-hr-1", "95-hr-2"]
    assert all(r["_detailed"] is False for r in out)


def test_paged_stops_once_the_reported_total_is_collected(monkeypatch):
    """A sub-collection stops at its count even when a next link is still offered."""
    calls: list = []

    async def _get(path, key, **params):
        calls.append(params["offset"])
        return {
            "actions": [{"text": "x"}] * api._PAGE_LIMIT,
            "pagination": {"next": "more", "count": api._PAGE_LIMIT},
        }

    monkeypatch.setattr(api, "_get", _get)

    out = asyncio.run(api._paged("bill/95/hr/1/actions", "k", "actions"))

    assert len(out) == api._PAGE_LIMIT
    assert calls == [0]
