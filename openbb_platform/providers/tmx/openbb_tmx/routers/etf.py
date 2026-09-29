"""TMX ETF sub-router."""

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

from openbb_tmx import ETF_INSTALLED
from openbb_tmx.utils.choices import cell_group

router = Router(prefix="/etf", description="TMX exchange-traded fund data.")


if not ETF_INSTALLED:

    @router.command(
        model="TmxEtfSearch",
        widget_config=cell_group(
            "symbol", "The symbol a click on the search results selects."
        ),
        examples=[
            APIEx(
                description="Search the listed ETF universe.",
                parameters={"provider": "tmx"},
            )
        ],
    )
    async def search(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Search the TMX-listed ETF universe."""
        return await OBBject.from_query(OBBQuery(**locals()))

    @router.command(
        model="TmxEtfInfo",
        examples=[
            APIEx(
                description="Fund profile and reference data.",
                parameters={"symbol": "XIU", "provider": "tmx"},
            )
        ],
    )
    async def info(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Fund profile, fees, and reference data."""
        return await OBBject.from_query(OBBQuery(**locals()))

    @router.command(
        model="TmxEtfHoldings",
        examples=[
            APIEx(
                description="Fund holdings.",
                parameters={"symbol": "XIU", "provider": "tmx"},
            )
        ],
    )
    async def holdings(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Return the holdings of a TMX-listed fund."""
        return await OBBject.from_query(OBBQuery(**locals()))

    @router.command(
        model="TmxEtfSectors",
        examples=[
            APIEx(
                description="Sector weights.",
                parameters={"symbol": "XIU", "provider": "tmx"},
            )
        ],
    )
    async def sectors(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Sector exposure of a TMX-listed fund."""
        return await OBBject.from_query(OBBQuery(**locals()))

    @router.command(
        model="TmxEtfCountries",
        examples=[
            APIEx(
                description="Country weights.",
                parameters={"symbol": "XIU", "provider": "tmx"},
            )
        ],
    )
    async def countries(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Country exposure of a TMX-listed fund."""
        return await OBBject.from_query(OBBQuery(**locals()))

    @router.command(
        model="TmxEtfHistorical",
        widget_config={
            "name": "TMX Fund Historical Price",
            "description": "Fund prices, charted over the TMX quote feed.",
            "category": "Markets",
            "type": "advanced_charting",
            "endpoint": "api/v1/tmx/udf",
            "gridData": {"w": 40, "h": 20},
            "data": {"defaultSymbol": "XIU", "updateFrequency": 60000},
        },
        examples=[
            APIEx(
                description="Daily fund price history.",
                parameters={"symbol": "XIU", "provider": "tmx"},
            )
        ],
    )
    async def historical(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Historical prices for a TMX-listed fund."""
        return await OBBject.from_query(OBBQuery(**locals()))


async def fund_info_page(symbol: str = "XIU", theme: str = "dark"):
    """Serve the styled fund overview for the Workspace."""
    from fastapi.responses import HTMLResponse

    from openbb_tmx.utils.asset_info import asset_info_html

    return HTMLResponse(content=await asset_info_html(symbol, theme))


router.api_router.add_api_route(
    path="/fund_info/view",
    endpoint=fund_info_page,
    methods=["GET"],
    include_in_schema=True,
    openapi_extra={
        "widget_config": {
            "name": "TMX Fund Info",
            "description": "A styled overview of the fund - session, performance,"
            + " facts, classification, holdings, and weightings.",
            "type": "iframe",
            "category": "ETF",
            "subCategory": "Profile",
            "widgetId": "tmx_etf_fund_info_obb",
            "params": [
                {
                    "paramName": "symbol",
                    "label": "Symbol",
                    "value": "XIU",
                    "description": "The fund to describe.",
                },
                {"paramName": "theme", "show": False},
            ],
            "gridData": {"w": 20, "h": 20},
            "refetchInterval": False,
            "source": ["TMX"],
        }
    },
)
