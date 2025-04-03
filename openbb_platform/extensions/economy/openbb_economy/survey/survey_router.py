"""Economy Survey Router."""

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

router = Router(prefix="/survey")

# pylint: disable=unused-argument


@router.command(
    model="BlsSeries",
    examples=[
        APIEx(parameters={"provider": "bls", "symbol": "CES0000000001"}),
    ],
)
async def bls_series(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get time series data for one, or more, BLS series IDs."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="BlsSearch",
    examples=[
        APIEx(
            parameters={
                "provider": "bls",
                "category": "cpi",
            }
        ),
        APIEx(
            description="Use semi-colon to separate multiple queries as an & operator.",
            parameters={
                "provider": "bls",
                "category": "cpi",
                "query": "seattle;gasoline",
            },
        ),
    ],
)
async def bls_search(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Search BLS surveys by category and keyword or phrase to identify BLS series IDs."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="SeniorLoanOfficerSurvey",
    examples=[
        APIEx(parameters={"provider": "fred"}),
        APIEx(parameters={"category": "credit_card", "provider": "fred"}),
    ],
)
async def sloos(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get Senior Loan Officers Opinion Survey."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="UniversityOfMichigan",
    examples=[
        APIEx(parameters={"provider": "fred"}),
    ],
)
async def university_of_michigan(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get University of Michigan Consumer Sentiment and Inflation Expectations Surveys."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="SurveyOfEconomicConditionsChicago",
    examples=[
        APIEx(parameters={"provider": "fred"}),
    ],
)
async def economic_conditions_chicago(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get The Survey Of Economic Conditions For The Chicago Region."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="ManufacturingOutlookTexas",
    examples=[
        APIEx(parameters={"provider": "fred"}),
        APIEx(
            parameters={
                "topic": "business_outlook,new_orders",
                "transform": "pc1",
                "provider": "fred",
            }
        ),
    ],
)
async def manufacturing_outlook_texas(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get The Manufacturing Outlook Survey For The Texas Region."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="ManufacturingOutlookNY",
    examples=[
        APIEx(parameters={"provider": "fred"}),
        APIEx(
            parameters={
                "topic": "hours_worked,new_orders",
                "transform": "pc1",
                "provider": "fred",
                "seasonally_adjusted": True,
            }
        ),
    ],
    openapi_extra={
        "widget_config": {
            "name": "Empire State Manufacturing Survey",
        }
    },
)
async def manufacturing_outlook_ny(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the Empire State Manufacturing Survey.

    It is a monthly survey of manufacturers in New York State conducted by the Federal Reserve Bank of New York.

    Participants from across the state in a variety of industries respond to a questionnaire
    and report the change in a variety of indicators from the previous month.

    Respondents also state the likely direction of these same indicators six months ahead.
    April 2002 is the first report, although survey data date back to July 2001.

    The survey is sent on the first day of each month to the same pool of about 200
    manufacturing executives in New York State, typically the president or CEO.

    About 100 responses are received. Most are completed by the tenth, although surveys are accepted until the fifteenth.
    """
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="NonFarmPayrolls",
    examples=[
        APIEx(parameters={"provider": "fred"}),
        APIEx(
            parameters={
                "category": "avg_hours",
                "provider": "fred",
            }
        ),
    ],
)
async def nonfarm_payrolls(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get Nonfarm Payrolls Survey."""
    return await OBBject.from_query(Query(**locals()))
