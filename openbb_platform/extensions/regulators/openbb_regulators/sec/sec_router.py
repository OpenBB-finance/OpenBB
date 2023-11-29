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
from pydantic import BaseModel

router = Router(prefix="/sec")


@router.command(model="CikMap")
async def cik_map(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Get the CIK number corresponding to a ticker symbol."""
    return await OBBject.from_query(Query(**locals()))


@router.command(model="InstitutionsSearch")
async def institutions_search(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Look up institutions regulated by the SEC."""
    return await OBBject.from_query(Query(**locals()))


@router.command(model="SchemaFiles")
async def schema_files(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Get lists of SEC XML schema files by year."""
    return await OBBject.from_query(Query(**locals()))


@router.command(model="SymbolMap")
async def symbol_map(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Get the ticker symbol corresponding to a company's CIK."""
    return await OBBject.from_query(Query(**locals()))


@router.command(model="RssLitigation")
async def rss_litigation(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """The RSS feed provides links to litigation releases concerning civil lawsuits brought by the Commission in federal court."""  # noqa: E501
    return await OBBject.from_query(Query(**locals()))


@router.command(model="SicSearch")
async def sic_search(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Fuzzy search for Industry Titles, Reporting Office, and SIC Codes."""
    return await OBBject.from_query(Query(**locals()))
