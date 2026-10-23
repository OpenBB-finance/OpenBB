"""Nasdaq Equity sub-router."""

from typing import Annotated

from fastapi import Query as FastAPIQuery
from openbb_core.app.model.command_context import CommandContext
from openbb_core.app.model.example import APIEx
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.provider_interface import (
    ExtraParams,
    ProviderChoices,
    StandardParams,
)
from openbb_core.app.query import Query as OBBQuery
from openbb_core.app.router import Router

from openbb_nasdaq import EQUITY_INSTALLED
from openbb_nasdaq.utils.constants import (
    DOCUMENT_CHOICES_ENDPOINT,
    FILING_YEARS_ENDPOINT,
    FORM_GROUPS,
    GHOST_SYMBOL_PARAM,
    SYMBOL_CHOICES_ENDPOINT,
)

router = Router(prefix="/equity", description="Nasdaq equity data.")


@router.command(
    methods=["GET"],
    widget_config={"exclude": True},
    examples=[
        APIEx(description="Get the Nasdaq-traded symbol directory.", parameters={})
    ],
)
async def symbol_choices() -> list[dict]:
    """``[{label, value}]`` of every operating company Nasdaq lists."""
    from openbb_nasdaq.utils.helpers import get_symbol_choices

    return await get_symbol_choices()


@router.command(
    methods=["GET"],
    widget_config={"exclude": True},
    examples=[
        APIEx(
            description="Get the filing documents available for a symbol.",
            parameters={"symbol": "AAPL", "year": 2026, "form_group": "8k"},
        )
    ],
)
async def document_choices(
    symbol: Annotated[
        str | None, FastAPIQuery(description="The ticker symbol.")
    ] = None,
    year: Annotated[
        int | None, FastAPIQuery(description="The calendar year of the filings.")
    ] = None,
    form_group: Annotated[
        FORM_GROUPS, FastAPIQuery(description="The SEC form group.")
    ] = "8k",
) -> list[dict]:
    """``[{label, value}]`` of filing PDFs for a symbol, year, and form group."""
    from openbb_nasdaq.utils.helpers import get_document_choices

    return await get_document_choices(symbol, year, form_group)


@router.command(
    methods=["POST"],
    widget_config={
        "type": "multi_file_viewer",
        "name": "Nasdaq SEC Filings",
        "description": "View SEC filings by company.",
        "category": "Equity",
        "subCategory": "Filings",
        "refetchInterval": False,
        "gridData": {"w": 40, "h": 30},
        "params": [
            {
                "paramName": "symbol",
                "label": "Symbol",
                "description": "Ticker symbol for the company. Foreign (dual-listed)"
                + " companies may not be required to file with the SEC.",
                "type": "endpoint",
                "value": "AAPL",
                "optionsEndpoint": SYMBOL_CHOICES_ENDPOINT,
                "style": {"popupWidth": 850},
            },
            {
                "paramName": "document_url",
                "label": "Document URL",
                "description": "Select the document to open.",
                "type": "endpoint",
                "optionsEndpoint": DOCUMENT_CHOICES_ENDPOINT,
                "optionsParams": {
                    "symbol": "$symbol",
                    "year": "$year",
                    "form_group": "$form_group",
                },
                "show": False,
                "roles": ["fileSelector"],
                "multiSelect": True,
            },
            {
                "paramName": "year",
                "label": "Calendar Year",
                "description": "Calendar year for the filings.",
                "type": "number",
                "optionsEndpoint": FILING_YEARS_ENDPOINT,
            },
            {
                "paramName": "form_group",
                "label": "Form Group",
                "description": "Form group for the filings.",
                "value": "8k",
                "type": "text",
                "options": [
                    {"label": "Annual", "value": "annual"},
                    {"label": "Quarterly", "value": "quarterly"},
                    {"label": "Proxy", "value": "proxy"},
                    {"label": "Insider", "value": "insider"},
                    {"label": "8-K", "value": "8k"},
                    {"label": "Registration", "value": "registration"},
                    {"label": "Comment", "value": "comment"},
                ],
            },
        ],
    },
)
async def filings_viewer(params: dict) -> list:
    """Open the selected SEC filing PDFs for the OpenBB Workspace file viewer."""
    from openbb_nasdaq.utils.helpers import open_filing_document

    documents: list = []

    for document_url in params.get("document_url") or []:
        if isinstance(document_url, str) and document_url.startswith("http"):
            document = await open_filing_document(document_url)

            if document:
                documents.append(document)

    return documents


@router.command(
    methods=["GET"],
    widget_config={"exclude": True},
    examples=[APIEx(description="Get the selectable filing years.", parameters={})],
)
async def filing_years() -> list[dict]:
    """``[{label, value}]`` of the calendar years Nasdaq indexes filings for."""
    from datetime import datetime

    current = datetime.now().year

    return [{"label": str(year), "value": year} for year in range(current, 1993, -1)]


if not EQUITY_INSTALLED:

    @router.command(
        model="NasdaqEquitySearch",
        examples=[
            APIEx(
                description="Search the Nasdaq-traded symbol directory.",
                parameters={"query": "apple", "provider": "nasdaq"},
            )
        ],
    )
    async def search(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Search the Nasdaq symbol directory."""
        return await OBBject.from_query(OBBQuery(**locals()))

    @router.command(
        model="NasdaqEquityScreener",
        widget_config={"params": [GHOST_SYMBOL_PARAM]},
        examples=[
            APIEx(
                description="Screen the full Nasdaq-listed universe.",
                parameters={"exchange": "nasdaq", "provider": "nasdaq"},
            )
        ],
    )
    async def screener(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Screen US-listed equities by exchange, sector, region, and market cap."""
        return await OBBject.from_query(OBBQuery(**locals()))

    @router.command(
        model="NasdaqEquityQuote",
        examples=[
            APIEx(
                description="Delayed quote with the Nasdaq summary block.",
                parameters={"symbol": "AAPL", "provider": "nasdaq"},
            )
        ],
    )
    async def quote(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Delayed Nasdaq quotes, with the sector, market cap, and dividend summary."""
        return await OBBject.from_query(OBBQuery(**locals()))

    @router.command(
        model="NasdaqEquityInfo",
        examples=[
            APIEx(
                description="The company profile.",
                parameters={"symbol": "AAPL", "provider": "nasdaq"},
            )
        ],
    )
    async def profile(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Company profile, sector, industry, and business description."""
        return await OBBject.from_query(OBBQuery(**locals()))

    @router.command(
        model="NasdaqEquityHistorical",
        examples=[
            APIEx(
                description="Daily historical prices.",
                parameters={"symbol": "AAPL", "provider": "nasdaq"},
            )
        ],
    )
    async def historical(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Daily OHLCV history for Nasdaq-quoted equities."""
        return await OBBject.from_query(OBBQuery(**locals()))

    @router.command(
        model="NasdaqCompanyFilings",
        examples=[
            APIEx(
                description="SEC filings indexed by Nasdaq.",
                parameters={"symbol": "AAPL", "provider": "nasdaq"},
            )
        ],
    )
    async def filings(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """SEC filings for a company, with links to the filed PDFs."""
        return await OBBject.from_query(OBBQuery(**locals()))
