# pylint: disable=import-outside-toplevel, W0613:unused-argument
"""News Router."""

from openbb_core.app.model.command_context import CommandContext
from openbb_core.app.model.obbject import Obbject
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


@router.command(model="GlobalNews")
def globalnews(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> Obbject[BaseModel]:
    """Global News."""
    return Obbject(results=Query(**locals()).execute())


@router.command
def sectornews() -> Obbject[Empty]:  # type: ignore
    """Sector news."""
    return Obbject(results=Empty())
