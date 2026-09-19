"""TMX Fundamentals sub-router."""

from openbb_core.app.model.command_context import CommandContext
from openbb_core.app.model.example import APIEx
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.provider_interface import (
    ExtraParams,
    ProviderChoices,
    StandardParams,
)
from openbb_core.app.query import Query as OBBQuery
from openbb_core.app.router import Router

from openbb_tmx import EQUITY_INSTALLED

router = Router(prefix="/equity/fundamental", description="TMX company fundamentals.")


if not EQUITY_INSTALLED:

    @router.command(
        model="TmxIncomeStatement",
        widget_config={"data": {"table": {"transpose": True}}},
        examples=[
            APIEx(
                description="Income statement.",
                parameters={"symbol": "AC", "provider": "tmx"},
            )
        ],
    )
    async def income(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Income statement, annual or quarterly."""
        return await OBBject.from_query(OBBQuery(**locals()))

    @router.command(
        model="TmxBalanceSheet",
        widget_config={"data": {"table": {"transpose": True}}},
        examples=[
            APIEx(
                description="Balance sheet.",
                parameters={"symbol": "AC", "provider": "tmx"},
            )
        ],
    )
    async def balance(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Balance sheet, annual or quarterly."""
        return await OBBject.from_query(OBBQuery(**locals()))

    @router.command(
        model="TmxCashFlowStatement",
        widget_config={"data": {"table": {"transpose": True}}},
        examples=[
            APIEx(
                description="Cash flow statement.",
                parameters={"symbol": "AC", "provider": "tmx"},
            )
        ],
    )
    async def cash(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Cash flow statement, annual or quarterly."""
        return await OBBject.from_query(OBBQuery(**locals()))

    @router.command(
        model="TmxHistoricalDividends",
        examples=[
            APIEx(
                description="Declared dividend history.",
                parameters={"symbol": "BNS", "provider": "tmx"},
            )
        ],
    )
    async def dividends(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Return declared dividends, with ex, record, and payable dates."""
        return await OBBject.from_query(OBBQuery(**locals()))

    @router.command(
        model="TmxHistoricalSplits",
        examples=[
            APIEx(
                description="Share split history.",
                parameters={"symbol": "BNS", "provider": "tmx"},
            )
        ],
    )
    async def splits(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Historical share splits."""
        return await OBBject.from_query(OBBQuery(**locals()))


def _statement_widget(name: str, statement: str) -> dict:
    """Build the Workspace widget config for one statement view."""
    return {
        "widget_config": {
            "name": name,
            "description": f"The {statement} statement, a column per reported period.",
            "category": "Equity",
            "subCategory": "Fundamental",
            "widgetId": f"tmx_equity_fundamental_{statement}_view_obb",
            "source": ["TMX"],
            "gridData": {"w": 40, "h": 20},
            "params": [
                {
                    "paramName": "symbol",
                    "label": "Symbol",
                    "value": "AC",
                    "description": "The company to report on.",
                },
                {
                    "paramName": "period",
                    "label": "Period",
                    "value": "annual",
                    "description": "Annual or quarterly reports.",
                    "options": [
                        {"label": "Annual", "value": "annual"},
                        {"label": "Quarter", "value": "quarter"},
                    ],
                },
                {
                    "paramName": "limit",
                    "label": "Periods",
                    "value": 10,
                    "description": "How many periods to report, newest first.",
                },
                {"paramName": "use_cache", "label": "Use Cache", "value": True},
            ],
        }
    }


async def income_view(
    symbol: str = "AC",
    period: str = "annual",
    limit: int = 10,
    use_cache: bool = True,
) -> list:
    """Serve the income statement, a column per reported period."""
    from openbb_tmx.utils.statements import statement_table

    return await statement_table("income", symbol, period, limit, use_cache)


async def balance_view(
    symbol: str = "AC",
    period: str = "annual",
    limit: int = 10,
    use_cache: bool = True,
) -> list:
    """Serve the balance sheet, a column per reported period."""
    from openbb_tmx.utils.statements import statement_table

    return await statement_table("balance", symbol, period, limit, use_cache)


async def cash_view(
    symbol: str = "AC",
    period: str = "annual",
    limit: int = 10,
    use_cache: bool = True,
) -> list:
    """Serve the cash flow statement, a column per reported period."""
    from openbb_tmx.utils.statements import statement_table

    return await statement_table("cash", symbol, period, limit, use_cache)


for _path, _endpoint, _name, _statement in (
    ("/income_view", income_view, "TMX Income Statement", "income"),
    ("/balance_view", balance_view, "TMX Balance Sheet", "balance"),
    ("/cash_view", cash_view, "TMX Cash Flow Statement", "cash"),
):
    router.api_router.add_api_route(
        path=_path,
        endpoint=_endpoint,
        methods=["GET"],
        include_in_schema=True,
        openapi_extra=_statement_widget(_name, _statement),
    )
