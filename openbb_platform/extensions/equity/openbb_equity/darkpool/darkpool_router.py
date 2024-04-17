"""Dark Pool Router."""

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

router = Router(prefix="/darkpool")

# pylint: disable=unused-argument


@router.command(
    model="OTCAggregate",
    examples=[
        APIEx(parameters={"provider": "finra"}),
        APIEx(
            description="Get OTC data for a symbol",
            parameters={"symbol": "AAPL", "provider": "finra"},
        ),
    ],
)
async def otc(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the weekly aggregate trade data for Over The Counter deals.

    ATS and non-ATS trading data for each ATS/firm
    with trade reporting obligations under FINRA rules.
    """
    return await OBBject.from_query(Query(**locals()))
