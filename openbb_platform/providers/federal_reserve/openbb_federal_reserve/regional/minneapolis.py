"""Federal Reserve Bank of Minneapolis regional router."""

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
    prefix="", description="Federal Reserve Bank of Minneapolis indicators."
)


@router.command(
    model="FederalReserveMinneapolisBusinessConditions",
    examples=[APIEx(parameters={"provider": "federal_reserve"})],
    widget_config={
        "name": "Minneapolis Fed Ninth District Business Conditions Survey",
        "description": "Monthly diffusion indexes from the Ninth District business"
        " conditions survey, each the net percentage of respondents reporting an"
        " increase over the prior three months.",
        "subCategory": "Business Conditions",
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
                        "field": "is_flash",
                        "headerName": "Is Flash",
                        "cellDataType": "boolean",
                    },
                    {
                        "field": "benefits",
                        "headerName": "Benefits",
                        "cellDataType": "number",
                        "formatterFn": "percent",
                    },
                    {
                        "field": "input_prices",
                        "headerName": "Input Prices",
                        "cellDataType": "number",
                        "formatterFn": "percent",
                    },
                    {
                        "field": "sales_prices",
                        "headerName": "Sales Prices",
                        "cellDataType": "number",
                        "formatterFn": "percent",
                    },
                    {
                        "field": "wages",
                        "headerName": "Wages",
                        "cellDataType": "number",
                        "formatterFn": "percent",
                    },
                    {
                        "field": "investment",
                        "headerName": "Investment",
                        "cellDataType": "number",
                        "formatterFn": "percent",
                    },
                    {
                        "field": "headcount",
                        "headerName": "Headcount",
                        "cellDataType": "number",
                        "formatterFn": "percent",
                    },
                    {
                        "field": "hiring",
                        "headerName": "Hiring Difficulty",
                        "cellDataType": "number",
                        "formatterFn": "percent",
                    },
                    {
                        "field": "inventories",
                        "headerName": "Inventories",
                        "cellDataType": "number",
                        "formatterFn": "percent",
                    },
                    {
                        "field": "profits",
                        "headerName": "Profits",
                        "cellDataType": "number",
                        "formatterFn": "percent",
                    },
                    {
                        "field": "sales",
                        "headerName": "Sales",
                        "cellDataType": "number",
                        "formatterFn": "percent",
                    },
                ],
            }
        },
    },
)
async def business_conditions(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the Minneapolis Fed Business Conditions Survey diffusion indexes."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="FederalReserveMinneapolisEmployment",
    examples=[APIEx(parameters={"provider": "federal_reserve"})],
    widget_config={
        "name": "Minneapolis Fed Ninth District Regional Employment",
        "description": "Monthly total nonfarm employment indexed to 100 at the series"
        " start for each Ninth District state and the United States.",
        "subCategory": "Labor Market",
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
                        "field": "MN",
                        "headerName": "Minnesota",
                        "cellDataType": "number",
                        "formatterFn": "none",
                    },
                    {
                        "field": "MT",
                        "headerName": "Montana",
                        "cellDataType": "number",
                        "formatterFn": "none",
                    },
                    {
                        "field": "ND",
                        "headerName": "North Dakota",
                        "cellDataType": "number",
                        "formatterFn": "none",
                    },
                    {
                        "field": "SD",
                        "headerName": "South Dakota",
                        "cellDataType": "number",
                        "formatterFn": "none",
                    },
                    {
                        "field": "WI",
                        "headerName": "Wisconsin",
                        "cellDataType": "number",
                        "formatterFn": "none",
                    },
                    {
                        "field": "US",
                        "headerName": "United States",
                        "cellDataType": "number",
                        "formatterFn": "none",
                    },
                ],
            }
        },
    },
)
async def regional_employment(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get Ninth District regional employment indexes."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="FederalReserveMinneapolisUnemployment",
    examples=[APIEx(parameters={"provider": "federal_reserve"})],
    widget_config={
        "name": "Minneapolis Fed Ninth District Unemployment Rate",
        "description": "The monthly unemployment rate, in percent, for each Ninth"
        " District state and the United States.",
        "subCategory": "Labor Market",
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
                        "field": "MN",
                        "headerName": "Minnesota",
                        "cellDataType": "number",
                        "formatterFn": "percent",
                    },
                    {
                        "field": "MT",
                        "headerName": "Montana",
                        "cellDataType": "number",
                        "formatterFn": "percent",
                    },
                    {
                        "field": "ND",
                        "headerName": "North Dakota",
                        "cellDataType": "number",
                        "formatterFn": "percent",
                    },
                    {
                        "field": "SD",
                        "headerName": "South Dakota",
                        "cellDataType": "number",
                        "formatterFn": "percent",
                    },
                    {
                        "field": "WI",
                        "headerName": "Wisconsin",
                        "cellDataType": "number",
                        "formatterFn": "percent",
                    },
                    {
                        "field": "US",
                        "headerName": "United States",
                        "cellDataType": "number",
                        "formatterFn": "percent",
                    },
                ],
            }
        },
    },
)
async def regional_unemployment(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get Ninth District regional unemployment rates."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="FederalReserveMinneapolisLaborForce",
    examples=[APIEx(parameters={"provider": "federal_reserve"})],
    widget_config={
        "name": "Minneapolis Fed Ninth District Labor Force Participation",
        "description": "The monthly labor force participation rate, in percent, for"
        " each Ninth District state and the United States.",
        "subCategory": "Labor Market",
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
                        "field": "MN",
                        "headerName": "Minnesota",
                        "cellDataType": "number",
                        "formatterFn": "percent",
                    },
                    {
                        "field": "MT",
                        "headerName": "Montana",
                        "cellDataType": "number",
                        "formatterFn": "percent",
                    },
                    {
                        "field": "ND",
                        "headerName": "North Dakota",
                        "cellDataType": "number",
                        "formatterFn": "percent",
                    },
                    {
                        "field": "SD",
                        "headerName": "South Dakota",
                        "cellDataType": "number",
                        "formatterFn": "percent",
                    },
                    {
                        "field": "WI",
                        "headerName": "Wisconsin",
                        "cellDataType": "number",
                        "formatterFn": "percent",
                    },
                    {
                        "field": "US",
                        "headerName": "United States",
                        "cellDataType": "number",
                        "formatterFn": "percent",
                    },
                ],
            }
        },
    },
)
async def labor_force_participation(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get Ninth District labor force participation rates."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="FederalReserveMinneapolisQuitsRate",
    examples=[APIEx(parameters={"provider": "federal_reserve"})],
    widget_config={
        "name": "Minneapolis Fed Ninth District Quits Rate",
        "description": "The monthly quits rate, in percent, for each Ninth District"
        " state and the United States, smoothed as a trailing three-month average.",
        "subCategory": "Labor Market",
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
                        "field": "MN",
                        "headerName": "Minnesota",
                        "cellDataType": "number",
                        "formatterFn": "percent",
                    },
                    {
                        "field": "MT",
                        "headerName": "Montana",
                        "cellDataType": "number",
                        "formatterFn": "percent",
                    },
                    {
                        "field": "ND",
                        "headerName": "North Dakota",
                        "cellDataType": "number",
                        "formatterFn": "percent",
                    },
                    {
                        "field": "SD",
                        "headerName": "South Dakota",
                        "cellDataType": "number",
                        "formatterFn": "percent",
                    },
                    {
                        "field": "WI",
                        "headerName": "Wisconsin",
                        "cellDataType": "number",
                        "formatterFn": "percent",
                    },
                    {
                        "field": "US",
                        "headerName": "United States",
                        "cellDataType": "number",
                        "formatterFn": "percent",
                    },
                ],
            }
        },
    },
)
async def quits_rate(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get Ninth District quits rates."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="FederalReserveMinneapolisGdp",
    examples=[APIEx(parameters={"provider": "federal_reserve"})],
    widget_config={
        "name": "Minneapolis Fed Ninth District Regional Real GDP",
        "description": "Quarterly inflation-adjusted gross domestic product indexed to"
        " 100 at the series start for each Ninth District state and the United States.",
        "subCategory": "Output & Prices",
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
                        "field": "MN",
                        "headerName": "Minnesota",
                        "cellDataType": "number",
                        "formatterFn": "none",
                    },
                    {
                        "field": "MT",
                        "headerName": "Montana",
                        "cellDataType": "number",
                        "formatterFn": "none",
                    },
                    {
                        "field": "ND",
                        "headerName": "North Dakota",
                        "cellDataType": "number",
                        "formatterFn": "none",
                    },
                    {
                        "field": "SD",
                        "headerName": "South Dakota",
                        "cellDataType": "number",
                        "formatterFn": "none",
                    },
                    {
                        "field": "WI",
                        "headerName": "Wisconsin",
                        "cellDataType": "number",
                        "formatterFn": "none",
                    },
                    {
                        "field": "US",
                        "headerName": "United States",
                        "cellDataType": "number",
                        "formatterFn": "none",
                    },
                ],
            }
        },
    },
)
async def regional_gdp(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get Ninth District regional real GDP indexes."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="FederalReserveMinneapolisCpi",
    examples=[APIEx(parameters={"provider": "federal_reserve"})],
    widget_config={
        "name": "Minneapolis Fed Ninth District Regional CPI Inflation",
        "description": "Monthly year-over-year CPI inflation, in percent, for the"
        " United States and the Census divisions that overlap the Ninth District, by"
        " headline and core measure.",
        "subCategory": "Output & Prices",
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
                        "field": "CPI-U US",
                        "headerName": "CPI-U US",
                        "cellDataType": "number",
                        "formatterFn": "percent",
                    },
                    {
                        "field": "CPI-U West North Central",
                        "headerName": "CPI-U West North Central",
                        "cellDataType": "number",
                        "formatterFn": "percent",
                    },
                    {
                        "field": "CPI-U Mountain",
                        "headerName": "CPI-U Mountain",
                        "cellDataType": "number",
                        "formatterFn": "percent",
                    },
                    {
                        "field": "Core US",
                        "headerName": "Core US",
                        "cellDataType": "number",
                        "formatterFn": "percent",
                    },
                    {
                        "field": "Core West North Central",
                        "headerName": "Core West North Central",
                        "cellDataType": "number",
                        "formatterFn": "percent",
                    },
                    {
                        "field": "Core Mountain",
                        "headerName": "Core Mountain",
                        "cellDataType": "number",
                        "formatterFn": "percent",
                    },
                ],
            }
        },
    },
)
async def regional_cpi(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get Ninth District regional Consumer Price Index inflation."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="FederalReserveMinneapolisClaims",
    examples=[APIEx(parameters={"provider": "federal_reserve"})],
    widget_config={
        "name": "Minneapolis Fed Minnesota Unemployment Claims",
        "description": "Weekly Minnesota initial and continued unemployment-insurance"
        " claims, indexed by the week-ending date.",
        "subCategory": "Labor Market",
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
                        "field": "initial_claims",
                        "headerName": "Initial Claims",
                        "cellDataType": "number",
                        "formatterFn": "int",
                    },
                    {
                        "field": "continued_claims",
                        "headerName": "Continued Claims",
                        "cellDataType": "number",
                        "formatterFn": "int",
                    },
                ],
            }
        },
    },
)
async def unemployment_claims(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get weekly Minnesota initial and continued unemployment claims."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="FederalReserveMinneapolisJobOpenings",
    examples=[APIEx(parameters={"provider": "federal_reserve"})],
    widget_config={
        "name": "Minneapolis Fed Ninth District Job Openings and Hiring",
        "description": "Monthly job opening and hiring rates, in percent, by Ninth"
        " District state.",
        "subCategory": "Labor Market",
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
                        "field": "MN Job Opening Rate",
                        "headerName": "MN Job Opening Rate",
                        "cellDataType": "number",
                        "formatterFn": "percent",
                    },
                    {
                        "field": "MN Hiring Rate",
                        "headerName": "MN Hiring Rate",
                        "cellDataType": "number",
                        "formatterFn": "percent",
                    },
                    {
                        "field": "MT Job Opening Rate",
                        "headerName": "MT Job Opening Rate",
                        "cellDataType": "number",
                        "formatterFn": "percent",
                    },
                    {
                        "field": "MT Hiring Rate",
                        "headerName": "MT Hiring Rate",
                        "cellDataType": "number",
                        "formatterFn": "percent",
                    },
                    {
                        "field": "ND Job Opening Rate",
                        "headerName": "ND Job Opening Rate",
                        "cellDataType": "number",
                        "formatterFn": "percent",
                    },
                    {
                        "field": "ND Hiring Rate",
                        "headerName": "ND Hiring Rate",
                        "cellDataType": "number",
                        "formatterFn": "percent",
                    },
                    {
                        "field": "SD Job Opening Rate",
                        "headerName": "SD Job Opening Rate",
                        "cellDataType": "number",
                        "formatterFn": "percent",
                    },
                    {
                        "field": "SD Hiring Rate",
                        "headerName": "SD Hiring Rate",
                        "cellDataType": "number",
                        "formatterFn": "percent",
                    },
                    {
                        "field": "WI Job Opening Rate",
                        "headerName": "WI Job Opening Rate",
                        "cellDataType": "number",
                        "formatterFn": "percent",
                    },
                    {
                        "field": "WI Hiring Rate",
                        "headerName": "WI Hiring Rate",
                        "cellDataType": "number",
                        "formatterFn": "percent",
                    },
                ],
            }
        },
    },
)
async def job_openings_hiring(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get Ninth District job opening and hiring rates by state."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="FederalReserveMinneapolisPublications",
    examples=[
        APIEx(parameters={"provider": "federal_reserve"}),
        APIEx(
            description="Index only the Working Papers series.",
            parameters={"series": "working_paper", "provider": "federal_reserve"},
        ),
    ],
)
async def publications(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Index the Minneapolis Fed research and Quarterly Review PDF archives."""
    return await OBBject.from_query(Query(**locals()))
