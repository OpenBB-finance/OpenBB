"""Tests for openbb_imf.utils.generate_cache."""

# ruff: noqa: I001

import json
import lzma

import pytest
import requests

from openbb_imf.utils import generate_cache as gc


class _FakeResp:
    """Minimal stand-in for ``requests.Response``."""

    def __init__(
        self,
        status_code: int = 200,
        json_data: dict | None = None,
        json_exc: Exception | None = None,
    ):
        self.status_code = status_code
        self._json_data = json_data or {}
        self._json_exc = json_exc

    def json(self):
        """Return JSON payload or raise the seeded exception."""
        if self._json_exc is not None:
            raise self._json_exc
        return self._json_data

    def raise_for_status(self):
        """Mirror ``requests.Response.raise_for_status``."""
        if self.status_code >= 400:
            raise requests.HTTPError(f"HTTP {self.status_code}")


class TestGet:
    """Tests for ``_get``."""

    def test_success(self, monkeypatch):
        """Returns parsed JSON on 200."""
        resp = _FakeResp(200, {"ok": True})
        monkeypatch.setattr(gc._session, "get", lambda *a, **kw: resp)
        assert gc._get("http://x") == {"ok": True}

    def test_400_returns_empty(self, monkeypatch):
        """HTTP 400 returns empty dict without raising."""
        resp = _FakeResp(400, {})
        monkeypatch.setattr(gc._session, "get", lambda *a, **kw: resp)
        assert gc._get("http://x") == {}

    def test_404_returns_empty(self, monkeypatch):
        """HTTP 404 returns empty dict."""
        resp = _FakeResp(404, {})
        monkeypatch.setattr(gc._session, "get", lambda *a, **kw: resp)
        assert gc._get("http://x") == {}

    def test_429_retries_then_succeeds(self, monkeypatch):
        """429 backs off then returns the next 200 response."""
        responses = [_FakeResp(429, {}), _FakeResp(200, {"ok": True})]
        calls = {"n": 0}

        def fake_get(*a, **kw):
            r = responses[calls["n"]]
            calls["n"] += 1
            return r

        monkeypatch.setattr(gc._session, "get", fake_get)
        monkeypatch.setattr(gc.time, "sleep", lambda *_a, **_kw: None)
        assert gc._get("http://x") == {"ok": True}
        assert calls["n"] == 2

    def test_request_exception_retried_then_raises(self, monkeypatch):
        """RequestException retries up to ``retries`` then re-raises."""

        def fake_get(*a, **kw):
            raise requests.ConnectionError("nope")

        monkeypatch.setattr(gc._session, "get", fake_get)
        monkeypatch.setattr(gc.time, "sleep", lambda *_a, **_kw: None)
        with pytest.raises(requests.ConnectionError):
            gc._get("http://x", retries=2, backoff=0.0)

    def test_request_exception_then_success(self, monkeypatch):
        """RequestException followed by success returns parsed JSON."""
        calls = {"n": 0}

        def fake_get(*a, **kw):
            calls["n"] += 1
            if calls["n"] == 1:
                raise requests.ConnectionError("flaky")
            return _FakeResp(200, {"ok": True})

        monkeypatch.setattr(gc._session, "get", fake_get)
        monkeypatch.setattr(gc.time, "sleep", lambda *_a, **_kw: None)
        assert gc._get("http://x", retries=3, backoff=0.0) == {"ok": True}

    def test_json_decode_error_retries(self, monkeypatch):
        """``json.JSONDecodeError`` triggers retry path."""
        calls = {"n": 0}

        def fake_get(*a, **kw):
            calls["n"] += 1
            if calls["n"] == 1:
                return _FakeResp(200, json_exc=json.JSONDecodeError("bad", "doc", 0))
            return _FakeResp(200, {"ok": True})

        monkeypatch.setattr(gc._session, "get", fake_get)
        monkeypatch.setattr(gc.time, "sleep", lambda *_a, **_kw: None)
        assert gc._get("http://x", retries=3, backoff=0.0) == {"ok": True}


class TestNormalizeVersion:
    """Tests for ``_normalize_version``."""

    def test_strips_plus(self):
        """SDMX 3 ``+`` wildcard is removed."""
        assert gc._normalize_version("1.0+.0") == "1.0.0"

    def test_no_plus(self):
        """Plain version is returned unchanged."""
        assert gc._normalize_version("1.0.0") == "1.0.0"


class TestEnglish:
    """Tests for ``_english``."""

    def test_none(self):
        """None returns empty string."""
        assert gc._english(None) == ""

    def test_string(self):
        """A bare string returns itself."""
        assert gc._english("foo") == "foo"

    def test_dict_with_en(self):
        """An ``en`` key wins."""
        assert gc._english({"en": "Hello", "fr": "Bonjour"}) == "Hello"

    def test_dict_without_en(self):
        """First value is used when ``en`` missing."""
        assert gc._english({"fr": "Bonjour"}) == "Bonjour"

    def test_dict_empty(self):
        """Empty dict returns empty string."""
        assert gc._english({}) == ""

    def test_non_string_value(self):
        """Non-string returns empty."""
        assert gc._english(123) == ""

    def test_dict_non_string_first(self):
        """Non-string fallback returns empty."""
        assert gc._english({"x": 1}) == ""


class TestParseStructureRef:
    """Tests for ``_parse_structure_ref``."""

    def test_valid(self):
        """Valid DSD URN parses fully."""
        urn = (
            "urn:sdmx:org.sdmx.infomodel.datastructure.DataStructure="
            "IMF.STA:DSD_X(1.0+.0)"
        )
        ref = gc._parse_structure_ref(urn)
        assert ref == {
            "agencyID": "IMF.STA",
            "id": "DSD_X",
            "version": "1.0.0",
            "package": "datastructure",
            "class": "DataStructure",
        }

    def test_invalid_returns_empty(self):
        """Unparsable URN yields empty dict."""
        assert gc._parse_structure_ref("garbage") == {}

    def test_none(self):
        """``None`` URN yields empty dict."""
        assert gc._parse_structure_ref(None) == {}


class TestParseConceptRef:
    """Tests for ``_parse_concept_ref``."""

    def test_valid(self):
        """Concept URN parses fully."""
        urn = (
            "urn:sdmx:org.sdmx.infomodel.conceptscheme.Concept=IMF.STA:CS_X(1.0+.0).GDP"
        )
        ref = gc._parse_concept_ref(urn)
        assert ref == {
            "maintainableParentID": "CS_X",
            "maintainableParentVersion": "1.0.0",
            "agencyID": "IMF.STA",
            "id": "GDP",
            "package": "conceptscheme",
            "class": "Concept",
        }

    def test_invalid(self):
        """Unparsable URN yields empty dict."""
        assert gc._parse_concept_ref("garbage") == {}


class TestParsePresentations:
    """Tests for ``_parse_presentations``."""

    def test_no_annotations(self):
        """Empty list returns empty list."""
        assert gc._parse_presentations([]) == []

    def test_skips_non_presentation(self):
        """Other annotation types are ignored."""
        out = gc._parse_presentations(
            [{"type": "OTHER", "text": "presentation_title=foo"}]
        )
        assert out == []

    def test_empty_text(self):
        """Empty text annotation is skipped."""
        out = gc._parse_presentations([{"type": "DATAFLOW_PRESENTATION"}])
        assert out == []

    def test_parses_entry(self):
        """Plain ``text`` is split on ';' and '='."""
        text = "presentation_title=Hello;presentation_description=Desc;extra=ignored"
        out = gc._parse_presentations([{"type": "DATAFLOW_PRESENTATION", "text": text}])
        assert out == [
            {"presentation_title": "Hello", "presentation_description": "Desc"}
        ]

    def test_uses_english_texts_when_text_missing(self):
        """Falls back to ``texts`` dict via ``_english``."""
        out = gc._parse_presentations(
            [
                {
                    "type": "DATAFLOW_PRESENTATION",
                    "texts": {"en": "presentation_title=From Texts"},
                }
            ]
        )
        assert out == [{"presentation_title": "From Texts"}]

    def test_part_without_equals_skipped(self):
        """Parts without '=' are silently skipped."""
        out = gc._parse_presentations(
            [
                {
                    "type": "DATAFLOW_PRESENTATION",
                    "text": "presentation_title=Foo;loose_part",
                }
            ]
        )
        assert out == [{"presentation_title": "Foo"}]

    def test_entry_with_no_known_keys(self):
        """Annotation with no known keys yields empty list."""
        out = gc._parse_presentations(
            [{"type": "DATAFLOW_PRESENTATION", "text": "random=value"}]
        )
        assert out == []


class TestFetchDataflows:
    """Tests for ``fetch_dataflows``."""

    def test_filters_vintage_and_normalizes(self, monkeypatch):
        """VINTAGE entries are filtered; non-VINTAGE entries normalized."""
        raw = {
            "data": {
                "dataflows": [
                    {
                        "id": "DF1",
                        "agencyID": "IMF.STA",
                        "version": "1.0+.0",
                        "name": "Flow One",
                        "description": "Desc One",
                        "structure": ("DataStructure=IMF.STA:DSD1(1.0+.0)"),
                        "annotations": [],
                    },
                    {
                        "id": "DF_2024_JAN_VINTAGE",
                        "agencyID": "IMF.STA",
                        "version": "1.0",
                    },
                    {"id": "", "agencyID": "IMF"},
                    {
                        "id": "DF2",
                        "agencyID": "IMF",
                        "version": "1.0",
                        "names": {"en": "Name two"},
                        "descriptions": {"en": "D2"},
                    },
                ]
            }
        }
        monkeypatch.setattr(gc, "_get", lambda *_a, **_kw: raw)
        out = gc.fetch_dataflows()
        assert set(out.keys()) == {"DF1", "DF2"}
        assert out["DF1"]["name"] == "Flow One"
        assert out["DF1"]["description"] == "Desc One"
        assert out["DF1"]["version"] == "1.0.0"
        assert out["DF1"]["structureRef"]["id"] == "DSD1"
        assert out["DF2"]["name"] == "Name two"
        assert out["DF2"]["description"] == "D2"


class TestConvertComponents:
    """Tests for ``_convert_components``."""

    def test_basic(self):
        """A component with position and conceptIdentity is fully populated."""
        comps = [
            {
                "id": "FREQ",
                "position": 1,
                "conceptIdentity": (
                    "urn:sdmx:org.sdmx.infomodel.conceptscheme.Concept="
                    "IMF:CS_X(1.0+.0).FREQ"
                ),
            },
            {"id": "OTHER"},
        ]
        out = gc._convert_components(comps)
        assert out[0]["id"] == "FREQ"
        assert out[0]["position"] == "1"
        assert out[0]["conceptRef"]["id"] == "FREQ"
        assert out[1] == {"id": "OTHER"}

    def test_empty(self):
        """An empty list returns empty list."""
        assert gc._convert_components([]) == []

    def test_none(self):
        """None returns empty list."""
        assert gc._convert_components(None) == []


class TestFetchDatastructures:
    """Tests for ``fetch_datastructures``."""

    def test_extract_dims_and_attrs(self, monkeypatch):
        """Dimensions and attributes are extracted and normalized."""
        raw = {
            "data": {
                "dataStructures": [
                    {
                        "id": "DSD1",
                        "agencyID": "IMF.STA",
                        "version": "1.0+.0",
                        "name": "X",
                        "dataStructureComponents": {
                            "dimensionList": {"dimensions": [{"id": "FREQ"}]},
                            "attributeList": {"attributes": [{"id": "UNIT"}]},
                        },
                    },
                    {"id": ""},
                    {
                        "id": "DSD2",
                        "agencyID": "IMF",
                        "version": "1.0",
                        "names": {"en": "From names"},
                    },
                ]
            }
        }
        monkeypatch.setattr(gc, "_get", lambda *_a, **_kw: raw)
        out = gc.fetch_datastructures()
        assert set(out.keys()) == {"DSD1", "DSD2"}
        assert out["DSD1"]["dimensions"][0]["id"] == "FREQ"
        assert out["DSD1"]["attributes"][0]["id"] == "UNIT"
        assert out["DSD2"]["name"] == "From names"


class TestFetchConceptschemes:
    """Tests for ``fetch_conceptschemes``."""

    def test_concepts_extracted(self, monkeypatch):
        """Concept schemes and their concepts come through normalized."""
        raw = {
            "data": {
                "conceptSchemes": [
                    {
                        "id": "CS1",
                        "agencyID": "IMF",
                        "version": "1.0",
                        "name": "CS One",
                        "concepts": [
                            {"id": "GDP", "name": "GDP concept"},
                            {"id": "", "name": "skipped"},
                            {"id": "POP", "names": {"en": "Pop"}},
                        ],
                    },
                    {"id": ""},
                    {
                        "id": "CS2",
                        "agencyID": "IMF",
                        "version": "1.0",
                        "names": {"en": "CS2 Name"},
                    },
                ]
            }
        }
        monkeypatch.setattr(gc, "_get", lambda *_a, **_kw: raw)
        out = gc.fetch_conceptschemes()
        assert set(out.keys()) == {"CS1", "CS2"}
        cs1_concepts = {c["id"]: c["name"] for c in out["CS1"]["concepts"]}
        assert cs1_concepts == {"GDP": "GDP concept", "POP": "Pop"}
        assert out["CS2"]["name"] == "CS2 Name"

    def test_concept_codelist_urn_extracted(self, monkeypatch):
        """A concept's ``coreRepresentation.enumeration`` URN is parsed into id+agency."""
        raw = {
            "data": {
                "conceptSchemes": [
                    {
                        "id": "CS_GS",
                        "agencyID": "IMF.STA",
                        "version": "4.0",
                        "name": "GS",
                        "concepts": [
                            {
                                "id": "GS_MS",
                                "name": "Marital Status",
                                "coreRepresentation": {
                                    "enumeration": (
                                        "urn:sdmx:org.sdmx.infomodel.codelist."
                                        "Codelist=IMF.STA:CL_GS_LI_MS(1.0+.0)"
                                    )
                                },
                            },
                            {
                                "id": "NO_ENUM",
                                "name": "No Enumeration",
                                "coreRepresentation": {},
                            },
                            {
                                "id": "BAD_URN",
                                "name": "Bad URN",
                                "coreRepresentation": {
                                    "enumeration": "not-a-codelist-urn"
                                },
                            },
                            {
                                "id": "ENUM_NOT_STR",
                                "name": "Enumeration is not a string",
                                "coreRepresentation": {"enumeration": {"x": "y"}},
                            },
                        ],
                    }
                ]
            }
        }
        monkeypatch.setattr(gc, "_get", lambda *_a, **_kw: raw)
        out = gc.fetch_conceptschemes()
        by_id = {c["id"]: c for c in out["CS_GS"]["concepts"]}
        assert by_id["GS_MS"]["codelist_id"] == "CL_GS_LI_MS"
        assert by_id["GS_MS"]["codelist_agency"] == "IMF.STA"
        assert "codelist_id" not in by_id["NO_ENUM"]
        assert "codelist_id" not in by_id["BAD_URN"]
        assert "codelist_id" not in by_id["ENUM_NOT_STR"]


class TestFetchCodelists:
    """Tests for ``fetch_codelists``."""

    def test_labels_and_descriptions(self, monkeypatch):
        """Codelists yield labels and descriptions per code."""
        raw = {
            "data": {
                "codelists": [
                    {
                        "id": "CL_X",
                        "codes": [
                            {
                                "id": "USA",
                                "names": {"en": "United States"},
                                "descriptions": {"en": "USA Desc"},
                            },
                            {
                                "id": "GBR",
                                "name": "United Kingdom",
                                "description": "UK Desc",
                            },
                            {"id": "OTHER"},
                            {"id": ""},
                        ],
                    },
                    {"id": ""},
                ]
            }
        }
        monkeypatch.setattr(gc, "_get", lambda *_a, **_kw: raw)
        codes_by_id, descs_by_id = gc.fetch_codelists()
        assert codes_by_id["CL_X"]["USA"] == "United States"
        assert codes_by_id["CL_X"]["GBR"] == "United Kingdom"
        # fallback: code_id becomes own label, label is fallback description
        assert codes_by_id["CL_X"]["OTHER"] == "OTHER"
        assert descs_by_id["CL_X"]["USA"] == "USA Desc"
        assert descs_by_id["CL_X"]["OTHER"] == "OTHER"


class TestFetchHierarchies:
    """Tests for ``fetch_hierarchies``."""

    def test_hierarchies_returned(self, monkeypatch):
        """Hierarchies are passed through, keyed by id."""
        raw = {
            "data": {
                "hierarchies": [
                    {"id": "H1", "extra": "stuff"},
                    {"id": ""},
                ]
            }
        }
        monkeypatch.setattr(gc, "_get", lambda *_a, **_kw: raw)
        out = gc.fetch_hierarchies()
        assert out == {"H1": {"id": "H1", "extra": "stuff"}}


class TestFetchOneConstraint:
    """Tests for ``_fetch_one_constraint``."""

    def test_extracts_keyvalues(self, monkeypatch):
        """Extracts ``keyValues`` entries from the response."""
        payload = {
            "data": {
                "dataConstraints": [
                    {
                        "cubeRegions": [
                            {
                                "keyValues": [
                                    {
                                        "id": "REF_AREA",
                                        "values": [
                                            {"value": "USA"},
                                            "GBR",
                                        ],
                                    },
                                    {"values": ["skipped"]},
                                ],
                                "components": [],
                            }
                        ]
                    }
                ]
            }
        }
        monkeypatch.setattr(gc, "_get", lambda *_a, **_kw: payload)
        key, out = gc._fetch_one_constraint("DF1", "IMF.STA")
        assert key == "DF1:all:all:available:all:()"
        kv = {x["id"]: set(x["values"]) for x in out["key_values"]}
        assert kv["REF_AREA"] == {"USA", "GBR"}

    def test_extracts_components(self, monkeypatch):
        """Extracts ``components`` entries from the response."""
        payload = {
            "data": {
                "dataConstraints": [
                    {
                        "cubeRegions": [
                            {
                                "keyValues": [],
                                "components": [
                                    {
                                        "id": "FREQ",
                                        "values": [
                                            {"value": "A"},
                                            "Q",
                                        ],
                                    },
                                    {"values": ["skip"]},
                                ],
                            }
                        ]
                    }
                ]
            }
        }
        monkeypatch.setattr(gc, "_get", lambda *_a, **_kw: payload)
        _key, out = gc._fetch_one_constraint("DF1", "IMF.STA")
        kv = {x["id"]: set(x["values"]) for x in out["key_values"]}
        assert kv["FREQ"] == {"A", "Q"}

    def test_returns_empty_on_get_exception(self, monkeypatch):
        """Exception from ``_get`` yields empty payload."""

        def fake_get(*_a, **_kw):
            raise requests.ConnectionError("boom")

        monkeypatch.setattr(gc, "_get", fake_get)
        key, out = gc._fetch_one_constraint("DF1", "IMF.STA")
        assert key == "DF1:all:all:available:all:()"
        assert out == {}

    def test_returns_empty_on_empty_response(self, monkeypatch):
        """Empty body produces empty result."""
        monkeypatch.setattr(gc, "_get", lambda *_a, **_kw: {})
        _key, out = gc._fetch_one_constraint("DF1", "IMF.STA")
        assert out == {}


class TestFetchConstraints:
    """Tests for ``fetch_constraints``."""

    def test_parallel_aggregates(self, monkeypatch):
        """Per-dataflow constraints are gathered in parallel."""

        def fake_fetch_one(df_id, _agency):
            if df_id == "FAIL":
                return f"{df_id}:all:all:available:all:()", {}
            return (
                f"{df_id}:all:all:available:all:()",
                {"key_values": [], "full_response": {}},
            )

        monkeypatch.setattr(gc, "_fetch_one_constraint", fake_fetch_one)

        dataflows = {
            "DF1": {"agencyID": "IMF"},
            "DF2": {"agencyID": "IMF"},
            "FAIL": {"agencyID": "IMF"},
        }
        out = gc.fetch_constraints(dataflows)
        assert "DF1:all:all:available:all:()" in out
        assert "DF2:all:all:available:all:()" in out
        assert "FAIL:all:all:available:all:()" not in out

    def test_exception_in_worker_counted(self, monkeypatch):
        """Future raising an exception is counted as a failure."""

        def fake_fetch_one(df_id, _agency):
            if df_id == "BOOM":
                raise RuntimeError("explode")
            return (
                f"{df_id}:all:all:available:all:()",
                {"key_values": [], "full_response": {}},
            )

        monkeypatch.setattr(gc, "_fetch_one_constraint", fake_fetch_one)
        dataflows = {"BOOM": {"agencyID": "IMF"}, "OK": {"agencyID": "IMF"}}
        out = gc.fetch_constraints(dataflows)
        assert "OK:all:all:available:all:()" in out
        assert "BOOM:all:all:available:all:()" not in out

    def test_progress_log_at_25_boundary(self, monkeypatch):
        """Logs every 25 dataflows and on the final entry."""

        def fake_fetch_one(df_id, _agency):
            return (
                f"{df_id}:all:all:available:all:()",
                {"key_values": [], "full_response": {}},
            )

        monkeypatch.setattr(gc, "_fetch_one_constraint", fake_fetch_one)
        dataflows = {f"DF{i}": {"agencyID": "IMF"} for i in range(26)}
        out = gc.fetch_constraints(dataflows)
        assert len(out) == 26


class TestDeriveDataflowGroups:
    """Tests for ``derive_dataflow_groups``."""

    def test_groups_and_sorts(self):
        """Dataflows are grouped by agency and sorted by id."""
        dataflows = {
            "DF2": {
                "urn": "u2",
                "agencyID": "A",
                "id": "DF2",
                "version": "1.0",
                "name": "n2",
                "description": "d2",
            },
            "DF1": {
                "urn": "u1",
                "agencyID": "A",
                "id": "DF1",
                "version": "1.0",
                "name": "n1",
                "description": "d1",
            },
            "DFX": {
                "urn": "ux",
                "agencyID": "B",
                "id": "DFX",
                "version": "1.0",
                "name": "nx",
                "description": "dx",
            },
        }
        groups = gc.derive_dataflow_groups(dataflows)
        assert [d["id"] for d in groups["A"]] == ["DF1", "DF2"]
        assert [d["id"] for d in groups["B"]] == ["DFX"]


class TestMain:
    """Tests for ``main``."""

    def test_main_writes_blob(self, monkeypatch, tmp_path):
        """``main`` collects fetchers and writes a compressed blob."""
        cache_file = tmp_path / "imf_cache.json.xz"
        assets_dir = tmp_path
        monkeypatch.setattr(gc, "CACHE_FILE", cache_file)
        monkeypatch.setattr(gc, "ASSETS_DIR", assets_dir)

        monkeypatch.setattr(
            gc,
            "fetch_dataflows",
            lambda: {
                "DF1": {
                    "agencyID": "IMF",
                    "id": "DF1",
                    "urn": "u",
                    "version": "1.0",
                    "name": "N",
                    "description": "D",
                }
            },
        )
        monkeypatch.setattr(gc, "fetch_datastructures", lambda: {"DSD": {}})
        monkeypatch.setattr(gc, "fetch_conceptschemes", lambda: {"CS": {}})
        monkeypatch.setattr(
            gc, "fetch_codelists", lambda: ({"CL": {"A": "Annual"}}, {"CL": {"A": "A"}})
        )
        monkeypatch.setattr(gc, "fetch_hierarchies", lambda: {"H": {}})
        monkeypatch.setattr(gc, "fetch_constraints", lambda _d: {"k": {}})

        result = gc.main()
        assert result is None
        assert cache_file.exists()

        with lzma.open(cache_file, "rb") as fh:
            blob = json.loads(fh.read().decode("utf-8"))

        assert set(blob.keys()) == {
            "dataflows",
            "datastructures",
            "conceptschemes",
            "dataflow_groups",
            "metadata_cache",
            "constraints_cache",
            "codelist_cache",
            "codelist_descriptions",
            "dataflow_parameters",
            "dataflow_indicators",
            "hierarchies",
        }
        assert blob["dataflows"]["DF1"]["id"] == "DF1"
        assert blob["dataflow_groups"]["IMF"][0]["id"] == "DF1"
        assert blob["constraints_cache"] == {"k": {}}
        assert blob["metadata_cache"] == {}


class TestModuleEntrypoint:
    """Tests to exercise the ``__main__`` guard."""

    def test_session_headers(self):
        """Module-level session has IMF-specific headers."""
        assert gc._session.headers["Accept"] == "application/json"
        assert "openbb-imf" in gc._session.headers["User-Agent"]

    def test_get_raises_unreachable_runtime_branch(self, monkeypatch):
        """Verify the unreachable ``raise`` after the loop is wired."""
        # We invoke _get with retries=0 — the for loop body never runs,
        # so we hit the final ``raise requests.RequestException`` line.
        monkeypatch.setattr(gc.time, "sleep", lambda *_a, **_kw: None)
        with pytest.raises(requests.RequestException, match="failed after"):
            gc._get("http://x", retries=0, backoff=0.0)


class TestSessionGetCalled:
    """Smoke test: confirm ``_session.get`` is wired in fetchers."""

    def test_fetch_dataflows_calls_session(self, monkeypatch):
        """The ``_get`` helper is hit and uses the seeded URL."""
        captured = {}

        def fake_session_get(url, timeout=300):
            captured["url"] = url
            return _FakeResp(200, {"data": {"dataflows": []}})

        monkeypatch.setattr(gc._session, "get", fake_session_get)
        gc.fetch_dataflows()
        assert "dataflow" in captured["url"]


class TestScriptEntrypoint:
    """Tests for the ``__main__`` guard."""

    @pytest.mark.filterwarnings("ignore::RuntimeWarning")
    def test_script_run_invokes_main_and_exits(self, monkeypatch, tmp_path):
        """Running the module as a script triggers ``sys.exit(main())``."""
        import runpy

        cache_file = tmp_path / "imf_cache.json.xz"

        def fake_session_get(self, *_a, **_kw):  # noqa: ARG001
            return _FakeResp(200, {"data": {}})

        monkeypatch.setattr("requests.sessions.Session.get", fake_session_get)
        monkeypatch.setattr(gc.time, "sleep", lambda *_a, **_kw: None)
        monkeypatch.setattr(
            "openbb_imf.utils.generate_cache.CACHE_FILE",
            cache_file,
            raising=True,
        )
        monkeypatch.setattr(
            "openbb_imf.utils.generate_cache.ASSETS_DIR",
            tmp_path,
            raising=True,
        )

        # runpy re-executes the module body in a fresh namespace; module-level
        # names (CACHE_FILE/ASSETS_DIR) get recomputed from the script path,
        # so we also need to redirect lzma.open and Path.mkdir for safety.
        real_open = lzma.open

        def safe_lzma_open(*_a, **kw):
            return real_open(cache_file, "wb", format=lzma.FORMAT_XZ, preset=6)

        monkeypatch.setattr(lzma, "open", safe_lzma_open)

        from pathlib import Path as _P

        real_mkdir = _P.mkdir

        def fake_mkdir(self, *_a, **_kw):
            return real_mkdir(tmp_path, parents=True, exist_ok=True)

        monkeypatch.setattr(_P, "mkdir", fake_mkdir)

        # Stub stat so the post-write size lookup hits our tmp file.
        # Pass-through for any other path (pathlib's ``is_dir``/``mkdir``
        # internals also call ``Path.stat``; redirecting those breaks the
        # ``exist_ok=True`` recovery path on Python 3.10).
        real_stat = _P.stat

        def fake_stat(self, *args, **kw):
            target = cache_file if str(self).endswith("imf_cache.json.xz") else self
            return real_stat(target, *args, **kw)

        monkeypatch.setattr(_P, "stat", fake_stat)

        with pytest.raises(SystemExit):
            runpy.run_module("openbb_imf.utils.generate_cache", run_name="__main__")
