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
    "<str:Code/>"
    "</str:Codelist>"
    '<str:Codelist id="CL_EMPTY"></str:Codelist>'
    "</str:Codelists></mes:Structures></mes:Structure>"
).encode()
_CONSTRAINT_XML = (
    f"<mes:Structure {_NS}><mes:Structures><str:Constraints>"
    "<str:ContentConstraint><str:CubeRegion>"
    '<str:KeyValue id="CURRENCY"><str:Value>USD</str:Value>'
    "<str:Value>JPY</str:Value></str:KeyValue>"
    "<str:KeyValue><str:Value>X</str:Value></str:KeyValue>"
    '<str:KeyValue id="EMPTY"></str:KeyValue>'
    "</str:CubeRegion></str:ContentConstraint>"
    "</str:Constraints></mes:Structures></mes:Structure>"
).encode()


class _FakeResp:
    def __init__(self, status_code=200, content=b""):
        self.status_code = status_code
        self.content = content


def test_cache_loads():
    meta = EcbMetadata()
    assert len(meta.dataflows) > 50
    assert "EXR" in meta.dataflows
    assert len(meta.codelists) > 100


def test_missing_cache_warns(monkeypatch, tmp_path):
    monkeypatch.setattr(_cache_mixin, "SHIPPED_CACHE_FILE", tmp_path / "absent.json.xz")
    EcbMetadata._reset()
    with pytest.warns(UserWarning):
        meta = EcbMetadata()
    assert meta.dataflows == {}


def test_search_and_list_dataflows():
    meta = EcbMetadata()
    assert "EXR" in {d["value"] for d in meta.search_dataflows("exchange")}
    assert {"MIR", "IRS"} & {d["value"] for d in meta.search_dataflows("interest rate")}
    assert any(d["value"] == "EXR" for d in meta.list_dataflows())


def test_dataflow_dimensions_and_parameters():
    meta = EcbMetadata()
    dims = meta.get_dataflow_dimensions("EXR")
    assert [d["id"] for d in dims][:2] == ["FREQ", "CURRENCY"]
    params = meta.get_dataflow_parameters("EXR")
    assert meta.get_dataflow_parameters("EXR") is params
    assert {"value": "D", "label": "Daily"} in params["FREQ"]
    assert meta.resolve_dimension_values("EXR", "FREQ")


def test_topics():
    meta = EcbMetadata()
    topics = meta.list_topics()
    assert topics and all("count" in t for t in topics)
    cat_id = topics[0]["value"]
    assert meta.get_topic_dataflows(cat_id)
    assert isinstance(meta.topics_for_dataflow("EXR"), list)


def test_concept_name_and_unknown_dataflow():
    meta = EcbMetadata()
    assert meta.concept_name("") == ""
    assert meta.concept_name("FREQ")
    assert meta.concept_name("NOPE") == "NOPE"
    with pytest.raises(OpenBBError):
        meta.get_dataflow("NOT_A_FLOW")


def test_get_dsd_raises_when_missing(monkeypatch):
    meta = EcbMetadata()
    meta.dataflows["FAKE"] = {"id": "FAKE", "dsd_id": "MISSING_DSD"}
    with pytest.raises(OpenBBError):
        meta.get_dsd_for_dataflow("FAKE")


def test_get_codelist_empty_id():
    meta = EcbMetadata()
    assert meta.get_codelist("") == {}


def test_fetch_codelist_live(monkeypatch):
    meta = EcbMetadata()
    monkeypatch.setattr(
        core_helpers, "make_request", lambda *a, **k: _FakeResp(200, _CODELIST_XML)
    )
    result = meta.get_codelist("CL_ABSENT_FROM_CACHE")
    assert result == {"A": "Alpha"}
    assert "CL_ABSENT_FROM_CACHE" in meta.codelists


def test_fetch_codelist_live_failure(monkeypatch):
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
    meta = EcbMetadata()
    monkeypatch.setattr(
        core_helpers, "make_request", lambda *a, **k: _FakeResp(200, _CONSTRAINT_XML)
    )
    out = meta._fetch_available_constraint("EXR", "D..EUR.SP00.A")
    assert out == {"CURRENCY": ["USD", "JPY"]}


def test_fetch_available_constraint_failure(monkeypatch):
    meta = EcbMetadata()
    monkeypatch.setattr(
        core_helpers, "make_request", lambda *a, **k: _FakeResp(404, b"")
    )
    assert meta._fetch_available_constraint("EXR", "key") == {}


def test_singleton_identity_and_copy():
    import copy

    meta = EcbMetadata()
    assert EcbMetadata() is meta
    assert copy.copy(meta) is meta
    assert copy.deepcopy(meta) is meta


def test_fetch_available_constraint_request_raises(monkeypatch):
    meta = EcbMetadata()

    def _boom(*a, **k):
        raise RuntimeError("down")

    monkeypatch.setattr(core_helpers, "make_request", _boom)
    assert meta._fetch_available_constraint("EXR", "key") == {}


def test_list_topics_skips_categories_without_dataflows():
    meta = EcbMetadata()
    meta.categories["EMPTY_CAT"] = {"name": "Empty", "description": ""}
    assert all(topic["value"] != "EMPTY_CAT" for topic in meta.list_topics())


def test_topics_for_dataflow_missing_category():
    meta = EcbMetadata()
    meta.dataflow_categories["EXR"] = ["NONEXISTENT_CAT"]
    assert meta.topics_for_dataflow("EXR") == []


def test_parse_search_query():
    from openbb_ecb.utils.metadata import _helpers

    assert _helpers.parse_search_query("   ") == []
    assert _helpers.parse_search_query("gdp + price") == [["gdp", "price"]]
    assert _helpers.parse_search_query('a "b c" | d') == [["a", "b c"], ["d"]]
    assert _helpers.parse_search_query("x+y") == [["x", "y"]]
    assert _helpers.parse_search_query("+ | +") == []


def test_matches_query():
    from openbb_ecb.utils.metadata import _helpers

    assert _helpers.matches_query("anything", []) is True
    assert _helpers.matches_query("hello world", [["hello", "world"]]) is True
    assert _helpers.matches_query("hello", [["zzz"]]) is False


def test_en_text():
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


_BSI_TABLE = "BSI01_01"
_JDF_TABLE = "HCL_JDF_BSI_MFI_BALANCE_SHEET@HCL_BSI"
_FAKE_TABLES = {
    "BSI01_01": {
        "id": "BSI01_01",
        "title": "Monetary aggregates",
        "category": "Money, credit and banking",
        "subcategory": "Monetary aggregates",
        "source": "publications",
        "rows": [{"flow": "BSI", "key": "M.U2.X"}, {"flow": "BSI", "key": "M.U2.Y"}],
    },
    "HICP01_01": {
        "id": "HICP01_01",
        "title": "HICP",
        "category": "Macroeconomic and sectoral statistics",
        "subcategory": "HICP",
        "source": "publications",
        "rows": [{"flow": "HICP", "key": "M.U2.Z"}],
    },
    _JDF_TABLE: {
        "id": _JDF_TABLE,
        "name": "Hierarchy",
        "dataflow_id": "BSI",
        "source": "jdf",
        "tree": [
            {
                "code": "80997156",
                "codelist_id": "JDF_ROW_LABELS",
                "children": [
                    {"code": "A20", "codelist_id": "CL_BS_ITEM", "children": []},
                ],
            }
        ],
        "default_context": {"FREQ": "M", "BS_ITEM": "A20"},
        "valid_context": {"FREQ": ["M", "Q"]},
    },
    "HCL_JDF_GONE@HCL_ZZZ": {
        "id": "HCL_JDF_GONE@HCL_ZZZ",
        "name": "Gone",
        "dataflow_id": "ZZZ",
        "source": "jdf",
        "tree": [],
    },
}
_FAKE_CONCEPTS = {
    "bank-interest-rates": {
        "slug": "bank-interest-rates",
        "name": "Bank interest rates",
        "datasets": ["MIR"],
    },
    "car-registrations": {
        "slug": "car-registrations",
        "name": "Car registrations",
        "datasets": [],
    },
}
_FAKE_INFO = {
    "MIR": {
        "title": "MFI Interest Rate Statistics - MIR",
        "catalogue": "",
        "fields": [{"key": "scope", "label": "Scope", "html": "<p>x</p>"}],
    },
}


def test_table_mixin_list(monkeypatch):
    meta = EcbMetadata()
    monkeypatch.setattr(meta, "presentation_tables", _FAKE_TABLES)
    tables = meta.list_tables()
    values = {t["value"] for t in tables}
    assert "HCL_JDF_GONE@HCL_ZZZ" not in values
    entry = next(t for t in tables if t["value"] == _BSI_TABLE)
    assert entry["source"] == "publications"
    assert entry["label"] == "Money, credit and banking — Monetary aggregates"
    jdf = next(t for t in tables if t["value"] == _JDF_TABLE)
    assert jdf["source"] == "jdf"
    assert jdf["label"] == "MFI balance sheet (BSI)"
    keys = [(t["category"], t["label"]) for t in tables]
    assert keys == sorted(keys)


def test_table_mixin_list_for_dataflow(monkeypatch):
    meta = EcbMetadata()
    monkeypatch.setattr(meta, "presentation_tables", _FAKE_TABLES)
    by_flow = meta.list_tables_for_dataflow("BSI")
    values = {t["value"] for t in by_flow}
    assert _BSI_TABLE in values
    assert _JDF_TABLE in values


def test_table_mixin_label():
    meta = EcbMetadata()
    assert meta._publication_label({"title": "T", "category": "C"}) == "C — T"
    assert meta._publication_label({"title": "T", "category": ""}) == "T"
    assert meta._publication_label({"id": "X"}) == "X"
    assert meta._jdf_label(_JDF_TABLE, "BSI") == "MFI balance sheet (BSI)"
    assert meta._jdf_label("HCL_JDF_BSI_CUSTOM@HCL_BSI", "BSI") == "Custom (BSI)"
    assert meta._jdf_label("OTHER@HCL_BSI", "BSI") == "Other (BSI)"


def test_table_mixin_get_table_and_rows(monkeypatch):
    meta = EcbMetadata()
    monkeypatch.setattr(meta, "presentation_tables", _FAKE_TABLES)
    with pytest.raises(OpenBBError):
        meta.get_table("DOES_NOT_EXIST")
    with pytest.raises(OpenBBError):
        meta.get_table_rows("DOES_NOT_EXIST")
    rows = meta.get_table_rows(_BSI_TABLE)
    assert rows and all("flow" in r and "key" in r for r in rows)


def test_table_mixin_jdf(monkeypatch):
    meta = EcbMetadata()
    monkeypatch.setattr(meta, "presentation_tables", _FAKE_TABLES)
    monkeypatch.setattr(meta, "row_labels", {"80997156": "Total"})
    monkeypatch.setattr(meta, "codelists", {"CL_BS_ITEM": {"A20": "Loans"}})
    monkeypatch.setattr(
        meta,
        "get_dsd_for_dataflow",
        lambda df: {"dimensions": [{"id": "BS_ITEM", "codelist_id": "CL_BS_ITEM"}]},
    )
    assert meta.resolve_node_label({"code": "", "codelist_id": ""}) == ""
    assert (
        meta.resolve_node_label({"code": "80997156", "codelist_id": "JDF_ROW_LABELS"})
        == "Total"
    )
    assert meta.resolve_node_label({"code": "A20", "codelist_id": "CL_BS_ITEM"}) == (
        "Loans"
    )
    assert meta.dimension_for_codelist("BSI", None) is None
    assert meta.dimension_for_codelist("BSI", "JDF_ROW_LABELS") is None
    assert meta.dimension_for_codelist("BSI", "CL_BS_ITEM") == "BS_ITEM"
    assert meta.dimension_for_codelist("BSI", "CL_MISSING") is None
    structure = meta.get_table_structure(_JDF_TABLE)
    assert structure[0]["label"] == "Total"
    assert structure[0]["children"][0]["dimension_id"] == "BS_ITEM"
    assert meta.get_table_dimensions(_JDF_TABLE) == ["BS_ITEM"]
    assert meta.get_table_default_context(_JDF_TABLE)["FREQ"] == "M"
    assert meta.get_table_valid_context(_JDF_TABLE)["FREQ"] == ["M", "Q"]


def test_table_mixin_dimension_for_codelist_error(monkeypatch):
    from openbb_core.app.model.abstract.error import OpenBBError as _Err

    meta = EcbMetadata()

    def _raise(df):
        raise _Err("no dsd")

    monkeypatch.setattr(meta, "get_dsd_for_dataflow", _raise)
    assert meta.dimension_for_codelist("BSI", "CL_BS_ITEM") is None


def test_dimensions_restricted_by_content_constraint():
    meta = EcbMetadata()
    assert "ICB" in meta.dataflow_constraints
    dims = {d["id"]: d for d in meta.get_dataflow_dimensions("ICB")}
    assert dims["FREQ"]["n_values"] == 1
    assert dims["FREQ"]["values"][0]["value"] == "Q"
    assert dims["REF_AREA"]["n_values"] < 50
    assert dims["REF_AREA"]["n_values"] < len(meta.get_codelist("CL_AREA"))
    assert all(v["label"] for v in dims["REF_AREA"]["values"])


def test_dimensions_unconstrained_uses_full_codelist(monkeypatch):
    meta = EcbMetadata()
    monkeypatch.setitem(meta.dataflow_constraints, "EXR", {})
    dims = {d["id"]: d for d in meta.get_dataflow_dimensions("EXR")}
    currency = dims["CURRENCY"]
    assert currency["n_values"] == len(meta.get_codelist(currency["codelist_id"]))


def test_concept_accessors(monkeypatch):
    meta = EcbMetadata()
    monkeypatch.setattr(meta, "portal_concepts", _FAKE_CONCEPTS)
    monkeypatch.setattr(meta, "dataflow_info", _FAKE_INFO)
    concepts = meta.list_concepts()
    bir = next(c for c in concepts if c["value"] == "bank-interest-rates")
    assert bir["datasets"] == ["MIR"] and bir["count"] == 1
    assert [c["name"] for c in concepts] == sorted(c["name"] for c in concepts)
    assert meta.get_concept("bank-interest-rates")["datasets"] == ["MIR"]
    with pytest.raises(OpenBBError):
        meta.get_concept("does-not-exist")
    info = meta.get_dataflow_info("MIR")
    assert info and info["fields"]
    assert meta.get_dataflow_info("NOPE_UNKNOWN") is None
    assert "Bank interest rates" in meta.concepts_for_dataflow("MIR")
