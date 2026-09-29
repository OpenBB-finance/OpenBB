"""FRED Rate sub-router."""

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

from openbb_fred import FIXEDINCOME_INSTALLED

router = Router(prefix="/fixedincome/rate", description="FRED reference rates.")


if not FIXEDINCOME_INSTALLED:

    @router.command(
        model="FredAmeribor",
        examples=[APIEx(parameters={"provider": "fred"})],
    )
    async def ameribor(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Ameribor."""
        return await OBBject.from_query(OBBQuery(**locals()))

    @router.command(
        model="FredDiscountWindowPrimaryCreditRate",
        examples=[APIEx(parameters={"provider": "fred"})],
    )
    async def dpcredit(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Discount Window Primary Credit Rate."""
        return await OBBject.from_query(OBBQuery(**locals()))

    @router.command(
        model="FredEuroShortTermRate",
        examples=[APIEx(parameters={"provider": "fred"})],
    )
    async def estr(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Euro Short-Term Rate."""
        return await OBBject.from_query(OBBQuery(**locals()))

    @router.command(
        model="FredEuropeanCentralBankInterestRates",
        examples=[APIEx(parameters={"provider": "fred"})],
    )
    async def ecb(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """European Central Bank Interest Rates."""
        return await OBBject.from_query(OBBQuery(**locals()))

    @router.command(
        model="FredFederalFundsRate",
        examples=[APIEx(parameters={"provider": "fred"})],
    )
    async def effr(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Fed Funds Rate."""
        return await OBBject.from_query(OBBQuery(**locals()))

    @router.command(
        model="FredIORB",
        examples=[APIEx(parameters={"provider": "fred"})],
    )
    async def iorb(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Interest on Reserve Balances."""
        return await OBBject.from_query(OBBQuery(**locals()))

    @router.command(
        model="FredOvernightBankFundingRate",
        examples=[APIEx(parameters={"provider": "fred"})],
    )
    async def overnight_bank_funding(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Overnight Bank Funding."""
        return await OBBject.from_query(OBBQuery(**locals()))

    @router.command(
        model="FredPROJECTIONS",
        examples=[APIEx(parameters={"provider": "fred"})],
    )
    async def effr_forecast(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Fed Funds Rate Projections."""
        return await OBBject.from_query(OBBQuery(**locals()))

    @router.command(
        model="FredSOFR",
        examples=[APIEx(parameters={"provider": "fred"})],
    )
    async def sofr(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Secured Overnight Financing Rate."""
        return await OBBject.from_query(OBBQuery(**locals()))

    @router.command(
        model="FredSONIA",
        examples=[APIEx(parameters={"provider": "fred"})],
    )
    async def sonia(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Sterling Overnight Index Average."""
        return await OBBject.from_query(OBBQuery(**locals()))
