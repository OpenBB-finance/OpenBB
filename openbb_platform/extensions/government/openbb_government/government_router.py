"""Government Router."""

# pylint: disable=unused-argument

from typing import Union

from openbb_core.app.deprecation import OpenBBDeprecationWarning
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

from openbb_government.us.us_router import router as us_router

router = Router(prefix="", description="Government data.")
router.include_router(us_router)
