"""Fixed Income Corporate Router."""
from openbb_core.app.model.command_context import CommandContext
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.provider_interface import (
    ExtraParams,
    ProviderChoices,
    StandardParams,
)
from openbb_core.app.query import Query
from openbb_core.app.router import Router
from pydantic import BaseModel

router = Router(prefix="/spreads")

# pylint: disable=unused-argument


@router.command(model="TreasuryConstantMaturity")
async def tmc(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Treasury Constant Maturity.

    Get data for 10-Year Treasury Constant Maturity Minus Selected Treasury Constant Maturity.
    Constant maturity is the theoretical value of a U.S. Treasury that is based on recent values of auctioned U.S.
    Treasuries. The value is obtained by the U.S. Treasury on a daily basis through interpolation of the Treasury
    yield curve which, in turn, is based on closing bid-yields of actively-traded Treasury securities.
    """
    return await OBBject.from_query(Query(**locals()))


@router.command(model="SelectedTreasuryConstantMaturity")
async def tmc_effr(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Select Treasury Constant Maturity.

    Get data for Selected Treasury Constant Maturity Minus Federal Funds Rate
    Constant maturity is the theoretical value of a U.S. Treasury that is based on recent values of auctioned U.S.
    Treasuries. The value is obtained by the U.S. Treasury on a daily basis through interpolation of the Treasury
    yield curve which, in turn, is based on closing bid-yields of actively-traded Treasury securities.
    """
    return await OBBject.from_query(Query(**locals()))


@router.command(model="SelectedTreasuryBill")
async def treasury_effr(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Select Treasury Bill.

    Get Selected Treasury Bill Minus Federal Funds Rate.
    Constant maturity is the theoretical value of a U.S. Treasury that is based on recent values of
    auctioned U.S. Treasuries.
    The value is obtained by the U.S. Treasury on a daily basis through interpolation of the Treasury
    yield curve which, in turn, is based on closing bid-yields of actively-traded Treasury securities.
    """
    return await OBBject.from_query(Query(**locals()))
