"""Dark Pool Shorts (DPS) Router."""
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

router = Router(prefix="/dps")

# pylint: disable=unused-argument


@router.command(model="StockFTD")
def ftd(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Get reported Fail-to-deliver (FTD) data."""
    return OBBject(results=Query(**locals()).execute())


@router.command(model="ShortVolume")
def short_volume(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Get reported Fail-to-deliver (FTD) data."""
    return OBBject(results=Query(**locals()).execute())


@router.command(model="EquityShortInterest")
def short_interest(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Get reported Short Volume and Days to Cover data."""
    return OBBject(results=Query(**locals()).execute())


@router.command(model="OTCAggregate")
def otc(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Weekly aggregate trade data for OTC.

    ATS and non-ATS) trading data for each ATS/firm
    with trade reporting obligations under FINRA rules.
    """
    return OBBject(results=Query(**locals()).execute())
