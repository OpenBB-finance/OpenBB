"""Federal Reserve Bank of St. Louis regional router."""

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

router = Router(
    prefix="", description="Federal Reserve Bank of Saint Louis indicators."
)


@router.command(
    model="FederalReserveStLouisFredMd",
    examples=[
        APIEx(parameters={"provider": "federal_reserve"}),
        APIEx(
            description="Return only selected series from the panel.",
            parameters={"series": "INDPRO,UNRATE", "provider": "federal_reserve"},
        ),
    ],
    widget_config={
        "name": "FRED-MD Monthly Macro Panel, St. Louis Fed",
        "description": "The McCracken-Ng monthly database of 120+ U.S."
        " macroeconomic series as a wide panel, one column per series.",
        "subCategory": "Macro Data Panels",
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
async def fred_md(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the FRED-MD monthly macroeconomic database as a tidy long panel."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="FederalReserveStLouisFredQd",
    examples=[
        APIEx(parameters={"provider": "federal_reserve"}),
        APIEx(
            description="Return only selected series from the panel.",
            parameters={"series": "GDPC1,PCECC96", "provider": "federal_reserve"},
        ),
    ],
    widget_config={
        "name": "FRED-QD Quarterly Macro Panel, St. Louis Fed",
        "description": "The McCracken-Ng quarterly database of 200+ U.S."
        " macroeconomic series as a wide panel, one column per series.",
        "subCategory": "Macro Data Panels",
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
async def fred_qd(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the FRED-QD quarterly macroeconomic database as a tidy long panel."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="FederalReserveStLouisNationalIndex",
    examples=[
        APIEx(
            description="The St. Louis Fed Financial Stress Index (weekly).",
            parameters={
                "index": "financial_stress_index",
                "provider": "federal_reserve",
            },
        ),
        APIEx(
            description="The Price Pressures Measure (monthly).",
            parameters={"index": "price_pressures", "provider": "federal_reserve"},
        ),
        APIEx(
            description="The Economic News Index real-GDP nowcast (quarterly).",
            parameters={"index": "economic_news_index", "provider": "federal_reserve"},
        ),
    ],
    widget_config={
        "name": "St. Louis Fed National Indexes",
        "description": "A selected St. Louis Fed national index: the Financial"
        " Stress Index, the Price Pressures Measure, or the Economic News nowcast.",
        "subCategory": "National Indexes",
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
                    {
                        "field": "index",
                        "headerName": "Index",
                    },
                    {
                        "field": "value",
                        "headerName": "Value",
                        "cellDataType": "number",
                        "formatterFn": "none",
                    },
                ],
            }
        },
    },
)
async def national_index(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get a St. Louis Fed national index: financial stress, price pressures, or nowcast."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="FederalReserveStLouisPublications",
    examples=[
        APIEx(parameters={"provider": "federal_reserve"}),
        APIEx(
            description="Filter the catalog to a date range.",
            parameters={
                "start_date": "2024-01-01",
                "end_date": "2024-12-31",
                "provider": "federal_reserve",
            },
        ),
    ],
)
async def publications(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Index the St. Louis Fed Economic Synopses PDF archive on FRASER."""
    return await OBBject.from_query(Query(**locals()))
