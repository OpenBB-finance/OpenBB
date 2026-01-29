"""固定收益路由器。"""

# pylint: disable=W0613:unused-argument

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

from openbb_fixedincome.corporate.corporate_router import router as corporate_router
from openbb_fixedincome.government.government_router import router as government_router
from openbb_fixedincome.rate.rate_router import router as rate_router
from openbb_fixedincome.spreads.spreads_router import router as spreads_router

router = Router(prefix="", description="固定收益市场数据。")
router.include_router(rate_router)
router.include_router(spreads_router)
router.include_router(government_router)
router.include_router(corporate_router)


@router.command(
    model="BondIndices",
    examples=[
        APIEx(
            description="FRED 的默认状态是用于构建美国公司债券收益率曲线的系列。",
            parameters={"provider": "fred"},
        ),
        APIEx(
            description="可以请求同一“类别”中的多个指数。",
            parameters={
                "category": "high_yield",
                "index": "us,europe,emerging",
                "index_type": "total_return",
                "provider": "fred",
            },
        ),
        APIEx(
            description="对于 FRED，有三个主要类别：'high_yield'、'us' 和 'emerging_markets'。"
            + " 新兴市场是一个广泛的类别。",
            parameters={
                "category": "emerging_markets",
                "index": "corporate,private_sector,public_sector",
                "provider": "fred",
            },
        ),
    ],
)
async def bond_indices(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:  # type: ignore
    """债券指数。"""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="MortgageIndices",
    examples=[
        APIEx(
            description="FRED 的默认状态是 Optimal Blue 的主要抵押贷款指数。",
            parameters={"provider": "fred"},
        ),
        APIEx(
            description="可以请求多个指数。",
            parameters={
                "index": "jumbo_30y,conforming_30y,conforming_15y",
                "provider": "fred",
            },
        ),
    ],
)
async def mortgage_indices(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:  # type: ignore
    """抵押贷款指数。"""
    return await OBBject.from_query(Query(**locals()))
