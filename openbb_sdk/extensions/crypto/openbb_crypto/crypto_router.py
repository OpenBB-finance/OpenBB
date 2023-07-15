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
@router.command(model="CryptoEOD")
def load(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> CommandOutput[Data]:
    """Crypto Intraday Price."""
    return CommandOutput(results=Query(**locals()).execute())
