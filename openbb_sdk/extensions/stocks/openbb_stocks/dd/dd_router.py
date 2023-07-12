# pylint: disable=W0613:unused-argument
"""Due Diligence Router."""

from openbb_core.app.model.command_context import CommandContext
from openbb_core.app.model.command_output import CommandOutput
from openbb_core.app.provider_interface import (
    ExtraParams,
    ProviderChoices,
    StandardParams,
)
from openbb_core.app.query import Query
from openbb_core.app.router import Router
from pydantic import BaseModel

router = Router(prefix="/dd")


@router.command(query="SECFilings")
def sec(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> CommandOutput[BaseModel]:
    """SEC Filings."""
    return CommandOutput(results=Query(**locals()).execute())
