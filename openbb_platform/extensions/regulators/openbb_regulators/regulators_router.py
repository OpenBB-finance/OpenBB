# pylint: disable=import-outside-toplevel
# pylint: disable=unused-import
# ruff: noqa: F401
"""Regulators Router."""

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

from openbb_regulators.companies_house.companies_house_router import (
    router as companies_house_router,
)
from openbb_regulators.sec.sec_router import router as sec_router

router = Router(prefix="")
router.include_router(sec_router)
router.include_router(companies_house_router)
