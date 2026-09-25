"""FINRA Equity sub-router."""

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

from openbb_finra import EQUITY_INSTALLED

router = Router(prefix="/equity", description="FINRA equity data.")
darkpool_router = Router(prefix="/darkpool", description="FINRA OTC and ATS volume.")
shorts_router = Router(prefix="/shorts", description="FINRA short interest.")


@router.command(
    model="FinraEquityList",
    widget_config={
        "name": "FINRA Security List",
        "description": "Every FINRA-traded stock, ETF, and closed-end fund, by type.",
        "category": "Equity",
        "subCategory": "Reference",
        "source": ["FINRA"],
    },
    examples=[
        APIEx(
            description="Every traded security, with its type.",
            parameters={"provider": "finra"},
        ),
        APIEx(
            description="Every traded ETF.",
            parameters={"security_type": "etf", "provider": "finra"},
        ),
    ],
)
async def securities(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """List every FINRA-traded security by type - stocks, ETFs, and closed-end funds."""
    return await OBBject.from_query(OBBQuery(**locals()))


if not EQUITY_INSTALLED:

    @router.command(
        model="FinraEquitySearch",
        widget_config={
            "name": "FINRA Security Search",
            "description": "Search stocks and funds by symbol, name, or ISIN.",
            "category": "Equity",
            "subCategory": "Search",
            "source": ["FINRA"],
        },
        examples=[
            APIEx(
                description="Search securities by symbol, name, or ISIN.",
                parameters={"query": "apple", "provider": "finra"},
            ),
            APIEx(
                description="Search only ETFs.",
                parameters={
                    "query": "SPY",
                    "security_type": "etf",
                    "provider": "finra",
                },
            ),
        ],
    )
    async def search(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Search stocks and funds in the FINRA Market Data Center."""
        return await OBBject.from_query(OBBQuery(**locals()))

    @router.command(
        model="FinraEquityInfo",
        widget_config={
            "name": "FINRA Security Profile",
            "description": "Identifiers, classification, prices, dividends, and ratios.",
            "category": "Equity",
            "subCategory": "Profile",
            "source": ["FINRA"],
        },
        examples=[
            APIEx(
                description="The reference profile of a stock.",
                parameters={"symbol": "AAPL", "provider": "finra"},
            ),
            APIEx(
                description="Profiles for several securities at once.",
                parameters={"symbol": "AAPL,SPY,VFIAX", "provider": "finra"},
            ),
        ],
    )
    async def profile(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Get identifiers, classification, prices, dividends, and ratios for securities."""
        return await OBBject.from_query(OBBQuery(**locals()))

    @darkpool_router.command(
        model="FinraOTCAggregate",
        widget_config={
            "name": "FINRA OTC and ATS Volume",
            "description": "Weekly OTC and ATS share and trade volume.",
            "category": "Equity",
            "subCategory": "Dark Pools",
            "source": ["FINRA"],
        },
        examples=[
            APIEx(
                description="The weekly ATS volume of a symbol.",
                parameters={"symbol": "AAPL", "provider": "finra"},
            ),
            APIEx(
                description="The latest week of non-ATS volume for every Tier 2 stock.",
                parameters={"tier": "T2", "is_ats": False, "provider": "finra"},
            ),
        ],
    )
    async def otc(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Get the weekly OTC and ATS trading volume reported to FINRA."""
        return await OBBject.from_query(OBBQuery(**locals()))

    @shorts_router.command(
        model="FinraEquityShortInterest",
        widget_config={
            "name": "FINRA Short Interest",
            "description": "Bi-monthly consolidated short interest and days to cover.",
            "category": "Equity",
            "subCategory": "Shorts",
            "source": ["FINRA"],
        },
        examples=[
            APIEx(
                description="The bi-monthly short interest of a symbol.",
                parameters={"symbol": "AAPL", "provider": "finra"},
            )
        ],
    )
    async def short_interest(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Get the bi-monthly consolidated short interest and days to cover."""
        return await OBBject.from_query(OBBQuery(**locals()))

    router.include_router(darkpool_router)
    router.include_router(shorts_router)
