"""Tests for the regional Fed subrouter registration and command bodies."""

import importlib.util
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from openbb_core.app.route_iter import iter_api_routes
from openbb_core.app.router import Router

import openbb_federal_reserve
from openbb_federal_reserve import federal_reserve_router as fr
from openbb_federal_reserve.regional import (
    atlanta,
    boston,
    chicago,
    cleveland,
    dallas,
    kansas_city,
    minneapolis,
    new_york,
    philadelphia,
    richmond,
    san_francisco,
    st_louis,
)

_NY_FIXEDINCOME_NAMES = ("sofr", "effr", "overnight_bank_funding")
_NY_ECONOMY_NAMES = (
    "central_bank_holdings",
    "primary_dealer_positioning",
    "primary_dealer_fails",
)


def _load_new_york_module(economy_installed: bool, fixedincome_installed: bool):
    """Re-execute the NY regional router with the host flags forced.

    Mirrors the main-router loader: the NY-Fed reference-rate and dealer
    commands are relocated fallbacks that bind only when their host extension
    is absent. ``Router.command`` is replaced with a passthrough so the
    commands bind without the host-prefixed models in the live registry.
    """
    spec = importlib.util.spec_from_file_location(
        "openbb_federal_reserve_new_york_standalone",
        Path(new_york.__file__),
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


class TestRegionalRoutes:
    """The district subrouters are mounted under district prefixes."""

    def test_subrouters_included(self):
        """Each district command is reachable under its prefix."""
        paths = {route.path for route in iter_api_routes(fr.router.api_router)}
        assert any(p.endswith("/chicago/national_activity") for p in paths)
        assert any(p.endswith("/chicago/financial_conditions") for p in paths)
        assert any(p.endswith("/philadelphia/business_conditions") for p in paths)
        assert any(p.endswith("/ny/supply_chain_pressure") for p in paths)
        assert any(p.endswith("/cleveland/inflation_expectations") for p in paths)

    def test_relocated_ny_fed_routes(self):
        """The NY-Fed reference-rate and dealer commands mount under ``/ny``."""
        paths = {route.path for route in iter_api_routes(fr.router.api_router)}
        for name in _NY_FIXEDINCOME_NAMES + _NY_ECONOMY_NAMES:
            assert any(p.endswith(f"/ny/{name}") for p in paths), name


class TestNyFedFallbackRegistration:
    """The relocated NY-Fed commands bind under ``/ny`` only when hosts absent."""

    def test_bind_when_hosts_absent(self):
        """Both hosts absent binds all relocated NY-Fed commands."""
        module = _load_new_york_module(
            economy_installed=False, fixedincome_installed=False
        )
        for name in _NY_ECONOMY_NAMES + _NY_FIXEDINCOME_NAMES:
            assert callable(getattr(module, name, None)), f"missing {name}"

    def test_absent_when_hosts_present(self):
        """Both hosts present binds none of the relocated NY-Fed commands."""
        module = _load_new_york_module(
            economy_installed=True, fixedincome_installed=True
        )
        for name in _NY_ECONOMY_NAMES + _NY_FIXEDINCOME_NAMES:
            assert getattr(module, name, None) is None, f"unexpected {name}"

    def test_only_economy_names_bind_when_economy_absent(self):
        """Economy absent, fixedincome present binds only the dealer/SOMA commands."""
        module = _load_new_york_module(
            economy_installed=False, fixedincome_installed=True
        )
        for name in _NY_ECONOMY_NAMES:
            assert callable(getattr(module, name, None)), f"missing {name}"
        for name in _NY_FIXEDINCOME_NAMES:
            assert getattr(module, name, None) is None, f"unexpected {name}"

    def test_only_fixedincome_names_bind_when_fixedincome_absent(self):
        """Fixedincome absent, economy present binds only the reference-rate commands."""
        module = _load_new_york_module(
            economy_installed=True, fixedincome_installed=False
        )
        for name in _NY_FIXEDINCOME_NAMES:
            assert callable(getattr(module, name, None)), f"missing {name}"
        for name in _NY_ECONOMY_NAMES:
            assert getattr(module, name, None) is None, f"unexpected {name}"


class TestMarketProbabilityMeetings:
    """Tests for the dynamic Atlanta market-probability meetings choices route."""

    def test_route_registered_on_main_and_atlanta(self):
        """The choices route mounts at the root and under the Atlanta district."""
        paths = {route.path for route in iter_api_routes(fr.router.api_router)}
        assert "/market_probability_meetings" in paths
        assert any(p.endswith("/atlanta/market_probability_meetings") for p in paths)

    @pytest.mark.asyncio
    async def test_returns_iso_label_value_choices(self, monkeypatch):
        """The endpoint returns the latest date's meetings as ISO label/value pairs."""
        from datetime import date

        from openbb_federal_reserve.models.regional import atlanta_market_probability

        monkeypatch.setattr(
            atlanta_market_probability.FederalReserveAtlantaMarketProbabilityFetcher,
            "extract_data",
            staticmethod(lambda *a, **k: [{"_raw": b"x"}]),
        )
        monkeypatch.setattr(
            atlanta_market_probability,
            "_load_meetings",
            lambda _content: (
                date(2026, 6, 23),
                [date(2026, 7, 29), date(2026, 9, 16)],
            ),
        )
        out = await fr.market_probability_meetings()
        assert out == [
            {"label": "2026-07-29", "value": "2026-07-29"},
            {"label": "2026-09-16", "value": "2026-09-16"},
        ]


class TestRegionalCommandBodies:
    """Each regional command delegates to ``OBBject.from_query``."""

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        ("module", "name"),
        [
            (chicago, "national_activity"),
            (chicago, "financial_conditions"),
            (philadelphia, "business_conditions"),
            (new_york, "supply_chain_pressure"),
            (new_york, "corporate_bond_distress"),
            (new_york, "consumer_expectations"),
            (new_york, "business_leaders"),
            (new_york, "market_expectations"),
            (new_york, "sofr"),
            (new_york, "effr"),
            (new_york, "overnight_bank_funding"),
            (new_york, "central_bank_holdings"),
            (new_york, "primary_dealer_positioning"),
            (new_york, "primary_dealer_fails"),
            (cleveland, "inflation_expectations"),
            (cleveland, "inflation_nowcast"),
            (cleveland, "median_cpi"),
            (cleveland, "median_cpi_components"),
            (cleveland, "systemic_risk"),
            (cleveland, "publications"),
            (cleveland, "publication_series"),
            (dallas, "manufacturing"),
            (dallas, "service_sector"),
            (dallas, "retail"),
            (dallas, "banking_conditions"),
            (dallas, "energy_survey"),
            (dallas, "trimmed_mean_pce"),
            (dallas, "weekly_economic_index"),
            (dallas, "leading_index"),
            (dallas, "global_economic_indicators"),
            (dallas, "global_real_economic_activity"),
            (dallas, "government_debt"),
            (dallas, "agricultural_survey"),
            (dallas, "breakeven_prices"),
            (dallas, "gigafactory_map"),
            (dallas, "lithium_map"),
            (dallas, "publications"),
            (dallas, "publication_series"),
            (san_francisco, "news_sentiment"),
            (san_francisco, "proxy_funds_rate"),
            (san_francisco, "cyclical_pce"),
            (san_francisco, "supply_demand_pce"),
            (san_francisco, "total_factor_productivity"),
            (san_francisco, "term_premium"),
            (san_francisco, "short_rate_path"),
            (san_francisco, "publications"),
            (san_francisco, "publication_series"),
            (minneapolis, "business_conditions"),
            (minneapolis, "regional_employment"),
            (minneapolis, "regional_unemployment"),
            (minneapolis, "labor_force_participation"),
            (minneapolis, "quits_rate"),
            (minneapolis, "regional_gdp"),
            (minneapolis, "regional_cpi"),
            (minneapolis, "unemployment_claims"),
            (minneapolis, "job_openings_hiring"),
            (minneapolis, "publications"),
            (minneapolis, "publication_series"),
            (st_louis, "fred_md"),
            (st_louis, "fred_qd"),
            (st_louis, "national_index"),
            (st_louis, "publications"),
            (st_louis, "publication_series"),
            (atlanta, "gdpnow"),
            (atlanta, "wage_growth"),
            (atlanta, "sticky_cpi"),
            (atlanta, "business_inflation_expectations"),
            (atlanta, "business_uncertainty"),
            (atlanta, "market_probability"),
            (atlanta, "taylor_rule"),
            (atlanta, "taylor_rule_measures"),
            (atlanta, "taylor_rule_heatmap"),
            (atlanta, "publications"),
            (atlanta, "publication_series"),
            (kansas_city, "financial_stress_index"),
            (kansas_city, "risk_index"),
            (kansas_city, "policy_rate_uncertainty"),
            (kansas_city, "natural_rate"),
            (kansas_city, "divisional_lmci"),
            (kansas_city, "ag_credit_survey"),
            (kansas_city, "ag_interest_rates"),
            (kansas_city, "ag_finance_databook"),
            (kansas_city, "ag_terms_of_lending"),
            (kansas_city, "ag_district_surveys"),
            (kansas_city, "ag_databook_archived"),
            (kansas_city, "publications"),
            (kansas_city, "publication_series"),
            (richmond, "manufacturing_survey"),
            (richmond, "service_sector_survey"),
            (richmond, "state_survey"),
            (richmond, "cfo_survey"),
            (richmond, "non_employment_index"),
            (richmond, "recession_indicator"),
            (richmond, "publications"),
            (richmond, "publication_series"),
            (chicago, "economic_conditions"),
            (chicago, "retail_trade"),
            (chicago, "labor_market"),
            (chicago, "farmland_values"),
            (chicago, "ag_credit_conditions"),
            (chicago, "farm_loan_rates"),
            (chicago, "brave_butters_kelley"),
            (chicago, "midwest_economy"),
            (chicago, "publications"),
            (chicago, "publication_series"),
            (philadelphia, "survey_professional_forecasters"),
            (philadelphia, "anxious_index"),
            (philadelphia, "gdpplus"),
            (philadelphia, "partisan_conflict"),
            (philadelphia, "state_coincident_index"),
            (philadelphia, "livingston_survey"),
            (philadelphia, "manufacturing_outlook"),
            (philadelphia, "nonmanufacturing_outlook"),
            (philadelphia, "term_structure_inflation"),
            (philadelphia, "publications"),
            (philadelphia, "publication_series"),
            (new_york, "empire_state_manufacturing"),
            (new_york, "consumer_labor_market"),
            (new_york, "consumer_housing"),
            (new_york, "consumer_credit_access"),
            (new_york, "household_debt"),
            (new_york, "core_trend_inflation"),
            (new_york, "empire_state_reports"),
            (new_york, "publications"),
            (new_york, "publication_series"),
            (boston, "economic_indicators"),
            (boston, "publications"),
            (boston, "publication_series"),
        ],
    )
    async def test_delegates_to_from_query(self, module, name):
        """The command awaits ``OBBject.from_query``."""
        sentinel = object()
        with (
            patch.object(module, "Query", new=MagicMock()),
            patch.object(
                module.OBBject, "from_query", new=AsyncMock(return_value=sentinel)
            ) as mock_from_query,
        ):
            out = await getattr(module, name)(
                cc=MagicMock(),
                provider_choices=MagicMock(),
                standard_params=MagicMock(),
                extra_params=MagicMock(),
            )
        assert out is sentinel
        mock_from_query.assert_awaited_once()
