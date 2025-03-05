# pylint: disable=W0613:unused-argument
"""Comparison Analysis Router."""

from openbb_core.app.model.command_context import CommandContext
from openbb_core.app.model.example import APIEx
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.provider_interface import (
    ExtraParams,
    ProviderChoices,
    StandardParams,
)
from openbb_core.app.query import Query
from openbb_core.app.router import Router

router = Router(prefix="/compare")


@router.command(
    model="EquityPeers",
    examples=[APIEx(parameters={"symbol": "AAPL", "provider": "fmp"})],
)
async def peers(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the closest peers for a given company.

    Peers consist of companies trading on the same exchange, operating within the same sector
    and with comparable market capitalizations.
    """
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="CompareGroups",
    examples=[
        APIEx(parameters={"provider": "finviz"}),
        APIEx(
            description="Group by sector and analyze valuation.",
            parameters={"group": "sector", "metric": "valuation", "provider": "finviz"},
        ),
        APIEx(
            description="Group by industry and analyze performance.",
            parameters={
                "group": "industry",
                "metric": "performance",
                "provider": "finviz",
            },
        ),
        APIEx(
            description="Group by country and analyze valuation.",
            parameters={
                "group": "country",
                "metric": "valuation",
                "provider": "finviz",
            },
        ),
    ],
)
async def groups(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get company data grouped by sector, industry or country and display either performance or valuation metrics.

    Valuation metrics include price to earnings, price to book, price to sales ratios and price to cash flow.
    Performance metrics include the stock price change for different time periods.
    """
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="CompareCompanyFacts",
    examples=[
        APIEx(parameters={"provider": "sec"}),
        APIEx(
            parameters={
                "provider": "sec",
                "fact": "PaymentsForRepurchaseOfCommonStock",
                "year": 2023,
            }
        ),
        APIEx(
            parameters={
                "provider": "sec",
                "symbol": "NVDA,AAPL,AMZN,MSFT,GOOG,SMCI",
                "fact": "RevenueFromContractWithCustomerExcludingAssessedTax",
                "year": 2024,
            }
        ),
    ],
)
async def company_facts(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Compare reported company facts and fundamental data points."""
    return await OBBject.from_query(Query(**locals()))
