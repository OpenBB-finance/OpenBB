from openbb_core.app.model.command_context import CommandContext
from openbb_core.app.model.command_output import CommandOutput
from openbb_core.app.provider_interface import (
    ExtraParams,
    ProviderChoices,
    StandardParams,
)
from openbb_core.app.query import Query
from openbb_core.app.router import Router
from openbb_provider.abstract.data import Data

router = Router(prefix="")


# pylint: disable=unused-argument
@router.command(query="ForexPairs")
def pairs(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> CommandOutput[Data]:
    """Forex Available Pairs."""
    return CommandOutput(results=Query(**locals()).execute())


# pylint: disable=unused-argument
@router.command(query="ForexEOD")
def load(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> CommandOutput[Data]:
    """Forex Intraday Price."""
    return CommandOutput(results=Query(**locals()).execute())
