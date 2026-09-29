"""Nasdaq Index sub-router."""

from openbb_core.app.model.command_context import CommandContext
from openbb_core.app.model.example import APIEx
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.provider_interface import (
    ExtraParams,
    ProviderChoices,
    StandardParams,
)
from openbb_core.app.query import Query as OBBQuery
from openbb_core.app.router import Router

from openbb_nasdaq import INDEX_INSTALLED
from openbb_nasdaq.utils.constants import GHOST_INDEX_SYMBOL_PARAM

router = Router(prefix="/index", description="Nasdaq index data.")


@router.command(
    methods=["GET"],
    widget_config={"exclude": True},
    examples=[
        APIEx(description="Get the Nasdaq-calculated index directory.", parameters={})
    ],
)
async def symbol_choices() -> list[dict]:
    """``[{label, value}]`` of every Nasdaq-calculated index."""
    from openbb_nasdaq.utils.helpers import get_index_symbol_choices

    return await get_index_symbol_choices()


if not INDEX_INSTALLED:

    @router.command(
        model="NasdaqIndexHistorical",
        examples=[
            APIEx(
                description="Daily index levels.",
                parameters={"symbol": "COMP", "provider": "nasdaq"},
            )
        ],
    )
    async def historical(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Daily OHLCV history for Nasdaq-calculated indexes."""
        return await OBBject.from_query(OBBQuery(**locals()))

    @router.command(
        model="NasdaqIndexSearch",
        examples=[
            APIEx(
                description="Screen the index universe.",
                parameters={"index_type": "us", "provider": "nasdaq"},
            )
        ],
    )
    async def search(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Screen indexes by domicile."""
        return await OBBject.from_query(OBBQuery(**locals()))

    @router.command(
        model="NasdaqIndexSnapshots",
        widget_config={"params": [GHOST_INDEX_SYMBOL_PARAM]},
        examples=[
            APIEx(
                description="The headline US indexes.",
                parameters={"provider": "nasdaq"},
            ),
            APIEx(
                description="The Nordic headline indexes.",
                parameters={"region": "nordic", "provider": "nasdaq"},
            ),
        ],
    )
    async def snapshots(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Get current levels, session ranges, and changes for a set of indexes."""
        return await OBBject.from_query(OBBQuery(**locals()))
