"""Tests for the US Treasury router commands and endpoints."""

import asyncio
from unittest.mock import AsyncMock, patch

import pytest
from openbb_core.app.router import Router

from openbb_government_us.treasury import FIXEDINCOME_INSTALLED, treasury_router
from openbb_government_us.treasury.utils import fiscal_data, usaspending


def _patch_usaspending(monkeypatch, get_response=None, post_response=None):
    """Patch the USAspending helpers and record the calls they receive."""
    captured: dict = {}

    async def _fake_get(path, **kwargs):
        captured["get_path"] = path
        return get_response or {}

    async def _fake_post(path, payload, **kwargs):
        captured["post_path"] = path
        captured["payload"] = payload
        return post_response or {}

    monkeypatch.setattr(usaspending, "get_usaspending", _fake_get)
    monkeypatch.setattr(usaspending, "post_usaspending", _fake_post)
    return captured


MODEL_COMMANDS = [
    treasury_router.debt_to_penny,
    treasury_router.daily_statement,
    treasury_router.upcoming_auctions,
    treasury_router.auction_results,
    treasury_router.weekly_bill_offerings,
    treasury_router.bulletin,
    treasury_router.award,
    treasury_router.award_search,
    treasury_router.spending_explorer,
    treasury_router.recipient_search,
    treasury_router.recipient_awards,
] + (
    []
    if FIXEDINCOME_INSTALLED
    else [treasury_router.treasury_auctions, treasury_router.treasury_prices]
)


class TestTreasuryRouter:
    """Tests for the treasury Router registration and command delegation."""

    def test_router_is_openbb_router(self):
        """The exported router is an openbb_core Router instance."""
        assert isinstance(treasury_router.router, Router)

    def test_registered_command_paths(self):
        """The FiscalData commands are always registered on the api_router."""
        paths = {route.path for route in treasury_router.router.api_router.routes}
        assert paths >= {
            "/debt_to_penny",
            "/daily_statement",
            "/upcoming_auctions",
            "/auction_results",
            "/weekly_bill_offerings",
            "/bulletin",
        }

    def test_option_endpoints_are_hidden_from_the_widget_list(self):
        """Every option endpoint is registered but excluded from the widgets."""
        routes = {
            route.path: route
            for route in treasury_router.router.api_router.routes
            if route.path
            in {
                "/dts_amount_bases",
                "/dts_sub_tables",
                "/explorer_types",
                "/spending_options",
                "/awarding_agencies",
                "/def_codes",
            }
        }
        assert len(routes) == 6
        for route in routes.values():
            assert route.openapi_extra["widget_config"] == {"exclude": True}

    def test_treasurydirect_commands_registered_without_fixedincome(self):
        """The TreasuryDirect commands register only when openbb-fixedincome is absent."""
        paths = {route.path for route in treasury_router.router.api_router.routes}
        expected = not FIXEDINCOME_INSTALLED
        assert ("/treasury_auctions" in paths) is expected
        assert ("/treasury_prices" in paths) is expected

    @pytest.mark.parametrize("command", MODEL_COMMANDS)
    def test_model_backed_commands(self, command):
        """Each command delegates to OBBject.from_query(OpenBBQuery(...))."""

        class _Result:
            results = ["sentinel"]

        with (
            patch.object(treasury_router, "OBBject") as mock_obbject,
            patch.object(treasury_router, "OpenBBQuery") as mock_query,
        ):
            mock_obbject.from_query = AsyncMock(return_value=_Result())

            result = asyncio.run(
                command(
                    cc=None,
                    provider_choices=None,
                    standard_params=None,
                    extra_params=None,
                )
            )

        assert mock_query.called
        mock_obbject.from_query.assert_awaited_once()
        assert mock_obbject.from_query.await_args.args == (mock_query.return_value,)
        assert result.results == ["sentinel"]


class TestDtsOptionEndpoints:
    """Tests for the Daily Treasury Statement option endpoints."""

    def test_amount_bases_list_the_balances_a_table_publishes(self):
        """The balance table offers its four balances plus the combined entry."""
        assert asyncio.run(treasury_router.dts_amount_bases()) == [
            {"label": "Close Today", "value": "Close Today"},
            {"label": "Open Today", "value": "Open Today"},
            {"label": "Open Month", "value": "Open Month"},
            {"label": "Open Fiscal Year", "value": "Open Fiscal Year"},
            {"label": "All bases", "value": "all"},
        ]

    def test_amount_bases_follow_the_requested_table(self):
        """A flow table offers the three cumulative bases, not the balances."""
        assert asyncio.run(
            treasury_router.dts_amount_bases("deposits_withdrawals_operating_cash")
        ) == [
            {"label": "Today", "value": "Today"},
            {"label": "Month to Date", "value": "Month to Date"},
            {"label": "Fiscal Year to Date", "value": "Fiscal Year to Date"},
            {"label": "All bases", "value": "all"},
        ]

    def test_sub_tables_list_the_published_values(self, monkeypatch):
        """The sub-table options come from the table's recent publications."""
        captured: dict = {}

        async def _fake(endpoint, filters=None, sort=None, **kwargs):
            captured["endpoint"] = endpoint
            return [
                {"transaction_type": "Withdrawals"},
                {"transaction_type": "Deposits"},
                {"transaction_type": "Deposits"},
            ]

        monkeypatch.setattr(fiscal_data, "get_fiscal_data", _fake)
        options = asyncio.run(
            treasury_router.dts_sub_tables("deposits_withdrawals_operating_cash")
        )
        assert captured["endpoint"] == (
            "v1/accounting/dts/deposits_withdrawals_operating_cash"
        )
        assert options == [
            {"label": "Deposits", "value": "Deposits"},
            {"label": "Withdrawals", "value": "Withdrawals"},
            {"label": "All Sub-Tables", "value": "all"},
        ]

    def test_sub_tables_of_an_unknown_table_are_empty(self):
        """A table the model does not publish offers nothing."""
        assert asyncio.run(treasury_router.dts_sub_tables("nope")) == []


class TestSpendingOptionEndpoints:
    """Tests for the USAspending option endpoints."""

    def test_explorer_types_hide_the_unscoped_breakdowns(self):
        """Without a scope, only the breakdowns that enumerate whole are offered."""
        options = asyncio.run(treasury_router.explorer_types())
        assert [option["value"] for option in options] == [
            "object_class",
            "budget_function",
            "budget_subfunction",
            "agency",
            "federal_account",
        ]
        assert options[0] == {"label": "Object Class", "value": "object_class"}

    def test_explorer_types_open_up_once_scoped(self):
        """Any scoping filter unlocks the breakdowns too large to list globally."""
        options = asyncio.run(treasury_router.explorer_types(agency="1173"))
        assert [option["value"] for option in options][-4:] == [
            "program_activity",
            "recipient",
            "award",
            "award_category",
        ]
        assert asyncio.run(treasury_router.explorer_types(object_class="30")) == options

    def test_spending_options_query_the_latest_submission(self, monkeypatch):
        """The dimension entries are fetched for the most recent published period."""
        captured = _patch_usaspending(
            monkeypatch,
            get_response={
                "available_periods": [
                    {"submission_fiscal_year": 2024, "submission_fiscal_month": 12},
                    {"submission_fiscal_year": 2025, "submission_fiscal_month": 8},
                ]
            },
            post_response={
                "results": [
                    {"id": 1173, "name": "Department of Justice"},
                    {"id": 12, "name": "Department of Agriculture"},
                ]
            },
        )
        options = asyncio.run(treasury_router.spending_options())
        assert captured["post_path"] == "spending/"
        assert captured["payload"] == {
            "type": "agency",
            "filters": {"fy": "2025", "period": "8"},
        }
        assert options == [
            {"label": "Department of Agriculture", "value": "12"},
            {"label": "Department of Justice", "value": "1173"},
        ]

    def test_spending_options_scope_to_an_agency(self, monkeypatch):
        """A given agency narrows the entries the source returns."""
        captured = _patch_usaspending(
            monkeypatch,
            get_response={
                "available_periods": [
                    {"submission_fiscal_year": 2025, "submission_fiscal_month": 8}
                ]
            },
            post_response={"results": [{"id": "075-0512", "name": "Defense Health"}]},
        )
        options = asyncio.run(
            treasury_router.spending_options("federal_account", agency="1173")
        )
        assert captured["payload"] == {
            "type": "federal_account",
            "filters": {"fy": "2025", "period": "8", "agency": "1173"},
        }
        assert options == [{"label": "Defense Health", "value": "075-0512"}]

    def test_awarding_agencies_are_listed_by_name(self, monkeypatch):
        """The agencies are sorted by name and the unnamed ones dropped."""
        captured = _patch_usaspending(
            monkeypatch,
            get_response={
                "results": [
                    {"agency_name": "Department of Defense"},
                    {"agency_name": "Department of Agriculture"},
                    {"agency_name": None},
                ]
            },
        )
        assert asyncio.run(treasury_router.awarding_agencies()) == [
            {
                "label": "Department of Agriculture",
                "value": "Department of Agriculture",
            },
            {"label": "Department of Defense", "value": "Department of Defense"},
        ]
        assert captured["get_path"] == "references/toptier_agencies/"

    def test_def_codes_label_the_code_with_its_title(self, monkeypatch):
        """Each code is labelled with its title, and a titleless code stands alone."""
        captured = _patch_usaspending(
            monkeypatch,
            get_response={
                "codes": [
                    {"code": "L", "title": "Coronavirus Preparedness"},
                    {"code": "Q", "title": None, "public_law": None},
                    {"code": None, "title": "dropped"},
                ]
            },
        )
        assert asyncio.run(treasury_router.def_codes()) == [
            {"label": "L - Coronavirus Preparedness", "value": "L"},
            {"label": "Q", "value": "Q"},
        ]
        assert captured["get_path"] == "references/def_codes/"
