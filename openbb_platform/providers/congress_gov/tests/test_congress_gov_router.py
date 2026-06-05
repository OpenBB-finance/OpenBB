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


def test_document_viewer_empty_workspace():
    """An empty package id in workspace mode returns a placeholder choice."""
    result = asyncio.run(router.mandated_report_urls(package_id="", is_workspace=True))
    assert result[0]["value"] == ""


def test_document_viewer_empty_raises():
    """An empty package id outside workspace raises an HTTPException."""
    with pytest.raises(HTTPException):
        asyncio.run(router.mandated_report_urls(package_id=""))


def test_law_text_urls_resolves_by_law_id():
    """The law viewer reconstructs the PLAW package id from law_id + law_type."""
    ws = asyncio.run(
        router.law_text_urls(law_id="119-1", law_type="public", is_workspace=True)
    )
    assert ws[0]["value"].endswith("/PLAW-119publ1/pdf/PLAW-119publ1.pdf")
    priv = asyncio.run(router.law_text_urls(law_id="119-2", law_type="private"))
    assert priv[0]["package_id"] == "PLAW-119pvtl2"


def test_law_text_urls_empty_workspace_and_raises():
    """A missing/invalid law_id returns a placeholder (workspace) or raises."""
    assert (
        asyncio.run(router.law_text_urls(law_id="", is_workspace=True))[0]["value"]
        == ""
    )
    with pytest.raises(HTTPException):
        asyncio.run(
            router.law_text_urls(law_id="not-a-law-id-without-dash".replace("-", ""))
        )


def test_calendar_urls_resolves_by_date():
    """The calendar viewer reconstructs the package id from chamber + congress + date."""
    ws = asyncio.run(
        router.calendar_urls(
            calendar_date="2026-05-21", chamber="house", congress=119, is_workspace=True
        )
    )
    assert ws[0]["value"].endswith(
        "/CCAL-119hcal-2026-05-21/pdf/CCAL-119hcal-2026-05-21.pdf"
    )
    sen = asyncio.run(
        router.calendar_urls(calendar_date="2026-05-21", chamber="senate", congress=119)
    )
    assert sen[0]["package_id"] == "CCAL-119scal-2026-05-21"


def test_calendar_urls_empty_workspace_and_default_congress():
    """No date returns a placeholder; a missing congress resolves to the current one."""
    assert (
        asyncio.run(router.calendar_urls(calendar_date="", is_workspace=True))[0][
            "value"
        ]
        == ""
    )
    out = asyncio.run(router.calendar_urls(calendar_date="2026-05-21", chamber="house"))
    assert out[0]["package_id"].startswith("CCAL-1")


def test_calendar_urls_empty_raises():
    """No date outside workspace raises an HTTPException."""
    with pytest.raises(HTTPException):
        asyncio.run(router.calendar_urls(calendar_date=""))


def test_preload_bills(monkeypatch):
    """_preload_bills warms BILLSTATUS + BILLSUM for every bill type of the Congress."""
    from openbb_congress_gov.utils.constants import BillTypes

    status_calls: list = []
    sum_calls: list = []

    async def _fake_status(congress, bill_type):
        status_calls.append((congress, bill_type))
        return []

    async def _fake_sum(congress, bill_type):
        sum_calls.append((congress, bill_type))
        return {}

    monkeypatch.setattr("openbb_congress_gov.utils.bulk.load_billstatus", _fake_status)
    monkeypatch.setattr("openbb_congress_gov.utils.bulk.load_billsum", _fake_sum)
    asyncio.run(router._preload_bills())
    assert {bt for _, bt in status_calls} == set(BillTypes)
    assert {bt for _, bt in sum_calls} == set(BillTypes)
    assert all(c >= 119 for c, _ in status_calls)


def test_warm_bills_cache_schedules_task(monkeypatch):
    """_warm_bills_cache schedules the preload coroutine on the running loop."""
    ran: dict = {}

    async def _fake_preload():
        ran["done"] = True

    monkeypatch.setattr(router, "_preload_bills", _fake_preload)

    async def _run():
        router._warm_bills_cache()
        await asyncio.sleep(0)
        await asyncio.sleep(0)

    asyncio.run(_run())
    assert ran.get("done") is True


def test_warm_bills_cache_no_running_loop():
    """Without a running event loop, the warmup is a no-op (no exception)."""
    router._warm_bills_cache()


def test_preload_members(monkeypatch):
    """_preload_members warms reference datasets + Voteview for both chambers."""
    ref: list = []
    vote_calls: list = []

    async def _members():
        ref.append("members")
        return []

    async def _social():
        ref.append("social")
        return {}

    async def _committee_membership():
        ref.append("committee_membership")
        return {}

    async def _committee_structure():
        ref.append("committee_structure")
        return []

    async def _legislators():
        ref.append("legislators")
        return {}

    async def _vv_members(congress, chamber):
        vote_calls.append(("members", congress, chamber))
        return {}

    async def _vv_rollcalls(congress, chamber):
        vote_calls.append(("rollcalls", congress, chamber))
        return {}

    async def _vv_votes(congress, chamber):
        vote_calls.append(("votes", congress, chamber))
        return {}

    status_calls: list = []

    async def _billstatus(congress, bill_type):
        status_calls.append((congress, bill_type))
        return []

    base = "openbb_congress_gov.utils.bulk."
    monkeypatch.setattr(base + "load_members", _members)
    monkeypatch.setattr(base + "load_social_media", _social)
    monkeypatch.setattr(base + "load_committee_membership", _committee_membership)
    monkeypatch.setattr(base + "load_committee_structure", _committee_structure)
    monkeypatch.setattr(base + "load_legislators", _legislators)
    monkeypatch.setattr(base + "load_voteview_members", _vv_members)
    monkeypatch.setattr(base + "load_voteview_rollcalls", _vv_rollcalls)
    monkeypatch.setattr(base + "load_voteview_votes", _vv_votes)
    monkeypatch.setattr(base + "load_billstatus", _billstatus)

    asyncio.run(router._preload_members())

    assert set(ref) == {
        "members",
        "social",
        "committee_membership",
        "committee_structure",
        "legislators",
    }
    assert {ch for _, _, ch in vote_calls} == {"H", "S"}
    congresses = {c for _, c, _ in vote_calls}
    assert 108 in congresses and max(congresses) >= 119
    assert {kind for kind, _, _ in vote_calls} == {"members", "rollcalls", "votes"}

    from openbb_congress_gov.utils.constants import BillTypes

    assert {bt for _, bt in status_calls} == set(BillTypes)
    assert {c for c, _ in status_calls} == congresses


def test_warm_members_cache_schedules_task(monkeypatch):
    """_warm_members_cache schedules the member preload on the running loop."""
    ran: dict = {}

    async def _fake_preload():
        ran["done"] = True

    monkeypatch.setattr(router, "_preload_members", _fake_preload)

    async def _run():
        router._warm_members_cache()
        await asyncio.sleep(0)
        await asyncio.sleep(0)

    asyncio.run(_run())
    assert ran.get("done") is True


def test_warm_members_cache_no_running_loop():
    """Without a running event loop, the member warmup is a no-op."""
    router._warm_members_cache()


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

    monkeypatch.setattr(
        "openbb_congress_gov.utils.committees.get_committee_members", _members
    )
    monkeypatch.setattr("openbb_congress_gov.utils.bulk.load_legislators", _leg)

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

    async def _passage(bioguide, service):
        return {"yea": 282, "nay": 11, "total": 293, "yea_pct": 96.2}

    monkeypatch.setattr("openbb_congress_gov.utils.bulk.load_member_record", _record)
    monkeypatch.setattr("openbb_congress_gov.utils.bulk.member_committees", _committees)
    monkeypatch.setattr("openbb_congress_gov.utils.bulk.load_social_media", _social)
    monkeypatch.setattr(
        "openbb_congress_gov.utils.bulk.member_passage_record", _passage
    )

    resp = asyncio.run(router.member_info(bioguide_id="A000055", theme="dark"))
    body = resp.body.decode()
    assert resp.media_type == "text/html"
    assert "225x275/A000055.jpg" in body
    assert "en.wikipedia.org/wiki/Robert_Aderholt" in body
    assert " " not in [h for h in re.findall(r'href="([^"]+)"', body)][0]
    assert "#c0392b" in body
    assert "96.2% Yea" in body
