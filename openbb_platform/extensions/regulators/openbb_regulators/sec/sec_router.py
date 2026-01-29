# pylint: disable=W0613:unused-argument
"""SEC 路由器。"""

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

router = Router(prefix="/sec")


@router.command(
    model="SecFiling",
    examples=[
        APIEx(
            parameters={
                "url": "https://www.sec.gov/Archives/edgar/data/317540/000119312524076556/d645509ddef14a.htm",
                "provider": "sec",
            }
        )
    ],
    openapi_extra={
        "widget_config": {
            "description": "获取与申报相关的所有文档及其直接 URL 的列表。",
            "gridData": {
                "w": 30,
                "h": 10,
            },
            "refetchInterval": False,
            "data": {"dataKey": "results.document_urls"},
        }
    },
)
async def filing_headers(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """下载任何 SEC 申报文件的索引标头和封面（如果可用）。"""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="SecHtmFile",
    examples=[
        APIEx(
            parameters={
                "url": "https://www.sec.gov/Archives/edgar/data/1723690/000119312525030074/d866336dex991.htm",
                "provider": "sec",
            }
        )
    ],
    openapi_extra={
        "widget_config": {
            "name": "Open HTML",
            "description": "打开来自 SEC 网站的 HTM/HTML 文档。",
            "gridData": {
                "w": 40,
                "h": 25,
            },
            "refetchInterval": False,
            "type": "markdown",
            "data": {
                "dataKey": "results.content",
            },
        }
    },
)
async def htm_file(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """从 SEC 网站下载原始 HTML 对象。"""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="CikMap",
    examples=[APIEx(parameters={"symbol": "MSFT", "provider": "sec"})],
)
async def cik_map(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """将股票代码映射到 CIK 编号。"""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="InstitutionsSearch",
    examples=[
        APIEx(parameters={"provider": "sec"}),
        APIEx(parameters={"query": "blackstone real estate", "provider": "sec"}),
    ],
)
async def institutions_search(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """按名称搜索受 SEC 监管的机构，并返回包含 CIK 编号的结果列表。"""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="SchemaFiles",
    examples=[
        APIEx(parameters={"provider": "sec"}),
        PythonEx(
            description="获取架构文件列表。",
            code=[
                "data = obb.regulators.sec.schema_files().results",
                "data.files[0]",
                "'https://xbrl.fasb.org/us-gaap/'",
                "# The directory structure can be navigated by constructing a URL from the 'results' list.",
                "url = data.files[0]+data.files[-1]",
                "# The URL base will always be the 0 position in the list, feed  the URL back in as a parameter.",
                "obb.regulators.sec.schema_files(url=url).results.files",
                "['https://xbrl.fasb.org/us-gaap/2024/'",
                "'USGAAP2024FileList.xml'",
                "'dis/'",
                "'dqcrules/'",
                "'ebp/'",
                "'elts/'",
                "'entire/'",
                "'meta/'",
                "'stm/'",
                "'us-gaap-2024.zip']",
            ],
        ),
    ],
)
async def schema_files(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """用于按年份导航 SEC XML 架构文件目录的工具。"""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="SymbolMap",
    examples=[APIEx(parameters={"query": "0000789019", "provider": "sec"})],
)
async def symbol_map(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """将 CIK 编号映射到股票代码，可以省略或包含前导 0。"""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="RssLitigation",
    examples=[APIEx(parameters={"provider": "sec"})],
)
async def rss_litigation(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """获取 RSS 源，提供有关委员会在联邦法院提起的民事诉讼的诉公发布链接。"""  # noqa: E501 pylint: disable=C0301
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="SicSearch",
    examples=[
        APIEx(parameters={"provider": "sec"}),
        APIEx(parameters={"query": "real estate investment trusts", "provider": "sec"}),
    ],
)
async def sic_search(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """搜索行业标题、报告办公室和 SIC 代码。空查询字符串返回所有结果。"""
    return await OBBject.from_query(Query(**locals()))
