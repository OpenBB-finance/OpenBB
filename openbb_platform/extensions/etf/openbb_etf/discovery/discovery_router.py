"""ETF 发现路由器。"""

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

router = Router(prefix="/discovery")

# pylint: disable=unused-argument


@router.command(
    model="ETFGainers",
    operation_id="etf_gainers",
    examples=[
        APIEx(description="Get the top ETF gainers.", parameters={"provider": "wsj"}),
    ],
)
async def gainers(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """获取 ETF 涨幅榜。"""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="ETFLosers",
    operation_id="etf_losers",
    examples=[
        APIEx(description="Get the top ETF losers.", parameters={"provider": "wsj"}),
    ],
)
async def losers(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """获取 ETF 跌幅榜。"""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="ETFActive",
    operation_id="etf_active",
    examples=[
        APIEx(description="Get the most active ETFs.", parameters={"provider": "wsj"}),
    ],
)
async def active(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """获取最活跃的 ETF。"""
    return await OBBject.from_query(Query(**locals()))
