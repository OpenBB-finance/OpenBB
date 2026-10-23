"""Nasdaq Fundamentals sub-router."""

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

from openbb_nasdaq import EQUITY_INSTALLED

router = Router(
    prefix="/equity/fundamental", description="Nasdaq company fundamentals."
)


if not EQUITY_INSTALLED:

    @router.command(
        model="NasdaqIncomeStatement",
        examples=[
            APIEx(
                description="The annual income statement.",
                parameters={"symbol": "AAPL", "provider": "nasdaq"},
            )
        ],
    )
    async def income(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Income statement, as published on the Nasdaq financials tab."""
        return await OBBject.from_query(OBBQuery(**locals()))

    @router.command(
        model="NasdaqBalanceSheet",
        examples=[
            APIEx(
                description="The annual balance sheet.",
                parameters={"symbol": "AAPL", "provider": "nasdaq"},
            )
        ],
    )
    async def balance(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Balance sheet, as published on the Nasdaq financials tab."""
        return await OBBject.from_query(OBBQuery(**locals()))

    @router.command(
        model="NasdaqCashFlowStatement",
        examples=[
            APIEx(
                description="The annual cash flow statement.",
                parameters={"symbol": "AAPL", "provider": "nasdaq"},
            )
        ],
    )
    async def cash(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Cash flow statement, as published on the Nasdaq financials tab."""
        return await OBBject.from_query(OBBQuery(**locals()))

    @router.command(
        model="NasdaqFinancialRatios",
        examples=[
            APIEx(
                description="Liquidity and profitability ratios.",
                parameters={"symbol": "AAPL", "provider": "nasdaq"},
            )
        ],
    )
    async def ratios(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Liquidity and profitability ratios, as published by Nasdaq."""
        return await OBBject.from_query(OBBQuery(**locals()))

    @router.command(
        model="NasdaqHistoricalDividends",
        examples=[
            APIEx(
                description="The dividend payment history.",
                parameters={"symbol": "AAPL", "provider": "nasdaq"},
            )
        ],
    )
    async def dividends(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Historical dividend payments for a symbol."""
        return await OBBject.from_query(OBBQuery(**locals()))

    @router.command(
        model="NasdaqHistoricalEps",
        examples=[
            APIEx(
                description="Reported versus consensus EPS.",
                parameters={"symbol": "AAPL", "provider": "nasdaq"},
            )
        ],
    )
    async def historical_eps(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Get reported EPS against the consensus forecast, with the surprise."""
        return await OBBject.from_query(OBBQuery(**locals()))
