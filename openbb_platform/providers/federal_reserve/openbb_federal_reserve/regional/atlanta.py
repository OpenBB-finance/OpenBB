"""Federal Reserve Bank of Atlanta regional router."""

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

router = Router(prefix="", description="Federal Reserve Bank of Atlanta indicators.")

_HEATMAP_COLOR_RULES = [
    {"condition": "lt", "value": 2, "color": "#2166ac", "fill": True},
    {
        "condition": "between",
        "range": {"min": 2, "max": 3},
        "color": "#4393c3",
        "fill": True,
    },
    {
        "condition": "between",
        "range": {"min": 3, "max": 4},
        "color": "#92c5de",
        "fill": True,
    },
    {
        "condition": "between",
        "range": {"min": 4, "max": 5},
        "color": "#fddbc7",
        "fill": True,
    },
    {
        "condition": "between",
        "range": {"min": 5, "max": 6},
        "color": "#f4a582",
        "fill": True,
    },
    {
        "condition": "between",
        "range": {"min": 6, "max": 7},
        "color": "#d6604d",
        "fill": True,
    },
    {"condition": "gte", "value": 7, "color": "#b2182b", "fill": True},
]
_HEATMAP_GAP_MEASURES = ["U-3 Gap", "U-3", "U-6", "Emp-Pop", "ZPOP", "GDP"]
_HEATMAP_COLUMNS = [
    {
        "field": "r_star_measure",
        "headerName": "r* Measure",
        "cellDataType": "text",
        "pinned": "left",
    },
    *(
        {
            "field": gap,
            "headerName": gap,
            "cellDataType": "number",
            "renderFn": "columnColor",
            "renderFnParams": {"colorRules": _HEATMAP_COLOR_RULES},
        }
        for gap in _HEATMAP_GAP_MEASURES
    ),
]


@router.command(
    model="FederalReserveAtlantaGdpNow",
    examples=[
        APIEx(parameters={"provider": "federal_reserve"}),
        APIEx(
            description="Return the latest-release component contributions table.",
            parameters={
                "table": "table_contributions",
                "provider": "federal_reserve",
            },
        ),
    ],
    widget_config={
        "name": "Atlanta Fed GDPNow",
        "description": "GDPNow real GDP nowcast evolution, contributions, and track"
        " record.",
        "subCategory": "Growth & Activity",
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
async def gdpnow(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the Atlanta Fed GDPNow nowcast model track record."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="FederalReserveAtlantaWageGrowth",
    examples=[
        APIEx(parameters={"provider": "federal_reserve"}),
        APIEx(
            description="Return the alternative wage-growth measures.",
            parameters={"cut": "alternative", "provider": "federal_reserve"},
        ),
    ],
    widget_config={
        "name": "Atlanta Fed Wage Growth Tracker",
        "description": "Median 12-month wage growth from the CPS, by demographic cut.",
        "subCategory": "Wages & Uncertainty",
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
async def wage_growth(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the Atlanta Fed Wage Growth Tracker by cohort."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="FederalReserveAtlantaStickyCpi",
    examples=[APIEx(parameters={"provider": "federal_reserve"})],
    widget_config={
        "name": "Atlanta Fed Sticky-Price CPI",
        "description": "Sticky and flexible CPI measures: monthly, annualized, and"
        " 12-month.",
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
                ],
            }
        },
    },
)
async def sticky_cpi(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the Atlanta Fed Sticky-Price CPI series."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="FederalReserveAtlantaBusinessInflation",
    examples=[
        APIEx(parameters={"provider": "federal_reserve"}),
        APIEx(
            description="Return the projected price-factor (discontinued) question.",
            parameters={"question": "price_factors", "provider": "federal_reserve"},
        ),
    ],
    widget_config={
        "name": "Atlanta Fed Business Inflation Expectations",
        "description": "Firms' inflation, unit-cost, and price-change expectations"
        " (BIE survey).",
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
                ],
            }
        },
    },
)
async def business_inflation_expectations(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the Atlanta Fed Business Inflation Expectations survey."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="FederalReserveAtlantaBusinessUncertainty",
    examples=[
        APIEx(parameters={"provider": "federal_reserve"}),
        APIEx(
            description="Return the discontinued natural-units series.",
            parameters={"table": "discontinued", "provider": "federal_reserve"},
        ),
    ],
    widget_config={
        "name": "Atlanta Fed Survey of Business Uncertainty",
        "description": "Monthly firm-level expectations and uncertainty indexes (SBU).",
        "subCategory": "Wages & Uncertainty",
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
async def business_uncertainty(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the Atlanta Fed Survey of Business Uncertainty index values."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="FederalReserveAtlantaMarketProbability",
    examples=[
        APIEx(parameters={"provider": "federal_reserve"}),
        APIEx(
            description="Limit to a recent window.",
            parameters={"start_date": "2026-01-01", "provider": "federal_reserve"},
        ),
    ],
    widget_config={
        "name": "Atlanta Fed Market Probability Tracker",
        "description": "Implied probability distribution across target-rate ranges"
        " for a selected upcoming FOMC meeting, latest date.",
        "subCategory": "Monetary Policy",
        "gridData": {"w": 40, "h": 18, "fullWidth": True},
        "data": {
            "table": {
                "showAll": True,
                "enableCharts": True,
                "chartView": {"enabled": True, "chartType": "column"},
                "columnsDefs": [
                    {
                        "field": "target_range",
                        "headerName": "Target Rate Range",
                        "cellDataType": "text",
                        "pinned": "left",
                    },
                    {
                        "field": "probability",
                        "headerName": "Probability",
                        "cellDataType": "number",
                    },
                ],
            }
        },
    },
)
async def market_probability(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the Atlanta Fed Market Probability Tracker series."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="FederalReserveAtlantaTaylorRule",
    examples=[APIEx(parameters={"provider": "federal_reserve"})],
    widget_config={
        "name": "Atlanta Fed Taylor Rule Prescriptions",
        "description": "Actual federal funds rate vs. the prescription from three"
        " Taylor rule forms.",
        "subCategory": "Monetary Policy",
        "gridData": {"w": 40, "h": 18, "fullWidth": True},
        "data": {
            "table": {
                "showAll": True,
                "enableCharts": True,
                "chartView": {"enabled": True, "chartType": "line"},
                "columnsDefs": [
                    {
                        "field": "date",
                        "headerName": "Date",
                        "cellDataType": "date",
                        "pinned": "left",
                        "sort": "desc",
                    },
                    {
                        "field": "actual_fed_funds_rate",
                        "headerName": "Actual Fed Funds Rate",
                        "cellDataType": "number",
                        "formatterFn": "percent",
                    },
                    {
                        "field": "taylor_93_unemployment",
                        "headerName": "Taylor 1993 (U-3 Gap)",
                        "cellDataType": "number",
                        "formatterFn": "percent",
                    },
                    {
                        "field": "taylor_99_unemployment",
                        "headerName": "Taylor 1999 (U-3 Gap)",
                        "cellDataType": "number",
                        "formatterFn": "percent",
                    },
                    {
                        "field": "taylor_93_gdp",
                        "headerName": "Taylor 1993 (CBO GDP Gap)",
                        "cellDataType": "number",
                        "formatterFn": "percent",
                    },
                ],
            }
        },
    },
)
async def taylor_rule(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the Atlanta Fed Taylor Rule prescribed federal funds rate vs. actual."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="FederalReserveAtlantaTaylorRuleMeasures",
    examples=[
        APIEx(parameters={"provider": "federal_reserve"}),
        APIEx(
            description="Return the candidate resource-gap measures.",
            parameters={"measure": "gap", "provider": "federal_reserve"},
        ),
    ],
    widget_config={
        "name": "Atlanta Fed Taylor Rule Input Measures",
        "description": "Candidate input series for the Taylor rule, by measure family.",
        "subCategory": "Monetary Policy",
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
async def taylor_rule_measures(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the Atlanta Fed Taylor Rule menu of candidate input measures."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="FederalReserveAtlantaTaylorRuleHeatmap",
    examples=[APIEx(parameters={"provider": "federal_reserve"})],
    widget_config={
        "name": "Atlanta Fed Taylor Rule Heat Map",
        "description": "Prescribed federal funds rate across the r-star and"
        " resource-gap measure grid.",
        "subCategory": "Monetary Policy",
        "gridData": {"w": 40, "h": 20},
        "data": {
            "table": {
                "showAll": True,
                "columnsDefs": _HEATMAP_COLUMNS,
            }
        },
    },
)
async def taylor_rule_heatmap(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """Get the Atlanta Fed Taylor Rule quarterly prescription heat map."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="FederalReserveAtlantaPublications",
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
    """Index the Atlanta Fed BIE, SBU, and Working Papers PDF archives."""
    return await OBBject.from_query(Query(**locals()))
