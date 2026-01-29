"""日历路由器。"""

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

router = Router(prefix="/calendar")

# pylint: disable=unused-argument


@router.command(
    model="CalendarIpo",
    examples=[
        APIEx(parameters={"provider": "intrinio"}),
        APIEx(parameters={"limit": 100, "provider": "nasdaq"}),
        APIEx(
            description="获取所有可用的 IPO。", parameters={"provider": "intrinio"}
        ),
        APIEx(
            description="获取特定日期的 IPO。",
            parameters={
                "start_date": "2024-02-01",
                "end_date": "2024-02-07",
                "provider": "nasdaq",
            },
        ),
    ],
)
async def ipo(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """获取历史和即将到来的首次公开募股 (IPO)。"""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="CalendarDividend",
    examples=[
        APIEx(parameters={"provider": "fmp"}),
        APIEx(
            description="获取特定日期的股息日历。",
            parameters={
                "start_date": "2024-02-01",
                "end_date": "2024-02-07",
                "provider": "nasdaq",
            },
        ),
    ],
)
async def dividend(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """获取历史和即将到来的股息支付。包括股息金额、除息日和支付日。"""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="CalendarSplits",
    examples=[
        APIEx(parameters={"provider": "fmp"}),
        APIEx(
            description="获取特定日期的股票拆分日历。",
            parameters={
                "start_date": "2024-02-01",
                "end_date": "2024-02-07",
                "provider": "fmp",
            },
        ),
    ],
)
async def splits(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """获取历史和即将到来的股票拆分操作。"""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="CalendarEvents",
    examples=[
        APIEx(parameters={"provider": "fmp"}),
        APIEx(
            description="获取特定日期的公司事件日历。",
            parameters={
                "start_date": "2024-02-01",
                "end_date": "2024-02-07",
                "provider": "fmp",
            },
        ),
    ],
)
async def events(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """获取历史和即将到来的公司事件，例如投资者日、电话会议、收益发布。"""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="CalendarEarnings",
    examples=[
        APIEx(parameters={"provider": "fmp"}),
        APIEx(
            description="获取特定日期的收益日历。",
            parameters={
                "start_date": "2024-02-01",
                "end_date": "2024-02-07",
                "provider": "fmp",
            },
        ),
    ],
)
async def earnings(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """获取历史和即将到来的公司收益发布。包括每股收益 (EPS) 和收入数据。"""
    return await OBBject.from_query(Query(**locals()))
