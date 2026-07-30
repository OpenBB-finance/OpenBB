"""Federal Reserve Bank of Boston regional router."""

from openbb_core.app.model.command_context import CommandContext
from openbb_core.app.model.example import APIEx
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.provider_interface import (
    ExtraParams,
    ProviderChoices,
    StandardParams,
)
from openbb_core.app.query import Query
from openbb_core.app.router import Router

router = Router(prefix="", description="Federal Reserve Bank of Boston indicators.")


@router.command(
    model="FederalReserveBostonEconomicIndicators",
    examples=[
        APIEx(parameters={"provider": "federal_reserve"}),
        APIEx(
            description="Get every state and supersector employment series.",
            parameters={
                "indicator": "employment_by_supersector",
                "provider": "federal_reserve",
            },
        ),
    ],
    widget_config={
        "name": "Boston Fed New England Economic Indicators",
        "description": "New England Economic Indicators across labor, income, price,"
        " housing, and trade charts; every series and geography returned as a column.",
        "subCategory": "New England Indicators",
        "gridData": {"w": 40, "h": 20},
        "data": {
            "table": {
                "showAll": True,
                "columnsDefs": [
                    {
                        "field": "date",
                        "headerName": "Date",
                        "cellDataType": "date",
                        "pinned": "left",
                        "sort": "desc",
                    },
                ],
            }
        },
    },
)
async def economic_indicators(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get headline New England Economic Indicators from the Boston Fed."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="FederalReserveBostonPublications",
    examples=[
        APIEx(parameters={"provider": "federal_reserve"}),
        APIEx(
            description="Index from a start date.",
            parameters={"start_date": "2025-01-01", "provider": "federal_reserve"},
        ),
    ],
)
async def publications(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Index the Boston Fed New England Economic Conditions PDF archive."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="FederalReserveBostonPublicationSeries",
    examples=[APIEx(parameters={"provider": "federal_reserve"})],
    widget_config={
        "name": "Boston Fed Publication Series",
        "description": "The publication series supported by the Boston Fed"
        " publications catalog, with the document count in each.",
        "subCategory": "Publications & Reports",
        "gridData": {"w": 20, "h": 15},
        "data": {
            "table": {
                "showAll": True,
                "columnsDefs": [
                    {"field": "name", "headerName": "Series"},
                    {"field": "series", "headerName": "Slug"},
                    {"field": "count", "headerName": "Documents"},
                ],
            }
        },
    },
)
async def publication_series(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """List the supported Boston Fed publication series and their document counts."""
    return await OBBject.from_query(Query(**locals()))
