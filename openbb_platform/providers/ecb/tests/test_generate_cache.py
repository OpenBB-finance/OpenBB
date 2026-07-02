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
    '<str:Dataflow agencyID="ECB" id="NOSTRUCT" version="1.0"/>'
    "<str:Dataflow/>"
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
    "<str:DataStructure/>"
    "</str:DataStructures>"
)
CODELISTS = _doc(
    "<str:Codelists>"
    '<str:Codelist id="CL_FREQ">'
    '<str:Code id="D"><com:Name xml:lang="en">Daily</com:Name></str:Code>'
    '<str:Code id="X"/>'
    "<str:Code/>"
    "</str:Codelist>"
    "<str:Codelist/>"
    "</str:Codelists>"
)
CONCEPTS = _doc(
    "<str:Concepts>"
    '<str:ConceptScheme id="ECB_CONCEPTS">'
    '<str:Concept id="FREQ"><com:Name xml:lang="en">Frequency</com:Name></str:Concept>'
    "<str:Concept/>"
    "</str:ConceptScheme></str:Concepts>"
)
CATSCHEME = _doc(
    "<str:CategorySchemes>"
    '<str:CategoryScheme id="MOBILE_NAVI"><str:Category id="01">'
    '<com:Name xml:lang="en">Monetary</com:Name>'
    '<com:Description xml:lang="en">desc</com:Description>'
    '<str:Category id="0101"><com:Name xml:lang="en">Sub</com:Name></str:Category>'
    "</str:Category>"
    '<str:Category><com:Name xml:lang="en">NoId</com:Name></str:Category>'
    "</str:CategoryScheme></str:CategorySchemes>"
)
CATEGORISATION = _doc(
    "<str:Categorisations>"
    '<str:Categorisation><str:Source><Ref id="EXR" class="Dataflow"/></str:Source>'
    '<str:Target><Ref id="01"/></str:Target></str:Categorisation>'
    '<str:Categorisation><str:Source><Ref id="EXR" class="Dataflow"/></str:Source>'
    '<str:Target><Ref id="01"/></str:Target></str:Categorisation>'
    '<str:Categorisation><str:Source><Ref id="ECB_EXR1" class="DataStructure"/></str:Source>'
    '<str:Target><Ref id="01"/></str:Target></str:Categorisation>'
    '<str:Categorisation><str:Source><Ref class="Dataflow"/></str:Source>'
    '<str:Target><Ref id="01"/></str:Target></str:Categorisation>'
    "<str:Categorisation/>"
    "</str:Categorisations>"
)
CONTENT_CONSTRAINTS = _doc(
    "<str:Constraints>"
    '<str:ContentConstraint id="EXR_CONSTRAINTS">'
    '<str:ConstraintAttachment><str:Dataflow><Ref id="EXR" class="Dataflow"/>'
    "</str:Dataflow></str:ConstraintAttachment>"
    '<str:CubeRegion include="true">'
    '<com:KeyValue id="FREQ"><com:Value>D</com:Value><com:Value>M</com:Value></com:KeyValue>'
    '<com:KeyValue id="CURRENCY"><com:Value>USD</com:Value></com:KeyValue>'
    '<com:KeyValue id="EMPTY"></com:KeyValue>'
    "</str:CubeRegion></str:ContentConstraint>"
    '<str:ContentConstraint id="EXCLUDED">'
    '<str:ConstraintAttachment><str:Dataflow><Ref id="FOO" class="Dataflow"/>'
    "</str:Dataflow></str:ConstraintAttachment>"
    '<str:CubeRegion include="false">'
    '<com:KeyValue id="FREQ"><com:Value>D</com:Value></com:KeyValue>'
    "</str:CubeRegion></str:ContentConstraint>"
    '<str:ContentConstraint id="NOFLOW">'
    '<str:CubeRegion include="true">'
    '<com:KeyValue id="FREQ"><com:Value>D</com:Value></com:KeyValue>'
    "</str:CubeRegion></str:ContentConstraint>"
    '<str:ContentConstraint id="NOCUBE">'
    '<str:ConstraintAttachment><str:Dataflow><Ref id="BAR" class="Dataflow"/>'
    "</str:Dataflow></str:ConstraintAttachment></str:ContentConstraint>"
    '<str:ContentConstraint id="NOCODES">'
    '<str:ConstraintAttachment><str:Dataflow><Ref id="BAZ" class="Dataflow"/>'
    "</str:Dataflow></str:ConstraintAttachment>"
    '<str:CubeRegion include="true"><com:KeyValue id="X"></com:KeyValue>'
    "</str:CubeRegion></str:ContentConstraint>"
    "</str:Constraints>"
)

_PUB_TABLE_HTML = (
    "<html><head><title>Test Table | ECB Data Portal</title></head><body>"
    '<nav aria-label="breadcrumb"><ol>'
    '<li><a href="/">Home</a></li>'
    '<li><a href="/publications">Publications</a></li>'
    '<li><a href="/publications/money-credit-and-banking">Money, credit and banking</a></li>'
    '<li><a href="/publications/money-credit-and-banking/1">Monetary aggregates</a></li>'
    "<li><a>Browse data</a></li>"
    "</ol></nav>"
    '<script type="application/json" data-drupal-selector="drupal-settings-json">'
    '{"async_series_obs":{"series_keys":{'
    '"111":{"serieskey":"BSI.M.U2.X"},'
    '"112":{"serieskey":"BSI.M.U2.Y"},'
    '"113":{"serieskey":"BSI.M.U2.X"},'
    '"114":{"serieskey":"NODOT"},'
    '"115":"notadict"}}}'
    "</script></body></html>"
)
_PUB_CATEGORY_HTML = '<a href="/data/publications/TBL01">t</a>'

_DSET_INFO_HTML = (
    "<html><head><title>Exchange Rates - EXR | ECB Data Portal</title></head><body>"
    '<a href="/data/datasets/exr/download">CSV</a>'
    '<div class="dataset__field-m-dsetinfo-scope">'
    '<div class="field__label">Scope</div>'
    '<div class="field__item"><p>Summary <a href="/x">EXR</a>.</p><button>x</button>'
    "</div></div>"
    '<div class="dataset__field-m-dsetinfo-legal">'
    '<div class="field__label">Legal</div>'
    '<div class="field__item"><p>Regulation.</p></div></div>'
    '<div class="dataset__field-m-dsetinfo-empty">'
    '<div class="field__label">Empty</div><button>only</button></div>'
    "</body></html>"
)
_CONCEPTS_INDEX_HTML = (
    '<a href="/data/concepts/exchange-rates">x</a><a href="/data/concepts/loans">y</a>'
)
_CONCEPT_HTML = (
    "<html><head><title>Exchange rates | ECB Data Portal</title></head>"
    '<body><a href="/data/datasets/exr/">x</a></body></html>'
)


class _FakeResp:
    def __init__(self, status_code=200, content=b""):
        self.status_code = status_code
        self.content = content

    @property
    def text(self):
        return self.content.decode("utf-8")

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(str(self.status_code))


_HTML_ROUTES = (
    (("/data/concepts/", "data-information"), _CONCEPT_HTML),
    (("/data/concepts",), _CONCEPTS_INDEX_HTML),
    (("/data/datasets/", "data-information"), _DSET_INFO_HTML),
    (("/data/publications/",), _PUB_TABLE_HTML),
    (("/publications/",), _PUB_CATEGORY_HTML),
)
_XML_ROUTES = {
    "/data/BSI/": b"KEY,TIME_PERIOD,OBS_VALUE\nBSI.M.U2.X,2024-01,1.0\n",
    "/dataflow/": DATAFLOWS,
    "/datastructure/": DSDS,
    "/codelist/": CODELISTS,
    "/conceptscheme/": CONCEPTS,
    "/categoryscheme/": CATSCHEME,
    "/categorisation/": CATEGORISATION,
    "/contentconstraint/": CONTENT_CONSTRAINTS,
}


def _dispatch(url, **kwargs):
    for fragments, body in _HTML_ROUTES:
        if all(fragment in url for fragment in fragments):
            return _FakeResp(200, body.encode())
    for fragment, body in _XML_ROUTES.items():
        if fragment in url:
            return _FakeResp(200, body)
    return _FakeResp(404, b"")


@pytest.fixture
def _mock_session(monkeypatch):
    monkeypatch.setattr(gc._session, "get", _dispatch)
    monkeypatch.setattr(gc.time, "sleep", lambda *a, **k: None)


def test_get_success(_mock_session):
    assert gc._get(f"{gc.BASE_URL}/dataflow/ECB") is not None


def test_get_404_returns_none(monkeypatch):
    monkeypatch.setattr(gc._session, "get", lambda *a, **k: _FakeResp(404))
    assert gc._get("http://x") is None


def test_get_429_then_success(monkeypatch):
    monkeypatch.setattr(gc.time, "sleep", lambda *a, **k: None)
    seq = [_FakeResp(429), _FakeResp(200, DATAFLOWS)]
    monkeypatch.setattr(gc._session, "get", lambda *a, **k: seq.pop(0))
    assert gc._get("http://x") is not None


def test_get_retries_then_raises(monkeypatch):
    monkeypatch.setattr(gc.time, "sleep", lambda *a, **k: None)

    def _boom(*a, **k):
        raise requests.ConnectionError("down")

    monkeypatch.setattr(gc._session, "get", _boom)
    with pytest.raises(requests.RequestException):
        gc._get("http://x", retries=2)


def test_get_all_429_exhausts(monkeypatch):
    monkeypatch.setattr(gc.time, "sleep", lambda *a, **k: None)
    monkeypatch.setattr(gc._session, "get", lambda *a, **k: _FakeResp(429))
    with pytest.raises(requests.RequestException):
        gc._get("http://x", retries=2)


def test_en_helper():
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
    monkeypatch.setattr(gc._session, "get", lambda *a, **k: _FakeResp(404))
    monkeypatch.setattr(gc.time, "sleep", lambda *a, **k: None)
    assert gc.fetch_dataflows() == {}
    assert gc.fetch_datastructures() == {}
    assert gc.fetch_codelists() == {}
    assert gc.fetch_concepts() == {}
    assert gc.fetch_categories() == ({}, {}, {})
    assert gc.fetch_presentation_tables() == {}
    assert gc.fetch_content_constraints() == {}
    assert gc.fetch_dataflow_info(["X"]) == {}
    assert gc.fetch_portal_concepts(set()) == {}


def test_fetch_content_constraints(_mock_session):
    out = gc.fetch_content_constraints()
    assert out == {"EXR": {"FREQ": ["D", "M"], "CURRENCY": ["USD"]}}


def test_get_text_success(monkeypatch):
    monkeypatch.setattr(
        gc._session, "get", lambda *a, **k: _FakeResp(200, b"<p>hi</p>")
    )
    assert gc._get_text("http://x") == "<p>hi</p>"


def test_get_text_non_200(monkeypatch):
    monkeypatch.setattr(gc._session, "get", lambda *a, **k: _FakeResp(404))
    assert gc._get_text("http://x") == ""


def test_get_text_retry_then_success(monkeypatch):
    monkeypatch.setattr(gc.time, "sleep", lambda *a, **k: None)
    seq = [_FakeResp(503), _FakeResp(200, b"ok")]
    monkeypatch.setattr(gc._session, "get", lambda *a, **k: seq.pop(0))
    assert gc._get_text("http://x") == "ok"


def test_get_text_all_5xx(monkeypatch):
    monkeypatch.setattr(gc.time, "sleep", lambda *a, **k: None)
    monkeypatch.setattr(gc._session, "get", lambda *a, **k: _FakeResp(500))
    assert gc._get_text("http://x", retries=2) == ""


def test_get_text_request_error(monkeypatch):
    monkeypatch.setattr(gc.time, "sleep", lambda *a, **k: None)
    calls = {"n": 0}

    def _boom(*a, **k):
        calls["n"] += 1
        raise requests.ConnectionError("down")

    monkeypatch.setattr(gc._session, "get", _boom)
    assert gc._get_text("http://x", retries=2) == ""
    assert calls["n"] == 2


def test_clean_html():
    assert gc._clean_html("<b>Hi  there</b>\n<i>x</i>") == "Hi there x"


def test_crawl_publication_tree(monkeypatch):
    category_html = (
        '<a href="/data/publications/TBL01">t</a>'
        '<a href="/publications/money-credit-and-banking/1">a</a>'
        '<a href="/publications/empty-branch/9">e</a>'
    )
    pages = {f"/publications/{c}": category_html for c in gc.PUBLICATION_CATEGORIES}
    pages["/publications/money-credit-and-banking/1"] = (
        '<a href="/data/publications/TBL02">t</a>'
        '<a href="/publications/money-credit-and-banking/2">b</a>'
    )
    pages["/publications/money-credit-and-banking/2"] = (
        '<a href="/publications/money-credit-and-banking/1">a</a>'
    )
    monkeypatch.setattr(
        gc, "_get_text", lambda url: pages.get(url.replace(gc.PORTAL_URL, ""), "")
    )
    assert gc._crawl_publication_tree() == {"TBL01", "TBL02"}


_PARSE_PAGES = {
    "GOOD": _PUB_TABLE_HTML,
    "NOSCRIPT": "<title>X | ECB</title><p>no settings</p>",
    "BADJSON": '<script data-drupal-selector="drupal-settings-json">{bad</script>',
    "NOKEYS": '<script data-drupal-selector="drupal-settings-json">'
    '{"async_series_obs":{"series_keys":{}}}</script>',
    "NOTITLE": '<script data-drupal-selector="drupal-settings-json">'
    '{"async_series_obs":{"series_keys":{"1":{"serieskey":"X.a.b"}}}}</script>',
    "ONECRUMB": "<title>Solo | ECB</title>"
    '<nav aria-label="breadcrumb"><ol>'
    '<li><a href="/">Home</a></li>'
    '<li><a href="/publications">Publications</a></li>'
    '<li><a href="/publications/solo">Solo Category</a></li>'
    "<li><a>Browse data</a></li></ol></nav>"
    '<script data-drupal-selector="drupal-settings-json">'
    '{"async_series_obs":{"series_keys":{"1":{"serieskey":"X.a.b"}}}}</script>',
}


def test_parse_publication_table(monkeypatch):
    monkeypatch.setattr(
        gc, "_get_text", lambda url: _PARSE_PAGES.get(url.rsplit("/", 1)[-1], "")
    )
    good = gc._parse_publication_table("GOOD")
    assert good["title"] == "Test Table"
    assert good["category"] == "Money, credit and banking"
    assert good["subcategory"] == "Monetary aggregates"
    assert good["rows"] == [
        {"flow": "BSI", "key": "M.U2.X"},
        {"flow": "BSI", "key": "M.U2.Y"},
    ]
    assert gc._parse_publication_table("MISSING") is None
    assert gc._parse_publication_table("NOSCRIPT") is None
    assert gc._parse_publication_table("BADJSON") is None
    assert gc._parse_publication_table("NOKEYS") is None
    notitle = gc._parse_publication_table("NOTITLE")
    assert notitle["title"] == "NOTITLE"
    assert notitle["category"] == "" and notitle["subcategory"] == ""
    one = gc._parse_publication_table("ONECRUMB")
    assert one["category"] == "Solo Category" and one["subcategory"] == ""


def test_fetch_presentation_tables(_mock_session):
    tables = gc.fetch_presentation_tables()
    assert set(tables) == {"TBL01"}
    assert tables["TBL01"]["title"] == "Test Table"
    assert tables["TBL01"]["rows"][0] == {"flow": "BSI", "key": "M.U2.X"}


def test_fetch_presentation_tables_drops_unparsed(monkeypatch):
    monkeypatch.setattr(gc, "_crawl_publication_tree", lambda: {"A", "B"})
    monkeypatch.setattr(
        gc,
        "_parse_publication_table",
        lambda tid: {"id": tid, "rows": [1]} if tid == "A" else None,
    )
    assert set(gc.fetch_presentation_tables()) == {"A"}


def test_sanitize_dsetinfo():
    out = gc._sanitize_dsetinfo(
        '<button>x</button><p class="c">Hi <a href="/y">L</a></p>'
        '<span>z</span> <div class="'
    )
    assert out == '<p>Hi <a href="https://data.ecb.europa.eu/y">L</a></p>z'


def test_extract_dataset_info():
    info = gc._extract_dataset_info(_DSET_INFO_HTML)
    assert info["title"] == "Exchange Rates - EXR"
    assert [f["label"] for f in info["fields"]] == ["Scope", "Legal"]
    scope = info["fields"][0]["html"]
    assert scope == '<p>Summary <a href="https://data.ecb.europa.eu/x">EXR</a>.</p>'
    assert "<button" not in scope and "<div" not in scope
    assert info["catalogue"] == "https://data.ecb.europa.eu/data/datasets/exr/download"
    assert gc._extract_dataset_info("<html>nothing</html>") is None


def test_fetch_dataflow_info(monkeypatch):
    pages = {"EXR": _DSET_INFO_HTML, "EMPTY": "<html>no fields</html>"}

    def fake(url):
        flow = url.split("/data/datasets/")[1].split("/")[0].upper()
        return pages.get(flow, "")

    monkeypatch.setattr(gc, "_get_text", fake)
    out = gc.fetch_dataflow_info(["EXR", "EMPTY", "MISSING"])
    assert set(out) == {"EXR"}
    assert out["EXR"]["title"] == "Exchange Rates - EXR"
    assert [f["key"] for f in out["EXR"]["fields"]] == ["scope", "legal"]


def test_fetch_portal_concepts(monkeypatch):

    def fake(url):
        if url.endswith("/data/concepts"):
            return _CONCEPTS_INDEX_HTML
        if "/data/concepts/" in url:
            return _CONCEPT_HTML
        return ""

    monkeypatch.setattr(gc, "_get_text", fake)
    out = gc.fetch_portal_concepts({"EXR"})
    assert set(out) == {"exchange-rates", "loans"}
    assert out["exchange-rates"]["name"] == "Exchange rates"
    assert out["exchange-rates"]["datasets"] == ["EXR"]


def test_main_writes_cache(_mock_session, monkeypatch, tmp_path):
    monkeypatch.setattr(gc, "ASSETS_DIR", tmp_path)
    monkeypatch.setattr(gc, "CACHE_FILE", tmp_path / "ecb_cache.json.xz")
    gc.main()
    with lzma.open(tmp_path / "ecb_cache.json.xz", "rb") as file:
        blob = json.loads(file.read().decode("utf-8"))
    assert "EXR" in blob["dataflows"]
    assert blob["codelists"]["CL_FREQ"]["D"] == "Daily"
    assert blob["dataflow_categories"] == {"EXR": ["01"]}
    assert "TBL01" in blob["presentation_tables"]
    assert blob["row_labels"] == {}
    assert blob["dataflow_constraints"] == {
        "EXR": {"FREQ": ["D", "M"], "CURRENCY": ["USD"]}
    }
    assert "EXR" in blob["dataflow_info"]
    assert set(blob["portal_concepts"]) == {"exchange-rates", "loans"}


import xml.etree.ElementTree as ET

_HCL_DOC = _doc(
    "<str:Codelists>"
    '<str:Codelist id="OTHER"><str:Code id="z"/></str:Codelist>'
    '<str:Codelist id="JDF_ROW_LABELS">'
    '<str:Code id="80997156"><com:Name xml:lang="en">Total</com:Name></str:Code>'
    '<str:Code id="bad"/>'
    "<str:Code/>"
    "</str:Codelist>"
    "</str:Codelists>"
    "<str:HierarchicalCodelists>"
    '<str:HierarchicalCodelist id="HCL_JDF_XX@HCL_BSI">'
    '<com:Name xml:lang="en">Hierarchy</com:Name>'
    "<str:Hierarchy><str:HierarchicalCode>"
    "<str:Code>"
    '<Ref id="80997156" maintainableParentID="JDF_ROW_LABELS" agencyID="ECB.DISS"/>'
    "</str:Code>"
    "<str:HierarchicalCode>"
    '<str:Code><Ref id="A20" maintainableParentID="CL_BS_ITEM" agencyID="ECB"/></str:Code>'
    "</str:HierarchicalCode>"
    "</str:HierarchicalCode></str:Hierarchy>"
    "</str:HierarchicalCodelist>"
    '<str:HierarchicalCodelist id="NOAT"/>'
    '<str:HierarchicalCodelist id="EU_GROUPINGS@HCL_CG"><str:Hierarchy/>'
    "</str:HierarchicalCodelist>"
    "</str:HierarchicalCodelists>"
)

_CC_DOC = _doc(
    "<str:ContentConstraints><str:ContentConstraint>"
    "<str:ConstraintAttachment><str:Dataflow>"
    '<Ref id="JDF_XX"/>'
    "</str:Dataflow></str:ConstraintAttachment>"
    "<str:CubeRegion>"
    '<com:KeyValue id="ADJUSTMENT"><com:Value>N</com:Value><com:Value/></com:KeyValue>'
    '<com:KeyValue id="FREQ"><com:Value>M</com:Value></com:KeyValue>'
    '<com:KeyValue id="MATURITY"><com:Value>_T</com:Value></com:KeyValue>'
    '<com:KeyValue id="BS_ITEM"><com:Value>A20</com:Value></com:KeyValue>'
    "</str:CubeRegion>"
    "</str:ContentConstraint></str:ContentConstraints>"
)

_DSD_DIMS = [
    {"id": "FREQ", "codelist_id": "CL_FREQ"},
    {"id": "BS_ITEM", "codelist_id": "CL_BS_ITEM"},
    {"id": "MATURITY", "codelist_id": "CL_MAT"},
    {"id": "REF_AREA", "codelist_id": "CL_AREA"},
]
_KEYS_RECORDS = [
    {"FREQ": "M", "BS_ITEM": "A20", "MATURITY": "_T", "REF_AREA": "U2"},
    {"FREQ": "M", "BS_ITEM": "A30", "MATURITY": "M1", "REF_AREA": "U2"},
    {"FREQ": "Q", "BS_ITEM": "A20", "MATURITY": "_T", "REF_AREA": "DE"},
]


class _JsonResp:
    def __init__(self, status_code, payload):
        self.status_code = status_code
        self._payload = payload

    def json(self):
        if self._payload is None:
            raise ValueError("bad json")
        return self._payload


def test_context_score():
    assert gc._context_score(("U2", "M", "N"), ["REF_AREA", "FREQ", "ADJUSTMENT"]) == 16
    assert gc._context_score(("Q",), ["FREQ"]) == 3
    assert gc._context_score((None,), ["FREQ"]) == 0
    assert gc._context_score(("X",), ["OTHER"]) == 0


def test_fetch_jdf_tables(monkeypatch):
    monkeypatch.setattr(gc, "_get", lambda *a, **k: ET.fromstring(_HCL_DOC))
    tables, labels = gc.fetch_jdf_tables()
    assert labels["80997156"] == "Total"
    assert labels["bad"] == "bad"
    assert "NOAT" not in tables
    assert "EU_GROUPINGS@HCL_CG" not in tables
    table = tables["HCL_JDF_XX@HCL_BSI"]
    assert table["dataflow_id"] == "BSI"
    assert table["source"] == "jdf"
    root = table["tree"][0]
    assert root["code"] == "80997156"
    assert root["codelist_id"] == "JDF_ROW_LABELS"
    assert root["children"][0]["code"] == "A20"


def test_core_key():
    assert gc._core_key("HCL_JDF_MNA_A_GDP_GROWTH_QOQ@HCL_MNA") == (
        "HCL_JDF_MNA_GDP_GROWTH_QOQ"
    )
    assert gc._core_key("HCL_JDF_MNA_GDP_GROWTH_QOQ@HCL_MNA") == (
        "HCL_JDF_MNA_GDP_GROWTH_QOQ"
    )


def test_fetch_jdf_tables_none(monkeypatch):
    monkeypatch.setattr(gc, "_get", lambda *a, **k: None)
    assert gc.fetch_jdf_tables() == ({}, {})


def test_serieskeysonly_records(monkeypatch):
    message = {
        "dataSets": [{"series": {"0:0": {}, "1:0": {}, "0:0:9": {}, "0:5": {}}}],
        "structure": {
            "dimensions": {
                "series": [
                    {"id": "FREQ", "values": [{"id": "M"}, {"id": "Q"}]},
                    {"id": "AREA", "values": [{"id": "U2"}]},
                ]
            }
        },
    }
    monkeypatch.setattr(gc._session, "get", lambda *a, **k: _JsonResp(200, message))
    recs = gc._serieskeysonly_records("BSI", "M+Q..")
    assert {"FREQ": "M", "AREA": "U2"} in recs
    assert {"FREQ": "Q", "AREA": "U2"} in recs
    assert {"FREQ": "M"} in recs
    monkeypatch.setattr(gc._session, "get", lambda *a, **k: _JsonResp(404, None))
    assert gc._serieskeysonly_records("BSI", "x") == []
    monkeypatch.setattr(gc._session, "get", lambda *a, **k: _JsonResp(200, None))
    assert gc._serieskeysonly_records("BSI", "x") == []
    monkeypatch.setattr(
        gc._session, "get", lambda *a, **k: _JsonResp(200, {"dataSets": []})
    )
    assert gc._serieskeysonly_records("BSI", "x") == []

    def _raise(*a, **k):
        raise requests.RequestException("boom")

    monkeypatch.setattr(gc._session, "get", _raise)
    assert gc._serieskeysonly_records("BSI", "x") == []


def test_derive_table_context(monkeypatch):
    monkeypatch.setattr(
        gc, "_serieskeysonly_records", lambda df, key: list(_KEYS_RECORDS)
    )
    table = {
        "dataflow_id": "BSI",
        "tree": [
            {
                "code": "80997156",
                "codelist_id": "JDF_ROW_LABELS",
                "children": [
                    {"code": "A20", "codelist_id": "CL_BS_ITEM", "children": []},
                    {
                        "code": "A30",
                        "codelist_id": "CL_BS_ITEM",
                        "children": [
                            {"code": "M1", "codelist_id": "CL_MAT", "children": []}
                        ],
                    },
                ],
            }
        ],
    }
    valid, default, row_dims, records = gc._derive_table_context(table, _DSD_DIMS)
    assert default["FREQ"] == "M"
    assert default["REF_AREA"] == "U2"
    assert "BS_ITEM" not in default
    assert row_dims == {"BS_ITEM"}
    assert len(records) == 3
    assert "FREQ" in valid and "REF_AREA" in valid

    allowed = {"FREQ": ["M"], "BS_ITEM": ["A20", "A30"], "MATURITY": ["_T", "M1"]}
    constrained = gc._derive_table_context(table, _DSD_DIMS, allowed)
    assert constrained[1]["FREQ"] == "M"
    assert len(constrained[3]) == 2

    off_constraint = gc._derive_table_context(table, _DSD_DIMS, {"FREQ": ["W"]})
    assert len(off_constraint[3]) == 3

    assert gc._derive_table_context({"tree": [], "dataflow_id": "BSI"}, _DSD_DIMS) == (
        {},
        {},
        set(),
        [],
    )

    disjoint = {
        "dataflow_id": "BSI",
        "tree": [
            {"code": "A20", "codelist_id": "CL_BS_ITEM", "children": []},
            {"code": "M1", "codelist_id": "CL_MAT", "children": []},
        ],
    }
    assert gc._derive_table_context(disjoint, _DSD_DIMS)[1] is not None

    monkeypatch.setattr(gc, "_serieskeysonly_records", lambda df, key: [])
    assert gc._derive_table_context(table, _DSD_DIMS)[:2] == ({}, {})


def test_resolve_leaf_keys():
    table = {
        "tree": [
            {
                "code": "80997156",
                "codelist_id": "JDF_ROW_LABELS",
                "children": [
                    {"code": "A20", "codelist_id": "CL_BS_ITEM", "children": []},
                    {"code": "A99", "codelist_id": "CL_BS_ITEM", "children": []},
                ],
            }
        ]
    }
    candidate = {"FREQ": "M", "MATURITY": "_T", "REF_AREA": "U2"}
    keys = gc._resolve_leaf_keys(table, _DSD_DIMS, list(_KEYS_RECORDS), candidate)
    assert keys == [None, "M.A20._T.U2", None]


def test_fetch_table_contexts(monkeypatch):
    monkeypatch.setattr(
        gc,
        "_get",
        lambda url, *a, **k: (
            ET.fromstring(_CC_DOC) if "contentconstraint" in url else None
        ),
    )
    monkeypatch.setattr(
        gc, "_serieskeysonly_records", lambda df, key: list(_KEYS_RECORDS)
    )
    _tree = [
        {
            "code": "80997156",
            "codelist_id": "JDF_ROW_LABELS",
            "children": [
                {"code": "A20", "codelist_id": "CL_BS_ITEM", "children": []},
                {
                    "code": "A30",
                    "codelist_id": "CL_BS_ITEM",
                    "children": [
                        {"code": "M1", "codelist_id": "CL_MAT", "children": []}
                    ],
                },
            ],
        }
    ]
    tables = {
        "HCL_JDF_XX@HCL_BSI": {
            "id": "HCL_JDF_XX@HCL_BSI",
            "dataflow_id": "BSI",
            "tree": _tree,
        },
        "HCL_JDF_Z_XX@HCL_BSI": {
            "id": "HCL_JDF_Z_XX@HCL_BSI",
            "dataflow_id": "BSI",
            "tree": _tree,
        },
        "HCL_JDF_YY@HCL_BSI": {
            "id": "HCL_JDF_YY@HCL_BSI",
            "dataflow_id": "BSI",
            "tree": _tree,
        },
        "T@HCL_GONE": {"id": "T@HCL_GONE", "dataflow_id": "GONE", "tree": []},
        "T@HCL_ZZ": {"id": "T@HCL_ZZ", "dataflow_id": "ZZ", "tree": []},
        "T@HCL_BSI": {"id": "T@HCL_BSI", "dataflow_id": "BSI", "tree": []},
    }
    dataflows = {"BSI": {"dsd_id": "D1"}, "ZZ": {"dsd_id": "NOPE"}}
    datastructures = {"D1": {"dimensions": _DSD_DIMS}}
    derived = gc.fetch_table_contexts(tables, dataflows, datastructures)
    assert derived == 2
    assert "HCL_JDF_Z_XX@HCL_BSI" not in tables
    ctx = tables["HCL_JDF_XX@HCL_BSI"]
    assert "default_context" in ctx
    assert ctx["valid_context"]["ADJUSTMENT"] == ["N"]
    assert ctx["default_context"]["ADJUSTMENT"] == "N"
    assert ctx["leaf_keys"] == [None, "M.A20._T.U2", None, None]
    assert tables["HCL_JDF_YY@HCL_BSI"]["leaf_keys"] == [
        None,
        "M.A20._T.U2",
        "M.A30.M1.U2",
        "M.A30.M1.U2",
    ]
    assert "valid_context" not in tables["T@HCL_GONE"]


def test_fetch_jdf_constraints_none(monkeypatch):
    monkeypatch.setattr(gc, "_get", lambda *a, **k: None)
    assert gc.fetch_jdf_constraints({}) == {}


_CSV_RESP = b"KEY,TIME_PERIOD,OBS_VALUE\nBSI.M.U2.X,2024-01,1.0\nBSI.M.U2.Z,2024-01,\n"


def _csv_session(monkeypatch, status=200, content=_CSV_RESP, raise_exc=False):
    def _fake(url, **kwargs):
        if raise_exc:
            raise requests.RequestException("boom")
        return _FakeResp(status, content)

    monkeypatch.setattr(gc._session, "get", _fake)


def test_table_has_data(monkeypatch):
    table = {
        "rows": [{"flow": "BSI", "key": "M.U2.X"}, {"flow": "BSI", "key": "M.U2.Y"}]
    }
    _csv_session(monkeypatch)
    assert gc._table_has_data(table) is True
    _csv_session(
        monkeypatch, content=b"KEY,TIME_PERIOD,OBS_VALUE\nBSI.M.U2.Z,2024-01,2\n"
    )
    assert gc._table_has_data(table) is False
    _csv_session(
        monkeypatch, content=b"KEY,TIME_PERIOD,OBS_VALUE\nBSI.M.U2.X,2024-01,\n"
    )
    assert gc._table_has_data(table) is False
    _csv_session(monkeypatch, status=404)
    assert gc._table_has_data(table) is False
    _csv_session(monkeypatch, status=500)
    assert gc._table_has_data(table) is True
    _csv_session(monkeypatch, raise_exc=True)
    assert gc._table_has_data(table) is True
    assert gc._table_has_data({"rows": []}) is False


def test_prune_dead_tables(monkeypatch):
    tables = {
        "ALIVE": {"rows": [{"flow": "BSI", "key": "M.U2.X"}]},
        "DEAD": {"rows": [{"flow": "BSI", "key": "M.U2.Q"}]},
    }
    _csv_session(monkeypatch)
    gc.prune_dead_tables(tables)
    assert "ALIVE" in tables
    assert "DEAD" not in tables
