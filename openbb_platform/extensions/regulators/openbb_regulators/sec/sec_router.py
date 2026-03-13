# pylint: disable=W0613:unused-argument
"""SEC Router."""

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
            "description": "Get a list of all the documents associated with a filing, and their direct URLs.",
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
    """Download the index headers, and cover page if available, for any SEC filing."""
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
            "description": "Open a HTM/HTML document from the SEC website.",
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
    """Download a raw HTML object from the SEC website."""
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
    """Map a ticker symbol to a CIK number."""
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
    """Search SEC-regulated institutions by name and return a list of results with CIK numbers."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="SchemaFiles",
    examples=[
        APIEx(parameters={"provider": "sec"}),
        PythonEx(
            description="Explore XBRL taxonomies progressively.",
            code=[
                "# List all available taxonomy families",
                "obb.regulators.sec.schema_files(provider='sec')",
                "# List components for US GAAP (latest year)",
                "obb.regulators.sec.schema_files(taxonomy='us-gaap', provider='sec')",
                "# List presentation components for US GAAP 2024",
                "obb.regulators.sec.schema_files(taxonomy='us-gaap', year=2024, provider='sec')",
                "# Get the Statement of Income presentation structure",
                "obb.regulators.sec.schema_files(taxonomy='us-gaap', year=2024, component='soi', provider='sec')",
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
    """Explore SEC and FASB XBRL taxonomy schemas, labels, and presentation structures.

    - No parameters: list all available taxonomy families.
    - taxonomy only: get all parsed structures for the most recent year.
    - taxonomy + year: get all parsed structures for a specific year.
    - taxonomy + component: get one component's structure using the most recent year.
    - taxonomy + year + component: get one component's parsed structure.
    """
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
    """Map a CIK number to a ticker symbol, leading 0s can be omitted or included."""
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
    """Get the RSS feed that provides links to litigation releases concerning civil lawsuits brought by the Commission in federal court."""  # noqa: E501 pylint: disable=C0301
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
    """Search for Industry Titles, Reporting Office, and SIC Codes. An empty query string returns all results."""
    return await OBBject.from_query(Query(**locals()))
