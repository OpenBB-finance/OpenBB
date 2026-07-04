"""Federal Reserve Bank of San Francisco regional router."""

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
    prefix="", description="Federal Reserve Bank of San Francisco indicators."
)


@router.command(
    model="FederalReserveSanFranciscoNewsSentiment",
    examples=[APIEx(parameters={"provider": "federal_reserve"})],
    widget_config={
        "name": "SF Fed Daily News Sentiment Index",
        "description": "Daily, high-frequency measure of economic sentiment built"
        " from the tone of economics coverage in major U.S. newspapers.",
        "subCategory": "Activity & Productivity",
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
                        "field": "news_sentiment",
                        "headerName": "News Sentiment",
                        "cellDataType": "number",
                        "formatterFn": "none",
                    },
                ],
            }
        },
    },
)
async def news_sentiment(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the San Francisco Fed Daily News Sentiment Index."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="FederalReserveSanFranciscoProxyFundsRate",
    examples=[
        APIEx(parameters={"provider": "federal_reserve"}),
        APIEx(
            description="Get the weekly series.",
            parameters={"frequency": "weekly", "provider": "federal_reserve"},
        ),
    ],
    widget_config={
        "name": "SF Fed Proxy Funds Rate",
        "description": "Single funds-rate-equivalent gauge of the overall stance of"
        " monetary policy, reported alongside the effective federal funds rate.",
        "subCategory": "Rates & Policy",
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
                        "field": "effective_funds_rate",
                        "headerName": "Effective Funds Rate",
                        "cellDataType": "number",
                        "formatterFn": "percent",
                    },
                    {
                        "field": "proxy_funds_rate",
                        "headerName": "Proxy Funds Rate",
                        "cellDataType": "number",
                        "formatterFn": "percent",
                    },
                ],
            }
        },
    },
)
async def proxy_funds_rate(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the San Francisco Fed Proxy Funds Rate."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="FederalReserveSanFranciscoCyclicalPce",
    examples=[APIEx(parameters={"provider": "federal_reserve"})],
    widget_config={
        "name": "SF Fed Cyclical & Acyclical Core PCE Inflation",
        "description": "Monthly decomposition of core PCE inflation into cyclical and"
        " acyclical components, as inflation rates and contributions.",
        "subCategory": "Inflation",
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
                        "field": "cyclical_inflation_yoy",
                        "headerName": "Cyclical Inflation (YoY)",
                        "cellDataType": "number",
                        "formatterFn": "percent",
                    },
                    {
                        "field": "acyclical_inflation_yoy",
                        "headerName": "Acyclical Inflation (YoY)",
                        "cellDataType": "number",
                        "formatterFn": "percent",
                    },
                    {
                        "field": "cyclical_contribution_yoy",
                        "headerName": "Cyclical Contribution (YoY)",
                        "cellDataType": "number",
                        "formatterFn": "percent",
                    },
                    {
                        "field": "acyclical_contribution_yoy",
                        "headerName": "Acyclical Contribution (YoY)",
                        "cellDataType": "number",
                        "formatterFn": "percent",
                    },
                    {
                        "field": "acyclical_healthcare_contribution_yoy",
                        "headerName": "Acyclical Health-Care Contribution (YoY)",
                        "cellDataType": "number",
                        "formatterFn": "percent",
                    },
                    {
                        "field": "acyclical_non_healthcare_contribution_yoy",
                        "headerName": "Acyclical Non-Health-Care Contribution (YoY)",
                        "cellDataType": "number",
                        "formatterFn": "percent",
                    },
                    {
                        "field": "cyclical_inflation_mom",
                        "headerName": "Cyclical Inflation (MoM, AR)",
                        "cellDataType": "number",
                        "formatterFn": "percent",
                    },
                    {
                        "field": "acyclical_inflation_mom",
                        "headerName": "Acyclical Inflation (MoM, AR)",
                        "cellDataType": "number",
                        "formatterFn": "percent",
                    },
                    {
                        "field": "cyclical_contribution_mom",
                        "headerName": "Cyclical Contribution (MoM, AR)",
                        "cellDataType": "number",
                        "formatterFn": "percent",
                    },
                    {
                        "field": "acyclical_contribution_mom",
                        "headerName": "Acyclical Contribution (MoM, AR)",
                        "cellDataType": "number",
                        "formatterFn": "percent",
                    },
                    {
                        "field": "acyclical_healthcare_contribution_mom",
                        "headerName": "Acyclical Health-Care Contribution (MoM, AR)",
                        "cellDataType": "number",
                        "formatterFn": "percent",
                    },
                    {
                        "field": "acyclical_non_healthcare_contribution_mom",
                        "headerName": "Acyclical Non-Health-Care Contribution (MoM, AR)",
                        "cellDataType": "number",
                        "formatterFn": "percent",
                    },
                ],
            }
        },
    },
)
async def cyclical_pce(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the San Francisco Fed Cyclical & Acyclical Core PCE Inflation series."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="FederalReserveSanFranciscoSupplyDemandPce",
    examples=[APIEx(parameters={"provider": "federal_reserve"})],
    widget_config={
        "name": "SF Fed Supply & Demand-Driven PCE Inflation",
        "description": "Monthly decomposition of core and headline PCE inflation into"
        " supply-driven, demand-driven, and ambiguous portions.",
        "subCategory": "Inflation",
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
                        "field": "demand_core_yoy",
                        "headerName": "Demand-Driven Core (YoY)",
                        "cellDataType": "number",
                        "formatterFn": "percent",
                    },
                    {
                        "field": "ambiguous_core_yoy",
                        "headerName": "Ambiguous Core (YoY)",
                        "cellDataType": "number",
                        "formatterFn": "percent",
                    },
                    {
                        "field": "supply_core_yoy",
                        "headerName": "Supply-Driven Core (YoY)",
                        "cellDataType": "number",
                        "formatterFn": "percent",
                    },
                    {
                        "field": "demand_core_mom",
                        "headerName": "Demand-Driven Core (MoM)",
                        "cellDataType": "number",
                        "formatterFn": "percent",
                    },
                    {
                        "field": "ambiguous_core_mom",
                        "headerName": "Ambiguous Core (MoM)",
                        "cellDataType": "number",
                        "formatterFn": "percent",
                    },
                    {
                        "field": "supply_core_mom",
                        "headerName": "Supply-Driven Core (MoM)",
                        "cellDataType": "number",
                        "formatterFn": "percent",
                    },
                    {
                        "field": "demand_headline_yoy",
                        "headerName": "Demand-Driven Headline (YoY)",
                        "cellDataType": "number",
                        "formatterFn": "percent",
                    },
                    {
                        "field": "ambiguous_headline_yoy",
                        "headerName": "Ambiguous Headline (YoY)",
                        "cellDataType": "number",
                        "formatterFn": "percent",
                    },
                    {
                        "field": "supply_headline_yoy",
                        "headerName": "Supply-Driven Headline (YoY)",
                        "cellDataType": "number",
                        "formatterFn": "percent",
                    },
                    {
                        "field": "demand_headline_mom",
                        "headerName": "Demand-Driven Headline (MoM)",
                        "cellDataType": "number",
                        "formatterFn": "percent",
                    },
                    {
                        "field": "ambiguous_headline_mom",
                        "headerName": "Ambiguous Headline (MoM)",
                        "cellDataType": "number",
                        "formatterFn": "percent",
                    },
                    {
                        "field": "supply_headline_mom",
                        "headerName": "Supply-Driven Headline (MoM)",
                        "cellDataType": "number",
                        "formatterFn": "percent",
                    },
                ],
            }
        },
    },
)
async def supply_demand_pce(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the San Francisco Fed Supply & Demand-Driven PCE Inflation series."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="FederalReserveSanFranciscoTfp",
    examples=[
        APIEx(parameters={"provider": "federal_reserve"}),
        APIEx(
            description="Get the capital-input composition detail.",
            parameters={
                "table": "capital_input_details",
                "provider": "federal_reserve",
            },
        ),
    ],
    widget_config={
        "name": "SF Fed Quarterly TFP (Fernald)",
        "description": "Fernald growth-accounting decomposition of U.S. business-sector"
        " output, including utilization-adjusted TFP, as annualized percent growth.",
        "subCategory": "Activity & Productivity",
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
async def total_factor_productivity(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the San Francisco Fed Quarterly TFP (Fernald) growth-accounting series."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="FederalReserveSanFranciscoTermPremium",
    examples=[
        APIEx(parameters={"provider": "federal_reserve"}),
        APIEx(
            description="Get the two-year decomposition.",
            parameters={"maturity": 2, "provider": "federal_reserve"},
        ),
    ],
    widget_config={
        "name": "SF Fed Treasury Term Premium",
        "description": "Daily decomposition of the zero-coupon Treasury yield into the"
        " expected short-rate component and the term premium.",
        "subCategory": "Rates & Policy",
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
                        "field": "yield_zero_coupon",
                        "headerName": "Zero-Coupon Yield",
                        "cellDataType": "number",
                        "formatterFn": "percent",
                    },
                    {
                        "field": "expected_short_rate",
                        "headerName": "Expected Short Rate",
                        "cellDataType": "number",
                        "formatterFn": "percent",
                    },
                    {
                        "field": "term_premium",
                        "headerName": "Term Premium",
                        "cellDataType": "number",
                        "formatterFn": "percent",
                    },
                ],
            }
        },
    },
)
async def term_premium(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the San Francisco Fed Treasury Term Premium decomposition."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="FederalReserveSanFranciscoShortRatePath",
    examples=[APIEx(parameters={"provider": "federal_reserve"})],
    widget_config={
        "name": "SF Fed Estimated Short-Rate Path",
        "description": "Model-implied expected path of the short-term interest rate by"
        " horizon, for the most-recent and FOMC scenarios.",
        "subCategory": "Rates & Policy",
        "gridData": {"w": 40, "h": 20},
        "data": {
            "table": {
                "showAll": True,
                "columnsDefs": [
                    {
                        "field": "maturity",
                        "headerName": "Maturity",
                        "cellDataType": "number",
                        "pinned": "left",
                        "sort": "asc",
                    },
                ],
            }
        },
    },
)
async def short_rate_path(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the San Francisco Fed model-implied expected short-rate path by horizon."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="FederalReserveSanFranciscoPublications",
    examples=[
        APIEx(parameters={"provider": "federal_reserve"}),
        APIEx(
            description="Index the SF FedViews archive.",
            parameters={"publication_type": "fedviews", "provider": "federal_reserve"},
        ),
    ],
)
async def publications(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Index the San Francisco Fed Economic Letter and FedViews PDF archives."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="FederalReserveSanFranciscoPublicationSeries",
    examples=[APIEx(parameters={"provider": "federal_reserve"})],
    widget_config={
        "name": "San Francisco Fed Publication Series",
        "description": "The publication series supported by the San Francisco Fed"
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
    """List the supported San Francisco Fed publication series and their document counts."""
    return await OBBject.from_query(Query(**locals()))
