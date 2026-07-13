"""Unit tests for ``openbb_sec.utils.xbrl_render``."""

from openbb_sec.utils.xbrl_render import (
    _clean_member,
    _dims_str,
    _format_value,
    _header_line,
    _is_text_block,
    _looks_xbrl,
    _period_label,
    _period_sort_key,
    _strip_prefix,
    render_xbrl_facts,
)

_XBRL_BYTES = b"<xbrl xmlns='http://www.xbrl.org/2003/instance'>data</xbrl>"

_TEXT_BLOCK_HTML = "<table><tr><td>policy</td></tr></table>"


def _facts():
    """A representative ``parse_instance`` facts mapping."""
    return {
        "us-gaap:Revenues": [
            {
                "start": "2023-01-01",
                "end": "2023-12-31",
                "period_type": "duration",
                "label": "Revenues",
                "tag": "us-gaap:Revenues",
                "dimensions": {},
                "value": 1000,
                "unit": "usd",
                "presentation": [{"table": "Statements Of Operations", "order": 2.0}],
            },
            {
                "start": "2022-01-01",
                "end": "2022-12-31",
                "period_type": "duration",
                "label": "Revenues",
                "tag": "us-gaap:Revenues",
                "dimensions": {},
                "value": 900.5,
                "unit": "usd",
                "presentation": [{"table": "Statements Of Operations", "order": 2.0}],
            },
        ],
        "us-gaap:GrossProfit": [
            {
                "start": "2023-01-01",
                "end": "2023-12-31",
                "period_type": "duration",
                "label": "Gross Profit",
                "tag": "us-gaap:GrossProfit",
                "dimensions": {"axis1": {"label": "Segment A [Member]"}},
                "value": 500,
                "unit": "usd",
                "presentation": [{"table": "Statements Of Operations", "order": 1.0}],
            },
        ],
        "us-gaap:SharesOutstanding": [
            {
                "start": "2023-01-01",
                "end": "2023-12-31",
                "period_type": "duration",
                "label": "Shares",
                "tag": "us-gaap:SharesOutstanding",
                "dimensions": {},
                "value": 42,
                "unit": None,
                "presentation": [{"table": "Statements Of Operations", "order": 3.0}],
            },
        ],
        "dei:EntityRegistrantName": [
            {
                "end": "2023-12-31",
                "period_type": "instant",
                "label": "Entity Registrant Name",
                "tag": "dei:EntityRegistrantName",
                "dimensions": {},
                "value": "Apple Inc",
                "unit": None,
                "presentation": [{"table": "Cover", "order": 1.0}],
            },
        ],
        "dei:DocumentType": [
            {
                "end": "2023-12-31",
                "period_type": "instant",
                "label": "Document Type",
                "tag": "dei:DocumentType",
                "dimensions": {},
                "value": "10-K",
                "unit": None,
                "presentation": [{"table": "Cover", "order": 2.0}],
            },
        ],
        "dei:DocumentPeriodEndDate": [
            {
                "end": "2023-12-31",
                "period_type": "instant",
                "label": "Document Period End Date",
                "tag": "dei:DocumentPeriodEndDate",
                "dimensions": {},
                "value": "2023-12-31",
                "unit": None,
                "presentation": [{"table": "Cover", "order": 3.0}],
            },
        ],
        "us-gaap:PoliciesTextBlock": [
            {
                "end": "2023-12-31",
                "period_type": "instant",
                "label": "Policies",
                "tag": "us-gaap:SignificantAccountingPoliciesTextBlock",
                "dimensions": {},
                "value": _TEXT_BLOCK_HTML,
                "unit": None,
                "presentation": [{"table": "Notes", "order": 1.0}],
            },
            {
                "end": "2023-12-31",
                "period_type": "instant",
                "label": "Policies",
                "tag": "us-gaap:SignificantAccountingPoliciesTextBlock",
                "dimensions": {},
                "value": _TEXT_BLOCK_HTML,
                "unit": None,
                "presentation": [{"table": "Notes", "order": 1.0}],
            },
            {
                "end": "2023-12-31",
                "period_type": "instant",
                "label": "Empty",
                "tag": "us-gaap:EmptyTextBlock",
                "dimensions": {},
                "value": "",
                "unit": None,
                "presentation": [{"table": "Notes", "order": 2.0}],
            },
        ],
    }


def _patch_parser(monkeypatch, *, contexts=None, units=None, facts=None, exc=None):
    """Replace ``XBRLParser`` with a fake returning fixed parse_instance output."""

    class _FakeXBRLParser:
        def parse_instance(self, stream, base_url=None):
            if exc is not None:
                raise exc
            return (contexts or {}, units or {}, facts if facts is not None else {})

    monkeypatch.setattr(
        "openbb_sec.utils.xbrl_taxonomy_helper.XBRLParser", _FakeXBRLParser
    )


class TestStringHelpers:
    """Prefix-stripping and dimension-member cleaning."""

    def test_strip_prefix(self):
        assert _strip_prefix("us-gaap:Assets") == "Assets"
        assert _strip_prefix("Assets") == "Assets"
        assert _strip_prefix("") == ""
        assert _strip_prefix(None) == ""

    def test_clean_member_strips_member_suffixes(self):
        assert _clean_member("us-gaap:SegmentA [Member]") == "Segment A"
        assert _clean_member("FooBarMember") == "Foo Bar"
        assert _clean_member("prefix:Plain") == "Plain"

    def test_dims_str(self):
        assert _dims_str(None) == ""
        assert _dims_str({}) == ""
        assert _dims_str({"a": {"label": "X [Member]"}}) == "X"
        assert _dims_str({"a": {"member": "ns:BetaMember"}}) == "Beta"
        assert _dims_str({"a": {}}) == ""
        assert _dims_str({"a": "ns:ZetaMember"}) == "Zeta"
        assert _dims_str({"a": {"label": "Alpha"}, "b": "Beta"}) == "Alpha; Beta"


class TestPeriodHelpers:
    """Period labels and sort keys."""

    def test_period_label_instant(self):
        assert (
            _period_label({"period_type": "instant", "start": "", "end": "2023-12-31"})
            == "2023-12-31"
        )

    def test_period_label_duration_range(self):
        assert (
            _period_label(
                {
                    "period_type": "duration",
                    "start": "2023-01-01",
                    "end": "2023-12-31",
                }
            )
            == "2023-01-01 – 2023-12-31"
        )

    def test_period_label_duration_without_start(self):
        assert (
            _period_label({"period_type": "duration", "start": "", "end": "2023-12-31"})
            == "2023-12-31"
        )

    def test_period_sort_key(self):
        assert _period_sort_key("2023-01-01 – 2023-12-31") == "2023-12-31"
        assert _period_sort_key("short") == "short"


class TestFactClassifiers:
    """Text-block detection and value formatting."""

    def test_is_text_block(self):
        assert _is_text_block({"tag": "us-gaap:FooTextBlock", "value": 1}) is True
        assert _is_text_block({"tag": "us-gaap:Foo", "value": "  <div>x"}) is True
        assert _is_text_block({"tag": "us-gaap:Foo", "value": 1000}) is False
        assert _is_text_block({"tag": "us-gaap:Foo", "value": "plain"}) is False

    def test_format_value(self):
        assert _format_value(None) == ""
        assert _format_value("") == ""
        assert _format_value(1000) == "1,000"
        assert _format_value(1000.0) == "1,000"
        assert _format_value(1234.5) == "1,234.5"
        assert _format_value("n/a") == "n/a"

    def test_header_line(self):
        assert _header_line(_facts()) == "Apple Inc · 10-K · 2023-12-31"
        assert _header_line({}) == ""


class TestRenderXbrlFacts:
    """End-to-end rendering of an XBRL instance via a patched parser."""

    def test_renders_statements_cover_and_notes(self, monkeypatch):
        _patch_parser(monkeypatch, units={"usd": "USD"}, facts=_facts())
        html = render_xbrl_facts(_XBRL_BYTES, source_url="https://www.sec.gov/d/x.xml")
        assert html is not None
        assert "<h1>XBRL Facts</h1>" in html
        assert "Apple Inc · 10-K · 2023-12-31" in html
        assert "1,000" in html and "900.5" in html
        assert "Gross Profit — Segment A" in html
        assert "USD" in html
        # Cover is ordered ahead of the other statement tables.
        assert html.index('data-name="Cover"') < html.index(
            'data-name="Statements Of Operations"'
        )
        # The duplicated text block is rendered exactly once.
        assert html.count(_TEXT_BLOCK_HTML) == 1

    def test_truncated_preview_with_source_url(self, monkeypatch):
        _patch_parser(monkeypatch, units={"usd": "USD"}, facts=_facts())
        html = render_xbrl_facts(
            _XBRL_BYTES, source_url="https://www.sec.gov/d/x.xml", truncated=True
        )
        assert "open the full document" in html
        assert "https://www.sec.gov/d/x.xml" in html

    def test_truncated_preview_without_source_url(self, monkeypatch):
        _patch_parser(monkeypatch, units={"usd": "USD"}, facts=_facts())
        html = render_xbrl_facts(_XBRL_BYTES, truncated=True)
        assert "Showing a preview of a large file." in html

    def test_not_xbrl_returns_none(self):
        assert render_xbrl_facts(b"<html><body>not xbrl</body></html>") is None

    def test_parse_error_returns_none(self, monkeypatch):
        _patch_parser(monkeypatch, exc=ValueError("bad"))
        assert render_xbrl_facts(_XBRL_BYTES) is None

    def test_no_facts_returns_none(self, monkeypatch):
        _patch_parser(monkeypatch, facts={})
        assert render_xbrl_facts(_XBRL_BYTES) is None

    def test_no_presentation_tables_returns_none(self, monkeypatch):
        facts = {
            "us-gaap:Revenues": [
                {
                    "end": "2023-12-31",
                    "period_type": "instant",
                    "label": "Revenues",
                    "tag": "us-gaap:Revenues",
                    "dimensions": {},
                    "value": 1,
                    "unit": None,
                    "presentation": None,
                }
            ]
        }
        _patch_parser(monkeypatch, facts=facts)
        assert render_xbrl_facts(_XBRL_BYTES) is None


def test_looks_xbrl():
    """``_looks_xbrl`` matches the instance namespace or root tag."""
    assert _looks_xbrl(b"<xbrl>") is True
    assert (
        _looks_xbrl(b"<?xml?><foo xmlns='http://www.xbrl.org/2003/instance'>") is True
    )
    assert _looks_xbrl(b"<html><body></body></html>") is False
