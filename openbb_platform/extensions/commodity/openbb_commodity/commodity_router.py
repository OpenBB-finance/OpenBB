"""The Commodity router."""

# pylint: disable=unused-argument,unused-import
# flake8: noqa: F401

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

from openbb_commodity.price.price_router import router as price_router

router = Router(prefix="", description="Commodity market data.")


router.include_router(price_router)
