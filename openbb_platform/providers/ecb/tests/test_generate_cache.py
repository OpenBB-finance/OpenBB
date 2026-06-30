"""Unit tests for ``openbb_ecb.utils.generate_cache`` (mocked HTTP)."""

import json
import lzma

import pytest
import requests

from openbb_ecb.utils import generate_cache as gc

_NS = (
    'xmlns:mes="http://www.sdmx.org/resources/sdmxml/schemas/v2_1/message" '
    'xmlns:str="http://www.sdmx.org/resources/sdmxml/schemas/v2_1/structure" '
    'xmlns:com="http://www.sdmx.org/resources/sdmxml/schemas/v2_1/common"'
)


def _doc(body: str) -> bytes:
    return f"<mes:Structure {_NS}><mes:Structures>{body}</mes:Structures></mes:Structure>".encode()


DATAFLOWS = _doc(
    "<str:Dataflows>"
    '<str:Dataflow agencyID="ECB" id="EXR" version="1.0">'
    '<com:Name xml:lang="en">Exchange Rates</com:Name>'
    '<str:Structure><Ref agencyID="ECB" id="ECB_EXR1" version="1.0"/></str:Structure>'
    "</str:Dataflow>"
    '<str:Dataflow agencyID="ECB" id="NOSTRUCT" version="1.0"/>'  # no DSD ref
    "<str:Dataflow/>"  # no id -> skipped
    "</str:Dataflows>"
)
DSDS = _doc(
    "<str:DataStructures>"
    '<str:DataStructure agencyID="ECB" id="ECB_EXR1" version="1.0">'
    "<str:DataStructureComponents><str:DimensionList>"
    '<str:Dimension id="FREQ" position="1">'
    '<str:ConceptIdentity><Ref id="FREQ"/></str:ConceptIdentity>'
    '<str:LocalRepresentation><str:Enumeration><Ref id="CL_FREQ"/></str:Enumeration>'
    "</str:LocalRepresentation></str:Dimension>"
    '<str:TimeDimension id="TIME_PERIOD"/>'
    "</str:DimensionList><str:AttributeList>"
    '<str:Attribute id="UNIT"><str:ConceptIdentity><Ref id="UNIT"/></str:ConceptIdentity>'
    "</str:Attribute></str:AttributeList></str:DataStructureComponents>"
    "</str:DataStructure>"
    "<str:DataStructure/>"  # no id -> skipped
    "</str:DataStructures>"
)
CODELISTS = _doc(
    "<str:Codelists>"
    '<str:Codelist id="CL_FREQ">'
    '<str:Code id="D"><com:Name xml:lang="en">Daily</com:Name></str:Code>'
    '<str:Code id="X"/>'  # no name -> falls back to id
    "<str:Code/>"  # no id -> skipped
    "</str:Codelist>"
    "<str:Codelist/>"  # no id -> skipped
    "</str:Codelists>"
)
CONCEPTS = _doc(
    "<str:Concepts>"
    '<str:ConceptScheme id="ECB_CONCEPTS">'
    '<str:Concept id="FREQ"><com:Name xml:lang="en">Frequency</com:Name></str:Concept>'
    "<str:Concept/>"  # no id -> skipped
    "</str:ConceptScheme></str:Concepts>"
)
CATSCHEME = _doc(
    "<str:CategorySchemes>"
    '<str:CategoryScheme id="MOBILE_NAVI"><str:Category id="01">'
    '<com:Name xml:lang="en">Monetary</com:Name>'
    '<com:Description xml:lang="en">desc</com:Description>'
    '<str:Category id="0101"><com:Name xml:lang="en">Sub</com:Name></str:Category>'
    "</str:Category>"
    '<str:Category><com:Name xml:lang="en">NoId</com:Name></str:Category>'  # no id
    "</str:CategoryScheme></str:CategorySchemes>"
)
CATEGORISATION = _doc(
    "<str:Categorisations>"
    '<str:Categorisation><str:Source><Ref id="EXR" class="Dataflow"/></str:Source>'
    '<str:Target><Ref id="01"/></str:Target></str:Categorisation>'
    '<str:Categorisation><str:Source><Ref id="EXR" class="Dataflow"/></str:Source>'
    '<str:Target><Ref id="01"/></str:Target></str:Categorisation>'  # duplicate -> deduped
    '<str:Categorisation><str:Source><Ref id="ECB_EXR1" class="DataStructure"/></str:Source>'
    '<str:Target><Ref id="01"/></str:Target></str:Categorisation>'  # not a Dataflow
    '<str:Categorisation><str:Source><Ref class="Dataflow"/></str:Source>'
    '<str:Target><Ref id="01"/></str:Target></str:Categorisation>'  # source has no id
    "<str:Categorisation/>"  # no source/target -> skipped
    "</str:Categorisations>"
)


HCLS = _doc(
    "<str:Codelists>"
    '<str:Codelist id="JDF_ROW_LABELS">'
    '<str:Code id="L1"><com:Name xml:lang="en">Assets</com:Name></str:Code>'
    "<str:Code/>"  # no id -> skipped
    "</str:Codelist>"
    '<str:Codelist id="OTHER"/>'  # not JDF_ROW_LABELS -> ignored
    "</str:Codelists>"
    "<str:HierarchicalCodelists>"
    '<str:HierarchicalCodelist agencyID="ECB.DISS" id="HCL_JDF_EXR_HCI_CPI@HCL_EXR">'
    '<com:Name xml:lang="en">Hierarchy for the HCL_JDF_EXR_HCI_CPI dataflow</com:Name>'
    '<str:Hierarchy><str:HierarchicalCode id="1">'
    '<str:Code><Ref maintainableParentID="JDF_ROW_LABELS" agencyID="ECB.DISS" id="L1"/></str:Code>'
    '<str:HierarchicalCode id="2">'
    '<str:Code><Ref maintainableParentID="CL_FREQ" agencyID="ECB" id="D"/></str:Code>'
    "</str:HierarchicalCode>"
    "</str:HierarchicalCode>"
    '<str:HierarchicalCode id="3"/>'  # no Code ref -> None fields
    "</str:Hierarchy>"
    "</str:HierarchicalCodelist>"
    '<str:HierarchicalCodelist agencyID="ECB.DISS" id="NO_SUFFIX">'  # no @HCL_ -> skipped
    '<com:Name xml:lang="en">skip</com:Name></str:HierarchicalCodelist>'
    '<str:HierarchicalCodelist agencyID="ECB.DISS" id="HCL_JDF_NOHIER@HCL_EXR">'  # no Hierarchy
    '<com:Name xml:lang="en">empty</com:Name></str:HierarchicalCodelist>'
    "<str:HierarchicalCodelist/>"  # no id -> skipped
    "</str:HierarchicalCodelists>"
)
CONTENT_CONSTRAINTS = _doc(
    "<str:Constraints>"
    '<str:ContentConstraint id="EXR_CONSTRAINTS">'
    '<str:ConstraintAttachment><str:Dataflow><Ref id="EXR" class="Dataflow"/>'
    "</str:Dataflow></str:ConstraintAttachment>"
    '<str:CubeRegion include="true">'
    '<com:KeyValue id="FREQ"><com:Value>D</com:Value><com:Value>M</com:Value></com:KeyValue>'
    '<com:KeyValue id="CURRENCY"><com:Value>USD</com:Value></com:KeyValue>'
    '<com:KeyValue id="EMPTY"></com:KeyValue>'  # no values -> skipped
    "</str:CubeRegion></str:ContentConstraint>"
    '<str:ContentConstraint id="EXCLUDED">'  # include=false -> skipped
    '<str:ConstraintAttachment><str:Dataflow><Ref id="FOO" class="Dataflow"/>'
    "</str:Dataflow></str:ConstraintAttachment>"
    '<str:CubeRegion include="false">'
    '<com:KeyValue id="FREQ"><com:Value>D</com:Value></com:KeyValue>'
    "</str:CubeRegion></str:ContentConstraint>"
    '<str:ContentConstraint id="NOFLOW">'  # no dataflow ref -> skipped
    '<str:CubeRegion include="true">'
    '<com:KeyValue id="FREQ"><com:Value>D</com:Value></com:KeyValue>'
    "</str:CubeRegion></str:ContentConstraint>"
    '<str:ContentConstraint id="NOCUBE">'  # no CubeRegion -> skipped
    '<str:ConstraintAttachment><str:Dataflow><Ref id="BAR" class="Dataflow"/>'
    "</str:Dataflow></str:ConstraintAttachment></str:ContentConstraint>"
    '<str:ContentConstraint id="NOCODES">'  # cube with no usable codes -> skipped
    '<str:ConstraintAttachment><str:Dataflow><Ref id="BAZ" class="Dataflow"/>'
    "</str:Dataflow></str:ConstraintAttachment>"
    '<str:CubeRegion include="true"><com:KeyValue id="X"></com:KeyValue>'
    "</str:CubeRegion></str:ContentConstraint>"
    "</str:Constraints>"
)


class _FakeResp:
    def __init__(self, status_code=200, content=b""):
        self.status_code = status_code
        self.content = content

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(str(self.status_code))


class _FakeJsonResp:
    def __init__(self, status_code=200, payload=None):
        self.status_code = status_code
        self._payload = payload if payload is not None else {}

    def json(self):
        return self._payload


# A small table: ITEM is the row dim (every leaf); SECTOR and MATURITY are partial
# (each pinned by one leaf, so the others need an aggregate); AREA is the context
# slice. The optimal slice (SECTOR=T, MATURITY=A) fills both partial rows but is
# split across two series, so only coordinate-ascent finds it.
_TABLE_DSD = [
    {"id": "ITEM", "codelist_id": "CL_ITEM"},
    {"id": "SECTOR", "codelist_id": "CL_SEC"},
    {"id": "MATURITY", "codelist_id": "CL_MAT"},
    {"id": "AREA", "codelist_id": "CL_AREA"},
]
_TABLE = {
    "dataflow_id": "TST",
    "tree": [
        {
            "code": "A20",
            "codelist_id": "CL_ITEM",
            "children": [
                {"code": "1000", "codelist_id": "CL_SEC", "children": []},
                {"code": "D", "codelist_id": "CL_MAT", "children": []},
            ],
        },
        {"code": "A21", "codelist_id": "CL_ITEM", "children": []},
        # A pure row-label leaf (no dimension code) is not a data row.
        {"code": "L0", "codelist_id": "JDF_ROW_LABELS", "children": []},
    ],
}
_TABLE_SERIESKEYS = {
    "dataSets": [
        {"series": {"0:0:0:0": {}, "0:1:1:0": {}, "0:0:0:1": {}, "0:0:2:2": {}}}
    ],
    "structure": {
        "dimensions": {
            "series": [
                {"id": "ITEM", "values": [{"id": "A20"}, {"id": "A21"}]},
                {"id": "SECTOR", "values": [{"id": "1000"}, {"id": "T"}]},
                {"id": "MATURITY", "values": [{"id": "A"}, {"id": "D"}, {"id": "K"}]},
                {"id": "AREA", "values": [{"id": "U2"}, {"id": "US"}, {"id": "ZZ"}]},
            ]
        }
    },
}


def _dispatch(url, **kwargs):
    table = {
        "/dataflow/": DATAFLOWS,
        "/datastructure/": DSDS,
        "/codelist/": CODELISTS,
        "/conceptscheme/": CONCEPTS,
        "/categoryscheme/": CATSCHEME,
        "/categorisation/": CATEGORISATION,
        "/hierarchicalcodelist/": HCLS,
        "/contentconstraint/": CONTENT_CONSTRAINTS,
    }
    for fragment, body in table.items():
        if fragment in url:
            return _FakeResp(200, body)
    return _FakeResp(404, b"")


@pytest.fixture
def _mock_session(monkeypatch):
    monkeypatch.setattr(gc._session, "get", _dispatch)
    monkeypatch.setattr(gc.time, "sleep", lambda *a, **k: None)
    # serieskeysonly (per-table context derivation) goes through requests.get.
    monkeypatch.setattr(gc.requests, "get", lambda *a, **k: _FakeJsonResp(404, {}))


def test_get_success(_mock_session):
    """A 200 returns a parsed element."""
    assert gc._get(f"{gc.BASE_URL}/dataflow/ECB") is not None


def test_get_404_returns_none(monkeypatch):
    """A 404 returns None without raising."""
    monkeypatch.setattr(gc._session, "get", lambda *a, **k: _FakeResp(404))
    assert gc._get("http://x") is None


def test_get_429_then_success(monkeypatch):
    """A 429 retries, then succeeds."""
    monkeypatch.setattr(gc.time, "sleep", lambda *a, **k: None)
    seq = [_FakeResp(429), _FakeResp(200, DATAFLOWS)]
    monkeypatch.setattr(gc._session, "get", lambda *a, **k: seq.pop(0))
    assert gc._get("http://x") is not None


def test_get_retries_then_raises(monkeypatch):
    """Persistent request errors raise after exhausting retries."""
    monkeypatch.setattr(gc.time, "sleep", lambda *a, **k: None)

    def _boom(*a, **k):
        raise requests.ConnectionError("down")

    monkeypatch.setattr(gc._session, "get", _boom)
    with pytest.raises(requests.RequestException):
        gc._get("http://x", retries=2)


def test_get_all_429_exhausts(monkeypatch):
    """Continuous 429s exhaust the retries and raise."""
    monkeypatch.setattr(gc.time, "sleep", lambda *a, **k: None)
    monkeypatch.setattr(gc._session, "get", lambda *a, **k: _FakeResp(429))
    with pytest.raises(requests.RequestException):
        gc._get("http://x", retries=2)


def test_en_helper():
    """``_en`` returns '' for None and prefers the English text."""
    import xml.etree.ElementTree as ET

    assert gc._en(None, "Name") == ""
    elem = ET.fromstring(
        f"<root {_NS}>"
        '<com:Name xml:lang="fr">Bonjour</com:Name>'
        '<com:Name xml:lang="en">Hello</com:Name></root>'
    )
    assert gc._en(elem, "Name") == "Hello"
    only_fr = ET.fromstring(
        f'<root {_NS}><com:Name xml:lang="fr">Bonjour</com:Name></root>'
    )
    assert gc._en(only_fr, "Name") == "Bonjour"


def test_fetch_functions(_mock_session):
    """Each fetch_* parser produces the expected catalog pieces."""
    dataflows = gc.fetch_dataflows()
    assert dataflows["EXR"]["dsd_id"] == "ECB_EXR1"
    assert dataflows["NOSTRUCT"]["dsd_id"] is None

    dsds = gc.fetch_datastructures()
    assert dsds["ECB_EXR1"]["dimensions"][0]["codelist_id"] == "CL_FREQ"
    assert dsds["ECB_EXR1"]["time_dimension"] == {"id": "TIME_PERIOD"}

    codelists = gc.fetch_codelists()
    assert codelists["CL_FREQ"] == {"D": "Daily", "X": "X"}

    concepts = gc.fetch_concepts()
    assert concepts["FREQ"] == "Frequency"

    categories, df_to_cat, cat_to_df = gc.fetch_categories()
    assert categories["01"]["name"] == "Monetary"
    assert categories["0101"]["name"] == "Sub"
    assert df_to_cat == {"EXR": ["01"]}
    assert cat_to_df == {"01": ["EXR"]}


def test_fetch_functions_empty(monkeypatch):
    """When the API yields nothing the parsers return empties."""
    monkeypatch.setattr(gc._session, "get", lambda *a, **k: _FakeResp(404))
    assert gc.fetch_dataflows() == {}
    assert gc.fetch_datastructures() == {}
    assert gc.fetch_codelists() == {}
    assert gc.fetch_concepts() == {}
    assert gc.fetch_categories() == ({}, {}, {})
    assert gc.fetch_presentation_tables() == ({}, {})
    assert gc.fetch_content_constraints() == {}


def test_fetch_content_constraints(_mock_session):
    """Content-constraint CubeRegions parse into per-dataflow allowed codes."""
    out = gc.fetch_content_constraints()
    # Only the included cube with a dataflow ref and real codes is kept.
    assert out == {"EXR": {"FREQ": ["D", "M"], "CURRENCY": ["USD"]}}


def test_fetch_presentation_tables(_mock_session):
    """Presentation-table HCLs parse into trees mapped to their dataflow."""
    tables, row_labels = gc.fetch_presentation_tables()
    assert row_labels == {"L1": "Assets"}

    table = tables["HCL_JDF_EXR_HCI_CPI@HCL_EXR"]
    assert table["dataflow_id"] == "EXR"
    node = table["tree"][0]
    assert node["code"] == "L1"
    assert node["codelist_id"] == "JDF_ROW_LABELS"
    assert node["agency"] == "ECB.DISS"
    child = node["children"][0]
    assert (child["code"], child["codelist_id"], child["agency"]) == (
        "D",
        "CL_FREQ",
        "ECB",
    )
    # A HierarchicalCode with no Code ref yields None fields.
    assert table["tree"][1]["code"] is None
    # No <Hierarchy> -> empty tree; no "@HCL_" -> skipped; no id -> skipped.
    assert tables["HCL_JDF_NOHIER@HCL_EXR"]["tree"] == []
    assert "NO_SUFFIX" not in tables


def test_main_writes_cache(_mock_session, monkeypatch, tmp_path):
    """``main`` assembles and writes a compressed cache blob."""
    monkeypatch.setattr(gc, "ASSETS_DIR", tmp_path)
    monkeypatch.setattr(gc, "CACHE_FILE", tmp_path / "ecb_cache.json.xz")
    gc.main()
    with lzma.open(tmp_path / "ecb_cache.json.xz", "rb") as file:
        blob = json.loads(file.read().decode("utf-8"))
    assert "EXR" in blob["dataflows"]
    assert blob["codelists"]["CL_FREQ"]["D"] == "Daily"
    assert blob["dataflow_categories"] == {"EXR": ["01"]}
    assert "HCL_JDF_EXR_HCI_CPI@HCL_EXR" in blob["presentation_tables"]
    assert blob["row_labels"] == {"L1": "Assets"}
    assert blob["dataflow_constraints"] == {
        "EXR": {"FREQ": ["D", "M"], "CURRENCY": ["USD"]}
    }


def test_serieskeysonly_records(monkeypatch):
    """serieskeysonly jsondata parses to one ``{dim: code}`` per series."""
    edge = {
        "dataSets": [{"series": {"0:0:0:0:9": {}, "0:9:0:0": {}}}],
        "structure": {
            "dimensions": {
                "series": [
                    {"id": "FREQ", "values": [{"id": "M"}]},
                    {"id": "ITEM", "values": [{"id": "A20"}]},
                    {"id": "SECTOR", "values": [{"id": "1000"}]},
                    {"id": "AREA", "values": [{"id": "U2"}]},
                ]
            }
        },
    }
    monkeypatch.setattr(gc.requests, "get", lambda *a, **k: _FakeJsonResp(200, edge))
    records = gc._serieskeysonly_records("TST", ".A20.1000.")
    # extra index breaks; out-of-range ITEM index is skipped.
    assert records == [
        {"FREQ": "M", "ITEM": "A20", "SECTOR": "1000", "AREA": "U2"},
        {"FREQ": "M", "SECTOR": "1000", "AREA": "U2"},
    ]


def test_serieskeysonly_records_failures(monkeypatch):
    """Non-200, request errors, bad JSON and empty datasets all return []."""
    monkeypatch.setattr(gc.requests, "get", lambda *a, **k: _FakeJsonResp(404, {}))
    assert gc._serieskeysonly_records("T", ".") == []

    def _boom(*a, **k):
        raise requests.ConnectionError("down")

    monkeypatch.setattr(gc.requests, "get", _boom)
    assert gc._serieskeysonly_records("T", ".") == []

    class _BadJson:
        status_code = 200

        def json(self):
            raise ValueError("bad")

    monkeypatch.setattr(gc.requests, "get", lambda *a, **k: _BadJson())
    assert gc._serieskeysonly_records("T", ".") == []

    monkeypatch.setattr(
        gc.requests, "get", lambda *a, **k: _FakeJsonResp(200, {"dataSets": []})
    )
    assert gc._serieskeysonly_records("T", ".") == []


def test_context_score():
    """Euro-area / monthly / unadjusted slices score higher; None is skipped."""
    high = gc._context_score(("U2", "M", "N"), ["REF_AREA", "FREQ", "ADJUSTMENT"])
    low = gc._context_score(("US", "A", "Y"), ["REF_AREA", "FREQ", "ADJUSTMENT"])
    assert high > low
    assert gc._context_score((None,), ["FREQ"]) == 0


def test_derive_table_context(monkeypatch):
    """Row/partial dims classify; the slice + partial aggregate maximize coverage."""
    monkeypatch.setattr(
        gc.requests, "get", lambda *a, **k: _FakeJsonResp(200, _TABLE_SERIESKEYS)
    )
    valid, default = gc._derive_table_context(_TABLE, _TABLE_DSD)
    # Coordinate-ascent finds SECTOR=T + MATURITY=A (filling both partial rows);
    # AREA stays U2. ZZ fills nothing so it is dropped from the valid slice.
    assert default == {"SECTOR": "T", "MATURITY": "A", "AREA": "U2"}
    assert valid == {"AREA": ["U2", "US"]}


def test_derive_table_context_empty(monkeypatch):
    """No hierarchy, or no series returned, yields empty context."""
    assert gc._derive_table_context({"dataflow_id": "T", "tree": []}, _TABLE_DSD) == (
        {},
        {},
    )
    monkeypatch.setattr(gc.requests, "get", lambda *a, **k: _FakeJsonResp(404, {}))
    assert gc._derive_table_context(_TABLE, _TABLE_DSD) == ({}, {})


def test_fetch_table_contexts(monkeypatch):
    """Heuristic resolves rows; the content constraint overrides context dims."""
    monkeypatch.setattr(
        gc.requests, "get", lambda *a, **k: _FakeJsonResp(200, _TABLE_SERIESKEYS)
    )

    def _run(area_values):
        monkeypatch.setattr(
            gc,
            "fetch_jdf_constraints",
            lambda tables: {
                "HCL_JDF_TST@HCL_T": {"AREA": area_values, "ITEM": ["A20"], "EMPTY": []}
            },
        )
        tbls = {"T": {**_TABLE, "id": "HCL_JDF_TST@HCL_T"}}
        gc.fetch_table_contexts(
            tbls, {"TST": {"dsd_id": "D1"}}, {"D1": {"dimensions": _TABLE_DSD}}
        )
        return tbls["T"]

    # Row/partial dims stay from the heuristic; AREA (a context dim) is overridden
    # by the constraint, while ITEM (a tree dim) and EMPTY (no values) are ignored.
    over = _run(["US"])
    assert over["default_context"]["SECTOR"] == "T"
    assert over["valid_context"]["AREA"] == ["US"]
    assert over["default_context"]["AREA"] == "US"
    # A heuristic default that is already valid under the constraint is kept.
    assert _run(["U2", "US"])["default_context"]["AREA"] == "U2"

    monkeypatch.setattr(gc, "fetch_jdf_constraints", lambda tables: {})
    # A table with no matching constraint keeps the heuristic context unchanged.
    plain = {"P": {**_TABLE, "id": "HCL_OTHER@HCL_X"}}
    assert (
        gc.fetch_table_contexts(
            plain, {"TST": {"dsd_id": "D1"}}, {"D1": {"dimensions": _TABLE_DSD}}
        )
        == 1
    )
    assert plain["P"]["valid_context"] == {"AREA": ["U2", "US"]}
    # Missing dataflow / DSD, or an empty hierarchy, is skipped.
    assert (
        gc.fetch_table_contexts({"X": {"dataflow_id": "NONE", "tree": []}}, {}, {}) == 0
    )
    assert (
        gc.fetch_table_contexts(
            {"Y": {"dataflow_id": "TST", "tree": []}}, {"TST": {"dsd_id": "MISS"}}, {}
        )
        == 0
    )
    assert (
        gc.fetch_table_contexts(
            {"Z": {"dataflow_id": "TST", "tree": []}},
            {"TST": {"dsd_id": "D1"}},
            {"D1": {"dimensions": _TABLE_DSD}},
        )
        == 0
    )


def test_fetch_jdf_constraints(monkeypatch):
    """Per-table content constraints parse into {table_id: {dim: values}}."""
    monkeypatch.setattr(
        gc._session, "get", lambda *a, **k: _FakeResp(200, CONTENT_CONSTRAINTS)
    )
    # The fixture's EXR constraint attaches to dataflow 'EXR' -> the table whose
    # id core (after 'HCL_') is 'EXR'. Empty-valued dims are dropped.
    out = gc.fetch_jdf_constraints({"HCL_EXR@HCL_X": {}})
    assert out == {"HCL_EXR@HCL_X": {"CURRENCY": ["USD"], "FREQ": ["D", "M"]}}
    # A DataKeySet with a blank <Value/> drops that dimension (empty-value branch).
    blank = _doc(
        '<str:Constraints><str:ContentConstraint id="C">'
        '<str:ConstraintAttachment><str:Dataflow><Ref id="EXR" class="Dataflow"/>'
        "</str:Dataflow></str:ConstraintAttachment><str:DataKeySet><str:Key>"
        '<str:KeyValue id="FREQ"><str:Value>A</str:Value></str:KeyValue>'
        '<str:KeyValue id="REF_AREA"><str:Value></str:Value></str:KeyValue>'
        "</str:Key></str:DataKeySet></str:ContentConstraint></str:Constraints>"
    )
    monkeypatch.setattr(gc._session, "get", lambda *a, **k: _FakeResp(200, blank))
    assert gc.fetch_jdf_constraints({"HCL_EXR@HCL_X": {}}) == {
        "HCL_EXR@HCL_X": {"FREQ": ["A"]}
    }
    # No structures -> empty.
    monkeypatch.setattr(gc._session, "get", lambda *a, **k: _FakeResp(404))
    assert gc.fetch_jdf_constraints({"HCL_EXR@HCL_X": {}}) == {}
