"""商品路由器。"""

# pylint: disable=unused-argument,unused-import
# flake8: noqa: F401

# pylint: disable=unused-argument

from datetime import datetime

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

from openbb_commodity.price.price_router import router as price_router

router = Router(prefix="", description="商品市场数据。")
router.include_router(price_router)
api_prefix = SystemService().system_settings.api_settings.prefix


@router.command(
    model="PetroleumStatusReport",
    examples=[
        APIEx(
            description="获取 EIA 的每周石油状况报告。",
            parameters={"provider": "eia"},
        ),
        APIEx(
            description="选择数据类别，并筛选报告中的特定表格。",
            parameters={
                "category": "weekly_estimates",
                "table": "imports",
                "provider": "eia",
            },
        ),
    ],
)
async def petroleum_status_report(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """EIA 每周石油状况报告。"""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="ShortTermEnergyOutlook",
    examples=[
        APIEx(
            description="获取 EIA 的短期能源展望。",
            parameters={"provider": "eia"},
        ),
        APIEx(
            description="从 STEO 中选择特定的数据表。表 03d 是世界原油产量。",
            parameters={
                "table": "03d",
                "provider": "eia",
            },
        ),
    ],
)
async def short_term_energy_outlook(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """使用 EIA 的 STEO 模型进行每月短期（18 个月）预测。

    来源: www.eia.gov/steo/
    """
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="CommodityPsdData",
    examples=[
        APIEx(
            description="获取世界作物产量摘要表。",
            parameters={
                "provider": "government_us",
            },
        ),
        APIEx(
            description="从 PDS 报告中获取当前玉米世界贸易表。",
            parameters={
                "provider": "government_us",
                "report_id": "corn_world_trade",
            },
        ),
        APIEx(
            description="获取某一年全球咖啡的所有属性。",
            parameters={
                "provider": "government_us",
                "commodity": "coffee",
                "start_year": 2025,
                "end_year": 2025,
            },
        ),
        APIEx(
            description="比较巴西咖啡出口量与世界咖啡出口量（2010 年至今）。",
            parameters={
                "provider": "government_us",
                "commodity": "coffee",
                "country": "brazil",
                "attribute": "exports",
                "aggregate_regions": True,
                "start_year": 2010,
            },
        ),
        APIEx(
            description="获取美国自 2020 年以来的玉米历史产量。",
            parameters={
                "provider": "government_us",
                "commodity": "corn",
                "country": "united_states",
                "attribute": "production",
                "start_year": 2020,
            },
        ),
        APIEx(
            description="获取自 2020 年以来小麦期初和期末库存的地区总量。",
            parameters={
                "provider": "government_us",
                "commodity": "wheat",
                "country": "world",
                "attribute": "beginning_stocks,ending_stocks",
                "aggregate_regions": True,
                "start_year": 2020,
            },
        ),
    ],
)
async def psd_data(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """从 USDA FAS 生产、供应和分销 (PSD) 报告中获取数据表和历史时间序列。"""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="CommodityPsdReport",
    no_validate=True,
    widget_config={
        "name": "USDA FAS Commodity Production Supply & Distribution Reports",
        "description": "USDA 外国农业局发布的月度出版物。",
        "type": "pdf",
        "refetchInterval": False,
        "gridData": {
            "w": 20,
            "h": 30,
        },
        "category": "Commodity",
        "subCategory": "Agriculture",
        "source": ["USDA", "FAS"],
    },
    examples=[
        APIEx(
            parameters={
                "provider": "government_us",
                "commodity": "sugar",
                "year": 2022,
                "month": 5,
            }
        ),
        APIEx(
            description="获取 2023 年 3 月的咖啡 PSD 报告。",
            parameters={
                "provider": "government_us",
                "commodity": "coffee",
                "year": 2023,
                "month": 3,
            },
        ),
    ],
)
async def psd_report(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """农产品生产、供应和分销 PDF 报告（世界农业展望）。

    此命令仅返回 OBBject 响应的结果部分。
    它包含一个字典，其中 PDF 内容在“content”键下进行 base64 编码。
    """
    response = await OBBject.from_query(Query(**locals()))
    return response.model_dump().get("results", {})


@router.command(
    model="WeatherBulletin",
    no_validate=True,
    widget_config={"exclude": True},
    examples=[
        APIEx(
            description="获取当前年份的天气公报。",
            parameters={
                "provider": "government_us",
            },
        ),
        APIEx(
            description="获取 2023 年 5 月第 2 周的天气公报。",
            parameters={
                "provider": "government_us",
                "year": 2023,
                "month": 5,
                "week": 2,
            },
        ),
        PythonEx(
            description="获取与 1 年前进行比较的 URL，并将 base64 编码的 PDF 内容下载到内存中。",
            code=[
                "from datetime import datetime",
                "urls = []",
                "for year in [datetime.now().year, datetime.now().year - 1]:",
                "    urls.append(obb.commodity.weather_bulletins(year=year, month=5, week=2)[0]['value'])",
                "pdfs = obb.commodity.weather_bulletins_download(urls=urls)",
                "# PDFs are now in a list where each item has 'content' and 'data_format' keys",
            ],
        ),
    ],
)
async def weather_bulletins(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """获取当前和历史天气公报及其 PDF 链接。

    此命令仅返回 OBBject 响应的结果部分。
    它包含一个字典列表，其中每个字典都有 'label' 和 'value' 键。

    使用此端点以编程方式访问可用天气公报的列表。
    适用于 UI 中的下拉选择。
    """
    response = await OBBject.from_query(Query(**locals()))
    return response.model_dump().get("results", {})


@router.command(
    methods=["POST"],
    model="WeatherBulletinDownload",
    no_validate=True,
    widget_config={
        "name": "USDA Weather & Crop Bulletin",
        "description": "USDA 每周天气和作物公报。",
        "type": "multi_file_viewer",
        "refetchInterval": False,
        "gridData": {
            "w": 20,
            "h": 30,
        },
        "category": "Commodity",
        "subCategory": "Agriculture",
        "source": ["USDA", "WAOB"],
        "params": [
            {
                "paramName": "urls",
                "type": "endpoint",
                "optionsEndpoint": f"{api_prefix}/commodity/weather_bulletins",
                "optionsParams": {
                    "year": "$year",
                    "month": "$month",
                    "week": "$week",
                    "provider": "government_us",
                },
                "show": False,
                "multiSelect": True,
                "roles": ["fileSelector"],
            },
            {
                "paramName": "year",
                "type": "number",
                "label": "Year",
                "value": datetime.now().year,
                "options": [
                    {"value": year, "label": str(year)}
                    for year in sorted(
                        list(range(1974, datetime.now().year + 1)),
                        reverse=True,
                    )
                ],
            },
            {
                "paramName": "month",
                "type": "number",
                "label": "Month",
                "value": None,
                "options": [
                    {"value": i, "label": month}
                    for i, month in enumerate(
                        [
                            "January",
                            "February",
                            "March",
                            "April",
                            "May",
                            "June",
                            "July",
                            "August",
                            "September",
                            "October",
                            "November",
                            "December",
                        ],
                        start=1,
                    )
                ]
                + [{"value": None, "label": "All Months"}],
            },
            {
                "paramName": "week",
                "type": "number",
                "label": "Week",
                "value": None,
                "options": [{"value": week, "label": str(week)} for week in range(1, 6)]
                + [{"value": None, "label": "All Weeks"}],
            },
            {
                "paramName": "provider",
                "show": False,
                "value": "government_us",
                "type": "text",
                "options": [{"value": "government_us", "label": "government_us"}],
            },
        ],
    },
    examples=[
        APIEx(
            parameters={
                "provider": "government_us",
                "urls": [
                    "https://esmis.nal.usda.gov/sites/default/release-files/cj82k728n/9w033w568/x059f4232/wwcb0125.pdf"
                ],
            }
        ),
    ],
)
async def weather_bulletins_download(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """下载一份或多份天气公报文档。

    此命令仅返回 OBBject 响应的结果部分。
    它包含一个字典列表，其中文档的 base64 编码内容在 'content' 键下。
    """
    response = await OBBject.from_query(Query(**locals()))
    return response.model_dump().get("results", {})
