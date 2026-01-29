"""货币的价格路由器。"""

# pylint: disable=unused-argument
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
    model="CurrencyHistorical",
    examples=[
        APIEx(parameters={"symbol": "EURUSD", "provider": "fmp"}),
        APIEx(
            description="使用特定开始和结束日期筛选历史数据。",
            parameters={
                "symbol": "EURUSD",
                "start_date": "2023-01-01",
                "end_date": "2023-12-31",
                "provider": "fmp",
            },
        ),
        APIEx(
            description="获取不同粒度的数据。",
            parameters={"symbol": "EURUSD", "provider": "polygon", "interval": "15m"},
        ),
    ],
)
async def historical(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """
    货币历史价格。货币历史数据。

    货币历史价格是指一种货币兑另一种货币在特定时期内的过去汇率。
    此数据提供了对外汇市场波动和趋势的洞察，
    帮助分析师、交易员和经济学家了解货币表现，
    评估经济健康状况，并对未来走势做出预测。
    """
    return await OBBject.from_query(Query(**locals()))
