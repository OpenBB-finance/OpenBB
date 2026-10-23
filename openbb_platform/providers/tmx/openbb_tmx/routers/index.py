"""TMX Index sub-router."""

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
from pydantic import BaseModel, Field

from openbb_tmx import INDEX_INSTALLED
from openbb_tmx.models.index_documents import TmxIndexDocumentsData
from openbb_tmx.utils.choices import api_prefix, cell_group

router = Router(prefix="/index", description="TMX index data.")


class DocumentRequest(BaseModel):
    """The selection the file viewer posts."""

    url: str | list[str] = Field(
        default_factory=list, description="The documents the viewer has selected."
    )


if not INDEX_INSTALLED:

    @router.command(
        model="TmxAvailableIndices",
        widget_config=cell_group("symbol", "The index a click on the list selects."),
        examples=[
            APIEx(
                description="Every index TMX publishes.",
                parameters={"provider": "tmx"},
            )
        ],
    )
    async def available(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Return the S&P/TSX index universe."""
        return await OBBject.from_query(OBBQuery(**locals()))

    @router.command(
        model="TmxIndexInfo",
        examples=[
            APIEx(
                description="Index profile, documents, and key data.",
                parameters={"symbol": "^TSX", "provider": "tmx"},
            )
        ],
    )
    async def info(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Profile of an index, with links to its factsheet and methodology."""
        return await OBBject.from_query(OBBQuery(**locals()))

    @router.command(
        model="TmxIndexHistorical",
        widget_config={
            "name": "TMX Index Historical Levels",
            "description": "Daily levels of an S&P/TSX index.",
            "category": "Markets",
            "subCategory": "Index",
            "type": "advanced_charting",
            "endpoint": "api/v1/tmx/udf",
            "gridData": {"w": 40, "h": 20},
            "data": {"defaultSymbol": "^TSX", "updateFrequency": 60000},
            "source": ["TMX"],
        },
        examples=[
            APIEx(
                description="Daily levels of an index.",
                parameters={"symbol": "^TSX", "provider": "tmx"},
            )
        ],
    )
    async def historical(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Daily open, high, low, close, and volume for an index."""
        return await OBBject.from_query(OBBQuery(**locals()))

    @router.command(
        model="TmxIndexConstituents",
        examples=[
            APIEx(
                description="Index constituents and weights.",
                parameters={"symbol": "^TSX", "provider": "tmx"},
            )
        ],
    )
    async def constituents(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Constituents of an index, with weights and key data."""
        return await OBBject.from_query(OBBQuery(**locals()))

    @router.command(
        model="TmxIndexSectors",
        examples=[
            APIEx(
                description="Index sector weights.",
                parameters={"symbol": "^TSX", "provider": "tmx"},
            )
        ],
    )
    async def sectors(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Sector weights of an index."""
        return await OBBject.from_query(OBBQuery(**locals()))

    @router.command(
        model="TmxIndexSnapshots",
        widget_config={
            "name": "TMX Index Snapshots",
            "description": "Levels, performance, and key data for a region's indices.",
            "source": ["TMX"],
            "params": [
                {
                    "paramName": "region",
                    "value": "ca",
                    "options": [
                        {"label": "Canada", "value": "ca"},
                        {"label": "United States", "value": "us"},
                    ],
                }
            ],
        },
        examples=[
            APIEx(
                description="Index levels and performance.",
                parameters={"region": "ca", "provider": "tmx"},
            )
        ],
    )
    async def snapshots(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Levels and performance for an entire index region."""
        return await OBBject.from_query(OBBQuery(**locals()))

    @router.command(
        model="TmxIndexDocuments",
        widget_config={"exclude": True},
        examples=[
            APIEx(
                description="Factsheets and methodologies published for an index.",
                parameters={"symbol": "^TSX", "provider": "tmx"},
            ),
            APIEx(
                description="Every document TMX publishes.",
                parameters={"provider": "tmx"},
            ),
        ],
    )
    async def documents(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Factsheet and methodology documents published for an index."""
        return await OBBject.from_query(OBBQuery(**locals()))


async def _documents(
    symbol: str | None = None, document_type: str = "all"
) -> list[TmxIndexDocumentsData]:
    """Read the published documents, or nothing when the file is unreachable."""
    from openbb_tmx.models.index_documents import (
        TmxIndexDocumentsData,
        TmxIndexDocumentsFetcher,
    )

    try:
        found = await TmxIndexDocumentsFetcher.fetch_data(
            {"symbol": symbol, "document_type": document_type}, {}
        )
    except Exception:  # noqa: BLE001
        return []

    return [d for d in found if isinstance(d, TmxIndexDocumentsData)]


async def document_choices(
    symbol: str | None = None, document_type: str = "all"
) -> list:
    """Return the documents the file selector offers."""
    return [
        {"label": d.name, "value": d.url}
        for d in await _documents(symbol, document_type)
    ]


def _document_filename(url: str, catalog: dict) -> str:
    """Name a document from the catalogue, or from the URL it was read at."""
    if url in catalog:
        return f"{catalog[url]}.pdf"

    return url.rsplit("/", 1)[-1].split("?", maxsplit=1)[0] or "document.pdf"


async def document_view(params: DocumentRequest) -> list:
    """Serve every selected document to the viewer."""
    from openbb_tmx.utils.documents import as_viewer_files

    urls = params.url if isinstance(params.url, list) else [params.url]
    catalog = {d.url: d.name for d in await _documents()}

    return await as_viewer_files(
        [(url, _document_filename(url, catalog)) for url in urls if url]
    )


router.api_router.add_api_route(
    path="/document_choices",
    endpoint=document_choices,
    methods=["GET"],
    include_in_schema=False,
)

router.api_router.add_api_route(
    path="/document_view",
    endpoint=document_view,
    methods=["POST"],
    include_in_schema=True,
    openapi_extra={
        "widget_config": {
            "name": "TMX Index Documents",
            "description": "Factsheets and methodologies published for the S&P/TSX"
            + " index family.",
            "type": "multi_file_viewer",
            "category": "Index",
            "subCategory": "Documents",
            "widgetId": "tmx_index_documents_obb",
            "params": [
                {
                    "paramName": "symbol",
                    "label": "Index",
                    "description": "The index to read documents for.",
                    "type": "endpoint",
                    "value": "^TSX",
                    "optionsEndpoint": f"{api_prefix()}/tmx/index/symbol_choices",
                },
                {
                    "paramName": "document_type",
                    "label": "Document",
                    "description": "The kind of document to offer.",
                    "type": "text",
                    "value": "all",
                    "options": [
                        {"label": "All", "value": "all"},
                        {"label": "Factsheet", "value": "factsheet"},
                        {"label": "Methodology", "value": "methodology"},
                    ],
                },
                {
                    "paramName": "url",
                    "type": "endpoint",
                    "optionsEndpoint": f"{api_prefix()}/tmx/index/document_choices",
                    "optionsParams": {
                        "symbol": "$symbol",
                        "document_type": "$document_type",
                    },
                    "show": False,
                    "multiSelect": True,
                    "roles": ["fileSelector"],
                },
            ],
            "gridData": {"w": 20, "h": 28},
            "refetchInterval": False,
            "source": ["TMX"],
        }
    },
)


async def symbol_choices() -> list:
    """Return every index the file selector can read documents for."""
    indices = {d.symbol: d.index_name or d.symbol for d in await _documents()}

    return [
        {"label": f"{name} ({symbol})", "value": symbol}
        for symbol, name in indices.items()
    ]


router.api_router.add_api_route(
    path="/symbol_choices",
    endpoint=symbol_choices,
    methods=["GET"],
    include_in_schema=False,
)
