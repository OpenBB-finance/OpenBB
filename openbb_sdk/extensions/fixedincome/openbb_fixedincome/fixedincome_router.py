# pylint: disable=W0613:unused-argument

from openbb_core.app.model.command_context import CommandContext
from openbb_core.app.model.command_output import CommandOutput
from openbb_core.app.model.results.empty import Empty
from openbb_core.app.provider_interface import (
    ExtraParams,
    ProviderChoices,
    StandardParams,
)
from openbb_core.app.query import Query
from openbb_core.app.router import Router
from pydantic import BaseModel

router = Router(prefix="")


@router.command(model="TreasuryRates")
def treasury(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> CommandOutput[BaseModel]:
    """Get treasury rates."""
    return CommandOutput(results=Query(**locals()).execute())


@router.command
def ycrv() -> CommandOutput[Empty]:  # type: ignore
    """Yield curve."""
    return CommandOutput(results=Empty())
