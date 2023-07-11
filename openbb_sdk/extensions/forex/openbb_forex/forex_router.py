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

router = Router(prefix="")


# pylint: disable=unused-argument
@router.command(query="ForexEOD")
def load(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> CommandOutput[Empty]:  # type: ignore
    """Forex Intraday Price."""
    return CommandOutput(results=Query(**locals()).execute())
