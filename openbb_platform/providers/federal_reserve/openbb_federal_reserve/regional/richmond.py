"""Federal Reserve Bank of Richmond regional router."""

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

router = Router(prefix="", description="Federal Reserve Bank of Richmond indicators.")


@router.command(
    model="FederalReserveRichmondManufacturing",
    examples=[APIEx(parameters={"provider": "federal_reserve"})],
    widget_config={
        "name": "Richmond Fed Manufacturing Survey",
        "subCategory": "Business Surveys",
        "description": "Fifth District Survey of Manufacturing Activity diffusion"
        " indexes, by indicator and horizon.",
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
                        "field": "adjustment",
                        "headerName": "Adjustment",
                    },
                    {
                        "field": "horizon",
                        "headerName": "Horizon",
                    },
                ],
            }
        },
    },
)
async def manufacturing_survey(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the Richmond Fed Fifth District Survey of Manufacturing Activity."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="FederalReserveRichmondServiceSector",
    examples=[APIEx(parameters={"provider": "federal_reserve"})],
    widget_config={
        "name": "Richmond Fed Service Sector Survey",
        "subCategory": "Business Surveys",
        "description": "Fifth District Survey of Service Sector Activity diffusion"
        " indexes, by indicator and horizon.",
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
                        "field": "adjustment",
                        "headerName": "Adjustment",
                    },
                    {
                        "field": "horizon",
                        "headerName": "Horizon",
                    },
                ],
            }
        },
    },
)
async def service_sector_survey(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the Richmond Fed Fifth District Survey of Service Sector Activity."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="FederalReserveRichmondStateSurvey",
    examples=[
        APIEx(parameters={"provider": "federal_reserve"}),
        APIEx(
            description="Get the Carolinas survey.",
            parameters={"state": "carolinas", "provider": "federal_reserve"},
        ),
    ],
    widget_config={
        "name": "Richmond Fed State Business Survey",
        "subCategory": "Business Surveys",
        "description": "Fifth District per-state combined business survey diffusion"
        " indexes, by indicator and horizon.",
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
                        "field": "adjustment",
                        "headerName": "Adjustment",
                    },
                    {
                        "field": "horizon",
                        "headerName": "Horizon",
                    },
                ],
            }
        },
    },
)
async def state_survey(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get a Richmond Fed Fifth District state business survey."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="FederalReserveRichmondCFO",
    examples=[
        APIEx(parameters={"provider": "federal_reserve"}),
        APIEx(
            description="Get the legacy pre-Q2-2020 Duke CFO Survey series.",
            parameters={
                "table": "legacy_through_q1_2020",
                "provider": "federal_reserve",
            },
        ),
    ],
    widget_config={
        "name": "Richmond Fed CFO Survey",
        "subCategory": "Business Surveys",
        "description": "Quarterly CFO Survey optimism, expectations, and credit"
        " series, by measure and breakdown.",
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
                        "field": "category",
                        "headerName": "Category",
                    },
                ],
            }
        },
    },
)
async def cfo_survey(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the Richmond Fed CFO Survey optimism series."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="FederalReserveRichmondNonEmployment",
    examples=[APIEx(parameters={"provider": "federal_reserve"})],
    widget_config={
        "name": "Richmond Fed Non-Employment Index (NEI)",
        "subCategory": "Labor & Recession",
        "description": "Monthly NEI and NEI+PTER labor-market underutilization,"
        " with the official U-5, U-6, and U-3 rates.",
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
                        "field": "nei",
                        "headerName": "NEI",
                        "cellDataType": "number",
                        "formatterFn": "percent",
                    },
                    {
                        "field": "nei_plus",
                        "headerName": "NEI+PTER",
                        "cellDataType": "number",
                        "formatterFn": "percent",
                    },
                    {
                        "field": "u_5",
                        "headerName": "U-5",
                        "cellDataType": "number",
                        "formatterFn": "percent",
                    },
                    {
                        "field": "u_6",
                        "headerName": "U-6",
                        "cellDataType": "number",
                        "formatterFn": "percent",
                    },
                    {
                        "field": "unemployment_rate",
                        "headerName": "U-3 Unemployment Rate",
                        "cellDataType": "number",
                        "formatterFn": "percent",
                    },
                ],
            }
        },
    },
)
async def non_employment_index(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the Richmond Fed Non-Employment Index (NEI)."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="FederalReserveRichmondRecessionIndicator",
    examples=[APIEx(parameters={"provider": "federal_reserve"})],
    widget_config={
        "name": "Richmond Fed SOS Recession Indicator",
        "subCategory": "Labor & Recession",
        "description": "Weekly Sum of Stalls (SOS) recession indicator, with its"
        " constant 0.2 recession-signal threshold.",
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
                        "field": "sos",
                        "headerName": "Sum of Stalls",
                        "cellDataType": "number",
                        "formatterFn": "none",
                    },
                    {
                        "field": "recession_threshold",
                        "headerName": "Recession Threshold",
                        "cellDataType": "number",
                        "formatterFn": "none",
                    },
                ],
            }
        },
    },
)
async def recession_indicator(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the Richmond Fed SOS (Sum of Stalls) Recession Indicator."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="FederalReserveRichmondPublications",
    examples=[
        APIEx(parameters={"provider": "federal_reserve"}),
        APIEx(
            description="Index only the manufacturing survey releases.",
            parameters={"survey": "manufacturing", "provider": "federal_reserve"},
        ),
    ],
)
async def survey_releases(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Index the Richmond Fed manufacturing and service-sector survey PDF archives."""
    return await OBBject.from_query(Query(**locals()))
