# pylint: disable=W0613:unused-argument
"""Commodity Futures Trading Commission (CFTC) Router."""

from openbb_core.app.model.command_context import CommandContext
from openbb_core.app.model.example import Example
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.provider_interface import (
    ExtraParams,
    ProviderChoices,
    StandardParams,
)
from openbb_core.app.query import Query
from openbb_core.app.router import Router

router = Router(prefix="/cftc")


@router.command(
    model="COTSearch",
    api_examples=[Example(parameters={"query": "gold"})],
)
async def cot_search(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Curated Commitment of Traders Reports.

    Search a list of curated Commitment of Traders Reports series information.
    """
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="COT",
    api_examples=[
        Example(
            description="Get the Commitment of Traders Report for Gold.",
            parameters={"series_id": "GC=F"},
        ),
        Example(
            description="Enter the report ID by the Nasdaq Data Link Code.",
            parameters={"series_id": "088691"},
        ),
        Example(
            description="Get the report for futures only.",
            parameters={"series_id": "088691", "data_type": "F"},
        ),
    ],
)
async def cot(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Commitment of Traders Reports."""
    return await OBBject.from_query(Query(**locals()))
