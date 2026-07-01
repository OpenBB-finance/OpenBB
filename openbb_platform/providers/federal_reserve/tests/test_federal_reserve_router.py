"""Tests for the Federal Reserve router and conditional command registration."""

import importlib.util
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.app.route_iter import iter_api_routes

from openbb_federal_reserve import federal_reserve_router as fr

_ECONOMY_FALLBACK_NAMES = (
    "fomc_documents",
    "inflation_expectations",
    "money_measures",
)
_FIXEDINCOME_FALLBACK_NAMES = (
    "treasury_rates",
    "yield_curve",
)
_ALL_FALLBACK_NAMES = _ECONOMY_FALLBACK_NAMES + _FIXEDINCOME_FALLBACK_NAMES


def _load_router_module(economy_installed: bool, fixedincome_installed: bool):
    """Re-execute ``federal_reserve_router`` with the host flags forced.

    The module is loaded under a private name so the live router used elsewhere
    in the suite is untouched. ``Router.command`` is replaced with a passthrough
    so the fallback endpoints bind without requiring the host-prefixed models in
    the live provider registry or FastAPI's response-model machinery.
    """
    from openbb_core.app.router import Router

    import openbb_federal_reserve

    spec = importlib.util.spec_from_file_location(
        "openbb_federal_reserve_router_standalone",
        Path(fr.__file__),
    )
    module = importlib.util.module_from_spec(spec)
    original_economy = openbb_federal_reserve.ECONOMY_INSTALLED
    original_fixedincome = openbb_federal_reserve.FIXEDINCOME_INSTALLED
    original_command = Router.command
    openbb_federal_reserve.ECONOMY_INSTALLED = economy_installed
    openbb_federal_reserve.FIXEDINCOME_INSTALLED = fixedincome_installed

    def _passthrough_command(self, func=None, **_kwargs):
        """Bind ``func`` without touching the underlying FastAPI router."""
        if func is None:
            return lambda f: _passthrough_command(self, f, **_kwargs)
        return func

    Router.command = _passthrough_command
    try:
        spec.loader.exec_module(module)
    finally:
        openbb_federal_reserve.ECONOMY_INSTALLED = original_economy
        openbb_federal_reserve.FIXEDINCOME_INSTALLED = original_fixedincome
        Router.command = original_command
    return module


class TestRewriteWidgetIds:
    """Tests for ``_rewrite_widget_ids`` and its per-host gating."""

    def test_both_hosts_present_is_identity(self, monkeypatch):
        """When both hosts are installed nothing is rewritten."""
        monkeypatch.setattr(fr, "ECONOMY_INSTALLED", True)
        monkeypatch.setattr(fr, "FIXEDINCOME_INSTALLED", True)
        apps = [
            {
                "tabs": {
                    "a": {
                        "layout": [{"i": "economy_money_measures_federal_reserve_obb"}]
                    }
                }
            }
        ]
        out = fr._rewrite_widget_ids(apps)
        assert out[0]["tabs"]["a"]["layout"][0]["i"] == (
            "economy_money_measures_federal_reserve_obb"
        )

    def test_economy_absent_only_rewrites_economy_ids(self, monkeypatch):
        """Economy absent, fixedincome present rewrites only the economy ids."""
        monkeypatch.setattr(fr, "ECONOMY_INSTALLED", False)
        monkeypatch.setattr(fr, "FIXEDINCOME_INSTALLED", True)
        apps = [
            {
                "tabs": {
                    "a": {
                        "layout": [
                            {"i": "economy_money_measures_federal_reserve_obb"},
                            {"i": "fixedincome_rate_sofr_federal_reserve_obb"},
                        ]
                    }
                }
            }
        ]
        out = fr._rewrite_widget_ids(apps)
        ids = [w["i"] for w in out[0]["tabs"]["a"]["layout"]]
        assert ids == [
            fr._ECONOMY_WIDGET_ID_FALLBACK_MAP[
                "economy_money_measures_federal_reserve_obb"
            ],
            "fixedincome_rate_sofr_federal_reserve_obb",
        ]

    def test_fixedincome_absent_only_rewrites_fixedincome_ids(self, monkeypatch):
        """Fixedincome absent, economy present rewrites only the fixedincome ids."""
        monkeypatch.setattr(fr, "ECONOMY_INSTALLED", True)
        monkeypatch.setattr(fr, "FIXEDINCOME_INSTALLED", False)
        apps = [
            {
                "tabs": {
                    "a": {
                        "layout": [
                            {"i": "economy_money_measures_federal_reserve_obb"},
                            {"i": "fixedincome_rate_sofr_federal_reserve_obb"},
                        ]
                    }
                }
            }
        ]
        out = fr._rewrite_widget_ids(apps)
        ids = [w["i"] for w in out[0]["tabs"]["a"]["layout"]]
        assert ids == [
            "economy_money_measures_federal_reserve_obb",
            fr._FIXEDINCOME_WIDGET_ID_FALLBACK_MAP[
                "fixedincome_rate_sofr_federal_reserve_obb"
            ],
        ]

    def test_tolerates_missing_tabs_and_layout(self, monkeypatch):
        """Apps without ``tabs`` or with ``layout=None`` are skipped gracefully."""
        monkeypatch.setattr(fr, "ECONOMY_INSTALLED", False)
        monkeypatch.setattr(fr, "FIXEDINCOME_INSTALLED", False)
        apps = [
            {},
            {"tabs": {}},
            {"tabs": {"x": {}}},
            {"tabs": {"x": {"layout": None}}},
            {
                "tabs": {
                    "x": {
                        "layout": [{"i": "economy_money_measures_federal_reserve_obb"}]
                    }
                }
            },
        ]
        out = fr._rewrite_widget_ids(apps)
        assert (
            out[-1]["tabs"]["x"]["layout"][0]["i"]
            == (
                fr._ECONOMY_WIDGET_ID_FALLBACK_MAP[
                    "economy_money_measures_federal_reserve_obb"
                ]
            )
        )


class TestGetAppsJson:
    """Tests for ``get_apps_json``."""

    @pytest.mark.asyncio
    async def test_returns_rewritten_apps_when_hosts_absent(self):
        """The bundled apps.json is served with federal_reserve-prefixed widget ids."""
        apps = await fr.get_apps_json()
        ids = [
            w.get("i")
            for app in apps
            for tab in (app.get("tabs", {}) or {}).values()
            for w in (tab.get("layout", []) or [])
        ]
        assert ids, "expected widgets in the bundled apps.json"
        assert all(
            not (str(i).startswith("economy_") or str(i).startswith("fixedincome_"))
            for i in ids
        )

    @pytest.mark.asyncio
    async def test_returns_empty_when_missing(self, tmp_path, monkeypatch):
        """A missing apps.json returns the empty fallback list."""
        monkeypatch.setattr(fr, "__file__", str(tmp_path / "federal_reserve_router.py"))
        assert await fr.get_apps_json() == []


class TestFomcDocumentsDownload:
    """Tests for the ``fomc_documents_download`` utility endpoint."""

    @pytest.mark.asyncio
    async def test_rejects_non_federalreserve_host(self):
        """A URL outside federalreserve.gov raises an error."""
        with pytest.raises(OpenBBError, match="Must be from federalreserve.gov"):
            await fr.fomc_documents_download({"url": ["https://example.com/a.pdf"]})

    @pytest.mark.asyncio
    async def test_rejects_unsupported_format(self):
        """A non-PDF/HTM document raises an error."""
        with pytest.raises(OpenBBError, match="Unsupported document format"):
            await fr.fomc_documents_download(
                {"url": ["https://www.federalreserve.gov/a.txt"]}
            )

    @pytest.mark.asyncio
    async def test_downloads_pdf_as_base64(self):
        """A valid PDF URL is downloaded and base64-encoded."""
        response = MagicMock()
        response.content = b"%PDF-1.7 fake"
        response.raise_for_status = MagicMock()
        with patch(
            "openbb_core.provider.utils.helpers.make_request", return_value=response
        ):
            out = await fr.fomc_documents_download(
                {"url": ["https://www.federalreserve.gov/files/a.pdf"]}
            )
        assert out[0]["data_format"]["data_type"] == "pdf"
        assert out[0]["data_format"]["filename"] == "a.pdf"
        assert isinstance(out[0]["content"], str)

    @pytest.mark.asyncio
    async def test_downloads_htm_as_markdown(self):
        """A valid HTM URL is tagged as markdown."""
        response = MagicMock()
        response.content = b"<html>hi</html>"
        response.raise_for_status = MagicMock()
        with patch(
            "openbb_core.provider.utils.helpers.make_request", return_value=response
        ):
            out = await fr.fomc_documents_download(
                {"url": ["https://www.federalreserve.gov/a.htm"]}
            )
        assert out[0]["data_format"]["data_type"] == "markdown"

    @pytest.mark.asyncio
    async def test_download_error_is_captured(self):
        """A request failure is captured as a download_error entry."""
        with patch(
            "openbb_core.provider.utils.helpers.make_request",
            side_effect=RuntimeError("boom"),
        ):
            out = await fr.fomc_documents_download(
                {"url": ["https://www.federalreserve.gov/a.pdf"]}
            )
        assert out[0]["error_type"] == "download_error"
        assert "RuntimeError" in out[0]["content"]


class TestFomcDocumentsChoices:
    """Tests for the ``fomc_documents_choices`` utility endpoint."""

    @pytest.mark.asyncio
    async def test_builds_label_value_choices(self, monkeypatch):
        """Choices are built from documents with both a type and a URL."""
        docs = [
            {"doc_type": "monetary_policy", "date": "2022-01-01", "url": "u1"},
            {"doc_type": "minutes", "date": "2022-02-01", "url": ""},
        ]
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.fomc_documents.get_fomc_documents_by_year",
            lambda *a, **k: docs,
        )
        out = await fr.fomc_documents_choices(year=2022)
        assert out == [{"label": "Monetary Policy - 2022-01-01", "value": "u1"}]


class TestFallbackRegistration:
    """Tests for the host-conditional fallback command registration."""

    def test_all_fallbacks_bind_when_hosts_absent(self):
        """Both hosts absent binds all non-NY fallback command functions."""
        module = _load_router_module(
            economy_installed=False, fixedincome_installed=False
        )
        for name in _ALL_FALLBACK_NAMES:
            assert callable(getattr(module, name, None)), f"missing {name}"

    def test_no_fallbacks_bind_when_hosts_present(self):
        """Both hosts present binds none of the fallback command functions."""
        module = _load_router_module(economy_installed=True, fixedincome_installed=True)
        for name in _ALL_FALLBACK_NAMES:
            assert getattr(module, name, None) is None, f"unexpected {name}"

    def test_only_economy_fallbacks_bind_when_economy_absent(self):
        """Economy absent, fixedincome present binds only the economy fallbacks."""
        module = _load_router_module(
            economy_installed=False, fixedincome_installed=True
        )
        for name in _ECONOMY_FALLBACK_NAMES:
            assert callable(getattr(module, name, None)), f"missing {name}"
        for name in _FIXEDINCOME_FALLBACK_NAMES:
            assert getattr(module, name, None) is None, f"unexpected {name}"

    def test_only_fixedincome_fallbacks_bind_when_fixedincome_absent(self):
        """Fixedincome absent, economy present binds only the fixedincome fallbacks."""
        module = _load_router_module(
            economy_installed=True, fixedincome_installed=False
        )
        for name in _FIXEDINCOME_FALLBACK_NAMES:
            assert callable(getattr(module, name, None)), f"missing {name}"
        for name in _ECONOMY_FALLBACK_NAMES:
            assert getattr(module, name, None) is None, f"unexpected {name}"

    def test_utility_routes_always_registered(self):
        """The three utility endpoints are registered on the live router."""
        paths = {route.path for route in iter_api_routes(fr.router.api_router)}
        assert {
            "/apps.json",
            "/fomc_documents_download",
            "/fomc_documents_choices",
        } <= (paths)


class TestFallbackCommandBodies:
    """Each fallback command delegates to ``OBBject.from_query``."""

    @pytest.mark.asyncio
    @pytest.mark.parametrize("name", _ALL_FALLBACK_NAMES)
    async def test_command_delegates_to_from_query(self, name):
        """The live fallback command awaits ``OBBject.from_query``."""
        fn = getattr(fr, name)
        sentinel = object()
        with (
            patch.object(fr, "Query", new=MagicMock()),
            patch.object(
                fr.OBBject, "from_query", new=AsyncMock(return_value=sentinel)
            ) as mock_from_query,
        ):
            out = await fn(
                cc=MagicMock(),
                provider_choices=MagicMock(),
                standard_params=MagicMock(),
                extra_params=MagicMock(),
            )
        assert out is sentinel
        mock_from_query.assert_awaited_once()


class TestProviderCommandBodies:
    """The remaining always-registered commands delegate to ``OBBject.from_query``."""

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "name",
        [
            "money_market_funds",
            "international_portfolio_investment",
        ],
    )
    async def test_command_delegates_to_from_query(self, name):
        """Each command awaits ``OBBject.from_query`` and returns its result."""
        sentinel = object()
        with (
            patch.object(fr, "Query", new=MagicMock()),
            patch.object(
                fr.OBBject, "from_query", new=AsyncMock(return_value=sentinel)
            ) as mock_from_query,
        ):
            out = await getattr(fr, name)(
                cc=MagicMock(),
                provider_choices=MagicMock(),
                standard_params=MagicMock(),
                extra_params=MagicMock(),
            )
        assert out is sentinel
        mock_from_query.assert_awaited_once()


class TestRegionalPublicationsDownload:
    """Tests for the ``regional_publications_download`` utility endpoint."""

    @pytest.mark.asyncio
    async def test_downloads_pdf_as_base64(self):
        """A valid URL is fetched and returned as base64-encoded PDF content."""
        response = MagicMock()
        response.content = b"%PDF-1.7 regional"
        response.raise_for_status = MagicMock()
        with patch(
            "openbb_core.provider.utils.helpers.make_request", return_value=response
        ):
            out = await fr.regional_publications_download(
                {"url": ["https://example.com/dir/report.pdf"]}
            )
        assert out[0]["data_format"]["data_type"] == "pdf"
        assert out[0]["data_format"]["filename"] == "report.pdf"
        assert isinstance(out[0]["content"], str)

    @pytest.mark.asyncio
    async def test_download_error_with_args_is_captured(self):
        """A failure carrying args records the first arg as the message."""
        with patch(
            "openbb_core.provider.utils.helpers.make_request",
            side_effect=RuntimeError("boom"),
        ):
            out = await fr.regional_publications_download(
                {"url": ["https://example.com/x.pdf"]}
            )
        assert out[0]["error_type"] == "download_error"
        assert out[0]["content"] == "RuntimeError: boom"
        assert out[0]["filename"] == "x.pdf"

    @pytest.mark.asyncio
    async def test_download_error_without_args_falls_back_to_str(self):
        """A failure with no args falls back to ``str(exc)`` for the message."""
        with patch(
            "openbb_core.provider.utils.helpers.make_request",
            side_effect=RuntimeError(),
        ):
            out = await fr.regional_publications_download(
                {"url": ["https://example.com/y.pdf"]}
            )
        assert out[0]["error_type"] == "download_error"
        assert out[0]["content"] == "RuntimeError: "

    @pytest.mark.asyncio
    async def test_empty_url_list_returns_empty(self):
        """An absent ``url`` key yields an empty result list."""
        assert await fr.regional_publications_download({}) == []


class TestKeyHelper:
    """Tests for the ``_key`` host-selection helper in the provider module."""

    def test_returns_standard_when_installed(self):
        """The standard model key is used when the host extension is installed."""
        from openbb_federal_reserve import _key

        assert _key("MoneyMeasures", "FederalReserveMoneyMeasures", True) == (
            "MoneyMeasures"
        )

    def test_returns_alias_when_absent(self):
        """The federal_reserve alias key is used when the host is absent."""
        from openbb_federal_reserve import _key

        assert _key("SOFR", "FederalReserveSOFR", False) == "FederalReserveSOFR"

    def test_live_fetcher_dict_uses_aliases_when_hosts_absent(self):
        """In this test environment the provider registers alias keys."""
        from openbb_federal_reserve import federal_reserve_provider

        keys = set(federal_reserve_provider.fetcher_dict)
        assert "FederalReserveMoneyMeasures" in keys
        assert "FederalReserveSOFR" in keys
        assert "MoneyMeasures" not in keys


class TestDdpCommands:
    """Tests for the always-registered Data Download Program commands."""

    def test_ddp_routes_registered(self):
        """The DDP discovery and data routes are present on the router."""
        paths = {route.path for route in iter_api_routes(fr.router.api_router)}
        assert {
            "/list_releases",
            "/list_datasets",
            "/release_calendar",
            "/fed_data",
        } <= paths

    @pytest.mark.asyncio
    async def test_list_releases_command(self, monkeypatch):
        """``list_releases`` returns the release catalog with public codes."""
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.ddp.list_releases",
            lambda: [
                {"dataset": "H.15", "code": "H15", "name": "Selected Interest Rates"}
            ],
        )
        releases = await fr.list_releases()
        assert any(record["dataset"] == "H.15" for record in releases)

    @pytest.mark.asyncio
    async def test_list_datasets_command(self, monkeypatch):
        """``list_datasets`` returns a release's table choices."""
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.ddp.list_datasets",
            lambda dataset: [
                {
                    "table": "Treasury Constant Maturities",
                    "dataset": "H.15",
                    "release_name": "Selected Interest Rates",
                }
            ],
        )
        datasets = await fr.list_datasets("H.15")
        assert datasets and all("table" in dataset for dataset in datasets)

    @pytest.mark.asyncio
    async def test_list_datasets_command_filtered(self, monkeypatch):
        """``list_datasets`` passes the selected release through."""
        captured: dict = {}
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.ddp.list_datasets",
            lambda dataset=None: (
                captured.update(dataset=dataset)
                or [{"dataset": "H.15", "table": "x", "release_name": "l"}]
            ),
        )
        datasets = await fr.list_datasets("H.15")
        assert captured == {"dataset": "H.15"}
        assert all(dataset["dataset"] == "H.15" for dataset in datasets)

    @pytest.mark.asyncio
    async def test_release_calendar_command(self, monkeypatch):
        """``release_calendar`` filters the schedule by the date window."""
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.ddp.fetch_release_schedule",
            lambda: [
                {"date": "2025-12-31", "release": "H.15", "title": "t"},
                {"date": "2026-06-30", "release": "Z.1", "title": "t"},
                {"date": "2026-12-31", "release": "H.6", "title": "t"},
            ],
        )
        rows = await fr.release_calendar(start_date="2026-01-01", end_date="2026-09-01")
        assert [r["release"] for r in rows] == ["Z.1"]

    @pytest.mark.asyncio
    async def test_release_calendar_defaults_to_upcoming(self, monkeypatch):
        """With no start date, only releases from today onward are returned."""
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.ddp.fetch_release_schedule",
            lambda: [
                {"date": "2000-01-01", "release": "H.15", "title": "past"},
                {"date": "2099-12-31", "release": "Z.1", "title": "future"},
            ],
        )
        rows = await fr.release_calendar()
        assert [r["release"] for r in rows] == ["Z.1"]

    @pytest.mark.asyncio
    async def test_fed_data_delegates_to_from_query(self):
        """``fed_data`` awaits ``OBBject.from_query``."""
        sentinel = object()
        with (
            patch.object(fr, "Query", new=MagicMock()),
            patch.object(
                fr.OBBject, "from_query", new=AsyncMock(return_value=sentinel)
            ) as mock_from_query,
        ):
            out = await fr.fed_data(
                cc=MagicMock(),
                provider_choices=MagicMock(),
                standard_params=MagicMock(),
                extra_params=MagicMock(),
            )
        assert out is sentinel
        mock_from_query.assert_awaited_once()


class TestFedDataSeriesCellClick:
    """The DDP table self-filters when a ``series_id`` cell is clicked."""

    @staticmethod
    def _series_column():
        """Return the ``fed_data`` route's ``series_id`` column definition."""
        for route in iter_api_routes(fr.router.api_router):
            if route.path.endswith("/fed_data"):
                extra = getattr(route, "openapi_extra", None) or {}
                cols = extra["widget_config"]["data"]["table"]["columnsDefs"]
                return next(c for c in cols if c["field"] == "series_id")
        raise AssertionError("fed_data route not found")

    def test_series_id_emits_groupby_on_the_series_param(self):
        """Clicking a series id groups the dashboard by the ``series`` param."""
        col = self._series_column()
        assert col["renderFn"] == "cellOnClick"
        assert col["renderFnParams"] == {
            "actionType": "groupBy",
            "groupBy": {"paramName": "series"},
        }


class TestYieldCurveWidgetConfig:
    """The yield-curve widget charts maturity on the x-axis, one line per date."""

    @staticmethod
    def _column_defs():
        """Return the yield-curve route's chart column definitions."""
        for route in iter_api_routes(fr.router.api_router):
            if route.path.endswith("/yield_curve"):
                extra = getattr(route, "openapi_extra", None) or {}
                return extra["widget_config"]["data"]["table"]["columnsDefs"]
        raise AssertionError("yield_curve route not found")

    def test_maturity_is_sole_x_axis_category(self):
        """Exactly one column is the chart category and it is ``maturity``."""
        cols = self._column_defs()
        categories = [c["field"] for c in cols if c.get("chartDataType") == "category"]
        assert categories == ["maturity"]

    def test_rate_is_the_series_value(self):
        """``rate`` is the plotted series and keeps the percent formatter."""
        cols = self._column_defs()
        rate = next(c for c in cols if c["field"] == "rate")
        assert rate["chartDataType"] == "series"
        assert rate["formatterFn"] == "normalizedPercent"

    def test_date_is_excluded_from_the_chart_axis(self):
        """``date`` splits the lines but is never a competing x-axis category."""
        cols = self._column_defs()
        date = next(c for c in cols if c["field"] == "date")
        assert date["chartDataType"] == "excluded"


class TestFfiecSubrouterMounted:
    """The FFIEC subrouter is mounted under ``/ffiec`` on the main router."""

    def test_ffiec_command_routes_mounted_under_prefix(self):
        """The moved FFIEC commands are reachable under the ``/ffiec`` prefix."""
        paths = {route.path for route in iter_api_routes(fr.router.api_router)}
        for name in (
            "institutions",
            "large_holding_companies",
            "institution_structure",
            "bhcpr_report",
            "ubpr",
            "call_report",
            "country_exposure",
        ):
            assert any(p.endswith(f"/ffiec/{name}") for p in paths), name

    def test_ffiec_commands_not_on_main_router_root(self):
        """The moved commands no longer bind at the bare main-router root."""
        paths = {route.path for route in iter_api_routes(fr.router.api_router)}
        for name in ("institutions", "ubpr", "bhcpr_report"):
            assert f"/{name}" not in paths, name
