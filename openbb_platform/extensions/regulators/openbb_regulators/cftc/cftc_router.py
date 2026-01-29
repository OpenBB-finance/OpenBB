# pylint: disable=W0613:unused-argument
"""商品期货交易委员会 (CFTC) 路由器。"""

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

router = Router(prefix="/cftc")


@router.command(
    model="COTSearch",
    examples=[
        APIEx(parameters={"provider": "cftc"}),
        APIEx(parameters={"query": "gold", "provider": "cftc"}),
    ],
)
async def cot_search(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """获取当前的交易者持仓报告。

    搜索当前的交易者持仓报告系列信息列表。
    """
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="COT",
    examples=[
        APIEx(parameters={"provider": "ctfc"}),
        APIEx(
            description="获取所有分类为 GOLD 的项目的最新报告。",
            parameters={"id": "gold", "provider": "cftc"},
        ),
        APIEx(
            description="输入单个 CFTC 市场合约代码的完整历史记录。",
            parameters={"id": "088691", "provider": "cftc"},
        ),
        APIEx(
            description="仅获取期货报告。",
            parameters={"id": "088691", "futures_only": True, "provider": "cftc"},
        ),
        APIEx(
            description="获取最新的商品指数交易者补充报告。",
            parameters={"id": "all", "report_type": "supplemental", "provider": "cftc"},
        ),
    ],
)
async def cot(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """获取交易者持仓报告。"""
    return await OBBject.from_query(Query(**locals()))
