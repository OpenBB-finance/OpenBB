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
