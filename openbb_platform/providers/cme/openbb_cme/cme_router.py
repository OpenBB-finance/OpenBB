"""CME provider router."""

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

from openbb_cme import DERIVATIVES_INSTALLED

router = Router(prefix="", description="CME Group provider router.")


if not DERIVATIVES_INSTALLED:

    @router.command(
        model="CmeFuturesHistorical",
        examples=[
            APIEx(
                parameters={
                    "symbol": "ES",
                    "provider": "cme",
                    "start_date": "2025-06-01",
                    "end_date": "2025-06-30",
                }
            ),
            APIEx(
                description="Filter the history to a specific contract month.",
                parameters={
                    "symbol": "NQ",
                    "provider": "cme",
                    "expiration": "2025-09",
                },
            ),
        ],
    )
    async def historical(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Get CME futures settlement history."""
        return await OBBject.from_query(Query(**locals()))

    @router.command(
        model="CmeFuturesCurve",
        examples=[
            APIEx(parameters={"symbol": "ES", "provider": "cme"}),
            APIEx(
                parameters={
                    "symbol": "NQ",
                    "provider": "cme",
                    "date": "2025-06-25",
                }
            ),
        ],
    )
    async def curve(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Get a current or historical CME futures term structure."""
        return await OBBject.from_query(Query(**locals()))

    @router.command(
        model="CmeFuturesInstruments",
        examples=[
            APIEx(parameters={"symbol": "ES", "provider": "cme"}),
            APIEx(parameters={"symbol": "ES,NQ", "provider": "cme"}),
        ],
    )
    async def instruments(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Get reference data for listed CME futures instruments."""
        return await OBBject.from_query(Query(**locals()))

    @router.command(
        model="CmeFuturesInfo",
        examples=[
            APIEx(parameters={"symbol": "ES", "provider": "cme"}),
            APIEx(parameters={"symbol": "ES,NQ,MES", "provider": "cme"}),
        ],
    )
    async def info(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Get CME futures specifications and latest settlements."""
        return await OBBject.from_query(Query(**locals()))
