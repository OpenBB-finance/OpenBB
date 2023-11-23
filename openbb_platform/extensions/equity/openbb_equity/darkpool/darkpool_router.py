"""Dark Pool Router."""
from openbb_core.app.model.command_context import CommandContext
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.provider_interface import (
    ExtraParams,
    ProviderChoices,
    StandardParams,
)
from openbb_core.app.query import Query
from openbb_core.app.router import Router
from pydantic import BaseModel

router = Router(prefix="/darkpool")

# pylint: disable=unused-argument


@router.command(model="OTCAggregate")
async def otc(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Weekly aggregate trade data for Over The Counter deals.

    ATS and non-ATS trading data for each ATS/firm
    with trade reporting obligations under FINRA rules.
    """
    return await OBBject.from_query(Query(**locals()))
