"""经济路由器。"""

# pylint: disable=unused-argument

from typing import Annotated

from fastapi import Body
from openbb_core.app.model.command_context import CommandContext
from openbb_core.app.model.example import APIEx, PythonEx
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.provider_interface import (
    ExtraParams,
    ProviderChoices,
    StandardParams,
)
from openbb_core.app.query import Query
from openbb_core.app.router import Router
from openbb_core.app.service.system_service import SystemService

from openbb_economy.gdp.gdp_router import router as gdp_router
from openbb_economy.shipping.shipping_router import router as shipping_router
from openbb_economy.survey.survey_router import router as survey_router

router = Router(prefix="", description="经济数据。")
router.include_router(gdp_router)
router.include_router(shipping_router)
router.include_router(survey_router)


api_prefix = (
    SystemService()
    .system_settings.python_settings.model_dump()
    .get("api_settings", {})
    .get("prefix", "")
    or "/api/v1"
)


@router.command(
    model="EconomicCalendar",
    examples=[
        APIEx(
            parameters={"provider": "fmp"},
            description="默认情况下，日历是前瞻性的。",
        ),
        APIEx(
            parameters={
                "provider": "fmp",
                "start_date": "2020-03-01",
                "end_date": "2020-03-31",
            }
        ),
        APIEx(
            description="默认情况下，日历是前瞻性的。",
            parameters={"provider": "nasdaq"},
        ),
    ],
)
async def calendar(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """获取全球事件的即将来临或历史经济日历。"""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="ConsumerPriceIndex",
    examples=[
        APIEx(parameters={"country": "japan,china,turkey", "provider": "fred"}),
        APIEx(
            description="使用 `transform` 参数定义值变更的参考周期。默认为同比 (YoY)。",
            parameters={
                "country": "united_states,united_kingdom",
                "transform": "period",
                "provider": "oecd",
            },
        ),
        PythonEx(
            description="从 IMF 获取某国 CPI 篮子的最新报告权重。",
            code=[
                "res = obb.economy.cpi("
                + "provider='imf', country='CAN', transform='weight_percent', expenditure='all', limit=1)",
                "print(res.model_dump(include='results')['results'])",
            ],
        ),
    ],
)
async def cpi(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """按国家获取消费者价格指数 (CPI) 数据。"""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="RiskPremium",
    examples=[APIEx(parameters={"provider": "fmp"})],
)
async def risk_premium(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """按国家获取市场风险溢价。"""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="BalanceOfPayments",
    examples=[
        APIEx(parameters={"provider": "fred"}),
        APIEx(parameters={"provider": "fred", "country": "brazil"}),
        APIEx(parameters={"provider": "ecb"}),
        APIEx(parameters={"report_type": "summary", "provider": "ecb"}),
        APIEx(
            description="`country` 参数将覆盖 `report_type`。",
            parameters={"country": "united_states", "provider": "ecb"},
        ),
    ],
)
async def balance_of_payments(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """国际收支报告。"""
    return await OBBject.from_query(Query(**locals()))


@router.command(model="FredSearch", examples=[APIEx(parameters={"provider": "fred"})])
async def fred_search(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """通过 ID 或字符串搜索 FRED 系列或经济发布。

    这不返回观测值，只返回元数据。
    使用此函数查找 `fred_series()` 的系列 ID。
    """
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="FredSeries",
    examples=[
        APIEx(parameters={"symbol": "NFCI", "provider": "fred"}),
        APIEx(
            description="多个系列可以作为列表传入。",
            parameters={"symbol": "NFCI,STLFSI4", "provider": "fred"},
        ),
        APIEx(
            description="使用 `transform` 参数将数据转换为变化、对数或百分比变化。",
            parameters={"symbol": "CBBTCUSD", "transform": "pc1", "provider": "fred"},
        ),
    ],
)
async def fred_series(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """从 FRED 获取系列 ID 的数据。"""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="FredReleaseTable",
    examples=[
        APIEx(
            description="通过不提供元素 ID 获取发布的顶级元素。",
            parameters={"release_id": "50", "provider": "fred"},
        ),
        APIEx(
            description="深入发布的特定部分。",
            parameters={"release_id": "50", "element_id": "4880", "provider": "fred"},
        ),
        APIEx(
            description="深入发布的特定表格。",
            parameters={"release_id": "50", "element_id": "4881", "provider": "fred"},
        ),
    ],
)
async def fred_release_table(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """从 FRED 获取 ID 和/或元素的经济发布数据。"""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="MoneyMeasures",
    examples=[
        APIEx(parameters={"provider": "federal_reserve"}),
        APIEx(parameters={"adjusted": False, "provider": "federal_reserve"}),
    ],
)
async def money_measures(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """获取货币计量 (M1/M2 及其组成部分)。

    美联储作为 H.6 发布的一部分进行发布。
    """
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="Unemployment",
    examples=[
        APIEx(parameters={"provider": "oecd"}),
        APIEx(
            parameters={"country": "all", "frequency": "quarter", "provider": "oecd"}
        ),
        APIEx(
            description="统计数据的人口统计资料通过 `age` 参数选择。",
            parameters={
                "country": "all",
                "frequency": "quarter",
                "age": "total",
                "provider": "oecd",
            },
        ),
    ],
)
async def unemployment(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """获取全球失业数据。"""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="CompositeLeadingIndicator",
    examples=[
        APIEx(parameters={"provider": "oecd"}),
        APIEx(parameters={"country": "all", "provider": "oecd", "growth_rate": True}),
    ],
)
async def composite_leading_indicator(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """获取综合领先指标 (CLI)。

    它旨在提供商业周期转折点的早期信号，
    显示经济活动围绕其长期潜在水平的波动。

    CLI 以定性而非定量的方式显示短期经济变动。
    """
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="FredRegional",
    examples=[
        APIEx(
            parameters={"symbol": "NYICLAIMS", "provider": "fred"},
        ),
        APIEx(
            description="如果有日期，则返回时间序列数据。",
            parameters={
                "symbol": "NYICLAIMS",
                "start_date": "2021-01-01",
                "end_date": "2021-12-31",
                "limit": 10,
                "provider": "fred",
            },
        ),
    ],
)
async def fred_regional(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """查询 Geo Fred API 以获取按系列组划分的区域经济数据。

    系列组 ID 通过使用 `fred_search` 和 `series_id` 参数找到。
    """
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="CountryProfile",
    examples=[
        APIEx(parameters={"provider": "econdb", "country": "united_kingdom"}),
        APIEx(
            description="输入国家全名或 ISO 代码。"
            + " 如果 `latest` 为 False，则返回每个系列的完整历史记录。",
            parameters={
                "country": "united_states,jp",
                "latest": False,
                "provider": "econdb",
            },
        ),
    ],
)
async def country_profile(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """获取国家统计数据和经济指标的概况。"""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="AvailableIndicators",
    examples=[
        APIEx(parameters={"provider": "econdb"}),
    ],
)
async def available_indicators(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """获取提供商的可用经济指标。"""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="EconomicIndicators",
    examples=[
        APIEx(parameters={"provider": "econdb", "symbol": "PCOCO"}),
        APIEx(
            description="输入国家全名或 ISO 代码。"
            + " 使用 `/economy/available_indicators` 从 EconDB 获取支持的指标列表。",
            parameters={
                "symbol": "CPI",
                "country": "united_states,jp",
                "provider": "econdb",
            },
        ),
        APIEx(
            description="使用 `main` 符号获取国家的主要指标组。",
            parameters={"provider": "econdb", "symbol": "main", "country": "eu"},
        ),
        APIEx(
            description="IMF 指标按其数据流和指标代码标识。"
            + " 使用 `/economy/available_indicators` 获取并搜索支持的指标符号列表。"
            + " 此示例获取各国持有的黄金储备（以金衡盎司为单位）。",
            parameters={
                "provider": "imf",
                "symbol": "IL::RGV_REVS",
                "country": "*",
                "frequency": "month",
                "limit": 1,
                "start_date": "2025-09-30",
            },
        ),
        APIEx(
            description="IMF 符号也可用于检索整个演示文稿表。"
            + " 此示例获取直接投资头寸 (DIP) 表。"
            + " 使用 `/imf_utils/list_tables` 获取支持的演示文稿表符号列表。",
            parameters={
                "provider": "imf",
                "symbol": "DIP::H_DIP_INDICATOR",
                "country": "BRA",
                "frequency": "annual",
                "limit": 2,
                "pivot": True,
            },
        ),
    ],
)
async def indicators(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """按国家和指标获取经济指标。"""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="CentralBankHoldings",
    examples=[
        APIEx(
            description="默认为美联储持有的最新国债。",
            parameters={"provider": "federal_reserve"},
        ),
        APIEx(
            description="获取美联储持有的历史摘要。",
            parameters={"provider": "federal_reserve", "summary": True},
        ),
        APIEx(
            description="获取截至历史日期的资产负债表持有情况。",
            parameters={"provider": "federal_reserve", "date": "2019-05-21"},
        ),
        APIEx(
            description="使用 `holding_type` 参数选择机构证券，"
            + " 或特定类别或国债。",
            parameters={"provider": "federal_reserve", "holding_type": "agency_debts"},
        ),
    ],
)
async def central_bank_holdings(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """获取中央银行的资产负债表持有情况。"""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="SharePriceIndex",
    examples=[
        APIEx(parameters={"provider": "oecd"}),
        APIEx(
            description="多个国家可以作为列表传入。",
            parameters={
                "country": "united_kingdom,germany",
                "frequency": "quarter",
                "provider": "oecd",
            },
        ),
    ],
)
async def share_price_index(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """从 OECD 短期经济统计数据中获取按国家划分的股价指数。"""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="HousePriceIndex",
    examples=[
        APIEx(parameters={"provider": "oecd"}),
        APIEx(
            description="多个国家可以作为列表传入。",
            parameters={
                "country": "united_kingdom,germany",
                "frequency": "quarter",
                "provider": "oecd",
            },
        ),
    ],
)
async def house_price_index(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """从 OECD 短期经济统计数据中获取按国家划分的房价指数。"""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="CountryInterestRates",
    examples=[
        APIEx(parameters={"provider": "oecd"}),
        APIEx(
            description="对于 OECD，期限可以是 'immediate', 'short', 或 'long'。"
            + " 默认为 'short'，即 3 个月利率。"
            + " 隔夜银行同业拆借利率为 'immediate'，10 年期利率为 'long'。",
            parameters={
                "provider": "oecd",
                "country": "all",
                "duration": "immediate",
                "frequency": "quarter",
            },
        ),
        APIEx(
            description="多个国家可以作为列表传入。",
            parameters={
                "duration": "long",
                "country": "united_kingdom,germany",
                "frequency": "monthly",
                "provider": "oecd",
            },
        ),
    ],
)
async def interest_rates(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """按国家和期限获取利率。
    大多数 OECD 国家每月发布短期、长期和即期利率。
    """
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="RetailPrices",
    examples=[
        APIEx(parameters={"provider": "fred"}),
        APIEx(
            description="东北普查区的鸡蛋价格。",
            parameters={
                "item": "eggs",
                "region": "northeast",
                "provider": "fred",
            },
        ),
        APIEx(
            description="美国城市平均各种肉类价格与一年前相比的百分比变化。",
            parameters={
                "item": "meats",
                "transform": "pc1",
                "provider": "fred",
            },
        ),
    ],
)
async def retail_prices(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """获取常见商品的零售价格。"""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="PrimaryDealerPositioning",
    examples=[
        APIEx(parameters={"provider": "federal_reserve"}),
        APIEx(
            parameters={
                "category": "abs",
                "provider": "federal_reserve",
            },
        ),
    ],
)
async def primary_dealer_positioning(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """获取一级交易商头寸统计数据。"""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="PersonalConsumptionExpenditures",
    examples=[
        APIEx(parameters={"provider": "fred"}),
        APIEx(
            description="获取多个日期的报告（输入为逗号分隔字符串）。",
            parameters={
                "provider": "fred",
                "date": "2024-05-01,2024-04-01,2023-05-01",
                "category": "pce_price_index",
            },
        ),
    ],
)
async def pce(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """获取个人消费支出 (PCE) 报告。"""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="ExportDestinations",
    examples=[
        APIEx(parameters={"provider": "econdb", "country": "us"}),
    ],
)
async def export_destinations(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """从联合国 Comtrade 国际贸易统计数据库获取按国家划分的主要出口目的地。"""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="PrimaryDealerFails",
    examples=[
        APIEx(parameters={"provider": "federal_reserve"}),
        APIEx(
            description="将数据转换为按资产类别分类的百分比总计",
            parameters={"provider": "federal_reserve", "unit": "percent"},
        ),
    ],
)
async def primary_dealer_fails(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """一级交易商交付失败和接收失败统计数据。

    纽约联储的数据大约在周四 4:15 p.m.
    更新上周的统计数据。

    有关此主题的研究，请参阅：
    https://www.federalreserve.gov/econres/notes/feds-notes/the-systemic-nature-of-settlement-fails-20170703.html

    “大量且长时间的结算失败被认为会破坏证券市场的流动性和良好运行。

    接近 100% 的失败传递表明抵押品再抵押程度很高，以及无力或不愿借入或购买所需证券。”
    """
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="DirectionOfTrade",
    examples=[
        APIEx(parameters={"provider": "imf", "country": "all", "counterpart": "china"}),
        APIEx(
            description="通过输入逗号分隔列表选择多个国家或对手方。"
            + " 贸易方向可以是 'exports', 'imports', 'balance', 或 'all'。",
            parameters={
                "provider": "imf",
                "country": "us",
                "counterpart": "world,eu",
                "frequency": "annual",
                "direction": "exports",
            },
        ),
    ],
)
async def direction_of_trade(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """从 IMF 数据库获取贸易方向统计数据。

    贸易方向统计 (DOTS) 提供了根据国家主要贸易伙伴分类的
    商品出口和进口价值。
    区域和世界总量包含在世界主要区域之间贸易流的显示中。
    当数据不可用或不最新时，用估计值补充报告数据。
    进口按成本加保险费加运费 (CIF) 报告
    出口按船上交货 (FOB) 报告。
    时间序列数据包含从伙伴国报告得出的估计值
    用于未报告和报告缓慢的国家。
    """
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="FomcDocuments",
    examples=[
        APIEx(parameters={"provider": "federal_reserve"}),
        APIEx(
            description="按年份筛选所有文档。",
            parameters={"provider": "federal_reserve", "year": 2022},
        ),
        APIEx(
            description="按年份和文档类型筛选所有文档。",
            parameters={
                "provider": "federal_reserve",
                "year": 2022,
                "document_type": "minutes",
            },
        ),
    ],
    response_model=list | dict,
    openapi_extra={
        "widget_config": {
            "type": "multi_file_viewer",
            "name": "FOMC PDF Document Viewer",
            "description": "当前和历史 FOMC PDF 材料。",
            "gridData": {
                "w": 30,
                "h": 27,
            },
            "refetchInterval": False,
            "endpoint": f"{api_prefix}/economy/fomc_documents/download",
            "params": [
                {
                    "type": "endpoint",
                    "paramName": "url",
                    "optionsEndpoint": f"{api_prefix}/economy/fomc_documents",
                    "optionsParams": {
                        "document_type": "$document_type",
                        "year": "$year",
                        "pdf_only": True,
                        "as_choices": True,
                        "provider": "federal_reserve",
                    },
                    "show": False,
                    "multiSelect": True,
                    "roles": ["fileSelector"],
                },
            ],
        }
    },
)
async def fomc_documents(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """
    按年份和文档类型获取 FOMC 文档。

    来源: https://www.federalreserve.gov/monetarypolicy/fomc_historical.htm

    来源: https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm

    此函数不返回典型的 OBBject 响应。

    响应是 FOMC 文档及其 URL 的 `list[dict[str, str]]`。

    每个字典条目都有键：`date`, `url`, `doc_type`, 和 `doc_format`。

    如果 `as_choices` 为 True，则响应是有效的工作区参数选项列表。
    键 `label` 和 `value` 分别对应 `doc_type` + `date` 和 `url`。
    """
    results = await OBBject.from_query(Query(**locals()))

    return results.results.content  # type: ignore


# This endpoint is used to download FOMC documents in Workspace.
# This is not included in the OpenAPI schema or Python SDK.


# pylint: disable=protected-access
@router._api_router.post(
    "/fomc_documents/download",
    include_in_schema=False,
    openapi_extra={},
)
async def fomc_documents_download(params: Annotated[dict, Body()]) -> list:
    """
    从美联储网站下载 FOMC 文档。

    此函数不返回典型的 OBBject 响应。

    响应是具有 `filename`、`content` 和 `data_format` 键的 `dict[str, Any]`。
    """
    # pylint: disable=import-outside-toplevel
    import base64  # noqa
    from io import BytesIO
    from openbb_core.provider.utils.helpers import make_request

    urls = params.get("url", [])

    results: list = []
    for url in urls:
        try:
            response = make_request(url)
            response.raise_for_status()
            pdf = (
                base64.b64encode(BytesIO(response.content).getvalue()).decode("utf-8")
                if isinstance(response.content, bytes)
                else response.content
            )
            results.append(
                {
                    "content": pdf,
                    "data_format": {
                        "data_type": "pdf",
                        "filename": url.split("/")[-1],
                    },
                }
            )
        except Exception as exc:
            results.append(
                {
                    "error_type": "download_error",
                    "content": f"{exc.__class__.__name__}: {exc.args[0]}",
                    "filename": url.split("/")[-1],
                }
            )
            continue

    return results
