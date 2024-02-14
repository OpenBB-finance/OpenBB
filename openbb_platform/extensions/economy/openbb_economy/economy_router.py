"""Economy Router."""

from openbb_core.app.model.command_context import CommandContext
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.provider_interface import (
    ExtraParams,
    ProviderChoices,
    StandardParams,
)
from openbb_core.app.query import Query
from openbb_core.app.router import Router

from openbb_economy.gdp.gdp_router import router as gdp_router

router = Router(prefix="")
router.include_router(gdp_router)

# pylint: disable=unused-argument


@router.command(
    model="EconomicCalendar",
    exclude_auto_examples=True,
    examples=[
        'obb.economy.calendar(provider="fmp", start_date="2020-03-01", end_date="2020-03-31")',
        "#### By default, the calendar will be forward-looking. ####",
        'obb.economy.calendar(provider="nasdaq")',
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
    exclude_auto_examples=True,
    examples=[
        'obb.economy.cpi(countries=["japan", "china", "turkey"]).to_df()',
        "#### Use the `units` parameter to define the reference period for the change in values. ####",
        'obb.economy.cpi(countries=["united_states", "united_kingdom"], units="growth_previous").to_df()',
    ],
)
async def cpi(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Consumer Price Index (CPI).  Returns either the rescaled index value, or a rate of change (inflation)."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="RiskPremium",
    exclude_auto_examples=True,
    examples=["obb.economy.risk_premium().to_df()"],
)
async def risk_premium(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Market Risk Premium by country."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="BalanceOfPayments",
    exclude_auto_examples=True,
    examples=[
        'obb.economy.balance_of_payments(report_type="summary").to_df().set_index("period").T',
        "#### The `country` parameter will override the `report_type`. ####",
        'obb.economy.balance_of_payments(country="united_states", provider="ecb").to_df().set_index("period").T',
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


@router.command(model="FredSearch")
async def fred_search(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """
    Search for FRED series or economic releases by ID or string.
    This does not return the observation values, only the metadata.
    Use this function to find series IDs for `fred_series()`.
    """
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="FredSeries",
    exclude_auto_examples=True,
    examples=[
        'obb.economy.fred_series("NFCI").to_df()',
        "#### Multiple series can be passed in as a list. ####",
        'obb.economy.fred_series(["NFCI","STLFSI4"]).to_df()',
        "#### Use the `transform` parameter to transform the data as change, log, or percent change. ####",
        'obb.economy.fred_series("CBBTCUSD", transform="pc1").to_df()',
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
    exclude_auto_examples=True,
    examples=[
        "obb.economy.money_measures(adjusted=False).to_df()",
    ],
)
async def money_measures(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Money Measures (M1/M2 and components). The Federal Reserve publishes as part of the H.6 Release."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="Unemployment",
    exclude_auto_examples=True,
    examples=[
        'obb.economy.unemployment(country="all", frequency="quarterly")',
        "#### Demographics for the statistics are selected with the `age` and `sex` parameters. ####",
        "obb.economy.unemployment(",
        'country="all", frequency="quarterly", age="25-54"',
        ').to_df().pivot(columns="country", values="value")',
    ],
)
async def unemployment(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Global unemployment data."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="CLI",
    exclude_auto_examples=True,
    examples=[
        'obb.economy.composite_leading_indicator(country="all").to_df()',
    ],
)
async def composite_leading_indicator(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """The composite leading indicator (CLI) is designed to provide early signals of turning points
    in business cycles showing fluctuation of the economic activity around its long term potential level.
    CLIs show short-term economic movements in qualitative rather than quantitative terms.
    """
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="STIR",
    exclude_auto_examples=True,
    examples=[
        'obb.economy.short_term_interest_rate(country="all", frequency="quarterly").to_df()',
    ],
)
async def short_term_interest_rate(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """
    Short-term interest rates are the rates at which short-term borrowings are effected between
    financial institutions or the rate at which short-term government paper is issued or traded in the market.
    Short-term interest rates are generally averages of daily rates, measured as a percentage.
    Short-term interest rates are based on three-month money market rates where available.
    Typical standardised names are "money market rate" and "treasury bill rate".
    """
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="LTIR",
    exclude_auto_examples=True,
    examples=[
        'obb.economy.long_term_interest_rate(country="all", frequency="quarterly").to_df()',
    ],
)
async def long_term_interest_rate(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """
    Long-term interest rates refer to government bonds maturing in ten years.
    Rates are mainly determined by the price charged by the lender, the risk from the borrower and the
    fall in the capital value. Long-term interest rates are generally averages of daily rates,
    measured as a percentage. These interest rates are implied by the prices at which the government bonds are
    traded on financial markets, not the interest rates at which the loans were issued.
    In all cases, they refer to bonds whose capital repayment is guaranteed by governments.
    Long-term interest rates are one of the determinants of business investment.
    Low long-term interest rates encourage investment in new equipment and high interest rates discourage it.
    Investment is, in turn, a major source of economic growth."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="FredRegional",
    exclude_auto_examples=True,
    examples=[
        "#### With no date, the most recent report is returned. ####",
        'obb.economy.fred_regional("NYICLAIMS")',
        "#### With a date, time series data is returned. ####",
        'obb.economy.fred_regional("NYICLAIMS", start_date="2021-01-01")',
    ],
)
async def fred_regional(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """
    Query the Geo Fred API for regional economic data by series group.
    The series group ID is found by using `fred_search` and the `series_id` parameter.
    """
    return await OBBject.from_query(Query(**locals()))
