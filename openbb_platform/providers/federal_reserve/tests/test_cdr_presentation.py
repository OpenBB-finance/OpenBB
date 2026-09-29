"""Tests for the CDR taxonomy presentation-linkbase parser."""

import io
import zipfile

from openbb_federal_reserve.utils import cdr
from openbb_federal_reserve.utils.cdr import (
    _is_column,
    _type_label,
    build_presentation,
    parse_taxonomy,
    parse_xbrl_instance,
    presentation_map,
)

_PRESENTATION = (
    '<?xml version="1.0"?>'
    '<linkbase xmlns="http://www.xbrl.org/2003/linkbase"'
    ' xmlns:xlink="http://www.w3.org/1999/xlink">'
    '<presentationLink xlink:role="detail">'
    '<loc xlink:href="c.xsd#pres_secA" xlink:label="A"/>'
    '<loc xlink:href="c.xsd#pres_grp" xlink:label="G"/>'
    '<loc xlink:href="c.xsd#pres_line1" xlink:label="L1"/>'
    '<loc xlink:href="c.xsd#pres_colA" xlink:label="COL"/>'
    '<loc xlink:href="c.xsd#uc_X001" xlink:label="X1"/>'
    '<loc xlink:href="c.xsd#uc_X002" xlink:label="X2"/>'
    '<presentationArc xlink:from="A" xlink:to="G" order="1"/>'
    '<presentationArc xlink:from="G" xlink:to="L1" order="1"/>'
    '<presentationArc xlink:from="L1" xlink:to="X1" order="1"/>'
    '<presentationArc xlink:from="G" xlink:to="COL" order="2"/>'
    '<presentationArc xlink:from="COL" xlink:to="X2" order="1"/>'
    "</presentationLink>"
    '<presentationLink xlink:role="flat">'
    '<loc xlink:href="c.xsd#pres_secB" xlink:label="B"/>'
    '<loc xlink:href="c.xsd#uc_X001" xlink:label="X1"/>'
    '<presentationArc xlink:from="B" xlink:to="X1" order="1"/>'
    "</presentationLink>"
    "</linkbase>"
)

_LABEL = (
    '<?xml version="1.0"?>'
    '<linkbase xmlns="http://www.xbrl.org/2003/linkbase"'
    ' xmlns:xlink="http://www.w3.org/1999/xlink">'
    "<labelLink>"
    '<loc xlink:href="c.xsd#pres_secA" xlink:label="A"/>'
    '<labelArc xlink:from="A" xlink:to="A_l"/>'
    '<label xlink:label="A_l">Section A</label>'
    '<loc xlink:href="c.xsd#pres_grp" xlink:label="G"/>'
    '<labelArc xlink:from="G" xlink:to="G_l"/>'
    '<label xlink:label="G_l">Group One</label>'
    '<loc xlink:href="c.xsd#pres_line1" xlink:label="L1"/>'
    '<labelArc xlink:from="L1" xlink:to="L1_l"/>'
    '<label xlink:label="L1_l">Item One</label>'
    '<loc xlink:href="c.xsd#pres_colA" xlink:label="COL"/>'
    '<labelArc xlink:from="COL" xlink:to="COL_l"/>'
    '<label xlink:label="COL_l">Column A</label>'
    '<loc xlink:href="c.xsd#pres_secB" xlink:label="B"/>'
    '<labelArc xlink:from="B" xlink:to="B_l"/>'
    '<label xlink:label="B_l">Section B</label>'
    "</labelLink>"
    "</linkbase>"
)


def _taxonomy(pres_name: str = "x-presentation.xml", label_name: str = "x-label.xml"):
    """Build a minimal taxonomy ZIP with a presentation and label linkbase."""
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        archive.writestr(pres_name, _PRESENTATION)
        archive.writestr(label_name, _LABEL)
    return buffer.getvalue()


class TestIsColumn:
    """Tests for the column-caption guard."""

    def test_column_captions(self):
        """Column headers are recognized; line items are not."""
        assert _is_column("Column A")
        assert _is_column("DummyColumn")
        assert not _is_column("Interest Income")
        assert not _is_column(None)


class TestBuildPresentation:
    """Tests for the presentation hierarchy builder."""

    def test_hierarchy_order_and_columns(self):
        """Concepts get report order, parent-child captions, and column collapse."""
        result = build_presentation(_taxonomy())
        assert set(result) == {"X001", "X002"}
        # Order is per-section (1..N within the table), both in "Section A".
        assert result["X001"]["order"] == 1
        assert result["X002"]["order"] == 2
        assert result["X001"]["section_order"] == result["X002"]["section_order"] == 1
        # X001 keeps its richest (deepest) placement; the section is the table,
        # so level is its indent within it and parent is the line above.
        assert result["X001"]["section"] == "Section A"
        assert result["X001"]["parent"] == "Group One"
        assert result["X001"]["label"] == "Item One"
        assert result["X001"]["level"] == 2
        # X002 hangs under a column, which collapses to its group (a top-level
        # line, so it has no parent within the table).
        assert result["X002"]["label"] == "Group One"
        assert result["X002"]["parent"] is None
        assert result["X002"]["level"] == 1

    def test_call_linkbase_naming(self):
        """The Call Report ``-pres.xml`` / ``-cap.xml`` names are recognized."""
        taxonomy = _taxonomy("call-051-pres.xml", "call-051-cap.xml")
        assert build_presentation(taxonomy)["X001"]["label"] == "Item One"

    def test_missing_linkbase_returns_empty(self):
        """A taxonomy without the linkbases yields an empty map."""
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w") as archive:
            archive.writestr("concepts.xsd", "<xsd/>")
        assert build_presentation(buffer.getvalue()) == {}


_CONCEPTS_XSD = (
    '<?xml version="1.0"?>'
    '<xsd:schema xmlns:xsd="http://www.w3.org/2001/XMLSchema"'
    ' xmlns:xbrli="http://www.xbrl.org/2003/instance">'
    '<xsd:element name="RCON2170" type="xbrli:monetaryItemType"'
    ' xbrli:periodType="instant" xbrli:balance="debit"/>'
    '<xsd:element name="UBPRE013" type="us-gaap:pureItemType"'
    ' xbrli:periodType="duration"/>'
    '<xsd:element name="RCON2170" type="xbrli:monetaryItemType"/>'  # duplicate
    '<xsd:element type="xbrli:monetaryItemType"/>'  # no name, skipped
    "</xsd:schema>"
)


def _concepts_zip() -> bytes:
    """Build a taxonomy ZIP carrying a single Concepts.xsd member."""
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        archive.writestr("call-051-Concepts.xsd", _CONCEPTS_XSD)
        archive.writestr("notConcepts.xml", "<ignored/>")
    return buffer.getvalue()


class TestTypeLabel:
    """Tests for the XBRL element type to display-label mapper."""

    def test_known_type_maps_directly(self):
        """A type in the lookup table returns its mapped label."""
        assert _type_label("monetary") == "Monetary"

    def test_unknown_monetary_variant_falls_back_to_monetary(self):
        """An unrecognized monetary variant degrades to the base Monetary label."""
        assert _type_label("nonPositiveMonetary") == "Monetary"

    def test_unknown_integer_variant_falls_back_to_integer(self):
        """An unrecognized integer variant degrades to the base Integer label."""
        assert _type_label("signedInteger") == "Integer"

    def test_unrecognized_type_passes_through(self):
        """A type matching neither family passes through unchanged."""
        assert _type_label("anyURI") == "anyURI"

    def test_empty_type_yields_none(self):
        """An empty type string resolves to None."""
        assert _type_label("") is None


class TestParseTaxonomy:
    """Tests for the XBRL taxonomy concept parser."""

    def test_parses_concepts_with_types_and_dedup(self):
        """Each concept yields its mapped data type, period type, and balance."""
        concepts = {c["mdrm"]: c for c in parse_taxonomy(_concepts_zip())}
        assert set(concepts) == {"RCON2170", "UBPRE013"}
        assert concepts["RCON2170"]["data_type"] == "Monetary"
        assert concepts["RCON2170"]["period_type"] == "instant"
        assert concepts["RCON2170"]["balance"] == "debit"
        assert concepts["UBPRE013"]["data_type"] == "Rate or ratio"
        assert concepts["UBPRE013"]["period_type"] == "duration"


class TestPresentationMap:
    """Tests for the cached presentation-map accessor."""

    def test_caches_built_presentation(self, monkeypatch):
        """The map is built from the fetched taxonomy and cached on disk."""
        calls: list[int] = []

        def _fetch(report, form_type=None):
            """Return the taxonomy bytes and record each fetch."""
            calls.append(1)
            return _taxonomy()

        monkeypatch.setattr(cdr, "fetch_taxonomy", _fetch)
        first = presentation_map("call_single", "051")
        assert first["X001"]["label"] == "Item One"
        # Second call is served from the disk cache, not re-fetched.
        assert presentation_map("call_single", "051") == first
        assert calls == [1]


_INSTANCE_NO_PERIOD = (
    '<?xml version="1.0"?>'
    '<xbrl xmlns="http://www.xbrl.org/2003/instance"'
    ' xmlns:xbrli="http://www.xbrl.org/2003/instance"'
    ' xmlns:cc="https://www.cdr.ffiec.gov/xbrl/call/concepts">'
    '<context id="NOPERIOD"><entity><identifier scheme="x">37</identifier>'
    "</entity></context>"
    '<context id="CI"><entity><identifier scheme="x">37</identifier></entity>'
    "<period><instant>2024-03-31</instant></period></context>"
    '<unit id="USD"><measure>iso4217:USD</measure></unit>'
    '<cc:RCON2170 contextRef="CI" unitRef="USD" decimals="0">100</cc:RCON2170>'
    "</xbrl>"
)


class TestParseXbrlInstanceContexts:
    """Tests for context handling in the instance parser."""

    def test_skips_context_without_period(self):
        """A context that carries no period element is ignored."""
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w") as archive:
            archive.writestr(
                "FFIEC CDR Call FI 37(ID RSSD) 03312024.xbrl.xml",
                _INSTANCE_NO_PERIOD,
            )
        parsed = parse_xbrl_instance(buffer.getvalue(), "37")
        assert parsed["date"] == "2024-03-31"
        assert [item["mdrm"] for item in parsed["items"]] == ["RCON2170"]
