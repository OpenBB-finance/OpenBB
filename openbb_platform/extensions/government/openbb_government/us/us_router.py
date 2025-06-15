"""Government US Router."""

from openbb_core.app.model.command_context import CommandContext
from openbb_core.app.model.example import APIEx
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.provider_interface import (
    ExtraParams,
    ProviderChoices,
    StandardParams,
)
from openbb_core.app.query import Query
from openbb_core.app.router import Router

router = Router(prefix="/us")

# pylint: disable=unused-argument


@router.command(
    model="CongressBills",
    examples=[
        APIEx(parameters={"provider": "congress_gov"}),
        APIEx(
            parameters={
                "start_date": "2025-01-01",
                "end_date": "2025-01-31",
                "provider": "congress_gov",
            }
        ),
    ],
)
async def congress_bills(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get Congress Bills Data."""
    return await OBBject.from_query(Query(**locals()))
