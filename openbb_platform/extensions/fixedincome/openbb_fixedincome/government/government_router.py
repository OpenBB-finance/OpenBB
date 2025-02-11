"""Fixed Income Government Router."""

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

router = Router(prefix="/government")

# pylint: disable=unused-argument


@router.command(
    model="YieldCurve",
    examples=[
        APIEx(parameters={"provider": "federal_reserve"}),
        APIEx(parameters={"date": "2023-05-01,2024-05-01", "provider": "fmp"}),
        APIEx(
            parameters={
                "date": "2023-05-01",
                "country": "united_kingdom",
                "provider": "econdb",
            }
        ),
        APIEx(parameters={"provider": "ecb", "yield_curve_type": "par_yield"}),
        APIEx(
            parameters={
                "provider": "fred",
                "yield_curve_type": "real",
                "date": "2023-05-01,2024-05-01",
            }
        ),
    ],
)
async def yield_curve(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:  # type: ignore
    """Get yield curve data by country and date."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="TreasuryRates",
    examples=[APIEx(parameters={"provider": "fmp"})],
)
async def treasury_rates(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Government Treasury Rates."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="TreasuryAuctions",
    examples=[
        APIEx(parameters={"provider": "government_us"}),
        APIEx(
            parameters={
                "security_type": "Bill",
                "start_date": "2022-01-01",
                "end_date": "2023-01-01",
                "provider": "government_us",
            }
        ),
    ],
)
async def treasury_auctions(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Government Treasury Auctions."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="TreasuryPrices",
    examples=[
        APIEx(parameters={"provider": "government_us"}),
        APIEx(parameters={"date": "2019-02-05", "provider": "government_us"}),
    ],
)
async def treasury_prices(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Government Treasury Prices by date."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="TipsYields",
    examples=[
        APIEx(parameters={"provider": "fred"}),
        APIEx(parameters={"maturity": 10, "provider": "fred"}),
    ],
)
async def tips_yields(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get current Treasury inflation-protected securities yields."""
    return await OBBject.from_query(Query(**locals()))
