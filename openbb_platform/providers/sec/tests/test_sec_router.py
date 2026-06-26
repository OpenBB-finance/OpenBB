"""Unit tests for the SEC router (``openbb_sec.sec_router``).

The router commands are otherwise only exercised by the live ``integration``
suite, so these tests cover registration and the command bodies without any
network access by mocking ``Query`` and ``OBBject.from_query``.

The SEC provider implements a number of standard models normally surfaced
through the ``openbb-equity`` and ``openbb-etf`` routers. When either extension
is not installed, those models are registered under SEC-prefixed names and
exposed through the SEC router instead. The fallback commands are therefore
registered conditionally, which the tests below account for.
"""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from openbb_sec import sec_router

# Commands that are always registered on the SEC router.
_BASE_COMMANDS = [
    "filing_headers",
    "htm_file",
    "cik_map",
    "institutions_search",
    "filing_index",
    "institutional_managers",
    "institutional_reporting_periods",
    "institutional_holdings",
    "investment_adviser_people",
    "investment_advisers",
    "private_offerings",
    "private_offering_people",
    "schema_files",
    "symbol_map",
    "rss_litigation",
    "sic_search",
    "financial_statements",
    "company_overview",
    "disclosures",
    "risk_factors",
    "segment_revenue",
    "legal_proceedings",
    "exhibit",
    "executive_compensation",
    "beneficial_ownership",
    "management_ownership",
    "pay_versus_performance",
    "company_filings",
    "latest_financial_reports",
    "full_text_search",
    "nport_fund_metrics",
]

# Non-command routes mounted on the router's APIRouter (raw GET handlers that
# back the OpenBB Workspace widgets, not OBBject commands).
_EXTRA_ROUTES = [
    "filing_options",
    "exhibits",
    "companies",
    "form_types",
    "report_types",
    "nport_funds",
    "nport_periods",
    "13f_filers",
    "13f_periods",
    "fts_categories",
    "fts_form_types",
    "fts_locations",
    "edgar_document",
    "edgar_document_markdown",
    "filing_viewer_app",
    "section_markdown",
    "as_filed_statement",
    "standardized_statement",
    "widgets.json",
    "apps.json",
]

# Registered on the SEC router only when ``openbb-equity`` is not installed.
_EQUITY_FALLBACK_COMMANDS = [
    "balance_sheet",
    "balance_sheet_growth",
    "cash_flow",
    "cash_flow_growth",
    "income_statement",
    "income_statement_growth",
    "compare_company_facts",
    "equity_search",
    "insider_trading",
    "form_13f",
    "equity_ftd",
    "management_discussion_analysis",
]

# Registered on the SEC router only when ``openbb-etf`` is not installed.
_ETF_FALLBACK_COMMANDS = ["nport_disclosure"]


def test_router_metadata():
    """The router uses an empty prefix and a SEC description."""
    assert sec_router.router.prefix == ""
    assert "SEC" in sec_router.router.description


def test_all_commands_registered():
    """The registered commands match the current install configuration.

    The base commands are always present; the equity/etf fallback commands are
    present only when the respective extension is absent.
    """
    paths = {route.path for route in sec_router.router.api_router.routes}
    expected = set(_BASE_COMMANDS) | set(_EXTRA_ROUTES)
    if not sec_router.EQUITY_INSTALLED:
        expected |= set(_EQUITY_FALLBACK_COMMANDS)
    if not sec_router.ETF_INSTALLED:
        expected |= set(_ETF_FALLBACK_COMMANDS)
    assert paths == {f"/{name}" for name in expected}


@pytest.mark.parametrize("command_name", _BASE_COMMANDS)
def test_command_delegates_to_from_query(command_name):
    """Each base command builds a Query and awaits OBBject.from_query."""
    sentinel = object()
    command = getattr(sec_router, command_name)
    with (
        patch.object(sec_router, "Query", MagicMock()) as mock_query,
        patch.object(
            sec_router.OBBject,
            "from_query",
            new=AsyncMock(return_value=sentinel),
        ) as mock_from_query,
    ):
        result = asyncio.run(
            command(
                cc=None,
                provider_choices=None,
                standard_params=None,
                extra_params=None,
            )
        )
    assert result is sentinel
    mock_query.assert_called_once()
    mock_from_query.assert_awaited_once()


def _load_router_module(*, equity_installed: bool, etf_installed: bool):
    """Re-execute ``sec_router`` with the install flags forced to given values.

    Loaded under a private module name so the live ``openbb_sec.sec_router``
    used elsewhere in the suite is untouched. ``Router.command`` is replaced
    during load with a passthrough decorator so the endpoints bind without
    requiring the SEC-prefixed models to be resolved through the live provider
    registry or FastAPI's response-model machinery.

    This exercises the install-gated endpoint definitions regardless of which
    extensions are actually present in the test environment.
    """
    import importlib.util
    from pathlib import Path

    from openbb_core.app.router import Router

    import openbb_sec

    spec = importlib.util.spec_from_file_location(
        f"openbb_sec_sec_router_e{int(equity_installed)}t{int(etf_installed)}",
        Path(openbb_sec.__file__).parent / "sec_router.py",
    )
    module = importlib.util.module_from_spec(spec)
    original_equity = openbb_sec.EQUITY_INSTALLED
    original_etf = openbb_sec.ETF_INSTALLED
    original_command = Router.command
    openbb_sec.EQUITY_INSTALLED = equity_installed
    openbb_sec.ETF_INSTALLED = etf_installed

    def _passthrough_command(self, func=None, **_kwargs):
        """Bind ``func`` without touching the underlying FastAPI router."""
        if func is None:
            return lambda f: _passthrough_command(self, f, **_kwargs)
        return func

    Router.command = _passthrough_command  # type: ignore[assignment]
    try:
        spec.loader.exec_module(module)
    finally:
        openbb_sec.EQUITY_INSTALLED = original_equity
        openbb_sec.ETF_INSTALLED = original_etf
        Router.command = original_command  # type: ignore[assignment]
    return module


def _load_standalone_router_module():
    """Re-execute ``sec_router`` with both install flags forced to False."""
    return _load_router_module(equity_installed=False, etf_installed=False)


class TestStandaloneFallbackEndpoints:
    """The commands registered only when ``openbb-equity``/``openbb-etf`` are absent."""

    _STANDALONE_NAMES = tuple(_EQUITY_FALLBACK_COMMANDS + _ETF_FALLBACK_COMMANDS)

    def test_standalone_module_binds_all_fallback_endpoint_names(self):
        """All fallback endpoint names exist as module attributes after reload."""
        module = _load_standalone_router_module()
        for name in self._STANDALONE_NAMES:
            assert callable(getattr(module, name, None)), f"missing {name}"

    def test_standalone_module_binds_base_endpoint_names(self):
        """The always-present base commands also bind in the standalone module."""
        module = _load_standalone_router_module()
        for name in _BASE_COMMANDS:
            assert callable(getattr(module, name, None)), f"missing {name}"

    @pytest.mark.parametrize(
        "endpoint_name",
        [*_STANDALONE_NAMES, "company_filings", "latest_financial_reports"],
    )
    def test_standalone_endpoint_body_delegates_to_from_query(self, endpoint_name):
        """Each fallback endpoint body calls ``OBBject.from_query(Query(**locals()))``."""
        module = _load_standalone_router_module()
        fn = getattr(module, endpoint_name)

        sentinel = object()
        with (
            patch.object(module, "Query", new=MagicMock()) as mock_query,
            patch.object(
                module.OBBject,
                "from_query",
                new=AsyncMock(return_value=sentinel),
            ) as mock_from_query,
        ):
            out = asyncio.run(
                fn(
                    cc=MagicMock(),
                    provider_choices=MagicMock(),
                    standard_params=MagicMock(),
                    extra_params=MagicMock(),
                )
            )
        assert out is sentinel
        mock_query.assert_called_once()
        mock_from_query.assert_awaited_once()


class TestInstalledExtensionEndpoints:
    """Endpoints registered when ``openbb-equity`` / ``openbb-etf`` ARE installed.

    Where those extensions are absent the installed-path branch never executes
    live, so it is exercised by reloading the router with the flags forced True.
    """

    _INSTALLED_NAMES = ("company_filings", "latest_financial_reports")

    def test_installed_module_binds_endpoints(self):
        """The installed-path endpoints bind when equity/etf are present."""
        module = _load_router_module(equity_installed=True, etf_installed=True)
        for name in self._INSTALLED_NAMES:
            assert callable(getattr(module, name, None)), f"missing {name}"

    @pytest.mark.parametrize("endpoint_name", _INSTALLED_NAMES)
    def test_installed_endpoint_body_delegates_to_from_query(self, endpoint_name):
        """Each installed-path endpoint body calls ``OBBject.from_query``."""
        module = _load_router_module(equity_installed=True, etf_installed=True)
        fn = getattr(module, endpoint_name)

        sentinel = object()
        with (
            patch.object(module, "Query", new=MagicMock()) as mock_query,
            patch.object(
                module.OBBject,
                "from_query",
                new=AsyncMock(return_value=sentinel),
            ) as mock_from_query,
        ):
            out = asyncio.run(
                fn(
                    cc=MagicMock(),
                    provider_choices=MagicMock(),
                    standard_params=MagicMock(),
                    extra_params=MagicMock(),
                )
            )
        assert out is sentinel
        mock_query.assert_called_once()
        mock_from_query.assert_awaited_once()


class TestWidgetEndpoints:
    """The raw GET handlers backing the OpenBB Workspace widgets."""

    def test_filing_options(self):
        filings = [
            {"period_ending": "2024-09-28"},
            {"period_ending": "2023-09-30"},
            {"period_ending": None},
        ]
        with patch(
            "openbb_sec.models.sec_financials.get_form10_urls_by_symbol",
            new=AsyncMock(return_value=filings),
        ):
            options = asyncio.run(sec_router.filing_options(symbol="AAPL"))
        assert {o["value"] for o in options} == {"2024", "2023"}

    def test_filing_options_empty_symbol(self):
        assert asyncio.run(sec_router.filing_options(symbol="")) == []

    def test_exhibits_empty_symbol(self):
        assert asyncio.run(sec_router.exhibits(symbol="")) == []

    def test_exhibits_no_filing(self):
        with patch(
            "openbb_sec.models.sec_financials.resolve_filing_url",
            new=AsyncMock(return_value=""),
        ):
            assert (
                asyncio.run(sec_router.exhibits(symbol="AAPL", calendar_year="1999"))
                == []
            )

    def test_exhibits_lists_choices(self):
        from types import SimpleNamespace

        fs = SimpleNamespace(exhibit_choices=lambda: [{"value": "EX-21", "label": "x"}])
        with (
            patch(
                "openbb_sec.models.sec_financials.resolve_filing_url",
                new=AsyncMock(return_value="u"),
            ),
            patch(
                "openbb_sec.models.sec_financials.FinancialStatements.from_url",
                return_value=fs,
            ),
        ):
            options = asyncio.run(sec_router.exhibits(symbol="AAPL"))
        assert options == [{"value": "EX-21", "label": "x"}]

    def test_standardized_statement(self):
        with patch(
            "openbb_sec.utils.statement_widget.get_statement_widget_rows",
            new=AsyncMock(return_value=[{"Line Item": "Total Assets"}]),
        ):
            rows = asyncio.run(sec_router.standardized_statement(symbol="AAPL"))
        assert rows == [{"Line Item": "Total Assets"}]

    def test_standardized_statement_empty_symbol(self):
        assert asyncio.run(sec_router.standardized_statement(symbol="")) == []

    def test_as_filed_statement(self):
        with patch(
            "openbb_sec.utils.as_filed_widget.get_as_filed_widget_rows",
            new=AsyncMock(return_value=[{"order": 1, "label": "Cash"}]),
        ):
            rows = asyncio.run(sec_router.as_filed_statement(symbol="ORCL"))
        assert rows == [{"order": 1, "label": "Cash"}]

    def test_as_filed_statement_empty_symbol(self):
        assert asyncio.run(sec_router.as_filed_statement(symbol="")) == []

    def test_companies(self):
        with patch(
            "openbb_sec.utils.company_choices.get_company_choices",
            new=AsyncMock(return_value=[{"label": "Apple Inc.", "value": "AAPL"}]),
        ):
            result = asyncio.run(sec_router.companies(use_cache=True))
        assert result == [{"label": "Apple Inc.", "value": "AAPL"}]

    def test_get_apps_json(self):
        apps = asyncio.run(sec_router.get_apps_json())
        assert isinstance(apps, list)
        assert apps[0]["name"]
        ids = {
            w["i"]
            for app in apps
            for tab in app["tabs"].values()
            for w in tab["layout"]
        }
        if sec_router.EQUITY_INSTALLED:
            assert "equity_ownership_form_13f_sec_obb" in ids
            assert "sec_form_13f_sec_obb" not in ids
        else:
            assert "sec_form_13f_sec_obb" in ids

    def test_section_markdown(self):
        with patch(
            "openbb_sec.utils.section_markdown.get_section_markdown",
            new=AsyncMock(return_value="## Risk\n\nBody"),
        ):
            result = asyncio.run(
                sec_router.section_markdown(symbol="AAPL", section="risk_factors")
            )
        assert result == "## Risk\n\nBody"

    def test_section_markdown_empty_symbol(self):
        assert asyncio.run(sec_router.section_markdown(symbol="")) == ""

    def test_warm_companies(self):
        with patch(
            "openbb_sec.utils.company_choices.get_company_choices",
            new=AsyncMock(return_value=[]),
        ) as warm:
            asyncio.run(sec_router._warm_companies())
        warm.assert_awaited_once()

    def test_warm_companies_suppresses_errors(self):
        with patch(
            "openbb_sec.utils.company_choices.get_company_choices",
            new=AsyncMock(side_effect=RuntimeError("boom")),
        ):
            asyncio.run(sec_router._warm_companies())

    def test_get_widgets_json_includes_curated(self):
        with (
            patch("openbb_sec.sec_router._warm_companies", new=AsyncMock()),
            patch("openbb_sec.sec_router._ensure_filing_viewer_mcp"),
        ):
            widgets = asyncio.run(sec_router.get_widgets_json())
        assert isinstance(widgets, dict)
        assert widgets["sec_company_overview_sec_obb"]["type"] == "markdown"

    def test_get_widgets_json_falls_back_on_error(self):
        with (
            patch("openbb_sec.sec_router._warm_companies", new=AsyncMock()),
            patch("openbb_sec.sec_router._ensure_filing_viewer_mcp"),
            patch(
                "openbb_platform_api.utils.widgets.build_json",
                side_effect=RuntimeError("boom"),
            ),
        ):
            widgets = asyncio.run(sec_router.get_widgets_json())
        assert "sec_balance_sheet_facts_sec_obb" in widgets


def test_nport_funds_endpoint(monkeypatch):
    """nport_funds delegates to the fund-choices helper."""

    async def _funds(use_cache=True):
        return [{"label": "XLK - Fund", "value": "XLK"}]

    monkeypatch.setattr("openbb_sec.utils.helpers.get_nport_fund_choices", _funds)
    assert asyncio.run(sec_router.nport_funds())[0]["value"] == "XLK"


def test_filers_13f_endpoint(monkeypatch):
    """filers_13f delegates to the filer-choices helper."""

    async def _filers(use_cache=True):
        return [{"label": "BlackRock", "value": "1"}]

    monkeypatch.setattr("openbb_sec.utils.helpers.get_13f_filer_choices", _filers)
    assert asyncio.run(sec_router.filers_13f())[0]["value"] == "1"


def test_periods_13f_endpoint(monkeypatch):
    """periods_13f returns sorted report dates, handling empties and errors."""
    from pandas import DataFrame

    assert asyncio.run(sec_router.periods_13f(symbol=None)) == []

    async def _cands(cik=None, symbol=None):
        return DataFrame(index=["2026-03-31", "2025-12-31"])

    monkeypatch.setattr("openbb_sec.utils.parse_13f.get_13f_candidates", _cands)
    out = asyncio.run(sec_router.periods_13f(symbol="1067983"))
    assert out[0]["value"] == "2026-03-31"

    async def _boom(**kwargs):
        raise RuntimeError("x")

    monkeypatch.setattr("openbb_sec.utils.parse_13f.get_13f_candidates", _boom)
    assert asyncio.run(sec_router.periods_13f(symbol="AAA")) == []


def test_nport_periods_endpoint(monkeypatch):
    """nport_periods dedupes filing periods, handling empties and errors."""
    assert asyncio.run(sec_router.nport_periods(symbol=None)) == []

    async def _cands(symbol, use_cache=True):
        return [
            {"period_ending": "2026-05-31", "form_type": "N-MFP3"},
            {"period_ending": "2026-05-31", "form_type": "N-MFP3"},
        ]

    monkeypatch.setattr("openbb_sec.utils.helpers.get_nport_candidates", _cands)
    assert len(asyncio.run(sec_router.nport_periods(symbol="vmfxx"))) == 1

    async def _boom(symbol, use_cache=True):
        raise RuntimeError("x")

    monkeypatch.setattr("openbb_sec.utils.helpers.get_nport_candidates", _boom)
    assert asyncio.run(sec_router.nport_periods(symbol="AAA")) == []


def test_form_types_endpoint(monkeypatch):
    """form_types returns distinct report types, handling empties and errors."""
    from types import SimpleNamespace

    assert asyncio.run(sec_router.form_types(symbol=None)) == []

    async def _fetch(self, params, creds):
        return [
            SimpleNamespace(report_type="10-K"),
            SimpleNamespace(report_type="8-K"),
            SimpleNamespace(report_type=None),
        ]

    monkeypatch.setattr(
        "openbb_sec.models.company_filings.SecCompanyFilingsFetcher.fetch_data", _fetch
    )
    assert {c["value"] for c in asyncio.run(sec_router.form_types(symbol="aapl"))} == {
        "10-K",
        "8-K",
    }

    async def _boom(self, params, creds):
        raise RuntimeError("x")

    monkeypatch.setattr(
        "openbb_sec.models.company_filings.SecCompanyFilingsFetcher.fetch_data", _boom
    )
    assert asyncio.run(sec_router.form_types(symbol="aapl")) == []


def test_report_types_endpoint():
    """report_types lists the latest-reports filter choices."""
    out = asyncio.run(sec_router.report_types())
    assert isinstance(out, list)
    assert out and "value" in out[0]


def test_get_apps_json_endpoint():
    """get_apps_json returns the app templates."""
    out = asyncio.run(sec_router.get_apps_json())
    assert isinstance(out, list)
    assert out


def _apps_widget_ids(apps):
    """Collect every widget id from tab layouts and groups."""
    ids = set()
    for app in apps:
        for tab in app["tabs"].values():
            ids.update(w["i"] for w in tab["layout"])
        for group in app.get("groups", []):
            ids.update(group.get("widgetIds", []))
    return ids


def test_get_apps_json_remaps_for_equity(monkeypatch):
    """With openbb-equity installed, form_13f maps to the equity widget id."""
    monkeypatch.setattr(sec_router, "EQUITY_INSTALLED", True)
    monkeypatch.setattr(sec_router, "ETF_INSTALLED", False)
    ids = _apps_widget_ids(asyncio.run(sec_router.get_apps_json()))
    assert "equity_ownership_form_13f_sec_obb" in ids
    assert "sec_form_13f_sec_obb" not in ids


def test_get_apps_json_remaps_for_etf(monkeypatch):
    """With openbb-etf installed, nport_disclosure maps to the etf widget id."""
    monkeypatch.setattr(sec_router, "EQUITY_INSTALLED", False)
    monkeypatch.setattr(sec_router, "ETF_INSTALLED", True)
    ids = _apps_widget_ids(asyncio.run(sec_router.get_apps_json()))
    assert "etf_nport_disclosure_sec_obb" in ids
    assert "sec_nport_disclosure_sec_obb" not in ids


def test_get_apps_json_no_remap_when_standalone(monkeypatch):
    """With neither extension installed, the SEC-native ids are served as-is."""
    monkeypatch.setattr(sec_router, "EQUITY_INSTALLED", False)
    monkeypatch.setattr(sec_router, "ETF_INSTALLED", False)
    ids = _apps_widget_ids(asyncio.run(sec_router.get_apps_json()))
    assert "sec_form_13f_sec_obb" in ids
    assert "sec_nport_disclosure_sec_obb" in ids


def test_filing_viewer_mcp_port(monkeypatch):
    """The MCP port reads its env override, defaulting to 7769."""
    monkeypatch.delenv("OPENBB_SEC_MCP_PORT", raising=False)
    assert sec_router.filing_viewer_mcp_port() == 7769
    monkeypatch.setenv("OPENBB_SEC_MCP_PORT", "9999")
    assert sec_router.filing_viewer_mcp_port() == 9999


def test_mcp_base_url_from_request():
    """_mcp_base_url honours X-Forwarded-Proto, else the request scheme."""
    from types import SimpleNamespace

    req = SimpleNamespace(
        headers={"x-forwarded-proto": "https", "host": "data.example.com:6900"},
        url=SimpleNamespace(scheme="http"),
    )
    assert sec_router._mcp_base_url(req).startswith("https://data.example.com:")
    req2 = SimpleNamespace(
        headers={"host": "localhost:6900"}, url=SimpleNamespace(scheme="http")
    )
    assert sec_router._mcp_base_url(req2).startswith("http://localhost:")


def test_mcp_base_from_config(monkeypatch):
    """_mcp_base_from_config builds from env, defaulting to http localhost."""
    monkeypatch.delenv("OPENBB_API_HOST", raising=False)
    assert sec_router._mcp_base_from_config().startswith("http://localhost:")
    monkeypatch.setenv("OPENBB_API_HOST", "0.0.0.0")  # noqa: S104
    assert sec_router._mcp_base_from_config().startswith("http://localhost:")
    monkeypatch.setenv("OPENBB_API_HOST", "example.com")
    assert "example.com" in sec_router._mcp_base_from_config()


def test_mcp_base_from_config_https(monkeypatch):
    """A TLS-configured server yields an https base."""
    monkeypatch.delenv("OPENBB_API_HOST", raising=False)

    class _SS:
        class system_settings:
            class python_settings:
                @staticmethod
                def model_dump():
                    return {"uvicorn": {"ssl_certfile": "cert.pem"}}

    monkeypatch.setattr("openbb_core.app.service.system_service.SystemService", _SS)
    assert sec_router._mcp_base_from_config().startswith("https://localhost:")


def test_filing_viewer_app_endpoint():
    """filing_viewer_app injects the MCP base into the served HTML."""
    resp = asyncio.run(sec_router.filing_viewer_app(mcp_base="http://localhost:7769"))
    body = resp.body.decode("utf-8")
    assert "http://localhost:7769" in body
    assert "__OB_MCP_BASE__" not in body


def test_edgar_document_markdown_endpoint(monkeypatch):
    """edgar_document_markdown returns markdown, empty when no url is given."""
    assert asyncio.run(sec_router.edgar_document_markdown(url=None)) == {"content": ""}
    monkeypatch.setattr(
        "openbb_sec.utils.filing_viewer_mcp.document_to_markdown", lambda u: "MD"
    )
    out = asyncio.run(
        sec_router.edgar_document_markdown(url="https://www.sec.gov/a.htm")
    )
    assert out == {"content": "MD"}


def test_fts_options_endpoints():
    """The full-text-search option endpoints return non-empty lists."""
    assert asyncio.run(sec_router.fts_categories())
    assert asyncio.run(sec_router.fts_form_types())[0]["value"]
    assert asyncio.run(sec_router.fts_locations())


def _patch_bytes(monkeypatch, fn):
    """Patch cached_bytes used by the edgar_document proxy."""
    monkeypatch.setattr("openbb_sec.utils.cache.cached_bytes", fn)


def test_edgar_document_no_url():
    """An empty URL shows the placeholder."""
    resp = asyncio.run(sec_router.edgar_document(url=None))
    assert b"Select a filing" in resp.body


def test_edgar_document_rejects_non_sec():
    """A non-SEC URL is rejected with 400."""
    resp = asyncio.run(sec_router.edgar_document(url="https://evil.com/x"))
    assert resp.status_code == 400


def test_edgar_document_load_error(monkeypatch):
    """A transport error returns a 502."""

    def _boom(target, **kwargs):
        raise RuntimeError("x")

    _patch_bytes(monkeypatch, _boom)
    resp = asyncio.run(sec_router.edgar_document(url="https://www.sec.gov/a.htm"))
    assert resp.status_code == 502


def test_edgar_document_pdf(monkeypatch):
    """PDFs are served as application/pdf by magic bytes or extension."""
    _patch_bytes(monkeypatch, lambda t, **k: b"%PDF-1.7")
    assert (
        asyncio.run(
            sec_router.edgar_document(url="https://www.sec.gov/a.htm")
        ).media_type
        == "application/pdf"
    )
    _patch_bytes(monkeypatch, lambda t, **k: b"data")
    assert (
        asyncio.run(
            sec_router.edgar_document(url="https://www.sec.gov/a.pdf")
        ).media_type
        == "application/pdf"
    )


def test_edgar_document_images(monkeypatch):
    """Images are detected by extension and by magic bytes."""
    _patch_bytes(monkeypatch, lambda t, **k: b"\x89PNG\r\n\x1a\n")
    assert (
        asyncio.run(
            sec_router.edgar_document(url="https://www.sec.gov/a.png")
        ).media_type
        == "image/png"
    )
    for magic in (b"\x89PNG\r\n\x1a\n", b"\xff\xd8\xff", b"GIF89a0000"):
        _patch_bytes(monkeypatch, lambda t, _m=magic, **k: _m)
        resp = asyncio.run(sec_router.edgar_document(url="https://www.sec.gov/a.dat"))
        assert resp.body == magic


def test_edgar_document_html_rewrites(monkeypatch):
    """HTML is rewritten: assets proxied, inline/anchors/external kept."""
    html = (
        "<html><body>"
        '<img src="pic.png">'
        '<img src="data:image/png;base64,xxx">'
        '<img src="https://cdn.com/a.png">'
        '<img src="//cdn.com/b.png">'
        '<img src="/files/c.png">'
        '<div style="background:url(bg.gif)"></div>'
        '<div style="background:url(data:image/gif;base64,zz)"></div>'
        '<div style="background:url(&#39;data:image/svg+xml,<svg/>&#39;)"></div>'
        '<a href="page.htm">x</a>'
        '<a href="#sec">y</a>'
        '<a href="https://x.com">z</a>'
        "</body></html>"
    )
    _patch_bytes(monkeypatch, lambda t, **k: html.encode())
    resp = asyncio.run(sec_router.edgar_document(url="https://www.sec.gov/dir/doc.htm"))
    body = resp.body.decode()
    assert resp.media_type == "text/html"
    assert "/api/v1/sec/edgar_document?url=" in body
    assert "data:image/png" in body
    assert "url(data:image/gif" in body
    assert 'href="#sec"' in body
    assert 'href="https://x.com"' in body
    assert 'href="https://www.sec.gov/dir/page.htm"' in body


def test_edgar_document_xsl_path_served_as_text(monkeypatch):
    """A non-HTML document already under /xsl is returned as plain text."""
    _patch_bytes(monkeypatch, lambda t, **k: b"raw xml content")
    resp = asyncio.run(
        sec_router.edgar_document(url="https://www.sec.gov/x/xslF345/form.xml")
    )
    assert resp.media_type.startswith("text/plain")


def test_edgar_document_rendered_html(monkeypatch):
    """A raw XML form resolves to its xsl-rendered HTML."""
    acc = "000123456724000077"
    base = "https://www.sec.gov/Archives/edgar/data/1/" + acc
    rendered_path = "/Archives/edgar/data/1/" + acc + "/xslF345X02/form.xml"

    def _bytes(target, **kwargs):
        if target.endswith("-index.html"):
            return ('<a href="' + rendered_path + '">Rendered</a>').encode()
        if "/xsl" in target:
            return b'<html><body>Rendered<img src="logo.png"></body></html>'
        return b"<?xml version='1.0'?><ownershipDocument/>"

    _patch_bytes(monkeypatch, _bytes)
    resp = asyncio.run(sec_router.edgar_document(url=base + "/form.xml"))
    assert resp.media_type == "text/html"
    assert "Rendered" in resp.body.decode()


def test_edgar_document_rendered_no_index_link(monkeypatch):
    """When the index has no xsl link, the raw text is served."""
    acc = "000123456724000077"
    base = "https://www.sec.gov/Archives/edgar/data/1/" + acc

    def _bytes(target, **kwargs):
        if target.endswith("-index.html"):
            return b"<html><body>no link</body></html>"
        return b"<?xml version='1.0'?><x/>"

    _patch_bytes(monkeypatch, _bytes)
    resp = asyncio.run(sec_router.edgar_document(url=base + "/form.xml"))
    assert resp.media_type.startswith("text/plain")


def test_edgar_document_rendered_index_error(monkeypatch):
    """An index-fetch error falls back to plain text."""
    acc = "000123456724000077"
    base = "https://www.sec.gov/Archives/edgar/data/1/" + acc

    def _bytes(target, **kwargs):
        if target.endswith("-index.html"):
            raise RuntimeError("boom")
        return b"<?xml version='1.0'?><x/>"

    _patch_bytes(monkeypatch, _bytes)
    resp = asyncio.run(sec_router.edgar_document(url=base + "/form.xml"))
    assert resp.media_type.startswith("text/plain")


def test_edgar_document_plain_text_short_dir(monkeypatch):
    """A non-HTML document outside an accession directory is plain text."""
    _patch_bytes(monkeypatch, lambda t, **k: b"plain content")
    resp = asyncio.run(sec_router.edgar_document(url="https://www.sec.gov/dir/x.txt"))
    assert resp.media_type.startswith("text/plain")


def test_ensure_filing_viewer_mcp(monkeypatch):
    """The MCP server is started once in a daemon thread, then guarded."""
    monkeypatch.setattr(sec_router, "_MCP_MOUNTED", set())
    captured: dict = {}

    class _FakeThread:
        def __init__(self, target=None, daemon=None, name=None):
            captured["target"] = target

        def start(self):
            captured["started"] = True

    monkeypatch.setattr("threading.Thread", _FakeThread)
    sec_router._ensure_filing_viewer_mcp()
    assert captured["started"] is True

    captured["started"] = False
    sec_router._ensure_filing_viewer_mcp()
    assert captured["started"] is False

    import openbb_sec.utils.filing_viewer_mcp as mcp

    monkeypatch.setattr(mcp, "build_mcp_app", object)
    ran: dict = {}
    monkeypatch.setattr("uvicorn.run", lambda *a, **k: ran.setdefault("ran", True))
    captured["target"]()
    assert ran.get("ran") is True
