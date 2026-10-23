"""Federal Reserve Bank of Dallas regional router."""

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

router = Router(prefix="", description="Federal Reserve Bank of Dallas indicators.")


@router.command(
    model="FederalReserveDallasManufacturing",
    examples=[APIEx(parameters={"provider": "federal_reserve"})],
    widget_config={
        "name": "Dallas Fed Texas Manufacturing Outlook Survey (TMOS)",
        "description": "Monthly diffusion indexes for Texas manufacturers, by"
        " indicator.",
        "subCategory": "Texas Outlook Surveys",
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
async def manufacturing(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the Dallas Fed Texas Manufacturing Outlook Survey (TMOS)."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="FederalReserveDallasServiceSector",
    examples=[APIEx(parameters={"provider": "federal_reserve"})],
    widget_config={
        "name": "Dallas Fed Texas Service Sector Outlook Survey (TSSOS)",
        "description": "Monthly diffusion indexes for Texas service-sector firms,"
        " by indicator.",
        "subCategory": "Texas Outlook Surveys",
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
async def service_sector(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the Dallas Fed Texas Service Sector Outlook Survey (TSSOS)."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="FederalReserveDallasRetail",
    examples=[APIEx(parameters={"provider": "federal_reserve"})],
    widget_config={
        "name": "Dallas Fed Texas Retail Outlook Survey (TROS)",
        "description": "Monthly diffusion indexes and response shares for Texas"
        " retailers, by indicator, horizon, and response component.",
        "subCategory": "Texas Outlook Surveys",
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
async def retail(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the Dallas Fed Texas Retail Outlook Survey (TROS)."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="FederalReserveDallasBanking",
    examples=[APIEx(parameters={"provider": "federal_reserve"})],
    widget_config={
        "name": "Dallas Fed Banking Conditions Survey (BCS)",
        "description": "Diffusion indexes of Eleventh District banking conditions,"
        " by indicator and horizon.",
        "subCategory": "Texas Outlook Surveys",
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
async def banking_conditions(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the Dallas Fed Banking Conditions Survey (BCS)."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="FederalReserveDallasEnergy",
    examples=[
        APIEx(parameters={"provider": "federal_reserve"}),
        APIEx(
            description="Get the exploration and production firm group.",
            parameters={
                "firm_group": "exploration_production",
                "provider": "federal_reserve",
            },
        ),
        APIEx(
            description="Get the full data with response shares, year-over-year.",
            parameters={
                "table": "all_data",
                "transform": "year_over_year",
                "provider": "federal_reserve",
            },
        ),
        APIEx(
            description="Get the oil and gas price-level forecasts.",
            parameters={"table": "price_forecasts", "provider": "federal_reserve"},
        ),
    ],
    widget_config={
        "name": "Dallas Fed Energy Survey",
        "description": "Quarterly Eleventh District oil and gas diffusion indexes,"
        " response shares, and price forecasts, by indicator.",
        "subCategory": "Energy",
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
async def energy_survey(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the Dallas Fed Energy Survey: indexes, response shares, and prices."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="FederalReserveDallasTrimmedMeanPCE",
    examples=[APIEx(parameters={"provider": "federal_reserve"})],
    widget_config={
        "name": "Dallas Fed Trimmed Mean PCE (PCE)",
        "description": "Annualized one-, six-, and twelve-month trimmed mean PCE"
        " inflation rates.",
        "subCategory": "Texas Economy",
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
                        "field": "one_month",
                        "headerName": "One-Month",
                        "cellDataType": "number",
                        "formatterFn": "percent",
                    },
                    {
                        "field": "six_month",
                        "headerName": "Six-Month",
                        "cellDataType": "number",
                        "formatterFn": "percent",
                    },
                    {
                        "field": "twelve_month",
                        "headerName": "Twelve-Month",
                        "cellDataType": "number",
                        "formatterFn": "percent",
                    },
                ],
            }
        },
    },
)
async def trimmed_mean_pce(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the Dallas Fed Trimmed Mean PCE Inflation Rate."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="FederalReserveDallasWeeklyEconomic",
    examples=[APIEx(parameters={"provider": "federal_reserve"})],
    widget_config={
        "name": "Dallas Fed Weekly Economic Index (WEI)",
        "description": "The weekly composite index of U.S. real economic activity,"
        " scaled to four-quarter GDP growth.",
        "subCategory": "Texas Economy",
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
                        "field": "wei",
                        "headerName": "WEI",
                        "cellDataType": "number",
                        "formatterFn": "none",
                    },
                ],
            }
        },
    },
)
async def weekly_economic_index(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the Dallas Fed Weekly Economic Index (WEI)."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="FederalReserveDallasLeadingIndex",
    examples=[APIEx(parameters={"provider": "federal_reserve"})],
    widget_config={
        "name": "Dallas Fed Texas Leading Index (TLI)",
        "description": "The Texas Leading Index level (1987 = 100) with its annual"
        " average and year-over-year and December-to-December percent changes.",
        "subCategory": "Texas Economy",
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
                        "cellDataType": "number",
                        "formatterFn": "none",
                    },
                    {
                        "field": "annual_average",
                        "headerName": "Annual Average",
                        "cellDataType": "number",
                        "formatterFn": "none",
                    },
                    {
                        "field": "yoy_change",
                        "headerName": "Year/Year % Change",
                        "cellDataType": "number",
                        "formatterFn": "percent",
                    },
                    {
                        "field": "dec_dec_change",
                        "headerName": "Dec/Dec % Change",
                        "cellDataType": "number",
                        "formatterFn": "percent",
                    },
                ],
            }
        },
    },
)
async def leading_index(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the Dallas Fed Texas Leading Index (TLI)."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="FederalReserveDallasDgei",
    examples=[
        APIEx(parameters={"provider": "federal_reserve"}),
        APIEx(
            description="Get global CPI under PPP-GDP weighting.",
            parameters={
                "indicator": "cpi",
                "weighting": "ppp_gdp",
                "provider": "federal_reserve",
            },
        ),
    ],
    widget_config={
        "name": "Dallas Fed Global Economic Indicators (DGEI)",
        "description": "Country-aggregate series for the selected global indicator"
        " and weighting scheme, by series.",
        "subCategory": "Global Indicators",
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
async def global_economic_indicators(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the Dallas Fed Database of Global Economic Indicators (DGEI)."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="FederalReserveDallasIgrea",
    examples=[APIEx(parameters={"provider": "federal_reserve"})],
    widget_config={
        "name": "Dallas Fed Index of Global Real Economic Activity (IGREA)",
        "description": "The monthly Kilian index of real activity in global"
        " industrial-commodity markets.",
        "subCategory": "Global Indicators",
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
                        "field": "value",
                        "headerName": "IGREA",
                        "cellDataType": "number",
                        "formatterFn": "none",
                    },
                ],
            }
        },
    },
)
async def global_real_economic_activity(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the Dallas Fed Index of Global Real Economic Activity (IGREA)."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="FederalReserveDallasGovernmentDebt",
    examples=[APIEx(parameters={"provider": "federal_reserve"})],
    widget_config={
        "name": "Dallas Fed U.S. Government Debt",
        "description": "Monthly par and market value of U.S. federal debt in billions"
        " of dollars, by series.",
        "subCategory": "Global Indicators",
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
async def government_debt(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the Dallas Fed par and market value of U.S. government debt."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="FederalReserveDallasAgSurvey",
    examples=[
        APIEx(parameters={"provider": "federal_reserve"}),
        APIEx(
            description="Get reported farmland values.",
            parameters={"table": "land_values", "provider": "federal_reserve"},
        ),
    ],
    widget_config={
        "name": "Dallas Fed Eleventh District Agricultural Survey",
        "description": "Quarterly diffusion indexes, response shares, and reported"
        " land values from the Eleventh District agricultural survey, by series.",
        "subCategory": "Agriculture & Resources",
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
async def agricultural_survey(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the Dallas Fed Eleventh District Agricultural Survey."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="FederalReserveDallasBreakeven",
    examples=[
        APIEx(parameters={"provider": "federal_reserve"}),
        APIEx(
            description="Get break-even prices to operate existing wells.",
            parameters={"well_type": "existing", "provider": "federal_reserve"},
        ),
    ],
    widget_config={
        "name": "Dallas Fed Energy Survey Oil Break-Even Prices",
        "description": "The WTI break-even oil price in dollars per barrel, by major"
        " U.S. shale play.",
        "subCategory": "Energy",
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
                        "field": "play",
                        "headerName": "Play",
                    },
                    {
                        "field": "value",
                        "headerName": "Break-Even Price ($/bbl)",
                        "cellDataType": "number",
                        "formatterFn": "none",
                    },
                ],
            }
        },
    },
)
async def breakeven_prices(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the Dallas Fed Energy Survey oil break-even prices by shale play."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="FederalReserveDallasGigafactory",
    examples=[APIEx(parameters={"provider": "federal_reserve"})],
    widget_config={
        "name": "Dallas Fed U.S. Gigafactory Map",
        "description": "Geolocated U.S. battery (gigafactory) manufacturing"
        " facilities, with operator, state, and coordinates.",
        "subCategory": "Agriculture & Resources",
        "gridData": {"w": 40, "h": 25},
        "data": {
            "table": {
                "showAll": True,
                "columnsDefs": [
                    {
                        "field": "facility_name",
                        "headerName": "Facility Name",
                        "pinned": "left",
                    },
                    {
                        "field": "operator",
                        "headerName": "Operator",
                    },
                    {
                        "field": "state",
                        "headerName": "State",
                    },
                    {
                        "field": "latitude",
                        "headerName": "Latitude",
                        "cellDataType": "number",
                        "formatterFn": "none",
                    },
                    {
                        "field": "longitude",
                        "headerName": "Longitude",
                        "cellDataType": "number",
                        "formatterFn": "none",
                    },
                ],
            }
        },
    },
)
async def gigafactory_map(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the Dallas Fed U.S. gigafactory (battery plant) map."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="FederalReserveDallasLithium",
    examples=[APIEx(parameters={"provider": "federal_reserve"})],
    widget_config={
        "name": "Dallas Fed U.S. Lithium Projects Map",
        "description": "Geolocated U.S. lithium resource projects, with company,"
        " resource type, development stage, and coordinates.",
        "subCategory": "Agriculture & Resources",
        "gridData": {"w": 40, "h": 25},
        "data": {
            "table": {
                "showAll": True,
                "columnsDefs": [
                    {
                        "field": "project_name",
                        "headerName": "Project Name",
                        "pinned": "left",
                    },
                    {
                        "field": "company",
                        "headerName": "Company",
                    },
                    {
                        "field": "type",
                        "headerName": "Type",
                    },
                    {
                        "field": "stage",
                        "headerName": "Stage",
                    },
                    {
                        "field": "latitude",
                        "headerName": "Latitude",
                        "cellDataType": "number",
                        "formatterFn": "none",
                    },
                    {
                        "field": "longitude",
                        "headerName": "Longitude",
                        "cellDataType": "number",
                        "formatterFn": "none",
                    },
                ],
            }
        },
    },
)
async def lithium_map(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the Dallas Fed U.S. lithium projects map."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="FederalReserveDallasPublications",
    examples=[
        APIEx(parameters={"provider": "federal_reserve"}),
        APIEx(
            description="Index only the Working Papers series.",
            parameters={"series": "working_papers", "provider": "federal_reserve"},
        ),
    ],
)
async def publications(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Index the Dallas Fed Working Papers and Southwest Economy PDF archives."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="FederalReserveDallasPublicationSeries",
    examples=[APIEx(parameters={"provider": "federal_reserve"})],
    widget_config={
        "name": "Dallas Fed Publication Series",
        "description": "The publication series supported by the Dallas Fed"
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
    """List the supported Dallas Fed publication series and their document counts."""
    return await OBBject.from_query(Query(**locals()))
