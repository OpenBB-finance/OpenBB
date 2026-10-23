"""FRED Economy sub-router."""

from typing import Annotated

from fastapi import Query
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
from openbb_core.app.service.system_service import SystemService

from openbb_fred import ECONOMY_INSTALLED
from openbb_fred.utils.query import USE_CACHE_DESCRIPTION

router = Router(prefix="/economy", description="FRED economic data.")

api_prefix = SystemService().system_settings.api_settings.prefix

PRESENTATION_PARAMS = [
    {
        "paramName": "release_id",
        "label": "Release",
        "description": "The economic release to present.",
        "type": "endpoint",
        "value": "9",
        "optionsEndpoint": f"{api_prefix}/fred/economy/release_choices",
        "style": {"popupWidth": 1000},
    },
    {
        "paramName": "element_id",
        "label": "Table",
        "description": "The table within the release.",
        "type": "endpoint",
        "value": "201241",
        "optionsEndpoint": f"{api_prefix}/fred/economy/element_choices",
        "optionsParams": {"release_id": "$release_id"},
        "style": {"popupWidth": 1000},
    },
    {
        "paramName": "frequency",
        "label": "Frequency",
        "description": "The interval the table is presented at.",
        "type": "endpoint",
        "optionsEndpoint": f"{api_prefix}/fred/economy/frequency_choices",
        "optionsParams": {"release_id": "$release_id", "element_id": "$element_id"},
    },
    {"paramName": "symbol", "show": False},
]

RELEASE_TABLE_PARAMS = [
    {
        "paramName": "release_id",
        "label": "Release",
        "description": "The economic release to read.",
        "type": "endpoint",
        "value": "52",
        "optionsEndpoint": f"{api_prefix}/fred/economy/release_choices",
    },
    {
        "paramName": "element_id",
        "label": "Table",
        "description": "The section or table within the release.",
        "type": "endpoint",
        "optionsEndpoint": f"{api_prefix}/fred/economy/element_choices",
        "optionsParams": {"release_id": "$release_id"},
    },
]


@router.api_router.get("/release_choices", include_in_schema=False)
async def release_choices() -> list:
    """Serve every release the tables endpoint can address."""
    from openbb_fred.utils.release_tables import list_releases

    return list_releases()


@router.command(
    methods=["GET"],
    widget_config={
        "name": "FRED Release Table",
        "description": "A published release table, in its own line order and"
        + " indentation, with the periods across the columns.",
        "category": "Economy",
        "subCategory": "Releases",
        "params": PRESENTATION_PARAMS,
        "gridData": {"w": 40, "h": 20},
        "refetchInterval": False,
        "data": {
            "table": {
                "showAll": True,
                "columnsDefs": [
                    {
                        "field": "series",
                        "headerName": "Series",
                        "cellDataType": "text",
                        "pinned": "left",
                        "minWidth": 380,
                    },
                    {
                        "field": "symbol",
                        "headerName": "Symbol",
                        "cellDataType": "text",
                        "width": 140,
                        "renderFn": "cellOnClick",
                        "renderFnParams": {
                            "actionType": "groupBy",
                            "groupBy": {"paramName": "symbol"},
                        },
                    },
                    {
                        "field": "units",
                        "headerName": "Units",
                        "cellDataType": "text",
                        "width": 170,
                    },
                    {
                        "field": "trend",
                        "headerName": "Trend",
                        "width": 170,
                        "sparkline": {
                            "type": "line",
                            "options": {
                                "stroke": "#2563eb",
                                "strokeWidth": 2,
                                "markers": {"enabled": False},
                                "pointsOfInterest": {
                                    "maximum": {
                                        "fill": "#22c55e",
                                        "stroke": "#16a34a",
                                        "size": 5,
                                    },
                                    "minimum": {
                                        "fill": "#ef4444",
                                        "stroke": "#dc2626",
                                        "size": 5,
                                    },
                                },
                                "customFormatter": "(params) => ({})",
                            },
                        },
                    },
                ],
            }
        },
    },
    examples=[
        APIEx(
            description="Advance retail sales by kind of business.",
            parameters={"release_id": "9", "element_id": "201241"},
        )
    ],
)
async def release_table(
    release_id: Annotated[
        str,
        Query(title="Release", description="The economic release to present."),
    ] = "9",
    element_id: Annotated[
        str | None,
        Query(
            title="Table",
            description="The table within the release. Without one, every"
            + " series the release publishes is listed.",
        ),
    ] = None,
    frequency: Annotated[
        str | None,
        Query(
            title="Frequency",
            description="The interval to present. A table reads at one"
            + " interval; without a choice the one it mostly publishes is used.",
        ),
    ] = None,
    limit: Annotated[
        int,
        Query(title="Periods", description="How many periods to present."),
    ] = 8,
    symbol: Annotated[
        str | None,
        Query(
            title="Symbol",
            description="The series the table groups on. Carried for the"
            + " grouping, not read.",
        ),
    ] = None,
    use_cache: Annotated[
        bool,
        Query(title="Use Cache", description=USE_CACHE_DESCRIPTION),
    ] = True,
) -> list[dict]:
    """Read a published release table, with the periods across the columns."""
    from openbb_core.app.service.user_service import UserService

    from openbb_fred.utils.release_tables import build_release_table, resolve_element

    credentials = UserService().default_user_settings.credentials.model_dump(
        mode="json"
    )

    return await build_release_table(
        release_id,
        resolve_element(release_id, element_id),
        frequency or "",
        limit,
        credentials.get("fred_api_key"),
        use_cache=use_cache,
    )


@router.api_router.get("/frequency_choices", include_in_schema=False)
async def frequency_choices(
    release_id: str = "10", element_id: str | None = None
) -> list:
    """Serve the publication frequencies present in one table."""
    from openbb_core.app.service.user_service import UserService

    from openbb_fred.utils.release_tables import list_frequencies, resolve_element

    credentials = UserService().default_user_settings.credentials.model_dump(
        mode="json"
    )

    return await list_frequencies(
        release_id, resolve_element(release_id, element_id), credentials
    )


@router.api_router.get("/element_choices", include_in_schema=False)
async def element_choices(release_id: str = "52") -> list:
    """Serve the sections and tables published under one release."""
    from openbb_fred.utils.release_tables import list_elements

    return list_elements(release_id)


if not ECONOMY_INSTALLED:

    @router.command(
        model="FredBalanceOfPayments",
        examples=[APIEx(parameters={"provider": "fred"})],
    )
    async def balance_of_payments(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Balance of Payments Reports."""
        return await OBBject.from_query(OBBQuery(**locals()))

    @router.command(
        model="FredConsumerPriceIndex",
        examples=[APIEx(parameters={"country": "united_states", "provider": "fred"})],
    )
    async def cpi(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Consumer Price Index (CPI)."""
        return await OBBject.from_query(OBBQuery(**locals()))

    @router.command(
        model="FredEconomicCalendar",
        examples=[APIEx(parameters={"provider": "fred"})],
    )
    async def calendar(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Economic release calendar."""
        return await OBBject.from_query(OBBQuery(**locals()))

    @router.command(
        model="FredPersonalConsumptionExpenditures",
        examples=[APIEx(parameters={"provider": "fred"})],
    )
    async def pce(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Personal Consumption Expenditures (PCE)."""
        return await OBBject.from_query(OBBQuery(**locals()))

    @router.command(
        model="FredRetailPrices",
        examples=[APIEx(parameters={"provider": "fred"})],
    )
    async def retail_prices(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Retail prices for common items."""
        return await OBBject.from_query(OBBQuery(**locals()))

    @router.command(
        model="FredSearch",
        widget_config={
            "params": [{"paramName": "symbol", "show": False}],
            "data": {
                "table": {
                    "columnsDefs": [
                        {
                            "field": "series_id",
                            "renderFn": "cellOnClick",
                            "renderFnParams": {
                                "actionType": "groupBy",
                                "groupBy": {"paramName": "symbol"},
                            },
                        },
                    ]
                }
            },
        },
        examples=[APIEx(parameters={"query": "gdp", "provider": "fred"})],
    )
    async def fred_search(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Search for FRED series or economic releases by ID or string."""
        return await OBBject.from_query(OBBQuery(**locals()))

    @router.command(
        model="FredSeries",
        examples=[APIEx(parameters={"symbol": "GDP", "provider": "fred"})],
    )
    async def fred_series(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Get data by series ID from FRED."""
        return await OBBject.from_query(OBBQuery(**locals()))

    @router.command(
        model="FredReleaseTable",
        widget_config={"exclude": True},
        examples=[APIEx(parameters={"release_id": "50", "provider": "fred"})],
    )
    async def fred_release_table(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Get economic release data by ID and/or element from FRED."""
        return await OBBject.from_query(OBBQuery(**locals()))

    @router.command(
        model="FredRegional",
        examples=[APIEx(parameters={"symbol": "NYUR", "provider": "fred"})],
    )
    async def fred_regional(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Query the Geo Federal Reserve Economic Data (GeoFRED) Regional Data API."""
        return await OBBject.from_query(OBBQuery(**locals()))
