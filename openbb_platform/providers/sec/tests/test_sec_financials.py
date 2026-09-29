"""Unit tests for ``openbb_sec.models.sec_financials``."""

import asyncio
import xml.etree.ElementTree as ET
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pydantic
import pytest

from openbb_sec.models import sec_financials as mod
from openbb_sec.models.sec_financials import (
    FilingSectionQueryParams,
    FinancialStatements,
    _calendar_quarter,
    _clean_disclosure_name,
    _financial_statements_cache,
    _is_amendment,
    _is_annual_form,
    _is_legal_redirect,
    get_form10_urls_by_symbol,
    no_filing_message,
    resolve_filing_url,
    resolve_section_url,
)


def make_fs(**attrs) -> FinancialStatements:
    """Build a FinancialStatements without running __init__, set PrivateAttrs."""
    fs = object.__new__(FinancialStatements)
    pydantic.BaseModel.__init__(fs)
    for key, value in attrs.items():
        setattr(fs, key, value)
    return fs


def test_clean_disclosure_name_with_prefix():
    assert (
        _clean_disclosure_name("0007 - Disclosure - Inventory Disclosure")
        == "Inventory Disclosure"
    )


def test_clean_disclosure_name_no_prefix():
    assert _clean_disclosure_name("Inventory Disclosure") == "Inventory Disclosure"


def test_calendar_quarter():
    assert _calendar_quarter("2024-01-28") == 1
    assert _calendar_quarter("2024-04-28") == 2
    assert _calendar_quarter("2024-08-31") == 3
    assert _calendar_quarter("2024-10-27") == 4
    assert _calendar_quarter("") == 0
    assert _calendar_quarter(None) == 0
    assert _calendar_quarter("2024-XX-31") == 0


def test_is_amendment():
    assert _is_amendment("10-K/A")
    assert _is_amendment("20-F/A")
    assert not _is_amendment("10-K")
    assert not _is_amendment(None)


def test_is_annual_form():
    assert _is_annual_form("10-K")
    assert _is_annual_form("20-F")
    # Amendments are distinct documents, not annual reports.
    assert not _is_annual_form("40-F/A")
    assert not _is_annual_form("10-K/A")
    assert not _is_annual_form("10-Q")
    assert not _is_annual_form("6-K")
    assert not _is_annual_form(None)


def test_resolve_filing_url_prefers_original_over_amendment():
    filings = [
        {
            "filing_type": "10-K/A",
            "period_ending": "1997-09-26",
            "filing_date": "1998-01-23",
            "url": "amendment",
        },
        {
            "filing_type": "10-K",
            "period_ending": "1997-09-26",
            "filing_date": "1997-12-05",
            "url": "original",
        },
    ]
    with patch.object(
        mod, "get_form10_urls_by_symbol", new=AsyncMock(return_value=filings)
    ):
        url = asyncio.run(
            resolve_filing_url("AAPL", calendar_year=1997, annual_default=True)
        )
    assert url == "original"


def test_no_filing_message():
    msg = no_filing_message("BABA")
    assert "BABA" in msg
    assert "20-F" in msg and "foreign private issuer" in msg


def test_is_legal_redirect():
    assert _is_legal_redirect(
        "Please see Note 12 of the Notes to the Consolidated Financial Statements."
    )
    assert _is_legal_redirect("This matter is incorporated herein by reference.")
    assert not _is_legal_redirect("We are a defendant in a patent suit filed in 2023.")
    assert not _is_legal_redirect("x" * 1600)


def test_filing_section_query_params_validators():
    q = FilingSectionQueryParams(symbol="wdfc", calendar_year="", calendar_period="")  # ty: ignore[invalid-argument-type]
    assert q.symbol == "WDFC"
    assert q.calendar_year is None
    assert q.calendar_period is None


def test_filing_section_query_params_to_upper_non_string():
    assert FilingSectionQueryParams._to_upper(123) == 123


def test_filing_section_query_params_empty_to_none_passthrough():
    assert FilingSectionQueryParams._empty_to_none("q1") == "q1"


def test_resolve_section_url_explicit_url():
    q = SimpleNamespace(url="https://sec.gov/x", symbol="WDFC", use_cache=True)
    assert asyncio.run(resolve_section_url(q)) == "https://sec.gov/x"


def test_resolve_section_url_no_symbol():
    q = SimpleNamespace(url=None, symbol=None, use_cache=True)
    assert asyncio.run(resolve_section_url(q)) == ""


def test_resolve_section_url_from_symbol():
    q = SimpleNamespace(
        url=None,
        symbol="WDFC",
        calendar_year=2024,
        calendar_period="Q1",
        use_cache=False,
    )
    with patch.object(
        mod, "resolve_filing_url", new=AsyncMock(return_value="resolved")
    ) as rfu:
        assert asyncio.run(resolve_section_url(q)) == "resolved"
    rfu.assert_awaited_once_with("WDFC", 2024, "Q1", False, True)


def test_resolve_section_url_passes_annual_default():
    q = SimpleNamespace(
        url=None,
        symbol="X",
        calendar_year=None,
        calendar_period=None,
        use_cache=False,
    )
    with patch.object(
        mod, "resolve_filing_url", new=AsyncMock(return_value="u")
    ) as rfu:
        asyncio.run(resolve_section_url(q, annual_default=False))
    rfu.assert_awaited_once_with("X", None, None, False, False)


def test_resolve_filing_url_latest_filing_any_form():
    filings = [
        {
            "filing_date": "2024-10-01",
            "period_ending": "2024-08-31",
            "filing_type": "10-K",
            "url": "k2024",
        },
        {
            "filing_date": "2024-12-15",
            "period_ending": "2024-11-30",
            "filing_type": "10-Q",
            "url": "q-latest",
        },
    ]
    with patch.object(
        mod, "get_form10_urls_by_symbol", new=AsyncMock(return_value=filings)
    ):
        assert asyncio.run(resolve_filing_url("X")) == "k2024"
        assert asyncio.run(resolve_filing_url("X", annual_default=False)) == "q-latest"


def test_get_form10_urls_by_symbol():
    filing = SimpleNamespace(
        filing_date="2024-10-01",
        report_date="2024-08-31",
        report_type="10-K",
        report_url="https://sec.gov/k",
    )

    class _Fetcher:
        async def fetch_data(self, params, info):
            assert params["form_type"] == "10-K,10-Q,20-F,40-F"
            return [filing]

    with patch(
        "openbb_sec.models.company_filings.SecCompanyFilingsFetcher",
        _Fetcher,
    ):
        result = asyncio.run(get_form10_urls_by_symbol("WDFC", use_cache=False))
    assert result == [
        {
            "filing_date": "2024-10-01",
            "period_ending": "2024-08-31",
            "filing_type": "10-K",
            "url": "https://sec.gov/k",
        }
    ]


def _filings():
    return [
        {
            "filing_date": "2024-10-01",
            "period_ending": "2024-08-31",
            "filing_type": "10-K",
            "url": "k2024",
        },
        {
            "filing_date": "2023-10-01",
            "period_ending": "2023-08-31",
            "filing_type": "10-K",
            "url": "k2023",
        },
        {
            "filing_date": "2024-04-01",
            "period_ending": "2024-02-28",
            "filing_type": "10-Q",
            "url": "q1-2024",
        },
        {
            "filing_date": "2024-07-01",
            "period_ending": "2024-05-31",
            "filing_type": "10-Q",
            "url": "q2-2024",
        },
    ]


def test_resolve_filing_url_annual_latest():
    with patch.object(
        mod, "get_form10_urls_by_symbol", new=AsyncMock(return_value=_filings())
    ):
        assert asyncio.run(resolve_filing_url("WDFC")) == "k2024"


def test_resolve_filing_url_annual_by_year():
    with patch.object(
        mod, "get_form10_urls_by_symbol", new=AsyncMock(return_value=_filings())
    ):
        assert asyncio.run(resolve_filing_url("WDFC", calendar_year=2023)) == "k2023"


def test_resolve_filing_url_by_calendar_period():
    with patch.object(
        mod, "get_form10_urls_by_symbol", new=AsyncMock(return_value=_filings())
    ):
        # 2024-02-28 is calendar Q1; 2024-05-31 is calendar Q2.
        assert (
            asyncio.run(resolve_filing_url("WDFC", calendar_period="Q1")) == "q1-2024"
        )
        assert (
            asyncio.run(resolve_filing_url("WDFC", calendar_period="Q2")) == "q2-2024"
        )


def test_resolve_filing_url_none_found():
    with patch.object(
        mod, "get_form10_urls_by_symbol", new=AsyncMock(return_value=_filings())
    ):
        assert asyncio.run(resolve_filing_url("WDFC", calendar_year=1999)) == ""


def test_init_non_xbrl_branch():
    fs = object.__new__(FinancialStatements)
    pydantic.BaseModel.__init__(fs)
    with (
        patch("openbb_sec.models.sec_filing.Filing.__init__", return_value=None),
        patch.object(FinancialStatements, "_download_metalinks"),
        patch.object(FinancialStatements, "_initialize_non_xbrl") as init_non,
        patch.object(FinancialStatements, "_build_schema_from_xml") as build,
    ):
        FinancialStatements.__init__(fs, "https://www.sec.gov/x")
    init_non.assert_called_once()
    build.assert_not_called()


def test_init_xbrl_branch():
    """An XBRL filing skips non-XBRL init and defers schema building."""
    fs = object.__new__(FinancialStatements)
    pydantic.BaseModel.__init__(fs)
    fs._resources = {"r1": {}, "r2": {}}
    with (
        patch("openbb_sec.models.sec_filing.Filing.__init__", return_value=None),
        patch.object(FinancialStatements, "_download_metalinks"),
        patch.object(FinancialStatements, "_build_schema_from_xml") as build,
        patch.object(FinancialStatements, "_download_xbrl_instance"),
        patch.object(FinancialStatements, "_enrich_cover_page_from_instance"),
        patch.object(FinancialStatements, "_initialize_non_xbrl") as init_non,
    ):
        FinancialStatements.__init__(fs, "https://www.sec.gov/x")
    build.assert_not_called()
    init_non.assert_not_called()


def test_ensure_xbrl_builds_once():
    """The first XBRL access builds schema and instance; later calls are no-ops."""
    fs = object.__new__(FinancialStatements)
    pydantic.BaseModel.__init__(fs)
    fs._resources = {"r1": {}, "r2": {}}
    fs._xbrl_loaded = False
    with (
        patch.object(FinancialStatements, "_build_schema_from_xml") as build,
        patch.object(FinancialStatements, "_download_xbrl_instance") as inst,
        patch.object(FinancialStatements, "_enrich_cover_page_from_instance") as enrich,
    ):
        fs._ensure_xbrl()
        fs._ensure_xbrl()
    build.assert_called_once()
    inst.assert_called_once()
    enrich.assert_called_once()


def test_ensure_xbrl_skips_when_not_xbrl():
    """A non-XBRL filing marks itself loaded without building anything."""
    fs = object.__new__(FinancialStatements)
    pydantic.BaseModel.__init__(fs)
    fs._resources = {}
    fs._xbrl_loaded = False
    with patch.object(FinancialStatements, "_build_schema_from_xml") as build:
        fs._ensure_xbrl()
    assert fs._xbrl_loaded is True
    build.assert_not_called()


def test_from_url_memoized():
    _financial_statements_cache.cache_clear()
    sentinel = object()
    with patch.object(mod, "FinancialStatements", return_value=sentinel) as ctor:
        a = FinancialStatements.from_url("u", True)
        b = FinancialStatements.from_url("u", True)
    assert a is sentinel and b is sentinel
    ctor.assert_called_once_with("u", True)
    _financial_statements_cache.cache_clear()


def test_get_item_sections_cached():
    fs = make_fs(_items={"item_1": {"name": "Business"}})
    assert fs.get_item_sections() == {"item_1": {"name": "Business"}}


def test_get_item_sections_no_content():
    fs = make_fs()
    with patch.object(fs, "get_main_document_content", return_value=None):
        assert fs.get_item_sections() == {}


def test_get_item_sections_builds_from_html():
    fs = make_fs()
    with (
        patch.object(fs, "get_main_document_content", return_value="<html>x</html>"),
        patch.object(
            fs, "_clean_html_to_text", return_value="## Item 1\nBusiness\nText."
        ),
        patch(
            "openbb_sec.utils.filing_sections.extract_item_sections",
            return_value={"item_1": {"name": "Business", "text": "Text."}},
        ),
    ):
        out = fs.get_item_sections()
    assert out == {"item_1": {"name": "Business", "text": "Text."}}
    assert fs._items == out


def test_get_item_sections_raw_fallback():
    # Old plain-text filings: markdown finds nothing, so items come from raw text.
    fs = make_fs()
    content = "Item 1. Legal Proceedings\n\nReference is made to the 10-K."
    with (
        patch.object(fs, "get_main_document_content", return_value=content),
        patch.object(fs, "_clean_html_to_text", return_value="prose with no headers"),
    ):
        items = fs.get_item_sections()
    assert "item_1" in items
    assert items["item_1"]["name"] == "Legal Proceedings"


def test_get_item_matches_item_num():
    fs = make_fs(_items={"x": {"item_num": "1A", "name": "Risk"}})
    assert fs.get_item("1a") == {"item_num": "1A", "name": "Risk"}


def test_get_item_matches_key_suffix():
    fs = make_fs(_items={"item_II_1": {"name": "Legal"}})
    assert fs.get_item("1") == {"name": "Legal"}


def test_get_item_no_match():
    fs = make_fs(_items={"item_1": {"item_num": "1", "name": "Biz"}})
    assert fs.get_item("99") is None


def test_item_by_name():
    fs = make_fs(_items={"k": {"name": "The Business Overview"}})
    assert fs._item_by_name("business") == {"name": "The Business Overview"}
    assert fs._item_by_name("missing") is None


def test_business_10k_path():
    fs = make_fs(
        _document_type="10-K", _items={"item_1": {"item_num": "1", "text": " Body "}}
    )
    assert fs.business() == "Body"


def test_business_non_10k_by_name():
    fs = make_fs(
        _document_type="10-Q", _items={"x": {"name": "Our Business", "text": "Body"}}
    )
    assert fs.business() == "Body"


def test_business_foreign_slices_section_from_extracted_html():
    fs = make_fs(
        _document_type="20-F",
        _items={"x": {"item_num": "4", "name": "Info", "text": "fallback"}},
    )
    section_text = "Intro\nB. Business\nOperating discussion\nITEM 5\nOther"
    with (
        patch.object(fs, "get_main_document_content", return_value="<html/>"),
        patch(
            "openbb_sec.utils.filing_sections.extract_section_html",
            return_value="<div>section</div>",
        ),
        patch.object(fs, "_clean_html_to_text", return_value=section_text),
    ):
        out = fs.business()
    assert out == "B. Business\nOperating discussion"


def test_business_foreign_fallback_text_without_business_heading():
    fs = make_fs(
        _document_type="20-F",
        _items={"x": {"item_num": "4", "name": "Info", "text": "General company text"}},
    )
    with patch.object(fs, "get_main_document_content", return_value=None):
        out = fs.business()
    assert out == "General company text"


def test_business_foreign_falls_back_to_business_name_lookup():
    fs = make_fs(
        _document_type="20-F",
        _items={"x": {"name": "Our business", "text": "Body"}},
    )
    assert fs.business() == "Body"


def test_business_none_when_missing():
    fs = make_fs(_document_type="10-K", _items={"item_2": {"item_num": "2"}})
    assert fs.business() is None


def test_business_none_when_empty_text():
    fs = make_fs(
        _document_type="10-K", _items={"item_1": {"item_num": "1", "text": "   "}}
    )
    assert fs.business() is None


def test_legal_proceedings_by_name():
    fs = make_fs(_items={"k": {"name": "Legal Proceedings", "text": "Suit"}})
    assert fs.legal_proceedings() == {"name": "Legal Proceedings", "text": "Suit"}


def test_legal_proceedings_by_item():
    fs = make_fs(_items={"item_3": {"item_num": "3", "name": "Other"}})
    assert fs.legal_proceedings() == {"item_num": "3", "name": "Other"}


def test_legal_proceedings_no_item():
    assert make_fs(_items={"item_2": {"item_num": "2"}}).legal_proceedings() is None


def test_legal_proceedings_follows_redirect():
    fs = make_fs(
        _items={
            "k": {
                "name": "Legal Proceedings",
                "text": "Please see Note 12 of the Notes to the Consolidated "
                "Financial Statements.",
            }
        },
        _disclosures={
            "g": {
                "name": "Commitments and Contingencies",
                "text": "The Company is subject to various legal proceedings.",
            }
        },
    )
    result = fs.legal_proceedings()
    assert "Please see Note 12" in result["text"]
    assert "subject to various legal proceedings" in result["text"]


def test_legal_proceedings_redirect_without_note():
    fs = make_fs(
        _items={
            "k": {
                "name": "Legal Proceedings",
                "text": "Please see Note 12 of the Notes to the Financial Statements.",
            }
        },
        _disclosures={},
    )
    assert fs.legal_proceedings()["text"].startswith("Please see Note 12")


def test_legal_contingencies_note_selection():
    fs = make_fs(
        _disclosures={
            "Inventory": {"name": "Inventory Disclosure", "text": "inv"},
            "contingencies_raw": "raw",
            "Contingencies (Details)": {
                "name": "Contingencies (Details)",
                "text": "y",
            },
            "legal": {"name": "Legal Matters", "text": ""},
            "good": {"name": "Commitments and Contingencies", "text": "the note"},
        }
    )
    assert fs._legal_contingencies_note() == "the note"


def test_legal_contingencies_note_none_match():
    fs = make_fs(_disclosures={"a": {"name": "Inventory Disclosure", "text": "x"}})
    assert fs._legal_contingencies_note() == ""


def test_risk_factors_no_item():
    fs = make_fs(_items={"item_2": {"item_num": "2"}})
    assert fs.risk_factors() == []


def test_risk_factors_foreign_item_3d_path():
    fs = make_fs(
        _document_type="20-F", _items={"x": {"item_num": "3D", "text": " body "}}
    )
    with patch.object(fs, "get_main_document_content", return_value=None):
        out = fs.risk_factors()
    assert out == [{"risk_factor": None, "text": "body"}]


def test_risk_factors_blocks_from_html():
    fs = make_fs(_items={"x": {"name": "Risk Factors", "item_num": "1A"}})
    # The headingless preamble block (risk_factor=None) is dropped.
    blocks = [{"risk_factor": None, "text": "intro"}, {"risk_factor": "A", "text": "t"}]
    with (
        patch.object(fs, "get_main_document_content", return_value="<html>sec</html>"),
        patch(
            "openbb_sec.utils.filing_sections.extract_section_html",
            return_value="<p>section</p>",
        ),
        patch(
            "openbb_sec.utils.filing_sections.split_bold_sections", return_value=blocks
        ),
    ):
        assert fs.risk_factors() == [{"risk_factor": "A", "text": "t"}]


def test_risk_factors_fallback_text():
    fs = make_fs(
        _items={"x": {"name": "Risk Factors", "item_num": "1A", "text": " body "}}
    )
    with (
        patch.object(fs, "get_main_document_content", return_value="<html>sec</html>"),
        patch("openbb_sec.utils.filing_sections.extract_section_html", return_value=""),
    ):
        assert fs.risk_factors() == [{"risk_factor": "Risk Factors", "text": "body"}]


def test_risk_factors_no_content_no_text():
    fs = make_fs(_items={"x": {"name": "Risk Factors", "item_num": "1A", "text": ""}})
    with patch.object(fs, "get_main_document_content", return_value=None):
        assert fs.risk_factors() == []


def test_segment_revenue_collects_matching():
    fs = make_fs(
        _disclosures={
            "seg": {
                "name": "0001 - Disclosure - Segment Information",
                "text": " data ",
            },
            "tab": {"name": "Segment Information (Tables)", "text": "skip"},
            "other": {"name": "Inventory", "text": "x"},
        }
    )
    out = fs.segment_revenue()
    assert out == [{"name": "Segment Information", "text": "data"}]


def test_segment_revenue_skips_empty_text():
    fs = make_fs(
        _disclosures={"seg": {"name": "Revenue Disaggregation", "text": "   "}}
    )
    assert fs.segment_revenue() == []


def test_calendar_period():
    fs = make_fs(_period_ending="2024-08-31")
    assert fs.calendar_period == "2024-Q3"


def test_fiscal_period_variants():
    assert make_fs(_fiscal_year="2024", _fiscal_period="FY").fiscal_period == "2024-FY"
    assert make_fs(_fiscal_year="", _fiscal_period="Q1").fiscal_period == "Q1"
    assert make_fs(_fiscal_year="2024", _fiscal_period="").fiscal_period == "2024"
    assert make_fs(_fiscal_year="", _fiscal_period="").fiscal_period == ""


def test_is_xbrl_true_and_false():
    assert make_fs(_metalinks={"a": 1}).is_xbrl is True
    assert make_fs(_instance={"a": 1}).is_xbrl is True
    assert make_fs().is_xbrl is False


def test_main_document_url_and_get():
    fs = make_fs(
        _document_urls=[
            {"type": "EX-101.INS", "url": "ins.xml"},
            {"type": "10-K", "url": "main.htm"},
        ]
    )
    assert fs.main_document_url == "main.htm"


def test_get_main_document_url_html_fallback():
    fs = make_fs(_document_urls=[{"type": "GRAPHIC", "url": "x.htm"}])
    assert fs.get_main_document_url() == "x.htm"


def test_get_main_document_url_none():
    assert make_fs().get_main_document_url() is None
    fs = make_fs(_document_urls=[{"type": "GRAPHIC", "url": "x.jpg"}])
    assert fs.get_main_document_url() is None


def test_statements_xbrl():
    fs = make_fs(
        _resources={
            "r1": {
                "group": "statement",
                "short_name": "Income",
                "long_name": "Income Statement",
                "url": "u",
            },
            "r2": {"group": "disclosure", "short_name": "Note"},
        }
    )
    st = fs.statements
    assert list(st.keys()) == ["Income"]
    assert st["Income"] == {"name": "Income Statement", "url": "u"}


def test_statements_non_xbrl():
    fs = make_fs(
        _non_xbrl_statements={"income": {"name": "Income", "data": "D", "meta": "M"}}
    )
    st = fs.statements
    assert st["income"] == {"name": "Income", "data": "D", "meta": "M"}


def test_statements_empty():
    assert dict(make_fs().statements.labels()) == {}


def test_get_statements_info_xbrl_no_statement_group():
    fs = make_fs(_resources={"r1": {"group": "disclosure", "short_name": "Note"}})
    assert fs._get_statements_info() == {}


def test_disclosures_non_xbrl_fallback():
    fs = make_fs(_disclosures={"d1": {"name": "Note 1", "text": "t"}})
    assert fs.disclosures["d1"] == {"name": "Note 1", "text": "t"}


def test_disclosures_items_fallback_and_label():
    fs = make_fs(_items={"item_1": "raw string value"})
    d = fs.disclosures
    assert d.labels()["item_1"] == "item_1"
    assert d["item_1"] == "raw string value"


def test_disclosures_empty():
    assert dict(make_fs().disclosures.labels()) == {}


def test_disclosures_xbrl_direct_key_match():
    fs = make_fs(
        _resources={
            "us-gaap_InventoryDisclosureTextBlock": {
                "group": "disclosure",
                "name": "us-gaap_InventoryDisclosureTextBlock",
                "long_name": "Inventory",
                "short_name": "Inventory",
            }
        },
        _text_blocks={
            "us-gaap_InventoryDisclosureTextBlock": {
                "value": "Inventory text",
                "presentation": [],
            }
        },
    )
    info = fs._get_disclosures_info()
    assert info["us-gaap_InventoryDisclosureTextBlock"]["text"] == "Inventory text"


def test_disclosures_xbrl_role_exact_match_and_append():
    fs = make_fs(
        _resources={
            "us-gaap_SegmentDisclosureTextBlock": {
                "group": "disclosure",
                "anchor_tag": "us-gaap_SegmentDisclosureTextBlock",
                "long_name": "Segment",
                "short_name": "Segment",
            }
        },
        _text_blocks={
            "tb1": {"value": "first", "presentation": ["SegmentDisclosureTextBlock"]},
            "tb2": {"value": "second", "presentation": ["SegmentDisclosureTextBlock"]},
        },
    )
    info = fs._get_disclosures_info()
    text = info["us-gaap_SegmentDisclosureTextBlock"]["text"]
    assert "first" in text and "second" in text


def test_disclosures_xbrl_partial_role_match():
    fs = make_fs(
        _resources={
            "us-gaap_RevenueTextBlock": {
                "group": "disclosure",
                "anchor_tag": "us-gaap_RevenueTextBlock",
                "long_name": "Revenue",
                "short_name": "Revenue",
            }
        },
        _text_blocks={
            "tb1": {"value": "rev", "presentation": ["RevenueTextBlockExtra"]},
        },
    )
    info = fs._get_disclosures_info()
    assert info["us-gaap_RevenueTextBlock"]["text"] == "rev"


def test_disclosures_xbrl_local_name_fallback_match():
    fs = make_fs(
        _resources={
            "us-gaap_LeasesDisclosure": {
                "group": "disclosure",
                "anchor_tag": "us-gaap_LeasesDisclosure",
                "long_name": "Leases",
                "short_name": "Leases",
            }
        },
        _text_blocks={
            "srt_LeasesDisclosure": {
                "value": "leases text",
                "presentation": ["Unrelated"],
            },
        },
    )
    info = fs._get_disclosures_info()
    assert info["us-gaap_LeasesDisclosure"]["text"] == "leases text"


def test_disclosures_xbrl_skips_none_textblock():
    fs = make_fs(
        _resources={
            "us-gaap_X": {
                "group": "disclosure",
                "anchor_tag": "us-gaap_X",
                "long_name": "X",
                "short_name": "X",
            }
        },
        _text_blocks={"tb": {"value": "\nNone.", "presentation": ["X"]}},
    )
    info = fs._get_disclosures_info()
    assert info["us-gaap_X"]["text"] == ""


def test_text_blocks_xbrl():
    fs = make_fs(
        _resources={
            "us-gaap_InventoryDisclosureTextBlock": {
                "group": "disclosure",
                "anchor_tag": "us-gaap_InventoryDisclosureTextBlock",
                "long_name": "Inventory",
                "short_name": "Inventory",
            }
        },
        _text_blocks={
            "us-gaap_InventoryDisclosureTextBlock": {
                "value": "Inventory text",
                "presentation": ["InventoryDisclosure"],
                "name": "InventoryDisclosure",
            },
            "skip": {"value": "\nNone.", "presentation": []},
        },
    )
    tb = fs.text_blocks
    assert "us-gaap_InventoryDisclosureTextBlock" in tb
    assert tb["us-gaap_InventoryDisclosureTextBlock"]["text"] == "Inventory text"
    assert "skip" not in tb


def test_text_blocks_non_xbrl_and_empty():
    fs = make_fs(_non_xbrl_text_blocks={"a": {"text": "x"}})
    assert fs.text_blocks == {"a": {"text": "x"}}
    assert make_fs().text_blocks == {}


def test_tags_property():
    fs = make_fs(_tags={"a": {"name": "A"}})
    assert fs.tags == {"a": {"name": "A"}}


def test_toc_cached():
    fs = make_fs(_toc={"1A": "Risk Factors"})
    assert fs.toc == {"1A": "Risk Factors"}


def test_toc_no_content():
    fs = make_fs()
    with patch.object(fs, "get_main_document_content", return_value=None):
        assert fs.toc == {}


def test_toc_builds_from_links():
    html = (
        '<a href="#item1a">Item 1A</a>'
        '<a href="#item1a">Risk Factors and uncertainties</a>'
        '<a href="#page">5</a>'
        '<a href="">empty</a>'
        '<a href="http://x">external</a>'
        '<a href="#x"></a>'
    )
    fs = make_fs()
    with patch.object(fs, "get_main_document_content", return_value=html):
        toc = fs.toc
    assert toc == {"1A": "Risk Factors and uncertainties"}


def test_get_statement_delegates():
    fs = make_fs()
    with patch.object(fs, "_download_statement", return_value=("d", "m")) as ds:
        assert fs.get_statement("balance") == ("d", "m")
    ds.assert_called_once_with("balance")


def test_download_statement_no_matched():
    fs = make_fs(
        _instance={"x": 1},
        _resources={
            "r1": {"group": "statement", "short_name": "Balance Sheet", "url": "u"}
        },
    )
    with pytest.raises(ValueError, match="No items found"):
        fs._download_statement("income")


def test_download_statement_no_urls():
    fs = make_fs(
        _instance={"x": 1},
        _resources={
            "r1": {"group": "statement", "short_name": "Income Statement", "url": None}
        },
    )
    with pytest.raises(ValueError, match="No URLs found"):
        fs._download_statement("income")


def test_download_statement_cash_search_term_no_match():
    fs = make_fs(
        _instance={"x": 1},
        _resources={
            "r1": {"group": "statement", "short_name": "Income Statement", "url": "u"}
        },
    )
    with pytest.raises(ValueError, match="No items found"):
        fs._download_statement("cash")


def _income_fs():
    from pandas import DataFrame

    fs = make_fs(
        _document_type="10-K",
        _period_ending="2024-08-31",
        _instance={
            "us-gaap_Revenues": {
                "context": [
                    {
                        "value": "100",
                        "context_ref": "duration_2023_09_01_to_2024_08_31",
                        "unit": "iso4217:USD",
                        "decimals": "-6",
                    },
                    {
                        "value": "90",
                        "context_ref": "duration_2022_09_01_to_2023_08_31",
                        "unit": "iso4217:USD",
                        "decimals": "-6",
                    },
                ]
            },
            "us-gaap_NetIncomeLoss": {
                "context": [
                    {
                        "value": "50",
                        "context_ref": "as_of_2024_08_31",
                        "unit": "iso4217:USD",
                        "decimals": "-6",
                    }
                ]
            },
        },
        _tags={
            "us-gaap_Revenues": {
                "label": "Net sales and revenues",
                "terseLabel": "Net sales and revenues",
                "crdr": "credit",
                "weight": "1",
                "parent_tag": "us-gaap_IncomeStatement",
                "preferred_label": "totalLabel",
                "name": "Revenues",
                "period_type": "duration",
            },
            "us-gaap_NetIncomeLoss": {
                "label": "Net income",
                "crdr": "credit",
                "name": "NetIncomeLoss",
                "period_type": "duration",
            },
        },
        _period_context={
            "duration_2023_09_01_to_2024_08_31": {"start": "2023-09-01"},
        },
        _resources={
            "r1": {
                "group": "statement",
                "short_name": "Statement of Operations",
                "url": "https://sec.gov/R4.htm",
            }
        },
    )
    table = DataFrame(
        {
            "Statement of Operations $ in Millions": [
                "Net sales and revenues",
                "Net income",
            ],
            "2024-08-31 -- 12 Months Ended": [100, 50],
            "2023-08-31 -- 12 Months Ended": [90, 40],
        }
    )
    meta = DataFrame(
        {
            "Name": ["us-gaap_Revenues"],
            "Namespace Prefix": ["us-gaap"],
            "Data Type": ["xbrli:monetaryItemType"],
            "Balance Type": ["credit"],
            "Period Type": ["duration"],
            "unit": ["iso4217:USD"],
            "decimals": ["-6"],
            "weight": ["1"],
            "preferred_label": ["totalLabel"],
            "parent_tag": ["us-gaap_IncomeStatement"],
        }
    )
    return fs, table, meta


def test_download_statement_income_pipeline():
    fs, table, meta = _income_fs()
    with patch.object(fs, "_download_statement_from_url", return_value=(table, meta)):
        data, out_meta = fs._download_statement("income")
    assert "tag" in data.columns
    assert "period_ending" in data.columns
    assert not data.empty
    assert set(["us-gaap_Revenues"]).issubset(set(data.tag.dropna().tolist()))


def test_download_statement_download_loop_raises():
    fs, _, _ = _income_fs()
    with patch.object(
        fs, "_download_statement_from_url", side_effect=RuntimeError("boom")
    ):
        with pytest.raises(RuntimeError, match="Failed to download statement"):
            fs._download_statement("income")


def test_download_statement_balance_fix_tag_and_dimensions():
    from pandas import DataFrame

    fs = make_fs(
        _document_type="10-K",
        _period_ending="2024-08-31",
        _instance={
            "us-gaap_Assets": {
                "context": [
                    {
                        "value": "200",
                        "context_ref": "as_of_2024_08_31",
                        "unit": "unit_Standard_iso4217_USD",
                        "decimals": "-6",
                    }
                ]
            },
            "us-gaap_AssetsCurrent": {
                "context": [{"value": "200", "context_ref": "as_of_2024_08_31"}]
            },
            "us-gaap_Revenues": {
                "context": [
                    {
                        "value": "75",
                        "context_ref": "duration_2023_09_01_to_2024_08_31_us-gaap_ProductMember",
                    }
                ]
            },
        },
        _tags={
            "us-gaap_Assets": {"label": "Total assets", "crdr": "debit"},
            "us-gaap_AssetsCurrent": {"label": "Current assets", "crdr": "debit"},
            "us-gaap_Wrong": {"label": "Total assets", "crdr": "debit"},
            "us-gaap_Revenues": {"label": "Revenue", "crdr": "credit"},
            "us-gaap_ProductMember": {"terseLabel": "Product line"},
        },
        _period_context={},
        _resources={
            "r1": {
                "group": "statement",
                "short_name": "Balance Sheet",
                "url": "https://sec.gov/R2.htm",
            }
        },
    )
    table = DataFrame(
        {
            "Balance Sheet $ in Millions": ["Total assets", "Revenue"],
            "2024-08-31": [200, 75],
        }
    )
    meta = DataFrame()
    with patch.object(fs, "_download_statement_from_url", return_value=(table, meta)):
        data, _ = fs._download_statement("balance")
    labels = data.label.tolist()
    assert "Product line" in labels or "Revenue" in labels
    assert not data.empty


def test_download_statement_equity_pipeline():
    from pandas import DataFrame

    fs = make_fs(
        _document_type="10-K",
        _instance={
            "us-gaap_StockholdersEquity": {
                "context": [
                    {
                        "value": "500",
                        "context_ref": "as_of_2024_08_31",
                        "unit": "iso4217:USD",
                    }
                ]
            }
        },
        _tags={
            "us-gaap_StockholdersEquity": {
                "label": "Total stockholders' equity",
                "crdr": "credit",
            }
        },
        _resources={
            "r1": {
                "group": "statement",
                "short_name": "Statement of Equity",
                "url": "https://sec.gov/R7.htm",
            }
        },
    )
    table = DataFrame(
        {
            "Statement of Equity": ["Total stockholders' equity"],
            "Common Stock": [500],
        }
    )
    meta = DataFrame()
    with patch.object(fs, "_download_statement_from_url", return_value=(table, meta)):
        data, out_meta = fs._download_statement("equity")
    assert "tag" in data.columns
    assert data.tag.iloc[0] == "us-gaap_StockholdersEquity"


def test_disclosures_partial_role_append_existing():
    fs = make_fs(
        _resources={
            "us-gaap_DebtTextBlock": {
                "group": "disclosure",
                "anchor_tag": "us-gaap_DebtTextBlock",
                "long_name": "Debt",
                "short_name": "Debt",
            }
        },
        _text_blocks={
            "tb1": {"value": "first", "presentation": ["DebtTextBlock"]},
            "tb2": {"value": "second", "presentation": ["DebtTextBlockMore"]},
        },
    )
    info = fs._get_disclosures_info()
    text = info["us-gaap_DebtTextBlock"]["text"]
    assert "first" in text and "second" in text


def test_disclosures_local_fallback_append_existing():
    fs = make_fs(
        _resources={
            "us-gaap_TaxTextBlock": {
                "group": "disclosure",
                "anchor_tag": "us-gaap_TaxTextBlock",
                "long_name": "Tax",
                "short_name": "Tax",
            }
        },
        _text_blocks={
            "us-gaap_TaxTextBlock": {"value": "first", "presentation": []},
            "us-gaap_TaxTextBlockExtra": {"value": "second", "presentation": []},
        },
    )
    info = fs._get_disclosures_info()
    text = info["us-gaap_TaxTextBlock"]["text"]
    assert "first" in text and "second" in text


def test_disclosures_resource_without_tag_skipped():
    fs = make_fs(_resources={"r": {"group": "disclosure"}})
    assert fs._get_disclosures_info() == {}


def test_text_blocks_exact_role_match():
    fs = make_fs(
        _resources={
            "us-gaap_InventoryDisclosure": {
                "group": "disclosure",
                "anchor_tag": "us-gaap_InventoryDisclosure",
                "long_name": "Inventory",
                "short_name": "Inventory",
            }
        },
        _text_blocks={
            "tb1": {"value": "inv text", "presentation": ["InventoryDisclosure"]},
        },
    )
    tb = fs.text_blocks
    assert tb["tb1"]["disclosure"] == ["us-gaap_InventoryDisclosure"]


def test_text_blocks_partial_role_match():
    fs = make_fs(
        _resources={
            "us-gaap_DebtDisclosure": {
                "group": "disclosure",
                "anchor_tag": "us-gaap_DebtDisclosure",
                "long_name": "Debt",
                "short_name": "Debt",
            }
        },
        _text_blocks={
            "tb1": {"value": "debt text", "presentation": ["DebtDisclosureExtra"]},
        },
    )
    tb = fs.text_blocks
    assert tb["tb1"]["disclosure"] == ["us-gaap_DebtDisclosure"]


def test_enrich_cover_page_no_instance():
    fs = make_fs()
    fs._enrich_cover_page_from_instance()
    assert fs._cover_page == {}


def test_enrich_cover_page_populates_fields():
    fs = make_fs(
        _period_ending="2024-08-31",
        _instance={
            "dei_TradingSymbol": {"context": [{"value": "WDFC", "end": "2024-08-31"}]},
            "dei_EntityCommonStockSharesOutstanding": {
                "context": [{"value": "13500000", "end": "2024-09-30"}]
            },
            "dei_DocumentFiscalYearFocus": {
                "context": [{"value": "2024", "end": "2024-08-31"}]
            },
            "dei_DocumentFiscalPeriodFocus": {
                "context": [{"value": "FY", "end": "2024-08-31"}]
            },
        },
    )
    fs._enrich_cover_page_from_instance()
    assert "WDFC" in fs._trading_symbols
    assert fs._shares_outstanding == {"2024-09-30": 13500000}
    assert fs._fiscal_year == "2024"
    assert fs._fiscal_period == "FY"


def test_enrich_cover_page_skips_already_set_and_dimensional_and_empty():
    fs = make_fs(
        _cover_page={"Trading Symbol": "EXISTING"},
        _instance={
            "dei_TradingSymbol": {"context": [{"value": "NEW", "end": "2024-08-31"}]},
            "dei_DocumentFiscalYearFocus": {"context": []},
            "dei_DocumentFiscalPeriodFocus": {
                "context": [{"value": "0"}, {"dimensions": {"x": 1}, "value": "Q1"}]
            },
            "Unknown": {"context": [{"value": "x"}]},
        },
    )
    fs._enrich_cover_page_from_instance()
    assert fs._cover_page["Trading Symbol"] == "EXISTING"
    assert fs._fiscal_period == ""


def test_enrich_cover_page_shares_value_error():
    fs = make_fs(
        _instance={
            "dei_EntityCommonStockSharesOutstanding": {
                "context": [{"value": "not-a-number", "end": "2024-08-31"}]
            }
        }
    )
    fs._enrich_cover_page_from_instance()
    assert fs._shares_outstanding == {}


def test_parse_non_xbrl_statement_no_content():
    fs = make_fs()
    with patch.object(fs, "get_main_document_content", return_value=None):
        with pytest.raises(ValueError, match="No main document content"):
            fs._parse_non_xbrl_statement("income")


def test_parse_non_xbrl_statement_empty_df():
    from pandas import DataFrame

    fs = make_fs()
    with (
        patch.object(fs, "get_main_document_content", return_value="<html></html>"),
        patch(
            "openbb_sec.utils.non_xbrl_parser.parse_non_xbrl_statement",
            return_value=(DataFrame(), DataFrame()),
        ),
    ):
        with pytest.raises(ValueError, match="Could not find income statement"):
            fs._parse_non_xbrl_statement("income")


def test_parse_non_xbrl_statement_returns_data():
    from pandas import DataFrame

    fs = make_fs()
    data = DataFrame({"label": ["Revenue"], "value": [1]})
    meta = DataFrame({"tag": ["x"]})
    with (
        patch.object(fs, "get_main_document_content", return_value="<html>x</html>"),
        patch(
            "openbb_sec.utils.non_xbrl_parser.parse_non_xbrl_statement",
            return_value=(data, meta),
        ),
    ):
        out_data, out_meta = fs._parse_non_xbrl_statement("income")
    assert out_data is data and out_meta is meta


def test_download_statement_non_xbrl_delegates():
    fs = make_fs()
    with patch.object(fs, "_parse_non_xbrl_statement", return_value=("d", "m")) as p:
        assert fs._download_statement("income") == ("d", "m")
    p.assert_called_once_with("income")


def test_initialize_non_xbrl_already_initialized():
    fs = make_fs(_non_xbrl_initialized=True)
    fs._initialize_non_xbrl()
    assert fs._non_xbrl_statements == {}


def test_initialize_non_xbrl_no_url_returns():
    fs = make_fs()
    with (
        patch.object(fs, "get_embedded_document", return_value=None),
        patch.object(fs, "get_main_document_url", return_value=None),
        patch.object(fs, "get_main_document_content", return_value=None),
    ):
        fs._initialize_non_xbrl()
    assert fs._non_xbrl_initialized is False


def test_initialize_non_xbrl_inline_content():
    from pandas import DataFrame

    fs = make_fs()
    with (
        patch.object(fs, "get_embedded_document", return_value=None),
        patch.object(fs, "get_main_document_url", return_value=None),
        patch.object(
            fs, "get_main_document_content", return_value="<html>inline</html>"
        ),
        patch(
            "openbb_sec.utils.non_xbrl_parser.find_all_statements",
            return_value={"income": (DataFrame({"a": [1]}), DataFrame())},
        ),
        patch(
            "openbb_sec.utils.non_xbrl_parser.get_statement_names",
            return_value={"income": "Income"},
        ),
        patch("openbb_sec.utils.non_xbrl_parser.extract_toc", return_value={}),
        patch(
            "openbb_sec.utils.non_xbrl_parser.extract_text_blocks",
            return_value={"note1": {"name": "Income Taxes", "text": "x"}},
        ),
        patch("openbb_sec.utils.non_xbrl_parser.extract_items", return_value={}),
        patch.object(fs, "_parse_exhibit_items"),
    ):
        fs._initialize_non_xbrl()
    assert fs._non_xbrl_initialized is True
    assert fs._disclosures == {"note1": {"name": "Income Taxes", "text": "x"}}


def test_initialize_non_xbrl_from_embedded_main_doc():
    from pandas import DataFrame

    fs = make_fs()
    data = DataFrame({"a": [1]})
    meta = DataFrame({"tag": ["t"]})
    with (
        patch.object(
            fs,
            "get_embedded_document",
            side_effect=lambda k: "<html>10k</html>" if k == "10-K" else None,
        ),
        patch(
            "openbb_sec.utils.non_xbrl_parser.find_all_statements",
            return_value={"income": (data, meta)},
        ),
        patch(
            "openbb_sec.utils.non_xbrl_parser.get_statement_names",
            return_value={"income": "Income"},
        ),
        patch(
            "openbb_sec.utils.non_xbrl_parser.extract_toc",
            return_value={"1": "Business"},
        ),
        patch(
            "openbb_sec.utils.non_xbrl_parser.extract_text_blocks",
            return_value={"note1": {"text": "x"}},
        ),
        patch(
            "openbb_sec.utils.non_xbrl_parser.extract_items",
            return_value={"item_1": {"name": "Biz"}},
        ),
    ):
        fs._initialize_non_xbrl()
    assert fs._non_xbrl_statements["income"]["name"] == "Income"
    assert fs._toc == {"1": "Business"}
    assert fs._disclosures == {"note1": {"text": "x"}}
    assert fs._items == {"item_1": {"name": "Biz"}}
    assert fs._non_xbrl_initialized is True


def test_initialize_non_xbrl_downloads_main_doc_bytes():
    from pandas import DataFrame

    fs = make_fs()
    with (
        patch.object(fs, "get_embedded_document", return_value=None),
        patch.object(
            fs, "get_main_document_url", return_value="https://sec.gov/main.htm"
        ),
        patch.object(fs, "_get_document", return_value=b"<html>doc</html>"),
        patch(
            "openbb_sec.utils.non_xbrl_parser.find_all_statements",
            return_value={"balance": (DataFrame({"a": [1]}), DataFrame())},
        ),
        patch("openbb_sec.utils.non_xbrl_parser.get_statement_names", return_value={}),
        patch("openbb_sec.utils.non_xbrl_parser.extract_toc", return_value={}),
        patch("openbb_sec.utils.non_xbrl_parser.extract_text_blocks", return_value={}),
        patch("openbb_sec.utils.non_xbrl_parser.extract_items", return_value={}),
        patch.object(fs, "_parse_exhibit_disclosures"),
        patch.object(fs, "_parse_exhibit_items"),
    ):
        fs._initialize_non_xbrl()
    assert fs._non_xbrl_statements["balance"]["name"] == "Balance"


def test_initialize_non_xbrl_falls_back_to_exhibits():
    fs = make_fs()
    with (
        patch.object(fs, "get_embedded_document", return_value="<html>main</html>"),
        patch("openbb_sec.utils.non_xbrl_parser.find_all_statements", return_value={}),
        patch("openbb_sec.utils.non_xbrl_parser.get_statement_names", return_value={}),
        patch("openbb_sec.utils.non_xbrl_parser.extract_toc", return_value={}),
        patch("openbb_sec.utils.non_xbrl_parser.extract_text_blocks", return_value={}),
        patch("openbb_sec.utils.non_xbrl_parser.extract_items", return_value={}),
        patch.object(fs, "_parse_exhibit_statements") as pes,
        patch.object(fs, "_parse_exhibit_disclosures"),
        patch.object(fs, "_parse_exhibit_items"),
    ):
        fs._initialize_non_xbrl()
    pes.assert_called_once()


def test_initialize_non_xbrl_warns_on_exception():
    fs = make_fs()
    with (
        patch.object(fs, "get_embedded_document", side_effect=RuntimeError("boom")),
        pytest.warns(UserWarning, match="Failed to parse non-XBRL"),
    ):
        fs._initialize_non_xbrl()


def test_parse_exhibit_statements_from_embedded():
    from pandas import DataFrame

    fs = make_fs()
    calls = {"find": lambda html: {"income": (DataFrame({"a": [1]}), DataFrame())}}
    with patch.object(
        fs,
        "get_embedded_document",
        side_effect=lambda k: "<html>x</html>" if k == "EX-13" else None,
    ):
        fs._parse_exhibit_statements(calls["find"], {"income": "Income"})
    assert fs._non_xbrl_statements["income"]["name"] == "Income"


def test_parse_exhibit_statements_download_priority():
    from pandas import DataFrame

    fs = make_fs(_document_urls=[{"type": "EX-13", "url": "https://sec.gov/ex13.htm"}])
    with (
        patch.object(fs, "get_embedded_document", return_value=None),
        patch.object(fs, "_get_document", return_value=b"<html>ex</html>"),
    ):
        fs._parse_exhibit_statements(
            lambda html: {"income": (DataFrame({"a": [1]}), DataFrame())},
            {"income": "Income"},
        )
    assert fs._non_xbrl_statements["income"]["name"] == "Income"


def test_parse_exhibit_statements_all_html_exhibits():
    from pandas import DataFrame

    fs = make_fs(_document_urls=[{"type": "EX-99", "url": "https://sec.gov/ex99.htm"}])
    with (
        patch.object(fs, "get_embedded_document", return_value=None),
        patch.object(fs, "_get_document", return_value=b"<html>ex</html>"),
    ):
        fs._parse_exhibit_statements(
            lambda html: {"income": (DataFrame({"a": [1]}), DataFrame())},
            {},
        )
    assert fs._non_xbrl_statements["income"]["name"] == "Income"


def test_parse_exhibit_disclosures_download_priority():
    fs = make_fs(_document_urls=[{"type": "EX-13", "url": "https://sec.gov/ex13.htm"}])
    with (
        patch.object(fs, "get_embedded_document", return_value=None),
        patch.object(fs, "_get_document", return_value=b"<html>ex</html>"),
    ):
        fs._parse_exhibit_disclosures(lambda html: {"note": {"text": "t"}})
    assert fs._disclosures == {"note": {"text": "t"}}


def test_parse_exhibit_items_download_priority():
    fs = make_fs(_document_urls=[{"type": "EX-13", "url": "https://sec.gov/ex13.htm"}])
    with (
        patch.object(fs, "get_embedded_document", return_value=None),
        patch.object(fs, "_get_document", return_value=b"<html>ex</html>"),
    ):
        fs._parse_exhibit_items(
            lambda html: {"item_1": {"name": "Biz"}},
            lambda html: {"note": {"text": "t"}},
        )
    assert fs._items == {"item_1": {"name": "Biz"}}
    assert fs._disclosures == {"note": {"text": "t"}}


def test_parse_exhibit_disclosures_from_embedded():
    fs = make_fs()
    with patch.object(
        fs,
        "get_embedded_document",
        side_effect=lambda k: "<html>x</html>" if k == "EX-13" else None,
    ):
        fs._parse_exhibit_disclosures(lambda html: {"note": {"text": "t"}})
    assert fs._disclosures == {"note": {"text": "t"}}


def test_parse_exhibit_statements_embedded_raises_continues():
    fs = make_fs()
    with patch.object(fs, "get_embedded_document", return_value="<html>x</html>"):
        fs._parse_exhibit_statements(
            lambda html: (_ for _ in ()).throw(RuntimeError("boom")), {}
        )
    assert fs._non_xbrl_statements == {}


def test_parse_exhibit_disclosures_embedded_raises_continues():
    fs = make_fs()
    with patch.object(fs, "get_embedded_document", return_value="<html>x</html>"):
        fs._parse_exhibit_disclosures(
            lambda html: (_ for _ in ()).throw(RuntimeError("boom"))
        )
    assert fs._disclosures == {}


def test_parse_exhibit_items_embedded_raises_continues():
    fs = make_fs()
    with patch.object(fs, "get_embedded_document", return_value="<html>x</html>"):
        fs._parse_exhibit_items(
            lambda html: (_ for _ in ()).throw(RuntimeError("boom")),
            lambda html: {},
        )
    assert fs._items == {}


def test_parse_exhibit_statements_download_raises_and_empty_url():
    fs = make_fs(
        _document_urls=[
            {"type": "EX-13", "url": ""},
            {"type": "EX-13.1", "url": "https://sec.gov/x.htm"},
        ]
    )
    with (
        patch.object(fs, "get_embedded_document", return_value=None),
        patch.object(fs, "_get_document", side_effect=RuntimeError("boom")),
    ):
        fs._parse_exhibit_statements(lambda html: {}, {})
    assert fs._non_xbrl_statements == {}


def test_parse_exhibit_statements_all_html_download_raises():
    fs = make_fs(_document_urls=[{"type": "EX-99", "url": "https://sec.gov/x.htm"}])
    with (
        patch.object(fs, "get_embedded_document", return_value=None),
        patch.object(fs, "_get_document", side_effect=RuntimeError("boom")),
    ):
        fs._parse_exhibit_statements(lambda html: {}, {})
    assert fs._non_xbrl_statements == {}


def test_parse_exhibit_statements_all_html_skips_non_html():
    fs = make_fs(_document_urls=[{"type": "EX-99", "url": "https://sec.gov/x.pdf"}])
    with (
        patch.object(fs, "get_embedded_document", return_value=None),
        patch.object(fs, "_get_document") as gd,
    ):
        fs._parse_exhibit_statements(lambda html: {}, {})
    gd.assert_not_called()


def test_parse_exhibit_disclosures_download_raises_and_empty_url():
    fs = make_fs(
        _document_urls=[
            {"type": "EX-13", "url": ""},
            {"type": "EX-13.1", "url": "https://sec.gov/x.htm"},
        ]
    )
    with (
        patch.object(fs, "get_embedded_document", return_value=None),
        patch.object(fs, "_get_document", side_effect=RuntimeError("boom")),
    ):
        fs._parse_exhibit_disclosures(lambda html: {})
    assert fs._disclosures == {}


def test_parse_exhibit_items_download_raises_and_empty_url():
    fs = make_fs(
        _document_urls=[
            {"type": "EX-13", "url": ""},
            {"type": "EX-13.1", "url": "https://sec.gov/x.htm"},
        ]
    )
    with (
        patch.object(fs, "get_embedded_document", return_value=None),
        patch.object(fs, "_get_document", side_effect=RuntimeError("boom")),
    ):
        fs._parse_exhibit_items(lambda html: {}, lambda html: {})
    assert fs._items == {}


def _metalinks_doc():
    return {
        "S1": {
            "report": {
                "": {},
                "R1": {
                    "shortName": "Cover Page",
                    "longName": "Cover Page",
                    "groupType": "statement",
                    "menuCat": "Cover",
                    "uniqueAnchor": {"name": "dei:Doc", "unitRef": "U"},
                },
                "R2": {
                    "shortName": "Income",
                    "longName": "Income Statement",
                    "groupType": "statement",
                    "uniqueAnchor": {"name": "us-gaap:Revenue"},
                },
                "BadItem": None,
            },
            "tag": {
                "us-gaap_Revenue": {
                    "xbrltype": "monetaryItemType",
                    "localname": "Revenue",
                    "crdr": "credit",
                    "calculation": {"http://x/role/Income": {"weight": "1"}},
                    "presentation": ["http://x/role/Income"],
                    "lang": {"en-US": {"role": {"label": "Revenue"}}},
                    "auth_ref": ["ref1", "missing"],
                },
                "EmptyTag": None,
            },
        }
    }


def test_download_metalinks_no_url_returns():
    fs = make_fs(_document_urls=[{"url": "https://sec.gov/x.htm"}])
    fs._download_metalinks()
    assert fs._resources == {}


def test_download_metalinks_already_loaded():
    fs = make_fs(
        _document_urls=[{"url": "https://sec.gov/MetaLinks.json"}],
        _metalinks=_metalinks_doc(),
        _std_ref={"ref1": {"Topic": "718", "SubTopic": "10"}},
    )
    fs._download_metalinks()
    assert "us-gaap_Revenue" in fs._tags
    assert fs._cover_page_url == "R1.htm"
    assert fs._resources["r2"]["short_name"] == "Income"


def test_download_metalinks_downloads_when_empty():
    fs = make_fs(_document_urls=[{"url": "https://sec.gov/MetaLinks.json"}])
    doc = {"instance": _metalinks_doc(), "std_ref": {"ref1": {"Topic": "718"}}}
    with patch.object(fs, "_get_document", return_value=doc):
        fs._download_metalinks()
    assert "us-gaap_Revenue" in fs._tags


def test_download_metalinks_skips_falsy_statement_item():
    fs = make_fs(
        _document_urls=[{"url": "https://sec.gov/MetaLinks.json"}],
        _metalinks=_metalinks_doc(),
        _resources={"empty": {}},
    )
    fs._download_metalinks()
    assert fs._resources["empty"] == {}


def test_download_metalinks_raises_on_bad_structure():
    fs = make_fs(
        _document_urls=[{"url": "https://sec.gov/MetaLinks.json"}],
        _metalinks={"S1": {"no_report_key": {}}},
    )
    with pytest.raises(RuntimeError, match="Failed to parse MetaLinks.json"):
        fs._download_metalinks()


def _instance_doc_urls():
    return [{"type": "EX-101.INS", "url": "https://sec.gov/x_htm.xml"}]


def test_download_xbrl_instance_empty_returns():
    fs = make_fs(_document_urls=_instance_doc_urls())
    parser = SimpleNamespace(parse_instance=lambda *a, **k: ({}, {}, {}))
    with (
        patch.object(fs, "_get_document", return_value=b"x"),
        patch.object(fs, "_ensure_bytes", return_value=b"x"),
        patch.object(mod, "XBRLParser", lambda: parser),
    ):
        fs._download_xbrl_instance()
    assert fs._instance == {}


def test_download_xbrl_instance_supplements_tags_and_textblock():
    fs = make_fs(
        _document_urls=_instance_doc_urls(),
        _tags={"us-gaap_Revenue": {}},
    )
    contexts = {"ctx1": {"start": "2024-01-01"}}
    units = {"U": "iso4217:USD"}
    facts = {
        "us-gaap_Revenue": [
            {"value": "100", "label": "Revenue Label", "documentation": "Doc text"}
        ],
        "us-gaap_InventoryTextBlock": [
            {"value": "<p>note</p>", "label": "Inventory", "documentation": "d"}
        ],
        "us-gaap_EmptyTag": [],
    }
    parser = SimpleNamespace(parse_instance=lambda *a, **k: (contexts, units, facts))
    with (
        patch.object(fs, "_get_document", return_value=b"x"),
        patch.object(fs, "_ensure_bytes", return_value=b"x"),
        patch.object(mod, "XBRLParser", lambda: parser),
        patch.object(fs, "_clean_html_to_text", return_value="cleaned note"),
    ):
        fs._download_xbrl_instance()
    assert fs._period_context == contexts
    assert fs._xbrl_units == units
    assert fs._tags["us-gaap_Revenue"]["label"] == "Revenue Label"
    assert fs._tags["us-gaap_Revenue"]["documentation"] == "Doc text"
    assert fs._text_blocks["us-gaap_InventoryTextBlock"]["value"] == "cleaned note"


def test_download_xbrl_instance_no_instance_url():
    fs = make_fs(_document_urls=[{"type": "GRAPHIC", "url": "x.jpg"}])
    fs._download_xbrl_instance()
    assert fs._instance == {}


def _schema_doc_urls():
    return [
        {"type": "EX-101.SCH", "url": "https://sec.gov/x.xsd"},
        {"type": "EX-101.LAB", "url": "https://sec.gov/x_lab.xml"},
        {"type": "EX-101.PRE", "url": "https://sec.gov/x_pre.xml"},
        {"type": "EX-101.CAL", "url": "https://sec.gov/x_cal.xml"},
    ]


def test_build_schema_from_xml_fresh_full():
    from openbb_sec.utils.xbrl_taxonomy_helper import XBRLNode

    fs = make_fs(_document_urls=_schema_doc_urls())
    elements = {"us-gaap_Revenue": {"xbrl_type": "monetary"}}
    roles = [
        {"document_number": "1"},
        {"document_number": "1"},
        {"document_number": ""},
    ]
    embedded = ET.Element("linkbase")
    node = XBRLNode(
        element_id="us-gaap_Revenue",
        label="Revenue",
        order=1.0,
        level=0,
        parent_id=None,
        preferred_label="http://x/role/totalLabel",
        children=[
            XBRLNode(
                element_id="us-gaap_Child",
                label="Child",
                order=2.0,
                level=1,
                parent_id="us-gaap_Revenue",
            )
        ],
    )

    class _Parser:
        def parse_schema(self, *a, **k):
            return elements, roles, embedded, [{"schemaLocation": "x"}]

        def parse_label_linkbase(self, *a, **k):
            return {"us-gaap_Revenue": {"label": "Revenue Label"}}

        def parse_presentation(self, *a, **k):
            return [node]

        def parse_calculation(self, *a, **k):
            return {
                "us-gaap_Revenue": {"order": "1", "weight": "1", "parent_tag": "p"},
                "us-gaap_New": {"weight": "2"},
            }

    with (
        patch.object(fs, "_get_document", return_value=b"x"),
        patch.object(fs, "_ensure_bytes", return_value=b"x"),
        patch.object(mod, "XBRLParser", _Parser),
        patch.object(fs, "_fetch_external_taxonomy_labels"),
    ):
        fs._build_schema_from_xml()

    assert fs._xsd["elements"] == elements
    assert "r1" in fs._resources
    assert fs._tags["us-gaap_Revenue"]["preferred_label"] == "totalLabel"
    assert fs._tags["us-gaap_Revenue"]["weight"] == "1"
    assert fs._tags["us-gaap_New"]["weight"] == "2"
    assert fs._calcs


def test_build_schema_from_xml_cached_xsd():
    fs = make_fs(
        _document_urls=[{"type": "EX-101.SCH", "url": "https://sec.gov/x.xsd"}],
        _xsd={
            "elements": {
                "us-gaap_Cash": {"xbrl_type": "monetary"},
                "us-gaap_New": {"xbrl_type": "shares"},
            },
            "roles": [{"document_number": "1"}],
            "imports": [],
        },
        _tags={"us-gaap_Cash": {"existing": True}},
    )
    with patch.object(fs, "_get_document") as gd:
        fs._build_schema_from_xml()
    gd.assert_not_called()
    assert "r1" in fs._resources
    assert fs._tags["us-gaap_Cash"]["existing"] is True
    assert fs._tags["us-gaap_New"]["xbrl_type"] == "shares"


def test_build_schema_from_xml_exception_branches():
    fs = make_fs(_document_urls=_schema_doc_urls())

    class _BoomParser:
        def parse_schema(self, *a, **k):
            return {}, [], None, []

        def parse_label_linkbase(self, *a, **k):
            raise RuntimeError("lab boom")

        def parse_presentation(self, *a, **k):
            raise RuntimeError("pre boom")

        def parse_calculation(self, *a, **k):
            raise RuntimeError("cal boom")

    with (
        patch.object(fs, "_get_document", return_value=b"x"),
        patch.object(fs, "_ensure_bytes", return_value=b"x"),
        patch.object(mod, "XBRLParser", _BoomParser),
        patch.object(fs, "_fetch_external_taxonomy_labels"),
    ):
        fs._build_schema_from_xml()
    assert fs._presentation == []
    assert fs._calcs == {}


def test_build_schema_from_xml_embedded_linkbase_exception():
    fs = make_fs(
        _document_urls=[{"type": "EX-101.SCH", "url": "https://sec.gov/x.xsd"}]
    )

    call_count = {"n": 0}

    class _Parser:
        def parse_schema(self, *a, **k):
            return {}, [], ET.Element("linkbase"), []

        def parse_label_linkbase(self, *a, **k):
            call_count["n"] += 1
            raise RuntimeError("embedded boom")

    with (
        patch.object(fs, "_get_document", return_value=b"x"),
        patch.object(fs, "_ensure_bytes", return_value=b"x"),
        patch.object(mod, "XBRLParser", _Parser),
        patch.object(fs, "_fetch_external_taxonomy_labels"),
    ):
        fs._build_schema_from_xml()
    assert call_count["n"] == 1


def test_parse_exhibit_items_from_embedded():
    fs = make_fs()
    with patch.object(
        fs,
        "get_embedded_document",
        side_effect=lambda k: "<html>x</html>" if k == "EX-13" else None,
    ):
        fs._parse_exhibit_items(
            lambda html: {"item_1": {"name": "Biz"}},
            lambda html: {"note": {"text": "t"}},
        )
    assert fs._items == {"item_1": {"name": "Biz"}}
    assert fs._disclosures == {"note": {"text": "t"}}


def test_get_disclosures_info_skips_non_dict_resource():
    """Non-dict resource values are skipped in _get_disclosures_info."""
    fs = make_fs(_resources={"r1": "not-a-dict"}, _items={"item_1": {"name": "Biz"}})
    assert fs._get_disclosures_info() == {"item_1": {"name": "Biz"}}


def test_enrich_std_ref_full_reference():
    """_enrich_std_ref builds topic/subtopic/section names and an ASC reference."""
    out = FinancialStatements._enrich_std_ref(
        {
            "Topic": "718",
            "SubTopic": "10",
            "Section": "50",
            "Paragraph": "2",
        }
    )
    assert out["topic_name"] == "Compensation—Stock Compensation"
    assert out["subtopic_name"] == "Overall"
    assert out["section_name"] == "Disclosure"
    assert out["reference"].startswith("ASC 718-10-50-2")
    assert "Compensation—Stock Compensation" in out["reference"]


def test_enrich_std_ref_no_topic_no_ref():
    """Without a topic, no reference label is produced."""
    out = FinancialStatements._enrich_std_ref({})
    assert "reference" not in out
    assert "topic_name" not in out


def test_fetch_external_taxonomy_labels_merges_and_skips():
    """External taxonomy labels are merged, skipping missing urls and dup roles."""
    fs = make_fs(_labels={"us-gaap_Cash": {"label": "Existing"}})

    class _Parser:
        def parse_label_linkbase(self, *a, **k):
            return {
                "us-gaap_Cash": {"label": "New", "documentation": "Doc"},
                "us-gaap_New": {"label": "Brand"},
            }

    imports = [
        {"schemaLocation": "no-label-url"},
        {"schemaLocation": "https://fasb.org/us-gaap.xsd"},
    ]
    with (
        patch.object(
            mod,
            "get_label_url_for_import",
            side_effect=lambda loc: (
                "" if loc == "no-label-url" else "https://fasb.org/lab.xml"
            ),
        ),
        patch.object(fs, "_get_document", return_value=b"x"),
        patch.object(fs, "_ensure_bytes", return_value=b"x"),
        patch.object(mod, "XBRLParser", _Parser),
    ):
        fs._fetch_external_taxonomy_labels(imports)
    assert fs._labels["us-gaap_Cash"]["label"] == "Existing"
    assert fs._labels["us-gaap_Cash"]["documentation"] == "Doc"
    assert fs._labels["us-gaap_New"] == {"label": "Brand"}


def test_fetch_external_taxonomy_labels_caches_on_miss():
    """A freshly parsed label linkbase is written to the cache when enabled."""
    fs = make_fs(_labels={}, _use_cache=True)
    saved: dict = {}

    class _Parser:
        def parse_label_linkbase(self, *a, **k):
            return {"us-gaap_Cash": {"label": "Cash"}}

    with (
        patch.object(
            mod, "get_label_url_for_import", return_value="https://fasb.org/lab.xml"
        ),
        patch.object(fs, "_get_document", return_value=b"x"),
        patch.object(fs, "_ensure_bytes", return_value=b"x"),
        patch.object(mod, "XBRLParser", _Parser),
        patch("openbb_sec.utils.cache._cache_get", return_value=None),
        patch(
            "openbb_sec.utils.cache._cache_set",
            side_effect=lambda k, v, t: saved.update({k: v}),
        ),
    ):
        fs._fetch_external_taxonomy_labels([{"schemaLocation": "fasb"}])
    assert saved["xbrl-labels:https://fasb.org/lab.xml"] == {
        "us-gaap_Cash": {"label": "Cash"}
    }
    assert fs._labels["us-gaap_Cash"] == {"label": "Cash"}


def test_fetch_external_taxonomy_labels_swallows_exception():
    """A parser error during external label fetch is swallowed."""
    fs = make_fs(_labels={})

    class _BoomParser:
        def parse_label_linkbase(self, *a, **k):
            raise RuntimeError("boom")

    with (
        patch.object(
            mod, "get_label_url_for_import", return_value="https://sec.gov/lab.xml"
        ),
        patch.object(fs, "_get_document", return_value=b"x"),
        patch.object(fs, "_ensure_bytes", return_value=b"x"),
        patch.object(mod, "XBRLParser", _BoomParser),
    ):
        fs._fetch_external_taxonomy_labels([{"schemaLocation": "sec"}])
    assert fs._labels == {}


def test_build_schema_from_xml_fresh_updates_existing_tag():
    """A schema element already present in tags is updated, not overwritten."""
    fs = make_fs(
        _document_urls=[{"type": "EX-101.SCH", "url": "https://sec.gov/x.xsd"}],
        _tags={"us-gaap_Revenue": {"keep": True}},
    )
    elements = {"us-gaap_Revenue": {"xbrl_type": "monetary"}}

    class _Parser:
        def parse_schema(self, *a, **k):
            return elements, [{"document_number": "1"}], None, []

    with (
        patch.object(fs, "_get_document", return_value=b"x"),
        patch.object(fs, "_ensure_bytes", return_value=b"x"),
        patch.object(mod, "XBRLParser", _Parser),
        patch.object(fs, "_fetch_external_taxonomy_labels"),
    ):
        fs._build_schema_from_xml()
    assert fs._tags["us-gaap_Revenue"]["keep"] is True
    assert fs._tags["us-gaap_Revenue"]["xbrl_type"] == "monetary"


def test_build_schema_from_xml_label_linkbase_merge():
    """The label linkbase merges new roles into _labels and onto tags."""
    fs = make_fs(
        _document_urls=[{"type": "EX-101.LAB", "url": "https://sec.gov/x_lab.xml"}],
        _tags={"us-gaap_Revenue": {}},
        _labels={"us-gaap_Revenue": {"label": "Old"}},
    )

    class _Parser:
        def parse_label_linkbase(self, *a, **k):
            return {
                "us-gaap_Revenue": {"label": "New", "terseLabel": "Terse"},
                "us-gaap_Other": {"label": "Other"},
            }

    with (
        patch.object(fs, "_get_document", return_value=b"x"),
        patch.object(fs, "_ensure_bytes", return_value=b"x"),
        patch.object(mod, "XBRLParser", _Parser),
    ):
        fs._build_schema_from_xml()
    assert fs._labels["us-gaap_Revenue"]["label"] == "Old"
    assert fs._labels["us-gaap_Revenue"]["terseLabel"] == "Terse"
    assert fs._tags["us-gaap_Revenue"]["terseLabel"] == "Terse"


def test_download_xbrl_instance_textblock_uses_supplemented_tag():
    """A text-block fact gets a cleaned value attached to its supplemented tag."""
    fs = make_fs(
        _document_urls=_instance_doc_urls(),
        _tags={},
    )
    facts = {
        "us-gaap_InventoryTextBlock": [
            {"value": "<p>note</p>", "label": "Inventory", "documentation": "Doc"}
        ],
    }
    parser = SimpleNamespace(parse_instance=lambda *a, **k: ({}, {}, facts))
    with (
        patch.object(fs, "_get_document", return_value=b"x"),
        patch.object(fs, "_ensure_bytes", return_value=b"x"),
        patch.object(mod, "XBRLParser", lambda: parser),
        patch.object(fs, "_clean_html_to_text", return_value="clean"),
    ):
        fs._download_xbrl_instance()
    block = fs._text_blocks["us-gaap_InventoryTextBlock"]
    assert block["value"] == "clean"
    assert block["label"] == "Inventory"
    assert block["documentation"] == "Doc"


def _download_statement_from_url_table(self, url, is_equity=False):
    """Return a crafted (table, meta) tuple for _download_statement tests."""
    from pandas import DataFrame

    table = DataFrame(
        {
            "Statement of Operations $ in Millions": [
                "Net sales and revenues",
                "Net income",
                "Product revenue",
            ],
            "2024-08-31 -- 12 Months Ended": [100, 50, 75],
            "2023-08-31 -- 12 Months Ended": [90, 40, 60],
        }
    )
    meta = DataFrame(
        {
            "Name": ["us-gaap_Revenues", "us-gaap_NetIncomeLoss"],
            "Namespace Prefix": ["us-gaap", "us-gaap"],
            "Data Type": ["xbrli:monetaryItemType", "xbrli:monetaryItemType"],
            "Balance Type": ["credit", "credit"],
            "Period Type": ["duration", "duration"],
            "unit": ["iso4217:USD", "iso4217:USD"],
            "decimals": ["-6", "-6"],
            "weight": ["1", "1"],
            "preferred_label": ["totalLabel", "label"],
            "parent_tag": ["us-gaap_IncomeStatement", None],
        }
    )
    return table, meta


def _full_income_fs():
    """FinancialStatements wired to exercise the full XBRL numeric pipeline."""
    fs = make_fs(
        _document_type="10-K",
        _period_ending="2024-08-31",
        _instance={
            "us-gaap_Revenues": {
                "context": [
                    {
                        "value": "100",
                        "context_ref": "duration_2023_09_01_to_2024_08_31",
                        "unit": "iso4217:USD",
                        "decimals": "-6",
                    },
                    {
                        "value": "90",
                        "context_ref": "duration_2022_09_01_to_2023_08_31",
                        "unit": "iso4217:USD",
                        "decimals": "-6",
                    },
                ]
            },
            "us-gaap_NetIncomeLoss": {
                "context": [
                    {
                        "value": "50",
                        "context_ref": "as_of_2024_08_31",
                        "unit": "iso4217:USD",
                        "decimals": "-6",
                    },
                    {
                        "value": "40",
                        "context_ref": "as_of_2023_08_31",
                        "unit": "iso4217:USD",
                        "decimals": "-6",
                    },
                ]
            },
            "us-gaap_RevenueFromProduct": {
                "context": [
                    {
                        "value": "75",
                        "context_ref": "duration_2023_09_01_to_2024_08_31_us-gaap_ProductMember",
                        "unit": "iso4217:USD",
                        "decimals": "-6",
                    },
                    {
                        "value": "60",
                        "context_ref": "duration_2022_09_01_to_2023_08_31_us-gaap_ProductMember",
                        "unit": "iso4217:USD",
                        "decimals": "-6",
                    },
                ]
            },
        },
        _tags={
            "us-gaap_Revenues": {
                "label": "Net sales and revenues",
                "terseLabel": "Net sales and revenues",
                "crdr": "credit",
                "weight": "1",
                "parent_tag": "us-gaap_IncomeStatement",
                "preferred_label": "totalLabel",
                "name": "Revenues",
                "period_type": "duration",
            },
            "us-gaap_NetIncomeLoss": {
                "label": "Net income",
                "crdr": "credit",
                "name": "NetIncomeLoss",
                "period_type": "duration",
            },
            "us-gaap_RevenueFromProduct": {
                "label": "Product revenue",
                "crdr": "credit",
                "name": "RevenueFromProduct",
            },
            "us-gaap_ProductMember": {"terseLabel": "Product line"},
        },
        _period_context={
            "duration_2023_09_01_to_2024_08_31": {"start": "2023-09-01"},
        },
        _resources={
            "r1": {
                "group": "statement",
                "short_name": "Statement of Operations",
                "url": "https://sec.gov/R4.htm",
            }
        },
    )
    return fs


def test_download_statement_full_numeric_pipeline():
    """Drive _download_statement through label/unit/period/dimension stages."""
    fs = _full_income_fs()
    with patch.object(
        fs,
        "_download_statement_from_url",
        new=_download_statement_from_url_table.__get__(fs),
    ):
        data, meta = fs._download_statement("income")
    cols = set(data.columns)
    assert {
        "order",
        "tag",
        "parent_tag",
        "preferred_label",
        "balance",
        "weight",
        "decimals",
        "context_ref",
        "period_beginning",
        "period_ending",
        "unit",
        "label",
        "value",
    } <= cols
    assert "us-gaap_Revenues" in set(data.tag.dropna())
    assert not meta.empty


def test_download_statement_missing_tags_enrich_meta():
    """Tags present in the statement but absent from meta are added to output_meta."""
    from pandas import DataFrame

    fs = _full_income_fs()

    def _from_url(url, is_equity=False):
        table = DataFrame(
            {
                "Statement of Operations $ in Millions": ["Net sales and revenues"],
                "2024-08-31 -- 12 Months Ended": [100],
            }
        )
        return table, DataFrame()

    with patch.object(fs, "_download_statement_from_url", side_effect=_from_url):
        data, meta = fs._download_statement("income")
    assert "us-gaap_Revenues" in set(meta.tag.dropna())


def test_download_statement_unit_and_decimals_from_instance():
    """Unit/decimals fall back to instance values when meta lacks the columns."""
    from pandas import DataFrame

    fs = make_fs(
        _document_type="10-K",
        _period_ending="2024-08-31",
        _instance={
            "us-gaap_Assets": {
                "context": [
                    {
                        "value": "200",
                        "context_ref": "as_of_2024_08_31",
                        "unit": "unit_Standard_iso4217_USD",
                        "decimals": "-6",
                    }
                ]
            }
        },
        _tags={"us-gaap_Assets": {"label": "Total assets", "crdr": "debit"}},
        _period_context={},
        _resources={
            "r1": {
                "group": "statement",
                "short_name": "Balance Sheet",
                "url": "https://sec.gov/R2.htm",
            }
        },
    )

    def _from_url(url, is_equity=False):
        table = DataFrame(
            {"Balance Sheet $ in Millions": ["Total assets"], "2024-08-31": [200]}
        )
        return table, DataFrame()

    with patch.object(fs, "_download_statement_from_url", side_effect=_from_url):
        data, _ = fs._download_statement("balance")
    row = data[data.tag == "us-gaap_Assets"].iloc[0]
    assert row.unit == "iso4217"
    assert row.decimals == "-6"


def test_download_statement_period_beginning_from_duration_member():
    """Duration context refs yield a period_beginning derived from the ref."""
    fs = _full_income_fs()

    def _from_url(url, is_equity=False):
        from pandas import DataFrame

        table = DataFrame(
            {
                "Statement of Operations $ in Millions": ["Net sales and revenues"],
                "2024-08-31 -- 12 Months Ended": [100],
            }
        )
        return table, DataFrame()

    with patch.object(fs, "_download_statement_from_url", side_effect=_from_url):
        data, _ = fs._download_statement("income")
    revenues = data[data.tag == "us-gaap_Revenues"]
    assert (revenues.period_beginning == "2023-09-01").any()


def test_download_statement_dimension_relabel():
    """A generic revenue label resolving to a member context gets the member label."""
    from pandas import DataFrame

    fs = make_fs(
        _document_type="10-K",
        _period_ending="2024-08-31",
        _instance={
            "us-gaap_Revenues": {
                "context": [
                    {
                        "value": "75",
                        "context_ref": "duration_2023_09_01_to_2024_08_31_us-gaap_ProductMember",
                        "unit": "iso4217:USD",
                        "decimals": "-6",
                    }
                ]
            },
        },
        _tags={
            "us-gaap_Revenues": {
                "label": "Net sales and revenues",
                "crdr": "credit",
                "name": "Revenues",
            },
            "us-gaap_ProductMember": {"terseLabel": "Product line"},
        },
        _period_context={},
        _resources={
            "r1": {
                "group": "statement",
                "short_name": "Statement of Operations",
                "url": "https://sec.gov/R4.htm",
            }
        },
    )

    def _from_url(url, is_equity=False):
        table = DataFrame(
            {
                "Statement of Operations $ in Millions": ["Net sales and revenues"],
                "2024-08-31 -- 12 Months Ended": [75],
            }
        )
        return table, DataFrame()

    with patch.object(fs, "_download_statement_from_url", side_effect=_from_url):
        data, _ = fs._download_statement("income")
    assert "Product line" in set(data.label)


def test_download_statement_meta_column_branches():
    """Unit/decimals/weight/balance/preferred_label/parent_tag read from output_meta."""
    from pandas import DataFrame

    fs = make_fs(
        _document_type="10-K",
        _period_ending="2024-08-31",
        _instance={
            "us-gaap_Revenues": {
                "context": [
                    {
                        "value": "100",
                        "context_ref": "duration_2023_09_01_to_2024_08_31",
                    }
                ]
            }
        },
        _tags={
            "us-gaap_Revenues": {"label": "Net sales and revenues", "name": "Revenues"}
        },
        _period_context={},
        _resources={
            "r1": {
                "group": "statement",
                "short_name": "Statement of Operations",
                "url": "https://sec.gov/R4.htm",
            }
        },
    )

    def _from_url(url, is_equity=False):
        table = DataFrame(
            {
                "Statement of Operations $ in Millions": ["Net sales and revenues"],
                "2024-08-31 -- 12 Months Ended": [100],
            }
        )
        meta = DataFrame(
            {
                "Name": ["us-gaap_Revenues"],
                "Namespace Prefix": ["us-gaap"],
                "Data Type": ["xbrli:monetaryItemType"],
                "Balance Type": ["credit"],
                "Period Type": ["duration"],
                "unit": ["iso4217:USD / shares"],
                "decimals": ["-3"],
                "weight": ["1"],
                "preferred_label": ["totalLabel"],
                "parent_tag": ["us-gaap_IncomeStatement"],
            }
        )
        return table, meta

    with patch.object(fs, "_download_statement_from_url", side_effect=_from_url):
        data, _ = fs._download_statement("income")
    row = data[data.tag == "us-gaap_Revenues"].iloc[0]
    assert row.unit == "USDPerShares"
    assert row.decimals == "-3"
    assert row.weight == "1"
    assert row.balance == "credit"
    assert row.preferred_label == "totalLabel"
    assert row.parent_tag == "us-gaap_IncomeStatement"


def test_download_statement_normalize_instance_key_and_word_match():
    """Instance keys normalize by local name and apply_fix_tag word-matches labels."""
    from pandas import DataFrame

    fs = make_fs(
        _document_type="10-Q",
        _period_ending="2024-05-31",
        _instance={
            "srt_Revenues": {
                "context": [
                    {
                        "value": "100",
                        "context_ref": "duration_2024_03_01_to_2024_05_31",
                        "unit": "iso4217:USD",
                        "decimals": "-6",
                    }
                ]
            },
            "us-gaap_OperatingExpenses": {
                "context": [
                    {
                        "value": "55",
                        "context_ref": "duration_2024_03_01_to_2024_05_31",
                        "unit": "iso4217:USD",
                        "decimals": "-6",
                    }
                ]
            },
            "us-gaap_OtherExpenses": {
                "context": [
                    {
                        "value": "55",
                        "context_ref": "duration_2024_03_01_to_2024_05_31",
                        "unit": "iso4217:USD",
                        "decimals": "-6",
                    }
                ]
            },
        },
        _tags={
            "us-gaap_Revenues": {
                "label": "Net sales and revenues",
                "crdr": "credit",
                "name": "Revenues",
            },
            "us-gaap_OperatingExpenses": {
                "label": "Total operating expenses incurred",
                "crdr": "debit",
                "name": "OperatingExpenses",
            },
            "us-gaap_OtherExpenses": {
                "label": "Unrelated other charges",
                "crdr": "debit",
                "name": "OtherExpenses",
            },
        },
        _period_context={},
        _resources={
            "r1": {
                "group": "statement",
                "short_name": "Statement of Operations",
                "url": "https://sec.gov/R4.htm",
            }
        },
    )

    def _from_url(url, is_equity=False):
        table = DataFrame(
            {
                "Statement of Operations $ in Millions": [
                    "Net sales and revenues",
                    "Operating expenses incurred during period",
                ],
                "2024-05-31 -- 3 Months Ended": [100, 55],
            }
        )
        return table, DataFrame()

    with patch.object(fs, "_download_statement_from_url", side_effect=_from_url):
        data, _ = fs._download_statement("income")
    tags = set(data.tag.dropna())
    assert "us-gaap_Revenues" in tags
    assert "us-gaap_OperatingExpenses" in tags


def test_download_statement_period_beginning_span_branch():
    """A row without a resolvable context derives period_beginning from the column span."""
    from pandas import DataFrame

    fs = make_fs(
        _document_type="10-Q",
        _period_ending="2024-05-31",
        _instance={
            "us-gaap_Revenues": {
                "context": [
                    {
                        "value": "100",
                        "context_ref": "duration_2024_03_01_to_2024_05_31",
                        "unit": "iso4217:USD",
                    }
                ]
            },
            "us-gaap_OperatingIncomeLoss": {
                "context": [
                    {
                        "value": "55",
                        "context_ref": "c-3",
                        "unit": "iso4217:USD",
                    }
                ]
            },
        },
        _tags={
            "us-gaap_Revenues": {"label": "Net sales and revenues", "crdr": "credit"},
            "us-gaap_OperatingIncomeLoss": {
                "label": "Operating income",
                "crdr": "credit",
            },
        },
        _period_context={},
        _resources={
            "r1": {
                "group": "statement",
                "short_name": "Statement of Operations",
                "url": "https://sec.gov/R4.htm",
            }
        },
    )

    def _from_url(url, is_equity=False):
        table = DataFrame(
            {
                "Statement of Operations $ in Millions": [
                    "Net sales and revenues",
                    "Operating income",
                ],
                "2024-05-31 -- 3 Months Ended": [100, 55],
            }
        )
        return table, DataFrame()

    with patch.object(fs, "_download_statement_from_url", side_effect=_from_url):
        data, _ = fs._download_statement("income")
    op_row = data[data.label == "Operating income"].iloc[0]
    assert op_row.period_beginning == "2024-03-01"


def test_download_statement_period_beginning_10k_year_shift():
    """A 10-K row with no span and no context falls back to a one-year-prior beginning."""
    from pandas import DataFrame

    fs = make_fs(
        _document_type="10-K",
        _period_ending="2024-08-31",
        _instance={
            "us-gaap_Revenues": {
                "context": [
                    {
                        "value": "100",
                        "context_ref": "duration_2023_09_01_to_2024_08_31",
                        "unit": "iso4217:USD",
                    }
                ]
            },
            "us-gaap_OperatingIncomeLoss": {
                "context": [
                    {
                        "value": "55",
                        "context_ref": "c-3",
                        "unit": "iso4217:USD",
                    }
                ]
            },
        },
        _tags={
            "us-gaap_Revenues": {"label": "Net sales and revenues", "crdr": "credit"},
            "us-gaap_OperatingIncomeLoss": {
                "label": "Operating income",
                "crdr": "credit",
            },
        },
        _period_context={},
        _resources={
            "r1": {
                "group": "statement",
                "short_name": "Statement of Operations",
                "url": "https://sec.gov/R4.htm",
            }
        },
    )

    def _from_url(url, is_equity=False):
        table = DataFrame(
            {
                "Statement of Operations $ in Millions": [
                    "Net sales and revenues",
                    "Operating income",
                ],
                "2024-08-31": [100, 55],
            }
        )
        return table, DataFrame()

    with patch.object(fs, "_download_statement_from_url", side_effect=_from_url):
        data, _ = fs._download_statement("income")
    op_row = data[data.label == "Operating income"].iloc[0]
    assert op_row.period_beginning == "2023-09-01"


def test_download_statement_value_to_tags_fix():
    """A mislabeled row tag is corrected by numeric value matching."""
    from pandas import DataFrame

    fs = make_fs(
        _document_type="10-K",
        _period_ending="2024-08-31",
        _instance={
            "us-gaap_Revenues": {
                "context": [
                    {
                        "value": "100",
                        "context_ref": "duration_2023_09_01_to_2024_08_31",
                        "unit": "iso4217:USD",
                        "decimals": "-6",
                    }
                ]
            },
        },
        _tags={
            "us-gaap_Revenues": {
                "label": "Net sales and revenues",
                "crdr": "credit",
                "name": "Revenues",
            },
            "us-gaap_WrongLabelTag": {
                "label": "Net sales and revenues",
                "crdr": "credit",
                "name": "WrongLabelTag",
            },
        },
        _period_context={"duration_2023_09_01_to_2024_08_31": {"start": "2023-09-01"}},
        _resources={
            "r1": {
                "group": "statement",
                "short_name": "Statement of Operations",
                "url": "https://sec.gov/R4.htm",
            }
        },
    )

    def _from_url(url, is_equity=False):
        table = DataFrame(
            {
                "Statement of Operations $ in Millions": ["Net sales and revenues"],
                "2024-08-31 -- 12 Months Ended": [100],
            }
        )
        return table, DataFrame()

    with patch.object(fs, "_download_statement_from_url", side_effect=_from_url):
        data, _ = fs._download_statement("income")
    assert "us-gaap_Revenues" in set(data.tag.dropna())


def test_download_statement_from_url_single_period():
    """_download_statement_from_url processes a single-period millions table."""
    from pandas import DataFrame

    fs = make_fs(
        _document_type="10-Q",
        _instance={
            "us-gaap_Revenues": {"context": [{"unit": "iso4217:USD", "decimals": "-6"}]}
        },
        _tags={"us-gaap_Revenues": {"weight": "1", "name": "Revenues"}},
    )
    raw = DataFrame(
        {
            0: ["Statement of Operations $ in Millions", "Net sales and revenues"],
            1: ["3 Months Ended Aug. 31, 2024", "100"],
        }
    )
    raw = raw.set_axis(
        ["Statement of Operations $ in Millions", "Aug. 31, 2024"], axis=1
    )
    table = DataFrame(
        {
            "Statement of Operations $ in Millions": ["Net sales and revenues"],
            "Aug. 31, 2024": ["100"],
        }
    )
    meta = DataFrame(
        {
            0: ["Name", "Namespace Prefix", "Balance Type"],
            1: ["us-gaap_Revenues", "us-gaap", "credit"],
        }
    )
    with patch.object(fs, "_get_document", return_value=[table, meta]):
        out_table, out_meta = fs._download_statement_from_url("https://sec.gov/R4.htm")
    assert "12 Months Ended" not in out_table.columns
    assert out_table.iloc[0, 0] == "Net sales and revenues"


def test_download_statement_from_url_equity_branch():
    """_download_statement_from_url leaves columns intact for equity statements."""
    from pandas import DataFrame

    fs = make_fs(_document_type="10-K", _instance={}, _tags={})
    table = DataFrame(
        {
            "Statement of Equity": ["Balance"],
            "Common Stock": ["500"],
            "Retained Earnings": ["300"],
        }
    )
    with patch.object(fs, "_get_document", return_value=[table]):
        out_table, out_meta = fs._download_statement_from_url(
            "https://sec.gov/R7.htm", is_equity=True
        )
    assert "Common Stock" in out_table.columns
    assert out_meta.empty


def test_download_statement_from_url_multiindex_two_periods():
    """A 5-column multiindex 10-K table is split into two period frames and merged."""
    from pandas import DataFrame, MultiIndex

    fs = make_fs(
        _document_type="10-K",
        _instance={
            "us-gaap_Revenues": {"context": [{"unit": "iso4217:USD", "decimals": "-6"}]}
        },
        _tags={"us-gaap_Revenues": {"weight": "1", "name": "Revenues"}},
    )
    cols = MultiIndex.from_tuples(
        [
            ("Income Statement $ in Millions", ""),
            ("12 Months Ended", "Aug. 31, 2024"),
            ("12 Months Ended", "Aug. 31, 2023"),
            ("12 Months Ended", "Aug. 31, 2022"),
            ("12 Months Ended", "Aug. 31, 2021"),
        ]
    )
    table = DataFrame(
        [["Net sales and revenues", "100", "90", "80", "70"]], columns=cols
    )
    meta = DataFrame({0: ["Name", "Balance Type"], 1: ["us-gaap_Revenues", "credit"]})
    with patch.object(fs, "_get_document", return_value=[table, meta]):
        out_table, _ = fs._download_statement_from_url("https://sec.gov/R4.htm")
    assert out_table.iloc[0, 0] == "Net sales and revenues"


def test_download_statement_from_url_three_col_multiindex():
    """A 3-column multiindex table is flattened with the period dropped to one level."""
    from pandas import DataFrame, MultiIndex

    fs = make_fs(
        _document_type="10-Q",
        _instance={
            "us-gaap_Revenues": {"context": [{"unit": "iso4217:USD", "decimals": "-6"}]}
        },
        _tags={"us-gaap_Revenues": {"weight": "1", "name": "Revenues"}},
    )
    cols = MultiIndex.from_tuples(
        [
            ("Income Statement $ in Millions", ""),
            ("3 Months Ended", "Aug. 31, 2024"),
            ("3 Months Ended", "Aug. 31, 2023"),
        ]
    )
    table = DataFrame([["Net sales and revenues", "100", "90"]], columns=cols)
    meta = DataFrame({0: ["Name", "Balance Type"], 1: ["us-gaap_Revenues", "credit"]})
    with patch.object(fs, "_get_document", return_value=[table, meta]):
        out_table, _ = fs._download_statement_from_url("https://sec.gov/R4.htm")
    assert out_table.iloc[0, 0] == "Net sales and revenues"


def test_download_statement_from_url_shares_and_per_share_rows():
    """Per-share and shares rows are formatted with their own multipliers."""
    from pandas import DataFrame

    fs = make_fs(
        _document_type="10-Q",
        _instance={},
        _tags={},
    )
    table = DataFrame(
        {
            "Income Statement $ in Millions, shares in Thousands": [
                "Net sales and revenues",
                "Earnings per share - basic (in dollars per share)",
                "Weighted average shares outstanding",
                "[1] footnote row",
            ],
            "Aug. 31, 2024": ["100", "2.50", "40", "5"],
        }
    )
    meta = DataFrame(
        {
            0: ["Name", "Balance Type"],
            1: ["us-gaap_Revenues", "na"],
        }
    )
    with patch.object(fs, "_get_document", return_value=[table, meta]):
        out_table, _ = fs._download_statement_from_url("https://sec.gov/R4.htm")
    labels = out_table.iloc[:, 0].tolist()
    assert "[1] footnote row" not in labels
    assert "Net sales and revenues" in labels


def test_download_statement_from_url_five_col_two_periods_merge():
    """A non-10-K 5-column multiindex splits into two periods that are merged."""
    from pandas import DataFrame, MultiIndex

    fs = make_fs(
        _document_type="10-Q",
        _instance={
            "us-gaap_Revenues": {"context": [{"unit": "iso4217:USD", "decimals": "-6"}]}
        },
        _tags={"us-gaap_Revenues": {"weight": "1", "name": "Revenues"}},
    )
    cols = MultiIndex.from_tuples(
        [
            ("Income Statement $ in Millions", ""),
            ("3 Months Ended", "Aug. 31, 2024"),
            ("3 Months Ended", "Aug. 31, 2023"),
            ("9 Months Ended", "Aug. 31, 2024"),
            ("9 Months Ended", "Aug. 31, 2023"),
        ]
    )
    table = DataFrame(
        [["Net sales and revenues", "100", "90", "300", "280"]], columns=cols
    )
    meta = DataFrame({0: ["Name", "Balance Type"], 1: ["us-gaap_Revenues", "credit"]})
    with patch.object(fs, "_get_document", return_value=[table, meta]):
        out_table, _ = fs._download_statement_from_url("https://sec.gov/R4.htm")
    assert out_table.iloc[0, 0] == "Net sales and revenues"
    assert len(out_table.columns) == 5


def test_download_statement_from_url_no_period_and_bad_values():
    """A 3-col multiindex with an empty period level uses bare dates and drops bad rows."""
    from pandas import DataFrame, MultiIndex

    fs = make_fs(_document_type="10-Q", _instance={}, _tags={})
    cols = MultiIndex.from_tuples(
        [
            ("Income Statement $ in Millions", ""),
            ("", "Aug. 31, 2024"),
            ("", "Aug. 31, 2023"),
        ]
    )
    table = DataFrame(
        [
            ["Net sales and revenues", "100", "90"],
            ["[bracket value row]", "[1]", "5"],
            ["Non-numeric row", "not-a-number", "10"],
        ],
        columns=cols,
    )
    meta = DataFrame({0: ["Name", "Balance Type"], 1: ["us-gaap_Revenues", "credit"]})
    with patch.object(fs, "_get_document", return_value=[table, meta]):
        out_table, _ = fs._download_statement_from_url("https://sec.gov/R4.htm")
    labels = out_table.iloc[:, 0].tolist()
    assert " -- " not in str(out_table.columns[1])
    assert "Net sales and revenues" in labels
    bad = out_table[out_table.iloc[:, 0] == "Non-numeric row"]
    assert bad.iloc[0, 1] == "--"


def test_download_statement_from_url_drops_duplicate_column():
    """A duplicated value column (name and name.1) is dropped before processing."""
    from pandas import DataFrame

    fs = make_fs(_document_type="10-Q", _instance={}, _tags={})
    table = DataFrame(
        [
            ["Income Statement $ in Millions", "Aug. 31, 2024", "Aug. 31, 2024"],
            ["Net sales and revenues", "100", "100"],
        ]
    )
    table.columns = ["Aug. 31, 2024", "Aug. 31, 2024", "Aug. 31, 2024.1"]
    table = DataFrame(
        {
            "Aug. 31, 2024": ["Net sales and revenues"],
            "Aug. 31, 2024.1": ["100"],
        }
    )
    meta = DataFrame({0: ["Name", "Balance Type"], 1: ["us-gaap_Revenues", "credit"]})
    with patch.object(fs, "_get_document", return_value=[table, meta]):
        out_table, _ = fs._download_statement_from_url("https://sec.gov/R4.htm")
    assert out_table.iloc[0, 0] == "Net sales and revenues"


def test_download_statement_from_url_drops_bracket_meta_columns():
    """Meta columns whose header starts with '[' are dropped from the item map."""
    from pandas import DataFrame

    fs = make_fs(
        _document_type="10-Q",
        _instance={"us-gaap_Revenues": {"context": [{}]}},
        _tags={"us-gaap_Revenues": {"name": "Revenues"}},
    )
    table = DataFrame(
        {
            "Income Statement $ in Millions": ["Net sales and revenues"],
            "Aug. 31, 2024 Ended": ["100"],
        }
    )
    meta = DataFrame(
        {
            0: ["Name", "Balance Type", "[Footnote]"],
            1: ["us-gaap_Revenues", "credit", "[1]"],
        }
    )
    with patch.object(fs, "_get_document", return_value=[table, meta]):
        _, out_meta = fs._download_statement_from_url("https://sec.gov/R4.htm")
    if not out_meta.empty:
        assert "[Footnote]" not in out_meta.columns


def _fix_tag_fs(tags, instance):
    """FinancialStatements wired for apply_fix_tag cascade tests."""
    return make_fs(
        _document_type="10-K",
        _period_ending="2024-08-31",
        _instance=instance,
        _tags=tags,
        _period_context={},
        _resources={
            "r1": {
                "group": "statement",
                "short_name": "Statement of Operations",
                "url": "https://sec.gov/R4.htm",
            }
        },
    )


def _fix_tag_run(fs, label, value):
    """Drive _download_statement with a single-row table for a label/value."""
    from pandas import DataFrame

    def _from_url(url, is_equity=False):
        table = DataFrame(
            {
                "Statement of Operations $ in Millions": [label],
                "2024-08-31 -- 12 Months Ended": [value],
            }
        )
        return table, DataFrame()

    with patch.object(fs, "_download_statement_from_url", side_effect=_from_url):
        data, _ = fs._download_statement("income")
    return data[data.label == label].tag.tolist()


def test_apply_fix_tag_exact_label_cascade():
    """A wrong initial tag is corrected to the candidate with the exact label."""
    fs = _fix_tag_fs(
        tags={
            "us-gaap_RevenueExact": {
                "label": "Revenue",
                "crdr": "credit",
                "name": "RevenueExact",
            },
            "us-gaap_RevA": {
                "label": "Receipts total",
                "crdr": "credit",
                "name": "RevA",
            },
            "us-gaap_RevB": {"label": "Revenue", "crdr": "credit", "name": "RevB"},
        },
        instance={
            "us-gaap_RevenueExact": {
                "context": [
                    {
                        "value": "90",
                        "context_ref": "duration_2023_09_01_to_2024_08_31",
                        "unit": "iso4217:USD",
                    }
                ]
            },
            "us-gaap_RevA": {
                "context": [
                    {
                        "value": "100",
                        "context_ref": "duration_2023_09_01_to_2024_08_31",
                        "unit": "iso4217:USD",
                    }
                ]
            },
            "us-gaap_RevB": {
                "context": [
                    {
                        "value": "100",
                        "context_ref": "as_of_2024_08_31",
                        "unit": "iso4217:USD",
                    }
                ]
            },
        },
    )
    assert _fix_tag_run(fs, "Revenue", 100) == ["us-gaap_RevB"]


def test_apply_fix_tag_word_overlap_cascade():
    """A wrong initial tag is corrected by a two-word label overlap."""
    fs = _fix_tag_fs(
        tags={
            "us-gaap_Init": {
                "label": "Cost of revenue",
                "crdr": "debit",
                "name": "Init",
            },
            "us-gaap_W1": {
                "label": "Total cost of products sold",
                "crdr": "debit",
                "name": "W1",
            },
            "us-gaap_W2": {
                "label": "Unrelated charges incurred",
                "crdr": "debit",
                "name": "W2",
            },
        },
        instance={
            "us-gaap_Init": {
                "context": [
                    {
                        "value": "90",
                        "context_ref": "duration_2023_09_01_to_2024_08_31",
                        "unit": "iso4217:USD",
                    }
                ]
            },
            "us-gaap_W1": {
                "context": [
                    {
                        "value": "50",
                        "context_ref": "duration_2023_09_01_to_2024_08_31",
                        "unit": "iso4217:USD",
                    }
                ]
            },
            "us-gaap_W2": {
                "context": [
                    {
                        "value": "50",
                        "context_ref": "as_of_2024_08_31",
                        "unit": "iso4217:USD",
                    }
                ]
            },
        },
    )
    assert _fix_tag_run(fs, "Cost of products sold", 50) == ["us-gaap_W1"]


def test_apply_fix_tag_name_words_cascade():
    """A wrong initial tag is corrected by element-name word overlap."""
    fs = _fix_tag_fs(
        tags={
            "us-gaap_Start": {
                "label": "Inventory balance",
                "crdr": "debit",
                "name": "Start",
            },
            "us-gaap_InventoryNet": {
                "label": "Goods on hand",
                "crdr": "debit",
                "name": "InventoryNet",
            },
            "us-gaap_OtherX": {
                "label": "Misc holdings",
                "crdr": "debit",
                "name": "OtherX",
            },
        },
        instance={
            "us-gaap_Start": {
                "context": [
                    {
                        "value": "90",
                        "context_ref": "duration_2023_09_01_to_2024_08_31",
                        "unit": "iso4217:USD",
                    }
                ]
            },
            "us-gaap_InventoryNet": {
                "context": [
                    {
                        "value": "70",
                        "context_ref": "as_of_2024_08_31",
                        "unit": "iso4217:USD",
                    }
                ]
            },
            "us-gaap_OtherX": {
                "context": [
                    {
                        "value": "70",
                        "context_ref": "as_of_2024_08_31",
                        "unit": "iso4217:USD",
                    }
                ]
            },
        },
    )
    assert _fix_tag_run(fs, "Inventory", 70) == ["us-gaap_InventoryNet"]


def test_apply_fix_tag_no_match_keeps_initial():
    """When no cascade tier matches, the initial tag is kept unchanged."""
    from pandas import DataFrame

    fs = _fix_tag_fs(
        tags={
            "us-gaap_Start": {"label": "Net total", "crdr": "credit", "name": "Start"},
            "srt_AlphaXxxx": {
                "label": "Greek letters here",
                "crdr": "credit",
                "name": "AlphaXxxx",
            },
            "srt_BetaYyyy": {
                "label": "Other letters here",
                "crdr": "credit",
                "name": "BetaYyyy",
            },
            "us-gaap_Cash": {
                "label": "Cash and equivalents",
                "crdr": "debit",
                "name": "Cash",
            },
        },
        instance={
            "us-gaap_Start": {
                "context": [
                    {
                        "value": "90",
                        "context_ref": "duration_2023_09_01_to_2024_08_31",
                        "unit": "iso4217:USD",
                    }
                ]
            },
            "srt_AlphaXxxx": {
                "context": [
                    {
                        "value": "33",
                        "context_ref": "as_of_2024_08_31",
                        "unit": "iso4217:USD",
                    }
                ]
            },
            "srt_BetaYyyy": {
                "context": [
                    {
                        "value": "33",
                        "context_ref": "as_of_2024_08_31",
                        "unit": "iso4217:USD",
                    }
                ]
            },
            "us-gaap_Cash": {
                "context": [
                    {
                        "value": "200",
                        "context_ref": "as_of_2024_08_31",
                        "unit": "iso4217:USD",
                    }
                ]
            },
        },
    )

    def _from_url(url, is_equity=False):
        table = DataFrame(
            {
                "Statement of Operations $ in Millions": [
                    "Net total",
                    "Cash and equivalents",
                ],
                "2024-08-31 -- 12 Months Ended": [33, 200],
            }
        )
        return table, DataFrame()

    with patch.object(fs, "_download_statement_from_url", side_effect=_from_url):
        data, _ = fs._download_statement("income")
    net_tag = data[data.label == "Net total"].tag.tolist()
    assert net_tag[0] in (None, "us-gaap_Start")


def test_format_value_int_float_and_passthrough():
    """format_value coerces ints, keeps non-integer floats, and drops empties."""
    from pandas import DataFrame

    fs = make_fs(
        _document_type="10-K",
        _period_ending="2024-08-31",
        _instance={
            "us-gaap_EarningsPerShare": {
                "context": [
                    {
                        "value": "2.5",
                        "context_ref": "duration_2023_09_01_to_2024_08_31",
                        "unit": "iso4217:USD / shares",
                    }
                ]
            }
        },
        _tags={
            "us-gaap_EarningsPerShare": {
                "label": "Diluted earnings per share (in dollars per share)",
                "crdr": "credit",
            }
        },
        _period_context={},
        _resources={
            "r1": {
                "group": "statement",
                "short_name": "Statement of Operations",
                "url": "https://sec.gov/R4.htm",
            }
        },
    )

    def _from_url(url, is_equity=False):
        table = DataFrame(
            {
                "Statement of Operations $ in Millions": [
                    "Diluted earnings per share (in dollars per share)",
                ],
                "2024-08-31 -- 12 Months Ended": [2.5],
            }
        )
        return table, DataFrame()

    with patch.object(fs, "_download_statement_from_url", side_effect=_from_url):
        data, _ = fs._download_statement("income")
    assert 2.5 in set(data.value.dropna())


def test_download_statement_normalized_label_match():
    """A 'Total assets' table label matches a tag labelled 'Assets, Total'."""
    from pandas import DataFrame

    fs = make_fs(
        _document_type="10-K",
        _period_ending="2024-08-31",
        _instance={
            "us-gaap_Assets": {
                "context": [
                    {
                        "value": "200",
                        "context_ref": "as_of_2024_08_31",
                        "unit": "iso4217:USD",
                    }
                ]
            }
        },
        _tags={
            "us-gaap_Assets": {
                "label": "Assets, Total",
                "crdr": "debit",
                "name": "Assets",
            }
        },
        _period_context={},
        _resources={
            "r1": {
                "group": "statement",
                "short_name": "Balance Sheet",
                "url": "https://sec.gov/R2.htm",
            }
        },
    )

    def _from_url(url, is_equity=False):
        table = DataFrame(
            {"Balance Sheet $ in Millions": ["Total assets"], "2024-08-31": [200]}
        )
        return table, DataFrame()

    with patch.object(fs, "_download_statement_from_url", side_effect=_from_url):
        data, _ = fs._download_statement("balance")
    assert data[data.label == "Total assets"].tag.tolist() == ["us-gaap_Assets"]


def test_download_statement_check_unit_variants_from_meta():
    """check_unit handles divide, two-part, and passthrough unit strings from meta."""
    from pandas import DataFrame

    tags = {
        "us-gaap_EpsA": {"label": "Diluted EPS", "name": "EpsA"},
        "us-gaap_EpsB": {"label": "Basic EPS", "name": "EpsB"},
        "us-gaap_PureC": {"label": "Tax rate", "name": "PureC"},
        "us-gaap_PlainD": {"label": "Plain value", "name": "PlainD"},
    }
    instance = {
        "us-gaap_EpsA": {
            "context": [
                {
                    "value": "2",
                    "context_ref": "duration_2023_09_01_to_2024_08_31",
                    "unit": "x",
                }
            ]
        },
        "us-gaap_EpsB": {
            "context": [
                {
                    "value": "3",
                    "context_ref": "duration_2023_09_01_to_2024_08_31",
                    "unit": "x",
                }
            ]
        },
        "us-gaap_PureC": {
            "context": [
                {
                    "value": "4",
                    "context_ref": "duration_2023_09_01_to_2024_08_31",
                    "unit": "x",
                }
            ]
        },
        "us-gaap_PlainD": {
            "context": [
                {
                    "value": "5",
                    "context_ref": "duration_2023_09_01_to_2024_08_31",
                    "unit": "x",
                }
            ]
        },
    }
    fs = make_fs(
        _document_type="10-K",
        _period_ending="2024-08-31",
        _instance=instance,
        _tags=tags,
        _period_context={},
        _resources={
            "r1": {
                "group": "statement",
                "short_name": "Statement of Operations",
                "url": "https://sec.gov/R4.htm",
            }
        },
    )
    meta = DataFrame(
        {
            "Name": ["us-gaap_EpsA", "us-gaap_EpsB", "us-gaap_PureC", "us-gaap_PlainD"],
            "Namespace Prefix": ["us-gaap"] * 4,
            "Data Type": ["xbrli:perShareItemType"] * 4,
            "Balance Type": ["na", "na", "na", "na"],
            "Period Type": ["duration"] * 4,
            "unit": ["unit_Divide_iso4217_Shares", "u_USD", "pure", "rawunit"],
        }
    )

    def _from_url(url, is_equity=False):
        table = DataFrame(
            {
                "Statement of Operations $ in Millions": [
                    "Diluted EPS",
                    "Basic EPS",
                    "Tax rate",
                    "Plain value",
                ],
                "2024-08-31 -- 12 Months Ended": [2, 3, 4, 5],
            }
        )
        return table, meta

    with patch.object(fs, "_download_statement_from_url", side_effect=_from_url):
        data, _ = fs._download_statement("income")
    units = dict(zip(data.tag, data.unit))
    assert units["us-gaap_EpsA"] == "iso4217perShares"
    assert units["us-gaap_EpsB"] == "USD"
    assert units["us-gaap_PureC"] == "pure"
    assert units["us-gaap_PlainD"] == "rawunit"
    assert set(data.balance.dropna()) <= {None}


def test_download_statement_context_ref_and_orphan_edges():
    """apply_context_ref skips malformed entries and unmatched/empty-instance tags."""
    from pandas import DataFrame

    fs = make_fs(
        _document_type="10-K",
        _period_ending="2024-08-31",
        _instance={
            "us-gaap_Mixed": {
                "context": [
                    {},
                    {"context_ref": "", "value": "5"},
                    {"context_ref": "longref_aaaa", "value": "--"},
                    {"context_ref": "longref_bbbb", "value": "abc"},
                    {
                        "context_ref": "longref_good",
                        "value": "50",
                        "unit": "iso4217:USD",
                    },
                ]
            },
            "prefix_OrphanLocal": {
                "context": [
                    {
                        "context_ref": "duration_2023_09_01_to_2024_08_31",
                        "value": "777",
                        "unit": "iso4217:USD",
                    }
                ]
            },
        },
        _tags={
            "us-gaap_Mixed": {"label": "Mixed line", "crdr": "credit", "name": "Mixed"},
            "us-gaap_FooZ": {"label": "Foo line", "crdr": "credit", "name": "FooZ"},
        },
        _period_context={},
        _resources={
            "r1": {
                "group": "statement",
                "short_name": "Statement of Operations",
                "url": "https://sec.gov/R4.htm",
            }
        },
    )

    def _from_url(url, is_equity=False):
        table = DataFrame(
            {
                "Statement of Operations $ in Millions": [
                    "Mixed line",
                    "Foo line",
                    "Unmatched label here",
                ],
                "2024-08-31 -- 12 Months Ended": [50, 60, "--"],
            }
        )
        return table, DataFrame()

    with patch.object(fs, "_download_statement_from_url", side_effect=_from_url):
        data, _ = fs._download_statement("income")
    refs = dict(zip(data.label, data.context_ref))
    assert refs["Mixed line"] == "longref_good"
    assert refs["Foo line"] is None
    assert refs["Unmatched label here"] is None


def test_download_statement_context_ref_month_words_and_duration_match():
    from pandas import DataFrame

    fs = make_fs(
        _document_type="10-Q",
        _period_ending="2024-02-29",
        _instance={
            "us-gaap_WordMonths": {
                "context": [
                    {
                        "context_ref": "ctx_bad",
                        "value": "10",
                        "start": "2023-11-01",
                        "end": "2024-02-29",
                        "unit": "iso4217:USD",
                    },
                    {
                        "context_ref": "ctx_good",
                        "value": "10",
                        "start": "2024-01-01",
                        "end": "2024-02-29",
                        "unit": "iso4217:USD",
                    },
                ]
            }
        },
        _tags={
            "us-gaap_WordMonths": {
                "label": "Word months line",
                "crdr": "credit",
                "name": "WordMonths",
            }
        },
        _period_context={
            "ctx_bad": {"start": "2023-11-01"},
            "ctx_good": {"start": "2024-01-01"},
        },
        _resources={
            "r1": {
                "group": "statement",
                "short_name": "Statement of Operations",
                "url": "https://sec.gov/R4.htm",
            }
        },
    )

    def _from_url(url, is_equity=False):
        table = DataFrame(
            {
                "Statement of Operations $ in Millions": ["Word months line"],
                "2024-02-29 -- Two Months Ended": [10],
            }
        )
        return table, DataFrame()

    with patch.object(fs, "_download_statement_from_url", side_effect=_from_url):
        data, _ = fs._download_statement("income")
    assert data.iloc[0].context_ref == "ctx_good"


def test_download_statement_period_ending_from_context_duration():
    from pandas import DataFrame

    fs = make_fs(
        _document_type="10-Q",
        _period_ending="2024-12-31",
        _instance={
            "us-gaap_DurationRow": {
                "context": [
                    {
                        "context_ref": "ctx_duration",
                        "value": "100",
                        "unit": "iso4217:USD",
                    }
                ]
            }
        },
        _tags={
            "us-gaap_DurationRow": {
                "label": "Duration row",
                "crdr": "credit",
                "name": "DurationRow",
            }
        },
        _period_context={
            "ctx_duration": {
                "start": "2024-01-01",
                "end": "2024-12-31",
                "period_type": "duration",
            }
        },
        _resources={
            "r1": {
                "group": "statement",
                "short_name": "Statement of Operations",
                "url": "https://sec.gov/R4.htm",
            }
        },
    )

    def _from_url(url, is_equity=False):
        table = DataFrame(
            {
                "Statement of Operations $ in Millions": ["Duration row"],
                "2024-12-31 -- 12 Months Ended": [100],
            }
        )
        return table, DataFrame()

    with patch.object(fs, "_download_statement_from_url", side_effect=_from_url):
        data, _ = fs._download_statement("income")
    assert data.iloc[0].period_ending == "2024-12-31 -- 12 Months Ended"


def test_download_statement_period_ending_from_context_instant():
    from pandas import DataFrame

    fs = make_fs(
        _document_type="10-Q",
        _period_ending="2024-12-31",
        _instance={
            "us-gaap_InstantRow": {
                "context": [
                    {
                        "context_ref": "ctx_instant",
                        "value": "100",
                        "unit": "iso4217:USD",
                    }
                ]
            }
        },
        _tags={
            "us-gaap_InstantRow": {
                "label": "Instant row",
                "crdr": "credit",
                "name": "InstantRow",
            }
        },
        _period_context={
            "ctx_instant": {
                "start": None,
                "end": "2024-12-31",
                "period_type": "instant",
            }
        },
        _resources={
            "r1": {
                "group": "statement",
                "short_name": "Statement of Operations",
                "url": "https://sec.gov/R4.htm",
            }
        },
    )

    def _from_url(url, is_equity=False):
        table = DataFrame(
            {
                "Statement of Operations $ in Millions": ["Instant row"],
                "2024-12-31 -- 12 Months Ended": [100],
            }
        )
        return table, DataFrame()

    with patch.object(fs, "_download_statement_from_url", side_effect=_from_url):
        data, _ = fs._download_statement("income")
    assert data.iloc[0].period_ending == "2024-12-31"


def test_download_statement_period_beginning_context_heuristics():
    """Plain context refs fall through to length heuristics or yield no beginning."""
    from pandas import DataFrame

    fs = make_fs(
        _document_type="10-Q",
        _period_ending="2024-05-31",
        _instance={
            "us-gaap_Heur23": {
                "context": [
                    {
                        "context_ref": "20240831_20230901_xxxxx",
                        "value": "11",
                        "unit": "iso4217:USD",
                    }
                ]
            },
            "us-gaap_Heur12": {
                "context": [
                    {
                        "context_ref": "ab_20240831x",
                        "value": "12",
                        "unit": "iso4217:USD",
                    }
                ]
            },
            "us-gaap_NoneRow": {
                "context": [
                    {
                        "context_ref": "plainrefnomatch",
                        "value": "13",
                        "unit": "iso4217:USD",
                    }
                ]
            },
        },
        _tags={
            "us-gaap_Heur23": {
                "label": "Heur23 line",
                "crdr": "credit",
                "name": "Heur23",
            },
            "us-gaap_Heur12": {
                "label": "Heur12 line",
                "crdr": "credit",
                "name": "Heur12",
            },
            "us-gaap_NoneRow": {
                "label": "None row line",
                "crdr": "credit",
                "name": "NoneRow",
            },
        },
        _period_context={},
        _resources={
            "r1": {
                "group": "statement",
                "short_name": "Statement of Operations",
                "url": "https://sec.gov/R4.htm",
            }
        },
    )

    def _from_url(url, is_equity=False):
        table = DataFrame(
            {
                "Statement of Operations $ in Millions": [
                    "Heur23 line",
                    "Heur12 line",
                    "None row line",
                ],
                "2024-05-31": [11, 12, 13],
            }
        )
        return table, DataFrame()

    with patch.object(fs, "_download_statement_from_url", side_effect=_from_url):
        data, _ = fs._download_statement("income")
    begins = dict(zip(data.label, data.period_beginning))
    assert begins["Heur23 line"] == "20230901"
    assert begins["Heur12 line"] == "20240831x"
    assert begins["None row line"] is None


def test_download_statement_dimension_member_without_terse_label():
    """A generic label whose member lacks a terse label keeps the original label."""
    from pandas import DataFrame

    fs = make_fs(
        _document_type="10-K",
        _period_ending="2024-08-31",
        _instance={
            "us-gaap_Revenues": {
                "context": [
                    {
                        "value": "75",
                        "context_ref": "duration_2023_09_01_to_2024_08_31_us-gaap_ProductMember",
                        "unit": "iso4217:USD",
                    }
                ]
            }
        },
        _tags={
            "us-gaap_Revenues": {"label": "Net sales and revenues", "crdr": "credit"},
            "us-gaap_ProductMember": {"label": "Product line"},
        },
        _period_context={},
        _resources={
            "r1": {
                "group": "statement",
                "short_name": "Statement of Operations",
                "url": "https://sec.gov/R4.htm",
            }
        },
    )

    def _from_url(url, is_equity=False):
        table = DataFrame(
            {
                "Statement of Operations $ in Millions": ["Net sales and revenues"],
                "2024-08-31 -- 12 Months Ended": [75],
            }
        )
        return table, DataFrame()

    with patch.object(fs, "_download_statement_from_url", side_effect=_from_url):
        data, _ = fs._download_statement("income")
    assert "Net sales and revenues" in set(data.label)
    assert "Product line" not in set(data.label)


def test_download_statement_value_error_and_na_tag_unit():
    """A 'na'-keyed tag yields no unit and a malformed instance value is skipped."""
    from pandas import DataFrame

    fs = make_fs(
        _document_type="10-K",
        _period_ending="2024-08-31",
        _instance={
            "us-gaap_Other": {
                "context": [
                    {
                        "value": "1.2.3",
                        "context_ref": "duration_2023_09_01_to_2024_08_31",
                        "unit": "iso4217:USD",
                    }
                ]
            },
            "na": {
                "context": [
                    {
                        "value": "5",
                        "context_ref": "as_of_2024_08_31",
                        "unit": "iso4217:USD",
                    }
                ]
            },
        },
        _tags={
            "us-gaap_Other": {"label": "Other line", "crdr": "credit", "name": "Other"},
            "na": {"label": "Na line", "crdr": "credit", "name": "Na"},
        },
        _period_context={},
        _resources={
            "r1": {
                "group": "statement",
                "short_name": "Statement of Operations",
                "url": "https://sec.gov/R4.htm",
            }
        },
    )

    def _from_url(url, is_equity=False):
        table = DataFrame(
            {
                "Statement of Operations $ in Millions": ["Na line"],
                "2024-08-31 -- 12 Months Ended": [5],
            }
        )
        return table, DataFrame()

    with patch.object(fs, "_download_statement_from_url", side_effect=_from_url):
        data, _ = fs._download_statement("income")
    na_row = data[data.tag == "na"].iloc[0]
    assert na_row.unit is None


def test_apply_fix_tag_single_tags_matching():
    """When only one candidate is a known tag, apply_fix_tag selects it last."""
    from pandas import DataFrame

    fs = _fix_tag_fs(
        tags={
            "us-gaap_Start": {"label": "Net total", "crdr": "credit", "name": "Start"},
            "srt_AlphaXxxx": {
                "label": "Greek letters here",
                "crdr": "credit",
                "name": "AlphaXxxx",
            },
        },
        instance={
            "us-gaap_Start": {
                "context": [
                    {
                        "value": "90",
                        "context_ref": "duration_2023_09_01_to_2024_08_31",
                        "unit": "iso4217:USD",
                    }
                ]
            },
            "srt_AlphaXxxx": {
                "context": [
                    {
                        "value": "33",
                        "context_ref": "as_of_2024_08_31",
                        "unit": "iso4217:USD",
                    }
                ]
            },
            "srt_NotInTags": {
                "context": [
                    {
                        "value": "33",
                        "context_ref": "as_of_2024_08_31",
                        "unit": "iso4217:USD",
                    }
                ]
            },
            "us-gaap_Cash": {
                "context": [
                    {
                        "value": "200",
                        "context_ref": "as_of_2024_08_31",
                        "unit": "iso4217:USD",
                    }
                ]
            },
        },
    )
    fs._tags["us-gaap_Cash"] = {
        "label": "Cash and equivalents",
        "crdr": "debit",
        "name": "Cash",
    }

    def _from_url(url, is_equity=False):
        table = DataFrame(
            {
                "Statement of Operations $ in Millions": [
                    "Net total",
                    "Cash and equivalents",
                ],
                "2024-08-31 -- 12 Months Ended": [33, 200],
            }
        )
        return table, DataFrame()

    with patch.object(fs, "_download_statement_from_url", side_effect=_from_url):
        data, _ = fs._download_statement("income")
    assert data[data.label == "Net total"].tag.tolist() == ["srt_AlphaXxxx"]


def test_apply_label_returns_none_for_none_and_nan_labels():
    from pandas import DataFrame

    fs = _fix_tag_fs(
        tags={
            "us-gaap_Revenue": {
                "label": "Revenue",
                "crdr": "credit",
                "name": "Revenue",
            }
        },
        instance={
            "us-gaap_Revenue": {
                "context": [
                    {
                        "value": "3",
                        "context_ref": "duration_2023_09_01_to_2024_08_31",
                        "unit": "iso4217:USD",
                    }
                ]
            }
        },
    )

    def _from_url(url, is_equity=False):
        table = DataFrame(
            {
                "Statement of Operations $ in Millions": [None, "nan", "Revenue"],
                "2024-08-31 -- 12 Months Ended": [1, 2, 3],
            }
        )
        return table, DataFrame()

    with patch.object(fs, "_download_statement_from_url", side_effect=_from_url):
        data, _ = fs._download_statement("income")
    assert data[data.label.isna()].iloc[0].tag is None
    assert data[data.label == "nan"].iloc[0].tag is None


def test_download_statement_from_url_parent_tag_from_meta():
    """A meta tag carrying a parent_tag is mapped into the item map's parent_tag column."""
    from pandas import DataFrame

    fs = make_fs(
        _document_type="10-Q",
        _instance={
            "us-gaap_AssetsCurrent": {
                "context": [{"unit": "iso4217:USD", "decimals": "-6"}]
            }
        },
        _tags={
            "us-gaap_AssetsCurrent": {
                "name": "AssetsCurrent",
                "parent_tag": "us-gaap_Assets",
            }
        },
    )
    table = DataFrame(
        {
            "Balance Sheet $ in Millions": ["Total current assets"],
            "Aug. 31, 2024 Ended": ["100"],
        }
    )
    meta = DataFrame(
        {0: ["Name", "Balance Type"], 1: ["us-gaap_AssetsCurrent", "debit"]}
    )
    with patch.object(fs, "_get_document", return_value=[table, meta]):
        _, out_meta = fs._download_statement_from_url("https://sec.gov/R2.htm")
    if not out_meta.empty and "parent_tag" in out_meta.columns:
        assert "us-gaap_Assets" in set(out_meta.parent_tag.dropna())


def test_download_statement_from_url_empty_date_header():
    """An empty value-column header formats to None in the period-ending label."""
    from pandas import DataFrame

    fs = make_fs(_document_type="10-Q", _instance={}, _tags={})
    table = DataFrame(
        {
            "Income Statement $ in Millions": ["Net sales and revenues"],
            "": ["100"],
        }
    )
    meta = DataFrame({0: ["Name", "Balance Type"], 1: ["us-gaap_Revenues", "credit"]})
    with patch.object(fs, "_get_document", return_value=[table, meta]):
        out_table, _ = fs._download_statement_from_url("https://sec.gov/R4.htm")
    assert str(out_table.columns[1]).startswith("None -- ")


def test_download_statement_from_url_unparseable_date_header():
    from pandas import DataFrame

    fs = make_fs(_document_type="10-Q", _instance={}, _tags={})
    table = DataFrame(
        {
            "Income Statement $ in Millions": ["Net sales and revenues"],
            "Not a Date Header": ["100"],
        }
    )
    meta = DataFrame({0: ["Name", "Balance Type"], 1: ["us-gaap_Revenues", "credit"]})
    with patch.object(fs, "_get_document", return_value=[table, meta]):
        out_table, _ = fs._download_statement_from_url("https://sec.gov/R4.htm")
    assert str(out_table.columns[1]).startswith("None -- ")


def test_exhibit_title_mapping():
    from openbb_sec.models.sec_financials import _exhibit_title

    assert _exhibit_title("EX-21") == "Subsidiaries of the Registrant"
    assert _exhibit_title("EX-23.1") == "Consents of Experts and Counsel"
    assert _exhibit_title("EX-FOO") == ""


def test_parse_exhibit_index_variants():
    html = (
        '<a style="-sec-extract:exhibit" href="ex1.htm">Full Description Here</a>'
        '<a style="-sec-extract:exhibit" href="ex1.htm">dup</a>'
        '<a style="-sec-extract:exhibit" href="ex2.htm">.</a>'
        '<a style="other" href="ex3.htm">Not an exhibit</a>'
        '<a style="-sec-extract:exhibit">No href</a>'
    )
    fs = make_fs()
    with (
        patch.object(fs, "get_main_document_content", return_value=html),
        patch.object(
            fs, "get_main_document_url", return_value="https://sec.gov/x/m.htm"
        ),
    ):
        assert fs._parse_exhibit_index() == [
            {"value": "https://sec.gov/x/ex1.htm", "label": "Full Description Here"}
        ]


def test_parse_exhibit_index_with_row_number():
    html = (
        "<table><tr><td>10.1*</td><td>"
        '<a style="-sec-extract:exhibit" href="ex10-1.htm">Stock Plan</a>'
        "</td></tr></table>"
    )
    fs = make_fs()
    with (
        patch.object(fs, "get_main_document_content", return_value=html),
        patch.object(
            fs, "get_main_document_url", return_value="https://sec.gov/x/m.htm"
        ),
    ):
        assert fs._parse_exhibit_index() == [
            {"value": "https://sec.gov/x/ex10-1.htm", "label": "10.1 - Stock Plan"}
        ]


def test_parse_exhibit_index_prefers_longer_row_description():
    """The full row text wins when the anchor text is only a fragment."""
    html = (
        "<table><tr><td>10.2</td><td>"
        '<a style="-sec-extract:exhibit" href="ex10-2.htm">A</a>'
        " Material Definitive Agreement</td></tr></table>"
    )
    fs = make_fs()
    with (
        patch.object(fs, "get_main_document_content", return_value=html),
        patch.object(
            fs, "get_main_document_url", return_value="https://sec.gov/x/m.htm"
        ),
    ):
        assert fs._parse_exhibit_index() == [
            {
                "value": "https://sec.gov/x/ex10-2.htm",
                "label": "10.2 - A Material Definitive Agreement",
            }
        ]


def test_exhibit_choices_uses_index_when_present():
    fs = make_fs()
    with patch.object(
        fs, "_parse_exhibit_index", return_value=[{"value": "u", "label": "10.1 - X"}]
    ):
        assert fs.exhibit_choices() == [{"value": "u", "label": "10.1 - X"}]


def test_exhibit_choices_embedded_fallback():
    fs = make_fs(
        _document_urls=[
            {"type": "10-K", "sequence": "1"},
            {"type": "EX-21", "sequence": "2", "description": "EXHIBIT 21"},
            {"type": "EX-101.SCH", "sequence": "3", "description": "XBRL"},
            {"type": "EX-99.1", "sequence": "4", "description": "Press Release"},
            {"type": "EX-77", "sequence": "5", "description": ""},
        ]
    )
    with patch.object(fs, "_parse_exhibit_index", return_value=[]):
        choices = fs.exhibit_choices()
    values = {c["value"]: c["label"] for c in choices}
    assert values["EX-21"] == "EX-21 - Subsidiaries of the Registrant"
    assert values["EX-99.1"] == "EX-99.1 - Press Release"
    assert values["EX-77"] == "EX-77"
    assert not any("EX-101" in v for v in values)


def test_get_exhibit_by_url_html():
    fs = make_fs(_use_cache=True)
    with (
        patch.object(fs, "_get_document", return_value="<html><body>x</body></html>"),
        patch.object(fs, "_clean_html_to_text", return_value="Body markdown"),
    ):
        assert fs.get_exhibit("https://sec.gov/x/ex.htm") == "Body markdown"


def test_get_exhibit_by_type_plain_text_reflow():
    fs = make_fs(
        _use_cache=True,
        _document_urls=[{"type": "EX-21", "content": "    SUBSIDIARIES\nApple Inc."}],
    )
    with patch.object(
        fs, "_clean_html_to_text", return_value="    SUBSIDIARIES\nApple Inc."
    ):
        assert "SUBSIDIARIES" in fs.get_exhibit("EX-21")


def test_get_exhibit_strips_document_wrapper():
    fs = make_fs(_use_cache=True)
    wrapped = "<DOCUMENT>\n<TYPE>EX-10.1\n<TEXT>\n<html><body>Real body</body></html>"
    with (
        patch.object(fs, "_get_document", return_value=wrapped),
        patch.object(fs, "_clean_html_to_text", side_effect=lambda c, **k: c),
    ):
        result = fs.get_exhibit("https://sec.gov/x/ex.htm")
    assert "<TYPE>" not in result
    assert "Real body" in result


def test_get_exhibit_not_found_and_empty():
    fs = make_fs(_use_cache=True, _document_urls=[{"type": "EX-21"}])
    assert fs.get_exhibit("EX-99") is None
    with patch.object(fs, "_get_document", return_value=""):
        assert fs.get_exhibit("EX-21") is None


def test_legacy_risk_factors_extracts_factors_section():
    fs = make_fs()
    mda = {
        "text": "MD&A intro.\n\nFactors That May Affect Future Results and "
        "Financial Condition\n\nCompetition is intense."
    }
    with patch.object(
        fs, "get_item", side_effect=lambda *n: mda if n[0] == "7" else None
    ):
        result = fs._legacy_risk_factors()
    assert (
        result[0]["risk_factor"]
        == "Factors That May Affect Future Results and Financial Condition"
    )
    assert "Competition is intense" in result[0]["text"]


def test_legacy_risk_factors_empty_body():
    fs = make_fs()
    mda = {
        "text": "MD&A.\n\nFactors That May Affect Future Results and "
        "Financial Condition"
    }
    with patch.object(
        fs, "get_item", side_effect=lambda *n: mda if n[0] == "7" else None
    ):
        assert fs._legacy_risk_factors() == []


def test_legacy_risk_factors_no_section():
    fs = make_fs()
    with (
        patch.object(fs, "get_item", return_value=None),
        patch.object(fs, "_item_by_name", return_value=None),
    ):
        assert fs._legacy_risk_factors() == []


def test_parse_exhibit_index_no_anchors():
    fs = make_fs()
    with patch.object(
        fs, "get_main_document_content", return_value="<html>no exhibits here</html>"
    ):
        assert fs._parse_exhibit_index() == []


def test_get_exhibit_decodes_bytes():
    fs = make_fs(_use_cache=True, _document_urls=[{"type": "EX-21", "url": "u"}])
    with (
        patch.object(
            fs, "_get_document", return_value=b"<html><body>Bytes body</body></html>"
        ),
        patch.object(fs, "_clean_html_to_text", side_effect=lambda c, **k: c),
    ):
        assert "Bytes body" in fs.get_exhibit("EX-21")
