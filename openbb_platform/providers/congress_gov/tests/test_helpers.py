"""Tests for openbb_congress_gov.utils.helpers, congress_search, and constants."""

import asyncio

import pytest
from fastapi.exceptions import HTTPException
from openbb_core.provider.utils import helpers as core_helpers

from openbb_congress_gov.utils import bulk, congress_search, helpers


def test_year_to_congress_valid():
    """A known year maps to the correct congress number."""
    assert helpers.year_to_congress(1935) == 74
    assert helpers.year_to_congress(1993) == 103


def test_year_to_congress_too_early():
    """A year before 1935 raises ValueError."""
    with pytest.raises(ValueError, match="1935 or later"):
        helpers.year_to_congress(1900)


def test_bills_state_singleton():
    """BillsState is a singleton sharing the same bulk mapping."""
    a = helpers.BillsState()
    b = helpers.BillsState()
    assert a is b
    a.bulk["x"] = 1
    assert b.bulk["x"] == 1
    a.bulk.clear()


def test_download_bills_invalid_url():
    """A non-congress.gov URL is reported as invalid."""
    result = helpers.download_bills(["https://example.com/foo.pdf"])
    assert result[0]["error_type"] == "invalid_url"
    assert result[0]["filename"] == "foo.pdf"


def test_download_bills_success(monkeypatch):
    """A valid URL returns base64-encoded content."""

    class _Resp:
        content = b"%PDF-1.4 data"

        def raise_for_status(self):
            """No-op."""

    monkeypatch.setattr(core_helpers, "make_request", lambda url: _Resp())
    result = helpers.download_bills(
        ["https://www.congress.gov/119/bills/s1/BILLS-119s1is.pdf"]
    )
    assert "content" in result[0]
    assert result[0]["data_format"]["data_type"] == "pdf"


def test_download_bills_string_content(monkeypatch):
    """Non-bytes content is passed through verbatim."""

    class _Resp:
        content = "already text"

        def raise_for_status(self):
            """No-op."""

    monkeypatch.setattr(core_helpers, "make_request", lambda url: _Resp())
    result = helpers.download_bills(["https://govinfo.gov/x.pdf"])
    assert result[0]["content"] == "already text"


def test_download_bills_download_error(monkeypatch):
    """A download exception is captured as a download_error."""

    def _boom(url):
        raise RuntimeError("network down")

    monkeypatch.setattr(core_helpers, "make_request", _boom)
    result = helpers.download_bills(["https://www.congress.gov/x.pdf"])
    assert result[0]["error_type"] == "download_error"
    assert "network down" in result[0]["content"]


_PKG = "https://www.govinfo.gov/content/pkg"
_TV_RECORD = {
    "number": 29,
    "textVersions": [
        {
            "type": "Placed on Calendar Senate",
            "date": "2025-02-10T05:00:00Z",
            "formats": [{"url": f"{_PKG}/BILLS-119hr29pcs/xml/BILLS-119hr29pcs.xml"}],
        },
        {
            "type": "Introduced in House",
            "date": "2025-01-03T05:00:00Z",
            "formats": [{"url": f"{_PKG}/BILLS-119hr29ih/xml/BILLS-119hr29ih.xml"}],
        },
        {
            "type": "Reprint",
            "date": "2025-01-04T00:00:00Z",
            "formats": [{"url": f"{_PKG}/BILLS-119hr29ih/xml/BILLS-119hr29ih.xml"}],
        },
        {
            "type": "No Formats",
            "date": "2025-01-01T00:00:00Z",
            "formats": [],
        },
    ],
}


def _patch_billstatus(monkeypatch, record):
    """Stub ensure_billstatus and store.get_bill to serve a single canned record."""
    from openbb_congress_gov.utils import store

    async def _ensure(congress, bill_type):
        return None

    monkeypatch.setattr(bulk, "ensure_billstatus", _ensure)
    monkeypatch.setattr(store, "get_bill", lambda bill_id: record)


def test_get_bill_text_choices_non_workspace(monkeypatch):
    """Non-workspace output returns versioned pdf/htm/xml dicts, deduped by PDF."""
    _patch_billstatus(monkeypatch, _TV_RECORD)
    result = asyncio.run(helpers.get_bill_text_choices("119/hr/29"))
    assert len(result) == 2
    assert result[0]["version_type"] == "Placed on Calendar Senate"
    assert result[0]["pdf"].endswith("/BILLS-119hr29pcs.pdf")
    assert result[0]["htm"].endswith("/BILLS-119hr29pcs.htm")
    assert result[0]["xml"].endswith("/BILLS-119hr29pcs.xml")


def test_get_bill_text_choices_non_workspace_empty(monkeypatch):
    """A bill with no usable text versions raises 404."""
    _patch_billstatus(monkeypatch, {"number": 29, "textVersions": []})
    with pytest.raises(HTTPException) as exc:
        asyncio.run(helpers.get_bill_text_choices("119/hr/29"))
    assert exc.value.status_code == 404


def test_get_bill_text_choices_bill_not_found(monkeypatch):
    """When the bill is absent from the bulk data, 404 is raised."""
    _patch_billstatus(monkeypatch, None)
    with pytest.raises(HTTPException) as exc:
        asyncio.run(helpers.get_bill_text_choices("119/hr/29"))
    assert exc.value.status_code == 404


def test_get_bill_text_choices_workspace(monkeypatch):
    """Workspace output returns label/value choices, deduped by PDF URL."""
    _patch_billstatus(monkeypatch, _TV_RECORD)
    result = asyncio.run(helpers.get_bill_text_choices("119/hr/29", is_workspace=True))
    assert len(result) == 2
    assert result[0]["value"].endswith("/BILLS-119hr29pcs.pdf")
    assert result[0]["label"].startswith("Placed on Calendar Senate")


def test_get_bill_text_choices_workspace_empty(monkeypatch):
    """Workspace output with no text versions returns a placeholder choice."""
    _patch_billstatus(monkeypatch, {"number": 29, "textVersions": []})
    result = asyncio.run(helpers.get_bill_text_choices("119/hr/29", is_workspace=True))
    assert result[0]["value"] == ""


def test_get_bill_text_choices_workspace_no_date(monkeypatch):
    """A workspace version with no date uses the document name as the label."""
    record = {
        "number": 29,
        "textVersions": [
            {
                "type": "Introduced",
                "date": "",
                "formats": [{"url": f"{_PKG}/BILLS-119hr29ih/xml/BILLS-119hr29ih.xml"}],
            }
        ],
    }
    _patch_billstatus(monkeypatch, record)
    result = asyncio.run(helpers.get_bill_text_choices("119/hr/29", is_workspace=True))
    assert result[0]["label"] == "BILLS-119hr29ih.pdf"


def _patch_amendment(monkeypatch, documents, record=None):
    """Patch the bulk amendment record loader and link-service resolver."""

    async def _record(amendment_id):
        return record if record is not None else {"type": "SAMDT"}

    async def _resolve(rec):
        return documents

    monkeypatch.setattr(bulk, "load_amendment_record", _record)
    monkeypatch.setattr(bulk, "resolve_amendment_text", _resolve)


_AMD_DOCS = [
    {
        "format": "HTML",
        "format_key": "htm",
        "date": "2025-01-01",
        "url": "https://www.govinfo.gov/content/pkg/CREC-2025-01-01/html/CREC-2025-01-01-pt1-PgS1.htm",
    },
    {
        "format": "PDF",
        "format_key": "pdf",
        "date": "2025-01-01",
        "url": "https://www.govinfo.gov/content/pkg/CREC-2025-01-01/pdf/CREC-2025-01-01-pt1-PgS1.pdf",
    },
]


def test_get_amendment_text_choices_workspace_pdf_only(monkeypatch):
    """Workspace mode offers only PDFs (the viewer cannot render HTML)."""
    _patch_amendment(monkeypatch, _AMD_DOCS)
    result = asyncio.run(
        helpers.get_amendment_text_choices("119-samdt-1", is_workspace=True)
    )
    assert len(result) == 1
    assert result[0]["label"].startswith("Congressional Record - 2025-01-01")
    assert result[0]["value"].endswith(".pdf")
    assert not any(c["value"].endswith(".htm") for c in result)


def test_get_amendment_text_choices_workspace_html_only(monkeypatch):
    """When only HTML resolves, the viewer shows the no-text placeholder."""
    _patch_amendment(
        monkeypatch,
        [
            {
                "format": "HTML",
                "format_key": "htm",
                "date": "2025-01-01",
                "url": "https://x/a.htm",
            }
        ],
    )
    result = asyncio.run(
        helpers.get_amendment_text_choices("119-samdt-1", is_workspace=True)
    )
    assert result[0]["value"] == ""


def test_get_amendment_text_choices_workspace_no_date(monkeypatch):
    """A PDF without a date uses the no-date label branch."""
    _patch_amendment(
        monkeypatch,
        [{"format": "PDF", "format_key": "pdf", "date": "", "url": "https://x/a.pdf"}],
    )
    result = asyncio.run(
        helpers.get_amendment_text_choices("119-samdt-1", is_workspace=True)
    )
    assert result[0]["label"] == "Congressional Record - a.pdf"


def test_get_amendment_text_choices_non_workspace(monkeypatch):
    """Non-workspace mode groups formats by date into version entries."""
    _patch_amendment(monkeypatch, _AMD_DOCS)
    result = asyncio.run(helpers.get_amendment_text_choices("119-samdt-1"))
    assert result[0]["version_type"] == "Congressional Record"
    assert result[0]["version_date"] == "2025-01-01"
    assert result[0]["htm"].endswith(".htm")
    assert result[0]["pdf"].endswith(".pdf")


def test_get_amendment_text_choices_none_non_workspace(monkeypatch):
    """No resolvable documents raises a 404 in non-workspace mode."""
    _patch_amendment(monkeypatch, [])
    with pytest.raises(HTTPException) as exc:
        asyncio.run(helpers.get_amendment_text_choices("119-hamdt-2"))
    assert exc.value.status_code == 404


def test_get_amendment_text_choices_none_workspace(monkeypatch):
    """No resolvable documents returns a placeholder choice in workspace mode."""
    _patch_amendment(monkeypatch, [])
    result = asyncio.run(
        helpers.get_amendment_text_choices("119-hamdt-2", is_workspace=True)
    )
    assert result[0]["value"] == ""


_RESULTS_HTML = """
<ol class="basic-search-results-lists expanded-view results">
<li>
  <span class="visualIndicator">Hearing</span>
  <span class="result-heading"><a href="/event/119/senate-event/12345">S.Hrg. 119-1</a></span>
  <span class="result-title">A Hearing About Things</span>
  <span class="result-item"><strong>Committee:</strong> <a>Armed Services</a></span>
  <span class="result-item">January 1, 2025</span>
</li>
<li>separator</li>
<li>
  <span class="visualIndicator">Report</span>
  <span class="result-heading"><a href="/report/119/srpt/2">S.Rept. 119-2</a></span>
</li>
<li>separator</li>
<li>
  <span class="visualIndicator">NoLink</span>
  <span class="result-heading">No href here</span>
</li>
<li>separator</li>
<li>
  <span class="result-heading"><a href="/x/1">No indicator</a></span>
</li>
<li>separator</li>
</ol>
"""


def test_congress_search_decode():
    """HTML entities and whitespace are normalised."""
    assert congress_search._decode("a &amp; b&mdash;c   d") == "a & b—c d"


def test_congress_search_parse_page():
    """_parse_page extracts type, url, heading, title, and metadata."""
    docs = congress_search._parse_page(_RESULTS_HTML)
    assert len(docs) == 2
    assert docs[0]["type"] == "Hearing"
    assert docs[0]["title"] == "A Hearing About Things"
    assert docs[0]["Committee"] == "Armed Services"
    assert docs[0]["date"] == "January 1, 2025"
    assert docs[1]["type"] == "Report"
    assert "title" not in docs[1]


def test_congress_search_parse_page_no_results():
    """A page with no results section returns an empty list."""
    assert congress_search._parse_page("<html>nope</html>") == []


def test_congress_search_get_total():
    """_get_total reads the total result count, defaulting to 0."""
    assert congress_search._get_total("Showing 1 - 250 of 1,234 results") == 1234
    assert congress_search._get_total("no totals here") == 0


def _patch_search_client(monkeypatch, pages):
    """Patch httpx.AsyncClient with a stub returning canned page HTML."""

    class _Resp:
        def __init__(self, text):
            self.text = text

        def raise_for_status(self):
            """No-op."""

    class _Client:
        def __init__(self, *args, **kwargs):
            self._calls = 0

        async def __aenter__(self):
            return self

        async def __aexit__(self, *exc):
            return False

        async def get(self, url, params=None):
            if params is None:
                return _Resp("")
            page = int(params.get("page", "1"))
            return _Resp(pages.get(page, ""))

    monkeypatch.setattr(congress_search.httpx, "AsyncClient", _Client)
    monkeypatch.setattr(congress_search.asyncio, "sleep", _coro_noop)


async def _coro_noop(*args, **kwargs):
    """Awaitable no-op replacement for asyncio.sleep."""
    return None


def test_search_async_single_page(monkeypatch):
    """A single page of results is parsed and tagged with the congress."""
    _patch_search_client(monkeypatch, {1: _RESULTS_HTML + "1 - 2 of 2"})
    result = asyncio.run(
        congress_search.search_async(
            congress=119,
            sources=["committee-meetings"],
            committee="Armed Services",
            chamber="senate",
        )
    )
    assert result
    assert all(d["congress"] == 119 for d in result)


def test_search_async_pagination(monkeypatch):
    """A total larger than the page size fetches and merges remaining pages."""
    page1 = _RESULTS_HTML + "1 - 250 of 300 results"
    page2 = _RESULTS_HTML
    _patch_search_client(monkeypatch, {1: page1, 2: page2})
    result = asyncio.run(
        congress_search.search_async(congress=119, sources=["comreports"])
    )
    assert len(result) == 4


def test_search_async_merge_chambers(monkeypatch):
    """A committee with no chamber merges and dedupes across all chambers."""
    _patch_search_client(monkeypatch, {1: _RESULTS_HTML + "1 - 2 of 2"})
    result = asyncio.run(
        congress_search.search_async(
            congress=119, sources=["comreports"], committee="Armed Services"
        )
    )
    assert len(result) == 2
