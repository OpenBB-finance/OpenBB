"""暗池路由器。"""

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

router = Router(prefix="/darkpool")

# pylint: disable=unused-argument


@router.command(
    model="OTCAggregate",
    examples=[
        APIEx(parameters={"provider": "finra"}),
        APIEx(
            description="获取股票的 OTC 数据",
            parameters={"symbol": "AAPL", "provider": "finra"},
        ),
    ],
)
async def otc(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """获取场外交易的每周汇总交易数据。

    每个根据 FINRA 规则有交易报告义务的 ATS/公司的 ATS 和非 ATS 交易数据。
    """
    return await OBBject.from_query(Query(**locals()))
