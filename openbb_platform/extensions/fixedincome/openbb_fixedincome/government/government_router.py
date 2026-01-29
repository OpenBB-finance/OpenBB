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


@router.command(
    model="SvenssonYieldCurve",
    examples=[
        APIEx(parameters={"provider": "federal_reserve"}),
        APIEx(
            description="Parameters are applied post-request to filter the data.",
            parameters={
                "series_type": "zero_coupon",
                "start_date": "2020-01-01",
                "end_date": "2025-12-31",
                "provider": "federal_reserve",
            },
        ),
    ],
)
async def svensson_yield_curve(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:  # type: ignore
    """Svensson Nominal Yield Curve Data.

    Source: https://www.federalreserve.gov/data/nominal-yield-curve.htm

    The Svensson model, stipulates that the shape of the yield curve on any given date
    can be adequately captured by a set of six parameters.

    The values of these parameters can be estimated by minimizing the discrepancy
    between the fitted Svensson yield curve and observed market yields.

    This Svensson model is used to fit daily yield curves for the period since 1980.

    Before 1980, the Nelson-Siegel model—a model with fewer parameters—was used to fit the yield curve,
    as there were not enough Treasury securities to fit the Svensson model.

    This data provides daily estimated nominal yield curve parameters,
    and smoothed yields on hypothetical Treasury securities that can
    be easily compared across maturities and over time, from 1961 to the present.

    - Zero-coupon yields (SVENY): Continuously compounded, 1-30 year maturities
    - Par yields (SVENPY): Coupon-equivalent, 1-30 year maturities
    - Instantaneous forward rates (SVENF): Continuously compounded, 1-30 year horizons
    - One-year forward rates (SVEN1F): Coupon-equivalent, at select horizons
    - Model parameters (BETA0-BETA3, TAU1-TAU2): Nelson-Siegel-Svensson coefficients
    """
    return await OBBject.from_query(Query(**locals()))
