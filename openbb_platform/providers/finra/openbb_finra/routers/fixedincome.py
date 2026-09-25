"""FINRA Fixed Income sub-router."""

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

from openbb_finra import FIXEDINCOME_INSTALLED

router = Router(prefix="/fixedincome", description="FINRA TRACE bond data.")


@router.command(
    model="FinraBondHistorical",
    widget_config={
        "name": "FINRA TRACE Bond History",
        "description": "End-of-day TRACE prices and yields of a bond.",
        "category": "Fixed Income",
        "subCategory": "Corporate Bonds",
        "source": ["FINRA"],
    },
    examples=[
        APIEx(
            description="Five years of end-of-day prices and yields for a bond.",
            parameters={"cusip": "037833EH9", "provider": "finra"},
        ),
        APIEx(
            description="A window of history for a bond by its FINRA symbol.",
            parameters={
                "cusip": "AAPL5231623",
                "start_date": "2026-01-01",
                "end_date": "2026-06-30",
                "provider": "finra",
            },
        ),
    ],
)
async def bond_historical(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the daily end-of-day TRACE price and yield of bonds."""
    return await OBBject.from_query(OBBQuery(**locals()))


@router.command(
    model="FinraBondList",
    widget_config={
        "name": "FINRA TRACE Bond List",
        "description": "Every TRACE-reported bond of one type.",
        "category": "Fixed Income",
        "subCategory": "Reference",
        "source": ["FINRA"],
    },
    examples=[
        APIEx(
            description="Every outstanding corporate and agency bond.",
            parameters={"provider": "finra"},
        ),
        APIEx(
            description="Every Treasury note and bond, matured ones included.",
            parameters={
                "bond_type": "TS",
                "include_matured": True,
                "provider": "finra",
            },
        ),
    ],
)
async def bonds(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """List every TRACE-reported bond of one type, with its reference data and last sale."""
    return await OBBject.from_query(OBBQuery(**locals()))


if not FIXEDINCOME_INSTALLED:

    @router.command(
        model="FinraBondPrices",
        widget_config={
            "name": "FINRA TRACE Bonds",
            "description": "TRACE-reported bonds with reference data and last sales.",
            "category": "Fixed Income",
            "subCategory": "Corporate Bonds",
            "source": ["FINRA"],
        },
        examples=[
            APIEx(
                description="Look up a bond by CUSIP; its TRACE product is detected.",
                parameters={"cusip": "037833EH9", "provider": "finra"},
            ),
            APIEx(
                description="Outstanding bonds of an issuer, matching every word.",
                parameters={"issuer_name": "apple", "provider": "finra"},
            ),
            APIEx(
                description="Treasury notes and bonds maturing within a window.",
                parameters={
                    "bond_type": "TS",
                    "maturity_date_min": "2030-01-01",
                    "maturity_date_max": "2035-12-31",
                    "provider": "finra",
                },
            ),
        ],
    )
    async def bond_prices(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Search TRACE-reported bonds, with reference data and the last reported sale."""
        return await OBBject.from_query(OBBQuery(**locals()))
