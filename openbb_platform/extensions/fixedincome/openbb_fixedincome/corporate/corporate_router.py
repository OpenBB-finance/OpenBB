"""固定收益公司路由器。"""

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

router = Router(prefix="/corporate")

# pylint: disable=unused-argument


@router.command(
    model="HighQualityMarketCorporateBond",
    examples=[
        APIEx(parameters={"provider": "fred"}),
        APIEx(parameters={"yield_curve": "par", "provider": "fred"}),
    ],
)
async def hqm(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """高质量市场公司债券。

    HQM 收益率曲线代表高质量公司债券市场，即
    评级为 AAA、AA 或 A 的公司债券。HQM 曲线包含两个回归项。
    这些项是调整因子，将 AAA、AA 和 A 债券混合成一条单一的 HQM 收益率曲线，
    即高质量债券的市场加权平均 (MWA) 质量。
    """
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="SpotRate",
    examples=[
        APIEx(parameters={"provider": "fred"}),
        APIEx(parameters={"maturity": "10,20,30,50", "provider": "fred"}),
    ],
)
async def spot_rates(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """即期利率。

    任何期限的即期利率是指在该期限提供单次付款的债券的收益率。
    这是一种零息债券。
    由于每个即期利率都与单个现金流有关，因此它是
    贴现相同期限养老金负债的相关利率概念。
    """
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="CommercialPaper",
    examples=[
        APIEx(parameters={"provider": "fred"}),
        APIEx(parameters={"category": "all", "maturity": "15d", "provider": "fred"}),
    ],
)
async def commercial_paper(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """商业票据。

    商业票据 (CP) 由主要由公司发行的短期本票组成。
    期限最长可达 270 天，但平均约为 30 天。
    许多公司使用 CP 筹集当前交易所需的现金，
    许多公司发现这是银行贷款的低成本替代方案。
    """
    return await OBBject.from_query(Query(**locals()))


@router.command(model="BondPrices", examples=[APIEx(parameters={"provider": "tmx"})])
async def bond_prices(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """公司债券价格。"""
    return await OBBject.from_query(Query(**locals()))
