"""Estimates Router."""
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

router = Router(prefix="/estimates")

# pylint: disable=unused-argument


@router.command(model="PriceTarget")
async def price_target(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Price Target. Price target data."""
    return await OBBject.from_query(Query(**locals()))


@router.command(model="AnalystEstimates")
async def historical(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Historical Analyst Estimates. Analyst stock recommendations."""
    return await OBBject.from_query(Query(**locals()))


@router.command(model="PriceTargetConsensus")
async def consensus(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Price Target Consensus. Price target consensus data."""
    return await OBBject.from_query(Query(**locals()))
