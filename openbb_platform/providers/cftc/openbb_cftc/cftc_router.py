"""Commodity Futures Trading Commission Router."""

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
from openbb_core.app.query import Query as OpenBBQuery
from openbb_core.app.router import Router

router = Router(
    prefix="",
    description="Commitment of Traders reports and DTCC swap transaction data.",
)


@router.command(
    model="CftcCotSearch",
    examples=[
        APIEx(parameters={"provider": "cftc"}),
        APIEx(parameters={"query": "gold", "provider": "cftc"}),
    ],
    widget_config={
        "name": "Commitment of Traders Search",
        "description": "Search for CFTC Commitment of Traders (COT) report series.",
        "category": "CFTC",
        "subCategory": "COT",
        "refetchInterval": False,
    },
)
async def cot_search(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Search current Commitment of Traders Reports."""
    return await OBBject.from_query(OpenBBQuery(**locals()))


@router.command(
    model="CftcCot",
    examples=[
        APIEx(parameters={"provider": "cftc"}),
        APIEx(
            description="Get the latest report for all items classified as, GOLD.",
            parameters={"code": "CFTC_088691", "limit": 1, "provider": "cftc"},
        ),
        APIEx(
            description="Get the report for futures only.",
            parameters={
                "code": "CFTC_088691",
                "futures_only": True,
                "limit": 1,
                "provider": "cftc",
            },
        ),
        APIEx(
            description="Filter the report down to a specific section.",
            parameters={
                "code": "CFTC_088691",
                "futures_only": True,
                "measure": "changes",
                "limit": 1,
                "provider": "cftc",
            },
        ),
    ],
    widget_config={
        "name": "Commitment of Traders",
        "description": "CFTC Commitment of Traders (COT) reports.",
        "category": "CFTC",
        "subCategory": "COT",
        "refetchInterval": False,
    },
)
async def cot(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get Commitment of Traders Reports."""
    return await OBBject.from_query(OpenBBQuery(**locals()))


@router.command(
    model="CftcCotIndex",
    examples=[
        APIEx(parameters={"provider": "cftc"}),
        APIEx(
            description="Score the index and bond markets against their own year.",
            parameters={"asset_class": "indices_bonds", "provider": "cftc"},
        ),
    ],
    widget_config={
        "name": "COT Positioning Index",
        "description": "Where each trader group's net position sits in its own"
        + " lookback range, 0 to 100, across the curated futures universe. A high"
        + " commercial score is their least-hedged reading, not a bullish one.",
        "category": "CFTC",
        "subCategory": "COT",
        "refetchInterval": False,
    },
)
async def cot_index(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Score COT positioning against each trader group's own lookback range."""
    return await OBBject.from_query(OpenBBQuery(**locals()))


@router.command(
    model="CftcCotMovers",
    examples=[
        APIEx(parameters={"provider": "cftc"}),
        APIEx(
            description="This week's biggest moves in index and bond futures.",
            parameters={"asset_class": "indices_bonds", "provider": "cftc"},
        ),
    ],
    widget_config={
        "name": "COT Largest Changes",
        "description": "This week's largest moves in positioning score, ranked by size,"
        + " with what each move did to that trader group's stance.",
        "category": "CFTC",
        "subCategory": "COT",
        "refetchInterval": False,
    },
)
async def cot_movers(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Rank this week's largest COT positioning score moves."""
    return await OBBject.from_query(OpenBBQuery(**locals()))


@router.command(
    model="CftcCotPositioning",
    examples=[
        APIEx(parameters={"provider": "cftc"}),
        APIEx(
            description="Weekly gold positioning, scored against its own year.",
            parameters={"code": "CFTC_088691", "provider": "cftc"},
        ),
    ],
    widget_config={
        "name": "COT Positioning History",
        "description": "One market's weekly COT history: each trader group's net"
        + " position, its share of open interest, and its 0-100 score within the"
        + " trailing window.",
        "category": "CFTC",
        "subCategory": "COT",
        "refetchInterval": False,
    },
)
async def cot_positioning(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Track one market's COT positioning week by week."""
    return await OBBject.from_query(OpenBBQuery(**locals()))


@router.command(
    model="CftcSwapTrades",
    examples=[
        APIEx(parameters={"provider": "cftc"}),
        APIEx(
            description="Get USD SOFR swap transactions reported on a given date.",
            parameters={
                "asset_class": "rates",
                "currency": "USD",
                "underlier": "SOFR",
                "action_type": "NEWT",
                "provider": "cftc",
            },
        ),
        APIEx(
            description="Get large cleared credit transactions.",
            parameters={
                "asset_class": "credits",
                "cleared": "Y",
                "min_notional": 50000000,
                "provider": "cftc",
            },
        ),
    ],
    widget_config={
        "name": "Swap Transactions",
        "description": "DTCC Public Price Dissemination swap transaction and pricing data.",
        "category": "CFTC",
        "subCategory": "Swaps",
        "refetchInterval": False,
    },
)
async def swap_trades(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get swap transaction and pricing data disseminated by DTCC."""
    return await OBBject.from_query(OpenBBQuery(**locals()))


@router.command(
    model="CftcSwapValuation",
    examples=[
        APIEx(parameters={"provider": "cftc"}),
        APIEx(
            description="Value a specific disseminated print against today's curve.",
            parameters={
                "currency": "USD",
                "dissemination_identifier": "4339565190000000401",
                "provider": "cftc",
            },
        ),
        APIEx(
            description="Value the largest CNY print off its fixed-float IRS curve.",
            parameters={"currency": "CNY", "provider": "cftc"},
        ),
    ],
    widget_config={
        "name": "Swap Valuation",
        "description": "Fixed-rate swap valuation and cash-flow schedule against the"
        + " DTCC-reported rate curve.",
        "category": "CFTC",
        "subCategory": "Swaps",
        "refetchInterval": False,
    },
)
async def swap_valuation(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Value a disseminated swap on its own printed terms against the rate curve."""
    return await OBBject.from_query(OpenBBQuery(**locals()))


@router.command(
    model="CftcHistoricalFixings",
    examples=[
        APIEx(parameters={"provider": "cftc"}),
        APIEx(
            description="A year of 3-month EURIBOR fixings.",
            parameters={"index": "EURIBOR", "provider": "cftc"},
        ),
        APIEx(
            description="SOFR over a chosen window.",
            parameters={
                "index": "SOFR",
                "start_date": "2026-01-01",
                "end_date": "2026-07-24",
                "provider": "cftc",
            },
        ),
    ],
    widget_config={
        "name": "Historical Fixings",
        "description": "Daily published fixings for a benchmark index, sourced from its"
        + " own administrator, with the day-on-day change in basis points.",
        "category": "CFTC",
        "subCategory": "Rates",
        "refetchInterval": False,
    },
)
async def historical_fixings(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Daily published fixings for a benchmark index."""
    return await OBBject.from_query(OpenBBQuery(**locals()))


@router.command(
    model="CftcSwapSummary",
    examples=[
        APIEx(parameters={"provider": "cftc"}),
        APIEx(
            description="Summarize a specific disseminated print's net economics.",
            parameters={
                "currency": "USD",
                "dissemination_identifier": "4339565190000000401",
                "provider": "cftc",
            },
        ),
    ],
    widget_config={
        "name": "Swap Summary",
        "description": "A disseminated swap's net economics right now: NPV against the"
        + " current curve, realized carry from published fixings, upfront and other"
        + " payments, and the side the trade currently favors.",
        "category": "CFTC",
        "subCategory": "Swaps",
        "refetchInterval": False,
    },
)
async def swap_summary(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Summarize a disseminated swap's net economics on the current curve."""
    return await OBBject.from_query(OpenBBQuery(**locals()))


@router.command(
    model="CftcCdsIndexTrades",
    examples=[
        APIEx(parameters={"provider": "cftc"}),
        APIEx(
            description="Get the CDX.NA.IG tape.",
            parameters={"index": "CDX.NA.IG", "provider": "cftc"},
        ),
        APIEx(
            description="Get the 5Y CDX.NA.HY prints of at least 10mm notional.",
            parameters={
                "index": "CDX.NA.HY",
                "tenor": "5Y",
                "min_notional": 10000000,
                "provider": "cftc",
            },
        ),
    ],
    widget_config={
        "name": "CDS Index Trades",
        "description": "DTCC Public Price Dissemination credit default swap index transactions.",
        "category": "CFTC",
        "subCategory": "Credit",
        "refetchInterval": False,
    },
)
async def cds_index_trades(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get credit default swap index transactions disseminated by DTCC."""
    return await OBBject.from_query(OpenBBQuery(**locals()))


@router.command(
    model="CftcOisCurve",
    examples=[
        APIEx(
            description="Get the USD SOFR curve.",
            parameters={"provider": "cftc"},
        ),
        APIEx(
            description="Get the EUR ESTR curve.",
            parameters={"currency": "EUR", "provider": "cftc"},
        ),
        APIEx(
            description="Fill in a thinly traded currency's short end, which needs a"
            + " longer window and admits single prints.",
            parameters={
                "currency": "CHF",
                "lookback_days": 30,
                "min_trades": 1,
                "provider": "cftc",
            },
        ),
        APIEx(
            description="Get the curve at every distinct tenor traded, not just benchmarks.",
            parameters={"granularity": "observed", "min_trades": 1, "provider": "cftc"},
        ),
        APIEx(
            description="Build from a single day's file instead of a search window.",
            parameters={"source": "slice", "provider": "cftc"},
        ),
    ],
    widget_config={
        "name": "Overnight Index Swap Curve",
        "data": {"chartView": {"enabled": True, "chartType": "line"}},
        "description": "Central bank overnight index swap curves built from executed transactions.",
        "category": "CFTC",
        "subCategory": "Swaps",
        "refetchInterval": False,
    },
)
async def ois_curve(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get an overnight index swap curve, built from executed swap transactions."""
    return await OBBject.from_query(OpenBBQuery(**locals()))


@router.command(
    model="CftcOisCurveHistory",
    examples=[
        APIEx(parameters={"provider": "cftc"}),
        APIEx(
            description="Track benchmark tenors over time.",
            parameters={"tenor": "2Y,5Y,10Y,30Y", "provider": "cftc"},
        ),
        APIEx(
            description="Get the history of bootstrapped SONIA zero rates, in long form.",
            parameters={
                "currency": "GBP",
                "measure": "zero_rate",
                "pivot": False,
                "provider": "cftc",
            },
        ),
    ],
    widget_config={
        "name": "Overnight Index Swap Curve History",
        "data": {"chartView": {"enabled": True, "chartType": "line"}},
        "description": "Central bank overnight index swap curves over time, by tenor.",
        "category": "CFTC",
        "subCategory": "Swaps",
        "refetchInterval": False,
    },
)
async def ois_curve_history(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get an overnight index swap curve over time, as a date-by-tenor table."""
    return await OBBject.from_query(OpenBBQuery(**locals()))


@router.command(
    model="CftcOisForwardCurve",
    examples=[
        APIEx(parameters={"provider": "cftc"}),
        APIEx(
            description="Plot the 5Y forward rate at yearly start dates.",
            parameters={
                "forward_tenor": "5Y",
                "forward_step": "1Y",
                "provider": "cftc",
            },
        ),
        APIEx(
            description="Get the next ten years of the SONIA 1Y forward.",
            parameters={
                "currency": "GBP",
                "forward_tenor": "1Y",
                "forward_step": "1Y",
                "forward_count": 10,
                "provider": "cftc",
            },
        ),
    ],
    widget_config={
        "name": "OIS Forward Rate Curve",
        "data": {"chartView": {"enabled": True, "chartType": "line"}},
        "description": "Forward par swap rate by start date, from executed transactions.",
        "category": "CFTC",
        "subCategory": "Swaps",
        "refetchInterval": False,
    },
)
async def ois_forward_curve(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the forward par swap rate curve, by forward start date."""
    return await OBBject.from_query(OpenBBQuery(**locals()))


@router.command(
    model="CftcOisPolicyPath",
    examples=[
        APIEx(parameters={"provider": "cftc"}),
        APIEx(
            description="The ECB path priced by EUR meeting-dated OIS.",
            parameters={"currency": "EUR", "provider": "cftc"},
        ),
    ],
    widget_config={
        "name": "OIS Policy Path",
        "data": {"chartView": {"enabled": True, "chartType": "line"}},
        "description": "Expected central-bank overnight-rate path, read from"
        + " forward-starting OIS reported to the DTCC.",
        "category": "CFTC",
        "subCategory": "Swaps",
        "refetchInterval": False,
    },
)
async def ois_policy_path(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the central bank's expected overnight-rate path from forward-starting OIS."""
    return await OBBject.from_query(OpenBBQuery(**locals()))


@router.command(
    model="CftcFxForwardPoints",
    examples=[
        APIEx(parameters={"provider": "cftc"}),
        APIEx(
            description="Get USDJPY forward points.",
            parameters={"pair": "USDJPY", "provider": "cftc"},
        ),
        APIEx(
            description="Include sub-institutional trades, which price away from the market.",
            parameters={"pair": "EURUSD", "min_notional": 0, "provider": "cftc"},
        ),
    ],
    widget_config={
        "name": "FX Forward Points",
        "data": {"chartView": {"enabled": True, "chartType": "line"}},
        "description": "FX forward points built from executed forwards and FX swaps.",
        "category": "CFTC",
        "subCategory": "FX",
        "refetchInterval": False,
    },
)
async def fx_forward_points(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get FX forward points, built from executed forwards and FX swaps."""
    return await OBBject.from_query(OpenBBQuery(**locals()))


@router.command(
    model="CftcFxForwardCurve",
    examples=[
        APIEx(parameters={"provider": "cftc"}),
        APIEx(
            description="Get the USDKRW forward curve, in KRW per US dollar.",
            parameters={"pair": "USDKRW", "provider": "cftc"},
        ),
    ],
    widget_config={
        "name": "FX Forward Curve",
        "data": {"chartView": {"enabled": True, "chartType": "line"}},
        "description": "Outright FX forward curve, in units of the currency per US dollar,"
        + " from executed forwards and FX swaps.",
        "category": "CFTC",
        "subCategory": "FX",
        "refetchInterval": False,
    },
)
async def fx_forward_curve(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the outright FX forward curve, in units of the currency per one US dollar."""
    return await OBBject.from_query(OpenBBQuery(**locals()))


@router.command(
    model="CftcFxImpliedVol",
    examples=[
        APIEx(parameters={"provider": "cftc"}),
        APIEx(
            description="Get the USDJPY implied-volatility smile by tenor.",
            parameters={"pair": "USDJPY", "provider": "cftc"},
        ),
    ],
    widget_config={
        "name": "FX Implied Volatility",
        "data": {"chartView": {"enabled": True, "chartType": "line"}},
        "description": "FX implied-volatility smiles by tenor from vanilla options reported to the CFTC.",
        "category": "CFTC",
        "subCategory": "FX",
        "refetchInterval": False,
    },
)
async def fx_implied_vol(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get FX implied volatility from vanilla options disseminated by DTCC."""
    return await OBBject.from_query(OpenBBQuery(**locals()))


@router.command(
    model="CftcFxOptionTrades",
    examples=[
        APIEx(parameters={"provider": "cftc"}),
        APIEx(
            description="Get the newly executed EURUSD option prints.",
            parameters={"pair": "EURUSD", "action_type": "NEWT", "provider": "cftc"},
        ),
        APIEx(
            description="Get the non-deliverable option prints (BRL, KRW, INR, ...).",
            parameters={"option_type": "Non-Deliverable", "provider": "cftc"},
        ),
        APIEx(
            description="Get the 20 largest JPY option prints of the day.",
            parameters={
                "pair": "JPY",
                "min_notional": 50000000,
                "limit": 20,
                "provider": "cftc",
            },
        ),
    ],
    widget_config={
        "name": "FX Option Trades",
        "description": "The raw FX option transactions reported to the CFTC, newest first.",
        "category": "CFTC",
        "subCategory": "FX",
        "refetchInterval": False,
    },
)
async def fx_option_trades(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the raw FX option transactions disseminated by DTCC, newest first."""
    return await OBBject.from_query(OpenBBQuery(**locals()))


@router.command(
    model="CftcFxForwardTrades",
    examples=[
        APIEx(parameters={"provider": "cftc"}),
        APIEx(
            description="Get the newly executed non-deliverable forward prints.",
            parameters={
                "product_type": "Non-Deliverable Forward",
                "action_type": "NEWT",
                "provider": "cftc",
            },
        ),
        APIEx(
            description="Get the USD-settled non-deliverable forward and swap prints.",
            parameters={"settlement_currency": "USD", "provider": "cftc"},
        ),
        APIEx(
            description="Get the 20 largest INR forward prints of the day.",
            parameters={
                "pair": "INR",
                "min_notional": 50000000,
                "limit": 20,
                "provider": "cftc",
            },
        ),
    ],
    widget_config={
        "name": "FX Forward Trades",
        "description": "The raw FX forward and swap transactions reported to the CFTC,"
        + " newest first.",
        "category": "CFTC",
        "subCategory": "FX",
        "refetchInterval": False,
    },
)
async def fx_forward_trades(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the raw FX forward and swap transactions disseminated by DTCC, newest first."""
    return await OBBject.from_query(OpenBBQuery(**locals()))


@router.command(
    methods=["GET"],
    include_in_schema=False,
    openapi_extra={"widget_config": {"exclude": True}},
    examples=[APIEx(description="Get COT contract choices.", parameters={})],
)
async def cot_choices() -> list:
    """Endpoint supplying COT contract choices to Workspace widgets."""
    from openbb_cftc.utils.helpers import get_cot_choices

    return await get_cot_choices()


@router.command(
    methods=["GET"],
    include_in_schema=False,
    openapi_extra={"widget_config": {"exclude": True}},
    examples=[APIEx(description="Get published report dates.", parameters={})],
)
async def ppd_date_choices(
    asset_class: Annotated[
        str, FastAPIQuery(description="Asset class to list report dates for.")
    ] = "rates",
) -> list:
    """Endpoint supplying PPD report dates to Workspace widgets."""
    from openbb_cftc.utils.helpers import get_ppd_date_choices

    return await get_ppd_date_choices(asset_class=asset_class)


@router.api_router.get("/apps.json", include_in_schema=False)
async def cftc_apps():
    """Serve the bundled CFTC dashboard templates."""
    import json
    from pathlib import Path

    apps_file = Path(__file__).parent / "assets" / "apps.json"
    apps = json.loads(apps_file.read_text(encoding="utf-8"))
    if isinstance(apps, dict):
        apps = [apps]

    return apps
