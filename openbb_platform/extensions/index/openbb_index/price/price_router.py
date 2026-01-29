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
    model="IndexHistorical",
    examples=[
        APIEx(parameters={"symbol": "^GSPC", "provider": "fmp"}),
        APIEx(
            description="并非所有提供商都具有相同的股票代码。",
            parameters={"symbol": "SPX", "provider": "intrinio"},
        ),
    ],
)
async def historical(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """历史指数水平。"""
    return await OBBject.from_query(Query(**locals()))
