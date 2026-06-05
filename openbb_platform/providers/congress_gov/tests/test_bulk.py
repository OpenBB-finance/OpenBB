"""Tests for openbb_congress_gov.utils.bulk (GovInfo bulk-data path)."""

import asyncio
import io
import json
import os
import zipfile
from datetime import date

import pytest
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.utils import helpers as core_helpers

from openbb_congress_gov.utils import bulk
from openbb_congress_gov.utils.helpers import BillsState

# ---------------------------------------------------------------------------
# Synthetic XML fixtures
# ---------------------------------------------------------------------------

_BILLSTATUS_29 = """<billStatus><bill>
  <number>29</number><congress>119</congress><type>HR</type>
  <originChamber>House</originChamber><originChamberCode>H</originChamberCode>
  <introducedDate>2025-01-03</introducedDate>
  <updateDate>2025-11-30T06:37:21Z</updateDate>
  <updateDateIncludingText>2025-11-30T06:37:21Z</updateDateIncludingText>
  <title>Laken Riley Act</title>
  <latestAction><actionDate>2025-02-10</actionDate><text>Read the second time.</text></latestAction>
  <policyArea><name>Immigration</name></policyArea>
  <sponsors><item><bioguideId>C001129</bioguideId><fullName>Rep. Collins</fullName></item></sponsors>
  <cosponsors><item><fullName>Rep. Allen</fullName><isOriginalCosponsor>True</isOriginalCosponsor><sponsorshipDate>2025-01-03</sponsorshipDate></item></cosponsors>
  <actions><item><actionDate>2025-02-10</actionDate><text>Read.</text><type>Calendars</type></item></actions>
  <committees><item><systemCode>hsju00</systemCode><name>Judiciary Committee</name><chamber>House</chamber><type>Standing</type></item></committees>
  <relatedBills><item><title>Companion</title><congress>119</congress><number>5</number><type>S</type></item></relatedBills>
  <subjects><legislativeSubjects><item><name>Border security</name><updateDate>2025-01-08T19:36:54Z</updateDate></item></legislativeSubjects><policyArea><name>Immigration</name></policyArea></subjects>
  <titles><item><titleType>Short Title</titleType><title>Laken Riley Act</title><chamberName>Senate</chamberName><billTextVersionName>Introduced</billTextVersionName><updateDate>2025-02-12T02:53:16Z</updateDate></item><item><title>No Type Title</title></item></titles>
  <summaries><summary><versionCode>00</versionCode><actionDate>2025-01-03</actionDate><actionDesc>Introduced in House</actionDesc><updateDate>2025-01-13T16:36:38Z</updateDate><cdata><text>&lt;p&gt;&lt;strong&gt;Laken Riley Act&lt;/strong&gt;&lt;/p&gt;&lt;p&gt;This bill.&lt;/p&gt;</text></cdata></summary></summaries>
  <textVersions><item><type>Introduced in House</type><date>2025-01-03T05:00:00Z</date><formats><item><url>https://www.govinfo.gov/content/pkg/BILLS-119hr29ih/xml/BILLS-119hr29ih.xml</url></item></formats></item></textVersions>
  <amendments>
    <amendment>
      <number>10</number><congress>119</congress><type>HAMDT</type>
      <description>An amendment in the nature of a substitute.</description><purpose>To amend.</purpose>
      <chamber>House of Representatives</chamber>
      <updateDate>2025-02-09T08:00:00Z</updateDate>
      <proposedDate>2025-02-08T05:00:00Z</proposedDate>
      <submittedDate>2025-02-08T05:00:00Z</submittedDate>
      <latestAction><actionDate>2025-02-09</actionDate><actionTime>10:00</actionTime><text>Agreed.</text></latestAction>
      <sponsors><item><fullName>Rep. Collins</fullName></item></sponsors>
      <cosponsors><item><fullName>Rep. Allen</fullName></item></cosponsors>
      <actions><actions><item><actionDate>2025-02-09</actionDate><text>Agreed.</text><type>X</type></item></actions></actions>
      <links><link><name>House Report 119-1</name><url>https://www.congress.gov/x</url></link></links>
      <amendedBill><congress>119</congress><type>HR</type><number>29</number><title>Laken Riley Act</title></amendedBill>
    </amendment>
    <amendment>
      <number>11</number><congress>119</congress><type>SAMDT</type>
      <description>Senate amendment.</description>
      <updateDate>2025-02-11T08:00:00Z</updateDate>
      <latestAction><actionDate>2025-02-11</actionDate><text>Submitted.</text></latestAction>
      <amendedAmendment><congress>119</congress><type>HAMDT</type><number>10</number></amendedAmendment>
    </amendment>
  </amendments>
</bill></billStatus>"""

_BILLSTATUS_5 = """<billStatus><bill>
  <number>5</number><congress>119</congress><type>HR</type>
  <originChamber>House</originChamber><originChamberCode>H</originChamberCode>
  <introducedDate>2025-03-01</introducedDate>
  <updateDate>2025-03-15T00:00:00Z</updateDate>
  <updateDateIncludingText>2025-03-15T00:00:00Z</updateDateIncludingText>
  <title>Other Act</title>
  <latestAction><actionDate>2025-03-20</actionDate><text>Passed House.</text></latestAction>
  <policyArea><name>Health</name></policyArea>
  <sponsors><item><fullName>Rep. Smith</fullName></item></sponsors>
</bill></billStatus>"""

# A member with no <bill> element (covers the `bill is None` continue branch).
_BILLSTATUS_NO_BILL = "<billStatus><notabill/></billStatus>"

_BILLSUM_29 = """<BillSummaries><item><title>Laken Riley Act</title>
  <summary><action-date>2025-01-03</action-date><action-desc>Introduced in House</action-desc><summary-text>&lt;p&gt;&lt;strong&gt;Laken Riley Act&lt;/strong&gt;&lt;/p&gt;CRS summary.</summary-text></summary>
</item>
<item><title>No summary item</title></item></BillSummaries>"""


def _zip_bytes(members: dict[str, str]) -> bytes:
    """Build an in-memory ZIP archive from ``{member_name: text}``."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as archive:
        for name, text in members.items():
            archive.writestr(name, text)
    return buf.getvalue()


def _billstatus_zip() -> bytes:
    """Return a BILLSTATUS ZIP with two bills, a non-bill member, and a non-XML file."""
    return _zip_bytes(
        {
            "BILLSTATUS-119hr29.xml": _BILLSTATUS_29,
            "BILLSTATUS-119hr5.xml": _BILLSTATUS_5,
            "BILLSTATUS-119hr7.xml": _BILLSTATUS_NO_BILL,
            "README.txt": "ignored non-xml member",
        }
    )


def _billsum_zip() -> bytes:
    """Return a BILLSUM ZIP with one summarized bill and a non-matching member."""
    return _zip_bytes(
        {
            "BILLSUM-119hr29.xml": _BILLSUM_29,
            "notamatch.txt": "ignored",
        }
    )


# ---------------------------------------------------------------------------
# bulk_zip_url / parse_bill_ref
# ---------------------------------------------------------------------------


def test_bulk_zip_url():
    """bulk_zip_url builds the canonical GovInfo bulk ZIP URL."""
    url = bulk.bulk_zip_url("BILLSTATUS", 119, "HR")
    assert url == (
        "https://www.govinfo.gov/bulkdata/BILLSTATUS/119/hr/BILLSTATUS-119-hr.zip"
    )


def test_parse_bill_ref_ok():
    """Dash id, shorthand, leading-slash, and full-URL references parse correctly."""
    assert bulk.parse_bill_ref("119-hr-29") == (119, "hr", 29)
    assert bulk.parse_bill_ref("119-HR-29") == (119, "hr", 29)
    assert bulk.parse_bill_ref("119/hr/29") == (119, "hr", 29)
    assert bulk.parse_bill_ref("/119/HR/29") == (119, "hr", 29)
    # A full API URL anchors on ``/bill/`` rather than the ``v3`` digits.
    assert bulk.parse_bill_ref(
        "https://api.congress.gov/v3/bill/119/s/1947?format=json"
    ) == (119, "s", 1947)


def test_parse_bill_ref_raises():
    """An unparseable reference raises OpenBBError."""
    with pytest.raises(OpenBBError, match="Could not parse"):
        bulk.parse_bill_ref("not-a-bill")


# ---------------------------------------------------------------------------
# _cache_dir / _text
# ---------------------------------------------------------------------------


def test_cache_dir(monkeypatch, tmp_path):
    """_cache_dir builds and creates the bulkdata cache path under the user cache."""
    from openbb_core.app import utils as core_utils

    monkeypatch.setattr(core_utils, "get_user_cache_directory", lambda: str(tmp_path))
    path = bulk._cache_dir()
    assert path == f"{tmp_path}/congress_gov/bulkdata"
    assert os.path.isdir(path)


def test_text_empty_self_closing():
    """_text returns an empty string when the found node has no text."""
    from defusedxml.ElementTree import fromstring

    root = fromstring("<bill><title/></bill>")
    assert bulk._text(root, "title") == ""
    assert bulk._text(root, "missing") == ""


# ---------------------------------------------------------------------------
# parse_billstatus / _billstatus_record
# ---------------------------------------------------------------------------


def test_parse_billstatus_all_blocks():
    """parse_billstatus maps every nested block from the BILLSTATUS XML."""
    records = bulk.parse_billstatus(_billstatus_zip())
    by_number = {r["number"]: r for r in records}
    assert set(by_number) == {29, 5}

    rec = by_number[29]
    assert rec["congress"] == 119
    assert rec["type"] == "HR"
    assert rec["bill_id"] == "119-hr-29"
    assert rec["originChamber"] == "House"
    assert rec["originChamberCode"] == "H"
    assert rec["title"] == "Laken Riley Act"
    assert rec["introducedDate"] == "2025-01-03"
    assert rec["latestAction"] == {
        "actionDate": "2025-02-10",
        "text": "Read the second time.",
    }
    assert rec["policyArea"] == {"name": "Immigration"}
    assert rec["sponsors"][0]["fullName"] == "Rep. Collins"
    # isOriginalCosponsor coerced to a bool.
    assert rec["cosponsors"][0]["isOriginalCosponsor"] is True
    assert rec["actions"][0]["type"] == "Calendars"
    assert rec["committees"][0]["systemCode"] == "hsju00"
    assert rec["relatedBills"][0]["number"] == "5"
    assert rec["subjects"][0]["name"] == "Border security"
    # titleType is mapped onto `type`; a title without titleType falls back to "".
    assert rec["titles"][0]["type"] == "Short Title"
    assert rec["titles"][1]["type"] == ""
    # Summary cdata/text is read.
    assert "Laken Riley Act" in rec["summaries"][0]["text"]
    assert rec["summaries"][0]["versionCode"] == "00"
    # textVersions are parsed with their format URLs.
    assert rec["textVersions"][0]["type"] == "Introduced in House"
    assert rec["textVersions"][0]["formats"][0]["url"].endswith(
        "/BILLS-119hr29ih/xml/BILLS-119hr29ih.xml"
    )


def test_derive_text_formats():
    """derive_text_formats builds pdf/htm/xml URLs from the package id."""
    version = {
        "type": "Introduced in House",
        "date": "2025-01-03T05:00:00Z",
        "formats": [
            {
                "url": "https://www.govinfo.gov/content/pkg/BILLS-119hr29ih/xml/BILLS-119hr29ih.xml"
            }
        ],
    }
    out = bulk.derive_text_formats(version)
    assert out["version_type"] == "Introduced in House"
    assert out["pdf"].endswith("/content/pkg/BILLS-119hr29ih/pdf/BILLS-119hr29ih.pdf")
    assert out["htm"].endswith("/content/pkg/BILLS-119hr29ih/html/BILLS-119hr29ih.htm")
    assert out["xml"].endswith("/content/pkg/BILLS-119hr29ih/xml/BILLS-119hr29ih.xml")


def test_derive_text_formats_no_package():
    """derive_text_formats returns None when no package id can be found."""
    # No formats at all.
    assert bulk.derive_text_formats({"formats": []}) is None
    # A URL that is not a GovInfo content-package link.
    assert (
        bulk.derive_text_formats({"formats": [{"url": "https://example.com/x"}]})
        is None
    )


# ---------------------------------------------------------------------------
# parse_billsum
# ---------------------------------------------------------------------------


def test_parse_billsum():
    """parse_billsum keys summaries by the bill number from the member filename."""
    out = bulk.parse_billsum(_billsum_zip())
    assert set(out) == {29}
    assert out[29][0]["actionDate"] == "2025-01-03"
    assert "CRS summary" in out[29][0]["text"]


# ---------------------------------------------------------------------------
# to_list_item
# ---------------------------------------------------------------------------


def test_to_list_item():
    """to_list_item projects a record to the slim list shape and truncates the date."""
    rec = bulk.parse_billstatus(_billstatus_zip())[0]
    item = bulk.to_list_item(rec)
    assert len(item["updateDate"]) == 10
    assert item["bill_id"] == rec["bill_id"]
    assert item["latestAction"] == rec["latestAction"]


def test_to_list_item_missing_fields():
    """to_list_item tolerates a record missing updateDate and latestAction."""
    item = bulk.to_list_item({})
    assert item["updateDate"] == ""
    assert item["latestAction"] == {}


# ---------------------------------------------------------------------------
# filter_bills
# ---------------------------------------------------------------------------

_FILTER_RECORDS = [
    {
        "number": 1,
        "updateDate": "2025-01-10T00:00:00Z",
        "latestAction": {"actionDate": "2025-01-10"},
    },
    {
        "number": 2,
        "updateDate": "2025-02-20T00:00:00Z",
        "latestAction": {"actionDate": "2025-02-20"},
    },
    {
        "number": 3,
        "updateDate": "2025-03-30T00:00:00Z",
        "latestAction": {},
    },
]


def test_filter_bills_window_and_sort_desc():
    """A start/end window filters records and desc sort orders newest first."""
    out = bulk.filter_bills(
        _FILTER_RECORDS,
        start_date=date(2025, 1, 15),
        end_date=date(2025, 3, 1),
        sort_by="desc",
    )
    assert [r["number"] for r in out] == [2]


def test_filter_bills_sort_asc():
    """Ascending sort orders oldest first; missing actionDate falls back to updateDate."""
    out = bulk.filter_bills(_FILTER_RECORDS, sort_by="asc")
    assert [r["number"] for r in out] == [1, 2, 3]


def test_filter_bills_offset_and_limit():
    """offset skips records and a positive limit caps the result."""
    out = bulk.filter_bills(_FILTER_RECORDS, sort_by="asc", offset=1, limit=1)
    assert [r["number"] for r in out] == [2]


def test_filter_bills_limit_none_caps_at_100():
    """limit=None caps the output at 100 records."""
    records = [{"number": i, "updateDate": "2025-01-01"} for i in range(150)]
    out = bulk.filter_bills(records, limit=None)
    assert len(out) == 100


def test_filter_bills_limit_zero_no_cap():
    """limit=0 returns all records uncapped."""
    records = [{"number": i, "updateDate": "2025-01-01"} for i in range(150)]
    out = bulk.filter_bills(records, limit=0)
    assert len(out) == 150


# ---------------------------------------------------------------------------
# Fake aiohttp session for _download_zip / load_* tests
# ---------------------------------------------------------------------------


class _FakeResponse:
    """Settable stand-in for an aiohttp response."""

    def __init__(self, status=200, headers=None, body=b"", raise_exc=None):
        self.status = status
        self.headers = headers or {}
        self._body = body
        self._raise_exc = raise_exc

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        return False

    async def read(self):
        """Return the canned body."""
        return self._body

    def raise_for_status(self):
        """Raise the configured error, if any."""
        if self._raise_exc is not None:
            raise self._raise_exc


class _FakeSession:
    """Fake aiohttp.ClientSession yielding a fixed response (or raising on get)."""

    def __init__(self, response=None, get_exc=None):
        self._response = response
        self._get_exc = get_exc
        self.requested_headers = None

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        return False

    def get(self, url, headers=None, **kwargs):
        """Return the canned response context manager (or raise)."""
        self.requested_headers = headers
        self.requested_url = url
        if self._get_exc is not None:
            raise self._get_exc
        return self._response


def _patch_session(monkeypatch, **kwargs):
    """Patch aiohttp.ClientSession to construct the supplied fake session."""
    import aiohttp

    session = _FakeSession(**kwargs)
    monkeypatch.setattr(aiohttp, "ClientSession", lambda *a, **k: session)
    return session


@pytest.fixture
def _cache(monkeypatch, tmp_path):
    """Point bulk._cache_dir at a temporary directory."""
    monkeypatch.setattr(bulk, "_cache_dir", lambda: str(tmp_path))
    return str(tmp_path)


# ---------------------------------------------------------------------------
# _download_zip
# ---------------------------------------------------------------------------


def test_download_zip_cold_200(monkeypatch, _cache):
    """A cold 200 response writes the zip and meta file and reports changed=True."""
    body = _billstatus_zip()
    resp = _FakeResponse(
        status=200,
        headers={"ETag": "etag-1", "Last-Modified": "yesterday"},
        body=body,
    )
    _patch_session(monkeypatch, response=resp)

    content, changed = asyncio.run(bulk._download_zip("BILLSTATUS", 119, "HR"))
    assert content == body
    assert changed is True

    zip_path = os.path.join(_cache, "BILLSTATUS-119-hr.zip")
    meta_path = zip_path + ".meta.json"
    assert os.path.exists(zip_path)
    with open(meta_path, encoding="utf-8") as f:
        meta = json.load(f)
    assert meta == {"etag": "etag-1", "last_modified": "yesterday"}


def test_download_zip_304_returns_cached(monkeypatch, _cache):
    """A 304 with a cached zip on disk returns the cached bytes and changed=False."""
    body = _billstatus_zip()
    zip_path = os.path.join(_cache, "BILLSTATUS-119-hr.zip")
    with open(zip_path, "wb") as f:
        f.write(body)
    meta_path = zip_path + ".meta.json"
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump({"etag": "etag-1", "last_modified": "yesterday"}, f)

    resp = _FakeResponse(status=304)
    session = _patch_session(monkeypatch, response=resp)

    content, changed = asyncio.run(bulk._download_zip("BILLSTATUS", 119, "HR"))
    assert content == body
    assert changed is False
    # Conditional headers were sent from the meta file.
    assert session.requested_headers["If-None-Match"] == "etag-1"
    assert session.requested_headers["If-Modified-Since"] == "yesterday"


def test_download_zip_exception_with_cache(monkeypatch, _cache):
    """A network error with a cached zip returns the cached bytes and changed=False."""
    body = _billstatus_zip()
    zip_path = os.path.join(_cache, "BILLSTATUS-119-hr.zip")
    with open(zip_path, "wb") as f:
        f.write(body)

    _patch_session(monkeypatch, get_exc=RuntimeError("network down"))

    content, changed = asyncio.run(bulk._download_zip("BILLSTATUS", 119, "HR"))
    assert content == body
    assert changed is False


def test_download_zip_exception_no_cache(monkeypatch, _cache):
    """A network error with no cached zip raises OpenBBError."""
    _patch_session(monkeypatch, get_exc=RuntimeError("network down"))
    with pytest.raises(OpenBBError, match="Failed to download data"):
        asyncio.run(bulk._download_zip("BILLSTATUS", 119, "HR"))


# ---------------------------------------------------------------------------
# load_billstatus / load_billsum (cold parse + in-memory reuse)
# ---------------------------------------------------------------------------


def test_load_billstatus_cold_and_reuse(monkeypatch):
    """load_billstatus parses when changed and reuses the cache when unchanged."""
    BillsState().bulk.clear()
    body = _billstatus_zip()

    calls = {"n": 0}

    async def _changed(collection, congress, bill_type):
        calls["n"] += 1
        return body, True

    monkeypatch.setattr(bulk, "_download_zip", _changed)
    records = asyncio.run(bulk.load_billstatus(119, "hr"))
    assert {r["number"] for r in records} == {29, 5}
    assert calls["n"] == 1

    parse_calls = {"n": 0}
    real_parse = bulk.parse_billstatus

    def _counting_parse(zip_bytes):
        parse_calls["n"] += 1
        return real_parse(zip_bytes)

    monkeypatch.setattr(bulk, "parse_billstatus", _counting_parse)

    async def _unchanged(collection, congress, bill_type):
        return body, False

    monkeypatch.setattr(bulk, "_download_zip", _unchanged)
    cached = asyncio.run(bulk.load_billstatus(119, "HR"))
    assert cached is records
    # Not re-parsed because nothing changed and a cached copy exists.
    assert parse_calls["n"] == 0


def test_load_billsum_cold_and_reuse(monkeypatch):
    """load_billsum parses when changed and reuses the cache when unchanged."""
    BillsState().bulk.clear()
    body = _billsum_zip()

    async def _changed(collection, congress, bill_type):
        return body, True

    monkeypatch.setattr(bulk, "_download_zip", _changed)
    summaries = asyncio.run(bulk.load_billsum(119, "hr"))
    assert set(summaries) == {29}

    async def _unchanged(collection, congress, bill_type):
        return body, False

    monkeypatch.setattr(bulk, "_download_zip", _unchanged)
    cached = asyncio.run(bulk.load_billsum(119, "hr"))
    assert cached is summaries


# ---------------------------------------------------------------------------
# load_bill_record
# ---------------------------------------------------------------------------


def test_load_bill_record_found_with_summary_merge(monkeypatch):
    """load_bill_record finds the record and merges in BILLSUM summaries."""
    BillsState().bulk.clear()

    async def _status(congress, bill_type):
        return bulk.parse_billstatus(_billstatus_zip())

    async def _sum(congress, bill_type):
        return bulk.parse_billsum(_billsum_zip())

    monkeypatch.setattr(bulk, "load_billstatus", _status)
    monkeypatch.setattr(bulk, "load_billsum", _sum)

    record = asyncio.run(bulk.load_bill_record("119/hr/29"))
    assert record["number"] == 29
    # Summaries replaced by the BILLSUM (CRS) summaries.
    assert "CRS summary" in record["summaries"][0]["text"]


def test_load_bill_record_found_no_summary(monkeypatch):
    """A bill with no matching BILLSUM keeps its BILLSTATUS summaries."""
    BillsState().bulk.clear()

    async def _status(congress, bill_type):
        return bulk.parse_billstatus(_billstatus_zip())

    async def _sum(congress, bill_type):
        return {}

    monkeypatch.setattr(bulk, "load_billstatus", _status)
    monkeypatch.setattr(bulk, "load_billsum", _sum)

    record = asyncio.run(bulk.load_bill_record("119/hr/5"))
    assert record["number"] == 5


def test_load_bill_record_not_found(monkeypatch):
    """A missing bill number raises OpenBBError."""
    BillsState().bulk.clear()

    async def _status(congress, bill_type):
        return bulk.parse_billstatus(_billstatus_zip())

    monkeypatch.setattr(bulk, "load_billstatus", _status)
    with pytest.raises(OpenBBError, match="Bill not found in bulk data"):
        asyncio.run(bulk.load_bill_record("119/hr/999"))


# ---------------------------------------------------------------------------
# PLAW: parse_plaw / load_plaw / filter_laws
# ---------------------------------------------------------------------------

_PLAW_1 = """<uslm xmlns="http://xml.house.gov/schemas/uslm/1.0" xmlns:dc="http://purl.org/dc/elements/1.1/">
  <meta>
    <dc:title>Public Law 119-1: To require the Secretary to act.</dc:title>
    <dc:type>Public Law</dc:type>
    <docNumber>1</docNumber>
    <citableAs>Public Law 119-1</citableAs>
    <citableAs>139 Stat. 3</citableAs>
    <approvedDate>2025-01-29</approvedDate>
    <congress>119</congress>
    <publicPrivate>public</publicPrivate>
  </meta>
</uslm>"""

# A law whose title has no "PL nnn: " prefix, and only one citableAs.
_PLAW_2 = """<uslm xmlns:dc="http://purl.org/dc/elements/1.1/">
  <meta>
    <dc:title>A short title with no prefix</dc:title>
    <docNumber>2</docNumber>
    <citableAs>Public Law 119-2</citableAs>
    <approvedDate>2025-02-15</approvedDate>
    <congress>119</congress>
    <publicPrivate>public</publicPrivate>
  </meta>
</uslm>"""

# A member without a <meta> element (covers the skip branch).
_PLAW_NO_META = "<uslm><main/></uslm>"


def _plaw_zip() -> bytes:
    """Return a PLAW ZIP with two laws, a meta-less member, and a non-XML file."""
    return _zip_bytes(
        {
            "PLAW-119publ1.xml": _PLAW_1,
            "PLAW-119publ2.xml": _PLAW_2,
            "PLAW-119publ9.xml": _PLAW_NO_META,
            "README.txt": "ignored",
        }
    )


def test_parse_plaw():
    """parse_plaw maps the USLM meta header and derives package text URLs."""
    records = bulk.parse_plaw(_plaw_zip())
    by_number = {r["law_number"]: r for r in records}
    assert set(by_number) == {1, 2}

    rec = by_number[1]
    assert rec["law_id"] == "119-1"
    assert rec["law_type"] == "public"
    assert rec["title"] == "To require the Secretary to act."
    assert rec["citation"] == "Public Law 119-1"
    assert rec["statute_citation"] == "139 Stat. 3"
    assert rec["enacted_date"] == "2025-01-29"
    assert rec["pdf"].endswith("/content/pkg/PLAW-119publ1/pdf/PLAW-119publ1.pdf")
    assert rec["xml"].endswith("/content/pkg/PLAW-119publ1/xml/PLAW-119publ1.xml")

    # Title without a "PL nnn: " prefix is kept as-is; single citation -> no statute.
    rec2 = by_number[2]
    assert rec2["title"] == "A short title with no prefix"
    assert rec2["statute_citation"] == ""


def test_filter_laws():
    """filter_laws sorts by law number and paginates."""
    records = bulk.parse_plaw(_plaw_zip())
    desc = bulk.filter_laws(records, sort_by="desc")
    assert [r["law_number"] for r in desc] == [2, 1]
    asc = bulk.filter_laws(records, sort_by="asc")
    assert [r["law_number"] for r in asc] == [1, 2]
    # offset + limit
    assert [r["law_number"] for r in bulk.filter_laws(records, offset=1)] == [1]
    assert len(bulk.filter_laws(records, limit=1)) == 1
    # limit 0 -> no cap
    assert len(bulk.filter_laws(records, limit=0)) == 2


def test_load_plaw_cold_and_reuse(monkeypatch):
    """load_plaw parses when changed and reuses the cache when unchanged."""
    BillsState().bulk.clear()
    body = _plaw_zip()

    async def _changed(collection, congress, law_type):
        return body, True

    monkeypatch.setattr(bulk, "_download_zip", _changed)
    records = asyncio.run(bulk.load_plaw(119, "public"))
    assert {r["law_number"] for r in records} == {1, 2}

    parse_calls = {"n": 0}
    real_parse = bulk.parse_plaw

    def _counting_parse(zip_bytes):
        parse_calls["n"] += 1
        return real_parse(zip_bytes)

    monkeypatch.setattr(bulk, "parse_plaw", _counting_parse)

    async def _unchanged(collection, congress, law_type):
        return body, False

    monkeypatch.setattr(bulk, "_download_zip", _unchanged)
    cached = asyncio.run(bulk.load_plaw(119, "PUBLIC"))
    assert cached is records
    assert parse_calls["n"] == 0


# ---------------------------------------------------------------------------
# CCAL calendars + CMR reports
# ---------------------------------------------------------------------------

_CCAL_SITEMAP = """<?xml version="1.0" encoding="UTF-8"?>
<urlset>
  <url><loc>https://www.govinfo.gov/app/details/CCAL-119hcal-2025-01-03</loc></url>
  <url><loc>https://www.govinfo.gov/app/details/CCAL-119hcal-2025-01-07</loc></url>
  <url><loc>https://www.govinfo.gov/app/details/CCAL-119scal-2025-01-03</loc></url>
  <url><loc>https://www.govinfo.gov/app/details/CCAL-118hcal-2024-12-20</loc></url>
</urlset>"""


def test_congress_years():
    """_congress_years maps a Congress to its two calendar years."""
    assert bulk._congress_years(119) == [2025, 2026]
    assert bulk._congress_years(118) == [2023, 2024]


def test_load_calendars_filter_and_reuse(monkeypatch):
    """load_calendars parses package ids, filters by chamber, and memoizes."""
    BillsState().bulk.clear()
    calls = {"n": 0}

    async def _changed(url, filename):
        calls["n"] += 1
        return _CCAL_SITEMAP.encode("utf-8"), True

    monkeypatch.setattr(bulk, "_cached_get", _changed)
    house = asyncio.run(bulk.load_calendars(119, "house"))
    # Only 119 House editions; 119 Senate and 118 House are excluded.
    assert [r["package_id"] for r in house] == [
        "CCAL-119hcal-2025-01-03",
        "CCAL-119hcal-2025-01-07",
    ]
    assert house[0]["pdf"].endswith("/CCAL-119hcal-2025-01-03.pdf")
    assert house[0]["chamber"] == "house"

    # Two year sitemaps fetched on the first call.
    assert calls["n"] == 2

    async def _unchanged(url, filename):
        return _CCAL_SITEMAP.encode("utf-8"), False

    monkeypatch.setattr(bulk, "_cached_get", _unchanged)
    cached = asyncio.run(bulk.load_calendars(119, "house"))
    assert cached is house


def test_filter_calendars():
    """filter_calendars handles mostrecent, a specific date, and pagination."""
    records = [
        {"package_id": "a", "calendar_date": "2025-01-03"},
        {"package_id": "b", "calendar_date": "2025-01-07"},
        {"package_id": "c", "calendar_date": "2025-02-01"},
    ]
    assert (
        bulk.filter_calendars(records, publishdate="mostrecent")[0]["package_id"] == "c"
    )
    assert [
        r["package_id"]
        for r in bulk.filter_calendars(records, publishdate="2025-01-07")
    ] == ["b"]
    desc = bulk.filter_calendars(records, sort_by="desc")
    assert [r["calendar_date"] for r in desc] == [
        "2025-02-01",
        "2025-01-07",
        "2025-01-03",
    ]
    assert [r["package_id"] for r in bulk.filter_calendars(records, offset=2)] == ["a"]
    assert len(bulk.filter_calendars(records, limit=1)) == 1
    assert len(bulk.filter_calendars(records, limit=0)) == 3


def test_parse_cmr():
    """parse_cmr maps raw resultSet records to the data-model shape."""
    result_set = [
        {
            "packageId": "CMR-A98-00199920",
            "title": "Report One",
            "submittingAgency": "Agency X",
            "publicationDate": "2026-03-13",
            "dateSubmittedToCongress": "2026-03-13",
            "dateRequiredToBeSubmittedToGPO": "2026-03-01",
            "isOnTime": "true",
            "pdfLink": "https://www.govinfo.gov/content/pkg/CMR-A98-00199920/pdf/CMR-A98-00199920.pdf",
            "detailsLink": "https://www.govinfo.gov/app/details/CMR-A98-00199920",
            "modsLink": "https://www.govinfo.gov/metadata/pkg/CMR-A98-00199920/mods.xml",
        },
        # Missing pdfLink -> derived from packageId; isOnTime false.
        {"packageId": "CMR-X1-00000001", "title": "Two", "isOnTime": "false"},
    ]
    out = bulk.parse_cmr(result_set)
    assert out[0]["package_id"] == "CMR-A98-00199920"
    assert out[0]["is_on_time"] is True
    assert out[0]["submitting_agency"] == "Agency X"
    assert out[1]["is_on_time"] is False
    assert out[1]["pdf"].endswith("/CMR-X1-00000001/pdf/CMR-X1-00000001.pdf")


def test_fetch_cmr(monkeypatch):
    """fetch_cmr requests the link API and returns parsed records."""
    captured = {}

    async def _fake_amake_request(url, *args, **kwargs):
        captured["url"] = url
        return {
            "resultSet": [{"packageId": "CMR-A98-1", "title": "T", "isOnTime": "true"}]
        }

    monkeypatch.setattr(core_helpers, "amake_request", _fake_amake_request)
    out = asyncio.run(bulk.fetch_cmr(119, pagesize=5, offset=10))
    assert out[0]["package_id"] == "CMR-A98-1"
    assert "congress=119" in captured["url"]
    assert "pagesize=5" in captured["url"]
    assert "offset=10" in captured["url"]


def test_fetch_cmr_non_dict(monkeypatch):
    """fetch_cmr returns an empty list when the response is not a dict."""

    async def _fake(url, *args, **kwargs):
        return None

    monkeypatch.setattr(core_helpers, "amake_request", _fake)
    assert asyncio.run(bulk.fetch_cmr(119)) == []


# ---------------------------------------------------------------------------
# Committees: wssearch + MODS (keyless)
# ---------------------------------------------------------------------------

_WSSEARCH_ITEM = {
    "line1": "H. Rept. 119-637 - NO FEDERAL FUNDS FOR CASHLESS BAIL ACT",
    "line2": (
        "Congressional Reports. Committee on the Judiciary. "
        "To accompany H.R. 5213. Monday, May 4, 2026."
    ),
    "fieldMap": {
        "packageid": "CRPT-119hrpt637",
        "pdffile": "pdf/CRPT-119hrpt637.pdf",
        "title": "NO FEDERAL FUNDS FOR CASHLESS BAIL ACT",
        "collectionCode": "CRPT",
    },
}

_COMMITTEES_CURRENT = [
    {
        "type": "house",
        "name": "House Committee on the Judiciary",
        "url": "https://judiciary.house.gov",
        "thomas_id": "HSJU",
        "jurisdiction": "Judicial matters.",
        "subcommittees": [{"name": "Subcommittee on Courts", "thomas_id": "03"}],
    }
]

_MODS = """<?xml version="1.0" encoding="UTF-8"?>
<mods xmlns="http://www.loc.gov/mods/v3">
  <extension>
    <witness>Jane Doe</witness>
    <witness>John Roe</witness>
    <witness>  </witness>
    <heldDate>2026-05-04</heldDate>
  </extension>
  <relatedItem type="constituent">
    <accessId>CHRG-119hhrg12345-Wstate-DoeJ-20260504</accessId>
    <titleInfo><title>Statement of Jane Doe</title></titleInfo>
  </relatedItem>
  <relatedItem type="constituent">
    <titleInfo><title>No access id here</title></titleInfo>
  </relatedItem>
  <relatedItem type="otherFormat">
    <accessId>IGNORED</accessId>
  </relatedItem>
</mods>"""


class _FakeJSONSession:
    """Fake aiohttp.ClientSession whose POST yields canned JSON (or raises)."""

    def __init__(self, payload=None, post_exc=None):
        self._payload = payload
        self._post_exc = post_exc
        self.body = None

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        return False

    def post(self, url, json=None):
        """Return the canned JSON response context manager (or raise)."""
        self.body = json
        if self._post_exc is not None:
            raise self._post_exc
        return _FakeJSONResponse(self._payload)


class _FakeJSONResponse:
    """Async context-manager stand-in returning fixed JSON."""

    def __init__(self, payload):
        self._payload = payload

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        return False

    def raise_for_status(self):
        """No-op for a successful response."""

    async def json(self):
        """Return the canned JSON payload."""
        return self._payload


def test_wssearch_success(monkeypatch):
    """wssearch posts the query body and returns the parsed JSON."""
    import aiohttp

    session = _FakeJSONSession(
        payload={"iTotalCount": 1, "resultSet": [_WSSEARCH_ITEM]}
    )
    monkeypatch.setattr(aiohttp, "ClientSession", lambda *a, **k: session)

    result = asyncio.run(bulk.wssearch('committee:"hsju00"', offset=5, pagesize=10))
    assert result["iTotalCount"] == 1
    assert session.body["query"] == 'committee:"hsju00"'
    assert session.body["offset"] == 5
    assert session.body["pageSize"] == 10


def test_wssearch_exception(monkeypatch):
    """A request failure is wrapped in an OpenBBError."""
    import aiohttp

    session = _FakeJSONSession(post_exc=RuntimeError("down"))
    monkeypatch.setattr(aiohttp, "ClientSession", lambda *a, **k: session)

    with pytest.raises(OpenBBError, match="GovInfo search failed"):
        asyncio.run(bulk.wssearch("q"))


def test_chamber_from_package():
    """_chamber_from_package maps the chamber code in a package id."""
    assert bulk._chamber_from_package("CRPT-119hrpt637") == "House"
    assert bulk._chamber_from_package("CRPT-119srpt1") == "Senate"
    assert bulk._chamber_from_package("CHRG-119jhrg1") == "Joint"
    assert bulk._chamber_from_package("BADID") == ""


def test_wssearch_record_full():
    """_wssearch_record parses citation, date, title, chamber, and the PDF URL."""
    record = bulk._wssearch_record(_WSSEARCH_ITEM, "report", 119)
    assert record["doc_type"] == "report"
    assert record["citation"] == "H. Rept. 119-637"
    assert record["title"] == "NO FEDERAL FUNDS FOR CASHLESS BAIL ACT"
    assert record["congress"] == 119
    assert record["chamber"] == "House"
    assert record["date"] == "2026-05-04"
    assert record["package_id"] == "CRPT-119hrpt637"
    assert record["doc_url"].endswith("/CRPT-119hrpt637/pdf/CRPT-119hrpt637.pdf")


def test_wssearch_record_no_date_no_citation_no_package():
    """A record with no parseable date/citation/package falls back gracefully."""
    item = {"line1": "PlainTitleNoSeparator", "line2": "no date here", "fieldMap": {}}
    record = bulk._wssearch_record(item, "meeting", 119)
    assert record["citation"] is None
    assert record["date"] is None
    # No fieldMap title -> falls back to line1; no package -> empty doc_url.
    assert record["title"] == "PlainTitleNoSeparator"
    assert record["doc_url"] == ""


def test_wssearch_record_bad_date():
    """An unparseable date string yields a None date."""
    item = {
        "line1": "S. Hrg. 119-1 - Title",
        "line2": "Held February 30, 2026.",
        "fieldMap": {"packageid": "CHRG-119shrg1"},
    }
    record = bulk._wssearch_record(item, "meeting", 119)
    assert record["citation"] == "S. Hrg. 119-1"
    assert record["date"] is None


def test_search_committee_docs(monkeypatch):
    """search_committee_docs builds the faceted query and maps the resultSet."""
    captured = {}

    async def _wssearch(query, *, offset=0, pagesize=20, sort="2"):
        captured["query"] = query
        captured["offset"] = offset
        captured["pagesize"] = pagesize
        return {"resultSet": [_WSSEARCH_ITEM]}

    monkeypatch.setattr(bulk, "wssearch", _wssearch)
    out = asyncio.run(
        bulk.search_committee_docs("HSJU00", "report", 119, limit=5, offset=10)
    )
    assert captured["query"] == (
        'committee:"hsju00" AND collection:CRPT AND congress:119'
    )
    assert captured["pagesize"] == 5
    assert captured["offset"] == 10
    assert out[0]["package_id"] == "CRPT-119hrpt637"


def test_search_committee_docs_non_dict(monkeypatch):
    """A non-dict wssearch response yields no records."""

    async def _wssearch(query, *, offset=0, pagesize=20, sort="2"):
        return ["not", "a", "dict"]

    monkeypatch.setattr(bulk, "wssearch", _wssearch)
    out = asyncio.run(bulk.search_committee_docs("hsju00", "meeting", 119))
    assert out == []


def test_load_committee_structure_cold_cached_and_non_list(monkeypatch):
    """Structure loads cold, memoizes, and tolerates a non-list payload."""
    BillsState().bulk.clear()
    calls = {"n": 0}

    async def _list(url, *args, **kwargs):
        calls["n"] += 1
        return list(_COMMITTEES_CURRENT)

    monkeypatch.setattr(core_helpers, "amake_request", _list)
    first = asyncio.run(bulk.load_committee_structure())
    assert first[0]["thomas_id"] == "HSJU"
    # Second call reuses the cache (no new request).
    second = asyncio.run(bulk.load_committee_structure())
    assert second is first
    assert calls["n"] == 1

    # A non-list payload is coerced to an empty list.
    BillsState().bulk.clear()

    async def _bad(url, *args, **kwargs):
        return {"not": "a list"}

    monkeypatch.setattr(core_helpers, "amake_request", _bad)
    assert asyncio.run(bulk.load_committee_structure()) == []


def test_load_committee_structure_exception(monkeypatch):
    """A request exception yields an empty structure list."""
    BillsState().bulk.clear()

    async def _boom(url, *args, **kwargs):
        raise RuntimeError("net")

    monkeypatch.setattr(core_helpers, "amake_request", _boom)
    assert asyncio.run(bulk.load_committee_structure()) == []


def test_fetch_package_mods(monkeypatch):
    """fetch_package_mods returns the cached MODS body bytes."""
    captured = {}

    async def _cached_get(url, filename):
        captured["url"] = url
        captured["filename"] = filename
        return b"<mods/>", True

    monkeypatch.setattr(bulk, "_cached_get", _cached_get)
    body = asyncio.run(bulk.fetch_package_mods("CHRG-119hhrg1"))
    assert body == b"<mods/>"
    assert captured["url"].endswith("/metadata/pkg/CHRG-119hhrg1/mods.xml")
    assert captured["filename"] == "CHRG-119hhrg1.mods.xml"


def test_parse_mods():
    """parse_mods extracts witnesses, held dates, and constituent granule docs."""
    detail = bulk.parse_mods(_MODS.encode("utf-8"), "CHRG-119hhrg12345")
    assert detail["witnesses"] == ["Jane Doe", "John Roe"]
    assert detail["held_dates"] == ["2026-05-04"]
    # Only the constituent relatedItem with an accessId becomes a document.
    assert len(detail["documents"]) == 1
    doc = detail["documents"][0]
    assert doc["granule_id"] == "CHRG-119hhrg12345-Wstate-DoeJ-20260504"
    assert doc["title"] == "Statement of Jane Doe"
    assert doc["pdf"].endswith(
        "/CHRG-119hhrg12345/pdf/CHRG-119hhrg12345-Wstate-DoeJ-20260504.pdf"
    )


def test_parse_mods_no_constituents():
    """A MODS with no constituent documents yields an empty documents list."""
    mods = (
        '<mods xmlns="http://www.loc.gov/mods/v3"><titleInfo>'
        "<title>Standalone</title></titleInfo></mods>"
    )
    detail = bulk.parse_mods(mods.encode("utf-8"), "CHRG-1")
    assert detail["documents"] == []
    assert detail["witnesses"] == []
    assert detail["held_dates"] == []


# ---------------------------------------------------------------------------
# Full-text search + legislators
# ---------------------------------------------------------------------------

_SEARCH_RESPONSE = {
    "iTotalCount": 2,
    "resultSet": [
        {
            "line1": "H. Rept. 119-637 - NO FEDERAL FUNDS",
            "line2": "Congressional Reports. Committee on the Judiciary. Monday, May 4, 2026.",
            "fieldMap": {
                "packageid": "CRPT-119hrpt637",
                "title": "NO FEDERAL FUNDS",
                "collectionCode": "CRPT",
            },
        },
        {
            "line1": "Union Calendar",
            "line2": "Congressional Calendars. Tuesday, June 3, 2026.",
            "fieldMap": {
                "packageid": "CCAL-119hcal-2026-06-03",
                "title": "Union Calendar",
                "collectionCode": "CCAL",
            },
        },
    ],
}


def test_search_record():
    """_search_record maps a wssearch item to a search record with congress + collection."""
    rec = bulk._search_record(_SEARCH_RESPONSE["resultSet"][0])
    assert rec["collection"] == "CRPT"
    assert rec["congress"] == 119
    assert rec["citation"] == "H. Rept. 119-637"
    assert rec["date"] == "2026-05-04"
    assert rec["package_id"] == "CRPT-119hrpt637"
    assert rec["doc_url"].endswith("/CRPT-119hrpt637.pdf")


def test_search_govinfo_all_collections(monkeypatch):
    """With no collection, the query ORs all congressional collections + adds filters."""
    captured = {}

    async def _fake(query, *, offset=0, pagesize=20, sort="2"):
        captured["query"] = query
        captured["pagesize"] = pagesize
        return _SEARCH_RESPONSE

    monkeypatch.setattr(bulk, "wssearch", _fake)
    out = asyncio.run(
        bulk.search_govinfo(
            "immigration",
            congress=119,
            start_date="2025-01-01",
            end_date="2026-06-03",
            limit=5,
        )
    )
    assert "immigration" in captured["query"]
    assert (
        "collection:CHRG" in captured["query"]
        and "collection:CRPT" in captured["query"]
    )
    assert "BILLSTATUS" not in captured["query"]
    assert "congress:119" in captured["query"]
    assert "publishdate:range(2025-01-01,2026-06-03)" in captured["query"]
    assert captured["pagesize"] == 5
    assert {r["collection"] for r in out} == {"CRPT", "CCAL"}


def test_search_govinfo_single_collection_and_open_range(monkeypatch):
    """A single collection is used verbatim; a one-sided date still forms a range."""
    captured = {}

    async def _fake(query, *, offset=0, pagesize=20, sort="2"):
        captured["query"] = query
        return {"resultSet": []}

    monkeypatch.setattr(bulk, "wssearch", _fake)
    asyncio.run(bulk.search_govinfo("ai", collection="CHRG", start_date="2025-01-01"))
    assert "collection:CHRG" in captured["query"]
    assert " OR " not in captured["query"]
    assert "publishdate:range(2025-01-01," in captured["query"]


def test_search_govinfo_non_dict(monkeypatch):
    """A non-dict search response yields an empty list."""

    async def _fake(query, **kwargs):
        return None

    monkeypatch.setattr(bulk, "wssearch", _fake)
    assert asyncio.run(bulk.search_govinfo("x")) == []


_LEGISLATORS = [
    {
        "id": {"bioguide": "C001129"},
        "name": {"official_full": "Mike Collins"},
        "bio": {"birthday": "1970-04-15"},
        "terms": [{"party": "Republican", "state": "GA"}],
    },
    {"id": {}, "name": {}, "terms": [{}]},  # no bioguide -> skipped
]


def test_load_legislators_cold_cached_and_non_list(monkeypatch):
    """load_legislators indexes by bioguide, caches, and tolerates non-list payloads."""
    BillsState().bulk.clear()
    calls = {"n": 0}

    async def _fake(url, *args, **kwargs):
        calls["n"] += 1
        return _LEGISLATORS

    monkeypatch.setattr(core_helpers, "amake_request", _fake)
    index = asyncio.run(bulk.load_legislators())
    assert set(index) == {"C001129"}
    assert index["C001129"]["party"] == "Republican"
    assert index["C001129"]["birthday"] == "1970-04-15"
    assert index["C001129"]["photo_url"].endswith("/C001129.jpg")
    # cached: no second fetch
    asyncio.run(bulk.load_legislators())
    assert calls["n"] == 1

    BillsState().bulk.clear()

    async def _bad(url, *args, **kwargs):
        return None

    monkeypatch.setattr(core_helpers, "amake_request", _bad)
    assert asyncio.run(bulk.load_legislators()) == {}


def test_load_legislators_download_error(monkeypatch):
    """A failed legislators download yields an empty index."""
    BillsState().bulk.clear()

    async def _boom(url, *args, **kwargs):
        raise RuntimeError("network down")

    monkeypatch.setattr(core_helpers, "amake_request", _boom)
    assert asyncio.run(bulk.load_legislators()) == {}


def test_memoized_dedupes_concurrent_loads(monkeypatch):
    """Concurrent loads of the same key share one download (in-flight dedup)."""
    BillsState().bulk.clear()
    bulk._LOAD_LOCKS.clear()
    calls = {"n": 0}

    async def _slow_download(collection, congress, bill_type):
        calls["n"] += 1
        await asyncio.sleep(0.05)  # hold the lock so the 2nd caller queues
        return _billstatus_zip(), True

    monkeypatch.setattr(bulk, "_download_zip", _slow_download)

    async def _run():
        return await asyncio.gather(
            bulk.load_billstatus(119, "hr"),
            bulk.load_billstatus(119, "hr"),
        )

    first, second = asyncio.run(_run())
    assert calls["n"] == 1  # downloaded once despite two concurrent callers
    assert first is second  # both received the same cached object


def test_load_billstatus_in_memory_short_circuit(monkeypatch):
    """A warmed key returns instantly without any download."""
    BillsState().bulk.clear()
    bulk._LOAD_LOCKS.clear()
    BillsState().bulk["BILLSTATUS_119_hr"] = [{"number": 1}]

    async def _boom(*args, **kwargs):
        raise AssertionError("warmed cache must not hit the network")

    monkeypatch.setattr(bulk, "_download_zip", _boom)
    assert asyncio.run(bulk.load_billstatus(119, "hr")) == [{"number": 1}]


# ---------------------------------------------------------------------------
# parse_amendment_ref / _amendment_record
# ---------------------------------------------------------------------------


def test_parse_amendment_ref_ok():
    """Dash id, shorthand, and full-URL amendment references parse correctly."""
    assert bulk.parse_amendment_ref("119-hamdt-2") == (119, "hamdt", "2")
    assert bulk.parse_amendment_ref("119/samdt/97") == (119, "samdt", "97")
    assert bulk.parse_amendment_ref(
        "https://api.congress.gov/v3/amendment/119/samdt/97?format=json"
    ) == (119, "samdt", "97")


def test_parse_amendment_ref_raises():
    """An unparseable amendment reference raises OpenBBError."""
    with pytest.raises(OpenBBError, match="Could not parse an amendment"):
        bulk.parse_amendment_ref("not-an-amendment")


def test_parse_billstatus_amendments():
    """The <amendments> block is parsed onto the bill record."""
    rec = {r["number"]: r for r in bulk.parse_billstatus(_billstatus_zip())}[29]
    amendments = rec["amendments"]
    assert len(amendments) == 2
    hamdt = amendments[0]
    assert hamdt["amendment_id"] == "119-hamdt-10"
    assert hamdt["type"] == "HAMDT"
    assert hamdt["amendedBill"] == {
        "congress": "119",
        "type": "HR",
        "number": "29",
        "title": "Laken Riley Act",
    }
    assert hamdt["sponsors"][0]["fullName"] == "Rep. Collins"
    assert hamdt["actions"][0]["text"] == "Agreed."
    assert hamdt["links"][0]["name"] == "House Report 119-1"
    # The Senate amendment has no amendedBill but an amendedAmendment.
    samdt = amendments[1]
    assert samdt["amendedBill"] == {}
    assert samdt["amendedAmendment"]["number"] == "10"


def test_to_amendment_list_item():
    """to_amendment_list_item projects to the slim shape and trims the date."""
    rec = {r["number"]: r for r in bulk.parse_billstatus(_billstatus_zip())}[29]
    item = bulk.to_amendment_list_item(rec["amendments"][0])
    assert item["amendment_id"] == "119-hamdt-10"
    assert item["updateDate"] == "2025-02-09"
    assert item["amendedBill"]["number"] == "29"
    assert "sponsors" in item


# ---------------------------------------------------------------------------
# load_amendments / load_amendment_record / filter_amendments
# ---------------------------------------------------------------------------


def test_load_amendments_aggregates_and_filters(monkeypatch):
    """load_amendments aggregates across bill types and filters by type."""
    BillsState().bulk.clear()
    records = bulk.parse_billstatus(_billstatus_zip())

    async def _status(congress, bill_type):
        # Only the 'hr' archive carries amendments in the fixture.
        return records if bill_type == "hr" else []

    monkeypatch.setattr(bulk, "load_billstatus", _status)

    all_amds = asyncio.run(bulk.load_amendments(119))
    assert {a["amendment_id"] for a in all_amds} == {"119-hamdt-10", "119-samdt-11"}

    # Type filter keeps only the matching chamber (served from the cache).
    hamdt = asyncio.run(bulk.load_amendments(119, "hamdt"))
    assert [a["amendment_id"] for a in hamdt] == ["119-hamdt-10"]


def test_load_amendment_record_found_and_missing(monkeypatch):
    """load_amendment_record finds a record by id and raises when absent."""
    BillsState().bulk.clear()
    records = bulk.parse_billstatus(_billstatus_zip())

    async def _status(congress, bill_type):
        return records if bill_type == "hr" else []

    monkeypatch.setattr(bulk, "load_billstatus", _status)

    rec = asyncio.run(bulk.load_amendment_record("119-hamdt-10"))
    assert rec["number"] == "10"

    with pytest.raises(OpenBBError, match="Amendment not found"):
        asyncio.run(bulk.load_amendment_record("119-hamdt-999"))


def test_filter_amendments():
    """filter_amendments applies date filters, sorting, offset, and limit."""
    records = [
        {"number": "1", "updateDate": "2025-01-05", "latestAction": {}},
        {"number": "2", "latestAction": {"actionDate": "2025-03-05"}},
        {"number": "3", "updateDate": "2025-06-05", "latestAction": {}},
    ]
    out = bulk.filter_amendments(
        records, start_date=date(2025, 2, 1), end_date=date(2025, 5, 1)
    )
    # Only #2 falls in range; it sorts/returns alone. (#2 has no updateDate so the
    # date filter drops it -> covers the `updated()` empty guard.)
    assert [r["number"] for r in out] == []

    # No date filter: default desc sort by action date / update date, default cap.
    out = bulk.filter_amendments(records)
    assert [r["number"] for r in out] == ["3", "2", "1"]

    # offset + limit.
    out = bulk.filter_amendments(records, offset=1, limit=1, sort_by="asc")
    assert len(out) == 1

    # limit=0 returns all (after offset).
    assert len(bulk.filter_amendments(records, limit=0)) == 3


# ---------------------------------------------------------------------------
# _resolve_link / amendment_link_base / resolve_amendment_text
# ---------------------------------------------------------------------------


def test_resolve_link_redirect(monkeypatch):
    """_resolve_link returns the Location header on a redirect."""
    resp = _FakeResponse(status=302, headers={"Location": "https://x/doc.htm"})
    _patch_session(monkeypatch, response=resp)
    assert asyncio.run(bulk._resolve_link("https://link")) == "https://x/doc.htm"


def test_resolve_link_no_redirect(monkeypatch):
    """_resolve_link returns None when the service answers without a redirect."""
    _patch_session(monkeypatch, response=_FakeResponse(status=400))
    assert asyncio.run(bulk._resolve_link("https://link")) is None


def test_resolve_link_exception(monkeypatch):
    """_resolve_link swallows network errors and returns None."""
    _patch_session(monkeypatch, get_exc=RuntimeError("boom"))
    assert asyncio.run(bulk._resolve_link("https://link")) is None


def test_amendment_link_base():
    """amendment_link_base builds hamendment/samendment URLs and guards missing bills."""
    hamdt = {
        "congress": 119,
        "number": "10",
        "type": "HAMDT",
        "amendedBill": {"type": "HR", "number": "29"},
    }
    assert bulk.amendment_link_base(hamdt) == (
        "https://www.govinfo.gov/link/crec/hamendment/119/hr/29/10"
    )
    samdt = {"congress": 119, "number": "97", "type": "SAMDT"}
    assert bulk.amendment_link_base(samdt) == (
        "https://www.govinfo.gov/link/crec/samendment/119/97"
    )
    # A House amendment with no amended bill cannot be linked.
    assert bulk.amendment_link_base({"type": "HAMDT", "amendedBill": {}}) is None


def test_resolve_amendment_text_senate(monkeypatch):
    """resolve_amendment_text resolves HTML/PDF and parses the CREC date."""
    urls = {
        "": "https://www.govinfo.gov/content/pkg/CREC-2025-01-01/html/CREC-2025-01-01-pt1-PgS1.htm",
        "pdf": "https://www.govinfo.gov/content/pkg/CREC-2025-01-01/pdf/CREC-2025-01-01-pt1-PgS1.pdf",
    }

    async def _fake_resolve(url):
        return urls["pdf"] if "link-type=pdf" in url else urls[""]

    monkeypatch.setattr(bulk, "_resolve_link", _fake_resolve)
    out = asyncio.run(
        bulk.resolve_amendment_text({"congress": 119, "number": "97", "type": "SAMDT"})
    )
    assert {d["format"] for d in out} == {"HTML", "PDF"}
    assert out[0]["date"] == "2025-01-01"


def test_resolve_amendment_text_no_base():
    """resolve_amendment_text returns [] when no link base can be built."""
    out = asyncio.run(bulk.resolve_amendment_text({"type": "HAMDT", "amendedBill": {}}))
    assert out == []


def test_resolve_amendment_text_unresolved(monkeypatch):
    """resolve_amendment_text drops formats the link service does not resolve."""

    async def _none(url):
        return None

    monkeypatch.setattr(bulk, "_resolve_link", _none)
    out = asyncio.run(
        bulk.resolve_amendment_text({"congress": 119, "number": "97", "type": "SAMDT"})
    )
    assert out == []


# ---------------------------------------------------------------------------
# Members: load_members / social / committees / legislation / votes
# ---------------------------------------------------------------------------

_MEMBERS_DATA = [
    {
        "id": {"bioguide": "A000055", "govtrack": 400004, "wikipedia": "Bob Aderholt"},
        "name": {
            "first": "Robert",
            "last": "Aderholt",
            "official_full": "Robert B. Aderholt",
        },
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
            },
        ],
    },
    {
        "id": {"bioguide": "C000127"},
        "name": {
            "first": "Maria",
            "last": "Cantwell",
            "official_full": "Maria Cantwell",
        },
        "bio": {"birthday": "1958-10-13", "gender": "F"},
        "terms": [
            {
                "type": "sen",
                "state": "WA",
                "party": "Democrat",
                "start": "2025-01-03",
                "end": "2031-01-03",
            }
        ],
    },
]


def test_load_members_cold_cached_and_non_list(monkeypatch):
    """load_members fetches once, caches, and tolerates a non-list payload."""
    BillsState().bulk.clear()
    calls = {"n": 0}

    async def _fake(url, *a, **k):
        calls["n"] += 1
        return _MEMBERS_DATA

    monkeypatch.setattr(core_helpers, "amake_request", _fake)
    members = asyncio.run(bulk.load_members())
    assert len(members) == 2
    asyncio.run(bulk.load_members())
    assert calls["n"] == 1

    BillsState().bulk.clear()

    async def _bad(url, *a, **k):
        return None

    monkeypatch.setattr(core_helpers, "amake_request", _bad)
    assert asyncio.run(bulk.load_members()) == []


def test_load_members_download_error(monkeypatch):
    """A failed members download yields an empty list."""
    BillsState().bulk.clear()

    async def _boom(url, *a, **k):
        raise RuntimeError("down")

    monkeypatch.setattr(core_helpers, "amake_request", _boom)
    assert asyncio.run(bulk.load_members()) == []


def test_to_member_list_item():
    """to_member_list_item projects rep (with district) and sen (no district)."""
    rep = bulk.to_member_list_item(_MEMBERS_DATA[0])
    assert rep["bioguide_id"] == "A000055"
    assert rep["chamber"] == "house"
    assert rep["district"] == 4
    assert rep["website"] == "https://aderholt.house.gov"
    sen = bulk.to_member_list_item(_MEMBERS_DATA[1])
    assert sen["chamber"] == "senate"
    assert sen["district"] is None
    # An empty record falls back to blanks without raising.
    empty = bulk.to_member_list_item({})
    assert empty["bioguide_id"] == ""
    assert empty["name"] == ""


def test_filter_members():
    """filter_members filters by chamber/state/party and sorts by name."""
    items = [bulk.to_member_list_item(m) for m in _MEMBERS_DATA]
    assert [m["name"] for m in bulk.filter_members(items)] == [
        "Maria Cantwell",
        "Robert B. Aderholt",
    ]
    assert len(bulk.filter_members(items, chamber="house")) == 1
    assert len(bulk.filter_members(items, state="wa")) == 1
    assert len(bulk.filter_members(items, party="republican")) == 1


def test_load_member_record_found_and_missing(monkeypatch):
    """load_member_record finds by bioguide and raises when absent."""
    BillsState().bulk.clear()

    async def _fake(url, *a, **k):
        return _MEMBERS_DATA

    monkeypatch.setattr(core_helpers, "amake_request", _fake)
    rec = asyncio.run(bulk.load_member_record("C000127"))
    assert rec["name"]["last"] == "Cantwell"
    with pytest.raises(OpenBBError, match="Member not found"):
        asyncio.run(bulk.load_member_record("ZZZ"))


def test_load_social_media(monkeypatch):
    """load_social_media indexes by bioguide and skips entries without one."""
    BillsState().bulk.clear()

    async def _fake(url, *a, **k):
        return [
            {"id": {"bioguide": "A000055"}, "social": {"twitter": "Robert_Aderholt"}},
            {"id": {}, "social": {"twitter": "x"}},  # no bioguide -> skipped
        ]

    monkeypatch.setattr(core_helpers, "amake_request", _fake)
    index = asyncio.run(bulk.load_social_media())
    assert index == {"A000055": {"twitter": "Robert_Aderholt"}}

    BillsState().bulk.clear()

    async def _bad(url, *a, **k):
        raise RuntimeError("down")

    monkeypatch.setattr(core_helpers, "amake_request", _bad)
    assert asyncio.run(bulk.load_social_media()) == {}


def test_load_committee_membership(monkeypatch):
    """load_committee_membership caches a dict and coerces non-dicts to {}."""
    BillsState().bulk.clear()

    async def _fake(url, *a, **k):
        return {
            "HSAP": [
                {"bioguide": "A000055", "rank": 1, "title": "", "party": "majority"}
            ]
        }

    monkeypatch.setattr(core_helpers, "amake_request", _fake)
    assert "HSAP" in asyncio.run(bulk.load_committee_membership())

    BillsState().bulk.clear()

    async def _bad(url, *a, **k):
        return ["not", "a", "dict"]

    monkeypatch.setattr(core_helpers, "amake_request", _bad)
    assert asyncio.run(bulk.load_committee_membership()) == {}

    BillsState().bulk.clear()

    async def _boom(url, *a, **k):
        raise RuntimeError("down")

    monkeypatch.setattr(core_helpers, "amake_request", _boom)
    assert asyncio.run(bulk.load_committee_membership()) == {}


def test_member_committees(monkeypatch):
    """member_committees inverts membership and resolves committee/subcommittee names."""

    async def _membership():
        return {
            "HSAP": [
                {"bioguide": "A000055", "rank": 1, "title": "", "party": "majority"}
            ],
            "HSAP01": [
                {
                    "bioguide": "A000055",
                    "rank": 1,
                    "title": "Chair",
                    "party": "majority",
                }
            ],
            "HSAG": [
                {"bioguide": "B000000", "rank": 2, "title": "", "party": "minority"}
            ],
        }

    async def _structure():
        return [
            {
                "thomas_id": "HSAP",
                "name": "House Committee on Appropriations",
                "subcommittees": [{"thomas_id": "01", "name": "Defense"}],
            }
        ]

    monkeypatch.setattr(bulk, "load_committee_membership", _membership)
    monkeypatch.setattr(bulk, "load_committee_structure", _structure)

    out = asyncio.run(bulk.member_committees("A000055"))
    names = [c["committee"] for c in out]
    assert "House Committee on Appropriations" in names
    assert "House Committee on Appropriations — Defense" in names
    # Parent committee sorts before its subcommittee.
    assert out[0]["is_subcommittee"] is False
    assert any(c["title"] == "Chair" for c in out)


def test_member_legislation(monkeypatch):
    """member_legislation finds sponsored/cosponsored bills and sorts newest-first."""
    bills = [
        {
            "bill_id": "119-hr-1",
            "title": "Sponsored Bill",
            "introducedDate": "2025-03-01",
            "sponsors": [{"bioguideId": "A000055"}],
            "cosponsors": [],
            "latestAction": {"actionDate": "2025-04-01", "text": "Referred"},
        },
        {
            "bill_id": "119-hr-2",
            "title": "Cosponsored Bill",
            "introducedDate": "2025-05-01",
            "sponsors": [{"bioguideId": "Z"}],
            "cosponsors": [{"bioguideId": "A000055"}],
            "latestAction": {},
        },
        {
            "bill_id": "119-hr-3",
            "title": "Unrelated",
            "introducedDate": "2025-06-01",
            "sponsors": [{"bioguideId": "Z"}],
            "cosponsors": [],
        },
    ]

    seen: list = []

    async def _status(congress, bill_type):
        seen.append((congress, bill_type))
        return bills if (congress == 119 and bill_type == "hr") else []

    monkeypatch.setattr(bulk, "load_billstatus", _status)
    out = asyncio.run(bulk.member_legislation("A000055", [119, 118]))
    assert [b["bill_id"] for b in out] == ["119-hr-2", "119-hr-1"]  # newest first
    assert out[0]["role"] == "Cosponsor"
    assert out[1]["role"] == "Sponsor"
    # Every bill is tagged with its Congress, and both Congresses were scanned.
    assert out[0]["congress"] == 119
    assert {c for c, _ in seen} == {119, 118}


def test_member_served_congresses():
    """member_served_congresses derives Congresses from terms, floored at the 108th."""
    record = {
        "terms": [
            {"start": "1789-03-04"},  # before 1935 -> year_to_congress raises, skipped
            {"start": "1997-01-07"},  # 105th -> below the 108th floor, dropped
            {"start": "2017-01-03"},  # 115th
            {"start": "2025-01-03"},  # 119th
            {"start": ""},  # unparseable, ignored
        ]
    }
    assert bulk.member_served_congresses(record) == [119, 115]


# ---------------------------------------------------------------------------
# Voteview: member_service / bill ids / members / rollcalls / votes / passage
# ---------------------------------------------------------------------------


def test_member_service():
    """member_service maps each served Congress to its chamber, newest first."""
    record = {
        "terms": [
            {"type": "rep", "start": "1789-03-04"},  # year_to_congress raises, skipped
            {"type": "rep", "start": "2013-01-03"},  # 113th House
            {"type": "sen", "start": "2025-01-03"},  # 119th Senate
            {"type": "rep", "start": ""},  # unparseable, skipped
        ]
    }
    assert bulk.member_service(record) == [(119, "S"), (113, "H")]


def test_bill_number_to_id():
    """Voteview bill_number values convert to bill ids; nominations return None."""
    assert bulk._bill_number_to_id("HR29", 119) == "119-hr-29"
    assert bulk._bill_number_to_id("HRES5", 119) == "119-hres-5"
    assert bulk._bill_number_to_id("SCONRES1", 119) == "119-sconres-1"
    assert bulk._bill_number_to_id("S5", 119) == "119-s-5"
    assert bulk._bill_number_to_id("PN1", 119) is None  # nomination
    assert bulk._bill_number_to_id("", 119) is None
    assert bulk._bill_number_to_id("MOTION", 119) is None


_VV_MEMBERS = (
    "congress,chamber,icpsr,bioguide_id\n"
    "119,Senate,39310,C000127\n"
    "119,Senate,99999,\n"  # no bioguide -> skipped
)
_VV_ROLLCALLS = (
    "congress,chamber,rollnumber,date,bill_number,vote_result,vote_desc,vote_question\n"
    "119,Senate,1,2026-01-10,S5,Passed,A bill to do things,On Passage of the Bill\n"
    "119,Senate,2,2026-01-11,PN1,Confirmed,A nominee,On the Nomination\n"
    "119,Senate,3,2026-01-12,S9,Rejected,Another bill,On Passage of the Bill\n"
)
_VV_VOTES = (
    "congress,chamber,rollnumber,icpsr,cast_code,prob\n"
    "119,Senate,1,39310,1,99\n"  # Yea on S5 (On Passage)
    "119,Senate,2,39310,1,99\n"  # Yea on nomination (not legislation)
    "119,Senate,3,39310,6,99\n"  # Nay on S9 (On Passage)
    "119,Senate,4,39310,0,99\n"  # cast_code 0 (not a member) -> skipped
    "119,Senate,1,99999,1,99\n"  # other member
)


def _patch_voteview(monkeypatch):
    """Patch _cached_get to serve the synthetic Voteview CSVs by filename."""

    async def _get(url, filename):
        if "members" in filename:
            body = _VV_MEMBERS
        elif "rollcalls" in filename:
            body = _VV_ROLLCALLS
        else:
            body = _VV_VOTES
        return body.encode("utf-8"), True

    monkeypatch.setattr(bulk, "_cached_get", _get)


def test_load_voteview_members(monkeypatch):
    """load_voteview_members indexes bioguide -> icpsr and skips blank bioguides."""
    BillsState().bulk.clear()
    _patch_voteview(monkeypatch)
    index = asyncio.run(bulk.load_voteview_members(119, "S"))
    assert index == {"C000127": "39310"}


def test_load_voteview_rollcalls(monkeypatch):
    """load_voteview_rollcalls maps rollnumber -> metadata."""
    BillsState().bulk.clear()
    _patch_voteview(monkeypatch)
    rolls = asyncio.run(bulk.load_voteview_rollcalls(119, "S"))
    assert rolls["1"]["bill_number"] == "S5"
    assert rolls["1"]["question"] == "On Passage of the Bill"


def test_voteview_text_download_error(monkeypatch):
    """A failed Voteview fetch degrades to an empty string."""

    async def _boom(url, filename):
        raise RuntimeError("down")

    monkeypatch.setattr(bulk, "_cached_get", _boom)
    assert asyncio.run(bulk._voteview_text("members", 119, "S")) == ""


def test_member_congress_votes(monkeypatch):
    """member_congress_votes joins votes to rollcalls and maps cast codes."""
    BillsState().bulk.clear()
    _patch_voteview(monkeypatch)
    votes = asyncio.run(bulk.member_congress_votes("C000127", 119, "S"))
    assert len(votes) == 3
    by_roll = {v["rollnumber"]: v for v in votes}
    assert by_roll[1]["position"] == "Yea"
    assert by_roll[1]["bill_id"] == "119-s-5"
    assert by_roll[1]["chamber"] == "senate"
    assert by_roll[2]["bill_id"] is None  # nomination -> no bill id
    assert by_roll[3]["position"] == "Nay"


def test_member_congress_votes_member_absent(monkeypatch):
    """A member not present in a Congress yields no votes."""
    BillsState().bulk.clear()
    _patch_voteview(monkeypatch)
    assert asyncio.run(bulk.member_congress_votes("ZZZ", 119, "S")) == []


def test_member_votes(monkeypatch):
    """member_votes keeps legislative votes only, newest-first, capped at limit."""
    BillsState().bulk.clear()
    _patch_voteview(monkeypatch)
    out = asyncio.run(bulk.member_votes("C000127", [(119, "S")], limit=5))
    # Nomination (roll 2) dropped; the two bill votes returned newest-first.
    assert [v["bill_id"] for v in out] == ["119-s-9", "119-s-5"]
    capped = asyncio.run(bulk.member_votes("C000127", [(119, "S")], limit=1))
    assert len(capped) == 1


def test_member_passage_record(monkeypatch):
    """member_passage_record tallies Yea/Nay on 'On Passage' votes across tenure."""
    BillsState().bulk.clear()
    _patch_voteview(monkeypatch)
    rec = asyncio.run(bulk.member_passage_record("C000127", [(119, "S")]))
    assert rec == {"yea": 1, "nay": 1, "total": 2, "yea_pct": 50.0}


def test_member_passage_record_empty(monkeypatch):
    """With no On-Passage votes, the percentage is None."""

    async def _votes(bioguide, congress, chamber):
        return [{"question": "On the Nomination", "cast_code": "1"}]

    monkeypatch.setattr(bulk, "member_congress_votes", _votes)
    rec = asyncio.run(bulk.member_passage_record("C000127", [(119, "S")]))
    assert rec == {"yea": 0, "nay": 0, "total": 0, "yea_pct": None}
