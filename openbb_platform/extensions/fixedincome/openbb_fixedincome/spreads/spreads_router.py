"""固定收益价差路由器。"""

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

router = Router(prefix="/spreads")

# pylint: disable=unused-argument


@router.command(
    model="TreasuryConstantMaturity",
    examples=[
        APIEx(parameters={"provider": "fred"}),
        APIEx(parameters={"maturity": "2y", "provider": "fred"}),
    ],
)
async def tcm(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """国债固定期限。

    获取 10 年期国债固定期限减去选定国债固定期限的数据。
    固定期限是基于最近拍卖的美国国债价值的美国国债理论价值。
    该价值由美国财政部每天通过国债收益率曲线的插值获得，
    而该曲线又是基于活跃交易的国债证券的收盘买入收益率。
    """
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="SelectedTreasuryConstantMaturity",
    examples=[
        APIEx(parameters={"provider": "fred"}),
        APIEx(parameters={"maturity": "10y", "provider": "fred"}),
    ],
)
async def tcm_effr(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """选定国债固定期限。

    获取选定国债固定期限减去联邦基金利率的数据。
    固定期限是基于最近拍卖的美国国债价值的美国国债理论价值。
    该价值由美国财政部每天通过国债收益率曲线的插值获得，
    而该曲线又是基于活跃交易的国债证券的收盘买入收益率。
    """
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="SelectedTreasuryBill",
    examples=[
        APIEx(parameters={"provider": "fred"}),
        APIEx(parameters={"maturity": "6m", "provider": "fred"}),
    ],
)
async def treasury_effr(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """选定国债票据。

    获取选定国债票据减去联邦基金利率的数据。
    固定期限是基于最近拍卖的美国国债价值的美国国债理论价值。
    该价值由美国财政部每天通过国债收益率曲线的插值获得，
    而该曲线又是基于活跃交易的国债证券的收盘买入收益率。
    """
    return await OBBject.from_query(Query(**locals()))
