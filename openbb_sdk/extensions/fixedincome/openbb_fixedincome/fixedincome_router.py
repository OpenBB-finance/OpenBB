# pylint: disable=W0613:unused-argument

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


@router.command(model="TreasuryRates")
def treasury(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> Obbject[BaseModel]:
    """Get treasury rates."""
    return Obbject(results=Query(**locals()).execute())


@router.command
def ycrv() -> Obbject[Empty]:  # type: ignore
    """Yield curve."""
    return Obbject(results=Empty())
