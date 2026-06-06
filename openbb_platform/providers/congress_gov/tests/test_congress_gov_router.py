"""Tests for the Congress.gov router commands and endpoints."""

import asyncio
import re
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.exceptions import HTTPException

from openbb_congress_gov import congress_gov_router as router

MODEL_COMMANDS = [
    router.bills,
    router.laws,
    router.calendars,
    router.mandated_reports,
    router.bill_info,
    router.bill_text,
    router.amendments,
    router.amendment_info,
    router.amendment_text,
    router.committee_info,
    router.committee_documents,
    router.search,
    router.members,
    router.member_votes,
    router.member_legislation,
]


@pytest.mark.parametrize("command", MODEL_COMMANDS)
def test_model_backed_commands(command):
    """Each model-backed command delegates to OBBject.from_query(OpenBBQuery(...))."""

    class _Result:
        results = ["sentinel"]

    with (
        patch.object(router, "OBBject") as mock_obbject,
        patch.object(router, "OpenBBQuery") as mock_query,
    ):
        mock_obbject.from_query = AsyncMock(return_value=_Result())

        result = asyncio.run(
            command(
                cc=None,
                provider_choices=None,
                standard_params=None,
                extra_params=None,
            )
        )

    assert mock_query.called
    mock_obbject.from_query.assert_awaited_once()
    assert result is not None


def test_bill_text_urls_empty_workspace():
    """An empty bill_id in workspace mode returns a placeholder."""
    result = asyncio.run(router.bill_text_urls(bill_id="", is_workspace=True))
    assert result[0]["value"] == ""


def test_bill_text_urls_empty_raises():
    """An empty bill_id outside workspace raises an HTTPException."""
    with pytest.raises(HTTPException):
        asyncio.run(router.bill_text_urls(bill_id=""))


def test_bill_text_urls_delegates(monkeypatch):
    """The bill id is passed straight through to the keyless helper."""
    captured = {}

    async def _fake(bill_id, is_workspace):
        captured["bill_id"] = bill_id
        return [{"label": "x", "value": "y"}]

    monkeypatch.setattr(
        "openbb_congress_gov.utils.helpers.get_bill_text_choices", _fake
    )
    result = asyncio.run(router.bill_text_urls(bill_id="119-s-1947"))
    assert result == [{"label": "x", "value": "y"}]
    assert captured["bill_id"] == "119-s-1947"


def test_amendment_text_urls_empty_workspace():
    """An empty amendment_id in workspace mode returns a placeholder."""
    result = asyncio.run(router.amendment_text_urls(amendment_id="", is_workspace=True))
    assert result[0]["value"] == ""


def test_amendment_text_urls_empty_raises():
    """An empty amendment_id outside workspace raises an HTTPException."""
    with pytest.raises(HTTPException):
        asyncio.run(router.amendment_text_urls(amendment_id=""))


def test_amendment_text_urls_delegates(monkeypatch):
    """The amendment id is passed straight through to the keyless helper."""
    captured = {}

    async def _fake(amendment_id, is_workspace):
        captured["amendment_id"] = amendment_id
        return [{"label": "x", "value": "y"}]

    monkeypatch.setattr(
        "openbb_congress_gov.utils.helpers.get_amendment_text_choices", _fake
    )
    result = asyncio.run(router.amendment_text_urls(amendment_id="119-hamdt-2"))
    assert result == [{"label": "x", "value": "y"}]
    assert captured["amendment_id"] == "119-hamdt-2"


def test_committee_choices_no_chamber():
    """No chamber returns the chamber options."""
    result = asyncio.run(router.committee_choices())
    assert any(c["value"] == "senate" for c in result)


def test_committee_choices_subcommittees_no_committee():
    """Subcommittees requested without a committee prompts for one."""
    result = asyncio.run(router.committee_choices(chamber="senate", subcommittees=True))
    assert "Select a committee first" in result[0]["label"]


def test_committee_choices_subcommittees():
    """Subcommittees for a known committee are returned from the mapping."""
    result = asyncio.run(
        router.committee_choices(
            chamber="house", committee="hsag00", subcommittees=True
        )
    )
    assert any(c["value"] == "hsag22" for c in result)


def test_committee_choices_subcommittees_unknown():
    """An unknown committee returns the default no-subcommittee option."""
    result = asyncio.run(
        router.committee_choices(
            chamber="house", committee="zzzz99", subcommittees=True
        )
    )
    assert result == router.NO_SUBCOMMITTEES


def test_committee_choices_invalid_chamber():
    """An invalid chamber returns the invalid-chamber message."""
    result = asyncio.run(router.committee_choices(chamber="elsewhere"))
    assert "Invalid chamber" in result[0]["label"]


def test_committee_choices_valid_chamber():
    """A valid chamber returns its committee list."""
    result = asyncio.run(router.committee_choices(chamber="senate"))
    assert any(c["value"] == "ssaf00" for c in result)


def test_committee_document_urls_empty_workspace():
    """No committee in workspace mode returns a placeholder."""
    result = asyncio.run(
        router.committee_document_urls(
            chamber="senate", committee="", is_workspace=True
        )
    )
    assert result[0]["value"] == ""


def test_committee_document_urls_empty_raises():
    """No committee outside workspace raises an HTTPException."""
    with pytest.raises(HTTPException):
        asyncio.run(router.committee_document_urls(chamber="senate", committee=""))


def test_committee_document_urls_delegates(monkeypatch):
    """A populated committee delegates to get_committee_doc_choices."""
    captured = {}

    async def _fake(**kwargs):
        captured.update(kwargs)
        return [{"label": "A Report", "value": "u1"}]

    monkeypatch.setattr(
        "openbb_congress_gov.utils.committees.get_committee_doc_choices", _fake
    )
    result = asyncio.run(
        router.committee_document_urls(
            chamber="senate",
            committee="ssaf00",
            doc_type="report",
            congress=119,
            is_workspace=True,
        )
    )
    assert result == [{"label": "A Report", "value": "u1"}]
    assert captured["system_code"] == "ssaf00"
    assert captured["congress"] == 119
    assert captured["doc_type"] == "report"
    assert captured["is_workspace"] is True


def test_committee_document_urls_default_congress(monkeypatch):
    """A None congress defaults to the current congress; subcommittee is preferred."""
    captured = {}

    async def _fake(**kwargs):
        captured.update(kwargs)
        return []

    monkeypatch.setattr(
        "openbb_congress_gov.utils.committees.get_committee_doc_choices", _fake
    )
    result = asyncio.run(
        router.committee_document_urls(
            chamber="house", committee="hsju00", subcommittee="hsju03"
        )
    )
    assert captured["congress"] >= 119
    assert captured["system_code"] == "hsju03"
    assert result == []


def test_get_congress_gov_apps_json_success():
    """The bundled apps.json is parsed and returned."""
    result = asyncio.run(router.get_congress_gov_apps_json())
    assert result
    assert isinstance(result, (dict, list))


def test_get_congress_gov_apps_json_missing(monkeypatch):
    """A missing/unreadable apps.json returns an empty list."""

    class _BadPath:
        def __truediv__(self, other):
            return self

        @property
        def parent(self):
            return self

        def open(self, *args, **kwargs):
            raise FileNotFoundError("nope")

    monkeypatch.setattr(router, "__file__", "/nonexistent/x.py")

    import pathlib

    monkeypatch.setattr(pathlib, "Path", lambda *a, **k: _BadPath())
    result = asyncio.run(router.get_congress_gov_apps_json())
    assert result == []


def test_document_viewers_resolve_package_id():
    """Each viewer options endpoint resolves a package id to its PDF link."""
    for command, pkg in (
        (router.mandated_report_urls, "CMR-A98-00199920"),
        (router.search_document_urls, "CHRG-119hhrg63299"),
    ):
        ws = asyncio.run(command(package_id=pkg, is_workspace=True))
        assert ws[0]["value"].endswith(f"/{pkg}/pdf/{pkg}.pdf")
        raw = asyncio.run(command(package_id=pkg))
        assert raw[0]["package_id"] == pkg
        assert raw[0]["pdf"].endswith(f"/{pkg}.pdf")


def test_search_document_urls_empty_workspace():
    """An empty package id in workspace mode returns a select-a-row placeholder."""
    result = asyncio.run(router.search_document_urls(package_id="", is_workspace=True))
    assert result == [{"label": "Select a row to view the document.", "value": ""}]


def test_search_document_urls_empty_raises():
    """An empty package id outside workspace raises an HTTPException."""
    with pytest.raises(HTTPException):
        asyncio.run(router.search_document_urls(package_id=""))


def _patch_fetch_cmr(monkeypatch, records):
    """Stub bulk.fetch_cmr to return canned mandated-report records."""

    async def _fake(congress, pagesize=100, offset=0):
        return list(records)

    monkeypatch.setattr("openbb_congress_gov.utils.bulk.fetch_cmr", _fake)


def test_mandated_report_urls_empty_workspace(monkeypatch):
    """No package id and no recent reports returns the workspace placeholder."""
    _patch_fetch_cmr(monkeypatch, [])
    result = asyncio.run(router.mandated_report_urls(package_id="", is_workspace=True))
    assert result == [{"label": "No documents available.", "value": ""}]


def test_mandated_report_urls_empty_non_workspace(monkeypatch):
    """No package id and no recent reports returns an empty non-workspace list."""
    _patch_fetch_cmr(monkeypatch, [])
    assert asyncio.run(router.mandated_report_urls(package_id="")) == []


def test_mandated_report_urls_fallback(monkeypatch):
    """No package id falls back to recent reports as document choices."""
    _patch_fetch_cmr(
        monkeypatch,
        [{"package_id": "CMR-A98-1", "title": "Report One", "pdf": "https://x/r.pdf"}],
    )
    ws = asyncio.run(router.mandated_report_urls(package_id="", is_workspace=True))
    assert ws[0]["label"] == "Report One - CMR-A98-1.pdf"
    assert ws[0]["value"] == "https://x/r.pdf"
    raw = asyncio.run(router.mandated_report_urls(package_id="", congress=119))
    assert raw[0]["package_id"] == "CMR-A98-1"


def test_law_text_urls_resolves_by_law_id():
    """The law viewer reconstructs the PLAW package id from law_id + law_type."""
    ws = asyncio.run(
        router.law_text_urls(law_id="119-1", law_type="public", is_workspace=True)
    )
    assert ws[0]["value"].endswith("/PLAW-119publ1/pdf/PLAW-119publ1.pdf")
    priv = asyncio.run(router.law_text_urls(law_id="119-2", law_type="private"))
    assert priv[0]["package_id"] == "PLAW-119pvtl2"


def _patch_load_plaw(monkeypatch, public=(), private=()):
    """Stub bulk.load_plaw to serve canned PLAW records per law type."""

    async def _fake(congress, law_type):
        return list(private if law_type == "private" else public)

    monkeypatch.setattr("openbb_congress_gov.utils.bulk.load_plaw", _fake)


def test_law_text_urls_empty_workspace_placeholder(monkeypatch):
    """An empty law_id with no recent laws returns the workspace placeholder."""
    _patch_load_plaw(monkeypatch)
    result = asyncio.run(router.law_text_urls(law_id="", is_workspace=True))
    assert result == [{"label": "No documents available.", "value": ""}]


def test_law_text_urls_empty_non_workspace(monkeypatch):
    """An empty law_id with no recent laws returns an empty non-workspace list."""
    _patch_load_plaw(monkeypatch)
    assert asyncio.run(router.law_text_urls(law_id="")) == []


def test_law_text_urls_fallback(monkeypatch):
    """A law_id with no dash merges public + private laws, most recent first."""
    _patch_load_plaw(
        monkeypatch,
        public=[{"package_id": "PLAW-119publ1", "title": "Law One"}],
        private=[{"package_id": "PLAW-119pvtl2", "title": "Law Two"}],
    )
    out = asyncio.run(router.law_text_urls(law_id="notalawid", congress=119))
    assert [c["package_id"] for c in out] == ["PLAW-119pvtl2", "PLAW-119publ1"]


def test_calendar_document_urls_resolves_by_package_id():
    """A package id resolves directly to its calendar document links."""
    ws = asyncio.run(
        router.calendar_document_urls(
            package_id="CCAL-119hcal-2026-05-21", is_workspace=True
        )
    )
    assert ws[0]["value"].endswith(
        "/CCAL-119hcal-2026-05-21/pdf/CCAL-119hcal-2026-05-21.pdf"
    )
    sen = asyncio.run(
        router.calendar_document_urls(package_id="CCAL-119scal-2026-05-21")
    )
    assert sen[0]["package_id"] == "CCAL-119scal-2026-05-21"


def _patch_load_calendars(monkeypatch, records):
    """Stub bulk.load_calendars to return canned CCAL records for any chamber."""

    async def _fake(congress, chamber):
        return list(records)

    monkeypatch.setattr("openbb_congress_gov.utils.bulk.load_calendars", _fake)


def test_calendar_document_urls_empty_workspace_placeholder(monkeypatch):
    """No package id and no recent editions returns the workspace placeholder."""
    _patch_load_calendars(monkeypatch, [])
    result = asyncio.run(
        router.calendar_document_urls(package_id="", is_workspace=True)
    )
    assert result == [{"label": "No documents available.", "value": ""}]


def test_calendar_document_urls_fallback(monkeypatch):
    """No package id falls back to recent editions, most recent first."""
    _patch_load_calendars(
        monkeypatch,
        [
            {"package_id": "CCAL-119hcal-2025-01-03", "calendar_date": "2025-01-03"},
            {"package_id": "CCAL-119hcal-2025-02-01", "calendar_date": "2025-02-01"},
        ],
    )
    out = asyncio.run(router.calendar_document_urls(package_id="", congress=119))
    assert out[0]["package_id"] == "CCAL-119hcal-2025-02-01"


def test_preload_bills(monkeypatch):
    """_preload_bills warms BILLSTATUS for every bill type of the current Congress."""
    from openbb_congress_gov.utils.constants import BillTypes

    status_calls: list = []

    async def _fake_ensure(congress, bill_type):
        status_calls.append((congress, bill_type))

    monkeypatch.setattr(
        "openbb_congress_gov.utils.bulk.ensure_billstatus", _fake_ensure
    )
    asyncio.run(router._preload_bills())
    assert {bt for _, bt in status_calls} == set(BillTypes)
    assert all(c >= 119 for c, _ in status_calls)


def test_served_range():
    """_served_range spans current back to the earliest valid term, skipping bad ones."""
    members = [
        {"terms": [{"start": "1979-01-03"}, {"start": "2025-01-03"}]},
        {"terms": [{"start": "1900-01-03"}, {"start": ""}]},
    ]
    out = router._served_range(members, 119)
    assert out[0] == 119
    assert min(out) == 96
    assert out == list(range(119, 95, -1))


def _patch_member_warmup(monkeypatch, *, members):
    """Patch the member-warmup dependencies; return the recorded calls dict."""
    calls: dict = {"passage": [], "legislation": [], "ref": []}

    async def _members():
        calls["ref"].append("members")
        return members

    async def _social():
        calls["ref"].append("social")
        return {}

    async def _committee_membership():
        calls["ref"].append("committee_membership")
        return {}

    async def _committee_structure():
        calls["ref"].append("committee_structure")
        return []

    async def _legislators():
        calls["ref"].append("legislators")
        return {}

    async def _build_passage(congresses, keep_votes=None):
        calls["passage"].append((list(congresses), keep_votes))

    async def _ingest_bills(congresses):
        calls["legislation"].append(list(congresses))

    base = "openbb_congress_gov.utils.bulk."
    monkeypatch.setattr(base + "load_members", _members)
    monkeypatch.setattr(base + "load_social_media", _social)
    monkeypatch.setattr(base + "load_committee_membership", _committee_membership)
    monkeypatch.setattr(base + "load_committee_structure", _committee_structure)
    monkeypatch.setattr(base + "load_legislators", _legislators)
    monkeypatch.setattr(base + "build_passage_index", _build_passage)
    monkeypatch.setattr(base + "ingest_billstatus_range", _ingest_bills)
    return calls


def test_preload_members(monkeypatch):
    """Cold warmup builds recent indexes first, then the full history in the store."""
    members = [{"terms": [{"start": "1979-01-03"}, {"start": "2025-01-03"}]}]
    calls = _patch_member_warmup(monkeypatch, members=members)

    asyncio.run(router._preload_members())

    assert set(calls["ref"]) == {
        "members",
        "social",
        "committee_membership",
        "committee_structure",
        "legislators",
    }
    assert len(calls["passage"]) == 1
    passage_congresses, keep = calls["passage"][0]
    assert passage_congresses[0] == 119 and min(passage_congresses) == 96
    assert keep == [119, 118]
    assert len(calls["legislation"]) == 1
    assert calls["legislation"][0][0] == 119 and min(calls["legislation"][0]) == 108


def test_preload_members_handles_failed_reference_load(monkeypatch):
    """A failed member load degrades to the current Congress without raising."""

    async def _boom():
        raise RuntimeError("network down")

    calls = _patch_member_warmup(monkeypatch, members=[])
    monkeypatch.setattr("openbb_congress_gov.utils.bulk.load_members", _boom)

    asyncio.run(router._preload_members())
    assert calls["passage"][0][0] == [119]


def test_preload_members_handles_index_failures(monkeypatch):
    """Passage and legislation index failures are caught and logged, not raised."""
    _patch_member_warmup(monkeypatch, members=[])

    async def _boom_passage(congresses, keep_votes=None):
        raise RuntimeError("passage down")

    async def _boom_legislation(congresses):
        raise RuntimeError("legislation down")

    base = "openbb_congress_gov.utils.bulk."
    monkeypatch.setattr(base + "build_passage_index", _boom_passage)
    monkeypatch.setattr(base + "ingest_billstatus_range", _boom_legislation)

    asyncio.run(router._preload_members())


def test_schedule_background_runs_and_tracks(monkeypatch):
    """_schedule_background runs the coroutine and clears the task when it finishes."""
    ran: dict = {}

    async def _coro():
        ran["done"] = True

    async def _run():
        router._BACKGROUND_TASKS.clear()
        router._schedule_background(_coro)
        await asyncio.sleep(0)
        await asyncio.sleep(0)

    asyncio.run(_run())
    assert ran.get("done") is True
    assert set() == router._BACKGROUND_TASKS


def test_schedule_background_logs_failure(monkeypatch):
    """A failing background coroutine is logged and removed from the task set."""

    async def _boom():
        raise RuntimeError("warmup failed")

    async def _run():
        router._BACKGROUND_TASKS.clear()
        router._schedule_background(_boom)
        await asyncio.sleep(0)
        await asyncio.sleep(0)

    asyncio.run(_run())
    assert set() == router._BACKGROUND_TASKS


def test_schedule_background_no_running_loop():
    """Without a running event loop, scheduling is a no-op (no exception)."""
    router._schedule_background(lambda: None)


def test_warm_cache_schedules_once(monkeypatch):
    """_warm_cache schedules the warmup once and the guard blocks a second call."""
    scheduled: list = []

    def _capture(coro_factory):
        scheduled.append(coro_factory)

    monkeypatch.setattr(router, "_schedule_background", _capture)
    router._WARM_GUARD.clear()
    router._warm_cache()
    router._warm_cache()
    assert scheduled == [router._warmup]
    router._WARM_GUARD.clear()


def test_warmup_orders_preloads_and_schedules_loops(monkeypatch):
    """_warmup preloads bills then members, seeds markers, and schedules refresh loops."""
    order: list = []

    async def _preload_bills():
        order.append("bills")

    async def _preload_members():
        order.append("members")

    async def _seed():
        order.append("seed")

    def _schedule(coro_factory):
        order.append(coro_factory.__name__)

    monkeypatch.setattr(router, "_preload_bills", _preload_bills)
    monkeypatch.setattr(router, "_preload_members", _preload_members)
    monkeypatch.setattr("openbb_congress_gov.utils.bulk.seed_billstatus_markers", _seed)
    monkeypatch.setattr(router, "_schedule_background", _schedule)

    asyncio.run(router._warmup())
    assert order == [
        "bills",
        "members",
        "seed",
        "_refresh_loop",
        "_passage_refresh_loop",
    ]


def _ticking_sleep():
    """Sleep stub that lets the first tick run, then cancels on the second."""
    state = {"n": 0}

    async def _sleep(_seconds):
        state["n"] += 1
        if state["n"] >= 2:
            raise asyncio.CancelledError

    return _sleep


def test_refresh_loop_logs_error_then_cancels(monkeypatch):
    """A refresh error is caught and logged; cancellation later propagates."""
    refreshed: dict = {"n": 0}

    async def _refresh():
        refreshed["n"] += 1
        raise RuntimeError("refresh down")

    monkeypatch.setattr("openbb_congress_gov.utils.bulk.refresh_billstatus", _refresh)
    monkeypatch.setattr(asyncio, "sleep", _ticking_sleep())
    with pytest.raises(asyncio.CancelledError):
        asyncio.run(router._refresh_loop())
    assert refreshed["n"] == 1


def test_passage_refresh_loop_logs_error_then_cancels(monkeypatch):
    """A passage refresh error is caught and logged; cancellation later propagates."""
    refreshed: dict = {"n": 0}

    async def _refresh():
        refreshed["n"] += 1
        raise RuntimeError("passage refresh down")

    monkeypatch.setattr("openbb_congress_gov.utils.bulk.refresh_passage", _refresh)
    monkeypatch.setattr(asyncio, "sleep", _ticking_sleep())
    with pytest.raises(asyncio.CancelledError):
        asyncio.run(router._passage_refresh_loop())
    assert refreshed["n"] == 1


def test_stop_background_cancels_tasks(monkeypatch):
    """_stop_background cancels every tracked background task."""

    async def _run():
        router._BACKGROUND_TASKS.clear()

        async def _forever():
            await asyncio.sleep(3600)

        task = asyncio.get_running_loop().create_task(_forever())
        router._BACKGROUND_TASKS.add(task)
        router._stop_background()
        await asyncio.sleep(0)
        return task

    task = asyncio.run(_run())
    assert task.cancelled()
    router._BACKGROUND_TASKS.clear()


def test_committee_members_html_endpoint(monkeypatch):
    """The committee_members endpoint returns a raw text/html card response."""

    async def _members(system_code):
        assert system_code == "hsju03"
        return [{"name": "Jim Jordan", "title": "Chair", "bioguide": "J000289"}]

    async def _leg():
        return {
            "J000289": {
                "party": "Republican",
                "state": "OH",
                "photo_url": "https://x/J000289.jpg",
            }
        }

    async def _photo(bioguide):
        return f"https://x/{bioguide}.jpg"

    monkeypatch.setattr(
        "openbb_congress_gov.utils.committees.get_committee_members", _members
    )
    monkeypatch.setattr("openbb_congress_gov.utils.bulk.load_legislators", _leg)
    monkeypatch.setattr("openbb_congress_gov.utils.bulk.member_photo_url", _photo)

    resp = asyncio.run(
        router.committee_members(
            chamber="house", committee="hsju00", subcommittee="HSJU03", theme="dark"
        )
    )
    body = resp.body.decode()
    assert resp.media_type == "text/html"
    assert body.lstrip().startswith("<style>")
    assert not body.lstrip().startswith("{")
    assert 'src="https://x/J000289.jpg"' in body
    assert "#c0392b" in body


def test_how_to_use_returns_markdown():
    """Each known note key returns its Markdown text; unknown keys return ''."""
    bills = asyncio.run(router.how_to_use(note="bills"))
    assert bills.startswith("## How To Use")
    assert "Bill ID" in bills

    amendments = asyncio.run(router.how_to_use(note="amendments"))
    assert "Amendment ID" in amendments

    members = asyncio.run(router.how_to_use(note="members"))
    assert "Bioguide ID" in members

    assert asyncio.run(router.how_to_use(note="does_not_exist")) == ""


def test_member_choices(monkeypatch):
    """member_choices builds 'Name (P-State[-district])' labels, filtered by chamber."""

    async def _load():
        return [
            {
                "id": {"bioguide": "A000055"},
                "name": {"official_full": "Robert B. Aderholt"},
                "terms": [
                    {"type": "rep", "state": "AL", "district": 4, "party": "Republican"}
                ],
            },
            {
                "id": {"bioguide": "C000127"},
                "name": {"official_full": "Maria Cantwell"},
                "terms": [{"type": "sen", "state": "WA", "party": "Democrat"}],
            },
        ]

    monkeypatch.setattr("openbb_congress_gov.utils.bulk.load_members", _load)

    house = asyncio.run(router.member_choices(chamber="house"))
    assert house == [{"label": "Robert B. Aderholt (R-AL-4)", "value": "A000055"}]

    every = asyncio.run(router.member_choices())
    assert {c["value"] for c in every} == {"A000055", "C000127"}
    assert any(c["label"] == "Maria Cantwell (D-WA)" for c in every)


def test_member_choices_empty(monkeypatch):
    """No members yields a single placeholder choice."""

    async def _load():
        return []

    monkeypatch.setattr("openbb_congress_gov.utils.bulk.load_members", _load)
    result = asyncio.run(router.member_choices())
    assert result == [{"label": "No members found.", "value": ""}]


def test_member_info_html_endpoint(monkeypatch):
    """The member_info endpoint returns a raw themed HTML bio card."""

    async def _record(bioguide):
        return {
            "id": {"bioguide": "A000055", "wikipedia": "Robert Aderholt"},
            "name": {"official_full": "Robert B. Aderholt"},
            "bio": {"birthday": "1965-07-22", "gender": "M"},
            "terms": [
                {
                    "type": "rep",
                    "state": "AL",
                    "district": 4,
                    "party": "Republican",
                    "start": "2025-01-03",
                    "end": "2027-01-03",
                }
            ],
        }

    async def _committees(bioguide):
        return [{"committee": "House Appropriations", "title": "Chair"}]

    async def _social():
        return {"A000055": {"twitter": "Robert_Aderholt"}}

    async def _passage(bioguide):
        return {"yea": 282, "nay": 11, "total": 293, "yea_pct": 96.2}

    async def _photo(bioguide):
        return f"https://unitedstates.github.io/images/congress/225x275/{bioguide}.jpg"

    monkeypatch.setattr("openbb_congress_gov.utils.bulk.load_member_record", _record)
    monkeypatch.setattr("openbb_congress_gov.utils.bulk.member_committees", _committees)
    monkeypatch.setattr("openbb_congress_gov.utils.bulk.load_social_media", _social)
    monkeypatch.setattr(
        "openbb_congress_gov.utils.bulk.member_passage_record", _passage
    )
    monkeypatch.setattr("openbb_congress_gov.utils.bulk.member_photo_url", _photo)

    resp = asyncio.run(router.member_info(bioguide_id="A000055", theme="dark"))
    body = resp.body.decode()
    assert resp.media_type == "text/html"
    assert "225x275/A000055.jpg" in body
    assert "en.wikipedia.org/wiki/Robert_Aderholt" in body
    assert " " not in [h for h in re.findall(r'href="([^"]+)"', body)][0]
    assert "#c0392b" in body
    assert "96.2% Yea" in body
