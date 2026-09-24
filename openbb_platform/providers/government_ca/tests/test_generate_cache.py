"""Government of Canada catalog generator tests."""

import contextlib
import importlib
import json
import lzma
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from unittest import mock

import pytest
import requests
import yaml
from hypothesis import (
    given,
    settings,
    strategies as st,
)

generate_cache = importlib.import_module("openbb_government_ca.utils.generate_cache")

# A valid PID is exactly 8 numeric digits.
_valid_pid = st.text(alphabet="0123456789", min_size=8, max_size=8)
# Numeric strings of the wrong length must be discarded.
_wrong_length = st.text(alphabet="0123456789", min_size=1, max_size=15).filter(
    lambda s: len(s) != 8
)
# Non-numeric strings (including 8-char ones with letters) must be discarded.
_non_numeric = st.text(min_size=1, max_size=10).filter(
    lambda s: not (len(s) == 8 and s.isdigit())
)
_source_value = st.one_of(_valid_pid, _wrong_length, _non_numeric)


@st.composite
def _ind_econ_payloads(draw):
    """Build an ``ind-econ.json``-shaped payload with a mix of sources.

    A small pool of candidate ``source`` values is drawn first, then a longer
    sequence is sampled from that pool so duplicates occur naturally.
    """
    pool = draw(st.lists(_source_value, min_size=1, max_size=8))
    sequence = draw(st.lists(st.sampled_from(pool), min_size=0, max_size=30))
    indicators = [{"source": value} for value in sequence]
    return {"results": {"indicators": indicators}}


# Feature: government-ca-build-phase-1, Property 1
@settings(max_examples=200)
@given(_ind_econ_payloads())
def test_derive_pids_filtered_deduped_order_preserving(payload):
    """Property 1: PID derivation is filtered, deduped, and order-preserving.

    For any mix of valid 8-digit numeric strings, wrong-length strings,
    non-numeric strings, and duplicates, ``derive_pids`` returns a list in
    which every element is exactly 8 numeric digits, no value appears more than
    once, and the surviving values appear in first-seen input order.

    Validates: Requirements 4.1
    """
    sources = [indicator["source"] for indicator in payload["results"]["indicators"]]
    result = generate_cache.derive_pids(payload)

    # (1) Every returned element is exactly 8 numeric digits.
    assert all(len(pid) == 8 and pid.isdigit() for pid in result)

    # (2) No value appears more than once.
    assert len(result) == len(set(result))

    # (3) Surviving values preserve first-seen order from the input.
    expected: list[str] = []
    seen: set[str] = set()
    for source in sources:
        if len(source) == 8 and source.isdigit() and source not in seen:
            seen.add(source)
            expected.append(source)
    assert result == expected


class _FakeResponse:
    """Minimal stand-in for a ``requests.Response`` success body."""

    def __init__(self, text: str, status_code: int = 200) -> None:
        self.text = text
        self.status_code = status_code


def _make_session(failures: list, success_body: str):
    """Build a fake session whose ``get`` raises then succeeds.

    The first ``len(failures)`` calls raise the queued transient exceptions
    (connection errors / timeouts); every subsequent call returns a successful
    response carrying ``success_body``.
    """
    queue = list(failures)
    calls = {"count": 0}

    def _get(url, headers=None, timeout=None):  # noqa: ARG001
        calls["count"] += 1
        if queue:
            raise queue.pop(0)
        return _FakeResponse(success_body)

    session = mock.Mock()
    session.get.side_effect = _get
    return session, calls


# Transient failure types treated as retryable by the generator.
_transient = st.sampled_from(
    [requests.ConnectionError("connect failed"), requests.Timeout("timed out")]
)


@st.composite
def _retry_scenarios(draw):
    """Draw a count of leading transient failures plus their types.

    ``num_failures`` spans 0 through ``MAX_ATTEMPTS`` (inclusive) so both the
    success-within-budget path and the exhausted-budget path are exercised.
    """
    num_failures = draw(st.integers(min_value=0, max_value=generate_cache.MAX_ATTEMPTS))
    failures = draw(st.lists(_transient, min_size=num_failures, max_size=num_failures))
    return num_failures, failures


# Feature: government-ca-build-phase-1, Property 10
@settings(max_examples=200)
@given(_retry_scenarios(), st.text(alphabet="0123456789", min_size=8, max_size=8))
def test_fetch_structure_retry_budget_and_abort(scenario, pid):
    """Property 10: Retry/backoff succeeds within budget and aborts when exhausted.

    For any sequence of leading transient failures (connection errors,
    timeouts) followed by a success, ``fetch_structure`` returns the successful
    body using at most ``MAX_ATTEMPTS`` attempts when the failures are fewer
    than ``MAX_ATTEMPTS``, and raises an error identifying the PID and reason
    when ``MAX_ATTEMPTS`` attempts are exhausted; attempts never exceed
    ``MAX_ATTEMPTS``.

    Validates: Requirements 4.4, 4.5
    """
    num_failures, failures = scenario
    success_body = "<Structure/>"
    session, calls = _make_session(failures, success_body)

    # Patch backoff sleeps so the test runs without real delays.
    with mock.patch.object(generate_cache.time, "sleep") as sleep_mock:
        if num_failures < generate_cache.MAX_ATTEMPTS:
            # Success-within-budget path.
            result = generate_cache.fetch_structure(session, pid)
            assert result == success_body
            assert calls["count"] == num_failures + 1
        else:
            # Exhausted-budget path: error identifies the PID and the reason.
            with pytest.raises(RuntimeError) as excinfo:
                generate_cache.fetch_structure(session, pid)
            message = str(excinfo.value)
            assert pid in message
            assert str(generate_cache.MAX_ATTEMPTS) in message
            assert calls["count"] == generate_cache.MAX_ATTEMPTS

        # Attempts never exceed the retry budget.
        assert calls["count"] <= generate_cache.MAX_ATTEMPTS
        # Backoff is bounded by attempts - 1 and never sleeps after success.
        assert sleep_mock.call_count <= generate_cache.MAX_ATTEMPTS - 1


def _make_error_session(status_code: int):
    """Build a fake session whose ``get`` always returns ``status_code``.

    Every call returns a non-success response (HTTP >= 400), so the generator
    retries to exhaustion and then aborts.
    """
    calls = {"count": 0}

    def _get(url, headers=None, timeout=None):  # noqa: ARG001
        calls["count"] += 1
        return _FakeResponse("error body", status_code=status_code)

    session = mock.Mock()
    session.get.side_effect = _get
    return session, calls


# Non-success HTTP status codes span the full >= 400 range.
_http_error_status = st.integers(min_value=400, max_value=599)


# Feature: government-ca-build-phase-1, Property 11
@settings(max_examples=100)
@given(_http_error_status, st.text(alphabet="0123456789", min_size=8, max_size=8))
def test_non_success_status_aborts_run(status_code, pid):
    """Property 11: Non-success HTTP status aborts the run.

    For any HTTP status code of 400 or greater returned for a structure fetch,
    the Catalog_Generator raises an error that identifies the failing fetch and
    the status code and writes no catalog asset.

    Validates: Requirements 11.6
    """
    session, calls = _make_error_session(status_code)

    with tempfile.TemporaryDirectory() as tmp:
        cache_file = Path(tmp) / "government_ca_cache.json.xz"
        with (
            mock.patch.object(generate_cache.time, "sleep"),
            mock.patch.object(generate_cache, "CACHE_FILE", cache_file),
        ):
            # (a) The generator raises rather than returning a body.
            with pytest.raises(RuntimeError) as excinfo:
                generate_cache.fetch_structure(session, pid)

            message = str(excinfo.value)
            # (b) The error identifies the failing fetch and the status code.
            assert pid in message
            assert "Data_Structure" in message
            assert str(status_code) in message
            # (c) No catalog asset is written.
            assert not cache_file.exists()

    # A non-success status is retried to exhaustion before aborting.
    assert calls["count"] == generate_cache.MAX_ATTEMPTS


# ---------------------------------------------------------------------------
# Cassette-driven example / edge tests (CFTC test-plus-cassette convention).
# Recorded SDMX interactions under tests/record/ are replayed; no live network.
# ---------------------------------------------------------------------------

# SDMX REST resources the generator must never request (all 404 on StatsCan).
_FORBIDDEN_URL_SEGMENTS = (
    "/dataflow",
    "/codelist",
    "/conceptscheme",
    "/availableconstraint",
    "/availability",
)


class _CassetteResponse:
    """Minimal stand-in for a recorded ``requests.Response``."""

    def __init__(self, text: str, status_code: int) -> None:
        self.text = text
        self.status_code = status_code

    def json(self):
        """Parse the recorded body as JSON, mirroring ``Response.json``."""
        return json.loads(self.text)


def _cassette_session(cassette_name: str):
    """Build an offline session replaying recorded interactions by URL.

    The returned session's ``get`` matches the requested URL against the
    recorded interactions in ``cassette_name`` and returns the stored body and
    status, recording every requested URL into a list. No network call is made.
    """
    interactions = yaml.safe_load((_CASSETTE_DIR / cassette_name).read_text())[
        "interactions"
    ]
    requested: list[str] = []

    def _get(url, headers=None, timeout=None):  # noqa: ARG001
        requested.append(url)
        for interaction in interactions:
            if interaction["request"]["uri"] == url:
                response = interaction["response"]
                return _CassetteResponse(
                    response["body"]["string"], response["status"]["code"]
                )
        raise AssertionError(f"no recorded interaction for {url!r}")

    session = mock.Mock()
    session.get.side_effect = _get
    return session, requested


def test_generate_cache_success():
    """Only ind-econ.json and structure URLs are requested over a full fetch.

    Replays the well-formed cassette offline and asserts the generator requests
    exactly ``ind-econ.json`` then ``/structure/Data_Structure_{pid}`` for each
    derived PID, and never a dataflow-listing, standalone codelist,
    concept-scheme, or availability endpoint.

    Validates: Requirements 4.2, 4.3, 4.6
    """
    session, requested = _cassette_session(
        "test_generate_cache_success_urllib3_v2.yaml"
    )

    ind_econ = generate_cache.fetch_ind_econ(session)
    pids = generate_cache.derive_pids(ind_econ)
    for pid in pids:
        generate_cache.fetch_structure(session, pid)

    # The cassette seeds a single valid, deduped PID.
    assert pids == ["18100004"]

    # Exactly the two allowed URL shapes, in order, and nothing else.
    assert requested == [
        generate_cache.IND_ECON_URL,
        f"{generate_cache.BASE_URL}/structure/Data_Structure_18100004",
    ]
    for url in requested:
        assert not any(segment in url for segment in _FORBIDDEN_URL_SEGMENTS)


def test_generate_cache_http_error():
    """A non-success status aborts the fetch and writes no catalog asset.

    Replays the cassette whose structure fetch returns HTTP 404 offline and
    asserts the generator raises an error identifying the failing fetch and the
    status, and leaves no catalog asset on disk.

    Validates: Requirements 4.3, 11.7
    """
    session, _ = _cassette_session("test_generate_cache_http_error_urllib3_v2.yaml")

    with tempfile.TemporaryDirectory() as tmp:
        cache_file = Path(tmp) / "government_ca_cache.json.xz"
        with (
            mock.patch.object(generate_cache, "CACHE_FILE", cache_file),
            mock.patch.object(generate_cache, "MAX_ATTEMPTS", 1),
        ):
            ind_econ = generate_cache.fetch_ind_econ(session)
            pids = generate_cache.derive_pids(ind_econ)
            with pytest.raises(RuntimeError) as excinfo:
                for pid in pids:
                    generate_cache.fetch_structure(session, pid)

            message = str(excinfo.value)
            # The error names the failing fetch and the HTTP status.
            assert "Data_Structure_18100004" in message
            assert "404" in message
            # No catalog asset is written when a fetch fails.
            assert not cache_file.exists()


def test_import_generate_cache_does_not_load_openbb_core():
    """Loading the generator never pulls ``openbb_core`` into ``sys.modules``.

    The generator is build-time code (stdlib + requests only) invoked by the
    build hook **by file path** (``[sys.executable, str(_GENERATE_CACHE)]``),
    never as the ``openbb_government_ca.utils.generate_cache`` package submodule
    — importing it by dotted path would run ``openbb_government_ca/__init__.py``,
    which legitimately imports ``openbb_core``. This test mirrors the build
    hook: it loads the module straight off disk by path in a clean subprocess
    and asserts no ``openbb_core`` module leaks into ``sys.modules``.

    Validates: Requirements 4.3
    """
    generator_path = Path(generate_cache.__file__).resolve()
    code = (
        "import sys, importlib.util;"
        f"spec = importlib.util.spec_from_file_location("
        f"'_gen_cache_by_path', {str(generator_path)!r});"
        "mod = importlib.util.module_from_spec(spec);"
        "spec.loader.exec_module(mod);"
        "leaked = sorted(m for m in sys.modules if m.startswith('openbb_core'));"
        "assert not leaked, leaked"
    )
    result = subprocess.run(  # noqa: S603
        [sys.executable, "-c", code],
        cwd=str(generator_path.parent),
        env={**os.environ},
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr


# Recorded cassettes live alongside the suite under record/http/<module>/.
_CASSETTE_DIR = Path(__file__).parent / "record" / "http" / "test_generate_cache"


def _cassette_body(cassette_name: str, uri_fragment: str) -> str:
    """Return the recorded response body whose request URI contains a fragment.

    Replays a recorded cassette without any network call by reading the stored
    interaction straight off disk.

    Parameters
    ----------
    cassette_name : str
        The cassette filename under ``record/http/test_generate_cache/``.
    uri_fragment : str
        A substring identifying the desired recorded request URI.

    Returns
    -------
    str
        The recorded response body string for the matching interaction.
    """
    cassette = yaml.safe_load((_CASSETTE_DIR / cassette_name).read_text())
    for interaction in cassette["interactions"]:
        if uri_fragment in interaction["request"]["uri"]:
            return interaction["response"]["body"]["string"]
    raise AssertionError(f"no recorded interaction matching {uri_fragment!r}")


def test_digest_well_formed_cpi_structure():
    """Digesting the well-formed CPI-like cassette yields the expected entry.

    Replays the recorded well-formed Consumer Price Index Structure_Message body
    through ``parse_structure`` (and ``classify_frequency`` for the derived
    frequency) and asserts the ``Normalized_Table_Entry`` matches the bilingual
    name, the dimensions ordered by ascending position with their codelist ids
    and code-to-label pairs (including the EN fallback for the FR-less ``Food``
    code), the declared attributes, and the monthly frequency.

    Validates: Requirements 5.1, 11.1
    """
    body = _cassette_body(
        "test_generate_cache_success_urllib3_v2.yaml", "Data_Structure_18100004"
    )

    entry = generate_cache.parse_structure(body, "18100004")
    entry["frequency"] = generate_cache.classify_frequency(entry.pop("freq_text"))

    assert entry == {
        "pid": "18100004",
        "name": {
            "en": "Consumer Price Index, monthly, not seasonally adjusted",
            "fr": "Indice des prix à la consommation, mensuel, non désaisonnalisé",
        },
        "frequency": "monthly",
        "dimensions": [
            {
                "id": "Geography",
                "position": 1,
                "codelist_id": "CL_Geography",
                "codes": [{"code": "2", "en": "Canada", "fr": "Canada"}],
            },
            {
                "id": "Products_and_product_groups",
                "position": 2,
                "codelist_id": "CL_Products_and_product_groups",
                "codes": [
                    {"code": "2", "en": "All-items", "fr": "Ensemble"},
                    # The FR label is omitted in the cassette; it falls back to EN.
                    {"code": "3", "en": "Food", "fr": "Food"},
                ],
            },
        ],
        "attributes": [
            "UOM",
            "DGUID",
            "SCALAR_FACTOR",
            "VECTOR_ID",
            "NB_DECIMAL",
            "SYMBOL",
            "STATUS_CAN",
            "TERMINATED",
            "SECURITY_LEVEL",
        ],
    }


# ---------------------------------------------------------------------------
# parse_structure error-branch example tests: every malformed/unexpected body
# raises StructureParseError (the caller, build_catalog, catches it to skip the
# offending PID). Each case is deterministic so the error paths are always hit.
# ---------------------------------------------------------------------------

_STRUCTURE_HEADER = (
    "<mes:Structure "
    'xmlns:mes="http://www.sdmx.org/resources/sdmxml/schemas/v2_1/message" '
    'xmlns:str="http://www.sdmx.org/resources/sdmxml/schemas/v2_1/structure" '
    'xmlns:com="http://www.sdmx.org/resources/sdmxml/schemas/v2_1/common">'
)
# A well-formed Dataflows block carrying an English name, so cases that need to
# get past the dataflow lookup and bilingual-name read can reuse it.
_DATAFLOW_EN = (
    '<str:Dataflows><str:Dataflow id="DF">'
    '<com:Name xml:lang="en">Some Table</com:Name>'
    "</str:Dataflow></str:Dataflows>"
)


def _wrap_structures(inner: str) -> str:
    """Wrap ``inner`` in a minimal SDMX-ML ``Structure_Message`` envelope."""
    return (
        f"{_STRUCTURE_HEADER}<mes:Structures>{inner}</mes:Structures></mes:Structure>"
    )


_PARSE_ERROR_CASES = {
    # Malformed XML: ElementTree.fromstring rejects it outright.
    "malformed_xml": ("this is not valid xml <<<", "malformed XML"),
    # Well-formed XML with no Dataflow element.
    "no_dataflow": (_wrap_structures(""), "no Dataflow"),
    # Dataflow present but its only name lacks the English (xml:lang="en") label.
    "missing_english_name": (
        _wrap_structures(
            '<str:Dataflows><str:Dataflow id="DF">'
            '<com:Name xml:lang="fr">Un tableau</com:Name>'
            "</str:Dataflow></str:Dataflows>"
        ),
        "missing English name",
    ),
    # Dataflow with an English name but no DataStructure element.
    "no_data_structure": (_wrap_structures(_DATAFLOW_EN), "no DataStructure"),
    # DataStructure present but missing its DataStructureComponents child.
    "no_components": (
        _wrap_structures(
            _DATAFLOW_EN + '<str:DataStructures><str:DataStructure id="DS">'
            "</str:DataStructure></str:DataStructures>"
        ),
        "no DataStructureComponents",
    ),
    # A Dimension whose declared position is not an integer.
    "invalid_position": (
        _wrap_structures(
            _DATAFLOW_EN + '<str:DataStructures><str:DataStructure id="DS">'
            "<str:DataStructureComponents><str:DimensionList>"
            '<str:Dimension id="D" position="not-an-int">'
            "<str:LocalRepresentation><str:Enumeration>"
            '<Ref id="CL_X"/>'
            "</str:Enumeration></str:LocalRepresentation>"
            "</str:Dimension></str:DimensionList>"
            "</str:DataStructureComponents></str:DataStructure></str:DataStructures>"
        ),
        "invalid dimension position",
    ),
}


@pytest.mark.parametrize(
    ("xml_text", "fragment"),
    list(_PARSE_ERROR_CASES.values()),
    ids=list(_PARSE_ERROR_CASES),
)
def test_parse_structure_raises_on_malformed_bodies(xml_text, fragment):
    """parse_structure raises StructureParseError on every malformed body.

    Covers each error branch: malformed XML, a missing Dataflow, a Dataflow
    without an English name, a missing DataStructure, a missing
    DataStructureComponents, and a non-integer dimension position. The raised
    error identifies the PID and the specific failure reason.

    Validates: Requirements 5.10
    """
    with pytest.raises(generate_cache.StructureParseError) as excinfo:
        generate_cache.parse_structure(xml_text, "12345678")

    message = str(excinfo.value)
    assert fragment in message
    # The PID is echoed into every parse error for traceability.
    assert "12345678" in message


def test_parse_structure_skips_non_freq_annotations():
    """parse_structure ignores annotations that are not the ``freq`` one.

    The cube's ``DataStructure`` carries several annotations: one whose type is
    not ``freq``, one with no ``AnnotationType`` at all, and finally the real
    ``freq`` annotation. The digest must skip the first two and read the English
    text of the ``freq`` annotation into ``freq_text``.

    Validates: Requirements 5.7
    """
    body = _wrap_structures(
        _DATAFLOW_EN + '<str:DataStructures><str:DataStructure id="DS">'
        "<com:Annotations>"
        # (1) An annotation whose type is not "freq" -> skipped.
        "<com:Annotation><com:AnnotationType>footnote</com:AnnotationType>"
        '<com:AnnotationText xml:lang="en">ignore me</com:AnnotationText>'
        "</com:Annotation>"
        # (2) An annotation with no AnnotationType element -> skipped.
        "<com:Annotation>"
        '<com:AnnotationText xml:lang="en">also ignored</com:AnnotationText>'
        "</com:Annotation>"
        # (3) The real freq annotation -> its English text is read.
        "<com:Annotation><com:AnnotationType>freq</com:AnnotationType>"
        '<com:AnnotationText xml:lang="fr">Mensuel</com:AnnotationText>'
        '<com:AnnotationText xml:lang="en">Monthly</com:AnnotationText>'
        "</com:Annotation>"
        "</com:Annotations>"
        "<str:DataStructureComponents>"
        "<str:DimensionList></str:DimensionList>"
        "<str:AttributeList></str:AttributeList>"
        "</str:DataStructureComponents>"
        "</str:DataStructure></str:DataStructures>"
    )

    entry = generate_cache.parse_structure(body, "12345678")

    assert entry["freq_text"] == "Monthly"
    assert generate_cache.classify_frequency(entry["freq_text"]) == "monthly"


# ---------------------------------------------------------------------------
# Property 2: Structure digest fidelity (parse_structure over synthetic
# schema-valid SDMX-ML Structure_Message strings).
# ---------------------------------------------------------------------------

# Identifiers (dataflow/dimension/codelist/code/attribute ids) use a safe,
# XML-clean alphabet so no escaping is needed.
_id_text = st.text(
    alphabet="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_",
    min_size=1,
    max_size=12,
)
# Human-readable labels include spaces and French accents but no XML-special
# characters; stripped + non-empty to match the parser's ``.strip()`` digest.
_label_text = (
    st.text(
        alphabet=(
            "abcdefghijklmnopqrstuvwxyz"
            "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
            "0123456789 éàùâêîôûçÉÀÈ"
        ),
        min_size=1,
        max_size=24,
    )
    .map(str.strip)
    .filter(bool)
)


@st.composite
def _structure_messages(draw):
    """Build a schema-valid SDMX-ML ``Structure_Message`` plus its expected digest.

    The dataflow name is bilingual with the French label randomly omitted;
    each classification dimension references a unique codelist whose codes carry
    English labels and optionally French labels; dimension declared positions are
    unique and the order in which dimensions appear in the XML is shuffled
    independently of those positions (so the parser must sort by ascending
    position). Returns ``(xml_text, pid, spec)`` where ``spec`` mirrors the
    expected normalized entry.
    """
    pid = draw(st.text(alphabet="0123456789", min_size=8, max_size=8))

    name_en = draw(_label_text)
    name_fr = draw(_label_text) if draw(st.booleans()) else None

    n_dims = draw(st.integers(min_value=1, max_value=5))
    dim_ids = draw(st.lists(_id_text, min_size=n_dims, max_size=n_dims, unique=True))
    codelist_ids = draw(
        st.lists(
            _id_text.map(lambda s: "CL_" + s),
            min_size=n_dims,
            max_size=n_dims,
            unique=True,
        )
    )
    positions = draw(
        st.lists(
            st.integers(min_value=1, max_value=50),
            min_size=n_dims,
            max_size=n_dims,
            unique=True,
        )
    )

    dimensions = []
    for dim_id, codelist_id, position in zip(dim_ids, codelist_ids, positions):
        code_ids = draw(st.lists(_id_text, min_size=0, max_size=4, unique=True))
        codes = []
        for code_id in code_ids:
            en = draw(_label_text)
            fr = draw(_label_text) if draw(st.booleans()) else None
            codes.append({"code": code_id, "en": en, "fr": fr})
        dimensions.append(
            {
                "id": dim_id,
                "position": position,
                "codelist_id": codelist_id,
                "codes": codes,
            }
        )

    attributes = draw(st.lists(_id_text, min_size=0, max_size=5, unique=True))

    # Shuffle the order dimensions are *declared* in the XML, independent of
    # their position attribute, so the parser's ascending-position sort is tested.
    xml_order = draw(st.permutations(list(range(n_dims))))

    spec = {
        "pid": pid,
        "name_en": name_en,
        "name_fr": name_fr,
        "dimensions": dimensions,
        "attributes": attributes,
    }
    xml_text = _build_structure_xml(spec, xml_order)
    return xml_text, pid, spec


def _build_structure_xml(spec, xml_order):
    """Render a ``spec`` into an SDMX-ML ``Structure_Message`` string.

    No XML declaration is emitted because ``parse_structure`` feeds the ``str``
    body straight to ``ElementTree.fromstring``, which rejects unicode strings
    carrying an encoding declaration.
    """
    out = [
        "<mes:Structure "
        'xmlns:mes="http://www.sdmx.org/resources/sdmxml/schemas/v2_1/message" '
        'xmlns:str="http://www.sdmx.org/resources/sdmxml/schemas/v2_1/structure" '
        'xmlns:com="http://www.sdmx.org/resources/sdmxml/schemas/v2_1/common">',
        "<mes:Structures>",
        "<str:Codelists>",
    ]
    for dim in spec["dimensions"]:
        out.append(f'<str:Codelist id="{dim["codelist_id"]}">')
        for code in dim["codes"]:
            out.append(f'<str:Code id="{code["code"]}">')
            out.append(f'<com:Name xml:lang="en">{code["en"]}</com:Name>')
            if code["fr"] is not None:
                out.append(f'<com:Name xml:lang="fr">{code["fr"]}</com:Name>')
            out.append("</str:Code>")
        out.append("</str:Codelist>")
    out.append("</str:Codelists>")

    out.append("<str:Dataflows>")
    out.append(f'<str:Dataflow id="DF_{spec["pid"]}">')
    out.append(f'<com:Name xml:lang="en">{spec["name_en"]}</com:Name>')
    if spec["name_fr"] is not None:
        out.append(f'<com:Name xml:lang="fr">{spec["name_fr"]}</com:Name>')
    out.append("</str:Dataflow>")
    out.append("</str:Dataflows>")

    out.append("<str:DataStructures>")
    out.append(f'<str:DataStructure id="Data_Structure_{spec["pid"]}">')
    out.append("<str:DataStructureComponents>")
    out.append("<str:DimensionList>")
    for idx in xml_order:
        dim = spec["dimensions"][idx]
        out.append(f'<str:Dimension id="{dim["id"]}" position="{dim["position"]}">')
        out.append("<str:LocalRepresentation>")
        out.append("<str:Enumeration>")
        out.append(f'<Ref id="{dim["codelist_id"]}"/>')
        out.append("</str:Enumeration>")
        out.append("</str:LocalRepresentation>")
        out.append("</str:Dimension>")
    out.append('<str:TimeDimension id="TIME_PERIOD">')
    out.append("<str:LocalRepresentation>")
    out.append("<str:TextFormat/>")
    out.append("</str:LocalRepresentation>")
    out.append("</str:TimeDimension>")
    out.append("</str:DimensionList>")
    out.append("<str:AttributeList>")
    for attr in spec["attributes"]:
        out.append(f'<str:Attribute id="{attr}"/>')
    out.append("</str:AttributeList>")
    out.append("</str:DataStructureComponents>")
    out.append("</str:DataStructure>")
    out.append("</str:DataStructures>")
    out.append("</mes:Structures>")
    out.append("</mes:Structure>")
    return "\n".join(out)


# Feature: government-ca-build-phase-1, Property 2
@settings(max_examples=100, deadline=None)
@given(_structure_messages())
def test_parse_structure_digest_fidelity(case):
    """Property 2: Structure digest fidelity.

    For any well-formed SDMX-ML ``Structure_Message`` (bilingual dataflow name,
    classification dimensions declared in arbitrary position order, per-dimension
    codelists whose codes carry English labels and optionally French labels, and
    a declared attribute list), the ``Normalized_Table_Entry`` produced by
    ``parse_structure`` (a) records both English and French dataflow names,
    (b) lists dimensions ordered strictly by ascending declared position,
    (c) records for each dimension its codelist id together with every
    code-to-label pair, (d) sets each code's French label equal to its English
    label whenever the structure omits the French label, and (e) records exactly
    the declared attribute ids.

    Validates: Requirements 5.2, 5.3, 5.4, 5.5, 5.6
    """
    xml_text, pid, spec = case
    entry = generate_cache.parse_structure(xml_text, pid)

    # (a) Both English and French dataflow names are recorded; FR falls back to
    # EN when the structure omits the French dataflow label.
    expected_name_fr = (
        spec["name_fr"] if spec["name_fr"] is not None else spec["name_en"]
    )
    assert entry["name"]["en"] == spec["name_en"]
    assert entry["name"]["fr"] == expected_name_fr

    # (b) Dimensions are ordered strictly by ascending declared position.
    got_positions = [dim["position"] for dim in entry["dimensions"]]
    assert got_positions == sorted(got_positions)
    assert all(
        got_positions[i] < got_positions[i + 1] for i in range(len(got_positions) - 1)
    )
    expected_dims = sorted(spec["dimensions"], key=lambda d: d["position"])
    assert [dim["id"] for dim in entry["dimensions"]] == [
        dim["id"] for dim in expected_dims
    ]

    # (c) Each dimension records its codelist id and every code-to-label pair,
    # and (d) a missing French label falls back to the English label.
    for got_dim, exp_dim in zip(entry["dimensions"], expected_dims):
        assert got_dim["codelist_id"] == exp_dim["codelist_id"]
        expected_codes = [
            {
                "code": code["code"],
                "en": code["en"],
                "fr": code["fr"] if code["fr"] is not None else code["en"],
            }
            for code in exp_dim["codes"]
        ]
        assert got_dim["codes"] == expected_codes
        # (d) explicit FR == EN fallback for codes whose French label was omitted.
        for got_code, exp_code in zip(got_dim["codes"], exp_dim["codes"]):
            if exp_code["fr"] is None:
                assert got_code["fr"] == got_code["en"] == exp_code["en"]

    # (e) Exactly the declared attribute ids are recorded, in declared order.
    assert entry["attributes"] == spec["attributes"]


# ---------------------------------------------------------------------------
# Property 3: Frequency classification totality (classify_frequency over the
# DataStructure ``freq`` annotation text).
# ---------------------------------------------------------------------------

# Recognized frequency labels mapped to their classify_frequency result.
_FREQ_LABELS = {
    "monthly": "monthly",
    "annual": "annual",
    "annually": "annual",
    "quarterly": "quarterly",
}
# Arbitrary surrounding whitespace exercises the ``.strip()`` in the classifier.
_whitespace = st.text(alphabet=" \t\n", max_size=3)


@st.composite
def _frequency_cases(draw):
    """Draw a freq annotation text paired with its expected frequency label.

    Recognized labels are emitted with random letter casing and arbitrary
    surrounding whitespace (so the case-insensitive, whitespace-trimmed match is
    exercised); arbitrary other strings (none equal to a recognized label after
    strip+lower) are emitted as the catch-all ``undetermined`` path.
    """
    if draw(st.booleans()):
        label = draw(st.sampled_from(sorted(_FREQ_LABELS)))
        cased = "".join(
            ch.upper() if draw(st.booleans()) else ch.lower() for ch in label
        )
        text = draw(_whitespace) + cased + draw(_whitespace)
        return text, _FREQ_LABELS[label]
    other = draw(
        st.text(max_size=20).filter(lambda s: s.strip().lower() not in _FREQ_LABELS)
    )
    return other, "undetermined"


# Feature: government-ca-build-phase-1, Property 3
@settings(max_examples=200)
@given(_frequency_cases())
def test_classify_frequency_is_total(case):
    """Property 3: Frequency classification is total.

    For any ``freq`` annotation text, ``classify_frequency`` returns a value in
    ``{annual, monthly, quarterly, undetermined}``; it returns ``monthly`` for
    ``"Monthly"``, ``annual`` for ``"Annual"``/``"Annually"``, and ``quarterly``
    for ``"Quarterly"`` (case-insensitive, whitespace-trimmed), and returns
    ``undetermined`` for any other or absent text.

    Validates: Requirements 5.7, 5.8
    """
    token, expected = case
    result = generate_cache.classify_frequency(token)

    # Totality: the return value is always one of the four known frequencies.
    assert result in {"annual", "monthly", "quarterly", "undetermined"}
    # Correct classification per label (and undetermined for everything else).
    assert result == expected


# ---------------------------------------------------------------------------
# Property 5: Catalog codec round-trip (serialize_catalog -> compress, then
# lzma.decompress -> json.loads) over synthetic catalog blobs carrying
# non-ASCII French text.
# ---------------------------------------------------------------------------

# Catalog string values use a safe alphabet that excludes the JSON separator
# characters (comma, colon), the escape character (backslash), and the quote,
# so that any ", " or ": " in the serialized output can only be separator
# whitespace and any "\\u" can only be a unicode escape. Spaces and French
# accents are included to exercise compact separators and non-ASCII handling.
_codec_label = (
    st.text(
        alphabet=(
            "abcdefghijklmnopqrstuvwxyz"
            "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
            "0123456789 éàùâêîôûçÉÀÈ-'()"
        ),
        min_size=1,
        max_size=24,
    )
    .map(str.strip)
    .filter(bool)
)
# A French label guaranteed to carry at least one non-ASCII character.
_french_label = st.builds(
    lambda accent, rest: accent + rest,
    st.sampled_from("éàùâêîôûçÉÀÈ"),
    _codec_label,
)


@st.composite
def _catalog_blobs(draw):
    """Build a ``Catalog_Cache`` blob whose entries carry non-ASCII French text.

    Each table is keyed by an 8-digit PID and mirrors a ``Normalized_Table_Entry``:
    a bilingual name whose French label always contains an accent, dimensions with
    code-to-bilingual-label pairs, and declared attributes. The shape varies
    (table count, dimension count, code count) so the codec is exercised across a
    range of nested blobs.
    """
    pids = draw(st.lists(_valid_pid, min_size=0, max_size=4, unique=True))
    tables: dict[str, dict] = {}
    for pid in pids:
        n_dims = draw(st.integers(min_value=0, max_value=3))
        dimensions = []
        for position in range(1, n_dims + 1):
            code_ids = draw(st.lists(_id_text, min_size=0, max_size=3, unique=True))
            codes = [
                {"code": code_id, "en": draw(_codec_label), "fr": draw(_french_label)}
                for code_id in code_ids
            ]
            dimensions.append(
                {
                    "id": draw(_id_text),
                    "position": position,
                    "codelist_id": draw(_id_text.map(lambda s: "CL_" + s)),
                    "codes": codes,
                }
            )
        tables[pid] = {
            "pid": pid,
            "name": {"en": draw(_codec_label), "fr": draw(_french_label)},
            "frequency": draw(
                st.sampled_from(["annual", "monthly", "quarterly", "undetermined"])
            ),
            "dimensions": dimensions,
            "attributes": draw(st.lists(_id_text, min_size=0, max_size=4, unique=True)),
        }
    return {"schema_version": 1, "source": "statcan-sdmx", "tables": tables}


def _all_strings(obj):
    """Yield every string appearing as a key or value within a nested blob."""
    if isinstance(obj, str):
        yield obj
    elif isinstance(obj, dict):
        for key, value in obj.items():
            yield key
            yield from _all_strings(value)
    elif isinstance(obj, list):
        for value in obj:
            yield from _all_strings(value)


# Feature: government-ca-build-phase-1, Property 5
@settings(max_examples=100)
@given(_catalog_blobs())
def test_catalog_codec_round_trip_preserves_content(blob):
    """Property 5: Catalog codec round-trip preserves content, including non-ASCII.

    For any catalog blob (including entries with non-ASCII French text),
    decompressing then JSON-decoding the output of serialize-then-LZMA-compress
    yields a structure equal to the original blob, and the serialized JSON
    contains no separator whitespace and no ``\\uXXXX`` escaping of non-ASCII
    characters (compact ``separators=(",", ":")``, ``ensure_ascii=False``, LZMA
    ``FORMAT_XZ`` preset 6).

    Validates: Requirements 6.1, 6.2
    """
    serialized = generate_cache.serialize_catalog(blob)
    compressed = generate_cache.compress(serialized)

    # Round-trip: decompress + JSON-decode reproduces the original blob exactly.
    restored = json.loads(lzma.decompress(compressed))
    assert restored == blob

    text = serialized.decode("utf-8")

    # Compact separators: no whitespace follows the comma or colon separators.
    assert ", " not in text
    assert ": " not in text

    # Non-ASCII French text is preserved literally, never escaped as \\uXXXX.
    assert "\\u" not in text
    non_ascii = {ch for value in _all_strings(blob) for ch in value if ord(ch) > 127}
    for ch in non_ascii:
        assert ch in text


# ---------------------------------------------------------------------------
# Property 4: Parse-skip vs keep orchestration (build_catalog over a curated
# PID set mixing well-formed and malformed structure bodies; the fetch layer
# is stubbed so no live network call occurs).
# ---------------------------------------------------------------------------

# Malformed/unparseable structure bodies that make parse_structure raise a
# StructureParseError: invalid XML, an empty body, and well-formed XML that is
# missing the expected Dataflow element.
_malformed_body = st.sampled_from(
    [
        "this is not xml <<<",
        "",
        "<root><child>no dataflow here</child></root>",
    ]
)


@st.composite
def _mixed_structure_runs(draw):
    """Build a curated PID set mixing well-formed and malformed structure bodies.

    For each unique 8-digit PID a coin flip decides whether its structure body
    is well-formed (a minimal schema-valid Structure_Message that
    ``parse_structure`` digests) or malformed (a body that makes
    ``parse_structure`` raise). Returns ``(pids, bodies, well_formed, skipped)``
    where ``bodies`` maps each PID to its structure body, ``well_formed`` are the
    PIDs expected to be kept, and ``skipped`` are the PIDs expected to be dropped.
    """
    n = draw(st.integers(min_value=1, max_value=6))
    pids = draw(st.lists(_valid_pid, min_size=n, max_size=n, unique=True))
    bodies: dict[str, str] = {}
    well_formed: list[str] = []
    skipped: list[str] = []
    for pid in pids:
        if draw(st.booleans()):
            spec = {
                "pid": pid,
                "name_en": draw(_label_text),
                "name_fr": None,
                "dimensions": [],
                "attributes": [],
            }
            bodies[pid] = _build_structure_xml(spec, [])
            well_formed.append(pid)
        else:
            bodies[pid] = draw(_malformed_body)
            skipped.append(pid)
    return pids, bodies, well_formed, skipped


# Feature: government-ca-build-phase-1, Property 4
@settings(max_examples=100, deadline=None)
@given(_mixed_structure_runs())
def test_malformed_structures_skipped_well_formed_kept(case):
    """Property 4: Malformed structures are skipped, well-formed ones are kept.

    For any Curated_PID_Set in which an arbitrary subset of PIDs returns a
    malformed/unparseable structure body and the rest return well-formed bodies,
    the resulting catalog's ``tables`` map contains a ``Normalized_Table_Entry``
    for exactly the PIDs whose bodies parsed successfully, and none for the
    skipped PIDs, and the run still completes and writes a cache.

    Validates: Requirements 5.9, 5.10
    """
    pids, bodies, well_formed, skipped = case

    def _fake_fetch_ind_econ(session):  # noqa: ARG001
        return {"results": {"indicators": [{"source": pid} for pid in pids]}}

    def _fake_fetch_structure(session, pid):  # noqa: ARG001
        return bodies[pid]

    with tempfile.TemporaryDirectory() as tmp:
        assets_dir = Path(tmp) / "assets"
        cache_file = assets_dir / "government_ca_cache.json.xz"
        with (
            mock.patch.object(generate_cache, "fetch_ind_econ", _fake_fetch_ind_econ),
            mock.patch.object(generate_cache, "fetch_structure", _fake_fetch_structure),
            mock.patch.object(generate_cache, "ASSETS_DIR", assets_dir),
            mock.patch.object(generate_cache, "CACHE_FILE", cache_file),
        ):
            # The full run completes without raising despite malformed bodies.
            generate_cache.main()

        # The run wrote a cache (parse-skip never aborts the run).
        assert cache_file.exists()

        blob = json.loads(lzma.decompress(cache_file.read_bytes()))

    tables = blob["tables"]

    # The tables map keys are exactly the successfully parsed PIDs.
    assert set(tables) == set(well_formed)
    # No entry exists for any skipped (malformed) PID.
    assert set(tables).isdisjoint(skipped)
    # Every kept entry is keyed by, and echoes, its own CODR PID.
    for pid, entry in tables.items():
        assert entry["pid"] == pid


# ---------------------------------------------------------------------------
# Property 9: Compressed catalog respects the size bound (compress over
# in-scope catalog blobs stays within the ceiling; write_cache rejects an
# over-bound payload and leaves any existing cache file unchanged).
# ---------------------------------------------------------------------------

# Bytes already on disk before an over-bound write is attempted.
_existing_cache = st.binary(min_size=0, max_size=64)
# Amount by which an over-bound payload exceeds the MAX_CACHE_BYTES ceiling.
_overage = st.integers(min_value=1, max_value=64)


# Feature: government-ca-build-phase-1, Property 9
@settings(max_examples=100, deadline=None)
@given(_catalog_blobs(), _existing_cache, _overage)
def test_compressed_catalog_respects_size_bound(blob, existing, overage):
    """Property 9: Compressed catalog respects the size bound.

    For any catalog blob within the curated scope, the compressed artifact is no
    larger than 1,048,576 bytes; when a payload would exceed the bound,
    ``write_cache`` surfaces an error and leaves any existing cache file
    unchanged.

    Validates: Requirements 6.4, 6.5
    """
    # (a) An in-scope catalog blob compresses to within the 1 MiB ceiling.
    compressed = generate_cache.compress(generate_cache.serialize_catalog(blob))
    assert len(compressed) <= generate_cache.MAX_CACHE_BYTES

    with tempfile.TemporaryDirectory() as tmp:
        assets_dir = Path(tmp) / "assets"
        cache_file = assets_dir / "government_ca_cache.json.xz"
        with (
            mock.patch.object(generate_cache, "ASSETS_DIR", assets_dir),
            mock.patch.object(generate_cache, "CACHE_FILE", cache_file),
        ):
            # The in-bound payload is written: assets/ is created and the
            # single .json.xz holds exactly the compressed bytes.
            generate_cache.write_cache(compressed)
            assert cache_file.read_bytes() == compressed

            # (b) An over-bound payload surfaces an error and leaves the
            # existing cache file untouched.
            cache_file.write_bytes(existing)
            over_bound = b"\x00" * (generate_cache.MAX_CACHE_BYTES + overage)
            with pytest.raises(ValueError):
                generate_cache.write_cache(over_bound)
            assert cache_file.read_bytes() == existing


# ---------------------------------------------------------------------------
# Generator filesystem and main() example / edge tests (Req 6.3, 6.6, 6.7).
# All disk writes are redirected to a temporary directory; no live network.
# ---------------------------------------------------------------------------


class _FakeJsonResponse:
    """Minimal stand-in for a JSON ``requests.Response`` success body."""

    def __init__(self, payload: dict) -> None:
        self.status_code = 200
        self.text = ""
        self._payload = payload

    def json(self) -> dict:
        return self._payload


def test_write_cache_creates_assets_and_overwrites():
    """assets/ is created on demand and an existing cache is overwritten.

    The first write into a missing ``assets/`` directory creates it and lands a
    single ``.json.xz`` file; a subsequent successful write replaces the bytes
    of the existing cache in place.

    Validates: Requirements 6.3
    """
    first = generate_cache.compress(b"first-version")
    second = generate_cache.compress(b"second-version")

    with tempfile.TemporaryDirectory() as tmp:
        assets_dir = Path(tmp) / "assets"
        cache_file = assets_dir / "government_ca_cache.json.xz"
        with (
            mock.patch.object(generate_cache, "ASSETS_DIR", assets_dir),
            mock.patch.object(generate_cache, "CACHE_FILE", cache_file),
        ):
            # assets/ does not exist yet; the first write creates it.
            assert not assets_dir.exists()
            generate_cache.write_cache(first)
            assert assets_dir.is_dir()

            # Exactly one .json.xz file is written into assets/.
            assert list(assets_dir.iterdir()) == [cache_file]
            assert cache_file.read_bytes() == first

            # A subsequent successful write overwrites the existing cache.
            generate_cache.write_cache(second)
            assert list(assets_dir.iterdir()) == [cache_file]
            assert cache_file.read_bytes() == second


@pytest.mark.parametrize("stage", ["serialize", "compress", "write"])
def test_main_failure_leaves_existing_cache_unchanged(stage):
    """A serialization/compression/write failure leaves any existing cache intact.

    For a failure forced at each of the three terminal stages, ``main`` surfaces
    the error to the caller and the cache file already on disk is left
    byte-for-byte unchanged.

    Validates: Requirements 6.6
    """
    blob = {"schema_version": 1, "source": "statcan-sdmx", "tables": {}}
    existing = generate_cache.compress(b"existing-catalog")

    with tempfile.TemporaryDirectory() as tmp:
        assets_dir = Path(tmp) / "assets"
        cache_file = assets_dir / "government_ca_cache.json.xz"
        assets_dir.mkdir()
        cache_file.write_bytes(existing)

        patches = [
            mock.patch.object(generate_cache, "build_catalog", return_value=blob),
            mock.patch.object(generate_cache, "ASSETS_DIR", assets_dir),
            mock.patch.object(generate_cache, "CACHE_FILE", cache_file),
        ]
        if stage == "serialize":
            patches.append(
                mock.patch.object(
                    generate_cache, "serialize_catalog", side_effect=RuntimeError("x")
                )
            )
            expected: type[Exception] = RuntimeError
        elif stage == "compress":
            patches.append(
                mock.patch.object(
                    generate_cache, "compress", side_effect=RuntimeError("x")
                )
            )
            expected = RuntimeError
        else:
            # A write-stage failure: an over-bound payload makes write_cache raise.
            over = b"\x00" * (generate_cache.MAX_CACHE_BYTES + 1)
            patches.append(
                mock.patch.object(generate_cache, "compress", return_value=over)
            )
            expected = ValueError

        with contextlib.ExitStack() as stack:
            for patch in patches:
                stack.enter_context(patch)
            with pytest.raises(expected):
                generate_cache.main()

        # The pre-existing cache file is left byte-for-byte unchanged.
        assert cache_file.read_bytes() == existing


def test_main_returns_on_success_and_raises_on_forced_failure():
    """``main`` returns on success and propagates a forced failure.

    On success ``main`` returns ``None`` after writing the single asset; when the
    build stage is forced to fail the error propagates out of ``main``.

    Validates: Requirements 6.7
    """
    blob = {"schema_version": 1, "source": "statcan-sdmx", "tables": {}}

    with tempfile.TemporaryDirectory() as tmp:
        assets_dir = Path(tmp) / "assets"
        cache_file = assets_dir / "government_ca_cache.json.xz"
        with (
            mock.patch.object(generate_cache, "build_catalog", return_value=blob),
            mock.patch.object(generate_cache, "ASSETS_DIR", assets_dir),
            mock.patch.object(generate_cache, "CACHE_FILE", cache_file),
        ):
            # Success: main returns None and writes the single asset.
            assert generate_cache.main() is None
            assert cache_file.exists()

    # A forced failure inside the build propagates out of main.
    with mock.patch.object(
        generate_cache, "build_catalog", side_effect=RuntimeError("boom")
    ):
        with pytest.raises(RuntimeError, match="boom"):
            generate_cache.main()


def test_main_guard_invokes_main():
    """The ``if __name__ == "__main__"`` guard runs ``main`` to completion.

    Executing the module source with ``__name__`` set to ``"__main__"`` fires the
    real guard, which calls ``main``. The network fetch and disk write are stubbed
    so the run completes without a live request and without touching the shipped
    asset, and the compressed catalog the guard produced is captured in memory.

    Validates: Requirements 6.7
    """
    written: dict[str, bytes] = {}

    def _fake_get(self, url, headers=None, timeout=None):  # noqa: ARG001
        return _FakeJsonResponse({"results": {"indicators": []}})

    def _fake_write_bytes(self, data):  # noqa: ARG001
        written["payload"] = data

    source = Path(generate_cache.__file__).read_text(encoding="utf-8")
    code = compile(source, generate_cache.__file__, "exec")
    namespace = {"__name__": "__main__", "__file__": generate_cache.__file__}
    with (
        mock.patch.object(requests.Session, "get", _fake_get),
        mock.patch.object(Path, "mkdir"),
        mock.patch.object(Path, "write_bytes", _fake_write_bytes),
    ):
        exec(code, namespace)  # noqa: S102

    # The guard fired main(), which built, compressed, and wrote the catalog.
    assert "payload" in written
    blob = json.loads(lzma.decompress(written["payload"]))
    assert blob == {"schema_version": 1, "source": "statcan-sdmx", "tables": {}}
