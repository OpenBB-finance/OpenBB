"""Unit tests for ``openbb_sec.utils.section_markdown``."""

import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from openbb_sec.utils.section_markdown import get_section_markdown


def _run(fs, section, url="https://sec.gov/f.htm"):
    with (
        patch(
            "openbb_sec.models.sec_financials.resolve_section_url",
            AsyncMock(return_value=url),
        ),
        patch(
            "openbb_sec.models.sec_financials.FinancialStatements.from_url",
            return_value=fs,
        ),
    ):
        return asyncio.run(get_section_markdown("AAPL", section))


def test_no_url_returns_friendly_message():
    with patch(
        "openbb_sec.models.sec_financials.resolve_section_url",
        AsyncMock(return_value=""),
    ):
        result = asyncio.run(get_section_markdown("AAPL", "risk_factors"))
    assert "No 10-K, 10-Q, 20-F, or 40-F filing" in result
    assert "AAPL" in result


def test_company_overview():
    fs = SimpleNamespace(business=lambda: "# Business\n\nWe make things.")
    assert "We make things." in _run(fs, "company_overview")


def test_risk_factors_combined_and_skips_empty():
    fs = SimpleNamespace(
        risk_factors=lambda: [
            {"risk_factor": "Risk A", "text": "Body A"},
            {"risk_factor": None, "text": "Intro"},
            {"risk_factor": "Risk B", "text": ""},
        ]
    )
    md = _run(fs, "risk_factors")
    assert "## Risk A\n\nBody A" in md
    assert "Intro" in md
    assert "Risk B" not in md


def test_segment_revenue_combined():
    fs = SimpleNamespace(segment_revenue=lambda: [{"name": "Revenue", "text": "table"}])
    assert "## Revenue\n\ntable" in _run(fs, "segment_revenue")


def test_segment_revenue_splits_into_per_year_tables():
    table = (
        "Intro text.\n\n"
        "|  | 2025 |  |  |\n"
        "|---|---|---|---|\n"
        "|  | Americas | Europe | Total |\n"
        "| Net sales | $1 | $2 | $3 |\n"
        "|  |  |  |  |\n"
        "|  | 2024 |  |  |\n"
        "|  | Americas | Europe | Total |\n"
        "| Net sales | $4 | $5 | $6 |\n"
    )
    fs = SimpleNamespace(segment_revenue=lambda: [{"name": "Segments", "text": table}])
    md = _run(fs, "segment_revenue")
    assert "### 2025" in md
    assert "### 2024" in md
    assert "Intro text." in md
    assert md.count("Net sales") == 2
    assert "$4" in md


def test_split_year_tables_leaves_plain_table_untouched():
    from openbb_sec.utils.section_markdown import _split_year_tables

    plain = "| A | B |\n|---|---|\n| 1 | 2 |"
    assert _split_year_tables(plain) == plain


def test_legal_proceedings_and_none():
    fs = SimpleNamespace(
        legal_proceedings=lambda: {"name": "Legal", "text": "## Item 3"}
    )
    assert _run(fs, "legal_proceedings") == "## Item 3"
    assert (
        _run(SimpleNamespace(legal_proceedings=lambda: None), "legal_proceedings") == ""
    )


def test_disclosures_combined_skips_invalid():
    fs = SimpleNamespace(
        is_xbrl=False,
        disclosures={
            "a": {"name": "Note A", "text": "Text A"},
            "b": "not a dict",
            "c": {"text": "  "},
        },
    )
    md = _run(fs, "disclosures")
    assert "## Note A\n\nText A" in md
    assert "not a dict" not in md


def test_disclosures_xbrl_text_left_unreflowed():
    fixed_width = "Cash     $ 5\nReceivables     $ 3"
    fs = SimpleNamespace(
        is_xbrl=True,
        disclosures={"a": {"name": "Note A", "text": fixed_width}},
    )
    md = _run(fs, "disclosures")
    assert fixed_width in md


def test_risk_factors_empty_returns_message():
    fs = SimpleNamespace(risk_factors=lambda: [])
    md = _run(fs, "risk_factors")
    assert "Item 1A" in md
    assert "2005" in md


def test_company_overview_empty_returns_message():
    fs = SimpleNamespace(business=lambda: None)
    md = _run(fs, "company_overview")
    assert "Business (Item 1)" in md


def test_unknown_section_returns_empty():
    assert _run(SimpleNamespace(), "bogus") == ""
