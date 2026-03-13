"""Comprehensive tests for XBRL taxonomy handling, parsing, and fact resolution.

Covers:
  - Taxonomy registry (TAXONOMIES dict, TaxonomyConfig, TaxonomyCategory)
  - XBRLNode dataclass
  - XBRLParser static helpers (_resolve_measure, _build_ns_prefix_map, _resolve_ns_prefix)
  - XBRLParser parsing methods (schema, labels, presentation, calculation, instance)
  - XBRLManager high-level API (list taxonomies, years, components, structure, metadata)
  - Instance-level fact resolution (units, contexts, labels, presentation, dimensions)
  - Schema files fetcher integration (progressive drill-down modes)

Network strategy
----------------
All tests that require HTTP make real network requests — no VCR cassettes.

**Module-scoped fixtures** ensure each expensive download or parse happens
at most **once per pytest run** of this file.  Cheap index-page fetches
(``get_available_years``, ``list_available_components``) are small enough
that per-test fetching is acceptable.
"""

# pylint: disable=C0415, C1803, W0212
# pylint: disable=redefined-outer-name, line-too-long, too-many-lines
# flake8: noqa: D102, E501

from __future__ import annotations

from io import BytesIO
from typing import Any

import pytest
from openbb_core.app.service.user_service import UserService
from openbb_sec.models.schema_files import (
    SecSchemaFilesFetcher,
    _flatten_nodes,
)
from openbb_sec.utils.xbrl_taxonomy_helper import (
    TAXONOMIES,
    TaxonomyCategory,
    TaxonomyConfig,
    TaxonomyStyle,
    XBRLManager,
    XBRLNode,
    XBRLParser,
)

test_credentials = UserService().default_user_settings.credentials.dict()


# ─── Per-test fixtures (cheap, no network) ────────────────────────────────


@pytest.fixture
def parser() -> XBRLParser:
    """Fresh XBRLParser instance."""
    return XBRLParser()


@pytest.fixture
def manager() -> XBRLManager:
    """Fresh XBRLManager instance."""
    return XBRLManager()


# ─── Module-scoped fixtures — each expensive fetch runs at most once ──────


@pytest.fixture(scope="module")
def apple_10k_parsed():
    """Download + fully parse Apple 10-K XBRL once for the module.

    This is the most expensive single operation in the suite (~15 s)
    because ``parse_instance`` with *base_url* resolves labels,
    presentation, and schemas from the filing's schemaRef chain.

    Returns ``(contexts, units, facts)``.
    """
    from openbb_core.provider.utils.helpers import make_request
    from openbb_sec.utils.definitions import HEADERS as SEC_HEADERS

    url = (
        "https://www.sec.gov/Archives/edgar/data/320193/"
        "000032019324000123/aapl-20240928_htm.xml"
    )
    resp = make_request(url, headers=SEC_HEADERS)
    p = XBRLParser()
    contexts, units, facts = p.parse_instance(BytesIO(resp.content), base_url=url)
    return contexts, units, facts


@pytest.fixture(scope="module")
def us_gaap_sfp_cls_nodes():
    """us-gaap 2024 classified balance-sheet structure (fetched once)."""
    return XBRLManager().get_structure("us-gaap", 2024, "sfp-cls")


@pytest.fixture(scope="module")
def dei_standard_nodes():
    """DEI 2024 standard structure (fetched once)."""
    return XBRLManager().get_structure("dei", 2024, "standard")


@pytest.fixture(scope="module")
def us_gaap_components_meta():
    """us-gaap 2024 component metadata list (fetched once)."""
    return XBRLManager().get_components_metadata("us-gaap", 2024)


@pytest.fixture(scope="module")
def hmrc_dpl_loaded():
    """HMRC DPL 2021 fully loaded — ``(manager, nodes)``.

    ``get_structure`` internally calls ``_ensure_labels`` and
    ``_ensure_element_properties``, so the returned manager has
    all parser state populated.
    """
    mgr = XBRLManager()
    nodes = mgr.get_structure("hmrc-dpl", 2021, "standard")
    return mgr, nodes


@pytest.fixture(scope="module")
def us_gaap_lab_bytes():
    """Raw bytes of the us-gaap 2024 label linkbase (fetched once)."""
    from openbb_sec.utils.xbrl_taxonomy_helper import FASBClient

    return FASBClient().fetch_file(
        "https://xbrl.fasb.org/us-gaap/2024/elts/us-gaap-lab-2024.xml"
    ).read()


@pytest.fixture(scope="module")
def us_gaap_doc_bytes():
    """Raw bytes of the us-gaap 2024 documentation linkbase (fetched once)."""
    from openbb_sec.utils.xbrl_taxonomy_helper import FASBClient

    return FASBClient().fetch_file(
        "https://xbrl.fasb.org/us-gaap/2024/elts/us-gaap-doc-2024.xml"
    ).read()


@pytest.fixture(scope="module")
def us_gaap_pres_bytes():
    """Raw bytes of the us-gaap sfp-cls presentation linkbase (fetched once)."""
    from openbb_sec.utils.xbrl_taxonomy_helper import FASBClient

    return FASBClient().fetch_file(
        "https://xbrl.fasb.org/us-gaap/2024/stm/us-gaap-stm-sfp-cls-pre-2024.xml"
    ).read()


@pytest.fixture(scope="module")
def us_gaap_cal_bytes():
    """Raw bytes of the us-gaap sfp-cls calculation linkbase (fetched once)."""
    from openbb_sec.utils.xbrl_taxonomy_helper import FASBClient

    return FASBClient().fetch_file(
        "https://xbrl.fasb.org/us-gaap/2024/stm/us-gaap-stm-sfp-cls-cal-2024.xml"
    ).read()


@pytest.fixture(scope="module")
def us_gaap_labels_manager():
    """XBRLManager with us-gaap 2024 labels + docs already loaded."""
    mgr = XBRLManager()
    mgr._ensure_labels("us-gaap", 2024)
    return mgr


# ═════════════════════════════════════════════════════════════════════════
# 1. Offline tests — no network, no fixtures
# ═════════════════════════════════════════════════════════════════════════


class TestTaxonomyRegistry:
    """Tests for the TAXONOMIES registry and its configuration objects."""

    def test_registry_has_expected_taxonomies(self):
        """All 24 registered taxonomies should be present."""
        expected = {
            "us-gaap",
            "srt",
            "dei",
            "ecd",
            "cyd",
            "ffd",
            "ifrs",
            "hmrc-dpl",
            "rxp",
            "spac",
            "cef",
            "oef",
            "vip",
            "fnd",
            "sro",
            "sbs",
            "rocr",
            "country",
            "currency",
            "exch",
            "naics",
            "sic",
            "stpr",
            "snj",
        }
        assert expected == set(TAXONOMIES.keys())

    def test_all_configs_are_taxonomy_config(self):
        """Every entry in TAXONOMIES must be a TaxonomyConfig instance."""
        for key, config in TAXONOMIES.items():
            assert isinstance(config, TaxonomyConfig), f"{key} is not TaxonomyConfig"

    def test_all_configs_have_required_fields(self):
        """Every TaxonomyConfig must have non-empty essential fields."""
        for key, config in TAXONOMIES.items():
            assert config.base_url_template, f"{key} missing base_url_template"
            assert isinstance(config.style, TaxonomyStyle), f"{key} bad style"
            assert config.label, f"{key} missing label"
            assert config.description, f"{key} missing description"
            assert isinstance(config.category, TaxonomyCategory), f"{key} bad category"

    def test_taxonomy_styles_complete(self):
        """All TaxonomyStyle values should be represented by at least one taxonomy."""
        styles_used = {config.style for config in TAXONOMIES.values()}
        for style in TaxonomyStyle:
            assert style in styles_used, f"TaxonomyStyle.{style.name} unused"

    def test_taxonomy_categories_complete(self):
        """All TaxonomyCategory values should be represented."""
        cats_used = {config.category for config in TAXONOMIES.values()}
        for cat in TaxonomyCategory:
            assert cat in cats_used, f"TaxonomyCategory.{cat.name} unused"

    def test_fasb_standard_taxonomies(self):
        """FASB_STANDARD taxonomies should point to xbrl.fasb.org."""
        for key, config in TAXONOMIES.items():
            if config.style == TaxonomyStyle.FASB_STANDARD:
                assert "xbrl.fasb.org" in config.base_url_template, key

    def test_sec_embedded_taxonomies(self):
        """SEC_EMBEDDED taxonomies should point to xbrl.sec.gov."""
        for key, config in TAXONOMIES.items():
            if config.style == TaxonomyStyle.SEC_EMBEDDED:
                assert "xbrl.sec.gov" in config.base_url_template, key

    def test_url_templates_have_year_placeholder(self):
        """Non-STATIC taxonomies must have {year} in their base_url_template."""
        for key, config in TAXONOMIES.items():
            if config.style != TaxonomyStyle.STATIC:
                assert (
                    "{year}" in config.base_url_template
                ), f"{key} missing {{year}} placeholder"

    def test_static_taxonomy_has_no_year_placeholder(self):
        """STATIC taxonomies should NOT have {year} in their base_url_template."""
        for key, config in TAXONOMIES.items():
            if config.style == TaxonomyStyle.STATIC:
                assert (
                    "{year}" not in config.base_url_template
                ), f"Static taxonomy {key} should not have {{year}}"


class TestXBRLNode:
    """Tests for the XBRLNode dataclass."""

    def test_basic_creation(self):
        """Create a minimal XBRLNode and verify fields."""
        node = XBRLNode(
            element_id="us-gaap_Assets",
            label="Assets",
            order=1.0,
            level=0,
            parent_id=None,
        )
        assert node.element_id == "us-gaap_Assets"
        assert node.label == "Assets"
        assert node.children == []
        assert node.abstract is False
        assert node.nillable is None

    def test_to_dict(self):
        """to_dict should serialize all fields including children."""
        child = XBRLNode(
            element_id="us-gaap_AssetsCurrent",
            label="Current Assets",
            order=1.0,
            level=1,
            parent_id="us-gaap_Assets",
        )
        parent = XBRLNode(
            element_id="us-gaap_Assets",
            label="Assets",
            order=1.0,
            level=0,
            parent_id=None,
            abstract=True,
            children=[child],
        )
        d = parent.to_dict()
        assert d["element_id"] == "us-gaap_Assets"
        assert d["abstract"] is True
        assert len(d["children"]) == 1
        assert d["children"][0]["element_id"] == "us-gaap_AssetsCurrent"

    def test_to_dict_all_metadata_fields(self):
        """to_dict should include all enriched metadata fields."""
        node = XBRLNode(
            element_id="us-gaap_Revenue",
            label="Revenue",
            order=2.0,
            level=0,
            parent_id=None,
            documentation="Total revenue recognized.",
            xbrl_type="monetaryItemType",
            period_type="duration",
            balance_type="credit",
            abstract=False,
            substitution_group="item",
            nillable=True,
            preferred_label="http://www.xbrl.org/2003/role/terseLabel",
        )
        d = node.to_dict()
        assert d["xbrl_type"] == "monetaryItemType"
        assert d["period_type"] == "duration"
        assert d["balance_type"] == "credit"
        assert d["substitution_group"] == "item"
        assert d["nillable"] is True
        assert d["preferred_label"] == "http://www.xbrl.org/2003/role/terseLabel"
        assert d["documentation"] == "Total revenue recognized."

    def test_flatten_nodes_helper(self):
        """_flatten_nodes should recursively flatten nested nodes."""
        child = XBRLNode(
            element_id="child",
            label="Child",
            order=1.0,
            level=1,
            parent_id="parent",
        )
        grandchild = XBRLNode(
            element_id="grandchild",
            label="Grandchild",
            order=1.0,
            level=2,
            parent_id="child",
        )
        child.children = [grandchild]
        parent = XBRLNode(
            element_id="parent",
            label="Parent",
            order=1.0,
            level=0,
            parent_id=None,
            children=[child],
        )
        flat = _flatten_nodes([parent])
        assert len(flat) == 3
        assert [f["name"] for f in flat] == ["parent", "child", "grandchild"]


class TestResolveHelpers:
    """Tests for XBRLParser static helper methods."""

    # -- _resolve_measure --

    def test_resolve_measure_currency(self):
        assert XBRLParser._resolve_measure("iso4217:USD") == "iso4217:USD"
        assert XBRLParser._resolve_measure("iso4217:EUR") == "iso4217:EUR"

    def test_resolve_measure_shares(self):
        assert XBRLParser._resolve_measure("xbrli:shares") == "shares"
        assert XBRLParser._resolve_measure("shares") == "shares"

    def test_resolve_measure_pure(self):
        assert XBRLParser._resolve_measure("xbrli:pure") == "pure"
        assert XBRLParser._resolve_measure("pure") == "pure"

    def test_resolve_measure_empty(self):
        assert XBRLParser._resolve_measure("") == ""
        assert XBRLParser._resolve_measure(None) == ""  # type: ignore

    def test_resolve_measure_custom(self):
        """Custom measures should be returned unchanged."""
        assert XBRLParser._resolve_measure("aapl:Vendor") == "aapl:Vendor"

    # -- _build_ns_prefix_map --

    def test_build_ns_prefix_map_simple(self):
        raw = b'<root xmlns:us-gaap="http://fasb.org/us-gaap/2024" xmlns:aapl="http://www.apple.com/20240928">'
        ns_map = XBRLParser._build_ns_prefix_map(raw)
        assert ns_map["http://fasb.org/us-gaap/2024"] == "us-gaap"
        assert ns_map["http://www.apple.com/20240928"] == "aapl"

    def test_build_ns_prefix_map_sec_taxonomies(self):
        raw = (
            b'<root xmlns:ecd="http://xbrl.sec.gov/ecd/2024" '
            b'xmlns:dei="http://xbrl.sec.gov/dei/2024" '
            b'xmlns:srt="http://fasb.org/srt/2024">'
        )
        ns_map = XBRLParser._build_ns_prefix_map(raw)
        assert ns_map["http://xbrl.sec.gov/ecd/2024"] == "ecd"
        assert ns_map["http://xbrl.sec.gov/dei/2024"] == "dei"
        assert ns_map["http://fasb.org/srt/2024"] == "srt"

    def test_build_ns_prefix_map_empty(self):
        ns_map = XBRLParser._build_ns_prefix_map(b"<root>")
        assert ns_map == {}

    def test_build_ns_prefix_map_single_quotes(self):
        raw = b"<root xmlns:foo='http://example.com/foo/2024'>"
        ns_map = XBRLParser._build_ns_prefix_map(raw)
        assert ns_map.get("http://example.com/foo/2024") == "foo"

    # -- _resolve_ns_prefix --

    def test_resolve_ns_prefix_direct_lookup(self):
        ns_map = {"http://www.apple.com/20240928": "aapl"}
        assert (
            XBRLParser._resolve_ns_prefix("http://www.apple.com/20240928", ns_map)
            == "aapl"
        )

    def test_resolve_ns_prefix_well_known_us_gaap(self):
        assert (
            XBRLParser._resolve_ns_prefix("http://fasb.org/us-gaap/2024", {})
            == "us-gaap"
        )

    def test_resolve_ns_prefix_well_known_dei(self):
        assert (
            XBRLParser._resolve_ns_prefix("http://xbrl.sec.gov/dei/2024", {}) == "dei"
        )

    def test_resolve_ns_prefix_well_known_srt(self):
        assert XBRLParser._resolve_ns_prefix("http://fasb.org/srt/2024", {}) == "srt"

    def test_resolve_ns_prefix_heuristic_skips_date(self):
        """Should skip trailing date-like segments to find semantic name."""
        assert (
            XBRLParser._resolve_ns_prefix("http://xbrl.sec.gov/ecd/2024", {}) == "ecd"
        )

    def test_resolve_ns_prefix_heuristic_company_extension(self):
        """Company extension URIs like http://company.com/20240928 get date skipped."""
        result = XBRLParser._resolve_ns_prefix("http://www.apple.com/20240928", {})
        assert not result.isdigit(), f"Got numeric prefix: {result}"

    def test_resolve_ns_prefix_prefers_xmlns_over_heuristic(self):
        """XMLS mapping should take priority over heuristic fallback."""
        ns_map = {"http://xbrl.sec.gov/ecd/2024": "ecd"}
        assert (
            XBRLParser._resolve_ns_prefix("http://xbrl.sec.gov/ecd/2024", ns_map)
            == "ecd"
        )


class TestParserWithSyntheticXML:
    """Tests using synthetic XBRL XML fragments — no network needed."""

    def _make_xml(self, xml_str: str) -> BytesIO:
        return BytesIO(xml_str.encode("utf-8"))

    def test_parse_units_simple(self, parser: XBRLParser):
        """Simple units should resolve correctly."""
        xml = self._make_xml(
            '<?xml version="1.0"?>'
            '<xbrli:xbrl xmlns:xbrli="http://www.xbrl.org/2003/instance">'
            '  <xbrli:unit id="usd">'
            "    <xbrli:measure>iso4217:USD</xbrli:measure>"
            "  </xbrli:unit>"
            '  <xbrli:unit id="shares">'
            "    <xbrli:measure>xbrli:shares</xbrli:measure>"
            "  </xbrli:unit>"
            '  <xbrli:unit id="pure">'
            "    <xbrli:measure>xbrli:pure</xbrli:measure>"
            "  </xbrli:unit>"
            "</xbrli:xbrl>"
        )
        root = parser._get_xml_root(xml)
        units = parser._parse_units(root)  # type: ignore
        assert units["usd"] == "iso4217:USD"
        assert units["shares"] == "shares"
        assert units["pure"] == "pure"

    def test_parse_units_compound(self, parser: XBRLParser):
        """Compound divide units (e.g. $/share) should resolve."""
        xml = self._make_xml(
            '<?xml version="1.0"?>'
            '<xbrli:xbrl xmlns:xbrli="http://www.xbrl.org/2003/instance">'
            '  <xbrli:unit id="usdPerShare">'
            "    <xbrli:divide>"
            "      <xbrli:unitNumerator>"
            "        <xbrli:measure>iso4217:USD</xbrli:measure>"
            "      </xbrli:unitNumerator>"
            "      <xbrli:unitDenominator>"
            "        <xbrli:measure>xbrli:shares</xbrli:measure>"
            "      </xbrli:unitDenominator>"
            "    </xbrli:divide>"
            "  </xbrli:unit>"
            "</xbrli:xbrl>"
        )
        root = parser._get_xml_root(xml)
        units = parser._parse_units(root)  # type: ignore
        assert units["usdPerShare"] == "iso4217:USD / shares"

    def test_parse_schema_elements(self, parser: XBRLParser):
        """parse_schema_elements should extract element definitions from a schema."""
        xml = self._make_xml(
            '<?xml version="1.0"?>'
            '<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema"'
            '           xmlns:xbrli="http://www.xbrl.org/2003/instance"'
            '           targetNamespace="http://example.com/2024">'
            '  <xs:element name="TestAsset"'
            '              id="example_TestAsset"'
            '              type="xbrli:monetaryItemType"'
            '              substitutionGroup="xbrli:item"'
            '              xbrli:periodType="instant"'
            '              xbrli:balance="debit"'
            '              abstract="false"'
            '              nillable="true"/>'
            "</xs:schema>"
        )
        nodes = parser.parse_schema_elements(xml)
        assert len(nodes) >= 1
        elem = nodes[0]
        assert elem.element_id == "example_TestAsset"

    def test_parse_instance_minimal(self, parser: XBRLParser):
        """Minimal instance doc with one context, one unit, one fact."""
        xml_str = (
            '<?xml version="1.0"?>'
            "<xbrli:xbrl "
            '  xmlns:xbrli="http://www.xbrl.org/2003/instance"'
            '  xmlns:us-gaap="http://fasb.org/us-gaap/2024"'
            '  xmlns:link="http://www.xbrl.org/2003/linkbase"'
            '  xmlns:xlink="http://www.w3.org/1999/xlink">'
            '  <xbrli:context id="ctx1">'
            "    <xbrli:entity>"
            '      <xbrli:identifier scheme="http://www.sec.gov/CIK">0000320193</xbrli:identifier>'
            "    </xbrli:entity>"
            "    <xbrli:period>"
            "      <xbrli:instant>2024-09-28</xbrli:instant>"
            "    </xbrli:period>"
            "  </xbrli:context>"
            '  <xbrli:unit id="usd">'
            "    <xbrli:measure>iso4217:USD</xbrli:measure>"
            "  </xbrli:unit>"
            '  <us-gaap:Assets contextRef="ctx1" unitRef="usd" decimals="-6">364980000000</us-gaap:Assets>'
            "</xbrli:xbrl>"
        )
        content = BytesIO(xml_str.encode("utf-8"))
        contexts, units, facts = parser.parse_instance(content)

        assert "ctx1" in contexts
        assert contexts["ctx1"]["entity"] == "0000320193"
        assert contexts["ctx1"]["period_type"] == "instant"
        assert contexts["ctx1"]["end"] == "2024-09-28"
        assert units["usd"] == "iso4217:USD"
        assert "us-gaap_Assets" in facts
        fact = facts["us-gaap_Assets"][0]
        assert fact["value"] == "364980000000"
        assert fact["unit"] == "iso4217:USD"
        assert fact["decimals"] == "-6"
        assert fact["entity"] == "0000320193"
        assert fact["period_type"] == "instant"

    def test_parse_instance_duration_context(self, parser: XBRLParser):
        """Duration contexts should have start and end dates."""
        xml_str = (
            '<?xml version="1.0"?>'
            "<xbrli:xbrl "
            '  xmlns:xbrli="http://www.xbrl.org/2003/instance"'
            '  xmlns:us-gaap="http://fasb.org/us-gaap/2024">'
            '  <xbrli:context id="dur1">'
            "    <xbrli:entity>"
            '      <xbrli:identifier scheme="http://www.sec.gov/CIK">0000789019</xbrli:identifier>'
            "    </xbrli:entity>"
            "    <xbrli:period>"
            "      <xbrli:startDate>2024-01-01</xbrli:startDate>"
            "      <xbrli:endDate>2024-12-31</xbrli:endDate>"
            "    </xbrli:period>"
            "  </xbrli:context>"
            '  <xbrli:unit id="usd"><xbrli:measure>iso4217:USD</xbrli:measure></xbrli:unit>'
            '  <us-gaap:Revenues contextRef="dur1" unitRef="usd" decimals="-6">245122000000</us-gaap:Revenues>'
            "</xbrli:xbrl>"
        )
        content = BytesIO(xml_str.encode("utf-8"))
        contexts, _, facts = parser.parse_instance(content)

        ctx = contexts["dur1"]
        assert ctx["period_type"] == "duration"
        assert ctx["start"] == "2024-01-01"
        assert ctx["end"] == "2024-12-31"

        fact = facts["us-gaap_Revenues"][0]
        assert fact["period_type"] == "duration"
        assert fact["start"] == "2024-01-01"
        assert fact["end"] == "2024-12-31"

    def test_parse_instance_dimensional_context(self, parser: XBRLParser):
        """Contexts with explicit dimensions should be captured."""
        xml_str = (
            '<?xml version="1.0"?>'
            "<xbrli:xbrl "
            '  xmlns:xbrli="http://www.xbrl.org/2003/instance"'
            '  xmlns:xbrldi="http://xbrl.org/2006/xbrldi"'
            '  xmlns:us-gaap="http://fasb.org/us-gaap/2024">'
            '  <xbrli:context id="dim1">'
            "    <xbrli:entity>"
            '      <xbrli:identifier scheme="http://www.sec.gov/CIK">0000320193</xbrli:identifier>'
            "      <xbrli:segment>"
            '        <xbrldi:explicitMember dimension="us-gaap:StatementBusinessSegmentsAxis">aapl:IPhoneMember</xbrldi:explicitMember>'
            "      </xbrli:segment>"
            "    </xbrli:entity>"
            "    <xbrli:period>"
            "      <xbrli:instant>2024-09-28</xbrli:instant>"
            "    </xbrli:period>"
            "  </xbrli:context>"
            '  <xbrli:unit id="usd"><xbrli:measure>iso4217:USD</xbrli:measure></xbrli:unit>'
            '  <us-gaap:Revenues contextRef="dim1" unitRef="usd" decimals="-6">46222000000</us-gaap:Revenues>'
            "</xbrli:xbrl>"
        )
        content = BytesIO(xml_str.encode("utf-8"))
        contexts, _, facts = parser.parse_instance(content)

        ctx = contexts["dim1"]
        assert "dimensions" in ctx
        assert "us-gaap:StatementBusinessSegmentsAxis" in ctx["dimensions"]
        assert (
            ctx["dimensions"]["us-gaap:StatementBusinessSegmentsAxis"]
            == "aapl:IPhoneMember"
        )

        fact = facts["us-gaap_Revenues"][0]
        assert "dimensions" in fact
        dim = fact["dimensions"]["us-gaap:StatementBusinessSegmentsAxis"]
        assert dim["member"] == "aapl:IPhoneMember"

    def test_parse_instance_namespace_prefix_resolution(self, parser: XBRLParser):
        """Tags from company-extension namespaces should use xmlns-declared prefixes."""
        xml_str = (
            '<?xml version="1.0"?>'
            "<xbrli:xbrl "
            '  xmlns:xbrli="http://www.xbrl.org/2003/instance"'
            '  xmlns:aapl="http://www.apple.com/20240928"'
            '  xmlns:ecd="http://xbrl.sec.gov/ecd/2024">'
            '  <xbrli:context id="c1">'
            "    <xbrli:entity>"
            '      <xbrli:identifier scheme="http://www.sec.gov/CIK">0000320193</xbrli:identifier>'
            "    </xbrli:entity>"
            "    <xbrli:period><xbrli:instant>2024-09-28</xbrli:instant></xbrli:period>"
            "  </xbrli:context>"
            '  <xbrli:unit id="usd"><xbrli:measure>iso4217:USD</xbrli:measure></xbrli:unit>'
            '  <aapl:CustomMeasure contextRef="c1" unitRef="usd" decimals="-6">123</aapl:CustomMeasure>'
            '  <ecd:TrdArrIndName contextRef="c1">John Doe</ecd:TrdArrIndName>'
            "</xbrli:xbrl>"
        )
        content = BytesIO(xml_str.encode("utf-8"))
        _, _, facts = parser.parse_instance(content)

        assert "aapl_CustomMeasure" in facts, f"Got keys: {list(facts.keys())}"
        assert "ecd_TrdArrIndName" in facts, f"Got keys: {list(facts.keys())}"
        wrong = [k for k in facts if k.startswith("20240928_") or k.startswith("2024_")]
        assert wrong == [], f"Wrong-prefix tags found: {wrong}"

    def test_parse_instance_multiple_facts_same_tag(self, parser: XBRLParser):
        """Multiple facts for the same tag should all be captured."""
        xml_str = (
            '<?xml version="1.0"?>'
            "<xbrli:xbrl "
            '  xmlns:xbrli="http://www.xbrl.org/2003/instance"'
            '  xmlns:us-gaap="http://fasb.org/us-gaap/2024">'
            '  <xbrli:context id="c1">'
            '    <xbrli:entity><xbrli:identifier scheme="http://www.sec.gov/CIK">123</xbrli:identifier></xbrli:entity>'
            "    <xbrli:period><xbrli:instant>2024-09-28</xbrli:instant></xbrli:period>"
            "  </xbrli:context>"
            '  <xbrli:context id="c2">'
            '    <xbrli:entity><xbrli:identifier scheme="http://www.sec.gov/CIK">123</xbrli:identifier></xbrli:entity>'
            "    <xbrli:period><xbrli:instant>2023-09-30</xbrli:instant></xbrli:period>"
            "  </xbrli:context>"
            '  <xbrli:unit id="usd"><xbrli:measure>iso4217:USD</xbrli:measure></xbrli:unit>'
            '  <us-gaap:Assets contextRef="c1" unitRef="usd" decimals="-6">364980000000</us-gaap:Assets>'
            '  <us-gaap:Assets contextRef="c2" unitRef="usd" decimals="-6">352583000000</us-gaap:Assets>'
            "</xbrli:xbrl>"
        )
        content = BytesIO(xml_str.encode("utf-8"))
        _, _, facts = parser.parse_instance(content)

        assert len(facts["us-gaap_Assets"]) == 2
        values = {f["value"] for f in facts["us-gaap_Assets"]}
        assert values == {"364980000000", "352583000000"}

    def test_parse_instance_no_unit(self, parser: XBRLParser):
        """Facts without unitRef should have empty/none unit."""
        xml_str = (
            '<?xml version="1.0"?>'
            "<xbrli:xbrl "
            '  xmlns:xbrli="http://www.xbrl.org/2003/instance"'
            '  xmlns:dei="http://xbrl.sec.gov/dei/2024">'
            '  <xbrli:context id="c1">'
            '    <xbrli:entity><xbrli:identifier scheme="http://www.sec.gov/CIK">123</xbrli:identifier></xbrli:entity>'
            "    <xbrli:period><xbrli:instant>2024-09-28</xbrli:instant></xbrli:period>"
            "  </xbrli:context>"
            '  <dei:EntityRegistrantName contextRef="c1">Apple Inc.</dei:EntityRegistrantName>'
            "</xbrli:xbrl>"
        )
        content = BytesIO(xml_str.encode("utf-8"))
        _, _, facts = parser.parse_instance(content)

        assert "dei_EntityRegistrantName" in facts
        fact = facts["dei_EntityRegistrantName"][0]
        assert fact["value"] == "Apple Inc."
        assert not fact.get("unit")


class TestXBRLManagerRegistry:
    """Tests for XBRLManager's taxonomy listing methods (registry-only)."""

    def test_list_available_taxonomies_all(self, manager: XBRLManager):
        """list_available_taxonomies() returns all 23 taxonomies."""
        result = manager.list_available_taxonomies()
        assert len(result) == len(TAXONOMIES)
        assert "us-gaap" in result
        assert "label" in result["us-gaap"]
        assert "description" in result["us-gaap"]
        assert "category" in result["us-gaap"]

    def test_list_available_taxonomies_filter_category(self, manager: XBRLManager):
        """Filtering by category should reduce results."""
        all_tax = manager.list_available_taxonomies()
        invest_tax = manager.list_available_taxonomies("investment_company")
        assert len(invest_tax) < len(all_tax)
        for meta in invest_tax.values():
            assert meta["category"] == "investment_company"

    def test_list_available_taxonomies_filter_enum(self, manager: XBRLManager):
        """Should also accept TaxonomyCategory enum value."""
        result = manager.list_available_taxonomies(TaxonomyCategory.COMMON_REFERENCE)
        for meta in result.values():
            assert meta["category"] == "common_reference"
        assert "dei" in result

    def test_list_available_taxonomies_invalid_category(self, manager: XBRLManager):
        """Invalid category string should raise ValueError."""
        with pytest.raises(ValueError, match="Invalid category"):
            manager.list_available_taxonomies("not_a_category")


# ═════════════════════════════════════════════════════════════════════════
# 2. Network tests — grouped by shared fixture
# ═════════════════════════════════════════════════════════════════════════


class TestXBRLManagerSmall:
    """Small / unique HTTP tests (cheap index-page fetches)."""

    def test_get_available_years_us_gaap(self, manager: XBRLManager):
        """us-gaap should have many years of taxonomy data."""
        years = manager.get_available_years("us-gaap")
        assert isinstance(years, list)
        assert len(years) > 5
        assert 2024 in years

    def test_get_available_years_dei(self, manager: XBRLManager):
        """DEI should have available years."""
        years = manager.get_available_years("dei")
        assert isinstance(years, list)
        assert len(years) > 0

    def test_get_available_years_unknown(self, manager: XBRLManager):
        """Unknown taxonomy should return empty list."""
        years = manager.get_available_years("nonexistent")
        assert years == []

    def test_list_available_components_us_gaap(self, manager: XBRLManager):
        """us-gaap 2024 should have multiple components."""
        components = manager.list_available_components("us-gaap", 2024)
        assert isinstance(components, list)
        assert len(components) > 10
        assert "sfp-cls" in components
        assert "soi" in components

    def test_list_available_components_dei(self, manager: XBRLManager):
        """Single-component taxonomies should return one standard component."""
        components = manager.list_available_components("dei", 2024)
        assert isinstance(components, list)
        assert len(components) >= 1


class TestUSGaapComponents:
    """Tests sharing the ``us_gaap_components_meta`` fixture (fetched once)."""

    def test_get_components_metadata_us_gaap(self, us_gaap_components_meta):
        """Component metadata should include labels and descriptions."""
        assert isinstance(us_gaap_components_meta, list)
        assert len(us_gaap_components_meta) > 10
        for item in us_gaap_components_meta:
            assert "name" in item
            assert "label" in item

    def test_mode2_taxonomy_with_year(self):
        """Mode 2: taxonomy + year → list components (fetcher integration)."""
        params: dict[str, Any] = {"taxonomy": "us-gaap", "year": 2024}
        fetcher = SecSchemaFilesFetcher()
        result = fetcher.test(params, test_credentials)
        assert result is None


class TestDEIStructure:
    """Tests sharing the ``dei_standard_nodes`` fixture (fetched once)."""

    def test_get_structure_dei(self, dei_standard_nodes):
        """get_structure should return XBRLNodes for a parsed component."""
        nodes = dei_standard_nodes
        assert isinstance(nodes, list)
        assert len(nodes) > 0
        assert all(isinstance(n, XBRLNode) for n in nodes)
        first = nodes[0]
        assert first.element_id
        assert first.label
        assert first.level >= 0

    def test_mode3_taxonomy_component(self):
        """Mode 3: taxonomy + component → parsed structure (fetcher integration)."""
        params: dict[str, Any] = {
            "taxonomy": "dei",
            "year": 2024,
            "component": "standard",
        }
        fetcher = SecSchemaFilesFetcher()
        result = fetcher.test(params, test_credentials)
        assert result is None


class TestUSGaapStructure:
    """Tests sharing the ``us_gaap_sfp_cls_nodes`` fixture (fetched once)."""

    def test_get_structure_us_gaap_balance_sheet(self, us_gaap_sfp_cls_nodes):
        """us-gaap classified balance sheet should have recognizable elements."""
        nodes = us_gaap_sfp_cls_nodes
        assert len(nodes) > 0
        flat = _flatten_nodes(nodes)
        element_ids = {f["name"] for f in flat}
        assert "us-gaap_Assets" in element_ids or any(
            "Assets" in eid for eid in element_ids
        )

    def test_get_structure_enriched_metadata(self, us_gaap_sfp_cls_nodes):
        """Parsed structure should include enriched element metadata."""
        flat = _flatten_nodes(us_gaap_sfp_cls_nodes)
        with_type = [f for f in flat if f.get("xbrl_type")]
        assert len(with_type) > 0, "Expected some elements with xbrl_type"
        with_period = [f for f in flat if f.get("period_type")]
        assert len(with_period) > 0

    def test_mode3_us_gaap_component(self):
        """Mode 3: us-gaap + specific component → parsed structure (fetcher integration)."""
        params: dict[str, Any] = {
            "taxonomy": "us-gaap",
            "year": 2024,
            "component": "sfp-cls",
        }
        fetcher = SecSchemaFilesFetcher()
        result = fetcher.test(params, test_credentials)
        assert result is None


class TestInstanceParsing:
    """Full instance document parsing — sharing ``apple_10k_parsed`` (parsed once)."""

    def test_parse_apple_10k_instance(self, apple_10k_parsed):
        """Parse Apple's 10-K XBRL instance with full resolution."""
        contexts, units, facts = apple_10k_parsed

        # Contexts
        assert len(contexts) > 10
        period_types = {ctx["period_type"] for ctx in contexts.values()}
        assert "instant" in period_types
        assert "duration" in period_types
        for ctx_id, ctx in contexts.items():
            assert ctx.get("entity"), f"Context {ctx_id} missing entity"

        # Units
        assert len(units) >= 2
        assert any("USD" in v for v in units.values())
        assert any("shares" in v.lower() for v in units.values())

        # Facts
        total_tags = len(facts)
        total_facts = sum(len(v) for v in facts.values())
        assert total_tags > 100, f"Only {total_tags} unique tags"
        assert total_facts > 500, f"Only {total_facts} total facts"

        wrong_prefix = [
            k for k in facts if k.startswith("20240928_") or k.startswith("2024_")
        ]
        assert wrong_prefix == [], f"Wrong-prefix tags: {wrong_prefix}"

        aapl_tags = [k for k in facts if k.startswith("aapl_")]
        ecd_tags = [k for k in facts if k.startswith("ecd_")]
        assert len(aapl_tags) > 0, "No aapl_ company extension tags found"
        assert len(ecd_tags) > 0, "No ecd_ tags found"

    def test_instance_label_coverage(self, apple_10k_parsed):
        """Label resolution should achieve very high coverage."""
        _, _, facts = apple_10k_parsed

        total_tags = len(facts)
        has_label = sum(1 for tag_facts in facts.values() if tag_facts[0].get("label"))
        coverage = has_label / total_tags * 100
        assert (
            coverage >= 95
        ), f"Label coverage only {coverage:.1f}% ({has_label}/{total_tags})"

    def test_instance_presentation_metadata(self, apple_10k_parsed):
        """Facts should have presentation metadata (table, parent, order)."""
        _, _, facts = apple_10k_parsed

        with_pres = sum(
            1 for tag_facts in facts.values() if tag_facts[0].get("presentation")
        )
        assert with_pres > 0, "No facts have presentation metadata"

        for tag_facts in facts.values():
            pres = tag_facts[0].get("presentation")
            if pres:
                entry = pres[0]
                assert "table" in entry
                assert "parent" in entry
                assert "order" in entry
                break

    def test_instance_unit_resolution(self, apple_10k_parsed):
        """Units should resolve to readable strings, not raw IDs."""
        _, units, facts = apple_10k_parsed

        unit_values = set(units.values())
        assert "iso4217:USD" in unit_values
        assert "shares" in unit_values

        compound = [v for v in unit_values if "/" in v]
        assert len(compound) > 0, "No compound units found (e.g. USD/share)"

        for tag, tag_facts in facts.items():
            for f in tag_facts:
                unit = f.get("unit")
                if unit:
                    assert (
                        "iso4217:" in unit
                        or unit in ("shares", "pure")
                        or "/" in unit
                        or ":" in unit
                    ), f"Unexpected unit format for {tag}: {unit}"


class TestSchemaFilesFetcher:
    """Integration tests for the SecSchemaFilesFetcher progressive modes."""

    def test_mode1_list_all_taxonomies(self):
        """Mode 1: No params → list all taxonomy families (no HTTP)."""
        params: dict[str, Any] = {}
        fetcher = SecSchemaFilesFetcher()
        result = fetcher.test(params, test_credentials)
        assert result is None

    def test_mode1_filter_by_category(self):
        """Mode 1: Filter by category (no HTTP)."""
        params: dict[str, Any] = {"category": "investment_company"}
        fetcher = SecSchemaFilesFetcher()
        result = fetcher.test(params, test_credentials)
        assert result is None

    def test_mode2_taxonomy_only(self):
        """Mode 2: taxonomy only → auto-resolve year, list components."""
        params: dict[str, Any] = {"taxonomy": "dei"}
        fetcher = SecSchemaFilesFetcher()
        result = fetcher.test(params, test_credentials)
        assert result is None

    def test_validation_year_without_taxonomy(self):
        """Test year without taxonomy should raise validation error."""
        with pytest.raises(Exception):
            params: dict[str, Any] = {"year": 2024}
            fetcher = SecSchemaFilesFetcher()
            fetcher.test(params, test_credentials)

    def test_validation_category_with_taxonomy(self):
        """Test category + taxonomy is invalid."""
        with pytest.raises(Exception):
            params: dict[str, Any] = {
                "taxonomy": "us-gaap",
                "category": "operating_company",
            }
            fetcher = SecSchemaFilesFetcher()
            fetcher.test(params, test_credentials)


class TestUSGaapLabelsParsing:
    """Tests for label/documentation/presentation linkbase parsing.

    Raw file bytes are shared via module-scoped fixtures so each file
    is downloaded at most once.
    """

    def test_parse_label_linkbase_us_gaap(self, us_gaap_lab_bytes):
        """Should parse labels from us-gaap label linkbase."""
        p = XBRLParser()
        result = p.parse_label_linkbase(
            BytesIO(us_gaap_lab_bytes), TaxonomyStyle.FASB_STANDARD
        )
        assert isinstance(result, dict)
        assert len(result) > 1000, f"Only {len(result)} labels parsed from us-gaap"
        assert len(p.labels) > 1000
        assert any("Assets" in k for k in p.labels), "No Assets-related label found"

    def test_parse_label_linkbase_documentation(self, us_gaap_doc_bytes):
        """FASB documentation lives in a separate *-doc-{year}.xml file."""
        p = XBRLParser()
        result = p.parse_label_linkbase(
            BytesIO(us_gaap_doc_bytes), TaxonomyStyle.FASB_STANDARD
        )

        all_roles: set[str] = set()
        for v in result.values():
            all_roles.update(v.keys())
        assert "documentation" in all_roles

        assert len(result) > 10000, f"Only {len(result)} doc entries"
        assert len(p.documentation) > 10000

        assets_docs = [
            v for k, v in p.documentation.items() if k.split("_")[-1] == "Assets"
        ]
        assert len(assets_docs) > 0, "No documentation for 'Assets'"
        assert len(assets_docs[0]) > 20, "Assets documentation is too short"

    def test_ensure_labels_loads_both_labels_and_docs(self, us_gaap_labels_manager):
        """XBRLManager._ensure_labels loads lab + doc files for FASB taxonomies."""
        mgr = us_gaap_labels_manager

        assert len(mgr.parser.labels) > 1000
        assert len(mgr.parser.documentation) > 1000, (
            f"Only {len(mgr.parser.documentation)} documentation entries — "
            "doc file not loaded"
        )

        has_both = [
            eid for eid in mgr.parser.labels if eid in mgr.parser.documentation
        ]
        assert (
            len(has_both) > 100
        ), f"Only {len(has_both)} elements have both label + documentation"

    def test_parse_presentation_balance_sheet(
        self, us_gaap_lab_bytes, us_gaap_pres_bytes
    ):
        """Should produce a tree structure for us-gaap classified balance sheet."""
        p = XBRLParser()
        p.parse_label_linkbase(
            BytesIO(us_gaap_lab_bytes), TaxonomyStyle.FASB_STANDARD
        )
        nodes = p.parse_presentation(
            BytesIO(us_gaap_pres_bytes), TaxonomyStyle.FASB_STANDARD
        )

        assert isinstance(nodes, list)
        assert len(nodes) > 0
        assert all(isinstance(n, XBRLNode) for n in nodes)
        assert all(n.level == 0 for n in nodes)

        flat = _flatten_nodes(nodes)
        element_ids = {f["name"] for f in flat}
        assert any("Assets" in eid for eid in element_ids)


class TestCalculationParsing:
    """Tests for calculation linkbase parsing."""

    def test_parse_calculation_us_gaap(self, us_gaap_cal_bytes):
        """Should parse calculation relationships."""
        p = XBRLParser()
        calculations = p.parse_calculation(
            BytesIO(us_gaap_cal_bytes), TaxonomyStyle.FASB_STANDARD
        )

        assert isinstance(calculations, dict)
        assert len(calculations) > 0

        for child_id, info in calculations.items():
            assert isinstance(child_id, str)
            assert isinstance(info, dict)
            assert "order" in info
            assert "weight" in info
            assert "parent_tag" in info
            assert isinstance(info["weight"], (int, float))
            assert isinstance(info["parent_tag"], str)


class TestHMRCDPLTaxonomy:
    """Offline tests for HMRC Detailed Profit & Loss taxonomy support."""

    def test_hmrc_dpl_in_registry(self):
        """hmrc-dpl should be in the TAXONOMIES registry."""
        assert "hmrc-dpl" in TAXONOMIES

    def test_hmrc_dpl_config(self):
        """hmrc-dpl config should have correct fields."""
        config = TAXONOMIES["hmrc-dpl"]
        assert config.style == TaxonomyStyle.EXTERNAL
        assert config.has_label_linkbase is True
        assert "{year}" in config.base_url_template
        assert "hmrc.gov.uk" in config.base_url_template
        assert config.label_file_pattern == "dpl-{year}-label.xml"
        assert config.presentation_file_template == "dpl-{year}-presentation.xml"

    def test_hmrc_dpl_available_years(self, manager: XBRLManager):
        """hmrc-dpl should return the known years (no HTTP needed)."""
        years = manager.get_available_years("hmrc-dpl")
        assert isinstance(years, list)
        assert 2021 in years
        assert 2019 in years
        assert len(years) == 2

    def test_hmrc_dpl_url_construction(self):
        """Verify URL templates format correctly for HMRC DPL."""
        config = TAXONOMIES["hmrc-dpl"]
        base_url = config.base_url_template.format(year=2021)
        assert base_url == "https://www.hmrc.gov.uk/schemas/ct/dpl/2021-01-01/"

        label_url = base_url + config.label_file_pattern.format(year=2021)
        assert label_url == (
            "https://www.hmrc.gov.uk/schemas/ct/dpl/2021-01-01/" "dpl-2021-label.xml"
        )

        pres_url = base_url + config.presentation_file_template.format(year=2021)
        assert pres_url == (
            "https://www.hmrc.gov.uk/schemas/ct/dpl/2021-01-01/"
            "dpl-2021-presentation.xml"
        )

    def test_hmrc_dpl_components(self, manager: XBRLManager):
        """hmrc-dpl should have a single 'standard' component."""
        components = manager.list_available_components("hmrc-dpl", 2021)
        assert components == ["standard"]


class TestHMRCDPLNetwork:
    """HMRC DPL HTTP tests — sharing ``hmrc_dpl_loaded`` (fetched once).

    ``get_structure`` internally calls ``_ensure_labels`` and
    ``_ensure_element_properties``, so the returned manager has all
    label and property state populated for verification.
    """

    def test_hmrc_dpl_labels(self, hmrc_dpl_loaded):
        """Should parse HMRC DPL labels from the standalone label XML."""
        mgr, _ = hmrc_dpl_loaded
        dpl_labels = {
            k: v for k, v in mgr.parser.labels.items() if k.startswith("dpl_")
        }
        assert (
            len(dpl_labels) >= 170
        ), f"Expected >=170 DPL labels, got {len(dpl_labels)}"
        assert "dpl_AdministrativeExpenses" in mgr.parser.labels
        assert (
            mgr.parser.labels["dpl_AdministrativeExpenses"]
            == "Administrative expenses"
        )

    def test_hmrc_dpl_element_properties(self, hmrc_dpl_loaded):
        """Should load element properties from dpl-2021.xsd."""
        mgr, _ = hmrc_dpl_loaded
        dpl_props = {
            k: v
            for k, v in mgr.parser.element_properties.items()
            if k.startswith("dpl_")
        }
        assert (
            len(dpl_props) >= 170
        ), f"Expected >=170 DPL properties, got {len(dpl_props)}"
        assert "dpl_AdministrativeExpenses" in mgr.parser.element_properties
        props = mgr.parser.element_properties["dpl_AdministrativeExpenses"]
        assert props.get("period_type") == "duration"

    def test_hmrc_dpl_structure(self, hmrc_dpl_loaded):
        """get_structure should return presentation tree for HMRC DPL."""
        _, nodes = hmrc_dpl_loaded
        assert isinstance(nodes, list)
        assert len(nodes) > 0
        assert all(isinstance(n, XBRLNode) for n in nodes)

        flat = _flatten_nodes(nodes)
        element_ids = {f["name"] for f in flat}

        assert any(eid.startswith("dpl_") for eid in element_ids)
        assert any(eid.startswith("core_") for eid in element_ids)
        assert len(flat) >= 500, f"Expected >=500 items, got {len(flat)}"

    def test_hmrc_dpl_frc_core_labels(self, hmrc_dpl_loaded):
        """FRC core labels should be loaded for cross-taxonomy resolution."""
        _, nodes = hmrc_dpl_loaded
        flat = _flatten_nodes(nodes)

        core_items = [f for f in flat if f["name"].startswith("core_")]
        assert len(core_items) > 0, "No FRC core elements found"

        labeled_core = [
            f for f in core_items if f.get("label") and f["label"] != f["name"]
        ]
        assert (
            len(labeled_core) > 0
        ), "FRC core labels not loaded — all core_* elements still show element_id as label"
