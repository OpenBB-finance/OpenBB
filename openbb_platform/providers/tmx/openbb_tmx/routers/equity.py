"""TMX Equity sub-router."""

import logging

from openbb_core.app.model.command_context import CommandContext
from openbb_core.app.model.example import APIEx, PythonEx
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.provider_interface import (
    ExtraParams,
    ProviderChoices,
    StandardParams,
)
from openbb_core.app.query import Query as OBBQuery
from openbb_core.app.router import Router
from pydantic import BaseModel, Field

from openbb_tmx import EQUITY_INSTALLED
from openbb_tmx.utils.choices import api_prefix, cell_group

router = Router(prefix="/equity", description="TMX equity data.")

_logger = logging.getLogger(__name__)

INVALID_CONFIG = "The configuration is not valid JSON."
NO_MATCHES = "No instruments matched the screen."
SCREEN_FAILED = "The screen could not be run."
PRESET_NOT_SAVED = "The preset could not be saved."


class FilingRequest(BaseModel):
    """The selection the filings viewer posts."""

    url: str | list[str] = Field(
        default_factory=list, description="The filings the viewer has selected."
    )


if not EQUITY_INSTALLED:

    @router.command(
        model="TmxEquitySearch",
        widget_config=cell_group(
            "symbol", "The symbol a click on the search results selects."
        ),
        examples=[
            APIEx(
                description="Search every market in the symbology.",
                parameters={"query": "bank", "provider": "tmx"},
            )
        ],
    )
    async def search(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Search the instrument symbology across markets and asset classes."""
        return await OBBject.from_query(OBBQuery(**locals()))

    @router.command(
        model="TmxEquityScreener",
        examples=[
            APIEx(
                description="Screen the listed universe by venue, type, and size.",
                parameters={"exchange": "TSX", "provider": "tmx"},
            )
        ],
    )
    async def screener(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Screen the listed universe by venue, instrument type, and size."""
        return await OBBject.from_query(OBBQuery(**locals()))

    @router.command(
        model="TmxEquityQuote",
        examples=[
            APIEx(
                description="Delayed quote for a listing.",
                parameters={"symbol": "AC", "provider": "tmx"},
            )
        ],
    )
    async def quote(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Delayed quote, for any symbol the feed addresses."""
        return await OBBject.from_query(OBBQuery(**locals()))

    @router.command(
        model="TmxEquityInfo",
        examples=[
            APIEx(
                description="Company profile and reference data.",
                parameters={"symbol": "AC", "provider": "tmx"},
            )
        ],
    )
    async def profile(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Company profile, sector, and reference data."""
        return await OBBject.from_query(OBBQuery(**locals()))

    @router.command(
        model="TmxEquityHistorical",
        widget_config={
            "name": "TMX Historical Price",
            "description": "Historical prices, charted over the TMX quote feed.",
            "category": "Markets",
            "type": "advanced_charting",
            "endpoint": "api/v1/tmx/udf",
            "gridData": {"w": 40, "h": 20},
            "data": {"defaultSymbol": "AC", "updateFrequency": 60000},
        },
        examples=[
            APIEx(
                description="Daily price history.",
                parameters={"symbol": "AC", "provider": "tmx"},
            )
        ],
    )
    async def historical(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Historical prices for any listed instrument."""
        return await OBBject.from_query(OBBQuery(**locals()))

    @router.command(
        model="TmxCompanyFilings",
        widget_config={"exclude": True},
        examples=[
            APIEx(
                description="SEDAR filings with document links.",
                parameters={"symbol": "AC", "provider": "tmx"},
            )
        ],
    )
    async def filings(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Filings published to SEDAR, with links to the PDFs."""
        return await OBBject.from_query(OBBQuery(**locals()))

    @router.command(
        model="TmxEquityGainers",
        examples=[
            APIEx(
                description="The most active and best performing listings.",
                parameters={"provider": "tmx"},
            )
        ],
    )
    async def gainers(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Curated stock lists of gainers and most actives."""
        return await OBBject.from_query(OBBQuery(**locals()))


@router.command(
    model="TmxRankings",
    widget_config={
        "name": "TMX Annual Rankings",
        "description": "The TSX 30 and TSX Venture 50 published rankings.",
        "source": ["TMX"],
        "gridData": {"w": 40, "h": 15},
    },
    examples=[
        APIEx(
            description="The Toronto Stock Exchange's top thirty performers.",
            parameters={"ranking": "tsx30", "provider": "tmx"},
        ),
        APIEx(
            description="The TSX Venture Exchange's top fifty performers.",
            parameters={"ranking": "venture50", "provider": "tmx"},
        ),
    ],
)
async def rankings(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Read the TSX 30 and TSX Venture 50 annual rankings."""
    return await OBBject.from_query(OBBQuery(**locals()))


@router.command(
    model="SymbolReference",
    widget_config={"exclude": True},
    examples=[
        APIEx(
            description="Resolve symbols to their canonical form and venue.",
            parameters={"symbol": "AC,IBM:US,$USDCAD", "provider": "tmx"},
        )
    ],
)
async def symbol_reference(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Resolve symbols to their canonical form, validity, and listing venue."""
    return await OBBject.from_query(OBBQuery(**locals()))


async def _filings(
    symbol: str,
    start_date: str | None = None,
    end_date: str | None = None,
) -> list:
    """Read the filings published for a symbol, or nothing when unreachable."""
    from openbb_tmx.models.company_filings import (
        TmxCompanyFilingsData,
        TmxCompanyFilingsFetcher,
    )

    try:
        found = await TmxCompanyFilingsFetcher.fetch_data(
            {"symbol": symbol, "start_date": start_date, "end_date": end_date}, {}
        )
    except Exception:  # noqa: BLE001
        return []

    return [f.model_dump() for f in found if isinstance(f, TmxCompanyFilingsData)]


async def filing_choices(
    symbol: str = "AC",
    start_date: str | None = None,
    end_date: str | None = None,
) -> list:
    """Return the filings the file selector offers, newest first.

    Parameters
    ----------
    symbol : str
        The symbol to list filings for.
    start_date : str | None
        The first filing date to offer. Defaults to sixteen weeks back.
    end_date : str | None
        The last filing date to offer. Defaults to today.
    """
    choices: list = []

    for filing in await _filings(symbol, start_date, end_date):
        url = filing.get("report_url")

        if not url:
            continue

        report = filing.get("report_type") or "Filing"
        description = filing.get("description")
        label = f"{filing.get('filing_date')} - {report}"

        if description and description != report:
            label = f"{label} - {description}"

        choices.append({"label": label, "value": url})

    return choices


def _filing_filename(url: str) -> str:
    """Name a filing from the symbol, date, and form the download URL carries."""
    from urllib.parse import parse_qs, urlsplit

    query = parse_qs(urlsplit(url).query)
    parts = [
        (query.get("symbol") or [""])[0].split(":")[0],
        (query.get("dateFiled") or [""])[0],
        (query.get("formDescription") or [""])[0],
    ]
    name = " ".join(part for part in parts if part)

    return f"{name}.pdf" if name else "filing.pdf"


async def filings_view(params: FilingRequest) -> list:
    """Serve every selected filing to the viewer."""
    from openbb_tmx.utils.documents import as_viewer_files

    urls = params.url if isinstance(params.url, list) else [params.url]

    return await as_viewer_files([(url, _filing_filename(url)) for url in urls if url])


router.api_router.add_api_route(
    path="/filing_choices",
    endpoint=filing_choices,
    methods=["GET"],
    include_in_schema=False,
)

router.api_router.add_api_route(
    path="/filings_view",
    endpoint=filings_view,
    methods=["POST"],
    include_in_schema=True,
    openapi_extra={
        "widget_config": {
            "name": "TMX Company Filings",
            "description": "Documents filed to SEDAR, read as PDFs.",
            "type": "multi_file_viewer",
            "category": "Equity",
            "subCategory": "Filings",
            "widgetId": "tmx_equity_filings_viewer_obb",
            "params": [
                {
                    "paramName": "symbol",
                    "label": "Symbol",
                    "description": "The symbol to read filings for.",
                    "value": "AC",
                },
                {
                    "paramName": "start_date",
                    "label": "Start Date",
                    "description": "The first filing date to offer.",
                    "type": "date",
                },
                {
                    "paramName": "end_date",
                    "label": "End Date",
                    "description": "The last filing date to offer.",
                    "type": "date",
                },
                {
                    "paramName": "url",
                    "type": "endpoint",
                    "optionsEndpoint": f"{api_prefix()}/tmx/equity/filing_choices",
                    "optionsParams": {
                        "symbol": "$symbol",
                        "start_date": "$start_date",
                        "end_date": "$end_date",
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


@router.api_router.get("/screener_choices", include_in_schema=False)
async def screener_choices(
    field: str = "sector",
    parent: str | None = None,
) -> list:
    """Serve the screener's filter vocabulary, narrowed by its parent."""
    from openbb_tmx.utils.choices import screener_options

    return screener_options(field, parent)


def _gui_available() -> bool:
    """Report whether a desktop display can host a native window."""
    import os
    import sys

    if sys.platform in ("darwin", "win32"):
        return True

    return bool(os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY"))


@router.command(
    methods=["POST"],
    widget_config={"exclude": True},
    examples=[
        PythonEx(
            description="Open the screener builder in a native window.",
            code=["obb.tmx.equity.screener_builder()"],
        ),
    ],
)
async def screener_builder(theme: str = "dark") -> OBBject:
    """Open the interactive TMX screener builder."""
    theme = "light" if str(theme).lower() == "light" else "dark"

    if not _gui_available():
        return OBBject(
            results={
                "message": "No desktop display available. Render the builder through"
                + " the GET /tmx/equity/screener_builder/view iframe endpoint.",
                "endpoint": f"/tmx/equity/screener_builder/view?theme={theme}",
            }
        )

    import asyncio

    from openbb_tmx.utils.screener_native import launch_screener_builder

    handle = await asyncio.get_running_loop().run_in_executor(
        None, launch_screener_builder, theme
    )

    return OBBject(results=handle)


async def screener_builder_page(theme: str = "dark"):
    """Serve the interactive screener-builder iframe page."""
    from fastapi.responses import HTMLResponse

    from openbb_tmx.utils.screener_iframe import build_screener_builder_html

    return HTMLResponse(
        content=build_screener_builder_html("light" if theme == "light" else "dark")
    )


async def screener_builder_catalog(country: str = "CA"):
    """Serve the filter catalog the builder renders."""
    from fastapi.responses import JSONResponse

    from openbb_tmx.utils.screener_catalog import build_screener_catalog

    return JSONResponse(content=build_screener_catalog(country))


async def screener_builder_run(config: str = "", limit: int = 100):
    """Run the screen for a builder configuration and return rows and columns."""
    import json

    from fastapi.responses import JSONResponse
    from openbb_core.app.model.abstract.error import OpenBBError
    from openbb_core.provider.utils.errors import EmptyDataError

    from openbb_tmx.models.equity_screener import (
        TmxEquityScreenerData,
        TmxEquityScreenerFetcher,
    )
    from openbb_tmx.utils.screener_catalog import query_from_config
    from openbb_tmx.utils.screener_iframe import columns_for, prune_empty_columns

    try:
        parsed = json.loads(config) if config else {}
    except (TypeError, ValueError):
        return JSONResponse(
            content={"error": INVALID_CONFIG, "rows": []},
            status_code=400,
        )

    if not isinstance(parsed, dict):
        return JSONResponse(content={"rows": [], "columns": []})

    params = query_from_config(parsed)
    params["limit"] = max(int(limit or 100), 1)

    try:
        results = await TmxEquityScreenerFetcher.fetch_data(params, {})
    except EmptyDataError:
        return JSONResponse(content={"error": NO_MATCHES, "rows": [], "columns": []})
    except (OpenBBError, ValueError):
        _logger.exception(SCREEN_FAILED)

        return JSONResponse(content={"error": SCREEN_FAILED, "rows": [], "columns": []})

    rows = [
        row.model_dump(mode="json", exclude_none=True)
        for row in results
        if isinstance(row, TmxEquityScreenerData)
    ]

    columns = columns_for(str(parsed.get("asset_type") or "Equity"))

    return JSONResponse(
        content={"rows": rows, "columns": prune_empty_columns(rows, columns)}
    )


async def screener_builder_presets():
    """List the saved screener configurations."""
    from fastapi.responses import JSONResponse

    from openbb_tmx.utils.screener_presets import list_presets

    return JSONResponse(content={"presets": list_presets()})


async def screener_builder_preset_load(name: str = ""):
    """Load one saved configuration."""
    from fastapi.responses import JSONResponse

    from openbb_tmx.utils.screener_presets import load_preset

    try:
        return JSONResponse(content={"config": load_preset(name)})
    except FileNotFoundError:
        return JSONResponse(content={"error": "Preset not found."}, status_code=404)


async def screener_builder_preset_save(name: str = "", config: str = ""):
    """Save the configuration under a name."""
    import json

    from fastapi.responses import JSONResponse

    from openbb_tmx.utils.screener_presets import save_preset

    try:
        parsed = json.loads(config) if config else {}
    except (TypeError, ValueError):
        return JSONResponse(content={"error": INVALID_CONFIG}, status_code=400)

    try:
        return JSONResponse(content={"presets": save_preset(name, parsed)})
    except (TypeError, ValueError, OSError):
        _logger.exception(PRESET_NOT_SAVED)

        return JSONResponse(content={"error": PRESET_NOT_SAVED}, status_code=400)


async def screener_builder_preset_delete(name: str = ""):
    """Delete one saved configuration."""
    from fastapi.responses import JSONResponse

    from openbb_tmx.utils.screener_presets import delete_preset

    return JSONResponse(content={"presets": delete_preset(name)})


for _preset_path, _preset_endpoint, _preset_method in (
    ("/screener_builder/presets", screener_builder_presets, "GET"),
    ("/screener_builder/presets/load", screener_builder_preset_load, "GET"),
    ("/screener_builder/presets/save", screener_builder_preset_save, "POST"),
    ("/screener_builder/presets/delete", screener_builder_preset_delete, "POST"),
):
    router.api_router.add_api_route(
        path=_preset_path,
        endpoint=_preset_endpoint,
        methods=[_preset_method],
        include_in_schema=False,
    )


router.api_router.add_api_route(
    path="/screener_builder/catalog",
    endpoint=screener_builder_catalog,
    methods=["GET"],
    include_in_schema=False,
)

router.api_router.add_api_route(
    path="/screener_builder/run",
    endpoint=screener_builder_run,
    methods=["GET"],
    include_in_schema=False,
)

router.api_router.add_api_route(
    path="/screener_builder/view",
    endpoint=screener_builder_page,
    methods=["GET"],
    include_in_schema=True,
    openapi_extra={
        "widget_config": {
            "name": "TMX Screener Builder",
            "description": "Build a screen across every published TMX filter,"
            + " then run it against the listed universe.",
            "type": "iframe",
            "category": "Equity",
            "subCategory": "Screener",
            "widgetId": "tmx_equity_screener_builder_obb",
            "params": [
                {
                    "paramName": "config",
                    "label": "Screener Config",
                    "value": "",
                    "description": "The configuration the builder emits.",
                    "show": False,
                },
                {"paramName": "theme", "show": False},
            ],
            "gridData": {"w": 40, "h": 20},
            "refetchInterval": False,
            "source": ["TMX"],
        }
    },
)


async def asset_info_page(symbol: str = "AC", theme: str = "dark"):
    """Serve the styled asset overview for the Workspace."""
    from fastapi.responses import HTMLResponse

    from openbb_tmx.utils.asset_info import asset_info_html

    return HTMLResponse(content=await asset_info_html(symbol, theme))


router.api_router.add_api_route(
    path="/asset_info/view",
    endpoint=asset_info_page,
    methods=["GET"],
    include_in_schema=True,
    openapi_extra={
        "widget_config": {
            "name": "TMX Asset Info",
            "description": "A styled overview of the symbol - session, performance,"
            + " valuation, analysts, ownership, calendar, and, for a fund, its"
            + " facts, holdings, and weightings.",
            "type": "iframe",
            "category": "Equity",
            "subCategory": "Profile",
            "widgetId": "tmx_equity_asset_info_obb",
            "params": [
                {
                    "paramName": "symbol",
                    "label": "Symbol",
                    "value": "AC",
                    "description": "The symbol to describe.",
                },
                {"paramName": "theme", "show": False},
            ],
            "gridData": {"w": 20, "h": 20},
            "refetchInterval": False,
            "source": ["TMX"],
        }
    },
)
