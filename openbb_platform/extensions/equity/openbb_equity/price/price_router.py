"""价格路由器。"""

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

router = Router(prefix="/price")

# pylint: disable=unused-argument


@router.command(
    model="EquityQuote",
    examples=[APIEx(parameters={"symbol": "AAPL", "provider": "fmp"})],
)
async def quote(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """获取给定股票的最新报价。报价包括价格、成交量和其他数据。"""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="EquityNBBO",
    examples=[APIEx(parameters={"symbol": "AAPL", "provider": "polygon"})],
)
async def nbbo(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """获取给定股票的全国最佳买入和卖出价。"""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="EquityHistorical",
    examples=[
        APIEx(parameters={"symbol": "AAPL", "provider": "fmp"}),
        APIEx(parameters={"symbol": "AAPL", "interval": "1d", "provider": "intrinio"}),
    ],
)
async def historical(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """获取给定股票的历史价格数据。这包括开盘价、最高价、最低价、收盘价和成交量。"""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="PricePerformance",
    examples=[APIEx(parameters={"symbol": "AAPL", "provider": "fmp"})],
)
async def performance(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """获取给定股票的价格表现数据。这包括不同时间段的价格变化。"""
    return await OBBject.from_query(Query(**locals()))
