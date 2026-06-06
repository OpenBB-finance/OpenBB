"""Tests for openbb_congress_gov.utils.committees (keyless GovInfo path)."""

import asyncio

from openbb_core.provider.utils import helpers as core_helpers

from openbb_congress_gov.utils import bulk, committees
from openbb_congress_gov.utils.helpers import BillsState

_COMMITTEES_CURRENT = [
    {
        "type": "house",
        "name": "House Committee on the Judiciary",
        "url": "https://judiciary.house.gov",
        "thomas_id": "HSJU",
        "jurisdiction": "Judicial matters.",
        "subcommittees": [
            {"name": "Subcommittee on Courts", "thomas_id": "03"},
            {"name": "", "thomas_id": "99"},
        ],
    }
]

_MEMBERSHIP = {
    "HSJU": [
        {
            "name": "Rep. Chair",
            "party": "majority",
            "rank": 1,
            "title": "Chair",
            "bioguide": "A000001",
        }
    ],
    "HSJU03": [
        {
            "name": "Rep. Sub",
            "party": "minority",
            "rank": 1,
            "title": "Ranking Member",
            "bioguide": "B000002",
        }
    ],
}

_MODS = """<?xml version="1.0" encoding="UTF-8"?>
<mods xmlns="http://www.loc.gov/mods/v3">
  <extension>
    <witness>Jane Doe</witness>
    <witness>John Roe</witness>
    <heldDate>2026-05-04</heldDate>
  </extension>
  <relatedItem type="constituent">
    <identifier>CHRG-119hhrg12345-Wstate</identifier>
    <accessId>CHRG-119hhrg12345-Wstate-DoeJ-20260504</accessId>
    <titleInfo><title>Statement of Jane Doe</title></titleInfo>
  </relatedItem>
  <relatedItem type="constituent">
    <titleInfo><title>No access id here</title></titleInfo>
  </relatedItem>
</mods>"""


def _patch_amake_request(monkeypatch, payload):
    """Patch core_helpers.amake_request to return a fixed payload."""
    calls = {"n": 0}

    async def _fake(url, *args, **kwargs):
        calls["n"] += 1
        return payload

    monkeypatch.setattr(core_helpers, "amake_request", _fake)
    return calls


def _clear_caches():
    """Reset the module-level and BillsState caches between tests."""
    committees._GOVTRACK_DATA_CACHE.clear()
    BillsState().bulk.clear()


def test_system_code_to_thomas_id():
    """Full committees strip '00'; subcommittees keep their suffix; JEC remaps."""
    assert committees._system_code_to_thomas_id("ssaf00") == "SSAF"
    assert committees._system_code_to_thomas_id("ssaf13") == "SSAF13"
    assert committees._system_code_to_thomas_id("jjec00") == "JSEC"


def test_get_committee_members_cold_fetch_and_cache(monkeypatch):
    """A cold fetch caches the membership and a second call reuses it."""
    _clear_caches()
    calls = _patch_amake_request(monkeypatch, _MEMBERSHIP)

    result = asyncio.run(committees.get_committee_members("hsju00"))
    assert result[0]["name"] == "Rep. Chair"
    assert "committee_membership" in committees._GOVTRACK_DATA_CACHE

    again = asyncio.run(committees.get_committee_members("hsju00"))
    assert again[0]["name"] == "Rep. Chair"
    assert calls["n"] == 1


def test_get_committee_members_subcommittee(monkeypatch):
    """A subcommittee thomas_id resolves its own roster."""
    _clear_caches()
    _patch_amake_request(monkeypatch, _MEMBERSHIP)
    result = asyncio.run(committees.get_committee_members("hsju03"))
    assert result[0]["bioguide"] == "B000002"


def test_get_committee_members_non_dict(monkeypatch):
    """A non-dict response yields an empty roster."""
    _clear_caches()
    _patch_amake_request(monkeypatch, ["not", "a", "dict"])
    assert asyncio.run(committees.get_committee_members("hsju00")) == []


def test_get_committee_members_exception(monkeypatch):
    """A request exception yields an empty roster."""
    _clear_caches()

    async def _boom(url, *a, **k):
        raise RuntimeError("net")

    monkeypatch.setattr(core_helpers, "amake_request", _boom)
    assert asyncio.run(committees.get_committee_members("hsju00")) == []


def test_get_committee_members_missing_key(monkeypatch):
    """A thomas_id absent from the data returns an empty list."""
    _clear_caches()
    _patch_amake_request(monkeypatch, {"OTHER": [{"name": "X"}]})
    assert asyncio.run(committees.get_committee_members("hsju00")) == []


def _patch_overview(monkeypatch, members):
    """Patch load_committee_structure + get_committee_members for overview tests."""

    async def _structure():
        return list(_COMMITTEES_CURRENT)

    async def _members(system_code):
        return members

    monkeypatch.setattr(bulk, "load_committee_structure", _structure)
    monkeypatch.setattr(committees, "get_committee_members", _members)


def test_get_committee_overview_parent(monkeypatch):
    """A parent committee populates subcommittees and the named-with-name detail."""
    _patch_overview(monkeypatch, _MEMBERSHIP["HSJU"])
    result = asyncio.run(committees.get_committee_overview("hsju00", "house"))

    detail = result["detail"]
    assert result["chamber"] == "house"
    assert result["system_code"] == "hsju00"
    assert detail["name"] == "House Committee on the Judiciary"
    assert detail["is_subcommittee"] is False
    assert detail["website"] == "https://judiciary.house.gov"
    assert detail["jurisdiction"] == "Judicial matters."
    assert detail["subcommittees"] == [
        {"name": "Subcommittee on Courts", "systemCode": "hsju03"}
    ]
    assert result["members"][0]["name"] == "Rep. Chair"


def test_get_committee_overview_subcommittee(monkeypatch):
    """A subcommittee system code yields is_subcommittee, parent_name, em-dash name."""
    _patch_overview(monkeypatch, _MEMBERSHIP["HSJU03"])
    result = asyncio.run(committees.get_committee_overview("hsju03", "house"))

    detail = result["detail"]
    assert detail["is_subcommittee"] is True
    assert detail["parent_name"] == "House Committee on the Judiciary"
    assert detail["name"] == (
        "House Committee on the Judiciary — Subcommittee on Courts"
    )
    assert detail["subcommittees"] == []


def test_get_committee_overview_unknown_parent(monkeypatch):
    """A code with no matching structure falls back to the upper-cased code."""
    _patch_overview(monkeypatch, [])
    result = asyncio.run(committees.get_committee_overview("zzzz00", "senate"))
    assert result["detail"]["name"] == "ZZZZ00"


def test_get_committee_overview_subcommittee_no_match(monkeypatch):
    """A subcommittee suffix with no match keeps the parent name only."""
    _patch_overview(monkeypatch, [])
    result = asyncio.run(committees.get_committee_overview("hsju77", "house"))
    detail = result["detail"]
    assert detail["is_subcommittee"] is True
    assert detail["name"] == "House Committee on the Judiciary"


def _doc(doc_type, package_id):
    """Build a minimal committee-document record."""
    return {
        "doc_type": doc_type,
        "package_id": package_id,
        "doc_url": f"https://x/{package_id}.pdf",
        "citation": package_id,
        "title": f"Title {package_id}",
        "date": "2026-05-04",
    }


def test_fetch_committee_documents_all_dedupes(monkeypatch):
    """doc_type='all' fans out over four collections and dedupes by package_id."""
    by_type = {
        "report": [_doc("report", "CRPT-1"), _doc("report", "CRPT-1")],
        "publication": [_doc("publication", "CPRT-1")],
        "meeting": [_doc("meeting", "CHRG-1")],
        "legislation": [_doc("legislation", "BILLS-1")],
    }

    async def _search(system_code, doc_type, congress, *, limit=20, offset=0):
        return list(by_type[doc_type])

    monkeypatch.setattr(bulk, "search_committee_docs", _search)
    result = asyncio.run(committees.fetch_committee_documents("hsju00", 119, "all"))
    ids = [d["package_id"] for d in result]
    assert sorted(ids) == ["BILLS-1", "CHRG-1", "CPRT-1", "CRPT-1"]


def test_fetch_committee_documents_single_type(monkeypatch):
    """A single doc_type only searches that collection."""
    seen_types = []

    async def _search(system_code, doc_type, congress, *, limit=20, offset=0):
        seen_types.append(doc_type)
        return [_doc(doc_type, "CRPT-9")]

    monkeypatch.setattr(bulk, "search_committee_docs", _search)
    result = asyncio.run(committees.fetch_committee_documents("hsju00", 119, "report"))
    assert seen_types == ["report"]
    assert result[0]["package_id"] == "CRPT-9"


def _patch_docs(monkeypatch, docs):
    """Patch fetch_committee_documents to return a canned docs list."""

    async def _fetch(system_code, congress, doc_type, limit=20):
        return list(docs)

    monkeypatch.setattr(committees, "fetch_committee_documents", _fetch)


def test_get_committee_doc_choices_empty_workspace(monkeypatch):
    """No documents in workspace mode returns a placeholder choice."""
    _patch_docs(monkeypatch, [])
    result = asyncio.run(
        committees.get_committee_doc_choices("hsju00", 119, is_workspace=True)
    )
    assert result == [{"label": "No documents found for this committee.", "value": ""}]


def test_get_committee_doc_choices_empty_non_workspace(monkeypatch):
    """No documents outside workspace mode returns an empty list."""
    _patch_docs(monkeypatch, [])
    result = asyncio.run(committees.get_committee_doc_choices("hsju00", 119))
    assert result == []


def test_get_committee_doc_choices_non_workspace_returns_docs(monkeypatch):
    """Outside workspace mode the raw docs list is returned unchanged."""
    docs = [_doc("report", "CRPT-1")]
    _patch_docs(monkeypatch, docs)
    result = asyncio.run(committees.get_committee_doc_choices("hsju00", 119))
    assert result == docs


def test_get_committee_doc_choices_workspace_report(monkeypatch):
    """Workspace report choices carry one label/value per document."""
    _patch_docs(monkeypatch, [_doc("report", "CRPT-1")])
    result = asyncio.run(
        committees.get_committee_doc_choices(
            "hsju00", 119, doc_type="report", is_workspace=True
        )
    )
    assert len(result) == 1
    assert result[0]["value"] == "https://x/CRPT-1.pdf"
    assert "CRPT-1" in result[0]["label"]
    assert "2026-05-04" in result[0]["label"]


def test_get_committee_doc_choices_workspace_report_no_citation_no_date(monkeypatch):
    """A workspace report with no citation/date falls back to the title label."""
    doc = _doc("report", "CRPT-2")
    doc["citation"] = None
    doc["date"] = None
    _patch_docs(monkeypatch, [doc])
    result = asyncio.run(
        committees.get_committee_doc_choices(
            "hsju00", 119, doc_type="report", is_workspace=True
        )
    )
    assert result[0]["label"] == "Title CRPT-2"


def test_get_committee_doc_choices_workspace_meeting_with_mods(monkeypatch):
    """Workspace meeting choices append constituent granule documents from MODS."""
    _patch_docs(monkeypatch, [_doc("meeting", "CHRG-1")])

    async def _mods(package_id):
        return _MODS.encode("utf-8")

    monkeypatch.setattr(bulk, "fetch_package_mods", _mods)

    result = asyncio.run(
        committees.get_committee_doc_choices(
            "hsju00", 119, doc_type="meeting", is_workspace=True
        )
    )
    values = [c["value"] for c in result]
    assert "https://x/CHRG-1.pdf" in values
    assert any(v.endswith("Wstate-DoeJ-20260504.pdf") for v in values)
    assert any("Statement of Jane Doe" in c["label"] for c in result)


def test_get_committee_doc_choices_workspace_meeting_dedupes_granules(monkeypatch):
    """An accompanying granule already seen across meetings is added only once."""
    _patch_docs(monkeypatch, [_doc("meeting", "CHRG-1"), _doc("meeting", "CHRG-1")])

    async def _mods(package_id):
        return _MODS.encode("utf-8")

    monkeypatch.setattr(bulk, "fetch_package_mods", _mods)

    result = asyncio.run(
        committees.get_committee_doc_choices(
            "hsju00", 119, doc_type="meeting", is_workspace=True
        )
    )
    granule_values = [
        c["value"] for c in result if c["value"].endswith("Wstate-DoeJ-20260504.pdf")
    ]
    assert len(granule_values) == 1


_MC_MEMBERS = [
    {"name": "Rep. Member", "title": "Member", "bioguide": "M001"},
    {"name": "Rep. Chair", "title": "Chair", "bioguide": "C001"},
    {"name": "Rep. Ranking", "title": "Ranking Member", "bioguide": "R001"},
    {"name": "No Photo", "title": "Member", "bioguide": "ZZZ"},
]
_MC_LEG = {
    "C001": {
        "party": "Republican",
        "state": "OH",
        "birthday": "1964-02-17",
        "photo_url": "https://x/C001.jpg",
    },
    "R001": {
        "party": "Democrat",
        "state": "MD",
        "birthday": "1955-11-03",
        "photo_url": "https://x/R001.jpg",
    },
    "M001": {
        "party": "Independent",
        "state": "VT",
        "birthday": "",
        "photo_url": "https://x/M001.jpg",
    },
}


def test_render_member_cards_themes_and_parties():
    """Cards render party colors, photos, initials fallback, sorting, and themes."""
    from openbb_congress_gov.utils.member_cards import render_member_cards

    dark = render_member_cards(_MC_MEMBERS, _MC_LEG, "dark")
    assert "#1b1f27" in dark
    assert "#c0392b" in dark and "#2563c9" in dark and "#6b7280" in dark
    assert 'src="https://x/C001.jpg"' in dark
    assert "initials" in dark
    assert "Age " in dark
    assert (
        dark.index("Rep. Chair")
        < dark.index("Rep. Ranking")
        < dark.index("Rep. Member")
    )

    light = render_member_cards(_MC_MEMBERS, _MC_LEG, "light")
    assert "#ffffff" in light and light != dark


def test_render_member_cards_empty():
    """No members renders the empty-state message."""
    from openbb_congress_gov.utils.member_cards import render_member_cards

    assert "No member data available" in render_member_cards([], {}, None)


def test_member_cards_age():
    """_age computes whole years and tolerates missing/invalid birthdays."""
    from datetime import date

    from openbb_congress_gov.utils.member_cards import _age

    today = date(2026, 6, 4)
    assert _age("1964-02-17", today) == 62
    assert _age("1964-12-25", today) == 61
    assert _age("", today) is None
    assert _age("not-a-date", today) is None


_BIO_RECORD = {
    "id": {"bioguide": "A000055", "wikipedia": "Robert Aderholt", "govtrack": 400004},
    "name": {"official_full": "Robert B. Aderholt"},
    "bio": {"birthday": "1965-07-22", "gender": "M"},
    "terms": [
        {
            "type": "rep",
            "state": "AL",
            "district": 4,
            "party": "Republican",
            "start": "1997-01-07",
            "end": "1999-01-03",
        },
        {
            "type": "rep",
            "state": "AL",
            "district": 4,
            "party": "Republican",
            "start": "2025-01-03",
            "end": "2027-01-03",
            "url": "https://aderholt.house.gov",
            "phone": "202-225-4876",
            "office": "266 Cannon",
            "contact_form": "https://x/c",
        },
    ],
}


def test_render_member_bio_full():
    """The bio card includes the photo, encoded links, social, committees, terms."""
    import re

    from openbb_congress_gov.utils.member_cards import render_member_bio

    html = render_member_bio(
        _BIO_RECORD,
        [{"committee": "House Appropriations", "title": "Chair"}],
        {"twitter": "Robert_Aderholt"},
        {"yea": 282, "nay": 11, "total": 293, "yea_pct": 96.2},
        "dark",
        "https://unitedstates.github.io/images/congress/225x275/A000055.jpg",
    )
    assert "225x275/A000055.jpg" in html
    assert "Robert B. Aderholt" in html
    assert "Representative · AL-4 · Republican" in html
    assert "Age " in html
    assert "en.wikipedia.org/wiki/Robert_Aderholt" in html
    assert all(" " not in h for h in re.findall(r'href="([^"]+)"', html))
    assert "On Passage" in html and "282 Yea" in html and "96.2% Yea" in html
    assert "Committee Assignments" in html and "Chair" in html
    assert "Term History" in html and "1997-01-07" in html
    assert "#c0392b" in html


def test_render_member_bio_minimal_and_theme():
    """A sparse record (no photo/links/committees) renders with initials + light theme."""
    from openbb_congress_gov.utils.member_cards import render_member_bio

    record = {
        "id": {},
        "name": {"first": "Jane", "last": "Doe"},
        "bio": {},
        "terms": [{"type": "sen", "state": "TX", "party": "Independent"}],
    }
    empty_voting = {"yea": 0, "nay": 0, "total": 0, "yea_pct": None}
    light = render_member_bio(record, [], {}, empty_voting, "light")
    dark = render_member_bio(record, [], {}, empty_voting, "dark")
    assert "color:#1b1f27" in light and light != dark
    assert "initials" in light and ">JD<" in light
    assert "Committee Assignments" not in light
    assert "Social" not in light
    assert "Senator · TX · Independent" in light
    assert "No On-Passage roll-call votes on record." in light
