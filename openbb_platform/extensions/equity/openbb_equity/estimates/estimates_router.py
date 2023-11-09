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
def price_target(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Price Target. Price target data."""
    return OBBject(results=Query(**locals()).execute())


@router.command(model="AnalystEstimates")
def historical(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Historical Analyst Estimates. Analyst stock recommendations."""
    return OBBject(results=Query(**locals()).execute())


@router.command(model="PriceTargetConsensus")
def consensus(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Price Target Consensus. Price target consensus data."""
    return OBBject(results=Query(**locals()).execute())
