# pylint: disable=W0613:unused-argument
"""SEC Router."""

from openbb_core.app.model.command_context import CommandContext
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
    model="CikMap",
    exclude_auto_examples=True,
    examples=[
        'obb.regulators.sec.cik_map(symbol="MSFT").results.cik',
        "    0000789019",
    ],
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
    exclude_auto_examples=True,
    examples=[
        'obb.regulators.sec.institutions_search(query="blackstone real estate").to_df()'
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
    exclude_auto_examples=True,
    examples=[
        "data = obb.regulators.sec.schema_files()",
        "data.files[0]",
        "    https://xbrl.fasb.org/us-gaap/",
        "#### The directory structure can be navigated by constructing a URL from the 'results' list. ####",
        "url = data.files[0]+data.files[-1]",
        "#### The URL base will always be the 0 position in the list, feed  the URL back in as a parameter. ####",
        "obb.regulators.sec.schema_files(url=url).results.files",
        "    ['https://xbrl.fasb.org/us-gaap/2024/'",
        "    'USGAAP2024FileList.xml'",
        "    'dis/'",
        "    'dqcrules/'",
        "    'ebp/'",
        "    'elts/'",
        "    'entire/'",
        "    'meta/'",
        "    'stm/'",
        "    'us-gaap-2024.zip']",
    ],
)
async def schema_files(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """A tool for navigating the directory of SEC XML schema files by year."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="SymbolMap",
    exclude_auto_examples=True,
    examples=['obb.regulators.sec.symbol_map("0000789019").results.symbol', "    MSFT"],
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
    exclude_auto_examples=True,
    examples=['obb.regulators.sec.rss_litigation().to_dict("records")[0]'],
)
async def rss_litigation(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """The RSS feed provides links to litigation releases concerning civil lawsuits brought by the Commission in federal court."""  # noqa: E501 pylint: disable=C0301
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="SicSearch",
    exclude_auto_examples=True,
    examples=[
        'obb.regulators.sec.sic_search("real estate investment trusts").results',
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
