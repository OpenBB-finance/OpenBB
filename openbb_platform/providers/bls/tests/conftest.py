"""Shared pytest fixtures for the openbb-bls test suite.

Cassette-management strategy
----------------------------

Small HTML scrapes and small XLSX downloads (≤200 KB) are recorded straight to
VCR cassettes under ``tests/record/http/test_bls_fetchers/`` and replayed on
subsequent runs.

Bulky XLSX downloads (productivity prod2 workbooks ~4 MB, JOLTS revision
workbooks ~1.6 MB each) bypass VCR. The ``mock_bls_xlsx_downloads`` fixture
monkeypatches the utility-layer fetch helpers to return tiny pre-built
workbooks shipped under ``tests/fixtures/*.xlsx``. Regenerate those fixtures
with ``python tests/fixtures/build_fixtures.py`` when parser expectations
change.

Recording / replay
------------------

This repo uses ``pytest_recorder`` (not ``pytest-recording``). To populate
missing cassettes on first run::

    pytest --record http

Subsequent runs use ``pytest`` with no flag — cassettes are replayed from
disk in ``record_mode='none'`` and will fail loudly if the underlying HTTP
request changes shape. Use ``--record all`` to force a re-record of every
cassette (network-heavy).
"""

import io
import json
import zipfile
from pathlib import Path

import pytest
from openbb_core.app.service.user_service import UserService

from openbb_bls.utils.metadata import BlsMetadata

_FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture(autouse=True)
def _reset_bls_metadata_singleton():
    """Reset ``BlsMetadata`` before and after every test.

    The singleton stashes archive bytes + memoised dataframes on the
    class. Each test must start from a clean slate so per-test
    monkeypatching of ``_SHIPPED_CACHE_FILE`` is honoured.
    """
    BlsMetadata._reset()
    yield
    BlsMetadata._reset()


def _make_stub_zip(
    categories: dict[str, dict] | None = None,
    series_rows: dict[str, list[dict]] | None = None,
    codes: dict[str, dict] | None = None,
    include_index: bool = True,
) -> bytes:
    """Build a small ``bls_cache.zip`` payload for unit testing.

    Parameters
    ----------
    categories : dict
        Mapping of category key to its ``index.json`` entry.
    series_rows : dict
        ``{category: [row, ...]}`` where each row is a CSV record.
    codes : dict
        ``{category: codes_dict}`` to be serialised under ``codes.json``.
    include_index : bool
        Whether to write the ``index.json`` member.

    Returns
    -------
    bytes
        Compressed ZIP archive bytes.
    """
    categories = categories or {}
    series_rows = series_rows or {}
    codes = codes or {}
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        if include_index:
            zf.writestr(
                "index.json",
                json.dumps({"categories": categories}).encode("utf-8"),
            )
        for cat, rows in series_rows.items():
            if not rows:
                continue
            keys: list[str] = []
            seen: set[str] = set()
            for r in rows:
                for k in r:
                    if k not in seen:
                        seen.add(k)
                        keys.append(k)
            import csv

            sbuf = io.StringIO()
            writer = csv.DictWriter(sbuf, fieldnames=keys)
            writer.writeheader()
            for row in rows:
                writer.writerow(row)
            zf.writestr(f"{cat}/series.csv", sbuf.getvalue().encode("utf-8"))
        for cat, code_map in codes.items():
            zf.writestr(
                f"{cat}/codes.json",
                json.dumps(code_map).encode("utf-8"),
            )
    return buf.getvalue()


@pytest.fixture
def make_stub_zip():
    """Return a factory that builds an in-memory stub ``bls_cache.zip``."""
    return _make_stub_zip


@pytest.fixture
def stub_cache_path(tmp_path, make_stub_zip, monkeypatch):
    """Materialise a stub ``bls_cache.zip`` and point the loader at it."""
    archive = tmp_path / "bls_cache.zip"
    payload = make_stub_zip(
        categories={
            "cpi": {
                "name": "Consumer Price Index",
                "surveys": ["cu"],
                "series_count": 2,
            },
            "ppi": {
                "name": "Producer Price Index",
                "surveys": ["wp"],
                "series_count": 1,
            },
        },
        series_rows={
            "cpi": [
                {
                    "series_id": "CUUR0000SA0",
                    "series_title": "All items in U.S. city average",
                    "survey_name": "Consumer Price Index - All Urban Consumers",
                    "area_code": "U.S. city average",
                },
                {
                    "series_id": "CUUR0000SAF1",
                    "series_title": "Food in U.S. city average",
                    "survey_name": "Consumer Price Index - All Urban Consumers",
                    "area_code": "U.S. city average",
                },
            ],
            "ppi": [
                {
                    "series_id": "WPU01",
                    "series_title": "Farm products",
                    "survey_name": "Producer Price Index - Commodity",
                },
            ],
        },
        codes={
            "cpi": {
                "cu": {"area_code": {"0000": "U.S. city average"}},
            },
        },
    )
    archive.write_bytes(payload)
    monkeypatch.setattr(
        "openbb_bls.utils.metadata._core._SHIPPED_CACHE_FILE",
        archive,
    )
    return archive


@pytest.fixture(scope="session")
def test_credentials() -> dict:
    """Return the default user credentials envelope used by fetcher tests."""
    return UserService().default_user_settings.credentials.model_dump(mode="json")


@pytest.fixture(scope="module")
def vcr_config() -> dict:
    """VCR config shared across the test module."""
    return {
        "filter_headers": [("User-Agent", None)],
        "filter_post_data_parameters": [("registrationkey", "MOCK_API_KEY")],
        "filter_query_parameters": [("registrationkey", "MOCK_API_KEY")],
        "decode_compressed_response": True,
    }


@pytest.fixture(scope="session")
def fixture_bytes():
    """Return a loader for bundled binary fixtures under ``tests/fixtures/``."""

    def _load(name: str) -> bytes:
        path = _FIXTURES_DIR / name
        if not path.exists():
            raise FileNotFoundError(
                f"Missing test fixture {path}. Run "
                "`python tests/fixtures/build_fixtures.py` to regenerate."
            )
        return path.read_bytes()

    return _load


class _FakeResponse:
    """Minimal stand-in for ``requests.Response`` used by patched fetchers."""

    def __init__(self, content: bytes, status_code: int = 200):
        self.content = content
        self.status_code = status_code
        self.text = (
            content.decode("utf-8", errors="replace")
            if isinstance(content, bytes)
            else content
        )

    def raise_for_status(self) -> None:
        """No-op — fixture responses are always 200."""


def _patch_module_attrs(monkeypatch, module, attrs: dict) -> None:
    """Set multiple attributes on a module via ``monkeypatch.setattr``."""
    for name, value in attrs.items():
        if hasattr(module, name):
            monkeypatch.setattr(module, name, value)


@pytest.fixture
def mock_bls_http(monkeypatch, fixture_bytes):
    """Intercept every BLS scrape/fetch helper so tests never hit the network.

    Patches are applied to the MODEL-side import binding (``from x import y``
    creates a separate name in the model that ``setattr(x, "y", ...)`` does
    not reach). Document-listing fetchers get canned ``scrape_archive``
    results; table fetchers get bundled small XLSX / TXT / HTML fixtures
    routed through the real parsers.
    """
    from datetime import date as _date

    # ----- Document-listing fetchers — canned scrape results ----------------
    import openbb_bls.models.cpi_documents as cpi_docs_mod
    import openbb_bls.models.empsit_documents as empsit_docs_mod
    import openbb_bls.models.jolts_documents as jolts_docs_mod
    import openbb_bls.models.ppi_documents as ppi_docs_mod
    import openbb_bls.models.productivity_documents as prod_docs_mod
    import openbb_bls.models.realer_documents as realer_docs_mod
    import openbb_bls.models.ximpim_documents as ximpim_docs_mod

    _patch_module_attrs(
        monkeypatch,
        cpi_docs_mod,
        {
            "scrape_archive": lambda: (
                {
                    "date": _date(2026, 5, 12),
                    "title": "April 2026 Consumer Price Index",
                    "url": "https://www.bls.gov/news.release/archives/cpi_05122026.pdf",
                },
                {
                    "date": _date(2026, 4, 10),
                    "title": "March 2026 Consumer Price Index",
                    "url": "https://www.bls.gov/news.release/archives/cpi_04102026.pdf",
                },
            ),
            "current_release": lambda: {
                "title": "Consumer Price Index — current release",
                "url": "https://www.bls.gov/news.release/pdf/cpi.pdf",
                "html_url": "https://www.bls.gov/news.release/cpi.nr0.htm",
            },
        },
    )

    _patch_module_attrs(
        monkeypatch,
        empsit_docs_mod,
        {
            "scrape_archive": lambda: (
                {
                    "date": _date(2026, 5, 8),
                    "title": "April 2026 Employment Situation",
                    "url": "https://www.bls.gov/news.release/archives/empsit_05082026.pdf",
                },
                {
                    "date": _date(2026, 3, 7),
                    "title": "February 2026 Employment Situation",
                    "url": "https://www.bls.gov/news.release/archives/empsit_03072026.pdf",
                },
            ),
            "current_release": lambda: {
                "title": "Employment Situation — current release",
                "url": "https://www.bls.gov/news.release/pdf/empsit.pdf",
                "html_url": "https://www.bls.gov/news.release/empsit.nr0.htm",
            },
        },
    )

    _patch_module_attrs(
        monkeypatch,
        realer_docs_mod,
        {
            "scrape_archive": lambda: (
                {
                    "date": _date(2026, 5, 12),
                    "title": "April 2026 Real Earnings",
                    "url": "https://www.bls.gov/news.release/archives/realer_05122026.pdf",
                },
                {
                    "date": _date(2026, 4, 10),
                    "title": "March 2026 Real Earnings",
                    "url": "https://www.bls.gov/news.release/archives/realer_04102026.pdf",
                },
            ),
            "current_release": lambda: {
                "title": "Real Earnings — current release",
                "url": "https://www.bls.gov/news.release/pdf/realer.pdf",
                "html_url": "https://www.bls.gov/news.release/realer.nr0.htm",
            },
        },
    )

    _patch_module_attrs(
        monkeypatch,
        ximpim_docs_mod,
        {
            "scrape_archive": lambda: (
                {
                    "date": _date(2026, 5, 14),
                    "title": "April 2026 U.S. Import and Export Price Indexes",
                    "url": "https://www.bls.gov/news.release/archives/ximpim_05142026.pdf",
                },
                {
                    "date": _date(2026, 4, 15),
                    "title": "March 2026 U.S. Import and Export Price Indexes",
                    "url": "https://www.bls.gov/news.release/archives/ximpim_04152026.pdf",
                },
            ),
            "current_release": lambda: {
                "title": "U.S. Import and Export Price Indexes — current release",
                "url": "https://www.bls.gov/news.release/pdf/ximpim.pdf",
                "html_url": "https://www.bls.gov/news.release/ximpim.nr0.htm",
            },
        },
    )

    _JOLTS_ARCH = {
        "jolts": (
            {
                "date": _date(2026, 5, 5),
                "title": "March 2026",
                "pdf_url": "https://www.bls.gov/news.release/archives/jolts_05052026.pdf",
            },
        ),
        "jltst": (
            {
                "date": _date(2026, 2, 19),
                "title": "December 2025",
                "pdf_url": "https://www.bls.gov/news.release/archives/jltst_02192026.pdf",
            },
        ),
    }
    _patch_module_attrs(
        monkeypatch,
        jolts_docs_mod,
        {
            "list_releases": lambda: [
                {
                    "code": "jolts",
                    "category": "national",
                    "title": "JOLTS — National (current release)",
                    "pdf_url": "https://www.bls.gov/news.release/pdf/jolts.pdf",
                },
                {
                    "code": "jltst",
                    "category": "state",
                    "title": "JOLTS — State estimates (current release)",
                    "pdf_url": "https://www.bls.gov/news.release/pdf/jltst.pdf",
                },
            ],
            "scrape_archive": lambda code: _JOLTS_ARCH.get(code, ()),
        },
    )

    _PROD_ARCH = {
        "prod2": (
            {
                "code": "prod2",
                "date": _date(2026, 5, 7),
                "title": "2026 First Quarter (Preliminary) Productivity and Costs",
                "html_url": None,
                "pdf_url": "https://www.bls.gov/news.release/archives/prod2_05072026.pdf",
            },
        ),
        "prod3": (
            {
                "code": "prod3",
                "date": _date(2026, 3, 19),
                "title": "2025 Total Factor Productivity",
                "html_url": None,
                "pdf_url": "https://www.bls.gov/news.release/archives/prod3_03192026.pdf",
            },
        ),
    }
    _patch_module_attrs(
        monkeypatch,
        prod_docs_mod,
        {
            "scrape_release_catalog": lambda: (
                {
                    "code": "prod2",
                    "category": "labor_productivity",
                    "title": "Productivity and Costs",
                    "pdf_url": "https://www.bls.gov/news.release/pdf/prod2.pdf",
                    "news_release_url": "https://www.bls.gov/news.release/prod2.nr0.htm",
                    "toc_url": "https://www.bls.gov/news.release/prod2.toc.htm",
                    "supplemental_toc_url": "https://www.bls.gov/web/prod2.supp.toc.htm",
                },
                {
                    "code": "prod3",
                    "category": "total_factor_productivity",
                    "title": "Total Factor Productivity",
                    "pdf_url": "https://www.bls.gov/news.release/pdf/prod3.pdf",
                    "news_release_url": "https://www.bls.gov/news.release/prod3.nr0.htm",
                    "toc_url": "https://www.bls.gov/news.release/prod3.toc.htm",
                    "supplemental_toc_url": None,
                },
            ),
            "scrape_archive": lambda code: _PROD_ARCH.get(code, ()),
        },
    )

    _patch_module_attrs(
        monkeypatch,
        ppi_docs_mod,
        {
            "_scrape_detailed_report_index": lambda: (
                {
                    "name": "PPI Detailed Report — April 2026",
                    "url": "https://www.bls.gov/ppi/detailed-report/"
                    "ppi-detailed-report-april-2026.pdf",
                    "category": "detailed_report",
                    "date": _date(2026, 4, 1),
                    "format": "pdf",
                },
            ),
        },
    )

    # ----- Table fetchers — bundled XLSX / TXT / HTML fixtures --------------

    import openbb_bls.models.ces_analytical_tables as ces_mod
    import openbb_bls.models.cpi_news_release as cpi_nr_mod
    import openbb_bls.models.cpi_relative_importance as cri_mod
    import openbb_bls.models.cpi_seasonal_factors as csf_mod
    import openbb_bls.models.cpi_supplemental_tables as cst_mod
    import openbb_bls.models.jolts_revisions as jolts_rev_mod
    import openbb_bls.models.jolts_tables as jolts_tab_mod
    import openbb_bls.models.ppi_seasonal_factors as psf_mod
    import openbb_bls.models.productivity_tables as prod_tab_mod

    # CES analytical tables resolve through stable /web/empsit/ces*.xlsx URLs;
    # serve each stem from its bundled trimmed fixture.
    _patch_module_attrs(
        monkeypatch,
        ces_mod,
        {
            "fetch_table_xlsx": lambda stem: fixture_bytes(f"{stem}.xlsx"),
        },
    )

    # Import/export chart pages: serve each chart's trimmed HTML table fixture.
    import openbb_bls.utils.ximpim_charts as ximpim_charts_mod

    _xc_slug_to_key = {v: k for k, v in ximpim_charts_mod.CHART_SLUGS.items()}

    def _xc_fetch(slug):
        key = _xc_slug_to_key[slug]
        return fixture_bytes(f"ximpim_chart_{key}.html").decode("utf-8")

    _patch_module_attrs(
        monkeypatch,
        ximpim_charts_mod,
        {
            "fetch_chart_html": _xc_fetch,
        },
    )

    # Employment Situation chart pages: serve each chart's trimmed HTML fixture.
    import openbb_bls.utils.empsit_charts as empsit_charts_mod

    _ec_slug_to_key = {
        spec["slug"]: key for key, spec in empsit_charts_mod.CHART_SPECS.items()
    }

    def _ec_fetch(slug):
        key = _ec_slug_to_key[slug]
        return fixture_bytes(f"empsit_chart_{key}.html").decode("utf-8")

    _patch_module_attrs(
        monkeypatch,
        empsit_charts_mod,
        {
            "fetch_chart_html": _ec_fetch,
        },
    )

    # Employment Situation summary tables A/B: serve trimmed HTML fixtures.
    import openbb_bls.utils.empsit_summary as empsit_summary_mod

    _es_slug_to_key = {
        spec["slug"]: key for key, spec in empsit_summary_mod.SUMMARY_SPECS.items()
    }

    def _es_summary_fetch(slug):
        key = _es_slug_to_key[slug]
        return fixture_bytes(f"empsit_summary_{key}.html").decode("utf-8")

    _patch_module_attrs(
        monkeypatch,
        empsit_summary_mod,
        {
            "fetch_summary_html": _es_summary_fetch,
        },
    )

    # Productivity and Costs chart pages: serve each chart's trimmed HTML fixture.
    import openbb_bls.utils.productivity_charts as productivity_charts_mod

    _pc_slug_to_key = {
        spec["slug"]: key for key, spec in productivity_charts_mod.CHART_SPECS.items()
    }

    def _pc_fetch(slug):
        key = _pc_slug_to_key[slug]
        return fixture_bytes(f"productivity_chart_{key}.html").decode("utf-8")

    _patch_module_attrs(
        monkeypatch,
        productivity_charts_mod,
        {
            "fetch_chart_html": _pc_fetch,
        },
    )

    # Consumer Price Index chart pages: serve each chart's trimmed HTML fixture.
    import openbb_bls.utils.cpi_charts as cpi_charts_mod

    _cc_slug_to_key = {
        spec["slug"]: key for key, spec in cpi_charts_mod.CHART_SPECS.items()
    }

    def _cc_fetch(slug):
        key = _cc_slug_to_key[slug]
        return fixture_bytes(f"cpi_chart_{key}.html").decode("utf-8")

    _patch_module_attrs(
        monkeypatch,
        cpi_charts_mod,
        {
            "fetch_chart_html": _cc_fetch,
        },
    )

    # Producer Price Index chart pages: serve each chart's trimmed HTML fixture.
    import openbb_bls.utils.ppi_charts as ppi_charts_mod

    _pp_slug_to_key = {
        spec["slug"]: key for key, spec in ppi_charts_mod.CHART_SPECS.items()
    }

    def _pp_fetch(slug):
        key = _pp_slug_to_key[slug]
        return fixture_bytes(f"ppi_chart_{key}.html").decode("utf-8")

    _patch_module_attrs(
        monkeypatch,
        ppi_charts_mod,
        {
            "fetch_chart_html": _pp_fetch,
        },
    )

    # Productivity sub-package chart pages (TFP, wholesale/retail, mining/mfg):
    # serve each chart's trimmed HTML fixture, keyed by slug -> chart key.
    import openbb_bls.utils.jolts_charts as jolts_charts_mod
    import openbb_bls.utils.mining_manufacturing_charts as mm_charts_mod
    import openbb_bls.utils.tfp_charts as tfp_charts_mod
    import openbb_bls.utils.wholesale_retail_charts as wr_charts_mod

    for _prefix, _mod in (
        ("tfp", tfp_charts_mod),
        ("wholesale_retail", wr_charts_mod),
        ("mining_manufacturing", mm_charts_mod),
        ("jolts", jolts_charts_mod),
    ):
        _slug_to_key = {spec["slug"]: key for key, spec in _mod.CHART_SPECS.items()}

        def _fetch(slug, _prefix=_prefix, _slug_to_key=_slug_to_key):
            key = _slug_to_key[slug]
            return fixture_bytes(f"{_prefix}_chart_{key}.html").decode("utf-8")

        _patch_module_attrs(monkeypatch, _mod, {"fetch_chart_html": _fetch})

    _patch_module_attrs(
        monkeypatch,
        cpi_nr_mod,
        {
            "_fetch_nr_xlsx": lambda year, month, table: fixture_bytes(
                f"cpi_nr_t{table}.xlsx"
            ),
            "_discover_latest_nr": lambda table: (
                2026,
                4,
                fixture_bytes(f"cpi_nr_t{table}.xlsx"),
            ),
        },
    )

    _cpi_supp_stem_fixture = {
        "c-cpi-u": "cpi_c_cpi_u.xlsx",
        "cpi-u": "cpi_supp_cpi_u.xlsx",
        "cpi-w": "cpi_supp_cpi_w.xlsx",
        "historical-cpi-u": "cpi_supp_historical_cpi_u.xlsx",
    }

    def _cpi_supp_bytes(stem):
        if stem in _cpi_supp_stem_fixture:
            return fixture_bytes(_cpi_supp_stem_fixture[stem])
        raise AssertionError(f"unexpected CPI supplemental stem: {stem}")

    _patch_module_attrs(
        monkeypatch,
        cst_mod,
        {
            "discover_latest": lambda stem: (2026, 4, _cpi_supp_bytes(stem)),
            "fetch_xlsx": lambda stem, year, month: _cpi_supp_bytes(stem),
        },
    )

    _patch_module_attrs(
        monkeypatch,
        cri_mod,
        {
            "_discover_latest_ri": lambda: (
                2025,
                fixture_bytes("cpi_relative_importance_2025.xlsx"),
            ),
            "_fetch_ri_xlsx": lambda year: fixture_bytes(
                "cpi_relative_importance_2025.xlsx"
            ),
        },
    )

    _patch_module_attrs(
        monkeypatch,
        csf_mod,
        {
            "_discover_latest_sa": lambda: (
                2025,
                fixture_bytes("cpi_seasonal_factors_2025.xlsx"),
            ),
            "_fetch_sa_xlsx": lambda year: fixture_bytes(
                "cpi_seasonal_factors_2025.xlsx"
            ),
        },
    )

    # PPI fetchers import ``requests`` inside their helpers; patch the shared
    # module so every in-function import sees our stub.
    _URL_TO_FIXTURE = {
        "https://www.bls.gov/web/ppi/ppi-fdallrel.xlsx": "ppi_fdallrel.xlsx",
        "https://www.bls.gov/web/ppi/ppi-seafac.htm": "ppi_seafac.html",
    }

    def _patched_get(url, *args, **kwargs):
        if url in _URL_TO_FIXTURE:
            return _FakeResponse(fixture_bytes(_URL_TO_FIXTURE[url]))
        raise AssertionError(
            f"network access not mocked for URL: {url} "
            "(add it to _URL_TO_FIXTURE in conftest.py)"
        )

    import requests

    monkeypatch.setattr(requests, "get", _patched_get)

    # PPI seasonal factors uses get_requests_session().get(...) — patch the
    # whole _fetch_html_table helper to run the bundled HTML through the real
    # parser without touching the network.
    def _patched_fetch_html_table(table_id, url, label):
        from bs4 import BeautifulSoup  # ty: ignore[unresolved-import]

        if not url.endswith("ppi-seafac.htm"):
            raise AssertionError(f"unexpected PPI HTML URL: {url}")
        html = fixture_bytes("ppi_seafac.html").decode("utf-8")
        soup = BeautifulSoup(html, "lxml")
        tables = soup.find_all("table")
        if len(tables) < 2:
            return {"rows": [], "table_id": table_id, "table_name": label}
        data_table = tables[1]
        title_text = soup.title.string if soup.title else ""
        rows = psf_mod._parse_seafac_rows(data_table, title_text or "")
        for row in rows:
            row["table_id"] = table_id
            row["table_name"] = label
        rows.sort(key=lambda r: (r["date"], r["code"]))
        return {"rows": rows, "table_id": table_id, "table_name": label}

    monkeypatch.setattr(psf_mod, "_fetch_html_table", _patched_fetch_html_table)

    _patch_module_attrs(
        monkeypatch,
        jolts_tab_mod,
        {
            "fetch_change_analysis_txt": lambda scope, table_number: fixture_bytes(
                f"jolts_{scope}_t{table_number}.txt"
            ).decode("utf-8"),
        },
    )

    _patch_module_attrs(
        monkeypatch,
        jolts_rev_mod,
        {
            "fetch_revision_xlsx": lambda seasonally_adjusted: fixture_bytes(
                "jolts_sa_rev_mini.xlsx"
                if seasonally_adjusted
                else "jolts_nsa_rev_mini.xlsx"
            ),
        },
    )

    _patch_module_attrs(
        monkeypatch,
        prod_tab_mod,
        {
            "fetch_xlsx": lambda filename: (
                fixture_bytes("prod2_lps_mini.xlsx")
                if filename.startswith("labor-productivity-major-sectors")
                else fixture_bytes("prod2_teh_mini.xlsx")
                if filename.startswith("total-economy-hours-employment")
                else (_ for _ in ()).throw(
                    AssertionError(f"unexpected productivity filename: {filename}")
                )
            ),
        },
    )


@pytest.fixture
def mock_bls_xlsx_downloads(mock_bls_http):
    """Back-compat alias — superseded by ``mock_bls_http``."""
    return mock_bls_http
