"""FRED Survey sub-router."""

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

from openbb_fred import ECONOMY_INSTALLED

router = Router(prefix="/economy/survey", description="FRED survey data.")


if not ECONOMY_INSTALLED:

    @router.command(
        model="FredManufacturingOutlookNY",
        examples=[APIEx(parameters={"provider": "fred"})],
    )
    async def manufacturing_outlook_ny(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Empire State Manufacturing Survey."""
        return await OBBject.from_query(OBBQuery(**locals()))

    @router.command(
        model="FredManufacturingOutlookTexas",
        examples=[APIEx(parameters={"provider": "fred"})],
    )
    async def manufacturing_outlook_texas(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Texas Manufacturing Outlook Survey."""
        return await OBBject.from_query(OBBQuery(**locals()))

    @router.command(
        model="FredNonFarmPayrolls",
        examples=[APIEx(parameters={"provider": "fred"})],
    )
    async def nonfarm_payrolls(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Nonfarm Payrolls Survey."""
        return await OBBject.from_query(OBBQuery(**locals()))

    @router.command(
        model="FredSeniorLoanOfficerSurvey",
        examples=[APIEx(parameters={"provider": "fred"})],
    )
    async def sloos(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Senior Loan Officer Opinion Survey on Bank Lending Practices."""
        return await OBBject.from_query(OBBQuery(**locals()))

    @router.command(
        model="FredSurveyOfEconomicConditionsChicago",
        examples=[APIEx(parameters={"provider": "fred"})],
    )
    async def economic_conditions_chicago(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Survey of Economic Conditions - Chicago Fed."""
        return await OBBject.from_query(OBBQuery(**locals()))

    @router.command(
        model="FredUniversityOfMichigan",
        examples=[APIEx(parameters={"provider": "fred"})],
    )
    async def university_of_michigan(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Get University of Michigan Consumer Sentiment and Inflation Expectations Surveys."""
        return await OBBject.from_query(OBBQuery(**locals()))
