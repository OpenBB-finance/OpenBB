# pylint: disable=import-outside-toplevel
# pylint: disable=unused-import
# ruff: noqa: F401
"""Regulators Router."""

from openbb_core.app.router import Router

from .sec.sec_router import router as sec_router

router = Router(prefix="", description="Financial market regulators data.")
router.include_router(sec_router)
