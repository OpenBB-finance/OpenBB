# pylint: disable=W0613:unused-argument

from openbb_core.app.model.command_context import CommandContext
from openbb_core.app.model.obbject import OBBject
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
) -> OBBject[BaseModel]:
    """Get treasury rates."""
    return OBBject(results=Query(**locals()).execute())


@router.command
def ycrv() -> OBBject[Empty]:  # type: ignore
    """Yield curve."""
    return OBBject(results=Empty())
