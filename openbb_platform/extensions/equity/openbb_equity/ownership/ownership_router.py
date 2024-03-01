"""Ownership Router."""

from openbb_core.app.model import CommandContext, Example, OBBject
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
    api_examples=[Example(parameters={"symbol": "AAPL", "page": 0})],
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
    api_examples=[Example(parameters={"symbol": "AAPL"})],
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
    api_examples=[Example(parameters={"symbol": "AAPL", "limit": 500})],
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
    model="ShareStatistics", api_examples=[Example(parameters={"symbol": "AAPL"})]
)
async def share_statistics(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get data about share float for a given company."""
    return await OBBject.from_query(Query(**locals()))
