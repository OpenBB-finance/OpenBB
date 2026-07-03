"""Tests for ``openbb_government_ca.utils.generate_cache``.

Covers:
- ``build_blob()`` — top-level orchestrator and degraded-mode handling
- ``_parse_homepage_response()`` — StatsCan ind-econ.json parser
- ``_fetch_statscan()`` — network fetcher with graceful error handling
- ``_write_cache()`` — LZMA-compressed JSON writer
- ``main()`` — CLI entry point
"""

from __future__ import annotations

import json
import lzma
from pathlib import Path
from unittest.mock import patch

import pytest

from openbb_government_ca.utils import generate_cache
from openbb_government_ca.utils._http import NetworkError

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------
_FIXTURE_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def homepage_sample() -> dict:
    """Load the synthetic ind-econ.json sample from the fixtures dir."""
    with (_FIXTURE_DIR / "statcan_ind_econ_sample.json").open() as f:
        return json.load(f)


@pytest.fixture
def degraded_statscan_blob() -> dict:
    """The shape returned by ``_fetch_statscan`` when the network fails."""
    return {
        "homepage_url": generate_cache.STATSCAN_HOMEPAGE_URL,
        "indicators": [],
        "geo_lookup": {},
        "themes_en": {},
        "themes_fr": {},
        "indicator_count": 0,
        "status": "degraded",
        "warning": "statscan homepage unreachable at build time: ...",
    }


# ---------------------------------------------------------------------------
# _parse_homepage_response
# ---------------------------------------------------------------------------
class TestParseHomepageResponse:
    """The StatsCan homepage parser handles the documented response shape."""

    def test_parses_documented_shape(self, homepage_sample):
        """The official documented shape (with ``results`` wrapper) parses."""
        parsed = generate_cache._parse_homepage_response(homepage_sample)
        assert parsed["indicator_count"] == 3
        assert parsed["homepage_url"] == generate_cache.STATSCAN_HOMEPAGE_URL

    def test_extracts_indicator_titles(self, homepage_sample):
        """Each indicator's English title is preserved."""
        parsed = generate_cache._parse_homepage_response(homepage_sample)
        titles = [i["title_en"] for i in parsed["indicators"]]
        assert "Imports" in titles
        assert "Employment" in titles
        assert "Capital expenditures: Machinery and equipment" in titles

    def test_extracts_source_vector_ids(self, homepage_sample):
        """The ``source`` field (vector ID) is preserved as a string."""
        parsed = generate_cache._parse_homepage_response(homepage_sample)
        sources = [i["source"] for i in parsed["indicators"]]
        assert "2280069" in sources  # Imports
        assert "2820087" in sources  # Employment
        assert "290045" in sources  # Capital expenditures

    def test_builds_observations_url(self, homepage_sample):
        """Each indicator carries a pre-built ``observations_url`` for Phase 4."""
        parsed = generate_cache._parse_homepage_response(homepage_sample)
        for ind in parsed["indicators"]:
            assert ind["observations_url"].startswith(
                "https://www150.statcan.gc.ca/t1/wds/rest/getDataVector"
            )
            assert f"vectorId={ind['source']}" in ind["observations_url"]

    def test_builds_geo_lookup(self, homepage_sample):
        """The ``geo`` list is collapsed into a ``geo_code -> label`` map."""
        parsed = generate_cache._parse_homepage_response(homepage_sample)
        assert parsed["geo_lookup"]["0"] == "Canada"
        assert parsed["geo_lookup"]["1"] == "Newfoundland and Labrador"
        assert parsed["geo_lookup"]["13"] == "Nunavut"

    def test_builds_theme_lookup(self, homepage_sample):
        """English and French theme lookups are built separately."""
        parsed = generate_cache._parse_homepage_response(homepage_sample)
        assert parsed["themes_en"]["920"] == "Agriculture"
        assert parsed["themes_en"]["2239"] == "Business performance and ownership"
        assert parsed["themes_fr"]["920"] == "Agriculture"

    def test_preserves_growth_rate_info(self, homepage_sample):
        """Growth rate (percentage + arrow direction + details) is preserved."""
        parsed = generate_cache._parse_homepage_response(homepage_sample)
        imports = next(i for i in parsed["indicators"] if i["title_en"] == "Imports")
        assert imports["growth_en"] == "4.7%"
        assert imports["growth_arrow"] == "1"
        assert imports["growth_details_en"] == "(monthly change)"

    def test_preserves_release_date(self, homepage_sample):
        """``release_date`` is preserved as a string."""
        parsed = generate_cache._parse_homepage_response(homepage_sample)
        for ind in parsed["indicators"]:
            assert ind["release_date"]  # non-empty

    def test_handles_unwrapped_indicators(self):
        """The parser tolerates indicators at the top level (no ``results`` wrapper)."""
        payload = {
            "indicators": [
                {
                    "registry_number": "1",
                    "indicator_number": "1",
                    "geo_code": "0",
                    "title": {"en": "Test", "fr": "Test"},
                    "value": {"en": "1.0", "fr": "1,0"},
                    "refper": {"en": "2024-01", "fr": "2024-01"},
                    "source": "1234567",
                    "release_date": "2024-02-01",
                    "growth_rate": {},
                }
            ],
            "geo": [],
            "themes_en": [],
            "themes_fr": [],
        }
        parsed = generate_cache._parse_homepage_response(payload)
        assert parsed["indicator_count"] == 1
        assert parsed["indicators"][0]["title_en"] == "Test"
        assert parsed["indicators"][0]["source"] == "1234567"

    def test_handles_none_payload(self):
        """A ``None`` payload produces an empty (but well-formed) blob."""
        parsed = generate_cache._parse_homepage_response(None)
        assert parsed["indicator_count"] == 0
        assert parsed["indicators"] == []

    def test_handles_non_dict_payload(self):
        """A non-dict payload (e.g. a bare list) produces an empty blob."""
        parsed = generate_cache._parse_homepage_response(["unexpected"])
        assert parsed["indicator_count"] == 0

    def test_skips_non_dict_indicators(self):
        """Non-dict entries in the indicators list are silently skipped."""
        payload = {
            "results": {
                "indicators": [
                    "not-a-dict",
                    {"source": "1", "title": {"en": "OK"}},
                    None,
                ],
                "geo": [],
                "themes_en": [],
                "themes_fr": [],
            }
        }
        parsed = generate_cache._parse_homepage_response(payload)
        assert parsed["indicator_count"] == 1
        assert parsed["indicators"][0]["source"] == "1"

    def test_handles_missing_optional_fields(self):
        """An indicator with only required fields still parses."""
        payload = {
            "results": {
                "indicators": [
                    {"source": "999", "title": {"en": "Minimal"}},
                ],
                "geo": [],
                "themes_en": [],
                "themes_fr": [],
            }
        }
        parsed = generate_cache._parse_homepage_response(payload)
        ind = parsed["indicators"][0]
        assert ind["source"] == "999"
        assert ind["title_en"] == "Minimal"
        # Optional fields default to empty strings.
        assert ind["value_en"] == ""
        assert ind["refper_en"] == ""
        assert ind["growth_en"] == ""
        # observations_url is built from source.
        assert "vectorId=999" in ind["observations_url"]

    def test_indicator_without_source_has_empty_url(self):
        """An indicator without a ``source`` field gets an empty ``observations_url``."""
        payload = {
            "results": {
                "indicators": [{"title": {"en": "No source"}}],
                "geo": [],
                "themes_en": [],
                "themes_fr": [],
            }
        }
        parsed = generate_cache._parse_homepage_response(payload)
        assert parsed["indicators"][0]["observations_url"] == ""


# ---------------------------------------------------------------------------
# _fetch_statscan (network layer with graceful degradation)
# ---------------------------------------------------------------------------
class TestFetchStatscan:
    """``_fetch_statscan`` handles network failures gracefully."""

    def test_success_path(self, homepage_sample):
        """A successful fetch returns a parsed blob with ``status='ok'``."""
        with patch(
            "openbb_government_ca.utils.generate_cache.http_get_json",
            return_value=homepage_sample,
        ):
            result = generate_cache._fetch_statscan()
        assert result["status"] == "ok"
        assert result["indicator_count"] == 3
        assert "warning" not in result

    def test_network_failure_returns_degraded_blob(self):
        """A ``NetworkError`` is caught and produces a degraded blob.

        This is the user's explicit requirement: "si StatsCan se cae al
        instalar el paquete, el hatch hook no deberia hacer que pip
        install falle catastroficamente sin explicacion".
        """
        with patch(
            "openbb_government_ca.utils.generate_cache.http_get_json",
            side_effect=NetworkError(
                "https://example.com", "connection failed: timeout"
            ),
        ):
            result = generate_cache._fetch_statscan()
        assert result["status"] == "degraded"
        assert result["indicator_count"] == 0
        assert "warning" in result
        assert "connection failed" in result["warning"]

    def test_degraded_blob_has_homepage_url(self):
        """A degraded blob still carries the homepage URL for reference."""
        with patch(
            "openbb_government_ca.utils.generate_cache.http_get_json",
            side_effect=NetworkError("https://example.com", "down"),
        ):
            result = generate_cache._fetch_statscan()
        assert result["homepage_url"] == generate_cache.STATSCAN_HOMEPAGE_URL

    def test_degraded_blob_has_empty_indicators(self):
        """A degraded blob has an empty (but present) indicators list."""
        with patch(
            "openbb_government_ca.utils.generate_cache.http_get_json",
            side_effect=NetworkError("https://example.com", "down"),
        ):
            result = generate_cache._fetch_statscan()
        assert result["indicators"] == []
        assert result["geo_lookup"] == {}


# ---------------------------------------------------------------------------
# build_blob (top-level orchestrator)
# ---------------------------------------------------------------------------
class TestBuildBlob:
    """``build_blob()`` always returns a well-formed blob, even on partial failure."""

    @pytest.fixture(autouse=True)
    def _mock_fetchers(self, monkeypatch):
        """Mock both fetchers so ``build_blob`` never hits the network.

        Individual tests can override the mock by re-patching within
        the test body. This fixture is ``autouse`` so a test that
        forgets to mock doesn't hang on a real network call.
        """
        monkeypatch.setattr(
            generate_cache,
            "_fetch_boc",
            lambda: {
                "valet_url": "https://www.bankofcanada.ca/valet",
                "series": {},
                "groups": {},
                "series_count": 0,
                "groups_count": 0,
                "status": "ok",
            },
        )
        monkeypatch.setattr(
            generate_cache,
            "_fetch_statscan",
            lambda: {
                "homepage_url": generate_cache.STATSCAN_HOMEPAGE_URL,
                "indicators": [],
                "geo_lookup": {},
                "themes_en": {},
                "themes_fr": {},
                "indicator_count": 0,
                "status": "ok",
            },
        )

    def test_returns_dict_with_required_keys(self):
        """The blob has the four required top-level keys."""
        blob = generate_cache.build_blob()
        for key in ("generated_at", "source", "boc", "statscan"):
            assert key in blob

    def test_boc_section_is_well_formed(self):
        """The ``boc`` section has ``series`` and ``groups`` sub-maps."""
        boc = generate_cache.build_blob()["boc"]
        assert "series" in boc and isinstance(boc["series"], dict)
        assert "groups" in boc and isinstance(boc["groups"], dict)

    def test_statscan_section_is_well_formed(self):
        """The ``statscan`` section has ``indicators`` list and ``geo_lookup`` map."""
        statscan = generate_cache.build_blob()["statscan"]
        assert "indicators" in statscan
        assert "geo_lookup" in statscan

    def test_generated_at_is_iso8601(self):
        """``generated_at`` is an ISO 8601 UTC timestamp ending in ``Z``."""
        ts = generate_cache.build_blob()["generated_at"]
        assert isinstance(ts, str)
        assert ts.endswith("Z")
        assert len(ts) == 20  # YYYY-MM-DDTHH:MM:SSZ

    def test_source_is_build_hook(self):
        """``source`` is the literal string ``'build-hook'``."""
        assert generate_cache.build_blob()["source"] == "build-hook"

    def test_both_sections_degraded_still_returns_blob(self, monkeypatch):
        """When both fetchers fail, ``build_blob`` still returns a valid blob."""
        monkeypatch.setattr(
            generate_cache,
            "_fetch_boc",
            lambda: {
                "valet_url": "https://www.bankofcanada.ca/valet",
                "series": {},
                "groups": {},
                "series_count": 0,
                "groups_count": 0,
                "status": "degraded",
                "warning": "boc down",
            },
        )
        monkeypatch.setattr(
            generate_cache,
            "_fetch_statscan",
            lambda: {
                "status": "degraded",
                "indicators": [],
                "warning": "statscan down",
            },
        )
        blob = generate_cache.build_blob()
        assert blob["boc"]["status"] == "degraded"
        assert blob["statscan"]["status"] == "degraded"

    def test_partial_success(self, monkeypatch, homepage_sample):
        """When one section succeeds and the other fails, the blob carries both."""
        monkeypatch.setattr(
            generate_cache,
            "_fetch_statscan",
            lambda: {
                "status": "ok",
                "indicators": [{"source": "1", "title_en": "X"}],
                "indicator_count": 1,
            },
        )
        blob = generate_cache.build_blob()
        assert blob["statscan"]["status"] == "ok"
        assert blob["statscan"]["indicator_count"] == 1


# ---------------------------------------------------------------------------
# _write_cache
# ---------------------------------------------------------------------------
class TestWriteCache:
    """``_write_cache`` produces a valid LZMA-compressed JSON file."""

    def test_creates_file(self, tmp_path: Path):
        target = tmp_path / "out.json.xz"
        result = generate_cache._write_cache({"hello": "world"}, target)
        assert result == target
        assert target.exists()
        assert target.stat().st_size > 0

    def test_file_is_lzma_compressed(self, tmp_path: Path):
        target = tmp_path / "out.json.xz"
        generate_cache._write_cache({"hello": "world"}, target)
        with lzma.open(target, "rb") as f:
            data = json.loads(f.read().decode("utf-8"))
        assert data == {"hello": "world"}

    def test_creates_parent_dirs(self, tmp_path: Path):
        target = tmp_path / "nested" / "deep" / "out.json.xz"
        generate_cache._write_cache({}, target)
        assert target.exists()

    def test_none_path_uses_module_default(self, tmp_path, monkeypatch):
        """When ``path=None``, the module-level ``_CACHE_FILE`` is used."""
        monkeypatch.setattr(generate_cache, "_CACHE_FILE", tmp_path / "c.json.xz")
        result = generate_cache._write_cache({"a": 1})
        assert result == tmp_path / "c.json.xz"
        assert (tmp_path / "c.json.xz").exists()


# ---------------------------------------------------------------------------
# main (CLI entry point)
# ---------------------------------------------------------------------------
class TestMainCLI:
    """The ``main()`` CLI writes the cache and returns 0."""

    def test_writes_default_cache_file(self, monkeypatch, tmp_path: Path):
        """``main()`` writes to ``_CACHE_FILE`` and returns 0."""
        monkeypatch.setattr(generate_cache, "_CACHE_FILE", tmp_path / "c.json.xz")
        monkeypatch.setattr(
            generate_cache, "_fetch_boc", lambda: {"series": {}, "groups": {}}
        )
        monkeypatch.setattr(
            generate_cache,
            "_fetch_statscan",
            lambda: {"indicators": [], "indicator_count": 0, "status": "ok"},
        )
        rc = generate_cache.main()
        assert rc == 0
        assert (tmp_path / "c.json.xz").exists()

    def test_returns_0_even_on_network_failure(self, monkeypatch, tmp_path: Path):
        """``main()`` returns 0 even when StatsCan is unreachable.

        This is the user's explicit requirement: a network failure
        during install must not break ``pip install``.
        """
        monkeypatch.setattr(generate_cache, "_CACHE_FILE", tmp_path / "c.json.xz")
        monkeypatch.setattr(
            generate_cache,
            "_fetch_statscan",
            lambda: {"status": "degraded", "indicators": [], "warning": "down"},
        )
        rc = generate_cache.main()
        assert rc == 0
        # The degraded cache is still written.
        assert (tmp_path / "c.json.xz").exists()

    def test_returns_2_on_malformed_blob(self, monkeypatch, tmp_path: Path):
        """``main()`` returns 2 if the blob is missing required keys."""
        monkeypatch.setattr(generate_cache, "_CACHE_FILE", tmp_path / "c.json.xz")
        monkeypatch.setattr(generate_cache, "build_blob", lambda: {"bad": "blob"})
        rc = generate_cache.main()
        assert rc == 2
