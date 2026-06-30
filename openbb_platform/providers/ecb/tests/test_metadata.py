"""Unit tests for the ``openbb_ecb.utils.metadata`` package."""

import openbb_core.provider.utils.helpers as core_helpers
import pytest
from openbb_core.app.model.abstract.error import OpenBBError

from openbb_ecb.utils.metadata import EcbMetadata, _cache_mixin

_NS = (
    'xmlns:mes="http://www.sdmx.org/resources/sdmxml/schemas/v2_1/message" '
    'xmlns:str="http://www.sdmx.org/resources/sdmxml/schemas/v2_1/structure" '
    'xmlns:com="http://www.sdmx.org/resources/sdmxml/schemas/v2_1/common"'
)
_CODELIST_XML = (
    f"<mes:Structure {_NS}><mes:Structures><str:Codelists>"
    '<str:Codelist id="CL_TEST"><str:Code id="A">'
    '<com:Name xml:lang="en">Alpha</com:Name></str:Code>'
    "<str:Code/>"  # no id -> skipped
    "</str:Codelist>"
    '<str:Codelist id="CL_EMPTY"></str:Codelist>'  # no codes
    "</str:Codelists></mes:Structures></mes:Structure>"
).encode()
_CONSTRAINT_XML = (
    f"<mes:Structure {_NS}><mes:Structures><str:Constraints>"
    "<str:ContentConstraint><str:CubeRegion>"
    '<str:KeyValue id="CURRENCY"><str:Value>USD</str:Value>'
    "<str:Value>JPY</str:Value></str:KeyValue>"
    "<str:KeyValue><str:Value>X</str:Value></str:KeyValue>"  # no id -> skipped
    '<str:KeyValue id="EMPTY"></str:KeyValue>'  # no values -> skipped
    "</str:CubeRegion></str:ContentConstraint>"
    "</str:Constraints></mes:Structures></mes:Structure>"
).encode()


class _FakeResp:
    def __init__(self, status_code=200, content=b""):
        self.status_code = status_code
        self.content = content


def test_cache_loads():
    """The shipped cache populates the catalog."""
    meta = EcbMetadata()
    assert len(meta.dataflows) > 50
    assert "EXR" in meta.dataflows
    assert len(meta.codelists) > 100


def test_missing_cache_warns(monkeypatch, tmp_path):
    """A missing cache asset warns and leaves the catalog empty."""
    monkeypatch.setattr(_cache_mixin, "SHIPPED_CACHE_FILE", tmp_path / "absent.json.xz")
    EcbMetadata._reset()
    with pytest.warns(UserWarning):
        meta = EcbMetadata()
    assert meta.dataflows == {}


def test_search_and_list_dataflows():
    """Listing and text search over the catalog."""
    meta = EcbMetadata()
    assert "EXR" in {d["value"] for d in meta.search_dataflows("exchange")}
    assert {"MIR", "IRS"} & {d["value"] for d in meta.search_dataflows("interest rate")}
    assert any(d["value"] == "EXR" for d in meta.list_dataflows())


def test_dataflow_dimensions_and_parameters():
    """EXR resolves five ordered dimensions with decoded codelist values."""
    meta = EcbMetadata()
    dims = meta.get_dataflow_dimensions("EXR")
    assert [d["id"] for d in dims][:2] == ["FREQ", "CURRENCY"]
    params = meta.get_dataflow_parameters("EXR")
    # cached on the second call
    assert meta.get_dataflow_parameters("EXR") is params
    assert {"value": "D", "label": "Daily"} in params["FREQ"]
    assert meta.resolve_dimension_values("EXR", "FREQ")


def test_topics():
    """Topics derive from the category scheme."""
    meta = EcbMetadata()
    topics = meta.list_topics()
    assert topics and all("count" in t for t in topics)
    cat_id = topics[0]["value"]
    assert meta.get_topic_dataflows(cat_id)
    assert isinstance(meta.topics_for_dataflow("EXR"), list)


def test_concept_name_and_unknown_dataflow():
    """Concept lookup falls back to the id; unknown dataflows raise."""
    meta = EcbMetadata()
    assert meta.concept_name("") == ""
    assert meta.concept_name("FREQ")
    assert meta.concept_name("NOPE") == "NOPE"
    with pytest.raises(OpenBBError):
        meta.get_dataflow("NOT_A_FLOW")


def test_get_dsd_raises_when_missing(monkeypatch):
    """A dataflow without a resolvable DSD raises."""
    meta = EcbMetadata()
    meta.dataflows["FAKE"] = {"id": "FAKE", "dsd_id": "MISSING_DSD"}
    with pytest.raises(OpenBBError):
        meta.get_dsd_for_dataflow("FAKE")


def test_get_codelist_empty_id():
    """An empty codelist id returns an empty mapping."""
    meta = EcbMetadata()
    assert meta.get_codelist("") == {}


def test_fetch_codelist_live(monkeypatch):
    """A codelist absent from the cache is fetched live and merged in."""
    meta = EcbMetadata()
    monkeypatch.setattr(
        core_helpers, "make_request", lambda *a, **k: _FakeResp(200, _CODELIST_XML)
    )
    result = meta.get_codelist("CL_ABSENT_FROM_CACHE")
    assert result == {"A": "Alpha"}
    assert "CL_ABSENT_FROM_CACHE" in meta.codelists


def test_fetch_codelist_live_failure(monkeypatch):
    """A non-200 (or raising) live fetch returns an empty mapping."""
    meta = EcbMetadata()
    monkeypatch.setattr(
        core_helpers, "make_request", lambda *a, **k: _FakeResp(500, b"")
    )
    assert meta._fetch_codelist_live("CL_X") == {}

    def _boom(*a, **k):
        raise RuntimeError("network down")

    monkeypatch.setattr(core_helpers, "make_request", _boom)
    assert meta._fetch_codelist_live("CL_Y") == {}


def test_fetch_codelist_live_no_valid_codes(monkeypatch):
    """A codelist with no id-bearing codes yields an empty (unmerged) result."""
    meta = EcbMetadata()
    xml = (
        f"<mes:Structure {_NS}><mes:Structures><str:Codelists>"
        '<str:Codelist id="CL_X"><str:Code/></str:Codelist>'
        "</str:Codelists></mes:Structures></mes:Structure>"
    ).encode()
    monkeypatch.setattr(
        core_helpers, "make_request", lambda *a, **k: _FakeResp(200, xml)
    )
    assert meta._fetch_codelist_live("CL_X") == {}
    assert "CL_X" not in meta.codelists


def test_fetch_available_constraint(monkeypatch):
    """Availability constraints parse into {dimension: [values]}."""
    meta = EcbMetadata()
    monkeypatch.setattr(
        core_helpers, "make_request", lambda *a, **k: _FakeResp(200, _CONSTRAINT_XML)
    )
    out = meta._fetch_available_constraint("EXR", "D..EUR.SP00.A")
    assert out == {"CURRENCY": ["USD", "JPY"]}


def test_fetch_available_constraint_failure(monkeypatch):
    """A failed availability fetch returns an empty mapping."""
    meta = EcbMetadata()
    monkeypatch.setattr(
        core_helpers, "make_request", lambda *a, **k: _FakeResp(404, b"")
    )
    assert meta._fetch_available_constraint("EXR", "key") == {}


def test_singleton_identity_and_copy():
    """The singleton is shared and copy-safe."""
    import copy

    meta = EcbMetadata()
    assert EcbMetadata() is meta
    assert copy.copy(meta) is meta
    assert copy.deepcopy(meta) is meta


def test_fetch_available_constraint_request_raises(monkeypatch):
    """A raising HTTP call returns an empty mapping."""
    meta = EcbMetadata()

    def _boom(*a, **k):
        raise RuntimeError("down")

    monkeypatch.setattr(core_helpers, "make_request", _boom)
    assert meta._fetch_available_constraint("EXR", "key") == {}


def test_list_topics_skips_categories_without_dataflows():
    """A category with no dataflows is omitted from the topic list."""
    meta = EcbMetadata()
    meta.categories["EMPTY_CAT"] = {"name": "Empty", "description": ""}
    assert all(topic["value"] != "EMPTY_CAT" for topic in meta.list_topics())


def test_topics_for_dataflow_missing_category():
    """A dataflow pointing at an unknown category yields no topics."""
    meta = EcbMetadata()
    meta.dataflow_categories["EXR"] = ["NONEXISTENT_CAT"]
    assert meta.topics_for_dataflow("EXR") == []


def test_parse_search_query():
    """The search grammar: AND (+/space), OR (|), quoted phrases, empties."""
    from openbb_ecb.utils.metadata import _helpers

    assert _helpers.parse_search_query("   ") == []
    assert _helpers.parse_search_query("gdp + price") == [["gdp", "price"]]
    assert _helpers.parse_search_query('a "b c" | d') == [["a", "b c"], ["d"]]
    assert _helpers.parse_search_query("x+y") == [["x", "y"]]
    assert _helpers.parse_search_query("+ | +") == []  # only '+' tokens -> empty


def test_matches_query():
    """An empty parsed query matches everything; AND/OR semantics hold."""
    from openbb_ecb.utils.metadata import _helpers

    assert _helpers.matches_query("anything", []) is True
    assert _helpers.matches_query("hello world", [["hello", "world"]]) is True
    assert _helpers.matches_query("hello", [["zzz"]]) is False


def test_en_text():
    """English text is preferred; the first is used when no English exists."""
    import xml.etree.ElementTree as ET

    from openbb_ecb.utils.metadata import _helpers

    ns = 'xmlns:com="http://www.sdmx.org/resources/sdmxml/schemas/v2_1/common"'
    both = ET.fromstring(
        f"<root {ns}>"
        '<com:Name xml:lang="fr">Bonjour</com:Name>'
        '<com:Name xml:lang="en">Hello</com:Name></root>'
    )
    only_fr = ET.fromstring(
        f'<root {ns}><com:Name xml:lang="fr">Bonjour</com:Name></root>'
    )
    assert _helpers.en_text(None, "Name") == ""
    assert _helpers.en_text(both, "Name") == "Hello"
    assert _helpers.en_text(only_fr, "Name") == "Bonjour"
    assert _helpers.en_text(both, "Missing") == ""


_BSI_TABLE = "HCL_JDF_BSI_MFI_BALANCE_SHEET@HCL_BSI"


def test_table_mixin_list_and_structure():
    """Presentation tables list (dataflow-backed only) and resolve to a tree."""
    meta = EcbMetadata()
    tables = meta.list_tables()
    # Only dataflow-backed tables are listed -> fewer than the full HCL set.
    assert tables
    assert len(tables) < len(meta.presentation_tables)
    assert all(t["dataflow_id"] in meta.dataflows for t in tables)
    assert any(t["value"] == _BSI_TABLE for t in tables)
    # The label is the curated human description, not the raw HCL name.
    label = next(t["label"] for t in tables if t["value"] == _BSI_TABLE)
    assert label == "MFI balance sheet (BSI)"
    # Filtering by dataflow.
    by_flow = meta.list_tables_for_dataflow("BSI")
    assert by_flow and all(t["dataflow_id"] == "BSI" for t in by_flow)
    # The structure resolves row labels + maps codes to DSD dimensions.
    structure = meta.get_table_structure(_BSI_TABLE)
    assert structure[0]["label"]
    assert "BS_ITEM" in meta.get_table_dimensions(_BSI_TABLE)


def test_table_mixin_label_derived_fallback():
    """An id not in the curated map falls back to a derived label."""
    meta = EcbMetadata()
    # No "HCL_JDF_" and no "BSI_" prefix -> title-cased as-is.
    assert meta._table_label("FOO_BAR@HCL_BSI", "BSI") == "Foo Bar (BSI)"
    # "HCL_JDF_" and the dataflow prefix are stripped before title-casing.
    assert meta._table_label("HCL_JDF_BSI_FOO@HCL_BSI", "BSI") == "Foo (BSI)"


def test_table_mixin_get_table_and_labels():
    """``get_table`` raises for unknown ids; labels resolve from the right source."""
    meta = EcbMetadata()
    with pytest.raises(OpenBBError):
        meta.get_table("DOES_NOT_EXIST")
    row_code = next(iter(meta.row_labels))
    assert (
        meta.resolve_node_label({"code": row_code, "codelist_id": "JDF_ROW_LABELS"})
        == meta.row_labels[row_code]
    )
    # No code -> empty label.
    assert meta.resolve_node_label({"code": None, "codelist_id": "CL_BS_ITEM"}) == ""
    # Unknown code -> falls back to the code itself.
    assert (
        meta.resolve_node_label({"code": "ZZZ", "codelist_id": "CL_BS_ITEM"}) == "ZZZ"
    )


def test_dimensions_restricted_by_content_constraint():
    """Dimension values are restricted to the dataflow's content constraint.

    The shared codelist (CL_AREA's ~900 areas) is not the source of truth — the
    dataflow's content constraint is. ICB pins FREQ to quarterly and REF_AREA to
    a handful of areas.
    """
    meta = EcbMetadata()
    assert "ICB" in meta.dataflow_constraints
    dims = {d["id"]: d for d in meta.get_dataflow_dimensions("ICB")}
    assert dims["FREQ"]["n_values"] == 1
    assert dims["FREQ"]["values"][0]["value"] == "Q"
    assert dims["REF_AREA"]["n_values"] < 50
    assert dims["REF_AREA"]["n_values"] < len(meta.get_codelist("CL_AREA"))
    # constrained codes still carry their codelist labels
    assert all(v["label"] for v in dims["REF_AREA"]["values"])


def test_table_context_accessors():
    """Each dataflow-backed table ships a cached working default + valid context."""
    meta = EcbMetadata()
    bsi = "HCL_JDF_BSI_MFI_BALANCE_SHEET@HCL_BSI"
    default = meta.get_table_default_context(bsi)
    assert default.get("FREQ") == "M"
    assert default.get("REF_AREA") == "U2"
    valid = meta.get_table_valid_context(bsi)
    assert "U2" in valid.get("REF_AREA", [])
    # A table whose dataflow is discontinued has no derived context -> empties.
    mna = next(tid for tid in meta.presentation_tables if "@HCL_MNA" in tid)
    assert meta.get_table_default_context(mna) == {}
    assert meta.get_table_valid_context(mna) == {}


def test_dimensions_unconstrained_uses_full_codelist(monkeypatch):
    """A dimension with no content constraint falls back to the full codelist."""
    meta = EcbMetadata()
    # Drop EXR's constraint so its dimensions span the full codelists again.
    monkeypatch.setitem(meta.dataflow_constraints, "EXR", {})
    dims = {d["id"]: d for d in meta.get_dataflow_dimensions("EXR")}
    currency = dims["CURRENCY"]
    assert currency["n_values"] == len(meta.get_codelist(currency["codelist_id"]))


def test_table_mixin_dimension_for_codelist():
    """A codelist resolves to its DSD dimension, with graceful fallbacks."""
    meta = EcbMetadata()
    assert meta.dimension_for_codelist("BSI", "CL_BS_ITEM") == "BS_ITEM"
    assert meta.dimension_for_codelist("BSI", None) is None
    assert meta.dimension_for_codelist("BSI", "JDF_ROW_LABELS") is None
    assert meta.dimension_for_codelist("BSI", "CL_NOT_A_DIM") is None
    # Unknown dataflow -> DSD lookup raises -> None.
    assert meta.dimension_for_codelist("ZZZ_UNKNOWN", "CL_BS_ITEM") is None
