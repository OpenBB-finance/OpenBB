# pylint: disable=W0613:unused-argument

from openbb_sdk_core.app.model.command_context import CommandContext
from openbb_sdk_core.app.model.command_output import CommandOutput
from openbb_sdk_core.app.model.results.empty import Empty
from openbb_sdk_core.app.provider_interface import ProviderChoices, StandardParams
from openbb_sdk_core.app.query import Query
from openbb_sdk_core.app.router import Router
from pydantic import BaseModel

router = Router(prefix="")


@router.command(query="TreasuryRates")
def treasury(
    cc: CommandContext,
    provider: ProviderChoices,
    standard_params: StandardParams,
) -> CommandOutput[BaseModel]:
    """Get treasury rates."""
    return CommandOutput(results=Query(**locals()).execute())


@router.command
def ycrv() -> CommandOutput[Empty]:  # type: ignore
    """Yield curve."""
    return CommandOutput(results=Empty())
