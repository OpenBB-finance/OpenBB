# pylint: disable=W0613:unused-argument
"""Crypto Volumes Router."""

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

router = Router(prefix="/volumes")


# pylint: disable=unused-argument,line-too-long
@router.command(
    model="VolumesOverview",
    examples=[
        APIEx(parameters={"provider": "defillama"}),
        APIEx(parameters={"provider": "defillama", "all": True}),
        APIEx(parameters={"provider": "defillama", "is_options": True}),
        APIEx(parameters={"provider": "defillama", "chain": "ethereum"}),
        APIEx(
            parameters={"provider": "defillama", "chain": "solana", "is_options": True}
        ),
        APIEx(
            parameters={
                "provider": "defillama",
                "chain": "solana",
                "is_options": True,
                "volume_type": "notional",
            }
        ),
    ],
)
async def overview(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the the latest overview of dexs or option dexs."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="VolumesSummary",
    examples=[
        APIEx(parameters={"provider": "defillama", "protocol": "litecoin"}),
        APIEx(
            parameters={
                "provider": "defillama",
                "protocol": "litecoin",
                "is_options": True,
            }
        ),
        APIEx(
            parameters={
                "provider": "defillama",
                "protocol": "litecoin",
                "volume_type": "notional",
            }
        ),
    ],
)
async def summary(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the the latest overview of dexs or option dexs."""
    return await OBBject.from_query(Query(**locals()))
