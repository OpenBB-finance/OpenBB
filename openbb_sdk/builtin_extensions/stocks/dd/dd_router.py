# pylint: disable=W0613:unused-argument
"""Due Diligence Router."""

from openbb_sdk_core.app.model.command_context import CommandContext
from openbb_sdk_core.app.model.command_output import CommandOutput
from openbb_sdk_core.app.provider_interface import ProviderChoices, StandardParams
from openbb_sdk_core.app.query import Query
from openbb_sdk_core.app.router import Router
from pydantic import BaseModel

router = Router(prefix="/dd")


@router.command(query="SECFilings")
def sec(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
) -> CommandOutput[BaseModel]:
    """SEC Filings."""
    return CommandOutput(
        results=Query(**locals()).execute(), provider=provider.provider
    )
