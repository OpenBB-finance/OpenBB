"""Deribit Reference sub-router."""

from typing import Annotated

from fastapi import Query as FastAPIQuery
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

router = Router(prefix="/reference", description="Deribit exchange reference data.")


@router.command(
    model="DeribitCurrencies",
    widget_config={
        "name": "Deribit Currencies",
        "description": "Every currency the exchange lists, with its yield and"
        + " withdrawal terms.",
        "category": "Crypto",
        "subCategory": "Reference",
        "source": ["Deribit"],
        "gridData": {"w": 40, "h": 12},
    },
    examples=[
        APIEx(
            description="List every currency Deribit lists.",
            parameters={"provider": "deribit"},
        )
    ],
)
async def currencies(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get every currency Deribit lists, with its yield and withdrawal terms."""
    return await OBBject.from_query(OBBQuery(**locals()))


@router.command(
    model="DeribitInstruments",
    widget_config={
        "name": "Deribit Instruments",
        "description": "The full contract specification of every listed instrument.",
        "category": "Crypto",
        "subCategory": "Reference",
        "source": ["Deribit"],
        "gridData": {"w": 40, "h": 15},
    },
    examples=[
        APIEx(
            description="Every instrument the exchange lists.",
            parameters={"provider": "deribit"},
        ),
        APIEx(
            description="Only the options settling in USDC.",
            parameters={"currency": "USDC", "kind": "option", "provider": "deribit"},
        ),
        APIEx(
            description="The specification of one named instrument.",
            parameters={"symbol": "BTC-PERPETUAL", "provider": "deribit"},
        ),
    ],
)
async def instruments(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the full contract specification of every listed Deribit instrument."""
    return await OBBject.from_query(OBBQuery(**locals()))


@router.command(
    model="DeribitExpirations",
    widget_config={
        "name": "Deribit Expirations",
        "description": "The expirations listed on each currency.",
        "category": "Crypto",
        "subCategory": "Reference",
        "source": ["Deribit"],
        "gridData": {"w": 20, "h": 12},
    },
    examples=[
        APIEx(
            description="Every expiration listed, kept apart by currency.",
            parameters={"provider": "deribit"},
        ),
        APIEx(
            description="The option expirations listed on BTC.",
            parameters={"currency": "BTC", "kind": "option", "provider": "deribit"},
        ),
    ],
)
async def expirations(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the expirations Deribit lists on each currency."""
    return await OBBject.from_query(OBBQuery(**locals()))


@router.command(
    model="DeribitCombos",
    widget_config={
        "name": "Deribit Combos",
        "description": "The listed multi-leg structures, one row per leg.",
        "category": "Crypto",
        "subCategory": "Reference",
        "source": ["Deribit"],
        "gridData": {"w": 30, "h": 12},
    },
    examples=[
        APIEx(
            description="Every combo listed on BTC.",
            parameters={"currency": "BTC", "provider": "deribit"},
        ),
        APIEx(
            description="The legs of one named combo.",
            parameters={
                "combo_id": "BTC-STRG-30OCT26-66000_90000",
                "provider": "deribit",
            },
        ),
    ],
)
async def combos(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the multi-leg structures Deribit lists, one row per leg."""
    return await OBBject.from_query(OBBQuery(**locals()))


@router.command(
    model="DeribitAnnouncements",
    widget_config={
        "name": "Deribit Announcements",
        "description": "What the exchange has announced.",
        "category": "Crypto",
        "subCategory": "Reference",
        "source": ["Deribit"],
        "gridData": {"w": 40, "h": 12},
    },
    examples=[
        APIEx(
            description="The most recent exchange announcements.",
            parameters={"provider": "deribit"},
        )
    ],
)
async def announcements(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get what Deribit has announced."""
    return await OBBject.from_query(OBBQuery(**locals()))


@router.command(
    methods=["GET"],
    widget_config={"exclude": True},
    examples=[
        APIEx(
            description="Read the contract size of one instrument.",
            parameters={"symbol": "BTC-PERPETUAL"},
        )
    ],
)
async def contract_size(
    symbol: Annotated[
        str, FastAPIQuery(description="The instrument name.")
    ] = "BTC-PERPETUAL",
) -> float | None:
    """Get the size of one contract of an instrument."""
    from openbb_deribit.utils.client import request

    result = await request("get_contract_size", {"instrument_name": symbol})

    return (result or {}).get("contract_size")


@router.command(
    methods=["GET"],
    widget_config={"exclude": True},
    examples=[APIEx(description="Read the exchange's platform status.", parameters={})],
)
async def status() -> dict:
    """Get whether the exchange has locked the platform."""
    from openbb_deribit.utils.client import request

    return await request("status", use_cache=False)


@router.command(
    methods=["GET"],
    widget_config={"exclude": True},
    examples=[APIEx(description="Read the exchange's server time.", parameters={})],
)
async def server_time() -> int:
    """Get the exchange's server time, in milliseconds since the epoch."""
    from openbb_deribit.utils.client import request

    return await request("get_time", use_cache=False)


@router.command(
    methods=["GET"],
    widget_config={"exclude": True},
    examples=[APIEx(description="Get currency choices.", parameters={})],
)
async def currency_choices() -> list[dict[str, str]]:
    """``[{label, value}]`` of every currency the exchange lists."""
    from openbb_deribit.utils.choices import currency_choices as choices

    return await choices()


@router.command(
    methods=["GET"],
    widget_config={"exclude": True},
    examples=[
        APIEx(description="Get the names of every published index.", parameters={})
    ],
)
async def index_choices(
    supported: Annotated[
        bool,
        FastAPIQuery(
            description="When True, returns only the indexes instruments settle"
            + " against, rather than every published index."
        ),
    ] = False,
    kind: Annotated[
        str,
        FastAPIQuery(
            description="Narrow the supported names to spot or derivative indexes."
        ),
    ] = "all",
) -> list[dict[str, str]]:
    """``[{label, value}]`` of every index the exchange publishes."""
    from openbb_deribit.utils.choices import (
        _choices,
        index_choices as choices,
    )
    from openbb_deribit.utils.client import request

    if not supported:
        return await choices()

    names = await request("get_supported_index_names", {"type": kind})

    return _choices(sorted(str(name) for name in names))


@router.command(
    methods=["GET"],
    widget_config={"exclude": True},
    examples=[
        APIEx(
            description="Get instrument choices for one kind.",
            parameters={"kind": "future"},
        )
    ],
)
async def instrument_choices(
    kind: Annotated[
        str | None,
        FastAPIQuery(description="The kind of instrument. Default is all of them."),
    ] = None,
    currency: Annotated[
        str, FastAPIQuery(description="The settlement currency of the instruments.")
    ] = "any",
    expired: Annotated[
        bool, FastAPIQuery(description="When True, returns expired instruments.")
    ] = False,
) -> list[dict[str, str]]:
    """``[{label, value}]`` of every instrument the exchange lists."""
    from openbb_deribit.utils.choices import instrument_choices as choices

    return await choices(kind, currency, expired)


@router.command(
    methods=["GET"],
    widget_config={"exclude": True},
    examples=[
        APIEx(
            description="Get the combo identifiers listed on one currency.",
            parameters={"currency": "BTC"},
        )
    ],
)
async def combo_choices(
    currency: Annotated[
        str, FastAPIQuery(description="The currency the combos settle in.")
    ] = "BTC",
    state: Annotated[
        str | None,
        FastAPIQuery(description="Narrow to active or inactive combos."),
    ] = None,
) -> list[dict[str, str]]:
    """``[{label, value}]`` of every combo identifier the exchange lists."""
    from openbb_deribit.utils.choices import combo_choices as choices

    return await choices(currency, state)
