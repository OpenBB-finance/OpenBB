"""Economy Router."""

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

from openbb_economy.gdp.gdp_router import router as gdp_router

router = Router(prefix="", description="Economic data.")
router.include_router(gdp_router)

# pylint: disable=unused-argument


@router.command(
    model="EconomicCalendar",
    examples=[
        APIEx(
            parameters={"provider": "fmp"},
            description="By default, the calendar will be forward-looking.",
        ),
        APIEx(
            parameters={
                "provider": "fmp",
                "start_date": "2020-03-01",
                "end_date": "2020-03-31",
            }
        ),
        APIEx(
            description="By default, the calendar will be forward-looking.",
            parameters={"provider": "nasdaq"},
        ),
    ],
)
async def calendar(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the upcoming, or historical, economic calendar of global events."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="ConsumerPriceIndex",
    examples=[
        APIEx(parameters={"country": "japan,china,turkey", "provider": "fred"}),
        APIEx(
            description="Use the `units` parameter to define the reference period for the change in values.",
            parameters={
                "country": "united_states,united_kingdom",
                "units": "growth_previous",
                "provider": "fred",
            },
        ),
    ],
)
async def cpi(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get Consumer Price Index (CPI).

    Returns either the rescaled index value, or a rate of change (inflation).
    """
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="RiskPremium",
    examples=[APIEx(parameters={"provider": "fmp"})],
)
async def risk_premium(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get Market Risk Premium by country."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="BalanceOfPayments",
    examples=[
        APIEx(parameters={"provider": "ecb"}),
        APIEx(parameters={"report_type": "summary", "provider": "ecb"}),
        APIEx(
            description="The `country` parameter will override the `report_type`.",
            parameters={"country": "united_states", "provider": "ecb"},
        ),
    ],
)
async def balance_of_payments(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Balance of Payments Reports."""
    return await OBBject.from_query(Query(**locals()))


@router.command(model="FredSearch", examples=[APIEx(parameters={"provider": "fred"})])
async def fred_search(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Search for FRED series or economic releases by ID or string.

    This does not return the observation values, only the metadata.
    Use this function to find series IDs for `fred_series()`.
    """
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="FredSeries",
    examples=[
        APIEx(parameters={"symbol": "NFCI", "provider": "fred"}),
        APIEx(
            description="Multiple series can be passed in as a list.",
            parameters={"symbol": "NFCI,STLFSI4", "provider": "fred"},
        ),
        APIEx(
            description="Use the `transform` parameter to transform the data as change, log, or percent change.",
            parameters={"symbol": "CBBTCUSD", "transform": "pc1", "provider": "fred"},
        ),
    ],
)
async def fred_series(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get data by series ID from FRED."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="MoneyMeasures",
    examples=[
        APIEx(parameters={"provider": "federal_reserve"}),
        APIEx(parameters={"adjusted": False, "provider": "federal_reserve"}),
    ],
)
async def money_measures(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get Money Measures (M1/M2 and components).

    The Federal Reserve publishes as part of the H.6 Release.
    """
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="Unemployment",
    examples=[
        APIEx(parameters={"provider": "oecd"}),
        APIEx(
            parameters={"country": "all", "frequency": "quarterly", "provider": "oecd"}
        ),
        APIEx(
            description="Demographics for the statistics are selected with the `age` parameter.",
            parameters={
                "country": "all",
                "frequency": "quarterly",
                "age": "25-54",
                "provider": "oecd",
            },
        ),
    ],
)
async def unemployment(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get global unemployment data."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="CLI",
    examples=[
        APIEx(parameters={"provider": "oecd"}),
        APIEx(parameters={"country": "all", "provider": "oecd"}),
    ],
)
async def composite_leading_indicator(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Use the composite leading indicator (CLI).

    It is designed to provide early signals of turning points
    in business cycles showing fluctuation of the economic activity around its long term potential level.

    CLIs show short-term economic movements in qualitative rather than quantitative terms.
    """
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="STIR",
    examples=[
        APIEx(parameters={"provider": "oecd"}),
        APIEx(
            parameters={"country": "all", "frequency": "quarterly", "provider": "oecd"}
        ),
    ],
)
async def short_term_interest_rate(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get Short-term interest rates.

    They are the rates at which short-term borrowings are effected between
    financial institutions or the rate at which short-term government paper is issued or traded in the market.

    Short-term interest rates are generally averages of daily rates, measured as a percentage.
    Short-term interest rates are based on three-month money market rates where available.
    Typical standardised names are "money market rate" and "treasury bill rate".
    """
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="LTIR",
    examples=[
        APIEx(parameters={"provider": "oecd"}),
        APIEx(
            parameters={"country": "all", "frequency": "quarterly", "provider": "oecd"}
        ),
    ],
)
async def long_term_interest_rate(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get Long-term interest rates that refer to government bonds maturing in ten years.

    Rates are mainly determined by the price charged by the lender, the risk from the borrower and the
    fall in the capital value. Long-term interest rates are generally averages of daily rates,
    measured as a percentage. These interest rates are implied by the prices at which the government bonds are
    traded on financial markets, not the interest rates at which the loans were issued.
    In all cases, they refer to bonds whose capital repayment is guaranteed by governments.
    Long-term interest rates are one of the determinants of business investment.
    Low long-term interest rates encourage investment in new equipment and high interest rates discourage it.
    Investment is, in turn, a major source of economic growth.
    """
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="FredRegional",
    examples=[
        APIEx(
            parameters={"symbol": "NYICLAIMS", "provider": "fred"},
        ),
        APIEx(
            description="With a date, time series data is returned.",
            parameters={
                "symbol": "NYICLAIMS",
                "start_date": "2021-01-01",
                "end_date": "2021-12-31",
                "limit": 10,
                "provider": "fred",
            },
        ),
    ],
)
async def fred_regional(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Query the Geo Fred API for regional economic data by series group.

    The series group ID is found by using `fred_search` and the `series_id` parameter.
    """
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="CountryProfile",
    examples=[
        APIEx(parameters={"provider": "econdb", "country": "united_kingdom"}),
        APIEx(
            description="Enter the country as the full name, or iso code."
            + " If `latest` is False, the complete history for each series is returned.",
            parameters={
                "country": "united_states,jp",
                "latest": False,
                "provider": "econdb",
            },
        ),
    ],
)
async def country_profile(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get a profile of country statistics and economic indicators."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="AvailableIndicators",
    examples=[
        APIEx(parameters={"provider": "econdb"}),
    ],
)
async def available_indicators(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the available economic indicators for a provider."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="EconomicIndicators",
    examples=[
        APIEx(parameters={"provider": "econdb", "symbol": "PCOCO"}),
        APIEx(
            description="Enter the country as the full name, or iso code."
            + " Use `available_indicators()` to get a list of supported indicators from EconDB.",
            parameters={
                "symbol": "CPI",
                "country": "united_states,jp",
                "provider": "econdb",
            },
        ),
    ],
)
async def indicators(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get economic indicators by country and indicator."""
    return await OBBject.from_query(Query(**locals()))
