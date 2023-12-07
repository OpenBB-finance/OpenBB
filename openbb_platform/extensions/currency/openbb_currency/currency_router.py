"""The Currency router."""
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

from openbb_currency.price.price_router import router as price_router

router = Router(prefix="")
router.include_router(price_router)


# pylint: disable=unused-argument
@router.command(model="CurrencyPairs")
async def search(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Currency Search. Search available currency pairs."""
    return await OBBject.from_query(Query(**locals()))


@router.command(model="CurrencyReferenceRates")
async def reference_rates(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Current, official, currency reference rates."""
    return await OBBject.from_query(Query(**locals()))
