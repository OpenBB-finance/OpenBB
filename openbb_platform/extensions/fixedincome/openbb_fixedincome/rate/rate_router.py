"""固定收益利率路由器。"""

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

router = Router(prefix="/rate")

# pylint: disable=unused-argument


@router.command(
    model="Ameribor",
    examples=[
        APIEx(parameters={"provider": "fred"}),
        APIEx(
            description="使用 transform 参数应用一年前的变化。",
            parameters={"maturity": "all", "transform": "pc1", "provider": "fred"},
        ),
    ],
)
async def ameribor(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:  # type: ignore
    """AMERIBOR。

    AMERIBOR（美国银行间同业拆借利率的缩写）是一种基准利率，反映了
    短期银行间借款的真实成本。该利率基于在
    美国金融交易所 (AFX) 进行的隔夜无抵押贷款交易。
    """
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="SONIA",
    examples=[
        APIEx(parameters={"provider": "fred"}),
        APIEx(parameters={"parameter": "total_nominal_value", "provider": "fred"}),
    ],
)
async def sonia(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:  # type: ignore
    """英镑隔夜指数平均值。

    SONIA（英镑隔夜指数平均值）是一个重要的利率基准。SONIA 基于实际
    交易，反映了银行从其他金融机构和其他机构投资者借入隔夜英镑所支付的平均利率。
    """
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="SOFR",
    examples=[
        APIEx(parameters={"provider": "fred"}),
    ],
)
async def sofr(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:  # type: ignore
    """有担保隔夜融资利率。

    有担保隔夜融资利率 (SOFR) 是衡量以国债作为抵押
    隔夜借入现金成本的广泛指标。
    """
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="IORB",
    examples=[APIEx(parameters={"provider": "fred"})],
)
async def iorb(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:  # type: ignore
    """准备金余额利息。

    获取准备金余额利率数据。银行利率是一个国家的中央银行向其
    国内银行收取的借款利率。中央银行收取的利率旨在稳定经济。在
    美国，联邦储备系统理事会设定银行利率，也称为贴现率。
    """
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="FederalFundsRate",
    examples=[
        APIEx(parameters={"provider": "fred"}),
        APIEx(parameters={"effr_only": True, "provider": "fred"}),
    ],
)
async def effr(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:  # type: ignore
    """联邦基金利率。

    获取有效联邦基金利率数据。银行利率是一个国家的中央银行向其
    国内银行收取的借款利率。中央银行收取的利率旨在稳定经济。
    """
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="PROJECTIONS",
    examples=[
        APIEx(parameters={"provider": "fred"}),
        APIEx(parameters={"long_run": True, "provider": "fred"}),
    ],
)
async def effr_forecast(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:  # type: ignore
    """联邦基金利率预测。

    联邦基金利率的预测是
    联邦基金利率的预计适当目标范围的中值，或
    在指定日历年末或长期内联邦基金利率的预计适当目标水平。
    """
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="EuroShortTermRate",
    examples=[
        APIEx(parameters={"provider": "fred"}),
        APIEx(parameters={"transform": "ch1", "provider": "fred"}),
    ],
)
async def estr(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:  # type: ignore
    """欧元短期利率。

    欧元短期利率 (€STR) 反映了位于欧元区的银行的批发欧元无抵押隔夜借款成本。
    €STR 在每个 TARGET2 工作日发布，基于在
    前一个 TARGET2 工作日（报告日期 “T”）进行和结算的交易，到期日为 T+1，这些交易被视为
    按公平原则执行，因此以公正的方式反映市场利率。
    """
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="EuropeanCentralBankInterestRates",
    examples=[
        APIEx(parameters={"provider": "fred"}),
        APIEx(parameters={"interest_rate_type": "refinancing", "provider": "fred"}),
    ],
)
async def ecb(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """欧洲中央银行利率。

    欧洲央行管理委员会设定欧元区的关键利率：

    - 主要再融资操作 (MRO) 的利率，为银行系统提供
    大量流动性。
    - 存款便利利率，银行可利用该利率在欧元系统进行隔夜存款。
    - 边际贷款便利利率，为银行提供来自欧元系统的隔夜信贷。
    """
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="DiscountWindowPrimaryCreditRate",
    examples=[
        APIEx(parameters={"provider": "fred"}),
        APIEx(
            parameters={
                "start_date": "2023-02-01",
                "end_date": "2023-05-01",
                "provider": "fred",
            }
        ),
    ],
)
async def dpcredit(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """贴现窗口一级信贷利率。

    银行利率是一个国家的中央银行向其国内银行收取的借款利率。
    中央银行收取的利率旨在稳定经济。
    在美国，联邦储备系统理事会设定银行利率，
    也称为贴现率。
    """
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="OvernightBankFundingRate",
    examples=[APIEx(parameters={"provider": "fred"})],
)
async def overnight_bank_funding(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:  # type: ignore
    """隔夜银行融资。

    对于美国，隔夜银行融资利率 (OBFR) 计算为
    FR 2420 选定货币市场利率报告中报告的隔夜联邦基金交易和欧洲美元交易的
    成交量加权中值。
    """
    return await OBBject.from_query(Query(**locals()))
