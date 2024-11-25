"""Ownership Router."""

from openbb_core.app.model.command_context import CommandContext
from openbb_core.app.model.example import APIEx, PythonEx
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.provider_interface import (
    ExtraParams,
    ProviderChoices,
    StandardParams,
)
from openbb_core.app.query import Query
from openbb_core.app.router import Router

router = Router(prefix="/ownership")

# pylint: disable=unused-argument


@router.command(
    model="EquityOwnership",
    examples=[
        APIEx(parameters={"symbol": "AAPL", "provider": "fmp"}),
        APIEx(parameters={"symbol": "AAPL", "page": 0, "provider": "fmp"}),
    ],
)
async def major_holders(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get data about major holders for a given company over time."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="InstitutionalOwnership",
    examples=[APIEx(parameters={"symbol": "AAPL", "provider": "fmp"})],
)
async def institutional(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get data about institutional ownership for a given company over time."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="InsiderTrading",
    examples=[
        APIEx(parameters={"symbol": "AAPL", "provider": "fmp"}),
        APIEx(parameters={"symbol": "AAPL", "limit": 500, "provider": "intrinio"}),
    ],
)
async def insider_trading(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get data about trading by a company's management team and board of directors."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="ShareStatistics",
    examples=[APIEx(parameters={"symbol": "AAPL", "provider": "fmp"})],
)
async def share_statistics(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get data about share float for a given company."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="Form13FHR",
    examples=[
        APIEx(parameters={"symbol": "NVDA", "provider": "sec"}),
        APIEx(
            description="Enter a date (calendar quarter ending) for a specific report.",
            parameters={"symbol": "BRK-A", "date": "2016-09-30", "provider": "sec"},
        ),
        PythonEx(
            description="Example finding Michael Burry's filings.",
            code=[
                'cik = obb.regulators.sec.institutions_search("Scion Asset Management").results[0].cik',
                "# Use the `limit` parameter to return N number of reports from the most recent.",
                "obb.equity.ownership.form_13f(cik, limit=2).to_df()",
            ],
        ),
    ],
)
async def form_13f(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the form 13F.

    The Securities and Exchange Commission's (SEC) Form 13F is a quarterly report
    that is required to be filed by all institutional investment managers with at least
    $100 million in assets under management.
    Managers are required to file Form 13F within 45 days after the last day of the calendar quarter.
    Most funds wait until the end of this period in order to conceal
    their investment strategy from competitors and the public.
    """
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="GovernmentTrades",
    examples=[
        APIEx(parameters={"symbol": "AAPL", "chamber": "all", "provider": "fmp"}),
        APIEx(parameters={"limit": 500, "chamber": "all", "provider": "fmp"}),
    ],
)
async def government_trades(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Obtain government transaction data, including data from the Senate
    and the House of Representatives.
    """
    return await OBBject.from_query(Query(**locals()))
