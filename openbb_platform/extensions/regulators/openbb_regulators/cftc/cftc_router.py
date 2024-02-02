# pylint: disable=W0613:unused-argument
"""Commodity Futures Trading Commission (CFTC) Router."""

from openbb_core.app.model.command_context import CommandContext
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.provider_interface import (
    ExtraParams,
    ProviderChoices,
    StandardParams,
)
from openbb_core.app.query import Query
from openbb_core.app.router import Router

router = Router(prefix="/cftc")


@router.command(model="COTSearch")
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


@router.command(model="COT")
async def cot(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Commitment of Traders Reports. Lookup Commitment of Traders Reports by series ID."""
    return await OBBject.from_query(Query(**locals()))
