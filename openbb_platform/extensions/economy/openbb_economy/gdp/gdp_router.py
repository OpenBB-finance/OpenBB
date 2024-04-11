"""Economy GDP Router."""

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

router = Router(prefix="/gdp")

# pylint: disable=unused-argument


@router.command(
    model="GdpForecast",
    examples=[
        APIEx(parameters={"provider": "oecd"}),
        APIEx(parameters={"period": "annual", "type": "real", "provider": "oecd"}),
    ],
)
async def forecast(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get Forecasted GDP Data."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="GdpNominal",
    examples=[
        APIEx(parameters={"provider": "oecd"}),
        APIEx(parameters={"units": "usd", "provider": "oecd"}),
    ],
)
async def nominal(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get Nominal GDP Data."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="GdpReal",
    examples=[
        APIEx(parameters={"provider": "oecd"}),
        APIEx(parameters={"units": "yoy", "provider": "oecd"}),
    ],
)
async def real(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get Real GDP Data."""
    return await OBBject.from_query(Query(**locals()))
