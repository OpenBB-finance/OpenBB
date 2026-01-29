"""经济调查路由器。"""

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

router = Router(prefix="/survey")

# pylint: disable=unused-argument


@router.command(
    model="BlsSeries",
    examples=[
        APIEx(parameters={"provider": "bls", "symbol": "CES0000000001"}),
    ],
)
async def bls_series(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """获取一个或多个 BLS 系列 ID 的时间序列数据。"""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="BlsSearch",
    examples=[
        APIEx(
            parameters={
                "provider": "bls",
                "category": "cpi",
            }
        ),
        APIEx(
            description="使用分号将多个查询作为 & 运算符分隔。",
            parameters={
                "provider": "bls",
                "category": "cpi",
                "query": "seattle;gasoline",
            },
        ),
    ],
)
async def bls_search(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """按类别和关键字或短语搜索 BLS 调查，以识别 BLS 系列 ID。"""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="SeniorLoanOfficerSurvey",
    examples=[
        APIEx(parameters={"provider": "fred"}),
        APIEx(parameters={"category": "credit_card", "provider": "fred"}),
    ],
)
async def sloos(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """获取高级信贷员意见调查。"""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="UniversityOfMichigan",
    examples=[
        APIEx(parameters={"provider": "fred"}),
    ],
)
async def university_of_michigan(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """获取密歇根大学消费者信心和通胀预期调查。"""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="SurveyOfEconomicConditionsChicago",
    examples=[
        APIEx(parameters={"provider": "fred"}),
    ],
)
async def economic_conditions_chicago(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """获取芝加哥地区经济状况调查。"""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="ManufacturingOutlookTexas",
    examples=[
        APIEx(parameters={"provider": "fred"}),
        APIEx(
            parameters={
                "topic": "business_outlook,new_orders",
                "transform": "pc1",
                "provider": "fred",
            }
        ),
    ],
)
async def manufacturing_outlook_texas(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """获取德克萨斯地区制造业展望调查。"""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="ManufacturingOutlookNY",
    examples=[
        APIEx(parameters={"provider": "fred"}),
        APIEx(
            parameters={
                "topic": "hours_worked,new_orders",
                "transform": "pc1",
                "provider": "fred",
                "seasonally_adjusted": True,
            }
        ),
    ],
    openapi_extra={
        "widget_config": {
            "name": "Empire State Manufacturing Survey",
        }
    },
)
async def manufacturing_outlook_ny(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """获取帝国州制造业调查。

    这是纽约联邦储备银行对纽约州制造商进行的月度调查。

    来自全州各行各业的参与者回答问卷
    并报告各种指标与上个月相比的变化。

    受访者还说明了未来六个月这些相同指标的可能方向。
    2002 年 4 月是第一份报告，尽管调查数据可追溯至 2001 年 7 月。

    调查于每月的最后一天发送给同一组约 200 名
    纽约州的制造业高管，通常是总裁或首席执行官。

    收到了大约 100 份回复。大多数在第十天之前完成，尽管调查接受至第十五天。
    """
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="NonFarmPayrolls",
    examples=[
        APIEx(parameters={"provider": "fred"}),
        APIEx(
            parameters={
                "category": "avg_hours",
                "provider": "fred",
            }
        ),
    ],
)
async def nonfarm_payrolls(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """获取非农就业人数调查。"""
    return await OBBject.from_query(Query(**locals()))
