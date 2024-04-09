"""Fixed Income Router."""

# pylint: disable=W0613:unused-argument

from openbb_core.app.model.command_context import CommandContext
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.provider_interface import (
    ExtraParams,
    ProviderChoices,
    StandardParams,
)
from openbb_core.app.query import Query
from openbb_core.app.router import Router

from openbb_fixedincome.corporate.corporate_router import router as corporate_router
from openbb_fixedincome.government.government_router import router as government_router
from openbb_fixedincome.rate.rate_router import router as rate_router
from openbb_fixedincome.spreads.spreads_router import router as spreads_router

router = Router(prefix="")
router.include_router(rate_router)
router.include_router(spreads_router)
router.include_router(government_router)
router.include_router(corporate_router)


@router.command(
    model="SOFR",
    exclude_auto_examples=True,
    examples=[
        'obb.fixedincome.fixedincome.sofr(period="overnight")',
    ],
)
async def sofr(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:  # type: ignore
    """Secured Overnight Financing Rate.

    The Secured Overnight Financing Rate (SOFR) is a broad measure of the cost of
    borrowing cash overnight collateralizing by Treasury securities.
    """
    return await OBBject.from_query(Query(**locals()))
