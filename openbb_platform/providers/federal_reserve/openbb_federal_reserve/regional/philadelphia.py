"""Federal Reserve Bank of Philadelphia regional router."""

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
    prefix="", description="Federal Reserve Bank of Philadelphia indicators."
)


@router.command(
    model="FederalReservePhiladelphiaAds",
    examples=[APIEx(parameters={"provider": "federal_reserve"})],
    widget_config={
        "name": "Philadelphia Fed ADS Business Conditions Index",
        "subCategory": "Business Conditions",
        "description": "Daily Aruoba-Diebold-Scotti index of real U.S. business"
        " conditions, with the NBER recession indicator.",
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
                        "field": "ads_index",
                        "headerName": "ADS Index",
                        "cellDataType": "number",
                        "formatterFn": "none",
                    },
                    {
                        "field": "recession",
                        "headerName": "Recession",
                        "cellDataType": "number",
                        "formatterFn": "int",
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
    """Get the Philadelphia Fed ADS Business Conditions Index."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="FederalReservePhiladelphiaSpf",
    examples=[
        APIEx(parameters={"provider": "federal_reserve"}),
        APIEx(
            description="Get the mean nominal GDP growth forecast.",
            parameters={
                "variable": "NGDP",
                "statistic": "mean",
                "transform": "growth",
                "provider": "federal_reserve",
            },
        ),
        APIEx(
            description="Get the long-run CPI inflation projection.",
            parameters={
                "variable": "CPI10",
                "statistic": "median",
                "provider": "federal_reserve",
            },
        ),
    ],
    widget_config={
        "name": "Philadelphia Fed Survey of Professional Forecasters",
        "subCategory": "Forecasts & Expectations",
        "description": "Quarterly consensus mean or median forecasts by horizon for"
        " the selected macroeconomic variable.",
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
                        "field": "horizon_1",
                        "headerName": "Current Quarter",
                        "cellDataType": "number",
                        "formatterFn": "none",
                    },
                    {
                        "field": "horizon_2",
                        "headerName": "1Q Ahead",
                        "cellDataType": "number",
                        "formatterFn": "none",
                    },
                    {
                        "field": "horizon_3",
                        "headerName": "2Q Ahead",
                        "cellDataType": "number",
                        "formatterFn": "none",
                    },
                    {
                        "field": "horizon_4",
                        "headerName": "3Q Ahead",
                        "cellDataType": "number",
                        "formatterFn": "none",
                    },
                    {
                        "field": "horizon_5",
                        "headerName": "4Q Ahead",
                        "cellDataType": "number",
                        "formatterFn": "none",
                    },
                    {
                        "field": "horizon_6",
                        "headerName": "5Q Ahead",
                        "cellDataType": "number",
                        "formatterFn": "none",
                    },
                    {
                        "field": "annual_a",
                        "headerName": "Current Year",
                        "cellDataType": "number",
                        "formatterFn": "none",
                    },
                    {
                        "field": "annual_b",
                        "headerName": "Next Year",
                        "cellDataType": "number",
                        "formatterFn": "none",
                    },
                    {
                        "field": "annual_c",
                        "headerName": "2 Years Ahead",
                        "cellDataType": "number",
                        "formatterFn": "none",
                    },
                    {
                        "field": "annual_d",
                        "headerName": "3 Years Ahead",
                        "cellDataType": "number",
                        "formatterFn": "none",
                    },
                    {
                        "field": "long_run",
                        "headerName": "Long Run",
                        "cellDataType": "number",
                        "formatterFn": "none",
                    },
                ],
            }
        },
    },
)
async def survey_professional_forecasters(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the Philadelphia Fed Survey of Professional Forecasters consensus."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="FederalReservePhiladelphiaAnxious",
    examples=[APIEx(parameters={"provider": "federal_reserve"})],
    widget_config={
        "name": "Philadelphia Fed Anxious Index",
        "subCategory": "Forecasts & Expectations",
        "description": "Survey-based probability of a decline in real GDP next quarter,"
        " with the NBER recession indicator.",
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
                        "field": "anxious_index",
                        "headerName": "Anxious Index",
                        "cellDataType": "number",
                        "formatterFn": "percent",
                    },
                    {
                        "field": "recession",
                        "headerName": "Recession",
                        "cellDataType": "number",
                        "formatterFn": "int",
                    },
                ],
            }
        },
    },
)
async def anxious_index(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the Philadelphia Fed Anxious Index recession probability series."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="FederalReservePhiladelphiaGdpPlus",
    examples=[APIEx(parameters={"provider": "federal_reserve"})],
    widget_config={
        "name": "Philadelphia Fed GDPplus",
        "subCategory": "Output & Risk",
        "description": "Annualized quarterly GDPplus output growth with the underlying"
        " GDP and GDI growth rates and the NBER recession indicator.",
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
                        "field": "gdpplus",
                        "headerName": "GDPplus",
                        "cellDataType": "number",
                        "formatterFn": "percent",
                    },
                    {
                        "field": "gdp_growth",
                        "headerName": "GDP Growth",
                        "cellDataType": "number",
                        "formatterFn": "percent",
                    },
                    {
                        "field": "gdi_growth",
                        "headerName": "GDI Growth",
                        "cellDataType": "number",
                        "formatterFn": "percent",
                    },
                    {
                        "field": "recession",
                        "headerName": "Recession",
                        "cellDataType": "number",
                        "formatterFn": "int",
                    },
                ],
            }
        },
    },
)
async def gdpplus(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the Philadelphia Fed GDPplus measure of output growth."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="FederalReservePhiladelphiaPartisan",
    examples=[APIEx(parameters={"provider": "federal_reserve"})],
    widget_config={
        "name": "Philadelphia Fed Partisan Conflict Index",
        "subCategory": "Output & Risk",
        "description": "Monthly index of the degree of political disagreement among"
        " U.S. federal politicians.",
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
                        "field": "partisan_conflict",
                        "headerName": "Partisan Conflict",
                        "cellDataType": "number",
                        "formatterFn": "none",
                    },
                ],
            }
        },
    },
)
async def partisan_conflict(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the Philadelphia Fed Partisan Conflict Index."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="FederalReservePhiladelphiaCoincident",
    examples=[
        APIEx(parameters={"provider": "federal_reserve"}),
        APIEx(
            description="Get a single state's coincident index.",
            parameters={"state": "PA", "provider": "federal_reserve"},
        ),
        APIEx(
            description="Get the diffusion of state-index increases.",
            parameters={"dataset": "diffusion", "provider": "federal_reserve"},
        ),
    ],
    widget_config={
        "name": "Philadelphia Fed State Coincident Indexes",
        "subCategory": "Business Conditions",
        "description": "Monthly state-level coincident indexes of current economic"
        " conditions, or the diffusion of state-index increases.",
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
                        "field": "state",
                        "headerName": "State",
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
async def state_coincident_index(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the Philadelphia Fed State Coincident Indexes."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="FederalReservePhiladelphiaLivingston",
    examples=[
        APIEx(parameters={"provider": "federal_reserve"}),
        APIEx(
            description="Get the median CPI forecast.",
            parameters={
                "variable": "CPI",
                "statistic": "median",
                "provider": "federal_reserve",
            },
        ),
    ],
    widget_config={
        "name": "Philadelphia Fed Livingston Survey",
        "subCategory": "Forecasts & Expectations",
        "description": "Semiannual consensus economist forecasts by horizon for the"
        " selected variable.",
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
                        "field": "base_prior",
                        "headerName": "Base Prior",
                        "cellDataType": "number",
                        "formatterFn": "none",
                    },
                    {
                        "field": "base_current",
                        "headerName": "Base Current",
                        "cellDataType": "number",
                        "formatterFn": "none",
                    },
                    {
                        "field": "six_month",
                        "headerName": "Six Month",
                        "cellDataType": "number",
                        "formatterFn": "none",
                    },
                    {
                        "field": "twelve_month",
                        "headerName": "Twelve Month",
                        "cellDataType": "number",
                        "formatterFn": "none",
                    },
                    {
                        "field": "base_year",
                        "headerName": "Base Year",
                        "cellDataType": "number",
                        "formatterFn": "none",
                    },
                    {
                        "field": "current_year",
                        "headerName": "Current Year",
                        "cellDataType": "number",
                        "formatterFn": "none",
                    },
                    {
                        "field": "one_year",
                        "headerName": "One Year",
                        "cellDataType": "number",
                        "formatterFn": "none",
                    },
                    {
                        "field": "two_year",
                        "headerName": "Two Year",
                        "cellDataType": "number",
                        "formatterFn": "none",
                    },
                    {
                        "field": "ten_year",
                        "headerName": "Ten Year",
                        "cellDataType": "number",
                        "formatterFn": "none",
                    },
                ],
            }
        },
    },
)
async def livingston_survey(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the Philadelphia Fed Livingston Survey forecasts."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="FederalReservePhiladelphiaManufacturing",
    examples=[
        APIEx(parameters={"provider": "federal_reserve"}),
    ],
    widget_config={
        "name": "Philadelphia Fed Manufacturing Business Outlook Survey",
        "subCategory": "Outlook Surveys",
        "description": "Monthly manufacturing diffusion indexes, one column per"
        " indicator code, for the Third Federal Reserve District.",
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
async def manufacturing_outlook(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the Philadelphia Fed Manufacturing Business Outlook Survey indexes."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="FederalReservePhiladelphiaNonmanufacturing",
    examples=[
        APIEx(parameters={"provider": "federal_reserve"}),
        APIEx(
            description="Get the not-seasonally-adjusted response shares.",
            parameters={"adjustment": "nsa", "provider": "federal_reserve"},
        ),
    ],
    widget_config={
        "name": "Philadelphia Fed Nonmanufacturing Business Outlook Survey",
        "subCategory": "Outlook Surveys",
        "description": "Monthly service-sector diffusion indexes and response shares"
        " by indicator, adjustment, horizon, and response component.",
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
async def nonmanufacturing_outlook(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the Philadelphia Fed Nonmanufacturing Business Outlook Survey indexes."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="FederalReservePhiladelphiaAtsix",
    examples=[
        APIEx(parameters={"provider": "federal_reserve"}),
        APIEx(
            description="Get the fitted Nelson-Siegel factors.",
            parameters={"dataset": "factors", "provider": "federal_reserve"},
        ),
    ],
    widget_config={
        "name": "Philadelphia Fed ATSIX Inflation Expectations",
        "subCategory": "Forecasts & Expectations",
        "description": "Monthly Aruoba term structure of expected CPI inflation by"
        " horizon, the ex-ante real-rate term structure, or the Nelson-Siegel"
        " factors, one column per horizon or factor.",
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
async def term_structure_inflation(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the Philadelphia Fed ATSIX term structure of inflation expectations."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="FederalReservePhiladelphiaPublications",
    examples=[
        APIEx(parameters={"provider": "federal_reserve"}),
        APIEx(
            description="Index only the Survey of Professional Forecasters reports.",
            parameters={"series": "spf", "provider": "federal_reserve"},
        ),
    ],
)
async def publications(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Index the Philadelphia Fed survey-report PDF archive."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="FederalReservePhiladelphiaPublicationSeries",
    examples=[APIEx(parameters={"provider": "federal_reserve"})],
    widget_config={
        "name": "Philadelphia Fed Publication Series",
        "description": "The publication series supported by the Philadelphia Fed"
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
    """List the supported Philadelphia Fed publication series and their document counts."""
    return await OBBject.from_query(Query(**locals()))
