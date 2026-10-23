"""Tests for the statements shaped a period per column."""

import pytest
from openbb_core.app.model.abstract.error import OpenBBError

from openbb_tmx.models.income_statement import TmxIncomeStatementData
from openbb_tmx.routers import fundamentals as fundamentals_router
from openbb_tmx.utils.statements import statement_table

REPORTS = [
    {
        "period_ending": "2025-12-31",
        "fiscal_period": "annual",
        "fiscal_year": 2025,
        "reported_currency": "CAD",
        "total_revenue": 22372000000.0,
        "cost_of_revenue": 17086000000.0,
    },
    {
        "period_ending": "2024-12-31",
        "fiscal_period": "annual",
        "fiscal_year": 2024,
        "reported_currency": "CAD",
        "total_revenue": 22255000000.0,
        "cost_of_revenue": None,
    },
]


@pytest.fixture
def reported(monkeypatch):
    """Serve two annual reports for every statement."""
    seen: dict = {}

    async def fetch(params, credentials):
        seen.update(params)

        return [TmxIncomeStatementData.model_validate(r) for r in REPORTS]

    for module, name in (
        ("income_statement", "TmxIncomeStatementFetcher"),
        ("balance_sheet", "TmxBalanceSheetFetcher"),
        ("cash_flow", "TmxCashFlowStatementFetcher"),
    ):
        monkeypatch.setattr(f"openbb_tmx.models.{module}.{name}.fetch_data", fetch)

    return seen


class TestStatementTable:
    """One line item per row, one reported period per column."""

    async def test_the_periods_are_the_columns(self, reported):
        rows = await statement_table("income", "AC")

        assert list(rows[0])[0] == "Item"
        assert list(rows[0])[1:] == ["2025-12-31", "2024-12-31"]

    async def test_every_line_item_is_a_row(self, reported):
        rows = await statement_table("income", "AC")
        items = [row["Item"] for row in rows]

        assert "Total Revenue" in items
        assert "Reported Currency" in items

    async def test_a_line_item_carries_each_period(self, reported):
        rows = await statement_table("income", "AC")
        revenue = next(r for r in rows if r["Item"] == "Total Revenue")

        assert revenue["2025-12-31"] == 22372000000.0
        assert revenue["2024-12-31"] == 22255000000.0

    async def test_a_period_the_company_left_empty_is_kept_empty(self, reported):
        rows = await statement_table("income", "AC")
        cost = next(r for r in rows if r["Item"] == "Cost Of Revenue")

        assert cost["2024-12-31"] is None

    async def test_the_period_and_the_fiscal_labels_are_not_rows(self, reported):
        items = [row["Item"] for row in await statement_table("income", "AC")]

        assert "Period Ending" not in items
        assert "Fiscal Period" not in items
        assert "Fiscal Year" not in items

    async def test_a_line_item_no_period_reports_is_left_out(self, reported):
        items = [row["Item"] for row in await statement_table("income", "AC")]

        assert "Gross Profit" not in items

    async def test_the_query_is_passed_through(self, reported):
        await statement_table("income", "GIL", "quarter", use_cache=False)

        assert reported["symbol"] == "GIL"
        assert reported["period"] == "quarter"
        assert reported["use_cache"] is False

    async def test_the_periods_can_be_capped(self, reported):
        rows = await statement_table("income", "AC", limit=1)

        assert list(rows[0])[1:] == ["2025-12-31"]

    async def test_an_unknown_statement_is_reported(self):
        with pytest.raises(OpenBBError, match="Unknown statement"):
            await statement_table("nope", "AC")


class TestStatementRoutes:
    """Each statement is served by its own route."""

    @pytest.mark.parametrize(
        ("view", "statement"),
        [
            (fundamentals_router.income_view, "income"),
            (fundamentals_router.balance_view, "balance"),
            (fundamentals_router.cash_view, "cash"),
        ],
    )
    async def test_the_statement_is_served(self, reported, view, statement):
        rows = await view(symbol="AC")

        assert rows[0]["Item"]
        assert "2025-12-31" in rows[0]

    def test_each_view_declares_its_widget(self):
        config = fundamentals_router._statement_widget("TMX Income", "income")[
            "widget_config"
        ]

        assert config["widgetId"] == "tmx_equity_fundamental_income_view_obb"
        assert [p["paramName"] for p in config["params"]] == [
            "symbol",
            "period",
            "limit",
            "use_cache",
        ]
