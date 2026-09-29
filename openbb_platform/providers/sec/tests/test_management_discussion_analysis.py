"""Unit tests for ``management_discussion_analysis.py``.

The module's two big static methods are exercised offline:

* ``transform_data`` is pure given synthetic ``data`` dicts containing
  raw HTML.  Crafted fixtures drive the 10-K / 10-Q / 20-F header paths,
  the Table-of-Contents normaliser, the stub cross-reference anchor
  extraction, the EX-13 / EX-99 exhibit fallbacks, the full-document
  fallback, and the various ``EmptyDataError`` branches.

* ``aextract_data`` performs network I/O.  Every transport is mocked:
  ``SecCompanyFilingsFetcher.fetch_data`` (filing discovery) and
  ``openbb_sec.utils.cache.cached_request`` (document downloads) are
  patched at their real attributes so no request leaves the process.
"""

import asyncio
from datetime import date
from unittest.mock import patch

import pytest
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.utils.errors import EmptyDataError

import openbb_sec.models.management_discussion_analysis as mda_mod
from openbb_sec.models.company_filings import SecCompanyFilingsData
from openbb_sec.models.management_discussion_analysis import (
    SecManagementDiscussionAnalysisData,
    SecManagementDiscussionAnalysisFetcher,
    SecManagementDiscussionAnalysisQueryParams,
)

F = SecManagementDiscussionAnalysisFetcher
Q = SecManagementDiscussionAnalysisQueryParams

_FS_FROM_URL = "openbb_sec.models.sec_financials.FinancialStatements.from_url"


@pytest.fixture(autouse=True)
def _no_network_fallback():
    """Make the full-submission MD&A fallback fail closed (no network in tests)."""
    with patch(_FS_FROM_URL, side_effect=RuntimeError("no network in tests")):
        yield


# ---------------------------------------------------------------------------
# fixtures / helpers
# ---------------------------------------------------------------------------

# Distinct words so the html-to-markdown converter does not de-duplicate
# the synthetic body paragraphs (it collapses near-identical lines).
_WORDS = [
    "Revenue",
    "Costs",
    "Margins",
    "Cashflow",
    "Liquidity",
    "Capital",
    "Segment",
    "Guidance",
    "Inventory",
    "Receivables",
    "Debt",
    "Equity",
    "Goodwill",
    "Taxes",
    "Pension",
    "Hedging",
    "Currency",
    "Backlog",
    "Orders",
    "Dividends",
]


def _body(label: str = "discussion") -> str:
    """Return >15 unique body <p> paragraphs (needed for _find_end)."""
    return "\n".join(
        f"<p>{w} {label} paragraph {i}: detailed analysis of {w} trends "
        f"during the fiscal period under review with specifics.</p>"
        for i, w in enumerate(_WORDS)
    )


def _data(content: str, report_type: str = "10-K", **extra):
    base = {
        "symbol": "AAPL",
        "calendar_year": 2023,
        "calendar_period": 4,
        "period_ending": date(2023, 12, 31),
        "report_type": report_type,
        "url": "https://www.sec.gov/Archives/edgar/data/1/b.htm",
        "content": content,
    }
    base.update(extra)
    return base


def _filing(form, filing_date, report_date, report_url, index_url):
    return SecCompanyFilingsData(
        form=form,
        filingDate=filing_date,
        reportDate=report_date,
        primaryDocumentUrl=report_url,
        filingDetailUrl=index_url,
    )


# ===========================================================================
# transform_data — pure paths
# ===========================================================================


def test_transform_query_builds_params():
    """transform_query returns the SEC query model."""
    q = F.transform_query({"symbol": "aapl"})
    assert isinstance(q, Q)
    assert q.symbol == "AAPL"
    assert q.include_tables is True


def test_transform_data_raw_html_passthrough():
    """raw_html=True returns the data dict verbatim (line 799)."""
    q = Q(symbol="AAPL", raw_html=True)
    data = _data("<html><body>anything</body></html>")
    res = F.transform_data(q, data)
    assert isinstance(res, SecManagementDiscussionAnalysisData)
    assert res.content == "<html><body>anything</body></html>"


def test_transform_data_empty_markdown_raises():
    """Empty conversion output raises EmptyDataError (line 815)."""
    q = Q(symbol="AAPL")
    # Content with no extractable text -> markdown is empty.
    data = _data("<html><body><!-- comment only --></body></html>")
    with pytest.raises(EmptyDataError) as exc:
        F.transform_data(q, data)
    assert "No content was found" in str(exc.value)


def test_transform_data_empty_after_strip_raises():
    """A section whose body is only running headers strips to empty (line 1461).

    No ``Item 7`` header is present, so the standalone-heading fallback locates
    the section.  Every line matches the repeated running-page-header regex, so
    ``mda_content`` is empty after stripping and ``EmptyDataError`` is raised.
    """
    q = Q(symbol="AAPL")
    hdr = (
        "Management's Discussion and Analysis of Financial Condition "
        "and Results of Operations"
    )
    # Distinct trailing words keep the converter from de-duplicating the
    # repeated header lines; all of them are removed by the running-header sub.
    body = "".join(
        f"<p>{hdr} {w}</p>" for w in ("Alpha", "Bravo", "Charlie", "Delta", "Echo")
    )
    data = _data(f"<html><body>{body}</body></html>")
    with pytest.raises(EmptyDataError) as exc:
        F.transform_data(q, data)
    assert "empty after extraction" in str(exc.value)


def test_transform_data_10k_happy_path():
    """10-K Item 7 extraction stops at the Item 7A end marker."""
    html = (
        "<html><body>"
        "<h2>Item 7. Management's Discussion and Analysis of Financial "
        "Condition and Results of Operations</h2>"
        f"{_body()}"
        "<h2>Item 7A. Quantitative and Qualitative Disclosures About "
        "Market Risk</h2><p>Out of scope market risk content here.</p>"
        "</body></html>"
    )
    res = F.transform_data(Q(symbol="AAPL"), _data(html))
    assert "Revenue discussion" in res.content
    assert "Dividends discussion" in res.content
    # End marker excluded.
    assert "Item 7A" not in res.content


def test_transform_data_10q_quarterly_end_patterns():
    """10-Q uses the quarterly end patterns (Item 3/4)."""
    html = (
        "<html><body>"
        "<h2>Item 2. Management's Discussion and Analysis of Financial "
        "Condition and Results of Operations</h2>"
        f"{_body('quarterly')}"
        "<h2>Item 3. Quantitative and Qualitative Disclosures About "
        "Market Risk</h2><p>Out of scope.</p>"
        "</body></html>"
    )
    res = F.transform_data(Q(symbol="AAPL"), _data(html, report_type="10-Q"))
    assert "Revenue quarterly" in res.content
    assert "Item 3" not in res.content


def test_transform_data_20f_item5_path():
    """20-F uses Item 5 'Operating and Financial Review' (lines 1043,1052)."""
    html = (
        "<html><body>"
        "<h2>Item 5. Operating and Financial Review and Prospects</h2>"
        f"{_body('review')}"
        "<h2>Item 6. Directors, Senior Management and Employees</h2>"
        "<p>Out of scope content.</p>"
        "</body></html>"
    )
    res = F.transform_data(Q(symbol="SHOP"), _data(html, report_type="20-F"))
    assert "Revenue review" in res.content
    assert "Item 6" not in res.content


def test_transform_data_split_header_bare_item():
    """Bare 'Item 2.' on one line, MD&A title on the next (lines 1164-1178)."""
    html = (
        "<html><body>"
        "<p>Item 2.</p>"
        "<p>Management's Discussion and Analysis of Financial Condition "
        "and Results of Operations</p>"
        f"{_body('split')}"
        "<h2>Item 3. Other</h2><p>Out of scope.</p>"
        "</body></html>"
    )
    res = F.transform_data(Q(symbol="AAPL"), _data(html, report_type="10-Q"))
    # The bare "Item 2." header is recognised and the section body extracted.
    assert "## Item 2." in res.content
    assert "Dividends split" in res.content


def test_transform_data_mixed_case_header_inline_remainder():
    """Mixed-case 'Item 7.' header with body text on the same line (line 1568)."""
    html = (
        "<html><body>"
        "<p>Item 7. Management's Discussion and Analysis of Financial Condition"
        " and Results of Operations The following discussion should be read"
        " together with the financial statements.</p>"
        f"{_body('inline')}"
        "<h2>Item 8. Financial Statements</h2><p>Out of scope.</p>"
        "</body></html>"
    )
    res = F.transform_data(Q(symbol="AAPL"), _data(html))
    assert res.content.startswith("## Item 7. Management's Discussion")
    assert "The following discussion should be read" in res.content


def test_transform_data_standalone_heading_fallback():
    """No Item number; standalone MD&A heading fallback (lines 1181-1195)."""
    html = (
        "<html><body>"
        "<h2>Management's Discussion and Analysis of Financial Condition "
        "and Results of Operations</h2>"
        f"{_body('standalone')}"
        "</body></html>"
    )
    res = F.transform_data(Q(symbol="AAPL"), _data(html))
    assert "Revenue standalone" in res.content


def test_transform_data_caps_title_prefix():
    """ALL-CAPS plain-text 'ITEM 7.' title gets a markdown prefix (1505-1516)."""
    html = (
        "<html><body>"
        "<p>ITEM 7. MANAGEMENT'S DISCUSSION AND ANALYSIS OF FINANCIAL "
        "CONDITION</p>"
        f"{_body('caps')}"
        "<p>ITEM 7A. QUANTITATIVE DISCLOSURES</p><p>out of scope.</p>"
        "</body></html>"
    )
    res = F.transform_data(Q(symbol="AAPL"), _data(html))
    assert res.content.startswith("## ITEM 7. MANAGEMENT'S DISCUSSION")


def test_transform_data_toc_table_normalized():
    """A Table-of-Contents markdown table is rebuilt (lines 856-915)."""
    html = (
        "<html><body>"
        "<table>"
        "<tr><td>Table of Contents</td><td></td><td></td><td></td></tr>"
        '<tr><td><a href="#s1">3</a></td><td>Business</td>'
        '<td><a href="#s2">5</a></td><td>Risk Factors</td></tr>'
        '<tr><td><a href="#s3">7</a></td><td>MD&A</td>'
        "<td></td><td></td></tr>"
        "<tr><td>Plain text only</td><td></td><td></td><td></td></tr>"
        "</table>"
        "<h2>Item 7. Management's Discussion and Analysis of Financial "
        "Condition and Results of Operations</h2>"
        f"{_body('toc')}"
        "<h2>Item 7A. Disclosures</h2><p>scope-out.</p>"
        "</body></html>"
    )
    res = F.transform_data(Q(symbol="AAPL"), _data(html))
    # The normalised TOC header is present in the converted markdown.
    assert "Revenue toc" in res.content


def test_transform_data_caps_title_with_blank_line():
    """ALL-CAPS title alone on a line, then blank, then body (1491-1516)."""
    body = "\n".join(
        f"<p>{w} discussion paragraph {i}: detailed analysis here for the "
        f"period under review.</p>"
        for i, w in enumerate(_WORDS)
    )
    title = (
        "ITEM 7. MANAGEMENT'S DISCUSSION AND ANALYSIS OF FINANCIAL "
        "CONDITION AND RESULTS OF OPERATIONS"
    )
    # A markdown table immediately after the title prevents the converter
    # from merging the first body paragraph onto the title line, so the
    # caps title stands alone followed by a blank line.  This drives the
    # blank-break (1491-1492) and split_idx-None (1505-1506) branches.
    tbl = (
        "<table><tr><td>Metric</td><td>2023</td></tr>"
        "<tr><td>Sales</td><td>100</td></tr></table>"
    )
    html = (
        f"<html><body><table><tr><td>{title}</td></tr></table>{tbl}"
        f"{body}<p>ITEM 7A. DISCLOSURES</p><p>scope out.</p></body></html>"
    )
    res = F.transform_data(Q(symbol="AAPL"), _data(html))
    assert res.content.startswith("## ITEM 7. MANAGEMENT'S DISCUSSION")


def test_transform_data_toc_all_rows_filtered():
    """TOC table whose rows all say 'Table of Contents' -> no rebuild (909)."""
    body = "".join(
        f"<p>Para {w} number {i} unique content for the section body.</p>"
        for i, w in enumerate(_WORDS)
    )
    html = (
        "<html><body><table>"
        "<tr><td>Table of Contents</td><td>x</td><td>y</td><td>z</td></tr>"
        "<tr><td>Table of Contents continued</td><td>a</td><td>b</td>"
        "<td>c</td></tr>"
        "<tr><td>Table of Contents again</td><td>d</td><td>e</td>"
        "<td>f</td></tr>"
        "</table>"
        "<h2>Item 7. Management's Discussion and Analysis of Financial "
        "Condition and Results of Operations</h2>"
        f"{body}"
        "<h2>Item 7A. Disclosures</h2><p>scope out.</p>"
        "</body></html>"
    )
    res = F.transform_data(Q(symbol="AAPL"), _data(html))
    assert "Para Revenue" in res.content


def test_transform_data_toc_table_at_eof_raises():
    """TOC table that runs to end-of-document (lines 866-867), no MD&A."""
    html = (
        "<html><body><table>"
        "<tr><td>Table of Contents</td><td></td><td></td><td></td></tr>"
        '<tr><td><a href="#s1">3</a></td><td>Business</td>'
        "<td></td><td></td></tr>"
        '<tr><td><a href="#s2">5</a></td><td>Risk</td>'
        "<td></td><td></td></tr>"
        "</table></body></html>"
    )
    with pytest.raises(EmptyDataError):
        F.transform_data(Q(symbol="AAPL"), _data(html))


def test_transform_data_no_mda_section_raises():
    """No locatable MD&A section, and the full-text fallback is empty, raises."""
    html = (
        "<html><body><h2>Item 1. Business</h2>"
        "<p>Just business description, no MD&A anywhere in this filing.</p>"
        "</body></html>"
    )
    with pytest.raises(EmptyDataError) as exc:
        F.transform_data(Q(symbol="AAPL"), _data(html))
    assert "Could not locate the MD&A section" in str(exc.value)


def test_mda_from_full_text_returns_item():
    from types import SimpleNamespace

    fs = SimpleNamespace(get_item=lambda _n: {"text": "  Item 7 MD&A body.  "})
    with patch(_FS_FROM_URL, return_value=fs):
        assert mda_mod._mda_from_full_text("u", True) == "Item 7 MD&A body."


def test_mda_from_full_text_no_item():
    from types import SimpleNamespace

    fs = SimpleNamespace(get_item=lambda _n: None)
    with patch(_FS_FROM_URL, return_value=fs):
        assert mda_mod._mda_from_full_text("u", True) == ""


def test_transform_data_full_text_fallback():
    html = (
        "<html><body><h2>Item 1. Business</h2><p>No MD&A here at all.</p></body></html>"
    )
    with patch.object(mda_mod, "_mda_from_full_text", return_value="**MD&A**\n\nbody"):
        res = F.transform_data(Q(symbol="AAPL"), _data(html))
    assert res.content == "**MD&A**\n\nbody"


# ---- stub / cross-reference anchor extraction ----------------------------


def test_transform_data_stub_anchor_extraction():
    """Stub Item 7 -> follow anchor into Financial Section (1146-1352)."""
    mda_body = " ".join(
        f"Detailed {w} analysis paragraph covering operating results and "
        f"trends across all segments."
        for w in (_WORDS * 3)
    )
    html = (
        "<html><body>"
        "<p>Item 7. Management's Discussion and Analysis. Reference is made "
        'to the information under <a href="#finsec">Financial Section</a> '
        "of this report.</p>"
        "<p>Item 8. Financial Statements and Supplementary Data. The "
        "information is in the Financial Section.</p>"
        '<div id="finsec">Financial Section Table of Contents</div>'
        "<table>"
        # Short link text (< 4 chars) -> skipped (line 1290-1291).
        '<tr><td><a href="#pg">Go</a></td></tr>'
        '<tr><td><a href="#mdaanchor">Management\'s Discussion and '
        "Analysis</a></td></tr>"
        # Duplicate anchor id already in _seen_toc -> skipped (line 1290-1291).
        '<tr><td><a href="#mdaanchor">Management\'s Discussion and '
        "Analysis (cont.)</a></td></tr>"
        '<tr><td><a href="#finstmtanchor">Consolidated Financial '
        "Statements</a></td></tr>"
        '<tr><td><a href="#auditanchor">Report of Independent Registered '
        "Public Accounting Firm</a></td></tr>"
        "</table>"
        '<h2 id="mdaanchor">Management\'s Discussion and Analysis</h2>'
        f"<p>{mda_body}</p>"
        '<h2 id="finstmtanchor">Consolidated Financial Statements</h2>'
        "<p>Balance sheet line items out of scope here.</p>"
        '<h2 id="auditanchor">Report of Independent Registered Public '
        "Accounting Firm</h2><p>Auditor opinion out of scope.</p>"
        "</body></html>"
    )
    res = F.transform_data(Q(symbol="CVX"), _data(html))
    assert "revenue analysis" in res.content.lower()
    # Cut at the post-MD&A anchor: financial statements excluded.
    assert "Auditor opinion" not in res.content


def test_transform_data_stub_crossref_then_no_anchor_raises():
    """A stub Item 7 with cross-ref text but no anchor -> EmptyDataError."""
    html = (
        "<html><body>"
        "<h2>Item 7. Management's Discussion and Analysis</h2>"
        "<p>The information required by this item is incorporated herein "
        "by reference to the Annual Report.</p>"
        "<h2>Item 8. Financial Statements</h2>"
        "<p>See the financial statements.</p>"
        "</body></html>"
    )
    with pytest.raises(EmptyDataError):
        F.transform_data(Q(symbol="AAPL"), _data(html))


# ---- exhibit fallbacks ----------------------------------------------------


def test_transform_data_exhibit_fallback_foreign():
    """40-F MD&A lives in a pre-fetched exhibit; end marker cuts it (1360-1415)."""
    # >15 unique body paragraphs so the exhibit end marker is honoured.
    ex_body = "\n".join(
        f"<p>{w} foreign analysis paragraph {i}: detailed review of {w} "
        f"results for the fiscal year.</p>"
        for i, w in enumerate(_WORDS)
    )
    main_html = (
        "<html><body><p>Cover page of the 40-F annual report. See "
        "exhibits for details.</p></body></html>"
    )
    ex_html = (
        "<html><body>"
        "<h2>Management's Discussion and Analysis</h2>"
        f"{ex_body}"
        "<h2>Report of Independent Registered Public Accounting Firm</h2>"
        "<p>Auditor opinion out of scope.</p>"
        "</body></html>"
    )
    data = _data(
        main_html,
        report_type="40-F",
        exhibit_content=ex_html,
        exhibit_url="https://www.sec.gov/Archives/edgar/data/1/ex99.htm",
    )
    res = F.transform_data(Q(symbol="SHOP"), data)
    assert "Revenue foreign analysis" in res.content
    # The end marker after the body excludes the auditor section.
    assert "Auditor opinion" not in res.content
    assert res.url == "https://www.sec.gov/Archives/edgar/data/1/ex99.htm"


def test_transform_data_exhibit_full_document_fallback():
    """6-K slide deck / update returns the whole exhibit (lines 1421-1428)."""
    main_html = (
        "<html><body><p>6-K cover page. Q4 2025 Update attached as "
        "exhibit.</p></body></html>"
    )
    ex_html = (
        "<html><body><h2>Q4 2025 Shareholder Update</h2>"
        "<p>Highlights of the quarter for investors and stakeholders "
        "worldwide.</p>"
        "<p>Revenue grew nicely this period across all business lines.</p>"
        "</body></html>"
    )
    data = _data(
        main_html,
        report_type="6-K",
        calendar_year=2025,
        exhibit_content=ex_html,
        exhibit_url="https://www.sec.gov/Archives/edgar/data/1/ex99.htm",
        exhibit_is_full_document=True,
    )
    res = F.transform_data(Q(symbol="SHOP"), data)
    assert "Q4 2025 Shareholder Update" in res.content
    assert res.url == "https://www.sec.gov/Archives/edgar/data/1/ex99.htm"


def test_transform_data_exhibit_present_but_no_mda_raises():
    """Exhibit present, not full-document, no MD&A heading -> EmptyDataError."""
    main_html = "<html><body><p>Cover page only.</p></body></html>"
    ex_html = (
        "<html><body><h2>Risk Factors</h2><p>Some unrelated exhibit "
        "content without any discussion section.</p></body></html>"
    )
    data = _data(
        main_html,
        report_type="40-F",
        exhibit_content=ex_html,
        exhibit_url="https://www.sec.gov/Archives/edgar/data/1/ex99.htm",
    )
    with pytest.raises(EmptyDataError):
        F.transform_data(Q(symbol="SHOP"), data)


# ===========================================================================
# aextract_data — mocked transports
# ===========================================================================

_GOOD_10K = "<html><body><p>Item 7. MD&amp;A body content here.</p></body></html>"


def _patches(fetch, cached):
    """Return a context-manager pair patching both transports."""
    return patch(
        "openbb_sec.models.company_filings.SecCompanyFilingsFetcher.fetch_data",
        fetch,
    ), patch("openbb_sec.utils.cache.cached_request", cached)


def test_aextract_most_recent_10k():
    """Most-recent 10-K is selected; 8-K lookup returns nothing (245-300)."""
    filings = [
        _filing(
            "10-K",
            date(2024, 2, 1),
            date(2023, 12, 31),
            "https://www.sec.gov/Archives/edgar/data/1/10k.htm",
            "https://www.sec.gov/Archives/edgar/data/1/index.htm",
        )
    ]

    async def fetch(params, creds):  # noqa: ARG001
        return filings if "10-K" in params.get("form_type", "") else []

    async def cached(url, **kwargs):  # noqa: ARG001
        return _GOOD_10K

    p1, p2 = _patches(fetch, cached)
    with p1, p2:
        res = asyncio.run(F.aextract_data(Q(symbol="AAPL", use_cache=False), None))
    assert res["report_type"] == "10-K"
    assert res["url"].endswith("10k.htm")
    assert res["calendar_year"] == 2023


def test_aextract_no_filings_raises():
    """No filings at all -> OpenBBError (lines 148-151)."""

    async def fetch(params, creds):  # noqa: ARG001
        return []

    async def cached(url, **kwargs):  # noqa: ARG001
        return ""

    p1, p2 = _patches(fetch, cached)
    with p1, p2:
        with pytest.raises(OpenBBError) as exc:
            asyncio.run(F.aextract_data(Q(symbol="ZZZZ", use_cache=False), None))
    assert "Could not find any" in str(exc.value)


def test_aextract_numeric_symbol_uses_cik():
    """A numeric symbol is routed through the CIK branch (lines 130-137)."""
    filings = [
        _filing(
            "10-K",
            date(2024, 2, 1),
            date(2023, 12, 31),
            "https://www.sec.gov/Archives/edgar/data/1/10k.htm",
            "https://www.sec.gov/Archives/edgar/data/1/index.htm",
        )
    ]
    seen = {}

    async def fetch(params, creds):  # noqa: ARG001
        seen.update(params)
        return filings if "10-K" in params.get("form_type", "") else []

    async def cached(url, **kwargs):  # noqa: ARG001
        return _GOOD_10K

    p1, p2 = _patches(fetch, cached)
    with p1, p2:
        res = asyncio.run(F.aextract_data(Q(symbol="320193", use_cache=False), None))
    assert seen.get("cik") == "320193"
    assert res["report_type"] == "10-K"


def test_aextract_calendar_year_selects_annual():
    """calendar_year (no period) picks the matching annual filing (313-332)."""
    filings = [
        _filing(
            "10-K",
            date(2023, 2, 1),
            date(2022, 12, 31),
            "https://www.sec.gov/Archives/edgar/data/1/10k_2023.htm",
            "https://www.sec.gov/Archives/edgar/data/1/index23.htm",
        ),
        _filing(
            "10-K",
            date(2022, 2, 1),
            date(2021, 12, 31),
            "https://www.sec.gov/Archives/edgar/data/1/10k_2022.htm",
            "https://www.sec.gov/Archives/edgar/data/1/index22.htm",
        ),
    ]

    async def fetch(params, creds):  # noqa: ARG001
        return filings if "10-K" in params.get("form_type", "") else []

    async def cached(url, **kwargs):  # noqa: ARG001
        return _GOOD_10K

    p1, p2 = _patches(fetch, cached)
    with p1, p2:
        res = asyncio.run(
            F.aextract_data(Q(symbol="AAPL", calendar_year=2023, use_cache=False), None)
        )
    assert res["url"].endswith("10k_2023.htm")
    assert res["calendar_year"] == 2023


def test_aextract_calendar_year_period_selects_quarter():
    """calendar_year + period selects a 10-Q in the quarter window (334-348)."""
    filings = [
        _filing(
            "10-Q",
            date(2023, 5, 1),
            date(2023, 3, 31),
            "https://www.sec.gov/Archives/edgar/data/1/10q_q1.htm",
            "https://www.sec.gov/Archives/edgar/data/1/indexq1.htm",
        ),
    ]

    async def fetch(params, creds):  # noqa: ARG001
        return filings if "10-K" in params.get("form_type", "") else []

    async def cached(url, **kwargs):  # noqa: ARG001
        return _GOOD_10K

    p1, p2 = _patches(fetch, cached)
    with p1, p2:
        res = asyncio.run(
            F.aextract_data(
                Q(
                    symbol="AAPL",
                    calendar_year=2023,
                    calendar_period="Q2",
                    use_cache=False,
                ),
                None,
            )
        )
    assert res["url"].endswith("10q_q1.htm")
    assert res["calendar_period"] == 2


def test_aextract_no_target_filing_raises():
    """Filings exist but none match the requested quarter -> OpenBBError (517)."""
    filings = [
        _filing(
            "10-K",
            date(2018, 2, 1),
            date(2017, 12, 31),
            "https://www.sec.gov/Archives/edgar/data/1/old.htm",
            "https://www.sec.gov/Archives/edgar/data/1/old_index.htm",
        ),
    ]

    async def fetch(params, creds):  # noqa: ARG001
        # 10-K search returns the old filing; 8-K search returns nothing.
        return filings if "10-K" in params.get("form_type", "") else []

    async def cached(url, **kwargs):  # noqa: ARG001
        return ""

    p1, p2 = _patches(fetch, cached)
    with p1, p2:
        with pytest.raises(OpenBBError) as exc:
            asyncio.run(
                F.aextract_data(
                    Q(
                        symbol="AAPL",
                        calendar_year=2023,
                        calendar_period="Q3",
                        use_cache=False,
                    ),
                    None,
                )
            )
    assert "Could not find a filing" in str(exc.value)


def test_aextract_ex13_incorporated_by_reference():
    """10-K stub 'incorporated by reference' -> EX-13 exhibit fetched (548-605)."""
    main_url = "https://www.sec.gov/Archives/edgar/data/1/10k.htm"
    index_url = "https://www.sec.gov/Archives/edgar/data/1/index.htm"
    filings = [
        _filing("10-K", date(2024, 2, 1), date(2023, 12, 31), main_url, index_url)
    ]

    main_html = (
        "<html><body><p>Item 7. The Annual Report is incorporated herein "
        "by reference.</p></body></html>"
    )
    # Index page exercises _extract_exhibit_links edge cases:
    #  - a row with < 4 cells (skipped),
    #  - a non-matching Type row (line 107),
    #  - a matching Type row whose Document cell has no <a href> (line 111),
    #  - the matching EX-13 row whose href carries the /ix?doc= viewer
    #    prefix that must be stripped (line 116).
    index_html = (
        "<html><body><table>"
        "<tr><th>Seq</th><th>Description</th><th>Document</th>"
        "<th>Type</th><th>Size</th></tr>"
        "<tr><td>short</td><td>row</td></tr>"
        "<tr><td>1</td><td>Cover</td>"
        '<td><a href="cover.htm">cover.htm</a></td>'
        "<td>10-K</td><td>500</td></tr>"
        "<tr><td>12</td><td>No link</td><td>plain text</td>"
        "<td>EX-13</td><td>900</td></tr>"
        "<tr><td>13</td><td>Annual Report</td>"
        '<td><a href="/ix?doc=/Archives/edgar/data/1/ex13.htm">ex13.htm</a>'
        "</td><td>EX-13</td><td>1000</td></tr>"
        "</table></body></html>"
    )
    ex13_html = "<html><body><h2>Annual Report</h2><p>MD&amp;A here.</p></body></html>"

    async def fetch(params, creds):  # noqa: ARG001
        return filings if "10-K" in params.get("form_type", "") else []

    async def cached(url, **kwargs):  # noqa: ARG001
        if url == main_url:
            return main_html
        if url == index_url:
            return index_html
        if url.endswith("ex13.htm"):
            return ex13_html
        return ""

    p1, p2 = _patches(fetch, cached)
    with p1, p2:
        res = asyncio.run(F.aextract_data(Q(symbol="AAPL", use_cache=False), None))
    assert res["exhibit_content"] == ex13_html
    assert res["exhibit_url"].endswith("ex13.htm")


def test_aextract_ex99_foreign_issuer_exhibit():
    """40-F MD&A discovered via EX-99 exhibit on the index page (625-695)."""
    main_url = "https://www.sec.gov/Archives/edgar/data/1/40f.htm"
    index_url = "https://www.sec.gov/Archives/edgar/data/1/index.htm"
    filings = [
        _filing("40-F", date(2024, 2, 1), date(2023, 12, 31), main_url, index_url)
    ]

    main_html = "<html><body><p>Cover page of 40-F.</p></body></html>"
    index_html = (
        "<html><body><table>"
        "<tr><th>Seq</th><th>Description</th><th>Document</th>"
        "<th>Type</th><th>Size</th></tr>"
        "<tr><td>99</td><td>MD&A</td>"
        '<td><a href="ex992.htm">ex992.htm</a></td>'
        "<td>EX-99.2</td><td>2000</td></tr>"
        "</table></body></html>"
    )
    ex99_html = (
        "<html><body><h2>Management's Discussion and Analysis</h2>"
        "<p>Foreign issuer MD&amp;A body.</p></body></html>"
    )

    async def fetch(params, creds):  # noqa: ARG001
        # 40-F is found via the main 10-K/40-F search; 6-K returns nothing.
        return filings if "10-K" in params.get("form_type", "") else []

    async def cached(url, **kwargs):  # noqa: ARG001
        if url == main_url:
            return main_html
        if url == index_url:
            return index_html
        if url.endswith("ex992.htm"):
            return ex99_html
        return ""

    p1, p2 = _patches(fetch, cached)
    with p1, p2:
        res = asyncio.run(F.aextract_data(Q(symbol="SHOP", use_cache=False), None))
    assert res["exhibit_url"].endswith("ex992.htm")
    assert "Discussion and Analysis" in res["exhibit_content"]


def test_aextract_unexpected_response_type_raises():
    """A non-string document response raises OpenBBError (lines 782-784)."""
    filings = [
        _filing(
            "10-K",
            date(2024, 2, 1),
            date(2023, 12, 31),
            "https://www.sec.gov/Archives/edgar/data/1/10k.htm",
            "https://www.sec.gov/Archives/edgar/data/1/index.htm",
        )
    ]

    async def fetch(params, creds):  # noqa: ARG001
        return filings if "10-K" in params.get("form_type", "") else []

    async def cached(url, **kwargs):  # noqa: ARG001
        # Bytes (not str) for the document download.
        return b"not a string"

    p1, p2 = _patches(fetch, cached)
    with p1, p2:
        with pytest.raises(OpenBBError) as exc:
            asyncio.run(F.aextract_data(Q(symbol="AAPL", use_cache=False), None))
    assert "Unexpected response" in str(exc.value)


def test_aextract_foreign_6k_more_recent_by_filename():
    """Foreign issuer: a newer 6-K MD&A supersedes the 40-F (lines 185-208)."""
    ann = _filing(
        "40-F",
        date(2024, 3, 1),
        date(2023, 12, 31),
        "https://www.sec.gov/a/40f.htm",
        "https://www.sec.gov/a/40f_index.htm",
    )
    sixk = _filing(
        "6-K",
        date(2024, 8, 1),
        date(2024, 6, 30),
        "https://www.sec.gov/a/6k.htm",
        "https://www.sec.gov/a/6k_index.htm",
    )
    sixk_index = (
        "<html><body><table>"
        "<tr><th>Seq</th><th>Desc</th><th>Document</th><th>Type</th>"
        "<th>Size</th></tr>"
        '<tr><td>99</td><td>MDA</td><td><a href="q2_mda.htm">q2_mda.htm</a>'
        "</td><td>EX-99.1</td><td>5</td></tr>"
        "</table></body></html>"
    )
    ex99 = (
        "<html><body><h2>Management's Discussion and Analysis</h2>"
        "<p>Q2 MD&amp;A body content here for the quarter.</p></body></html>"
    )

    async def fetch(params, creds):  # noqa: ARG001
        ft = params.get("form_type", "")
        if "10-K" in ft:
            return [ann]
        if ft == "6-K":
            return [sixk]
        return []

    async def cached(url, **kwargs):  # noqa: ARG001
        if url == "https://www.sec.gov/a/6k_index.htm":
            return sixk_index
        if url == "https://www.sec.gov/a/6k.htm" or "q2_mda" in url:
            return ex99
        return ""

    p1, p2 = _patches(fetch, cached)
    with p1, p2:
        res = asyncio.run(F.aextract_data(Q(symbol="SHOP", use_cache=False), None))
    assert res["report_type"] == "6-K"
    assert res["url"] == "https://www.sec.gov/a/6k.htm"


def test_aextract_foreign_6k_more_recent_by_cover():
    """Foreign issuer 6-K matched on the second-pass cover page (213-239)."""
    ann = _filing(
        "40-F",
        date(2020, 3, 1),
        date(2019, 12, 31),
        "https://www.sec.gov/a/40f.htm",
        "https://www.sec.gov/a/40f_index.htm",
    )
    sixk = _filing(
        "6-K",
        date(2024, 8, 1),
        date(2024, 6, 30),
        "https://www.sec.gov/a/6k.htm",
        "https://www.sec.gov/a/6k_index.htm",
    )
    sixk_index = (
        "<html><body><table>"
        "<tr><th>Seq</th><th>Desc</th><th>Document</th><th>Type</th>"
        "<th>Size</th></tr>"
        '<tr><td>99</td><td>Update</td><td><a href="update.htm">update.htm'
        "</a></td><td>EX-99.1</td><td>5</td></tr>"
        "</table></body></html>"
    )
    # Filename has no MD&A keyword; cover page describes "Letter to Shareholders".
    sixk_cover = (
        "<html><body><p>Letter to Shareholders for the quarter. Earnings "
        "Release attached as exhibit.</p></body></html>"
    )
    # Exhibit lacks an MD&A title -> full-document path via cover desc.
    ex99 = (
        "<html><body><p>Quarterly results presentation for stakeholders "
        "worldwide.</p></body></html>"
    )

    async def fetch(params, creds):  # noqa: ARG001
        ft = params.get("form_type", "")
        if "10-K" in ft:
            return [ann]
        if ft == "6-K":
            return [sixk]
        return []

    async def cached(url, **kwargs):  # noqa: ARG001
        if url == "https://www.sec.gov/a/6k_index.htm":
            return sixk_index
        if url == "https://www.sec.gov/a/6k.htm":
            return sixk_cover
        if "update" in url:
            return ex99
        return ""

    p1, p2 = _patches(fetch, cached)
    with p1, p2:
        res = asyncio.run(F.aextract_data(Q(symbol="SHOP", use_cache=False), None))
    assert res["report_type"] == "6-K"
    assert res.get("exhibit_is_full_document") is True


def test_aextract_domestic_8k_more_recent_earnings():
    """Domestic issuer: a newer 8-K earnings release supersedes 10-K (257-300)."""
    tenk = _filing(
        "10-K",
        date(2024, 2, 1),
        date(2023, 12, 31),
        "https://www.sec.gov/a/10k.htm",
        "https://www.sec.gov/a/10k_index.htm",
    )
    eightk = _filing(
        "8-K",
        date(2024, 7, 15),
        date(2024, 6, 30),
        "https://www.sec.gov/a/8k.htm",
        "https://www.sec.gov/a/8k_index.htm",
    )
    eightk_index = (
        "<html><body><table>"
        "<tr><th>Seq</th><th>Desc</th><th>Document</th><th>Type</th>"
        "<th>Size</th></tr>"
        '<tr><td>99</td><td>PR</td><td><a href="earnings.htm">earnings.htm'
        "</a></td><td>EX-99.1</td><td>5</td></tr>"
        "</table></body></html>"
    )
    eightk_cover = (
        "<html><body><p>Item 2.02 Results of Operations and Financial "
        "Condition. Earnings Release attached.</p></body></html>"
    )
    ex99 = (
        "<html><body><h2>Management's Discussion and Analysis</h2>"
        "<p>Q2 earnings MD&amp;A body content.</p></body></html>"
    )

    async def fetch(params, creds):  # noqa: ARG001
        ft = params.get("form_type", "")
        if "10-K" in ft:
            return [tenk]
        if ft == "8-K":
            return [eightk]
        return []

    async def cached(url, **kwargs):  # noqa: ARG001
        if url == "https://www.sec.gov/a/8k_index.htm":
            return eightk_index
        if url == "https://www.sec.gov/a/8k.htm":
            return eightk_cover
        if "earnings" in url:
            return ex99
        if url == "https://www.sec.gov/a/10k.htm":
            return "<html><body><p>10-K content.</p></body></html>"
        return ""

    p1, p2 = _patches(fetch, cached)
    with p1, p2:
        res = asyncio.run(F.aextract_data(Q(symbol="AAPL", use_cache=False), None))
    assert res["report_type"] == "8-K"
    assert res["url"] == "https://www.sec.gov/a/8k.htm"


def test_aextract_domestic_8k_multi_exhibit_slide_deck():
    """8-K with two EX-99 exhibits + slide deck -> combined full document."""
    tenk = _filing(
        "10-K",
        date(2024, 2, 1),
        date(2023, 12, 31),
        "https://www.sec.gov/a/10k.htm",
        "https://www.sec.gov/a/10k_index.htm",
    )
    eightk = _filing(
        "8-K",
        date(2024, 7, 15),
        date(2024, 6, 30),
        "https://www.sec.gov/a/8k.htm",
        "https://www.sec.gov/a/8k_index.htm",
    )
    eightk_index = (
        "<html><body><table>"
        "<tr><th>Seq</th><th>Desc</th><th>Document</th><th>Type</th>"
        "<th>Size</th></tr>"
        '<tr><td>99</td><td>PR</td><td><a href="ex991.htm">ex991.htm</a>'
        "</td><td>EX-99.1</td><td>5</td></tr>"
        '<tr><td>99</td><td>Slides</td><td><a href="ex992.htm">ex992.htm'
        "</a></td><td>EX-99.2</td><td>9</td></tr>"
        "</table></body></html>"
    )
    eightk_cover = (
        "<html><body><p>Item 2.02 Results of Operations. Earnings Release "
        "attached.</p></body></html>"
    )
    ex991 = (
        "<html><body><p>Press release highlights for investors and the "
        "quarter.</p></body></html>"
    )
    ex992 = (
        '<html><body><div class="slide"><img src="a.png"/></div>'
        "<p>Slide deck quarterly update.</p></body></html>"
    )

    async def fetch(params, creds):  # noqa: ARG001
        ft = params.get("form_type", "")
        if "10-K" in ft:
            return [tenk]
        if ft == "8-K":
            return [eightk]
        return []

    async def cached(url, **kwargs):  # noqa: ARG001
        if url == "https://www.sec.gov/a/8k_index.htm":
            return eightk_index
        if url == "https://www.sec.gov/a/8k.htm":
            return eightk_cover
        if "ex991" in url:
            return ex991
        if "ex992" in url:
            return ex992
        return ""

    p1, p2 = _patches(fetch, cached)
    with p1, p2:
        res = asyncio.run(F.aextract_data(Q(symbol="AAPL", use_cache=False), None))
    assert res["report_type"] == "8-K"
    assert res.get("exhibit_is_full_document") is True
    assert "additional exhibit" in res["exhibit_content"]


def test_aextract_foreign_6k_quarterly_fallback():
    """Foreign 6-K quarterly fallback for a specific quarter (lines 370-446)."""
    ann = _filing(
        "40-F",
        date(2020, 3, 1),
        date(2019, 12, 31),
        "https://www.sec.gov/a/40f.htm",
        "https://www.sec.gov/a/40f_index.htm",
    )
    sixk = _filing(
        "6-K",
        date(2024, 5, 15),
        date(2024, 3, 31),
        "https://www.sec.gov/a/6k.htm",
        "https://www.sec.gov/a/6k_index.htm",
    )
    sixk_index = (
        "<html><body><table>"
        "<tr><th>Seq</th><th>Desc</th><th>Document</th><th>Type</th>"
        "<th>Size</th></tr>"
        '<tr><td>99</td><td>MDA</td><td><a href="q1_quarterly.htm">'
        "q1_quarterly.htm</a></td><td>EX-99.1</td><td>5</td></tr>"
        "</table></body></html>"
    )
    ex99 = (
        "<html><body><h2>Management's Discussion and Analysis</h2>"
        "<p>Quarterly MD&amp;A body content.</p></body></html>"
    )

    async def fetch(params, creds):  # noqa: ARG001
        ft = params.get("form_type", "")
        if "10-K" in ft:
            return [ann]
        if ft == "6-K":
            return [sixk]
        return []

    async def cached(url, **kwargs):  # noqa: ARG001
        if url == "https://www.sec.gov/a/6k_index.htm":
            return sixk_index
        if url == "https://www.sec.gov/a/6k.htm" or "quarterly" in url:
            return ex99
        return ""

    p1, p2 = _patches(fetch, cached)
    with p1, p2:
        res = asyncio.run(
            F.aextract_data(
                Q(
                    symbol="SHOP",
                    calendar_year=2024,
                    calendar_period="Q2",
                    use_cache=False,
                ),
                None,
            )
        )
    assert res["report_type"] == "6-K"


def test_aextract_domestic_8k_quarterly_fallback():
    """Domestic 8-K quarterly fallback for a specific quarter (lines 468-515)."""
    tenk = _filing(
        "10-K",
        date(2020, 2, 1),
        date(2019, 12, 31),
        "https://www.sec.gov/a/10k.htm",
        "https://www.sec.gov/a/10k_index.htm",
    )
    eightk = _filing(
        "8-K",
        date(2024, 5, 15),
        date(2024, 3, 31),
        "https://www.sec.gov/a/8k.htm",
        "https://www.sec.gov/a/8k_index.htm",
    )
    eightk_index = (
        "<html><body><table>"
        "<tr><th>Seq</th><th>Desc</th><th>Document</th><th>Type</th>"
        "<th>Size</th></tr>"
        '<tr><td>99</td><td>PR</td><td><a href="earnings.htm">earnings.htm'
        "</a></td><td>EX-99.1</td><td>5</td></tr>"
        "</table></body></html>"
    )
    eightk_cover = (
        "<html><body><p>Q1 2024 Earnings Release. Press Release of operating "
        "results.</p></body></html>"
    )
    ex99 = (
        "<html><body><h2>Management's Discussion and Analysis</h2>"
        "<p>Q1 earnings MD&amp;A body content.</p></body></html>"
    )

    async def fetch(params, creds):  # noqa: ARG001
        ft = params.get("form_type", "")
        if "10-K" in ft:
            return [tenk]
        if ft == "8-K":
            return [eightk]
        return []

    async def cached(url, **kwargs):  # noqa: ARG001
        if url == "https://www.sec.gov/a/8k_index.htm":
            return eightk_index
        if url == "https://www.sec.gov/a/8k.htm":
            return eightk_cover
        if "earnings" in url:
            return ex99
        return ""

    p1, p2 = _patches(fetch, cached)
    with p1, p2:
        res = asyncio.run(
            F.aextract_data(
                Q(
                    symbol="AAPL",
                    calendar_year=2024,
                    calendar_period="Q2",
                    use_cache=False,
                ),
                None,
            )
        )
    assert res["report_type"] == "8-K"


def test_aextract_ex99_weak_mda_fallback():
    """EX-99 chosen by the weak 'MD&A' abbreviation fallback (lines 690-695)."""
    main_url = "https://www.sec.gov/a/40f.htm"
    index_url = "https://www.sec.gov/a/index.htm"
    filings = [
        _filing("40-F", date(2024, 2, 1), date(2023, 12, 31), main_url, index_url)
    ]
    main_html = "<html><body><p>Cover page of 40-F.</p></body></html>"
    index_html = (
        "<html><body><table>"
        "<tr><th>Seq</th><th>Desc</th><th>Document</th><th>Type</th>"
        "<th>Size</th></tr>"
        '<tr><td>99</td><td>AIF</td><td><a href="aif.htm">aif.htm</a></td>'
        "<td>EX-99.1</td><td>5</td></tr>"
        "</table></body></html>"
    )
    # No full MD&A title, only the 'MD&A' abbreviation -> weak pass 2 selects it.
    ex99 = (
        "<html><body><p>Annual Information Form. Refer to the MD&amp;A for "
        "details.</p></body></html>"
    )

    async def fetch(params, creds):  # noqa: ARG001
        return filings if "10-K" in params.get("form_type", "") else []

    async def cached(url, **kwargs):  # noqa: ARG001
        if url == main_url:
            return main_html
        if url == index_url:
            return index_html
        if "aif" in url:
            return ex99
        return ""

    p1, p2 = _patches(fetch, cached)
    with p1, p2:
        res = asyncio.run(F.aextract_data(Q(symbol="SHOP", use_cache=False), None))
    assert res["exhibit_url"].endswith("aif.htm")


def test_aextract_ex99_absolute_href_links():
    """EX-99 hrefs given as absolute / site-rooted paths (lines 650-657)."""
    main_url = "https://www.sec.gov/a/40f.htm"
    index_url = "https://www.sec.gov/a/index.htm"
    filings = [
        _filing("40-F", date(2024, 2, 1), date(2023, 12, 31), main_url, index_url)
    ]
    main_html = "<html><body><p>Cover page of 40-F.</p></body></html>"
    # One absolute http href, one site-rooted /Archives href.
    index_html = (
        "<html><body><table>"
        "<tr><th>Seq</th><th>Desc</th><th>Document</th><th>Type</th>"
        "<th>Size</th></tr>"
        "<tr><td>99</td><td>Other</td>"
        '<td><a href="https://www.sec.gov/a/other.htm">other.htm</a></td>'
        "<td>EX-99.1</td><td>5</td></tr>"
        "<tr><td>99</td><td>MDA</td>"
        '<td><a href="/Archives/edgar/data/1/mda.htm">mda.htm</a></td>'
        "<td>EX-99.2</td><td>5</td></tr>"
        "</table></body></html>"
    )
    mda_html = (
        "<html><body><h2>Management's Discussion and Analysis</h2>"
        "<p>Foreign MD&amp;A.</p></body></html>"
    )

    async def fetch(params, creds):  # noqa: ARG001
        return filings if "10-K" in params.get("form_type", "") else []

    async def cached(url, **kwargs):  # noqa: ARG001
        if url == main_url:
            return main_html
        if url == index_url:
            return index_html
        if url == "https://www.sec.gov/a/other.htm":
            return "<html><body><p>Unrelated other exhibit.</p></body></html>"
        if url == "https://www.sec.gov/Archives/edgar/data/1/mda.htm":
            return mda_html
        return ""

    p1, p2 = _patches(fetch, cached)
    with p1, p2:
        res = asyncio.run(F.aextract_data(Q(symbol="SHOP", use_cache=False), None))
    assert res["exhibit_url"] == "https://www.sec.gov/Archives/edgar/data/1/mda.htm"


def test_aextract_calendar_period_only_uses_today():
    """calendar_period without year uses the current year/quarter (304-305)."""
    # Provide a 10-K dated this year so the year-match path finds it after
    # the calendar_year defaults to today's year.
    today_year = date.today().year
    filings = [
        _filing(
            "10-Q",
            date(today_year, 5, 15),
            date(today_year, 3, 31),
            "https://www.sec.gov/a/10q.htm",
            "https://www.sec.gov/a/index.htm",
        ),
    ]

    async def fetch(params, creds):  # noqa: ARG001
        return filings if "10-K" in params.get("form_type", "") else []

    async def cached(url, **kwargs):  # noqa: ARG001
        return "<html><body><p>Item 2. MD&amp;A.</p></body></html>"

    p1, p2 = _patches(fetch, cached)
    with p1, p2:
        # The exact match depends on today's quarter; we only require that
        # the calendar_period-only branch runs without a network call.
        try:
            res = asyncio.run(
                F.aextract_data(
                    Q(symbol="AAPL", calendar_period="Q2", use_cache=False), None
                )
            )
            assert res["report_type"] == "10-Q"
        except OpenBBError as exc:
            # Acceptable when today's quarter window excludes the fixture.
            assert "Could not find a filing" in str(exc)


class _Boom(Exception):
    """Stand-in transport error for cached_request failures."""


def test_aextract_foreign_6k_recent_exception_and_break_paths():
    """Foreign 6-K most-recent loop: exceptions, non-string, older-break.

    Exercises lines 188 (older-break), 197-198 (index error continue),
    224 (second-pass older-break), 233-234 (cover error continue).  None
    of the 6-Ks qualify, so the 40-F is used and its EX-99 exhibit is
    fetched instead.
    """
    ann = _filing(
        "40-F",
        date(2024, 3, 1),
        date(2023, 12, 31),
        "https://www.sec.gov/a/40f.htm",
        "https://www.sec.gov/a/40f_index.htm",
    )
    sixk1 = _filing(
        "6-K",
        date(2024, 9, 1),
        date(2024, 6, 30),
        "https://www.sec.gov/a/6k1.htm",
        "https://www.sec.gov/a/6k1_index.htm",
    )
    # Older than the 40-F -> triggers the older-break in both passes.
    sixk_old = _filing(
        "6-K",
        date(2023, 1, 1),
        date(2022, 12, 31),
        "https://www.sec.gov/a/6kold.htm",
        "https://www.sec.gov/a/6kold_index.htm",
    )
    ann_index = (
        "<html><body><table>"
        "<tr><th>S</th><th>D</th><th>Doc</th><th>Type</th><th>Sz</th></tr>"
        '<tr><td>99</td><td>MDA</td><td><a href="mda.htm">mda.htm</a></td>'
        "<td>EX-99.2</td><td>5</td></tr>"
        "</table></body></html>"
    )
    ann_mda = (
        "<html><body><h2>Management's Discussion and Analysis</h2>"
        "<p>Foreign annual MD&amp;A.</p></body></html>"
    )

    async def fetch(params, creds):  # noqa: ARG001
        ft = params.get("form_type", "")
        if "10-K" in ft:
            return [ann]
        if ft == "6-K":
            return [sixk1, sixk_old]
        return []

    async def cached(url, **kwargs):  # noqa: ARG001
        if url == "https://www.sec.gov/a/6k1_index.htm":
            raise _Boom("index fail")  # 197-198
        if url == "https://www.sec.gov/a/6k1.htm":
            raise _Boom("cover fail")  # 233-234 second-pass cover error
        if url == "https://www.sec.gov/a/40f.htm":
            return "<html><body><p>Cover 40-F.</p></body></html>"
        if url == "https://www.sec.gov/a/40f_index.htm":
            return ann_index
        if "mda" in url:
            return ann_mda
        return ""

    p1, p2 = _patches(fetch, cached)
    with p1, p2:
        res = asyncio.run(F.aextract_data(Q(symbol="SHOP", use_cache=False), None))
    assert res["report_type"] == "40-F"
    assert res.get("exhibit_content") == ann_mda


def test_aextract_foreign_6k_recent_index_non_string():
    """Foreign 6-K first pass: index returns non-string -> continue (199-200)."""
    ann = _filing(
        "40-F",
        date(2024, 3, 1),
        date(2023, 12, 31),
        "https://www.sec.gov/a/40f.htm",
        "https://www.sec.gov/a/40f_index.htm",
    )
    sixk1 = _filing(
        "6-K",
        date(2024, 9, 1),
        date(2024, 6, 30),
        "https://www.sec.gov/a/6k1.htm",
        "https://www.sec.gov/a/6k1_index.htm",
    )
    ann_index = (
        "<html><body><table>"
        "<tr><th>S</th><th>D</th><th>Doc</th><th>Type</th><th>Sz</th></tr>"
        '<tr><td>99</td><td>MDA</td><td><a href="mda.htm">mda.htm</a></td>'
        "<td>EX-99.2</td><td>5</td></tr>"
        "</table></body></html>"
    )
    ann_mda = (
        "<html><body><h2>Management's Discussion and Analysis</h2>"
        "<p>Foreign annual MD&amp;A.</p></body></html>"
    )

    async def fetch(params, creds):  # noqa: ARG001
        ft = params.get("form_type", "")
        if "10-K" in ft:
            return [ann]
        if ft == "6-K":
            return [sixk1]
        return []

    async def cached(url, **kwargs):  # noqa: ARG001
        if url == "https://www.sec.gov/a/6k1_index.htm":
            return b"not a string"  # 199-200
        if url == "https://www.sec.gov/a/6k1.htm":
            return "<html><body><p>nothing matches here.</p></body></html>"
        if url == "https://www.sec.gov/a/40f.htm":
            return "<html><body><p>Cover 40-F.</p></body></html>"
        if url == "https://www.sec.gov/a/40f_index.htm":
            return ann_index
        if "mda" in url:
            return ann_mda
        return ""

    p1, p2 = _patches(fetch, cached)
    with p1, p2:
        res = asyncio.run(F.aextract_data(Q(symbol="SHOP", use_cache=False), None))
    assert res["report_type"] == "40-F"


def test_aextract_domestic_8k_recent_exception_and_break_paths():
    """Domestic 8-K most-recent loop: exceptions, non-string, no-ex99, break.

    Exercises lines 267 (older-break), 277-280 (index error / non-string),
    283 (no EX-99 continue), 294-295 (cover error continue).  No 8-K
    qualifies, so the 10-K is used directly.
    """
    tenk = _filing(
        "10-K",
        date(2024, 2, 1),
        date(2023, 12, 31),
        "https://www.sec.gov/a/10k.htm",
        "https://www.sec.gov/a/10k_index.htm",
    )
    eightk1 = _filing(
        "8-K",
        date(2024, 9, 1),
        date(2024, 6, 30),
        "https://www.sec.gov/a/8k1.htm",
        "https://www.sec.gov/a/8k1_index.htm",
    )
    eightk2 = _filing(
        "8-K",
        date(2024, 8, 1),
        date(2024, 5, 31),
        "https://www.sec.gov/a/8k2.htm",
        "https://www.sec.gov/a/8k2_index.htm",
    )
    eightk_old = _filing(
        "8-K",
        date(2023, 1, 1),
        date(2022, 12, 31),
        "https://www.sec.gov/a/8kold.htm",
        "https://www.sec.gov/a/8kold_index.htm",
    )

    async def fetch(params, creds):  # noqa: ARG001
        ft = params.get("form_type", "")
        if "10-K" in ft:
            return [tenk]
        if ft == "8-K":
            return [eightk1, eightk2, eightk_old]
        return []

    async def cached(url, **kwargs):  # noqa: ARG001
        if url == "https://www.sec.gov/a/8k1_index.htm":
            raise _Boom("index fail")  # 277-278
        if url == "https://www.sec.gov/a/8k2_index.htm":
            # Valid index but with NO EX-99 rows -> no-ex99 continue (283).
            return (
                "<html><body><table>"
                "<tr><td>1</td><td>x</td>"
                '<td><a href="a.htm">a</a></td><td>10-K</td><td>1</td></tr>'
                "</table></body></html>"
            )
        if url == "https://www.sec.gov/a/10k.htm":
            return "<html><body><p>Item 7. MD&amp;A inline.</p></body></html>"
        return ""

    p1, p2 = _patches(fetch, cached)
    with p1, p2:
        res = asyncio.run(F.aextract_data(Q(symbol="AAPL", use_cache=False), None))
    assert res["report_type"] == "10-K"


def test_aextract_domestic_8k_recent_index_non_string_and_cover_fail():
    """Domestic 8-K most-recent: index non-string (280) and cover error (294)."""
    tenk = _filing(
        "10-K",
        date(2024, 2, 1),
        date(2023, 12, 31),
        "https://www.sec.gov/a/10k.htm",
        "https://www.sec.gov/a/10k_index.htm",
    )
    eightk1 = _filing(
        "8-K",
        date(2024, 9, 1),
        date(2024, 6, 30),
        "https://www.sec.gov/a/8k1.htm",
        "https://www.sec.gov/a/8k1_index.htm",
    )
    eightk2 = _filing(
        "8-K",
        date(2024, 8, 1),
        date(2024, 5, 31),
        "https://www.sec.gov/a/8k2.htm",
        "https://www.sec.gov/a/8k2_index.htm",
    )
    ex99_index = (
        "<html><body><table>"
        "<tr><th>S</th><th>D</th><th>Doc</th><th>Type</th><th>Sz</th></tr>"
        '<tr><td>99</td><td>PR</td><td><a href="pr.htm">pr.htm</a></td>'
        "<td>EX-99.1</td><td>5</td></tr>"
        "</table></body></html>"
    )

    async def fetch(params, creds):  # noqa: ARG001
        ft = params.get("form_type", "")
        if "10-K" in ft:
            return [tenk]
        if ft == "8-K":
            return [eightk1, eightk2]
        return []

    async def cached(url, **kwargs):  # noqa: ARG001
        if url == "https://www.sec.gov/a/8k1_index.htm":
            return b"non-string index"  # 279-280
        if url == "https://www.sec.gov/a/8k2_index.htm":
            return ex99_index
        if url == "https://www.sec.gov/a/8k2.htm":
            raise _Boom("cover fail")  # 294-295
        if url == "https://www.sec.gov/a/10k.htm":
            return "<html><body><p>Item 7. MD&amp;A inline.</p></body></html>"
        return ""

    p1, p2 = _patches(fetch, cached)
    with p1, p2:
        res = asyncio.run(F.aextract_data(Q(symbol="AAPL", use_cache=False), None))
    assert res["report_type"] == "10-K"


def test_aextract_calendar_year_matches_non_annual_filing():
    """calendar_year matches only a 10-Q (no annual) -> broader filter (328)."""
    filings = [
        _filing(
            "10-Q",
            date(2021, 5, 1),
            date(2021, 3, 31),
            "https://www.sec.gov/a/10q.htm",
            "https://www.sec.gov/a/index.htm",
        ),
    ]

    async def fetch(params, creds):  # noqa: ARG001
        return filings if "10-K" in params.get("form_type", "") else []

    async def cached(url, **kwargs):  # noqa: ARG001
        return "<html><body><p>Item 2. MD&amp;A.</p></body></html>"

    p1, p2 = _patches(fetch, cached)
    with p1, p2:
        res = asyncio.run(
            F.aextract_data(Q(symbol="AAPL", calendar_year=2021, use_cache=False), None)
        )
    assert res["url"].endswith("10q.htm")


def test_aextract_foreign_6k_quarterly_second_pass_cover():
    """Foreign 6-K quarterly fallback: index error then cover-desc 2nd pass.

    Exercises lines 404-405 (index fetch error continue via _fetch_6k None),
    424-425 (remember EX-99 candidate) and 432-446 (cover-description
    second pass selects the filing).
    """
    ann = _filing(
        "40-F",
        date(2020, 3, 1),
        date(2019, 12, 31),
        "https://www.sec.gov/a/40f.htm",
        "https://www.sec.gov/a/40f_index.htm",
    )
    # 6-K in the Q2-2024 window; filename has no MD&A keyword.
    sixk = _filing(
        "6-K",
        date(2024, 5, 15),
        date(2024, 3, 31),
        "https://www.sec.gov/a/6k.htm",
        "https://www.sec.gov/a/6k_index.htm",
    )
    sixk_index = (
        "<html><body><table>"
        "<tr><th>S</th><th>D</th><th>Doc</th><th>Type</th><th>Sz</th></tr>"
        '<tr><td>99</td><td>Update</td><td><a href="update.htm">update.htm'
        "</a></td><td>EX-99.1</td><td>5</td></tr>"
        "</table></body></html>"
    )
    sixk_cover = (
        "<html><body><p>Q2 2024 Update for shareholders. Quarterly "
        "Results attached.</p></body></html>"
    )

    async def fetch(params, creds):  # noqa: ARG001
        ft = params.get("form_type", "")
        if "10-K" in ft:
            return [ann]
        if ft == "6-K":
            return [sixk]
        return []

    async def cached(url, **kwargs):  # noqa: ARG001
        if url == "https://www.sec.gov/a/6k_index.htm":
            return sixk_index
        if url == "https://www.sec.gov/a/6k.htm":
            return sixk_cover
        if "update" in url:
            return "<html><body><p>Quarterly update body.</p></body></html>"
        return ""

    p1, p2 = _patches(fetch, cached)
    with p1, p2:
        res = asyncio.run(
            F.aextract_data(
                Q(
                    symbol="SHOP",
                    calendar_year=2024,
                    calendar_period="Q2",
                    use_cache=False,
                ),
                None,
            )
        )
    assert res["report_type"] == "6-K"


def test_aextract_foreign_6k_quarterly_fetch_6k_raises_then_match():
    """Foreign 6-K quarterly: first candidate's index raises, second matches.

    The first 6-K's index fetch raises inside ``_fetch_6k`` (lines 404-405
    return None) so ``_idx_html`` is None and the ``not isinstance(..., str)``
    guard (line 412) skips it.  The second 6-K's index yields an MD&A-named
    EX-99 exhibit, which is selected.
    """
    ann = _filing(
        "40-F",
        date(2020, 3, 1),
        date(2019, 12, 31),
        "https://www.sec.gov/a/40f.htm",
        "https://www.sec.gov/a/40f_index.htm",
    )
    # Both 6-Ks fall inside the Q2-2024 window (Apr 1 - Jun 30).
    sixk_bad = _filing(
        "6-K",
        date(2024, 6, 1),
        date(2024, 4, 30),
        "https://www.sec.gov/a/6kbad.htm",
        "https://www.sec.gov/a/6kbad_index.htm",
    )
    sixk_good = _filing(
        "6-K",
        date(2024, 5, 1),
        date(2024, 4, 1),
        "https://www.sec.gov/a/6kgood.htm",
        "https://www.sec.gov/a/6kgood_index.htm",
    )
    good_index = (
        "<html><body><table>"
        "<tr><th>S</th><th>D</th><th>Doc</th><th>Type</th><th>Sz</th></tr>"
        '<tr><td>99</td><td>MDA</td><td><a href="q1_mda.htm">q1_mda.htm</a>'
        "</td><td>EX-99.1</td><td>5</td></tr>"
        "</table></body></html>"
    )
    ex99 = (
        "<html><body><h2>Management's Discussion and Analysis</h2>"
        "<p>Quarterly MD&amp;A body content.</p></body></html>"
    )

    async def fetch(params, creds):  # noqa: ARG001
        ft = params.get("form_type", "")
        if "10-K" in ft:
            return [ann]
        if ft == "6-K":
            return [sixk_bad, sixk_good]
        return []

    async def cached(url, **kwargs):  # noqa: ARG001
        if url == "https://www.sec.gov/a/6kbad_index.htm":
            raise _Boom("index fail")  # 404-405 -> None -> 412 continue
        if url == "https://www.sec.gov/a/6kgood_index.htm":
            return good_index
        if "q1_mda" in url or url == "https://www.sec.gov/a/6kgood.htm":
            return ex99
        return ""

    p1, p2 = _patches(fetch, cached)
    with p1, p2:
        res = asyncio.run(
            F.aextract_data(
                Q(
                    symbol="SHOP",
                    calendar_year=2024,
                    calendar_period="Q2",
                    use_cache=False,
                ),
                None,
            )
        )
    assert res["report_type"] == "6-K"
    assert res["url"] == "https://www.sec.gov/a/6kgood.htm"


def test_aextract_domestic_8k_quarterly_non_string_and_no_ex99():
    """Domestic 8-K quarterly fallback: _fetch_8k raises (488-489) + no-ex99 (508).

    The first candidate's index fetch raises inside ``_fetch_8k`` (lines
    488-489 return None), so the ``not isinstance(..., str)`` guard (line
    505) skips it.  The second candidate's index has no EX-99 rows (line
    508).  Neither yields an earnings exhibit, so OpenBBError is raised.
    """
    tenk = _filing(
        "10-K",
        date(2020, 2, 1),
        date(2019, 12, 31),
        "https://www.sec.gov/a/10k.htm",
        "https://www.sec.gov/a/10k_index.htm",
    )
    # Two 8-Ks in the Q2-2024 window; neither yields a usable earnings exhibit.
    eightk1 = _filing(
        "8-K",
        date(2024, 5, 20),
        date(2024, 4, 1),
        "https://www.sec.gov/a/8k1.htm",
        "https://www.sec.gov/a/8k1_index.htm",
    )
    eightk2 = _filing(
        "8-K",
        date(2024, 5, 10),
        date(2024, 3, 31),
        "https://www.sec.gov/a/8k2.htm",
        "https://www.sec.gov/a/8k2_index.htm",
    )

    async def fetch(params, creds):  # noqa: ARG001
        ft = params.get("form_type", "")
        if "10-K" in ft:
            return [tenk]
        if ft == "8-K":
            return [eightk1, eightk2]
        return []

    async def cached(url, **kwargs):  # noqa: ARG001
        if url == "https://www.sec.gov/a/8k1_index.htm":
            raise _Boom("index fail")  # 488-489 -> None -> 505 continue
        if url == "https://www.sec.gov/a/8k2_index.htm":
            # No EX-99 rows -> 508 continue.
            return (
                "<html><body><table>"
                "<tr><td>1</td><td>x</td>"
                '<td><a href="a.htm">a</a></td><td>10-K</td><td>1</td></tr>'
                "</table></body></html>"
            )
        return ""

    p1, p2 = _patches(fetch, cached)
    with p1, p2:
        with pytest.raises(OpenBBError) as exc:
            asyncio.run(
                F.aextract_data(
                    Q(
                        symbol="AAPL",
                        calendar_year=2024,
                        calendar_period="Q2",
                        use_cache=False,
                    ),
                    None,
                )
            )
    assert "Could not find a filing" in str(exc.value)


def test_aextract_ex13_absolute_http_href():
    """EX-13 row with an absolute http href is used as-is (line 579)."""
    main_url = "https://www.sec.gov/a/10k.htm"
    index_url = "https://www.sec.gov/a/index.htm"
    filings = [
        _filing("10-K", date(2024, 2, 1), date(2023, 12, 31), main_url, index_url)
    ]
    main_html = (
        "<html><body><p>Item 7. The Annual Report is incorporated herein "
        "by reference.</p></body></html>"
    )
    ex13_url = "https://example.com/ar/ex13.htm"
    index_html = (
        "<html><body><table>"
        "<tr><th>Seq</th><th>Description</th><th>Document</th>"
        "<th>Type</th><th>Size</th></tr>"
        "<tr><td>13</td><td>Annual Report</td>"
        f'<td><a href="{ex13_url}">ex13.htm</a></td>'
        "<td>EX-13</td><td>1000</td></tr>"
        "</table></body></html>"
    )
    ex13_html = "<html><body><h2>Annual Report</h2><p>MD&amp;A.</p></body></html>"

    async def fetch(params, creds):  # noqa: ARG001
        return filings if "10-K" in params.get("form_type", "") else []

    async def cached(url, **kwargs):  # noqa: ARG001
        if url == main_url:
            return main_html
        if url == index_url:
            return index_html
        if url == ex13_url:
            return ex13_html
        return ""

    p1, p2 = _patches(fetch, cached)
    with p1, p2:
        res = asyncio.run(F.aextract_data(Q(symbol="AAPL", use_cache=False), None))
    assert res["exhibit_url"] == ex13_url


def test_aextract_ex13_relative_href():
    """EX-13 index row with a bare relative href is joined to the base dir (583)."""
    main_url = "https://www.sec.gov/Archives/edgar/data/1/10k.htm"
    index_url = "https://www.sec.gov/Archives/edgar/data/1/index.htm"
    filings = [
        _filing("10-K", date(2024, 2, 1), date(2023, 12, 31), main_url, index_url)
    ]
    main_html = (
        "<html><body><p>Item 7. The Annual Report is incorporated herein "
        "by reference.</p></body></html>"
    )
    # Bare relative href (no http, no leading '/', no /ix?doc= prefix) ->
    # the else-branch joins it onto the index page's base directory.
    index_html = (
        "<html><body><table>"
        "<tr><th>Seq</th><th>Description</th><th>Document</th>"
        "<th>Type</th><th>Size</th></tr>"
        "<tr><td>13</td><td>Annual Report</td>"
        '<td><a href="ex13rel.htm">ex13rel.htm</a></td>'
        "<td>EX-13</td><td>1000</td></tr>"
        "</table></body></html>"
    )
    ex13_html = "<html><body><h2>Annual Report</h2><p>MD&amp;A.</p></body></html>"
    expected_ex13_url = "https://www.sec.gov/Archives/edgar/data/1/ex13rel.htm"

    async def fetch(params, creds):  # noqa: ARG001
        return filings if "10-K" in params.get("form_type", "") else []

    async def cached(url, **kwargs):  # noqa: ARG001
        if url == main_url:
            return main_html
        if url == index_url:
            return index_html
        if url == expected_ex13_url:
            return ex13_html
        return ""

    p1, p2 = _patches(fetch, cached)
    with p1, p2:
        res = asyncio.run(F.aextract_data(Q(symbol="AAPL", use_cache=False), None))
    assert res["exhibit_url"] == expected_ex13_url
    assert res["exhibit_content"] == ex13_html


def test_aextract_ex13_index_fetch_exception():
    """EX-13 strategy-2 index fetch raising is swallowed (lines 591-592).

    The inline-link strategy fails (no <a>Annual Report</a>) and the index
    fetch raises, so no exhibit is attached.  The inline (stub) content is
    still returned so transform_data can attempt extraction.
    """
    main_url = "https://www.sec.gov/a/10k.htm"
    index_url = "https://www.sec.gov/a/index.htm"
    filings = [
        _filing("10-K", date(2024, 2, 1), date(2023, 12, 31), main_url, index_url)
    ]
    main_html = (
        "<html><body><p>Item 7. The required information is incorporated "
        "herein by reference to the Annual Report.</p></body></html>"
    )

    async def fetch(params, creds):  # noqa: ARG001
        return filings if "10-K" in params.get("form_type", "") else []

    async def cached(url, **kwargs):  # noqa: ARG001
        if url == main_url:
            return main_html
        if url == index_url:
            raise _Boom("index unavailable")  # 591-592
        return ""

    p1, p2 = _patches(fetch, cached)
    with p1, p2:
        res = asyncio.run(F.aextract_data(Q(symbol="AAPL", use_cache=False), None))
    # No exhibit attached; the inline cover content is returned verbatim.
    assert "exhibit_content" not in res
    assert res["report_type"] == "10-K"


def test_aextract_ex99_fetch_returns_none_for_exhibit():
    """EX-99 exhibit fetch failing is tolerated (lines 638-639 via _fetch).

    The index lists two EX-99 rows; fetching the first raises (-> None,
    skipped) and the second returns the MD&A exhibit.
    """
    main_url = "https://www.sec.gov/a/40f.htm"
    index_url = "https://www.sec.gov/a/index.htm"
    filings = [
        _filing("40-F", date(2024, 2, 1), date(2023, 12, 31), main_url, index_url)
    ]
    main_html = "<html><body><p>Cover page 40-F.</p></body></html>"
    index_html = (
        "<html><body><table>"
        "<tr><th>S</th><th>D</th><th>Doc</th><th>Type</th><th>Sz</th></tr>"
        '<tr><td>99</td><td>bad</td><td><a href="bad.htm">bad.htm</a></td>'
        "<td>EX-99.1</td><td>5</td></tr>"
        '<tr><td>99</td><td>MDA</td><td><a href="good.htm">good.htm</a></td>'
        "<td>EX-99.2</td><td>5</td></tr>"
        "</table></body></html>"
    )
    good_html = (
        "<html><body><h2>Management's Discussion and Analysis</h2>"
        "<p>Foreign MD&amp;A.</p></body></html>"
    )

    async def fetch(params, creds):  # noqa: ARG001
        return filings if "10-K" in params.get("form_type", "") else []

    async def cached(url, **kwargs):  # noqa: ARG001
        if url == main_url:
            return main_html
        if url == index_url:
            return index_html
        if "bad" in url:
            raise _Boom("exhibit fetch failed")  # 638-639
        if "good" in url:
            return good_html
        return ""

    p1, p2 = _patches(fetch, cached)
    with p1, p2:
        res = asyncio.run(F.aextract_data(Q(symbol="SHOP", use_cache=False), None))
    assert res["exhibit_url"].endswith("good.htm")
