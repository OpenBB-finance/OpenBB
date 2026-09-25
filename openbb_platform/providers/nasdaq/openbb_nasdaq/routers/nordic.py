"""Nasdaq Nordic sub-router."""

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

router = Router(prefix="/nordic", description="Nasdaq Nordic and Baltic market data.")


@router.command(
    methods=["GET"],
    widget_config={"exclude": True},
    examples=[
        APIEx(description="Get the Nasdaq Nordic instrument directory.", parameters={})
    ],
)
async def symbol_choices() -> list[dict]:
    """``[{label, value}]`` of every instrument Nasdaq Nordic lists."""
    from openbb_nasdaq.utils.nordic import get_nordic_symbol_choices

    return await get_nordic_symbol_choices()


@router.command(
    model="NasdaqNordicScreener",
    examples=[
        APIEx(
            description="Every share listed on the Nordic main market.",
            parameters={"provider": "nasdaq"},
        ),
        APIEx(
            description="First North growth market shares.",
            parameters={"market": "first_north", "provider": "nasdaq"},
        ),
        APIEx(
            description="Swedish corporate bonds.",
            parameters={
                "asset_class": "corporate_bonds",
                "market": "sweden",
                "provider": "nasdaq",
            },
        ),
    ],
)
async def screener(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Screen shares, funds, indexes, bonds, and derivatives across Nasdaq Nordic."""
    return await OBBject.from_query(OBBQuery(**locals()))


@router.command(
    model="NasdaqNordicNews",
    examples=[
        APIEx(
            description="The latest exchange notices across every Nordic market.",
            parameters={"provider": "nasdaq"},
        ),
        APIEx(
            description="Stockholm notices only.",
            parameters={"market": "stockholm", "provider": "nasdaq"},
        ),
    ],
)
async def news(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Company announcements and exchange notices from the Nasdaq Nordic markets."""
    return await OBBject.from_query(OBBQuery(**locals()))


@router.command(
    model="NasdaqNordicInfo",
    examples=[
        APIEx(
            description="Bond metadata - coupon, listing day, and repayment terms.",
            parameters={"symbol": "CATME_HO1", "provider": "nasdaq"},
        ),
        APIEx(
            description="Share metadata - shares outstanding, ICB code, and segment.",
            parameters={"symbol": "ATCO A", "provider": "nasdaq"},
        ),
    ],
)
async def info(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the reference and trading metadata for a Nasdaq Nordic instrument."""
    return await OBBject.from_query(OBBQuery(**locals()))


@router.command(
    model="NasdaqNordicFundamentals",
    examples=[
        APIEx(
            description="Morningstar statements, ratios, and growth rates.",
            parameters={"symbol": "AAK", "provider": "nasdaq"},
        )
    ],
)
async def fundamentals(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the Morningstar fundamentals published for a Nasdaq Nordic listing."""
    return await OBBject.from_query(OBBQuery(**locals()))


@router.command(
    model="NasdaqNordicDividends",
    examples=[
        APIEx(
            description="Declared distributions, with ex and payment dates.",
            parameters={"symbol": "AAK", "provider": "nasdaq"},
        )
    ],
)
async def dividends(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the declared distributions for a Nasdaq Nordic listing."""
    return await OBBject.from_query(OBBQuery(**locals()))


@router.command(
    model="NasdaqNordicHistorical",
    examples=[
        APIEx(
            description="Daily closes, volume, duration, and yield.",
            parameters={"symbol": "CATME_HO1", "provider": "nasdaq"},
        )
    ],
)
async def historical(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the daily price history for a Nasdaq Nordic instrument."""
    return await OBBject.from_query(OBBQuery(**locals()))


@router.command(
    model="NasdaqNordicHistoricalTrades",
    examples=[
        APIEx(
            description="Every reported trade, with the buying and selling members.",
            parameters={"symbol": "CATME_HO1", "provider": "nasdaq"},
        )
    ],
)
async def historical_trades(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the trade-by-trade history for a Nasdaq Nordic instrument."""
    return await OBBject.from_query(OBBQuery(**locals()))


@router.command(
    model="NasdaqNordicMovers",
    examples=[
        APIEx(
            description="The most traded Nordic shares.",
            parameters={"provider": "nasdaq"},
        ),
        APIEx(
            description="The most traded Nordic options and futures.",
            parameters={"asset_group": "options_futures", "provider": "nasdaq"},
        ),
    ],
)
async def movers(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the most traded instruments in a Nasdaq Nordic asset group."""
    return await OBBject.from_query(OBBQuery(**locals()))


@router.command(
    methods=["GET"],
    widget_config={
        "name": "Nasdaq Nordic Derivatives Volume",
        "category": "Derivatives",
        "subCategory": "Nordic",
    },
    examples=[
        APIEx(description="Session volume by derivatives market.", parameters={})
    ],
)
async def derivatives_volume() -> list[dict]:
    """Get the session volume for each Nasdaq Nordic equity derivatives market."""
    from openbb_nasdaq.utils.helpers import get_nasdaq_data, rows_from_table, to_number

    data = await get_nasdaq_data(
        "nordic/markets/volume-summary?assetGroup=OPTIONS_FUTURES&lang=en"
    )
    rows = rows_from_table((data or {}).get("volumeSummary"))

    return [
        {"market": row.get("name"), "volume": to_number(row.get("volume"))}
        for row in rows
    ]


@router.command(
    model="NasdaqNordicKnockedOut",
    examples=[
        APIEx(
            description="Leverage instruments whose barrier has been breached.",
            parameters={"provider": "nasdaq"},
        )
    ],
)
async def knocked_out(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the knocked-out leverage instruments, in buyback or halted."""
    return await OBBject.from_query(OBBQuery(**locals()))


@router.command(
    model="NasdaqNordicBondYields",
    examples=[
        APIEx(
            description="Average Danish bond yields by maturity bucket.",
            parameters={"provider": "nasdaq"},
        )
    ],
)
async def bond_yields(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the average bond yield by issuer segment and residual maturity."""
    return await OBBject.from_query(OBBQuery(**locals()))


@router.command(
    model="NasdaqNordicIndexFactors",
    examples=[
        APIEx(
            description="Inflation index factors for index-linked bonds.",
            parameters={"provider": "nasdaq"},
        )
    ],
)
async def index_factors(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the index factors applied to Danish index-linked mortgage bonds."""
    return await OBBject.from_query(OBBQuery(**locals()))


@router.command(
    model="NasdaqNordicMortgageRates",
    examples=[
        APIEx(
            description="Listed mortgage rates by lender and term.",
            parameters={"provider": "nasdaq"},
        )
    ],
)
async def mortgage_rates(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the mortgage rates each Nordic lender lists, by fixed-rate term."""
    return await OBBject.from_query(OBBQuery(**locals()))


@router.command(
    model="NasdaqNordicTradingHours",
    examples=[
        APIEx(
            description="Session hours for every Nordic market.",
            parameters={"provider": "nasdaq"},
        )
    ],
)
async def trading_hours(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the session hours for each Nasdaq Nordic market and segment."""
    return await OBBject.from_query(OBBQuery(**locals()))


@router.command(
    model="NasdaqNordicHolidays",
    examples=[
        APIEx(
            description="The exchange holiday calendar.",
            parameters={"year": 2026, "provider": "nasdaq"},
        )
    ],
)
async def holidays(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the dates each Nasdaq Nordic market is closed."""
    return await OBBject.from_query(OBBQuery(**locals()))
