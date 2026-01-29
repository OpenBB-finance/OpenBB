# pylint: disable=import-outside-toplevel
# pylint: disable=unused-import
# ruff: noqa: F401
"""监管机构路由器。"""

from openbb_core.app.router import Router

from .cftc.cftc_router import (
    router as cftc_router,
)
from .sec.sec_router import router as sec_router

router = Router(prefix="", description="金融市场监管机构数据。")
router.include_router(sec_router)
router.include_router(cftc_router)
