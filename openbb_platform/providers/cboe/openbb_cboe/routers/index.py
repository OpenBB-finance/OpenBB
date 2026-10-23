"""Cboe Index sub-router."""

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

from openbb_cboe import INDEX_INSTALLED
from openbb_cboe.utils.constants import (
    DOCUMENT_CHOICES_ENDPOINT,
    INDEX_CHOICES_ENDPOINT,
)

router = Router(prefix="/index", description="Cboe index data.")


@router.command(
    methods=["GET"],
    widget_config={"exclude": True},
    examples=[
        APIEx(
            description="Get symbol choices from the Cboe index directory.",
            parameters={},
        )
    ],
)
async def symbol_choices(
    use_cache: Annotated[
        bool,
        FastAPIQuery(
            description="When True, the index directory is cached for 24 hours."
        ),
    ] = True,
) -> list[dict[str, str]]:
    """``[{label, value}]`` of every index in the Cboe index directory."""
    from openbb_cboe.utils.helpers import get_index_choices

    return await get_index_choices(use_cache=use_cache)


@router.command(
    methods=["GET"],
    widget_config={"exclude": True},
    examples=[
        APIEx(
            description="Get the Cboe European proprietary index choices.",
            parameters={},
        )
    ],
)
async def constituent_choices(
    use_cache: Annotated[
        bool,
        FastAPIQuery(
            description="When True, the index directory is cached for 24 hours."
        ),
    ] = True,
) -> list[dict[str, str]]:
    """``[{label, value}]`` of the Cboe European proprietary indices with constituents."""
    from openbb_cboe.utils.helpers import get_eu_index_choices

    return await get_eu_index_choices(use_cache=use_cache)


@router.command(
    model="CboeIndexDocuments",
    widget_config={"exclude": True},
    examples=[
        APIEx(
            description="The full Cboe index documents catalog.",
            parameters={"provider": "cboe"},
        ),
        APIEx(
            description="Documents that apply to a single index.",
            parameters={"symbol": "X2C", "provider": "cboe"},
        ),
        APIEx(
            description="Only the methodology documents.",
            parameters={"category": "Methodology", "provider": "cboe"},
        ),
    ],
)
async def documents(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the factsheets, methodologies, and governance documents Cboe publishes."""
    return await OBBject.from_query(OBBQuery(**locals()))


@router.command(
    methods=["GET"],
    widget_config={"exclude": True},
    examples=[
        APIEx(
            description="Get the documents available for an index.",
            parameters={"symbol": "BXM"},
        )
    ],
)
async def document_choices(
    symbol: Annotated[
        str | None,
        FastAPIQuery(description="Restrict the choices to one index symbol."),
    ] = None,
) -> list[dict]:
    """``[{label, value}]`` of index documents, where the value is the PDF URL."""
    from openbb_cboe.utils.helpers import get_document_choices

    return await get_document_choices(symbol)


@router.command(
    methods=["POST"],
    widget_config={
        "type": "multi_file_viewer",
        "name": "Cboe Index Documents",
        "description": "Factsheets, methodologies, and governance documents.",
        "category": "Index",
        "subCategory": "Reference",
        "source": ["Cboe"],
        "refetchInterval": False,
        "gridData": {"w": 40, "h": 30},
        "params": [
            {
                "paramName": "document_url",
                "label": "Document",
                "description": "Select the documents to open.",
                "type": "endpoint",
                "optionsEndpoint": DOCUMENT_CHOICES_ENDPOINT,
                "show": False,
                "roles": ["fileSelector"],
                "multiSelect": True,
                "style": {"popupWidth": 850},
            },
        ],
    },
)
async def documents_viewer(params: dict) -> list:
    """Open the selected Cboe index documents for the Workspace file viewer."""
    from openbb_cboe.utils.helpers import is_cboe_document_url, open_index_document

    documents_out: list = []

    for document_url in params.get("document_url") or []:
        if is_cboe_document_url(document_url):
            document = await open_index_document(document_url)

            if document:
                documents_out.append(document)

    return documents_out


_SYMBOL_CLICK_COLUMN = {
    "field": "symbol",
    "headerName": "Symbol",
    "cellDataType": "text",
    "pinned": "left",
    "renderFn": "cellOnClick",
    "renderFnParams": {
        "actionType": "groupBy",
        "groupBy": {"paramName": "symbol"},
    },
}


def _click_widget(name: str, height: int) -> dict:
    """Build a table widget whose symbol column drives the shared parameter."""
    return {
        "name": name,
        "source": ["Cboe"],
        "gridData": {"w": 40, "h": height},
        "params": [
            {
                "paramName": "symbol",
                "label": "Symbol",
                "type": "endpoint",
                "optionsEndpoint": INDEX_CHOICES_ENDPOINT,
                "value": "VIX",
                "multiSelect": False,
                "show": False,
            }
        ],
        "data": {"table": {"columnsDefs": [_SYMBOL_CLICK_COLUMN]}},
    }


_INDEX_HISTORY_COLUMNS = [
    {
        "field": "date",
        "headerName": "Date",
        "pinned": "left",
        "chartDataType": "category",
    },
    {
        "field": "close",
        "headerName": "Close",
        "cellDataType": "number",
        "chartDataType": "series",
    },
    {
        "field": "open",
        "headerName": "Open",
        "cellDataType": "number",
        "chartDataType": "excluded",
    },
    {
        "field": "high",
        "headerName": "High",
        "cellDataType": "number",
        "chartDataType": "excluded",
    },
    {
        "field": "low",
        "headerName": "Low",
        "cellDataType": "number",
        "chartDataType": "excluded",
    },
]


if not INDEX_INSTALLED:

    @router.command(
        model="CboeAvailableIndices",
        examples=[
            APIEx(
                description="All indices published by Cboe.",
                parameters={"provider": "cboe"},
            )
        ],
    )
    async def available(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """All indices available from Cboe, US and European."""
        return await OBBject.from_query(OBBQuery(**locals()))

    @router.command(
        model="CboeIndexSearch",
        widget_config=_click_widget("Index Search", 12),
        examples=[
            APIEx(
                description="Search the Cboe index directory.",
                parameters={"query": "uk", "provider": "cboe"},
            ),
            APIEx(
                description="Restrict the search to ticker symbols.",
                parameters={"query": "BUK", "is_symbol": True, "provider": "cboe"},
            ),
        ],
    )
    async def search(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Filter the Cboe index directory for rows containing the query."""
        return await OBBject.from_query(OBBQuery(**locals()))

    @router.command(
        model="CboeIndexSnapshots",
        widget_config=_click_widget("Index Snapshots", 14),
        examples=[
            APIEx(
                description="Current levels for all US indices.",
                parameters={"region": "us", "provider": "cboe"},
            ),
            APIEx(
                description="Current levels for all European indices.",
                parameters={"region": "eu", "provider": "cboe"},
            ),
        ],
    )
    async def snapshots(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Get current levels for all Cboe indices, grouped by region."""
        return await OBBject.from_query(OBBQuery(**locals()))

    @router.command(
        model="CboeIndexConstituents",
        examples=[
            APIEx(
                description="Current constituents of a Cboe European index.",
                parameters={"symbol": "BUK100P", "provider": "cboe"},
            )
        ],
    )
    async def constituents(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Get current trading day prices for the constituents of a Cboe European index."""
        return await OBBject.from_query(OBBQuery(**locals()))

    @router.command(
        model="CboeIndexHistorical",
        widget_config={
            "name": "Index History",
            "params": [{"paramName": "symbol", "multiSelect": False, "value": "VIX"}],
            "description": "Daily or intraday closing levels for a Cboe index.",
            "source": ["Cboe"],
            "gridData": {"w": 40, "h": 14},
            "data": {
                "table": {
                    "chartView": {"enabled": True, "chartType": "line"},
                    "columnsDefs": _INDEX_HISTORY_COLUMNS,
                }
            },
        },
        examples=[
            APIEx(
                description="Daily historical index levels.",
                parameters={"symbol": "AAVE10RP", "provider": "cboe"},
            ),
            APIEx(
                description="One-minute levels for the most recent trading day.",
                parameters={"symbol": "BUK100P", "interval": "1m", "provider": "cboe"},
            ),
        ],
    )
    async def historical(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Historical Cboe index levels, daily or one-minute."""
        return await OBBject.from_query(OBBQuery(**locals()))
