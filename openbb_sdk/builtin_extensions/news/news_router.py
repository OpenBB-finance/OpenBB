# pylint: disable=import-outside-toplevel, W0613:unused-argument
"""News Router."""
from typing import Optional

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


@router.command(query="GlobalNews")
def globalnews(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: Optional[ExtraParams] = None,
) -> CommandOutput[BaseModel]:
    """Global News."""
    return CommandOutput(
        results=Query(**locals()).execute(), provider=provider_choices.provider
    )


@router.command
def sectornews() -> CommandOutput[Empty]:  # type: ignore
    """Sector news."""
    return CommandOutput(results=Empty())
