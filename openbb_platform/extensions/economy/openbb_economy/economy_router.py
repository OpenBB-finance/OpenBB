"""Economy Router."""

# pylint: disable=unused-argument

from openbb_core.app.model.command_context import CommandContext
from openbb_core.app.model.example import APIEx, PythonEx
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.provider_interface import (
    ExtraParams,
    ProviderChoices,
    StandardParams,
)
from openbb_core.app.query import Query
from openbb_core.app.router import Router
from openbb_core.app.service.system_service import SystemService

from openbb_economy.gdp.gdp_router import router as gdp_router
from openbb_economy.shipping.shipping_router import router as shipping_router
from openbb_economy.survey.survey_router import router as survey_router

router = Router(prefix="", description="Economic data.")
router.include_router(gdp_router)
router.include_router(shipping_router)
router.include_router(survey_router)


api_prefix = (
    SystemService()
    .system_settings.python_settings.model_dump()
    .get("api_settings", {})
    .get("prefix", "")
    or "/api/v1"
)


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
            description="Use the `transform` parameter to define the reference period for the change in values."
            + " Default is YoY.",
            parameters={
                "country": "united_states,united_kingdom",
                "transform": "period",
                "provider": "oecd",
            },
        ),
        PythonEx(
            description="Get the latest reported weightings of a country's CPI basket, from IMF.",
            code=[
                "res = obb.economy.cpi("
                + "provider='imf', country='CAN', transform='weight_percent', expenditure='all', limit=1)",
                "print(res.model_dump(include='results')['results'])",
            ],
        ),
    ],
)
async def cpi(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get Consumer Price Index (CPI) data by country."""
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
        APIEx(parameters={"provider": "fred"}),
        APIEx(parameters={"provider": "fred", "country": "brazil"}),
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
    model="FredReleaseTable",
    examples=[
        APIEx(
            description="Get the top-level elements of a release by not supplying an element ID.",
            parameters={"release_id": "50", "provider": "fred"},
        ),
        APIEx(
            description="Drill down on a specific section of the release.",
            parameters={"release_id": "50", "element_id": "4880", "provider": "fred"},
        ),
        APIEx(
            description="Drill down on a specific table of the release.",
            parameters={"release_id": "50", "element_id": "4881", "provider": "fred"},
        ),
    ],
)
async def fred_release_table(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get economic release data by ID and/or element from FRED."""
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
            parameters={"country": "all", "frequency": "quarter", "provider": "oecd"}
        ),
        APIEx(
            description="Demographics for the statistics are selected with the `age` parameter.",
            parameters={
                "country": "all",
                "frequency": "quarter",
                "age": "total",
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
    model="CompositeLeadingIndicator",
    examples=[
        APIEx(parameters={"provider": "oecd"}),
        APIEx(parameters={"country": "all", "provider": "oecd", "growth_rate": True}),
    ],
)
async def composite_leading_indicator(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the composite leading indicator (CLI).

    It is designed to provide early signals of turning points
    in business cycles showing fluctuation of the economic activity around its long term potential level.

    CLIs show short-term economic movements in qualitative rather than quantitative terms.
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
            + " Use `/economy/available_indicators` to get a list of supported indicators from EconDB.",
            parameters={
                "symbol": "CPI",
                "country": "united_states,jp",
                "provider": "econdb",
            },
        ),
        APIEx(
            description="Use the `main` symbol to get the group of main indicators for a country.",
            parameters={"provider": "econdb", "symbol": "main", "country": "eu"},
        ),
        APIEx(
            description="IMF indicators are identified by their dataflow and indicator code."
            + " Use `/economy/available_indicators` to get and search a list of supported indicators symbols."
            + " This example gets gold reserves held by countries, measured in Fine Troy Ounces.",
            parameters={
                "provider": "imf",
                "symbol": "IL::RGV_REVS",
                "country": "*",
                "frequency": "month",
                "limit": 1,
                "start_date": "2025-09-30",
            },
        ),
        APIEx(
            description="IMF symbols can also be used for retrieving entire presentation tables."
            + " This example gets the Direct Investment Position (DIP) table."
            + " Use `/imf_utils/list_tables` to get a list of supported presentation table symbols.",
            parameters={
                "provider": "imf",
                "symbol": "DIP::H_DIP_INDICATOR",
                "country": "BRA",
                "frequency": "annual",
                "limit": 2,
                "pivot": True,
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


@router.command(
    model="CentralBankHoldings",
    examples=[
        APIEx(
            description="The default is the latest Treasury securities held by the Federal Reserve.",
            parameters={"provider": "federal_reserve"},
        ),
        APIEx(
            description="Get historical summaries of the Fed's holdings.",
            parameters={"provider": "federal_reserve", "summary": True},
        ),
        APIEx(
            description="Get the balance sheet holdings as-of a historical date.",
            parameters={"provider": "federal_reserve", "date": "2019-05-21"},
        ),
        APIEx(
            description="Use the `holding_type` parameter to select Agency securities,"
            + " or specific categories or Treasury securities.",
            parameters={"provider": "federal_reserve", "holding_type": "agency_debts"},
        ),
    ],
)
async def central_bank_holdings(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the balance sheet holdings of a central bank."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="SharePriceIndex",
    examples=[
        APIEx(parameters={"provider": "oecd"}),
        APIEx(
            description="Multiple countries can be passed in as a list.",
            parameters={
                "country": "united_kingdom,germany",
                "frequency": "quarter",
                "provider": "oecd",
            },
        ),
    ],
)
async def share_price_index(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the Share Price Index by country from the OECD Short-Term Economics Statistics."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="HousePriceIndex",
    examples=[
        APIEx(parameters={"provider": "oecd"}),
        APIEx(
            description="Multiple countries can be passed in as a list.",
            parameters={
                "country": "united_kingdom,germany",
                "frequency": "quarter",
                "provider": "oecd",
            },
        ),
    ],
)
async def house_price_index(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the House Price Index by country from the OECD Short-Term Economics Statistics."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="CountryInterestRates",
    examples=[
        APIEx(parameters={"provider": "oecd"}),
        APIEx(
            description="For OECD, duration can be 'immediate', 'short', or 'long'."
            + " Default is 'short', which is the 3-month rate."
            + " Overnight interbank rate is 'immediate', and 10-year rate is 'long'.",
            parameters={
                "provider": "oecd",
                "country": "all",
                "duration": "immediate",
                "frequency": "quarter",
            },
        ),
        APIEx(
            description="Multiple countries can be passed in as a list.",
            parameters={
                "duration": "long",
                "country": "united_kingdom,germany",
                "frequency": "monthly",
                "provider": "oecd",
            },
        ),
    ],
)
async def interest_rates(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get interest rates by country(s) and duration.
    Most OECD countries publish short-term, a long-term, and immediate rates monthly.
    """
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="RetailPrices",
    examples=[
        APIEx(parameters={"provider": "fred"}),
        APIEx(
            description="The price of eggs in the northeast census region.",
            parameters={
                "item": "eggs",
                "region": "northeast",
                "provider": "fred",
            },
        ),
        APIEx(
            description="The percentage change in price, from one-year ago, of various meats, US City Average.",
            parameters={
                "item": "meats",
                "transform": "pc1",
                "provider": "fred",
            },
        ),
    ],
)
async def retail_prices(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get retail prices for common items."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="PrimaryDealerPositioning",
    examples=[
        APIEx(parameters={"provider": "federal_reserve"}),
        APIEx(
            parameters={
                "category": "abs",
                "provider": "federal_reserve",
            },
        ),
    ],
)
async def primary_dealer_positioning(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get Primary dealer positioning statistics."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="PersonalConsumptionExpenditures",
    examples=[
        APIEx(parameters={"provider": "fred"}),
        APIEx(
            description="Get reports for multiple dates, entered as a comma-separated string.",
            parameters={
                "provider": "fred",
                "date": "2024-05-01,2024-04-01,2023-05-01",
                "category": "pce_price_index",
            },
        ),
    ],
)
async def pce(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get Personal Consumption Expenditures (PCE) reports."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="ExportDestinations",
    examples=[
        APIEx(parameters={"provider": "econdb", "country": "us"}),
    ],
)
async def export_destinations(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get top export destinations by country from the UN Comtrade International Trade Statistics Database."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="PrimaryDealerFails",
    examples=[
        APIEx(parameters={"provider": "federal_reserve"}),
        APIEx(
            description="Transform the data to be percentage totals by asset class",
            parameters={"provider": "federal_reserve", "unit": "percent"},
        ),
    ],
)
async def primary_dealer_fails(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Primary Dealer Statistics for Fails to Deliver and Fails to Receive.

    Data from the NY Federal Reserve are updated on Thursdays at approximately
    4:15 p.m. with the previous week's statistics.

    For research on the topic, see:
    https://www.federalreserve.gov/econres/notes/feds-notes/the-systemic-nature-of-settlement-fails-20170703.html

    "Large and protracted settlement fails are believed to undermine the liquidity
    and well-functioning of securities markets.

    Near-100 percent pass-through of fails suggests a high degree of collateral
    re-hypothecation together with the inability or unwillingness to borrow or buy the needed securities."
    """
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="DirectionOfTrade",
    examples=[
        APIEx(parameters={"provider": "imf", "country": "all", "counterpart": "china"}),
        APIEx(
            description="Select multiple countries or counterparts by entering a comma-separated list."
            + " The direction of trade can be 'exports', 'imports', 'balance', or 'all'.",
            parameters={
                "provider": "imf",
                "country": "us",
                "counterpart": "world,eu",
                "frequency": "annual",
                "direction": "exports",
            },
        ),
    ],
)
async def direction_of_trade(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get Direction Of Trade Statistics from the IMF database.

    The Direction of Trade Statistics (DOTS) presents the value of merchandise exports and
    imports disaggregated according to a country's primary trading partners.
    Area and world aggregates are included in the display of trade flows between major areas of the world.
    Reported data is supplemented by estimates whenever such data is not available or current.
    Imports are reported on a cost, insurance and freight (CIF) basis
    and exports are reported on a free on board (FOB) basis.
    Time series data includes estimates derived from reports of partner countries
    for non-reporting and slow-reporting countries.
    """
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="FomcDocuments",
    examples=[
        APIEx(parameters={"provider": "federal_reserve"}),
        APIEx(
            description="Filter all documents by year.",
            parameters={"provider": "federal_reserve", "year": 2022},
        ),
        APIEx(
            description="Filter all documents by year and document type.",
            parameters={
                "provider": "federal_reserve",
                "year": 2022,
                "document_type": "minutes",
            },
        ),
    ],
)
async def fomc_documents(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """
    Get lists of FOMC documents by year and document type.

    Source: https://www.federalreserve.gov/monetarypolicy/fomc_historical.htm

    Source: https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm
    """
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="TotalFactorProductivity",
    examples=[
        APIEx(parameters={"provider": "federal_reserve"}),
        APIEx(
            description="Get summary data instead of the default quarterly time series.",
            parameters={"provider": "federal_reserve", "frequency": "summary"},
        ),
    ],
)
async def total_factor_productivity(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Total Factor Productivity (TFP)

    A real-time, quarterly series on total factor productivity (TFP) for the U.S. business sector,
    adjusted for variations in factor utilization - labor effort and capital's workweek.

    The utilization adjustments follows Basu, Fernald, and Kimball (BFK, 2006).
    Using relative prices and input-output information, the series is also decomposed into separate TFP
    and utilization-adjusted TFP series for equipment investment (including consumer durables) and "consumption"
    (defined as business output less equipment and consumer durables).

    Labor includes an adjustment for "quality" or composition.
    Capital services are also adjusted for changes in composition over time
    (e.g. computers, other equipment, structures, and inventories).

    Source: https://www.frbsf.org/research-and-insights/data-and-indicators/total-factor-productivity-tfp/
    """
    return await OBBject.from_query(Query(**locals()))
