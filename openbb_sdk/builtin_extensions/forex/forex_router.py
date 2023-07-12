from openbb_sdk_core.app.model.command_context import CommandContext
from openbb_sdk_core.app.model.command_output import CommandOutput
from openbb_sdk_core.app.model.results.empty import Empty
from openbb_sdk_core.app.provider_interface import (
    ExtraParams,
    ProviderChoices,
    StandardParams,
)
from openbb_sdk_core.app.query import Query
from openbb_sdk_core.app.router import Router
from pydantic import BaseModel

router = Router(prefix="")


@router.command(query="ForexPairs")
def pairs(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> CommandOutput[BaseModel]:
    """Forex Available Pairs."""
    return CommandOutput(results=Query(**locals()).execute())


@router.command(query="ForexEOD")
def load(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> CommandOutput[BaseModel]:
    """Forex Intraday Price."""
    return CommandOutput(results=Query(**locals()).execute())
