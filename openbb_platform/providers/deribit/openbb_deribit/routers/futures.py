"""Deribit Futures sub-router."""

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

from openbb_deribit import DERIVATIVES_INSTALLED

router = Router(prefix="/futures", description="Deribit futures data.")


@router.command(
    methods=["GET"],
    widget_config={"exclude": True},
    examples=[
        APIEx(
            description="Get the underlyings with a listed futures curve.",
            parameters={},
        )
    ],
)
async def curve_choices() -> list[dict[str, str]]:
    """``[{label, value}]`` of every underlying with a listed futures curve."""
    from openbb_deribit.utils.choices import futures_root_choices

    return await futures_root_choices()


@router.command(
    methods=["GET"],
    widget_config={"exclude": True},
    examples=[APIEx(description="Get the listed perpetuals.", parameters={})],
)
async def perpetual_choices() -> list[dict[str, str]]:
    """``[{label, value}]`` of every perpetual the exchange lists."""
    from openbb_deribit.utils.choices import perpetual_choices as choices

    return await choices()


if not DERIVATIVES_INSTALLED:

    @router.command(
        model="DeribitFuturesInstruments",
        widget_config={
            "name": "Deribit Futures Instruments",
            "description": "The contract specification of every listed future.",
            "category": "Crypto",
            "subCategory": "Futures",
            "source": ["Deribit"],
            "gridData": {"w": 40, "h": 15},
        },
        examples=[
            APIEx(
                description="Every future Deribit lists.",
                parameters={"provider": "deribit"},
            )
        ],
    )
    async def instruments(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Get the contract specification of every listed Deribit future."""
        return await OBBject.from_query(OBBQuery(**locals()))

    @router.command(
        model="DeribitFuturesCurve",
        widget_config={
            "name": "Deribit Futures Curve",
            "description": "The term structure of an underlying's dated futures,"
            + " optionally against how it stood some hours ago.",
            "category": "Crypto",
            "subCategory": "Futures",
            "source": ["Deribit"],
            "gridData": {"w": 40, "h": 15},
            "params": [{"paramName": "symbol", "value": "BTC"}],
            "data": {
                "table": {
                    "chartView": {"enabled": True, "chartType": "line"},
                }
            },
        },
        examples=[
            APIEx(
                description="The current BTC futures term structure.",
                parameters={"symbol": "BTC", "provider": "deribit"},
            ),
            APIEx(
                description="The curve against where it stood a day ago.",
                parameters={"symbol": "BTC", "hours_ago": 24, "provider": "deribit"},
            ),
        ],
    )
    async def curve(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Get the term structure of a Deribit underlying's dated futures."""
        return await OBBject.from_query(OBBQuery(**locals()))

    @router.command(
        model="DeribitFuturesHistorical",
        widget_config={
            "name": "Deribit Historical Prices",
            "description": "Candles for any listed instrument, not only futures.",
            "category": "Crypto",
            "subCategory": "Futures",
            "source": ["Deribit"],
            "gridData": {"w": 40, "h": 15},
            "params": [{"paramName": "symbol", "value": "BTC-PERPETUAL"}],
            "data": {
                "table": {
                    "chartView": {"enabled": True, "chartType": "line"},
                }
            },
        },
        examples=[
            APIEx(
                description="Daily candles for the BTC perpetual.",
                parameters={"symbol": "BTC-PERPETUAL", "provider": "deribit"},
            ),
            APIEx(
                description="Hourly candles over a named span.",
                parameters={
                    "symbol": "BTC-PERPETUAL",
                    "interval": "1h",
                    "start_date": "2026-09-01",
                    "end_date": "2026-09-15",
                    "provider": "deribit",
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
        """Get candles for any listed Deribit instrument."""
        return await OBBject.from_query(OBBQuery(**locals()))

    @router.command(
        model="DeribitFuturesInfo",
        widget_config={
            "name": "Deribit Futures Info",
            "description": "The live quote and session statistics of a perpetual or"
            + " dated future.",
            "category": "Crypto",
            "subCategory": "Futures",
            "source": ["Deribit"],
            "gridData": {"w": 40, "h": 8},
            "params": [{"paramName": "symbol", "value": "BTC-PERPETUAL"}],
        },
        examples=[
            APIEx(
                description="The live quote of the BTC perpetual.",
                parameters={"symbol": "BTC-PERPETUAL", "provider": "deribit"},
            )
        ],
    )
    async def info(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Get the live quote and session statistics of a Deribit future."""
        return await OBBject.from_query(OBBQuery(**locals()))
