"""Economy Router."""

# pylint: disable=unused-argument

from typing import Annotated, Union

from fastapi import Body
from openbb_core.app.deprecation import OpenBBDeprecationWarning
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
    model="STIR",
    deprecated=True,
    deprecation=OpenBBDeprecationWarning(
        message="This endpoint will be removed in a future version. Use, `/economy/interest_rates`, instead.",
        since=(4, 3),
        expected_removal=(4, 5),
    ),
    examples=[
        APIEx(parameters={"provider": "oecd"}),
        APIEx(
            parameters={"country": "all", "frequency": "quarterly", "provider": "oecd"}
        ),
    ],
    openapi_extra={
        "widget_config": {
            "exclude": True,
        }
    },
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
    deprecated=True,
    deprecation=OpenBBDeprecationWarning(
        message="This endpoint will be removed in a future version. Use, `/economy/interest_rates`, instead.",
        since=(4, 3),
        expected_removal=(4, 5),
    ),
    examples=[
        APIEx(parameters={"provider": "oecd"}),
        APIEx(
            parameters={"country": "all", "frequency": "quarterly", "provider": "oecd"}
        ),
    ],
    openapi_extra={
        "widget_config": {
            "exclude": True,
        }
    },
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
        APIEx(
            description="Use the `main` symbol to get the group of main indicators for a country.",
            parameters={"provider": "econdb", "symbol": "main", "country": "eu"},
        ),
        APIEx(
            description="When the provider is 'imf', the absence of a symbol will default to 'irfcl_top_lines'."
            + " Use 'IRFCL' to get all the data from the set of indicators.",
            parameters={"provider": "imf"},
        ),
        APIEx(
            description="When the provider is 'imf', complete tables are returned by using a 'preset'."
            + " Refer to the function's docstring for descriptions of each preset."
            + " When no country is supplied, the data is returned for all countries.",
            parameters={"provider": "imf", "symbol": "gold_reserves"},
        ),
        APIEx(
            description="When the provider is 'imf', multiple countries and symbols can be supplied."
            + " Enter countries as a two-letter ISO country code, or the country name in lower_snake_case.",
            parameters={
                "provider": "imf",
                "symbol": "RAFA_USD,RAPFA_USD,RAFA_RAPFA_RO",
                "country": "us,china,jp,4f,gb",
                "start_date": "2010-01-01",
                "end_date": "2020-12-31",
                "frequency": "annual",
            },
        ),
        APIEx(
            description=(
                "When the provider is 'imf', additional presets return the core Financial Soundness Indicators."
                "\n    'fsi_core' -  Core FSIs"
                "\n    'fsi_encouraged_set' - Encouraged Set of FSIs,"
                "\n    'fsi_core_underlying' - Underlying data for the Core FSIs."
                "\n    'fsi_other' - Additional/Other FSIs that are not in the Core or Encouraged Set."
                "\n    'fsi_all' - all FSI data for a single country."
            ),
            parameters={
                "provider": "imf",
                "symbol": "fsi_encouraged_set",
                "country": "us,fr,gb",
                "start_date": "2022-01-01",
                "end_date": "2023-12-31",
                "frequency": "annual",
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
    model="ImmediateInterestRate",
    deprecated=True,
    deprecation=OpenBBDeprecationWarning(
        message="This endpoint will be removed in a future version. Use, `/economy/interest_rates`, instead.",
        since=(4, 3),
        expected_removal=(4, 5),
    ),
    examples=[
        APIEx(parameters={"provider": "oecd"}),
        APIEx(
            description="Multiple countries can be passed in as a list.",
            parameters={
                "country": "united_kingdom,germany",
                "frequency": "monthly",
                "provider": "oecd",
            },
        ),
    ],
    openapi_extra={
        "widget_config": {
            "exclude": True,
        }
    },
)
async def immediate_interest_rate(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get immediate interest rates by country."""
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
    model="PortVolume",
    examples=[
        APIEx(parameters={"provider": "econdb"}),
        APIEx(
            description="Get daily port calls and estimated trading volumes for specific ports"
            + " Get the list of available ports with `openbb shipping port_info`",
            parameters={
                "provider": "imf",
                "port_code": "rotterdam,singapore",
            },
        ),
    ],
    deprecated=True,
    deprecation=OpenBBDeprecationWarning(
        message="This endpoint has been moved and will be removed in a future version."
        + " Use, `/economy/shipping/port_volume`, instead.",
        since=(4, 4),
        expected_removal=(4, 5),
    ),
    openapi_extra={
        "widget_config": {
            "exclude": True,
        }
    },
)
async def port_volume(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get average dwelling times and TEU volumes from the top ports."""
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
    response_model=Union[list, dict],
    openapi_extra={
        "widget_config": {
            "type": "multi_file_viewer",
            "name": "FOMC PDF Document Viewer",
            "description": "Current and historical FOMC PDF materials.",
            "gridData": {
                "w": 30,
                "h": 27,
            },
            "refetchInterval": False,
            "endpoint": "/api/v1/economy/fomc_documents/download",
            "params": [
                {
                    "type": "endpoint",
                    "paramName": "url",
                    "optionsEndpoint": f"{api_prefix}/economy/fomc_documents",
                    "optionsParams": {
                        "document_type": "$document_type",
                        "year": "$year",
                        "pdf_only": True,
                        "as_choices": True,
                        "provider": "federal_reserve",
                    },
                    "show": False,
                    "multiSelect": True,
                    "roles": ["fileSelector"],
                },
            ],
        }
    },
)
async def fomc_documents(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """
    Get FOMC documents by year and document type.

    Source: https://www.federalreserve.gov/monetarypolicy/fomc_historical.htm

    Source: https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm

    This function does not return the typical OBBject response.

    The response is `list[dict[str, str]]` of FOMC documents and their URLs.

    Each dictionary entry has keys: `date`, `url`, `doc_type`, and `doc_format`.

    If `as_choices` is True, the response is a list of valid Workspace parameter choices.
    Keys, `label` and `value`, correspond with the `doc_type` + `date`, and the `url`, respectively.
    """
    results = await OBBject.from_query(Query(**locals()))

    return results.results.content


# This endpoint is used to download FOMC documents in Workspace.
# This is not included in the OpenAPI schema or Python SDK.


# pylint: disable=protected-access
@router._api_router.post(
    "/fomc_documents/download",
    include_in_schema=False,
    openapi_extra={
        "widget_config": {
            "exclude": True,
        }
    },
)
async def fomc_documents_download(params: Annotated[dict, Body()]) -> list:
    """
    Download FOMC documents from the Federal Reserve's website.

    This function does not return the typical OBBject response.

    The response is a `dict[str, Any]` with keys `filename`, `content`, and `data_format`.
    """
    # pylint: disable=import-outside-toplevel
    import base64  # noqa
    from io import BytesIO
    from openbb_core.provider.utils.helpers import make_request

    urls = params.get("url", [])

    results = []
    for url in urls:
        try:
            response = make_request(url)
            response.raise_for_status()
            pdf = (
                base64.b64encode(BytesIO(response.content).getvalue()).decode("utf-8")
                if isinstance(response.content, bytes)
                else response.content
            )
            results.append(
                {
                    "content": pdf,
                    "data_format": {
                        "data_type": "pdf",
                        "filename": url.split("/")[-1],
                    },
                }
            )
        except Exception as exc:
            results.append(
                {
                    "error_type": "download_error",
                    "content": f"{exc.__class__.__name__}: {exc.args[0]}",
                    "filename": url.split("/")[-1],
                }
            )
            continue

    return results
