"""经济航运路由器。"""

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

router = Router(prefix="/shipping")

# pylint: disable=unused-argument


@router.command(
    model="PortInfo",
    examples=[
        APIEx(parameters={"provider": "imf"}),
        APIEx(parameters={"provider": "imf", "continent": "asia_pacific"}),
    ],
)
async def port_info(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """获取给定提供商所有港口的一般元数据和统计信息。"""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="PortVolume",
    examples=[
        APIEx(
            description="获取主要港口的平均停留时间和 TEU 吞吐量。",
            parameters={"provider": "econdb"},
        ),
        APIEx(
            description="获取特定港口的每日停靠次数和预计交易量。"
            + " 使用 `openbb shipping port_info` 获取可用港口列表",
            parameters={
                "provider": "imf",
                "port_code": "rotterdam,singapore",
            },
        ),
        APIEx(
            description="获取特定国家/地区所有港口的数据。使用 3 个字母的 ISO 国家代码。",
            parameters={
                "provider": "imf",
                "country": "GBR",
            },
        ),
    ],
)
async def port_volume(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """世界各地港口的每日停靠次数和预计交易量。"""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="MaritimeChokePointInfo",
    examples=[
        APIEx(parameters={"provider": "imf"}),
    ],
)
async def chokepoint_info(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """从给定提供商获取所有海上咽喉要道的一般元数据和统计信息。"""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="MaritimeChokePointVolume",
    examples=[
        APIEx(parameters={"provider": "imf"}),
        APIEx(
            parameters={
                "provider": "imf",
                "chokepoint": "suez_canal,panama_canal",
            }
        ),
    ],
)
async def chokepoint_volume(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """世界各地航运咽喉要道的每日过境呼叫和预计过境贸易量。"""
    return await OBBject.from_query(Query(**locals()))
