# pylint: disable=import-outside-toplevel, W0613:unused-argument
"""新闻路由器。"""

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

router = Router(prefix="", description="金融市场新闻数据。")


@router.command(
    model="WorldNews",
    examples=[
        APIEx(parameters={"provider": "fmp"}),
        APIEx(parameters={"limit": 100, "provider": "intrinio"}),
        APIEx(
            description="获取指定日期的新闻。",
            parameters={
                "start_date": "2024-02-01",
                "end_date": "2024-02-07",
                "provider": "intrinio",
            },
        ),
        APIEx(
            description="显示新闻标题。",
            parameters={"display": "headline", "provider": "benzinga"},
        ),
        APIEx(
            description="按主题获取新闻。",
            parameters={"topics": "finance", "provider": "benzinga"},
        ),
        APIEx(
            description="使用 'tiingo' 作为提供商按来源获取新闻。",
            parameters={"provider": "tiingo", "source": "bloomberg"},
        ),
        APIEx(
            description="使用 'biztoc' 作为提供商按术语筛选文章。",
            parameters={"provider": "biztoc", "term": "apple"},
        ),
    ],
)
async def world(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """世界新闻。全球新闻数据。"""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="CompanyNews",
    examples=[
        APIEx(parameters={"provider": "benzinga"}),
        APIEx(parameters={"limit": 100, "provider": "benzinga"}),
        APIEx(
            description="获取指定日期的新闻。",
            parameters={
                "symbol": "AAPL",
                "start_date": "2024-02-01",
                "end_date": "2024-02-07",
                "provider": "intrinio",
            },
        ),
        APIEx(
            description="显示新闻标题。",
            parameters={
                "symbol": "AAPL",
                "display": "headline",
                "provider": "benzinga",
            },
        ),
        APIEx(
            description="获取多个交易品种的新闻。",
            parameters={"symbol": "aapl,tsla", "provider": "fmp"},
        ),
        APIEx(
            description="获取新闻公司的 ISIN。",
            parameters={
                "symbol": "NVDA",
                "isin": "US0378331005",
                "provider": "benzinga",
            },
        ),
    ],
)
async def company(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """公司新闻。获取一家或多家公司的新闻。"""
    return await OBBject.from_query(Query(**locals()))
