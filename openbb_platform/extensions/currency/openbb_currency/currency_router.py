"""货币路由器。"""

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

from openbb_currency.price.price_router import router as price_router

router = Router(prefix="", description="外汇 (FX) 市场数据。")
router.include_router(price_router)


# pylint: disable=unused-argument
@router.command(
    model="CurrencyPairs",
    examples=[
        APIEx(parameters={"provider": "fmp"}),
        APIEx(
            description="使用 'intrinio' 作为提供商搜索 'EUR' 货币对。",
            parameters={"provider": "intrinio", "query": "EUR"},
        ),
        APIEx(
            description="使用 'polygon' 作为提供商搜索术语。",
            parameters={"provider": "polygon", "query": "EUR"},
        ),
    ],
)
async def search(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """货币搜索。

    搜索可用货币对。
    货币对是来自两个国家的货币，在外汇市场 (FX) 上配对交易。
    两种货币都有汇率，交易将以此为基础。
    外汇市场内的所有交易，无论是卖出、买入还是交易，都将通过货币对进行。
    (参考: Investopedia)
    主要货币对包括 EUR/USD, USD/JPY, GBP/USD 等。
    """
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="CurrencyReferenceRates",
    examples=[APIEx(parameters={"provider": "ecb"})],
)
async def reference_rates(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """获取当前的官方货币参考汇率。

    外汇参考汇率是由主要金融机构或监管机构设定的汇率，
    作为世界各地货币价值的基准。
    这些汇率用作促进国际贸易和金融交易的标准，
    确保货币转换的一致性和可靠性。
    它们通常每天更新，反映特定时间的市场状况。
    中央银行和金融机构通常使用这些汇率来指导自己的汇率，
    影响全球贸易、贷款和投资。
    """
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="CurrencySnapshots",
    examples=[
        APIEx(parameters={"provider": "fmp"}),
        APIEx(
            description="使用 'fmp' 作为提供商获取从 USD 和 XAU 到 EUR, JPY 和 GBP 的汇率。",
            parameters={
                "provider": "fmp",
                "base": "USD,XAU",
                "counter_currencies": "EUR,JPY,GBP",
                "quote_type": "indirect",
            },
        ),
    ],
)
async def snapshots(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """从基础货币的间接或直接角度查看货币汇率快照。"""
    return await OBBject.from_query(Query(**locals()))
