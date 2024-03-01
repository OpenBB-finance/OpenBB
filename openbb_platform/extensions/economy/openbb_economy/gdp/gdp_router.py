"""Economy GDP Router."""

from openbb_core.app.model import CommandContext, Example, OBBject
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
    api_examples=[Example(parameters={"period": "annual", "type": "real"})],
)
async def forecast(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Forecasted GDP Data."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="GdpNominal",
    api_examples=[Example(parameters={"units": "usd"})],
)
async def nominal(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Nominal GDP Data."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="GdpReal",
    api_examples=[Example(parameters={"units": "yoy"})],
)
async def real(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Real GDP Data."""
    return await OBBject.from_query(Query(**locals()))
