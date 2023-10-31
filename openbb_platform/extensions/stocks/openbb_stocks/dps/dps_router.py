from openbb_core.app.router import Router

from openbb_core.app.model.command_context import CommandContext
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.provider_interface import (
    ExtraParams,
    ProviderChoices,
    StandardParams,
)
from openbb_core.app.query import Query
from openbb_core.app.router import Router
from pydantic import BaseModel

router = Router(prefix="/dps")


@router.command(model="StockFTD")
def ftd(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Get reported Fail-to-deliver (FTD) data."""
    return OBBject(results=Query(**locals()).execute())


@router.command(model="ShortVolume")
def short_volume(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Get reported Fail-to-deliver (FTD) data."""
    return OBBject(results=Query(**locals()).execute())
