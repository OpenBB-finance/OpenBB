"""Federal Reserve Bank of Cleveland regional router."""

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

router = Router(prefix="", description="Federal Reserve Bank of Cleveland indicators.")


@router.command(
    model="FederalReserveClevelandInflation",
    examples=[
        APIEx(
            description="One- and ten-year model-based inflation expectations.",
            parameters={"horizon": "1,10", "provider": "federal_reserve"},
        )
    ],
    widget_config={
        "name": "Cleveland Fed Inflation Expectations",
        "description": "Model-based estimates of expected average annual inflation"
        " and the implied real interest rate, by horizon.",
        "subCategory": "Inflation Expectations",
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
async def inflation_expectations(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the Cleveland Fed model-based inflation expectations."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="FederalReserveClevelandInflationNowcast",
    examples=[
        APIEx(parameters={"provider": "federal_reserve"}),
        APIEx(
            description="Get the quarterly annualized nowcasts.",
            parameters={"frequency": "quarter", "provider": "federal_reserve"},
        ),
    ],
    widget_config={
        "name": "Cleveland Fed Inflation Nowcast",
        "description": "Model nowcasts of CPI, core CPI, PCE, and core PCE inflation"
        " by target period, alongside the actual figure once released.",
        "subCategory": "Inflation Expectations",
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
async def inflation_nowcast(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the Cleveland Fed CPI and PCE inflation nowcasts by target period."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="FederalReserveClevelandMedianCpi",
    examples=[
        APIEx(parameters={"provider": "federal_reserve"}),
        APIEx(
            description="Get the full revised median CPI history.",
            parameters={"table": "median_cpi", "provider": "federal_reserve"},
        ),
    ],
    widget_config={
        "name": "Cleveland Fed Median CPI",
        "description": "Median and 16% trimmed-mean CPI inflation, with headline and"
        " core CPI, by series.",
        "subCategory": "Median CPI",
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
async def median_cpi(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the Cleveland Fed Median CPI and 16% Trimmed-Mean CPI series."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="FederalReserveClevelandMedianCpiComponents",
    examples=[APIEx(parameters={"provider": "federal_reserve"})],
    widget_config={
        "name": "Cleveland Fed Median CPI Components",
        "description": "The latest month's CPI expenditure categories ranked by"
        " 1-month annualized price change, with relative importance weights.",
        "subCategory": "Median CPI",
        "gridData": {"w": 40, "h": 20},
        "data": {
            "table": {
                "showAll": True,
                "columnsDefs": [
                    {
                        "field": "component",
                        "headerName": "Component",
                        "pinned": "left",
                    },
                    {
                        "field": "change",
                        "headerName": "1-Month Annualized Percent Change",
                        "cellDataType": "number",
                        "formatterFn": "percent",
                    },
                    {
                        "field": "relative_importance",
                        "headerName": "Relative Importance",
                        "cellDataType": "number",
                        "formatterFn": "percent",
                    },
                    {
                        "field": "cumulative_relative_importance",
                        "headerName": "Cumulative Relative Importance",
                        "cellDataType": "number",
                        "formatterFn": "percent",
                    },
                ],
            }
        },
    },
)
async def median_cpi_components(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the latest Median CPI component distribution by expenditure category."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="FederalReserveClevelandSystemicRisk",
    examples=[APIEx(parameters={"provider": "federal_reserve"})],
    widget_config={
        "name": "Cleveland Fed Systemic Risk Indicator",
        "description": "A daily gauge of U.S. banking-system stress, the average"
        " distance to default minus the portfolio distance to default.",
        "subCategory": "Financial Risk",
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
async def systemic_risk(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the Cleveland Fed Systemic Risk Indicator and distance-to-default legs."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="FederalReserveClevelandPublications",
    examples=[
        APIEx(parameters={"provider": "federal_reserve"}),
        APIEx(
            description="Index a single series from a start date.",
            parameters={
                "series": "working_paper",
                "start_date": "2025-01-01",
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
    """Index the Cleveland Fed publication PDF archives."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="FederalReserveClevelandPublicationSeries",
    examples=[APIEx(parameters={"provider": "federal_reserve"})],
    widget_config={
        "name": "Cleveland Fed Publication Series",
        "description": "The publication series supported by the Cleveland Fed"
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
    """List the supported Cleveland Fed publication series and their document counts."""
    return await OBBject.from_query(Query(**locals()))
